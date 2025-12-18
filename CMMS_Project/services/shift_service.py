"""
Shift Schedule Service
Handles user shift schedules and work shift management
"""

from typing import Optional, List, Dict
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import or_

from database.session_manager import SessionLocal
from database.models import User, ShiftSchedule, ShiftOverride, Role, utcnow
from services.log_service import log_action
from services.context_service import get_current_user_id
from config.roles import ROLE_MAINTENANCE_TECH

import logging

logger = logging.getLogger(__name__)


class ShiftServiceError(Exception):
    """Generic shift service error"""
    pass


def _get_session(session: Optional[Session]) -> tuple:
    """Get database session, creating one if needed"""
    if session is None:
        return SessionLocal(), True
    return session, False


def set_user_shift_schedule(
    user_id: int,
    shift_type: str,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    effective_from: Optional[datetime] = None,
    rotation_start_date: Optional[date] = None,
    initial_shift: Optional[str] = None,
    rotation_pattern: str = "weekly",
    session: Session = None
) -> ShiftSchedule:
    """
    Set user shift schedule
    
    Args:
        user_id: User ID
        shift_type: Shift type ("single", "3_shift", "4_shift")
        start_time: Start time in HH:MM format (required for single shift)
        end_time: End time in HH:MM format (required for single shift)
        effective_from: When this schedule becomes effective (default: now)
        session: Database session
    
    Returns:
        Created ShiftSchedule object
    """
    session, should_close = _get_session(session)
    
    try:
        # Validate shift type
        if shift_type not in ["single", "3_shift", "4_shift"]:
            raise ShiftServiceError(f"Invalid shift type: {shift_type}")
        
        # Validate single shift requires times
        if shift_type == "single":
            if not start_time or not end_time:
                raise ShiftServiceError("Start time and end time required for single shift")
        
        # Validate user exists
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            raise ShiftServiceError("User not found")
        
        # Set effective_from to now if not provided
        if effective_from is None:
            effective_from = utcnow()
        
        # Deactivate previous active schedules
        previous_schedules = session.query(ShiftSchedule).filter(
            ShiftSchedule.user_id == user_id,
            ShiftSchedule.effective_to.is_(None)
        ).all()
        
        for prev_schedule in previous_schedules:
            prev_schedule.effective_to = effective_from
        
        # Validate rotation parameters for 3_shift
        if shift_type == "3_shift":
            if not rotation_start_date or not initial_shift:
                raise ShiftServiceError("rotation_start_date and initial_shift are required for 3_shift type")
            if initial_shift not in ["DE", "ÉJ", "DU"]:
                raise ShiftServiceError(f"Invalid initial_shift: {initial_shift}. Must be DE, ÉJ, or DU")
        
        # Create new schedule
        shift_schedule = ShiftSchedule(
            user_id=user_id,
            shift_type=shift_type,
            start_time=start_time,
            end_time=end_time,
            effective_from=effective_from,
            effective_to=None,  # Active schedule
            rotation_start_date=rotation_start_date if shift_type == "3_shift" else None,
            initial_shift=initial_shift if shift_type == "3_shift" else None,
            rotation_pattern=rotation_pattern if shift_type == "3_shift" else None
        )
        
        session.add(shift_schedule)
        
        # Update user's shift fields for quick access
        user.shift_type = shift_type
        user.shift_start_time = start_time
        user.shift_end_time = end_time
        
        session.commit()
        session.refresh(shift_schedule)
        
        # Log action
        try:
            current_user_id = get_current_user_id()
            action_type = "set_rotation" if shift_type == "3_shift" and rotation_start_date else "create"
            log_action(
                category="shift",
                action_type=action_type,
                entity_type="ShiftSchedule",
                entity_id=shift_schedule.id,
                user_id=current_user_id or user_id,
                description=f"Műszak beosztás beállítva: {shift_type}" + (f" (forgás kezdete: {rotation_start_date}, kezdő műszak: {initial_shift})" if rotation_start_date else ""),
                metadata={
                    "shift_type": shift_type,
                    "start_time": start_time,
                    "end_time": end_time,
                    "effective_from": effective_from.isoformat() if effective_from else None,
                    "rotation_start_date": rotation_start_date.isoformat() if rotation_start_date else None,
                    "initial_shift": initial_shift,
                    "rotation_pattern": rotation_pattern,
                },
                session=session
            )
        except Exception as e:
            logger.warning(f"Error logging shift schedule creation: {e}")
        
        logger.info(f"Shift schedule created for user {user_id}: {shift_type}")
        return shift_schedule
        
    except Exception as e:
        session.rollback()
        if isinstance(e, ShiftServiceError):
            raise
        logger.error(f"Error setting shift schedule: {e}")
        raise ShiftServiceError(f"Error setting shift schedule: {str(e)}")
    finally:
        if should_close:
            session.close()


