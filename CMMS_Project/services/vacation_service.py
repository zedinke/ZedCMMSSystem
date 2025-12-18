"""
Vacation Management Service
Handles vacation requests, approvals, calendar data, and workday calculations
"""

from typing import Optional, List, Dict
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from database.session_manager import SessionLocal
from database.models import (
    User, VacationRequest, VacationDocument, utcnow, get_date_categories
)
from services.log_service import log_action
from services.context_service import get_current_user_id

import logging

logger = logging.getLogger(__name__)


class VacationServiceError(Exception):
    """Generic vacation service error"""
    pass


def _get_session(session: Optional[Session]) -> tuple:
    """Get database session, creating one if needed"""
    if session is None:
        return SessionLocal(), True
    return session, False


def calculate_workdays(start_date: datetime, end_date: datetime, user_id: Optional[int] = None, session: Session = None) -> int:
    """
    Calculate number of workdays between two dates (excluding weekends)
    
    Args:
        start_date: Start date (inclusive)
        end_date: End date (inclusive)
        user_id: Optional user ID to get work_days_per_week setting
        session: Database session
    
    Returns:
        Number of workdays
    """
    # Convert to date if datetime
    if isinstance(start_date, datetime):
        start_date = start_date.date()
    if isinstance(end_date, datetime):
        end_date = end_date.date()
    
    # Get user's work days per week setting if provided
    work_days_per_week = 5  # Default: Monday-Friday
    if user_id:
        session, should_close = _get_session(session)
        try:
            user = session.query(User).filter_by(id=user_id).first()
            if user and user.work_days_per_week:
                work_days_per_week = user.work_days_per_week
        except Exception as e:
            logger.warning(f"Error getting user work_days_per_week: {e}")
        finally:
            if should_close:
                session.close()
    
    # Calculate workdays
    current_date = start_date
    workdays = 0
    
    while current_date <= end_date:
        # Check if it's a weekday (Monday=0, Sunday=6)
        weekday = current_date.weekday()
        
        # Count as workday if it's within the work week
        # For 5-day week: Monday-Friday (0-4)
        # For 6-day week: Monday-Saturday (0-5)
        if weekday < work_days_per_week:
            workdays += 1
        
        current_date += timedelta(days=1)
    
    return workdays


def create_vacation_request(
    user_id: int,
    start_date: datetime,
    end_date: datetime,
    vacation_type: str = "annual",
    reason: Optional[str] = None,
    session: Session = None
) -> VacationRequest:
    """
    Create a new vacation request
    
    Args:
        user_id: User ID requesting vacation
        start_date: Start date of vacation
        end_date: End date of vacation
        vacation_type: Type of vacation (annual, child_care, etc.)
        reason: Optional reason for vacation
        session: Database session
    
    Returns:
        Created VacationRequest object
    """
    session, should_close = _get_session(session)
    
    try:
        # Validate dates
        if start_date >= end_date:
            raise VacationServiceError("Start date must be before end date")
        
        # Calculate workdays
        days_count = calculate_workdays(start_date, end_date, user_id, session)
        
        if days_count <= 0:
            raise VacationServiceError("Invalid date range: no workdays found")
        
        # Check if user has enough remaining vacation days
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            raise VacationServiceError("User not found")
        
        remaining_days = user.vacation_days_remaining
        if days_count > remaining_days:
            raise VacationServiceError(f"Insufficient vacation days. Available: {remaining_days}, Requested: {days_count}")
        
        # Check for overlapping requests
        overlapping = session.query(VacationRequest).filter(
            VacationRequest.user_id == user_id,
            VacationRequest.status.in_(["pending", "approved"]),
            or_(
                and_(
                    VacationRequest.start_date <= start_date,
                    VacationRequest.end_date >= start_date
                ),
                and_(
                    VacationRequest.start_date <= end_date,
                    VacationRequest.end_date >= end_date
                ),
                and_(
                    VacationRequest.start_date >= start_date,
                    VacationRequest.end_date <= end_date
                )
            )
        ).first()
        
        if overlapping:
            raise VacationServiceError("Overlapping vacation request already exists")
        
        # Create vacation request
        vacation_request = VacationRequest(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            vacation_type=vacation_type,
            reason=reason,
            status="pending",
            days_count=days_count,
            requested_at=utcnow()
        )
        
        session.add(vacation_request)
        session.commit()
        session.refresh(vacation_request)
        
        # Log action
        try:
            log_action(
                category="vacation",
                action_type="create",
                entity_type="VacationRequest",
                entity_id=vacation_request.id,
                user_id=user_id,
                description=f"Szabadság igénylés létrehozva: {start_date.date()} - {end_date.date()} ({days_count} nap)",
                metadata={
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days_count": days_count,
                    "vacation_type": vacation_type,
                },
                session=session
            )
        except Exception as e:
            logger.warning(f"Error logging vacation request creation: {e}")
        
        # Send notifications to approvers
        try:
            from services.notification_service import notify_vacation_request
            notify_vacation_request(vacation_request.id, session=session)
        except Exception as e:
            logger.warning(f"Error sending vacation request notifications: {e}")
        
        logger.info(f"Vacation request created: {vacation_request.id} for user {user_id}")
        return vacation_request
        
    except Exception as e:
        session.rollback()
        if isinstance(e, VacationServiceError):
            raise
        logger.error(f"Error creating vacation request: {e}")
        raise VacationServiceError(f"Error creating vacation request: {str(e)}")
    finally:
        if should_close:
            session.close()


