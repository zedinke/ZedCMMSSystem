"""
Users Router
User CRUD operations with role-based access control
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, func
from typing import Optional
from api.schemas import (
    UserCreate, UserUpdate, UserResponse, UserListResponse, ErrorResponse
)
from api.dependencies import get_db, get_current_user, require_role, get_user_language
from api.security import TokenData, hash_password
from database.models import User, Role
from services.user_service import (
    create_user as service_create_user,
    list_all_users,
    update_user_details,
    anonymize_user as service_anonymize_user,
    reset_user_password
)
from utils.localization_helper import get_localized_error
import logging

router = APIRouter(prefix="/users", tags=["Users"])
logger = logging.getLogger(__name__)


@router.get(
    "/",
    response_model=UserListResponse,
    dependencies=[Depends(get_current_user)]
)
async def list_users(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    role_name: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status")
):
    """
    List all users with pagination and filtering
    
    **Query Parameters:**
    - `skip`: Number of records to skip (default: 0)
    - `limit`: Number of records to return (default: 10, max: 100)
    - `role_name`: Filter by role name (optional)
    - `status`: Filter by status (optional)
    
    **Example:**
    ```bash
    curl -X GET "http://localhost:8000/api/users?skip=0&limit=10&role_name=manager" \\
      -H "Authorization: Bearer <token>"
    ```
    """
    try:
        # Build query
        stmt = select(User).options(joinedload(User.role)).offset(skip).limit(limit)
        
        if role_name:
            stmt = stmt.join(Role).where(Role.name == role_name)
        
        # Execute query
        users = db.execute(stmt).scalars().unique().all()
        
        # Get total count
        count_stmt = select(User)
        if role_name:
            count_stmt = count_stmt.join(Role).where(Role.name == role_name)
        total = db.execute(select(func.count()).select_from(User)).scalar()
        
        return UserListResponse(
            total=total,
            items=[UserResponse.from_orm(user) for user in users]
        )
    except Exception as e:
        logger.error(f"Error listing users: {str(e)}")
        lang_code = "en"  # Default for API errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=get_localized_error("database.query_failed", lang_code=lang_code)
        )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[Depends(get_current_user)]
)
async def get_user(
    user_id: int, 
    db: Session = Depends(get_db),
    lang_code: str = Depends(get_user_language)
):
    """
    Get user by ID
    
    **Path Parameters:**
    - `user_id`: User ID
    
    **Example:**
    ```bash
    curl -X GET "http://localhost:8000/api/users/1" \\
      -H "Authorization: Bearer <token>"
    ```
    """
    try:
        stmt = select(User).where(User.id == user_id).options(joinedload(User.role))
        user = db.execute(stmt).scalars().first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse.from_orm(user)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=get_localized_error("database.query_failed", lang_code=lang_code)
        )


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse},
        409: {"model": ErrorResponse}
    }
)
async def create_user(
    user_data: UserCreate,
    current_user: TokenData = Depends(require_role("admin", "manager")),
    db: Session = Depends(get_db),
    lang_code: str = Depends(get_user_language)
):
    """
    Create new user (requires admin or manager role)
    
    **Request Body:**
    - `username`: Unique username
    - `email`: User email
    - `full_name`: User's full name (optional)
    - `phone`: User's phone number (optional)
    - `role_id`: Role ID
    
    **Example:**
    ```bash
    curl -X POST "http://localhost:8000/api/users/" \\
      -H "Authorization: Bearer <token>" \\
      -H "Content-Type: application/json" \\
      -d '{
        "username": "jsmith",
        "email": "john@company.com",
        "full_name": "John Smith",
        "phone": "+36301234567",
        "role_id": 2
      }'
    ```
    """
    try:
        # Check if username exists
        stmt = select(User).where(User.username == user_data.username)
        if db.execute(stmt).scalars().first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=get_localized_error("validation.username_exists", lang_code=lang_code)
            )
        
        # Check if email exists
        stmt = select(User).where(User.email == user_data.email)
        if db.execute(stmt).scalars().first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=get_localized_error("duplicate_email", lang_code=lang_code)
            )
        
        # Create user
        new_user = service_create_user(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            phone=user_data.phone,
            role_id=user_data.role_id,
            session=db
        )
        
        # Refresh to get role relationship
        db.refresh(new_user, ["role"])
        
        logger.info(f"User created: {user_data.username} by {current_user.username}")
        return UserResponse.from_orm(new_user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=get_localized_error("database.query_failed", lang_code=lang_code)
        )


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    responses={
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse}
    }
)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: TokenData = Depends(require_role("admin", "manager")),
    db: Session = Depends(get_db),
    lang_code: str = Depends(get_user_language)
):
    """
    Update user (requires admin or manager role)
    
    **Path Parameters:**
    - `user_id`: User ID to update
    
    **Request Body:** Any of these fields
    - `username`: New username (optional)
    - `email`: New email (optional)
    - `full_name`: New full name (optional)
    - `phone`: New phone number (optional)
    - `role_id`: New role ID (optional)
    
    **Example:**
    ```bash
    curl -X PUT "http://localhost:8000/api/users/5" \\
      -H "Authorization: Bearer <token>" \\
      -H "Content-Type: application/json" \\
      -d '{"email": "john.new@company.com"}'
    ```
    """
    try:
        # Check if user exists
        stmt = select(User).where(User.id == user_id)
        user = db.execute(stmt).scalars().first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=get_localized_error("user_not_found", lang_code=lang_code)
            )
        
        # Update fields
        update_dict = user_data.dict(exclude_unset=True)
        
        if "username" in update_dict and update_dict["username"] != user.username:
            stmt = select(User).where(User.username == update_dict["username"])
            if db.execute(stmt).scalars().first():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=get_localized_error("validation.username_exists", lang_code=lang_code)
                )
        
        if "email" in update_dict and update_dict["email"] != user.email:
            stmt = select(User).where(User.email == update_dict["email"])
            if db.execute(stmt).scalars().first():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=get_localized_error("duplicate_email", lang_code=lang_code)
                )
        
        # Use service to update
        updated_user = update_user_details(
            user_id=user_id,
            username=update_dict.get("username"),
            full_name=update_dict.get("full_name"),
            phone=update_dict.get("phone"),
            email=update_dict.get("email"),
            role_name=None,  # Handle role_id separately
            session=db
        )
        
        if "role_id" in update_dict:
            updated_user.role_id = update_dict["role_id"]
            db.commit()
        
        db.refresh(updated_user, ["role"])
        logger.info(f"User {user_id} updated by {current_user.username}")
        return UserResponse.from_orm(updated_user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=get_localized_error("database.query_failed", lang_code=lang_code)
        )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"model": ErrorResponse},
        403: {"model": ErrorResponse}
    }
)
async def delete_user(
    user_id: int,
    current_user: TokenData = Depends(require_role("admin")),
    db: Session = Depends(get_db),
    lang_code: str = Depends(get_user_language)
):
    """
    Delete user (admin only)
    
    **Path Parameters:**
    - `user_id`: User ID to delete
    
    **Example:**
    ```bash
    curl -X DELETE "http://localhost:8000/api/users/5" \\
      -H "Authorization: Bearer <token>"
    ```
    """
    try:
        # Check if user exists
        stmt = select(User).where(User.id == user_id)
        user = db.execute(stmt).scalars().first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=get_localized_error("user_not_found", lang_code=lang_code)
            )
        
        # Don't allow anonymizing admin/developer users
        if user.role and user.role.name in ["admin", "Developer"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=get_localized_error("cannot_anonymize_developer", lang_code=lang_code)
            )
        
        # Use anonymize_user instead of delete_user (GDPR compliant)
        service_anonymize_user(user_id=user_id, anonymized_by_user_id=current_user.user_id, session=db)
        logger.info(f"User {user_id} deleted by {current_user.username}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=get_localized_error("database.query_failed", lang_code=lang_code)
        )


@router.post(
    "/{user_id}/reset-password",
    response_model=UserResponse,
    responses={404: {"model": ErrorResponse}}
)
async def reset_password(
    user_id: int,
    current_user: TokenData = Depends(require_role("admin", "manager")),
    db: Session = Depends(get_db),
    lang_code: str = Depends(get_user_language)
):
    """
    Reset user password to default (requires admin or manager role)
    
    **Path Parameters:**
    - `user_id`: User ID
    
    **Example:**
    ```bash
    curl -X POST "http://localhost:8000/api/users/5/reset-password" \\
      -H "Authorization: Bearer <token>"
    ```
    """
    try:
        stmt = select(User).where(User.id == user_id)
        user = db.execute(stmt).scalars().first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=get_localized_error("user_not_found", lang_code=lang_code)
            )
        
        reset_user_password(user_id=user_id, session=db)
        db.refresh(user, ["role"])
        
        logger.info(f"Password reset for user {user_id} by {current_user.username}")
        return UserResponse.from_orm(user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resetting password for user {user_id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=get_localized_error("database.query_failed", lang_code=lang_code)
        )
