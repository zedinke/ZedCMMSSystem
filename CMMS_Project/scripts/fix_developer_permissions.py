"""
Fix Developer role permissions in database
Updates Developer role permissions to match config/roles.py
"""
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.session_manager import SessionLocal
from database.models import Role
from config.roles import ROLE_DEVELOPER, DEFAULT_PERMISSIONS

def fix_developer_permissions():
    session = SessionLocal()
    try:
        # Find Developer role
        dev_role = session.query(Role).filter_by(name=ROLE_DEVELOPER).first()
        if not dev_role:
            print(f"❌ Developer role not found! Available roles:")
            for role in session.query(Role).all():
                print(f"  - {role.name} (ID: {role.id})")
            return
        
        print(f"Current Developer role permissions:")
        print(f"  {dev_role.permissions}")
        print()
        
        # Get correct permissions from config
        correct_permissions = DEFAULT_PERMISSIONS.get(ROLE_DEVELOPER, {})
        print(f"Correct permissions from config:")
        print(f"  {correct_permissions}")
        print()
        
        # Update permissions
        dev_role.permissions = correct_permissions
        session.commit()
        
        print(f"✓ Developer role permissions updated!")
        print(f"  New permissions: {dev_role.permissions}")
        print()
        print("⚠ IMPORTANT: You need to log out and log back in for the changes to take effect!")
        
    except Exception as e:
        session.rollback()
        print(f"✗ Error updating permissions: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    fix_developer_permissions()

