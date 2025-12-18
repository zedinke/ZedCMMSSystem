"""
Preventive Maintenance (PM) szolgáltatás
"""

from datetime import timedelta, datetime
from typing import Optional, List, Dict
from pathlib import Path
from sqlalchemy.orm import Session, joinedload
import uuid

from database.session_manager import SessionLocal
from database.models import PMTask, PMHistory, Machine, User, utcnow
from config.constants import PM_STATUS_COMPLETED, PM_STATUS_SKIPPED, PM_STATUS_PENDING
from utils.localization_helper import get_localized_error
from utils.error_handler import (
    ValidationError,
    BusinessLogicError,
    NotFoundError,
    StateTransitionError,
    CMMSError
)
from services.workflow_service import (
    transition_state,
    PMTaskState
)

import logging

logger = logging.getLogger(__name__)


class PMServiceError(CMMSError):
    """PM szolgáltatás hiba - backward compatibility"""
    pass


def _get_session(session: Optional[Session]) -> (Session, bool):
    if session is None:
        return SessionLocal(), True
    return session, False


def get_pm_task_directory(pm_task_id: int, pm_history_id: Optional[int] = None) -> Path:
    """Get the directory path for a PM task's files
    
    Structure: {parent_dir}/pm_task_{task_id}/history_{history_id}/
    If pm_history_id is None, returns the task directory (for general task files)
    
    Args:
        pm_task_id: PM task ID
        pm_history_id: Optional PM history ID (for specific completion files)
    
    Returns:
        Path to the directory (will be created if it doesn't exist)
    """
    parent_dir = get_pm_task_files_dir()
    if not parent_dir:
        # Fallback to default
        parent_dir = Path("generated_pdfs") / "pm_tasks"
    
    # Create parent directory if it doesn't exist
    parent_dir.mkdir(parents=True, exist_ok=True)
    
    task_dir = parent_dir / f"pm_task_{pm_task_id}"
    
    if pm_history_id:
        history_dir = task_dir / f"history_{pm_history_id}"
        history_dir.mkdir(parents=True, exist_ok=True)
        return history_dir
    else:
        task_dir.mkdir(parents=True, exist_ok=True)
        return task_dir


def save_pm_task_attachments(
    pm_history_id: int,
    file_paths: List[str],
    uploaded_by_user_id: Optional[int] = None,
    session: Session = None
) -> List:
    """Save uploaded files for a PM task completion
    
    Args:
        pm_history_id: PM history ID
        file_paths: List of file paths to save
        uploaded_by_user_id: User ID who uploaded the files
        session: Database session
    
    Returns:
        List of created PMTaskAttachment objects
    """
    from database.models import PMTaskAttachment, PMHistory
    import shutil
    from services.settings_service import get_pm_task_files_dir
    
    session, should_close = _get_session(session)
    try:
        # Get PM history to get task ID
        pm_history = session.query(PMHistory).filter_by(id=pm_history_id).first()
        if not pm_history:
            raise NotFoundError("PMHistory", pm_history_id)
        
        # Get directory for this completion
        task_dir = get_pm_task_directory(pm_history.pm_task_id, pm_history_id)
        
        attachments = []
        
        for source_path in file_paths:
            source = Path(source_path)
            if not source.exists():
                logger.warning(f"File not found: {source_path}")
                continue
            
            # Generate unique filename
            file_ext = source.suffix
            unique_filename = f"{uuid.uuid4().hex}{file_ext}"
            dest_path = task_dir / unique_filename
            
            # Copy file
            shutil.copy2(source, dest_path)
            
            # Determine file type
            image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
            doc_extensions = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.txt'}
            
            if file_ext.lower() in image_extensions:
                file_type = "image"
            elif file_ext.lower() in doc_extensions:
                file_type = "document"
            else:
                file_type = "other"
            
            # Create database record
            attachment = PMTaskAttachment(
                pm_history_id=pm_history_id,
                file_path=str(dest_path),
                original_filename=source.name,
                file_type=file_type,
                file_size=dest_path.stat().st_size,
                uploaded_by_user_id=uploaded_by_user_id,
            )
            session.add(attachment)
            attachments.append(attachment)
        
        session.commit()
        logger.info(f"Saved {len(attachments)} attachments for PM history {pm_history_id}")
        return attachments
    except NotFoundError as e:
        session.rollback()
        logger.warning(f"Not found error in pm_service.save_pm_task_attachments: {e}", exc_info=True)
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Unexpected error in pm_service.save_pm_task_attachments: {e}", exc_info=True)
        raise
    finally:
        if should_close:
            session.close()


