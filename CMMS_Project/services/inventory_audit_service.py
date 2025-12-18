"""
Inventory Audit Service - Készletellenőrzés/Leltás szolgáltatások
"""

from typing import Optional, Dict, List, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, asc
from sqlalchemy.orm import joinedload

from database.session_manager import SessionLocal
from database.models import (
    Part, InventoryLevel, StockTransaction, StockBatch, InventoryThreshold,
    Machine, Worksheet, WorksheetPart, PMHistory, ServiceRecord, User, Supplier
)
from services import inventory_service
from services.context_service import get_app_context, get_current_user_id

import logging

logger = logging.getLogger(__name__)


def _get_session(session: Optional[Session]) -> Tuple[Session, bool]:
    """Get database session"""
    if session is None:
        return SessionLocal(), True
    return session, False


def _get_date_range(period: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Tuple[datetime, datetime]:
    """Get date range for period (weekly/monthly/yearly)"""
    now = datetime.utcnow()
    
    if start_date and end_date:
        return start_date, end_date
    
    if period == "weekly":
        # Start of week (Monday)
        days_since_monday = now.weekday()
        start = (now - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=6, hours=23, minutes=59, seconds=59, microseconds=999999)
    elif period == "monthly":
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        # Last day of month
        if now.month == 12:
            end = now.replace(year=now.year + 1, month=1, day=1) - timedelta(microseconds=1)
        else:
            end = now.replace(month=now.month + 1, day=1) - timedelta(microseconds=1)
        end = end.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif period == "yearly":
        start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end = now.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)
    else:
        # Default to all time
        start = datetime(2000, 1, 1)
        end = now
    
    return start, end


def get_inventory_overview(
    period: str = "monthly",
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    machine_id: Optional[int] = None,
    session: Session = None
) -> Dict:
    """Get inventory overview statistics"""
    session, should_close = _get_session(session)
    try:
        period_start, period_end = _get_date_range(period, start_date, end_date)
        
        # Calculate previous period for comparison
        if period == "weekly":
            prev_start = period_start - timedelta(days=7)
            prev_end = period_start - timedelta(microseconds=1)
        elif period == "monthly":
            if period_start.month == 1:
                prev_start = period_start.replace(year=period_start.year - 1, month=12, day=1)
            else:
                prev_start = period_start.replace(month=period_start.month - 1, day=1)
            prev_end = period_start - timedelta(microseconds=1)
        elif period == "yearly":
            prev_start = period_start.replace(year=period_start.year - 1)
            prev_end = period_start - timedelta(microseconds=1)
        else:
            prev_start = period_start
            prev_end = period_end
        
        # Total stock quantity
        total_quantity_query = session.query(func.sum(InventoryLevel.quantity_on_hand))
        if machine_id:
            # Filter parts used by this machine
            parts_used = session.query(WorksheetPart.part_id).join(Worksheet).filter(
                Worksheet.machine_id == machine_id
            ).distinct().subquery()
            total_quantity_query = total_quantity_query.filter(InventoryLevel.part_id.in_(session.query(parts_used.c.part_id)))
        total_quantity = total_quantity_query.scalar() or 0
        
        # Total stock value (FIFO based)
        total_value = 0.0
        parts_query = session.query(Part)
        if machine_id:
            parts_used = session.query(WorksheetPart.part_id).join(Worksheet).filter(
                Worksheet.machine_id == machine_id
            ).distinct().subquery()
            parts_query = parts_query.filter(Part.id.in_(session.query(parts_used.c.part_id)))
        
        for part in parts_query.all():
            inv_level = session.query(InventoryLevel).filter_by(part_id=part.id).first()
            if inv_level and inv_level.quantity_on_hand > 0:
                fifo_cost = inventory_service.get_fifo_cost(part.id, inv_level.quantity_on_hand, session=session)
                total_value += inv_level.quantity_on_hand * fifo_cost
        
        # Active parts count
        active_parts_query = session.query(func.count(Part.id)).join(InventoryLevel).filter(
            InventoryLevel.quantity_on_hand > 0
        )
        if machine_id:
            parts_used = session.query(WorksheetPart.part_id).join(Worksheet).filter(
                Worksheet.machine_id == machine_id
            ).distinct().subquery()
            active_parts_query = active_parts_query.filter(Part.id.in_(session.query(parts_used.c.part_id)))
        active_parts = active_parts_query.scalar() or 0
        
        # Low stock parts count
        low_stock_query = session.query(func.count(Part.id)).join(InventoryLevel).filter(
            and_(
                InventoryLevel.quantity_on_hand > 0,
                InventoryLevel.quantity_on_hand <= Part.safety_stock
            )
        )
        if machine_id:
            parts_used = session.query(WorksheetPart.part_id).join(Worksheet).filter(
                Worksheet.machine_id == machine_id
            ).distinct().subquery()
            low_stock_query = low_stock_query.filter(Part.id.in_(session.query(parts_used.c.part_id)))
        low_stock_parts = low_stock_query.scalar() or 0
        
        # Out of stock parts count
        out_of_stock_query = session.query(func.count(Part.id)).join(InventoryLevel).filter(
            InventoryLevel.quantity_on_hand == 0
        )
        if machine_id:
            parts_used = session.query(WorksheetPart.part_id).join(Worksheet).filter(
                Worksheet.machine_id == machine_id
            ).distinct().subquery()
            out_of_stock_query = out_of_stock_query.filter(Part.id.in_(session.query(parts_used.c.part_id)))
        out_of_stock_parts = out_of_stock_query.scalar() or 0
        
        # Stock change (compare with previous period)
        prev_total_quantity = 0  # Placeholder - would need historical data
        stock_change = total_quantity - prev_total_quantity
        stock_change_percent = (stock_change / prev_total_quantity * 100) if prev_total_quantity > 0 else 0.0
        
        # Top 10 most used parts
        top_used_query = session.query(
            Part.id,
            Part.name,
            Part.sku,
            func.sum(WorksheetPart.quantity_used).label('total_used')
        ).join(WorksheetPart).join(Worksheet).filter(
            and_(
                Worksheet.created_at >= period_start,
                Worksheet.created_at <= period_end
            )
        )
        if machine_id:
            top_used_query = top_used_query.filter(Worksheet.machine_id == machine_id)
        
        top_used = top_used_query.group_by(Part.id, Part.name, Part.sku).order_by(desc('total_used')).limit(10).all()
        
        # Top 10 least used parts
        least_used_query = session.query(
            Part.id,
            Part.name,
            Part.sku,
            func.sum(WorksheetPart.quantity_used).label('total_used')
        ).join(WorksheetPart).join(Worksheet).filter(
            and_(
                Worksheet.created_at >= period_start,
                Worksheet.created_at <= period_end
            )
        )
        if machine_id:
            least_used_query = least_used_query.filter(Worksheet.machine_id == machine_id)
        
        least_used = least_used_query.group_by(Part.id, Part.name, Part.sku).order_by(asc('total_used')).limit(10).all()
        
        return {
            "total_stock_quantity": total_quantity,
            "total_stock_value": total_value,
            "active_parts": active_parts,
            "low_stock_parts": low_stock_parts,
            "out_of_stock_parts": out_of_stock_parts,
            "stock_change": stock_change,
            "stock_change_percent": stock_change_percent,
            "top_used_parts": [
                {
                    "id": p.id,
                    "name": p.name,
                    "sku": p.sku,
                    "total_used": p.total_used
                }
                for p in top_used
            ],
            "least_used_parts": [
                {
                    "id": p.id,
                    "name": p.name,
                    "sku": p.sku,
                    "total_used": p.total_used
                }
                for p in least_used
            ],
            "period_start": period_start,
            "period_end": period_end,
        }
    finally:
        if should_close:
            session.close()