def approve_vacation_request(
    request_id: int,
    approved_by_user_id: int,
    session: Session = None
) -> VacationRequest:
    """
    Approve a vacation request
    
    Args:
        request_id: Vacation request ID
        approved_by_user_id: User ID approving the request
        session: Database session
    
    Returns:
        Updated VacationRequest object
    """
    session, should_close = _get_session(session)
    
    try:
        vacation_request = session.query(VacationRequest).filter_by(id=request_id).first()
        if not vacation_request:
            raise VacationServiceError("Vacation request not found")
        
        if vacation_request.status != "pending":
            raise VacationServiceError(f"Cannot approve request with status: {vacation_request.status}")
        
        # Update request status
        vacation_request.status = "approved"
        vacation_request.approved_by_user_id = approved_by_user_id
        vacation_request.approved_at = utcnow()
        
        # Update user's used vacation days
        user = session.query(User).filter_by(id=vacation_request.user_id).first()
        if user:
            user.vacation_days_used = (user.vacation_days_used or 0) + vacation_request.days_count
        
        session.commit()
        session.refresh(vacation_request)
        
        # Log action
        try:
            log_action(
                category="vacation",
                action_type="approve",
                entity_type="VacationRequest",
                entity_id=request_id,
                user_id=approved_by_user_id,
                description=f"Szabadság igénylés jóváhagyva: {vacation_request.start_date.date()} - {vacation_request.end_date.date()}",
                metadata={
                    "requested_by_user_id": vacation_request.user_id,
                    "days_count": vacation_request.days_count,
                },
                session=session
            )
        except Exception as e:
            logger.warning(f"Error logging vacation approval: {e}")
        
        # Generate vacation document
        try:
            from services.pdf_service import generate_vacation_document
            generate_vacation_document(request_id, session=session)
        except Exception as e:
            logger.warning(f"Error generating vacation document: {e}")
        
        logger.info(f"Vacation request {request_id} approved by user {approved_by_user_id}")
        return vacation_request
        
    except Exception as e:
        session.rollback()
        if isinstance(e, VacationServiceError):
            raise
        logger.error(f"Error approving vacation request: {e}")
        raise VacationServiceError(f"Error approving vacation request: {str(e)}")
    finally:
        if should_close:
            session.close()