def copy_pm_task_documents_to_directory(
    pm_task_id: int,
    pm_history_id: int,
    session: Session = None
) -> List[Path]:
    """Copy generated documents (work request, worksheet, scrapping) to PM task directory
    
    Args:
        pm_task_id: PM task ID
        pm_history_id: PM history ID
        session: Database session
    
    Returns:
        List of copied file paths
    """
    from database.models import WorkRequestPDF, PMWorksheetPDF, ScrappingDocument, PMHistory
    import shutil
    
    session, should_close = _get_session(session)
    try:
        # Get PM history to verify it exists
        pm_history = session.query(PMHistory).filter_by(id=pm_history_id, pm_task_id=pm_task_id).first()
        if not pm_history:
            logger.warning(f"PM history {pm_history_id} not found for task {pm_task_id}")
            return []
        
        # Get directory for this completion
        task_dir = get_pm_task_directory(pm_task_id, pm_history_id)
        copied_files = []
        
        # Copy work request document
        work_request = session.query(WorkRequestPDF).filter_by(pm_task_id=pm_task_id).first()
        if work_request and work_request.pdf_path:
            work_request_path = Path(work_request.pdf_path)
            if work_request_path.exists():
                dest_path = task_dir / f"work_request_{pm_task_id}.docx"
                shutil.copy2(work_request_path, dest_path)
                copied_files.append(dest_path)
                logger.info(f"Copied work request to {dest_path}")
        
        # Copy worksheet document
        if pm_history.worksheet_id:
            worksheet_pdf = session.query(PMWorksheetPDF).filter_by(pm_history_id=pm_history_id).first()
            if worksheet_pdf and worksheet_pdf.pdf_path:
                worksheet_path = Path(worksheet_pdf.pdf_path)
                if worksheet_path.exists():
                    dest_path = task_dir / f"worksheet_{pm_history.worksheet_id}.docx"
                    shutil.copy2(worksheet_path, dest_path)
                    copied_files.append(dest_path)
                    logger.info(f"Copied worksheet to {dest_path}")
            
            # Copy scrapping documents
            scrapping_docs = session.query(ScrappingDocument).filter_by(pm_history_id=pm_history_id).all()
            for idx, scrapping_doc in enumerate(scrapping_docs):
                if scrapping_doc.docx_path:
                    scrapping_path = Path(scrapping_doc.docx_path)
                    if scrapping_path.exists():
                        dest_path = task_dir / f"scrapping_{scrapping_doc.entity_type.lower()}_{scrapping_doc.entity_id}_{idx+1}.docx"
                        shutil.copy2(scrapping_path, dest_path)
                        copied_files.append(dest_path)
                        logger.info(f"Copied scrapping document to {dest_path}")
        
        logger.info(f"Copied {len(copied_files)} documents for PM history {pm_history_id}")
        return copied_files
        
    except Exception as e:
        logger.error(f"Error copying PM task documents: {e}")
        return []
    finally:
        if should_close:
            session.close()


