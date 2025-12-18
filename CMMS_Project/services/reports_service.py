"""
Reports service for generating statistics and reports
"""

from typing import Optional, Dict, List, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from sqlalchemy.orm import joinedload

from database.session_manager import SessionLocal
from database.models import (
    Worksheet, WorksheetPart, PMHistory, PMTask, ServiceRecord, User, Machine
)
from sqlalchemy import distinct, case

import logging
from utils.cache import cached, LRUCache

logger = logging.getLogger(__name__)

# Cache for dashboard statistics (5 minutes TTL)
_stats_cache = LRUCache(max_size=50, default_ttl=300)


def _get_session(session: Optional[Session]) -> (Session, bool):
    if session is None:
        return SessionLocal(), True
    return session, False


def _get_date_range(period: str, user_id: Optional[int] = None) -> Tuple[datetime, datetime]:
    """Get date range for period (day/week/month/year)"""
    now = datetime.utcnow()
    
    if period == "day":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif period == "week":
        # Start of week (Monday)
        days_since_monday = now.weekday()
        start = (now - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=6, hours=23, minutes=59, seconds=59, microseconds=999999)
    elif period == "month":
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        # Last day of month
        if now.month == 12:
            end = now.replace(year=now.year + 1, month=1, day=1) - timedelta(microseconds=1)
        else:
            end = now.replace(month=now.month + 1, day=1) - timedelta(microseconds=1)
        end = end.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif period == "year":
        start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end = now.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)
    else:
        # Default to all time
        start = datetime(2000, 1, 1)
        end = now
    
    return start, end


def get_cost_statistics(period: str = "month", user_id: Optional[int] = None, 
                       machine_id: Optional[int] = None, status: Optional[str] = None,
                       priority: Optional[str] = None, session: Session = None) -> Dict:
    """Get cost statistics for period"""
    session, should_close = _get_session(session)
    try:
        start_date, end_date = _get_date_range(period, user_id)
        
        # Worksheet parts costs
        worksheet_query = session.query(
            func.sum(WorksheetPart.quantity_used * WorksheetPart.unit_cost_at_time).label('total_cost')
        ).join(Worksheet).filter(
            and_(
                Worksheet.created_at >= start_date,
                Worksheet.created_at <= end_date
            )
        )
        if user_id:
            worksheet_query = worksheet_query.filter(Worksheet.assigned_to_user_id == user_id)
        if machine_id:
            worksheet_query = worksheet_query.filter(Worksheet.machine_id == machine_id)
        if status:
            worksheet_query = worksheet_query.filter(Worksheet.status == status)
        # Priority filter - only applies to PM-related worksheets
        if priority:
            # Filter worksheets that are linked to PM tasks with this priority
            worksheet_query = worksheet_query.join(PMHistory, Worksheet.id == PMHistory.worksheet_id).join(
                PMTask, PMHistory.pm_task_id == PMTask.id
            ).filter(PMTask.priority == priority)
        worksheet_cost = worksheet_query.scalar() or 0.0
        
        # Service record costs
        service_query = session.query(
            func.sum(ServiceRecord.service_cost).label('total_cost')
        ).filter(
            and_(
                ServiceRecord.service_date >= start_date,
                ServiceRecord.service_date <= end_date
            )
        )
        if user_id:
            service_query = service_query.filter(ServiceRecord.created_by_user_id == user_id)
        service_cost = service_query.scalar() or 0.0
        
        # Convert Decimal to float if needed
        from decimal import Decimal
        if isinstance(worksheet_cost, Decimal):
            worksheet_cost = float(worksheet_cost)
        if isinstance(service_cost, Decimal):
            service_cost = float(service_cost)
        
        total_cost = float(worksheet_cost) + float(service_cost)
        
        return {
            'period': period,
            'start_date': start_date,
            'end_date': end_date,
            'worksheet_cost': float(worksheet_cost),
            'service_cost': float(service_cost),
            'total_cost': float(total_cost),
            'worksheet_count': _count_worksheets(start_date, end_date, user_id, machine_id, status, priority, session),
        }
    finally:
        if should_close:
            session.close()


def _count_worksheets(start_date: datetime, end_date: datetime, user_id: Optional[int] = None,
                     machine_id: Optional[int] = None, status: Optional[str] = None,
                     priority: Optional[str] = None, session: Session = None) -> int:
    """Helper function to count worksheets with filters"""
    query = session.query(Worksheet).filter(
        and_(
            Worksheet.created_at >= start_date,
            Worksheet.created_at <= end_date
        )
    )
    if user_id:
        query = query.filter(Worksheet.assigned_to_user_id == user_id)
    if machine_id:
        query = query.filter(Worksheet.machine_id == machine_id)
    if status:
        query = query.filter(Worksheet.status == status)
    if priority:
        # Filter by PM task priority - only PM-related worksheets
        query = query.join(PMHistory, Worksheet.id == PMHistory.worksheet_id).join(
            PMTask, PMHistory.pm_task_id == PMTask.id
        ).filter(PMTask.priority == priority)
    return query.count()


