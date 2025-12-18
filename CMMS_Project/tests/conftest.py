import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import uuid

# Pytest fixture für in-memory database für integration tests
@pytest.fixture(scope="function")
def test_session():
    """Create fresh in-memory SQLite database for each test"""
    from database import Base
    
    # Use in-memory SQLite for test isolation
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    
    TestSession = sessionmaker(bind=engine)
    session = TestSession()
    
    yield session
    
    session.close()
    engine.dispose()


@pytest.fixture(scope="function")
def unique_id():
    """Generate unique identifier for test data"""
    return uuid.uuid4().hex[:8]


@pytest.fixture(scope="function")
def unique_timestamp():
    """Generate timestamp for unique test data"""
    return datetime.utcnow().timestamp()
