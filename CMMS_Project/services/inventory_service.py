"""
Készletkezelő szolgáltatás (beszállítók, cikkek, készletmozgások)
"""

from typing import Optional, List, Dict
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from database.session_manager import SessionLocal
from database.models import Supplier, Part, InventoryLevel, StockTransaction, StockBatch, utcnow
from utils.validators import validate_sku, validate_email
from utils.localization_helper import get_localized_error
from config.constants import TRANSACTION_TYPE_RECEIVED, TRANSACTION_TYPE_INITIAL_STOCK
from utils.error_handler import (
    ValidationError,
    BusinessLogicError,
    NotFoundError,
    CMMSError
)

import logging

logger = logging.getLogger(__name__)


class InventoryServiceError(CMMSError):
    """Általános készletkezelési hiba - backward compatibility"""
    pass


class StockError(InventoryServiceError):
    """Készletmozgás-specifikus hiba"""
    pass


def _get_session(session: Optional[Session]) -> (Session, bool):
    if session is None:
        return SessionLocal(), True
    return session, False


def create_supplier(name: str, email: Optional[str] = None, phone: Optional[str] = None,
                    contact_person: Optional[str] = None, session: Session = None) -> Supplier:
    session, should_close = _get_session(session)
    try:
        if session.query(Supplier).filter_by(name=name).first():
            raise InventoryServiceError(get_localized_error("supplier_name_exists"))
        if email and not validate_email(email):
            raise InventoryServiceError(get_localized_error("validation.invalid_email"))

        supplier = Supplier(
            name=name,
            email=email,
            phone=phone,
            contact_person=contact_person,
            created_at=datetime.now(timezone.utc),
        )
        session.add(supplier)
        session.commit()
        logger.info(f"Beszállító létrehozva: {name}")
        return supplier
    except InventoryServiceError as e:
        session.rollback()
        logger.warning(f"Business logic error in inventory_service.create_supplier: {e}", exc_info=True)
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Unexpected error in inventory_service.create_supplier: {e}", exc_info=True)
        raise
    finally:
        if should_close:
            session.close()


def create_part(
    sku: str,
    name: str,
    category: Optional[str] = None,
    supplier_id: Optional[int] = None,
    buy_price: float = 0.0,
    sell_price: float = 0.0,
    safety_stock: int = 0,
    reorder_quantity: int = 0,
    description: Optional[str] = None,
    bin_location: Optional[str] = None,
    unit: str = "db",
    compatible_machine_ids: Optional[List[int]] = None,
    initial_quantity: int = 0,
    session: Session = None,
) -> Part:
    session, should_close = _get_session(session)
    try:
        if not validate_sku(sku):
            raise ValidationError(
                f"Invalid SKU format: {sku}",
                field="sku",
                user_message=get_localized_error("validation.invalid_sku")
            )
        if session.query(Part).filter_by(sku=sku).first():
            raise ValidationError(
                f"SKU already exists: {sku}",
                field="sku",
                user_message=get_localized_error("validation.duplicate_sku")
            )

        if supplier_id:
            supplier = session.query(Supplier).filter_by(id=supplier_id).first()
            if not supplier:
                raise NotFoundError("Supplier", supplier_id, user_message=get_localized_error("supplier_not_found"))
        
        # Kompatibilis gépek lekérése
        machines = []
        if compatible_machine_ids:
            from database.models import Machine
            machines = session.query(Machine).filter(Machine.id.in_(compatible_machine_ids)).all()
            if len(machines) != len(compatible_machine_ids):
                # Opcionális: warning vagy error ha valamelyik gép nem létezik. Most csak azokat kötjük be amik megvannak.
                pass

        part = Part(
            sku=sku,
            name=name,
            category=category,
            supplier_id=supplier_id,
            buy_price=buy_price,
            sell_price=sell_price,
            safety_stock=safety_stock,
            reorder_quantity=reorder_quantity,
            description=description,
            unit=unit,
            created_at=utcnow(),
            updated_at=utcnow(),
        )
        # Kapcsolatok beállítása
        if machines:
            part.compatible_machines = machines
            
        session.add(part)
        session.commit()

        # Készletszint inicializálása
        inv = InventoryLevel(
            part_id=part.id,
            quantity_on_hand=initial_quantity if initial_quantity > 0 else 0,
            quantity_reserved=0,
            bin_location=bin_location,
            last_updated=utcnow(),
        )
        session.add(inv)
        session.commit()
        
        # Stock transaction létrehozása, ha van kezdeti mennyiség
        if initial_quantity > 0:
            transaction = StockTransaction(
                part_id=part.id,
                transaction_type=TRANSACTION_TYPE_RECEIVED,
                quantity=initial_quantity,
                notes=f"Kezdeti készlet / Initial stock (unit cost: {buy_price})",
                timestamp=utcnow(),
            )
            session.add(transaction)
            session.commit()

        # Logolás
        from services.log_service import log_action
        from services.context_service import get_current_user_id
        
        user_id = get_current_user_id()
        try:
            log_action(
                category="inventory",
                action_type="create",
                entity_type="Part",
                entity_id=part.id,
                user_id=user_id,
                description=f"Alkatrész létrehozva: {name} (SKU: {sku})",
                metadata={
                    "part_name": name,
                    "part_sku": sku,
                    "category": category,
                    "initial_quantity": initial_quantity,
                    "unit_price": buy_price,
                    "total_price": initial_quantity * buy_price if initial_quantity > 0 else 0,
                    "supplier_id": supplier_id,
                    "bin_location": bin_location,
                    "compatible_machine_ids": compatible_machine_ids or [],
                },
                session=session
            )
        except Exception as e:
            logger.warning(f"Error logging part creation: {e}")

        logger.info(f"Cikk létrehozva: {sku} - {name}")
        return part
    except ValidationError as e:
        session.rollback()
        logger.warning(f"Validation error in inventory_service.create_part: {e}", exc_info=True)
        raise
    except NotFoundError as e:
        session.rollback()
        logger.warning(f"Not found error in inventory_service.create_part: {e}", exc_info=True)
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Unexpected error in inventory_service.create_part: {e}", exc_info=True)
        raise
    finally:
        if should_close:
            session.close()


