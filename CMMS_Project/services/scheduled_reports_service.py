"""
Scheduled reports service for automatic report generation and delivery
"""

from typing import Optional, List, Dict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from database.models import ScheduledReport, ReportTemplate, utcnow
from database.session_manager import SessionLocal
from services.excel_export_service import export_reports_to_excel
from services.reports_service import get_all_statistics, get_period_comparison
import logging
import csv
from pathlib import Path

logger = logging.getLogger(__name__)


def create_scheduled_report(
    name: str,
    report_type: str,
    schedule_type: str,
    recipients: List[str],
    created_by_user_id: int,
    schedule_day: Optional[int] = None,
    schedule_time: str = "09:00",
    filters: Optional[Dict] = None,
    template_id: Optional[int] = None,
    format: str = "excel",
    session: Session = None
) -> ScheduledReport:
    """Create a new scheduled report"""
    if session is None:
        session = SessionLocal()
        should_close = True
    else:
        should_close = False
    
    try:
        # Calculate next run time
        next_run = _calculate_next_run_time(schedule_type, schedule_day, schedule_time)
        
        report = ScheduledReport(
            name=name,
            report_type=report_type,
            schedule_type=schedule_type,
            schedule_day=schedule_day,
            schedule_time=schedule_time,
            recipients=recipients or [],
            filters=filters or {},
            template_id=template_id,
            format=format,
            next_run_at=next_run,
            created_by_user_id=created_by_user_id,
            is_active=True
        )
        
        session.add(report)
        session.commit()
        logger.info(f"Created scheduled report: {name}")
        return report
    
    finally:
        if should_close:
            session.close()


def list_scheduled_reports(active_only: bool = False, session: Session = None) -> List[ScheduledReport]:
    """List all scheduled reports"""
    if session is None:
        session = SessionLocal()
        should_close = True
    else:
        should_close = False
    
    try:
        query = session.query(ScheduledReport)
        if active_only:
            query = query.filter(ScheduledReport.is_active == True)
        return query.order_by(ScheduledReport.next_run_at).all()
    
    finally:
        if should_close:
            session.close()


def get_due_reports(session: Session = None) -> List[ScheduledReport]:
    """Get reports that are due to run"""
    if session is None:
        session = SessionLocal()
        should_close = True
    else:
        should_close = False
    
    try:
        now = utcnow()
        return session.query(ScheduledReport).filter(
            and_(
                ScheduledReport.is_active == True,
                ScheduledReport.next_run_at <= now
            )
        ).all()
    
    finally:
        if should_close:
            session.close()


def run_scheduled_report(report_id: int, session: Session = None) -> Optional[Path]:
    """Run a scheduled report and generate the file"""
    if session is None:
        session = SessionLocal()
        should_close = True
    else:
        should_close = False
    
    try:
        report = session.query(ScheduledReport).filter_by(id=report_id).first()
        if not report:
            raise ValueError(f"Scheduled report {report_id} not found")
        
        if not report.is_active:
            logger.warning(f"Scheduled report {report_id} is not active")
            return None
        
        # Generate report based on type
        filters = report.filters or {}
        periods = filters.get('periods', ['month'])
        user_id = filters.get('user_id')
        
        if report.format == "csv":
            output_path = _generate_csv_report(report, periods, user_id)
        else:
            # Excel format
            output_path = export_reports_to_excel(
                periods=periods,
                user_id=user_id,
                output_path=None  # Auto-generate path
            )
        
        # Update last run and calculate next run
        report.last_run_at = utcnow()
        report.next_run_at = _calculate_next_run_time(
            report.schedule_type,
            report.schedule_day,
            report.schedule_time
        )
        session.commit()
        
        logger.info(f"Generated scheduled report {report_id}: {output_path}")
        return output_path
    
    finally:
        if should_close:
            session.close()


def _generate_csv_report(report: ScheduledReport, periods: List[str], user_id: Optional[int]) -> Path:
    """Generate CSV report"""
    output_dir = Path("generated_reports")
    output_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"report_{report.id}_{timestamp}.csv"
    
    # Get statistics
    stats = get_period_comparison(periods, user_id)
    
    # Write CSV
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow(['Period', 'Total Cost', 'Total Time (hours)', 'Total Tasks'])
        
        # Data rows
        for period in periods:
            period_stats = stats.get(period, {})
            cost = period_stats.get('cost', {}).get('total_cost', 0)
            time = period_stats.get('time', {}).get('total_time_hours', 0)
            tasks = period_stats.get('tasks', {}).get('total_tasks', 0)
            writer.writerow([period, cost, time, tasks])
    
    return output_path


