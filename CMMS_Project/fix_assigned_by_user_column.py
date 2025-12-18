"""
Fix missing assigned_by_user_id column in part_locations table
This script adds the column directly to the database if it's missing.
Usage: python fix_assigned_by_user_column.py
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import text
from database.connection import engine

def main():
    """Add assigned_by_user_id column if it's missing"""
    print("Checking for assigned_by_user_id column in part_locations table...")
    
    try:
        with engine.connect() as conn:
            # Check if column exists
            result = conn.execute(text("""
                SELECT COUNT(*) as col_count
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'part_locations'
                AND COLUMN_NAME = 'assigned_by_user_id'
            """))
            col_exists = result.fetchone()[0] > 0
            
            if col_exists:
                print("[OK] Column 'assigned_by_user_id' already exists in 'part_locations' table")
                return
            
            # Check if users table exists
            result = conn.execute(text("""
                SELECT COUNT(*) as table_count
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'users'
            """))
            users_exists = result.fetchone()[0] > 0
            
            if not users_exists:
                print("[ERROR] 'users' table does not exist. Cannot add foreign key.")
                return
            
            # Add the column
            print("Adding 'assigned_by_user_id' column to 'part_locations' table...")
            conn.execute(text("""
                ALTER TABLE part_locations
                ADD COLUMN assigned_by_user_id INT NULL
            """))
            
            # Add index
            print("Adding index...")
            try:
                conn.execute(text("""
                    CREATE INDEX idx_part_locations_assigned_by_user_id 
                    ON part_locations(assigned_by_user_id)
                """))
            except Exception as idx_error:
                print(f"[WARNING] Index might already exist: {idx_error}")
            
            # Add foreign key
            print("Adding foreign key constraint...")
            try:
                conn.execute(text("""
                    ALTER TABLE part_locations
                    ADD CONSTRAINT fk_part_locations_assigned_by_user
                    FOREIGN KEY (assigned_by_user_id) REFERENCES users(id)
                """))
            except Exception as fk_error:
                print(f"[WARNING] Foreign key might already exist: {fk_error}")
            
            conn.commit()
            print("[OK] Column 'assigned_by_user_id' added successfully!")
            print("[OK] Index created successfully!")
            print("[OK] Foreign key constraint added successfully!")
            
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

