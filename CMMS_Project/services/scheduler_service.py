"""
Background task scheduler for CMMS
"""
import schedule
import threading
import time
from datetime import datetime
import logging

from services.pm_service import update_pm_task_statuses
from services.notification_service import check_and_create_pm_notifications

logger = logging.getLogger(__name__)

_scheduler_thread = None
_scheduler_running = False


def start_scheduler():
    """Start background scheduler"""
    global _scheduler_thread, _scheduler_running
    
    if _scheduler_running:
        logger.warning("Scheduler already running")
        return
    
    _scheduler_running = True
    
    # Schedule PM status updates (every hour)
    schedule.every().hour.do(_update_pm_statuses_job)
    
    # Schedule PM notifications (every 6 hours)
    schedule.every(6).hours.do(_create_pm_notifications_job)
    
    # Schedule daily cleanup (at 2 AM)
    schedule.every().day.at("02:00").do(_daily_cleanup_job)
    
    def run_scheduler():
        """Scheduler loop"""
        while _scheduler_running:
            try:
                schedule.run_pending()
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
            time.sleep(60)  # Check every minute
    
    _scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    _scheduler_thread.start()
    logger.info("Background scheduler started")


def stop_scheduler():
    """Stop background scheduler"""
    global _scheduler_running
    _scheduler_running = False
    schedule.clear()
    logger.info("Background scheduler stopped")


def _update_pm_statuses_job():
    """Job: Update PM task statuses"""
    try:
        logger.info("Running PM status update job")
        stats = update_pm_task_statuses()
        logger.info(f"PM status update completed: {stats}")
    except Exception as e:
        logger.error(f"PM status update job failed: {e}")


def _create_pm_notifications_job():
    """Job: Create PM notifications"""
    try:
        logger.info("Running PM notification job")
        check_and_create_pm_notifications()
        logger.info("PM notification job completed")
    except Exception as e:
        logger.error(f"PM notification job failed: {e}")


def _daily_cleanup_job():
    """Job: Daily cleanup tasks"""
    try:
        logger.info("Running daily cleanup job")
        # Add cleanup tasks here (old logs, expired sessions, etc.)
        # For now, just log
        logger.info("Daily cleanup job completed")
    except Exception as e:
        logger.error(f"Daily cleanup job failed: {e}")


