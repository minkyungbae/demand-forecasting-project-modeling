from fastapi import APIRouter, Depends, HTTPException, status, Form
from app.models.user import UserCreate, TokenResponse
from app.services.auth.auth_service import AuthService

router = APIRouter()

def get_auth_service() -> AuthService:
    """인증 서비스 의존성"""
    return AuthService()

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED, summary="회원가입")
async def register(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    회원가입
    
    새로운 사용자 계정을 생성합니다. 이메일, 비밀번호(최소 8자), 이름을 입력받아 계정을 생성하고,
    즉시 JWT 액세스 토큰을 발급하여 로그인 상태로 전환합니다.
    
    - **username**: 이메일 주소, 중복 불가
    - **비밀번호**: 최소 8자 이상
    - **이름**: 사용자 이름
    - **user_type**: 사용자 타입 (admin, premium, basic). 기본값: basic
    
    성공 시 JWT 토큰과 사용자 정보가 반환됩니다.
    """
    try:
        result = await auth_service.register(
            username=user_data.username,
            password=user_data.password,
            name=user_data.name,
            user_type=user_data.user_type
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/login", response_model=TokenResponse, summary="로그인")
async def login(
    username: str = Form(..., description="이메일 주소"),
    password: str = Form(..., description="비밀번호"),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    로그인
    
    이메일과 비밀번호를 사용하여 사용자 인증을 수행합니다. 인증 성공 시 JWT 액세스 토큰을 발급받습니다.
    
    **Swagger UI에서 사용 방법:**
    - "Try it out" 버튼 클릭
    - **username** 필드에 이메일 주소 입력 (예: user@example.com)
    - password 필드에 비밀번호 입력
    - "Execute" 버튼 클릭
    
    **프론트엔드에서 사용 시:**
    - Form Data로 전송: `username` 파라미터에 이메일 주소를 넣어서 보내면 됩니다
    - 예: `username=user@example.com&password=password123`
    
    **참고**: 
    - Swagger UI의 "Authorize" 버튼도 `username` 필드를 사용하므로 동일하게 작동합니다
    
    인증 성공 시 JWT 토큰과 사용자 정보가 반환되며, 이후 API 요청 시 이 토큰을 사용하여 인증할 수 있습니다.
    이메일 또는 비밀번호가 일치하지 않으면 401 에러가 반환됩니다.
    """
    try:
        result = await auth_service.login(
            username=username,
            password=password
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="이메일 또는 비밀번호가 올바르지 않습니다",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

