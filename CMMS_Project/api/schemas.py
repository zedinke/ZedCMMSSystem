"""
Pydantic schemas for API request/response validation
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


# ============================================================================
# AUTH SCHEMAS
# ============================================================================

class LoginRequest(BaseModel):
    """User login request"""
    username: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=1)

    class Config:
        json_schema_extra = {
            "example": {
                "username": "admin",
                "password": "password123"
            }
        }


# ============================================================================
# USER SCHEMAS
# ============================================================================

class RoleBase(BaseModel):
    """Role base schema"""
    name: str
    description: Optional[str] = None


class RoleResponse(RoleBase):
    """Role response schema"""
    id: int
    
    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    """Create user request"""
    username: str = Field(..., min_length=1, max_length=255)
    email: str = Field(..., min_length=1, max_length=255)
    full_name: Optional[str] = None
    phone: Optional[str] = None
    role_id: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "jsmith",
                "email": "john.smith@company.com",
                "full_name": "John Smith",
                "phone": "+36301234567",
                "role_id": 2
            }
        }


class UserUpdate(BaseModel):
    """Update user request"""
    username: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    role_id: Optional[int] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "john.smith@newcompany.com",
                "full_name": "John Robert Smith"
            }
        }


class UserResponse(BaseModel):
    """User response schema"""
    id: int
    username: str
    email: str
    full_name: Optional[str]
    phone: Optional[str]
    must_change_password: bool
    created_at: datetime
    updated_at: Optional[datetime]
    role: Optional[RoleResponse]
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """User list response"""
    total: int
    items: List[UserResponse]


# ============================================================================
# MACHINE SCHEMAS
# ============================================================================

class MachineCreate(BaseModel):
    """Create machine request"""
    name: str = Field(..., min_length=1, max_length=255)
    model: Optional[str] = None
    serial_number: Optional[str] = None
    production_line_id: Optional[int] = None
    status: Optional[str] = "operational"
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "CNC Machine A1",
                "model": "HAAS VF-4",
                "serial_number": "ABC123456",
                "production_line_id": 1,
                "status": "operational"
            }
        }


class MachineUpdate(BaseModel):
    """Update machine request"""
    name: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    production_line_id: Optional[int] = None
    status: Optional[str] = None


class MachineResponse(BaseModel):
    """Machine response schema"""
    id: int
    name: str
    model: Optional[str]
    serial_number: Optional[str]
    production_line_id: Optional[int]
    status: str
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class MachineListResponse(BaseModel):
    """Machine list response"""
    total: int
    items: List[MachineResponse]


# ============================================================================
# WORKSHEET SCHEMAS
# ============================================================================

class WorksheetCreate(BaseModel):
    """Create worksheet request"""
    machine_id: int
    maintenance_type: str
    description: Optional[str] = None
    assigned_to_user_id: Optional[int] = None
    status: Optional[str] = "pending"
    
    class Config:
        json_schema_extra = {
            "example": {
                "machine_id": 1,
                "maintenance_type": "preventive",
                "description": "Monthly maintenance check",
                "assigned_to_user_id": 2,
                "status": "pending"
            }
        }


class WorksheetUpdate(BaseModel):
    """Update worksheet request"""
    description: Optional[str] = None
    assigned_to_user_id: Optional[int] = None
    status: Optional[str] = None


class WorksheetResponse(BaseModel):
    """Worksheet response schema"""
    id: int
    machine_id: int
    maintenance_type: str
    description: Optional[str]
    assigned_to_user_id: Optional[int]
    status: str
    created_at: datetime
    updated_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class WorksheetListResponse(BaseModel):
    """Worksheet list response"""
    total: int
    items: List[WorksheetResponse]


# ============================================================================
# ASSET SCHEMAS
# ============================================================================

class AssetCreate(BaseModel):
    """Create asset request"""
    name: str = Field(..., min_length=1, max_length=255)
    asset_type: str
    asset_tag: Optional[str] = None
    machine_id: Optional[int] = None
    status: Optional[str] = "active"
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Hydraulic Pump",
                "asset_type": "component",
                "asset_tag": "HYD-001",
                "machine_id": 1,
                "status": "active"
            }
        }


class AssetUpdate(BaseModel):
    """Update asset request"""
    name: Optional[str] = None
    asset_type: Optional[str] = None
    asset_tag: Optional[str] = None
    machine_id: Optional[int] = None
    status: Optional[str] = None


class AssetResponse(BaseModel):
    """Asset response schema"""
    id: int
    name: str
    asset_type: str
    asset_tag: Optional[str]
    machine_id: Optional[int]
    status: str
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class AssetListResponse(BaseModel):
    """Asset list response"""
    total: int
    items: List[AssetResponse]


# ============================================================================
# ERROR SCHEMAS
# ============================================================================

class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str
    message: str
    status_code: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "validation_error",
                "message": "Invalid request parameters",
                "status_code": 422
            }
        }


# ============================================================================
# PERMISSIONS SCHEMAS
# ============================================================================

class RoleHierarchyResponse(BaseModel):
    """Role with hierarchy level"""
    name: str
    level: int
    display_name: str
    
    class Config:
        from_attributes = True


class MenuItemActionResponse(BaseModel):
    """Menu item action response"""
    action: str
    role: Optional[str] = None  # Role name that has access
    
    class Config:
        from_attributes = True


class MenuItemResponse(BaseModel):
    """Menu item response"""
    key: str
    actions: List[str]
    
    class Config:
        from_attributes = True


class PermissionConfigResponse(BaseModel):
    """Permission configuration response"""
    menu_items: Dict[str, Dict[str, Optional[str]]]  # menu_key -> {action -> role_name}
    manage_permission_level: Optional[str] = None  # Role name
    
    class Config:
        from_attributes = True


class PermissionConfigUpdate(BaseModel):
    """Permission configuration update request"""
    menu_items: Dict[str, Dict[str, Optional[str]]] = Field(..., description="Menu items and their action permissions")
    manage_permission_level: Optional[str] = Field(None, description="Role name that can manage permissions")
    
    class Config:
        json_schema_extra = {
            "example": {
                "menu_items": {
                    "inventory": {
                        "view": "Karbantartó",
                        "create": "Manager",
                        "edit": "Manager",
                        "delete": "Manager"
                    }
                },
                "manage_permission_level": "Manager"
            }
        }


# ============================================================================
# INVENTORY SCHEMAS
# ============================================================================

class InventoryDto(BaseModel):
    """Inventory item response schema"""
    id: int
    name: str
    sku: Optional[str] = None
    quantity: Optional[int] = None
    min_stock_level: Optional[int] = None
    location: Optional[str] = None
    unit_price: Optional[float] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CreateInventoryDto(BaseModel):
    """Create inventory item request"""
    name: str = Field(..., min_length=1, max_length=255)
    sku: Optional[str] = None
    quantity: Optional[int] = None
    min_stock_level: Optional[int] = None
    location: Optional[str] = None
    unit_price: Optional[float] = None


class UpdateInventoryDto(BaseModel):
    """Update inventory item request"""
    name: Optional[str] = None
    sku: Optional[str] = None
    quantity: Optional[int] = None
    min_stock_level: Optional[int] = None
    location: Optional[str] = None
    unit_price: Optional[float] = None


class InventoryListResponse(BaseModel):
    """Inventory list response"""
    total: int
    items: List[InventoryDto]


# ============================================================================
# PM TASK SCHEMAS
# ============================================================================

class PMTaskDto(BaseModel):
    """PM Task response schema"""
    id: int
    machine_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    frequency: Optional[str] = None
    next_due_date: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CreatePMTaskDto(BaseModel):
    """Create PM task request"""
    machine_id: Optional[int] = None
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    frequency: Optional[str] = None
    next_due_date: Optional[datetime] = None


class UpdatePMTaskDto(BaseModel):
    """Update PM task request"""
    machine_id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    frequency: Optional[str] = None
    next_due_date: Optional[datetime] = None


class PMTaskListResponse(BaseModel):
    """PM Task list response"""
    total: int
    items: List[PMTaskDto]


# ============================================================================
# REPORTS SCHEMAS
# ============================================================================

class ReportsSummaryDto(BaseModel):
    """Reports summary response"""
    machines_total: int
    worksheets_open: int
    inventory_low_stock: int
    pm_due_this_week: int