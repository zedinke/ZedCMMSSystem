"""
SQLAlchemy ORM Models
Defines all database entities and relationships
"""

from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Date, Boolean, JSON, Text,
    ForeignKey, UniqueConstraint, Index, Table, CheckConstraint
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


def utcnow():
    """Timezone-aware UTC now for defaults and onupdate."""
    return datetime.now(timezone.utc)


def get_date_categories(dt: datetime) -> tuple:
    """Get year, month, week, day categories for a datetime"""
    year = dt.year
    month = dt.month
    # ISO week number
    week = dt.isocalendar()[1]
    day = dt.day
    return year, month, week, day

# ============================================================================
# USER & AUTHENTICATION MODELS
# ============================================================================

class Role(Base):
    """User roles (Manager, Technician)"""
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)  # Manager, Technician
    permissions = Column(JSON, default={})  # Feature flags: {can_edit_inventory: True, ...}
    created_at = Column(DateTime, default=utcnow)
    
    # Relationships
    users = relationship("User", back_populates="role")
    
    def __repr__(self):
        return f"<Role {self.name}>"


class User(Base):
    """Application users"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    full_name = Column(String(100), nullable=True)  # Teljes név
    email = Column(String(120), unique=True, nullable=True)  # Email is now optional
    phone = Column(String(20), nullable=True)  # Telefonszám
    profile_picture = Column(Text, nullable=True)  # Base64 encoded image or file path
    password_hash = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    language_preference = Column(String(10), default="hu")  # hu, en
    must_change_password = Column(Boolean, default=False)  # Force password change on next login
    anonymized_at = Column(DateTime, nullable=True)  # GDPR Right to be Forgotten
    anonymized_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    # Vacation fields
    vacation_days_per_year = Column(Integer, default=20)  # Éves szabadság napok száma
    vacation_days_used = Column(Integer, default=0)  # Használt szabadság napok
    # Shift schedule fields
    shift_type = Column(String(50), nullable=True)  # "single", "3_shift", "4_shift"
    shift_start_time = Column(String(10), nullable=True)  # Műszak kezdési idő (pl. "06:00")
    shift_end_time = Column(String(10), nullable=True)  # Műszak befejezési idő (pl. "14:00")
    work_days_per_week = Column(Integer, default=5)  # Heti munkanapok száma
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    
    # Relationships
    role = relationship("Role", back_populates="users")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    worksheets = relationship("Worksheet", back_populates="assigned_user", foreign_keys="Worksheet.assigned_to_user_id")
    audit_logs = relationship("AuditLog", back_populates="user")
    pm_histories_assigned = relationship("PMHistory", back_populates="assigned_user", foreign_keys="PMHistory.assigned_to_user_id")
    pm_histories_completed = relationship("PMHistory", back_populates="completed_user", foreign_keys="PMHistory.completed_by_user_id")
    pm_tasks_assigned = relationship("PMTask", foreign_keys="PMTask.assigned_to_user_id", back_populates="assigned_user")
    pm_tasks_created = relationship("PMTask", foreign_keys="PMTask.created_by_user_id", back_populates="created_by_user")
    stock_transactions = relationship("StockTransaction", back_populates="user")
    notifications = relationship("Notification", foreign_keys="Notification.user_id", cascade="all, delete-orphan", overlaps="user")
    service_records_created = relationship("ServiceRecord", foreign_keys="ServiceRecord.created_by_user_id", overlaps="created_by_user")
    # Vacation relationships
    vacation_requests = relationship("VacationRequest", foreign_keys="VacationRequest.user_id", back_populates="user")
    vacation_requests_approved = relationship("VacationRequest", foreign_keys="VacationRequest.approved_by_user_id", back_populates="approved_by")
    shift_schedules = relationship("ShiftSchedule", back_populates="user")
    shift_overrides = relationship("ShiftOverride", foreign_keys="ShiftOverride.user_id", back_populates="user")
    
    __table_args__ = (
        Index('idx_username', 'username'),
    )
    
    @property
    def vacation_days_remaining(self) -> int:
        """Calculate remaining vacation days"""
        return max(0, (self.vacation_days_per_year or 0) - (self.vacation_days_used or 0))
    
    def __repr__(self):
        return f"<User {self.username}>"


class UserSession(Base):
    """Active user sessions with tokens"""
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token_hash = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=utcnow)
    expires_at = Column(DateTime, nullable=False)
    last_activity_at = Column(DateTime, default=utcnow)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    
    def is_expired(self) -> bool:
        """Check if session is expired"""
        expiry = self.expires_at
        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
        return utcnow() > expiry
    
    def __repr__(self):
        return f"<UserSession user_id={self.user_id}>"


class AuditLog(Base):
    """Audit trail for all operations"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action_type = Column(String(50), nullable=False)  # login, create, update, delete
    entity_type = Column(String(50), nullable=False)  # User, Asset, Part, Worksheet
    entity_id = Column(Integer)
    changes = Column(JSON, default={})  # {field: {old: val, new: val}, ...}
    timestamp = Column(DateTime, default=utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    
    __table_args__ = (
        Index('idx_audit_logs_timestamp', 'timestamp'),
        Index('idx_audit_logs_entity', 'entity_type', 'entity_id'),
    )
    
    def __repr__(self):
        return f"<AuditLog {self.action_type} {self.entity_type}:{self.entity_id}>"


# ============================================================================
# ASSET MANAGEMENT MODELS
# ============================================================================

class ProductionLine(Base):
    """Production lines (top level of asset hierarchy)"""
    __tablename__ = "production_lines"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True)  # Unique code/identifier for the production line
    description = Column(Text)
    location = Column(String(200))
    status = Column(String(50), default="Active")  # Active, Inactive, Maintenance, etc.
    capacity = Column(String(200))  # Production capacity description
    responsible_person = Column(String(200))  # Responsible person/team
    commission_date = Column(DateTime)  # Commission/start date
    notes = Column(Text)  # Additional notes
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    
    # Relationships
    machines = relationship("Machine", back_populates="production_line", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('name', name='uq_production_line_name'),
    )
    
    def __repr__(self):
        return f"<ProductionLine {self.name}>"



# Valid association table for Many-to-Many relationship
machine_parts = Table(
    "machine_parts",
    Base.metadata,
    Column("machine_id", Integer, ForeignKey("machines.id"), primary_key=True),
    Column("part_id", Integer, ForeignKey("parts.id"), primary_key=True),
)