def get_part_by_sku(sku: str, session: Session = None) -> Optional[Part]:
    session, should_close = _get_session(session)
    try:
        return session.query(Part).filter_by(sku=sku).first()
    finally:
        if should_close:
            session.close()


def get_inventory_level(part_id: int, session: Session = None) -> InventoryLevel:
    """Get inventory level for a part"""
    session, should_close = _get_session(session)
    try:
        inv = session.query(InventoryLevel).filter_by(part_id=part_id).first()
        if not inv:
            raise NotFoundError("InventoryLevel", part_id, user_message=get_localized_error("inventory_level_not_found"))
        return inv
    except NotFoundError as e:
        logger.warning(f"Not found error in inventory_service.get_inventory_level: {e}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Unexpected error in inventory_service.get_inventory_level: {e}", exc_info=True)
        raise
    finally:
        if should_close:
            session.close()


def adjust_stock(part_id: int, quantity: int, transaction_type: str,
                 reference_type: Optional[str] = None, reference_id: Optional[int] = None,
                 user_id: Optional[int] = None, notes: Optional[str] = None,
                 storage_location_id: Optional[int] = None,
                 session: Session = None) -> StockTransaction:
    """
    Adjust stock with FIFO support for issuance.
    For positive quantities (receipt), use receive_stock() instead.
    """
    session, should_close = _get_session(session)
    try:
        if quantity == 0:
            raise StockError(get_localized_error("quantity_cannot_be_zero"))
        
        # If positive quantity, redirect to receive_stock (but without batch details)
        # This maintains backward compatibility
        if quantity > 0:
            # For backward compatibility, create a simple batch without detailed info
            part = session.query(Part).filter_by(id=part_id).first()
            if not part:
                raise InventoryServiceError(get_localized_error("part_not_found"))
            
            # Use receive_stock with default values
            batch = receive_stock(
                part_id=part_id,
                quantity=quantity,
                unit_price=part.buy_price or 0.0,
                received_date=utcnow(),
                supplier_id=None,
                invoice_number=None,
                notes=notes,
                user_id=user_id,
                session=session
            )
            # Return the transaction from the batch
            return batch.stock_transaction
        
        # Negative quantity (issuance) - FIFO logic
        inv = session.query(InventoryLevel).filter_by(part_id=part_id).with_for_update().first()
        if not inv:
            raise InventoryServiceError(get_localized_error("inventory_level_not_found"))

        # Check if we have enough stock
        if inv.quantity_on_hand < abs(quantity):
            raise StockError(get_localized_error("insufficient_stock"))

        # Get batches in FIFO order (oldest first)
        # FIFO is global for the part (same SKU), regardless of storage location
        # We get all batches for this part and use FIFO globally
        batches = session.query(StockBatch).filter(
            StockBatch.part_id == part_id,
            StockBatch.quantity_remaining > 0
        ).order_by(StockBatch.received_date.asc()).all()
        
        if not batches:
            # No batches - fallback to simple adjustment (backward compatibility)
            new_qty = inv.quantity_on_hand + quantity
            inv.quantity_on_hand = new_qty
            inv.last_updated = utcnow()
            
            # Update PartLocation quantity if storage_location_id provided (even without batches)
            if storage_location_id:
                from database.models import PartLocation
                from datetime import datetime
                part_location = session.query(PartLocation).filter_by(
                    part_id=part_id,
                    storage_location_id=storage_location_id
                ).first()
                
                if part_location:
                    total_deducted = abs(quantity)  # quantity is negative
                    part_location.quantity = max(0, part_location.quantity - total_deducted)
                    part_location.last_movement_date = datetime.now()
                    part_location.updated_at = datetime.now()
                    # Remove if quantity becomes 0
                    if part_location.quantity == 0:
                        session.delete(part_location)
                else:
                    # If PartLocation doesn't exist but we're deducting from this location,
                    # this is a data inconsistency - log a warning but continue
                    logger.warning(f"PartLocation not found for part_id={part_id}, storage_location_id={storage_location_id} when deducting {abs(quantity)} (no batches)")
            
            tx = StockTransaction(
                part_id=part_id,
                transaction_type=transaction_type,
                quantity=quantity,
                reference_id=reference_id,
                reference_type=reference_type,
                user_id=user_id,
                notes=notes,
                timestamp=utcnow(),
            )
            session.add(tx)
            session.commit()
            logger.info(f"Készletmozgás (nincs batch): part_id={part_id} mennyiség={quantity} típus={transaction_type}, storage_location_id={storage_location_id}")
            return tx
        
        # FIFO issuance: deduct from batches in order
        remaining_to_issue = abs(quantity)
        used_batches = []
        
        for batch in batches:
            if remaining_to_issue <= 0:
                break
            
            if batch.quantity_remaining > 0:
                deduct_amount = min(remaining_to_issue, batch.quantity_remaining)
                batch.quantity_remaining -= deduct_amount
                remaining_to_issue -= deduct_amount
                used_batches.append({
                    "batch_id": batch.id,
                    "quantity": deduct_amount,
                    "unit_price": batch.unit_price
                })
        
        if remaining_to_issue > 0:
            # Rollback batch changes
            session.rollback()
            if storage_location_id:
                raise StockError(get_localized_error("insufficient_stock") + f" (location_id={storage_location_id})")
            raise StockError(get_localized_error("insufficient_stock"))
        
        # Calculate total deducted quantity
        total_deducted = abs(quantity)  # quantity is negative, so we need abs()
        if used_batches:
            total_deducted = sum(b['quantity'] for b in used_batches)
        
        # Update PartLocation quantity if storage_location_id provided
        # This should happen regardless of whether we used batches or not
        if storage_location_id:
            from database.models import PartLocation
            from datetime import datetime
            part_location = session.query(PartLocation).filter_by(
                part_id=part_id,
                storage_location_id=storage_location_id
            ).first()
            
            if part_location:
                part_location.quantity = max(0, part_location.quantity - total_deducted)
                part_location.last_movement_date = datetime.now()
                part_location.updated_at = datetime.now()
                # Remove if quantity becomes 0
                if part_location.quantity == 0:
                    session.delete(part_location)
            else:
                # If PartLocation doesn't exist but we're deducting from this location,
                # this is a data inconsistency - log a warning but continue
                logger.warning(f"PartLocation not found for part_id={part_id}, storage_location_id={storage_location_id} when deducting {total_deducted}")
        
        # Update inventory level
        inv.quantity_on_hand += quantity  # quantity is negative
        inv.last_updated = utcnow()

        # Create transaction
        tx = StockTransaction(
            part_id=part_id,
            transaction_type=transaction_type,
            quantity=quantity,
            reference_id=reference_id,
            reference_type=reference_type,
            user_id=user_id,
            notes=notes,
            timestamp=utcnow(),
        )
        session.add(tx)
        session.flush()  # Get tx.id
        
        # Log with batch information
        from services.log_service import log_action
        try:
            part = session.query(Part).filter_by(id=part_id).first()
            log_action(
                category="inventory",
                action_type="issue",
                entity_type="Part",
                entity_id=part_id,
                user_id=user_id,
                description=f"Készletkiadás: {part.name if part else 'N/A'} - {abs(quantity)} {part.unit if part else 'db'}",
                metadata={
                    "quantity": quantity,
                    "used_batches": used_batches,
                    "reference_type": reference_type,
                    "reference_id": reference_id,
                },
                session=session
            )
        except Exception as e:
            logger.warning(f"Error logging stock issuance: {e}")
        
        session.commit()
        
        # Validate inventory level consistency if storage_location_id was provided
        if storage_location_id:
            discrepancies = validate_inventory_levels(part_id=part_id, session=session)
            if discrepancies:
                discrepancy = discrepancies[0]  # Get first discrepancy for this part
                logger.warning(
                    f"Inventory level discrepancy detected for part {part_id} after stock adjustment: "
                    f"inventory_level={discrepancy['inventory_level_qty']}, "
                    f"total_in_locations={discrepancy['total_in_locations_qty']}, "
                    f"difference={discrepancy['difference']}"
                )
        
        logger.info(f"Készletmozgás (FIFO): part_id={part_id} mennyiség={quantity} típus={transaction_type}, batch-ek: {len(used_batches)}")
        return tx
    except ValidationError as e:
        session.rollback()
        logger.warning(f"Validation error in inventory_service.adjust_stock: {e}", exc_info=True)
        raise
    except NotFoundError as e:
        session.rollback()
        logger.warning(f"Not found error in inventory_service.adjust_stock: {e}", exc_info=True)
        raise
    except (StockError, InventoryServiceError) as e:
        session.rollback()
        logger.warning(f"Business logic error in inventory_service.adjust_stock: {e}", exc_info=True)
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Unexpected error in inventory_service.adjust_stock: {e}", exc_info=True)
        raise
    finally:
        if should_close:
            session.close()


