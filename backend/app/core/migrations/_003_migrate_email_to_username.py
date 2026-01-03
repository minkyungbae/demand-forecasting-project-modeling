"""
마이그레이션 003: email 필드를 username으로 마이그레이션
기존 email 필드가 있는 사용자 데이터를 username 필드로 변환합니다.
"""
from app.core.database import get_database

async def up():
    """email 필드를 username으로 마이그레이션"""
    db = await get_database()
    users_collection = db["users"]
    
    # email 필드가 있지만 username 필드가 없는 사용자 찾기 (배치 처리로 최적화)
    query = {
        "$or": [
            {"email": {"$exists": True}, "username": {"$exists": False}},
            {"email": {"$exists": True}, "username": None},
            {"email": {"$exists": True}, "username": ""}
        ]
    }
    
    # 배치 업데이트로 한 번에 처리 (더 빠름)
    result = await users_collection.update_many(
        query,
        [{"$set": {"username": "$email"}}]  # email 값을 username으로 복사
    )
    
    migrated_count = result.modified_count
    
    # email 인덱스가 있으면 삭제 (username 인덱스는 이미 001에서 생성됨)
    try:
        indexes = await users_collection.list_indexes().to_list(length=None)
        index_names = [idx.get("name") for idx in indexes]
        if "email_1" in index_names:
            await users_collection.drop_index("email_1")
    except:
        pass  # 인덱스가 없으면 무시

async def down():
    """마이그레이션 롤백 (username을 email로 복원)"""
    db = await get_database()
    users_collection = db["users"]
    
    # username 필드가 있지만 email 필드가 없는 사용자 찾기
    users_with_username = await users_collection.find({"username": {"$exists": True}}).to_list(length=None)
    
    for user in users_with_username:
        if "email" not in user or not user.get("email"):
            username_value = user.get("username")
            if username_value:
                await users_collection.update_one(
                    {"_id": user["_id"]},
                    {"$set": {"email": username_value}}
                )
    
    # username 인덱스 삭제하고 email 인덱스 생성
    try:
        await users_collection.drop_index("username_1")
    except:
        pass
    
    try:
        await users_collection.create_index("email", unique=True)
    except:
        pass

