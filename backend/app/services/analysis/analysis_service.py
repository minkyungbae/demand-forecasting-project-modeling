from typing import Dict, Optional, List, Set
from datetime import datetime
from fastapi import BackgroundTasks
from app.core.database import get_database
from app.services.analysis.task_repository import TaskRepository
from app.services.analysis.statistics_service import StatisticsService
from app.services.file.file_service import FileService
from app.services.file.file_analysis_config_repository import FileAnalysisConfigRepository
from app.services.correlation.correlation_service import CorrelationService
from app.services.prediction.prediction_service import PredictionService
from app.services.solution.solution_service import SolutionService
from app.services.visualization.visualization_service import VisualizationService
import pandas as pd
import plotly.graph_objects as go
import base64
import asyncio
import weakref

class AnalysisService:
    """전체 분석 작업 서비스 (백그라운드 자동 처리)"""
    
    # 실행 중인 태스크 추적 (weakref로 메모리 누수 방지)
    _running_tasks: Set[asyncio.Task] = set()
    
    @classmethod
    def _register_task(cls, task: asyncio.Task):
        """실행 중인 태스크 등록"""
        cls._running_tasks.add(task)
        
        # 태스크 완료 시 자동으로 제거 (콜백 추가)
        def remove_task(t):
            cls._running_tasks.discard(t)
        task.add_done_callback(remove_task)
    
    @classmethod
    def get_running_tasks_info(cls) -> Dict:
        """실행 중인 태스크 정보 조회"""
        tasks_info = []
        for task in cls._running_tasks.copy():  # 복사본으로 순회 (안전)
            try:
                task_info = {
                    'task_name': task.get_name(),
                    'done': task.done(),
                    'cancelled': task.cancelled(),
                }
                if task.done():
                    try:
                        task_info['result'] = 'completed'
                        if task.exception():
                            task_info['exception'] = str(task.exception())
                    except:
                        pass
                tasks_info.append(task_info)
            except:
                pass
        
        return {
            'total_tasks': len(cls._running_tasks),
            'tasks': tasks_info
        }
    
    @classmethod
    def cancel_all_tasks(cls) -> Dict:
        """모든 실행 중인 태스크 취소"""
        cancelled_count = 0
        for task in cls._running_tasks.copy():
            if not task.done():
                task.cancel()
                cancelled_count += 1
        
        return {
            'cancelled_count': cancelled_count,
            'message': f'{cancelled_count}개의 태스크를 취소했습니다'
        }
    
    @classmethod
    async def cleanup_completed_tasks(cls):
        """완료된 태스크 정리"""
        initial_count = len(cls._running_tasks)
        cls._running_tasks = {t for t in cls._running_tasks if not t.done()}
        removed_count = initial_count - len(cls._running_tasks)
        
        return {
            'removed_count': removed_count,
            'remaining_tasks': len(cls._running_tasks)
        }
    
    def __init__(self):
        self.task_repository = TaskRepository()
        self.file_service = FileService()
        self.config_repository = FileAnalysisConfigRepository()
        self.statistics_service = StatisticsService()
        self.correlation_service = CorrelationService()
        self.prediction_service = PredictionService()
        self.solution_service = SolutionService()
        self.visualization_service = VisualizationService()
    
    async def start_analysis(
        self,
        file_id: str,
        user_id: str,
        background_tasks: BackgroundTasks
    ) -> Dict:
        """분석 작업 시작 (백그라운드)"""
        # 파일 정보에서 target_column 가져오기
        file_info = await self.file_service.repository.get_sales_info(file_id, user_id)
        if not file_info:
            raise ValueError("파일을 찾을 수 없습니다")
        
        target_column = file_info.get('target_column')
        if not target_column:
            raise ValueError("파일 업로드 시 target_column을 지정하지 않았습니다. 파일을 다시 업로드하거나 target_column을 지정해주세요.")
        
        # 작업 생성
        task = await self.task_repository.create_task(
            file_id=file_id,
            user_id=user_id,
            target_column=target_column
        )
        
        return {
            'task_id': task['task_id'],
            'status': task['status'],
            'message': '분석 작업이 시작되었습니다'
        }
    
    async def _run_analysis_pipeline(
        self,
        task_id: str,
        file_id: str,
        user_id: str
    ):
        """전체 분석 파이프라인 실행"""
        try:
            # 파일 정보에서 target_column 가져오기
            file_info = await self.file_service.repository.get_sales_info(file_id, user_id)
            if not file_info:
                raise ValueError("파일을 찾을 수 없습니다")
            
            target_column = file_info.get('target_column')
            if not target_column:
                raise ValueError("파일 업로드 시 target_column을 지정하지 않았습니다.")
            
            # 작업 상태를 processing으로 변경
            await self.task_repository.update_task_status(task_id, 'processing')
            
            # 1. 관련 컬럼 추천 확인 (파일 업로드 시 이미 자동 생성됨)
            await self.task_repository.update_step_status(task_id, 'related_columns', 'processing')
            
            # config에서 valid_columns 사용 (Lag 피처 포함)
            config = await self.config_repository.get_config(file_id, target_column)
            if not config:
                # config가 없으면 자동으로 생성 (파일 업로드 시 생성되지 않은 경우)
                related_columns_result = await self.file_service.suggest_related_columns(
                    file_id=file_id,
                    target_column=target_column,
                    user_id=user_id
                )
                config = await self.config_repository.get_config(file_id, target_column)
            
            await self.task_repository.update_step_status(
                task_id, 'related_columns', 'completed',
                result={'final_columns': config.get('final_columns', []) if config else []}
            )
            valid_columns = config.get('valid_columns', []) if config else []
            grouping_columns = config.get('grouping_columns', []) if config else []
            group_by_column = config.get('group_by_column') if config else None
            date_column = config.get('date_column') if config else None
            
            # features는 valid_columns 사용 (그룹화 컬럼 제외)
            if valid_columns and len(valid_columns) > 0:
                features = [col for col in valid_columns if col not in grouping_columns]
            else:
                # 하위 호환성: valid_columns가 없으면 related_columns 사용
                features = related_columns_result.related_columns
            
            # 2. 통계 분석 (LLM 설명 포함)
            await self.task_repository.update_step_status(task_id, 'statistics', 'processing')
            statistics_result = await self.statistics_service.generate_statistics(
                file_id=file_id,
                user_id=user_id,
                target_column=target_column,
                group_by_column=group_by_column
            )
            # 통계 결과 저장
            db = await get_database()
            stats_collection = db['statistics']
            stats_id = f"stats_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
            await stats_collection.insert_one({
                'statistics_id': stats_id,
                'file_id': file_id,
                'user_id': user_id,
                'target_column': target_column,
                'statistics': statistics_result['statistics'],
                'llm_explanation': statistics_result['llm_explanation'],
                'created_at': datetime.now()
            })
            await self.task_repository.update_step_status(
                task_id, 'statistics', 'completed',
                result={'statistics_id': stats_id}
            )
            
            # 3. 시각화 생성
            await self.task_repository.update_step_status(task_id, 'visualizations', 'processing')
            # config를 다시 조회하여 최신 group_by_column 정보 가져오기
            config = await self.config_repository.get_config(file_id, target_column)
            group_by_column = config.get('group_by_column') if config else None
            visualizations_result = await self._generate_visualizations(
                file_id, user_id, target_column, features, group_by_column, config
            )
            await self.task_repository.update_step_status(
                task_id, 'visualizations', 'completed',
                result=visualizations_result
            )
            
            # 4. 상관관계 분석
            await self.task_repository.update_step_status(task_id, 'correlation', 'processing')
            correlation_result = await self.correlation_service.analyze_correlations(
                file_id=file_id,
                features=features,
                user_id=user_id
            )
            await self.task_repository.update_step_status(
                task_id, 'correlation', 'completed',
                result={'correlation_id': correlation_result.correlation_id}
            )
            
            # 5. 예측 모델링
            await self.task_repository.update_step_status(task_id, 'prediction', 'processing')
            prediction_result = await self.prediction_service.create_prediction(
                file_id=file_id,
                features=features,
                model_type='random_forest',  # 기본값
                forecast_periods=30,  # 기본값
                user_id=user_id
            )
            await self.task_repository.update_step_status(
                task_id, 'prediction', 'completed',
                result={'prediction_id': prediction_result.prediction_id}
            )
            
            # 6. 솔루션 생성
            await self.task_repository.update_step_status(task_id, 'solution', 'processing')
            solution_result = await self.solution_service.generate_solution(
                file_id=file_id,
                correlation_id=correlation_result.correlation_id,
                prediction_id=prediction_result.prediction_id,
                question=None,
                user_id=user_id
            )
            await self.task_repository.update_step_status(
                task_id, 'solution', 'completed',
                result={'solution_id': solution_result.solution_id}
            )
            
            # 전체 작업 완료 상태 업데이트
            await self.task_repository.update_task_status(task_id, 'completed')
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            
            # 현재 단계 확인하여 해당 단계를 failed로 설정
            task = await self.task_repository.get_task(task_id)
            current_step = task.get('current_step', 'solution') if task else 'solution'
            
            # 실패 상태 저장 (DB에 영구 저장됨)
            await self.task_repository.update_step_status(
                task_id, current_step, 'failed',
                error_message=f"{str(e)}\n\n상세:\n{error_trace}"
            )
    
    async def _generate_visualizations(
        self,
        file_id: str,
        user_id: str,
        target_column: str,
        features: list,
        group_by_column: Optional[str],
        config: Optional[Dict]
    ) -> Dict:
        """시각화 생성 (상품별 선그래프, 막대그래프)"""
        visualization_ids = []
        
        # 데이터 로드 (get_csv_data는 이미 data 필드만 반환)
        data = await self.file_service.repository.get_csv_data(file_id, 0, 10000)
        if not data:
            return {'visualization_ids': []}
        
        df = pd.DataFrame(data)
        
        # 그룹화 컬럼이 없으면 자동 감지 (더 강력한 로직)
        if not group_by_column:
            # 먼저 config에서 group_by_columns 목록 확인 (LLM이 추천한 것)
            if config and config.get('group_by_columns'):
                group_by_columns_from_config = config.get('group_by_columns', [])
                for col in group_by_columns_from_config:
                    if col in df.columns:
                        unique_count = df[col].nunique()
                        total_count = len(df)
                        if 1 < unique_count < total_count * 0.5:
                            group_by_column = col
                            break
            
            # 여전히 없으면 키워드 기반 자동 감지
            if not group_by_column:
                group_keywords = [
                    '상품명', '제품명', '상품', '제품', 
                    'product', 'item', 'product_name', 'item_name',
                    'id', 'ID', '명', 'name', '이름'
                ]
                exclude_columns = {target_column} | set(features)
                candidate_columns = list(set(df.columns) - exclude_columns)
                
                # 키워드 매칭 우선순위 적용
                matched_columns = []
                for col in candidate_columns:
                    col_lower = col.lower()
                    for keyword in group_keywords:
                        if keyword in col_lower:
                            unique_count = df[col].nunique()
                            total_count = len(df)
                            if 1 < unique_count < total_count * 0.5:
                                matched_columns.append((col, keyword, unique_count))
                                break
                
                # 매칭된 컬럼이 있으면 정렬하여 선택
                if matched_columns:
                    # 우선순위: 상품명/제품명 > 상품/제품 > product/item > id/ID > 기타
                    priority_keywords = ['상품명', '제품명', 'product_name', 'item_name', '상품', '제품', 'product', 'item']
                    matched_columns.sort(key=lambda x: (
                        priority_keywords.index(x[1]) if x[1] in priority_keywords else 999,
                        -x[2]  # 고유값 개수 역순 (많을수록 좋음)
                    ))
                    group_by_column = matched_columns[0][0]
        
        # 제품별 개수 계산
        product_counts = {}
        if config:
            product_counts = config.get('product_counts', {})
        
        # product_counts가 없고 group_by_column이 있으면 직접 계산
        if not product_counts and group_by_column and group_by_column in df.columns:
            product_counts = df[group_by_column].value_counts().to_dict()
            product_counts = {str(k): int(v) for k, v in product_counts.items()}
        
        if group_by_column and group_by_column in df.columns:
            
            # 1. 상품별 시간별 추세 선그래프 (가장 개수가 많은 상품 10개)
            if product_counts:
                top_products = sorted(product_counts.items(), key=lambda x: x[1], reverse=True)[:10]
                top_product_names = [name for name, _ in top_products]
                
                line_chart_id = await self._create_product_trend_line_chart(
                    df, file_id, user_id, target_column, group_by_column, top_product_names
                )
                if line_chart_id:
                    visualization_ids.append(line_chart_id)
            
            # 2. 상품별 개수 막대그래프
            bar_chart_id = await self._create_product_count_bar_chart(
                df, file_id, user_id, group_by_column, product_counts
            )
            if bar_chart_id:
                visualization_ids.append(bar_chart_id)
        
        return {'visualization_ids': visualization_ids}
    
    async def _create_product_trend_line_chart(
        self,
        df: pd.DataFrame,
        file_id: str,
        user_id: str,
        target_column: str,
        group_by_column: str,
        product_names: List[str]
    ) -> Optional[str]:
        """상품별 시간별 추세 선그래프 생성"""
        try:
            # 날짜 컬럼 찾기
            date_columns = [col for col in df.columns if any(keyword in col.lower() for keyword in ['날짜', 'date', '시간', 'time'])]
            date_column = date_columns[0] if date_columns else None
            
            if not date_column:
                return None
            
            fig = go.Figure()
            
            # 각 상품별로 선 그래프 추가
            for product_name in product_names:
                product_df = df[df[group_by_column] == product_name].copy()
                if len(product_df) == 0:
                    continue
                
                # 날짜 정렬 및 변환
                try:
                    if pd.api.types.is_datetime64_any_dtype(product_df[date_column]):
                        product_df = product_df.sort_values(date_column)
                        dates = product_df[date_column]
                    else:
                        # 문자열 날짜를 datetime으로 변환 시도
                        try:
                            product_df[date_column] = pd.to_datetime(product_df[date_column], errors='coerce')
                            product_df = product_df.sort_values(date_column)
                            dates = product_df[date_column]
                        except:
                            product_df = product_df.sort_values(date_column)
                            dates = product_df[date_column].astype(str)
                except Exception as e:
                    pass  # 날짜 정렬 실패 시 해당 제품 건너뜀
                    continue
                
                values = pd.to_numeric(product_df[target_column], errors='coerce').dropna()
                if len(values) == 0:
                    continue
                
                # 날짜와 값의 길이 맞추기
                dates_clean = dates.iloc[:len(values)]
                
                fig.add_trace(go.Scatter(
                    x=dates_clean,
                    y=values,
                    mode='lines+markers',
                    name=str(product_name),
                    line=dict(width=2)
                ))
            
            fig.update_layout(
                title=f"{target_column} 상품별 시간별 추세 (상위 10개 상품)",
                xaxis_title=date_column,
                yaxis_title=target_column,
                hovermode='closest',
                height=500
            )
            
            # Base64 인코딩
            img_bytes = fig.to_image(format="png")
            img_base64 = base64.b64encode(img_bytes).decode('utf-8')
            
            # 저장
            visualization_id = f"viz_line_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
            db = await get_database()
            collection = db['visualizations']
            await collection.insert_one({
                'visualization_id': visualization_id,
                'file_id': file_id,
                'user_id': user_id,
                'chart_type': 'line',
                'chart_data': img_base64,
                'metadata': {
                    'target_column': target_column,
                    'group_by_column': group_by_column,
                    'products': product_names,
                    'description': '상품별 시간별 추세 선그래프'
                },
                'created_at': datetime.now()
            })
            
            return visualization_id
        except Exception:
            return None
    
    async def _create_product_count_bar_chart(
        self,
        df: pd.DataFrame,
        file_id: str,
        user_id: str,
        group_by_column: str,
        product_counts: Dict[str, int]
    ) -> Optional[str]:
        """상품별 개수 막대그래프 생성"""
        try:
            if not product_counts:
                # product_counts가 없으면 직접 계산
                product_counts = df[group_by_column].value_counts().head(20).to_dict()
                product_counts = {str(k): int(v) for k, v in product_counts.items()}
            
            # 상위 20개만 표시
            sorted_products = sorted(product_counts.items(), key=lambda x: x[1], reverse=True)[:20]
            product_names = [name for name, _ in sorted_products]
            counts = [count for _, count in sorted_products]
            
            fig = go.Figure(data=[
                go.Bar(x=product_names, y=counts, marker_color='lightblue')
            ])
            
            fig.update_layout(
                title="상품별 데이터 개수",
                xaxis_title=group_by_column,
                yaxis_title="개수",
                height=500,
                xaxis_tickangle=-45
            )
            
            # Base64 인코딩
            img_bytes = fig.to_image(format="png")
            img_base64 = base64.b64encode(img_bytes).decode('utf-8')
            
            # 저장
            visualization_id = f"viz_bar_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
            db = await get_database()
            collection = db['visualizations']
            await collection.insert_one({
                'visualization_id': visualization_id,
                'file_id': file_id,
                'user_id': user_id,
                'chart_type': 'bar',
                'chart_data': img_base64,
                'metadata': {
                    'group_by_column': group_by_column,
                    'description': '상품별 개수 막대그래프'
                },
                'created_at': datetime.now()
            })
            
            return visualization_id
        except Exception as e:
            pass
            return None
    
    async def get_task_status(self, task_id: str, user_id: str) -> Optional[Dict]:
        """작업 상태 조회"""
        task = await self.task_repository.get_task(task_id)
        if not task or task['user_id'] != user_id:
            return None
        return task
    
    async def get_task_result(self, task_id: str, user_id: str) -> Optional[Dict]:
        """작업 결과 조회"""
        task = await self.task_repository.get_task(task_id)
        if not task or task['user_id'] != user_id:
            return None
        
        # 결과가 완료된 경우만 상세 결과 조회
        if task['status'] != 'completed':
            return {'status': task['status'], 'message': '작업이 아직 완료되지 않았습니다'}
        
        # 각 단계별 결과 수집
        result = {
            'task_id': task_id,
            'status': task['status'],
            'statistics': task['steps'].get('statistics', {}).get('result'),
            'visualizations': task['steps'].get('visualizations', {}).get('result'),
            'correlation': task['steps'].get('correlation', {}).get('result'),
            'prediction': task['steps'].get('prediction', {}).get('result'),
            'solution': task['steps'].get('solution', {}).get('result')
        }
        
        return result
    
    async def get_task_statistics(self, task_id: str, user_id: str) -> Optional[Dict]:
        """작업의 통계 분석 결과 조회"""
        task = await self.task_repository.get_task(task_id)
        if not task or task['user_id'] != user_id:
            return None
        
        stats_id = task['steps'].get('statistics', {}).get('result', {}).get('statistics_id')
        if not stats_id:
            return None
        
        db = await get_database()
        collection = db['statistics']
        stats = await collection.find_one({'statistics_id': stats_id})
        if stats:
            stats.pop('_id', None)
        return stats
    
    async def get_task_visualizations(self, task_id: str, user_id: str) -> Optional[Dict]:
        """작업의 시각화 결과 조회"""
        task = await self.task_repository.get_task(task_id)
        if not task or task['user_id'] != user_id:
            return None
        
        visualization_ids = task['steps'].get('visualizations', {}).get('result', {}).get('visualization_ids', [])
        if not visualization_ids:
            return {'visualizations': []}
        
        db = await get_database()
        collection = db['visualizations']
        visualizations = []
        for viz_id in visualization_ids:
            viz = await collection.find_one({'visualization_id': viz_id})
            if viz:
                viz.pop('_id', None)
                visualizations.append(viz)
        
        return {'visualizations': visualizations}
    
    async def get_task_correlation(self, task_id: str, user_id: str) -> Optional[Dict]:
        """작업의 상관관계 분석 결과 조회"""
        task = await self.task_repository.get_task(task_id)
        if not task or task['user_id'] != user_id:
            return None
        
        correlation_id = task['steps'].get('correlation', {}).get('result', {}).get('correlation_id')
        if not correlation_id:
            return None
        
        correlation_result = await self.correlation_service.get_correlations(task['file_id'])
        if correlation_result:
            return {
                'correlation_id': correlation_id,
                'correlation_matrix': correlation_result.correlation_matrix,
                'top_correlations': correlation_result.top_correlations,
                'weights': correlation_result.weights,
                'chart': correlation_result.chart
            }
        return None
    
    async def get_task_prediction(self, task_id: str, user_id: str) -> Optional[Dict]:
        """작업의 예측 결과 조회"""
        task = await self.task_repository.get_task(task_id)
        if not task or task['user_id'] != user_id:
            return None
        
        prediction_id = task['steps'].get('prediction', {}).get('result', {}).get('prediction_id')
        if not prediction_id:
            return None
        
        prediction_result = await self.prediction_service.get_prediction(prediction_id)
        if prediction_result:
            return {
                'prediction_id': prediction_result.prediction_id,
                'target_column': prediction_result.target_column,
                'forecast_data': prediction_result.forecast_data,
                'model_metrics': prediction_result.model_metrics,
                'chart': prediction_result.chart
            }
        return None
    
    async def get_task_solution(self, task_id: str, user_id: str) -> Optional[Dict]:
        """작업의 솔루션 결과 조회"""
        task = await self.task_repository.get_task(task_id)
        if not task or task['user_id'] != user_id:
            return None
        
        solution_id = task['steps'].get('solution', {}).get('result', {}).get('solution_id')
        if not solution_id:
            return None
        
        solution_result = await self.solution_service.get_solution(solution_id)
        if solution_result:
            return {
                'solution_id': solution_result.solution_id,
                'insights': solution_result.insights,
                'recommendations': solution_result.recommendations,
                'generated_text': solution_result.generated_text
            }
        return None
    
    async def get_latest_analysis_by_file(self, file_id: str, user_id: str) -> Optional[Dict]:
        """파일의 최신 분석 작업 결과 조회"""
        db = await get_database()
        collection = db['analysis_tasks']
        task = await collection.find_one(
            {'file_id': file_id, 'user_id': user_id, 'status': 'completed'},
            sort=[('created_at', -1)]
        )
        
        if not task:
            return None
        
        task.pop('_id', None)
        task_id = task['task_id']
        
        # 각 단계별 결과 수집
        result = {
            'task_id': task_id,
            'file_id': file_id,
            'target_column': task['target_column'],
            'status': task['status'],
            'statistics': await self.get_task_statistics(task_id, user_id),
            'visualizations': await self.get_task_visualizations(task_id, user_id),
            'correlation': await self.get_task_correlation(task_id, user_id),
            'prediction': await self.get_task_prediction(task_id, user_id),
            'solution': await self.get_task_solution(task_id, user_id)
        }
        
        return result

