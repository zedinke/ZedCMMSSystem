"""
Asset lifecycle management service
"""

from typing import Optional, Dict, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from database.models import Machine, Worksheet, WorksheetPart, PMHistory, ServiceRecord, utcnow
from database.session_manager import SessionLocal
from services.depreciation_service import calculate_depreciation
import logging

logger = logging.getLogger(__name__)


def get_asset_lifecycle_stats(machine_id: int, session: Session = None) -> Dict:
    """
    Get comprehensive lifecycle statistics for a machine
    
    Returns:
        {
            'purchase_info': {...},
            'depreciation': {...},
            'performance_metrics': {...},
            'maintenance_costs': {...},
            'lifecycle_stage': str
        }
    """
    from database.session_manager import SessionLocal
    if session is None:
        session = SessionLocal()
        should_close = True
    else:
        should_close = False
    
    try:
        machine = session.query(Machine).filter_by(id=machine_id).first()
        if not machine:
            raise ValueError(f"Machine {machine_id} not found")
        
        # Purchase info
        purchase_info = {
            'purchase_date': machine.purchase_date.isoformat() if machine.purchase_date else None,
            'purchase_price': float(machine.purchase_price) if machine.purchase_price else None,
            'supplier': machine.supplier,
            'warranty_expiry': machine.warranty_expiry_date.isoformat() if machine.warranty_expiry_date else None,
            'warranty_active': (
                machine.warranty_expiry_date and 
                machine.warranty_expiry_date > utcnow()
            ) if machine.warranty_expiry_date else False
        }
        
        # Depreciation
        depreciation_data = calculate_depreciation(machine_id, session=session)
        
        # Performance metrics
        performance = get_performance_metrics(machine_id, session=session)
        
        # Maintenance costs
        maintenance_costs = get_maintenance_costs(machine_id, session=session)
        
        # Determine lifecycle stage
        lifecycle_stage = _determine_lifecycle_stage(machine, depreciation_data)
        
        return {
            'purchase_info': purchase_info,
            'depreciation': depreciation_data,
            'performance_metrics': performance,
            'maintenance_costs': maintenance_costs,
            'lifecycle_stage': lifecycle_stage,
            'status': machine.status
        }
    
    finally:
        if should_close:
            session.close()


def get_performance_metrics(machine_id: int, session: Session = None) -> Dict:
    """
    Calculate performance metrics: MTBF, MTTR, Availability
    
    MTBF = Mean Time Between Failures
    MTTR = Mean Time To Repair
    Availability = (Total Time - Downtime) / Total Time
    """
    from database.session_manager import SessionLocal
    if session is None:
        session = SessionLocal()
        should_close = True
    else:
        should_close = False
    
    try:
        machine = session.query(Machine).filter_by(id=machine_id).first()
        if not machine:
            return {}
        
        # Get all worksheets for this machine
        worksheets = session.query(Worksheet).filter_by(machine_id=machine_id).all()
        
        if not worksheets:
            return {
                'mtbf_hours': None,
                'mttr_hours': None,
                'availability_percent': None,
                'total_downtime_hours': 0.0,
                'total_maintenance_events': 0,
                'total_operating_hours': float(machine.operating_hours or 0.0)
            }
        
        # Calculate MTTR (Mean Time To Repair)
        completed_worksheets = [w for w in worksheets if w.status == "Completed" and w.total_downtime_hours]
        if completed_worksheets:
            total_repair_time = sum(w.total_downtime_hours or 0.0 for w in completed_worksheets)
            mttr_hours = total_repair_time / len(completed_worksheets)
        else:
            mttr_hours = None
        
        # Calculate MTBF (Mean Time Between Failures)
        # Assuming each worksheet represents a failure/maintenance event
        if machine.purchase_date:
            purchase_date = machine.purchase_date
            if isinstance(purchase_date, datetime):
                days_since_purchase = (utcnow() - purchase_date).days
            else:
                days_since_purchase = (utcnow().date() - purchase_date).days
            
            if days_since_purchase > 0 and len(worksheets) > 1:
                # MTBF = Operating time / Number of failures
                operating_hours = float(machine.operating_hours or (days_since_purchase * 24))
                mtbf_hours = operating_hours / len(worksheets) if len(worksheets) > 0 else None
            else:
                mtbf_hours = None
        else:
            mtbf_hours = None
        
        # Calculate Availability
        total_downtime = sum(w.total_downtime_hours or 0.0 for w in worksheets)
        operating_hours = float(machine.operating_hours or 0.0)
        if operating_hours > 0:
            availability_percent = ((operating_hours - total_downtime) / operating_hours) * 100
        else:
            availability_percent = None
        
        # Update machine's performance_metrics JSON field
        metrics = {
            'mtbf_hours': round(mtbf_hours, 2) if mtbf_hours else None,
            'mttr_hours': round(mttr_hours, 2) if mttr_hours else None,
            'availability_percent': round(availability_percent, 2) if availability_percent else None,
            'total_downtime_hours': round(total_downtime, 2),
            'total_maintenance_events': len(worksheets),
            'total_operating_hours': round(operating_hours, 2),
            'last_updated': utcnow().isoformat()
        }
        
        machine.performance_metrics = metrics
        session.commit()
        
        return metrics
    
    finally:
        if should_close:
            session.close()