def receive_stock(
    part_id: int,
    quantity: int,
    unit_price: float = 0.0,
    received_date: Optional[datetime] = None,
    supplier_id: Optional[int] = None,
    invoice_number: Optional[str] = None,
    notes: Optional[str] = None,
    user_id: Optional[int] = None,
    storage_location_id: Optional[int] = None,
    session: Session = None
) -> StockBatch:
    """
    Receive stock and create a FIFO batch.
    
    Args:
        part_id: Part ID
        quantity: Quantity received
        unit_price: Unit price at receipt
        received_date: Receipt date (defaults to now)
        supplier_id: Optional supplier ID
        invoice_number: Optional invoice number
        notes: Optional notes
        user_id: User who received the stock
        session: Database session
        
    Returns:
        StockBatch: Created batch
    """
    session, should_close = _get_session(session)
    try:
        if quantity <= 0:
            raise StockError(get_localized_error("quantity_cannot_be_zero"))
        
        part = session.query(Part).filter_by(id=part_id).first()
        if not part:
            raise InventoryServiceError(get_localized_error("part_not_found"))
        
        # Ensure inventory level exists
        inv = session.query(InventoryLevel).filter_by(part_id=part_id).with_for_update().first()
        if not inv:
            inv = InventoryLevel(
                part_id=part_id,
                quantity_on_hand=0,
                quantity_reserved=0,
            )
            session.add(inv)
            session.flush()
        
        # Update inventory level
        inv.quantity_on_hand += quantity
        inv.last_updated = utcnow()
        
        # Create stock transaction
        tx = StockTransaction(
            part_id=part_id,
            transaction_type=TRANSACTION_TYPE_RECEIVED,
            quantity=quantity,
            reference_type=None,
            reference_id=None,
            user_id=user_id,
            notes=notes,
            timestamp=received_date or utcnow(),
        )
        session.add(tx)
        session.flush()  # Get tx.id
        
        # Create batch
        batch = StockBatch(
            part_id=part_id,
            quantity=quantity,
            quantity_remaining=quantity,
            unit_price=unit_price,
            received_date=received_date or utcnow(),
            supplier_id=supplier_id,
            invoice_number=invoice_number,
            notes=notes,
            stock_transaction_id=tx.id,
            storage_location_id=storage_location_id,
        )
        session.add(batch)
        session.flush()  # Get batch.id
        
        # Update part location assignment if storage_location_id provided
        if storage_location_id:
            from services.storage_service import assign_part_to_location
            try:
                assign_part_to_location(
                    part_id=part_id,
                    location_id=storage_location_id,
                    quantity=quantity,
                    assigned_date=received_date or utcnow(),
                    notes=notes,
                    session=session
                )
            except Exception as e:
                logger.warning(f"Error updating part location assignment: {e}")
        
        # Log the receipt
        from services.log_service import log_action
        try:
            log_action(
                category="inventory",
                action_type="receive",
                entity_type="Part",
                entity_id=part_id,
                user_id=user_id,
                description=f"Készletbeérkezés: {part.name} - {quantity} {part.unit}",
                metadata={
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "supplier_id": supplier_id,
                    "invoice_number": invoice_number,
                    "batch_id": batch.id,
                },
                session=session
            )
        except Exception as e:
            logger.warning(f"Error logging stock receipt: {e}")
        
        session.commit()
        logger.info(f"Készletbeérkezés: part_id={part_id} mennyiség={quantity} ár={unit_price} batch_id={batch.id}")
        return batch
    finally:
        if should_close:
            session.close()