def get_user_shift_schedule(
    user_id: int,
    date: Optional[date] = None,
    session: Session = None
) -> Optional[ShiftSchedule]:
    """
    Get user's active shift schedule for a specific date
    
    Args:
        user_id: User ID
        date: Date to check (default: today)
        session: Database session
    
    Returns:
        ShiftSchedule object or None
    """
    session, should_close = _get_session(session)
    
    try:
        if date is None:
            date = datetime.now().date()
        
        # Convert date to datetime for comparison
        check_datetime = datetime.combine(date, datetime.min.time())
        
        # Find active schedule for the date
        schedule = session.query(ShiftSchedule).filter(
            ShiftSchedule.user_id == user_id,
            ShiftSchedule.effective_from <= check_datetime,
            or_(
                ShiftSchedule.effective_to.is_(None),
                ShiftSchedule.effective_to >= check_datetime
            )
        ).order_by(ShiftSchedule.effective_from.desc()).first()
        
        return schedule
        
    finally:
        if should_close:
            session.close()


def get_all_shift_schedules(
    date: Optional[date] = None,
    session: Session = None
) -> List[ShiftSchedule]:
    """
    Get all active shift schedules for a specific date
    
    Args:
        date: Date to check (default: today)
        session: Database session
    
    Returns:
        List of ShiftSchedule objects
    """
    session, should_close = _get_session(session)
    
    try:
        if date is None:
            date = datetime.now().date()
        
        # Convert date to datetime for comparison
        check_datetime = datetime.combine(date, datetime.min.time())
        
        # Find all active schedules for the date
        schedules = session.query(ShiftSchedule).filter(
            ShiftSchedule.effective_from <= check_datetime,
            or_(
                ShiftSchedule.effective_to.is_(None),
                ShiftSchedule.effective_to >= check_datetime
            )
        ).order_by(ShiftSchedule.user_id, ShiftSchedule.effective_from.desc()).all()
        
        return schedules
        
    finally:
        if should_close:
            session.close()


def calculate_shift_for_date(user_id: int, target_date: date, session: Session = None) -> Optional[str]:
    """
    Calculate shift type for a specific date based on rotation
    
    Args:
        user_id: User ID
        target_date: Target date to calculate shift for
        session: Database session
    
    Returns:
        Shift type string (DE, ÉJ, DU) or None if no rotation configured
    """
    session, should_close = _get_session(session)
    
    try:
        # Check for override first
        override = session.query(ShiftOverride).filter(
            ShiftOverride.user_id == user_id,
            ShiftOverride.override_date == target_date
        ).first()
        
        if override:
            return override.shift_type
        
        # Get active schedule for the date
        schedule = get_user_shift_schedule(user_id, target_date, session=session)
        
        if not schedule or schedule.shift_type != "3_shift":
            return None
        
        if not schedule.rotation_start_date or not schedule.initial_shift:
            return None
        
        # Calculate weeks since rotation start (assuming weekly rotation)
        if schedule.rotation_pattern == "weekly":
            # Get the Monday of the rotation start week
            rotation_start = schedule.rotation_start_date
            rotation_monday = rotation_start - timedelta(days=rotation_start.weekday())
            target_monday = target_date - timedelta(days=target_date.weekday())
            
            # Calculate week number (weeks since rotation start, can be negative if target is before start)
            days_diff = (target_monday - rotation_monday).days
            weeks_since_start = days_diff // 7
            
            # Rotation: DE -> ÉJ -> DU -> DE (cycle every 3 weeks)
            shift_cycle = ["DE", "ÉJ", "DU"]
            
            # Find the index of initial_shift in the cycle
            initial_index = shift_cycle.index(schedule.initial_shift)
            
            # Calculate the shift for this week (handle negative weeks)
            current_shift_index = (initial_index + weeks_since_start) % 3
            if current_shift_index < 0:
                current_shift_index += 3
            return shift_cycle[current_shift_index]
        
        # For other rotation patterns, return None (not implemented)
        return None
        
    finally:
        if should_close:
            session.close()


