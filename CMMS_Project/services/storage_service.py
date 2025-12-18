"""
Storage Service
Hierarchical storage location management with part assignment and FIFO support
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
import sqlalchemy as sa
from sqlalchemy import and_, or_, func
from database.models import StorageLocation, PartLocation, Part, StockBatch, InventoryLevel, User
from database.session_manager import SessionLocal
from services.context_service import get_current_user_id
from services.log_service import log_action
from utils.error_handler import (
    ValidationError,
    NotFoundError,
)
import logging

logger = logging.getLogger(__name__)


def _get_session(session: Optional[Session]) -> Tuple[Session, bool]:
    """Get session or create new one"""
    if session is not None:
        return session, False
    return SessionLocal(), True


# ============================================================================
# HIERARCHICAL STORAGE LOCATION OPERATIONS
# ============================================================================

def create_storage_location(
    name: str,
    parent_id: Optional[int] = None,
    location_type: Optional[str] = None,
    description: Optional[str] = None,
    code: Optional[str] = None,
    session: Session = None
) -> StorageLocation:
    """Create a new storage location"""
    session, should_close = _get_session(session)
    try:
        # Validate parent exists if provided
        if parent_id:
            parent = session.query(StorageLocation).filter_by(id=parent_id).first()
            if not parent:
                raise NotFoundError("StorageLocation", parent_id, user_message=f"Parent location with id {parent_id} not found")
        
        # Check code uniqueness if provided
        if code:
            existing = session.query(StorageLocation).filter_by(code=code).first()
            if existing:
                raise ValidationError(
                    f"Storage location with code '{code}' already exists",
                    field="code",
                    user_message=f"Storage location with code '{code}' already exists"
                )
        
        user_id = get_current_user_id()
        
        location = StorageLocation(
            name=name,
            code=code,
            parent_id=parent_id,
            location_type=location_type,
            description=description,
            is_active=True,
            created_by_user_id=user_id,
        )
        session.add(location)
        session.commit()
        session.refresh(location)
        logger.info(f"Created storage location: {name} (id={location.id})")
        
        # Log action
        try:
            log_action(
                category="storage",
                action_type="create",
                entity_type="StorageLocation",
                entity_id=location.id,
                user_id=user_id,
                description=f"Raktárhely létrehozva: {location.name}",
                metadata={
                    "name": location.name,
                    "code": location.code,
                    "parent_id": location.parent_id,
                    "location_type": location.location_type,
                },
                session=session
            )
        except Exception as e:
            logger.warning(f"Error logging storage location creation: {e}")
        
        return location
    finally:
        if should_close:
            session.close()


def update_storage_location(
    location_id: int,
    name: Optional[str] = None,
    parent_id: Optional[int] = None,
    location_type: Optional[str] = None,
    description: Optional[str] = None,
    code: Optional[str] = None,
    is_active: Optional[bool] = None,
    session: Session = None
) -> StorageLocation:
    """Update a storage location"""
    session, should_close = _get_session(session)
    try:
        location = session.query(StorageLocation).filter_by(id=location_id).first()
        if not location:
            raise NotFoundError("StorageLocation", location_id, user_message=f"Storage location with id {location_id} not found")
        
        # Prevent circular reference (location cannot be its own parent or descendant)
        if parent_id:
            if parent_id == location_id:
                raise ValidationError(
                    "Location cannot be its own parent",
                    field="parent_id",
                    user_message="Location cannot be its own parent"
                )
            # Check if parent_id is a descendant of location_id
            if _is_descendant(session, parent_id, location_id):
                raise ValidationError(
                    "Cannot set parent to a descendant location",
                    field="parent_id",
                    user_message="Cannot set parent to a descendant location"
                )
        
        # Validate parent exists if provided
        if parent_id:
            parent = session.query(StorageLocation).filter_by(id=parent_id).first()
            if not parent:
                raise NotFoundError("StorageLocation", parent_id, user_message=f"Parent location with id {parent_id} not found")
        
        # Check code uniqueness if provided
        if code and code != location.code:
            existing = session.query(StorageLocation).filter_by(code=code).first()
            if existing:
                raise ValidationError(
                    f"Storage location with code '{code}' already exists",
                    field="code",
                    user_message=f"Storage location with code '{code}' already exists"
                )
        
        if name is not None:
            location.name = name
        if code is not None:
            location.code = code
        if parent_id is not None:
            location.parent_id = parent_id
        if location_type is not None:
            location.location_type = location_type
        if description is not None:
            location.description = description
        if is_active is not None:
            location.is_active = is_active
        
        location.updated_at = datetime.now()
        session.commit()
        session.refresh(location)
        logger.info(f"Updated storage location: {location.name} (id={location.id})")
        
        # Log action
        try:
            user_id = get_current_user_id()
            log_action(
                category="storage",
                action_type="update",
                entity_type="StorageLocation",
                entity_id=location.id,
                user_id=user_id,
                description=f"Raktárhely módosítva: {location.name}",
                metadata={
                    "name": location.name,
                    "code": location.code,
                    "parent_id": location.parent_id,
                    "location_type": location.location_type,
                },
                session=session
            )
        except Exception as e:
            logger.warning(f"Error logging storage location update: {e}")
        
        return location
    finally:
        if should_close:
            session.close()


def _is_descendant(session: Session, potential_descendant_id: int, ancestor_id: int) -> bool:
    """Check if potential_descendant_id is a descendant of ancestor_id"""
    current_id = potential_descendant_id
    visited = set()
    
    while current_id:
        if current_id == ancestor_id:
            return True
        if current_id in visited:
            break  # Circular reference detected
        visited.add(current_id)
        
        location = session.query(StorageLocation).filter_by(id=current_id).first()
        if not location or not location.parent_id:
            break
        current_id = location.parent_id
    
    return False


def delete_storage_location(location_id: int, session: Session = None) -> bool:
    """Delete a storage location (only if no parts assigned and no children)"""
    session, should_close = _get_session(session)
    try:
        location = session.query(StorageLocation).filter_by(id=location_id).first()
        if not location:
            raise NotFoundError("StorageLocation", location_id, user_message=f"Storage location with id {location_id} not found")
        
        # Check if has children
        children_count = session.query(StorageLocation).filter_by(parent_id=location_id).count()
        if children_count > 0:
            raise ValidationError(
                f"Cannot delete location '{location.name}': has {children_count} child location(s)",
                field="location_id",
                user_message=f"Cannot delete location '{location.name}': has {children_count} child location(s)"
            )
        
        # Check if has parts assigned
        parts_count = session.query(PartLocation).filter_by(storage_location_id=location_id).count()
        if parts_count > 0:
            raise ValidationError(
                f"Cannot delete location '{location.name}': has {parts_count} part(s) assigned",
                field="location_id",
                user_message=f"Cannot delete location '{location.name}': has {parts_count} part(s) assigned"
            )
        
        # Check if has stock batches
        batches_count = session.query(StockBatch).filter_by(storage_location_id=location_id).count()
        if batches_count > 0:
            raise ValidationError(
                f"Cannot delete location '{location.name}': has {batches_count} stock batch(es)",
                field="location_id",
                user_message=f"Cannot delete location '{location.name}': has {batches_count} stock batch(es)"
            )
        
        location_name = location.name
        location_id_for_log = location_id
        
        session.delete(location)
        session.commit()
        logger.info(f"Deleted storage location: {location_name} (id={location_id_for_log})")
        
        # Log action
        try:
            user_id = get_current_user_id()
            log_action(
                category="storage",
                action_type="delete",
                entity_type="StorageLocation",
                entity_id=location_id_for_log,
                user_id=user_id,
                description=f"Raktárhely törölve: {location_name}",
                metadata={
                    "name": location_name,
                },
                session=session
            )
        except Exception as e:
            logger.warning(f"Error logging storage location deletion: {e}")
        
        return True
    finally:
        if should_close:
            session.close()


def get_storage_location(location_id: int, session: Session = None) -> Optional[StorageLocation]:
    """Get a storage location by ID"""
    session, should_close = _get_session(session)
    try:
        return session.query(StorageLocation).filter_by(id=location_id).first()
    except Exception as e:
        logger.error(f"Unexpected error in storage_service.get_storage_location: {e}", exc_info=True)
        raise
    finally:
        if should_close:
            session.close()


def get_storage_location_tree(root_id: Optional[int] = None, session: Session = None) -> List[Dict]:
    """Get storage location hierarchy as tree structure"""
    session, should_close = _get_session(session)
    try:
        if root_id:
            root = session.query(StorageLocation).filter_by(id=root_id).first()
            if not root:
                return []
            # Get root and all descendants recursively
            descendants = _get_descendants(session, root_id)
            locations = [root] + descendants
        else:
            # Get ALL active locations (not just roots) to build complete tree
            # If no active locations, get all locations (including inactive) for debugging
            locations = session.query(StorageLocation).filter_by(is_active=True).all()
            if not locations:
                # Fallback: get all locations if no active ones found
                locations = session.query(StorageLocation).all()
        
        if not locations:
            return []
        
        # Build tree structure
        location_dict = {loc.id: {
            'id': loc.id,
            'name': loc.name,
            'code': loc.code,
            'parent_id': loc.parent_id,
            'location_type': loc.location_type,
            'description': loc.description,
            'is_active': loc.is_active,
            'children': []
        } for loc in locations}
        
        # Build tree - only root nodes (no parent) go to top level
        tree = []
        for loc in locations:
            loc_data = location_dict[loc.id]
            if loc.parent_id and loc.parent_id in location_dict:
                # Add to parent's children
                location_dict[loc.parent_id]['children'].append(loc_data)
            elif loc.parent_id is None:
                # Root node - add to tree
                tree.append(loc_data)
        
        # If no root nodes found but we have locations, return all as flat list
        # This can happen if all locations have parent_id but parent doesn't exist
        if not tree and locations:
            # Return all locations as root nodes (flat structure)
            tree = list(location_dict.values())
        
        return tree
    except Exception as e:
        logger.error(f"Unexpected error in storage_service.get_storage_location_tree: {e}", exc_info=True)
        raise
    finally:
        if should_close:
            session.close()


def _get_descendants(session: Session, parent_id: int) -> List[StorageLocation]:
    """Get all descendants of a location recursively"""
    descendants = []
    children = session.query(StorageLocation).filter_by(parent_id=parent_id, is_active=True).all()
    for child in children:
        descendants.append(child)
        descendants.extend(_get_descendants(session, child.id))
    return descendants

def _get_descendants_recursive(session: Session, parent_id: int) -> List[StorageLocation]:
    """Get all descendants of a location recursively (alias for _get_descendants)"""
    return _get_descendants(session, parent_id)


def get_storage_location_path(location_id: int, session: Session = None) -> str:
    """Get full path of a storage location (e.g., 'Raktár → Szekrény → Polc')"""
    session, should_close = _get_session(session)
    try:
        location = session.query(StorageLocation).filter_by(id=location_id).first()
        if not location:
            return ""
        
        path_parts = [location.name]
        current = location
        
        while current.parent_id:
            current = session.query(StorageLocation).filter_by(id=current.parent_id).first()
            if not current:
                break
            path_parts.insert(0, current.name)
        
        return " → ".join(path_parts)
    except Exception as e:
        logger.error(f"Unexpected error in storage_service.get_storage_location_path: {e}", exc_info=True)
        raise
    finally:
        if should_close:
            session.close()


def get_all_storage_locations_flat(session: Session = None) -> List[StorageLocation]:
    """Get all storage locations as flat list (for dropdowns)"""
    session, should_close = _get_session(session)
    try:
        locations = session.query(StorageLocation).filter_by(is_active=True).order_by(StorageLocation.name).all()
        return locations
    except Exception as e:
        logger.error(f"Unexpected error in storage_service.get_all_storage_locations_flat: {e}", exc_info=True)
        raise
    finally:
        if should_close:
            session.close()


# ============================================================================
# PART-LOCATION ASSIGNMENT OPERATIONS
# ============================================================================

def assign_part_to_location(
    part_id: int,
    location_id: int,
    quantity: int,
    assigned_date: Optional[datetime] = None,
    notes: Optional[str] = None,
    session: Session = None
) -> PartLocation:
    """Assign a part to a storage location"""
    session, should_close = _get_session(session)
    try:
        # Validate part exists
        part = session.query(Part).filter_by(id=part_id).first()
        if not part:
            raise NotFoundError("Part", part_id, user_message=f"Part with id {part_id} not found")
        
        # Validate location exists
        location = session.query(StorageLocation).filter_by(id=location_id).first()
        if not location:
            raise NotFoundError("StorageLocation", location_id, user_message=f"Storage location with id {location_id} not found")
        
        if quantity < 0:
            raise ValidationError(
                "Quantity cannot be negative",
                field="quantity",
                user_message="Quantity cannot be negative"
            )
        
        # Get part info for comparison (with supplier relationship)
        part = session.query(Part).options(joinedload(Part.supplier)).filter_by(id=part_id).first()
        if not part:
            raise NotFoundError("Part", part_id, user_message=f"Part with id {part_id} not found")
        
        # Check if there are ANY parts at target location (not just the same part)
        existing_part_locations = session.query(PartLocation).filter_by(
            storage_location_id=location_id
        ).all()
        
        # Check if there's a different part (different SKU) at target location
        for existing_pl in existing_part_locations:
            if existing_pl.part_id != part_id:
                # Different part found - get details (with supplier relationship)
                existing_part = session.query(Part).options(joinedload(Part.supplier)).filter_by(id=existing_pl.part_id).first()
                if existing_part:
                    # Get location path
                    location_path = get_storage_location_path(location_id, session)
                    
                    # Get assigned by user info
                    assigned_by_user = None
                    if existing_pl.assigned_by_user_id:
                        assigned_by_user = session.query(User).filter_by(id=existing_pl.assigned_by_user_id).first()
                    
                    # Build detailed error message
                    error_parts = [
                        f"Az adott tárhelyen ({location_path}) már egy másik cikkszámú alkatrész szerepel.",
                        "",
                        f"Jelenlegi alkatrész a tárhelyen:",
                        f"  • Cikkszám (SKU): {existing_part.sku}",
                        f"  • Név: {existing_part.name}",
                        f"  • Mennyiség: {existing_pl.quantity} {existing_part.unit if existing_part.unit else 'db'}",
                        f"  • Hozzárendelés dátuma: {existing_pl.assigned_date.strftime('%Y-%m-%d %H:%M') if existing_pl.assigned_date else '-'}",
                    ]
                    
                    if assigned_by_user:
                        error_parts.append(f"  • Hozzárendelte: {assigned_by_user.username}")
                    
                    if existing_pl.last_movement_date:
                        error_parts.append(f"  • Utolsó mozgás: {existing_pl.last_movement_date.strftime('%Y-%m-%d %H:%M')}")
                    
                    if existing_part.description:
                        error_parts.append(f"  • Leírás: {existing_part.description}")
                    
                    if existing_part.category:
                        error_parts.append(f"  • Kategória: {existing_part.category}")
                    
                    if existing_part.supplier:
                        error_parts.append(f"  • Beszállító: {existing_part.supplier.name}")
                    
                    error_parts.extend([
                        "",
                        f"Hozzárendelni kívánt alkatrész:",
                        f"  • Cikkszám (SKU): {part.sku}",
                        f"  • Név: {part.name}",
                        "",
                        "Egy tárhelyen csak ugyanaz a cikkszámú alkatrész tárolható."
                    ])
                    
                    error_message = "\n".join(error_parts)
                    raise ValidationError(
                        error_message,
                        field="target_location_id",
                        user_message=error_message
                    )
        
        # Get current stock quantity
        inventory_level = session.query(InventoryLevel).filter_by(part_id=part_id).first()
        if not inventory_level:
            raise NotFoundError("InventoryLevel", part_id, user_message=f"Inventory level not found for part {part_id}")
        
        stock_quantity = inventory_level.quantity_on_hand or 0
        
        # Get total quantity already assigned to storage locations
        total_assigned = session.query(func.sum(PartLocation.quantity)).filter_by(
            part_id=part_id
        ).scalar() or 0
        
        # Check if assignment already exists (same part - can merge)
        existing = session.query(PartLocation).filter_by(
            part_id=part_id,
            storage_location_id=location_id
        ).first()
        
        # Calculate new total assigned quantity
        if existing:
            # If updating existing assignment, subtract current quantity first
            new_total_assigned = total_assigned - existing.quantity + quantity
        else:
            # If new assignment, add to total
            new_total_assigned = total_assigned + quantity
        
        # Validate that total assigned doesn't exceed stock
        if new_total_assigned > stock_quantity:
            available = stock_quantity - total_assigned
            raise ValidationError(
                f"Cannot assign {quantity} units. Stock quantity: {stock_quantity}, Already assigned: {total_assigned}, Available: {max(0, available)}",
                field="quantity",
                user_message=f"Cannot assign {quantity} units. Stock quantity: {stock_quantity}, Already assigned: {total_assigned}, Available: {max(0, available)}"
            )
        
        # Get current user ID for assignment tracking
        assigned_by_user_id = None
        try:
            assigned_by_user_id = get_current_user_id()
        except Exception:
            logger.warning("Could not get current user ID for part assignment")
        
        # Note: 'part' variable is already defined above from the validation
        if existing:
            # Update existing assignment
            existing.quantity += quantity
            existing.last_movement_date = assigned_date or datetime.now()
            if notes:
                existing.notes = (existing.notes or "") + f"\n{notes}" if existing.notes else notes
            existing.updated_at = datetime.now()
            # Update assigned_by_user_id if not set
            if not existing.assigned_by_user_id and assigned_by_user_id:
                existing.assigned_by_user_id = assigned_by_user_id
            session.commit()
            session.refresh(existing)
            
            # Validate inventory level consistency after update
            from services.inventory_service import validate_inventory_levels
            
            discrepancies = validate_inventory_levels(part_id=part_id, session=session)
            if discrepancies:
                discrepancy = discrepancies[0]  # Get first discrepancy for this part
                logger.warning(
                    f"Inventory level discrepancy detected for part {part_id} after assignment update: "
                    f"inventory_level={discrepancy['inventory_level_qty']}, "
                    f"total_in_locations={discrepancy['total_in_locations_qty']}, "
                    f"difference={discrepancy['difference']}"
                )
            
            return existing
        else:
            # Create new assignment
            part_location = PartLocation(
                part_id=part_id,
                storage_location_id=location_id,
                quantity=quantity,
                assigned_date=assigned_date or datetime.now(),
                assigned_by_user_id=assigned_by_user_id,
                last_movement_date=assigned_date or datetime.now(),
                notes=notes,
            )
            session.add(part_location)
            session.commit()
            session.refresh(part_location)
            logger.info(f"Assigned part {part_id} to location {location_id} (quantity={quantity})")
            
            # Log action
            try:
                user_id = get_current_user_id()
                part = session.query(Part).filter_by(id=part_id).first()
                location = session.query(StorageLocation).filter_by(id=location_id).first()
                log_action(
                    category="storage",
                    action_type="assign",
                    entity_type="PartLocation",
                    entity_id=part_location.id,
                    user_id=user_id,
                    description=f"Alkatrész hozzárendelve: {part.name if part else part_id} → {location.name if location else location_id}",
                    metadata={
                        "part_id": part_id,
                        "part_name": part.name if part else None,
                        "storage_location_id": location_id,
                        "location_name": location.name if location else None,
                        "quantity": quantity,
                    },
                    session=session
                )
            except Exception as e:
                logger.warning(f"Error logging part assignment: {e}")
            
            # Validate inventory level consistency after assignment
            from services.inventory_service import validate_inventory_levels
            
            discrepancies = validate_inventory_levels(part_id=part_id, session=session)
            if discrepancies:
                discrepancy = discrepancies[0]  # Get first discrepancy for this part
                logger.warning(
                    f"Inventory level discrepancy detected for part {part_id} after assignment: "
                    f"inventory_level={discrepancy['inventory_level_qty']}, "
                    f"total_in_locations={discrepancy['total_in_locations_qty']}, "
                    f"difference={discrepancy['difference']}"
                )
                # Note: We log the warning but don't fail the operation
                # The discrepancy might be due to manual adjustments or race conditions
                # The validation button in UI can be used to fix discrepancies
            
            return part_location
    except ValidationError as e:
        session.rollback()
        logger.warning(f"Validation error in storage_service.assign_part_to_location: {e}", exc_info=True)
        raise
    except NotFoundError as e:
        session.rollback()
        logger.warning(f"Not found error in storage_service.assign_part_to_location: {e}", exc_info=True)
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Unexpected error in storage_service.assign_part_to_location: {e}", exc_info=True)
        raise
    finally:
        if should_close:
            session.close()


def update_part_location(
    part_location_id: int,
    quantity: Optional[int] = None,
    location_id: Optional[int] = None,
    notes: Optional[str] = None,
    session: Session = None
) -> PartLocation:
    """Update a part-location assignment"""
    session, should_close = _get_session(session)
    try:
        part_location = session.query(PartLocation).filter_by(id=part_location_id).first()
        if not part_location:
            raise NotFoundError("PartLocation", part_location_id, user_message=f"Part location with id {part_location_id} not found")
        
        if quantity is not None:
            if quantity < 0:
                raise ValidationError(
                    "Quantity cannot be negative",
                    field="quantity",
                    user_message="Quantity cannot be negative"
                )
            
            # Get current stock quantity
            inventory_level = session.query(InventoryLevel).filter_by(part_id=part_location.part_id).first()
            if not inventory_level:
                raise NotFoundError("InventoryLevel", part_location.part_id, user_message=f"Inventory level not found for part {part_location.part_id}")
            
            stock_quantity = inventory_level.quantity_on_hand or 0
            
            # Get total quantity already assigned to storage locations (excluding current assignment)
            total_assigned = session.query(func.sum(PartLocation.quantity)).filter_by(
                part_id=part_location.part_id
            ).scalar() or 0
            
            # Subtract current assignment quantity to get total without this assignment
            total_assigned_without_current = total_assigned - part_location.quantity
            
            # Calculate new total assigned quantity
            new_total_assigned = total_assigned_without_current + quantity
            
            # Validate that total assigned doesn't exceed stock
            if new_total_assigned > stock_quantity:
                available = stock_quantity - total_assigned_without_current
                raise ValidationError(
                    f"Cannot set quantity to {quantity}. Stock quantity: {stock_quantity}, Already assigned (excluding this): {total_assigned_without_current}, Available: {max(0, available)}",
                    field="quantity",
                    user_message=f"Cannot set quantity to {quantity}. Stock quantity: {stock_quantity}, Already assigned (excluding this): {total_assigned_without_current}, Available: {max(0, available)}"
                )
            
            part_location.quantity = quantity
            part_location.last_movement_date = datetime.now()
        
        if location_id is not None:
            # Validate new location exists
            location = session.query(StorageLocation).filter_by(id=location_id).first()
            if not location:
                raise NotFoundError("StorageLocation", location_id, user_message=f"Storage location with id {location_id} not found")
            
            # Check if assignment already exists at new location
            existing = session.query(PartLocation).filter_by(
                part_id=part_location.part_id,
                storage_location_id=location_id
            ).first()
            
            if existing and existing.id != part_location_id:
                # Merge with existing assignment
                existing.quantity += part_location.quantity
                existing.last_movement_date = datetime.now()
                session.delete(part_location)
                session.commit()
                session.refresh(existing)
                return existing
            else:
                part_location.storage_location_id = location_id
                part_location.last_movement_date = datetime.now()
        
        if notes is not None:
            part_location.notes = notes
        
        part_location.updated_at = datetime.now()
        session.commit()
        session.refresh(part_location)
        
        # Log action
        try:
            user_id = get_current_user_id()
            part = session.query(Part).filter_by(id=part_location.part_id).first()
            location = session.query(StorageLocation).filter_by(id=part_location.storage_location_id).first()
            log_action(
                category="storage",
                action_type="update",
                entity_type="PartLocation",
                entity_id=part_location.id,
                user_id=user_id,
                description=f"Alkatrész-hely kapcsolat módosítva: {part.name if part else part_location.part_id}",
                metadata={
                    "part_id": part_location.part_id,
                    "storage_location_id": part_location.storage_location_id,
                    "quantity": part_location.quantity,
                },
                session=session
            )
        except Exception as e:
            logger.warning(f"Error logging part location update: {e}")
        
        return part_location
    except ValidationError as e:
        session.rollback()
        logger.warning(f"Validation error in storage_service.update_part_location: {e}", exc_info=True)
        raise
    except NotFoundError as e:
        session.rollback()
        logger.warning(f"Not found error in storage_service.update_part_location: {e}", exc_info=True)
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Unexpected error in storage_service.update_part_location: {e}", exc_info=True)
        raise
    finally:
        if should_close:
            session.close()


def remove_part_from_location(part_location_id: int, session: Session = None) -> bool:
    """Remove a part from a storage location"""
    session, should_close = _get_session(session)
    try:
        part_location = session.query(PartLocation).filter_by(id=part_location_id).first()
        if not part_location:
            raise NotFoundError("PartLocation", part_location_id, user_message=f"Part location with id {part_location_id} not found")
        
        # Get info before deletion for logging
        part_id = part_location.part_id
        location_id = part_location.storage_location_id
        
        session.delete(part_location)
        session.commit()
        logger.info(f"Removed part location assignment (id={part_location_id})")
        
        # Log action
        try:
            user_id = get_current_user_id()
            part = session.query(Part).filter_by(id=part_id).first()
            location = session.query(StorageLocation).filter_by(id=location_id).first()
            log_action(
                category="storage",
                action_type="remove",
                entity_type="PartLocation",
                entity_id=part_location_id,
                user_id=user_id,
                description=f"Alkatrész eltávolítva helyről: {part.name if part else part_id} ← {location.name if location else location_id}",
                metadata={
                    "part_id": part_id,
                    "part_name": part.name if part else None,
                    "storage_location_id": location_id,
                    "location_name": location.name if location else None,
                },
                session=session
            )
        except Exception as e:
            logger.warning(f"Error logging part location removal: {e}")
        
        return True
    finally:
        if should_close:
            session.close()


def get_parts_at_location(
    location_id: int,
    include_children: bool = False,
    session: Session = None
) -> List[Dict]:
    """Get all parts at a storage location (optionally including child locations)"""
    session, should_close = _get_session(session)
    try:
        location_ids = [location_id]
        
        if include_children:
            descendants = _get_descendants(session, location_id)
            location_ids.extend([loc.id for loc in descendants])
        
        part_locations = session.query(PartLocation).options(
            joinedload(PartLocation.assigned_by_user)
        ).filter(
            PartLocation.storage_location_id.in_(location_ids)
        ).all()
        
        result = []
        for pl in part_locations:
            location_path = get_storage_location_path(pl.storage_location_id, session)
            result.append({
                'part_location_id': pl.id,
                'part_id': pl.part.id,
                'part_name': pl.part.name,
                'part_sku': pl.part.sku,
                'location_id': pl.storage_location_id,
                'location_name': pl.storage_location.name,
                'location_path': location_path,
                'quantity': pl.quantity,
                'assigned_date': pl.assigned_date,
                'assigned_by_user_id': pl.assigned_by_user_id,
                'assigned_by_username': pl.assigned_by_user.username if pl.assigned_by_user else None,
                'last_movement_date': pl.last_movement_date,
                'notes': pl.notes,
            })
        
        return result
    except Exception as e:
        logger.error(f"Unexpected error in storage_service.get_parts_at_location: {e}", exc_info=True)
        raise
    finally:
        if should_close:
            session.close()


def get_part_locations(part_id: int, session: Session = None) -> List[Dict]:
    """Get all storage locations for a specific part"""
    session, should_close = _get_session(session)
    try:
        part_locations = session.query(PartLocation).filter_by(part_id=part_id).all()
        
        result = []
        for pl in part_locations:
            location_path = get_storage_location_path(pl.storage_location_id, session)
            result.append({
                'part_location_id': pl.id,
                'location_id': pl.storage_location_id,
                'location_name': pl.storage_location.name,
                'location_path': location_path,
                'quantity': pl.quantity,
                'assigned_date': pl.assigned_date,
                'last_movement_date': pl.last_movement_date,
                'notes': pl.notes,
            })
        
        return result
    finally:
        if should_close:
            session.close()


def search_parts_by_location(search_term: str, session: Session = None) -> List[Dict]:
    """Search for parts by name or SKU, return locations where found"""
    session, should_close = _get_session(session)
    try:
        # Search parts by name or SKU
        search_pattern = f"%{search_term}%"
        parts = session.query(Part).filter(
            or_(
                Part.name.ilike(search_pattern),
                Part.sku.ilike(search_pattern)
            )
        ).all()
        
        if not parts:
            return []
        
        part_ids = [p.id for p in parts]
        
        # Get all part locations for these parts
        part_locations = session.query(PartLocation).filter(
            PartLocation.part_id.in_(part_ids)
        ).all()
        
        # Group by part
        result = []
        for part in parts:
            locations = [pl for pl in part_locations if pl.part_id == part.id]
            if locations:
                location_info = []
                total_quantity = 0
                for pl in locations:
                    location_path = get_storage_location_path(pl.storage_location_id, session)
                    location_info.append({
                        'location_id': pl.storage_location_id,
                        'location_name': pl.storage_location.name,
                        'location_path': location_path,
                        'quantity': pl.quantity,
                    })
                    total_quantity += pl.quantity
                
                result.append({
                    'part_id': part.id,
                    'part_name': part.name,
                    'part_sku': part.sku,
                    'total_quantity': total_quantity,
                    'locations': location_info,
                })
        
        return result
    finally:
        if should_close:
            session.close()


# ============================================================================
# FIFO SUPPORT
# ============================================================================

def get_oldest_batch_at_location(
    part_id: int,
    location_id: int,
    session: Session = None
) -> Optional[StockBatch]:
    """Get the oldest stock batch for a part at a specific location"""
    session, should_close = _get_session(session)
    try:
        batch = session.query(StockBatch).filter(
            and_(
                StockBatch.part_id == part_id,
                StockBatch.storage_location_id == location_id,
                StockBatch.quantity_remaining > 0
            )
        ).order_by(StockBatch.received_date.asc()).first()
        
        return batch
    finally:
        if should_close:
            session.close()


def get_fifo_recommendation(
    part_id: int,
    location_id: Optional[int] = None,
    session: Session = None
) -> Optional[Dict]:
    """
    Get FIFO recommendation (oldest batch info) for a part.
    FIFO is global for the part (same SKU), regardless of storage location.
    The location_id parameter is only used for display purposes (showing where the oldest batch is).
    """
    session, should_close = _get_session(session)
    try:
        # Get the oldest batch globally for this part (same SKU), regardless of location
        # FIFO should work across all storage locations for the same part
        batch = session.query(StockBatch).filter(
            and_(
                StockBatch.part_id == part_id,
                StockBatch.quantity_remaining > 0
            )
        ).order_by(StockBatch.received_date.asc()).first()
        
        if not batch:
            return None
        
        location_path = ""
        if batch.storage_location_id:
            location_path = get_storage_location_path(batch.storage_location_id, session)
        
        return {
            'batch_id': batch.id,
            'part_id': batch.part_id,
            'location_id': batch.storage_location_id,
            'location_path': location_path,
            'quantity_remaining': batch.quantity_remaining,
            'received_date': batch.received_date,
            'unit_price': batch.unit_price,
        }
    finally:
        if should_close:
            session.close()


def transfer_part_location(
    part_location_id: int,
    target_location_id: int,
    quantity: Optional[int] = None,
    notes: Optional[str] = None,  # Notes is now required in UI, but kept optional here for backward compatibility
    session: Session = None
) -> PartLocation:
    """Transfer part from one storage location to another"""
    session, should_close = _get_session(session)
    try:
        # Get source part location
        source_part_location = session.query(PartLocation).filter_by(id=part_location_id).first()
        if not source_part_location:
            raise NotFoundError("PartLocation", part_location_id, user_message=f"Part location with id {part_location_id} not found")
        
        # Validate target location exists
        target_location = session.query(StorageLocation).filter_by(id=target_location_id).first()
        if not target_location:
            raise NotFoundError("StorageLocation", target_location_id, user_message=f"Target storage location with id {target_location_id} not found")
        
        # If transferring to same location, just update notes
        if source_part_location.storage_location_id == target_location_id:
            if notes:
                source_part_location.notes = (source_part_location.notes or "") + f"\n{notes}" if source_part_location.notes else notes
            source_part_location.last_movement_date = datetime.now()
            source_part_location.updated_at = datetime.now()
            session.commit()
            session.refresh(source_part_location)
            return source_part_location
        
        # Determine transfer quantity
        transfer_quantity = quantity if quantity is not None else source_part_location.quantity
        
        if transfer_quantity <= 0:
            raise ValidationError(
                "Transfer quantity must be positive",
                field="quantity",
                user_message="Transfer quantity must be positive"
            )
        
        if transfer_quantity > source_part_location.quantity:
            raise ValidationError(
                f"Cannot transfer {transfer_quantity} units, only {source_part_location.quantity} available at source location",
                field="quantity",
                user_message=f"Cannot transfer {transfer_quantity} units, only {source_part_location.quantity} available at source location"
            )
        
        # Get source part info for comparison (with supplier relationship)
        source_part = session.query(Part).options(joinedload(Part.supplier)).filter_by(id=source_part_location.part_id).first()
        if not source_part:
            raise NotFoundError("Part", source_part_location.part_id, user_message=f"Source part with id {source_part_location.part_id} not found")
        
        # Check if there are ANY parts at target location (not just the same part)
        existing_part_locations = session.query(PartLocation).filter_by(
            storage_location_id=target_location_id
        ).all()
        
        # Check if there's a different part (different SKU) at target location
        for existing_pl in existing_part_locations:
            if existing_pl.part_id != source_part_location.part_id:
                # Different part found - get details (with supplier relationship)
                existing_part = session.query(Part).options(joinedload(Part.supplier)).filter_by(id=existing_pl.part_id).first()
                if existing_part:
                    # Get location path
                    location_path = get_storage_location_path(target_location_id, session)
                    
                    # Get assigned by user info
                    assigned_by_user = None
                    if existing_pl.assigned_by_user_id:
                        assigned_by_user = session.query(User).filter_by(id=existing_pl.assigned_by_user_id).first()
                    
                    # Build detailed error message
                    error_parts = [
                        f"Az adott tárhelyen ({location_path}) már egy másik cikkszámú alkatrész szerepel.",
                        "",
                        f"Jelenlegi alkatrész a tárhelyen:",
                        f"  • Cikkszám (SKU): {existing_part.sku}",
                        f"  • Név: {existing_part.name}",
                        f"  • Mennyiség: {existing_pl.quantity} {existing_part.unit if existing_part.unit else 'db'}",
                        f"  • Hozzárendelés dátuma: {existing_pl.assigned_date.strftime('%Y-%m-%d %H:%M') if existing_pl.assigned_date else '-'}",
                    ]
                    
                    if assigned_by_user:
                        error_parts.append(f"  • Hozzárendelte: {assigned_by_user.username}")
                    
                    if existing_pl.last_movement_date:
                        error_parts.append(f"  • Utolsó mozgás: {existing_pl.last_movement_date.strftime('%Y-%m-%d %H:%M')}")
                    
                    if existing_part.description:
                        error_parts.append(f"  • Leírás: {existing_part.description}")
                    
                    if existing_part.category:
                        error_parts.append(f"  • Kategória: {existing_part.category}")
                    
                    if existing_part.supplier:
                        error_parts.append(f"  • Beszállító: {existing_part.supplier.name}")
                    
                    error_parts.extend([
                        "",
                        f"Áttárazni kívánt alkatrész:",
                        f"  • Cikkszám (SKU): {source_part.sku}",
                        f"  • Név: {source_part.name}",
                        "",
                        "Egy tárhelyen csak ugyanaz a cikkszámú alkatrész tárolható."
                    ])
                    
                    error_message = "\n".join(error_parts)
                    raise ValidationError(
                        error_message,
                        field="target_location_id",
                        user_message=error_message
                    )
        
        # Check if part already exists at target location (same part - can merge)
        target_part_location = session.query(PartLocation).filter_by(
            part_id=source_part_location.part_id,
            storage_location_id=target_location_id
        ).first()
        
        user_id = get_current_user_id()
        
        if target_part_location:
            # Add to existing assignment
            target_part_location.quantity += transfer_quantity
            target_part_location.last_movement_date = datetime.now()
            if notes:
                target_part_location.notes = (target_part_location.notes or "") + f"\n{notes}" if target_part_location.notes else notes
            target_part_location.updated_at = datetime.now()
        else:
            # Create new assignment at target location
            target_part_location = PartLocation(
                part_id=source_part_location.part_id,
                storage_location_id=target_location_id,
                quantity=transfer_quantity,
                assigned_date=datetime.now(),
                assigned_by_user_id=user_id,
                last_movement_date=datetime.now(),
                notes=notes,
            )
            session.add(target_part_location)
        
        # Update source location
        source_part_location.quantity -= transfer_quantity
        source_part_location.last_movement_date = datetime.now()
        source_part_location.updated_at = datetime.now()
        
        # Remove source location if quantity becomes 0
        if source_part_location.quantity == 0:
            session.delete(source_part_location)
            result_part_location = target_part_location
        else:
            result_part_location = target_part_location
        
        session.flush()
        
        # Log action
        try:
            part = session.query(Part).filter_by(id=source_part_location.part_id).first()
            source_location = session.query(StorageLocation).filter_by(id=source_part_location.storage_location_id if source_part_location.quantity > 0 else part_location_id).first()
            log_action(
                category="storage",
                action_type="transfer",
                entity_type="PartLocation",
                entity_id=result_part_location.id,
                user_id=user_id,
                description=f"Alkatrész áttárazva: {part.name if part else source_part_location.part_id} ({transfer_quantity} db) {source_location.name if source_location else '?'} → {target_location.name}",
                metadata={
                    "part_id": source_part_location.part_id,
                    "source_location_id": source_part_location.storage_location_id if source_part_location.quantity > 0 else None,
                    "target_location_id": target_location_id,
                    "quantity": transfer_quantity,
                    "notes": notes if notes else None,
                },
                session=session
            )
        except Exception as e:
            logger.warning(f"Error logging part transfer: {e}")
        
        # Save original source location ID before commit (needed for document generation)
        original_source_location_id = source_part_location.storage_location_id
        
        session.commit()
        session.refresh(result_part_location)
        logger.info(f"Transferred {transfer_quantity} units of part {source_part_location.part_id} from location {original_source_location_id} to {target_location_id}")
        
        # Generate storage transfer document if template is configured
        try:
            from services.storage_document_service import generate_storage_transfer_document
            from services.settings_service import get_selected_storage_transfer_template
            if get_selected_storage_transfer_template(session=session):
                # Use the original source part location ID (before deletion)
                # Pass notes to document generation
                generate_storage_transfer_document(
                    part_location_id,  # Original source part location ID
                    target_location_id,
                    transfer_quantity,
                    notes=notes,  # Pass notes to document
                    session=session
                )
        except Exception as doc_error:
            logger.warning(f"Error generating storage transfer document: {doc_error}")
        
        return result_part_location
    finally:
        if should_close:
            session.close()