class Machine(Base):
    """Machines within production lines"""
    __tablename__ = "machines"
    
    id = Column(Integer, primary_key=True)
    production_line_id = Column(Integer, ForeignKey("production_lines.id"), nullable=False)
    name = Column(String(100), nullable=False)
    serial_number = Column(String(100), unique=True)
    model = Column(String(100))
    manufacturer = Column(String(100))
    manual_pdf_path = Column(String(500))  # Path to PDF manual
    
    # Basic fields
    install_date = Column(DateTime)
    status = Column(String(50), default="Active")  # Active, Stopped, Scrapped
    maintenance_interval = Column(String(100))  # e.g. "Monthly", "500 hours"
    
    # Extended CMMS fields
    asset_tag = Column(String(50), unique=True)  # Asset identification tag/number
    purchase_date = Column(DateTime)  # Date of purchase
    purchase_price = Column(Float)  # Purchase price
    warranty_expiry_date = Column(DateTime)  # Warranty expiration date
    supplier = Column(String(200))  # Supplier/vendor name
    operating_hours = Column(Float, default=0.0)  # Total operating hours
    last_service_date = Column(DateTime)  # Last service/maintenance date
    next_service_date = Column(DateTime)  # Next scheduled service date
    # Operating hours update frequency settings
    operating_hours_update_frequency_type = Column(String(20))  # 'day', 'week', 'month'
    operating_hours_update_frequency_value = Column(Integer)  # How many days/weeks/months
    last_operating_hours_update = Column(DateTime)  # Last time operating hours were updated
    criticality_level = Column(String(50))  # Critical, High, Medium, Low
    energy_consumption = Column(String(100))  # e.g. "15 kW", "220V/3-phase"
    power_requirements = Column(String(200))  # Power requirements description
    operating_temperature_range = Column(String(100))  # e.g. "0-40°C"
    weight = Column(Float)  # Weight in kg
    dimensions = Column(String(200))  # e.g. "2000x1500x1800 mm"
    notes = Column(Text)  # Additional notes/comments
    version = Column(Integer, default=1)  # Version number for tracking changes
    
    # Asset Lifecycle Management fields - commented out, not in DB
    # depreciation_method = Column(String(50))  # "linear", "declining", "sum_of_years"
    # depreciation_rate = Column(Float)  # Annual depreciation rate (e.g., 0.20 for 20%)
    # depreciation_period_years = Column(Integer)  # Useful life in years
    # current_value = Column(Float)  # Current book value (calculated)
    # salvage_value = Column(Float, default=0.0)  # Residual value at end of life
    # scrapping_date = Column(DateTime)  # Date when machine was scrapped
    # scrapping_reason = Column(Text)  # Reason for scrapping
    # scrapping_cost = Column(Float)  # Cost associated with scrapping
    # performance_metrics = Column(JSON, default={})  # MTBF, MTTR, Availability, etc.
    
    # Audit fields
    created_by_user_id = Column(Integer, ForeignKey("users.id"))
    updated_by_user_id = Column(Integer, ForeignKey("users.id"))
    
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    
    # Relationships
    production_line = relationship("ProductionLine", back_populates="machines")
    modules = relationship("Module", back_populates="machine", cascade="all, delete-orphan")
    worksheets = relationship("Worksheet", back_populates="machine", cascade="all, delete-orphan")
    pm_tasks = relationship("PMTask", back_populates="machine", cascade="all, delete-orphan")
    asset_history = relationship("AssetHistory", back_populates="machine", cascade="all, delete-orphan")
    machine_versions = relationship("MachineVersion", back_populates="machine", cascade="all, delete-orphan")
    service_records = relationship("ServiceRecord", foreign_keys="ServiceRecord.machine_id", cascade="all, delete-orphan", overlaps="machine")
    id_compatible_parts = relationship("Part", secondary=machine_parts, back_populates="compatible_machines")
    created_by_user = relationship("User", foreign_keys=[created_by_user_id])
    updated_by_user = relationship("User", foreign_keys=[updated_by_user_id])
    
    __table_args__ = (
        Index('idx_production_line_id', 'production_line_id'),
        Index('idx_serial_number', 'serial_number'),
        Index('idx_asset_tag', 'asset_tag'),
    )
    
    def __repr__(self):
        return f"<Machine {self.name} ({self.serial_number})>"


class Module(Base):
    """Sub-components of machines"""
    __tablename__ = "modules"
    
    id = Column(Integer, primary_key=True)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    specifications = Column(JSON, default={})
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    
    # Relationships
    machine = relationship("Machine", back_populates="modules")
    
    __table_args__ = (
        Index('idx_modules_machine_id', 'machine_id'),
    )
    
    def __repr__(self):
        return f"<Module {self.name}>"


class MachineVersion(Base):
    """Version history for machines - tracks all changes"""
    __tablename__ = "machine_versions"
    
    id = Column(Integer, primary_key=True)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False)
    version = Column(Integer, nullable=False)  # Version number
    changed_fields = Column(JSON)  # Dictionary of changed fields: {"field_name": {"old": value, "new": value}}
    changed_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    change_description = Column(Text)  # User-provided description of the change
    timestamp = Column(DateTime, default=utcnow, index=True)
    
    # Relationships
    machine = relationship("Machine", back_populates="machine_versions")
    changed_by_user = relationship("User", foreign_keys=[changed_by_user_id])
    
    __table_args__ = (
        Index('idx_machine_versions_machine_id', 'machine_id'),
        Index('idx_machine_versions_timestamp', 'timestamp'),
        Index('idx_machine_versions_version', 'version'),
    )
    
    def __repr__(self):
        return f"<MachineVersion machine_id={self.machine_id} version={self.version}>"


class AssetHistory(Base):
    """History of changes to assets - simplified log"""
    __tablename__ = "asset_history"
    
    id = Column(Integer, primary_key=True)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=True)
    action_type = Column(String(50), nullable=False)  # created, modified, manual_updated, deleted
    description = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"))
    timestamp = Column(DateTime, default=utcnow, index=True)
    
    # Relationships
    machine = relationship("Machine", back_populates="asset_history")
    user = relationship("User")
    
    __table_args__ = (
        Index('idx_asset_history_machine_id', 'machine_id'),
        Index('idx_asset_history_timestamp', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<AssetHistory {self.action_type}>"


# ============================================================================
# INVENTORY & WAREHOUSE MODELS
# ============================================================================

class Supplier(Base):
    """Parts suppliers"""
    __tablename__ = "suppliers"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False, unique=True)
    contact_person = Column(String(100))
    email = Column(String(120))
    phone = Column(String(20))
    address = Column(String(200))
    city = Column(String(100))
    postal_code = Column(String(20))
    country = Column(String(100))
    created_at = Column(DateTime, default=utcnow)
    
    # Relationships
    parts = relationship("Part", back_populates="supplier")
    
    def __repr__(self):
        return f"<Supplier {self.name}>"


class Part(Base):
    """Inventory parts/items"""
    __tablename__ = "parts"
    
    id = Column(Integer, primary_key=True)
    sku = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(150), nullable=False)
    description = Column(Text)
    category = Column(String(100))
    unit = Column(String(20), default="db")  # db, m, l, kg, etc.
    buy_price = Column(Float, default=0.0)
    sell_price = Column(Float, default=0.0)
    safety_stock = Column(Integer, default=0)
    reorder_quantity = Column(Integer, default=0)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    last_count_date = Column(DateTime)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    
    # Relationships
    supplier = relationship("Supplier", back_populates="parts")
    inventory_level = relationship("InventoryLevel", back_populates="part", uselist=False, cascade="all, delete-orphan")
    worksheet_parts = relationship("WorksheetPart", back_populates="part")
    stock_transactions = relationship("StockTransaction", back_populates="part", cascade="all, delete-orphan")
    stock_batches = relationship("StockBatch", back_populates="part", cascade="all, delete-orphan")
    qr_codes = relationship("QRCodeData", back_populates="part", cascade="all, delete-orphan")
    compatible_machines = relationship("Machine", secondary="machine_parts", back_populates="id_compatible_parts")
    part_locations = relationship("PartLocation", back_populates="part", cascade="all, delete-orphan")
    reservations = relationship("StockReservation", back_populates="part")
    
    __table_args__ = (
        Index('idx_sku', 'sku'),
    )
    
    def __repr__(self):
        return f"<Part {self.sku} - {self.name}>"


