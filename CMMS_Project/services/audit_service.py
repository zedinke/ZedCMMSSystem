"""
Audit Logging Service
Centralized audit logging for all system actions
"""

from typing import Optional, List, Dict
from datetime import datetime
from sqlalchemy.orm import Session, joinedload

from database.session_manager import SessionLocal
from database.models import AuditLog, User

import logging

logger = logging.getLogger(__name__)


def _get_session(session: Optional[Session] = None) -> tuple:
    """Get database session"""
    if session is not None:
        return session, False
    return SessionLocal(), True


def log_audit(user_id: int, action_type: str, entity_type: str, 
             entity_id: Optional[int] = None, changes: Optional[Dict] = None,
             session: Session = None) -> AuditLog:
    """
    Log an audit event
    
    Args:
        user_id: User who performed the action
        action_type: Type of action (create, update, delete, view, login, logout)
        entity_type: Type of entity (worksheet, machine, part, user, etc.)
        entity_id: ID of the entity (if applicable)
        changes: Dictionary of changes (for update actions)
        session: Database session
    
    Returns:
        AuditLog object
    """
    session, should_close = _get_session(session)
    
    try:
        audit_log = AuditLog(
            user_id=user_id,
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            changes=changes or {},
            timestamp=datetime.utcnow(),
        )
        session.add(audit_log)
        session.commit()
        logger.debug(f"Audit logged: {action_type} on {entity_type} by user {user_id}")
        return audit_log
    except Exception as e:
        logger.error(f"Error logging audit: {e}")
        session.rollback()
        raise
    finally:
        if should_close:
            session.close()


def get_audit_logs(user_id: Optional[int] = None, entity_type: Optional[str] = None,
                   action_type: Optional[str] = None, limit: int = 100,
                   session: Session = None) -> List[AuditLog]:
    """
    Get audit logs with optional filters
    
    Args:
        user_id: Filter by user ID
        entity_type: Filter by entity type
        action_type: Filter by action type
        limit: Maximum number of logs to return
        session: Database session
    
    Returns:
        List of AuditLog objects
    """
    session, should_close = _get_session(session)
    
    try:
        query = session.query(AuditLog).options(
            joinedload(AuditLog.user)
        )
        
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        if entity_type:
            query = query.filter(AuditLog.entity_type == entity_type)
        if action_type:
            query = query.filter(AuditLog.action_type == action_type)
        
        return query.order_by(AuditLog.timestamp.desc()).limit(limit).all()
    finally:
        if should_close:
            session.close()


def get_audit_logs_for_entity(entity_type: str, entity_id: int,
                              session: Session = None) -> List[AuditLog]:
    """
    Get audit logs for a specific entity
    
    Args:
        entity_type: Type of entity
        entity_id: ID of entity
        session: Database session
    
    Returns:
        List of AuditLog objects
    """
    session, should_close = _get_session(session)
    
    try:
        return session.query(AuditLog).filter(
            AuditLog.entity_type == entity_type,
            AuditLog.entity_id == entity_id
        ).order_by(AuditLog.timestamp.desc()).all()
    finally:
        if should_close:
            session.close()

