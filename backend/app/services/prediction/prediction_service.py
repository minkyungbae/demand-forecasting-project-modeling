from typing import Optional, List
from datetime import datetime, timedelta
from app.models.prediction import PredictionResponse
from app.services.prediction.model_trainer import ModelTrainer
from app.services.prediction.forecast_generator import ForecastGenerator
from app.services.file.file_repository import FileRepository
from app.services.file.file_analysis_config_repository import FileAnalysisConfigRepository
from app.core.database import get_database

class PredictionService:
    """예측 서비스"""
    
    def __init__(self):
        self.model_trainer = ModelTrainer()
        self.forecast_generator = ForecastGenerator()
        self.file_repository = FileRepository()
        self.config_repository = FileAnalysisConfigRepository()
    
    async def create_prediction(
        self,
        file_id: str,
        features: List[str],
        model_type: str,
        forecast_periods: int,
        user_id: str
    ) -> PredictionResponse:
        """예측 생성"""
        # 파일 소유권 확인 및 target_column 가져오기
        file_info = await self.file_repository.get_sales_info(file_id, user_id)
        if not file_info:
            raise ValueError("파일을 찾을 수 없습니다")
        
        target_column = file_info.get('target_column')
        if not target_column:
            raise ValueError("파일 업로드 시 target_column을 지정하지 않았습니다. 파일을 다시 업로드하거나 target_column을 지정해주세요.")
        
        # 데이터 로드
        raw_data = await self.file_repository.get_csv_data(file_id, 0, 10000)
        # CSV Collection에서 가져온 데이터는 data 필드 안에 있을 수 있음
        if raw_data and len(raw_data) > 0 and 'data' in raw_data[0]:
            data = [row['data'] for row in raw_data]
        else:
            data = raw_data
        
        # Lag 피처 생성 (필요시)
        config = await self.config_repository.get_config(file_id, target_column)
        date_column = config.get('date_column') if config else None
        lag_feature_columns = config.get('lag_feature_columns', []) if config else []
        valid_columns = config.get('valid_columns', []) if config else []
        grouping_columns = config.get('grouping_columns', []) if config else []
        
        # Lag 피처가 필요한데 데이터에 없으면 실시간 생성
        if lag_feature_columns and date_column and data:
            from app.services.feature.lag_feature_generator import LagFeatureGenerator
            lag_generator = LagFeatureGenerator()
            
            # Lag 피처가 데이터에 있는지 확인
            sample_row = data[0] if data else {}
            needs_lag_generation = any(lag_col not in sample_row for lag_col in lag_feature_columns[:3])
            
            if needs_lag_generation:
                print(f"📊 예측 모델링: Lag 피처 실시간 생성 중...")
                try:
                    # Lag 피처 생성에 필요한 정보
                    valid_base_columns = [col for col in valid_columns if not any(lag_col in col for lag_col in ['_lag_7d', '_lag_14d', '_lag_30d'])]
                    
                    processed_df, _ = await lag_generator.generate_lag_features(
                        data=data,
                        date_column=date_column,
                        target_column=target_column,
                        numeric_columns=valid_base_columns,
                        group_by_columns=grouping_columns,
                        lag_periods=[7, 30]
                    )
                    
                    # DataFrame을 다시 List[Dict]로 변환
                    data = processed_df.to_dict('records')
                    print(f"✅ Lag 피처 생성 완료: {len(lag_feature_columns)}개 컬럼")
                except Exception as e:
                    print(f"⚠️ Lag 피처 생성 실패: {str(e)}, 기존 데이터 사용")
                    import traceback
                    print(traceback.format_exc())
        
        # valid_columns가 있으면 features 업데이트
        if valid_columns and len(valid_columns) > 0:
            # grouping_columns 제외한 순수 피처만 사용
            features_for_prediction = [col for col in valid_columns if col not in (grouping_columns or [])]
            if features_for_prediction:
                features = features_for_prediction
                print(f"✅ 예측 모델링: valid_columns 사용 ({len(features)}개 피처)")
        
        # 모델 학습
        model, metrics = await self.model_trainer.train_model(
            data=data,
            target_column=target_column,
            features=features,
            model_type=model_type
        )
        
        # 예측 생성
        forecast_data = await self.forecast_generator.generate_forecast(
            model=model,
            data=data,
            target_column=target_column,
            features=features,
            periods=forecast_periods
        )
        
        # 차트 생성
        chart = await self._create_chart(data, forecast_data, target_column)
        
        # 결과 저장
        prediction_id = f"pred_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        await self._save_prediction(
            prediction_id=prediction_id,
            file_id=file_id,
            target_column=target_column,
            forecast_data=forecast_data,
            model_metrics=metrics,
            chart=chart,
            user_id=user_id
        )
        
        return PredictionResponse(
            prediction_id=prediction_id,
            file_id=file_id,
            target_column=target_column,
            forecast_data=forecast_data,
            model_metrics=metrics,
            chart=chart,
            created_at=datetime.now()
        )
    
    async def get_prediction(self, prediction_id: str) -> Optional[PredictionResponse]:
        """예측 결과 조회"""
        db = await get_database()
        collection = db['predictions']
        pred = await collection.find_one({'prediction_id': prediction_id})
        
        if pred:
            pred.pop('_id', None)
            return PredictionResponse(**pred)
        return None
    
    async def _create_chart(self, data: List[dict], forecast_data: List[dict], target_column: str) -> str:
        """예측 차트 생성"""
        import plotly.graph_objects as go
        import base64
        
        # 실제 데이터
        actual_values = [d[target_column] for d in data if target_column in d]
        actual_dates = list(range(len(actual_values)))
        
        # 예측 데이터
        forecast_values = [d['forecast'] for d in forecast_data]
        forecast_dates = list(range(len(actual_values), len(actual_values) + len(forecast_values)))
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=actual_dates, y=actual_values, name='실제값', mode='lines'))
        fig.add_trace(go.Scatter(x=forecast_dates, y=forecast_values, name='예측값', mode='lines', line=dict(dash='dash')))
        
        fig.update_layout(
            title=f"{target_column} 예측",
            xaxis_title="기간",
            yaxis_title="값"
        )
        
        img_bytes = fig.to_image(format="png")
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
        return img_base64
    
    async def _save_prediction(
        self,
        prediction_id: str,
        file_id: str,
        target_column: str,
        forecast_data: List[dict],
        model_metrics: dict,
        chart: str,
        user_id: str
    ):
        """예측 결과 저장"""
        db = await get_database()
        collection = db['predictions']
        await collection.insert_one({
            'prediction_id': prediction_id,
            'file_id': file_id,
            'target_column': target_column,
            'forecast_data': forecast_data,
            'model_metrics': model_metrics,
            'chart': chart,
            'user_id': user_id,
            'created_at': datetime.now()
        })

