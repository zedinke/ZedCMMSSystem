"""
Backup & Recovery Service
Handles database and file backups
"""

import shutil
import zipfile
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List
import sqlite3
import threading
import time

from database.session_manager import SessionLocal
from database.models import Base
from sqlalchemy import create_engine
from config.app_config import DATABASE_PATH, BACKUPS_DIR

import logging

logger = logging.getLogger(__name__)

# Global backup scheduler state
_backup_scheduler_thread = None
_backup_scheduler_running = False
_backup_schedule_interval_hours = 24  # Default: daily backups


def backup_database(output_path: Optional[Path] = None) -> Optional[Path]:
    """
    Backup database to compressed file
    
    Args:
        output_path: Optional output path (if None, auto-generate)
    
    Returns:
        Path to backup file, or None on error
    """
    try:
        # Create backup directory
        backup_dir = Path("data/system_backups")
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate backup filename
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = backup_dir / f"cmms_backup_{timestamp}.db"
        else:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy database file (only for SQLite, MySQL uses different backup method)
        if DATABASE_PATH is None:
            logger.warning("DATABASE_PATH is None - MySQL database backup not yet implemented. Use mysqldump manually.")
            return None
        
        if DATABASE_PATH.exists():
            shutil.copy2(DATABASE_PATH, output_path)
            logger.info(f"Database backed up to: {output_path}")
            return output_path
        else:
            logger.error(f"Database file not found: {DATABASE_PATH}")
            return None
            
    except Exception as e:
        logger.error(f"Error backing up database: {e}")
        import traceback
        traceback.print_exc()
        return None


def backup_all_files(output_path: Optional[Path] = None) -> Optional[Path]:
    """
    Backup database and all files to a zip archive
    
    Args:
        output_path: Optional output path (if None, auto-generate)
    
    Returns:
        Path to backup zip file, or None on error
    """
    try:
        # Create backup directory
        backup_dir = Path("data/system_backups")
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate backup filename
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = backup_dir / f"cmms_full_backup_{timestamp}.zip"
        else:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create zip archive
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add database (only for SQLite, MySQL uses different backup method)
            if DATABASE_PATH is not None and DATABASE_PATH.exists():
                zipf.write(DATABASE_PATH, f"database/{DATABASE_PATH.name}")
            
            # Add files directory
            files_dir = Path("data/files")
            if files_dir.exists():
                for file_path in files_dir.rglob('*'):
                    if file_path.is_file():
                        arcname = f"files/{file_path.relative_to(files_dir)}"
                        zipf.write(file_path, arcname)
            
            # Add generated PDFs/DOCX
            generated_dir = Path("generated_pdfs")
            if generated_dir.exists():
                for file_path in generated_dir.rglob('*'):
                    if file_path.is_file():
                        arcname = f"generated/{file_path.relative_to(generated_dir)}"
                        zipf.write(file_path, arcname)
        
        logger.info(f"Full backup created: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Error creating full backup: {e}")
        import traceback
        traceback.print_exc()
        return None


def restore_from_backup(backup_file: Path, restore_files: bool = False) -> bool:
    """
    Restore database from backup file
    
    Args:
        backup_file: Path to backup file (.db or .zip)
        restore_files: If True and backup is .zip, also restore files
    
    Returns:
        True if successful, False otherwise
    """
    try:
        backup_path = Path(backup_file)
        if not backup_path.exists():
            logger.error(f"Backup file not found: {backup_path}")
            return False
        
        if backup_path.suffix == '.zip':
            # Extract from zip
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                # Extract database
                db_members = [m for m in zipf.namelist() if m.startswith('database/')]
                if db_members:
                    # Extract to temp location first
                    temp_db = Path("data/temp_restore.db")
                    zipf.extract(db_members[0], "data/")
                    temp_db_path = Path("data") / db_members[0]
                    if temp_db_path.exists():
                        # Backup current database
                        current_backup = backup_database()
                        if current_backup:
                            logger.info(f"Current database backed up to: {current_backup}")
                        
                        # Restore database (only for SQLite, MySQL uses different restore method)
                        if DATABASE_PATH is not None:
                            shutil.copy2(temp_db_path, DATABASE_PATH)
                        else:
                            logger.warning("DATABASE_PATH is None - MySQL database restore not yet implemented. Use mysql import manually.")
                        temp_db_path.unlink()  # Clean up
                
                # Extract files if requested
                if restore_files:
                    file_members = [m for m in zipf.namelist() if m.startswith('files/')]
                    for member in file_members:
                        zipf.extract(member, "data/")
        
        elif backup_path.suffix == '.db':
            # Direct database restore
            # Backup current database first
            current_backup = backup_database()
            if current_backup:
                logger.info(f"Current database backed up to: {current_backup}")
            
            # Restore database (only for SQLite, MySQL uses different restore method)
            if DATABASE_PATH is not None:
                shutil.copy2(backup_path, DATABASE_PATH)
            else:
                logger.warning("DATABASE_PATH is None - MySQL database restore not yet implemented. Use mysql import manually.")
                return False
        
        else:
            logger.error(f"Unsupported backup file format: {backup_path.suffix}")
            return False
        
        logger.info(f"Database restored from: {backup_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error restoring from backup: {e}")
        import traceback
        traceback.print_exc()
        return False


