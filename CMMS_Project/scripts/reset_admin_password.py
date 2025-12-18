"""
Script to reset admin password to bcrypt hash
Run this if admin password hash is in old Argon2 format
"""
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.session_manager import SessionLocal
from database.models import User
from services.auth_service import hash_password

def reset_admin_password():
    """Reset admin password to use bcrypt hash"""
    session = SessionLocal()
    try:
        admin = session.query(User).filter_by(username="admin").first()
        if admin:
            print(f"Current hash type: {'Argon2' if '$argon2' in admin.password_hash else 'bcrypt' if '$2' in admin.password_hash else 'unknown'}")
            print("Resetting admin password to bcrypt...")
            admin.password_hash = hash_password("admin123")
            session.commit()
            print("✓ Admin password reset successfully (bcrypt)")
            print("  Username: admin")
            print("  Password: admin123")
        else:
            print("Admin user not found")
    except Exception as e:
        print(f"Error: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    reset_admin_password()

