"""
마이그레이션 수동 실행 스크립트
앱을 시작하지 않고 마이그레이션만 실행하고 싶을 때 사용
"""
import asyncio
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.database import init_db, close_db
from app.core.migrations.migration_manager import MigrationManager

async def main():
    """마이그레이션 실행"""
    print("🔄 마이그레이션 시작...")
    
    try:
        # 데이터베이스 연결
        await init_db()
        
        # 마이그레이션 실행
        migration_manager = MigrationManager()
        await migration_manager.run_migrations()
        
        print("✅ 모든 마이그레이션이 완료되었습니다.")
        
    except Exception as e:
        print(f"❌ 마이그레이션 실패: {str(e)}")
        sys.exit(1)
    finally:
        await close_db()

if __name__ == "__main__":
    asyncio.run(main())

