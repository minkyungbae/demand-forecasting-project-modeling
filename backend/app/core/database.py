from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

class Database:
    client: AsyncIOMotorClient = None

database = Database()

async def get_database():
    """MongoDB 데이터베이스 인스턴스 반환"""
    return database.client[settings.DATABASE_NAME]

async def init_db():
    """MongoDB 연결 초기화 및 마이그레이션 실행"""
    import asyncio
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            database.client = AsyncIOMotorClient(
                settings.MONGODB_URL, 
                serverSelectionTimeoutMS=10000,
                connectTimeoutMS=10000
            )
            # 연결 테스트
            await database.client.admin.command('ping')
            print(f"MongoDB 연결 성공: {settings.MONGODB_URL}")
            break
        except Exception as e:
            error_msg = str(e)
            if attempt < max_retries - 1:
                print(f"MongoDB 연결 실패 (시도 {attempt + 1}/{max_retries})")
                print(f"   오류: {error_msg[:200]}...")  # 긴 에러 메시지 일부만 표시
                print(f"   {retry_delay}초 후 재시도...")
                await asyncio.sleep(retry_delay)
            else:
                print("\n" + "="*60)
                print("MongoDB 연결 실패 (최대 재시도 횟수 초과)")
                print("="*60)
                print(f"연결 URL: {settings.MONGODB_URL}")
                print(f"오류: {error_msg}")
                print("\n해결 방법:")
                print("1. MongoDB 서버가 실행 중인지 확인하세요")
                print("   - Docker 사용 시: docker-compose up -d mongodb")
                print("   - 로컬 설치 시: mongod 서비스가 실행 중인지 확인")
                print("2. MongoDB 포트(기본값: 27017)가 열려있는지 확인하세요")
                print("3. 방화벽 설정을 확인하세요")
                print("="*60 + "\n")
                raise ConnectionError(
                    f"MongoDB 연결 실패: {settings.MONGODB_URL}. "
                    "MongoDB 서버가 실행 중인지 확인하세요."
                ) from e
    
    # 마이그레이션 실행
    from app.core.migrations.migration_manager import MigrationManager
    migration_manager = MigrationManager()
    try:
        await migration_manager.run_migrations()
        print("데이터베이스 마이그레이션 완료")
    except Exception as e:
        print(f"마이그레이션 오류: {str(e)}")
        # 마이그레이션 실패해도 앱은 계속 실행

async def close_db():
    """MongoDB 연결 종료"""
    if database.client:
        database.client.close()