def get_time_statistics(period: str = "month", user_id: Optional[int] = None,
                       machine_id: Optional[int] = None, status: Optional[str] = None,
                       priority: Optional[str] = None, session: Session = None) -> Dict:
    """Get time statistics for period"""
    session, should_close = _get_session(session)
    try:
        start_date, end_date = _get_date_range(period, user_id)
        
        # Worksheet downtime
        worksheet_query = session.query(
            func.sum(Worksheet.total_downtime_hours).label('total_downtime')
        ).filter(
            and_(
                Worksheet.created_at >= start_date,
                Worksheet.created_at <= end_date
            )
        )
        if user_id:
            worksheet_query = worksheet_query.filter(Worksheet.assigned_to_user_id == user_id)
        if machine_id:
            worksheet_query = worksheet_query.filter(Worksheet.machine_id == machine_id)
        if status:
            worksheet_query = worksheet_query.filter(Worksheet.status == status)
        if priority:
            # Priority filter only applies to PM-related worksheets
            worksheet_query = worksheet_query.join(PMHistory, Worksheet.id == PMHistory.worksheet_id).join(
                PMTask, PMHistory.pm_task_id == PMTask.id
            ).filter(PMTask.priority == priority)
        worksheet_downtime = worksheet_query.scalar() or 0.0
        
        # PM history duration
        pm_query = session.query(
            func.sum(PMHistory.duration_minutes).label('total_duration')
        ).join(PMTask, PMHistory.pm_task_id == PMTask.id).filter(
            and_(
                PMHistory.executed_date >= start_date,
                PMHistory.executed_date <= end_date
            )
        )
        if user_id:
            pm_query = pm_query.filter(
                or_(
                    PMHistory.assigned_to_user_id == user_id,
                    PMHistory.completed_by_user_id == user_id
                )
            )
        if priority:
            pm_query = pm_query.filter(PMTask.priority == priority)
        pm_duration_minutes = pm_query.scalar() or 0
        
        # Service record duration
        service_query = session.query(
            func.sum(ServiceRecord.service_duration_hours).label('total_duration')
        ).filter(
            and_(
                ServiceRecord.service_date >= start_date,
                ServiceRecord.service_date <= end_date
            )
        )
        if user_id:
            service_query = service_query.filter(ServiceRecord.created_by_user_id == user_id)
        service_duration = service_query.scalar() or 0.0
        
        # Convert Decimal to float if needed
        from decimal import Decimal
        if isinstance(worksheet_downtime, Decimal):
            worksheet_downtime = float(worksheet_downtime)
        if isinstance(pm_duration_minutes, Decimal):
            pm_duration_minutes = float(pm_duration_minutes)
        if isinstance(service_duration, Decimal):
            service_duration = float(service_duration)
        
        pm_duration_hours = float(pm_duration_minutes) / 60.0
        total_time = float(worksheet_downtime) + pm_duration_hours + float(service_duration)
        
        return {
            'period': period,
            'start_date': start_date,
            'end_date': end_date,
            'worksheet_downtime_hours': float(worksheet_downtime),
            'pm_duration_hours': float(pm_duration_hours),
            'service_duration_hours': float(service_duration),
            'total_time_hours': float(total_time),
        }
    finally:
        if should_close:
            session.close()


def get_task_statistics(period: str = "month", user_id: Optional[int] = None,
                       machine_id: Optional[int] = None, status: Optional[str] = None,
                       priority: Optional[str] = None, session: Session = None) -> Dict:
    """Get task statistics for period"""
    session, should_close = _get_session(session)
    try:
        start_date, end_date = _get_date_range(period, user_id)
        
        # Worksheets
        worksheet_query = session.query(Worksheet).filter(
            and_(
                Worksheet.created_at >= start_date,
                Worksheet.created_at <= end_date
            )
        )
        if user_id:
            worksheet_query = worksheet_query.filter(Worksheet.assigned_to_user_id == user_id)
        if machine_id:
            worksheet_query = worksheet_query.filter(Worksheet.machine_id == machine_id)
        if status:
            worksheet_query = worksheet_query.filter(Worksheet.status == status)
        if priority:
            # Priority filter only applies to PM-related worksheets
            worksheet_query = worksheet_query.join(PMHistory, Worksheet.id == PMHistory.worksheet_id).join(
                PMTask, PMHistory.pm_task_id == PMTask.id
            ).filter(PMTask.priority == priority)
        worksheet_count = worksheet_query.count()
        
        # PM tasks completed
        pm_query = session.query(PMHistory).join(PMTask, PMHistory.pm_task_id == PMTask.id).filter(
            and_(
                PMHistory.executed_date >= start_date,
                PMHistory.executed_date <= end_date,
                PMHistory.completion_status == 'completed'
            )
        )
        if user_id:
            pm_query = pm_query.filter(
                or_(
                    PMHistory.assigned_to_user_id == user_id,
                    PMHistory.completed_by_user_id == user_id
                )
            )
        if priority:
            pm_query = pm_query.filter(PMTask.priority == priority)
        pm_count = pm_query.count()
        
        total_tasks = worksheet_count + pm_count
        
        return {
            'period': period,
            'start_date': start_date,
            'end_date': end_date,
            'worksheet_count': worksheet_count,
            'pm_count': pm_count,
            'total_tasks': total_tasks,
        }
    finally:
        if should_close:
            session.close()