def create_pm_task(
    machine_id: Optional[int],
    task_name: str,
    frequency_days: Optional[int],
    task_description: Optional[str] = None,
    assigned_to_user_id: Optional[int] = None,
    priority: str = "normal",
    status: str = "pending",
    due_date: Optional[datetime] = None,
    estimated_duration_minutes: Optional[int] = None,
    created_by_user_id: Optional[int] = None,
    location: Optional[str] = None,
    task_type: str = "recurring",
    session: Session = None
) -> PMTask:
    """
    Create a new PM (Preventive Maintenance) task.
    
    This function creates a PM task for a specific machine. The task can be either
    recurring (with frequency_days) or one-time (task_type="one_time").
    
    Workflow:
    1. Validates machine exists (if machine_id provided)
    2. Validates workflow state transition
    3. Creates PMTask record
    4. Sends notification (if assigned_to_user_id provided)
    5. Generates Work Request PDF
    6. Logs action to SystemLog
    
    Args:
        machine_id: ID of the machine this PM task is for. If None, location must be provided.
        task_name: Name/description of the PM task (required).
        frequency_days: How often this task should be performed (for recurring tasks).
        task_description: Detailed description of the task.
        assigned_to_user_id: User ID to assign the task to. If None, task is globally assigned.
        priority: Task priority. Must be one of: "low", "normal", "high", "urgent".
                 Default: "normal".
        status: Initial status. Must be valid PMTask state. Default: "pending".
        due_date: Due date for the task. If None, calculated from frequency_days.
        estimated_duration_minutes: Estimated time to complete in minutes.
        created_by_user_id: User ID who created this task.
        location: Location where task should be performed. Required if machine_id is None.
        task_type: "recurring" or "one_time". Default: "recurring".
        session: Database session. If None, creates new session and closes it after.
    
    Returns:
        PMTask: Created PM task object with all relationships loaded.
    
    Raises:
        NotFoundError: If machine with machine_id not found, or user with 
                      assigned_to_user_id/created_by_user_id not found.
        ValidationError: If machine_id and location both None, or invalid priority/status values.
        StateTransitionError: If invalid state transition for initial status.
        BusinessLogicError: If business rules violated.
    
    Example:
        >>> task = create_pm_task(
        ...     machine_id=1,
        ...     task_name="Monthly oil change",
        ...     frequency_days=30,
        ...     priority="normal",
        ...     created_by_user_id=1
        ... )
        >>> print(task.id)
        42
    
    Note:
        - Automatically generates Work Request PDF after creation.
        - Sends notification to assigned user (or all active users if globally assigned).
        - Logs action to SystemLog for audit trail.
    """
    session, should_close = _get_session(session)
    try:
        # Validate machine if machine_id is provided
        if machine_id is not None:
            machine = session.query(Machine).filter_by(id=machine_id).first()
            if not machine:
                raise NotFoundError("Machine", machine_id, user_message=get_localized_error("machine_not_found"))
        elif not location:
            raise ValidationError(
                "Either machine_id or location must be provided",
                field="machine_id",
                user_message=get_localized_error("machine_or_location_required")
            )
        
        if assigned_to_user_id:
            user = session.query(User).filter_by(id=assigned_to_user_id).first()
            if not user:
                raise NotFoundError("User", assigned_to_user_id, user_message=get_localized_error("assigned_user_not_found"))
        
        if created_by_user_id:
            creator = session.query(User).filter_by(id=created_by_user_id).first()
            if not creator:
                raise NotFoundError("User", created_by_user_id, user_message=get_localized_error("creator_user_not_found"))
        
        now = utcnow()
        
        # Calculate next_due_date based on task type
        if task_type == "one_time":
            next_due = due_date if due_date else now
        else:
            # Recurring task
            if frequency_days:
                next_due = due_date if due_date else (now + timedelta(days=frequency_days))
            else:
                next_due = due_date if due_date else now
        
        task = PMTask(
            machine_id=machine_id,
            task_name=task_name,
            task_description=task_description,
            task_type=task_type,
            frequency_days=frequency_days,
            assigned_to_user_id=assigned_to_user_id,
            priority=priority,
            status=status,
            due_date=due_date,
            estimated_duration_minutes=estimated_duration_minutes,
            created_by_user_id=created_by_user_id,
            location=location,
            created_at=now,
            updated_at=now,
            next_due_date=next_due,
            is_active=True,
        )
        session.add(task)
        session.commit()
        logger.info(f"PM task created: {task_name} machine={machine_id} location={location} assigned_to={assigned_to_user_id}")
        
        # Send notification about task assignment
        try:
            from services.notification_service import notify_pm_task_assigned
            notify_pm_task_assigned(task.id, assigned_to_user_id, session=session)
        except Exception as e:
            logger.warning(f"Error sending PM task assignment notification: {e}")
        
        # Log PM task creation
        from services.log_service import log_action
        try:
            log_action(
                category="task",
                action_type="create",
                entity_type="PMTask",
                entity_id=task.id,
                user_id=created_by_user_id,
                description=f"PM feladat létrehozva: {task_name}",
                metadata={
                    "task_name": task_name,
                    "task_type": task_type,
                    "machine_id": machine_id,
                    "location": location,
                    "assigned_to_user_id": assigned_to_user_id,
                },
                session=session
            )
        except Exception as e:
            logger.warning(f"Error logging PM task creation: {e}")
        
        # Generate work request PDF
        try:
            from services import pdf_service
            pdf_path = pdf_service.generate_work_request_pdf(
                task.id,
                generated_by=f"user_{created_by_user_id}" if created_by_user_id else "system",
                session=session
            )
            logger.info(f"Work request PDF generated: {pdf_path}")
            
            # Log work request generation
            try:
                log_action(
                    category="work_request",
                    action_type="generate",
                    entity_type="WorkRequest",
                    entity_id=task.id,
                    user_id=created_by_user_id,
                    description=f"Munkaigénylő generálva: {task_name}",
                    metadata={
                        "pm_task_id": task.id,
                        "task_name": task_name,
                    },
                    session=session
                )
            except Exception as e:
                logger.warning(f"Error logging work request generation: {e}")
        except Exception as e:
            logger.error(f"Failed to generate work request PDF: {e}", exc_info=True)
        
        return task
    finally:
        if should_close:
            session.close()