class InventoryLevel(Base):
    """Current stock levels for parts"""
    __tablename__ = "inventory_levels"
    
    id = Column(Integer, primary_key=True)
    part_id = Column(Integer, ForeignKey("parts.id"), unique=True, nullable=False)
    quantity_on_hand = Column(Integer, default=0)
    quantity_reserved = Column(Integer, default=0)
    bin_location = Column(String(100))
    last_updated = Column(DateTime, default=utcnow, onupdate=utcnow)
    
    # Relationships
    part = relationship("Part", back_populates="inventory_level")
    
    @property
    def quantity_available(self) -> int:
        """Available quantity = on_hand - reserved"""
        return max(0, self.quantity_on_hand - self.quantity_reserved)
    
    @property
    def is_low_stock(self) -> bool:
        """Check if stock is below safety level"""
        return self.quantity_on_hand <= self.part.safety_stock
    
    __table_args__ = (
        CheckConstraint('quantity_on_hand >= 0', name='chk_inv_qty_on_hand'),
        CheckConstraint('quantity_reserved >= 0', name='chk_inv_qty_reserved'),
    )
    
    def __repr__(self):
        return f"<InventoryLevel part_id={self.part_id} qty={self.quantity_on_hand}>"


class StockTransaction(Base):
    """Record of all stock movements"""
    __tablename__ = "stock_transactions"
    
    id = Column(Integer, primary_key=True)
    part_id = Column(Integer, ForeignKey("parts.id"), nullable=False)
    transaction_type = Column(String(50), nullable=False)  # received, issued, adjustment
    quantity = Column(Integer, nullable=False)
    reference_id = Column(Integer)  # worksheet_id, purchase_order_id, etc.
    reference_type = Column(String(50))  # worksheet, purchase_order, etc.
    user_id = Column(Integer, ForeignKey("users.id"))
    notes = Column(Text)
    timestamp = Column(DateTime, default=utcnow, index=True)
    
    # Relationships
    part = relationship("Part", back_populates="stock_transactions")
    user = relationship("User", back_populates="stock_transactions")
    
    __table_args__ = (
        Index('idx_stock_transactions_part_id', 'part_id'),
        Index('idx_stock_transactions_timestamp', 'timestamp'),
        Index('idx_stock_transactions_reference', 'reference_id', 'reference_type'),
        CheckConstraint('quantity != 0', name='chk_stock_quantity'),
    )
    
    def __repr__(self):
        return f"<StockTransaction {self.transaction_type} qty={self.quantity}>"


class StockBatch(Base):
    """Stock batches for FIFO inventory tracking"""
    __tablename__ = "stock_batches"
    
    id = Column(Integer, primary_key=True)
    part_id = Column(Integer, ForeignKey("parts.id"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)  # Original quantity received
    quantity_remaining = Column(Integer, nullable=False)  # Remaining quantity after FIFO issues
    unit_price = Column(Float, nullable=False, default=0.0)
    received_date = Column(DateTime, default=utcnow, nullable=False, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)
    invoice_number = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    stock_transaction_id = Column(Integer, ForeignKey("stock_transactions.id"), nullable=False)
    storage_location_id = Column(Integer, ForeignKey("storage_locations.id"), nullable=True, index=True)  # Storage location where batch is stored
    
    # Relationships
    part = relationship("Part", back_populates="stock_batches")
    supplier = relationship("Supplier")
    stock_transaction = relationship("StockTransaction")
    storage_location = relationship("StorageLocation", back_populates="stock_batches")
    
    __table_args__ = (
        Index('idx_stock_batches_part_id', 'part_id'),
        Index('idx_stock_batches_received_date', 'received_date'),
        Index('idx_stock_batches_quantity_remaining', 'quantity_remaining'),
    )
    
    def __repr__(self):
        return f"<StockBatch part_id={self.part_id} qty={self.quantity_remaining}/{self.quantity}>"


class StorageLocation(Base):
    """Hierarchical storage locations (warehouse, cabinet, shelf, bin, etc.)"""
    __tablename__ = "storage_locations"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    code = Column(String(50), nullable=True)  # Optional unique code/identifier
    parent_id = Column(Integer, ForeignKey("storage_locations.id"), nullable=True)  # Self-referential for hierarchy
    location_type = Column(String(50), nullable=True)  # warehouse, cabinet, shelf, bin, etc.
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    parent = relationship("StorageLocation", remote_side=[id], back_populates="children")
    children = relationship("StorageLocation", back_populates="parent", cascade="all, delete-orphan")
    part_locations = relationship("PartLocation", back_populates="storage_location", cascade="all, delete-orphan")
    stock_batches = relationship("StockBatch", back_populates="storage_location")
    created_by_user = relationship("User")
    
    __table_args__ = (
        Index('idx_storage_locations_parent_id', 'parent_id'),
        Index('idx_storage_locations_code', 'code'),
        Index('idx_storage_locations_is_active', 'is_active'),
    )
    
    def __repr__(self):
        return f"<StorageLocation {self.name} (id={self.id})>"


class PartLocation(Base):
    """Association table linking parts to storage locations with quantity"""
    __tablename__ = "part_locations"
    
    id = Column(Integer, primary_key=True)
    part_id = Column(Integer, ForeignKey("parts.id"), nullable=False, index=True)
    storage_location_id = Column(Integer, ForeignKey("storage_locations.id"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False, default=0)
    assigned_date = Column(DateTime, default=utcnow, nullable=False)  # When part was assigned to this location
    assigned_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Who assigned the part to this location
    last_movement_date = Column(DateTime, default=utcnow, nullable=False, onupdate=utcnow)  # Last movement date
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)
    
    # Relationships
    part = relationship("Part", back_populates="part_locations")
    storage_location = relationship("StorageLocation", back_populates="part_locations")
    assigned_by_user = relationship("User", foreign_keys=[assigned_by_user_id])
    
    __table_args__ = (
        UniqueConstraint('part_id', 'storage_location_id', name='uq_part_location'),
        Index('idx_part_locations_part_id', 'part_id'),
        Index('idx_part_locations_storage_location_id', 'storage_location_id'),
        Index('idx_part_locations_assigned_date', 'assigned_date'),
    )
    
    def __repr__(self):
        return f"<PartLocation part_id={self.part_id} location_id={self.storage_location_id} qty={self.quantity}>"


class InventoryThreshold(Base):
    """Inventory threshold settings for notifications and interventions"""
    __tablename__ = "inventory_thresholds"
    
    id = Column(Integer, primary_key=True)
    part_id = Column(Integer, ForeignKey("parts.id"), nullable=False, index=True)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=True, index=True)
    notification_threshold = Column(Float, nullable=False)  # Threshold value for notifications
    intervention_threshold = Column(Float, nullable=True)  # Threshold value for interventions
    threshold_type = Column(String(50), nullable=False)  # e.g., "quantity", "usage_rate", "cost"
    period = Column(String(50), nullable=False)  # e.g., "daily", "weekly", "monthly"
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)
    
    # Relationships
    part = relationship("Part")
    machine = relationship("Machine")
    
    __table_args__ = (
        Index('idx_inventory_thresholds_part_id', 'part_id'),
        Index('idx_inventory_thresholds_machine_id', 'machine_id'),
        Index('idx_inventory_thresholds_active', 'is_active'),
    )
    
    def __repr__(self):
        return f"<InventoryThreshold part_id={self.part_id} type={self.threshold_type} threshold={self.notification_threshold}>"


