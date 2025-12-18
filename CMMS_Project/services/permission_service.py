"""
Permission Service
Role-based access control helper utilities with hierarchical role support
"""

from typing import Dict, List, Optional
from database.models import User, Role
from database.session_manager import SessionLocal
from config.roles import (
    ROLE_HIERARCHY,
    ALL_ROLES,
    MENU_ITEMS,
    PERM_MANAGE_PERMISSIONS,
)
from sqlalchemy.orm import Session


class PermissionError(Exception):
    """Custom exception for permission errors"""
    pass


def get_role_hierarchy_level(role_name: str) -> int:
    """Get hierarchy level for a role (lower number = lower in hierarchy)"""
    return ROLE_HIERARCHY.get(role_name, 999)


def get_roles_by_hierarchy_level(level: int) -> List[str]:
    """Get all roles at a specific hierarchy level"""
    return [role for role, role_level in ROLE_HIERARCHY.items() if role_level == level]


def get_roles_at_or_above(role_name: str) -> List[str]:
    """Get all roles at the same level or higher than the given role"""
    role_level = get_role_hierarchy_level(role_name)
    return [role for role, level in ROLE_HIERARCHY.items() if level >= role_level]


def has_permission(user: User, permission_key: str) -> bool:
    """Check if user has a specific permission flag"""
    if not user or not user.role:
        return False
    perms = user.role.permissions or {}
    return perms.get(permission_key, False)


def has_permission_hierarchical(role_name: str, permission_key: str, session: Session = None) -> bool:
    """Check if a role has permission using hierarchical logic"""
    should_close = False
    if session is None:
        session = SessionLocal()
        should_close = True
    
    try:
        role = session.query(Role).filter_by(name=role_name).first()
        if not role:
            return False
        
        perms = role.permissions or {}
        
        # First check direct permission
        if perms.get(permission_key, False):
            return True
        
        # Check if any role at same or lower level has this permission
        role_level = get_role_hierarchy_level(role_name)
        
        # Get all roles at same or lower level
        roles_to_check = [r for r, level in ROLE_HIERARCHY.items() if level <= role_level]
        
        for check_role_name in roles_to_check:
            if check_role_name == role_name:
                continue
            check_role = session.query(Role).filter_by(name=check_role_name).first()
            if check_role:
                check_perms = check_role.permissions or {}
                if check_perms.get(permission_key, False):
                    # Check if the role we're checking is actually lower in hierarchy
                    check_role_level = get_role_hierarchy_level(check_role_name)
                    if check_role_level < role_level:
                        return True
        
        return False
    finally:
        if should_close:
            session.close()


def can_manage_permissions(role_name: str, session: Session = None) -> bool:
    """Check if a role can manage permissions"""
    return has_permission_hierarchical(role_name, PERM_MANAGE_PERMISSIONS, session)


def require_permission(user: User, permission_key: str):
    """Raise error if user lacks permission"""
    if not has_permission(user, permission_key):
        raise PermissionError(f"Missing permission: {permission_key}")


def get_all_menu_items() -> List[Dict]:
    """Get all menu items with their available actions"""
    return list(MENU_ITEMS.values())


def reset_to_default_permissions(session: Session = None) -> None:
    """Reset all role permissions to default values (new format)"""
    from database.models import Role
    
    should_close = False
    if session is None:
        session = SessionLocal()
        should_close = True
    
    try:
        # Reset to empty permissions first
        for role_name in ALL_ROLES:
            role = session.query(Role).filter_by(name=role_name).first()
            if role:
                role.permissions = {}
        
        # Build config from default permissions (old format) and convert to new format
        # For now, just set basic permissions based on DEFAULT_PERMISSIONS
        # This is a simplified reset - full implementation would convert old format to new
        for role_name in ALL_ROLES:
            role = session.query(Role).filter_by(name=role_name).first()
            if role:
                # Start with empty permissions in new format
                role.permissions = {}
        
        session.commit()
    finally:
        if should_close:
            session.close()


def get_permission_summary(session: Session = None) -> Dict:
    """Get summary of permissions for all roles"""
    from database.models import Role
    
    should_close = False
    if session is None:
        session = SessionLocal()
        should_close = True
    
    try:
        roles = session.query(Role).all()
        summary = {}
        
        for role in roles:
            perms = role.permissions or {}
            summary[role.name] = {
                "total_permissions": len([p for p in perms.values() if p]),
                "total_available": len(perms),
                "level": ROLE_HIERARCHY.get(role.name, 999)
            }
        
        return summary
    finally:
        if should_close:
            session.close()