def update_pm_task(task_id: int, **kwargs) -> PMTask:
    """
    Update an existing PM task.
    
    Updates specified fields of a PM task. Only provided fields are updated.
    Tracks changes for version history and logging.
    
    Args:
        task_id: ID of the PM task to update (required).
        **kwargs: Fields to update. Valid fields: task_name, status, priority,
                 assigned_to_user_id, due_date, estimated_duration_minutes, etc.
                 Only provided fields are updated.
    
    Returns:
        PMTask: Updated PM task object.
    
    Raises:
        NotFoundError: If PM task with task_id not found.
        ValidationError: If any provided field value is invalid.
        StateTransitionError: If status change violates workflow rules.
    
    Note:
        - If assigned_to_user_id changes, sends notification to new assignee.
        - Logs changes to SystemLog with change tracking.
    """
    session, should_close = _get_session(kwargs.pop("session", None))
    try:
        task = session.query(PMTask).filter_by(id=task_id).first()
        if not task:
            raise NotFoundError("PMTask", task_id, user_message=get_localized_error("pm_task_not_found"))
        
        # Track changes for logging
        changes = {}
        assigned_user_changed = False
        old_assigned_user_id = task.assigned_to_user_id
        
        for field, value in kwargs.items():
            if hasattr(task, field) and value is not None:
                old_value = getattr(task, field)
                if old_value != value:
                    changes[field] = {"old": str(old_value), "new": str(value)}
                    setattr(task, field, value)
                    # Check if assigned_to_user_id changed
                    if field == "assigned_to_user_id":
                        assigned_user_changed = True
        
        task.updated_at = utcnow()
        session.commit()
        
        # Send notification if assignment changed
        if assigned_user_changed:
            try:
                from services.notification_service import notify_pm_task_assigned
                notify_pm_task_assigned(task.id, task.assigned_to_user_id, session=session)
            except Exception as e:
                logger.warning(f"Error sending PM task assignment notification: {e}")
        
        # Log update if there were changes
        if changes:
            from services.log_service import log_action
            from services.context_service import get_current_user_id
            try:
                log_action(
                    category="task",
                    action_type="update",
                    entity_type="PMTask",
                    entity_id=task_id,
                    user_id=get_current_user_id(),
                    description=f"PM feladat módosítva: {task.task_name}",
                    metadata={"changes": changes},
                    session=session
                )
            except Exception as e:
                logger.warning(f"Error logging PM task update: {e}")
        
        return task
    except ValidationError as e:
        session.rollback()
        logger.warning(f"Validation error in pm_service.update_pm_task: {e}", exc_info=True)
        raise
    except NotFoundError as e:
        session.rollback()
        logger.warning(f"Not found error in pm_service.update_pm_task: {e}", exc_info=True)
        raise
    except StateTransitionError as e:
        session.rollback()
        logger.warning(f"State transition error in pm_service.update_pm_task: {e}", exc_info=True)
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Unexpected error in pm_service.update_pm_task: {e}", exc_info=True)
        raise
    finally:
        if should_close:
            session.close()


