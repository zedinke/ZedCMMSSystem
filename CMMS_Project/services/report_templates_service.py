"""
Report templates service for custom report configurations
"""

from typing import Optional, List, Dict
from datetime import datetime
from sqlalchemy.orm import Session
from database.models import ReportTemplate, utcnow
from database.session_manager import SessionLocal
import logging

logger = logging.getLogger(__name__)


def create_report_template(
    name: str,
    report_type: str,
    template_config: Dict,
    created_by_user_id: int,
    description: Optional[str] = None,
    is_default: bool = False,
    is_public: bool = False,
    session: Session = None
) -> ReportTemplate:
    """Create a new report template"""
    if session is None:
        session = SessionLocal()
        should_close = True
    else:
        should_close = False
    
    try:
        template = ReportTemplate(
            name=name,
            description=description,
            report_type=report_type,
            template_config=template_config,
            is_default=is_default,
            is_public=is_public,
            created_by_user_id=created_by_user_id
        )
        
        session.add(template)
        
        # If this is set as default, unset other defaults of the same type
        if is_default:
            session.query(ReportTemplate).filter(
                ReportTemplate.report_type == report_type,
                ReportTemplate.id != template.id,
                ReportTemplate.is_default == True
            ).update({'is_default': False})
        
        session.commit()
        logger.info(f"Created report template: {name}")
        return template
    
    finally:
        if should_close:
            session.close()


def list_report_templates(
    report_type: Optional[str] = None,
    user_id: Optional[int] = None,
    include_public: bool = True,
    session: Session = None
) -> List[ReportTemplate]:
    """List report templates"""
    if session is None:
        session = SessionLocal()
        should_close = True
    else:
        should_close = False
    
    try:
        query = session.query(ReportTemplate)
        
        if report_type:
            query = query.filter(ReportTemplate.report_type == report_type)
        
        if user_id:
            if include_public:
                query = query.filter(
                    (ReportTemplate.created_by_user_id == user_id) |
                    (ReportTemplate.is_public == True)
                )
            else:
                query = query.filter(ReportTemplate.created_by_user_id == user_id)
        
        return query.order_by(ReportTemplate.is_default.desc(), ReportTemplate.name).all()
    
    finally:
        if should_close:
            session.close()


def get_report_template(template_id: int, session: Session = None) -> Optional[ReportTemplate]:
    """Get a report template by ID"""
    if session is None:
        session = SessionLocal()
        should_close = True
    else:
        should_close = False
    
    try:
        return session.query(ReportTemplate).filter_by(id=template_id).first()
    
    finally:
        if should_close:
            session.close()


def get_default_template(report_type: str, session: Session = None) -> Optional[ReportTemplate]:
    """Get the default template for a report type"""
    if session is None:
        session = SessionLocal()
        should_close = True
    else:
        should_close = False
    
    try:
        return session.query(ReportTemplate).filter(
            ReportTemplate.report_type == report_type,
            ReportTemplate.is_default == True
        ).first()
    
    finally:
        if should_close:
            session.close()


def update_report_template(
    template_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    template_config: Optional[Dict] = None,
    is_default: Optional[bool] = None,
    is_public: Optional[bool] = None,
    session: Session = None
) -> ReportTemplate:
    """Update a report template"""
    if session is None:
        session = SessionLocal()
        should_close = True
    else:
        should_close = False
    
    try:
        template = session.query(ReportTemplate).filter_by(id=template_id).first()
        if not template:
            raise ValueError(f"Report template {template_id} not found")
        
        if name is not None:
            template.name = name
        if description is not None:
            template.description = description
        if template_config is not None:
            template.template_config = template_config
        if is_public is not None:
            template.is_public = is_public
        if is_default is not None:
            template.is_default = is_default
            # If setting as default, unset other defaults
            if is_default:
                session.query(ReportTemplate).filter(
                    ReportTemplate.report_type == template.report_type,
                    ReportTemplate.id != template_id,
                    ReportTemplate.is_default == True
                ).update({'is_default': False})
        
        session.commit()
        logger.info(f"Updated report template: {template_id}")
        return template
    
    finally:
        if should_close:
            session.close()


def delete_report_template(template_id: int, session: Session = None) -> bool:
    """Delete a report template"""
    if session is None:
        session = SessionLocal()
        should_close = True
    else:
        should_close = False
    
    try:
        template = session.query(ReportTemplate).filter_by(id=template_id).first()
        if not template:
            raise ValueError(f"Report template {template_id} not found")
        
        session.delete(template)
        session.commit()
        logger.info(f"Deleted report template: {template_id}")
        return True
    
    finally:
        if should_close:
            session.close()