def get_permission_config(session: Session = None) -> Dict:
    """
    Get current permission configuration
    Returns a dict with structure:
    {
        "menu_items": {
            "inventory": {
                "view": "Karbantartó",  # Role name that has access
                "create": "Manager",
                ...
            },
            ...
        },
        "manage_permission_level": "Manager"  # Role name that can manage permissions
    }
    """
    should_close = False
    if session is None:
        session = SessionLocal()
        should_close = True
    
    try:
        config = {
            "menu_items": {},
            "manage_permission_level": None
        }
        
        # Get all roles
        roles = session.query(Role).all()
        role_permissions = {role.name: (role.permissions or {}) for role in roles}
        
        # For each menu item, find the lowest role that has each permission
        for menu_key, menu_info in MENU_ITEMS.items():
            config["menu_items"][menu_key] = {}
            
            for action in menu_info["actions"]:
                permission_key = f"{menu_key}_{action}"
                
                # Find the lowest role (by hierarchy) that has this permission
                lowest_role = None
                lowest_level = 999
                
                for role_name in ALL_ROLES:
                    perms = role_permissions.get(role_name, {})
                    if perms.get(permission_key, False):
                        level = get_role_hierarchy_level(role_name)
                        if level < lowest_level:
                            lowest_level = level
                            lowest_role = role_name
                
                config["menu_items"][menu_key][action] = lowest_role
        
        # Find manage_permissions level
        lowest_manage_role = None
        lowest_manage_level = 999
        
        for role_name in ALL_ROLES:
            perms = role_permissions.get(role_name, {})
            if perms.get(PERM_MANAGE_PERMISSIONS, False):
                level = get_role_hierarchy_level(role_name)
                if level < lowest_manage_level:
                    lowest_manage_level = level
                    lowest_manage_role = role_name
        
        config["manage_permission_level"] = lowest_manage_role
        
        return config
    finally:
        if should_close:
            session.close()


def update_permission_config(config: Dict, session: Session = None) -> None:
    """
    Update permission configuration
    config structure:
    {
        "menu_items": {
            "inventory": {
                "view": "Karbantartó",  # Role name
                ...
            },
            ...
        },
        "manage_permission_level": "Manager"
    }
    """
    should_close = False
    if session is None:
        session = SessionLocal()
        should_close = True
    
    try:
        # Get all roles
        roles = {role.name: role for role in session.query(Role).all()}
        
        # Initialize all permissions to False for all roles
        for role_name in ALL_ROLES:
            if role_name not in roles:
                continue
            role = roles[role_name]
            if role.permissions is None:
                role.permissions = {}
        
        # Clear all menu item permissions first
        for menu_key, menu_info in MENU_ITEMS.items():
            for action in menu_info["actions"]:
                permission_key = f"{menu_key}_{action}"
                for role_name in ALL_ROLES:
                    if role_name in roles:
                        role = roles[role_name]
                        role.permissions[permission_key] = False
        
        # Set permissions based on config (hierarchical)
        menu_items_config = config.get("menu_items", {})
        
        for menu_key, actions_config in menu_items_config.items():
            if menu_key not in MENU_ITEMS:
                continue
            
            for action, role_name in actions_config.items():
                if not role_name or role_name not in ALL_ROLES:
                    continue
                
                if action not in MENU_ITEMS[menu_key]["actions"]:
                    continue
                
                permission_key = f"{menu_key}_{action}"
                
                # Get all roles at or above the specified role
                roles_with_access = get_roles_at_or_above(role_name)
                
                # Set permission for all these roles
                for access_role_name in roles_with_access:
                    if access_role_name in roles:
                        role = roles[access_role_name]
                        role.permissions[permission_key] = True
        
        # Set manage_permissions
        manage_level = config.get("manage_permission_level")
        if manage_level and manage_level in ALL_ROLES:
            roles_with_manage = get_roles_at_or_above(manage_level)
            
            for role_name in roles_with_manage:
                if role_name in roles:
                    role = roles[role_name]
                    role.permissions[PERM_MANAGE_PERMISSIONS] = True
        else:
            # Clear manage_permissions if not set
            for role_name in ALL_ROLES:
                if role_name in roles:
                    role = roles[role_name]
                    role.permissions[PERM_MANAGE_PERMISSIONS] = False
        
        session.commit()
        
        # Log the permission configuration change
        if change_reason:
            try:
                from services.log_service import log_action
                from services.context_service import get_current_user_id
                
                user_id = get_current_user_id()
                log_action(
                    category="permissions",
                    action_type="update",
                    entity_type="PermissionConfig",
                    entity_id=None,
                    user_id=user_id,
                    description="Jogosultságok konfigurációja módosítva",
                    metadata={"change_reason": change_reason, "config": config},
                    session=session
                )
            except Exception as e:
                logger.warning(f"Error logging permission config update: {e}")
        
    finally:
        if should_close:
            session.close()
