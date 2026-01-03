from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import List, Optional
from app.models.file import FileUploadResponse, FileInfoResponse, FileListResponse, CSVDataRequest, CSVDataResponse, ColumnsResponse
from app.services.file.file_service import FileService
from app.dependencies import get_current_user

router = APIRouter()

def get_file_service() -> FileService:
    """파일 서비스 의존성"""
    return FileService()

@router.post("/upload", response_model=FileUploadResponse, status_code=201, summary="CSV 파일 업로드")
async def upload_file(
    file: UploadFile = File(...),
    target_column: Optional[str] = Form(None, description="예측 대상 컬럼명 (선택사항, 나중에 분석 시 사용)"),
    current_user: dict = Depends(get_current_user),
    file_service: FileService = Depends(get_file_service)
):
    """
    CSV 파일 업로드
    
    분석을 위한 CSV 파일을 업로드합니다. 파일은 데이터베이스에 저장되며, 이후 분석 및 예측에 사용할 수 있습니다.
    
    - **파일 형식**: CSV 파일만 업로드 가능
    - **target_column**: (선택사항) 예측 대상 컬럼명. 지정하면 파일 정보와 함께 저장되며, 이후 자동 컬럼 추천 및 예측 피처 생성에 사용됩니다.
    - **저장 위치**: 현재 사용자 계정에 연결되어 저장됨
    - **자동 처리**: 업로드 시 파일 메타데이터(컬럼 정보, 데이터 타입 등)가 자동으로 분석됨
    - **자동 피처 생성**: target_column이 지정되면 자동으로 컬럼 추천 및 예측 피처가 생성됩니다.
    
    업로드 성공 시 파일 ID와 파일 정보가 반환됩니다. 이 파일 ID를 사용하여 이후 분석 작업을 수행할 수 있습니다.
    """
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="CSV 파일만 업로드 가능합니다")
        
        result = await file_service.upload_file(
            file=file,
            user_id=current_user['user_id'],
            target_column=target_column
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=FileListResponse, summary="파일 목록 조회")
async def list_files(
    current_user: dict = Depends(get_current_user),
    file_service: FileService = Depends(get_file_service)
):
    """
    파일 목록 조회
    
    현재 사용자가 업로드한 모든 파일 목록을 조회합니다.
    
    반환 정보:
    - 파일 ID, 파일명, 업로드 시간, 파일 크기, 컬럼 정보 등
    
    인증된 사용자만 자신이 업로드한 파일 목록을 조회할 수 있습니다.
    """
    try:
        files = await file_service.list_files(user_id=current_user['user_id'])
        return FileListResponse(files=files, total=len(files))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{file_id}", response_model=FileInfoResponse, summary="파일 상세 정보 조회")
async def get_file_info(
    file_id: str,
    current_user: dict = Depends(get_current_user),
    file_service: FileService = Depends(get_file_service)
):
    """
    파일 상세 정보 조회
    
    특정 파일의 상세 정보를 조회합니다.
    
    - **file_id**: 조회할 파일의 고유 ID
    
    반환 정보:
    - 파일명, 업로드 시간, 파일 크기, 행 수, 컬럼 목록 및 데이터 타입 등
    
    본인이 업로드한 파일만 조회 가능하며, 존재하지 않는 파일이거나 권한이 없는 경우 404 에러가 반환됩니다.
    """
    try:
        file_info = await file_service.get_file_info(file_id, current_user['user_id'])
        if not file_info:
            raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다")
        return file_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{file_id}/data", response_model=CSVDataResponse, summary="CSV 데이터 조회 (페이지네이션)")
async def get_csv_data(
    file_id: str,
    request: CSVDataRequest,
    current_user: dict = Depends(get_current_user),
    file_service: FileService = Depends(get_file_service)
):
    """
    CSV 데이터 조회 (페이지네이션)
    
    업로드된 CSV 파일의 실제 데이터를 페이지네이션하여 조회합니다.
    
    - **file_id**: 조회할 파일의 고유 ID
    - **page**: 페이지 번호 (기본값: 1)
    - **page_size**: 페이지당 데이터 행 수 (기본값: 100)
    
    대용량 CSV 파일의 경우 모든 데이터를 한 번에 조회하는 것은 비효율적이므로,
    페이지네이션을 통해 필요한 데이터만 조회할 수 있습니다.
    
    반환 정보:
    - 현재 페이지의 데이터 행 목록
    - 전체 데이터 행 수
    - 현재 페이지 번호 및 전체 페이지 수
    """
    try:
        data = await file_service.get_csv_data(
            file_id=file_id,
            page=request.page,
            page_size=request.page_size,
            user_id=current_user['user_id']
        )
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{file_id}/columns", response_model=ColumnsResponse, summary="컬럼 목록 조회")
async def get_columns(
    file_id: str,
    current_user: dict = Depends(get_current_user),
    file_service: FileService = Depends(get_file_service)
):
    """
    컬럼 목록 조회
    
    업로드된 CSV 파일의 컬럼 이름 목록을 조회합니다.
    
    - **file_id**: 조회할 파일의 고유 ID
    
    반환 정보:
    - **columns**: CSV 파일의 컬럼 이름 목록
    
    본인이 업로드한 파일만 조회 가능하며, 존재하지 않는 파일이거나 권한이 없는 경우 404 에러가 반환됩니다.
    """
    try:
        result = await file_service.get_columns(file_id, current_user['user_id'])
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{file_id}", summary="파일 삭제")
async def delete_file(
    file_id: str,
    current_user: dict = Depends(get_current_user),
    file_service: FileService = Depends(get_file_service)
):
    """
    파일 삭제
    
    업로드한 CSV 파일을 삭제합니다.
    
    - **file_id**: 삭제할 파일의 고유 ID
    
    파일 삭제 시 해당 파일과 관련된 모든 데이터(원본 데이터, 분석 결과, 예측 결과 등)도 함께 삭제됩니다.
    본인이 업로드한 파일만 삭제 가능하며, 삭제된 파일은 복구할 수 없습니다.
    
    성공 시 삭제 완료 메시지가 반환됩니다.
    """
    try:
        success = await file_service.delete_file(file_id, current_user['user_id'])
        if not success:
            raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다")
        return {"success": True, "message": "파일이 삭제되었습니다"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

