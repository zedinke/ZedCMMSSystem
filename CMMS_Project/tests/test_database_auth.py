"""
Database and authentication tests (pytest)
"""

import sys
from pathlib import Path

import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.database import reset_database
from database.session_manager import SessionLocal
from database.models import User, Role
from services.auth_service import (
    hash_password,
    verify_password,
    login,
    logout_session,
    validate_session,
    AuthenticationError,
)


@pytest.fixture(autouse=True)
def _reset_db():
    """Ensure a fresh database for each test"""
    reset_database()
    yield


def test_database_creation():
    session = SessionLocal()
    assert session.query(Role).count() >= 2
    session.close()


def test_default_roles():
    session = SessionLocal()
    developer = session.query(Role).filter_by(name="Developer").first()
    manager = session.query(Role).filter_by(name="Manager").first()
    assert developer is not None
    assert manager is not None
    session.close()


def test_default_admin():
    session = SessionLocal()
    admin = session.query(User).filter_by(username="admin").first()
    assert admin is not None
    assert admin.role.name == "Developer"  # Admin gets Developer role by default
    assert admin.language_preference == "hu"
    session.close()


def test_password_hashing():
    password = "testPassword123"
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True
    assert verify_password("wrongPassword", hashed) is False


def test_login_and_logout_flow():
    token = login("admin", "admin123")
    user_info = validate_session(token)
    assert user_info["username"] == "admin"
    assert user_info["role"] == "Developer"  # Admin gets Developer role by default
    assert logout_session(token) is True
    with pytest.raises(AuthenticationError):
        validate_session(token)


def test_invalid_login():
    with pytest.raises(AuthenticationError):
        login("admin", "wrongPassword")
    with pytest.raises(AuthenticationError):
        login("nonexistent", "password")
