from typing import Dict, Optional, List
from datetime import datetime
from app.core.database import get_database

class FileAnalysisConfigRepository:
    """파일 분석 설정 데이터 접근 레이어 (File Analysis Config Collection)"""
    
    async def save_config(
        self,
        file_id: str,
        user_id: str,
        target_column: str,
        related_columns: list,
        excluded_columns: list,
        final_columns: list,
        group_by_column: Optional[str],
        product_counts: Dict[str, int],
        column_type_counts: Dict[str, int],
        group_by_columns: Optional[List[str]] = None,
        grouping_columns: Optional[List[str]] = None,
        valid_columns: Optional[List[str]] = None,
        date_column: Optional[str] = None,
        lag_feature_columns: Optional[List[str]] = None
    ) -> Dict:
        """파일 분석 설정 저장"""
        db = await get_database()
        collection = db['file_analysis_config']
        
        config_id = f"config_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        doc = {
            'config_id': config_id,
            'file_id': file_id,
            'user_id': user_id,
            'target_column': target_column,
            'related_columns': related_columns,
            'excluded_columns': excluded_columns,
            'final_columns': final_columns,
            'group_by_column': group_by_column,  # 시각화용 주요 그룹화 컬럼
            'group_by_columns': group_by_columns or [],  # 상관계수 분석용 모든 그룹화 컬럼 목록
            'grouping_columns': grouping_columns or [],  # 그룹화 전용 컬럼 (브랜드, 카테고리, 상품ID, 상품명 등)
            'valid_columns': valid_columns or [],  # 예측/상관관계 분석에 사용할 유효 컬럼 (Lag 피처 포함)
            'date_column': date_column,  # 날짜 컬럼명
            'lag_feature_columns': lag_feature_columns or [],  # 생성된 Lag 피처 컬럼 목록
            'product_counts': product_counts,  # {"상품A": 100, "상품B": 50, ...}
            'column_type_counts': column_type_counts,  # {"int": 3, "varchar": 2, "date": 1, "object": 4}
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        # 기존 설정이 있으면 업데이트, 없으면 생성
        existing = await collection.find_one({'file_id': file_id, 'target_column': target_column})
        if existing:
            await collection.update_one(
                {'file_id': file_id, 'target_column': target_column},
                {'$set': {**doc, 'updated_at': datetime.now()}}
            )
            doc['config_id'] = existing.get('config_id', config_id)
        else:
            await collection.insert_one(doc)
        
        return doc
    
    async def get_config(
        self,
        file_id: str,
        target_column: Optional[str] = None
    ) -> Optional[Dict]:
        """파일 분석 설정 조회"""
        db = await get_database()
        collection = db['file_analysis_config']
        
        query = {'file_id': file_id}
        if target_column:
            query['target_column'] = target_column
        
        result = await collection.find_one(query, sort=[('updated_at', -1)])
        if result:
            result.pop('_id', None)
        return result
    
    async def delete_config(self, file_id: str) -> bool:
        """파일 분석 설정 삭제 (파일 삭제 시)"""
        db = await get_database()
        collection = db['file_analysis_config']
        result = await collection.delete_many({'file_id': file_id})
        return result.deleted_count > 0