def get_maintenance_costs(machine_id: int, period_years: Optional[float] = None, session: Session = None) -> Dict:
    """Get maintenance costs over time"""
    from database.session_manager import SessionLocal
    if session is None:
        session = SessionLocal()
        should_close = True
    else:
        should_close = False
    
    try:
        # Get worksheet costs
        worksheet_costs = session.query(
            func.sum(WorksheetPart.quantity_used * WorksheetPart.unit_cost_at_time)
        ).join(Worksheet).filter(
            Worksheet.machine_id == machine_id
        ).scalar() or 0.0
        
        # Get PM costs (if tracked)
        pm_costs = 0.0  # Can be extended if PM costs are tracked
        
        # Get service record costs
        service_costs = session.query(
            func.sum(ServiceRecord.service_cost)
        ).filter(
            ServiceRecord.machine_id == machine_id
        ).scalar() or 0.0
        
        total_cost = float(worksheet_costs) + float(pm_costs) + float(service_costs)
        
        # Calculate annual average
        machine = session.query(Machine).filter_by(id=machine_id).first()
        if machine and machine.purchase_date:
            purchase_date = machine.purchase_date
            if isinstance(purchase_date, datetime):
                days_since_purchase = (utcnow() - purchase_date).days
            else:
                days_since_purchase = (utcnow().date() - purchase_date).days
            
            years_since_purchase = days_since_purchase / 365.25
            if years_since_purchase > 0:
                annual_avg_cost = total_cost / years_since_purchase
            else:
                annual_avg_cost = total_cost
        else:
            annual_avg_cost = total_cost
        
        return {
            'total_maintenance_cost': round(total_cost, 2),
            'worksheet_costs': round(float(worksheet_costs), 2),
            'pm_costs': round(float(pm_costs), 2),
            'service_costs': round(float(service_costs), 2),
            'annual_average_cost': round(annual_avg_cost, 2),
            'years_in_service': round(years_since_purchase, 2) if machine and machine.purchase_date else None
        }
    
    finally:
        if should_close:
            session.close()


def _determine_lifecycle_stage(machine: Machine, depreciation_data: Dict) -> str:
    """Determine current lifecycle stage"""
    if machine.status == "Scrapped":
        return "scrapped"
    
    years_depreciated = depreciation_data.get('years_depreciated', 0)
    remaining_years = depreciation_data.get('remaining_years', 0)
    period_years = machine.depreciation_period_years or 10
    
    if years_depreciated < period_years * 0.25:
        return "new"
    elif years_depreciated < period_years * 0.50:
        return "mature"
    elif years_depreciated < period_years * 0.75:
        return "aging"
    else:
        return "end_of_life"




