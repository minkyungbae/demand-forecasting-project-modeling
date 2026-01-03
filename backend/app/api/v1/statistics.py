from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from app.services.analysis.statistics_service import StatisticsService
from app.services.file.file_analysis_config_repository import FileAnalysisConfigRepository
from app.dependencies import get_current_user
from app.core.database import get_database

router = APIRouter()

def get_statistics_service() -> StatisticsService:
    """통계 분석 서비스 의존성"""
    return StatisticsService()

def get_config_repository() -> FileAnalysisConfigRepository:
    """설정 저장소 의존성"""
    return FileAnalysisConfigRepository()

@router.post("/analyze", status_code=201, summary="통계 분석 수행")
async def analyze_statistics(
    file_id: str,
    group_by_column: Optional[str] = Query(None, description="그룹화할 컬럼명 (선택사항)"),
    current_user: dict = Depends(get_current_user),
    statistics_service: StatisticsService = Depends(get_statistics_service),
    config_repository: FileAnalysisConfigRepository = Depends(get_config_repository)
):
    """
    통계 분석 수행
    
    지정된 컬럼에 대한 기본 통계를 계산하고 LLM으로 설명을 생성합니다.
    
    - **file_id**: 분석할 파일의 고유 ID (파일 업로드 시 지정한 target_column이 자동으로 사용됩니다)
    - **group_by_column**: (선택사항) 그룹화할 컬럼명 (예: 상품명, 브랜드)
    
    **자동 모드**:
    - target_column은 파일 업로드 시 지정한 값이 자동으로 사용됩니다.
    - group_by_column이 None이면, 저장된 설정에서 자동으로 가져옵니다.
    
    반환 정보:
    - **statistics**: 통계 값 (평균, 중앙값, 표준편차, 최솟값, 최댓값, 합계 등)
    - **llm_explanation**: LLM이 생성한 통계 설명
    - **group_by_column**: 사용된 그룹화 컬럼
    - **target_column**: 사용된 대상 컬럼명
    
    통계 분석 결과는 데이터베이스에 저장되어 나중에 다시 조회할 수 있습니다.
    """
    try:
        # 파일 정보에서 target_column 가져오기
        from app.services.file.file_repository import FileRepository
        file_repository = FileRepository()
        file_info = await file_repository.get_sales_info(file_id, current_user['user_id'])
        if not file_info:
            raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다")
        
        target_column = file_info.get('target_column')
        if not target_column:
            raise HTTPException(status_code=400, detail="파일 업로드 시 target_column을 지정하지 않았습니다. 파일을 다시 업로드하거나 target_column을 지정해주세요.")
        
        # group_by_column이 없으면 config에서 가져오기
        if not group_by_column:
            config = await config_repository.get_config(file_id, target_column)
            group_by_column = config.get('group_by_column') if config else None
        
        result = await statistics_service.generate_statistics(
            file_id=file_id,
            user_id=current_user['user_id'],
            target_column=target_column,
            group_by_column=group_by_column
        )
        
        # 결과 저장
        from datetime import datetime
        db = await get_database()
        stats_collection = db['statistics']
        stats_id = f"stats_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        await stats_collection.insert_one({
            'statistics_id': stats_id,
            'file_id': file_id,
            'user_id': current_user['user_id'],
            'target_column': target_column,
            'statistics': result['statistics'],
            'llm_explanation': result['llm_explanation'],
            'group_by_column': result.get('group_by_column'),
            'created_at': datetime.now()
        })
        
        return {
            "statistics_id": stats_id,
            "file_id": file_id,
            "target_column": target_column,
            "statistics": result['statistics'],
            "llm_explanation": result['llm_explanation'],
            "group_by_column": result.get('group_by_column')
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{file_id}", summary="통계 분석 결과 조회")
async def get_statistics(
    file_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    통계 분석 결과 조회
    
    특정 파일에 대해 이전에 수행한 통계 분석 결과를 조회합니다.
    
    - **file_id**: 분석 결과를 조회할 파일의 고유 ID (파일 업로드 시 지정한 target_column에 대한 결과를 조회합니다)
    
    저장된 통계 분석 결과(통계 값, LLM 설명 등)를 반환합니다.
    아직 분석을 수행하지 않은 파일인 경우 404 에러가 반환됩니다.
    """
    try:
        # 파일 정보에서 target_column 가져오기
        from app.services.file.file_repository import FileRepository
        file_repository = FileRepository()
        file_info = await file_repository.get_sales_info(file_id, current_user['user_id'])
        if not file_info:
            raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다")
        
        target_column = file_info.get('target_column')
        if not target_column:
            raise HTTPException(status_code=400, detail="파일 업로드 시 target_column을 지정하지 않았습니다.")
        
        db = await get_database()
        stats_collection = db['statistics']
        
        query = {'file_id': file_id, 'user_id': current_user['user_id'], 'target_column': target_column}
        
        result = await stats_collection.find_one(
            query,
            sort=[('created_at', -1)]
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="통계 분석 결과를 찾을 수 없습니다")
        
        result.pop('_id', None)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

