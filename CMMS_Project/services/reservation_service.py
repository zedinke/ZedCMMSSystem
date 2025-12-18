"""
Stock reservation service
"""
from typing import Optional
from datetime import timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from database.session_manager import SessionLocal
from database.models import StockReservation, InventoryLevel, Part, Worksheet, utcnow
from utils.error_handler import BusinessLogicError, NotFoundError
import logging

logger = logging.getLogger(__name__)


def _get_session(session: Optional[Session]) -> (Session, bool):
    if session is None:
        return SessionLocal(), True
    return session, False


def reserve_stock(
    part_id: int,
    quantity: int,
    worksheet_id: Optional[int] = None,
    expires_in_hours: int = 24,
    user_id: Optional[int] = None,
    notes: Optional[str] = None,
    session: Session = None
) -> StockReservation:
    """
    Reserve stock for a worksheet
    
    Args:
        part_id: Part ID
        quantity: Quantity to reserve
        worksheet_id: Worksheet ID (optional)
        expires_in_hours: Reservation expiry in hours
        user_id: User making reservation
        notes: Optional notes
    
    Returns:
        StockReservation: Created reservation
    
    Raises:
        NotFoundError: If part not found
        BusinessLogicError: If insufficient stock
    """
    session, should_close = _get_session(session)
    try:
        # Validate part
        part = session.query(Part).filter_by(id=part_id).first()
        if not part:
            raise NotFoundError("Part", part_id)
        
        # Get inventory level with lock
        inv = session.query(InventoryLevel).filter_by(
            part_id=part_id
        ).with_for_update().first()
        
        if not inv:
            raise NotFoundError("InventoryLevel", part_id)
        
        # Calculate available stock (on_hand - reserved)
        reserved_qty = session.query(
            func.sum(StockReservation.quantity_reserved)
        ).filter(
            StockReservation.part_id == part_id,
            StockReservation.expires_at > utcnow()
        ).scalar() or 0
        
        available = inv.quantity_on_hand - reserved_qty
        
        if available < quantity:
            raise BusinessLogicError(
                f"Insufficient available stock. Available: {available}, "
                f"Requested: {quantity}",
                rule="STOCK_AVAILABILITY"
            )
        
        # Create reservation
        reservation = StockReservation(
            part_id=part_id,
            worksheet_id=worksheet_id,
            quantity_reserved=quantity,
            reserved_at=utcnow(),
            expires_at=utcnow() + timedelta(hours=expires_in_hours),
            user_id=user_id,
            notes=notes
        )
        session.add(reservation)
        
        # Update reserved quantity
        inv.quantity_reserved += quantity
        
        session.commit()
        logger.info(
            f"Stock reserved: part={part_id} qty={quantity} "
            f"worksheet={worksheet_id}"
        )
        return reservation
        
    finally:
        if should_close:
            session.close()


def release_reservation(reservation_id: int, session: Session = None) -> bool:
    """Release a stock reservation"""
    session, should_close = _get_session(session)
    try:
        reservation = session.query(StockReservation).filter_by(
            id=reservation_id
        ).first()
        
        if not reservation:
            raise NotFoundError("StockReservation", reservation_id)
        
        # Update inventory
        inv = session.query(InventoryLevel).filter_by(
            part_id=reservation.part_id
        ).with_for_update().first()
        
        if inv:
            inv.quantity_reserved = max(0, inv.quantity_reserved - reservation.quantity_reserved)
        
        session.delete(reservation)
        session.commit()
        logger.info(f"Reservation released: {reservation_id}")
        return True
        
    finally:
        if should_close:
            session.close()


def cleanup_expired_reservations(session: Session = None) -> int:
    """Clean up expired reservations"""
    session, should_close = _get_session(session)
    try:
        now = utcnow()
        expired = session.query(StockReservation).filter(
            StockReservation.expires_at <= now
        ).all()
        
        count = 0
        for reservation in expired:
            # Release reserved quantity
            inv = session.query(InventoryLevel).filter_by(
                part_id=reservation.part_id
            ).with_for_update().first()
            
            if inv:
                inv.quantity_reserved = max(
                    0, 
                    inv.quantity_reserved - reservation.quantity_reserved
                )
            
            session.delete(reservation)
            count += 1
        
        session.commit()
        logger.info(f"Cleaned up {count} expired reservations")
        return count
        
    finally:
        if should_close:
            session.close()


