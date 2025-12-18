"""
Role and Permission Definitions
"""

# Role names
ROLE_DEVELOPER = "Developer"
ROLE_MANAGER = "Manager"
ROLE_MAINTENANCE_SUPERVISOR = "Műszakvezető - Karbantartó"
ROLE_PRODUCTION_SUPERVISOR = "Műszakvezető - Termelés"
ROLE_MAINTENANCE_TECH = "Karbantartó"

# All roles
ALL_ROLES = [
    ROLE_DEVELOPER,
    ROLE_MANAGER,
    ROLE_MAINTENANCE_SUPERVISOR,
    ROLE_PRODUCTION_SUPERVISOR,
    ROLE_MAINTENANCE_TECH,
]

# Role hierarchy - defines the order from lowest to highest
# Lower number = lower in hierarchy
ROLE_HIERARCHY = {
    ROLE_MAINTENANCE_TECH: 1,                    # Legalacsonyabb
    ROLE_PRODUCTION_SUPERVISOR: 2,               # Ugyanaz a szint
    ROLE_MAINTENANCE_SUPERVISOR: 2,              # Ugyanaz a szint
    ROLE_MANAGER: 3,
    ROLE_DEVELOPER: 4,                           # Legmagasabb
}

# Permission keys - Legacy format (kept for backwards compatibility)
PERM_VIEW_DASHBOARD = "view_dashboard"
PERM_VIEW_INVENTORY = "view_inventory"
PERM_EDIT_INVENTORY = "edit_inventory"
PERM_VIEW_ASSETS = "view_assets"
PERM_EDIT_ASSETS = "edit_assets"
PERM_VIEW_WORKSHEETS = "view_worksheets"
PERM_CREATE_WORKSHEET = "create_worksheet"
PERM_EDIT_WORKSHEET = "edit_worksheet"
PERM_VIEW_PM = "view_pm"
PERM_EDIT_PM = "edit_pm"
PERM_VIEW_SETTINGS = "view_settings"
PERM_MANAGE_USERS = "manage_users"
PERM_MANAGE_PERMISSIONS = "manage_permissions"
PERM_VIEW_DEVELOPER_TOOLS = "view_developer_tools"
PERM_VIEW_INVENTORY_AUDIT = "view_inventory_audit"

# New permission keys format: {menu_item}_{action}
# Dashboard
PERM_DASHBOARD_VIEW = "dashboard_view"

# Inventory
PERM_INVENTORY_VIEW = "inventory_view"
PERM_INVENTORY_CREATE = "inventory_create"
PERM_INVENTORY_EDIT = "inventory_edit"
PERM_INVENTORY_DELETE = "inventory_delete"

# Assets
PERM_ASSETS_VIEW = "assets_view"
PERM_ASSETS_CREATE = "assets_create"
PERM_ASSETS_EDIT = "assets_edit"
PERM_ASSETS_DELETE = "assets_delete"

# Worksheets
PERM_WORKSHEETS_VIEW = "worksheets_view"
PERM_WORKSHEETS_CREATE = "worksheets_create"
PERM_WORKSHEETS_EDIT = "worksheets_edit"
PERM_WORKSHEETS_DELETE = "worksheets_delete"

# PM (Preventive Maintenance)
PERM_PM_VIEW = "pm_view"
PERM_PM_CREATE = "pm_create"
PERM_PM_EDIT = "pm_edit"
PERM_PM_DELETE = "pm_delete"

# Reports
PERM_REPORTS_VIEW = "reports_view"

# Settings
PERM_SETTINGS_VIEW = "settings_view"
PERM_SETTINGS_EDIT = "settings_edit"

# Users
PERM_USERS_VIEW = "users_view"
PERM_USERS_CREATE = "users_create"
PERM_USERS_EDIT = "users_edit"
PERM_USERS_DELETE = "users_delete"

# Developer Tools
PERM_DEVELOPER_TOOLS_VIEW = "developer_tools_view"

# Documentation
PERM_DOCUMENTATION_VIEW = "documentation_view"

# Logs
PERM_LOGS_VIEW = "logs_view"

# Vacation
PERM_VACATION_VIEW = "vacation_view"
PERM_VACATION_CREATE = "vacation_create"
PERM_VACATION_EDIT = "vacation_edit"
PERM_VACATION_DELETE = "vacation_delete"

# Shift Schedule
PERM_SHIFT_SCHEDULE_VIEW = "shift_schedule_view"
PERM_SHIFT_SCHEDULE_CREATE = "shift_schedule_create"
PERM_SHIFT_SCHEDULE_EDIT = "shift_schedule_edit"
PERM_SHIFT_SCHEDULE_DELETE = "shift_schedule_delete"

# Service Records
PERM_SERVICE_RECORDS_VIEW = "service_records_view"
PERM_SERVICE_RECORDS_CREATE = "service_records_create"
PERM_SERVICE_RECORDS_EDIT = "service_records_edit"
PERM_SERVICE_RECORDS_DELETE = "service_records_delete"

