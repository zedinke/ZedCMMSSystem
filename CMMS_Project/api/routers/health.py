"""
Health Check Router
API health and status endpoints
"""

from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from pydantic import BaseModel
import logging

router = APIRouter(prefix="/health", tags=["Health"])
logger = logging.getLogger(__name__)


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime
    version: str = "1.0.0"


@router.get(
    "/",
    response_model=HealthResponse
)
async def health_check():
    """
    API health check endpoint
    
    Returns current API status and timestamp.
    
    **Example:**
    ```bash
    curl -X GET "http://localhost:8000/api/health/"
    ```
    
    **Response:**
    ```json
    {
      "status": "healthy",
      "timestamp": "2025-12-13T10:30:45.123456",
      "version": "1.0.0"
    }
    ```
    """
    try:
        return HealthResponse(
            status="healthy",
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unhealthy"
        )


@router.get("/ready")
async def readiness_check():
    """
    Readiness check endpoint
    
    Returns 200 if API is ready to handle requests.
    """
    return {"ready": True}
