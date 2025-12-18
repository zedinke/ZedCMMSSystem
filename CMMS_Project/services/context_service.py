"""
Application Context Service
Holds current user/session/language context in memory
"""

from dataclasses import dataclass, field
from typing import Optional, Dict


@dataclass
class AppContext:
    user_id: Optional[int] = None
    username: Optional[str] = None
    full_name: Optional[str] = None  # Add full_name to context
    email: Optional[str] = None
    role: Optional[str] = None
    language: str = "hu"
    token: Optional[str] = None
    permissions: Dict = field(default_factory=dict)

    def is_authenticated(self) -> bool:
        return self.user_id is not None


# Global singleton context (desktop app single-user at a time)
_context = AppContext()


def get_app_context() -> AppContext:
    return _context


def set_app_context(user_info: dict, token: str):
    _context.user_id = user_info.get("user_id")
    _context.username = user_info.get("username")
    _context.full_name = user_info.get("full_name")  # Store full_name in context
    _context.email = user_info.get("email")
    _context.role = user_info.get("role")
    _context.language = user_info.get("language", "hu")
    _context.permissions = user_info.get("permissions", {})
    _context.token = token


def clear_app_context():
    global _context
    _context = AppContext()


def get_current_user():
    """Get current user object from database based on context"""
    if not _context.user_id:
        return None
    
    from services import user_service
    return user_service.get_user(_context.user_id)


def get_user(user_id: int):
    """Get user object from database by user ID"""
    from services import user_service
    return user_service.get_user(user_id)


def get_current_user_id() -> Optional[int]:
    """Get current user ID from context"""
    return _context.user_id


def get_client_ip() -> Optional[str]:
    """Get client IP address (for desktop app, returns None)"""
    # For desktop app, IP is not available
    # This can be extended for web/API usage
    return None


def get_user_agent() -> Optional[str]:
    """Get user agent string (for desktop app, returns app identifier)"""
    # For desktop app, return app identifier
    from config.app_config import APP_NAME, APP_VERSION
    return f"{APP_NAME}/{APP_VERSION}"