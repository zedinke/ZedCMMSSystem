"""
PM service tesztek
"""

import sys
from pathlib import Path
import pytest

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.database import reset_database
from database.session_manager import SessionLocal
from services import pm_service, asset_service
from services.pm_service import PMServiceError
from database.models import PMTask


@pytest.fixture(autouse=True)
def _reset_db():
    reset_database()
    yield


def test_create_and_list_due():
    session = SessionLocal()
    pl = asset_service.create_production_line("PL-PM", session=session)
    machine = asset_service.create_machine(pl.id, "Pump-1", session=session)
    task = pm_service.create_pm_task(machine.id, "Kenés", 7, session=session)

    due = pm_service.list_due_tasks(reference_time=task.next_due_date, session=session)
    assert any(t.id == task.id for t in due)
    session.close()


def test_record_execution_updates_due_date():
    session = SessionLocal()
    pl = asset_service.create_production_line("PL-PM2", session=session)
    machine = asset_service.create_machine(pl.id, "Press-PM", session=session)
    task = pm_service.create_pm_task(machine.id, "Szűrő csere", 10, session=session)

    hist = pm_service.record_execution(task.id, completion_status="completed", duration_minutes=30, session=session)
    session.refresh(task)
    assert task.last_executed_date is not None
    assert task.next_due_date > hist.executed_date
    session.close()


def test_invalid_task():
    session = SessionLocal()
    with pytest.raises(PMServiceError):
        pm_service.record_execution(999, session=session)
    session.close()


if __name__ == "__main__":
    pytest.main([__file__])
