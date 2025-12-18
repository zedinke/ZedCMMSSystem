"""
Routers package initialization
"""

from .auth import router as auth_router
from .users import router as users_router
from .machines import router as machines_router
from .worksheets import router as worksheets_router
from .assets import router as assets_router
from .permissions import router as permissions_router

__all__ = [
    "auth_router",
    "users_router", 
    "machines_router",
    "worksheets_router",
    "assets_router",
    "permissions_router"
]
