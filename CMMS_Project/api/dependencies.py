"""
FastAPI dependencies for authentication and authorization
"""

from fastapi import Depends, HTTPException, status, Header, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from api.security import verify_token, TokenData
from sqlalchemy.orm import Session
from database.connection import get_db as get_db_connection
from database.models import User

# Try to get SessionLocal from connection
try:
    from database.connection import SessionLocal
except (ImportError, AttributeError):
    # Fallback: try session_manager
    try:
        from database.session_manager import SessionLocal
    except ImportError:
        # Last resort: create from connection
        try:
            from database.connection import engine
            from sqlalchemy.orm import sessionmaker
            SessionLocal = sessionmaker(bind=engine)
        except:
            SessionLocal = None

# Fallback function if utils.localization_helper is not available
def get_localized_error(key: str, lang_code: str = "en") -> str:
    """Fallback localization helper"""
    error_messages = {
        "auth.invalid_token": "Invalid token",
        "auth.permissions.access_denied": "Access denied",
    }
    return error_messages.get(key, key)

security = HTTPBearer()


def get_db() -> Session:
    """
    Get database session dependency
    
    Yields:
        SQLAlchemy Session
    """
    # Use get_db from database.connection (works on server)
    db_gen = get_db_connection()
    try:
        db = next(db_gen)
        yield db
    finally:
        try:
            next(db_gen, None)
        except StopIteration:
            pass


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> TokenData:
    """
    Get current authenticated user from JWT token
    
    Args:
        credentials: HTTP Bearer token from Authorization header
        
    Returns:
        TokenData with user information
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials
    token_data = verify_token(token)
    
    if token_data is None:
        lang_code = "en"  # Default language for API errors
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=get_localized_error("auth.invalid_token", lang_code=lang_code),
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return token_data


def get_user_language(
    current_user: Optional[TokenData] = Depends(get_current_user),
    accept_language: Optional[str] = Header(None, alias="Accept-Language")
) -> str:
    """
    Get user's preferred language from Accept-Language header or user preferences
    
    Args:
        current_user: Current authenticated user (optional)
        accept_language: Accept-Language header value (e.g., "hu", "en", "hu,en;q=0.9")
    
    Returns:
        Language code (hu or en)
    """
    # Try to get from Accept-Language header first
    if accept_language:
        # Parse Accept-Language header (simple: just take first language)
        lang = accept_language.split(',')[0].split(';')[0].strip().lower()
        if lang in ['hu', 'en']:
            return lang
        # Handle full locale codes like "hu-HU" -> "hu"
        if lang.startswith('hu'):
            return 'hu'
        if lang.startswith('en'):
            return 'en'
    
    # Fall back to user's language preference
    if current_user:
        try:
            db_gen = get_db_connection()
            db = next(db_gen)
            try:
                user = db.query(User).filter_by(id=current_user.user_id).first()
                if user and user.language_preference:
                    return user.language_preference
            finally:
                try:
                    next(db_gen, None)
                except StopIteration:
                    pass
        except Exception:
            pass
    
    # Default to Hungarian
    return "hu"


def require_role(*allowed_roles: str):
    """
    Dependency factory to require specific roles
    
    Args:
        allowed_roles: List of allowed role names
        
    Returns:
        Dependency function that checks if current user has required role
    """
    async def check_role(
        current_user: TokenData = Depends(get_current_user),
        lang_code: str = Depends(get_user_language)
    ) -> TokenData:
        if current_user.role_name not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=get_localized_error("auth.permissions.access_denied", lang_code=lang_code)
            )
        return current_user
    
    return check_role