def get_fifo_cost(part_id: int, quantity: int, session: Session = None) -> float:
    """
    Calculate FIFO-based average unit cost for a given quantity.
    
    Args:
        part_id: Part ID
        quantity: Quantity to calculate cost for
        session: Database session
        
    Returns:
        float: Average unit price based on FIFO batches
    """
    session, should_close = _get_session(session)
    try:
        if quantity <= 0:
            return 0.0
        
        # Get batches in FIFO order
        batches = session.query(StockBatch).filter(
            StockBatch.part_id == part_id,
            StockBatch.quantity_remaining > 0
        ).order_by(StockBatch.received_date.asc()).all()
        
        if not batches:
            # No batches - use part buy_price as fallback
            part = session.query(Part).filter_by(id=part_id).first()
            if part and part.buy_price:
                return part.buy_price
            return 0.0
        
        # Calculate weighted average from FIFO batches
        total_cost = 0.0
        remaining_qty = quantity
        
        for batch in batches:
            if remaining_qty <= 0:
                break
            
            available = min(remaining_qty, batch.quantity_remaining)
            total_cost += available * batch.unit_price
            remaining_qty -= available
        
        if quantity > 0:
            return total_cost / quantity
        return 0.0
    finally:
        if should_close:
            session.close()


def list_stock_batches(part_id: int, include_empty: bool = False, session: Session = None) -> List[StockBatch]:
    """
    List stock batches for a part.
    
    Args:
        part_id: Part ID
        include_empty: Include batches with zero remaining quantity
        session: Database session
        
    Returns:
        List[StockBatch]: List of batches ordered by received_date
    """
    session, should_close = _get_session(session)
    try:
        query = session.query(StockBatch).filter_by(part_id=part_id)
        
        if not include_empty:
            query = query.filter(StockBatch.quantity_remaining > 0)
        
        return query.order_by(StockBatch.received_date.asc()).all()
    finally:
        if should_close:
            session.close()