def reject_vacation_request(
    request_id: int,
    approved_by_user_id: int,
    rejection_reason: str,
    session: Session = None
) -> VacationRequest:
    """
    Reject a vacation request
    
    Args:
        request_id: Vacation request ID
        approved_by_user_id: User ID rejecting the request
        rejection_reason: Reason for rejection
        session: Database session
    
    Returns:
        Updated VacationRequest object
    """
    session, should_close = _get_session(session)
    
    try:
        vacation_request = session.query(VacationRequest).filter_by(id=request_id).first()
        if not vacation_request:
            raise VacationServiceError("Vacation request not found")
        
        if vacation_request.status != "pending":
            raise VacationServiceError(f"Cannot reject request with status: {vacation_request.status}")
        
        # Update request status
        vacation_request.status = "rejected"
        vacation_request.approved_by_user_id = approved_by_user_id
        vacation_request.approved_at = utcnow()
        vacation_request.rejection_reason = rejection_reason
        
        session.commit()
        session.refresh(vacation_request)
        
        # Log action
        try:
            log_action(
                category="vacation",
                action_type="reject",
                entity_type="VacationRequest",
                entity_id=request_id,
                user_id=approved_by_user_id,
                description=f"Szabadság igénylés elutasítva: {vacation_request.start_date.date()} - {vacation_request.end_date.date()}",
                metadata={
                    "requested_by_user_id": vacation_request.user_id,
                    "rejection_reason": rejection_reason,
                },
                session=session
            )
        except Exception as e:
            logger.warning(f"Error logging vacation rejection: {e}")
        
        logger.info(f"Vacation request {request_id} rejected by user {approved_by_user_id}")
        return vacation_request
        
    except Exception as e:
        session.rollback()
        if isinstance(e, VacationServiceError):
            raise
        logger.error(f"Error rejecting vacation request: {e}")
        raise VacationServiceError(f"Error rejecting vacation request: {str(e)}")
    finally:
        if should_close:
            session.close()


def get_vacation_requests(
    user_id: Optional[int] = None,
    status: Optional[str] = None,
    year: Optional[int] = None,
    session: Session = None
) -> List[VacationRequest]:
    """
    Get vacation requests with optional filters
    
    Args:
        user_id: Filter by user ID (None = all users)
        status: Filter by status (pending, approved, rejected)
        year: Filter by year
        session: Database session
    
    Returns:
        List of VacationRequest objects
    """
    session, should_close = _get_session(session)
    
    try:
        query = session.query(VacationRequest)
        
        if user_id:
            query = query.filter(VacationRequest.user_id == user_id)
        
        # Only filter by status if status is not None and not empty string
        # None or empty string means "show all statuses"
        if status is not None and status != "":
            query = query.filter(VacationRequest.status == status)
        
        if year:
            query = query.filter(
                VacationRequest.start_date >= datetime(year, 1, 1),
                VacationRequest.start_date < datetime(year + 1, 1, 1)
            )
        
        query = query.order_by(VacationRequest.start_date.desc())
        
        return query.all()
        
    finally:
        if should_close:
            session.close()