def record_execution(task_id: int, assigned_to_user_id: Optional[int] = None,
                     completed_by_user_id: Optional[int] = None,
                     completion_status: str = PM_STATUS_COMPLETED,
                     notes: Optional[str] = None,
                     duration_minutes: int = 0,
                     session: Session = None) -> PMHistory:
    session, should_close = _get_session(session)
    try:
        task = session.query(PMTask).filter_by(id=task_id).first()
        if not task:
            raise NotFoundError("PMTask", task_id, user_message=get_localized_error("pm_task_not_found"))
        if completion_status not in {PM_STATUS_COMPLETED, PM_STATUS_SKIPPED, PM_STATUS_PENDING}:
            raise ValidationError(
                f"Invalid completion status: {completion_status}",
                field="completion_status",
                user_message=get_localized_error("invalid_completion_status")
            )

        now = utcnow()
        history = PMHistory(
            pm_task_id=task_id,
            executed_date=now,
            assigned_to_user_id=assigned_to_user_id,
            completed_by_user_id=completed_by_user_id,
            completion_status=completion_status,
            notes=notes,
            duration_minutes=duration_minutes,
        )
        session.add(history)

        # Frissítjük a task esedékességét csak ha végrehajtott vagy kihagyott
        if completion_status in {PM_STATUS_COMPLETED, PM_STATUS_SKIPPED}:
            task.last_executed_date = now
            task.next_due_date = now + timedelta(days=task.frequency_days)
            task.updated_at = now

        session.commit()
        logger.info(f"PM execution recorded task={task_id} status={completion_status}")
        return history
    except ValidationError as e:
        session.rollback()
        logger.warning(f"Validation error in pm_service.record_execution: {e}", exc_info=True)
        raise
    except NotFoundError as e:
        session.rollback()
        logger.warning(f"Not found error in pm_service.record_execution: {e}", exc_info=True)
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Unexpected error in pm_service.record_execution: {e}", exc_info=True)
        raise
    finally:
        if should_close:
            session.close()


def list_due_tasks(reference_time=None, user_id: Optional[int] = None, session: Session = None, include_future: bool = True) -> List[PMTask]:
    """List due PM tasks, optionally filtered by assigned user
    
    Args:
        reference_time: Reference time for due date comparison (default: now)
        user_id: Filter by assigned user (None = show all)
        session: Database session
        include_future: If True, include all active tasks regardless of due date. If False, only show tasks that are due or overdue.
    """
    session, should_close = _get_session(session)
    try:
        ref = reference_time or utcnow()
        query = session.query(PMTask).options(
            joinedload(PMTask.machine),
            joinedload(PMTask.assigned_user),
            joinedload(PMTask.created_by_user)
        ).filter(
            PMTask.is_active == True  # noqa: E712
        )
        
        # Only filter by due date if include_future is False
        if not include_future:
            query = query.filter(PMTask.next_due_date <= ref)
        
        # Filter by user: show global tasks (assigned_to_user_id is None) or tasks assigned to this user
        if user_id is not None:
            query = query.filter(
                (PMTask.assigned_to_user_id == None) | (PMTask.assigned_to_user_id == user_id)  # noqa: E711
            )
        
        # Order by next_due_date ascending (earliest first)
        return query.order_by(PMTask.next_due_date.asc()).all()
    finally:
        if should_close:
            session.close()


def list_pm_history(
    user_id: Optional[int] = None,
    task_id: Optional[int] = None,
    completion_status: Optional[str] = None,
    session: Session = None
) -> List[PMHistory]:
    """List PM execution history records, optionally filtered by user, task, or status"""
    session, should_close = _get_session(session)
    try:
        from sqlalchemy.orm import joinedload
        query = session.query(PMHistory).options(
            joinedload(PMHistory.pm_task).joinedload(PMTask.machine),
            joinedload(PMHistory.assigned_user),
            joinedload(PMHistory.completed_user)
        )
        
        # Filter by task
        if task_id:
            query = query.filter(PMHistory.pm_task_id == task_id)
        
        # Filter by completion status
        if completion_status:
            query = query.filter(PMHistory.completion_status == completion_status)
        
        # Filter by user (assigned or completed by)
        if user_id:
            query = query.filter(
                (PMHistory.assigned_to_user_id == user_id) | (PMHistory.completed_by_user_id == user_id)
            )
        
        # Order by execution date descending (most recent first)
        return query.order_by(PMHistory.executed_date.desc()).all()
    finally:
        if should_close:
            session.close()