def get_usage_report(
    period: str = "monthly",
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    machine_id: Optional[int] = None,
    part_id: Optional[int] = None,
    session: Session = None
) -> Dict:
    """Get usage report with breakdown by period"""
    session, should_close = _get_session(session)
    try:
        period_start, period_end = _get_date_range(period, start_date, end_date)
        
        # Base query for worksheet parts usage
        usage_query = session.query(
            Part.id,
            Part.name,
            Part.sku,
            Part.unit,
            func.sum(WorksheetPart.quantity_used).label('total_used'),
            func.sum(WorksheetPart.quantity_used * WorksheetPart.unit_cost_at_time).label('total_cost'),
            func.count(Worksheet.id.distinct()).label('worksheet_count')
        ).join(WorksheetPart, Part.id == WorksheetPart.part_id).join(
            Worksheet, WorksheetPart.worksheet_id == Worksheet.id
        ).filter(
            and_(
                Worksheet.created_at >= period_start,
                Worksheet.created_at <= period_end
            )
        )
        
        if machine_id:
            usage_query = usage_query.filter(Worksheet.machine_id == machine_id)
        if part_id:
            usage_query = usage_query.filter(Part.id == part_id)
        
        usage_data = usage_query.group_by(Part.id, Part.name, Part.sku, Part.unit).all()
        
        # Calculate trends (compare with previous period)
        prev_start, prev_end = period_start - (period_end - period_start), period_start - timedelta(microseconds=1)
        
        prev_usage_query = session.query(
            Part.id,
            func.sum(WorksheetPart.quantity_used).label('total_used')
        ).join(WorksheetPart, Part.id == WorksheetPart.part_id).join(
            Worksheet, WorksheetPart.worksheet_id == Worksheet.id
        ).filter(
            and_(
                Worksheet.created_at >= prev_start,
                Worksheet.created_at <= prev_end
            )
        )
        
        if machine_id:
            prev_usage_query = prev_usage_query.filter(Worksheet.machine_id == machine_id)
        if part_id:
            prev_usage_query = prev_usage_query.filter(Part.id == part_id)
        
        prev_usage = {p.id: p.total_used for p in prev_usage_query.group_by(Part.id).all()}
        
        # Build result with trend analysis
        result = []
        for u in usage_data:
            prev_qty = prev_usage.get(u.id, 0) or 0
            current_qty = u.total_used or 0
            
            if prev_qty > 0:
                trend_percent = ((current_qty - prev_qty) / prev_qty) * 100
                if trend_percent > 5:
                    trend = "increasing"
                elif trend_percent < -5:
                    trend = "decreasing"
                else:
                    trend = "stable"
            else:
                trend = "new" if current_qty > 0 else "stable"
                trend_percent = 0.0
            
            # Calculate average monthly usage (if period is not monthly, estimate)
            # Convert Decimal to float for calculations
            current_qty_float = float(current_qty) if current_qty is not None else 0.0
            if period == "monthly":
                avg_monthly = current_qty_float
            elif period == "yearly":
                avg_monthly = current_qty_float / 12.0
            elif period == "weekly":
                avg_monthly = current_qty_float * 4.33  # Approximate
            else:
                avg_monthly = current_qty_float
            
            result.append({
                "part_id": u.id,
                "part_name": u.name,
                "sku": u.sku,
                "unit": u.unit,
                "total_used": current_qty,
                "total_cost": float(u.total_cost or 0.0),
                "worksheet_count": u.worksheet_count,
                "trend": trend,
                "trend_percent": trend_percent,
                "avg_monthly_usage": avg_monthly,
                "peak_usage": current_qty,  # Simplified - could calculate actual peak
            })
        
        # Usage by machine (if machine_id not specified)
        machine_usage = []
        if not machine_id:
            machine_usage_query = session.query(
                Machine.id,
                Machine.name,
                Machine.serial_number,
                Part.id.label('part_id'),
                Part.name.label('part_name'),
                func.sum(WorksheetPart.quantity_used).label('total_used')
            ).join(Worksheet, Machine.id == Worksheet.machine_id).join(
                WorksheetPart, Worksheet.id == WorksheetPart.worksheet_id
            ).join(Part, WorksheetPart.part_id == Part.id).filter(
                and_(
                    Worksheet.created_at >= period_start,
                    Worksheet.created_at <= period_end
                )
            )
            if part_id:
                machine_usage_query = machine_usage_query.filter(Part.id == part_id)
            
            machine_usage_data = machine_usage_query.group_by(
                Machine.id, Machine.name, Machine.serial_number, Part.id, Part.name
            ).all()
            
            machine_usage = [
                {
                    "machine_id": m.id,
                    "machine_name": m.name,
                    "serial_number": m.serial_number,
                    "part_id": m.part_id,
                    "part_name": m.part_name,
                    "total_used": m.total_used or 0,
                }
                for m in machine_usage_data
            ]
        
        return {
            "period_start": period_start,
            "period_end": period_end,
            "period": period,
            "usage_data": result,
            "machine_usage": machine_usage,
            "total_parts_used": len(result),
            "total_quantity_used": sum(r["total_used"] for r in result),
            "total_cost": sum(r["total_cost"] for r in result),
        }
    finally:
        if should_close:
            session.close()


