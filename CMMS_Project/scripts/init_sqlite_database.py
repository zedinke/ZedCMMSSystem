"""
Initialize SQLite database on server
Creates database file and initializes schema
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, event
from database.models import Base
from database.db_init import init_database
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_sqlite_db(db_path: str):
    """Initialize SQLite database with specified path"""
    try:
        logger.info(f"Initializing SQLite database at: {db_path}")
        
        # Ensure parent directory exists
        db_path_obj = Path(db_path)
        db_path_obj.parent.mkdir(parents=True, exist_ok=True)
        
        # Create SQLite engine directly
        database_url = f"sqlite:///{db_path}"
        
        # SQLite connection arguments
        connect_args = {
            "check_same_thread": False,
            "timeout": 30,
        }
        
        engine = create_engine(
            database_url,
            connect_args=connect_args,
            echo=False,
            future=True,
            pool_pre_ping=True,
        )
        
        # Enable foreign key constraints for SQLite
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA cache_size=-64000")
            cursor.execute("PRAGMA temp_store=MEMORY")
            cursor.close()
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("✓ Database schema created")
        
        # Temporarily override the engine in db_init module
        import database.connection
        original_engine = database.connection.engine
        database.connection.engine = engine
        
        # Initialize default data (roles, admin user, etc.)
        from database.session_manager import SessionLocal as OriginalSessionLocal
        from sqlalchemy.orm import sessionmaker
        database.connection.SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
        
        try:
            init_database()
            logger.info("✓ Database initialized with default data")
        finally:
            # Restore original engine
            database.connection.engine = original_engine
        
        logger.info(f"✓ SQLite database successfully initialized at {db_path}")
        return True
        
    except Exception as e:
        logger.error(f"✗ Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Initialize SQLite database")
    parser.add_argument(
        "--db-path",
        type=str,
        default="/opt/cmms-backend/data/cmms_prod.db",
        help="Path to SQLite database file (default: /opt/cmms-backend/data/cmms_prod.db)"
    )
    
    args = parser.parse_args()
    
    success = init_sqlite_db(args.db_path)
    sys.exit(0 if success else 1)

