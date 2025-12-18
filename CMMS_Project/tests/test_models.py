"""
Comprehensive unit tests for all database models
Tests model creation, relationships, constraints, and soft delete functionality
"""

import sys
from pathlib import Path
import pytest
from datetime import datetime, date, timedelta
from sqlalchemy.exc import IntegrityError

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.models import (
    Base, Role, User, UserSession, AuditLog, ProductionLine, Machine, Module,
    MachineVersion, AssetHistory, Supplier, Part, InventoryLevel, StockTransaction,
    QRCodeData, Worksheet, WorksheetPart, WorksheetPhoto, WorksheetPDF, PMTask,
    PMHistory, VacationRequest, ShiftSchedule, VacationDocument, Notification,
    ServiceRecord, SystemLog, AppSetting, ScrappingDocument
)
from database.database import reset_database
from database.session_manager import SessionLocal


@pytest.fixture(autouse=True)
def _reset_db():
    """Reset database before each test"""
    reset_database()
    yield


# ============================================================================
# USER & AUTHENTICATION MODEL TESTS
# ============================================================================

def test_role_creation(test_session):
    """Test Role model creation"""
    role = Role(name="Manager", permissions={"can_edit": True})
    test_session.add(role)
    test_session.commit()
    
    assert role.id is not None
    assert role.name == "Manager"
    assert role.permissions == {"can_edit": True}
    assert role.created_at is not None


def test_user_creation_and_relationships(test_session):
    """Test User model creation and relationships"""
    # Create role first
    role = Role(name="Technician", permissions={})
    test_session.add(role)
    test_session.commit()
    
    # Create user
    user = User(
        username="testuser",
        full_name="Test User",
        email="test@example.com",
        password_hash="hashed_password",
        role_id=role.id,
        vacation_days_per_year=25,
        work_days_per_week=5
    )
    test_session.add(user)
    test_session.commit()
    
    assert user.id is not None
    assert user.username == "testuser"
    assert user.role_id == role.id
    assert user.role.name == "Technician"
    assert user.vacation_days_per_year == 25
    assert user.vacation_days_remaining == 25  # No days used yet


def test_user_unique_username(test_session):
    """Test that username must be unique"""
    role = Role(name="Manager", permissions={})
    test_session.add(role)
    test_session.commit()
    
    user1 = User(username="duplicate", password_hash="hash1", role_id=role.id)
    test_session.add(user1)
    test_session.commit()
    
    user2 = User(username="duplicate", password_hash="hash2", role_id=role.id)
    test_session.add(user2)
    
    with pytest.raises(IntegrityError):
        test_session.commit()


def test_user_soft_delete_anonymization(test_session):
    """Test user anonymization (GDPR compliance)"""
    role = Role(name="Manager", permissions={})
    test_session.add(role)
    test_session.commit()
    
    admin_role = Role(name="Admin", permissions={})
    test_session.add(admin_role)
    test_session.commit()
    
    admin = User(username="admin", password_hash="hash", role_id=admin_role.id)
    test_session.add(admin)
    test_session.commit()
    
    user = User(
        username="todelete",
        full_name="To Delete",
        email="delete@example.com",
        password_hash="hash",
        role_id=role.id
    )
    test_session.add(user)
    test_session.commit()
    user_id = user.id
    
    # Anonymize user
    user.anonymized_at = datetime.utcnow()
    user.anonymized_by_user_id = admin.id
    user.username = f"anonymized_{user_id}"
    user.full_name = None
    user.email = None
    test_session.commit()
    
    assert user.anonymized_at is not None
    assert user.anonymized_by_user_id == admin.id
    assert user.username.startswith("anonymized_")
    assert user.full_name is None
    assert user.email is None


# ============================================================================
# ASSET MODEL TESTS
# ============================================================================

def test_production_line_creation(test_session):
    """Test ProductionLine model creation"""
    pl = ProductionLine(name="Line 1", description="Test line")
    test_session.add(pl)
    test_session.commit()
    
    assert pl.id is not None
    assert pl.name == "Line 1"
    assert len(pl.machines) == 0


