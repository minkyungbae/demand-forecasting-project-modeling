from typing import Optional, Dict
from datetime import datetime
from app.core.database import get_database

class TaskRepository:
    """작업 상태 데이터 접근 레이어 (Analysis Tasks Collection)"""
    
    async def create_task(
        self,
        file_id: str,
        user_id: str,
        target_column: str
    ) -> Dict:
        """작업 생성"""
        db = await get_database()
        collection = db['analysis_tasks']
        
        task_id = f"task_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        doc = {
            'task_id': task_id,
            'file_id': file_id,
            'user_id': user_id,
            'target_column': target_column,
            'status': 'pending',  # pending, processing, completed, failed
            'current_step': None,
            'steps': {
                'related_columns': {'status': 'pending', 'result': None},
                'statistics': {'status': 'pending', 'result': None},
                'visualizations': {'status': 'pending', 'result': None},
                'correlation': {'status': 'pending', 'result': None},
                'prediction': {'status': 'pending', 'result': None},
                'solution': {'status': 'pending', 'result': None}
            },
            'error_message': None,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        await collection.insert_one(doc)
        return doc
    
    async def get_task(self, task_id: str) -> Optional[Dict]:
        """작업 조회"""
        db = await get_database()
        collection = db['analysis_tasks']
        result = await collection.find_one({'task_id': task_id})
        if result:
            result.pop('_id', None)
        return result
    
    async def update_step_status(
        self,
        task_id: str,
        step_name: str,
        status: str,
        result: Optional[Dict] = None,
        error_message: Optional[str] = None
    ):
        """단계 상태 업데이트"""
        db = await get_database()
        collection = db['analysis_tasks']
        
        update_data = {
            'updated_at': datetime.now(),
            f'steps.{step_name}.status': status
        }
        
        if result is not None:
            update_data[f'steps.{step_name}.result'] = result
        
        if status == 'processing':
            update_data['status'] = 'processing'
            update_data['current_step'] = step_name
        elif status == 'completed':
            # 모든 단계 완료 확인
            task = await collection.find_one({'task_id': task_id})
            all_completed = all(
                step['status'] == 'completed' or 
                (step_name == name and status == 'completed')
                for name, step in task.get('steps', {}).items()
            )
            if all_completed:
                update_data['status'] = 'completed'
                update_data['current_step'] = None
        elif status == 'failed':
            update_data['status'] = 'failed'
            if error_message:
                update_data['error_message'] = error_message
        
        await collection.update_one(
            {'task_id': task_id},
            {'$set': update_data}
        )
    
    async def update_task_status(
        self,
        task_id: str,
        status: str
    ):
        """전체 작업 상태 업데이트"""
        db = await get_database()
        collection = db['analysis_tasks']
        
        await collection.update_one(
            {'task_id': task_id},
            {'$set': {
                'status': status,
                'updated_at': datetime.now()
            }}
        )

