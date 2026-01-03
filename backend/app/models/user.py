from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class UserType(str, Enum):
    """사용자 타입"""
    ADMIN = "admin"
    PREMIUM = "premium"
    BASIC = "basic"

class UserCreate(BaseModel):
    """유저 생성 요청"""
    username: str = Field(..., min_length=1, description="이메일 주소")
    password: str = Field(..., min_length=8, description="비밀번호 (최소 8자)")
    name: str = Field(..., min_length=1, description="이름")
    user_type: Optional[UserType] = Field(UserType.BASIC, description="사용자 타입 (admin, premium, basic). 기본값: basic")

class UserLogin(BaseModel):
    """유저 로그인 요청"""
    username: str = Field(..., description="이메일 주소", examples=["user@example.com"])
    password: str = Field(..., description="비밀번호", examples=["password123"])
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "user@example.com",
                "password": "password123"
            }
        }

class UserResponse(BaseModel):
    """유저 응답"""
    user_id: str
    username: str
    name: str
    user_type: Optional[str] = Field(None, description="사용자 타입 (admin, premium, basic)")
    created_at: Optional[datetime] = None

class TokenResponse(BaseModel):
    """토큰 응답"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

