"""
Update admin user with full name
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.session_manager import SessionLocal
from services import user_service

def update_admin():
    session = SessionLocal()
    try:
        user = session.query(user_service.User).filter_by(username='admin').first()
        if user:
            user.full_name = "Rendszergazda"
            user.phone = "+36 30 000 0000"
            session.commit()
            print(f"✓ Admin user updated:")
            print(f"  - Full name: {user.full_name}")
            print(f"  - Phone: {user.phone}")
        else:
            print("Admin user not found!")
    finally:
        session.close()

if __name__ == "__main__":
    update_admin()
