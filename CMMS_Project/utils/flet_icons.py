"""
Flet Icons Helper
Compatibility layer for flet 0.23.2 which doesn't have ft.Icons
Maps icon names to string values used by flet
"""

# Icon name mappings for flet 0.23.2
# In flet 0.23.2, icons are specified as strings, not as ft.Icons.XXX
ICONS = {
    # Navigation
    "DASHBOARD": "dashboard",
    "INVENTORY_2": "inventory_2",
    "PRECISION_MANUFACTURING": "precision_manufacturing",
    "FACTORY": "factory",
    "CONSTRUCTION": "construction",
    "BUILD": "build",
    "ASSIGNMENT": "assignment",
    "DESCRIPTION": "description",
    "BAR_CHART": "bar_chart",
    "ANALYTICS": "analytics",
    "GROUP": "group",
    "PEOPLE": "people",
    
    # Actions
    "EDIT": "edit",
    "EDIT_OUTLINED": "edit_outlined",
    "DELETE": "delete",
    "ADD": "add",
    "CLOSE": "close",
    "CHECK": "check",
    "CHECK_CIRCLE": "check_circle",
    "CHECK_CIRCLE_OUTLINED": "check_circle_outlined",
    "DONE_ALL": "done_all",
    "DOWNLOAD": "download",
    "FILE_DOWNLOAD": "file_download",
    "ARROW_BACK": "arrow_back",
    "ARROW_RIGHT": "arrow_forward",
    "KEYBOARD_ARROW_RIGHT": "arrow_forward",
    "CHEVRON_RIGHT": "chevron_right",
    "NAVIGATE_NEXT": "navigate_next",
    
    # Status
    "PLAY_ARROW": "play_arrow",
    "PLAY_CIRCLE_OUTLINED": "play_circle_outlined",
    "PAUSE": "pause",
    "PAUSE_CIRCLE_OUTLINED": "pause_circle_outlined",
    "INFO": "info",
    "INFO_OUTLINE": "info_outline",
    "RESTORE": "restore",
    
    # UI
    "EXPAND_MORE": "expand_more",
    "EXPAND_LESS": "expand_less",
    "FOLDER": "folder",
    "FOLDER_OPEN": "folder_open",
    "ARROW_FORWARD": "arrow_forward",
    "WARNING": "warning",
    
    # Other
    "HISTORY": "history",
    "LIST": "list",
    "BUILD_CIRCLE": "build_circle",
    "STORAGE": "storage",
    "DATABASE": "database",
    "REFRESH": "refresh",
    "BACKUP": "backup",
    "COMPUTER": "computer",
    "SECURITY": "security",
    "CODE": "code",
    "DEVELOPER_MODE": "developer_mode",
    "QR_CODE": "qr_code",
    "Qr_CODE": "qr_code",
    "EXIT_TO_APP": "exit_to_app",
    "LOGOUT": "logout",
    "SETTINGS": "settings",
    "SETTINGS_APPLICATIONS": "settings_applications",
    "TUNE": "tune",
    # Additional icons used in the UI
    "ACCESS_TIME": "access_time",
    "ADD_CIRCLE": "add_circle",
    "ADD_TASK": "add_task",
    "ARCHIVE": "archive",
    "ATTACH_MONEY": "attach_money",
    "BADGE": "badge",
    "BOLT": "bolt",
    "BUSINESS": "business",
    "CALENDAR_MONTH": "calendar_month",
    "CALENDAR_TODAY": "calendar_today",
    "CALENDAR_VIEW_MONTH": "calendar_view_month",
    "CONFIRMATION_NUMBER": "confirmation_number",
    "DARK_MODE": "dark_mode",
    "DESIGN_SERVICES": "design_services",
    "FLAG": "flag",
    "INVENTORY_": "inventory",
    "LABEL": "label",
    "LIGHT_MODE": "light_mode",
    "LOCATION_ON": "location_on",
    "LOCK_RESET": "lock_reset",
    "NOTE": "note",
    "NUMBERS": "numbers",
    "PAYMENTS": "payments",
    "PERSON": "person",
    "ACCOUNT_CIRCLE": "account_circle",
    "PICTURE_AS_PDF": "picture_as_pdf",
    "POWER": "power",
    "PRINT": "print",
    "PRINT_OUTLINED": "print_outlined",
    "PRIORITY_HIGH": "priority_high",
    "Q": "q",
    "REPEAT": "repeat",
    "SAVE": "save",
    "SAVE_ALT": "save_alt",
    "SCALE": "scale",
    "SCHEDULE": "schedule",
    "SEARCH": "search",
    "SHOPPING_CART": "shopping_cart",
    "STOREFRONT": "storefront",
    "STRAIGHTEN": "straighten",
    "TAG": "tag",
    "THERMOSTAT": "thermostat",
    "TRENDING_UP": "trending_up",
    "WARNING": "warning",
    "WARNING_AMBER_OUTLINED": "warning_amber",
    "ERROR": "error",
    "ERROR_OUTLINED": "error_outline",
    "NOTIFICATIONS": "notifications",
    "NOTIFICATIONS_OUTLINED": "notifications_outlined",
    "NOTIFICATIONS_ACTIVE": "notifications_active",
    "NOTIFICATIONS_NONE": "notifications_none",
    "CIRCLE_NOTIFICATIONS": "circle_notifications",
    "INFO_OUTLINED": "info_outline",
}


