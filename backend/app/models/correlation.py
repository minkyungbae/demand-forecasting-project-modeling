from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime

class CorrelationAnalysisRequest(BaseModel):
    """상관관계 분석 요청"""
    file_id: str = Field(..., description="파일 ID (파일 업로드 시 지정한 target_column이 자동으로 사용됩니다)")
    features: Optional[List[str]] = Field(None, description="분석할 피처 리스트. None이면 저장된 valid_columns 자동 사용")
    
    class Config:
        json_schema_extra = {
            "example": {
                "file_id": "file_123456",
                "features": None  # 자동 선택 (저장된 valid_columns 사용)
            },
            "description": "target_column은 파일 업로드 시 지정한 값이 자동으로 사용됩니다. features가 None이면 저장된 valid_columns가 자동으로 사용됩니다."
        }

class TopCorrelationItem(BaseModel):
    """상위 상관관계 항목"""
    feature: str = Field(..., description="피처 컬럼명")
    correlation: float = Field(..., description="상관계수")

class CorrelationAnalysisResponse(BaseModel):
    """상관관계 분석 응답"""
    correlation_matrix: Dict[str, Any] = Field(..., description="상관관계 행렬 (전체 + 그룹별)")
    top_correlations: List[TopCorrelationItem] = Field(..., description="상위 상관관계")
    chart: str = Field(..., description="차트 이미지 (Base64)")
    weights: Dict[str, float] = Field(..., description="피처 가중치")
    correlation_id: Optional[str] = Field(None, description="저장된 분석 ID")
    created_at: Optional[datetime] = None

