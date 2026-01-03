from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Literal
from datetime import datetime
from app.utils.constants import CHART_TYPES

class VisualizationRequest(BaseModel):
    """시각화 생성 요청"""
    file_id: str = Field(..., description="시각화할 파일 ID (파일 정보 조회 API로 컬럼 목록 확인 가능)")
    chart_type: Literal["line", "bar", "scatter", "heatmap", "pie", "area"] = Field(
        ..., 
        description="차트 타입. 가능한 값: line, bar, scatter, heatmap, pie, area"
    )
    target_column: Optional[str] = Field(
        None, 
        description="시각화하고 싶은 주요 컬럼명 (예: '판매량', '매출'). 지정하면 LLM이 자동으로 적절한 x_column, y_column을 추천합니다."
    )
    x_column: Optional[str] = Field(None, description="X축에 사용할 컬럼명 (target_column이 없을 때 필수. 파일 정보 조회 시 받은 columns 목록에서 선택)")
    y_column: Optional[str] = Field(None, description="Y축에 사용할 컬럼명 (target_column이 없을 때 필수. 파일 정보 조회 시 받은 columns 목록에서 선택)")
    columns: Optional[List[str]] = Field(None, description="다중 컬럼 차트에 사용할 컬럼명 리스트 (heatmap 등에 사용)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "file_id": "file_123456",
                "chart_type": "line",
                "x_column": "날짜",
                "y_column": "판매량",
                "columns": None
            },
            "description": "컬럼명은 `/api/v1/files/{file_id}` 엔드포인트로 파일 정보를 조회한 후, 반환된 `columns` 배열에서 선택해야 합니다."
        }

class VisualizationResponse(BaseModel):
    """시각화 응답"""
    visualization_id: str
    file_id: str
    chart_type: str
    chart_data: str = Field(..., description="차트 데이터 (JSON 또는 Base64 이미지)")
    created_at: datetime

class ProductListResponse(BaseModel):
    """상품명 목록 응답"""
    file_id: str
    products: List[str]
    count: int

class VisualizationDetailResponse(BaseModel):
    """시각화 상세 응답 (추가 정보 포함)"""
    visualization_id: str
    file_id: str
    chart_type: str
    chart_data: str = Field(..., description="차트 데이터 (Base64 이미지)")
    description: Optional[str] = None
    product_name: Optional[str] = None
    created_at: datetime