def get_icon(icon_name: str, fallback: str = "info") -> str:
    """
    Get icon string for flet 0.23.2
    
    Args:
        icon_name: Icon name (e.g., "DASHBOARD", "EDIT")
        fallback: Fallback icon if not found
    
    Returns:
        Icon string for flet
    """
    return ICONS.get(icon_name, fallback)


# Create a mock Icons class for compatibility
class Icons:
    """Mock Icons class for flet 0.23.2 compatibility"""
    DASHBOARD = "dashboard"
    INVENTORY_2 = "inventory_2"
    PRECISION_MANUFACTURING = "precision_manufacturing"
    FACTORY = "factory"
    CONSTRUCTION = "construction"
    BUILD = "build"
    ASSIGNMENT = "assignment"
    DESCRIPTION = "description"
    BAR_CHART = "bar_chart"
    ANALYTICS = "analytics"
    GROUP = "group"
    PEOPLE = "people"
    EDIT = "edit"
    EDIT_OUTLINED = "edit_outlined"
    DELETE = "delete"
    ADD = "add"
    CLOSE = "close"
    CHECK = "check"
    CHECK_CIRCLE = "check_circle"
    CHECK_CIRCLE_OUTLINED = "check_circle_outlined"
    DONE_ALL = "done_all"
    DOWNLOAD = "download"
    FILE_DOWNLOAD = "file_download"
    ARROW_BACK = "arrow_back"
    ARROW_FORWARD = "arrow_forward"
    ARROW_RIGHT = "arrow_forward"  # Alias for arrow_forward
    KEYBOARD_ARROW_RIGHT = "arrow_forward"  # Alias for arrow_forward
    CHEVRON_RIGHT = "chevron_right"
    NAVIGATE_NEXT = "navigate_next"
    PLAY_ARROW = "play_arrow"
    PLAY_CIRCLE_OUTLINED = "play_circle_outlined"
    PAUSE = "pause"
    PAUSE_CIRCLE_OUTLINED = "pause_circle_outlined"
    INFO = "info"
    INFO_OUTLINE = "info_outline"
    RESTORE = "restore"
    EXPAND_MORE = "expand_more"
    EXPAND_LESS = "expand_less"
    FOLDER = "folder"
    FOLDER_OPEN = "folder_open"
    ARROW_FORWARD = "arrow_forward"
    HISTORY = "history"
    LIST = "list"
    BUILD_CIRCLE = "build_circle"
    STORAGE = "storage"
    DATABASE = "database"
    REFRESH = "refresh"
    BACKUP = "backup"
    COMPUTER = "computer"
    SECURITY = "security"
    CODE = "code"
    DEVELOPER_MODE = "developer_mode"
    QR_CODE = "qr_code"
    Qr_CODE = "qr_code"
    EXIT_TO_APP = "exit_to_app"
    LOGOUT = "logout"
    SETTINGS = "settings"
    SETTINGS_APPLICATIONS = "settings_applications"
    TUNE = "tune"
    # Additional icons used in the UI
    ACCESS_TIME = "access_time"
    ADD_CIRCLE = "add_circle"
    ADD_TASK = "add_task"
    ARCHIVE = "archive"
    ATTACH_MONEY = "attach_money"
    BADGE = "badge"
    BOLT = "bolt"
    BUSINESS = "business"
    CALENDAR_MONTH = "calendar_month"
    CALENDAR_TODAY = "calendar_today"
    CALENDAR_VIEW_MONTH = "calendar_view_month"
    CONFIRMATION_NUMBER = "confirmation_number"
    DARK_MODE = "dark_mode"
    DESIGN_SERVICES = "design_services"
    FLAG = "flag"
    INVENTORY_ = "inventory"
    LABEL = "label"
    LIGHT_MODE = "light_mode"
    LOCATION_ON = "location_on"
    LOCK_RESET = "lock_reset"
    NOTE = "note"
    NUMBERS = "numbers"
    PAYMENTS = "payments"
    PERSON = "person"
    ACCOUNT_CIRCLE = "account_circle"
    PICTURE_AS_PDF = "picture_as_pdf"
    POWER = "power"
    PRINT = "print"
    PRINT_OUTLINED = "print_outlined"
    PRIORITY_HIGH = "priority_high"
    Q = "q"
    REPEAT = "repeat"
    SAVE = "save"
    SAVE_ALT = "save_alt"
    SCALE = "scale"
    SCHEDULE = "schedule"
    SEARCH = "search"
    SHOPPING_CART = "shopping_cart"
    STOREFRONT = "storefront"
    STRAIGHTEN = "straighten"
    TAG = "tag"
    THERMOSTAT = "thermostat"
    TRENDING_UP = "trending_up"
    WARNING = "warning"
    WARNING_AMBER_OUTLINED = "warning_amber"
    ERROR = "error"
    ERROR_OUTLINED = "error_outline"
    NOTIFICATIONS = "notifications"
    NOTIFICATIONS_OUTLINED = "notifications_outlined"
    NOTIFICATIONS_ACTIVE = "notifications_active"
    NOTIFICATIONS_NONE = "notifications_none"
    CIRCLE_NOTIFICATIONS = "circle_notifications"
    INFO_OUTLINED = "info_outline"
    # Additional icons used in the UI
    ACCESS_TIME = "access_time"
    ADD_CIRCLE = "add_circle"
    ADD_TASK = "add_task"
    ARCHIVE = "archive"
    ATTACH_MONEY = "attach_money"
    BADGE = "badge"
    BOLT = "bolt"
    BUSINESS = "business"
    CALENDAR_MONTH = "calendar_month"
    CALENDAR_TODAY = "calendar_today"
    CALENDAR_VIEW_MONTH = "calendar_view_month"
    CONFIRMATION_NUMBER = "confirmation_number"
    DARK_MODE = "dark_mode"
    DESIGN_SERVICES = "design_services"
    FLAG = "flag"
    INVENTORY_ = "inventory"
    LABEL = "label"
    LIGHT_MODE = "light_mode"
    LOCATION_ON = "location_on"
    LOCK_RESET = "lock_reset"
    NOTE = "note"
    NUMBERS = "numbers"
    PAYMENTS = "payments"
    PERSON = "person"
    ACCOUNT_CIRCLE = "account_circle"
    PICTURE_AS_PDF = "picture_as_pdf"
    POWER = "power"
    PRINT = "print"
    PRINT_OUTLINED = "print_outlined"
    PRIORITY_HIGH = "priority_high"
    Q = "q"
    REPEAT = "repeat"
    SAVE = "save"
    SAVE_ALT = "save_alt"
    SCALE = "scale"
    SCHEDULE = "schedule"
    SEARCH = "search"
    SHOPPING_CART = "shopping_cart"
    STOREFRONT = "storefront"
    STRAIGHTEN = "straighten"
    TAG = "tag"
    THERMOSTAT = "thermostat"
    TRENDING_UP = "trending_up"
    WARNING = "warning"

