from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class BaseResponse(BaseModel):
    """기본 응답 모델"""
    success: bool = True
    message: Optional[str] = None

class TimestampMixin(BaseModel):
    """타임스탬프 믹스인"""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