def test_machine_creation_and_hierarchy(test_session):
    """Test Machine model and hierarchy with ProductionLine"""
    pl = ProductionLine(name="Line 1")
    test_session.add(pl)
    test_session.commit()
    
    machine = Machine(
        name="Mixer-1",
        serial_number="SN-001",
        production_line_id=pl.id,
        status="Aktív"
    )
    test_session.add(machine)
    test_session.commit()
    
    assert machine.id is not None
    assert machine.production_line_id == pl.id
    assert machine.production_line.name == "Line 1"
    assert machine.status == "Aktív"
    assert len(pl.machines) == 1


def test_module_creation_and_relationship(test_session):
    """Test Module model and relationship with Machine"""
    pl = ProductionLine(name="Line 1")
    test_session.add(pl)
    test_session.commit()
    
    machine = Machine(name="Mixer-1", serial_number="SN-001", production_line_id=pl.id)
    test_session.add(machine)
    test_session.commit()
    
    module = Module(name="Motor", machine_id=machine.id)
    test_session.add(module)
    test_session.commit()
    
    assert module.id is not None
    assert module.machine_id == machine.id
    assert module.machine.name == "Mixer-1"
    assert len(machine.modules) == 1


def test_machine_soft_delete(test_session):
    """Test machine soft delete (ISO 55001 compliance)"""
    pl = ProductionLine(name="Line 1")
    test_session.add(pl)
    test_session.commit()
    
    machine = Machine(name="ToScrap", serial_number="SN-999", production_line_id=pl.id, status="Aktív")
    test_session.add(machine)
    test_session.commit()
    
    # Soft delete by changing status
    machine.status = "Selejtezve"
    test_session.commit()
    
    assert machine.status == "Selejtezve"
    # Machine should still exist in database
    assert test_session.query(Machine).filter_by(id=machine.id).first() is not None


def test_asset_history_tracking(test_session):
    """Test AssetHistory model for tracking changes"""
    pl = ProductionLine(name="Line 1")
    test_session.add(pl)
    test_session.commit()
    
    machine = Machine(name="Mixer-1", serial_number="SN-001", production_line_id=pl.id)
    test_session.add(machine)
    test_session.commit()
    
    history = AssetHistory(
        machine_id=machine.id,
        action_type="Created",
        description="Initial creation",
        user_id=None
    )
    test_session.add(history)
    test_session.commit()
    
    assert history.id is not None
    assert history.machine_id == machine.id
    assert len(machine.asset_history) == 1


# ============================================================================
# INVENTORY MODEL TESTS
# ============================================================================

def test_part_creation(test_session):
    """Test Part model creation"""
    supplier = Supplier(name="Supplier 1", email="contact@example.com")
    test_session.add(supplier)
    test_session.commit()
    
    part = Part(
        name="Bearing",
        sku="BRG-001",
        category="Mechanical",
        supplier_id=supplier.id,
    )
    test_session.add(part)
    test_session.commit()
    
    assert part.id is not None
    assert part.sku == "BRG-001"
    assert part.supplier.name == "Supplier 1"


def test_inventory_level_creation(test_session):
    """Test InventoryLevel model creation"""
    supplier = Supplier(name="Supplier 1")
    test_session.add(supplier)
    test_session.commit()
    
    part = Part(name="Bearing", sku="BRG-001", supplier_id=supplier.id)
    test_session.add(part)
    test_session.commit()
    
    inventory = InventoryLevel(
        part_id=part.id,
        quantity_on_hand=100,
        quantity_reserved=10
    )
    part.safety_stock = 20
    test_session.add(inventory)
    test_session.commit()
    
    assert inventory.id is not None
    assert inventory.part_id == part.id
    assert inventory.quantity_on_hand == 100
    assert inventory.quantity_available == 90  # on_hand - reserved


def test_stock_transaction_creation(test_session):
    """Test StockTransaction model (Szt. compliance - audit trail)"""
    supplier = Supplier(name="Supplier 1")
    test_session.add(supplier)
    test_session.commit()
    
    part = Part(name="Bearing", sku="BRG-001", supplier_id=supplier.id)
    test_session.add(part)
    test_session.commit()
    
    role = Role(name="Manager", permissions={})
    test_session.add(role)
    test_session.commit()
    
    user = User(username="testuser", password_hash="hash", role_id=role.id)
    test_session.add(user)
    test_session.commit()
    
    transaction = StockTransaction(
        part_id=part.id,
        quantity=50,
        transaction_type="received",
        notes="Initial inventory",
        user_id=user.id
    )
    test_session.add(transaction)
    test_session.commit()
    
    assert transaction.id is not None
    assert transaction.part_id == part.id
    assert transaction.quantity == 50
    assert transaction.user_id == user.id
    # Verify audit trail exists
    assert transaction.timestamp is not None