def migrate_existing_stock_to_batches(session: Session = None) -> int:
    """
    Migrate existing inventory levels to stock batches.
    Creates a batch for each part with positive quantity_on_hand.
    
    Args:
        session: Database session
        
    Returns:
        int: Number of batches created
    """
    session, should_close = _get_session(session)
    batches_created = 0
    try:
        # Get all inventory levels with positive quantity
        inventory_levels = session.query(InventoryLevel).filter(
            InventoryLevel.quantity_on_hand > 0
        ).all()
        
        for inv in inventory_levels:
            # Check if batches already exist for this part
            existing_batches = session.query(StockBatch).filter_by(part_id=inv.part_id).count()
            if existing_batches > 0:
                logger.info(f"Part {inv.part_id} already has batches, skipping")
                continue
            
            part = session.query(Part).filter_by(id=inv.part_id).first()
            if not part:
                logger.warning(f"Part {inv.part_id} not found, skipping")
                continue
            
            # Create transaction
            tx = StockTransaction(
                part_id=inv.part_id,
                transaction_type=TRANSACTION_TYPE_INITIAL_STOCK,
                quantity=inv.quantity_on_hand,
                reference_type=None,
                reference_id=None,
                user_id=None,
                notes="Migrated from existing inventory",
                timestamp=part.created_at or utcnow(),
            )
            session.add(tx)
            session.flush()
            
            # Create batch
            batch = StockBatch(
                part_id=inv.part_id,
                quantity=inv.quantity_on_hand,
                quantity_remaining=inv.quantity_on_hand,
                unit_price=part.buy_price or 0.0,
                received_date=part.created_at or utcnow(),
                supplier_id=part.supplier_id,
                invoice_number=None,
                notes="Migrated from existing inventory",
                stock_transaction_id=tx.id,
            )
            session.add(batch)
            batches_created += 1
            logger.info(f"Created batch for part {inv.part_id}: {inv.quantity_on_hand} @ {part.buy_price or 0.0}")
        
        session.commit()
        logger.info(f"Migration completed: {batches_created} batches created")
        return batches_created
    except Exception as e:
        session.rollback()
        logger.error(f"Error migrating stock to batches: {e}", exc_info=True)
        raise
    finally:
        if should_close:
            session.close()


