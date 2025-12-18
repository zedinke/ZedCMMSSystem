"""
Service Records service
"""

from typing import Optional, List, Dict
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from database.session_manager import SessionLocal
from database.models import ServiceRecord, Machine, PMHistory, PMTask, Worksheet, User, utcnow
import logging

logger = logging.getLogger(__name__)


class ServiceRecordServiceError(Exception):
    """Service record service error"""
    pass


def _get_session(session: Optional[Session]) -> (Session, bool):
    if session is None:
        return SessionLocal(), True
    return session, False


def create_service_record(
    machine_id: int,
    service_date: datetime,
    service_type: str,
    service_cost: float,
    created_by_user_id: int,
    performed_by: Optional[str] = None,
    technician_name: Optional[str] = None,
    service_duration_hours: Optional[float] = None,
    description: Optional[str] = None,
    notes: Optional[str] = None,
    parts_replaced: Optional[str] = None,
    next_service_date: Optional[datetime] = None,
    session: Session = None
) -> ServiceRecord:
    """Create a new service record"""
    session, should_close = _get_session(session)
    try:
        machine = session.query(Machine).filter_by(id=machine_id).first()
        if not machine:
            raise ServiceRecordServiceError("Machine not found")
        
        service_record = ServiceRecord(
            machine_id=machine_id,
            service_date=service_date,
            service_type=service_type,
            service_cost=service_cost,
            created_by_user_id=created_by_user_id,
            performed_by=performed_by,
            technician_name=technician_name,
            service_duration_hours=service_duration_hours,
            description=description,
            notes=notes,
            parts_replaced=parts_replaced,
            next_service_date=next_service_date,
            created_at=utcnow(),
        )
        session.add(service_record)
        session.commit()
        logger.info(f"Service record created id={service_record.id}")
        return service_record
    finally:
        if should_close:
            session.close()


def get_service_records(
    machine_id: Optional[int] = None,
    session: Session = None
) -> List[ServiceRecord]:
    """Get all service records, optionally filtered by machine"""
    session, should_close = _get_session(session)
    try:
        query = session.query(ServiceRecord).options(
            joinedload(ServiceRecord.machine),
            joinedload(ServiceRecord.created_by_user)
        )
        if machine_id:
            query = query.filter(ServiceRecord.machine_id == machine_id)
        query = query.order_by(ServiceRecord.service_date.desc())
        return query.all()
    finally:
        if should_close:
            session.close()


def get_service_record(service_record_id: int, session: Session = None) -> Optional[ServiceRecord]:
    """Get a specific service record by ID"""
    session, should_close = _get_session(session)
    try:
        return session.query(ServiceRecord).options(
            joinedload(ServiceRecord.machine),
            joinedload(ServiceRecord.created_by_user)
        ).filter_by(id=service_record_id).first()
    finally:
        if should_close:
            session.close()


def update_service_record(
    service_record_id: int,
    service_date: Optional[datetime] = None,
    service_type: Optional[str] = None,
    service_cost: Optional[float] = None,
    performed_by: Optional[str] = None,
    technician_name: Optional[str] = None,
    service_duration_hours: Optional[float] = None,
    description: Optional[str] = None,
    notes: Optional[str] = None,
    parts_replaced: Optional[str] = None,
    next_service_date: Optional[datetime] = None,
    session: Session = None
) -> ServiceRecord:
    """Update a service record"""
    session, should_close = _get_session(session)
    try:
        service_record = session.query(ServiceRecord).filter_by(id=service_record_id).first()
        if not service_record:
            raise ServiceRecordServiceError("Service record not found")
        
        if service_date is not None:
            service_record.service_date = service_date
        if service_type is not None:
            service_record.service_type = service_type
        if service_cost is not None:
            service_record.service_cost = service_cost
        if performed_by is not None:
            service_record.performed_by = performed_by
        if technician_name is not None:
            service_record.technician_name = technician_name
        if service_duration_hours is not None:
            service_record.service_duration_hours = service_duration_hours
        if description is not None:
            service_record.description = description
        if notes is not None:
            service_record.notes = notes
        if parts_replaced is not None:
            service_record.parts_replaced = parts_replaced
        if next_service_date is not None:
            service_record.next_service_date = next_service_date
        
        session.commit()
        logger.info(f"Service record updated id={service_record_id}")
        return service_record
    finally:
        if should_close:
            session.close()


def delete_service_record(service_record_id: int, session: Session = None) -> bool:
    """Delete a service record"""
    session, should_close = _get_session(session)
    try:
        service_record = session.query(ServiceRecord).filter_by(id=service_record_id).first()
        if not service_record:
            raise ServiceRecordServiceError("Service record not found")
        session.delete(service_record)
        session.commit()
        logger.info(f"Service record deleted id={service_record_id}")
        return True
    finally:
        if should_close:
            session.close()


