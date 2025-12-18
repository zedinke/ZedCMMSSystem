"""
Inventory service tesztek
"""

import sys
from pathlib import Path
import pytest

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.database import reset_database
from database.session_manager import SessionLocal
from services import inventory_service
from services.inventory_service import InventoryServiceError, StockError
from database.models import InventoryLevel


@pytest.fixture(autouse=True)
def _reset_db():
    reset_database()
    yield


def test_create_supplier_and_part():
    session = SessionLocal()
    supplier = inventory_service.create_supplier("Supplier A", email="a@example.com", session=session)
    part = inventory_service.create_part(
        sku="PART-001",
        name="Csapágy",
        supplier_id=supplier.id,
        safety_stock=5,
        reorder_quantity=10,
        session=session,
    )

    fetched = inventory_service.get_part_by_sku("PART-001", session=session)
    inv = session.query(InventoryLevel).filter_by(part_id=part.id).first()

    assert fetched is not None
    assert fetched.supplier_id == supplier.id
    assert inv.quantity_on_hand == 0
    session.close()


def test_adjust_stock_increase_and_decrease():
    session = SessionLocal()
    supplier = inventory_service.create_supplier("Supplier B", session=session)
    part = inventory_service.create_part("PART-002", "Szíj", supplier_id=supplier.id, session=session)

    # Bevét
    tx_in = inventory_service.adjust_stock(part.id, 10, "received", session=session)
    inv = inventory_service.get_inventory_level(part.id, session=session)
    assert inv.quantity_on_hand == 10

    # Kiadás
    tx_out = inventory_service.adjust_stock(part.id, -4, "issued", session=session)
    inv = inventory_service.get_inventory_level(part.id, session=session)
    assert inv.quantity_on_hand == 6

    assert tx_in.transaction_type == "received"
    assert tx_out.transaction_type == "issued"
    session.close()


def test_adjust_stock_insufficient():
    session = SessionLocal()
    part = inventory_service.create_part("PART-003", "Csavar", session=session)
    with pytest.raises(StockError):
        inventory_service.adjust_stock(part.id, -1, "issued", session=session)
    session.close()


def test_duplicate_sku():
    session = SessionLocal()
    inventory_service.create_part("PART-004", "Szűrő", session=session)
    with pytest.raises(InventoryServiceError):
        inventory_service.create_part("PART-004", "Másik szűrő", session=session)
    session.close()


def test_invalid_sku():
    session = SessionLocal()
    with pytest.raises(InventoryServiceError):
        inventory_service.create_part("!!bad!!", "Hibás SKU", session=session)
    session.close()


if __name__ == "__main__":
    pytest.main([__file__])
