"""
Application Configuration
Global settings, constants, and environment variables
"""

import os
import sys
from pathlib import Path
from typing import Optional

# Project Root
# In PyInstaller, __file__ points to the temp directory, so we need to handle it differently
if getattr(sys, 'frozen', False):
    # Running as compiled executable (PyInstaller)
    # Use sys.executable's directory as project root
    PROJECT_ROOT = Path(sys.executable).parent
else:
    # Running as script
    PROJECT_ROOT = Path(__file__).parent.parent

# Runtime data directory (user data)
# Use %LOCALAPPDATA% when running as executable, otherwise use PROJECT_ROOT
if getattr(sys, 'frozen', False):
    # Running as compiled executable - use user data directory
    import os
    LOCALAPPDATA = Path(os.getenv('LOCALAPPDATA', os.path.expanduser('~/.local/share')))
    RUNTIME_DATA_ROOT = LOCALAPPDATA / "ZedCMMS"
else:
    # Running as script - use project root
    RUNTIME_DATA_ROOT = PROJECT_ROOT

# Database Configuration - SQLite
# SQLite fájl-alapú adatbázis
# Production Database (Éles adatbázis)
# Use RUNTIME_DATA_ROOT for Windows compatibility, fallback to Linux path

def _get_default_db_path(mode: str = "production") -> str:
    """Get default database path based on mode"""
    if mode == "learning":
        default_path = RUNTIME_DATA_ROOT / "data" / "cmms_learn.db"
    else:  # production
        default_path = RUNTIME_DATA_ROOT / "data" / "cmms_prod.db"
    return str(default_path)

def _load_db_path_from_config(mode: str = "production") -> Optional[str]:
    """
    Load database path from configuration file
    This avoids the "chicken and egg" problem of storing paths in the database
    
    Args:
        mode: "production" or "learning"
    
    Returns:
        Database path string or None if not set
    """
    try:
        from config.database_config_manager import get_database_path_from_config
        path = get_database_path_from_config(mode)
        if path:
            return path
    except Exception as e:
        # If config file is not available, return None
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"Could not load database path from config file for {mode}: {e}")
    return None

# Initialize database paths
# Priority: 1. Environment variable, 2. Database settings, 3. Default path
if getattr(sys, 'frozen', False):
    # Running as compiled executable - use RUNTIME_DATA_ROOT
    _default_prod = str(RUNTIME_DATA_ROOT / "data" / "cmms_prod.db")
    _default_learn = str(RUNTIME_DATA_ROOT / "data" / "cmms_learn.db")
else:
    # Running as script - use project root
    _default_prod = str(PROJECT_ROOT / "data" / "cmms_prod.db")
    _default_learn = str(PROJECT_ROOT / "data" / "cmms_learn.db")

# Get from environment variable first
DB_PROD_PATH = os.getenv("DB_PROD_PATH")
DB_LEARN_PATH = os.getenv("DB_LEARN_PATH")

# If not in env, try to load from config file (lazy loading)
if not DB_PROD_PATH:
    try:
        DB_PROD_PATH = _load_db_path_from_config("production")
    except Exception:
        pass
if not DB_LEARN_PATH:
    try:
        DB_LEARN_PATH = _load_db_path_from_config("learning")
    except Exception:
        pass

# Fallback to defaults if still not set
if not DB_PROD_PATH:
    DB_PROD_PATH = _default_prod
if not DB_LEARN_PATH:
    DB_LEARN_PATH = _default_learn


def _build_sqlite_url(database_path: str) -> str:
    """Build SQLite connection URL"""
    # SQLite fájl útvonal - absolute path
    return f"sqlite:///{database_path}"


def get_database_config(mode: str = "production"):
    """
    Get database configuration for the specified mode
    Loads path from database settings if available
    
    Args:
        mode: "production" or "learning"
    
    Returns:
        dict with keys: path, url
    """
    # Try to load from config file first (always available, no database dependency)
    db_path = None
    try:
        db_path = _load_db_path_from_config(mode)
    except Exception:
        pass
    
    # Fallback to environment variable or default
    if not db_path:
        if mode == "learning":
            db_path = os.getenv("DB_LEARN_PATH", DB_LEARN_PATH)
        else:  # production (default)
            db_path = os.getenv("DB_PROD_PATH", DB_PROD_PATH)
    
    # Ensure parent directory exists
    db_path_obj = Path(db_path)
    db_path_obj.parent.mkdir(parents=True, exist_ok=True)
    
    return {
        "path": db_path,
        "url": _build_sqlite_url(db_path)
    }


# Default to production database
DATABASE_URL = get_database_config("production")["url"]
# For compatibility with backup_service
DATABASE_PATH = get_database_config("production")["path"]

# Application Settings
APP_NAME = "CMMS - Computerized Maintenance Management System"

