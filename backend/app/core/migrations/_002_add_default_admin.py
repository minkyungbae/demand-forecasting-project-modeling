"""
마이그레이션 002: 기본 관리자 계정 생성 (선택적)
개발 환경에서만 사용하거나 제거할 수 있습니다.
"""
from app.core.database import get_database
from app.core.security import get_password_hash
from datetime import datetime

async def up():
    """기본 관리자 계정 생성"""
    db = await get_database()
    users_collection = db["users"]
    
    # 이미 admin 계정이 있는지 확인
    existing_admin = await users_collection.find_one({"username": "admin@forecastly.com"})
    if existing_admin:
        return
    
    # 기본 관리자 계정 생성
    admin_user = {
        "user_id": "admin_001",
        "username": "admin@forecastly.com",
        "password": get_password_hash("admin123"),  # 프로덕션에서는 변경 필수!
        "user_type": "admin",
        "file_upload_count": 0,
        "name": "Administrator",
        "created_at": datetime.now()
    }
    
    await users_collection.insert_one(admin_user)

async def down():
    """기본 관리자 계정 삭제"""
    db = await get_database()
    users_collection = db["users"]
    await users_collection.delete_one({"username": "admin@forecastly.com"})

