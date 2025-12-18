"""
Service Error Handling Utilities
Provides consistent error handling patterns for service functions
"""

import logging
from typing import Callable, Any, TypeVar, ParamSpec
from functools import wraps
from sqlalchemy.orm import Session
from utils.error_handler import (
    ValidationError,
    BusinessLogicError,
    NotFoundError,
    StateTransitionError,
    CMMSError
)

logger = logging.getLogger(__name__)

P = ParamSpec('P')
R = TypeVar('R')


def handle_service_errors(
    func: Callable[P, R],
    entity_name: str = None,
    operation_name: str = None
) -> Callable[P, R]:
    """
    Decorator for consistent error handling in service functions
    
    Args:
        func: Service function to wrap
        entity_name: Name of the entity being operated on (for logging)
        operation_name: Name of the operation (for logging)
    
    Usage:
        @handle_service_errors(entity_name="PMTask", operation_name="create")
        def create_pm_task(...):
            ...
    """
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        func_name = operation_name or func.__name__
        entity = entity_name or "Entity"
        
        # Try to extract session from kwargs or args
        session = kwargs.get('session') or (args[0] if args and isinstance(args[0], Session) else None)
        
        try:
            result = func(*args, **kwargs)
            return result
        except ValidationError as e:
            if session:
                try:
                    session.rollback()
                except Exception:
                    pass
            logger.warning(
                f"Validation error in {func.__module__}.{func_name}: {e}",
                exc_info=True
            )
            raise
        except BusinessLogicError as e:
            if session:
                try:
                    session.rollback()
                except Exception:
                    pass
            logger.warning(
                f"Business logic error in {func.__module__}.{func_name}: {e}",
                exc_info=True
            )
            raise
        except NotFoundError as e:
            if session:
                try:
                    session.rollback()
                except Exception:
                    pass
            logger.warning(
                f"Not found error in {func.__module__}.{func_name}: {entity} not found - {e}",
                exc_info=True
            )
            raise
        except StateTransitionError as e:
            if session:
                try:
                    session.rollback()
                except Exception:
                    pass
            logger.warning(
                f"State transition error in {func.__module__}.{func_name}: {e}",
                exc_info=True
            )
            raise
        except Exception as e:
            if session:
                try:
                    session.rollback()
                except Exception:
                    pass
            logger.error(
                f"Unexpected error in {func.__module__}.{func_name}: {e}",
                exc_info=True
            )
            raise
    
    return wrapper


def log_service_error(
    error: Exception,
    service_name: str,
    function_name: str,
    entity_name: str = None,
    session: Session = None
) -> None:
    """
    Log service errors with consistent formatting
    
    Args:
        error: The exception that occurred
        service_name: Name of the service module
        function_name: Name of the function where error occurred
        entity_name: Name of the entity being operated on
        session: Database session (for rollback)
    """
    entity = entity_name or "entity"
    
    if session:
        try:
            session.rollback()
            logger.debug(f"Session rolled back after error in {service_name}.{function_name}")
        except Exception as rollback_error:
            logger.error(f"Error during rollback in {service_name}.{function_name}: {rollback_error}")
    
    if isinstance(error, (ValidationError, BusinessLogicError, NotFoundError, StateTransitionError)):
        logger.warning(
            f"{type(error).__name__} in {service_name}.{function_name}: {error}",
            exc_info=True
        )
    else:
        logger.error(
            f"Unexpected error in {service_name}.{function_name}: {error}",
            exc_info=True
        )

