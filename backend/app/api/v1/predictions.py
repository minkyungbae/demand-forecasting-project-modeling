from fastapi import APIRouter, Depends, HTTPException
from app.models.prediction import PredictionRequest, PredictionResponse
from app.services.prediction.prediction_service import PredictionService
from app.dependencies import get_current_user

router = APIRouter()

def get_prediction_service() -> PredictionService:
    """예측 서비스 의존성"""
    return PredictionService()

@router.post("/predict", response_model=PredictionResponse, status_code=201, summary="수요 예측 모델 생성 및 예측 수행")
async def create_prediction(
    request: PredictionRequest,
    current_user: dict = Depends(get_current_user),
    prediction_service: PredictionService = Depends(get_prediction_service)
):
    """
    수요 예측 모델 생성 및 예측 수행
    
    머신러닝 모델을 학습시켜 미래 수요를 예측합니다.
    
    - **file_id**: 학습 및 예측에 사용할 파일의 고유 ID (파일 업로드 시 지정한 target_column이 자동으로 사용됩니다)
    - **features**: 모델 학습에 사용할 피처 컬럼 목록
    - **model_type**: 사용할 머신러닝 모델 유형 (linear, random_forest 등)
    - **forecast_periods**: 예측할 기간 수 (예: 30일 후까지 예측)
    
    처리 과정:
    1. 파일 정보에서 target_column 자동 가져오기
    2. 지정된 피처들을 사용하여 머신러닝 모델 학습
    3. 모델 성능 평가 (RMSE, MAE, R² 등)
    4. 미래 기간에 대한 예측값 생성
    5. 예측 결과 시각화 차트 생성
    
    반환 정보:
    - 예측 ID
    - 학습된 모델 정보
    - 모델 성능 지표
    - 예측값 (미래 기간별)
    - 예측 결과 시각화 차트
    
    상관관계 분석 결과가 있다면 자동으로 가중치가 적용되어 더 정확한 예측이 가능합니다.
    """
    try:
        result = await prediction_service.create_prediction(
            file_id=request.file_id,
            features=request.features,
            model_type=request.model_type,
            forecast_periods=request.forecast_periods,
            user_id=current_user['user_id']
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{prediction_id}", response_model=PredictionResponse, summary="예측 결과 조회")
async def get_prediction(
    prediction_id: str,
    current_user: dict = Depends(get_current_user),
    prediction_service: PredictionService = Depends(get_prediction_service)
):
    """
    예측 결과 조회
    
    이전에 수행한 예측 결과를 조회합니다.
    
    - **prediction_id**: 조회할 예측 결과의 고유 ID
    
    저장된 예측 결과, 모델 성능 지표, 예측값, 시각화 차트 등을 반환합니다.
    존재하지 않는 예측 ID인 경우 404 에러가 반환됩니다.
    """
    try:
        result = await prediction_service.get_prediction(prediction_id)
        if not result:
            raise HTTPException(status_code=404, detail="예측 결과를 찾을 수 없습니다")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