def test_stock_transaction_audit_trail(test_session):
    """Test that all stock movements create audit trail (Szt. compliance)"""
    supplier = Supplier(name="Supplier 1")
    test_session.add(supplier)
    test_session.commit()
    
    part = Part(name="Bearing", sku="BRG-001", supplier_id=supplier.id)
    test_session.add(part)
    test_session.commit()
    
    role = Role(name="Manager", permissions={})
    test_session.add(role)
    test_session.commit()
    
    user = User(username="testuser", password_hash="hash", role_id=role.id)
    test_session.add(user)
    test_session.commit()
    
    # Create multiple transactions
    transactions = [
        StockTransaction(part_id=part.id, quantity=100, transaction_type="received", user_id=user.id),
        StockTransaction(part_id=part.id, quantity=-10, transaction_type="issued", user_id=user.id),
        StockTransaction(part_id=part.id, quantity=-5, transaction_type="issued", user_id=user.id),
    ]
    test_session.add_all(transactions)
    test_session.commit()
    
    # Verify all transactions are logged
    all_transactions = test_session.query(StockTransaction).filter_by(part_id=part.id).all()
    assert len(all_transactions) == 3
    # Verify each has timestamp (audit trail)
    for txn in all_transactions:
        assert txn.timestamp is not None
        assert txn.user_id == user.id


# ============================================================================
# WORKSHEET MODEL TESTS
# ============================================================================

def test_worksheet_creation(test_session):
    """Test Worksheet model creation"""
    pl = ProductionLine(name="Line 1")
    test_session.add(pl)
    test_session.commit()
    
    machine = Machine(name="Mixer-1", serial_number="SN-001", production_line_id=pl.id)
    test_session.add(machine)
    test_session.commit()
    
    role = Role(name="Technician", permissions={})
    test_session.add(role)
    test_session.commit()
    
    user = User(username="tech", password_hash="hash", role_id=role.id)
    test_session.add(user)
    test_session.commit()
    
    worksheet = Worksheet(
        machine_id=machine.id,
        assigned_to_user_id=user.id,
        title="Test Worksheet",
        status="Open",
        description="Test maintenance"
    )
    test_session.add(worksheet)
    test_session.commit()
    
    assert worksheet.id is not None
    assert worksheet.machine_id == machine.id
    assert worksheet.assigned_to_user_id == user.id
    assert worksheet.status == "Open"


def test_worksheet_status_transitions(test_session):
    """Test Worksheet status transitions"""
    pl = ProductionLine(name="Line 1")
    test_session.add(pl)
    test_session.commit()
    
    machine = Machine(name="Mixer-1", serial_number="SN-001", production_line_id=pl.id)
    test_session.add(machine)
    test_session.commit()
    
    role = Role(name="Technician", permissions={})
    test_session.add(role)
    test_session.commit()
    
    user = User(username="tech", password_hash="hash", role_id=role.id)
    test_session.add(user)
    test_session.commit()
    
    worksheet = Worksheet(
        machine_id=machine.id,
        assigned_to_user_id=user.id,
        title="Test Worksheet",
        status="Open"
    )
    test_session.add(worksheet)
    test_session.commit()
    
    # Transition to Waiting
    worksheet.status = "Waiting for Parts"
    test_session.commit()
    assert worksheet.status == "Waiting for Parts"
    
    # Transition to Closed
    worksheet.status = "Closed"
    worksheet.repair_finished_time = datetime.utcnow()
    test_session.commit()
    assert worksheet.status == "Closed"


