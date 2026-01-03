from typing import Optional, List
from datetime import datetime
from app.core.database import get_database
from app.models.solution import SolutionResponse
from app.services.solution.llm_service import LLMService
from app.services.correlation.correlation_repository import CorrelationRepository
from app.services.prediction.prediction_service import PredictionService

class SolutionService:
    """솔루션 서비스"""
    
    def __init__(self):
        self.llm_service = LLMService()
        self.correlation_repo = CorrelationRepository()
        self.prediction_service = PredictionService()
    
    async def generate_solution(
        self,
        file_id: str,
        correlation_id: Optional[str],
        prediction_id: Optional[str],
        question: Optional[str],
        user_id: str
    ) -> SolutionResponse:
        """솔루션 생성"""
        # 관련 데이터 수집
        correlation_data = None
        prediction_data = None
        
        if correlation_id:
            correlation_data = await self.correlation_repo.get_by_file_id(file_id)
        
        if prediction_id:
            prediction_data = await self.prediction_service.get_prediction(prediction_id)
        
        # LLM으로 인사이트 및 추천사항 생성
        result = await self.llm_service.generate_insights(
            file_id=file_id,
            correlation_data=correlation_data,
            prediction_data=prediction_data,
            question=question
        )
        
        # 결과 저장
        solution_id = f"sol_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        await self._save_solution(
            solution_id=solution_id,
            file_id=file_id,
            insights=result['insights'],
            recommendations=result['recommendations'],
            generated_text=result['generated_text'],
            user_id=user_id
        )
        
        return SolutionResponse(
            solution_id=solution_id,
            file_id=file_id,
            insights=result['insights'],
            recommendations=result['recommendations'],
            generated_text=result['generated_text'],
            created_at=datetime.now()
        )
    
    async def get_solution(self, solution_id: str) -> Optional[SolutionResponse]:
        """솔루션 조회"""
        db = await get_database()
        collection = db['solutions']
        sol = await collection.find_one({'solution_id': solution_id})
        
        if sol:
            sol.pop('_id', None)
            return SolutionResponse(**sol)
        return None
    
    async def _save_solution(
        self,
        solution_id: str,
        file_id: str,
        insights: List[str],
        recommendations: List[str],
        generated_text: str,
        user_id: str
    ):
        """솔루션 저장"""
        db = await get_database()
        collection = db['solutions']
        await collection.insert_one({
            'solution_id': solution_id,
            'file_id': file_id,
            'insights': insights,
            'recommendations': recommendations,
            'generated_text': generated_text,
            'user_id': user_id,
            'created_at': datetime.now()
        })