def get_all_statistics(period: str = "month", user_id: Optional[int] = None,
                      machine_id: Optional[int] = None, status: Optional[str] = None,
                      priority: Optional[str] = None, session: Session = None) -> Dict:
    """Get all statistics for period (cached for 5 minutes)"""
    # Create cache key
    cache_key = f"stats|{period}|{user_id}|{machine_id}|{status}|{priority}"
    
    # Try to get from cache
    cached_result = _stats_cache.get(cache_key)
    if cached_result is not None:
        logger.debug(f"Returning cached statistics for {cache_key}")
        return cached_result
    
    # Calculate statistics
    result = {
        'cost': get_cost_statistics(period, user_id, machine_id, status, priority, session),
        'time': get_time_statistics(period, user_id, machine_id, status, priority, session),
        'tasks': get_task_statistics(period, user_id, machine_id, status, priority, session),
    }
    
    # Cache for 5 minutes
    _stats_cache.set(cache_key, result, ttl=300)
    return result


def get_period_comparison(periods: List[str], user_id: Optional[int] = None,
                         machine_id: Optional[int] = None, status: Optional[str] = None,
                         priority: Optional[str] = None, session: Session = None) -> Dict:
    """Get statistics for multiple periods for comparison"""
    result = {}
    for period in periods:
        result[period] = get_all_statistics(period, user_id, machine_id, status, priority, session)
    return result


def get_technician_statistics(period: str = "month", session: Session = None) -> List[Dict]:
    """Get statistics grouped by technician/user"""
    session, should_close = _get_session(session)
    try:
        start_date, end_date = _get_date_range(period)
        
        # Get all users who have worksheets, PM histories, or service records in this period
        
        # Get unique user IDs from worksheets
        worksheet_user_ids = session.query(distinct(Worksheet.assigned_to_user_id)).filter(
            and_(
                Worksheet.created_at >= start_date,
                Worksheet.created_at <= end_date
            )
        ).all()
        
        # Get unique user IDs from PM histories
        pm_user_ids = session.query(distinct(PMHistory.completed_by_user_id)).filter(
            and_(
                PMHistory.executed_date >= start_date,
                PMHistory.executed_date <= end_date,
                PMHistory.completion_status == 'completed',
                PMHistory.completed_by_user_id.isnot(None)
            )
        ).all()
        
        # Get unique user IDs from service records
        service_user_ids = session.query(distinct(ServiceRecord.created_by_user_id)).filter(
            and_(
                ServiceRecord.service_date >= start_date,
                ServiceRecord.service_date <= end_date,
                ServiceRecord.created_by_user_id.isnot(None)
            )
        ).all()
        
        # Combine all user IDs
        all_user_ids = set()
        for (user_id,) in worksheet_user_ids:
            if user_id:
                all_user_ids.add(user_id)
        for (user_id,) in pm_user_ids:
            if user_id:
                all_user_ids.add(user_id)
        for (user_id,) in service_user_ids:
            if user_id:
                all_user_ids.add(user_id)
        
        # Get statistics for each user
        result = []
        for uid in all_user_ids:
            user = session.query(User).filter(User.id == uid).first()
            if not user:
                continue
            
            # Get task statistics for this user
            task_stats = get_task_statistics(period=period, user_id=uid, session=session)
            
            # Get time statistics for this user
            time_stats = get_time_statistics(period=period, user_id=uid, session=session)
            
            result.append({
                'user_id': uid,
                'username': user.username,
                'full_name': user.full_name or user.username,
                'tasks_completed': task_stats.get('total_tasks', 0),
                'worksheets_count': task_stats.get('worksheet_count', 0),
                'pm_count': task_stats.get('pm_count', 0),
                'downtime_hours': time_stats.get('worksheet_downtime_hours', 0),
                'pm_hours': time_stats.get('pm_duration_hours', 0),
                'service_hours': time_stats.get('service_duration_hours', 0),
                'total_hours': time_stats.get('total_time_hours', 0),
            })
        
        # Sort by total tasks descending
        result.sort(key=lambda x: x['tasks_completed'], reverse=True)
        
        return result
    finally:
        if should_close:
            session.close()

