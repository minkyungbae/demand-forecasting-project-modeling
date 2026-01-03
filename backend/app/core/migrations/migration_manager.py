from typing import List, Dict
from datetime import datetime
from app.core.database import get_database

class MigrationManager:
    """MongoDB 마이그레이션 관리자"""
    
    MIGRATION_COLLECTION = "migrations"
    
    async def ensure_migration_collection(self):
        """마이그레이션 상태 추적 컬렉션 생성"""
        db = await get_database()
        collection = db[self.MIGRATION_COLLECTION]
        
        # 인덱스 생성
        await collection.create_index("version", unique=True)
    
    async def get_applied_migrations(self) -> List[str]:
        """적용된 마이그레이션 목록 조회"""
        db = await get_database()
        collection = db[self.MIGRATION_COLLECTION]
        cursor = collection.find({}, {"version": 1})
        migrations = await cursor.to_list(length=None)
        return [m["version"] for m in migrations]
    
    async def mark_migration_applied(self, version: str, description: str):
        """마이그레이션 적용 완료 표시"""
        db = await get_database()
        collection = db[self.MIGRATION_COLLECTION]
        await collection.insert_one({
            "version": version,
            "description": description,
            "applied_at": datetime.now()
        })
    
    async def run_migrations(self):
        """모든 마이그레이션 실행"""
        from app.core.migrations import migrations_list
        
        await self.ensure_migration_collection()
        applied = await self.get_applied_migrations()
        
        for migration in migrations_list:
            if migration["version"] not in applied:
                try:
                    await migration["up"]()
                    await self.mark_migration_applied(
                        migration["version"],
                        migration["description"]
                    )
                except Exception as e:
                    print(f"마이그레이션 실패: {migration['version']} - {str(e)}")
                    raise