class QRCodeData(Base):
    """QR code metadata for parts"""
    __tablename__ = "qr_codes"
    
    id = Column(Integer, primary_key=True)
    part_id = Column(Integer, ForeignKey("parts.id"), nullable=False)
    qr_data = Column(String(500), nullable=False)  # QR data content
    generated_at = Column(DateTime, default=utcnow)
    is_printed = Column(Boolean, default=False)
    
    # Relationships
    part = relationship("Part", back_populates="qr_codes")
    
    def __repr__(self):
        return f"<QRCodeData part_id={self.part_id}>"


# ============================================================================
# WORKSHEET MODELS (CORE)
# ============================================================================

class Worksheet(Base):
    """Maintenance worksheets/work orders"""
    __tablename__ = "worksheets"
    
    id = Column(Integer, primary_key=True)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False)
    assigned_to_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(String(50), default="Open", nullable=False)  # Open, Waiting for Parts, Closed
    breakdown_time = Column(DateTime)
    repair_finished_time = Column(DateTime)
    total_downtime_hours = Column(Float, default=0.0)
    fault_cause = Column(Text, nullable=True)  # MSZ EN 13460 kötelező mező
    version = Column(Integer, default=1, nullable=False)  # Optimistic locking
    created_at = Column(DateTime, default=utcnow, index=True)
    closed_at = Column(DateTime)
    notes = Column(Text)
    
    # Relationships
    machine = relationship("Machine", back_populates="worksheets")
    assigned_user = relationship("User", back_populates="worksheets", foreign_keys=[assigned_to_user_id])
    parts = relationship("WorksheetPart", back_populates="worksheet", cascade="all, delete-orphan")
    photos = relationship("WorksheetPhoto", back_populates="worksheet", cascade="all, delete-orphan")
    pdf = relationship("WorksheetPDF", back_populates="worksheet", uselist=False, cascade="all, delete-orphan")
    reservations = relationship("StockReservation", back_populates="worksheet")
    
    def increment_version(self):
        """Increment version for optimistic locking"""
        self.version = (self.version or 1) + 1
    
    __table_args__ = (
        Index('idx_machine_id', 'machine_id'),
        Index('idx_status', 'status'),
        Index('idx_created_at', 'created_at'),
        CheckConstraint(
            'repair_finished_time IS NULL OR breakdown_time IS NULL OR '
            'repair_finished_time >= breakdown_time',
            name='chk_worksheet_dates'
        ),
        CheckConstraint(
            "status != 'Closed' OR (fault_cause IS NOT NULL AND fault_cause != '')",
            name='chk_worksheet_status_closed'
        ),
    )
    
    def calculate_downtime(self):
        """Calculate total downtime in hours"""
        if self.breakdown_time and self.repair_finished_time:
            delta = self.repair_finished_time - self.breakdown_time
            return delta.total_seconds() / 3600  # Convert to hours
        return 0.0
    
    def __repr__(self):
        return f"<Worksheet {self.id} - {self.title}>"


class WorksheetPart(Base):
    """Parts used in a worksheet"""
    __tablename__ = "worksheet_parts"
    
    id = Column(Integer, primary_key=True)
    worksheet_id = Column(Integer, ForeignKey("worksheets.id"), nullable=False)
    part_id = Column(Integer, ForeignKey("parts.id"), nullable=False)
    quantity_used = Column(Integer, nullable=False)
    unit_cost_at_time = Column(Float, default=0.0)
    notes = Column(Text)
    added_at = Column(DateTime, default=utcnow)
    
    # Relationships
    worksheet = relationship("Worksheet", back_populates="parts")
    part = relationship("Part", back_populates="worksheet_parts")
    
    @property
    def total_cost(self) -> float:
        """Total cost = quantity × unit cost"""
        return self.quantity_used * self.unit_cost_at_time
    
    __table_args__ = (
        Index('idx_worksheet_id', 'worksheet_id'),
        Index('idx_part_id', 'part_id'),
    )
    
    def __repr__(self):
        return f"<WorksheetPart ws={self.worksheet_id} part={self.part_id}>"


class WorksheetPhoto(Base):
    """Photos attached to worksheets"""
    __tablename__ = "worksheet_photos"
    
    id = Column(Integer, primary_key=True)
    worksheet_id = Column(Integer, ForeignKey("worksheets.id"), nullable=False)
    photo_path = Column(String(500), nullable=False)  # UUID filename
    original_filename = Column(String(255))
    description = Column(Text)
    uploaded_at = Column(DateTime, default=utcnow)
    
    # Relationships
    worksheet = relationship("Worksheet", back_populates="photos")
    
    def __repr__(self):
        return f"<WorksheetPhoto ws={self.worksheet_id}>"


class WorksheetPDF(Base):
    """Generated PDF for worksheets"""
    __tablename__ = "worksheet_pdfs"
    
    id = Column(Integer, primary_key=True)
    worksheet_id = Column(Integer, ForeignKey("worksheets.id"), unique=True, nullable=False)
    pdf_path = Column(String(500), nullable=False)
    generated_at = Column(DateTime, default=utcnow)
    page_count = Column(Integer, default=1)
    
    # Relationships
    worksheet = relationship("Worksheet", back_populates="pdf")
    
    def __repr__(self):
        return f"<WorksheetPDF ws={self.worksheet_id}>"