def get_value_change_report(
    period: str = "monthly",
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    session: Session = None
) -> Dict:
    """Get value change report showing inventory value changes"""
    session, should_close = _get_session(session)
    try:
        period_start, period_end = _get_date_range(period, start_date, end_date)
        
        # Get all parts with inventory
        parts = session.query(Part).join(InventoryLevel).filter(
            InventoryLevel.quantity_on_hand > 0
        ).all()
        
        result = []
        total_initial_value = 0.0
        total_final_value = 0.0
        total_received_value = 0.0
        total_issued_value = 0.0
        
        for part in parts:
            inv_level = session.query(InventoryLevel).filter_by(part_id=part.id).first()
            if not inv_level:
                continue
            
            # Calculate initial value (at period start)
            # For simplicity, use current FIFO cost - in real scenario would need historical data
            initial_qty = inv_level.quantity_on_hand  # Simplified - should query historical
            initial_unit_cost = inventory_service.get_fifo_cost(part.id, initial_qty, session=session)
            initial_value = initial_qty * initial_unit_cost
            
            # Calculate final value (at period end = current)
            final_qty = inv_level.quantity_on_hand
            final_unit_cost = inventory_service.get_fifo_cost(part.id, final_qty, session=session)
            final_value = final_qty * final_unit_cost
            
            # Calculate received value (stock transactions with positive quantity)
            received_txs = session.query(
                func.sum(StockTransaction.quantity).label('total_qty'),
                func.sum(StockTransaction.quantity * StockBatch.unit_price).label('total_value')
            ).join(StockBatch, StockTransaction.id == StockBatch.stock_transaction_id).filter(
                and_(
                    StockTransaction.part_id == part.id,
                    StockTransaction.quantity > 0,
                    StockTransaction.timestamp >= period_start,
                    StockTransaction.timestamp <= period_end
                )
            ).first()
            
            received_qty = received_txs.total_qty or 0
            received_value = float(received_txs.total_value or 0.0)
            
            # Calculate issued value (negative transactions)
            issued_txs = session.query(
                func.sum(func.abs(StockTransaction.quantity)).label('total_qty'),
                func.sum(func.abs(StockTransaction.quantity) * WorksheetPart.unit_cost_at_time).label('total_value')
            ).join(WorksheetPart, StockTransaction.reference_id == WorksheetPart.worksheet_id).filter(
                and_(
                    StockTransaction.part_id == part.id,
                    StockTransaction.quantity < 0,
                    StockTransaction.timestamp >= period_start,
                    StockTransaction.timestamp <= period_end
                )
            ).first()
            
            issued_qty = issued_txs.total_qty or 0
            issued_value = float(issued_txs.total_value or 0.0)
            
            # Value change
            value_change = final_value - initial_value
            value_change_percent = (value_change / initial_value * 100) if initial_value > 0 else 0.0
            
            # Average inventory value
            avg_value = (initial_value + final_value) / 2
            
            # Turnover rate (cost of goods sold / average inventory)
            turnover_rate = (issued_value / avg_value) if avg_value > 0 else 0.0
            
            result.append({
                "part_id": part.id,
                "part_name": part.name,
                "sku": part.sku,
                "initial_quantity": initial_qty,
                "initial_value": initial_value,
                "final_quantity": final_qty,
                "final_value": final_value,
                "value_change": value_change,
                "value_change_percent": value_change_percent,
                "received_quantity": received_qty,
                "received_value": received_value,
                "issued_quantity": issued_qty,
                "issued_value": issued_value,
                "avg_inventory_value": avg_value,
                "turnover_rate": turnover_rate,
            })
            
            total_initial_value += initial_value
            total_final_value += final_value
            total_received_value += received_value
            total_issued_value += issued_value
        
        return {
            "period_start": period_start,
            "period_end": period_end,
            "period": period,
            "parts": result,
            "summary": {
                "total_initial_value": total_initial_value,
                "total_final_value": total_final_value,
                "total_value_change": total_final_value - total_initial_value,
                "total_received_value": total_received_value,
                "total_issued_value": total_issued_value,
                "avg_inventory_value": (total_initial_value + total_final_value) / 2,
                "overall_turnover_rate": (total_issued_value / ((total_initial_value + total_final_value) / 2)) if (total_initial_value + total_final_value) > 0 else 0.0,
            }
        }
    finally:
        if should_close:
            session.close()


