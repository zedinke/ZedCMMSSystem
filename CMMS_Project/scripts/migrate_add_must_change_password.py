"""
Database Migration: Add must_change_password field to users table
Run this script to update existing database
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from database.connection import engine
from database.session_manager import SessionLocal

def migrate():
    """Add must_change_password column if it doesn't exist"""
    
    session = SessionLocal()
    try:
        # Check if column exists
        result = session.execute(text("""
            SELECT COUNT(*) 
            FROM pragma_table_info('users') 
            WHERE name='must_change_password'
        """))
        
        count = result.scalar()
        
        if count == 0:
            print("Adding must_change_password column...")
            session.execute(text("""
                ALTER TABLE users 
                ADD COLUMN must_change_password BOOLEAN DEFAULT 0
            """))
            session.commit()
            print("✓ Column added successfully")
        else:
            print("✓ Column already exists")
            
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    migrate()
