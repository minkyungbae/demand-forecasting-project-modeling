from typing import List, Dict
from datetime import datetime
import uuid

def generate_id(prefix: str = "") -> str:
    """고유 ID 생성"""
    if prefix:
        return f"{prefix}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    return str(uuid.uuid4())

def format_datetime(dt: datetime) -> str:
    """날짜시간 포맷팅"""
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def paginate_list(items: List, page: int, page_size: int) -> Dict:
    """리스트 페이지네이션"""
    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size
    paginated_items = items[start:end]
    
    return {
        'items': paginated_items,
        'total': total,
        'page': page,
        'page_size': page_size,
        'total_pages': (total + page_size - 1) // page_size
    }

