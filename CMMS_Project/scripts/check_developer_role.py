"""
Check Developer role ID and permissions
"""
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.session_manager import SessionLocal
from database.models import User, Role
from config.roles import ROLE_DEVELOPER

def check_developer_role():
    session = SessionLocal()
    try:
        # Find Developer role
        dev_role = session.query(Role).filter_by(name=ROLE_DEVELOPER).first()
        if not dev_role:
            print(f"❌ Developer role not found! Available roles:")
            for role in session.query(Role).all():
                print(f"  - {role.name} (ID: {role.id})")
            return
        
        print(f"✓ Developer role found:")
        print(f"  - ID: {dev_role.id}")
        print(f"  - Name: {dev_role.name}")
        print(f"  - Permissions: {dev_role.permissions}")
        print()
        
        # Check all users with Developer role
        dev_users = session.query(User).filter_by(role_id=dev_role.id).all()
        print(f"Users with Developer role (role_id={dev_role.id}):")
        if not dev_users:
            print("  (No users found)")
        else:
            for user in dev_users:
                print(f"  - {user.username} (ID: {user.id}, email: {user.email})")
                print(f"    Active: {user.is_active}")
                print(f"    Permissions from role: {user.role.permissions}")
        print()
        
        # Show all roles with their IDs
        print("All roles in database:")
        for role in session.query(Role).order_by(Role.id).all():
            user_count = session.query(User).filter_by(role_id=role.id).count()
            print(f"  - {role.name} (ID: {role.id}, users: {user_count})")
        
    finally:
        session.close()

if __name__ == "__main__":
    check_developer_role()

