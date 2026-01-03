from typing import Optional
from app.core.database import get_database

class UserRepository:
    """유저 데이터 접근 레이어 (User Collection)"""
    
    async def create(self, user_data: dict) -> dict:
        """유저 생성"""
        db = await get_database()
        collection = db['users']  # User Collection
        await collection.insert_one(user_data)
        return user_data
    
    async def get_by_id(self, user_id: str) -> Optional[dict]:
        """유저 ID로 조회"""
        db = await get_database()
        collection = db['users']
        user = await collection.find_one({'user_id': user_id})
        if user:
            user.pop('_id', None)
        return user
    
    async def get_by_username(self, username: str) -> Optional[dict]:
        """이메일로 유저 조회 (username 또는 email 필드 확인)"""
        db = await get_database()
        collection = db['users']
        # 먼저 username으로 조회
        user = await collection.find_one({'username': username})
        if not user:
            # username이 없으면 email로도 조회 (마이그레이션 전 데이터 대응)
            user = await collection.find_one({'email': username})
            # email로 찾았으면 username 필드 추가
            if user and 'username' not in user:
                await collection.update_one(
                    {'_id': user['_id']},
                    {'$set': {'username': user.get('email', username)}}
                )
                user['username'] = user.get('email', username)
        if user:
            user.pop('_id', None)
        return user
    
    async def increment_file_upload_count(self, user_id: str):
        """파일 업로드 횟수 증가"""
        db = await get_database()
        collection = db['users']
        await collection.update_one(
            {'user_id': user_id},
            {'$inc': {'file_upload_count': 1}}
        )

