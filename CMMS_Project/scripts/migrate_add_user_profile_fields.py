"""
Migration: Add user profile fields (full_name, phone, profile_picture)
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.session_manager import SessionLocal
from database.database import engine
from sqlalchemy import text

def migrate():
    """Add full_name, phone, profile_picture columns to users table"""
    session = SessionLocal()
    
    try:
        # Check if columns already exist
        inspector = text("PRAGMA table_info(users)")
        result = session.execute(inspector)
        columns = [row[1] for row in result]
        
        changes_made = False
        
        # Add full_name column if not exists
        if 'full_name' not in columns:
            print("Adding full_name column...")
            session.execute(text("ALTER TABLE users ADD COLUMN full_name VARCHAR(100)"))
            changes_made = True
            print("✓ full_name column added")
        else:
            print("○ full_name column already exists")
        
        # Add phone column if not exists
        if 'phone' not in columns:
            print("Adding phone column...")
            session.execute(text("ALTER TABLE users ADD COLUMN phone VARCHAR(20)"))
            changes_made = True
            print("✓ phone column added")
        else:
            print("○ phone column already exists")
        
        # Add profile_picture column if not exists
        if 'profile_picture' not in columns:
            print("Adding profile_picture column...")
            session.execute(text("ALTER TABLE users ADD COLUMN profile_picture TEXT"))
            changes_made = True
            print("✓ profile_picture column added")
        else:
            print("○ profile_picture column already exists")
        
        if changes_made:
            session.commit()
            print("\n✓ Migration completed successfully!")
        else:
            print("\n○ No changes needed - all columns already exist")
        
    except Exception as e:
        session.rollback()
        print(f"\n✗ Migration failed: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    print("=" * 60)
    print("Migration: Add User Profile Fields")
    print("=" * 60)
    migrate()
