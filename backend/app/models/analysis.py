from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime

class AnalysisStartRequest(BaseModel):
    """분석 시작 요청"""
    file_id: str = Field(..., description="파일 ID (파일 업로드 시 지정한 target_column이 자동으로 사용됩니다)")

class AnalysisStartResponse(BaseModel):
    """분석 시작 응답"""
    task_id: str = Field(..., description="작업 ID")
    status: str = Field(..., description="작업 상태 (pending, processing, completed, failed)")
    message: str = Field(..., description="메시지")

class TaskStatusResponse(BaseModel):
    """작업 상태 응답"""
    task_id: str
    file_id: str
    target_column: str
    status: str  # pending, processing, completed, failed
    current_step: Optional[str] = None
    steps: Dict[str, Dict] = Field(..., description="각 단계별 상태 및 결과")
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class TaskResultResponse(BaseModel):
    """작업 결과 응답"""
    task_id: str
    status: str
    statistics: Optional[Dict] = None
    visualizations: Optional[Dict] = None
    correlation: Optional[Dict] = None
    prediction: Optional[Dict] = None
    solution: Optional[Dict] = None

