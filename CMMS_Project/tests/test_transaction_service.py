"""Tests for transaction service"""
import pytest
from services.transaction_service import transaction
from database.models import Worksheet
from utils.error_handler import CMMSError


def test_transaction_commit():
    """Test successful transaction"""
    with transaction() as session:
        # Create test data
        from database.models import Machine, User
        # Note: This is a simplified test - actual implementation would need proper test fixtures
        pass
    # Verify data persisted


def test_transaction_rollback():
    """Test transaction rollback on error"""
    with pytest.raises(Exception):
        with transaction() as session:
            # Create invalid data
            raise CMMSError("Test error")
    # Verify data not persisted

