"""
Fix admin user role to Developer
"""
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.session_manager import SessionLocal
from database.models import User, Role
from config.roles import ROLE_DEVELOPER

def fix_admin_role():
    session = SessionLocal()
    try:
        # Find admin user
        admin = session.query(User).filter_by(username="admin").first()
        if not admin:
            print("Admin user not found")
            return
        
        print(f"Current admin role: {admin.role.name}")
        
        # Find Developer role
        dev_role = session.query(Role).filter_by(name=ROLE_DEVELOPER).first()
        if not dev_role:
            print(f"Developer role not found! Available roles:")
            for role in session.query(Role).all():
                print(f"  - {role.name}")
            return
        
        # Update admin to Developer
        admin.role_id = dev_role.id
        admin.must_change_password = False
        session.commit()
        
        print(f"✓ Admin role updated to: {admin.role.name}")
        print(f"  Permissions: {admin.role.permissions}")
        
    finally:
        session.close()

if __name__ == "__main__":
    fix_admin_role()
