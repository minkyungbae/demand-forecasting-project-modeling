"""
관리자 계정 생성/삭제 스크립트

사용법:
    생성: python scripts/create_admin.py create
    삭제: python scripts/create_admin.py delete
"""
import asyncio
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.database import init_db, close_db
from app.core.migrations._002_add_default_admin import up, down


async def main():
    if len(sys.argv) < 2:
        print("사용법:")
        print("  python scripts/create_admin.py create   # 관리자 계정 생성")
        print("  python scripts/create_admin.py delete   # 관리자 계정 삭제")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    try:
        # DB 연결 초기화
        await init_db()
        
        if command == "create":
            print("관리자 계정 생성 중...")
            await up()
            print("완료!")
        elif command == "delete":
            print("관리자 계정 삭제 중...")
            await down()
            print("완료!")
        else:
            print(f"❌ 알 수 없는 명령어: {command}")
            print("사용법: python scripts/create_admin.py [create|delete]")
            sys.exit(1)
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # DB 연결 종료
        await close_db()


if __name__ == "__main__":
    asyncio.run(main())

