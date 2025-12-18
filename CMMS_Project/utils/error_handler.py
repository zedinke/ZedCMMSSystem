"""
Structured error handling for CMMS system
"""
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class CMMSError(Exception):
    """Base exception for CMMS system"""
    def __init__(
        self, 
        message: str, 
        error_code: str = None, 
        details: Dict[str, Any] = None,
        user_message: str = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.user_message = user_message or message
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for API responses"""
        return {
            "error": self.error_code or "UNKNOWN_ERROR",
            "message": self.user_message,
            "details": self.details
        }


class ValidationError(CMMSError):
    """Validation error - invalid input data"""
    def __init__(self, message: str, field: str = None, **kwargs):
        super().__init__(message, error_code="VALIDATION_ERROR", **kwargs)
        if field:
            self.details["field"] = field


class BusinessLogicError(CMMSError):
    """Business logic error - rule violation"""
    def __init__(self, message: str, rule: str = None, **kwargs):
        super().__init__(message, error_code="BUSINESS_LOGIC_ERROR", **kwargs)
        if rule:
            self.details["rule"] = rule


class NotFoundError(CMMSError):
    """Resource not found error"""
    def __init__(self, resource_type: str, resource_id: int = None, **kwargs):
        message = f"{resource_type} not found"
        if resource_id:
            message += f" (ID: {resource_id})"
        super().__init__(message, error_code="NOT_FOUND", **kwargs)
        self.details["resource_type"] = resource_type
        if resource_id:
            self.details["resource_id"] = resource_id


class PermissionError(CMMSError):
    """Permission denied error"""
    def __init__(self, action: str = None, resource: str = None, **kwargs):
        message = "Permission denied"
        if action and resource:
            message = f"Permission denied: {action} on {resource}"
        super().__init__(message, error_code="PERMISSION_DENIED", **kwargs)
        if action:
            self.details["action"] = action
        if resource:
            self.details["resource"] = resource


class StateTransitionError(CMMSError):
    """Invalid state transition error"""
    def __init__(
        self, 
        entity_type: str, 
        current_state: str, 
        target_state: str, 
        **kwargs
    ):
        message = (
            f"Invalid state transition for {entity_type}: "
            f"{current_state} -> {target_state}"
        )
        super().__init__(message, error_code="INVALID_STATE_TRANSITION", **kwargs)
        self.details.update({
            "entity_type": entity_type,
            "current_state": current_state,
            "target_state": target_state
        })


