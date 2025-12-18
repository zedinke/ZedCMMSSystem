"""
Application Configuration
Global settings, constants, and environment variables
"""

import os
import sys
from pathlib import Path

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
# SQLite fájl-alapú adatbázis a szerveren
# Production Database (Éles adatbázis)
DB_PROD_PATH = os.getenv("DB_PROD_PATH", "/opt/cmms-backend/data/cmms_prod.db")

# Learning Database (Tanuló adatbázis)
DB_LEARN_PATH = os.getenv("DB_LEARN_PATH", "/opt/cmms-backend/data/cmms_learn.db")


def _build_sqlite_url(database_path: str) -> str:
    """Build SQLite connection URL"""
    # SQLite fájl útvonal - absolute path
    return f"sqlite:///{database_path}"


def get_database_config(mode: str = "production"):
    """
    Get database configuration for the specified mode
    
    Args:
        mode: "production" or "learning"
    
    Returns:
        dict with keys: path, url
    """
    if mode == "learning":
        db_path = DB_LEARN_PATH
    else:  # production (default)
        db_path = DB_PROD_PATH
    
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
REPORTS_DIR = RUNTIME_DATA_ROOT / "data" / "reports" / "generated"
BACKUPS_DIR = RUNTIME_DATA_ROOT / "data" / "system_backups"
LOGS_DIR = RUNTIME_DATA_ROOT / "data" / "logs"
# Templates directory - always use PROJECT_ROOT (installed files)
TEMPLATES_DIR = PROJECT_ROOT / "templates"

# Ensure directories exist (with error handling)
for directory in [
    EQUIPMENT_MANUALS_DIR,
    MAINTENANCE_PHOTOS_DIR,
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
GITHUB_REPO = os.getenv("GITHUB_REPO", "Artence_CMMS")  # Default repository name
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}" if GITHUB_OWNER else None
UPDATE_CHECK_ENABLED = os.getenv("UPDATE_CHECK_ENABLED", "True").lower() == "true"
UPDATE_CHECK_ON_STARTUP = os.getenv("UPDATE_CHECK_ON_STARTUP", "False").lower() == "true"