def get_vacation_calendar(year: int, session: Session = None) -> Dict[str, Dict]:
    """
    Get vacation calendar data for a year
    Returns a dictionary with date strings as keys and status info as values
    
    Args:
        year: Year to get calendar for
        session: Database session
    
    Returns:
        Dictionary with date strings (YYYY-MM-DD) as keys and status info as values
        Status info: {"status": "free"|"approved"|"pending", "users": [user_ids]}
    """
    session, should_close = _get_session(session)
    
    try:
        # Get all vacation requests for the year
        requests = session.query(VacationRequest).filter(
            VacationRequest.start_date >= datetime(year, 1, 1),
            VacationRequest.start_date < datetime(year + 1, 1, 1)
        ).all()
        
        calendar = {}
        
        # Initialize all dates as "free" (gray)
        current_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        
        while current_date <= end_date:
            date_str = current_date.isoformat()
            calendar[date_str] = {
                "status": "free",
                "users": []
            }
            current_date += timedelta(days=1)
        
        # Process vacation requests
        for request in requests:
            start = request.start_date.date() if isinstance(request.start_date, datetime) else request.start_date
            end = request.end_date.date() if isinstance(request.end_date, datetime) else request.end_date
            
            current = start
            while current <= end:
                date_str = current.isoformat()
                
                if date_str in calendar:
                    # Determine status priority: pending (pink) > approved (green) > free (gray)
                    if request.status == "pending":
                        if calendar[date_str]["status"] == "free":
                            calendar[date_str]["status"] = "pending"
                            calendar[date_str]["users"] = [request.user_id]
                        elif calendar[date_str]["status"] == "approved":
                            # Keep approved but add pending user
                            calendar[date_str]["users"].append(request.user_id)
                        else:
                            # Already pending, add user
                            if request.user_id not in calendar[date_str]["users"]:
                                calendar[date_str]["users"].append(request.user_id)
                    elif request.status == "approved":
                        if calendar[date_str]["status"] == "free":
                            calendar[date_str]["status"] = "approved"
                            calendar[date_str]["users"] = [request.user_id]
                        elif calendar[date_str]["status"] == "pending":
                            # Keep pending status but add approved user
                            if request.user_id not in calendar[date_str]["users"]:
                                calendar[date_str]["users"].append(request.user_id)
                        else:
                            # Already approved, add user
                            if request.user_id not in calendar[date_str]["users"]:
                                calendar[date_str]["users"].append(request.user_id)
                
                current += timedelta(days=1)
        
        return calendar
        
    finally:
        if should_close:
            session.close()


def get_user_vacation_summary(user_id: int, year: Optional[int] = None, session: Session = None) -> Dict:
    """
    Get vacation summary for a user
    
    Args:
        user_id: User ID
        year: Optional year (default: current year)
        session: Database session
    
    Returns:
        Dictionary with summary data
    """
    session, should_close = _get_session(session)
    
    try:
        if year is None:
            year = datetime.now().year
        
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            raise VacationServiceError("User not found")
        
        # Get requests for the year
        requests = get_vacation_requests(user_id=user_id, year=year, session=session)
        
        # Calculate statistics
        approved_requests = [r for r in requests if r.status == "approved"]
        pending_requests = [r for r in requests if r.status == "pending"]
        rejected_requests = [r for r in requests if r.status == "rejected"]
        
        days_used = sum(r.days_count for r in approved_requests)
        days_pending = sum(r.days_count for r in pending_requests)
        
        return {
            "user_id": user_id,
            "year": year,
            "days_per_year": user.vacation_days_per_year or 0,
            "days_used": days_used,
            "days_pending": days_pending,
            "days_remaining": user.vacation_days_remaining,
            "total_requests": len(requests),
            "approved_count": len(approved_requests),
            "pending_count": len(pending_requests),
            "rejected_count": len(rejected_requests),
        }
        
    finally:
        if should_close:
            session.close()


def update_user_vacation_days(
    user_id: int,
    days_per_year: int,
    session: Session = None
) -> User:
    """
    Update user's vacation days per year
    
    Args:
        user_id: User ID
        days_per_year: New vacation days per year
        session: Database session
    
    Returns:
        Updated User object
    """
    session, should_close = _get_session(session)
    
    try:
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            raise VacationServiceError("User not found")
        
        old_days = user.vacation_days_per_year
        user.vacation_days_per_year = days_per_year
        
        session.commit()
        session.refresh(user)
        
        # Log action
        try:
            current_user_id = get_current_user_id()
            log_action(
                category="vacation",
                action_type="update",
                entity_type="User",
                entity_id=user_id,
                user_id=current_user_id,
                description=f"Szabadság napok frissítve: {old_days} -> {days_per_year}",
                metadata={
                    "old_days_per_year": old_days,
                    "new_days_per_year": days_per_year,
                },
                session=session
            )
        except Exception as e:
            logger.warning(f"Error logging vacation days update: {e}")
        
        logger.info(f"Updated vacation days for user {user_id}: {days_per_year}")
        return user
        
    except Exception as e:
        session.rollback()
        if isinstance(e, VacationServiceError):
            raise
        logger.error(f"Error updating vacation days: {e}")
        raise VacationServiceError(f"Error updating vacation days: {str(e)}")
    finally:
        if should_close:
            session.close()