def _calculate_next_run_time(schedule_type: str, schedule_day: Optional[int], schedule_time: str) -> datetime:
    """Calculate next run time for scheduled report"""
    now = utcnow()
    if isinstance(now, datetime):
        current_time = now
    else:
        current_time = datetime.now()
    
    # Parse schedule time
    try:
        hour, minute = map(int, schedule_time.split(':'))
    except:
        hour, minute = 9, 0
    
    if schedule_type == "daily":
        next_run = current_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if next_run <= current_time:
            next_run += timedelta(days=1)
    
    elif schedule_type == "weekly":
        # schedule_day: 0=Monday, 6=Sunday
        days_ahead = (schedule_day or 0) - current_time.weekday()
        if days_ahead < 0:
            days_ahead += 7
        next_run = current_time + timedelta(days=days_ahead)
        next_run = next_run.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if next_run <= current_time:
            next_run += timedelta(days=7)
    
    elif schedule_type == "monthly":
        # schedule_day: day of month (1-31)
        day = schedule_day or 1
        next_run = current_time.replace(day=day, hour=hour, minute=minute, second=0, microsecond=0)
        if next_run <= current_time:
            # Move to next month
            if next_run.month == 12:
                next_run = next_run.replace(year=next_run.year + 1, month=1)
            else:
                next_run = next_run.replace(month=next_run.month + 1)
    
    elif schedule_type == "yearly":
        # schedule_day: day of year (1-365)
        day = schedule_day or 1
        next_run = current_time.replace(month=1, day=day, hour=hour, minute=minute, second=0, microsecond=0)
        if next_run <= current_time:
            next_run = next_run.replace(year=next_run.year + 1)
    
    else:
        # Default: daily
        next_run = current_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if next_run <= current_time:
            next_run += timedelta(days=1)
    
    return next_run


def update_scheduled_report(
    report_id: int,
    name: Optional[str] = None,
    schedule_type: Optional[str] = None,
    schedule_day: Optional[int] = None,
    schedule_time: Optional[str] = None,
    recipients: Optional[List[str]] = None,
    filters: Optional[Dict] = None,
    is_active: Optional[bool] = None,
    session: Session = None
) -> ScheduledReport:
    """Update a scheduled report"""
    if session is None:
        session = SessionLocal()
        should_close = True
    else:
        should_close = False
    
    try:
        report = session.query(ScheduledReport).filter_by(id=report_id).first()
        if not report:
            raise ValueError(f"Scheduled report {report_id} not found")
        
        if name is not None:
            report.name = name
        if schedule_type is not None:
            report.schedule_type = schedule_type
        if schedule_day is not None:
            report.schedule_day = schedule_day
        if schedule_time is not None:
            report.schedule_time = schedule_time
        if recipients is not None:
            report.recipients = recipients
        if filters is not None:
            report.filters = filters
        if is_active is not None:
            report.is_active = is_active
        
        # Recalculate next run if schedule changed
        if schedule_type is not None or schedule_day is not None or schedule_time is not None:
            report.next_run_at = _calculate_next_run_time(
                report.schedule_type,
                report.schedule_day,
                report.schedule_time
            )
        
        session.commit()
        logger.info(f"Updated scheduled report: {report_id}")
        return report
    
    finally:
        if should_close:
            session.close()


def delete_scheduled_report(report_id: int, session: Session = None) -> bool:
    """Delete a scheduled report"""
    if session is None:
        session = SessionLocal()
        should_close = True
    else:
        should_close = False
    
    try:
        report = session.query(ScheduledReport).filter_by(id=report_id).first()
        if not report:
            raise ValueError(f"Scheduled report {report_id} not found")
        
        session.delete(report)
        session.commit()
        logger.info(f"Deleted scheduled report: {report_id}")
        return True
    
    finally:
        if should_close:
            session.close()




