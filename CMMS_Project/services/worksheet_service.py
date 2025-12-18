"""
Worksheet service: alap CRUD, státuszkezelés, alkatrész felhasználás
"""

from typing import Optional
from sqlalchemy.orm import Session, joinedload

from config.constants import (
    WORKSHEET_STATUS_OPEN,
    WORKSHEET_STATUS_WAITING,
    WORKSHEET_STATUS_CLOSED,
    WORKSHEET_STATUSES,
    TRANSACTION_TYPE_ISSUED,
)
from database.session_manager import SessionLocal
from database.models import Worksheet, WorksheetPart, Machine, User, PMHistory, PMTask, WorkRequestPDF, utcnow
from sqlalchemy.orm import aliased
from services import inventory_service
from services.transaction_service import transaction
from services.workflow_service import (
    transition_state,
    get_allowed_transitions,
    WorksheetState
)
from utils.localization_helper import get_localized_error
from utils.error_handler import (
    ValidationError,
    BusinessLogicError,
    StateTransitionError,
    NotFoundError,
    CMMSError
)
from utils.pagination import paginate_query, PaginatedResult

import logging

logger = logging.getLogger(__name__)

ALLOWED_TRANSITIONS = {
    WORKSHEET_STATUS_OPEN: {WORKSHEET_STATUS_WAITING, WORKSHEET_STATUS_CLOSED},
    WORKSHEET_STATUS_WAITING: {WORKSHEET_STATUS_CLOSED},
    WORKSHEET_STATUS_CLOSED: set(),
}


class WorksheetServiceError(CMMSError):
    """Worksheet service hiba - backward compatibility"""
    pass


def _get_session(session: Optional[Session]) -> (Session, bool):
    if session is None:
        return SessionLocal(), True
    return session, False


