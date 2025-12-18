"""
Permissions Router
Permission configuration and management endpoints
"""

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import List
from api.schemas import (
    RoleHierarchyResponse,
    MenuItemResponse,
    PermissionConfigResponse,
    PermissionConfigUpdate,
    ErrorResponse
)
from api.dependencies import get_db, get_current_user, get_user_language
from api.security import TokenData
from services.permission_service import (
    get_all_menu_items,
    get_permission_config,
    update_permission_config,
    can_manage_permissions,
    get_role_hierarchy_level
)
from config.roles import ALL_ROLES, MENU_ITEMS
from utils.localization_helper import get_localized_error
import logging

router = APIRouter(prefix="/permissions", tags=["Permissions"])
logger = logging.getLogger(__name__)


@router.get(
    "/roles",
    response_model=List[RoleHierarchyResponse],
    dependencies=[Depends(get_current_user)]
)
async def get_roles(
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get all roles with their hierarchy levels
    
    **Response:**
    - List of roles with name, level, and display name
    """
    try:
        roles = []
        for role_name in ALL_ROLES:
            roles.append(RoleHierarchyResponse(
                name=role_name,
                level=get_role_hierarchy_level(role_name),
                display_name=role_name
            ))
        
        # Sort by level (ascending - lowest first)
        roles.sort(key=lambda x: x.level)
        return roles
    except Exception as e:
        logger.error(f"Error getting roles: {str(e)}")
        lang_code = "en"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=get_localized_error("common.messages.error_occurred", lang_code=lang_code)
        )


@router.get(
    "/menu-items",
    response_model=List[MenuItemResponse],
    dependencies=[Depends(get_current_user)]
)
async def get_menu_items(
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get all menu items with their available actions
    
    **Response:**
    - List of menu items with their actions
    """
    try:
        menu_items = []
        for menu_key, menu_info in MENU_ITEMS.items():
            menu_items.append(MenuItemResponse(
                key=menu_key,
                actions=menu_info["actions"]
            ))
        return menu_items
    except Exception as e:
        logger.error(f"Error getting menu items: {str(e)}")
        lang_code = "en"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=get_localized_error("common.messages.error_occurred", lang_code=lang_code)
        )


@router.get(
    "/config",
    response_model=PermissionConfigResponse,
    dependencies=[Depends(get_current_user)]
)
async def get_config(
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get current permission configuration
    
    **Response:**
    - Current permission configuration for all menu items and actions
    """
    try:
        config = get_permission_config(db)
        return PermissionConfigResponse(**config)
    except Exception as e:
        logger.error(f"Error getting permission config: {str(e)}")
        lang_code = "en"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=get_localized_error("common.messages.error_occurred", lang_code=lang_code)
        )


@router.put(
    "/config",
    response_model=PermissionConfigResponse,
    dependencies=[Depends(get_current_user)],
    responses={
        403: {"model": ErrorResponse, "description": "Permission denied"},
        422: {"model": ErrorResponse, "description": "Validation error"}
    }
)
async def update_config(
    config_update: PermissionConfigUpdate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
    lang_code: str = Depends(get_user_language)
):
    """
    Update permission configuration
    
    **Request Body:**
    - `menu_items`: Dict mapping menu keys to action permissions
    - `manage_permission_level`: Role name that can manage permissions
    
    **Example:**
    ```json
    {
        "menu_items": {
            "inventory": {
                "view": "Karbantartó",
                "create": "Manager",
                "edit": "Manager",
                "delete": "Manager"
            }
        },
        "manage_permission_level": "Manager"
    }
    ```
    
    **Response:**
    - Updated permission configuration
    """
    try:
        # Check if user can manage permissions
        if not can_manage_permissions(current_user.role_name, db):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=get_localized_error("auth.permissions.access_denied", lang_code=lang_code)
            )
        
        # Validate role names
        config_dict = config_update.dict()
        
        # Validate menu items
        for menu_key, actions_config in config_dict.get("menu_items", {}).items():
            if menu_key not in MENU_ITEMS:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Invalid menu key: {menu_key}"
                )
            
            valid_actions = MENU_ITEMS[menu_key]["actions"]
            for action, role_name in actions_config.items():
                if action not in valid_actions:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail=f"Invalid action '{action}' for menu '{menu_key}'"
                    )
                
                if role_name and role_name not in ALL_ROLES:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail=f"Invalid role name: {role_name}"
                    )
        
        # Validate manage_permission_level
        manage_level = config_dict.get("manage_permission_level")
        if manage_level and manage_level not in ALL_ROLES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid role name for manage_permission_level: {manage_level}"
            )
        
        # Update configuration
        update_permission_config(config_dict, db)
        
        # Return updated config
        updated_config = get_permission_config(db)
        return PermissionConfigResponse(**updated_config)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating permission config: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=get_localized_error("common.messages.error_occurred", lang_code=lang_code)
        )


@router.get(
    "/manage-permission-level",
    response_model=dict,
    dependencies=[Depends(get_current_user)]
)
async def get_manage_permission_level(
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get which role level can manage permissions
    
    **Response:**
    - Role name that can manage permissions
    """
    try:
        config = get_permission_config(db)
        return {"role": config.get("manage_permission_level")}
    except Exception as e:
        logger.error(f"Error getting manage permission level: {str(e)}")
        lang_code = "en"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=get_localized_error("common.messages.error_occurred", lang_code=lang_code)
        )

