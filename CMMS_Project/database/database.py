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
import os
from pathlib import Path

# Alembic imports for running migrations
try:
    from alembic import command
    from alembic.config import Config
    ALEMBIC_AVAILABLE = True
except ImportError:
    ALEMBIC_AVAILABLE = False

logger = logging.getLogger(__name__)


def run_migrations():
    """Run Alembic migrations to ensure database schema is up to date"""
    if not ALEMBIC_AVAILABLE:
        logger.warning("Alembic not available, skipping migrations")
        return False
    
    try:
        # Get project root directory (where alembic.ini is located)
        project_root = Path(__file__).parent.parent
        alembic_ini_path = project_root / "alembic.ini"
        
        if not alembic_ini_path.exists():
            logger.warning(f"Alembic config not found at {alembic_ini_path}, skipping migrations")
            return False
        
        # Load Alembic configuration
        alembic_cfg = Config(str(alembic_ini_path))
        
        # Run migrations
        print("  Running database migrations...")
        command.upgrade(alembic_cfg, "head")
        print("  ✓ Migrations applied successfully")
        return True
    except Exception as e:
        logger.warning(f"Failed to run migrations: {e}", exc_info=True)
        print(f"  ⚠ Warning: Failed to run migrations: {e}")
        print("  Attempting to add missing column directly...")
        
        # Fallback: Try to add missing columns directly if migration fails
        try:
            _add_missing_storage_location_id_column()
            _add_missing_operating_hours_update_columns()
            return True
        except Exception as fallback_error:
            logger.error(f"Fallback column addition also failed: {fallback_error}")
            print(f"  ✗ Fallback also failed: {fallback_error}")
            print("  The application will continue, but schema may be out of date.")
            return False


def _add_missing_storage_location_id_column():
    """Fallback: Add storage_location_id column directly if migration fails"""
    try:
        with engine.connect() as conn:
            # Check if column exists
            result = conn.execute(text("""
                SELECT COUNT(*) as col_count
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'stock_batches'
                AND COLUMN_NAME = 'storage_location_id'
            """))
            col_exists = result.fetchone()[0] > 0
            
            if not col_exists:
                print("  Adding storage_location_id column to stock_batches table...")
                # Add the column
                conn.execute(text("""
                    ALTER TABLE stock_batches
                    ADD COLUMN storage_location_id INT NULL,
                    ADD INDEX idx_stock_batches_storage_location_id (storage_location_id),
                    ADD FOREIGN KEY (storage_location_id) REFERENCES storage_locations(id)
                """))
                conn.commit()
                print("  ✓ Column added successfully")
            else:
                print("  ✓ Column already exists")
    except Exception as e:
        logger.error(f"Error adding column directly: {e}", exc_info=True)
        raise


def _add_missing_operating_hours_update_columns():
    """Fallback: Add operating hours update columns directly if migration fails"""
    try:
        with engine.connect() as conn:
            # Check and add operating_hours_update_frequency_type
            result = conn.execute(text("""
                SELECT COUNT(*) as col_count
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'machines'
                AND COLUMN_NAME = 'operating_hours_update_frequency_type'
            """))
            col_exists = result.fetchone()[0] > 0
            
            if not col_exists:
                print("  Adding operating_hours_update_frequency_type column to machines table...")
                conn.execute(text("""
                    ALTER TABLE machines
                    ADD COLUMN operating_hours_update_frequency_type VARCHAR(20) NULL
                """))
                conn.commit()
                print("  ✓ Column added successfully")
            else:
                print("  ✓ Column already exists")
            
            # Check and add operating_hours_update_frequency_value
            result = conn.execute(text("""
                SELECT COUNT(*) as col_count
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'machines'
                AND COLUMN_NAME = 'operating_hours_update_frequency_value'
            """))
            col_exists = result.fetchone()[0] > 0
            
            if not col_exists:
                print("  Adding operating_hours_update_frequency_value column to machines table...")
                conn.execute(text("""
                    ALTER TABLE machines
                    ADD COLUMN operating_hours_update_frequency_value INT NULL
                """))
                conn.commit()
                print("  ✓ Column added successfully")
            else:
                print("  ✓ Column already exists")
            
            # Check and add last_operating_hours_update
            result = conn.execute(text("""
                SELECT COUNT(*) as col_count
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'machines'
                AND COLUMN_NAME = 'last_operating_hours_update'
            """))
            col_exists = result.fetchone()[0] > 0
            
            if not col_exists:
                print("  Adding last_operating_hours_update column to machines table...")
                conn.execute(text("""
                    ALTER TABLE machines
                    ADD COLUMN last_operating_hours_update DATETIME NULL
                """))
                conn.commit()
                print("  ✓ Column added successfully")
            else:
                print("  ✓ Column already exists")
    except Exception as e:
        logger.error(f"Error adding operating hours update columns directly: {e}", exc_info=True)
        raise


