from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

class FileUploadResponse(BaseModel):
    """파일 업로드 응답"""
    file_id: str
    filename: str
    file_size: int
    columns: List[str]
    row_count: int
    uploaded_at: datetime
    matched_quantity_column: Optional[str] = Field(None, description="자동 매칭된 수량 컬럼명")
    matched_price_column: Optional[str] = Field(None, description="자동 매칭된 금액 컬럼명")
    date_column: Optional[str] = Field(None, description="자동 감지된 날짜 컬럼명")
    target_column: Optional[str] = Field(None, description="예측 대상 컬럼명")
    grouping_columns: Optional[List[str]] = Field(None, description="그룹화 전용 컬럼 목록")
    directly_related_columns: Optional[List[str]] = Field(None, description="직접 연관 컬럼 목록 (제외된 컬럼)")
    valid_columns: Optional[List[str]] = Field(None, description="유효 컬럼 목록 (예측/상관관계 분석용)")
    related_columns: Optional[List[str]] = Field(None, description="관련 컬럼 목록 (valid_columns + grouping_columns)")
    final_columns: Optional[List[str]] = Field(None, description="최종 컬럼 목록 (target_column + valid_columns)")
    lag_feature_columns: Optional[List[str]] = Field(None, description="생성된 Lag 피처 컬럼 목록")

class FileInfoResponse(BaseModel):
    """파일 정보 응답"""
    file_id: str
    filename: str
    file_size: int
    columns: List[str]
    row_count: int
    uploaded_at: datetime
    user_id: str
    matched_quantity_column: Optional[str] = Field(None, description="자동 매칭된 수량 컬럼명")
    matched_price_column: Optional[str] = Field(None, description="자동 매칭된 금액 컬럼명")
    target_column: Optional[str] = Field(None, description="예측 대상 컬럼명 (파일 업로드 시 지정)")

class FileListResponse(BaseModel):
    """파일 목록 응답"""
    files: List[FileInfoResponse]
    total: int

class CSVDataRequest(BaseModel):
    """CSV 데이터 조회 요청"""
    file_id: str
    page: int = Field(1, ge=1, description="페이지 번호")
    page_size: int = Field(100, ge=1, le=1000, description="페이지 크기")

class CSVDataResponse(BaseModel):
    """CSV 데이터 응답"""
    file_id: str
    data: List[Dict]
    total_rows: int
    page: int
    page_size: int

class ColumnAnalysisResponse(BaseModel):
    """컬럼 분석 응답"""
    file_id: str
    columns: List[Dict[str, str]] = Field(..., description="컬럼명과 타입 정보 [{\"name\": \"컬럼명\", \"type\": \"price|quantity|date|category|other\"}]")
    price_column: Optional[str] = Field(None, description="가격 컬럼명 (있을 경우)")
    quantity_column: Optional[str] = Field(None, description="수량 컬럼명 (있을 경우)")
    feature_columns: List[str] = Field(..., description="상관관계 분석에 사용할 피처 컬럼 목록 (가격/수량 제외)")

class RelatedColumnsResponse(BaseModel):
    """관련 컬럼 추천 응답"""
    file_id: str
    target_column: str
    grouping_columns: List[str] = Field(..., description="그룹화 전용 컬럼 목록 (브랜드, 카테고리, 상품_ID, 상품명 등 - 그룹화/집계용)")
    valid_columns: List[str] = Field(..., description="유효 컬럼 목록 (예측/상관관계 분석에 사용할 컬럼, Lag 피처 포함)")
    related_columns: List[str] = Field(..., description="관련 컬럼 목록 (valid_columns + grouping_columns, 하위 호환성용)")
    excluded_columns: List[str] = Field(..., description="제외된 컬럼 목록 (직접적인 관계라서 제외 - 예: 금액)")
    final_columns: List[str] = Field(..., description="최종 컬럼 목록 (target_column + valid_columns)")
    reason: str = Field(..., description="추천 이유 및 제외 이유")

class ColumnsResponse(BaseModel):
    """컬럼 목록 응답"""
    file_id: str
    columns: List[str] = Field(..., description="컬럼 이름 목록")