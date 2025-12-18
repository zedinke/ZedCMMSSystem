"""
JWT Token Security and Authentication
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
import os

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenData(BaseModel):
    """JWT token payload"""
    user_id: int
    username: str
    role_name: str


class TokenResponse(BaseModel):
    """Token response structure"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: int
    username: str
    role_name: str


def create_access_token(user_id: int, username: str, role_name: str) -> TokenResponse:
    """
    Create JWT access token
    
    Args:
        user_id: User ID
        username: Username
        role_name: Role name
        
    Returns:
        TokenResponse with token and metadata
    """
    expires_delta = timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    expire = datetime.utcnow() + expires_delta
    
    to_encode = {
        "sub": username,
        "user_id": user_id,
        "role_name": role_name,
        "exp": expire
    }
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return TokenResponse(
        access_token=encoded_jwt,
        token_type="bearer",
        expires_in=int(expires_delta.total_seconds()),
        user_id=user_id,
        username=username,
        role_name=role_name
    )


def verify_token(token: str) -> Optional[TokenData]:
    """
    Verify JWT token and return token data
    
    Args:
        token: JWT token string
        
    Returns:
        TokenData if valid, None if invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        username: str = payload.get("sub")
        role_name: str = payload.get("role_name")
        
        if user_id is None or username is None or role_name is None:
            return None
        
        return TokenData(user_id=user_id, username=username, role_name=role_name)
    except JWTError:
        return None


def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)
