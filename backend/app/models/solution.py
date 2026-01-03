from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class SolutionRequest(BaseModel):
    """솔루션 생성 요청"""
    file_id: str = Field(..., description="파일 ID")
    correlation_id: Optional[str] = Field(None, description="상관관계 분석 ID")
    prediction_id: Optional[str] = Field(None, description="예측 분석 ID")
    question: Optional[str] = Field(None, description="추가 질문")

class SolutionResponse(BaseModel):
    """솔루션 응답"""
    solution_id: str
    file_id: str
    insights: List[str] = Field(..., description="인사이트 리스트")
    recommendations: List[str] = Field(..., description="추천사항 리스트")
    generated_text: str = Field(..., description="생성된 텍스트")
    created_at: datetime

