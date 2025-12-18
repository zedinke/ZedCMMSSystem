"""
Pagination utilities
"""
from typing import Tuple, List, TypeVar, Generic
from sqlalchemy.orm import Query

T = TypeVar('T')


class PaginatedResult(Generic[T]):
    """Paginated query result"""
    def __init__(
        self,
        items: List[T],
        total: int,
        page: int,
        per_page: int
    ):
        self.items = items
        self.total = total
        self.page = page
        self.per_page = per_page
        self.pages = (total + per_page - 1) // per_page if per_page > 0 else 0
        self.has_prev = page > 1
        self.has_next = page < self.pages
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API responses"""
        return {
            "items": self.items,
            "total": self.total,
            "page": self.page,
            "per_page": self.per_page,
            "pages": self.pages,
            "has_prev": self.has_prev,
            "has_next": self.has_next
        }


def paginate_query(
    query: Query[T],
    page: int = 1,
    per_page: int = 20,
    max_per_page: int = 100
) -> PaginatedResult[T]:
    """
    Paginate a SQLAlchemy query
    
    Args:
        query: SQLAlchemy query
        page: Page number (1-based)
        per_page: Items per page
        max_per_page: Maximum items per page
    
    Returns:
        PaginatedResult with items and metadata
    """
    # Validate and limit per_page
    per_page = min(per_page, max_per_page)
    per_page = max(1, per_page)
    page = max(1, page)
    
    # Get total count
    total = query.count()
    
    # Get paginated items
    offset = (page - 1) * per_page
    items = query.offset(offset).limit(per_page).all()
    
    return PaginatedResult(
        items=items,
        total=total,
        page=page,
        per_page=per_page
    )
