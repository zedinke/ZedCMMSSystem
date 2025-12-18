"""
Database Migration: Add missing fields to production_lines table
Adds: code, status, capacity, responsible_person, commission_date, notes
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
    """Add missing columns to production_lines table if they don't exist"""
    
    session = SessionLocal()
    try:
        # Check database type (MySQL/MariaDB)
        result = session.execute(text("SELECT DATABASE()"))
        db_name = result.scalar()
        print(f"Connected to database: {db_name}")
        
        # Get existing columns
        result = session.execute(text("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'production_lines'
        """))
        existing_columns = {row[0] for row in result.fetchall()}
        print(f"Existing columns: {sorted(existing_columns)}")
        
        changes_made = False
        
        # Columns to add (with their definitions)
        columns_to_add = {
            'code': 'VARCHAR(50)',
            'status': "VARCHAR(50) DEFAULT 'Active'",
            'capacity': 'VARCHAR(200)',
            'responsible_person': 'VARCHAR(200)',
            'commission_date': 'DATETIME',
            'notes': 'TEXT'
        }
        
        # Add each column if it doesn't exist
        for column_name, column_def in columns_to_add.items():
            if column_name not in existing_columns:
                print(f"Adding {column_name} column...")
                try:
                    session.execute(text(f"""
                        ALTER TABLE production_lines 
                        ADD COLUMN {column_name} {column_def}
                    """))
                    changes_made = True
                    print(f"[OK] {column_name} column added")
                except Exception as e:
                    print(f"[ERROR] Error adding {column_name}: {e}")
            else:
                print(f"[SKIP] {column_name} column already exists")
        
        # Add unique index on code if code column was added
        if 'code' in existing_columns or (changes_made and 'code' in columns_to_add):
            try:
                # Check if unique index already exists
                result = session.execute(text("""
                    SELECT COUNT(*) 
                    FROM INFORMATION_SCHEMA.STATISTICS 
                    WHERE TABLE_SCHEMA = DATABASE()
                    AND TABLE_NAME = 'production_lines'
                    AND INDEX_NAME = 'uq_production_line_code'
                """))
                index_exists = result.scalar() > 0
                
                if not index_exists:
                    print("Adding unique index on code column...")
                    session.execute(text("""
                        CREATE UNIQUE INDEX uq_production_line_code 
                        ON production_lines(code)
                    """))
                    print("[OK] Unique index on code added")
                else:
                    print("[SKIP] Unique index on code already exists")
            except Exception as e:
                print(f"[WARNING] Could not add unique index on code: {e}")
        
        if changes_made:
            session.commit()
            print("\n[SUCCESS] Migration completed successfully")
        else:
            print("\n[INFO] No changes needed - all columns already exist")
            
    except Exception as e:
        print(f"\n[ERROR] Migration failed: {e}")
        import traceback
        traceback.print_exc()
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    migrate()

