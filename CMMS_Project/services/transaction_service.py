"""
Transaction management service for CMMS
"""
from contextlib import contextmanager
from typing import Optional, Callable, Any
from sqlalchemy.orm import Session
from database.session_manager import SessionLocal
from utils.error_handler import CMMSError
import logging

logger = logging.getLogger(__name__)


@contextmanager
def transaction(session: Optional[Session] = None, rollback_on_error: bool = True):
    """
    Transaction wrapper with automatic rollback on error
    
    Usage:
        with transaction() as session:
            # Database operations
            create_worksheet(...)
            adjust_stock(...)
            # All operations succeed or all rollback
    
    Args:
        session: Existing session (creates new if None)
        rollback_on_error: If True, rollback on exception
    
    Yields:
        Session: Database session
    """
    should_close = False
    if session is None:
        session = SessionLocal()
        should_close = True
    
    try:
        yield session
        session.commit()
        logger.debug("Transaction committed successfully")
    except Exception as e:
        if rollback_on_error:
            session.rollback()
            logger.error(f"Transaction rolled back due to error: {e}")
        raise
    finally:
        if should_close:
            session.close()


@contextmanager
def nested_transaction(session: Session):
    """
    Nested transaction (savepoint) within existing transaction
    
    Usage:
        with transaction() as outer_session:
            # Some operations
            with nested_transaction(outer_session) as inner_session:
                # Operations that can be rolled back independently
                pass
    
    Args:
        session: Existing session
    
    Yields:
        Session: Same session (for savepoint)
    """
    savepoint = session.begin_nested()
    try:
        yield session
        savepoint.commit()
        logger.debug("Nested transaction committed")
    except Exception as e:
        savepoint.rollback()
        logger.error(f"Nested transaction rolled back: {e}")
        raise


def transactional(func: Callable) -> Callable:
    """
    Decorator for automatic transaction management
    
    Usage:
        @transactional
        def create_worksheet_with_parts(...):
            # Function automatically wrapped in transaction
            pass
    """
    def wrapper(*args, **kwargs):
        # Check if session is already provided
        session = kwargs.get('session')
        if session is not None:
            # Use existing session
            return func(*args, **kwargs)
        else:
            # Create new transaction
            with transaction() as new_session:
                kwargs['session'] = new_session
                return func(*args, **kwargs)
    
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


