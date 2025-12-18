"""
Update role permissions in database to match DEFAULT_PERMISSIONS
"""
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.session_manager import SessionLocal
from database.models import Role
from config.roles import DEFAULT_PERMISSIONS, ALL_ROLES

def update_role_permissions():
    print("Updating role permissions in database...\n")
    session = SessionLocal()
    try:
        for role_name in ALL_ROLES:
            role = session.query(Role).filter_by(name=role_name).first()
            if role:
                old_perms = role.permissions
                new_perms = DEFAULT_PERMISSIONS[role_name]
                role.permissions = new_perms
                print(f"✓ Updated {role_name}")
                print(f"  Old: {old_perms}")
                print(f"  New: {new_perms}\n")
            else:
                print(f"⚠ Role not found: {role_name}")
        
        session.commit()
        print("\n✓ All role permissions updated successfully")
        
    finally:
        session.close()

if __name__ == "__main__":
    update_role_permissions()
