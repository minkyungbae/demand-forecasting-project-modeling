from datetime import timedelta
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.config import settings
from app.services.user.user_service import UserService
from app.models.user import TokenResponse, UserResponse, UserType

class AuthService:
    """인증 서비스"""
    
    def __init__(self):
        self.user_service = UserService()
    
    async def register(self, username: str, password: str, name: str, user_type: UserType = None) -> TokenResponse:
        """회원가입"""
        # 이메일 중복 확인
        existing_user = await self.user_service.get_user_by_username(username)
        if existing_user:
            raise ValueError("이미 등록된 이메일입니다")
        
        # 비밀번호 해싱
        hashed_password = get_password_hash(password)
        
        # user_type이 없으면 기본값 사용
        from app.models.user import UserType
        if user_type is None:
            user_type = UserType.BASIC
        
        # 유저 생성
        user = await self.user_service.create_user(
            username=username,
            hashed_password=hashed_password,
            name=name,
            user_type=user_type
        )
        
        # 토큰 생성
        access_token = create_access_token(
            data={"sub": user['user_id']},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(**user)
        )
    
    async def login(self, username: str, password: str) -> TokenResponse:
        """로그인"""
        # 유저 조회
        user = await self.user_service.get_user_by_username(username)
        if not user:
            return None
        
        # 비밀번호 검증
        stored_password = user.get('password') or user.get('hashed_password', '')
        if not verify_password(password, stored_password):
            return None
        
        # 토큰 생성
        access_token = create_access_token(
            data={"sub": user['user_id']},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(
                user_id=user['user_id'],
                username=user['username'],
                name=user.get('name', user.get('username', '').split('@')[0] if '@' in user.get('username', '') else user.get('username', '')),
                user_type=user.get('user_type'),
                created_at=user.get('created_at')
            )
        )

