"""
Worksheet service tesztek
"""

import sys
from pathlib import Path
import pytest

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.database import reset_database
from database.session_manager import SessionLocal
from database.models import User, Worksheet
from services import asset_service, worksheet_service, inventory_service
from services.worksheet_service import WorksheetServiceError
from config.constants import WORKSHEET_STATUS_CLOSED, WORKSHEET_STATUS_OPEN, TRANSACTION_TYPE_RECEIVED
from datetime import datetime


@pytest.fixture(autouse=True)
def _reset_db():
    reset_database()
    yield


def _get_admin(session):
    return session.query(User).filter_by(username="admin").first()


def test_create_and_close_worksheet_with_parts():
    session = SessionLocal()
    admin = _get_admin(session)

    pl = asset_service.create_production_line("Line-W1", session=session)
    machine = asset_service.create_machine(pl.id, "Press-1", session=session)

    part = inventory_service.create_part("WS-PART-1", "Szuro", session=session)
    inventory_service.adjust_stock(part.id, 5, TRANSACTION_TYPE_RECEIVED, session=session)

    ws = worksheet_service.create_worksheet(machine.id, admin.id, "Hiba javitas", description="Hiba javítás leírása", breakdown_time=datetime.now(), session=session)
    ws.fault_cause = "Teszt hiba"
    session.commit()
    wp = worksheet_service.add_part_to_worksheet(ws.id, part.id, 2, unit_cost_at_time=100.0, session=session)

    inv = inventory_service.get_inventory_level(part.id, session=session)
    assert inv.quantity_on_hand == 3
    assert wp.quantity_used == 2

    # update_status commits internally and returns the updated worksheet
    # Since we pass session=session, it uses our session and commits in it
    # The result should be the updated worksheet
    result = worksheet_service.update_status(ws.id, WORKSHEET_STATUS_CLOSED, repair_finished_time=datetime.now(), session=session)
    # Use the result directly - it should have the updated status
    # If result is None or doesn't have the right status, something went wrong
    assert result is not None, "update_status should return a worksheet"
    # The result should have the updated status
    # Note: The result might be from a reloaded query, so it should be fresh
    assert result.status == WORKSHEET_STATUS_CLOSED, f"Expected Closed, got {result.status}"
    assert result.closed_at is not None
    session.close()


def test_invalid_status_transition():
    session = SessionLocal()
    admin = _get_admin(session)
    pl = asset_service.create_production_line("Line-W2", session=session)
    machine = asset_service.create_machine(pl.id, "Press-2", session=session)
    ws = worksheet_service.create_worksheet(machine.id, admin.id, "Teszt", description="Teszt leírás", breakdown_time=datetime.now(), session=session)
    ws.fault_cause = "Teszt hiba"
    session.commit()

    worksheet_service.update_status(ws.id, WORKSHEET_STATUS_CLOSED, repair_finished_time=datetime.now(), session=session)
    with pytest.raises(WorksheetServiceError):
        worksheet_service.update_status(ws.id, WORKSHEET_STATUS_OPEN, session=session)
    session.close()


if __name__ == "__main__":
    pytest.main([__file__])