def validate_inventory_levels(part_id: Optional[int] = None, session: Session = None) -> List[Dict]:
    """Validálja, hogy InventoryLevel.quantity_on_hand = SUM(PartLocation.quantity)
    
    Returns a list of discrepancies:
    {
        'part_id': int,
        'part_name': str,
        'inventory_level': int,
        'total_in_locations': int,
        'difference': int
    }
    """
    session, should_close = _get_session(session)
    try:
        from sqlalchemy import func
        from database.models import PartLocation
        
        query = session.query(
            Part.id,
            Part.name,
            InventoryLevel.quantity_on_hand,
            func.coalesce(func.sum(PartLocation.quantity), 0).label('total_in_locations')
        ).join(
            InventoryLevel, Part.id == InventoryLevel.part_id
        ).outerjoin(
            PartLocation, Part.id == PartLocation.part_id
        )
        
        if part_id:
            query = query.filter(Part.id == part_id)
        
        query = query.group_by(Part.id, Part.name, InventoryLevel.quantity_on_hand)
        
        discrepancies = []
        for row in query.all():
            part_id_val, part_name, inv_level_qty, total_in_locations = row
            total = total_in_locations if total_in_locations else 0
            
            if inv_level_qty != total:
                discrepancies.append({
                    'part_id': part_id_val,
                    'part_name': part_name,
                    'inventory_level': inv_level_qty,
                    'total_in_locations': total,
                    'difference': inv_level_qty - total
                })
        
        return discrepancies
    finally:
        if should_close:
            session.close()


def fix_inventory_level_discrepancy(part_id: int, session: Session = None) -> bool:
    """Javít egy InventoryLevel eltérést a PartLocation[] összege alapján"""
    session, should_close = _get_session(session)
    try:
        from sqlalchemy import func
        from database.models import PartLocation
        
        # Get sum of PartLocation quantities
        total_in_locations = session.query(
            func.coalesce(func.sum(PartLocation.quantity), 0)
        ).filter_by(part_id=part_id).scalar() or 0
        
        # Update InventoryLevel
        inv_level = session.query(InventoryLevel).filter_by(part_id=part_id).first()
        if inv_level:
            inv_level.quantity_on_hand = total_in_locations
            session.commit()
            return True
        return False
    finally:
        if should_close:
            session.close()


def list_stock_transactions(part_id: Optional[int] = None, limit: int = 100, session: Session = None) -> List[StockTransaction]:
    session, should_close = _get_session(session)
    try:
        query = session.query(StockTransaction).order_by(StockTransaction.timestamp.desc())
        if part_id:
            query = query.filter_by(part_id=part_id)
        return query.limit(limit).all()
    finally:
        if should_close:
            session.close()


def list_parts(session: Session = None, limit: Optional[int] = None, offset: int = 0) -> List[Part]:
    """List parts with inventory levels loaded in batch (with optional pagination)"""
    session, should_close = _get_session(session)
    try:
        from sqlalchemy.orm import joinedload
        query = session.query(Part).options(
            joinedload(Part.supplier),
            joinedload(Part.compatible_machines)
        ).order_by(Part.name)
        
        # Apply pagination if specified
        if limit is not None:
            query = query.limit(limit).offset(offset)
        
        parts = query.all()
        
        # Batch load all inventory levels in one query to avoid N+1
        if parts:
            part_ids = [p.id for p in parts]
            inventory_levels = session.query(InventoryLevel).filter(
                InventoryLevel.part_id.in_(part_ids)
            ).all()
            
            # Create a dictionary for quick lookup
            inv_dict = {inv.part_id: inv for inv in inventory_levels}
            
            # Attach inventory levels to parts (for backward compatibility)
            for part in parts:
                if part.id in inv_dict:
                    # Store reference for easy access
                    part._inventory_level = inv_dict[part.id]
        
        return parts
    finally:
        if should_close:
            session.close()