def list_backups() -> List[Path]:
    """
    List all available backup files
    
    Returns:
        List of backup file paths
    """
    try:
        backup_dir = Path("data/system_backups")
        if not backup_dir.exists():
            return []
        
        # Convert generators to lists before concatenation
        db_backups = list(backup_dir.glob("cmms_*.db"))
        zip_backups = list(backup_dir.glob("cmms_*.zip"))
        
        backups = sorted(
            db_backups + zip_backups,
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        return backups
        
    except Exception as e:
        logger.error(f"Error listing backups: {e}")
        return []


def cleanup_old_backups(keep_count: int = 10) -> int:
    """
    Remove old backup files, keeping only the most recent ones
    
    Args:
        keep_count: Number of backups to keep
    
    Returns:
        Number of backups deleted
    """
    try:
        backups = list_backups()
        if len(backups) <= keep_count:
            return 0
        
        # Delete oldest backups
        to_delete = backups[keep_count:]
        deleted_count = 0
        
        for backup in to_delete:
            try:
                backup.unlink()
                deleted_count += 1
                logger.info(f"Deleted old backup: {backup}")
            except Exception as e:
                logger.error(f"Error deleting backup {backup}: {e}")
        
        return deleted_count
        
    except Exception as e:
        logger.error(f"Error cleaning up backups: {e}")
        return 0


def _backup_scheduler_worker():
    """Background worker thread for scheduled backups"""
    global _backup_scheduler_running, _backup_schedule_interval_hours
    while _backup_scheduler_running:
        try:
            # Perform backup
            backup_database()
            # Wait for next interval
            time.sleep(_backup_schedule_interval_hours * 3600)
        except Exception as e:
            logger.error(f"Error in backup scheduler: {e}")
            # Wait a bit before retrying
            time.sleep(3600)  # Retry after 1 hour


def schedule_backup(interval_hours: int = 24, retention_days: int = 30) -> bool:
    """
    Start automatic backup scheduler
    
    Args:
        interval_hours: Hours between backups (default: 24)
        retention_days: Days to keep backups (default: 30)
    
    Returns:
        True if scheduler started, False otherwise
    """
    global _backup_scheduler_thread, _backup_scheduler_running, _backup_schedule_interval_hours
    
    if _backup_scheduler_running:
        logger.warning("Backup scheduler is already running")
        return False
    
    try:
        _backup_schedule_interval_hours = interval_hours
        _backup_scheduler_running = True
        
        _backup_scheduler_thread = threading.Thread(
            target=_backup_scheduler_worker,
            daemon=True,
            name="BackupScheduler"
        )
        _backup_scheduler_thread.start()
        
        logger.info(f"Backup scheduler started (interval: {interval_hours} hours)")
        return True
        
    except Exception as e:
        logger.error(f"Error starting backup scheduler: {e}")
        _backup_scheduler_running = False
        return False


def stop_backup_scheduler() -> bool:
    """
    Stop automatic backup scheduler
    
    Returns:
        True if scheduler stopped, False otherwise
    """
    global _backup_scheduler_thread, _backup_scheduler_running
    
    if not _backup_scheduler_running:
        logger.warning("Backup scheduler is not running")
        return False
    
    try:
        _backup_scheduler_running = False
        
        if _backup_scheduler_thread and _backup_scheduler_thread.is_alive():
            _backup_scheduler_thread.join(timeout=5.0)
        
        logger.info("Backup scheduler stopped")
        return True
        
    except Exception as e:
        logger.error(f"Error stopping backup scheduler: {e}")
        return False


def is_backup_scheduler_running() -> bool:
    """
    Check if backup scheduler is currently running
    
    Returns:
        True if running, False otherwise
    """
    global _backup_scheduler_running
    return _backup_scheduler_running


def get_backup_schedule_interval() -> int:
    """
    Get current backup schedule interval in hours
    
    Returns:
        Interval in hours
    """
    global _backup_schedule_interval_hours
    return _backup_schedule_interval_hours

