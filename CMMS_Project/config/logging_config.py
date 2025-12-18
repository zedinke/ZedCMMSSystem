"""
Logging Configuration
Centralized logging setup with rotation
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional

# Import LOGS_DIR from app_config to use correct path for frozen executables
try:
    from config.app_config import LOGS_DIR
    LOG_DIR = LOGS_DIR
    LOG_FILE = LOGS_DIR / "cmms.log"
except ImportError:
    # Fallback if app_config is not available (shouldn't happen in normal operation)
    if getattr(sys, 'frozen', False):
        # Running as executable - use user data directory
        import os
        LOCALAPPDATA = Path(os.getenv('LOCALAPPDATA', os.path.expanduser('~/.local/share')))
        LOG_DIR = LOCALAPPDATA / "ZedCMMS" / "data" / "logs"
    else:
        # Running as script - use project root
        LOG_DIR = Path("data/logs")
    LOG_FILE = LOG_DIR / "cmms.log"

# Log rotation settings
MAX_BYTES = 10 * 1024 * 1024  # 10 MB
BACKUP_COUNT = 10  # Keep last 10 files


def setup_logging(log_level: int = logging.INFO, log_file: Optional[Path] = None) -> None:
    """
    Setup application-wide logging configuration
    
    Args:
        log_level: Logging level (default: INFO)
        log_file: Optional custom log file path
    """
    # Ensure log directory exists
    log_dir = (log_file or LOG_FILE).parent
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        # If we can't create the directory, try to use a fallback location
        import os
        fallback_dir = Path(os.getenv('LOCALAPPDATA', os.path.expanduser('~/.local/share'))) / "ZedCMMS" / "data" / "logs"
        fallback_dir.mkdir(parents=True, exist_ok=True)
        log_file = fallback_dir / (log_file.name if log_file else "cmms.log")
        log_dir = fallback_dir
    
    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        filename=str(log_file or LOG_FILE),
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT,
        encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Log startup message
    logging.info("Logging system initialized")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)

