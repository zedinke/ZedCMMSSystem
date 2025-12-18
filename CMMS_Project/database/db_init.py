"""
Database Initialization
Creates database schema and inserts initial data
"""

from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text
from database.connection import engine
from database.models import Base, Role, User, AppSetting
from database.session_manager import SessionLocal
from config.roles import ALL_ROLES, DEFAULT_PERMISSIONS, ROLE_DEVELOPER, DEFAULT_PASSWORD
import logging

logger = logging.getLogger(__name__)


def init_database():
    """Initialize database - create schema and default data"""
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("✓ Database schema created")

        # Initialize roles
        session = SessionLocal()
        try:
            for role_name in ALL_ROLES:
                existing_role = session.query(Role).filter_by(name=role_name).first()
                if not existing_role:
                    role = Role(name=role_name)
                    session.add(role)
                    logger.info(f"✓ Role created: {role_name}")

            session.commit()
            logger.info("✓ All roles initialized")
        except IntegrityError:
            session.rollback()
            logger.info("⚠ Roles already exist")
        finally:
            session.close()

        # Initialize default user
        session = SessionLocal()
        try:
            default_user = session.query(User).filter_by(username="admin").first()
            if not default_user:
                from services.auth_service import hash_password
                admin_role = session.query(Role).filter_by(name="admin").first()
                user = User(
                    username="admin",
                    email="admin@cmms.local",
                    password_hash=hash_password(DEFAULT_PASSWORD),
                    first_name="System",
                    last_name="Administrator",
                    is_active=True,
                    role_id=admin_role.id if admin_role else None,
                    created_at=datetime.utcnow()
                )
                session.add(user)
                session.commit()
                logger.info("✓ Default admin user created")
            else:
                logger.info("⚠ Default admin user already exists")
        except IntegrityError as e:
            session.rollback()
            logger.error(f"Error initializing admin user: {e}")
        finally:
            session.close()

        logger.info("✓ Database initialization complete")

    except Exception as e:
        logger.error(f"Database initialization error: {str(e)}")
        raise


if __name__ == "__main__":
    init_database()

