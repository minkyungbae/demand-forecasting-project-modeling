from typing import Optional, List, Dict
from datetime import datetime
import pandas as pd
import numpy as np
from app.core.database import get_database
from app.models.visualization import VisualizationResponse
from app.services.visualization.chart_generator import ChartGenerator
from app.services.file.file_repository import FileRepository
from app.services.file.file_analysis_config_repository import FileAnalysisConfigRepository
from app.services.correlation.correlation_repository import CorrelationRepository
from app.services.solution.llm_service import LLMService

class VisualizationService:
    """시각화 서비스"""
    
    def __init__(self):
        self.chart_generator = ChartGenerator()
        self.file_repository = FileRepository()
        self.config_repository = FileAnalysisConfigRepository()
        self.correlation_repository = CorrelationRepository()
        self.llm_service = LLMService()
    
    async def create_visualization(
        self,
        file_id: str,
        chart_type: str,
        target_column: Optional[str],
        x_column: Optional[str],
        y_column: Optional[str],
        columns: Optional[List[str]],
        user_id: str
    ) -> VisualizationResponse:
        """시각화 생성"""
        # 파일 정보 조회 및 컬럼명 검증
        file_info = await self.file_repository.get_sales_info(file_id, user_id)
        if not file_info:
            raise ValueError("파일을 찾을 수 없습니다")
        
        available_columns = file_info.get('columns_list', [])
        
        # target_column이 있으면 LLM으로 자동 추천
        if target_column:
            try:
                # 데이터 샘플 가져오기
                data_sample = await self.file_repository.get_csv_data(file_id, 0, 20)
                
                # LLM으로 컬럼 추천
                suggestion = await self.llm_service.suggest_visualization_columns(
                    target_column=target_column,
                    chart_type=chart_type,
                    all_columns=available_columns,
                    data_sample=data_sample
                )
                
                # 추천된 컬럼 사용
                if chart_type in ["heatmap", "pie"]:
                    # heatmap과 pie는 columns 사용
                    columns = suggestion.get("columns", columns)
                    # pie의 경우 x_column, y_column도 설정 가능
                    if chart_type == "pie" and not columns:
                        x_column = suggestion.get("x_column") or x_column
                        y_column = suggestion.get("y_column") or y_column
                else:
                    x_column = suggestion.get("x_column") or x_column
                    y_column = suggestion.get("y_column") or y_column
            except Exception:
                pass  # LLM 실패 시 사용자 입력값 사용
        
        # 컬럼명 검증
        if x_column and x_column not in available_columns:
            raise ValueError(f"X축 컬럼 '{x_column}'이(가) 파일에 존재하지 않습니다. 사용 가능한 컬럼: {available_columns}")
        
        if y_column and y_column not in available_columns:
            raise ValueError(f"Y축 컬럼 '{y_column}'이(가) 파일에 존재하지 않습니다. 사용 가능한 컬럼: {available_columns}")
        
        if columns:
            invalid_columns = [col for col in columns if col not in available_columns]
            if invalid_columns:
                raise ValueError(f"컬럼 {invalid_columns}이(가) 파일에 존재하지 않습니다. 사용 가능한 컬럼: {available_columns}")
        
        # 데이터 로드
        data = await self._load_data(file_id, user_id)
        
        # 차트 생성
        chart_data = await self.chart_generator.generate_chart(
            data=data,
            chart_type=chart_type,
            x_column=x_column,
            y_column=y_column,
            columns=columns
        )
        
        # 결과 저장
        visualization_id = f"viz_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        await self._save_visualization(
            visualization_id=visualization_id,
            file_id=file_id,
            chart_type=chart_type,
            chart_data=chart_data,
            user_id=user_id
        )
        
        return VisualizationResponse(
            visualization_id=visualization_id,
            file_id=file_id,
            chart_type=chart_type,
            chart_data=chart_data,
            created_at=datetime.now()
        )
    
    async def get_visualization(self, visualization_id: str) -> Optional[VisualizationResponse]:
        """시각화 조회"""
        db = await get_database()
        collection = db['visualizations']
        viz = await collection.find_one({'visualization_id': visualization_id})
        
        if viz:
            viz.pop('_id', None)
            return VisualizationResponse(**viz)
        return None
    
    async def _load_data(self, file_id: str, user_id: str) -> List[dict]:
        """데이터 로드"""
        # 파일 소유권 확인 (이미 create_visualization에서 확인했지만, 재확인)
        file_info = await self.file_repository.get_sales_info(file_id, user_id)
        if not file_info:
            raise ValueError("파일을 찾을 수 없습니다")
        
        # 데이터 로드
        data = await self.file_repository.get_csv_data(file_id, 0, 10000)
        return data
    
    async def _save_visualization(
        self,
        visualization_id: str,
        file_id: str,
        chart_type: str,
        chart_data: str,
        user_id: str
    ):
        """시각화 저장"""
        db = await get_database()
        collection = db['visualizations']
        await collection.insert_one({
            'visualization_id': visualization_id,
            'file_id': file_id,
            'chart_type': chart_type,
            'chart_data': chart_data,
            'user_id': user_id,
            'created_at': datetime.now()
        })
    
    async def get_product_count_bar_chart(
        self,
        file_id: str,
        user_id: str,
        top_n: Optional[int] = None,
        use_sum: bool = False
    ) -> Dict:
        """상품명별 count 또는 sum 막대그래프 생성"""
        # 파일 정보 조회
        file_info = await self.file_repository.get_sales_info(file_id, user_id)
        if not file_info:
            raise ValueError("파일을 찾을 수 없습니다")
        
        target_column = file_info.get('target_column')
        if not target_column:
            raise ValueError("파일 업로드 시 target_column을 지정하지 않았습니다")
        
        # 설정 조회 (그룹화 컬럼 확인)
        config = await self.config_repository.get_config(file_id, target_column)
        if not config:
            raise ValueError("컬럼 추천 설정을 먼저 생성해야 합니다")
        
        grouping_columns = config.get('grouping_columns', [])
        if not grouping_columns:
            raise ValueError("그룹화 컬럼이 설정되지 않았습니다")
        
        # 첫 번째 그룹화 컬럼 사용 (보통 상품명)
        group_column = grouping_columns[0]
        
        # 데이터 로드
        data = await self.file_repository.get_csv_data(file_id, 0, 10000)
        if not data:
            raise ValueError("데이터를 찾을 수 없습니다")
        
        df = pd.DataFrame(data)
        
        # 그룹별 계산
        if group_column not in df.columns:
            raise ValueError(f"그룹화 컬럼 '{group_column}'을 찾을 수 없습니다")
        
        if target_column not in df.columns:
            raise ValueError(f"타겟 컬럼 '{target_column}'을 찾을 수 없습니다")
        
        # use_sum이 True이면 sum 계산, False이면 count 계산
        if use_sum:
            # 상품별 합계 계산
            df[target_column] = pd.to_numeric(df[target_column], errors='coerce')
            sum_df = df.groupby(group_column)[target_column].sum().reset_index()
            sum_df.columns = [group_column, 'sum']
            sum_df = sum_df.sort_values('sum', ascending=False)
            
            # top_n이 있으면 상위 N개만 선택
            if top_n:
                sum_df = sum_df.head(top_n)
                title = f"상위 {top_n}개 상품별 {target_column} 합계"
            else:
                title = f"전체 상품별 {target_column} 합계"
            
            # 막대그래프 생성
            import plotly.express as px
            fig = px.bar(
                sum_df,
                x=group_column,
                y='sum',
                title=title,
                labels={group_column: '상품명', 'sum': target_column}
            )
        else:
            # 전체 count 계산
            count_df = df[group_column].value_counts().reset_index()
            count_df.columns = [group_column, 'count']
            
            # top_n이 있으면 상위 N개만 선택
            if top_n:
                count_df = count_df.head(top_n)
                title = f"상위 {top_n}개 상품별 데이터 개수"
            else:
                title = "전체 상품별 데이터 개수"
            
            # 막대그래프 생성
            import plotly.express as px
            fig = px.bar(
                count_df,
                x=group_column,
                y='count',
                title=title,
                labels={group_column: '상품명', 'count': '개수'}
            )
        fig.update_xaxes(tickangle=-45)
        
        # Base64 인코딩
        import base64
        img_bytes = fig.to_image(format="png")
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
        
        # visualization_id 생성 및 저장
        visualization_id = f"viz_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        chart_type = "bar"
        await self._save_visualization(
            visualization_id=visualization_id,
            file_id=file_id,
            chart_type=chart_type,
            chart_data=img_base64,
            user_id=user_id
        )
        
        return {
            "visualization_id": visualization_id,
            "chart_data": img_base64
        }
    
    async def get_product_list(self, file_id: str, user_id: str) -> List[str]:
        """상품명 목록 조회"""
        # 파일 정보 조회
        file_info = await self.file_repository.get_sales_info(file_id, user_id)
        if not file_info:
            raise ValueError("파일을 찾을 수 없습니다")
        
        target_column = file_info.get('target_column')
        if not target_column:
            raise ValueError("파일 업로드 시 target_column을 지정하지 않았습니다")
        
        # 설정 조회 (그룹화 컬럼 확인)
        config = await self.config_repository.get_config(file_id, target_column)
        if not config:
            raise ValueError("컬럼 추천 설정을 먼저 생성해야 합니다")
        
        grouping_columns = config.get('grouping_columns', [])
        if not grouping_columns:
            raise ValueError("그룹화 컬럼이 설정되지 않았습니다")
        
        # 첫 번째 그룹화 컬럼 사용
        group_column = grouping_columns[0]
        
        # 데이터 로드
        data = await self.file_repository.get_csv_data(file_id, 0, 10000)
        if not data:
            raise ValueError("데이터를 찾을 수 없습니다")
        
        df = pd.DataFrame(data)
        
        if group_column not in df.columns:
            raise ValueError(f"그룹화 컬럼 '{group_column}'을 찾을 수 없습니다")
        
        # 고유한 상품명 목록 반환 (정렬)
        product_list = sorted(df[group_column].unique().tolist())
        return product_list
    
    async def get_product_quantity_trend(
        self,
        file_id: str,
        product_name: str,
        user_id: str
    ) -> Dict:
        """특정 상품명의 수량 추세 선그래프 생성"""
        # 파일 정보 조회
        file_info = await self.file_repository.get_sales_info(file_id, user_id)
        if not file_info:
            raise ValueError("파일을 찾을 수 없습니다")
        
        target_column = file_info.get('target_column')
        if not target_column:
            raise ValueError("파일 업로드 시 target_column을 지정하지 않았습니다")
        
        # 설정 조회
        config = await self.config_repository.get_config(file_id, target_column)
        if not config:
            raise ValueError("컬럼 추천 설정을 먼저 생성해야 합니다")
        
        grouping_columns = config.get('grouping_columns', [])
        date_column = config.get('date_column')
        
        if not grouping_columns:
            raise ValueError("그룹화 컬럼이 설정되지 않았습니다")
        if not date_column:
            raise ValueError("날짜 컬럼이 설정되지 않았습니다")
        
        group_column = grouping_columns[0]
        
        # 데이터 로드
        data = await self.file_repository.get_csv_data(file_id, 0, 10000)
        if not data:
            raise ValueError("데이터를 찾을 수 없습니다")
        
        df = pd.DataFrame(data)
        
        # 필터링 (특정 상품명만)
        if group_column not in df.columns:
            raise ValueError(f"그룹화 컬럼 '{group_column}'을 찾을 수 없습니다")
        if target_column not in df.columns:
            raise ValueError(f"타겟 컬럼 '{target_column}'을 찾을 수 없습니다")
        if date_column not in df.columns:
            raise ValueError(f"날짜 컬럼 '{date_column}'을 찾을 수 없습니다")
        
        filtered_df = df[df[group_column] == product_name].copy()
        
        if len(filtered_df) == 0:
            raise ValueError(f"상품명 '{product_name}'에 대한 데이터를 찾을 수 없습니다")
        
        # 날짜 컬럼 정렬
        filtered_df = filtered_df.sort_values(date_column)
        
        # 선그래프 생성
        import plotly.express as px
        fig = px.line(
            filtered_df,
            x=date_column,
            y=target_column,
            title=f"{product_name}의 {target_column} 추세",
            labels={date_column: '날짜', target_column: target_column}
        )
        
        # Base64 인코딩
        import base64
        img_bytes = fig.to_image(format="png")
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
        
        # visualization_id 생성 및 저장
        visualization_id = f"viz_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        chart_type = "line"
        await self._save_visualization(
            visualization_id=visualization_id,
            file_id=file_id,
            chart_type=chart_type,
            chart_data=img_base64,
            user_id=user_id
        )
        
        return {
            "visualization_id": visualization_id,
            "chart_data": img_base64
        }
    
    async def get_correlation_heatmap(
        self,
        file_id: str,
        user_id: str
    ) -> Dict:
        """상관관계 분석 결과 기반 히트맵 생성"""
        # 파일 정보 조회
        file_info = await self.file_repository.get_sales_info(file_id, user_id)
        if not file_info:
            raise ValueError("파일을 찾을 수 없습니다")
        
        target_column = file_info.get('target_column')
        if not target_column:
            raise ValueError("파일 업로드 시 target_column을 지정하지 않았습니다")
        
        # 상관관계 분석 결과 조회
        correlation_result = await self.correlation_repository.get_by_file_id(file_id)
        if not correlation_result:
            raise ValueError("상관관계 분석 결과를 찾을 수 없습니다. 먼저 상관관계 분석을 수행해주세요.")
        
        correlation_matrix = correlation_result.get('correlation_matrix', {})
        if not correlation_matrix:
            raise ValueError("상관관계 행렬 데이터가 없습니다")
        
        # 설정 조회 (valid_columns 확인)
        config = await self.config_repository.get_config(file_id, target_column)
        if not config:
            raise ValueError("컬럼 추천 설정을 먼저 생성해야 합니다")
        
        valid_columns = config.get('valid_columns', [])
        grouping_columns = config.get('grouping_columns', [])
        
        # 피처 목록 (그룹화 컬럼 제외)
        features = [col for col in valid_columns if col not in grouping_columns]
        
        # 전체 상관관계 행렬 생성 (피처들 간의 상관관계 포함)
        # 데이터 로드하여 피처들 간의 상관관계 계산
        data = await self.file_repository.get_csv_data(file_id, 0, 10000)
        if not data:
            raise ValueError("데이터를 찾을 수 없습니다")
        
        df = pd.DataFrame(data)
        
        # 히트맵용 컬럼 선택 (target_column + features)
        heatmap_columns = [target_column] + features
        
        # 존재하는 컬럼만 선택
        available_columns = [col for col in heatmap_columns if col in df.columns]
        
        if len(available_columns) < 2:
            raise ValueError("히트맵을 생성하기 위한 충분한 컬럼이 없습니다")
        
        # 숫자형 컬럼만 선택
        numeric_df = df[available_columns].select_dtypes(include=[np.number])
        
        if len(numeric_df.columns) < 2:
            raise ValueError("숫자형 컬럼이 부족하여 히트맵을 생성할 수 없습니다")
        
        # 정규화 후 상관관계 행렬 계산
        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()
        # NaN 값 제거
        numeric_df_clean = numeric_df.dropna()
        if len(numeric_df_clean) < 2:
            raise ValueError("유효한 데이터가 부족하여 히트맵을 생성할 수 없습니다")
        
        # 각 컬럼을 정규화 (평균 0, 표준편차 1)
        numeric_df_normalized = pd.DataFrame(
            scaler.fit_transform(numeric_df_clean),
            columns=numeric_df_clean.columns,
            index=numeric_df_clean.index
        )
        
        # 정규화된 데이터로 상관관계 행렬 계산
        corr_matrix = numeric_df_normalized.corr()
        
        # 히트맵 생성
        import plotly.express as px
        fig = px.imshow(
            corr_matrix,
            text_auto='.2f',
            aspect="auto",
            title=f"상관관계 히트맵 ({target_column} 포함)",
            labels=dict(x="변수", y="변수", color="상관계수"),
            color_continuous_scale="RdBu",
            color_continuous_midpoint=0
        )
        fig.update_xaxes(side="bottom")
        
        # Base64 인코딩
        import base64
        img_bytes = fig.to_image(format="png")
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
        
        # visualization_id 생성 및 저장
        visualization_id = f"viz_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        chart_type = "heatmap"
        await self._save_visualization(
            visualization_id=visualization_id,
            file_id=file_id,
            chart_type=chart_type,
            chart_data=img_base64,
            user_id=user_id
        )
        
        return {
            "visualization_id": visualization_id,
            "chart_data": img_base64
        }