def create_worksheet(machine_id: int, assigned_to_user_id: int, title: str,
                     description: Optional[str] = None, breakdown_time=None, session: Session = None) -> Worksheet:
    """
    Create a new worksheet for maintenance work.
    
    Creates a worksheet (work order) for a machine. The worksheet title is automatically
    formatted using the configured format from settings (includes worksheet ID, user name).
    
    Workflow:
    1. Validates machine and user exist
    2. Creates Worksheet with status "Open"
    3. Formats title with actual worksheet ID
    4. Sends notification to assigned user
    5. Logs action to SystemLog
    
    Args:
        machine_id: ID of the machine this worksheet is for (required).
        assigned_to_user_id: User ID to assign the worksheet to (required).
        title: Worksheet title. If empty, will be auto-generated from settings format.
        description: Detailed description of the work to be done.
        breakdown_time: Time when breakdown occurred (for downtime calculation).
        session: Database session. If None, creates new session.
    
    Returns:
        Worksheet: Created worksheet object with relationships loaded (machine, assigned_user, parts).
    
    Raises:
        NotFoundError: If machine with machine_id not found, or user with assigned_to_user_id not found.
        ValidationError: If validation fails.
    
    Note:
        - Worksheet title is automatically formatted with worksheet ID after creation.
        - Sends notification to assigned user.
        - Logs creation to SystemLog.
    """
    session, should_close = _get_session(session)
    try:
        print(f"[WS] create_worksheet machine_id={machine_id} user={assigned_to_user_id} breakdown={breakdown_time}")
        machine = session.query(Machine).filter_by(id=machine_id).first()
        if not machine:
            raise NotFoundError("Machine", machine_id, user_message=get_localized_error("machine_not_found"))
        user = session.query(User).filter_by(id=assigned_to_user_id).first()
        if not user:
            raise NotFoundError("User", assigned_to_user_id, user_message=get_localized_error("assigned_user_not_found"))
        
        # Always use the format from settings for worksheet title
        from services.settings_service import get_worksheet_name_format
        name_format = get_worksheet_name_format()
        user_name = user.full_name if user.full_name else user.username
        
        # Use temporary title first (will be updated after commit with actual ID)
        temp_title = name_format.format(
            worksheet_name="Munkalap",
            user_name=user_name,
            worksheet_id=0  # Temporary, will be replaced
        )
        
        ws = Worksheet(
            machine_id=machine_id,
            assigned_to_user_id=assigned_to_user_id,
            title=temp_title,
            description=description,
            status=WORKSHEET_STATUS_OPEN,
            breakdown_time=breakdown_time,
            created_at=utcnow(),
        )
        session.add(ws)
        session.commit()  # Commit first to get the ID
        logger.info(f"Worksheet created id={ws.id} title={temp_title}")
        
        # Now format title with actual ID
        final_title = name_format.format(
            worksheet_name="Munkalap",
            user_name=user_name,
            worksheet_id=ws.id
        )
        # Update the title with actual ID
        ws.title = final_title
        session.commit()
        logger.info(f"Worksheet title updated id={ws.id} title={final_title}")
        print(f"[WS] worksheet committed id={ws.id}")
        
        # Send notification about worksheet assignment
        try:
            from services.notification_service import notify_worksheet_assigned
            notify_worksheet_assigned(ws.id, session=session)
        except Exception as e:
            logger.warning(f"Error sending worksheet assignment notification: {e}")
        
        # Log worksheet creation
        from services.log_service import log_action
        from services.context_service import get_current_user_id
        
        user_id = get_current_user_id() or assigned_to_user_id
        try:
            log_action(
                category="worksheet",
                action_type="create",
                entity_type="Worksheet",
                entity_id=ws.id,
                user_id=user_id,
                description=f"Munkalap létrehozva: {final_title}",
                metadata={
                    "worksheet_title": final_title,
                    "machine_id": machine_id,
                    "assigned_to_user_id": assigned_to_user_id,
                    "breakdown_time": breakdown_time.isoformat() if breakdown_time else None,
                },
                session=session
            )
        except Exception as e:
            logger.warning(f"Error logging worksheet creation: {e}")
        
        # Return fully loaded instance so UI can access relationships after session close
        ws_full = (
            session.query(Worksheet)
            .options(
                joinedload(Worksheet.machine),
                joinedload(Worksheet.assigned_user),
                joinedload(Worksheet.parts).joinedload(WorksheetPart.part),
            )
            .filter(Worksheet.id == ws.id)
            .first()
        )
        print(f"[WS] worksheet loaded ws_full={ws_full.id if ws_full else None}")
        return ws_full or ws
    except ValidationError as e:
        session.rollback()
        logger.warning(f"Validation error in worksheet_service.create_worksheet: {e}", exc_info=True)
        raise
    except NotFoundError as e:
        session.rollback()
        logger.warning(f"Not found error in worksheet_service.create_worksheet: {e}", exc_info=True)
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Unexpected error in worksheet_service.create_worksheet: {e}", exc_info=True)
        raise
    finally:
        if should_close:
            session.close()


