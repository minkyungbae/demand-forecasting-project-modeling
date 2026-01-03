from fastapi import APIRouter, Depends, HTTPException
from app.models.correlation import CorrelationAnalysisRequest, CorrelationAnalysisResponse
from app.services.correlation.correlation_service import CorrelationService
from app.dependencies import get_current_user

router = APIRouter()

def get_correlation_service() -> CorrelationService:
    """상관관계 서비스 의존성"""
    return CorrelationService()

@router.post("/analyze", response_model=CorrelationAnalysisResponse, summary="상관관계 분석 수행")
async def analyze_correlations(
    request: CorrelationAnalysisRequest,
    current_user: dict = Depends(get_current_user),
    correlation_service: CorrelationService = Depends(get_correlation_service)
):
    """
    상관관계 분석 수행
    
    업로드된 데이터에서 목표 변수와 다른 피처들 간의 상관관계를 분석합니다.
    
    - **file_id**: 분석할 파일의 고유 ID (파일 업로드 시 지정한 target_column이 자동으로 사용됩니다)
    - **features**: 분석할 피처 리스트. None이면 저장된 valid_columns가 자동으로 사용됩니다.
    
    **사용 예시**:
    ```json
    {
      "file_id": "file_123456",
      "features": null  // 자동 선택 (저장된 valid_columns 사용)
    }
    ```
    
    분석 결과:
    - 각 피처와 목표 변수 간의 상관계수 (피어슨 상관계수)
    - 피처별 가중치 (상관관계 기반)
    - 상관관계 히트맵 차트 (Base64 인코딩된 이미지)
    
    상관계수는 -1부터 1까지의 값을 가지며, 1에 가까울수록 강한 양의 상관관계, 
    -1에 가까울수록 강한 음의 상관관계를 의미합니다. 0에 가까우면 상관관계가 약합니다.
    
    분석 결과는 데이터베이스에 저장되어 이후 예측 모델 생성 시 가중치로 활용됩니다.
    """
    try:
        result = await correlation_service.analyze_correlations(
            file_id=request.file_id,
            features=request.features,
            user_id=current_user['user_id']
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{file_id}", response_model=CorrelationAnalysisResponse, summary="상관관계 분석 결과 조회")
async def get_correlations(
    file_id: str,
    current_user: dict = Depends(get_current_user),
    correlation_service: CorrelationService = Depends(get_correlation_service)
):
    """
    상관관계 분석 결과 조회
    
    특정 파일에 대해 이전에 수행한 상관관계 분석 결과를 조회합니다.
    
    - **file_id**: 분석 결과를 조회할 파일의 고유 ID
    
    이전에 분석을 수행한 경우 저장된 분석 결과(상관계수, 가중치, 차트 등)를 반환합니다.
    아직 분석을 수행하지 않은 파일인 경우 404 에러가 반환됩니다.
    """
    try:
        result = await correlation_service.get_correlations(file_id)
        if not result:
            raise HTTPException(status_code=404, detail="결과를 찾을 수 없습니다")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