def init_database():
    """Initialize database schema and default data"""
    
    print("Initializing database...")
    
    # Try to connect and create tables
    try:
        # Test connection first
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        # Create all tables (for initial setup or if migrations fail)
        Base.metadata.create_all(bind=engine)
        print("✓ Database schema created")
        
        # Run Alembic migrations to ensure schema is up to date
        run_migrations()
        
        # Insert default data
        session = SessionLocal()
        try:
            # Create default roles
            create_default_roles(session)
            
            # Create default admin user
            create_default_admin(session)
            
            # Create default settings
            create_default_settings(session)
            
            session.commit()
            print("✓ Database initialized successfully")
            
        except Exception as e:
            session.rollback()
            print(f"✗ Error initializing database: {e}")
            raise
        finally:
            session.close()
            
    except Exception as e:
        # Connection error - don't fail, just warn
        error_msg = str(e)
        if "Can't connect" in error_msg or "timed out" in error_msg or "OperationalError" in error_msg:
            print(f"⚠ Warning: Cannot connect to MySQL server: {error_msg}")
            print("   The application will start, but database operations may fail.")
            print("   Please check your connection settings in Developer Tools > Environment Variables.")
            print("   You can configure the database connection there.")
            # Don't raise - allow app to start
            return False
        else:
            # Other errors - still raise
            print(f"✗ Error creating schema: {e}")
            raise


def create_default_roles(session):
    """Create all defined roles with default permissions"""
    
    for role_name in ALL_ROLES:
        role = session.query(Role).filter_by(name=role_name).first()
        
        if not role:
            role = Role(
                name=role_name,
                permissions=DEFAULT_PERMISSIONS.get(role_name, {})
            )
            session.add(role)
            print(f"  + Created '{role_name}' role")

    # Ensure IDs are available for subsequent inserts in the same transaction
    session.flush()


def create_default_admin(session):
    """Create default admin user if none exists"""
    
    admin = session.query(User).filter_by(username="admin").first()
    
    if not admin:
        from services.auth_service import hash_password
        
        developer_role = session.query(Role).filter_by(name=ROLE_DEVELOPER).first()
        
        admin = User(
            username="admin",
            email="admin@cmms.local",
            password_hash=hash_password("admin123"),  # Change this in production!
            role_id=developer_role.id,
            language_preference="hu",
            must_change_password=False  # Admin starts without forced password change
        )
        session.add(admin)
        print(f"  + Created default admin user (username: 'admin', password: 'admin123')")
    else:
        print(f"  Admin user already exists")


def create_default_settings(session):
    """Create default application settings"""
    
    # Import here to avoid circular imports
    from config.app_config import TEMPLATES_DIR
    from pathlib import Path
    
    default_settings = {
        "company_name": "CMMS Demo",
        "default_currency": "HUF",
        "timezone": "Europe/Budapest",
        "backup_enabled": "true",
        "backup_frequency_hours": "24",
        "log_retention_days": "30",
    }
    
    for key, value in default_settings.items():
        setting = session.query(AppSetting).filter_by(key=key).first()
        if not setting:
            setting = AppSetting(key=key, value=value)
            session.add(setting)
            print(f"  + Created setting '{key}'")
    
    # Set default QR label template if it exists
    default_qr_template = TEMPLATES_DIR / "default_qr_label_template.docx"
    if default_qr_template.exists():
        existing_template = session.query(AppSetting).filter_by(key="selected_qr_label_template").first()
        if not existing_template:
            setting = AppSetting(
                key="selected_qr_label_template",
                value=str(default_qr_template),
                description="Kiválasztott QR címke sablon"
            )
            session.add(setting)
            print(f"  + Set default QR label template: {default_qr_template.name}")
    
    # Set default storage transfer template if it exists
    default_storage_transfer_template = TEMPLATES_DIR / "default_storage_transfer_template.docx"
    if default_storage_transfer_template.exists():
        existing_template = session.query(AppSetting).filter_by(key="selected_storage_transfer_template").first()
        if not existing_template:
            setting = AppSetting(
                key="selected_storage_transfer_template",
                value=str(default_storage_transfer_template),
                description="Kiválasztott áttárazás sablon"
            )
            session.add(setting)
            print(f"  + Set default storage transfer template: {default_storage_transfer_template.name}")


def drop_all_tables():
    """Drop all tables (for development/testing)"""
    Base.metadata.drop_all(bind=engine)
    print("✓ All tables dropped")


def reset_database():
    """Drop and recreate database"""
    drop_all_tables()
    init_database()