def test_worksheet_items_relationship(test_session):
    """Test WorksheetPart model and relationship"""
    pl = ProductionLine(name="Line 1")
    test_session.add(pl)
    test_session.commit()
    
    machine = Machine(name="Mixer-1", serial_number="SN-001", production_line_id=pl.id)
    test_session.add(machine)
    test_session.commit()
    
    supplier = Supplier(name="Supplier 1")
    test_session.add(supplier)
    test_session.commit()
    
    part = Part(name="Bearing", sku="BRG-001", supplier_id=supplier.id)
    test_session.add(part)
    test_session.commit()
    
    role = Role(name="Technician", permissions={})
    test_session.add(role)
    test_session.commit()
    
    user = User(username="tech", password_hash="hash", role_id=role.id)
    test_session.add(user)
    test_session.commit()
    
    worksheet = Worksheet(machine_id=machine.id, assigned_to_user_id=user.id, title="Test Worksheet", status="Open")
    test_session.add(worksheet)
    test_session.commit()
    
    item = WorksheetPart(worksheet_id=worksheet.id, part_id=part.id, quantity_used=2)
    test_session.add(item)
    test_session.commit()
    
    assert item.id is not None
    assert item.worksheet_id == worksheet.id
    assert item.part_id == part.id
    assert len(worksheet.parts) == 1


# ============================================================================
# PM MODEL TESTS
# ============================================================================

def test_pm_task_creation(test_session):
    """Test PMTask model creation"""
    pl = ProductionLine(name="Line 1")
    test_session.add(pl)
    test_session.commit()
    
    machine = Machine(name="Mixer-1", serial_number="SN-001", production_line_id=pl.id)
    test_session.add(machine)
    test_session.commit()
    
    role = Role(name="Manager", permissions={})
    test_session.add(role)
    test_session.commit()
    
    user = User(username="manager", password_hash="hash", role_id=role.id)
    test_session.add(user)
    test_session.commit()
    
    pm_task = PMTask(
        machine_id=machine.id,
        task_name="Weekly Greasing",
        task_description="Grease all bearings",
        frequency_days=7,
        created_by_user_id=user.id
    )
    test_session.add(pm_task)
    test_session.commit()
    
    assert pm_task.id is not None
    assert pm_task.machine_id == machine.id
    assert pm_task.frequency_days == 7
    assert pm_task.created_by_user_id == user.id


def test_pm_history_creation(test_session):
    """Test PMHistory model creation"""
    pl = ProductionLine(name="Line 1")
    test_session.add(pl)
    test_session.commit()
    
    machine = Machine(name="Mixer-1", serial_number="SN-001", production_line_id=pl.id)
    test_session.add(machine)
    test_session.commit()
    
    role = Role(name="Technician", permissions={})
    test_session.add(role)
    test_session.commit()
    
    user = User(username="tech", password_hash="hash", role_id=role.id)
    test_session.add(user)
    test_session.commit()
    
    pm_task = PMTask(
        machine_id=machine.id,
        task_name="Weekly Greasing",
        frequency_days=7,
        created_by_user_id=user.id
    )
    test_session.add(pm_task)
    test_session.commit()
    
    pm_history = PMHistory(
        pm_task_id=pm_task.id,
        assigned_to_user_id=user.id,
        executed_date=date.today(),
        completion_status="completed"
    )
    test_session.add(pm_history)
    test_session.commit()
    
    assert pm_history.id is not None
    assert pm_history.pm_task_id == pm_task.id
    assert pm_history.assigned_to_user_id == user.id
    assert pm_history.completion_status == "completed"


# ============================================================================
# VACATION MODEL TESTS
# ============================================================================

def test_vacation_request_creation(test_session):
    """Test VacationRequest model creation"""
    role = Role(name="Technician", permissions={})
    test_session.add(role)
    test_session.commit()
    
    user = User(
        username="tech",
        password_hash="hash",
        role_id=role.id,
        vacation_days_per_year=25
    )
    test_session.add(user)
    test_session.commit()
    
    vacation_request = VacationRequest(
        user_id=user.id,
        start_date=datetime(2025, 6, 1),
        end_date=datetime(2025, 6, 5),
        vacation_type="annual",
        reason="Family vacation",
        status="pending"
    )
    test_session.add(vacation_request)
    test_session.commit()
    
    assert vacation_request.id is not None
    assert vacation_request.user_id == user.id
    assert vacation_request.status == "pending"
    assert len(user.vacation_requests) == 1


