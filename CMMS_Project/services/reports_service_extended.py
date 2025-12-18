"""
Extended reports service with filters and detailed analytics
"""

from typing import Optional, Dict, List, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, case
from sqlalchemy.orm import joinedload

from database.session_manager import SessionLocal
from database.models import (
    Worksheet, WorksheetPart, PMHistory, PMTask, ServiceRecord, User, Machine
)
from sqlalchemy import distinct

import logging

logger = logging.getLogger(__name__)


def _get_session(session: Optional[Session]) -> (Session, bool):
    if session is None:
        return SessionLocal(), True
    return session, False


def get_trend_statistics(periods: List[str], user_id: Optional[int] = None, 
                        machine_id: Optional[int] = None, session: Session = None) -> Dict:
    """Get trend statistics across multiple periods"""
    from services.reports_service import get_all_statistics
    
    trends = {}
    for period in periods:
        stats = get_all_statistics(period, user_id, session)
        trends[period] = stats
    
    # Calculate trends (increase/decrease percentages)
    if len(periods) >= 2:
        prev_period = periods[0]
        current_period = periods[-1]
        
        prev_stats = trends.get(prev_period, {})
        current_stats = trends.get(current_period, {})
        
        trends['_comparison'] = {
            'cost_change': _calculate_percentage_change(
                prev_stats.get('cost', {}).get('total_cost', 0),
                current_stats.get('cost', {}).get('total_cost', 0)
            ),
            'time_change': _calculate_percentage_change(
                prev_stats.get('time', {}).get('total_time_hours', 0),
                current_stats.get('time', {}).get('total_time_hours', 0)
            ),
            'tasks_change': _calculate_percentage_change(
                prev_stats.get('tasks', {}).get('total_tasks', 0),
                current_stats.get('tasks', {}).get('total_tasks', 0)
            ),
        }
    
    return trends


def _calculate_percentage_change(old_value: float, new_value: float) -> float:
    """Calculate percentage change between two values"""
    from decimal import Decimal
    
    # Convert Decimal to float if needed
    if isinstance(old_value, Decimal):
        old_value = float(old_value)
    if isinstance(new_value, Decimal):
        new_value = float(new_value)
    
    # Ensure all values are float
    old_value = float(old_value) if old_value else 0.0
    new_value = float(new_value) if new_value else 0.0
    
    if old_value == 0:
        return 100.0 if new_value > 0 else 0.0
    return ((new_value - old_value) / old_value) * 100.0


def get_average_statistics(period: str = "month", user_id: Optional[int] = None, 
                          machine_id: Optional[int] = None, session: Session = None) -> Dict:
    """Get average statistics (average cost per task, average time per task, etc.)"""
    from decimal import Decimal
    from services.reports_service import get_all_statistics
    
    stats = get_all_statistics(period, user_id, session)
    
    task_count = stats.get('tasks', {}).get('total_tasks', 0)
    total_cost = stats.get('cost', {}).get('total_cost', 0)
    total_time = stats.get('time', {}).get('total_time_hours', 0)
    
    # Convert Decimal to float if needed
    if isinstance(total_cost, Decimal):
        total_cost = float(total_cost)
    if isinstance(total_time, Decimal):
        total_time = float(total_time)
    if isinstance(task_count, Decimal):
        task_count = float(task_count)
    
    # Ensure all values are float
    total_cost = float(total_cost) if total_cost else 0.0
    total_time = float(total_time) if total_time else 0.0
    task_count = float(task_count) if task_count else 0.0
    
    averages = {
        'avg_cost_per_task': total_cost / task_count if task_count > 0 else 0.0,
        'avg_time_per_task': total_time / task_count if task_count > 0 else 0.0,
        'avg_cost_per_hour': total_cost / total_time if total_time > 0 else 0.0,
        'tasks_per_day': task_count / _get_days_in_period(period) if _get_days_in_period(period) > 0 else 0.0,
    }
    
    return averages


def _get_days_in_period(period: str) -> int:
    """Get number of days in period"""
    if period == "day":
        return 1
    elif period == "week":
        return 7
    elif period == "month":
        return 30
    elif period == "year":
        return 365
    return 1


def get_machine_statistics(period: str = "month", machine_id: Optional[int] = None, 
                          session: Session = None) -> List[Dict]:
    """Get statistics grouped by machine"""
    session, should_close = _get_session(session)
    try:
        from services.reports_service import _get_date_range
        start_date, end_date = _get_date_range(period)
        
        # Get all machines with worksheets in this period
        query = session.query(Machine).join(Worksheet).filter(
            and_(
                Worksheet.created_at >= start_date,
                Worksheet.created_at <= end_date
            )
        ).distinct()
        
        if machine_id:
            query = query.filter(Machine.id == machine_id)
        
        machines = query.all()
        
        result = []
        for machine in machines:
            # Get worksheet count for this machine
            worksheet_count = session.query(Worksheet).filter(
                and_(
                    Worksheet.machine_id == machine.id,
                    Worksheet.created_at >= start_date,
                    Worksheet.created_at <= end_date
                )
            ).count()
            
            # Get total downtime for this machine
            total_downtime = session.query(
                func.sum(Worksheet.total_downtime_hours)
            ).filter(
                and_(
                    Worksheet.machine_id == machine.id,
                    Worksheet.created_at >= start_date,
                    Worksheet.created_at <= end_date
                )
            ).scalar() or 0.0
            
            # Get total cost for this machine
            total_cost = session.query(
                func.sum(WorksheetPart.quantity_used * WorksheetPart.unit_cost_at_time)
            ).join(Worksheet).filter(
                and_(
                    Worksheet.machine_id == machine.id,
                    Worksheet.created_at >= start_date,
                    Worksheet.created_at <= end_date
                )
            ).scalar() or 0.0
            
            result.append({
                'machine_id': machine.id,
                'machine_name': machine.name,
                'serial_number': machine.serial_number,
                'worksheet_count': worksheet_count,
                'total_downtime_hours': float(total_downtime),
                'total_cost': float(total_cost),
            })
        
        # Sort by worksheet count descending
        result.sort(key=lambda x: x['worksheet_count'], reverse=True)
        
        return result
    finally:
        if should_close:
            session.close()