def get_stock_quantity_report(
    machine_id: Optional[int] = None,
    include_zero: bool = False,
    session: Session = None
) -> List[Dict]:
    """Get stock quantity report with all part information"""
    session, should_close = _get_session(session)
    try:
        query = session.query(Part).join(InventoryLevel)
        
        if not include_zero:
            query = query.filter(InventoryLevel.quantity_on_hand > 0)
        
        if machine_id:
            # Filter parts used by this machine
            parts_used = session.query(WorksheetPart.part_id).join(Worksheet).filter(
                Worksheet.machine_id == machine_id
            ).distinct().subquery()
            query = query.filter(Part.id.in_(session.query(parts_used.c.part_id)))
        
        parts = query.all()
        
        result = []
        for part in parts:
            inv_level = session.query(InventoryLevel).filter_by(part_id=part.id).first()
            if not inv_level:
                continue
            
            # Get last receipt date
            last_receipt = session.query(StockBatch).filter_by(part_id=part.id).order_by(
                StockBatch.received_date.desc()
            ).first()
            
            # Get last issue date
            last_issue = session.query(StockTransaction).filter(
                and_(
                    StockTransaction.part_id == part.id,
                    StockTransaction.quantity < 0
                )
            ).order_by(StockTransaction.timestamp.desc()).first()
            
            # Determine stock status
            qty = inv_level.quantity_on_hand
            if qty == 0:
                status = "out_of_stock"
            elif qty <= (part.safety_stock or 0):
                status = "low_stock"
            else:
                status = "ok"
            
            # Calculate stock value using FIFO
            fifo_unit_cost = inventory_service.get_fifo_cost(part.id, qty, session=session)
            stock_value = qty * fifo_unit_cost
            
            result.append({
                "part_id": part.id,
                "part_name": part.name,
                "sku": part.sku,
                "category": part.category,
                "current_quantity": qty,
                "safety_stock": part.safety_stock or 0,
                "reorder_quantity": part.reorder_quantity or 0,
                "status": status,
                "location": None,  # Not in current schema
                "supplier_id": part.supplier_id,
                "supplier_name": part.supplier.name if part.supplier else None,
                "buy_price": part.buy_price or 0.0,
                "stock_value": stock_value,
                "fifo_unit_cost": fifo_unit_cost,
                "last_receipt_date": last_receipt.received_date if last_receipt else None,
                "last_issue_date": last_issue.timestamp if last_issue else None,
                "unit": part.unit,
            })
        
        return result
    finally:
        if should_close:
            session.close()