# ============================================================================
# STOCK RESERVATION MODELS
# ============================================================================

class StockReservation(Base):
    """Stock reservation for worksheets"""
    __tablename__ = "stock_reservations"
    
    id = Column(Integer, primary_key=True)
    part_id = Column(Integer, ForeignKey("parts.id"), nullable=False)
    worksheet_id = Column(Integer, ForeignKey("worksheets.id"), nullable=True)
    quantity_reserved = Column(Integer, nullable=False)
    reserved_at = Column(DateTime, default=utcnow)
    expires_at = Column(DateTime)  # Reservation expiry
    user_id = Column(Integer, ForeignKey("users.id"))
    notes = Column(Text)
    
    # Relationships
    part = relationship("Part", back_populates="reservations")
    worksheet = relationship("Worksheet", back_populates="reservations")
    user = relationship("User")
    
    __table_args__ = (
        Index('idx_reservation_part', 'part_id'),
        Index('idx_reservation_worksheet', 'worksheet_id'),
        Index('idx_reservation_expires', 'expires_at'),
    )
    
    def is_expired(self) -> bool:
        """Check if reservation is expired"""
        if not self.expires_at:
            return False
        return utcnow() > self.expires_at
    
    def __repr__(self):
        return f"<StockReservation part={self.part_id} qty={self.quantity_reserved}>"


# ============================================================================
# PREVENTIVE MAINTENANCE MODELS
# ============================================================================

class PMTask(Base):
    """Preventive maintenance tasks"""
    __tablename__ = "pm_tasks"
    
    id = Column(Integer, primary_key=True)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=True)  # None if "other" location is used
    task_name = Column(String(150), nullable=False)
    task_description = Column(Text)
    task_type = Column(String(20), default="recurring")  # recurring, one_time
    frequency_days = Column(Integer, nullable=True)  # Recurrence interval (NULL for one-time tasks)
    last_executed_date = Column(DateTime)
    next_due_date = Column(DateTime, index=True)
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1, nullable=False)  # Optimistic locking
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    
    # Assignment and priority fields
    assigned_to_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # None = global, assigned = user-specific
    priority = Column(String(20), default="normal")  # low, normal, high, urgent
    status = Column(String(50), default="pending")  # pending, in_progress, completed, cancelled
    due_date = Column(DateTime, nullable=True)  # Specific due date (overrides next_due_date for one-time tasks)
    estimated_duration_minutes = Column(Integer, nullable=True)  # Estimated time to complete
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Who created the task
    location = Column(String(200), nullable=True)  # Location when machine_id is None (for "other" option)
    
    # Relationships
    machine = relationship("Machine", back_populates="pm_tasks")
    histories = relationship("PMHistory", back_populates="pm_task", cascade="all, delete-orphan")
    assigned_user = relationship("User", foreign_keys=[assigned_to_user_id])
    created_by_user = relationship("User", foreign_keys=[created_by_user_id])
    work_request_pdf = relationship("WorkRequestPDF", back_populates="pm_task", uselist=False, cascade="all, delete-orphan")
    
    def increment_version(self):
        """Increment version for optimistic locking"""
        self.version = (self.version or 1) + 1
    
    __table_args__ = (
        Index('idx_pm_tasks_machine_id', 'machine_id'),
        Index('idx_pm_tasks_next_due_date', 'next_due_date'),
        Index('idx_pm_tasks_assigned_to_user_id', 'assigned_to_user_id'),
        Index('idx_pm_tasks_status', 'status'),
        CheckConstraint(
            'last_executed_date IS NULL OR next_due_date IS NULL OR '
            'next_due_date >= last_executed_date',
            name='chk_pm_task_dates'
        ),
    )
    
    def __repr__(self):
        return f"<PMTask {self.task_name}>"


class PMHistory(Base):
    """Execution history of PM tasks"""
    __tablename__ = "pm_histories"
    
    id = Column(Integer, primary_key=True)
    pm_task_id = Column(Integer, ForeignKey("pm_tasks.id"), nullable=False)
    executed_date = Column(DateTime, default=utcnow)
    assigned_to_user_id = Column(Integer, ForeignKey("users.id"))
    completed_by_user_id = Column(Integer, ForeignKey("users.id"))
    completion_status = Column(String(50), default="pending")  # completed, skipped
    notes = Column(Text)
    duration_minutes = Column(Integer, default=0)
    worksheet_id = Column(Integer, ForeignKey("worksheets.id"), nullable=True)  # Link to worksheet if created
    
    # Relationships
    pm_task = relationship("PMTask", back_populates="histories")
    assigned_user = relationship("User", back_populates="pm_histories_assigned", foreign_keys=[assigned_to_user_id])
    completed_user = relationship("User", back_populates="pm_histories_completed", foreign_keys=[completed_by_user_id])
    worksheet = relationship("Worksheet", foreign_keys=[worksheet_id])
    worksheet_pdf = relationship("PMWorksheetPDF", back_populates="pm_history", uselist=False, cascade="all, delete-orphan")
    attachments = relationship("PMTaskAttachment", back_populates="pm_history", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_pm_histories_pm_task_id', 'pm_task_id'),
        Index('idx_pm_histories_executed_date', 'executed_date'),
    )
    
    def __repr__(self):
        return f"<PMHistory pm_task={self.pm_task_id}>"


class PMTaskAttachment(Base):
    """Photos and documents attached to PM task completions"""
    __tablename__ = "pm_task_attachments"
    
    id = Column(Integer, primary_key=True)
    pm_history_id = Column(Integer, ForeignKey("pm_histories.id"), nullable=False)
    file_path = Column(String(500), nullable=False)  # Full path to the file
    original_filename = Column(String(255), nullable=False)  # Original filename
    file_type = Column(String(50), nullable=False)  # "image", "document", "other"
    file_size = Column(Integer, nullable=True)  # File size in bytes
    description = Column(Text, nullable=True)  # Optional description
    uploaded_at = Column(DateTime, default=utcnow)
    uploaded_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    pm_history = relationship("PMHistory", back_populates="attachments")
    uploaded_by_user = relationship("User", foreign_keys=[uploaded_by_user_id])
    
    __table_args__ = (
        Index('idx_pm_attachment_history', 'pm_history_id'),
        Index('idx_pm_attachment_uploaded_at', 'uploaded_at'),
    )
    
    def __repr__(self):
        return f"<PMTaskAttachment pm_history={self.pm_history_id} file={self.original_filename}>"


