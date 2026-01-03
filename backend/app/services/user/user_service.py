from typing import Optional
from datetime import datetime
from app.core.database import get_database
from app.services.user.user_repository import UserRepository
from app.models.user import UserType

class UserService:
    """유저 서비스"""
    
    def __init__(self):
        self.repository = UserRepository()
    
    async def create_user(self, username: str, hashed_password: str, name: str = None, user_type: UserType = UserType.BASIC) -> dict:
        """유저 생성"""
        user_id = f"user_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        user_data = {
            'user_id': user_id,
            'username': username,
            'password': hashed_password,
            'user_type': user_type.value,  # Enum 값을 문자열로 저장
            'file_upload_count': 0,
            'name': name or (username.split('@')[0] if '@' in username else username),  # name이 없으면 username 앞부분 사용
            'created_at': datetime.now()
        }
        return await self.repository.create(user_data)
    
    async def get_user_by_id(self, user_id: str) -> Optional[dict]:
        """유저 ID로 조회"""
        user = await self.repository.get_by_id(user_id)
        if user:
            # 비밀번호 제외하고 반환
            user.pop('password', None)
        return user
    
    async def increment_file_upload_count(self, user_id: str):
        """파일 업로드 횟수 증가"""
        await self.repository.increment_file_upload_count(user_id)
    
    async def get_user_by_username(self, username: str) -> Optional[dict]:
        """이메일로 유저 조회"""
        return await self.repository.get_by_username(username)