def get_stock_change_report(
    period: str = "monthly",
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    part_id: Optional[int] = None,
    session: Session = None
) -> Dict:
    """Get stock change report showing quantity changes"""
    session, should_close = _get_session(session)
    try:
        period_start, period_end = _get_date_range(period, start_date, end_date)
        
        # Get parts to analyze
        parts_query = session.query(Part)
        if part_id:
            parts_query = parts_query.filter(Part.id == part_id)
        
        parts = parts_query.all()
        
        result = []
        for part in parts:
            inv_level = session.query(InventoryLevel).filter_by(part_id=part.id).first()
            if not inv_level:
                continue
            
            # Initial quantity (simplified - would need historical data)
            initial_qty = inv_level.quantity_on_hand  # Should query historical
            
            # Final quantity (current)
            final_qty = inv_level.quantity_on_hand
            
            # Calculate received quantity
            received_sum = session.query(func.sum(StockTransaction.quantity)).filter(
                and_(
                    StockTransaction.part_id == part.id,
                    StockTransaction.quantity > 0,
                    StockTransaction.timestamp >= period_start,
                    StockTransaction.timestamp <= period_end
                )
            ).scalar() or 0
            
            # Calculate issued quantity
            issued_sum = session.query(func.sum(func.abs(StockTransaction.quantity))).filter(
                and_(
                    StockTransaction.part_id == part.id,
                    StockTransaction.quantity < 0,
                    StockTransaction.timestamp >= period_start,
                    StockTransaction.timestamp <= period_end
                )
            ).scalar() or 0
            
            # Stock change
            qty_change = final_qty - initial_qty
            qty_change_percent = (qty_change / initial_qty * 100) if initial_qty > 0 else 0.0
            
            # Average stock during period
            # Convert Decimal to float for calculations
            initial_qty_float = float(initial_qty) if initial_qty is not None else 0.0
            final_qty_float = float(final_qty) if final_qty is not None else 0.0
            issued_sum_float = float(issued_sum) if issued_sum is not None else 0.0
            avg_stock = (initial_qty_float + final_qty_float) / 2.0
            
            # Stock turnover days (average stock / (issued quantity / days in period))
            days_in_period = (period_end - period_start).days + 1
            if issued_sum_float > 0 and days_in_period > 0:
                daily_usage = issued_sum_float / float(days_in_period)
                turnover_days = (avg_stock / daily_usage) if daily_usage > 0 else 0.0
            else:
                turnover_days = 0.0
            
            result.append({
                "part_id": part.id,
                "part_name": part.name,
                "sku": part.sku,
                "initial_quantity": initial_qty,
                "final_quantity": final_qty,
                "quantity_change": qty_change,
                "quantity_change_percent": qty_change_percent,
                "received_quantity": received_sum,
                "issued_quantity": issued_sum,
                "avg_quantity": avg_stock,
                "turnover_days": turnover_days,
            })
        
        return {
            "period_start": period_start,
            "period_end": period_end,
            "period": period,
            "parts": result,
            "summary": {
                "total_initial_quantity": sum(r["initial_quantity"] for r in result),
                "total_final_quantity": sum(r["final_quantity"] for r in result),
                "total_received": sum(r["received_quantity"] for r in result),
                "total_issued": sum(r["issued_quantity"] for r in result),
            }
        }
    finally:
        if should_close:
            session.close()


def get_machine_usage_trend(
    machine_id: int,
    period: str = "monthly",
    breakdown: str = "monthly",
    session: Session = None
) -> Dict:
    """Get machine usage trend with breakdown by period"""
    session, should_close = _get_session(session)
    try:
        machine = session.query(Machine).filter_by(id=machine_id).first()
        if not machine:
            raise ValueError(f"Machine {machine_id} not found")
        
        period_start, period_end = _get_date_range(period)
        
        # Get all worksheets for this machine in the period
        worksheets = session.query(Worksheet).filter(
            and_(
                Worksheet.machine_id == machine_id,
                Worksheet.created_at >= period_start,
                Worksheet.created_at <= period_end
            )
        ).all()
        
        # Get parts used by this machine
        parts_used_query = session.query(
            Part.id,
            Part.name,
            Part.sku,
            func.sum(WorksheetPart.quantity_used).label('total_used'),
            func.sum(WorksheetPart.quantity_used * WorksheetPart.unit_cost_at_time).label('total_cost')
        ).join(WorksheetPart, Part.id == WorksheetPart.part_id).join(
            Worksheet, WorksheetPart.worksheet_id == Worksheet.id
        ).filter(
            and_(
                Worksheet.machine_id == machine_id,
                Worksheet.created_at >= period_start,
                Worksheet.created_at <= period_end
            )
        ).group_by(Part.id, Part.name, Part.sku).all()
        
        # Breakdown by time periods
        breakdown_data = []
        if breakdown == "monthly":
            current = period_start
            while current <= period_end:
                month_end = (current.replace(month=current.month+1, day=1) - timedelta(days=1)) if current.month < 12 else current.replace(year=current.year+1, month=1, day=1) - timedelta(days=1)
                month_end = min(month_end, period_end)
                
                month_worksheets = [w for w in worksheets if current <= w.created_at <= month_end]
                
                month_parts_query = session.query(
                    Part.id,
                    func.sum(WorksheetPart.quantity_used).label('total_used'),
                    func.sum(WorksheetPart.quantity_used * WorksheetPart.unit_cost_at_time).label('total_cost')
                ).join(WorksheetPart, Part.id == WorksheetPart.part_id).join(
                    Worksheet, WorksheetPart.worksheet_id == Worksheet.id
                ).filter(
                    and_(
                        Worksheet.machine_id == machine_id,
                        Worksheet.created_at >= current,
                        Worksheet.created_at <= month_end
                    )
                ).group_by(Part.id).all()
                
                breakdown_data.append({
                    "period": current.strftime("%Y-%m"),
                    "period_start": current,
                    "period_end": month_end,
                    "quantity_used": sum(p.total_used or 0 for p in month_parts_query),
                    "cost": sum(float(p.total_cost or 0.0) for p in month_parts_query),
                    "worksheet_count": len(month_worksheets),
                })
                
                current = month_end + timedelta(days=1)
        elif breakdown == "weekly":
            current = period_start
            while current <= period_end:
                week_end = min(current + timedelta(days=6), period_end)
                
                week_worksheets = [w for w in worksheets if current <= w.created_at <= week_end]
                
                week_parts_query = session.query(
                    Part.id,
                    func.sum(WorksheetPart.quantity_used).label('total_used'),
                    func.sum(WorksheetPart.quantity_used * WorksheetPart.unit_cost_at_time).label('total_cost')
                ).join(WorksheetPart, Part.id == WorksheetPart.part_id).join(
                    Worksheet, WorksheetPart.worksheet_id == Worksheet.id
                ).filter(
                    and_(
                        Worksheet.machine_id == machine_id,
                        Worksheet.created_at >= current,
                        Worksheet.created_at <= week_end
                    )
                ).group_by(Part.id).all()
                
                breakdown_data.append({
                    "period": f"{current.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}",
                    "period_start": current,
                    "period_end": week_end,
                    "quantity_used": sum(p.total_used or 0 for p in week_parts_query),
                    "cost": sum(float(p.total_cost or 0.0) for p in week_parts_query),
                    "worksheet_count": len(week_worksheets),
                })
                
                current = week_end + timedelta(days=1)
        
        # Analyze trend
        if len(breakdown_data) > 1:
            first_cost = breakdown_data[0]["cost"]
            last_cost = breakdown_data[-1]["cost"]
            if first_cost > 0:
                trend_percent = ((last_cost - first_cost) / first_cost) * 100
                if trend_percent > 5:
                    trend = "increasing"
                elif trend_percent < -5:
                    trend = "decreasing"
                else:
                    trend = "stable"
            else:
                trend = "new" if last_cost > 0 else "stable"
                trend_percent = 0.0
        else:
            trend = "stable"
            trend_percent = 0.0
        
        # Most used parts
        most_used = sorted(parts_used_query, key=lambda x: x.total_used or 0, reverse=True)[:10]
        
        return {
            "machine_id": machine_id,
            "machine_name": machine.name,
            "serial_number": machine.serial_number,
            "period_start": period_start,
            "period_end": period_end,
            "breakdown": breakdown,
            "breakdown_data": breakdown_data,
            "trend": trend,
            "trend_percent": trend_percent,
            "parts_used": [
                {
                    "part_id": p.id,
                    "part_name": p.name,
                    "sku": p.sku,
                    "total_used": p.total_used or 0,
                    "total_cost": float(p.total_cost or 0.0),
                }
                for p in parts_used_query
            ],
            "most_used_parts": [
                {
                    "part_id": p.id,
                    "part_name": p.name,
                    "sku": p.sku,
                    "total_used": p.total_used or 0,
                }
                for p in most_used
            ],
            "total_worksheets": len(worksheets),
            "total_parts_used": len(parts_used_query),
        }
    finally:
        if should_close:
            session.close()