class WorkRequestPDF(Base):
    """Generated work request PDF for PM tasks (ISO 9001)"""
    __tablename__ = "work_request_pdfs"
    
    id = Column(Integer, primary_key=True)
    pm_task_id = Column(Integer, ForeignKey("pm_tasks.id"), unique=True, nullable=False)
    pdf_path = Column(String(500), nullable=False)
    generated_at = Column(DateTime, default=utcnow)
    generated_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    page_count = Column(Integer, default=1)
    
    # Relationships
    pm_task = relationship("PMTask", back_populates="work_request_pdf")
    generated_by_user = relationship("User", foreign_keys=[generated_by_user_id])
    
    def __repr__(self):
        return f"<WorkRequestPDF pm_task={self.pm_task_id}>"


class PMWorksheetPDF(Base):
    """Generated worksheet PDF for completed PM tasks (ISO 9001)"""
    __tablename__ = "pm_worksheet_pdfs"
    
    id = Column(Integer, primary_key=True)
    pm_history_id = Column(Integer, ForeignKey("pm_histories.id"), unique=True, nullable=False)
    pdf_path = Column(String(500), nullable=False)
    generated_at = Column(DateTime, default=utcnow)
    generated_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    page_count = Column(Integer, default=1)
    
    # Relationships
    pm_history = relationship("PMHistory", back_populates="worksheet_pdf")
    generated_by_user = relationship("User", foreign_keys=[generated_by_user_id])
    
    def __repr__(self):
        return f"<PMWorksheetPDF pm_history={self.pm_history_id}>"


# ============================================================================
# SCRAPPING DOCUMENT MODELS
# ============================================================================

class ScrappingDocument(Base):
    """Generated scrapping documents for parts and machines"""
    __tablename__ = "scrapping_documents"
    
    id = Column(Integer, primary_key=True)
    entity_type = Column(String(50), nullable=False)  # "Part" or "Machine"
    entity_id = Column(Integer, nullable=False)
    docx_path = Column(String(500), nullable=False)
    generated_at = Column(DateTime, default=utcnow)
    generated_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    reason = Column(Text, nullable=True)  # Scrapping reason
    worksheet_id = Column(Integer, ForeignKey("worksheets.id"), nullable=True)  # If from worksheet
    pm_history_id = Column(Integer, ForeignKey("pm_histories.id"), nullable=True)  # If from PM task
    
    # Relationships
    generated_by_user = relationship("User", foreign_keys=[generated_by_user_id])
    worksheet = relationship("Worksheet", foreign_keys=[worksheet_id])
    pm_history = relationship("PMHistory", foreign_keys=[pm_history_id])
    
    __table_args__ = (
        Index('idx_scrapping_entity', 'entity_type', 'entity_id'),
        Index('idx_scrapping_timestamp', 'generated_at'),
    )
    
    def __repr__(self):
        return f"<ScrappingDocument {self.entity_type}:{self.entity_id}>"


# ============================================================================
# SYSTEM LOG MODELS
# ============================================================================

class SystemLog(Base):
    """Detailed system logging for all operations"""
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True)
    log_category = Column(String(50), nullable=False, index=True)  # document, worksheet, work_request, scrapping, task, assignment, inventory, asset, user
    action_type = Column(String(50), nullable=False)  # create, update, delete, generate, assign, complete, scrap
    entity_type = Column(String(50), nullable=False)  # Worksheet, WorkRequest, ScrappingDocument, PMTask, Part, Machine, etc.
    entity_id = Column(Integer, nullable=True)  # Entity ID
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Who performed the action
    description = Column(Text, nullable=True)  # Detailed description
    log_metadata = Column(JSON, default={})  # Additional information (changes, parameters, etc.)
    ip_address = Column(String(45))  # IPv4 or IPv6
    user_agent = Column(String(500))  # Browser/client info
    timestamp = Column(DateTime, default=utcnow, index=True)
    
    # Date categorization for filtering
    year = Column(Integer, index=True)
    month = Column(Integer, index=True)  # 1-12
    week = Column(Integer, index=True)  # ISO week number
    day = Column(Integer, index=True)  # Day of month
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    
    __table_args__ = (
        Index('idx_system_logs_timestamp', 'timestamp'),
        Index('idx_system_logs_category', 'log_category'),
        Index('idx_system_logs_entity', 'entity_type', 'entity_id'),
        Index('idx_system_logs_date', 'year', 'month', 'week', 'day'),
    )
    
    def __repr__(self):
        return f"<SystemLog {self.log_category}:{self.action_type} {self.entity_type}:{self.entity_id}>"


# ============================================================================
# APPLICATION SETTINGS MODEL
# ============================================================================

class AppSetting(Base):
    """Application-level settings and configurations"""
    __tablename__ = "app_settings"
    
    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text, nullable=False)  # JSON-friendly format
    description = Column(String(500))
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    
    def __repr__(self):
        return f"<AppSetting {self.key}>"


# ============================================================================
# VACATION MANAGEMENT MODELS
# ============================================================================

class VacationRequest(Base):
    """Vacation requests from users"""
    __tablename__ = "vacation_requests"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    vacation_type = Column(String(50), default="annual")  # annual, child_care, etc.
    reason = Column(Text, nullable=True)
    status = Column(String(50), default="pending")  # pending, approved, rejected
    requested_at = Column(DateTime, default=utcnow)
    approved_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    days_count = Column(Integer)  # Számított munkanapok száma
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="vacation_requests")
    approved_by = relationship("User", foreign_keys=[approved_by_user_id], back_populates="vacation_requests_approved")
    documents = relationship("VacationDocument", back_populates="vacation_request", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_vacation_requests_user_id', 'user_id'),
        Index('idx_vacation_requests_status', 'status'),
        Index('idx_vacation_requests_dates', 'start_date', 'end_date'),
        Index('idx_vacation_requests_requested_at', 'requested_at'),
    )
    
    def __repr__(self):
        return f"<VacationRequest {self.id} user={self.user_id} status={self.status}>"


class ShiftSchedule(Base):
    """User shift schedules"""
    __tablename__ = "shift_schedules"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    shift_type = Column(String(50), nullable=False)  # single, 3_shift, 4_shift
    start_time = Column(String(10), nullable=True)  # HH:MM format
    end_time = Column(String(10), nullable=True)  # HH:MM format
    effective_from = Column(DateTime, nullable=False)
    effective_to = Column(DateTime, nullable=True)  # NULL = aktív
    # Rotation fields for 3_shift system
    rotation_start_date = Column(Date, nullable=True)  # When rotation starts (e.g., Jan 1)
    initial_shift = Column(String(10), nullable=True)  # DE, ÉJ, DU - shift on rotation_start_date
    rotation_pattern = Column(String(20), nullable=True, default="weekly")  # weekly, daily, etc.
    created_at = Column(DateTime, default=utcnow)
    
    # Relationships
    user = relationship("User", back_populates="shift_schedules")
    
    __table_args__ = (
        Index('idx_shift_schedules_user_id', 'user_id'),
        Index('idx_shift_schedules_effective', 'effective_from', 'effective_to'),
    )
    
    def __repr__(self):
        return f"<ShiftSchedule {self.id} user={self.user_id} type={self.shift_type}>"


