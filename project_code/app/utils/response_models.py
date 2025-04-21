from pydantic import BaseModel
from typing import Any, Dict, List, Optional


class APIResponse(BaseModel):
    """Base API response model"""

    success: bool
    data: Optional[Any] = None
    message: Optional[str] = None
    code: int
    errors: Optional[List[Dict[str, Any]]] = None


class ErrorResponse(APIResponse):
    """Error response model"""

    success: bool = False
    errors: List[Dict[str, Any]]


class CommonResponse(APIResponse):
    """Common successful response model"""

    success: bool = True


class PaginatedResponse(APIResponse):
    """Paginated response model"""

    success: bool = True
    pagination: Dict[str, Any]
    timestamp: Optional[str] = None


class SuccessResponse(CommonResponse):
    """Successful response model with data"""

    data: Any


class PaginatedSuccessResponse(PaginatedResponse):
    """Successful paginated response model"""

    data: List[Any]
    pagination: Dict[str, Any] = {
        "page": 1,
        "size": 10,
        "total_count": 0,
        "total_pages": 0,
    }
