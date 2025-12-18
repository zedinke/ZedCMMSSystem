"""
Permission Utility Functions
Check user permissions for various features
"""

from typing import Optional, Union
from database.models import User
from services.context_service import get_app_context
from config.roles import (
    PERM_VIEW_DASHBOARD,
    PERM_VIEW_INVENTORY,
    PERM_EDIT_INVENTORY,
    PERM_VIEW_ASSETS,
    PERM_EDIT_ASSETS,
    PERM_VIEW_WORKSHEETS,
    PERM_CREATE_WORKSHEET,
    PERM_EDIT_WORKSHEET,
    PERM_VIEW_PM,
    PERM_EDIT_PM,
    PERM_VIEW_SETTINGS,
    PERM_MANAGE_USERS,
    PERM_MANAGE_PERMISSIONS,
    PERM_VIEW_DEVELOPER_TOOLS,
    PERM_VIEW_INVENTORY_AUDIT,
    ROLE_DEVELOPER,
)


def has_permission(user: Optional[Union[User, bool]], permission_key: str) -> bool:
    """Check if user has a specific permission
    
    Args:
        user: User object, None, or anything else (for backwards compatibility)
        permission_key: Permission key to check
    
    Returns:
        bool: True if user has permission
    
    Note: The update_permission_config function already sets permissions hierarchically
    (if supervisor has permission, all roles at or above supervisor level get it),
    so we only need to check direct permissions here.
    """
    # Use context instead of User object to avoid session issues
    ctx = get_app_context()
    if not ctx.is_authenticated():
        return False
    
    # Get permission value from context permissions dict
    # The permissions are already set hierarchically by update_permission_config,
    # so we only need to check if the user's role has the permission directly
    return ctx.permissions.get(permission_key, False)


def is_developer(user: Optional[Union[User, bool]] = None) -> bool:
    """Check if user has Developer role"""
    ctx = get_app_context()
    if not ctx.is_authenticated():
        return False
    return ctx.role == ROLE_DEVELOPER


def can_view_dashboard(user: Optional[Union[User, bool]] = None) -> bool:
    """Check if user can view dashboard"""
    return has_permission(user, PERM_VIEW_DASHBOARD)


def can_view_inventory(user: Optional[Union[User, bool]] = None) -> bool:
    """Check if user can view inventory"""
    return has_permission(user, PERM_VIEW_INVENTORY)


def can_edit_inventory(user: Optional[Union[User, bool]] = None) -> bool:
    """Check if user can edit inventory"""
    return has_permission(user, PERM_EDIT_INVENTORY)


def can_view_assets(user: Optional[Union[User, bool]] = None) -> bool:
    """Check if user can view assets"""
    return has_permission(user, PERM_VIEW_ASSETS)


def can_edit_assets(user: Optional[Union[User, bool]] = None) -> bool:
    """Check if user can edit assets"""
    return has_permission(user, PERM_EDIT_ASSETS)


def can_view_worksheets(user: Optional[Union[User, bool]] = None) -> bool:
    """Check if user can view worksheets"""
    return has_permission(user, PERM_VIEW_WORKSHEETS)


def can_create_worksheet(user: Optional[Union[User, bool]] = None) -> bool:
    """Check if user can create worksheets"""
    return has_permission(user, PERM_CREATE_WORKSHEET)


def can_edit_worksheet(user: Optional[Union[User, bool]] = None) -> bool:
    """Check if user can edit worksheets"""
    return has_permission(user, PERM_EDIT_WORKSHEET)


def can_view_pm(user: Optional[Union[User, bool]] = None) -> bool:
    """Check if user can view PM tasks"""
    return has_permission(user, PERM_VIEW_PM)


def can_edit_pm(user: Optional[Union[User, bool]] = None) -> bool:
    """Check if user can edit PM tasks"""
    return has_permission(user, PERM_EDIT_PM)


def can_view_settings(user: Optional[Union[User, bool]] = None) -> bool:
    """Check if user can view settings"""
    return has_permission(user, PERM_VIEW_SETTINGS)


def can_manage_users(user: Optional[Union[User, bool]] = None) -> bool:
    """Check if user can manage users"""
    return has_permission(user, PERM_MANAGE_USERS)


def can_manage_permissions(user: Optional[Union[User, bool]] = None) -> bool:
    """Check if user can manage role permissions"""
    # Use context to check role and permissions
    ctx = get_app_context()
    if not ctx.is_authenticated():
        return False
    
    # Developer role always can manage permissions
    if ctx.role == ROLE_DEVELOPER:
        return True
    
    # Check permission flag
    return has_permission(user, PERM_MANAGE_PERMISSIONS)


def can_view_developer_tools(user: Optional[Union[User, bool]] = None) -> bool:
    """Check if user can view developer tools (Developer role only)"""
    # Support both old and new permission key formats for compatibility
    from config.roles import PERM_DEVELOPER_TOOLS_VIEW, ROLE_DEVELOPER
    from services.context_service import get_app_context
    
    # First check if user is developer role (direct check)
    ctx = get_app_context()
    if ctx.is_authenticated() and ctx.role == ROLE_DEVELOPER:
        return True
    
    # Then check permissions (both old and new format)
    return has_permission(user, PERM_VIEW_DEVELOPER_TOOLS) or has_permission(user, PERM_DEVELOPER_TOOLS_VIEW)


def can_view_inventory_audit(user: Optional[Union[User, bool]] = None) -> bool:
    """Check if user can view inventory audit"""
    return has_permission(user, PERM_VIEW_INVENTORY_AUDIT)


def can_view_storage(user: Optional[Union[User, bool]] = None) -> bool:
    """Check if user can view storage locations"""
    return has_permission(user, "storage_view")
