"""
Database Connection Management
SQLite connection setup with SQLAlchemy
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from config.app_config import get_database_config, DEBUG
from pathlib import Path

# Global engine variable
_engine = None
_current_mode = None
SessionLocal = None


def create_db_engine(mode: str = "production"):
    """
    Create SQLAlchemy engine for SQLite with optimized connection settings
    
    Args:
        mode: "production" or "learning"
    
    Returns:
        SQLAlchemy engine
    """
    config = get_database_config(mode)
    database_url = config["url"]
    
    # SQLite connection arguments
    connect_args = {
        "check_same_thread": False,  # Allow multi-threaded access
        "timeout": 30,               # Timeout for busy database (seconds)
    }
    
    # SQLite engine with optimizations
    engine = create_engine(
        database_url,
        connect_args=connect_args,
        echo=DEBUG,                  # Log SQL queries if DEBUG=True
        future=True,                 # Use SQLAlchemy 2.0 style
        pool_pre_ping=True,          # Check connection before using
    )
    
    # Enable foreign key constraints for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging for better concurrency
        cursor.execute("PRAGMA synchronous=NORMAL")  # Good balance between safety and performance
        cursor.execute("PRAGMA cache_size=-64000")  # 64MB cache
        cursor.execute("PRAGMA temp_store=MEMORY")  # Store temporary tables in memory
        cursor.close()
    
    return engine


def recreate_engine(mode: str = "production"):
    """
    Recreate the engine with a new mode
    
    Args:
        mode: "production" or "learning"
    """
    global _engine, _current_mode, SessionLocal
    
    # Dispose old engine if exists
    if _engine is not None:
        _engine.dispose()
    
    # Create new engine
    _engine = create_db_engine(mode)
    _current_mode = mode
    
    # Recreate SessionLocal with new engine (for connection.py usage)
    SessionLocal = sessionmaker(bind=_engine, autocommit=False, autoflush=False)
    
    # session_manager.py uses DynamicSessionLocal which always gets current engine
    # No need to update it manually, it will automatically use the new engine
    
    return _engine


# Initialize engine with default mode (production)
# Note: Engine creation doesn't connect immediately - connection happens on first use
try:
    engine = create_db_engine("production")
    _engine = engine
    _current_mode = "production"
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
except Exception as e:
    # If engine creation fails (e.g., invalid config), create a dummy engine
    # The actual connection will be tested when needed
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"Could not create database engine at import time: {e}")
    # Create engine anyway - connection will be tested later
    engine = create_db_engine("production")
    _engine = engine
    _current_mode = "production"
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db() -> Generator[Session, None, None]:
    """
    Get database session for dependency injection (always uses current engine)

    Yields:
        SQLAlchemy Session
    """
    # Always use current engine for mode switching support
    session_factory = sessionmaker(bind=_engine, autocommit=False, autoflush=False)
    db = session_factory()
    try:
        yield db
    finally:
        db.close()


def get_session() -> Session:
    """
    Get a new database session (non-generator version, always uses current engine)

    Returns:
        SQLAlchemy Session (remember to close it!)
    """
    # Always use current engine for mode switching support
    session_factory = sessionmaker(bind=_engine, autocommit=False, autoflush=False)
    return session_factory()
