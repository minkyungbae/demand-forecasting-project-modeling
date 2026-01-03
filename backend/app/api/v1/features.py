from fastapi import APIRouter, Depends, HTTPException, Query
from app.services.file.file_service import FileService
from app.dependencies import get_current_user

router = APIRouter()

def get_file_service() -> FileService:
    """파일 서비스 의존성"""
    return FileService()

@router.get("/{file_id}/preprocess", summary="전처리 데이터 정보 조회")
async def get_preprocessed_info(
    file_id: str,
    current_user: dict = Depends(get_current_user),
    file_service: FileService = Depends(get_file_service)
):
    """
    전처리 데이터 정보 조회
    
    파일 업로드 시 자동으로 생성된 전처리 데이터의 정보(컬럼 목록, 행 수 등)를 조회합니다.
    
    - **file_id**: 파일의 고유 ID (파일 업로드 시 지정한 target_column에 대한 전처리 데이터를 조회합니다)
    
    전처리 데이터가 존재하지 않으면 404 에러가 반환됩니다.
    
    **참고**: 전처리 피처는 파일 업로드 시 `target_column`을 지정하면 자동으로 생성됩니다.
    """
    try:
        # 파일 정보에서 target_column 가져오기
        file_info = await file_service.repository.get_sales_info(file_id, current_user['user_id'])
        if not file_info:
            raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다")
        
        target_column = file_info.get('target_column')
        if not target_column:
            raise HTTPException(status_code=400, detail="파일 업로드 시 target_column을 지정하지 않았습니다.")
        
        info = await file_service.repository.get_preprocessed_info(file_id, target_column)
        if not info:
            raise HTTPException(status_code=404, detail="전처리 데이터를 찾을 수 없습니다. 파일 업로드 시 target_column을 지정했는지 확인하세요.")
        
        # 사용자 권한 확인
        file_info = await file_service.repository.get_sales_info(file_id, current_user['user_id'])
        if not file_info:
            raise HTTPException(status_code=403, detail="접근 권한이 없습니다")
        
        return info
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{file_id}/preprocess/data", summary="전처리 데이터 조회")
async def get_preprocessed_data(
    file_id: str,
    skip: int = Query(0, ge=0, description="건너뛸 행 수"),
    limit: int = Query(100, ge=1, le=10000, description="조회할 행 수"),
    current_user: dict = Depends(get_current_user),
    file_service: FileService = Depends(get_file_service)
):
    """
    전처리 데이터 조회
    
    파일 업로드 시 자동으로 생성된 전처리 데이터를 조회합니다. Lag 피처가 포함된 전처리된 데이터가 반환됩니다.
    
    - **file_id**: 파일의 고유 ID (파일 업로드 시 지정한 target_column에 대한 전처리 데이터를 조회합니다)
    - **skip**: 건너뛸 행 수 (페이징용, 기본값: 0)
    - **limit**: 조회할 행 수 (기본값: 100, 최대: 10000)
    
    전처리 데이터가 존재하지 않으면 404 에러가 반환됩니다.
    
    **참고**: 전처리 피처는 파일 업로드 시 `target_column`을 지정하면 자동으로 생성됩니다.
    """
    try:
        # 파일 정보에서 target_column 가져오기
        file_info = await file_service.repository.get_sales_info(file_id, current_user['user_id'])
        if not file_info:
            raise HTTPException(status_code=403, detail="접근 권한이 없습니다")
        
        target_column = file_info.get('target_column')
        if not target_column:
            raise HTTPException(status_code=400, detail="파일 업로드 시 target_column을 지정하지 않았습니다.")
        
        data = await file_service.repository.get_preprocessed_data(file_id, target_column, skip, limit)
        if not data:
            raise HTTPException(status_code=404, detail="전처리 데이터를 찾을 수 없습니다. 파일 업로드 시 target_column을 지정했는지 확인하세요.")
        
        return {
            "file_id": file_id,
            "target_column": target_column,
            "data": data,
            "count": len(data),
            "skip": skip,
            "limit": limit
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