# All menu items with their available actions
MENU_ITEMS = {
    "dashboard": {
        "key": "dashboard",
        "actions": ["view"]
    },
    "inventory": {
        "key": "inventory",
        "actions": ["view", "create", "edit", "delete"]
    },
    "assets": {
        "key": "assets",
        "actions": ["view", "create", "edit", "delete"]
    },
    "worksheets": {
        "key": "worksheets",
        "actions": ["view", "create", "edit", "delete"]
    },
    "pm": {
        "key": "pm",
        "actions": ["view", "create", "edit", "delete"]
    },
    "reports": {
        "key": "reports",
        "actions": ["view"]
    },
    "settings": {
        "key": "settings",
        "actions": ["view", "edit"]
    },
    "users": {
        "key": "users",
        "actions": ["view", "create", "edit", "delete"]
    },
    "developer_tools": {
        "key": "developer_tools",
        "actions": ["view"]
    },
    "documentation": {
        "key": "documentation",
        "actions": ["view"]
    },
    "logs": {
        "key": "logs",
        "actions": ["view"]
    },
    "vacation": {
        "key": "vacation",
        "actions": ["view", "create", "edit", "delete"]
    },
    "shift_schedule": {
        "key": "shift_schedule",
        "actions": ["view", "create", "edit", "delete"]
    },
    "service_records": {
        "key": "service_records",
        "actions": ["view", "create", "edit", "delete"]
    },
    "inventory_audit": {
        "key": "inventory_audit",
        "actions": ["view"]
    },
    "storage": {
        "key": "storage",
        "actions": ["view", "create", "edit", "delete"]
    },
}

# Default permissions for each role
DEFAULT_PERMISSIONS = {
    ROLE_DEVELOPER: {
        PERM_VIEW_DASHBOARD: True,
        PERM_VIEW_INVENTORY: True,
        PERM_EDIT_INVENTORY: True,
        PERM_VIEW_ASSETS: True,
        PERM_EDIT_ASSETS: True,
        PERM_VIEW_WORKSHEETS: True,
        PERM_CREATE_WORKSHEET: True,
        PERM_EDIT_WORKSHEET: True,
        PERM_VIEW_PM: True,
        PERM_EDIT_PM: True,
        PERM_VIEW_SETTINGS: True,
        PERM_MANAGE_USERS: True,
        PERM_MANAGE_PERMISSIONS: True,
        PERM_VIEW_DEVELOPER_TOOLS: True,  # Only Developer has this
        PERM_VIEW_INVENTORY_AUDIT: True,
        "storage_view": True,
        "storage_create": True,
        "storage_edit": True,
        "storage_delete": True,
    },
    ROLE_MANAGER: {
        PERM_VIEW_DASHBOARD: True,
        PERM_VIEW_INVENTORY: True,
        PERM_EDIT_INVENTORY: True,
        PERM_VIEW_ASSETS: True,
        PERM_EDIT_ASSETS: True,
        PERM_VIEW_WORKSHEETS: True,
        PERM_CREATE_WORKSHEET: True,
        PERM_EDIT_WORKSHEET: True,
        PERM_VIEW_PM: True,
        PERM_EDIT_PM: True,
        PERM_VIEW_SETTINGS: True,
        PERM_MANAGE_USERS: True,
        PERM_MANAGE_PERMISSIONS: True,
        PERM_VIEW_DEVELOPER_TOOLS: False,
        PERM_VIEW_INVENTORY_AUDIT: True,
        "storage_view": True,
        "storage_create": True,
        "storage_edit": True,
        "storage_delete": True,
    },
    ROLE_MAINTENANCE_SUPERVISOR: {
        PERM_VIEW_DASHBOARD: True,
        PERM_VIEW_INVENTORY: True,
        PERM_EDIT_INVENTORY: True,
        PERM_VIEW_ASSETS: True,
        PERM_EDIT_ASSETS: True,
        PERM_VIEW_WORKSHEETS: True,
        PERM_CREATE_WORKSHEET: True,
        PERM_EDIT_WORKSHEET: True,
        PERM_VIEW_PM: True,
        PERM_EDIT_PM: True,
        PERM_VIEW_SETTINGS: False,
        PERM_MANAGE_USERS: False,
        PERM_MANAGE_PERMISSIONS: False,
        PERM_VIEW_DEVELOPER_TOOLS: False,
        PERM_VIEW_INVENTORY_AUDIT: True,
        "storage_view": True,
        "storage_create": True,
        "storage_edit": True,
        "storage_delete": False,
    },
    ROLE_PRODUCTION_SUPERVISOR: {
        PERM_VIEW_DASHBOARD: True,
        PERM_VIEW_INVENTORY: True,
        PERM_EDIT_INVENTORY: False,
        PERM_VIEW_ASSETS: True,
        PERM_EDIT_ASSETS: False,
        PERM_VIEW_WORKSHEETS: True,
        PERM_CREATE_WORKSHEET: True,
        PERM_EDIT_WORKSHEET: True,
        PERM_VIEW_PM: True,
        PERM_EDIT_PM: False,
        PERM_VIEW_SETTINGS: False,
        PERM_MANAGE_USERS: False,
        PERM_MANAGE_PERMISSIONS: False,
        PERM_VIEW_DEVELOPER_TOOLS: False,
        PERM_VIEW_INVENTORY_AUDIT: True,
        "storage_view": True,
        "storage_create": False,
        "storage_edit": False,
        "storage_delete": False,
    },
    ROLE_MAINTENANCE_TECH: {
        PERM_VIEW_DASHBOARD: True,
        PERM_VIEW_INVENTORY: True,
        PERM_EDIT_INVENTORY: False,
        PERM_VIEW_ASSETS: True,
        PERM_EDIT_ASSETS: False,
        PERM_VIEW_WORKSHEETS: True,
        PERM_CREATE_WORKSHEET: True,
        PERM_EDIT_WORKSHEET: True,
        PERM_VIEW_PM: True,
        PERM_EDIT_PM: False,
        PERM_VIEW_SETTINGS: False,
        PERM_MANAGE_USERS: False,
        PERM_MANAGE_PERMISSIONS: False,
        PERM_VIEW_DEVELOPER_TOOLS: False,
        PERM_VIEW_INVENTORY_AUDIT: True,
        "storage_view": True,
        "storage_create": False,
        "storage_edit": False,
        "storage_delete": False,
    },
}

# Default password for new users and password resets
DEFAULT_PASSWORD = "cmms2025"