def get_shift_override(user_id: int, override_date: date, session: Session = None) -> Optional[ShiftOverride]:
    """
    Get shift override for a specific date
    
    Args:
        user_id: User ID
        override_date: Date to check
        session: Database session
    
    Returns:
        ShiftOverride object or None
    """
    session, should_close = _get_session(session)
    
    try:
        return session.query(ShiftOverride).filter(
            ShiftOverride.user_id == user_id,
            ShiftOverride.override_date == override_date
        ).first()
    finally:
        if should_close:
            session.close()


def create_shift_override(
    user_id: int,
    override_date: date,
    shift_type: str,
    created_by_user_id: int,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    notes: Optional[str] = None,
    session: Session = None
) -> ShiftOverride:
    """
    Create a shift override for a specific date
    
    Args:
        user_id: User ID
        override_date: Date to override
        shift_type: Shift type (DE, ÉJ, DU)
        created_by_user_id: User who created the override
        start_time: Optional start time
        end_time: Optional end time
        notes: Optional notes
        session: Database session
    
    Returns:
        Created ShiftOverride object
    """
    session, should_close = _get_session(session)
    
    try:
        # Validate shift type
        if shift_type not in ["DE", "ÉJ", "DU"]:
            raise ShiftServiceError(f"Invalid shift type for override: {shift_type}. Must be DE, ÉJ, or DU")
        
        # Validate user exists
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            raise ShiftServiceError("User not found")
        
        # Check if override already exists
        existing = get_shift_override(user_id, override_date, session=session)
        if existing:
            # Update existing override
            existing.shift_type = shift_type
            existing.start_time = start_time
            existing.end_time = end_time
            existing.notes = notes
            existing.created_by_user_id = created_by_user_id
            existing.created_at = utcnow()
            override = existing
        else:
            # Create new override
            override = ShiftOverride(
                user_id=user_id,
                override_date=override_date,
                shift_type=shift_type,
                start_time=start_time,
                end_time=end_time,
                created_by_user_id=created_by_user_id,
                notes=notes
            )
            session.add(override)
        
        session.commit()
        session.refresh(override)
        
        # Log action
        try:
            log_action(
                category="shift",
                action_type="create_override",
                entity_type="ShiftOverride",
                entity_id=override.id,
                user_id=created_by_user_id,
                description=f"Műszak felülírás létrehozva: {user.full_name or user.username} - {override_date} - {shift_type}",
                metadata={
                    "user_id": user_id,
                    "override_date": override_date.isoformat(),
                    "shift_type": shift_type,
                    "start_time": start_time,
                    "end_time": end_time,
                    "notes": notes,
                },
                session=session
            )
        except Exception as e:
            logger.warning(f"Error logging shift override creation: {e}")
        
        logger.info(f"Shift override created for user {user_id} on {override_date}: {shift_type}")
        return override
        
    except Exception as e:
        session.rollback()
        if isinstance(e, ShiftServiceError):
            raise
        logger.error(f"Error creating shift override: {e}")
        raise ShiftServiceError(f"Error creating shift override: {str(e)}")
    finally:
        if should_close:
            session.close()


