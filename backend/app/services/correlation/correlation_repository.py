from typing import Dict, Optional
from datetime import datetime
from app.core.database import get_database

class CorrelationRepository:
    """상관관계 데이터 접근 레이어"""
    
    async def save(
        self,
        file_id: str,
        user_id: str,
        target_column: str,
        correlations: Dict[str, float],
        weights: Dict[str, float],
        chart: str
    ) -> Dict:
        """상관관계 분석 결과 저장"""
        db = await get_database()
        collection = db['correlations']
        
        correlation_id = f"corr_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        doc = {
            'correlation_id': correlation_id,
            'file_id': file_id,
            'user_id': user_id,
            'target_column': target_column,
            'correlation_matrix': correlations,
            'weights': weights,
            'chart': chart,
            'created_at': datetime.now()
        }
        
        await collection.insert_one(doc)
        return doc
    
    async def get_by_file_id(self, file_id: str) -> Optional[Dict]:
        """파일 ID로 조회"""
        db = await get_database()
        collection = db['correlations']
        result = await collection.find_one(
            {'file_id': file_id},
            sort=[('created_at', -1)]
        )
        if result:
            result.pop('_id', None)
        return result

