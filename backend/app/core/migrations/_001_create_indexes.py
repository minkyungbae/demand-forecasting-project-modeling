"""
마이그레이션 001: 인덱스 생성
모든 컬렉션에 필요한 인덱스를 생성합니다.
"""
from app.core.database import get_database

# 파일명이 숫자로 시작하면 import가 안되므로 _ 접두사 사용
# 실제 파일명: 001_create_indexes.py
# import 시: _001_create_indexes

async def up():
    """마이그레이션 실행"""
    db = await get_database()
    
    # User Collection 인덱스
    users_collection = db["users"]
    await users_collection.create_index("user_id", unique=True)
    await users_collection.create_index("username", unique=True)
    print("  ✓ User Collection 인덱스 생성 완료")
    
    # Sales Collection 인덱스
    sales_collection = db["sales"]
    await sales_collection.create_index("file_id", unique=True)
    await sales_collection.create_index("user_id")
    await sales_collection.create_index([("upload_time", -1)])
    await sales_collection.create_index("sales_id")
    print("  ✓ Sales Collection 인덱스 생성 완료")
    
    # CSV Collection 인덱스
    csv_collection = db["csv"]
    await csv_collection.create_index([("file_id", 1), ("row_index", 1)])
    await csv_collection.create_index("user_id")
    await csv_collection.create_index("csv_id")
    print("  ✓ CSV Collection 인덱스 생성 완료")
    
    # Analysis Results Collection 인덱스
    analysis_collection = db["analysis_results"]
    await analysis_collection.create_index("file_id")
    await analysis_collection.create_index("user_id")
    await analysis_collection.create_index("results_id", unique=True)
    await analysis_collection.create_index("analysis_id")
    await analysis_collection.create_index([("created_at", -1)])
    print("  ✓ Analysis Results Collection 인덱스 생성 완료")
    
    # User Suggestions Collection 인덱스
    suggestions_collection = db["user_suggestions"]
    await suggestions_collection.create_index("file_id")
    await suggestions_collection.create_index("user_id")
    await suggestions_collection.create_index("sug_id", unique=True)
    await suggestions_collection.create_index([("created_at", -1)])
    print("  ✓ User Suggestions Collection 인덱스 생성 완료")
    
    # Feature Weights Collection 인덱스
    weights_collection = db["feature_weights"]
    await weights_collection.create_index("file_id")
    await weights_collection.create_index("user_id")
    await weights_collection.create_index("weight_id", unique=True)
    await weights_collection.create_index([("created_at", -1)])
    print("  ✓ Feature Weights Collection 인덱스 생성 완료")

async def down():
    """마이그레이션 롤백 (인덱스 삭제)"""
    db = await get_database()
    
    collections = [
        "users", "sales", "csv", "analysis_results",
        "user_suggestions", "feature_weights"
    ]
    
    for collection_name in collections:
        collection = db[collection_name]
        indexes = await collection.list_indexes().to_list(length=None)
        for index in indexes:
            if index["name"] != "_id_":  # 기본 _id 인덱스는 유지
                try:
                    await collection.drop_index(index["name"])
                except:
                    pass

