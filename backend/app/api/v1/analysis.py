from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Response
from typing import Optional
import asyncio
import base64
from app.models.analysis import AnalysisStartRequest, AnalysisStartResponse, TaskStatusResponse, TaskResultResponse
from app.services.analysis.analysis_service import AnalysisService
from app.dependencies import get_current_user
from app.core.database import get_database

router = APIRouter()

def get_analysis_service() -> AnalysisService:
    """분석 서비스 의존성"""
    return AnalysisService()

@router.post("/start", response_model=AnalysisStartResponse, status_code=201, summary="전체 분석 작업 시작")
async def start_analysis(
    request: AnalysisStartRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """
    전체 분석 작업 시작
    
    CSV 업로드 시 자동으로 생성된 컬럼 추천 및 전처리 피처를 기반으로 모든 분석 작업이 자동으로 진행됩니다.
    
    처리 단계:
    1. 통계 분석 + LLM 설명
    2. 시각화 생성 (상품별 선그래프, 막대그래프)
    3. 상관관계 분석 (전체, 상품별)
    4. 예측 모델링 (여러 모델 비교 후 최적 모델 선택)
    5. 솔루션 생성 (LLM 기반 인사이트)
    
    - **file_id**: 분석할 파일의 고유 ID (파일 업로드 시 지정한 target_column이 자동으로 사용됩니다)
    
    반환:
    - **task_id**: 작업 추적용 ID
    - **status**: 초기 상태 (pending → processing → completed)
    
    작업 진행 상황은 `GET /analysis/{task_id}`로 확인할 수 있습니다.
    """
    try:
        result = await analysis_service.start_analysis(
            file_id=request.file_id,
            user_id=current_user['user_id'],
            background_tasks=background_tasks
        )
        
        # 백그라운드 작업을 asyncio.create_task로 시작 (현재 이벤트 루프 사용)
        task = asyncio.create_task(
            analysis_service._run_analysis_pipeline(
                result['task_id'],
                request.file_id,
                current_user['user_id']
            )
        )
        task.set_name(f"analysis_task_{result['task_id']}")
        AnalysisService._register_task(task)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{task_id}", response_model=TaskStatusResponse, summary="작업 진행 상황 조회")
async def get_task_status(
    task_id: str,
    current_user: dict = Depends(get_current_user),
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """
    작업 진행 상황 조회
    
    분석 작업의 현재 상태와 각 단계별 진행 상황을 조회합니다.
    
    - **task_id**: 조회할 작업 ID
    
    반환 정보:
    - 전체 작업 상태 (pending, processing, completed, failed)
    - 현재 진행 중인 단계
    - 각 단계별 상태 및 결과 (있는 경우)
    - 오류 메시지 (있는 경우)
    """
    try:
        task = await analysis_service.get_task_status(task_id, current_user['user_id'])
        if not task:
            raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다")
        return task
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{task_id}/result", response_model=TaskResultResponse, summary="작업 결과 조회")
async def get_task_result(
    task_id: str,
    current_user: dict = Depends(get_current_user),
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """
    작업 결과 조회 (완료된 경우)
    
    완료된 분석 작업의 최종 결과를 조회합니다.
    
    - **task_id**: 조회할 작업 ID
    
    반환 정보:
    - 통계 분석 결과
    - 시각화 결과 (차트 이미지)
    - 상관관계 분석 결과
    - 예측 결과
    - 솔루션 결과 (LLM 인사이트)
    """
    try:
        result = await analysis_service.get_task_result(task_id, current_user['user_id'])
        if not result:
            raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다")
        if result['status'] != 'completed':
            raise HTTPException(status_code=400, detail=f"작업이 아직 완료되지 않았습니다. 현재 상태: {result['status']}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{task_id}/statistics", summary="통계 분석 결과 조회")
async def get_task_statistics(
    task_id: str,
    current_user: dict = Depends(get_current_user),
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """작업의 통계 분석 결과 조회"""
    try:
        result = await analysis_service.get_task_statistics(task_id, current_user['user_id'])
        if not result:
            raise HTTPException(status_code=404, detail="통계 결과를 찾을 수 없습니다")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{task_id}/visualizations", summary="시각화 결과 조회")
async def get_task_visualizations(
    task_id: str,
    current_user: dict = Depends(get_current_user),
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """작업의 시각화 결과 조회"""
    try:
        result = await analysis_service.get_task_visualizations(task_id, current_user['user_id'])
        if not result:
            raise HTTPException(status_code=404, detail="시각화 결과를 찾을 수 없습니다")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{task_id}/visualizations/{visualization_id}/image", summary="분석 작업 시각화 이미지 직접 조회")
async def get_task_visualization_image(
    task_id: str,
    visualization_id: str,
    current_user: dict = Depends(get_current_user),
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """
    분석 작업에서 생성된 시각화 이미지를 직접 반환 (PNG 형식)
    
    Swagger UI나 브라우저에서 이미지를 직접 볼 수 있도록 이미지를 반환합니다.
    
    - **task_id**: 분석 작업 ID
    - **visualization_id**: 시각화 ID
    
    브라우저에서 이 URL을 직접 열면 차트 이미지를 볼 수 있습니다.
    """
    try:
        # 작업 소유권 확인
        task = await analysis_service.get_task_status(task_id, current_user['user_id'])
        if not task:
            raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다")
        
        # 시각화 조회
        db = await get_database()
        collection = db['visualizations']
        viz = await collection.find_one({'visualization_id': visualization_id})
        
        if not viz:
            raise HTTPException(status_code=404, detail="시각화를 찾을 수 없습니다")
        
        # 사용자 권한 확인
        if viz.get('user_id') != current_user['user_id']:
            raise HTTPException(status_code=403, detail="접근 권한이 없습니다")
        
        # Base64 디코딩
        chart_data = viz.get('chart_data', '')
        if not chart_data:
            raise HTTPException(status_code=404, detail="이미지 데이터가 없습니다")
        
        image_bytes = base64.b64decode(chart_data)
        
        # 이미지를 직접 반환
        return Response(
            content=image_bytes,
            media_type="image/png",
            headers={
                "Content-Disposition": f"inline; filename=visualization_{visualization_id}.png"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{task_id}/correlation", summary="상관관계 분석 결과 조회")
async def get_task_correlation(
    task_id: str,
    current_user: dict = Depends(get_current_user),
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """작업의 상관관계 분석 결과 조회"""
    try:
        result = await analysis_service.get_task_correlation(task_id, current_user['user_id'])
        if not result:
            raise HTTPException(status_code=404, detail="상관관계 결과를 찾을 수 없습니다")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{task_id}/prediction", summary="예측 결과 조회")
async def get_task_prediction(
    task_id: str,
    current_user: dict = Depends(get_current_user),
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """작업의 예측 결과 조회"""
    try:
        result = await analysis_service.get_task_prediction(task_id, current_user['user_id'])
        if not result:
            raise HTTPException(status_code=404, detail="예측 결과를 찾을 수 없습니다")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{task_id}/solution", summary="솔루션 결과 조회")
async def get_task_solution(
    task_id: str,
    current_user: dict = Depends(get_current_user),
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """작업의 솔루션 결과 조회"""
    try:
        result = await analysis_service.get_task_solution(task_id, current_user['user_id'])
        if not result:
            raise HTTPException(status_code=404, detail="솔루션 결과를 찾을 수 없습니다")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/file/{file_id}/latest", summary="파일의 최신 분석 결과 조회")
async def get_latest_analysis_by_file(
    file_id: str,
    current_user: dict = Depends(get_current_user),
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """특정 파일의 최신 분석 작업 결과 조회"""
    try:
        result = await analysis_service.get_latest_analysis_by_file(file_id, current_user['user_id'])
        if not result:
            raise HTTPException(status_code=404, detail="분석 결과를 찾을 수 없습니다")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
