import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.session_manager import SessionLocal
from services import user_service

def check_admin():
    session = SessionLocal()
    try:
        user = session.query(user_service.User).filter_by(username='admin').first()
        if user:
            print(f"Username: {user.username}")
            print(f"User ID: {user.id}")
            print(f"Role Name: {user.role.name}")
            print(f"Role Permissions: {user.role.permissions}")
            print(f"Must Change Password: {user.must_change_password}")
        else:
            print("Admin user not found!")
    finally:
        session.close()

if __name__ == "__main__":
    check_admin()