def delete_shift_override(override_id: int, deleted_by_user_id: int, session: Session = None) -> None:
    """
    Delete a shift override
    
    Args:
        override_id: Override ID to delete
        deleted_by_user_id: User who deleted the override
        session: Database session
    """
    session, should_close = _get_session(session)
    
    try:
        override = session.query(ShiftOverride).filter_by(id=override_id).first()
        if not override:
            raise ShiftServiceError("Shift override not found")
        
        user = session.query(User).filter_by(id=override.user_id).first()
        user_name = user.full_name if user and user.full_name else (user.username if user else "Unknown")
        
        override_date = override.override_date
        shift_type = override.shift_type
        
        session.delete(override)
        session.commit()
        
        # Log action
        try:
            log_action(
                category="shift",
                action_type="delete_override",
                entity_type="ShiftOverride",
                entity_id=override_id,
                user_id=deleted_by_user_id,
                description=f"Műszak felülírás törölve: {user_name} - {override_date} - {shift_type}",
                metadata={
                    "user_id": override.user_id,
                    "override_date": override_date.isoformat(),
                    "shift_type": shift_type,
                },
                session=session
            )
        except Exception as e:
            logger.warning(f"Error logging shift override deletion: {e}")
        
        logger.info(f"Shift override {override_id} deleted")
        
    except Exception as e:
        session.rollback()
        if isinstance(e, ShiftServiceError):
            raise
        logger.error(f"Error deleting shift override: {e}")
        raise ShiftServiceError(f"Error deleting shift override: {str(e)}")
    finally:
        if should_close:
            session.close()