def update_status(worksheet_id: int, new_status: str, repair_finished_time=None, session: Session = None) -> Worksheet:
    """Update worksheet status with optional repair_finished_time for Closed status"""
    session, should_close = _get_session(session)
    try:
        if new_status not in WORKSHEET_STATUSES:
            raise ValidationError(
                f"Invalid worksheet status: {new_status}",
                field="status",
                user_message=get_localized_error("invalid_worksheet_status")
            )
        ws = session.query(Worksheet).filter_by(id=worksheet_id).first()
        if not ws:
            raise NotFoundError("Worksheet", worksheet_id, user_message=get_localized_error("worksheet_not_found"))
        
        # Use centralized workflow validation
        is_valid, error_msg = transition_state(
            "worksheet",
            ws.status,
            new_status,
            raise_on_error=False
        )
        
        if not is_valid:
            raise StateTransitionError(
                "Worksheet",
                ws.status,
                new_status,
                user_message=get_localized_error("status_transition_not_allowed", old_status=ws.status, new_status=new_status)
            )
        
        old_status = ws.status
        ws.status = new_status
        
        # Log status change if it's different
        if old_status != new_status:
            from services.log_service import log_action
            from services.context_service import get_current_user_id
            from services.notification_service import notify_worksheet_status_change
            
            user_id = get_current_user_id()
            try:
                log_action(
                    category="worksheet",
                    action_type="update",
                    entity_type="Worksheet",
                    entity_id=worksheet_id,
                    user_id=user_id,
                    description=f"Munkalap státusz módosítva: {old_status} → {new_status}",
                    metadata={
                        "worksheet_title": ws.title,
                        "old_status": old_status,
                        "new_status": new_status,
                        "machine_id": ws.machine_id,
                    },
                    session=session
                )
            except Exception as e:
                logger.warning(f"Error logging worksheet status update: {e}")
            
            # Create notification for status change (but not for Closed - that gets special notification)
            try:
                if new_status != WORKSHEET_STATUS_CLOSED:
                    notify_worksheet_status_change(
                        worksheet_id=worksheet_id,
                        old_status=old_status,
                        new_status=new_status,
                        assigned_user_id=ws.assigned_to_user_id,
                        session=session
                    )
            except Exception as e:
                logger.warning(f"Error creating notification: {e}")
        
        # Handle Closed status with downtime calculation and validation (MSZ EN 13460)
        if new_status == WORKSHEET_STATUS_CLOSED:
            # MSZ EN 13460 validation: description and dates are required for closing
            if not ws.description or not ws.description.strip():
                raise ValidationError(
                    "Description is required for closing worksheet",
                    field="description",
                    user_message=get_localized_error("description_required")
                )
            if not ws.breakdown_time:
                raise ValidationError(
                    "Breakdown time is required for closing worksheet",
                    field="breakdown_time",
                    user_message=get_localized_error("breakdown_time_required")
                )
            if not repair_finished_time and not ws.repair_finished_time:
                raise ValidationError(
                    "Repair finished time is required for closing worksheet",
                    field="repair_finished_time",
                    user_message=get_localized_error("repair_finished_time_required")
                )
            # fault_cause is mandatory for MSZ EN 13460 compliance
            if not hasattr(ws, 'fault_cause') or not ws.fault_cause or not ws.fault_cause.strip():
                raise ValidationError(
                    "Fault cause is required for closing worksheet (MSZ EN 13460)",
                    field="fault_cause",
                    user_message=get_localized_error("fault_cause_required")
                )
            
            ws.repair_finished_time = repair_finished_time or ws.repair_finished_time or utcnow()
            ws.closed_at = utcnow()
            # Normalize tz info to avoid naive/aware subtraction
            if ws.breakdown_time and ws.repair_finished_time:
                bdt = ws.breakdown_time
                rdt = ws.repair_finished_time
                if (bdt.tzinfo is None) != (rdt.tzinfo is None):
                    # If one is aware and the other is naive, drop tzinfo from aware to align
                    if bdt.tzinfo is None and rdt.tzinfo is not None:
                        rdt = rdt.replace(tzinfo=None)
                    elif bdt.tzinfo is not None and rdt.tzinfo is None:
                        bdt = bdt.replace(tzinfo=None)
                    ws.breakdown_time = bdt
                    ws.repair_finished_time = rdt
            # Calculate downtime if breakdown_time is set
            if ws.breakdown_time:
                ws.total_downtime_hours = ws.calculate_downtime()
            logger.info(f"Worksheet closed id={worksheet_id}, downtime={ws.total_downtime_hours}h")
            
            # Send notification about worksheet closure
            try:
                from services.notification_service import notify_worksheet_closed
                notify_worksheet_closed(worksheet_id, user_id, session=session)
            except Exception as e:
                logger.warning(f"Error sending worksheet closed notification: {e}")
            
            # Generate scrapping documents for used parts
            from services.settings_service import get_auto_generate_scrapping_doc
            from services.scrapping_service import generate_scrapping_document
            from services.log_service import log_action
            from services.context_service import get_current_user_id
            
            user_id = get_current_user_id()
            
            if get_auto_generate_scrapping_doc() and ws.parts:
                for worksheet_part in ws.parts:
                    if worksheet_part.part:
                        try:
                            generate_scrapping_document(
                                entity_type="Part",
                                entity_id=worksheet_part.part.id,
                                reason=f"Munkalap lezárása - Elhasznált alkatrész (Munkalap #{worksheet_id})",
                                worksheet_id=worksheet_id,
                                session=session
                            )
                        except Exception as e:
                            logger.warning(f"Error generating scrapping document for part {worksheet_part.part.id}: {e}")
            
            # Log worksheet closure
            try:
                log_action(
                    category="worksheet",
                    action_type="complete",
                    entity_type="Worksheet",
                    entity_id=worksheet_id,
                    user_id=user_id,
                    description=f"Munkalap lezárva: {ws.title}",
                    metadata={
                        "worksheet_title": ws.title,
                        "machine_id": ws.machine_id,
                        "downtime_hours": ws.total_downtime_hours,
                        "parts_count": len(ws.parts) if ws.parts else 0,
                    },
                    session=session
                )
            except Exception as e:
                logger.warning(f"Error logging worksheet closure: {e}")
        
        session.commit()
        logger.info(f"Worksheet status updated id={worksheet_id} -> {new_status}")
        # Re-load with relationships eagerly for UI use
        ws_full = (
            session.query(Worksheet)
            .options(
                joinedload(Worksheet.machine),
                joinedload(Worksheet.assigned_user),
                joinedload(Worksheet.parts).joinedload(WorksheetPart.part),
            )
            .filter(Worksheet.id == ws.id)
            .first()
        )
        return ws_full or ws
    except ValidationError as e:
        session.rollback()
        logger.warning(f"Validation error in worksheet_service.update_status: {e}", exc_info=True)
        raise
    except NotFoundError as e:
        session.rollback()
        logger.warning(f"Not found error in worksheet_service.update_status: {e}", exc_info=True)
        raise
    except StateTransitionError as e:
        session.rollback()
        logger.warning(f"State transition error in worksheet_service.update_status: {e}", exc_info=True)
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Unexpected error in worksheet_service.update_status: {e}", exc_info=True)
        raise
    finally:
        if should_close:
            session.close()


