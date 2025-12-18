"""
Fix script to add missing columns to database tables
This script adds missing columns that are defined in models but missing from the database.
- Adds version column to pm_tasks and worksheets tables
- Adds ip_address and user_agent columns to system_logs table
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import text
from database.connection import engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clear_connection_pool():
    """Clear connection pool to force fresh connections"""
    try:
        engine.dispose(close=False)
        logger.info("[INFO] Connection pool cleared")
    except Exception as e:
        logger.warning(f"[WARNING] Could not clear connection pool: {e}")


def fix_version_column(table_name: str):
    """Add version column to a table if it doesn't exist"""
    try:
        with engine.begin() as conn:
            # Check if version column exists
            result = conn.execute(text("""
                SELECT COUNT(*) as col_count
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = :table_name
                AND COLUMN_NAME = 'version'
            """), {"table_name": table_name})
            
            col_exists = result.fetchone()[0] > 0
            
            if col_exists:
                logger.info(f"[OK] version column already exists in {table_name} table")
                return True
            
            # Add the version column
            logger.info(f"Adding version column to {table_name} table...")
            conn.execute(text(f"""
                ALTER TABLE {table_name} 
                ADD COLUMN version INTEGER NOT NULL DEFAULT 1
            """))
            
            # Update existing records to have version = 1 (in case any are NULL)
            conn.execute(text(f"""
                UPDATE {table_name} 
                SET version = 1 
                WHERE version IS NULL OR version = 0
            """))
            
            # begin() context manager auto-commits on success
            logger.info(f"[OK] Successfully added version column to {table_name} table")
            logger.info(f"[OK] Updated existing records to have version = 1")
            return True
            
    except Exception as e:
        logger.error(f"[ERROR] Error adding version column to {table_name}: {e}")
        import traceback
        traceback.print_exc()
        return False


def fix_system_logs_columns():
    """Add ip_address and user_agent columns to system_logs table if they don't exist"""
    try:
        with engine.begin() as conn:
            # Check if columns exist
            result = conn.execute(text("""
                SELECT COLUMN_NAME
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'system_logs'
                AND COLUMN_NAME IN ('ip_address', 'user_agent')
            """))
            
            existing_columns = {row[0] for row in result.fetchall()}
            
            # Add ip_address if missing
            if 'ip_address' not in existing_columns:
                logger.info("Adding ip_address column to system_logs table...")
                conn.execute(text("""
                    ALTER TABLE system_logs 
                    ADD COLUMN ip_address VARCHAR(45)
                """))
                logger.info("[OK] Successfully added ip_address column to system_logs table")
            else:
                logger.info("[OK] ip_address column already exists in system_logs table")
            
            # Add user_agent if missing
            if 'user_agent' not in existing_columns:
                logger.info("Adding user_agent column to system_logs table...")
                conn.execute(text("""
                    ALTER TABLE system_logs 
                    ADD COLUMN user_agent VARCHAR(500)
                """))
                logger.info("[OK] Successfully added user_agent column to system_logs table")
            else:
                logger.info("[OK] user_agent column already exists in system_logs table")
            
            # begin() context manager auto-commits on success
            return True
            
    except Exception as e:
        logger.error(f"[ERROR] Error adding columns to system_logs: {e}")
        import traceback
        traceback.print_exc()
        return False


def fix_all_version_columns():
    """Fix version columns in both pm_tasks and worksheets tables"""
    success = True
    
    # Fix pm_tasks table
    logger.info("\n--- Fixing pm_tasks table ---")
    if not fix_version_column('pm_tasks'):
        success = False
    
    # Fix worksheets table
    logger.info("\n--- Fixing worksheets table ---")
    if not fix_version_column('worksheets'):
        success = False
    
    return success


def fix_all_missing_columns():
    """Fix all missing columns in database tables"""
    success = True
    
    # Fix version columns
    if not fix_all_version_columns():
        success = False
    
    # Fix system_logs columns
    logger.info("\n--- Fixing system_logs table ---")
    if not fix_system_logs_columns():
        success = False
    
    return success


if __name__ == "__main__":
    print("=" * 60)
    print("Fix: Add missing columns to database tables")
    print("=" * 60)
    
    # Clear connection pool to ensure fresh connections
    clear_connection_pool()
    
    success = fix_all_missing_columns()
    
    # Clear connection pool again after changes to ensure schema cache is refreshed
    clear_connection_pool()
    
    if success:
        print("\n[OK] Fix completed successfully!")
        print("[INFO] Please restart the application to refresh schema cache")
        sys.exit(0)
    else:
        print("\n[ERROR] Fix failed. Please check the error messages above.")
        sys.exit(1)

