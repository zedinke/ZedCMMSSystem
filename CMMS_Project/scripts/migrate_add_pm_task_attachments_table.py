"""
Migration script to create pm_task_attachments table
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from database.connection import engine
from database.session_manager import SessionLocal
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate():
    """Create pm_task_attachments table if it doesn't exist"""
    session = SessionLocal()
    
    try:
        # Check if table exists
        check_table_query = text("""
            SELECT COUNT(*) as count
            FROM information_schema.tables
            WHERE table_schema = DATABASE()
            AND table_name = 'pm_task_attachments'
        """)
        result = session.execute(check_table_query)
        table_exists = result.fetchone()[0] > 0
        
        if table_exists:
            logger.info("[SKIP] Table pm_task_attachments already exists")
            return
        
        # Create table
        create_table_query = text("""
            CREATE TABLE pm_task_attachments (
                id INT NOT NULL AUTO_INCREMENT,
                pm_history_id INT NOT NULL,
                file_path VARCHAR(500) NOT NULL,
                original_filename VARCHAR(255) NOT NULL,
                file_type VARCHAR(50) NOT NULL,
                file_size INT,
                description TEXT,
                uploaded_at DATETIME,
                uploaded_by_user_id INT,
                PRIMARY KEY (id),
                FOREIGN KEY(pm_history_id) REFERENCES pm_histories (id) ON DELETE CASCADE,
                FOREIGN KEY(uploaded_by_user_id) REFERENCES users (id),
                INDEX idx_pm_attachment_history (pm_history_id),
                INDEX idx_pm_attachment_uploaded_at (uploaded_at)
            )
        """)
        
        session.execute(create_table_query)
        session.commit()
        logger.info("[OK] Table pm_task_attachments created successfully")
    finally:
        session.close()


if __name__ == "__main__":
    try:
        migrate()
        print("\n[SUCCESS] Migration completed successfully!")
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