class ShiftOverride(Base):
    """Shift overrides for specific dates (one-time shift changes)"""
    __tablename__ = "shift_overrides"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    override_date = Column(Date, nullable=False)  # Which date this override applies to
    shift_type = Column(String(10), nullable=False)  # DE, ÉJ, DU (only for 3_shift system)
    start_time = Column(String(10), nullable=True)  # HH:MM format (optional)
    end_time = Column(String(10), nullable=True)  # HH:MM format (optional)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=utcnow)
    notes = Column(Text, nullable=True)  # Optional notes
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="shift_overrides")
    created_by = relationship("User", foreign_keys=[created_by_user_id])
    
    __table_args__ = (
        Index('idx_shift_overrides_user_date', 'user_id', 'override_date'),
        UniqueConstraint('user_id', 'override_date', name='uq_user_date_override'),
    )
    
    def __repr__(self):
        return f"<ShiftOverride {self.id} user={self.user_id} date={self.override_date} shift={self.shift_type}>"


class VacationDocument(Base):
    """Generated vacation request documents"""
    __tablename__ = "vacation_documents"
    
    id = Column(Integer, primary_key=True)
    vacation_request_id = Column(Integer, ForeignKey("vacation_requests.id"), nullable=False)
    docx_path = Column(String(500), nullable=False)
    generated_at = Column(DateTime, default=utcnow)
    generated_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    vacation_request = relationship("VacationRequest", back_populates="documents")
    generated_by = relationship("User", foreign_keys=[generated_by_user_id])
    
    __table_args__ = (
        Index('idx_vacation_documents_request_id', 'vacation_request_id'),
        Index('idx_vacation_documents_generated_at', 'generated_at'),
    )
    
    def __repr__(self):
        return f"<VacationDocument {self.id} request={self.vacation_request_id}>"


# ============================================================================
# NOTIFICATION MODELS
# ============================================================================

class Notification(Base):
    """Internal notifications for users"""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), default="info")  # info, warning, error, success
    is_read = Column(Boolean, default=False)
    related_entity_type = Column(String(50))  # machine, pm_task, worksheet, etc.
    related_entity_id = Column(Integer)
    created_at = Column(DateTime, default=utcnow, index=True)
    read_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], overlaps="notifications")
    
    __table_args__ = (
        Index('idx_notifications_user_id', 'user_id'),
        Index('idx_notifications_created_at', 'created_at'),
        Index('idx_notifications_is_read', 'is_read'),
    )
    
    def __repr__(self):
        return f"<Notification {self.title} for user {self.user_id}>"


# ============================================================================
# SERVICE RECORD MODELS
# ============================================================================

class ServiceRecord(Base):
    """Service/maintenance records for machines"""
    __tablename__ = "service_records"
    
    id = Column(Integer, primary_key=True)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False)
    service_date = Column(DateTime, nullable=False)
    service_type = Column(String(100))  # Preventive, Corrective, Emergency, etc.
    performed_by = Column(String(200))  # Service provider name
    technician_name = Column(String(200))  # Technician who performed the service
    service_cost = Column(Float)  # Cost of service
    service_duration_hours = Column(Float)  # Duration in hours
    description = Column(Text)  # What was done
    notes = Column(Text)  # Additional notes
    next_service_date = Column(DateTime)  # When next service is due
    parts_replaced = Column(Text)  # List of parts replaced
    created_by_user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    
    # Relationships
    machine = relationship("Machine", foreign_keys=[machine_id], overlaps="service_records")
    created_by_user = relationship("User", foreign_keys=[created_by_user_id], overlaps="service_records_created")
    
    __table_args__ = (
        Index('idx_service_records_machine_id', 'machine_id'),
        Index('idx_service_records_service_date', 'service_date'),
        Index('idx_service_records_next_service_date', 'next_service_date'),
    )
    
    def __repr__(self):
        return f"<ServiceRecord machine_id={self.machine_id} date={self.service_date}>"


class ScheduledReport(Base):
    """Scheduled reports for automatic generation and email delivery"""
    __tablename__ = "scheduled_reports"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    report_type = Column(String(50), nullable=False)  # "maintenance", "cost", "performance", "custom"
    schedule_type = Column(String(20), nullable=False)  # "daily", "weekly", "monthly", "yearly"
    schedule_day = Column(Integer)  # Day of week (0-6) or day of month (1-31)
    schedule_time = Column(String(10))  # Time in HH:MM format
    recipients = Column(JSON, default=[])  # List of email addresses
    filters = Column(JSON, default={})  # Report filters (period, user_id, machine_id, etc.)
    template_id = Column(Integer, ForeignKey("report_templates.id"), nullable=True)
    format = Column(String(20), default="excel")  # "excel", "csv"
    is_active = Column(Boolean, default=True)
    last_run_at = Column(DateTime)
    next_run_at = Column(DateTime)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    
    # Relationships
    template = relationship("ReportTemplate", foreign_keys=[template_id], overlaps="scheduled_reports")
    created_by_user = relationship("User", foreign_keys=[created_by_user_id])
    
    def __repr__(self):
        return f"<ScheduledReport {self.name} ({self.schedule_type})>"


class ReportTemplate(Base):
    """Custom report templates"""
    __tablename__ = "report_templates"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    report_type = Column(String(50), nullable=False)  # "maintenance", "cost", "performance", "custom"
    template_config = Column(JSON, nullable=False)  # Template configuration (columns, charts, filters)
    is_default = Column(Boolean, default=False)
    is_public = Column(Boolean, default=False)  # Can be used by other users
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    
    # Relationships
    created_by_user = relationship("User", foreign_keys=[created_by_user_id])
    scheduled_reports = relationship("ScheduledReport", foreign_keys="ScheduledReport.template_id", overlaps="template")
    
    def __repr__(self):
        return f"<ReportTemplate {self.name}>"


# ============================================================================
# SAFETY & COMPLIANCE MODELS
# ============================================================================

class SafetyIncident(Base):
    """Safety incidents tracking"""
    __tablename__ = "safety_incidents"
    
    id = Column(Integer, primary_key=True)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Person involved
    incident_date = Column(DateTime, nullable=False, default=utcnow)
    incident_type = Column(String(100), nullable=False)  # "injury", "near_miss", "property_damage", "environmental"
    severity = Column(String(50), nullable=False)  # "minor", "moderate", "severe", "critical"
    description = Column(Text, nullable=False)
    location = Column(String(200))
    actions_taken = Column(Text)  # Actions taken to address the incident
    status = Column(String(50), default="open")  # "open", "investigating", "resolved", "closed"
    reported_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    resolved_at = Column(DateTime)
    resolved_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    
    # Relationships
    machine = relationship("Machine", foreign_keys=[machine_id])
    user = relationship("User", foreign_keys=[user_id])
    reported_by_user = relationship("User", foreign_keys=[reported_by_user_id])
    resolved_by_user = relationship("User", foreign_keys=[resolved_by_user_id])
    
    __table_args__ = (
        Index('idx_safety_incidents_date', 'incident_date'),
        Index('idx_safety_incidents_severity', 'severity'),
        Index('idx_safety_incidents_status', 'status'),
    )
    
    def __repr__(self):
        return f"<SafetyIncident {self.incident_type} ({self.severity})>"


