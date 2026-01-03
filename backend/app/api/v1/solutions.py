from fastapi import APIRouter, Depends, HTTPException
from app.models.solution import SolutionRequest, SolutionResponse
from app.services.solution.solution_service import SolutionService
from app.dependencies import get_current_user

router = APIRouter()

def get_solution_service() -> SolutionService:
    """솔루션 서비스 의존성"""
    return SolutionService()

@router.post("/generate", response_model=SolutionResponse, status_code=201, summary="AI 기반 인사이트 및 솔루션 생성")
async def generate_solution(
    request: SolutionRequest,
    current_user: dict = Depends(get_current_user),
    solution_service: SolutionService = Depends(get_solution_service)
):
    """
    AI 기반 인사이트 및 솔루션 생성
    
    상관관계 분석 결과와 예측 결과를 바탕으로 LLM(대규모 언어 모델)을 활용하여 
    비즈니스 인사이트와 개선 방안을 생성합니다.
    
    - **file_id**: 분석에 사용된 파일의 고유 ID
    - **correlation_id**: (선택사항) 사용할 상관관계 분석 결과 ID
    - **prediction_id**: (선택사항) 사용할 예측 결과 ID
    - **question**: (선택사항) 추가로 질문할 내용
    
    LLM이 분석:
    - 데이터 패턴 및 트렌드 해석
    - 주요 피처의 영향도 분석
    - 예측 결과에 대한 의미 해석
    - 비즈니스 개선 방안 제안
    - 리스크 요소 식별 및 대응 방안
    
    반환 정보:
    - 생성된 인사이트 요약
    - 상세 분석 내용
    - 추천 사항 및 액션 아이템
    
    OpenRouter API를 통해 다양한 LLM 모델(GPT-4, Claude 등)을 활용할 수 있습니다.
    """
    try:
        result = await solution_service.generate_solution(
            file_id=request.file_id,
            correlation_id=request.correlation_id,
            prediction_id=request.prediction_id,
            question=request.question,
            user_id=current_user['user_id']
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{solution_id}", response_model=SolutionResponse, summary="생성된 솔루션 조회")
async def get_solution(
    solution_id: str,
    current_user: dict = Depends(get_current_user),
    solution_service: SolutionService = Depends(get_solution_service)
):
    """
    생성된 솔루션 조회
    
    이전에 생성한 AI 기반 인사이트 및 솔루션 결과를 조회합니다.
    
    - **solution_id**: 조회할 솔루션의 고유 ID
    
    저장된 인사이트, 분석 내용, 추천 사항 등을 반환합니다.
    존재하지 않는 솔루션 ID인 경우 404 에러가 반환됩니다.
    """
    try:
        result = await solution_service.get_solution(solution_id)
        if not result:
            raise HTTPException(status_code=404, detail="솔루션을 찾을 수 없습니다")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