def get_maintenance_trend_report(
    machine_id: Optional[int] = None,
    period: str = "monthly",
    breakdown: str = "monthly",
    session: Session = None
) -> Dict:
    """Get maintenance trend report with MTBF, MTTR, availability"""
    session, should_close = _get_session(session)
    try:
        period_start, period_end = _get_date_range(period)
        
        # Base query for worksheets
        worksheets_query = session.query(Worksheet).filter(
            and_(
                Worksheet.created_at >= period_start,
                Worksheet.created_at <= period_end
            )
        )
        
        if machine_id:
            worksheets_query = worksheets_query.filter(Worksheet.machine_id == machine_id)
        
        worksheets = worksheets_query.all()
        
        # Breakdown by time periods
        breakdown_data = []
        if breakdown == "monthly":
            current = period_start
            while current <= period_end:
                month_end = (current.replace(month=current.month+1, day=1) - timedelta(days=1)) if current.month < 12 else current.replace(year=current.year+1, month=1, day=1) - timedelta(days=1)
                month_end = min(month_end, period_end)
                
                month_worksheets = [w for w in worksheets if current <= w.created_at <= month_end]
                
                # Calculate costs
                month_cost = sum(
                    sum(wp.quantity_used * wp.unit_cost_at_time for wp in w.parts)
                    for w in month_worksheets
                )
                
                # Calculate downtime
                month_downtime = sum(w.total_downtime_hours or 0.0 for w in month_worksheets)
                
                # Count by type (preventive = linked to PMHistory)
                pm_history_worksheet_ids = set(
                    h.worksheet_id for h in session.query(PMHistory.worksheet_id).filter(
                        PMHistory.worksheet_id.isnot(None)
                    ).distinct().all()
                )
                preventive_count = len([w for w in month_worksheets if w.id in pm_history_worksheet_ids])
                corrective_count = len(month_worksheets) - preventive_count
                
                breakdown_data.append({
                    "period": current.strftime("%Y-%m"),
                    "period_start": current,
                    "period_end": month_end,
                    "maintenance_count": len(month_worksheets),
                    "preventive_count": preventive_count,
                    "corrective_count": corrective_count,
                    "maintenance_cost": month_cost,
                    "downtime_hours": month_downtime,
                })
                
                current = month_end + timedelta(days=1)
        elif breakdown == "weekly":
            current = period_start
            while current <= period_end:
                week_end = min(current + timedelta(days=6), period_end)
                
                week_worksheets = [w for w in worksheets if current <= w.created_at <= week_end]
                
                week_cost = sum(
                    sum(wp.quantity_used * wp.unit_cost_at_time for wp in w.parts)
                    for w in week_worksheets
                )
                
                week_downtime = sum(w.total_downtime_hours or 0.0 for w in week_worksheets)
                
                pm_history_worksheet_ids = set(
                    h.worksheet_id for h in session.query(PMHistory.worksheet_id).filter(
                        PMHistory.worksheet_id.isnot(None)
                    ).distinct().all()
                )
                preventive_count = len([w for w in week_worksheets if w.id in pm_history_worksheet_ids])
                corrective_count = len(week_worksheets) - preventive_count
                
                breakdown_data.append({
                    "period": f"{current.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}",
                    "period_start": current,
                    "period_end": week_end,
                    "maintenance_count": len(week_worksheets),
                    "preventive_count": preventive_count,
                    "corrective_count": corrective_count,
                    "maintenance_cost": week_cost,
                    "downtime_hours": week_downtime,
                })
                
                current = week_end + timedelta(days=1)
        
        # Calculate MTBF (Mean Time Between Failures)
        # Simplified: average time between worksheets
        mtbf_hours = 0.0
        if len(worksheets) > 1:
            sorted_worksheets = sorted(worksheets, key=lambda w: w.created_at)
            intervals = []
            for i in range(1, len(sorted_worksheets)):
                interval = (sorted_worksheets[i].created_at - sorted_worksheets[i-1].created_at).total_seconds() / 3600
                intervals.append(interval)
            if intervals:
                mtbf_hours = sum(intervals) / len(intervals)
        
        # Calculate MTTR (Mean Time To Repair)
        # Average downtime per worksheet
        mttr_hours = 0.0
        worksheets_with_downtime = [w for w in worksheets if w.total_downtime_hours and w.total_downtime_hours > 0]
        if worksheets_with_downtime:
            mttr_hours = sum(w.total_downtime_hours for w in worksheets_with_downtime) / len(worksheets_with_downtime)
        
        # Calculate Availability
        # Simplified: (total_time - downtime) / total_time
        total_hours = (period_end - period_start).total_seconds() / 3600
        total_downtime = sum(w.total_downtime_hours or 0.0 for w in worksheets)
        availability_percent = ((total_hours - total_downtime) / total_hours * 100) if total_hours > 0 else 100.0
        
        # Preventive vs Corrective ratio
        pm_history_worksheet_ids = set(
            h.worksheet_id for h in session.query(PMHistory.worksheet_id).filter(
                PMHistory.worksheet_id.isnot(None)
            ).distinct().all()
        )
        preventive_worksheets = [w for w in worksheets if w.id in pm_history_worksheet_ids]
        corrective_worksheets = [w for w in worksheets if w.id not in pm_history_worksheet_ids]
        
        preventive_cost = sum(
            sum(wp.quantity_used * wp.unit_cost_at_time for wp in w.parts)
            for w in preventive_worksheets
        )
        corrective_cost = sum(
            sum(wp.quantity_used * wp.unit_cost_at_time for wp in w.parts)
            for w in corrective_worksheets
        )
        
        return {
            "period_start": period_start,
            "period_end": period_end,
            "breakdown": breakdown,
            "breakdown_data": breakdown_data,
            "summary": {
                "total_maintenances": len(worksheets),
                "preventive_count": len(preventive_worksheets),
                "corrective_count": len(corrective_worksheets),
                "total_cost": preventive_cost + corrective_cost,
                "preventive_cost": preventive_cost,
                "corrective_cost": corrective_cost,
                "total_downtime_hours": total_downtime,
                "mtbf_hours": mtbf_hours,
                "mttr_hours": mttr_hours,
                "availability_percent": availability_percent,
            },
            "machines": [] if machine_id else [
                {
                    "machine_id": m.id,
                    "machine_name": m.name,
                    "serial_number": m.serial_number,
                    "maintenance_count": len([w for w in worksheets if w.machine_id == m.id]),
                }
                for m in session.query(Machine).all()
            ],
        }
    finally:
        if should_close:
            session.close()