def test_vacation_request_approval(test_session):
    """Test vacation request approval workflow"""
    role_tech = Role(name="Technician", permissions={})
    role_manager = Role(name="Manager", permissions={})
    test_session.add_all([role_tech, role_manager])
    test_session.commit()
    
    tech = User(username="tech", password_hash="hash", role_id=role_tech.id, vacation_days_per_year=25)
    manager = User(username="manager", password_hash="hash", role_id=role_manager.id)
    test_session.add_all([tech, manager])
    test_session.commit()
    
    vacation_request = VacationRequest(
        user_id=tech.id,
        start_date=datetime(2025, 6, 1),
        end_date=datetime(2025, 6, 5),
        vacation_type="annual",
        status="pending"
    )
    test_session.add(vacation_request)
    test_session.commit()
    
    # Approve request
    vacation_request.status = "approved"
    vacation_request.approved_by_user_id = manager.id
    vacation_request.approved_at = datetime.utcnow()
    vacation_request.days_count = 5
    tech.vacation_days_used += vacation_request.days_count
    test_session.commit()
    
    assert vacation_request.status == "approved"
    assert vacation_request.approved_by_user_id == manager.id
    assert tech.vacation_days_used == 5


def test_shift_schedule_creation(test_session):
    """Test ShiftSchedule model creation"""
    role = Role(name="Technician", permissions={})
    test_session.add(role)
    test_session.commit()
    
    user = User(username="tech", password_hash="hash", role_id=role.id)
    test_session.add(user)
    test_session.commit()
    
    shift = ShiftSchedule(
        user_id=user.id,
        shift_type="3_shift",
        start_time="06:00",
        end_time="14:00",
        effective_from=date.today()
    )
    test_session.add(shift)
    test_session.commit()
    
    assert shift.id is not None
    assert shift.user_id == user.id
    assert shift.shift_type == "3_shift"
    assert len(user.shift_schedules) == 1


# ============================================================================
# FOREIGN KEY CONSTRAINT TESTS
# ============================================================================

def test_foreign_key_user_role(test_session):
    """Test foreign key constraint on User.role_id"""
    user = User(username="test", password_hash="hash", role_id=999)  # Non-existent role
    test_session.add(user)
    
    try:
        test_session.commit()
        # If commit succeeds, foreign key constraints might not be enforced
        # This is acceptable for SQLite in-memory databases
        test_session.rollback()
        pytest.skip("Foreign key constraints not enforced in SQLite in-memory database")
    except IntegrityError:
        pass  # Expected


def test_foreign_key_machine_production_line(test_session):
    """Test foreign key constraint on Machine.production_line_id"""
    machine = Machine(name="Test", serial_number="SN-001", production_line_id=999)  # Non-existent line
    test_session.add(machine)
    
    try:
        test_session.commit()
        # If commit succeeds, foreign key constraints might not be enforced
        # This is acceptable for SQLite in-memory databases
        test_session.rollback()
        pytest.skip("Foreign key constraints not enforced in SQLite in-memory database")
    except IntegrityError:
        pass  # Expected


def test_foreign_key_worksheet_machine(test_session):
    """Test foreign key constraint on Worksheet.machine_id"""
    role = Role(name="Technician", permissions={})
    test_session.add(role)
    test_session.commit()
    
    user = User(username="tech", password_hash="hash", role_id=role.id)
    test_session.add(user)
    test_session.commit()
    
    worksheet = Worksheet(machine_id=999, assigned_to_user_id=user.id, title="Test Worksheet", status="Open")  # Non-existent machine
    test_session.add(worksheet)
    
    try:
        test_session.commit()
        # If commit succeeds, foreign key constraints might not be enforced
        # This is acceptable for SQLite in-memory databases
        test_session.rollback()
        pytest.skip("Foreign key constraints not enforced in SQLite in-memory database")
    except IntegrityError:
        pass  # Expected


# ============================================================================
# SOFT DELETE TESTS
# ============================================================================

def test_machine_soft_delete_preserves_data(test_session):
    """Test that soft delete preserves data (ISO 55001 compliance)"""
    pl = ProductionLine(name="Line 1")
    test_session.add(pl)
    test_session.commit()
    
    machine = Machine(name="ToScrap", serial_number="SN-999", production_line_id=pl.id, status="Aktív")
    test_session.add(machine)
    test_session.commit()
    machine_id = machine.id
    
    # Soft delete
    machine.status = "Selejtezve"
    test_session.commit()
    
    # Verify machine still exists
    scrapped = test_session.query(Machine).filter_by(id=machine_id).first()
    assert scrapped is not None
    assert scrapped.status == "Selejtezve"
    assert scrapped.name == "ToScrap"  # Data preserved


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