def count_parts(session: Session = None) -> int:
    """Count total number of parts (for pagination)"""
    session, should_close = _get_session(session)
    try:
        from sqlalchemy import func
        return session.query(func.count(Part.id)).scalar() or 0
    finally:
        if should_close:
            session.close()


def get_inventory_levels_batch(part_ids: List[int], session: Session = None) -> dict:
    """Get inventory levels for multiple parts in one query (optimized)"""
    session, should_close = _get_session(session)
    try:
        inventory_levels = session.query(InventoryLevel).filter(
            InventoryLevel.part_id.in_(part_ids)
        ).all()
        
        # Return as dictionary: {part_id: InventoryLevel}
        return {inv.part_id: inv for inv in inventory_levels}
    finally:
        if should_close:
            session.close()


def get_part(part_id: int, session: Session = None) -> Optional[Part]:
    """Get part by ID"""
    session, should_close = _get_session(session)
    try:
        from sqlalchemy.orm import joinedload
        return session.query(Part).options(
            joinedload(Part.supplier),
            joinedload(Part.compatible_machines)
        ).filter_by(id=part_id).first()
    finally:
        if should_close:
            session.close()


def update_part(
    part_id: int,
    name: Optional[str] = None,
    category: Optional[str] = None,
    supplier_id: Optional[int] = None,
    buy_price: Optional[float] = None,
    sell_price: Optional[float] = None,
    safety_stock: Optional[int] = None,
    reorder_quantity: Optional[int] = None,
    description: Optional[str] = None,
    bin_location: Optional[str] = None,
    unit: Optional[str] = None,
    compatible_machine_ids: Optional[List[int]] = None,
    change_reason: Optional[str] = None,
    session: Session = None,
) -> Part:
    """Update part"""
    session, should_close = _get_session(session)
    try:
        from sqlalchemy.orm import joinedload
        part = session.query(Part).options(
            joinedload(Part.compatible_machines)
        ).filter_by(id=part_id).first()
        if not part:
            raise InventoryServiceError(get_localized_error("part_not_found"))
        
        # Track changes for logging
        changes = {}
        old_compatible_machine_ids = set([m.id for m in part.compatible_machines])
        
        if name is not None and part.name != name:
            changes["name"] = {"old": part.name, "new": name}
            part.name = name
        if category is not None and part.category != category:
            changes["category"] = {"old": part.category or "-", "new": category or "-"}
            part.category = category
        if supplier_id is not None:
            if supplier_id:
                supplier = session.query(Supplier).filter_by(id=supplier_id).first()
                if not supplier:
                    raise InventoryServiceError(get_localized_error("supplier_not_found"))
            if part.supplier_id != supplier_id:
                changes["supplier_id"] = {"old": str(part.supplier_id or "-"), "new": str(supplier_id or "-")}
            part.supplier_id = supplier_id
        if buy_price is not None and part.buy_price != buy_price:
            changes["buy_price"] = {"old": str(part.buy_price), "new": str(buy_price)}
            part.buy_price = buy_price
        if sell_price is not None and part.sell_price != sell_price:
            changes["sell_price"] = {"old": str(part.sell_price), "new": str(sell_price)}
            part.sell_price = sell_price
        if safety_stock is not None and part.safety_stock != safety_stock:
            changes["safety_stock"] = {"old": str(part.safety_stock), "new": str(safety_stock)}
            part.safety_stock = safety_stock
        if reorder_quantity is not None and part.reorder_quantity != reorder_quantity:
            changes["reorder_quantity"] = {"old": str(part.reorder_quantity), "new": str(reorder_quantity)}
            part.reorder_quantity = reorder_quantity
        if description is not None and part.description != description:
            changes["description"] = {"old": part.description or "-", "new": description or "-"}
            part.description = description
        if unit is not None and part.unit != unit:
            changes["unit"] = {"old": part.unit or "-", "new": unit or "-"}
            part.unit = unit
        
        # Update compatible machines
        if compatible_machine_ids is not None:
            new_compatible_machine_ids = set(compatible_machine_ids)
            if old_compatible_machine_ids != new_compatible_machine_ids:
                from database.models import Machine
                old_machines = session.query(Machine).filter(Machine.id.in_(old_compatible_machine_ids)).all()
                new_machines = session.query(Machine).filter(Machine.id.in_(new_compatible_machine_ids)).all()
                changes["compatible_machine_ids"] = {
                    "old": ", ".join([m.name for m in old_machines]) if old_machines else "-",
                    "new": ", ".join([m.name for m in new_machines]) if new_machines else "-"
                }
                part.compatible_machines = new_machines
        
        # Update bin location in inventory level
        if bin_location is not None:
            inv = session.query(InventoryLevel).filter_by(part_id=part_id).first()
            if inv:
                if inv.bin_location != bin_location:
                    changes["bin_location"] = {"old": inv.bin_location or "-", "new": bin_location or "-"}
                inv.bin_location = bin_location
        
        part.updated_at = utcnow()
        session.commit()
        
        # Invalidate cache after update
        invalidate_inventory_cache()
        
        # Logolás, ha volt változás
        if changes:
            from services.log_service import log_action
            from services.context_service import get_current_user_id
            
            user_id = get_current_user_id()
            try:
                log_action(
                    category="inventory",
                    action_type="update",
                    entity_type="Part",
                    entity_id=part_id,
                    user_id=user_id,
                    description=f"Alkatrész módosítva: {part.name}",
                    metadata={"changes": changes, "change_reason": change_reason},
                    session=session
                )
            except Exception as e:
                logger.warning(f"Error logging part update: {e}")
        
        logger.info(f"Alkatrész frissítve: {part.sku}")
        return part
    except ValidationError as e:
        session.rollback()
        logger.warning(f"Validation error in inventory_service.update_part: {e}", exc_info=True)
        raise
    except NotFoundError as e:
        session.rollback()
        logger.warning(f"Not found error in inventory_service.update_part: {e}", exc_info=True)
        raise
    except InventoryServiceError as e:
        session.rollback()
        logger.warning(f"Business logic error in inventory_service.update_part: {e}", exc_info=True)
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Unexpected error in inventory_service.update_part: {e}", exc_info=True)
        raise
    finally:
        if should_close:
            session.close()