def add_part_to_worksheet(worksheet_id: int, part_id: int, quantity_used: int,
                          unit_cost_at_time: float = 0.0, notes: Optional[str] = None,
                          user_id: Optional[int] = None, storage_location_id: Optional[int] = None,
                          session: Session = None) -> WorksheetPart:
    """
    Add part to worksheet with stock deduction - atomic operation
    Uses transaction wrapper to ensure all operations succeed or all rollback
    """
    if quantity_used <= 0:
        raise ValidationError(
            "Quantity must be positive",
            field="quantity_used",
            user_message=get_localized_error("quantity_must_be_positive")
        )
    
    # Use transaction wrapper for atomicity
    with transaction(session) as trans_session:
        # Use trans_session instead of session
        ws = trans_session.query(Worksheet).filter_by(id=worksheet_id).with_for_update().first()
        if not ws:
            raise NotFoundError("Worksheet", worksheet_id, user_message=get_localized_error("worksheet_not_found"))
        
        # Check stock availability with lock
        from database.models import InventoryLevel
        inv = trans_session.query(InventoryLevel).filter_by(
            part_id=part_id
        ).with_for_update().first()
        
        if not inv or inv.quantity_on_hand < quantity_used:
            raise BusinessLogicError(
                f"Insufficient stock: {quantity_used} requested, "
                f"{inv.quantity_on_hand if inv else 0} available",
                rule="STOCK_AVAILABILITY_CHECK",
                user_message=get_localized_error("insufficient_stock")
            )

        # Calculate FIFO cost if not provided
        if unit_cost_at_time == 0.0:
            unit_cost_at_time = inventory_service.get_fifo_cost(
                part_id=part_id,
                quantity=quantity_used,
                session=trans_session
            )
            # Fallback to part buy_price if no batches exist
            if unit_cost_at_time == 0.0:
                from database.models import Part
                part = trans_session.query(Part).filter_by(id=part_id).first()
                if part and part.buy_price:
                    unit_cost_at_time = part.buy_price

        # Készlet csökkentése
        inventory_service.adjust_stock(
            part_id=part_id,
            quantity=-quantity_used,
            transaction_type=TRANSACTION_TYPE_ISSUED,
            reference_type="worksheet",
            reference_id=worksheet_id,
            user_id=user_id,
            notes=notes,
            storage_location_id=storage_location_id,
            session=trans_session,  # Use transaction session
        )

        wp = WorksheetPart(
            worksheet_id=worksheet_id,
            part_id=part_id,
            quantity_used=quantity_used,
            unit_cost_at_time=unit_cost_at_time,
            notes=notes,
            added_at=utcnow(),
        )
        trans_session.add(wp)
        trans_session.flush()  # Flush to get wp.id
        
        # Generate scrapping documents for each unit used
        from services.settings_service import get_auto_generate_scrapping_doc
        from services.scrapping_service import generate_scrapping_document
        from database.models import Part, PMHistory
        
        part = trans_session.query(Part).filter_by(id=part_id).first()
        if part and get_auto_generate_scrapping_doc():
            # Find PM history associated with this worksheet (if any)
            pm_history = trans_session.query(PMHistory).filter_by(worksheet_id=worksheet_id).first()
            pm_history_id = pm_history.id if pm_history else None
            
            for i in range(quantity_used):
                try:
                    generate_scrapping_document(
                        entity_type="Part",
                        entity_id=part_id,
                        reason=f"Munkalap #{worksheet_id} - Elhasznált alkatrész",
                        worksheet_id=worksheet_id,
                        pm_history_id=pm_history_id,
                        item_number=i+1,
                        total_items=quantity_used,
                        session=trans_session
                    )
                    logger.info(f"Scrapping document {i+1}/{quantity_used} generated for part {part_id} from worksheet {worksheet_id}")
                except Exception as e:
                    logger.warning(f"Error generating scrapping document {i+1}/{quantity_used} for part {part_id}: {e}")
        
        # Transaction commits automatically on exit
        
        # Log worksheet part addition
        from services.log_service import log_action
        from services.context_service import get_current_user_id
        from database.models import Part
        
        # Get user_id (from parameter or context)
        log_user_id = user_id or get_current_user_id()
        
        # Get part info for logging (within transaction session)
        part = trans_session.query(Part).filter_by(id=part_id).first()
        part_name = part.name if part else f"Part ID {part_id}"
        
        try:
            log_action(
                category="worksheet",
                action_type="update",
                entity_type="WorksheetPart",
                entity_id=wp.id,
                user_id=log_user_id,
                description=f"Alkatrész hozzáadva a munkalaphoz: {part_name} (mennyiség: {quantity_used})",
                metadata={
                    "worksheet_id": worksheet_id,
                    "part_id": part_id,
                    "part_name": part_name,
                    "quantity_used": quantity_used,
                    "unit_cost_at_time": unit_cost_at_time,
                    "storage_location_id": storage_location_id,
                    "total_cost": quantity_used * unit_cost_at_time,
                },
                session=trans_session
            )
        except Exception as e:
            logger.warning(f"Error logging worksheet part addition: {e}")
        
        logger.info(f"Worksheet part added ws={worksheet_id} part={part_id} qty={quantity_used}")
        return wp