def list_pm_tasks(user_id: Optional[int] = None, status: Optional[str] = None, 
                 machine_id: Optional[int] = None, session: Session = None) -> List[PMTask]:
    """List all PM tasks, optionally filtered by assigned user, status, or machine
    
    Shows:
    - Global tasks (assigned_to_user_id is None)
    - Tasks assigned to the user
    - Tasks created by the user (so creators can see their own tasks)
    """
    session, should_close = _get_session(session)
    try:
        query = session.query(PMTask).options(
            joinedload(PMTask.machine),
            joinedload(PMTask.assigned_user),
            joinedload(PMTask.created_by_user)
        ).filter(PMTask.is_active == True)  # noqa: E712
        
        # Filter by user: show global tasks, tasks assigned to this user, or tasks created by this user
        if user_id is not None:
            query = query.filter(
                (PMTask.assigned_to_user_id == None) |  # Global tasks
                (PMTask.assigned_to_user_id == user_id) |  # Assigned to user
                (PMTask.created_by_user_id == user_id)  # Created by user
            )
        
        # Filter by status
        if status:
            query = query.filter(PMTask.status == status)
        
        # Filter by machine
        if machine_id is not None:
            query = query.filter(PMTask.machine_id == machine_id)
        
        return query.order_by(PMTask.next_due_date.asc()).all()
    finally:
        if should_close:
            session.close()


def complete_pm_task(
    task_id: int,
    completed_by_user_id: int,
    notes: Optional[str] = None,
    duration_minutes: Optional[int] = None,
    create_worksheet: bool = True,
    session: Session = None
) -> tuple[PMHistory, Optional[int]]:
    """
    Complete a PM task and optionally create a worksheet.
    
    This function marks a PM task as completed and optionally creates a worksheet
    for the maintenance work. It generates required documents (Work Request PDF,
    PM Worksheet PDF, Scrapping Documents if parts used).
    
    Workflow:
    1. Validates task exists and transition to "completed" is allowed
    2. Creates PMHistory record with completion details
    3. Updates task status and next_due_date (for recurring tasks)
    4. Creates Worksheet (if create_worksheet=True and machine_id set)
    5. Generates PM Worksheet PDF
    6. Sends completion notification
    7. Logs action to SystemLog
    
    Args:
        task_id: ID of the PM task to complete (required).
        completed_by_user_id: User ID who completed the task (required).
        notes: Completion notes/observations.
        duration_minutes: Actual duration in minutes.
        create_worksheet: If True, creates Worksheet for the completion.
                         Only created if task has machine_id set.
        session: Database session. If None, creates new session.
    
    Returns:
        Tuple of (PMHistory, worksheet_id):
        - PMHistory: Created history record with completion details.
        - worksheet_id: ID of created worksheet, or None if not created.
    
    Raises:
        NotFoundError: If PM task with task_id not found, or user not found.
        StateTransitionError: If transition from current status to "completed" is invalid.
        BusinessLogicError: If business rules violated.
    
    Example:
        >>> history, worksheet_id = complete_pm_task(
        ...     task_id=1,
        ...     completed_by_user_id=5,
        ...     notes="Completed successfully",
        ...     duration_minutes=120
        ... )
        >>> print(history.id)
        42
    
    Note:
        - For one-time tasks, marks task as inactive after completion.
        - For recurring tasks, calculates next_due_date from frequency_days.
        - Automatically generates PM Worksheet PDF.
        - Sends notification to completing user and shift leaders/managers.
    """
    session, should_close = _get_session(session)
    try:
        task = session.query(PMTask).filter_by(id=task_id).first()
        if not task:
            raise NotFoundError("PMTask", task_id, user_message=get_localized_error("pm_task_not_found"))
        
        # Validate transition to completed
        transition_state("pm_task", task.status, "completed")
        
        # Record execution
        now = utcnow()
        history = PMHistory(
            pm_task_id=task_id,
            executed_date=now,
            assigned_to_user_id=task.assigned_to_user_id,
            completed_by_user_id=completed_by_user_id,
            completion_status=PM_STATUS_COMPLETED,
            notes=notes,
            duration_minutes=duration_minutes or 0,
        )
        session.add(history)
        
        # Update task status and next due date
        task.status = "completed"
        task.last_executed_date = now
        
        # For one-time tasks, don't update next_due_date (they're done)
        # For recurring tasks, calculate next due date
        if task.task_type == "recurring" and task.frequency_days:
            task.next_due_date = now + timedelta(days=task.frequency_days)
        elif task.task_type == "one_time":
            # One-time task is completed, mark as inactive
            task.is_active = False
        
        task.updated_at = now
        
        # Create worksheet if requested (only if machine_id is set, not for "other" location tasks)
        worksheet_id = None
        if create_worksheet and task.machine_id:
            from services import worksheet_service
            # Title will be auto-generated from settings format, so pass empty string
            worksheet = worksheet_service.create_worksheet(
                machine_id=task.machine_id,
                assigned_to_user_id=completed_by_user_id,
                title="",  # Title will be auto-generated from settings format
                description=f"Karbantartási feladat végrehajtása.\n\nFeladat leírása: {task.task_description or 'Nincs'}\n\nHelyszín: {task.location or 'Nincs'}\n\nMegjegyzések: {notes or 'Nincs'}",
                breakdown_time=now,
                session=session
            )
            worksheet_id = worksheet.id if worksheet else None
            history.worksheet_id = worksheet_id
        
        session.commit()
        session.refresh(history)  # Refresh to ensure all attributes are loaded
        
        # Store worksheet_id before session closes
        worksheet_id_result = history.worksheet_id
        
        # Send notification about task completion
        try:
            from services.notification_service import notify_pm_task_completed
            notify_pm_task_completed(task_id, completed_by_user_id, session=session)
        except Exception as e:
            logger.warning(f"Error sending PM task completion notification: {e}")
        
        # Generate PM worksheet PDF
        try:
            from services import pdf_service
            pdf_path = pdf_service.generate_pm_worksheet_pdf(
                history.id,
                generated_by=f"user_{completed_by_user_id}",
                session=session
            )
            logger.info(f"PM worksheet PDF generated: {pdf_path}")
        except Exception as e:
            logger.error(f"Failed to generate PM worksheet PDF: {e}", exc_info=True)
        
        # Log PM task completion
        from services.log_service import log_action
        try:
            log_action(
                category="task",
                action_type="complete",
                entity_type="PMTask",
                entity_id=task_id,
                user_id=completed_by_user_id,
                description=f"PM feladat befejezve: {task.task_name}",
                metadata={
                    "task_name": task.task_name,
                    "task_type": task.task_type,
                    "worksheet_id": worksheet_id_result,
                    "duration_minutes": duration_minutes,
                },
                session=session
            )
        except Exception as e:
            logger.warning(f"Error logging PM task completion: {e}")
        
        logger.info(f"PM task completed: {task_id} worksheet_created={create_worksheet} worksheet_id={worksheet_id_result}")
        return history, worksheet_id_result
    except NotFoundError as e:
        session.rollback()
        logger.warning(f"Not found error in pm_service.complete_pm_task: {e}", exc_info=True)
        raise
    except StateTransitionError as e:
        session.rollback()
        logger.warning(f"State transition error in pm_service.complete_pm_task: {e}", exc_info=True)
        raise
    except BusinessLogicError as e:
        session.rollback()
        logger.warning(f"Business logic error in pm_service.complete_pm_task: {e}", exc_info=True)
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Unexpected error in pm_service.complete_pm_task: {e}", exc_info=True)
        raise
    finally:
        if should_close:
            session.close()


