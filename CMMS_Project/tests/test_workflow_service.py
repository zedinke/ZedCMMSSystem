"""Tests for workflow service"""
import pytest
from services.workflow_service import (
    validate_transition,
    get_allowed_transitions,
    transition_state,
    StateTransitionError
)


def test_worksheet_transition_valid():
    """Test valid worksheet transition"""
    is_valid, error = validate_transition("worksheet", "Open", "Closed")
    assert is_valid is True
    assert error is None


def test_worksheet_transition_invalid():
    """Test invalid worksheet transition"""
    is_valid, error = validate_transition("worksheet", "Closed", "Open")
    assert is_valid is False
    assert error is not None


def test_pm_task_transitions():
    """Test PM task transitions"""
    allowed = get_allowed_transitions("pm_task", "pending")
    assert "in_progress" in allowed
    assert "overdue" in allowed


def test_transition_state_raises_error():
    """Test that transition_state raises error on invalid transition"""
    with pytest.raises(StateTransitionError):
        transition_state("worksheet", "Closed", "Open")


def test_transition_state_same_state():
    """Test that same state transition is allowed"""
    result = transition_state("worksheet", "Open", "Open", raise_on_error=False)
    assert result is True

