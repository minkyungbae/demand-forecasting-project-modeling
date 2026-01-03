from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.models.user import UserResponse
from app.services.user.user_service import UserService
from app.dependencies import get_current_user
from app.core.database import get_database

router = APIRouter()

def get_user_service() -> UserService:
    """유저 서비스 의존성"""
    return UserService()

@router.get("/me", response_model=UserResponse, summary="현재 사용자 정보 조회")
async def get_current_user_info(
    current_user: dict = Depends(get_current_user)
):
    """
    현재 사용자 정보 조회
    
    현재 로그인한 사용자의 정보를 조회합니다. JWT 토큰에서 사용자 정보를 추출하여 반환합니다.
    
    인증된 사용자만 접근 가능하며, 사용자 ID, 이메일, 이름, 사용자 타입(admin/premium/basic), 계정 생성일 등의 정보를 반환합니다.
    """
    return current_user

@router.get("/{user_id}", response_model=UserResponse, summary="특정 사용자 정보 조회")
async def get_user(
    user_id: str,
    current_user: dict = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """
    특정 사용자 정보 조회
    
    사용자 ID를 통해 특정 사용자의 정보를 조회합니다.
    
    - **user_id**: 조회할 사용자의 고유 ID
    
    인증된 사용자만 접근 가능하며, 존재하지 않는 사용자 ID인 경우 404 에러가 반환됩니다.
    """
    try:
        user = await user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다")
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/admin/all", summary="[관리자] 모든 사용자 목록 조회 (비밀번호 해시 포함)")
async def get_all_users_with_password(
    current_user: dict = Depends(get_current_user)
):
    """
    [관리자 전용] 모든 사용자 목록 조회 (비밀번호 해시 포함)
    
    데이터베이스에 저장된 모든 사용자 정보를 조회합니다.
    비밀번호는 bcrypt로 해싱된 해시값으로 저장되어 있으며, 원본 비밀번호는 복구할 수 없습니다.
    
    **주의**: 이 엔드포인트는 관리자만 사용해야 합니다.
    """
    try:
        db = await get_database()
        collection = db['users']
        
        # 모든 사용자 조회
        users = await collection.find({}).to_list(length=1000)  # 최대 1000명
        
        # _id 제거 및 포맷팅
        result = []
        for user in users:
            user.pop('_id', None)
            result.append({
                'user_id': user.get('user_id'),
                'username': user.get('username'),
                'password_hash': user.get('password'),  # 해시된 비밀번호
                'name': user.get('name'),
                'user_type': user.get('user_type', 'basic'),
                'file_upload_count': user.get('file_upload_count', 0),
                'created_at': user.get('created_at')
            })
        
        return {
            'total': len(result),
            'users': result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/admin/{user_id}/full", summary="[관리자] 특정 사용자 상세 정보 조회 (비밀번호 해시 포함)")
async def get_user_full_info(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    [관리자 전용] 특정 사용자 상세 정보 조회 (비밀번호 해시 포함)
    
    사용자 ID로 특정 사용자의 모든 정보를 조회합니다.
    비밀번호는 bcrypt로 해싱된 해시값으로 저장되어 있으며, 원본 비밀번호는 복구할 수 없습니다.
    
    - **user_id**: 조회할 사용자의 고유 ID
    
    **주의**: 이 엔드포인트는 관리자만 사용해야 합니다.
    """
    try:
        db = await get_database()
        collection = db['users']
        
        user = await collection.find_one({'user_id': user_id})
        if not user:
            raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다")
        
        user.pop('_id', None)
        return {
            'user_id': user.get('user_id'),
            'username': user.get('username'),
            'password_hash': user.get('password'),  # 해시된 비밀번호
            'name': user.get('name'),
            'user_type': user.get('user_type', 'basic'),
            'file_upload_count': user.get('file_upload_count', 0),
            'created_at': user.get('created_at')
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