def close_worksheet(worksheet_id: int, session: Session = None) -> Worksheet:
    return update_status(worksheet_id, WORKSHEET_STATUS_CLOSED, session=session)


def list_active_worksheets(session: Session = None) -> list:
    """List all active (non-closed) worksheets, including PM-related worksheets"""
    session, should_close = _get_session(session)
    try:
        active = (
            session.query(Worksheet)
            .options(
                joinedload(Worksheet.machine),
                joinedload(Worksheet.assigned_user),
                joinedload(Worksheet.parts).joinedload(WorksheetPart.part),
            )
            .filter(Worksheet.status != WORKSHEET_STATUS_CLOSED)
            .order_by(Worksheet.created_at.desc())
            .all()
        )
        logger.info(f"Listed {len(active)} active worksheets")
        return active
    finally:
        if should_close:
            session.close()


def list_worksheets_for_machine(machine_id: int, session: Session = None) -> list:
    """List all worksheets for a specific machine"""
    session, should_close = _get_session(session)
    try:
        worksheets = (
            session.query(Worksheet)
            .options(
                joinedload(Worksheet.machine),
                joinedload(Worksheet.assigned_user),
            )
            .filter(Worksheet.machine_id == machine_id)
            .order_by(Worksheet.created_at.desc())
            .all()
        )
        logger.info(f"Listed {len(worksheets)} worksheets for machine {machine_id}")
        return worksheets
    finally:
        if should_close:
            session.close()