# Threshold management functions
def create_threshold(
    part_id: int,
    notification_threshold: float,
    threshold_type: str,
    period: str,
    machine_id: Optional[int] = None,
    intervention_threshold: Optional[float] = None,
    notes: Optional[str] = None,
    session: Session = None
) -> InventoryThreshold:
    """Create a new inventory threshold"""
    session, should_close = _get_session(session)
    try:
        # Get part info for logging
        from database.models import Part
        part = session.query(Part).filter_by(id=part_id).first()
        part_name = part.name if part else f"ID: {part_id}"
        
        threshold = InventoryThreshold(
            part_id=part_id,
            machine_id=machine_id,
            notification_threshold=notification_threshold,
            intervention_threshold=intervention_threshold,
            threshold_type=threshold_type,
            period=period,
            notes=notes,
            is_active=True,
        )
        session.add(threshold)
        session.commit()
        session.refresh(threshold)
        
        # Log action
        from services.log_service import log_action
        from services.context_service import get_current_user_id
        
        user_id = get_current_user_id()
        try:
            log_action(
                category="inventory",
                action_type="create",
                entity_type="InventoryThreshold",
                entity_id=threshold.id,
                user_id=user_id,
                description=f"Készlet limitálási határ létrehozva: {part_name}",
                metadata={
                    "part_id": part_id,
                    "part_name": part_name,
                    "machine_id": machine_id,
                    "threshold_type": threshold_type,
                    "period": period,
                    "notification_threshold": notification_threshold,
                    "intervention_threshold": intervention_threshold,
                    "notes": notes,
                },
                session=session
            )
        except Exception as e:
            logger.warning(f"Error logging threshold creation: {e}")
        
        return threshold
    finally:
        if should_close:
            session.close()