class LOTOProcedure(Base):
    """Lockout/Tagout procedures"""
    __tablename__ = "loto_procedures"
    
    id = Column(Integer, primary_key=True)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False)
    worksheet_id = Column(Integer, ForeignKey("worksheets.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Person performing LOTO
    lockout_date = Column(DateTime, nullable=False, default=utcnow)
    tagout_date = Column(DateTime, nullable=True)
    release_date = Column(DateTime, nullable=True)
    status = Column(String(50), default="active")  # "active", "released", "cancelled"
    lock_numbers = Column(JSON, default=[])  # List of lock numbers/tags
    tag_numbers = Column(JSON, default=[])  # List of tag numbers
    notes = Column(Text)
    released_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    
    # Relationships
    machine = relationship("Machine", foreign_keys=[machine_id])
    worksheet = relationship("Worksheet", foreign_keys=[worksheet_id])
    user = relationship("User", foreign_keys=[user_id])
    released_by_user = relationship("User", foreign_keys=[released_by_user_id])
    
    __table_args__ = (
        Index('idx_loto_machine_id', 'machine_id'),
        Index('idx_loto_status', 'status'),
        Index('idx_loto_lockout_date', 'lockout_date'),
    )
    
    def __repr__(self):
        return f"<LOTOProcedure machine_id={self.machine_id} status={self.status}>"


class SafetyCertification(Base):
    """Safety certifications and training records"""
    __tablename__ = "safety_certifications"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    certification_type = Column(String(200), nullable=False)  # "OSHA", "First Aid", "LOTO", etc.
    issued_date = Column(DateTime, nullable=False)
    expiry_date = Column(DateTime, nullable=True)
    issuing_authority = Column(String(200))
    certificate_number = Column(String(100))
    file_path = Column(String(500))  # Path to certificate document
    notes = Column(Text)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    
    __table_args__ = (
        Index('idx_safety_cert_user_id', 'user_id'),
        Index('idx_safety_cert_expiry', 'expiry_date'),
    )
    
    @property
    def is_expired(self) -> bool:
        """Check if certification is expired"""
        if not self.expiry_date:
            return False
        return utcnow() > self.expiry_date
    
    @property
    def is_expiring_soon(self) -> bool:
        """Check if certification expires within 30 days"""
        if not self.expiry_date:
            return False
        from datetime import timedelta
        return utcnow() <= self.expiry_date <= (utcnow() + timedelta(days=30))
    
    def __repr__(self):
        return f"<SafetyCertification {self.certification_type} user_id={self.user_id}>"


class RiskAssessment(Base):
    """Risk assessments for machines"""
    __tablename__ = "risk_assessments"
    
    id = Column(Integer, primary_key=True)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False)
    assessed_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assessment_date = Column(DateTime, nullable=False, default=utcnow)
    risk_level = Column(String(50), nullable=False)  # "low", "medium", "high", "critical"
    hazards = Column(JSON, default=[])  # List of identified hazards
    controls = Column(JSON, default=[])  # List of control measures
    review_date = Column(DateTime, nullable=True)  # Next review date
    status = Column(String(50), default="active")  # "active", "reviewed", "archived"
    notes = Column(Text)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    
    # Relationships
    machine = relationship("Machine", foreign_keys=[machine_id])
    assessed_by_user = relationship("User", foreign_keys=[assessed_by_user_id])
    
    __table_args__ = (
        Index('idx_risk_assessment_machine_id', 'machine_id'),
        Index('idx_risk_assessment_risk_level', 'risk_level'),
        Index('idx_risk_assessment_review_date', 'review_date'),
    )
    
    def __repr__(self):
        return f"<RiskAssessment machine_id={self.machine_id} risk_level={self.risk_level}>"


# ============================================================================
# MULTI-SITE / MULTI-TENANT MODELS
# ============================================================================

class Site(Base):
    """Sites/locations for multi-site support"""
    __tablename__ = "sites"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    code = Column(String(50), unique=True, nullable=False)  # Site code (e.g., "HQ", "PLANT1")
    address = Column(Text)
    timezone = Column(String(50), default="UTC")  # Timezone (e.g., "Europe/Budapest")
    is_active = Column(Boolean, default=True)
    settings = Column(JSON, default={})  # Site-specific settings
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    
    # Relationships
    site_users = relationship("SiteUser", back_populates="site", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('code', name='uq_site_code'),
        Index('idx_site_code', 'code'),
    )
    
    def __repr__(self):
        return f"<Site {self.name} ({self.code})>"


class SiteUser(Base):
    """User-site associations for multi-site support"""
    __tablename__ = "site_users"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=False)
    role_at_site = Column(String(50))  # Role specific to this site (can differ from user's global role)
    is_primary_site = Column(Boolean, default=False)  # User's primary/default site
    assigned_at = Column(DateTime, default=utcnow)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    site = relationship("Site", back_populates="site_users")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'site_id', name='uq_site_user'),
        Index('idx_site_user_user_id', 'user_id'),
        Index('idx_site_user_site_id', 'site_id'),
    )
    
    def __repr__(self):
        return f"<SiteUser user_id={self.user_id} site_id={self.site_id}>"


# ============================================================================
# All models listed for reference
# ============================================================================

__all__ = [
    # Auth
    'Role', 'User', 'UserSession', 'AuditLog',
    # Assets
    'ProductionLine', 'Machine', 'Module', 'AssetHistory',
    # Inventory
    'Supplier', 'Part', 'InventoryLevel', 'StockTransaction', 'StockBatch', 'StorageLocation', 'PartLocation', 'QRCodeData',
    # Worksheets
    'Worksheet', 'WorksheetPart', 'WorksheetPhoto', 'WorksheetPDF',
    # PM
    'PMTask', 'PMHistory', 'PMTaskAttachment', 'WorkRequestPDF', 'PMWorksheetPDF',
    # Scrapping
    'ScrappingDocument',
    # Logging
    'SystemLog',
    # Settings
    'AppSetting',
    # Notifications
    'Notification',
    # Service Records
    'ServiceRecord',
    # Vacation Management
    'VacationRequest',
    'ShiftSchedule',
    'VacationDocument',
    # Advanced Reporting
    'ScheduledReport',
    'ReportTemplate',
    # Safety & Compliance
    'SafetyIncident',
    'LOTOProcedure',
    'SafetyCertification',
    'RiskAssessment',
    # Multi-site
    'Site',
    'SiteUser',
]
