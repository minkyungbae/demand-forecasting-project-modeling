from typing import Dict, List, Optional
from datetime import datetime
import time
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from scipy.stats import chi2_contingency
from app.core.database import get_database
from app.models.correlation import CorrelationAnalysisResponse, TopCorrelationItem
from app.services.correlation.weight_calculator import WeightCalculator
from app.services.correlation.correlation_repository import CorrelationRepository
from app.services.file.file_repository import FileRepository
from app.services.file.file_service import FileService
from app.services.weight.weight_repository import WeightRepository
from app.services.file.file_analysis_config_repository import FileAnalysisConfigRepository
from app.services.analysis.analysis_repository import AnalysisRepository

class CorrelationService:
    """상관관계 분석 서비스"""
    
    def __init__(self):
        self.weight_calculator = WeightCalculator()
        self.repository = CorrelationRepository()
        self.file_repository = FileRepository()
        self.file_service = FileService()
        self.weight_repository = WeightRepository()
        self.config_repository = FileAnalysisConfigRepository()
        self.analysis_repository = AnalysisRepository()
    
    async def analyze_correlations(
        self, 
        file_id: str,
        features: Optional[List[str]],
        user_id: str
    ) -> CorrelationAnalysisResponse:
        """상관관계 분석 및 가중치 계산"""
        # 1. 파일 소유권 확인 및 target_column 가져오기
        file_info = await self.file_repository.get_sales_info(file_id, user_id)
        if not file_info:
            raise ValueError("파일을 찾을 수 없습니다")
        
        target_column = file_info.get('target_column')
        if not target_column:
            raise ValueError("파일 업로드 시 target_column을 지정하지 않았습니다. 파일을 다시 업로드하거나 target_column을 지정해주세요.")
        
        # 2. 설정 정보 가져오기 (valid_columns와 grouping_columns 사용)
        config = await self.file_service.config_repository.get_config(file_id, target_column)
        group_by_columns = config.get('group_by_columns', []) if config else []
        primary_group_by_column = config.get('group_by_column') if config else None
        date_column = config.get('date_column') if config else None
        lag_feature_columns = config.get('lag_feature_columns', []) if config else []
        
        # valid_columns가 있으면 사용 (Lag 피처 포함된 유효 컬럼), 없으면 features 사용 (하위 호환성)
        valid_columns = config.get('valid_columns', []) if config else []
        if not features or len(features) == 0:
            # features가 없으면 valid_columns 사용
            if valid_columns and len(valid_columns) > 0:
                # valid_columns는 그룹화 컬럼을 제외한 순수 피처만 포함
                # grouping_columns는 상관관계 분석에서 그룹화 용도로만 사용
                features_for_correlation = [col for col in valid_columns if col not in (group_by_columns or [])]
                if features_for_correlation:
                    features = features_for_correlation
                    print(f"✅ valid_columns 사용: {len(features)}개 피처 (Lag 피처 포함)")
            else:
                raise ValueError("features를 지정하거나, 파일 업로드 시 target_column을 지정하여 컬럼 추천을 먼저 수행해야 합니다.")
        
        # 3. 데이터 로드 및 Lag 피처 생성 (필요시)
        data = await self._load_data(file_id)
        
        # Lag 피처가 필요한데 데이터에 없으면 실시간 생성
        if lag_feature_columns and date_column:
            from app.services.feature.lag_feature_generator import LagFeatureGenerator
            lag_generator = LagFeatureGenerator()
            
            # Lag 피처가 데이터에 있는지 확인
            sample_row = data[0] if data else {}
            needs_lag_generation = any(lag_col not in sample_row for lag_col in lag_feature_columns[:3])  # 처음 3개만 체크
            
            if needs_lag_generation:
                print(f"📊 Lag 피처 실시간 생성 중...")
                try:
                    # Lag 피처 생성에 필요한 정보
                    valid_base_columns = [col for col in valid_columns if not col.endswith('_lag_7d') and not col.endswith('_lag_14d') and not col.endswith('_lag_30d')]
                    grouping_cols = config.get('grouping_columns', []) if config else []
                    
                    processed_df, _ = await lag_generator.generate_lag_features(
                        data=data,
                        date_column=date_column,
                        target_column=target_column,
                        numeric_columns=valid_base_columns,
                        group_by_columns=grouping_cols,
                        lag_periods=[7, 30]
                    )
                    
                    # DataFrame을 다시 List[Dict]로 변환
                    data = processed_df.to_dict('records')
                    print(f"✅ Lag 피처 생성 완료: {len(lag_feature_columns)}개 컬럼")
                except Exception as e:
                    print(f"⚠️ Lag 피처 생성 실패: {str(e)}, 기존 데이터 사용")
        
        # 4. 상관계수 계산 (전체 + 그룹별)
        # 4-1. 전체 상관계수 (그룹화 없이) - valid_columns만 사용 (그룹화 컬럼 제외)
        overall_correlations = await self._calculate_correlations(
            data, target_column, features, None
        )
        
        # 4-2. 그룹별 상관계수 계산
        group_correlations_dict = {}
        if group_by_columns:
            df_check = pd.DataFrame(data)
            for group_col in group_by_columns:
                if group_col in df_check.columns:
                    print(f"📊 그룹별 상관계수 계산 시작: '{group_col}'")
                    group_corr = await self._calculate_correlations_by_group(
                        data, target_column, features, group_col
                    )
                    if group_corr:
                        group_correlations_dict[f"by_{group_col}"] = group_corr
        
        # 전체 상관계수를 기본값으로 사용 (하위 호환성)
        correlations = overall_correlations
        
        # 5. 가중치 계산
        start_time = time.time()
        weights = self.weight_calculator.calculate(correlations)
        
        # 6. 시각화 생성
        chart = await self._create_chart(correlations, target_column)
        
        processing_time = time.time() - start_time
        
        # 7. Feature Weights 저장
        await self.weight_repository.save_weights(
            file_id=file_id,
            user_id=user_id,
            weights=weights
        )
        
        # 8. Analysis Results 저장
        analysis_result = await self.analysis_repository.save_analysis_result(
            file_id=file_id,
            user_id=user_id,
            analysis_type='correlation',
            metrics={},  # 상관관계 분석은 별도 메트릭 없음
            feature_count=len(features),
            target_column=target_column,
            group_by=[],
            processing_time_seconds=processing_time,
            result={
                'correlation_matrix': correlations,
                'chart': chart
            }
        )
        
        # 9. 기존 방식 호환성을 위한 저장 (선택적)
        result = await self.repository.save(
            file_id=file_id,
            user_id=user_id,
            target_column=target_column,
            correlations=correlations,
            weights=weights,
            chart=chart
        )
        
        # 상관관계 행렬 구성 (전체 + 그룹별)
        correlation_matrix = {
            'overall': correlations,  # 전체 상관계수
            **group_correlations_dict  # 그룹별 상관계수 (예: {"by_상품_ID": {...}, "by_브랜드": {...}})
        }
        
        return CorrelationAnalysisResponse(
            correlation_matrix=correlation_matrix,
            top_correlations=self._get_top_correlations(correlations),
            chart=chart,
            weights=weights,
            correlation_id=result['correlation_id'],
            created_at=result['created_at']
        )
    
    async def get_correlations(self, file_id: str) -> Optional[CorrelationAnalysisResponse]:
        """저장된 상관관계 분석 결과 조회"""
        result = await self.repository.get_by_file_id(file_id)
        if not result:
            return None
        
        # correlation_matrix가 이미 딕셔너리인 경우와 문자열 키인 경우 처리
        correlation_matrix = result.get('correlation_matrix', {})
        if isinstance(correlation_matrix, dict) and 'overall' in correlation_matrix:
            # 이미 올바른 형식
            matrix = correlation_matrix
        else:
            # 기존 형식: target_column을 키로 사용
            matrix = {'overall': correlation_matrix}
        
        return CorrelationAnalysisResponse(
            correlation_matrix=matrix,
            top_correlations=self._get_top_correlations(matrix.get('overall', {})),
            chart=result.get('chart', ''),
            weights=result.get('weights', {}),
            correlation_id=result.get('correlation_id', ''),
            created_at=result.get('created_at', datetime.now())
        )
    
    async def _load_data(self, file_id: str) -> List[dict]:
        """MongoDB에서 데이터 로드"""
        data = await self.file_repository.get_csv_data(file_id, 0, 10000)
        # CSV Collection에서 가져온 데이터는 data 필드 안에 있음
        if data and 'data' in data[0]:
            # data 필드를 펼쳐서 사용
            return [row['data'] for row in data]
        return data
    
    def _detect_group_column(self, data: List[dict], target_column: str, features: List[str]) -> Optional[str]:
        """제품별 그룹화 컬럼 자동 감지 (상품_ID, 상품명 등)"""
        if not data:
            return None
        
        df = pd.DataFrame(data)
        # 제품 식별 가능한 컬럼 키워드
        group_keywords = ['상품', '제품', 'product', 'item', 'id', 'ID', '명']
        
        # 타겟 컬럼과 features가 아닌 컬럼 중에서 그룹화 컬럼 찾기
        all_columns = set(df.columns)
        exclude_columns = {target_column} | set(features)
        candidate_columns = all_columns - exclude_columns
        
        for col in candidate_columns:
            col_lower = col.lower()
            # 키워드 매칭
            if any(keyword in col_lower for keyword in group_keywords):
                # 고유 값이 여러 개인지 확인 (그룹화 가능)
                unique_count = df[col].nunique()
                total_count = len(df)
                # 고유 값이 많지만 전체의 일부인 경우 그룹화 컬럼일 가능성
                if 1 < unique_count < total_count * 0.5:  # 전체의 50% 미만이면 그룹화 컬럼일 가능성
                    print(f"📊 제품별 그룹화 컬럼 자동 감지: '{col}' ({unique_count}개 고유 값)")
                    return col
        
        return None
    
    async def _calculate_correlations(
        self, 
        data: List[dict], 
        target: str, 
        features: List[str],
        group_by_column: Optional[str] = None
    ) -> Dict[str, float]:
        """상관계수 계산 (object 타입 지원: 원핫 인코딩, 날짜는 그룹별 인덱스)
        
        Args:
            data: 분석할 데이터
            target: 타겟 컬럼명
            features: 피처 컬럼 목록
            group_by_column: 그룹화할 컬럼명 (예: 상품_ID, 상품명). 있으면 날짜를 그룹별 인덱스로 변환
        """
        df = pd.DataFrame(data)
        correlations = {}
        
        if target not in df.columns:
            raise ValueError(f"타겟 컬럼 {target}을 찾을 수 없습니다")
        
        # 그룹화 기준 컬럼 확인
        group_by_series = None
        if group_by_column and group_by_column in df.columns:
            group_by_series = df[group_by_column]
            print(f"📊 그룹화 기준: '{group_by_column}' - 날짜를 그룹별 인덱스로 변환합니다")
        
        # 타겟 컬럼 전처리
        target_series = self._preprocess_column(df[target], group_by_series)
        
        for feature in features:
            if feature not in df.columns:
                continue
            
            try:
                # 피처 컬럼 전처리 (같은 그룹화 기준 사용)
                feature_series = self._preprocess_column(df[feature], group_by_series)
                
                # 상관계수 계산
                if pd.api.types.is_numeric_dtype(target_series) and pd.api.types.is_numeric_dtype(feature_series):
                    # 둘 다 숫자형: 정규화 후 피어슨 상관계수
                    # NaN 값 제거
                    valid_mask = ~(target_series.isna() | feature_series.isna())
                    if valid_mask.sum() < 2:  # 최소 2개 이상의 유효한 데이터 필요
                        continue
                    
                    target_valid = target_series[valid_mask]
                    feature_valid = feature_series[valid_mask]
                    
                    # 정규화 (StandardScaler: 평균 0, 표준편차 1)
                    scaler = StandardScaler()
                    # 2D 배열로 변환 (sklearn 요구사항)
                    target_normalized = scaler.fit_transform(target_valid.values.reshape(-1, 1)).flatten()
                    feature_normalized = scaler.fit_transform(feature_valid.values.reshape(-1, 1)).flatten()
                    
                    # 정규화된 데이터로 상관계수 계산
                    corr = np.corrcoef(target_normalized, feature_normalized)[0, 1]
                elif pd.api.types.is_numeric_dtype(target_series) or pd.api.types.is_numeric_dtype(feature_series):
                    # 하나는 숫자형, 하나는 범주형: 원핫 인코딩 후 상관계수
                    corr = self._calculate_categorical_correlation(target_series, feature_series)
                else:
                    # 둘 다 범주형: Cramér's V (또는 원핫 인코딩 후 상관계수)
                    corr = self._calculate_categorical_correlation(target_series, feature_series)
                
                if not np.isnan(corr) and not pd.isna(corr):
                    correlations[feature] = float(corr)
            except Exception as e:
                # 상관계수 계산 실패 시 해당 피처는 제외
                print(f"⚠️ 피처 '{feature}'의 상관계수 계산 실패: {str(e)}")
                continue
        
        return correlations
    
    async def _calculate_correlations_by_group(
        self,
        data: List[dict],
        target: str,
        features: List[str],
        group_by_column: str
    ) -> Dict[str, Dict[str, float]]:
        """그룹별 상관계수 계산
        
        Args:
            data: 분석할 데이터
            target: 타겟 컬럼명
            features: 피처 컬럼 목록
            group_by_column: 그룹화할 컬럼명
        
        Returns:
            {group_value: {feature: correlation}} 형식의 딕셔너리
        """
        df = pd.DataFrame(data)
        
        if group_by_column not in df.columns:
            return {}
        
        group_correlations = {}
        group_values = df[group_by_column].unique()
        
        for group_value in group_values:
            group_df = df[df[group_by_column] == group_value]
            if len(group_df) < 3:  # 데이터가 너무 적으면 스킵
                continue
            
            group_corr = {}
            target_series = self._preprocess_column(group_df[target], None)
            
            for feature in features:
                if feature not in group_df.columns:
                    continue
                
                try:
                    feature_series = self._preprocess_column(group_df[feature], None)
                    
                    if pd.api.types.is_numeric_dtype(target_series) and pd.api.types.is_numeric_dtype(feature_series):
                        # 정규화 후 피어슨 상관계수
                        valid_mask = ~(target_series.isna() | feature_series.isna())
                        if valid_mask.sum() < 2:
                            continue
                        
                        target_valid = target_series[valid_mask]
                        feature_valid = feature_series[valid_mask]
                        
                        # 정규화 (StandardScaler: 평균 0, 표준편차 1)
                        scaler = StandardScaler()
                        target_normalized = scaler.fit_transform(target_valid.values.reshape(-1, 1)).flatten()
                        feature_normalized = scaler.fit_transform(feature_valid.values.reshape(-1, 1)).flatten()
                        
                        # 정규화된 데이터로 상관계수 계산
                        corr = np.corrcoef(target_normalized, feature_normalized)[0, 1]
                    else:
                        corr = self._calculate_categorical_correlation(target_series, feature_series)
                    
                    if not np.isnan(corr) and not pd.isna(corr):
                        group_corr[feature] = float(corr)
                except Exception as e:
                    continue
            
            if group_corr:
                group_correlations[str(group_value)] = group_corr
        
        return group_correlations
    
    def _preprocess_column(self, series: pd.Series, group_by: Optional[pd.Series] = None) -> pd.Series:
        """컬럼 전처리: 문자열을 숫자로 변환, 날짜는 타임스탬프 또는 그룹별 인덱스로 변환
        
        Args:
            series: 전처리할 컬럼 데이터
            group_by: 그룹화할 기준 컬럼 (예: 상품_ID, 상품명 등). 있으면 그룹별로 날짜 인덱스 부여
        """
        # 날짜 타입인지 먼저 확인 (datetime)
        if pd.api.types.is_datetime64_any_dtype(series):
            if group_by is not None:
                # 그룹별로 날짜를 순서 인덱스로 변환 (제품별로 독립적인 인덱스)
                result = pd.Series(index=series.index, dtype=float)
                for group_value in group_by.unique():
                    mask = group_by == group_value
                    group_dates = series[mask].sort_values()
                    date_to_index = {date: idx for idx, date in enumerate(group_dates.unique())}
                    result[mask] = series[mask].map(date_to_index)
                return pd.to_numeric(result, errors='coerce')
            else:
                # 그룹화 기준이 없으면 타임스탬프로 변환 (절대 시간 유지)
                # 또는 전체 순서 인덱스로 변환 (시간 추세는 유지하되 제품별 구분 없음)
                return pd.to_numeric(series, errors='coerce')
        
        # 숫자형이면 그대로 반환
        if pd.api.types.is_numeric_dtype(series):
            return pd.to_numeric(series, errors='coerce')
        
        # 문자열/object 타입 처리
        try:
            # 숫자로 변환 가능한 문자열이면 변환 시도 (예: "배송_지연시간" = "30", "45" 등)
            numeric_series = pd.to_numeric(series, errors='coerce')
            if numeric_series.notna().sum() > len(series) * 0.8:  # 80% 이상이 숫자면 숫자형으로 사용
                return numeric_series
        except:
            pass
        
        # 범주형: 라벨 인코딩
        le = LabelEncoder()
        encoded = le.fit_transform(series.astype(str).fillna(''))
        return pd.Series(encoded, index=series.index)
    
    def _calculate_categorical_correlation(self, series1: pd.Series, series2: pd.Series) -> float:
        """범주형 변수 간 상관계수 계산 (원핫 인코딩 또는 라벨 인코딩 사용)"""
        
        # 하나는 숫자형, 하나는 범주형인 경우
        if pd.api.types.is_numeric_dtype(series1) and not pd.api.types.is_numeric_dtype(series2):
            # 범주형을 원핫 인코딩 후 각 더미 변수와의 상관계수 중 최대값 사용
            dummies = pd.get_dummies(series2, prefix='cat')
            if dummies.empty:
                return 0.0
            # 각 더미 변수와의 상관계수 중 절댓값이 가장 큰 값
            correlations = [abs(series1.corr(dummies[col])) for col in dummies.columns]
            return max(correlations) if correlations else 0.0
        
        elif not pd.api.types.is_numeric_dtype(series1) and pd.api.types.is_numeric_dtype(series2):
            # 동일하게 처리
            dummies = pd.get_dummies(series1, prefix='cat')
            if dummies.empty:
                return 0.0
            correlations = [abs(series2.corr(dummies[col])) for col in dummies.columns]
            return max(correlations) if correlations else 0.0
        
        else:
            # 둘 다 범주형: Cramér's V 또는 원핫 인코딩 후 상관계수
            try:
                # 교차표 생성
                contingency = pd.crosstab(series1, series2)
                # 카이제곱 검정
                chi2, _, _, _ = chi2_contingency(contingency)
                n = contingency.sum().sum()
                # Cramér's V 계산
                cramers_v = np.sqrt(chi2 / (n * (min(contingency.shape) - 1)))
                return float(cramers_v)
            except:
                # 실패 시 라벨 인코딩 후 피어슨 상관계수
                le1 = LabelEncoder()
                le2 = LabelEncoder()
                encoded1 = pd.Series(le1.fit_transform(series1.astype(str).fillna('')), index=series1.index)
                encoded2 = pd.Series(le2.fit_transform(series2.astype(str).fillna('')), index=series2.index)
                corr = encoded1.corr(encoded2)
                return corr if not pd.isna(corr) else 0.0
    
    async def _create_chart(self, correlations: Dict, target: str) -> str:
        """차트 생성"""
        import plotly.graph_objects as go
        import base64
        
        features = list(correlations.keys())
        values = list(correlations.values())
        
        fig = go.Figure(data=[
            go.Bar(x=features, y=values, marker_color='lightblue')
        ])
        fig.update_layout(
            title=f"{target}과의 상관관계",
            xaxis_title="피처",
            yaxis_title="상관계수"
        )
        
        img_bytes = fig.to_image(format="png")
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
        return img_base64
    
    def _get_top_correlations(self, correlations: Dict, top_n: int = 5) -> List[TopCorrelationItem]:
        """상위 상관관계 추출"""
        sorted_items = sorted(correlations.items(), key=lambda x: abs(x[1]), reverse=True)
        return [
            TopCorrelationItem(feature=k, correlation=float(v))
            for k, v in sorted_items[:top_n]
        ]