def update_threshold(
    threshold_id: int,
    notification_threshold: Optional[float] = None,
    intervention_threshold: Optional[float] = None,
    is_active: Optional[bool] = None,
    notes: Optional[str] = None,
    session: Session = None
) -> InventoryThreshold:
    """Update an inventory threshold"""
    session, should_close = _get_session(session)
    try:
        threshold = session.query(InventoryThreshold).filter_by(id=threshold_id).first()
        if not threshold:
            raise ValueError(f"Threshold {threshold_id} not found")
        
        # Track changes for logging
        changes = {}
        old_values = {}
        
        if notification_threshold is not None and threshold.notification_threshold != notification_threshold:
            old_values["notification_threshold"] = threshold.notification_threshold
            threshold.notification_threshold = notification_threshold
            changes["notification_threshold"] = notification_threshold
        
        if intervention_threshold is not None and threshold.intervention_threshold != intervention_threshold:
            old_values["intervention_threshold"] = threshold.intervention_threshold
            threshold.intervention_threshold = intervention_threshold
            changes["intervention_threshold"] = intervention_threshold
        
        if is_active is not None and threshold.is_active != is_active:
            old_values["is_active"] = threshold.is_active
            threshold.is_active = is_active
            changes["is_active"] = is_active
        
        if notes is not None and threshold.notes != notes:
            old_values["notes"] = threshold.notes
            threshold.notes = notes
            changes["notes"] = notes
        
        from database.models import utcnow
        threshold.updated_at = utcnow()
        session.commit()
        session.refresh(threshold)
        
        # Log action if there were changes
        if changes:
            from services.log_service import log_action
            from services.context_service import get_current_user_id
            from database.models import Part
            
            part = session.query(Part).filter_by(id=threshold.part_id).first()
            part_name = part.name if part else f"ID: {threshold.part_id}"
            
            user_id = get_current_user_id()
            try:
                log_action(
                    category="inventory",
                    action_type="update",
                    entity_type="InventoryThreshold",
                    entity_id=threshold_id,
                    user_id=user_id,
                    description=f"Készlet limitálási határ módosítva: {part_name}",
                    metadata={
                        "part_id": threshold.part_id,
                        "part_name": part_name,
                        "machine_id": threshold.machine_id,
                        "threshold_type": threshold.threshold_type,
                        "period": threshold.period,
                        "changes": changes,
                        "old_values": old_values,
                    },
                    session=session
                )
            except Exception as e:
                logger.warning(f"Error logging threshold update: {e}")
        
        return threshold
    finally:
        if should_close:
            session.close()


def delete_threshold(threshold_id: int, session: Session = None) -> bool:
    """Delete an inventory threshold"""
    session, should_close = _get_session(session)
    try:
        threshold = session.query(InventoryThreshold).filter_by(id=threshold_id).first()
        if not threshold:
            return False
        
        # Get part info for logging before deletion
        from database.models import Part
        part = session.query(Part).filter_by(id=threshold.part_id).first()
        part_name = part.name if part else f"ID: {threshold.part_id}"
        
        # Store threshold data for logging
        threshold_data = {
            "part_id": threshold.part_id,
            "part_name": part_name,
            "machine_id": threshold.machine_id,
            "threshold_type": threshold.threshold_type,
            "period": threshold.period,
            "notification_threshold": threshold.notification_threshold,
            "intervention_threshold": threshold.intervention_threshold,
            "is_active": threshold.is_active,
            "notes": threshold.notes,
        }
        
        session.delete(threshold)
        session.commit()
        
        # Log action
        from services.log_service import log_action
        from services.context_service import get_current_user_id
        
        user_id = get_current_user_id()
        try:
            log_action(
                category="inventory",
                action_type="delete",
                entity_type="InventoryThreshold",
                entity_id=threshold_id,
                user_id=user_id,
                description=f"Készlet limitálási határ törölve: {part_name}",
                metadata=threshold_data,
                session=session
            )
        except Exception as e:
            logger.warning(f"Error logging threshold deletion: {e}")
        
        return True
    finally:
        if should_close:
            session.close()


def list_thresholds(
    part_id: Optional[int] = None,
    machine_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    session: Session = None
) -> List[InventoryThreshold]:
    """List inventory thresholds"""
    session, should_close = _get_session(session)
    try:
        query = session.query(InventoryThreshold)
        
        if part_id is not None:
            query = query.filter_by(part_id=part_id)
        if machine_id is not None:
            query = query.filter_by(machine_id=machine_id)
        if is_active is not None:
            query = query.filter_by(is_active=is_active)
        
        return query.order_by(InventoryThreshold.created_at.desc()).all()
    finally:
        if should_close:
            session.close()


def check_thresholds(session: Session = None) -> List[Dict]:
    """Check thresholds and return violations"""
    session, should_close = _get_session(session)
    try:
        # TODO: Implement threshold checking logic
        return []
    finally:
        if should_close:
            session.close()


def get_threshold_violations(session: Session = None) -> List[Dict]:
    """Get current threshold violations"""
    session, should_close = _get_session(session)
    try:
        # TODO: Implement threshold violation detection
        return []
    finally:
        if should_close:
            session.close()

