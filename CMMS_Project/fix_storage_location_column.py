"""
Fix missing storage_location_id column in stock_batches table
This script adds the column directly to the database if it's missing.
Usage: python fix_storage_location_column.py
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import text
from database.connection import engine

def main():
    """Add storage_location_id column if it's missing"""
    print("Checking for storage_location_id column in stock_batches table...")
    
    try:
        with engine.connect() as conn:
            # Check if column exists
            result = conn.execute(text("""
                SELECT COUNT(*) as col_count
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'stock_batches'
                AND COLUMN_NAME = 'storage_location_id'
            """))
            col_exists = result.fetchone()[0] > 0
            
            if col_exists:
                print("[OK] Column 'storage_location_id' already exists in 'stock_batches' table")
                return
            
            # Check if storage_locations table exists
            result = conn.execute(text("""
                SELECT COUNT(*) as table_count
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'storage_locations'
            """))
            storage_locations_exists = result.fetchone()[0] > 0
            
            if not storage_locations_exists:
                print("[WARNING] 'storage_locations' table does not exist.")
                print("  Creating storage_locations table first...")
                
                # Create storage_locations table first
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS storage_locations (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(150) NOT NULL,
                        code VARCHAR(50) NULL,
                        parent_id INT NULL,
                        location_type VARCHAR(50) NULL,
                        description TEXT NULL,
                        is_active BOOLEAN NOT NULL DEFAULT TRUE,
                        created_at DATETIME NOT NULL,
                        updated_at DATETIME NOT NULL,
                        created_by_user_id INT NULL,
                        FOREIGN KEY (parent_id) REFERENCES storage_locations(id),
                        FOREIGN KEY (created_by_user_id) REFERENCES users(id),
                        INDEX idx_storage_locations_parent_id (parent_id),
                        INDEX idx_storage_locations_code (code),
                        INDEX idx_storage_locations_is_active (is_active)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """))
                conn.commit()
                print("  [OK] storage_locations table created")
            
            # Add the column
            print("Adding 'storage_location_id' column to 'stock_batches' table...")
            conn.execute(text("""
                ALTER TABLE stock_batches
                ADD COLUMN storage_location_id INT NULL
            """))
            
            # Add index
            print("Adding index...")
            conn.execute(text("""
                CREATE INDEX idx_stock_batches_storage_location_id 
                ON stock_batches(storage_location_id)
            """))
            
            # Add foreign key
            print("Adding foreign key constraint...")
            conn.execute(text("""
                ALTER TABLE stock_batches
                ADD CONSTRAINT fk_stock_batches_storage_location
                FOREIGN KEY (storage_location_id) REFERENCES storage_locations(id)
            """))
            
            conn.commit()
            print("[OK] Column 'storage_location_id' added successfully!")
            print("[OK] Index created successfully!")
            print("[OK] Foreign key constraint added successfully!")
            
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

