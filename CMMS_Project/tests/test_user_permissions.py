"""
Tests for user service and permissions
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.database import reset_database
from database.session_manager import SessionLocal
from database.models import User
from services import user_service
from services.permission_service import has_permission
from services.permission_checks import CAN_EDIT_INVENTORY, CAN_VIEW_ASSETS
from config.roles import PERM_VIEW_ASSETS, PERM_EDIT_INVENTORY


def setup_db():
    reset_database()


def test_create_user_and_permissions():
    setup_db()
    session = SessionLocal()

    # Create technician
    tech = user_service.create_user(
        username="tech1",
        email="tech1@example.com",
        password="TechPass123",
        role_name="Karbantartó",
        language="hu",
        session=session,
    )

    assert tech.id is not None

    # Permissions - use the actual permission keys from roles
    # Refresh user to get role with permissions loaded
    session.refresh(tech)
    session.refresh(tech.role)
    
    # Check permissions using the role's permission keys
    assert has_permission(tech, PERM_VIEW_ASSETS) is True
    assert has_permission(tech, PERM_EDIT_INVENTORY) is False

    session.close()


def test_change_language():
    setup_db()
    session = SessionLocal()

    tech = user_service.create_user(
        username="tech2",
        email="tech2@example.com",
        password="TechPass123",
        role_name="Karbantartó",
        language="hu",
        session=session,
    )

    user_service.update_user_language(tech.id, "en", session=session)
    updated = session.query(User).filter_by(id=tech.id).first()
    assert updated.language_preference == "en"

    session.close()


def test_deactivate_user():
    setup_db()
    session = SessionLocal()

    tech = user_service.create_user(
        username="tech3",
        email="tech3@example.com",
        password="TechPass123",
        role_name="Karbantartó",
        language="hu",
        session=session,
    )

    user_service.deactivate_user(tech.id, session=session)
    updated = session.query(User).filter_by(id=tech.id).first()
    assert updated.is_active is False

    session.close()


if __name__ == "__main__":
    test_create_user_and_permissions()
    test_change_language()
    test_deactivate_user()
    print("All user/permission tests passed")
