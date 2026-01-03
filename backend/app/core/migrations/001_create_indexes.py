"""
마이그레이션 001: 인덱스 생성
모든 컬렉션에 필요한 인덱스를 생성합니다.
"""
from app.core.database import get_database

# 파일명이 숫자로 시작하면 import가 안되므로 _ 접두사 사용
# 실제 파일명: 001_create_indexes.py
# import 시: _001_create_indexes

async def create_index_if_not_exists(collection, index_spec, **kwargs):
    """인덱스가 없으면 생성"""
    try:
        indexes = await collection.list_indexes().to_list(length=None)
        index_names = [idx.get("name") for idx in indexes]
        
        # 인덱스 이름 생성 (MongoDB 자동 생성 규칙)
        if isinstance(index_spec, str):
            index_name = f"{index_spec}_1"
        elif isinstance(index_spec, list):
            index_name = "_".join([f"{field}_{direction}" for field, direction in index_spec])
        else:
            index_name = str(index_spec)
        
        if index_name not in index_names:
            await collection.create_index(index_spec, **kwargs)
            return True
        return False
    except Exception as e:
        # 인덱스 생성 실패 시 무시 (이미 존재할 수 있음)
        return False

async def up():
    """마이그레이션 실행"""
    db = await get_database()
    
    # User Collection 인덱스
    users_collection = db["users"]
    await create_index_if_not_exists(users_collection, "user_id", unique=True)
    await create_index_if_not_exists(users_collection, "username", unique=True)
    
    # Sales Collection 인덱스
    sales_collection = db["sales"]
    await create_index_if_not_exists(sales_collection, "file_id", unique=True)
    await create_index_if_not_exists(sales_collection, "user_id")
    await create_index_if_not_exists(sales_collection, [("upload_time", -1)])
    await create_index_if_not_exists(sales_collection, "sales_id")
    
    # CSV Collection 인덱스
    csv_collection = db["csv"]
    await create_index_if_not_exists(csv_collection, [("file_id", 1), ("row_index", 1)])
    await create_index_if_not_exists(csv_collection, "user_id")
    await create_index_if_not_exists(csv_collection, "csv_id")
    
    # Analysis Results Collection 인덱스
    analysis_collection = db["analysis_results"]
    await create_index_if_not_exists(analysis_collection, "file_id")
    await create_index_if_not_exists(analysis_collection, "user_id")
    await create_index_if_not_exists(analysis_collection, "results_id", unique=True)
    await create_index_if_not_exists(analysis_collection, "analysis_id")
    await create_index_if_not_exists(analysis_collection, [("created_at", -1)])
    
    # User Suggestions Collection 인덱스
    suggestions_collection = db["user_suggestions"]
    await create_index_if_not_exists(suggestions_collection, "file_id")
    await create_index_if_not_exists(suggestions_collection, "user_id")
    await create_index_if_not_exists(suggestions_collection, "sug_id", unique=True)
    await create_index_if_not_exists(suggestions_collection, [("created_at", -1)])
    
    # Feature Weights Collection 인덱스
    weights_collection = db["feature_weights"]
    await create_index_if_not_exists(weights_collection, "file_id")
    await create_index_if_not_exists(weights_collection, "user_id")
    await create_index_if_not_exists(weights_collection, "weight_id", unique=True)
    await create_index_if_not_exists(weights_collection, [("created_at", -1)])
    
    # File Analysis Config Collection 인덱스
    config_collection = db["file_analysis_config"]
    await create_index_if_not_exists(config_collection, "file_id")
    await create_index_if_not_exists(config_collection, [("file_id", 1), ("target_column", 1)])
    await create_index_if_not_exists(config_collection, "user_id")
    await create_index_if_not_exists(config_collection, [("updated_at", -1)])
    await create_index_if_not_exists(config_collection, "config_id", unique=True)
    
    # Analysis Tasks Collection 인덱스
    tasks_collection = db["analysis_tasks"]
    await create_index_if_not_exists(tasks_collection, "task_id", unique=True)
    await create_index_if_not_exists(tasks_collection, "file_id")
    await create_index_if_not_exists(tasks_collection, "user_id")
    await create_index_if_not_exists(tasks_collection, "status")
    await create_index_if_not_exists(tasks_collection, [("created_at", -1)])
    
    # Statistics Collection 인덱스
    statistics_collection = db["statistics"]
    await create_index_if_not_exists(statistics_collection, "statistics_id", unique=True)
    await create_index_if_not_exists(statistics_collection, "file_id")
    await create_index_if_not_exists(statistics_collection, "user_id")
    await create_index_if_not_exists(statistics_collection, [("created_at", -1)])

async def down():
    """마이그레이션 롤백 (인덱스 삭제)"""
    db = await get_database()
    
    collections = [
        "users", "sales", "csv", "analysis_results",
        "user_suggestions", "feature_weights", "file_analysis_config", "analysis_tasks", "statistics"
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

