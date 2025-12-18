"""
Depreciation calculation service for asset lifecycle management
"""

from typing import Optional, Dict
from datetime import datetime, date
from sqlalchemy.orm import Session
from database.models import Machine, utcnow
from database.session_manager import SessionLocal
import logging

logger = logging.getLogger(__name__)


def calculate_depreciation(
    machine_id: int,
    as_of_date: Optional[datetime] = None,
    session: Session = None
) -> Dict:
    """
    Calculate depreciation for a machine using the configured method
    
    Returns:
        {
            'current_value': float,
            'depreciation_to_date': float,
            'annual_depreciation': float,
            'years_depreciated': float,
            'remaining_years': float
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
        
        if not machine.purchase_price or machine.purchase_price <= 0:
            return {
                'current_value': 0.0,
                'depreciation_to_date': 0.0,
                'annual_depreciation': 0.0,
                'years_depreciated': 0.0,
                'remaining_years': 0.0
            }
        
        if not machine.purchase_date:
            return {
                'current_value': machine.purchase_price or 0.0,
                'depreciation_to_date': 0.0,
                'annual_depreciation': 0.0,
                'years_depreciated': 0.0,
                'remaining_years': machine.depreciation_period_years or 0.0
            }
        
        as_of = as_of_date or utcnow()
        if isinstance(as_of, datetime):
            as_of_date_obj = as_of.date()
        else:
            as_of_date_obj = as_of
        
        purchase_date_obj = machine.purchase_date
        if isinstance(purchase_date_obj, datetime):
            purchase_date_obj = purchase_date_obj.date()
        
        purchase_price = float(machine.purchase_price)
        salvage_value = float(machine.salvage_value or 0.0)
        period_years = machine.depreciation_period_years or 10
        method = machine.depreciation_method or "linear"
        
        # Calculate years since purchase
        days_diff = (as_of_date_obj - purchase_date_obj).days
        years_depreciated = max(0.0, days_diff / 365.25)
        
        if years_depreciated >= period_years:
            # Fully depreciated
            current_value = salvage_value
            depreciation_to_date = purchase_price - salvage_value
            annual_depreciation = depreciation_to_date / period_years if period_years > 0 else 0.0
        else:
            if method == "linear":
                annual_depreciation = (purchase_price - salvage_value) / period_years
                depreciation_to_date = annual_depreciation * years_depreciated
                current_value = purchase_price - depreciation_to_date
            
            elif method == "declining":
                # Declining balance method
                rate = machine.depreciation_rate or 0.20  # Default 20%
                current_value = purchase_price * ((1 - rate) ** years_depreciated)
                depreciation_to_date = purchase_price - current_value
                annual_depreciation = purchase_price * rate
            
            elif method == "sum_of_years":
                # Sum of years digits method
                total_digits = sum(range(1, period_years + 1))
                remaining_years = period_years - years_depreciated
                if remaining_years > 0:
                    depreciation_rate = remaining_years / total_digits
                    annual_depreciation = (purchase_price - salvage_value) * depreciation_rate
                    depreciation_to_date = purchase_price - (purchase_price - salvage_value) * (remaining_years / total_digits)
                    current_value = purchase_price - depreciation_to_date
                else:
                    current_value = salvage_value
                    depreciation_to_date = purchase_price - salvage_value
                    annual_depreciation = 0.0
            
            else:
                # Default to linear
                annual_depreciation = (purchase_price - salvage_value) / period_years
                depreciation_to_date = annual_depreciation * years_depreciated
                current_value = purchase_price - depreciation_to_date
        
        # Update machine's current_value
        machine.current_value = current_value
        
        return {
            'current_value': round(current_value, 2),
            'depreciation_to_date': round(depreciation_to_date, 2),
            'annual_depreciation': round(annual_depreciation, 2),
            'years_depreciated': round(years_depreciated, 2),
            'remaining_years': max(0.0, period_years - years_depreciated)
        }
    
    finally:
        if should_close:
            session.close()


def update_all_machines_depreciation(session: Session = None):
    """Update depreciation for all machines"""
    from database.session_manager import SessionLocal
    if session is None:
        session = SessionLocal()
        should_close = True
    else:
        should_close = False
    
    try:
        machines = session.query(Machine).filter(
            Machine.purchase_price.isnot(None),
            Machine.purchase_price > 0
        ).all()
        
        updated_count = 0
        for machine in machines:
            try:
                result = calculate_depreciation(machine.id, session=session)
                session.commit()
                updated_count += 1
            except Exception as e:
                logger.error(f"Error calculating depreciation for machine {machine.id}: {e}")
                session.rollback()
        
        logger.info(f"Updated depreciation for {updated_count} machines")
        return updated_count
    
    finally:
        if should_close:
            session.close()




