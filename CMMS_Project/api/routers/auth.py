"""
Authentication Router
Login and token generation endpoints
"""

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from api.schemas import LoginRequest, ErrorResponse
from api.security import verify_password, create_access_token, TokenResponse
from api.dependencies import get_db
from database.models import User
import logging

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = logging.getLogger(__name__)


@router.post(
    "/login",
    response_model=TokenResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Invalid credentials"},
        422: {"model": ErrorResponse, "description": "Validation error"}
    }
)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    User login endpoint
    
    Returns JWT token for authenticated user.
    
    **Request Body:**
    - `username`: User's username
    - `password`: User's password
    
    **Response:**
    - `access_token`: JWT token for subsequent requests
    - `token_type`: Always "bearer"
    - `expires_in`: Token expiration time in seconds
    - `user_id`: Authenticated user's ID
    - `username`: Authenticated user's username
    - `role_name`: Authenticated user's role
    
    **Example:**
    ```bash
    curl -X POST "http://localhost:8000/api/auth/login" \\
      -H "Content-Type: application/json" \\
      -d '{"username": "admin", "password": "password123"}'
    ```
    
    **Response Example:**
    ```json
    {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "token_type": "bearer",
      "expires_in": 86400,
      "user_id": 1,
      "username": "admin",
      "role_name": "admin"
    }
    ```
    """
    try:
        # Query user with eager-loaded role
        stmt = select(User).where(User.username == request.username).options(
            joinedload(User.role)
        )
        user = db.execute(stmt).scalars().first()
        
        if not user:
            logger.warning(f"Login attempt with non-existent username: {request.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # Verify password
        if not verify_password(request.password, user.password_hash):
            logger.warning(f"Failed login attempt for user: {request.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # Create and return token
        token_response = create_access_token(
            user_id=user.id,
            username=user.username,
            role_name=user.role.name if user.role else "user"
        )
        
        logger.info(f"Successful login for user: {request.username}")
        return token_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )
