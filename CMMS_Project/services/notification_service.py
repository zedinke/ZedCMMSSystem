"""
Notification service for internal notifications
"""

from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from database.session_manager import SessionLocal
from database.models import Notification, PMTask, Worksheet, User, Role, utcnow
from config.roles import (
    ROLE_MANAGER,
    ROLE_MAINTENANCE_SUPERVISOR,
    ROLE_PRODUCTION_SUPERVISOR
)

import logging

logger = logging.getLogger(__name__)


class NotificationServiceError(Exception):
    """Generic notification service error"""
    pass


def _get_session(session: Optional[Session]) -> (Session, bool):
    if session is None:
        return SessionLocal(), True
    return session, False


def create_notification(
    user_id: int,
    title: str,
    message: str,
    notification_type: str = "info",
    related_entity_type: Optional[str] = None,
    related_entity_id: Optional[int] = None,
    session: Session = None
) -> Notification:
    """Create a new notification"""
    session, should_close = _get_session(session)
    try:
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id,
            created_at=utcnow(),
        )
        session.add(notification)
        session.commit()
        logger.info(f"Notification created: {title} for user {user_id}")
        return notification
    finally:
        if should_close:
            session.close()


def get_user_notifications(
    user_id: int,
    unread_only: bool = False,
    limit: Optional[int] = None,
    session: Session = None
) -> List[Notification]:
    """Get notifications for a user"""
    session, should_close = _get_session(session)
    try:
        query = session.query(Notification).filter_by(user_id=user_id)
        if unread_only:
            query = query.filter_by(is_read=False)
        query = query.order_by(Notification.created_at.desc())
        if limit:
            query = query.limit(limit)
        return query.all()
    finally:
        if should_close:
            session.close()


def mark_notification_read(notification_id: int, session: Session = None) -> bool:
    """Mark a notification as read"""
    session, should_close = _get_session(session)
    try:
        notification = session.query(Notification).filter_by(id=notification_id).first()
        if not notification:
            raise NotificationServiceError("Notification not found")
        notification.is_read = True
        notification.read_at = utcnow()
        session.commit()
        return True
    finally:
        if should_close:
            session.close()


def mark_all_read(user_id: int, session: Session = None) -> int:
    """Mark all notifications as read for a user"""
    session, should_close = _get_session(session)
    try:
        count = session.query(Notification).filter_by(
            user_id=user_id,
            is_read=False
        ).update({
            'is_read': True,
            'read_at': utcnow()
        })
        session.commit()
        return count
    finally:
        if should_close:
            session.close()


def get_unread_count(user_id: int, session: Session = None) -> int:
    """Get count of unread notifications for a user"""
    session, should_close = _get_session(session)
    try:
        return session.query(Notification).filter_by(
            user_id=user_id,
            is_read=False
        ).count()
    finally:
        if should_close:
            session.close()


def delete_notification(notification_id: int, session: Session = None) -> bool:
    """Delete a notification"""
    session, should_close = _get_session(session)
    try:
        notification = session.query(Notification).filter_by(id=notification_id).first()
        if not notification:
            raise NotificationServiceError("Notification not found")
        session.delete(notification)
        session.commit()
        return True
    finally:
        if should_close:
            session.close()


def notify_vacation_request(vacation_request_id: int, session: Session = None) -> List[Notification]:
    """
    Send notifications to Manager and Maintenance Manager role users about a new vacation request
    
    Args:
        vacation_request_id: Vacation request ID
        session: Database session
    
    Returns:
        List of created Notification objects
    """
    from database.models import VacationRequest, User, Role
    
    session, should_close = _get_session(session)
    
    try:
        # Get vacation request
        vacation_request = session.query(VacationRequest).filter_by(id=vacation_request_id).first()
        if not vacation_request:
            raise NotificationServiceError("Vacation request not found")
        
        # Get requesting user
        requesting_user = session.query(User).filter_by(id=vacation_request.user_id).first()
        if not requesting_user:
            raise NotificationServiceError("Requesting user not found")
        
        # Get Manager and Maintenance Manager roles
        manager_role = session.query(Role).filter_by(name="Manager").first()
        maintenance_manager_role = session.query(Role).filter_by(name="Karbantartás vezető").first()
        
        if not manager_role and not maintenance_manager_role:
            logger.warning("No Manager or Maintenance Manager roles found")
            return []
        
        # Get users with these roles
        role_ids = []
        if manager_role:
            role_ids.append(manager_role.id)
        if maintenance_manager_role:
            role_ids.append(maintenance_manager_role.id)
        
        if not role_ids:
            return []
        
        approvers = session.query(User).filter(
            User.role_id.in_(role_ids),
            User.is_active == True
        ).all()
        
        if not approvers:
            logger.warning("No active Manager or Maintenance Manager users found")
            return []
        
        # Create notifications
        notifications = []
        user_name = requesting_user.full_name or requesting_user.username
        start_date_str = vacation_request.start_date.strftime("%Y-%m-%d") if isinstance(vacation_request.start_date, datetime) else str(vacation_request.start_date.date())
        end_date_str = vacation_request.end_date.strftime("%Y-%m-%d") if isinstance(vacation_request.end_date, datetime) else str(vacation_request.end_date.date())
        
        for approver in approvers:
            notification = create_notification(
                user_id=approver.id,
                title="Új szabadság igénylés / New Vacation Request",
                message=f"{user_name} szabadság igényt adott le: {start_date_str} - {end_date_str} ({vacation_request.days_count} nap) / {user_name} requested vacation: {start_date_str} - {end_date_str} ({vacation_request.days_count} days)",
                notification_type="info",
                related_entity_type="VacationRequest",
                related_entity_id=vacation_request_id,
                session=session
            )
            notifications.append(notification)
        
        logger.info(f"Vacation request notifications sent to {len(notifications)} approvers")
        return notifications
        
    except Exception as e:
        logger.error(f"Error sending vacation request notifications: {e}")
        raise NotificationServiceError(f"Error sending notifications: {str(e)}")
    finally:
        if should_close:
            session.close()


def check_and_create_pm_notifications(session: Session = None):
    """
    Create notifications for due PM tasks
    
    Creates notifications for:
    - Tasks due in 3 days
    - Overdue tasks
    """
    session, should_close = _get_session(session)
    try:
        now = utcnow()
        due_soon = now + timedelta(days=3)
        
        # Tasks due soon (3 days)
        tasks_due_soon = session.query(PMTask).filter(
            PMTask.is_active == True  # noqa: E712
        ).filter(
            PMTask.status == "pending"
        ).filter(
            PMTask.next_due_date <= due_soon,
            PMTask.next_due_date > now
        ).all()
        
        for task in tasks_due_soon:
            if task.assigned_to_user_id:
                create_notification(
                    user_id=task.assigned_to_user_id,
                    title=f"PM Task esedékes: {task.task_name}",
                    message=(
                        f"A '{task.task_name}' feladat "
                        f"{task.next_due_date.strftime('%Y-%m-%d')}-án esedékes."
                    ),
                    notification_type="warning",
                    related_entity_type="PMTask",
                    related_entity_id=task.id,
                    session=session
                )
        
        # Overdue tasks
        overdue_tasks = session.query(PMTask).filter(
            PMTask.is_active == True  # noqa: E712
        ).filter(
            PMTask.status == "overdue"
        ).all()
        
        for task in overdue_tasks:
            if task.assigned_to_user_id:
                days_overdue = (now.date() - task.next_due_date.date()).days
                create_notification(
                    user_id=task.assigned_to_user_id,
                    title=f"PM Task késésben: {task.task_name}",
                    message=(
                        f"A '{task.task_name}' feladat "
                        f"{days_overdue} napja késésben van."
                    ),
                    notification_type="error",
                    related_entity_type="PMTask",
                    related_entity_id=task.id,
                    session=session
                )
        
        session.commit()
        logger.info(
            f"Created notifications: {len(tasks_due_soon)} due soon, "
            f"{len(overdue_tasks)} overdue"
        )
    finally:
        if should_close:
            session.close()


def notify_worksheet_status_change(
    worksheet_id: int,
    old_status: str,
    new_status: str,
    assigned_user_id: int,
    session: Session = None
):
    """Create notification for worksheet status change"""
    session, should_close = _get_session(session)
    try:
        worksheet = session.query(Worksheet).filter_by(id=worksheet_id).first()
        if not worksheet:
            return
        
        create_notification(
            user_id=assigned_user_id,
            title=f"Munkalap státusz változás: {worksheet.title}",
            message=(
                f"A munkalap státusza '{old_status}' → '{new_status}' "
                f"változott."
            ),
            notification_type="info",
            related_entity_type="Worksheet",
            related_entity_id=worksheet_id,
            session=session
        )
        session.commit()
    finally:
        if should_close:
            session.close()


# ============================================================================
# Helper functions for role-based user queries
# ============================================================================

def get_users_by_roles(role_names: List[str], session: Session = None) -> List[User]:
    """
    Get all active users with the specified roles
    
    Args:
        role_names: List of role names (e.g., ["Manager", "Műszakvezető - Karbantartó"])
        session: Database session
    
    Returns:
        List of User objects
    """
    session, should_close = _get_session(session)
    try:
        roles = session.query(Role).filter(Role.name.in_(role_names)).all()
        if not roles:
            logger.warning(f"No roles found for names: {role_names}")
            return []
        
        role_ids = [role.id for role in roles]
        users = session.query(User).filter(
            User.role_id.in_(role_ids),
            User.is_active == True  # noqa: E712
        ).all()
        
        return users
    finally:
        if should_close:
            session.close()


def get_shift_leaders_and_managers(session: Session = None) -> List[User]:
    """
    Get all shift leaders (supervisors) and managers
    
    Returns:
        List of User objects with Manager, Maintenance Supervisor, or Production Supervisor roles
    """
    role_names = [
        ROLE_MANAGER,
        ROLE_MAINTENANCE_SUPERVISOR,
        ROLE_PRODUCTION_SUPERVISOR
    ]
    return get_users_by_roles(role_names, session=session)


def get_all_active_users(session: Session = None) -> List[User]:
    """
    Get all active users
    
    Returns:
        List of all active User objects
    """
    session, should_close = _get_session(session)
    try:
        users = session.query(User).filter(
            User.is_active == True  # noqa: E712
        ).all()
        return users
    finally:
        if should_close:
            session.close()


# ============================================================================
# PM Task notification functions
# ============================================================================

def notify_pm_task_assigned(task_id: int, assigned_to_user_id: Optional[int], session: Session = None) -> List[Notification]:
    """
    Send notification when a PM task is assigned
    
    Args:
        task_id: PM task ID
        assigned_to_user_id: User ID to assign to, or None for global (all active users)
        session: Database session
    
    Returns:
        List of created Notification objects
    """
    from localization.translator import translator
    
    session, should_close = _get_session(session)
    notifications = []
    
    try:
        task = session.query(PMTask).filter_by(id=task_id).first()
        if not task:
            logger.warning(f"PM task {task_id} not found for notification")
            return []
        
        # Determine recipients
        if assigned_to_user_id is None:
            # Global assignment - notify all active users
            recipients = get_all_active_users(session=session)
            title = translator.get_text("notifications.pm_task_assigned_global", task_name=task.task_name)
            message = translator.get_text("notifications.pm_task_assigned_global_message", task_name=task.task_name)
        else:
            # Specific user assignment
            user = session.query(User).filter_by(id=assigned_to_user_id).first()
            if not user:
                logger.warning(f"User {assigned_to_user_id} not found for PM task notification")
                return []
            recipients = [user]
            title = translator.get_text("notifications.pm_task_assigned", task_name=task.task_name)
            message = translator.get_text("notifications.pm_task_assigned_message", task_name=task.task_name)
        
        # Create notifications for each recipient
        for recipient in recipients:
            try:
                notification = create_notification(
                    user_id=recipient.id,
                    title=title,
                    message=message,
                    notification_type="info",
                    related_entity_type="PMTask",
                    related_entity_id=task_id,
                    session=session
                )
                notifications.append(notification)
            except Exception as e:
                logger.error(f"Error creating notification for user {recipient.id}: {e}")
        
        session.commit()
        logger.info(f"PM task assignment notifications sent to {len(notifications)} users")
        return notifications
        
    except Exception as e:
        logger.error(f"Error sending PM task assignment notifications: {e}")
        return notifications
    finally:
        if should_close:
            session.close()


def notify_pm_task_completed(task_id: int, completed_by_user_id: int, session: Session = None) -> List[Notification]:
    """
    Send notification when a PM task is completed
    
    Notifies:
    - The user who completed the task
    - All shift leaders and managers
    
    Args:
        task_id: PM task ID
        completed_by_user_id: User ID who completed the task
        session: Database session
    
    Returns:
        List of created Notification objects
    """
    from localization.translator import translator
    
    session, should_close = _get_session(session)
    notifications = []
    
    try:
        task = session.query(PMTask).filter_by(id=task_id).first()
        if not task:
            logger.warning(f"PM task {task_id} not found for notification")
            return []
        
        completed_user = session.query(User).filter_by(id=completed_by_user_id).first()
        if not completed_user:
            logger.warning(f"User {completed_by_user_id} not found for PM task notification")
            return []
        
        # Get shift leaders and managers
        supervisors = get_shift_leaders_and_managers(session=session)
        
        # Collect all recipients (completed user + supervisors, avoiding duplicates)
        recipient_ids = {completed_by_user_id}
        for supervisor in supervisors:
            recipient_ids.add(supervisor.id)
        
        recipients = session.query(User).filter(User.id.in_(recipient_ids)).all()
        
        # Create notifications
        completed_user_name = completed_user.full_name or completed_user.username
        task_name = task.task_name
        
        for recipient in recipients:
            try:
                if recipient.id == completed_by_user_id:
                    # Notification for the user who completed
                    title = translator.get_text("notifications.pm_task_completed", task_name=task_name)
                    message = translator.get_text("notifications.pm_task_completed_message", task_name=task_name)
                else:
                    # Notification for supervisors/managers
                    title = translator.get_text("notifications.pm_task_completed_supervisor", task_name=task_name)
                    message = translator.get_text(
                        "notifications.pm_task_completed_supervisor_message",
                        user_name=completed_user_name,
                        task_name=task_name
                    )
                
                notification = create_notification(
                    user_id=recipient.id,
                    title=title,
                    message=message,
                    notification_type="success",
                    related_entity_type="PMTask",
                    related_entity_id=task_id,
                    session=session
                )
                notifications.append(notification)
            except Exception as e:
                logger.error(f"Error creating notification for user {recipient.id}: {e}")
        
        session.commit()
        logger.info(f"PM task completion notifications sent to {len(notifications)} users")
        return notifications
        
    except Exception as e:
        logger.error(f"Error sending PM task completion notifications: {e}")
        return notifications
    finally:
        if should_close:
            session.close()


# ============================================================================
# Worksheet notification functions
# ============================================================================

def notify_worksheet_assigned(worksheet_id: int, session: Session = None) -> Optional[Notification]:
    """
    Send notification when a worksheet is assigned to a user
    
    Args:
        worksheet_id: Worksheet ID
        session: Database session
    
    Returns:
        Created Notification object or None
    """
    from localization.translator import translator
    
    session, should_close = _get_session(session)
    
    try:
        worksheet = session.query(Worksheet).filter_by(id=worksheet_id).first()
        if not worksheet:
            logger.warning(f"Worksheet {worksheet_id} not found for notification")
            return None
        
        if not worksheet.assigned_to_user_id:
            logger.warning(f"Worksheet {worksheet_id} has no assigned user")
            return None
        
        title = translator.get_text("notifications.worksheet_assigned", worksheet_title=worksheet.title)
        message = translator.get_text("notifications.worksheet_assigned_message", worksheet_title=worksheet.title)
        
        notification = create_notification(
            user_id=worksheet.assigned_to_user_id,
            title=title,
            message=message,
            notification_type="info",
            related_entity_type="Worksheet",
            related_entity_id=worksheet_id,
            session=session
        )
        
        session.commit()
        logger.info(f"Worksheet assignment notification sent to user {worksheet.assigned_to_user_id}")
        return notification
        
    except Exception as e:
        logger.error(f"Error sending worksheet assignment notification: {e}")
        return None
    finally:
        if should_close:
            session.close()


def notify_worksheet_closed(worksheet_id: int, closed_by_user_id: int, session: Session = None) -> List[Notification]:
    """
    Send notification when a worksheet is closed
    
    Notifies:
    - The user who closed the worksheet
    - All shift leaders and managers
    
    Args:
        worksheet_id: Worksheet ID
        closed_by_user_id: User ID who closed the worksheet
        session: Database session
    
    Returns:
        List of created Notification objects
    """
    from localization.translator import translator
    
    session, should_close = _get_session(session)
    notifications = []
    
    try:
        worksheet = session.query(Worksheet).filter_by(id=worksheet_id).first()
        if not worksheet:
            logger.warning(f"Worksheet {worksheet_id} not found for notification")
            return []
        
        closed_user = session.query(User).filter_by(id=closed_by_user_id).first()
        if not closed_user:
            logger.warning(f"User {closed_by_user_id} not found for worksheet notification")
            return []
        
        # Get shift leaders and managers
        supervisors = get_shift_leaders_and_managers(session=session)
        
        # Collect all recipients (closed user + supervisors, avoiding duplicates)
        recipient_ids = {closed_by_user_id}
        for supervisor in supervisors:
            recipient_ids.add(supervisor.id)
        
        recipients = session.query(User).filter(User.id.in_(recipient_ids)).all()
        
        # Create notifications
        closed_user_name = closed_user.full_name or closed_user.username
        worksheet_title = worksheet.title
        
        for recipient in recipients:
            try:
                if recipient.id == closed_by_user_id:
                    # Notification for the user who closed
                    title = translator.get_text("notifications.worksheet_closed", worksheet_title=worksheet_title)
                    message = translator.get_text("notifications.worksheet_closed_message", worksheet_title=worksheet_title)
                else:
                    # Notification for supervisors/managers
                    title = translator.get_text("notifications.worksheet_closed_supervisor", worksheet_title=worksheet_title)
                    message = translator.get_text(
                        "notifications.worksheet_closed_supervisor_message",
                        user_name=closed_user_name,
                        worksheet_title=worksheet_title
                    )
                
                notification = create_notification(
                    user_id=recipient.id,
                    title=title,
                    message=message,
                    notification_type="success",
                    related_entity_type="Worksheet",
                    related_entity_id=worksheet_id,
                    session=session
                )
                notifications.append(notification)
            except Exception as e:
                logger.error(f"Error creating notification for user {recipient.id}: {e}")
        
        session.commit()
        logger.info(f"Worksheet closed notifications sent to {len(notifications)} users")
        return notifications
        
    except Exception as e:
        logger.error(f"Error sending worksheet closed notifications: {e}")
        return notifications
    finally:
        if should_close:
            session.close()
