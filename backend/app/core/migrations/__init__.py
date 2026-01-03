# Migrations module
from app.core.migrations.migration_manager import MigrationManager
from app.core.migrations import _001_create_indexes
from app.core.migrations import _003_migrate_email_to_username
# from app.core.migrations import _002_add_default_admin  # 선택적

# 마이그레이션 목록 (버전 순서대로)
migrations_list = [
    {
        "version": "001",
        "description": "인덱스 생성",
        "up": _001_create_indexes.up,
    },
    {
        "version": "003",
        "description": "email 필드를 username으로 마이그레이션",
        "up": _003_migrate_email_to_username.up,
    },
    # 기본 관리자 계정은 선택적이므로 주석 처리
    # {
    #     "version": "002",
    #     "description": "기본 관리자 계정 생성",
    #     "up": _002_add_default_admin.up,
    # },
]
