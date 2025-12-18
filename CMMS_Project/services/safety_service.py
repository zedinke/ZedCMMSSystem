"""
Safety and compliance service
"""

from typing import Optional, List, Dict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from database.models import (
    SafetyIncident, LOTOProcedure, SafetyCertification, RiskAssessment,
    Machine, Worksheet, User, utcnow
)
from database.session_manager import SessionLocal
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# Safety Incidents
# ============================================================================

def create_safety_incident(
    incident_type: str,
    severity: str,
    description: str,
    reported_by_user_id: int,
    machine_id: Optional[int] = None,
    user_id: Optional[int] = None,
    incident_date: Optional[datetime] = None,
    location: Optional[str] = None,
    actions_taken: Optional[str] = None,
    session: Session = None
) -> SafetyIncident:
    """Create a new safety incident"""
    if session is None:
        session = SessionLocal()
        should_close = True
    else:
        should_close = False
    
    try:
        incident = SafetyIncident(
            machine_id=machine_id,
            user_id=user_id,
            incident_date=incident_date or utcnow(),
            incident_type=incident_type,
            severity=severity,
            description=description,
            location=location,
            actions_taken=actions_taken,
            status="open",
            reported_by_user_id=reported_by_user_id
        )
        
        session.add(incident)
        session.commit()
        logger.info(f"Created safety incident: {incident_type} ({severity})")
        return incident
    except Exception as e:
        session.rollback()
        logger.error(f"Unexpected error in safety_service.create_safety_incident: {e}", exc_info=True)
        raise
    finally:
        if should_close:
            session.close()


def list_safety_incidents(
    machine_id: Optional[int] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    session: Session = None
) -> List[SafetyIncident]:
    """List safety incidents with filters"""
    if session is None:
        session = SessionLocal()
        should_close = True
    else:
        should_close = False
    
    try:
        query = session.query(SafetyIncident)
        
        if machine_id:
            query = query.filter(SafetyIncident.machine_id == machine_id)
        if severity:
            query = query.filter(SafetyIncident.severity == severity)
        if status:
            query = query.filter(SafetyIncident.status == status)
        if start_date:
            query = query.filter(SafetyIncident.incident_date >= start_date)
        if end_date:
            query = query.filter(SafetyIncident.incident_date <= end_date)
        
        return query.order_by(SafetyIncident.incident_date.desc()).all()
    
    finally:
        if should_close:
            session.close()


def resolve_safety_incident(
    incident_id: int,
    resolved_by_user_id: int,
    actions_taken: Optional[str] = None,
    session: Session = None
) -> SafetyIncident:
    """Resolve a safety incident"""
    if session is None:
        session = SessionLocal()
        should_close = True
    else:
        should_close = False
    
    try:
        incident = session.query(SafetyIncident).filter_by(id=incident_id).first()
        if not incident:
            raise ValueError(f"Safety incident {incident_id} not found")
        
        incident.status = "resolved"
        incident.resolved_at = utcnow()
        incident.resolved_by_user_id = resolved_by_user_id
        if actions_taken:
            incident.actions_taken = actions_taken
        
        session.commit()
        logger.info(f"Resolved safety incident: {incident_id}")
        return incident
    
    finally:
        if should_close:
            session.close()


# ============================================================================
# LOTO Procedures
# ============================================================================

def create_loto_procedure(
    machine_id: int,
    user_id: int,
    lockout_date: Optional[datetime] = None,
    worksheet_id: Optional[int] = None,
    lock_numbers: Optional[List[str]] = None,
    tag_numbers: Optional[List[str]] = None,
    notes: Optional[str] = None,
    session: Session = None
) -> LOTOProcedure:
    """Create a new LOTO procedure"""
    if session is None:
        session = SessionLocal()
        should_close = True
    else:
        should_close = False
    
    try:
        loto = LOTOProcedure(
            machine_id=machine_id,
            worksheet_id=worksheet_id,
            user_id=user_id,
            lockout_date=lockout_date or utcnow(),
            tagout_date=lockout_date or utcnow(),
            status="active",
            lock_numbers=lock_numbers or [],
            tag_numbers=tag_numbers or [],
            notes=notes
        )
        
        session.add(loto)
        session.commit()
        logger.info(f"Created LOTO procedure for machine {machine_id}")
        return loto
    
    finally:
        if should_close:
            session.close()


def release_loto_procedure(
    loto_id: int,
    released_by_user_id: int,
    session: Session = None
) -> LOTOProcedure:
    """Release a LOTO procedure"""
    if session is None:
        session = SessionLocal()
        should_close = True
    else:
        should_close = False
    
    try:
        loto = session.query(LOTOProcedure).filter_by(id=loto_id).first()
        if not loto:
            raise ValueError(f"LOTO procedure {loto_id} not found")
        
        if loto.status != "active":
            raise ValueError(f"LOTO procedure {loto_id} is not active")
        
        loto.status = "released"
        loto.release_date = utcnow()
        loto.released_by_user_id = released_by_user_id
        
        session.commit()
        logger.info(f"Released LOTO procedure: {loto_id}")
        return loto
    
    finally:
        if should_close:
            session.close()


