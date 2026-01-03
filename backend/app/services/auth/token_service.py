from datetime import datetime, timedelta
from app.core.security import create_access_token, decode_access_token
from app.core.config import settings

class TokenService:
    """토큰 관리 서비스"""
    
    def create_token(self, user_id: str) -> str:
        """액세스 토큰 생성"""
        return create_access_token(
            data={"sub": user_id},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
    
    def verify_token(self, token: str) -> dict:
        """토큰 검증"""
        return decode_access_token(token)
    
    def refresh_token(self, token: str) -> str:
        """토큰 갱신"""
        payload = self.verify_token(token)
        if payload:
            user_id = payload.get("sub")
            return self.create_token(user_id)
        return None

