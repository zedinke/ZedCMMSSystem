"""
Asset service tesztek
"""

import sys
from pathlib import Path
import pytest

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.database import reset_database
from database.session_manager import SessionLocal
from services import asset_service
from services.asset_service import AssetServiceError
from config.constants import ACTION_CREATED


@pytest.fixture(autouse=True)
def _reset_db():
    reset_database()
    yield


def test_create_machine_module_history():
    session = SessionLocal()
    pl = asset_service.create_production_line("Line-1", session=session)
    machine = asset_service.create_machine(pl.id, "Mixer-1", serial_number="SN-100", session=session)
    module = asset_service.add_module(machine.id, "Motor", session=session)
    hist = asset_service.log_asset_history(machine.id, ACTION_CREATED, "Init", session=session)

    assert machine.production_line_id == pl.id
    assert module.machine_id == machine.id
    assert hist.machine_id == machine.id
    session.close()


def test_duplicate_serial_fails():
    session = SessionLocal()
    pl = asset_service.create_production_line("Line-2", session=session)
    asset_service.create_machine(pl.id, "M1", serial_number="SN-200", session=session)
    with pytest.raises(AssetServiceError):
        asset_service.create_machine(pl.id, "M2", serial_number="SN-200", session=session)
    session.close()


if __name__ == "__main__":
    pytest.main([__file__])