def get_all_service_records_combined(
    machine_id: Optional[int] = None,
    user_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    session: Session = None
) -> List[Dict]:
    """Get all service records combined: ServiceRecord + PMHistory + Worksheet (closed only)
    
    Returns a list of dictionaries with unified structure:
    {
        'type': 'service_record' | 'pm_history' | 'worksheet',
        'id': int,
        'date': datetime,
        'machine_id': int,
        'machine_name': str,
        'user_name': str,
        'description': str,
        'cost': float,
        'duration_hours': float,
        'entity': ServiceRecord | PMHistory | Worksheet (original object)
    }
    """
    session, should_close = _get_session(session)
    try:
        results = []
        
        # 1. Service Records
        service_query = session.query(ServiceRecord).options(
            joinedload(ServiceRecord.machine),
            joinedload(ServiceRecord.created_by_user)
        )
        if machine_id:
            service_query = service_query.filter(ServiceRecord.machine_id == machine_id)
        if user_id:
            service_query = service_query.filter(ServiceRecord.created_by_user_id == user_id)
        if start_date:
            service_query = service_query.filter(ServiceRecord.service_date >= start_date)
        if end_date:
            service_query = service_query.filter(ServiceRecord.service_date <= end_date)
        service_records = service_query.all()
        
        for sr in service_records:
            results.append({
                'type': 'service_record',
                'id': sr.id,
                'date': sr.service_date,
                'machine_id': sr.machine_id,
                'machine_name': sr.machine.name if sr.machine else f"Gép ID: {sr.machine_id}",
                'user_name': sr.created_by_user.full_name if sr.created_by_user and sr.created_by_user.full_name else (sr.created_by_user.username if sr.created_by_user else "-"),
                'description': sr.description or sr.service_type or "-",
                'cost': sr.service_cost or 0.0,
                'duration_hours': sr.service_duration_hours or 0.0,
                'entity': sr
            })
        
        # 2. PM History (completed PM tasks)
        pm_query = session.query(PMHistory).options(
            joinedload(PMHistory.pm_task).joinedload(PMTask.machine),
            joinedload(PMHistory.completed_user)
        ).filter(PMHistory.completion_status == 'completed')
        if machine_id:
            pm_query = pm_query.join(PMTask).filter(PMTask.machine_id == machine_id)
        if user_id:
            pm_query = pm_query.filter(PMHistory.completed_by_user_id == user_id)
        if start_date:
            pm_query = pm_query.filter(PMHistory.executed_date >= start_date)
        if end_date:
            pm_query = pm_query.filter(PMHistory.executed_date <= end_date)
        pm_histories = pm_query.all()
        
        for pmh in pm_histories:
            machine_name = pmh.pm_task.machine.name if pmh.pm_task and pmh.pm_task.machine else "-"
            machine_id_val = pmh.pm_task.machine_id if pmh.pm_task else None
            user_name = pmh.completed_user.full_name if pmh.completed_user and pmh.completed_user.full_name else (pmh.completed_user.username if pmh.completed_user else "-")
            description = pmh.pm_task.task_name if pmh.pm_task else "-"
            duration_hours = (pmh.duration_minutes / 60.0) if pmh.duration_minutes else 0.0
            
            results.append({
                'type': 'pm_history',
                'id': pmh.id,
                'date': pmh.executed_date,
                'machine_id': machine_id_val,
                'machine_name': machine_name,
                'user_name': user_name,
                'description': description,
                'cost': 0.0,  # PM tasks don't have cost directly
                'duration_hours': duration_hours,
                'entity': pmh
            })
        
        # 3. Worksheets (closed only)
        worksheet_query = session.query(Worksheet).options(
            joinedload(Worksheet.machine),
            joinedload(Worksheet.assigned_user)
        ).filter(Worksheet.status == 'Closed')
        if machine_id:
            worksheet_query = worksheet_query.filter(Worksheet.machine_id == machine_id)
        if user_id:
            worksheet_query = worksheet_query.filter(Worksheet.assigned_to_user_id == user_id)
        if start_date:
            worksheet_query = worksheet_query.filter(Worksheet.closed_at >= start_date)
        if end_date:
            worksheet_query = worksheet_query.filter(Worksheet.closed_at <= end_date)
        worksheets = worksheet_query.all()
        
        for ws in worksheets:
            machine_name = ws.machine.name if ws.machine else f"Gép ID: {ws.machine_id}"
            user_name = ws.assigned_user.full_name if ws.assigned_user and ws.assigned_user.full_name else (ws.assigned_user.username if ws.assigned_user else "-")
            description = ws.title or "-"
            # Calculate cost from parts used
            cost = 0.0
            if hasattr(ws, 'parts') and ws.parts:
                for wp in ws.parts:
                    cost += (wp.quantity_used * wp.unit_cost_at_time) if wp.unit_cost_at_time else 0.0
            duration_hours = ws.total_downtime_hours or 0.0
            
            results.append({
                'type': 'worksheet',
                'id': ws.id,
                'date': ws.closed_at or ws.created_at,
                'machine_id': ws.machine_id,
                'machine_name': machine_name,
                'user_name': user_name,
                'description': description,
                'cost': cost,
                'duration_hours': duration_hours,
                'entity': ws
            })
        
        # Sort by date descending (most recent first)
        results.sort(key=lambda x: x['date'] if x['date'] else datetime.min, reverse=True)
        
        return results
    finally:
        if should_close:
            session.close()
