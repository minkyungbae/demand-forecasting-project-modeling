from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.core.config import settings
from app.core.security import decode_access_token
from app.services.user.user_service import UserService

# tokenUrl을 실제 로그인 엔드포인트로 설정하여 Swagger UI에서 직접 로그인 가능하도록 함
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """현재 사용자 조회 (JWT 검증)"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증 정보를 확인할 수 없습니다",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    user_service = UserService()
    user = await user_service.get_user_by_id(user_id)
    if user is None:
        raise credentials_exception
    
    return user

