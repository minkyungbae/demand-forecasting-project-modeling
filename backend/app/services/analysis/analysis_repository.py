from typing import Dict, Optional, List
from datetime import datetime
from app.core.database import get_database

class AnalysisRepository:
    """Analysis Results 데이터 접근 레이어"""
    
    async def save_analysis_result(
        self,
        file_id: str,
        user_id: str,
        analysis_type: str,
        metrics: Dict,
        feature_count: int,
        target_column: str,
        group_by: List[str],
        processing_time_seconds: float,
        result: Dict
    ) -> Dict:
        """분석 결과 저장 (Analysis Results Collection)"""
        db = await get_database()
        collection = db['analysis_results']
        
        # results_id, analysis_id 생성
        results_id = f"results_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        analysis_id = f"analysis_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        
        doc = {
            'results_id': results_id,
            'analysis_id': analysis_id,
            'file_id': file_id,
            'user_id': user_id,
            'analysis_type': analysis_type,
            'metrics': metrics,
            'feature_count': feature_count,
            'target_column': target_column,
            'group_by': group_by,
            'processing_time_seconds': processing_time_seconds,
            'result': result,
            'created_at': datetime.now()
        }
        
        await collection.insert_one(doc)
        return doc
    
    async def get_analysis_by_file_id(self, file_id: str) -> Optional[Dict]:
        """파일 ID로 분석 결과 조회"""
        db = await get_database()
        collection = db['analysis_results']
        result = await collection.find_one(
            {'file_id': file_id},
            sort=[('created_at', -1)]
        )
        if result:
            result.pop('_id', None)
        return result
    
    async def get_analysis_by_id(self, results_id: str) -> Optional[Dict]:
        """results_id로 분석 결과 조회"""
        db = await get_database()
        collection = db['analysis_results']
        result = await collection.find_one({'results_id': results_id})
        if result:
            result.pop('_id', None)
        return result

