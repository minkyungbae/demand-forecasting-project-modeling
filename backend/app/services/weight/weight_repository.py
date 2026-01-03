from typing import Dict, Optional
from datetime import datetime
from app.core.database import get_database

class WeightRepository:
    """Feature Weights 데이터 접근 레이어"""
    
    async def save_weights(
        self,
        file_id: str,
        user_id: str,
        weights: Dict[str, float],
        model_metrics: Optional[Dict] = None
    ) -> Dict:
        """피처 가중치 저장 (Feature Weights Collection)"""
        db = await get_database()
        collection = db['feature_weights']
        
        weight_id = f"weight_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        
        doc = {
            'weight_id': weight_id,
            'file_id': file_id,
            'user_id': user_id,
            'weights': weights,
            'model_metrics': model_metrics,
            'created_at': datetime.now()
        }
        
        await collection.insert_one(doc)
        return doc
    
    async def get_weights_by_file_id(self, file_id: str) -> Optional[Dict]:
        """파일 ID로 가중치 조회"""
        db = await get_database()
        collection = db['feature_weights']
        result = await collection.find_one(
            {'file_id': file_id},
            sort=[('created_at', -1)]
        )
        if result:
            result.pop('_id', None)
        return result