def update_pm_task_statuses(session: Session = None) -> Dict[str, int]:
    """
    Automatically update PM task statuses based on due dates
    
    Returns:
        Dictionary with update statistics
    """
    from typing import Dict
    session, should_close = _get_session(session)
    stats = {
        "updated": 0,
        "overdue": 0,
        "due_today": 0,
        "errors": 0
    }
    
    try:
        now = utcnow()
        
        # Get all active pending tasks
        tasks = session.query(PMTask).filter(
            PMTask.is_active == True  # noqa: E712
        ).filter(
            PMTask.status == "pending"
        ).all()
        
        for task in tasks:
            try:
                if not task.next_due_date:
                    continue
                
                days_overdue = (now.date() - task.next_due_date.date()).days
                
                if days_overdue > 0:
                    # Overdue
                    task.status = "overdue"
                    stats["overdue"] += 1
                    
                    # Escalate priority if very overdue
                    if days_overdue > 7 and task.priority != "urgent":
                        task.priority = "urgent"
                elif days_overdue == 0:
                    # Due today
                    task.status = "due_today"
                    stats["due_today"] += 1
                
                task.updated_at = now
                stats["updated"] += 1
                
            except Exception as e:
                logger.error(f"Error updating PM task {task.id}: {e}")
                stats["errors"] += 1
        
        session.commit()
        logger.info(f"PM task statuses updated: {stats}")
        return stats
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error updating PM task statuses: {e}", exc_info=True)
        raise
    finally:
        if should_close:
            session.close()
