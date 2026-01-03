from typing import List, Dict, Optional
from datetime import datetime
from app.core.database import get_database

class SuggestionRepository:
    """User Suggestions 데이터 접근 레이어"""
    
    async def save_suggestion(
        self,
        file_id: str,
        user_id: str,
        suggestions: List[str],
        detected_features: Dict
    ) -> Dict:
        """제안 저장 (User Suggestions Collection)"""
        db = await get_database()
        collection = db['user_suggestions']
        
        sug_id = f"sug_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        
        doc = {
            'sug_id': sug_id,
            'file_id': file_id,
            'user_id': user_id,
            'suggestions': suggestions,
            'detected_features': detected_features,
            'created_at': datetime.now()
        }
        
        await collection.insert_one(doc)
        return doc
    
    async def get_suggestions_by_file_id(self, file_id: str) -> Optional[Dict]:
        """파일 ID로 제안 조회"""
        db = await get_database()
        collection = db['user_suggestions']
        result = await collection.find_one(
            {'file_id': file_id},
            sort=[('created_at', -1)]
        )
        if result:
            result.pop('_id', None)
        return result