def list_all_worksheets(session: Session = None) -> list:
    """List all worksheets (including closed), with PM task information if available"""
    session, should_close = _get_session(session)
    try:
        items = (
            session.query(Worksheet)
            .options(
                joinedload(Worksheet.machine),
                joinedload(Worksheet.assigned_user),
                joinedload(Worksheet.parts).joinedload(WorksheetPart.part),
            )
            .order_by(Worksheet.created_at.desc())
            .all()
        )
        logger.info(f"Listed {len(items)} worksheets (all statuses)")
        return items
    finally:
        if should_close:
            session.close()


def list_worksheets(
    machine_id: Optional[int] = None,
    status: Optional[str] = None,
    page: int = 1,
    per_page: int = 20,
    session: Session = None
) -> PaginatedResult[Worksheet]:
    """List worksheets with pagination"""
    session, should_close = _get_session(session)
    try:
        query = session.query(Worksheet).options(
            joinedload(Worksheet.machine),
            joinedload(Worksheet.assigned_user),
            joinedload(Worksheet.parts).joinedload(WorksheetPart.part),
            joinedload(Worksheet.photos)
        )
        
        if machine_id:
            query = query.filter(Worksheet.machine_id == machine_id)
        if status:
            query = query.filter(Worksheet.status == status)
        
        query = query.order_by(Worksheet.created_at.desc())
        
        return paginate_query(query, page=page, per_page=per_page)
    finally:
        if should_close:
            session.close()


def get_pm_task_for_worksheet(worksheet_id: int, session: Session = None) -> Optional[dict]:
    """Get PM task information for a worksheet if it's related to a PM task"""
    session, should_close = _get_session(session)
    try:
        pm_history = (
            session.query(PMHistory)
            .options(
                joinedload(PMHistory.pm_task).joinedload(PMTask.machine),
            )
            .filter(PMHistory.worksheet_id == worksheet_id)
            .first()
        )
        if pm_history and pm_history.pm_task:
            return {
                'pm_task_id': pm_history.pm_task.id,
                'pm_task_name': pm_history.pm_task.task_name,
                'pm_task_description': pm_history.pm_task.task_description,
                'pm_history_id': pm_history.id,
                'executed_date': pm_history.executed_date,
            }
        return None
    finally:
        if should_close:
            session.close()