def delete_part(part_id: int, session: Session = None) -> bool:
    """Delete part"""
    session, should_close = _get_session(session)
    try:
        part = session.query(Part).filter_by(id=part_id).first()
        if not part:
            raise InventoryServiceError(get_localized_error("part_not_found"))
        
        # Check if part has stock transactions
        tx_count = session.query(StockTransaction).filter_by(part_id=part_id).count()
        if tx_count > 0:
            raise InventoryServiceError(get_localized_error("part_has_transactions"))
        
        # Get part info before deletion for logging
        part_name = part.name
        part_sku = part.sku
        
        # Generate scrapping document if auto-generate is enabled
        from services.settings_service import get_auto_generate_scrapping_doc
        from services.scrapping_service import generate_scrapping_document
        from services.context_service import get_current_user_id
        from services.log_service import log_action
        
        user_id = get_current_user_id()
        
        if get_auto_generate_scrapping_doc():
            try:
                generate_scrapping_document(
                    entity_type="Part",
                    entity_id=part_id,
                    reason="Alkatrész törlése",
                    session=session
                )
            except Exception as e:
                logger.warning(f"Error generating scrapping document for part {part_id}: {e}")
        
        # Log the deletion
        try:
            log_action(
                category="inventory",
                action_type="delete",
                entity_type="Part",
                entity_id=part_id,
                user_id=user_id,
                description=f"Alkatrész törölve: {part_name} (SKU: {part_sku})",
                metadata={
                    "part_name": part_name,
                    "part_sku": part_sku,
                },
                session=session
            )
        except Exception as e:
            logger.warning(f"Error logging part deletion: {e}")
        
        # Delete inventory level
        inv = session.query(InventoryLevel).filter_by(part_id=part_id).first()
        if inv:
            session.delete(inv)
        
        # Delete part
        session.delete(part)
        session.commit()
        logger.info(f"Alkatrész törölve: {part_id}")
        return True
    finally:
        if should_close:
            session.close()