# Read version from version.txt file
# In PyInstaller, use sys._MEIPASS to find bundled files
if getattr(sys, 'frozen', False):
    # Running as compiled executable (PyInstaller)
    # Try sys._MEIPASS first (where PyInstaller extracts files)
    try:
        import sys
        MEIPASS = getattr(sys, '_MEIPASS', None)
        if MEIPASS:
            VERSION_FILE = Path(MEIPASS) / "version.txt"
            if VERSION_FILE.exists():
                with open(VERSION_FILE, "r", encoding="utf-8") as f:
                    APP_VERSION = f.read().strip()
            else:
                # Fallback to PROJECT_ROOT
                VERSION_FILE = PROJECT_ROOT / "version.txt"
                with open(VERSION_FILE, "r", encoding="utf-8") as f:
                    APP_VERSION = f.read().strip()
        else:
            raise FileNotFoundError
    except (FileNotFoundError, IOError):
        # Final fallback: try PROJECT_ROOT
        try:
            VERSION_FILE = PROJECT_ROOT / "version.txt"
            with open(VERSION_FILE, "r", encoding="utf-8") as f:
                APP_VERSION = f.read().strip()
        except (FileNotFoundError, IOError):
            APP_VERSION = "1.0.0"  # Default fallback
else:
    # Running as script
    VERSION_FILE = PROJECT_ROOT / "version.txt"
    try:
        with open(VERSION_FILE, "r", encoding="utf-8") as f:
            APP_VERSION = f.read().strip()
    except (FileNotFoundError, IOError):
        APP_VERSION = "1.0.0"  # Default fallback

APP_TITLE = "CMMS Rendszer"

# UI Settings
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
DEFAULT_LANGUAGE = "hu"  # hu (Hungarian) or en (English)

# File Upload Settings
MAX_FILE_SIZE_MB = 10
ALLOWED_EXTENSIONS = {
    "pdf": ["application/pdf"],
    "jpg": ["image/jpeg"],
    "jpeg": ["image/jpeg"],
    "png": ["image/png"],
}

# Directory Paths
# Runtime data directories (user data) - use RUNTIME_DATA_ROOT
EQUIPMENT_MANUALS_DIR = RUNTIME_DATA_ROOT / "data" / "files" / "equipment_manuals"
MAINTENANCE_PHOTOS_DIR = RUNTIME_DATA_ROOT / "data" / "files" / "maintenance_photos"
MESSAGE_ATTACHMENTS_DIR = RUNTIME_DATA_ROOT / "data" / "files" / "message_attachments"
REPORTS_DIR = RUNTIME_DATA_ROOT / "data" / "reports" / "generated"
BACKUPS_DIR = RUNTIME_DATA_ROOT / "data" / "system_backups"
LOGS_DIR = RUNTIME_DATA_ROOT / "data" / "logs"
# Templates directory - always use PROJECT_ROOT (installed files)
TEMPLATES_DIR = PROJECT_ROOT / "templates"

# Ensure directories exist (with error handling)
for directory in [
    EQUIPMENT_MANUALS_DIR,
    MAINTENANCE_PHOTOS_DIR,
    MESSAGE_ATTACHMENTS_DIR,
    REPORTS_DIR,
    BACKUPS_DIR,
    LOGS_DIR,
]:
    try:
        directory.mkdir(parents=True, exist_ok=True)
    except (PermissionError, OSError) as e:
        # Log error but don't fail - directories will be created when needed
        import logging
        logging.warning(f"Could not create directory {directory}: {e}")

# Session Configuration
SESSION_EXPIRY_HOURS = 24
SESSION_TOKEN_LENGTH = 32

# Cache / Redis
CACHE_DEFAULT_TTL = int(os.getenv("CACHE_DEFAULT_TTL", "300"))
REDIS_URL = os.getenv("REDIS_URL")

# Password Configuration
MIN_PASSWORD_LENGTH = 8
REQUIRE_UPPERCASE = True
REQUIRE_LOWERCASE = True
REQUIRE_NUMBERS = True

# Logging Configuration
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = LOGS_DIR / "cmms.log"
LOG_MAX_SIZE_MB = 10
LOG_BACKUP_COUNT = 10

# Debug Mode
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Date/Time Formats by Language
DATE_FORMATS = {
    "en": "%m/%d/%Y",
    "hu": "%Y.%m.%d",
}

DATETIME_FORMATS = {
    "en": "%m/%d/%Y %I:%M %p",
    "hu": "%Y.%m.%d %H:%M",
}

TIME_FORMATS = {
    "en": "%I:%M %p",
    "hu": "%H:%M",
}

# Update Configuration
GITHUB_OWNER = os.getenv("GITHUB_OWNER", "")  # Set via environment variable or config
GITHUB_REPO = os.getenv("GITHUB_REPO", "ZedCMMSSystem")  # Default repository name
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}" if GITHUB_OWNER else None
UPDATE_CHECK_ENABLED = os.getenv("UPDATE_CHECK_ENABLED", "True").lower() == "true"
UPDATE_CHECK_ON_STARTUP = os.getenv("UPDATE_CHECK_ON_STARTUP", "False").lower() == "true"