def get_shift_calendar(year: int, user_id: Optional[int] = None, role_filter: Optional[str] = None, session: Session = None) -> Dict[str, Dict]:
    """
    Get shift calendar data for a year, integrating with vacation calendar
    OPTIMIZED: Uses batch queries instead of per-day queries
    
    Args:
        year: Year to get calendar for
        user_id: Optional user ID to filter (None = all users)
        role_filter: Optional role name to filter (e.g., ROLE_MAINTENANCE_TECH)
        session: Database session
    
    Returns:
        Dictionary with date strings (YYYY-MM-DD) as keys and shift info as values
        Format: {"YYYY-MM-DD": {"users": [{"user_id": int, "shift": str, "is_vacation": bool, "vacation_status": str}], ...}
    """
    from services.vacation_service import get_vacation_calendar
    from sqlalchemy.orm import joinedload
    
    session, should_close = _get_session(session)
    
    try:
        # Get vacation calendar data (already optimized)
        vacation_calendar = get_vacation_calendar(year, session=session)
        
        # Build user query with eager loading
        query = session.query(User).join(Role).options(joinedload(User.role))
        if role_filter:
            query = query.filter(Role.name == role_filter)
        if user_id:
            query = query.filter(User.id == user_id)
        
        users = query.all()
        
        # Initialize calendar for all dates
        calendar = {}
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        current_date = start_date
        
        while current_date <= end_date:
            date_str = current_date.isoformat()
            calendar[date_str] = {"users": []}
            current_date += timedelta(days=1)
        
        # OPTIMIZATION: Batch load all schedules and overrides for the year
        year_start_datetime = datetime.combine(start_date, datetime.min.time())
        year_end_datetime = datetime.combine(end_date, datetime.max.time())
        
        # Get all active schedules for users in one query
        user_ids = [u.id for u in users]
        if not user_ids:
            return calendar
        
        all_schedules = session.query(ShiftSchedule).filter(
            ShiftSchedule.user_id.in_(user_ids),
            ShiftSchedule.shift_type == "3_shift",
            ShiftSchedule.effective_from <= year_end_datetime,
            or_(
                ShiftSchedule.effective_to.is_(None),
                ShiftSchedule.effective_to >= year_start_datetime
            )
        ).all()
        
        # Get all overrides for the year in one query
        all_overrides = session.query(ShiftOverride).filter(
            ShiftOverride.user_id.in_(user_ids),
            ShiftOverride.override_date >= start_date,
            ShiftOverride.override_date <= end_date
        ).all()
        
        # Build override lookup: {(user_id, date): shift_type}
        override_lookup = {}
        for override in all_overrides:
            key = (override.user_id, override.override_date)
            override_lookup[key] = override.shift_type
        
        # Get all vacation requests for the year in one query (for status lookup)
        from database.models import VacationRequest
        vacation_requests = session.query(VacationRequest).filter(
            VacationRequest.user_id.in_(user_ids),
            VacationRequest.start_date <= year_end_datetime,
            VacationRequest.end_date >= year_start_datetime
        ).all()
        
        # Build vacation request lookup: {(user_id, date): status}
        vacation_request_lookup = {}
        for req in vacation_requests:
            req_start = req.start_date.date() if isinstance(req.start_date, datetime) else req.start_date
            req_end = req.end_date.date() if isinstance(req.end_date, datetime) else req.end_date
            req_date = req_start
            while req_date <= req_end and req_date <= end_date:
                if req_date >= start_date:
                    key = (req.user_id, req_date)
                    # Keep the most recent request status if multiple overlap
                    if key not in vacation_request_lookup:
                        vacation_request_lookup[key] = req.status
                req_date += timedelta(days=1)
        
        # Process each user with their schedule
        for user in users:
            # Find user's active schedule for the year
            user_schedule = None
            for schedule in all_schedules:
                if schedule.user_id == user.id:
                    # Check if schedule is active for the year
                    if schedule.effective_from <= year_end_datetime and (
                        schedule.effective_to is None or schedule.effective_to >= year_start_datetime
                    ):
                        user_schedule = schedule
                        break
            
            if not user_schedule or user_schedule.shift_type != "3_shift":
                continue
            
            if not user_schedule.rotation_start_date or not user_schedule.initial_shift:
                continue
            
            # Pre-calculate rotation parameters
            rotation_start = user_schedule.rotation_start_date
            rotation_monday = rotation_start - timedelta(days=rotation_start.weekday())
            shift_cycle = ["DE", "ÉJ", "DU"]
            initial_index = shift_cycle.index(user_schedule.initial_shift)
            
            # Process all dates for this user
            current_date = start_date
            while current_date <= end_date:
                date_str = current_date.isoformat()
                
                # Check for override first (fast lookup)
                override_key = (user.id, current_date)
                if override_key in override_lookup:
                    shift = override_lookup[override_key]
                else:
                    # Calculate shift from rotation (no DB query needed)
                    target_monday = current_date - timedelta(days=current_date.weekday())
                    days_diff = (target_monday - rotation_monday).days
                    weeks_since_start = days_diff // 7
                    current_shift_index = (initial_index + weeks_since_start) % 3
                    if current_shift_index < 0:
                        current_shift_index += 3
                    shift = shift_cycle[current_shift_index]
                
                if shift:
                    # Check vacation status (fast lookup)
                    is_vacation = False
                    vacation_status = None
                    
                    if date_str in vacation_calendar:
                        vacation_info = vacation_calendar[date_str]
                        if user.id in vacation_info.get("users", []):
                            is_vacation = True
                            # Get status from lookup or calendar
                            vac_key = (user.id, current_date)
                            if vac_key in vacation_request_lookup:
                                vacation_status = vacation_request_lookup[vac_key]
                            else:
                                vacation_status = vacation_info.get("status", "approved")
                    
                    calendar[date_str]["users"].append({
                        "user_id": user.id,
                        "shift": shift,
                        "is_vacation": is_vacation,
                        "vacation_status": vacation_status
                    })
                
                current_date += timedelta(days=1)
        
        return calendar
        
    finally:
        if should_close:
            session.close()

