from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

class PredictionRequest(BaseModel):
    """예측 요청"""
    file_id: str = Field(..., description="파일 ID (파일 업로드 시 지정한 target_column이 자동으로 사용됩니다)")
    features: List[str] = Field(..., description="사용할 피처 리스트")
    model_type: str = Field("linear", description="모델 타입 (linear, random_forest, xgboost)")
    forecast_periods: int = Field(7, ge=1, le=365, description="예측 기간 (일)")

class PredictionResponse(BaseModel):
    """예측 응답"""
    prediction_id: str
    file_id: str
    target_column: str
    forecast_data: List[Dict] = Field(..., description="예측 데이터")
    model_metrics: Dict[str, float] = Field(..., description="모델 성능 지표")
    chart: str = Field(..., description="예측 차트 (Base64)")
    created_at: datetime

