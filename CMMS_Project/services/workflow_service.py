"""
Centralized workflow state management
"""
from enum import Enum
from typing import Dict, Set, Optional, Tuple
from utils.error_handler import StateTransitionError
import logging

logger = logging.getLogger(__name__)


class WorksheetState(Enum):
    """Worksheet states"""
    OPEN = "Open"
    WAITING = "Waiting for Parts"
    CLOSED = "Closed"


class PMTaskState(Enum):
    """PM Task states"""
    PENDING = "pending"
    DUE_TODAY = "due_today"
    OVERDUE = "overdue"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class MachineState(Enum):
    """Machine states"""
    ACTIVE = "Active"  # or "Aktív" in Hungarian
    STOPPED = "Stopped"
    MAINTENANCE = "Maintenance"
    SCRAPPED = "Selejtezve"  # Scrapped


class PartState(Enum):
    """Part states (for future use when Part.status field is added)"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    OBSOLETE = "obsolete"


# Centralized workflow rules
WORKFLOW_RULES: Dict[str, Dict[Enum, Set[Enum]]] = {
    "worksheet": {
        WorksheetState.OPEN: {WorksheetState.WAITING, WorksheetState.CLOSED},
        WorksheetState.WAITING: {WorksheetState.CLOSED},
        WorksheetState.CLOSED: set(),  # Terminal state
    },
    "pm_task": {
        PMTaskState.PENDING: {
            PMTaskState.DUE_TODAY, 
            PMTaskState.OVERDUE, 
            PMTaskState.IN_PROGRESS,
            PMTaskState.COMPLETED,  # Allow direct completion from pending
            PMTaskState.CANCELLED
        },
        PMTaskState.DUE_TODAY: {
            PMTaskState.IN_PROGRESS,
            PMTaskState.COMPLETED,  # Allow direct completion from due_today
            PMTaskState.OVERDUE
        },
        PMTaskState.OVERDUE: {
            PMTaskState.IN_PROGRESS,
            PMTaskState.COMPLETED,  # Allow direct completion from overdue
            PMTaskState.CANCELLED
        },
        PMTaskState.IN_PROGRESS: {
            PMTaskState.COMPLETED, 
            PMTaskState.CANCELLED
        },
        PMTaskState.COMPLETED: set(),  # Terminal state
        PMTaskState.CANCELLED: set(),  # Terminal state
    },
    "machine": {
        MachineState.ACTIVE: {
            MachineState.STOPPED,
            MachineState.MAINTENANCE,
            MachineState.SCRAPPED
        },
        MachineState.STOPPED: {
            MachineState.ACTIVE,
            MachineState.MAINTENANCE,
            MachineState.SCRAPPED
        },
        MachineState.MAINTENANCE: {
            MachineState.ACTIVE,
            MachineState.STOPPED,
            MachineState.SCRAPPED
        },
        MachineState.SCRAPPED: set(),  # Terminal state
    },
    # Part workflow - commented out until Part.status field is added to model
    # "part": {
    #     PartState.ACTIVE: {PartState.INACTIVE, PartState.OBSOLETE},
    #     PartState.INACTIVE: {PartState.ACTIVE, PartState.OBSOLETE},
    #     PartState.OBSOLETE: set(),  # Terminal state
    # }
}


def _normalize_machine_state(state: str) -> str:
    """Normalize machine state values (handle Hungarian/English variants)"""
    if not state:
        return "Active"  # Default
    state_normalized = state.strip()
    # Handle Hungarian "Aktív" -> "Active"
    if state_normalized.lower() in ["aktív", "active"]:
        return "Active"
    # Handle Hungarian "Selejtezve" -> keep as is (matches enum value)
    if state_normalized.lower() in ["selejtezve", "scrapped"]:
        return "Selejtezve"
    # Other states are consistent (Stopped, Maintenance)
    return state_normalized


def validate_transition(
    entity_type: str, 
    current_state: str, 
    new_state: str
) -> Tuple[bool, Optional[str]]:
    """
    Validate state transition
    
    Args:
        entity_type: Entity type ("worksheet", "pm_task", "machine")
        current_state: Current state
        new_state: Target state
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    rules = WORKFLOW_RULES.get(entity_type)
    if not rules:
        return False, f"Unknown entity type: {entity_type}"
    
    # Normalize machine states (handle Hungarian/English variants)
    if entity_type == "machine":
        current_state = _normalize_machine_state(current_state)
        new_state = _normalize_machine_state(new_state)
    
    # Convert string states to Enum
    state_enums = {
        "worksheet": WorksheetState,
        "pm_task": PMTaskState,
        "machine": MachineState,
        # "part": PartState,  # Uncomment when Part.status field is added
    }
    
    enum_class = state_enums.get(entity_type)
    if not enum_class:
        return False, f"No enum class for {entity_type}"
    
    try:
        # Try to match enum by value (case-insensitive for machine states)
        if entity_type == "machine":
            current_enum = None
            new_enum = None
            for state_enum in enum_class:
                if state_enum.value.lower() == current_state.lower():
                    current_enum = state_enum
                if state_enum.value.lower() == new_state.lower():
                    new_enum = state_enum
            if current_enum is None or new_enum is None:
                return False, f"Invalid state value for machine: current={current_state}, new={new_state}"
        else:
            current_enum = enum_class(current_state)
            new_enum = enum_class(new_state)
    except ValueError:
        return False, f"Invalid state value"
    
    # Check if transition is allowed
    allowed_states = rules.get(current_enum, set())
    if new_enum in allowed_states or current_enum == new_enum:
        return True, None
    
    return False, (
        f"Invalid transition: {current_state} -> {new_state}. "
        f"Allowed: {[s.value for s in allowed_states]}"
    )


def get_allowed_transitions(entity_type: str, current_state: str) -> Set[str]:
    """
    Get allowed transitions from current state
    
    Args:
        entity_type: Entity type
        current_state: Current state
    
    Returns:
        Set of allowed state values
    """
    rules = WORKFLOW_RULES.get(entity_type, {})
    state_enums = {
        "worksheet": WorksheetState,
        "pm_task": PMTaskState,
        "machine": MachineState,
        # "part": PartState,  # Uncomment when Part.status field is added
    }
    
    enum_class = state_enums.get(entity_type)
    if not enum_class:
        return set()
    
    # Normalize machine states
    if entity_type == "machine":
        current_state = _normalize_machine_state(current_state)
    
    try:
        # Try to match enum by value (case-insensitive for machine states)
        if entity_type == "machine":
            current_enum = None
            for state_enum in enum_class:
                if state_enum.value.lower() == current_state.lower():
                    current_enum = state_enum
                    break
            if current_enum is None:
                return set()
        else:
            current_enum = enum_class(current_state)
        allowed = rules.get(current_enum, set())
        return {s.value for s in allowed}
    except ValueError:
        return set()


def transition_state(
    entity_type: str,
    current_state: str,
    new_state: str,
    raise_on_error: bool = True
) -> bool:
    """
    Validate and perform state transition
    
    Args:
        entity_type: Entity type
        current_state: Current state
        new_state: Target state
        raise_on_error: If True, raise exception on invalid transition
    
    Returns:
        True if transition is valid
    
    Raises:
        StateTransitionError if transition is invalid and raise_on_error=True
    """
    is_valid, error_msg = validate_transition(entity_type, current_state, new_state)
    
    if not is_valid:
        if raise_on_error:
            raise StateTransitionError(
                entity_type,
                current_state,
                new_state,
                details={"error_message": error_msg}
            )
        return False
    
    logger.info(
        f"State transition validated: {entity_type} {current_state} -> {new_state}"
    )
    return True