def list_active_loto_procedures(
    machine_id: Optional[int] = None,
    session: Session = None
) -> List[LOTOProcedure]:
    """List active LOTO procedures"""
    if session is None:
        session = SessionLocal()
        should_close = True
    else:
        should_close = False
    
    try:
        query = session.query(LOTOProcedure).filter(LOTOProcedure.status == "active")
        if machine_id:
            query = query.filter(LOTOProcedure.machine_id == machine_id)
        return query.order_by(LOTOProcedure.lockout_date.desc()).all()
    
    finally:
        if should_close:
            session.close()


# ============================================================================
# Safety Certifications
# ============================================================================

def create_safety_certification(
    user_id: int,
    certification_type: str,
    issued_date: datetime,
    issuing_authority: Optional[str] = None,
    expiry_date: Optional[datetime] = None,
    certificate_number: Optional[str] = None,
    file_path: Optional[str] = None,
    notes: Optional[str] = None,
    session: Session = None
) -> SafetyCertification:
    """Create a new safety certification"""
    if session is None:
        session = SessionLocal()
        should_close = True
    else:
        should_close = False
    
    try:
        cert = SafetyCertification(
            user_id=user_id,
            certification_type=certification_type,
            issued_date=issued_date,
            expiry_date=expiry_date,
            issuing_authority=issuing_authority,
            certificate_number=certificate_number,
            file_path=file_path,
            notes=notes
        )
        
        session.add(cert)
        session.commit()
        logger.info(f"Created safety certification: {certification_type} for user {user_id}")
        return cert
    
    finally:
        if should_close:
            session.close()


def list_safety_certifications(
    user_id: Optional[int] = None,
    certification_type: Optional[str] = None,
    expired_only: bool = False,
    expiring_soon: bool = False,
    session: Session = None
) -> List[SafetyCertification]:
    """List safety certifications"""
    if session is None:
        session = SessionLocal()
        should_close = True
    else:
        should_close = False
    
    try:
        query = session.query(SafetyCertification)
        
        if user_id:
            query = query.filter(SafetyCertification.user_id == user_id)
        if certification_type:
            query = query.filter(SafetyCertification.certification_type == certification_type)
        
        certs = query.order_by(SafetyCertification.expiry_date).all()
        
        # Filter by expiration status
        if expired_only:
            certs = [c for c in certs if c.is_expired]
        elif expiring_soon:
            certs = [c for c in certs if c.is_expiring_soon]
        
        return certs
    
    finally:
        if should_close:
            session.close()


def get_expiring_certifications(days: int = 30, session: Session = None) -> List[SafetyCertification]:
    """Get certifications expiring within specified days"""
    if session is None:
        session = SessionLocal()
        should_close = True
    else:
        should_close = False
    
    try:
        cutoff_date = utcnow() + timedelta(days=days)
        return session.query(SafetyCertification).filter(
            and_(
                SafetyCertification.expiry_date.isnot(None),
                SafetyCertification.expiry_date <= cutoff_date,
                SafetyCertification.expiry_date >= utcnow()
            )
        ).order_by(SafetyCertification.expiry_date).all()
    
    finally:
        if should_close:
            session.close()


# ============================================================================
# Risk Assessments
# ============================================================================

def create_risk_assessment(
    machine_id: int,
    assessed_by_user_id: int,
    risk_level: str,
    hazards: List[str],
    controls: List[str],
    assessment_date: Optional[datetime] = None,
    review_date: Optional[datetime] = None,
    notes: Optional[str] = None,
    session: Session = None
) -> RiskAssessment:
    """Create a new risk assessment"""
    if session is None:
        session = SessionLocal()
        should_close = True
    else:
        should_close = False
    
    try:
        assessment = RiskAssessment(
            machine_id=machine_id,
            assessed_by_user_id=assessed_by_user_id,
            assessment_date=assessment_date or utcnow(),
            risk_level=risk_level,
            hazards=hazards,
            controls=controls,
            review_date=review_date,
            notes=notes,
            status="active"
        )
        
        session.add(assessment)
        session.commit()
        logger.info(f"Created risk assessment for machine {machine_id}: {risk_level}")
        return assessment
    
    finally:
        if should_close:
            session.close()


def list_risk_assessments(
    machine_id: Optional[int] = None,
    risk_level: Optional[str] = None,
    status: Optional[str] = None,
    session: Session = None
) -> List[RiskAssessment]:
    """List risk assessments"""
    if session is None:
        session = SessionLocal()
        should_close = True
    else:
        should_close = False
    
    try:
        query = session.query(RiskAssessment)
        
        if machine_id:
            query = query.filter(RiskAssessment.machine_id == machine_id)
        if risk_level:
            query = query.filter(RiskAssessment.risk_level == risk_level)
        if status:
            query = query.filter(RiskAssessment.status == status)
        
        return query.order_by(RiskAssessment.assessment_date.desc()).all()
    
    finally:
        if should_close:
            session.close()


def get_due_for_review_assessments(session: Session = None) -> List[RiskAssessment]:
    """Get risk assessments due for review"""
    if session is None:
        session = SessionLocal()
        should_close = True
    else:
        should_close = False
    
    try:
        return session.query(RiskAssessment).filter(
            and_(
                RiskAssessment.status == "active",
                RiskAssessment.review_date.isnot(None),
                RiskAssessment.review_date <= utcnow()
            )
        ).order_by(RiskAssessment.review_date).all()
    
    finally:
        if should_close:
            session.close()




