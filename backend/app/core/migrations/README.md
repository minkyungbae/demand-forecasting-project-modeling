# MongoDB 마이그레이션 시스템

## 개요

MongoDB는 스키마리스 데이터베이스이지만, 인덱스 생성, 초기 데이터 설정, 데이터 구조 변경 등이 필요합니다. 이 마이그레이션 시스템은 이러한 작업을 자동화합니다.

## 구조

```
app/core/migrations/
├── __init__.py              # 마이그레이션 목록 정의
├── migration_manager.py      # 마이그레이션 실행 관리자
├── _001_create_indexes.py    # 인덱스 생성
├── _002_add_default_admin.py # 기본 관리자 계정 (선택적)
└── README.md                 # 이 파일
```

## 동작 방식

1. **앱 시작 시 자동 실행**: `app/core/database.py`의 `init_db()` 함수에서 자동으로 마이그레이션을 실행합니다.

2. **마이그레이션 상태 추적**: `migrations` 컬렉션에 적용된 마이그레이션 버전을 저장하여 중복 실행을 방지합니다.

3. **버전 관리**: 각 마이그레이션은 고유한 버전 번호를 가지며, 순서대로 실행됩니다.

## 새 마이그레이션 추가하기

### 1. 마이그레이션 파일 생성

```python
# app/core/migrations/_003_your_migration.py

"""
마이그레이션 003: 설명
"""

async def up():
    """마이그레이션 실행"""
    from app.core.database import get_database
    db = await get_database()
    
    # 마이그레이션 로직 작성
    collection = db["your_collection"]
    # ... 작업 수행
    
    print("  ✓ 마이그레이션 작업 완료")

async def down():
    """마이그레이션 롤백 (선택적)"""
    # 롤백 로직 작성
    pass
```

### 2. 마이그레이션 목록에 추가

`app/core/migrations/__init__.py` 파일에 추가:

```python
from app.core.migrations import _003_your_migration

migrations_list = [
    # ... 기존 마이그레이션들
    {
        "version": "003",
        "description": "설명",
        "up": _003_your_migration.up,
    },
]
```

## 마이그레이션 실행

### 자동 실행 (기본)
앱을 시작하면 자동으로 마이그레이션이 실행됩니다:

```bash
python run.py
```

### 수동 실행
필요한 경우 별도 스크립트로 실행할 수 있습니다:

```python
from app.core.migrations.migration_manager import MigrationManager

async def main():
    manager = MigrationManager()
    await manager.run_migrations()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## 마이그레이션 상태 확인

MongoDB에서 직접 확인:

```javascript
use forecastly
db.migrations.find().sort({version: 1})
```

## 주의사항

1. **버전 번호는 순차적으로**: 001, 002, 003... 순서대로 증가해야 합니다.

2. **파일명 규칙**: 숫자로 시작하는 파일명은 Python에서 import가 안되므로 `_001_` 형식을 사용합니다.

3. **멱등성**: 마이그레이션은 여러 번 실행해도 안전해야 합니다. 이미 적용된 마이그레이션은 건너뜁니다.

4. **롤백**: `down()` 함수는 선택적이지만, 필요시 롤백을 지원할 수 있습니다.

## 예제 마이그레이션

### 인덱스 생성
```python
async def up():
    db = await get_database()
    collection = db["users"]
    await collection.create_index("email", unique=True)
```

### 데이터 마이그레이션
```python
async def up():
    db = await get_database()
    collection = db["users"]
    
    # 모든 문서에 새 필드 추가
    await collection.update_many(
        {},
        {"$set": {"new_field": "default_value"}}
    )
```

### 컬렉션 이름 변경
```python
async def up():
    db = await get_database()
    await db["old_collection"].rename("new_collection")
```

