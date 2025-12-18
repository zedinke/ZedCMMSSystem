"""
Database Session Management
Session factory and context management
"""

from sqlalchemy.orm import sessionmaker, Session

def _get_engine():
    """Get the current database engine (always get fresh reference)"""
    from database.connection import engine
    return engine

class DynamicSessionLocal:
    """
    Dynamic SessionLocal that always uses the current engine.
    This allows database mode switching (production/learning) to work correctly.
    """
    def __call__(self):
        """Create a new session using the current engine"""
        session_factory = sessionmaker(autocommit=False, autoflush=False, bind=_get_engine())
        return session_factory()

# Create dynamic SessionLocal instance
SessionLocal = DynamicSessionLocal()


def get_session() -> Session:
    """Get a new database session (always uses current engine)"""
    # Always create session from current engine to ensure mode switching works
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=_get_engine())
    return session_factory()


def get_session_context():
    """Context manager for database sessions"""
    session = get_session()
    try:
        yield session
    finally:
        session.close()
