"""
Log service for detailed system logging
"""

from typing import Optional, List, Dict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from database.session_manager import SessionLocal
from database.models import SystemLog, utcnow, get_date_categories
from utils.localization_helper import get_localized_error

import logging

logger = logging.getLogger(__name__)


def _get_session(session: Optional[Session]) -> (Session, bool):
    if session is None:
        return SessionLocal(), True
    return session, False


def log_action(
    category: str,
    action_type: str,
    entity_type: str,
    entity_id: Optional[int] = None,
    user_id: Optional[int] = None,
    description: Optional[str] = None,
    metadata: Optional[Dict] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    session: Session = None
) -> SystemLog:
    """
    Create a detailed log entry with extended information
    
    Args:
        category: Log category (document, worksheet, work_request, scrapping, task, assignment, inventory, asset, user)
        action_type: Action type (create, update, delete, generate, assign, complete, scrap)
        entity_type: Entity type (Worksheet, WorkRequest, ScrappingDocument, PMTask, Part, Machine, etc.)
        entity_id: Entity ID
        user_id: User who performed the action
        description: Detailed description
        metadata: Additional information (changes, parameters, etc.)
        ip_address: Client IP address
        user_agent: User agent string
        session: Database session
    
    Returns:
        SystemLog: Created log entry
    """
    session, should_close = _get_session(session)
    try:
        # Get IP and user agent from context if not provided
        if not ip_address:
            from services.context_service import get_client_ip
            ip_address = get_client_ip()
        
        if not user_agent:
            from services.context_service import get_user_agent
            user_agent = get_user_agent()
        
        timestamp = utcnow()
        year, month, week, day = get_date_categories(timestamp)
        
        log_entry = SystemLog(
            log_category=category,
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            description=description,
            log_metadata=metadata or {},
            timestamp=timestamp,
            year=year,
            month=month,
            week=week,
            day=day,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        
        session.add(log_entry)
        session.commit()
        session.refresh(log_entry)
        
        logger.info(f"Log entry created: {category}:{action_type} {entity_type}:{entity_id} by user {user_id}")
        return log_entry
    except Exception as e:
        session.rollback()
        logger.error(f"Error creating log entry: {e}", exc_info=True)
        raise
    finally:
        if should_close:
            session.close()


def get_logs(
    category: Optional[str] = None,
    entity_type: Optional[str] = None,
    year: Optional[int] = None,
    month: Optional[int] = None,
    week: Optional[int] = None,
    day: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    user_id: Optional[int] = None,
    limit: int = 100,
    offset: int = 0,
    session: Session = None
) -> List[SystemLog]:
    """
    Get logs with filtering options
    
    Args:
        category: Filter by log category
        entity_type: Filter by entity type
        year: Filter by year
        month: Filter by month (1-12)
        week: Filter by ISO week number
        day: Filter by day of month
        start_date: Filter by start date
        end_date: Filter by end date
        user_id: Filter by user ID
        limit: Maximum number of results
        offset: Offset for pagination
        session: Database session
    
    Returns:
        List[SystemLog]: List of log entries
    """
    session, should_close = _get_session(session)
    try:
        from sqlalchemy.orm import joinedload
        
        query = session.query(SystemLog).options(joinedload(SystemLog.user))
        
        # Apply filters
        if category:
            query = query.filter(SystemLog.log_category == category)
        if entity_type:
            query = query.filter(SystemLog.entity_type == entity_type)
        if year:
            query = query.filter(SystemLog.year == year)
        if month:
            query = query.filter(SystemLog.month == month)
        if week:
            query = query.filter(SystemLog.week == week)
        if day:
            query = query.filter(SystemLog.day == day)
        if start_date:
            query = query.filter(SystemLog.timestamp >= start_date)
        if end_date:
            query = query.filter(SystemLog.timestamp <= end_date)
        if user_id:
            query = query.filter(SystemLog.user_id == user_id)
        
        # Order by timestamp descending (newest first)
        query = query.order_by(desc(SystemLog.timestamp))
        
        # Apply pagination
        query = query.offset(offset).limit(limit)
        
        return query.all()
    finally:
        if should_close:
            session.close()


def archive_old_logs(archive_years: int, session: Session = None) -> int:
    """
    Archive old logs (move to archive table or export to JSON files)
    
    Args:
        archive_years: Archive logs older than this many years
        session: Database session
    
    Returns:
        int: Number of archived logs
    """
    session, should_close = _get_session(session)
    try:
        cutoff_date = utcnow() - timedelta(days=archive_years * 365)
        
        # Get logs to archive
        logs_to_archive = session.query(SystemLog).filter(
            SystemLog.timestamp < cutoff_date
        ).all()
        
        count = len(logs_to_archive)
        
        if count > 0:
            # TODO: Implement actual archiving (export to JSON files or move to archive table)
            # For now, we'll just mark them or export them
            logger.info(f"Archiving {count} log entries older than {archive_years} years")
            
            # Export to JSON file (simple implementation)
            import json
            from pathlib import Path
            from config.app_config import PROJECT_ROOT
            
            archive_dir = PROJECT_ROOT / "archived_logs"
            archive_dir.mkdir(exist_ok=True)
            
            archive_file = archive_dir / f"logs_archive_{cutoff_date.strftime('%Y%m%d')}.json"
            
            archived_data = []
            for log in logs_to_archive:
                archived_data.append({
                    'id': log.id,
                    'log_category': log.log_category,
                    'action_type': log.action_type,
                    'entity_type': log.entity_type,
                    'entity_id': log.entity_id,
                    'user_id': log.user_id,
                    'description': log.description,
                    'log_metadata': log.log_metadata,
                    'timestamp': log.timestamp.isoformat() if log.timestamp else None,
                    'year': log.year,
                    'month': log.month,
                    'week': log.week,
                    'day': log.day,
                })
            
            with open(archive_file, 'w', encoding='utf-8') as f:
                json.dump(archived_data, f, indent=2, ensure_ascii=False)
            
            # Delete archived logs from main table
            session.query(SystemLog).filter(
                SystemLog.timestamp < cutoff_date
            ).delete()
            session.commit()
            
            logger.info(f"Archived {count} log entries to {archive_file}")
        
        return count
    except Exception as e:
        session.rollback()
        logger.error(f"Error archiving logs: {e}", exc_info=True)
        raise
    finally:
        if should_close:
            session.close()


def delete_old_logs(delete_years: int, session: Session = None) -> int:
    """
    Delete old logs permanently
    
    Args:
        delete_years: Delete logs older than this many years
        session: Database session
    
    Returns:
        int: Number of deleted logs
    """
    session, should_close = _get_session(session)
    try:
        cutoff_date = utcnow() - timedelta(days=delete_years * 365)
        
        # Count logs to delete
        count = session.query(SystemLog).filter(
            SystemLog.timestamp < cutoff_date
        ).count()
        
        if count > 0:
            # Delete logs
            session.query(SystemLog).filter(
                SystemLog.timestamp < cutoff_date
            ).delete()
            session.commit()
            
            logger.info(f"Deleted {count} log entries older than {delete_years} years")
        
        return count
    except Exception as e:
        session.rollback()
        logger.error(f"Error deleting logs: {e}", exc_info=True)
        raise
    finally:
        if should_close:
            session.close()


def get_log_statistics(year: Optional[int] = None, month: Optional[int] = None, session: Session = None) -> Dict:
    """
    Get statistics about logs
    
    Args:
        year: Filter by year
        month: Filter by month (1-12)
        session: Database session
    
    Returns:
        Dict: Statistics dictionary
    """
    session, should_close = _get_session(session)
    try:
        query = session.query(SystemLog)
        
        if year:
            query = query.filter(SystemLog.year == year)
        if month:
            query = query.filter(SystemLog.month == month)
        
        total_logs = query.count()
        
        # Count by category
        categories = {}
        for log in query.all():
            cat = log.log_category
            categories[cat] = categories.get(cat, 0) + 1
        
        # Count by action type
        actions = {}
        for log in query.all():
            act = log.action_type
            actions[act] = actions.get(act, 0) + 1
        
        # Count by entity type
        entities = {}
        for log in query.all():
            ent = log.entity_type
            entities[ent] = entities.get(ent, 0) + 1
        
        return {
            'total_logs': total_logs,
            'by_category': categories,
            'by_action': actions,
            'by_entity': entities,
        }
    finally:
        if should_close:
            session.close()