def get_work_request_for_worksheet(worksheet_id: int, session: Session = None) -> Optional[str]:
    """Get work request DOCX/XLSX path for a worksheet if it's related to a PM task
    
    Checks:
    1. PMHistory -> PMTask -> WorkRequestPDF (if worksheet was created from PM task completion)
    2. Worksheet -> Machine -> PMTask -> WorkRequestPDF (if worksheet is for a machine with active PM tasks)
    
    Note: WorkRequestPDF.pdf_path actually stores DOCX/XLSX file paths, not PDF paths.
    """
    session, should_close = _get_session(session)
    try:
        from pathlib import Path
        
        def is_valid_document_file(file_path: str) -> bool:
            """Check if file exists and is DOCX or XLSX (not PDF)"""
            if not file_path:
                return False
            path = Path(file_path)
            if not path.exists():
                return False
            # Only accept DOCX or XLSX files, not PDF
            suffix = path.suffix.lower()
            return suffix in ['.docx', '.xlsx']
        
        # First, try to find via PMHistory (worksheet created from PM task completion)
        pm_history = (
            session.query(PMHistory)
            .options(
                joinedload(PMHistory.pm_task),
            )
            .filter(PMHistory.worksheet_id == worksheet_id)
            .first()
        )
        if pm_history and pm_history.pm_task:
            work_request = session.query(WorkRequestPDF).filter_by(pm_task_id=pm_history.pm_task.id).first()
            if work_request and work_request.pdf_path:
                if is_valid_document_file(work_request.pdf_path):
                    return work_request.pdf_path
        
        # Second, try to find via machine -> PMTask (worksheet for machine with PM task)
        worksheet = session.query(Worksheet).filter_by(id=worksheet_id).first()
        if worksheet and worksheet.machine_id:
            # Find active PM tasks for this machine
            pm_tasks = (
                session.query(PMTask)
                .filter(
                    PMTask.machine_id == worksheet.machine_id,
                    PMTask.is_active == True  # noqa: E712
                )
                .order_by(PMTask.created_at.desc())
                .limit(1)
                .all()
            )
            # Get the most recent PM task's work request
            for pm_task in pm_tasks:
                work_request = session.query(WorkRequestPDF).filter_by(pm_task_id=pm_task.id).first()
                if work_request and work_request.pdf_path:
                    if is_valid_document_file(work_request.pdf_path):
                        return work_request.pdf_path
        
        return None
    finally:
        if should_close:
            session.close()


def get_worksheet(worksheet_id: int, session: Session = None) -> Worksheet:
    """Get a single worksheet by ID"""
    session, should_close = _get_session(session)
    try:
        ws = (
            session.query(Worksheet)
            .options(
                joinedload(Worksheet.machine),
                joinedload(Worksheet.assigned_user),
                joinedload(Worksheet.parts).joinedload(WorksheetPart.part),
            )
            .filter_by(id=worksheet_id)
            .first()
        )
        if not ws:
            raise WorksheetServiceError(get_localized_error("worksheet_not_found"))
        return ws
    finally:
        if should_close:
            session.close()


def update_worksheet_status(worksheet_id: int, new_status: str, repair_finished_time=None, session: Session = None) -> Worksheet:
    """Update worksheet status - wrapper around update_status with repair_finished_time support"""
    return update_status(worksheet_id, new_status, repair_finished_time=repair_finished_time, session=session)


def update_notes(worksheet_id: int, notes: str, session: Session = None) -> Worksheet:
    """Update worksheet notes field"""
    session, should_close = _get_session(session)
    try:
        ws = session.query(Worksheet).filter_by(id=worksheet_id).first()
        if not ws:
            raise NotFoundError("Worksheet", worksheet_id, user_message=get_localized_error("worksheet_not_found"))
        old_notes = ws.notes
        ws.notes = notes if notes else None
        session.commit()
        
        # Log notes update
        from services.log_service import log_action
        from services.context_service import get_current_user_id
        
        user_id = get_current_user_id()
        try:
            log_action(
                category="worksheet",
                action_type="update",
                entity_type="Worksheet",
                entity_id=worksheet_id,
                user_id=user_id,
                description=f"Munkalap megjegyzések módosítva: {ws.title}",
                metadata={
                    "worksheet_title": ws.title,
                    "old_notes": old_notes or "-",
                    "new_notes": notes or "-",
                    "machine_id": ws.machine_id,
                },
                session=session
            )
        except Exception as e:
            logger.warning(f"Error logging worksheet notes update: {e}")
        
        logger.info(f"Worksheet notes updated id={worksheet_id}")
        return ws
    finally:
        if should_close:
            session.close()
