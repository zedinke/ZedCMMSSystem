"""
Settings service for application settings
"""

from typing import Optional, List
from pathlib import Path
from sqlalchemy.orm import Session
import json

from database.session_manager import SessionLocal
from database.models import AppSetting, utcnow
from config.app_config import TEMPLATES_DIR

import logging

logger = logging.getLogger(__name__)


def _get_session(session: Optional[Session]) -> (Session, bool):
    if session is None:
        return SessionLocal(), True
    return session, False


def get_setting(key: str, default_value: Optional[str] = None, session: Session = None) -> Optional[str]:
    """Get a setting value by key"""
    session, should_close = _get_session(session)
    try:
        setting = session.query(AppSetting).filter_by(key=key).first()
        if setting:
            return setting.value
        return default_value
    finally:
        if should_close:
            session.close()


def set_setting(key: str, value: str, description: Optional[str] = None, session: Session = None) -> AppSetting:
    """Set or update a setting"""
    session, should_close = _get_session(session)
    try:
        setting = session.query(AppSetting).filter_by(key=key).first()
        if setting:
            setting.value = value
            if description:
                setting.description = description
            setting.updated_at = utcnow()
        else:
            setting = AppSetting(
                key=key,
                value=value,
                description=description,
                updated_at=utcnow(),
            )
            session.add(setting)
        session.commit()
        logger.info(f"Setting {key} updated")
        return setting
    finally:
        if should_close:
            session.close()


def get_maintenance_notification_settings(session: Session = None) -> dict:
    """Get maintenance notification settings"""
    return {
        'months_ahead': int(get_setting('maintenance_notification_months', '1', session) or '1'),
        'weeks_ahead': int(get_setting('maintenance_notification_weeks', '0', session) or '0'),
        'days_ahead': int(get_setting('maintenance_notification_days', '0', session) or '0'),
        'hours_ahead': int(get_setting('maintenance_notification_hours', '0', session) or '0'),
    }


def set_maintenance_notification_settings(
    months: int = 0,
    weeks: int = 0,
    days: int = 0,
    hours: int = 0,
    session: Session = None
) -> dict:
    """Set maintenance notification settings"""
    set_setting('maintenance_notification_months', str(months), 'Hónapok száma előrejelzéshez', session)
    set_setting('maintenance_notification_weeks', str(weeks), 'Hetek száma előrejelzéshez', session)
    set_setting('maintenance_notification_days', str(days), 'Napok száma előrejelzéshez', session)
    set_setting('maintenance_notification_hours', str(hours), 'Órák száma előrejelzéshez', session)
    return get_maintenance_notification_settings(session)


def get_operating_hours_notification_settings(session: Session = None) -> dict:
    """Get operating hours correction notification settings"""
    return {
        'months_ahead': int(get_setting('operating_hours_notification_months', '0', session) or '0'),
        'weeks_ahead': int(get_setting('operating_hours_notification_weeks', '0', session) or '0'),
        'days_ahead': int(get_setting('operating_hours_notification_days', '7', session) or '7'),
        'hours_ahead': int(get_setting('operating_hours_notification_hours', '0', session) or '0'),
    }


def set_operating_hours_notification_settings(
    months: int = 0,
    weeks: int = 0,
    days: int = 0,
    hours: int = 0,
    session: Session = None
) -> dict:
    """Set operating hours correction notification settings"""
    set_setting('operating_hours_notification_months', str(months), 'Hónapok száma üzemóra korrekció figyelmeztetéshez', session)
    set_setting('operating_hours_notification_weeks', str(weeks), 'Hetek száma üzemóra korrekció figyelmeztetéshez', session)
    set_setting('operating_hours_notification_days', str(days), 'Napok száma üzemóra korrekció figyelmeztetéshez', session)
    set_setting('operating_hours_notification_hours', str(hours), 'Órák száma üzemóra korrekció figyelmeztetéshez', session)
    return get_operating_hours_notification_settings(session)


def list_docx_templates() -> List[Path]:
    """List all .docx template files in the templates directory"""
    try:
        if not TEMPLATES_DIR.exists():
            TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
        return sorted([p for p in TEMPLATES_DIR.iterdir() if p.suffix.lower() == '.docx'])
    except Exception as e:
        logger.error(f"Error listing docx templates: {e}")
        return []


def get_selected_worksheet_template(session: Session = None) -> Optional[Path]:
    """Get the selected worksheet template path"""
    template_path_str = get_setting('selected_worksheet_template', None, session)
    if template_path_str:
        try:
            template_path = Path(template_path_str)
            if template_path.exists() and template_path.suffix.lower() == '.docx':
                return template_path
        except Exception as e:
            logger.error(f"Error parsing template path: {e}")
    return None


def set_selected_worksheet_template(template_path: Path, session: Session = None) -> AppSetting:
    """Set the selected worksheet template path"""
    if not template_path.exists():
        raise ValueError(f"Template file not found: {template_path}")
    if template_path.suffix.lower() != '.docx':
        raise ValueError(f"Template must be a .docx file: {template_path}")
    return set_setting('selected_worksheet_template', str(template_path), 'Kiválasztott worksheet sablon', session)


def get_selected_work_request_template(session: Session = None) -> Optional[Path]:
    """Get the selected work request template path"""
    template_path_str = get_setting('selected_work_request_template', None, session)
    if template_path_str:
        try:
            template_path = Path(template_path_str)
            if template_path.exists() and template_path.suffix.lower() == '.docx':
                return template_path
        except Exception as e:
            logger.error(f"Error parsing work request template path: {e}")
    return None


def set_selected_work_request_template(template_path: Path, session: Session = None) -> AppSetting:
    """Set the selected work request template path"""
    if not template_path.exists():
        raise ValueError(f"Template file not found: {template_path}")
    if template_path.suffix.lower() != '.docx':
        raise ValueError(f"Template must be a .docx file: {template_path}")
    return set_setting('selected_work_request_template', str(template_path), 'Kiválasztott munkaigénylő lap sablon', session)


def get_selected_storage_receipt_template(session: Session = None) -> Optional[Path]:
    """Get the selected storage receipt template path"""
    template_path_str = get_setting('selected_storage_receipt_template', None, session)
    if template_path_str:
        try:
            template_path = Path(template_path_str)
            if template_path.exists() and template_path.suffix.lower() == '.docx':
                return template_path
        except Exception as e:
            logger.error(f"Error parsing storage receipt template path: {e}")
    return None


def set_selected_storage_receipt_template(template_path: Path, session: Session = None) -> AppSetting:
    """Set the selected storage receipt template path"""
    if not template_path.exists():
        raise ValueError(f"Template file not found: {template_path}")
    if template_path.suffix.lower() != '.docx':
        raise ValueError(f"Template must be a .docx file: {template_path}")
    return set_setting('selected_storage_receipt_template', str(template_path), 'Kiválasztott betárazás sablon', session)


def get_selected_storage_transfer_template(session: Session = None) -> Optional[Path]:
    """Get the selected storage transfer template path"""
    template_path_str = get_setting('selected_storage_transfer_template', None, session)
    if template_path_str:
        try:
            template_path = Path(template_path_str)
            if template_path.exists() and template_path.suffix.lower() == '.docx':
                return template_path
        except Exception as e:
            logger.error(f"Error parsing storage transfer template path: {e}")
    return None


def set_selected_storage_transfer_template(template_path: Path, session: Session = None) -> AppSetting:
    """Set the selected storage transfer template path"""
    if not template_path.exists():
        raise ValueError(f"Template file not found: {template_path}")
    if template_path.suffix.lower() != '.docx':
        raise ValueError(f"Template must be a .docx file: {template_path}")
    return set_setting('selected_storage_transfer_template', str(template_path), 'Kiválasztott áttárazás sablon', session)


def get_selected_qr_label_template(session: Session = None) -> Optional[Path]:
    """Get the selected QR label template path"""
    template_path_str = get_setting('selected_qr_label_template', None, session)
    if template_path_str:
        try:
            template_path = Path(template_path_str)
            if template_path.exists() and template_path.suffix.lower() == '.docx':
                return template_path
        except Exception as e:
            logger.error(f"Error parsing QR label template path: {e}")
    return None


def set_selected_qr_label_template(template_path: Path, session: Session = None) -> AppSetting:
    """Set the selected QR label template path"""
    if not template_path.exists():
        raise ValueError(f"Template file not found: {template_path}")
    if template_path.suffix.lower() != '.docx':
        raise ValueError(f"Template must be a .docx file: {template_path}")
    return set_setting('selected_qr_label_template', str(template_path), 'Kiválasztott QR címke sablon', session)


def get_worksheet_name_format(session: Session = None) -> str:
    """Get the worksheet name format template"""
    # Default format: "Munkalap - {user_name} - #{worksheet_id}"
    default_format = "Munkalap - {user_name} - #{worksheet_id}"
    return get_setting('worksheet_name_format', default_format, session) or default_format


def set_worksheet_name_format(format_template: str, session: Session = None) -> AppSetting:
    """Set the worksheet name format template
    
    Available variables:
    - {worksheet_name}: Base name (e.g., "Munkalap")
    - {user_name}: Assigned user's full name or username
    - {worksheet_id}: Worksheet ID number
    """
    return set_setting('worksheet_name_format', format_template, 'Munkalap névformátum sablon', session)


def get_selected_scrapping_template(session: Session = None) -> Optional[Path]:
    """Get the selected scrapping template path"""
    template_path_str = get_setting('selected_scrapping_template', None, session)
    if template_path_str:
        try:
            template_path = Path(template_path_str)
            if template_path.exists() and template_path.suffix.lower() == '.docx':
                return template_path
        except Exception as e:
            logger.error(f"Error parsing scrapping template path: {e}")
    return None


def set_selected_scrapping_template(template_path: Path, session: Session = None) -> AppSetting:
    """Set the selected scrapping template path"""
    if not template_path.exists():
        raise ValueError(f"Template file not found: {template_path}")
    if template_path.suffix.lower() != '.docx':
        raise ValueError(f"Template must be a .docx file: {template_path}")
    return set_setting('selected_scrapping_template', str(template_path), 'Kiválasztott selejtezési sablon', session)


def get_log_archive_years(session: Session = None) -> int:
    """Get log archive years setting (default: 1)"""
    value = get_setting('log_archive_years', '1', session)
    try:
        return int(value) if value else 1
    except (ValueError, TypeError):
        return 1


def set_log_archive_years(years: int, session: Session = None) -> AppSetting:
    """Set log archive years setting"""
    if years < 0:
        raise ValueError("Archive years must be non-negative")
    return set_setting('log_archive_years', str(years), 'Log archiválási időszak (év)', session)


def get_log_delete_years(session: Session = None) -> int:
    """Get log delete years setting (default: 2)"""
    value = get_setting('log_delete_years', '2', session)
    try:
        return int(value) if value else 2
    except (ValueError, TypeError):
        return 2


def set_log_delete_years(years: int, session: Session = None) -> AppSetting:
    """Set log delete years setting"""
    if years < 0:
        raise ValueError("Delete years must be non-negative")
    return set_setting('log_delete_years', str(years), 'Log törlési időszak (év)', session)


def get_auto_generate_scrapping_doc(session: Session = None) -> bool:
    """Get auto-generate scrapping document setting (default: True)"""
    value = get_setting('auto_generate_scrapping_doc', 'true', session)
    return value.lower() in ('true', '1', 'yes', 'on')


def get_selected_vacation_template(session: Session = None) -> Optional[Path]:
    """Get the selected vacation document template path"""
    template_path_str = get_setting('vacation_document_template', None, session)
    if template_path_str:
        try:
            template_path = Path(template_path_str)
            if template_path.exists() and template_path.suffix.lower() == '.docx':
                return template_path
        except Exception as e:
            logger.error(f"Error parsing vacation template path: {e}")
    return None


def set_selected_vacation_template(template_path: Path, session: Session = None) -> AppSetting:
    """Set the selected vacation document template path"""
    if not template_path.exists():
        raise ValueError(f"Template file not found: {template_path}")
    if template_path.suffix.lower() != '.docx':
        raise ValueError(f"Template must be a .docx file: {template_path}")
    return set_setting('vacation_document_template', str(template_path), 'Kiválasztott szabadság dokumentum sablon', session)


def set_auto_generate_scrapping_doc(enabled: bool, session: Session = None) -> AppSetting:
    """Set auto-generate scrapping document setting"""
    return set_setting('auto_generate_scrapping_doc', 'true' if enabled else 'false', 'Automatikus selejtezési lap generálás', session)


# Inventory Audit Excel Template Settings
def get_inventory_audit_excel_template_dir(session: Session = None) -> Optional[Path]:
    """Get the inventory audit Excel template directory"""
    template_dir_str = get_setting('inventory_audit_excel_template_dir', None, session)
    if template_dir_str:
        try:
            template_dir = Path(template_dir_str)
            if template_dir.exists() and template_dir.is_dir():
                return template_dir
        except Exception as e:
            logger.error(f"Error parsing inventory audit Excel template directory: {e}")
    # Default to templates directory
    from config.app_config import TEMPLATES_DIR
    return TEMPLATES_DIR / "excel_templates" if (TEMPLATES_DIR / "excel_templates").exists() else None


def set_inventory_audit_excel_template_dir(template_dir: Path, session: Session = None) -> AppSetting:
    """Set the inventory audit Excel template directory"""
    if not template_dir.exists():
        raise ValueError(f"Template directory not found: {template_dir}")
    if not template_dir.is_dir():
        raise ValueError(f"Path must be a directory: {template_dir}")
    return set_setting('inventory_audit_excel_template_dir', str(template_dir), 'Készletellenőrzés Excel sablon könyvtár', session)


def list_excel_templates(template_dir: Optional[Path] = None) -> List[Path]:
    """List all .xlsx template files in the template directory"""
    if template_dir is None:
        template_dir = get_inventory_audit_excel_template_dir()
    
    if template_dir is None:
        return []
    
    try:
        if not template_dir.exists():
            template_dir.mkdir(parents=True, exist_ok=True)
        return sorted([p for p in template_dir.iterdir() if p.suffix.lower() == '.xlsx'])
    except Exception as e:
        logger.error(f"Error listing Excel templates: {e}")
        return []


# Update Settings
def get_auto_update_check(session: Session = None) -> bool:
    """Get auto update check setting (default: False)"""
    value = get_setting('auto_update_check', 'false', session)
    return value.lower() in ('true', '1', 'yes', 'on')


def set_auto_update_check(enabled: bool, session: Session = None) -> AppSetting:
    """Set auto update check setting"""
    return set_setting('auto_update_check', 'true' if enabled else 'false', 'Automatikus frissítés ellenőrzés', session)


def get_update_check_frequency(session: Session = None) -> str:
    """Get update check frequency setting (default: 'startup')"""
    return get_setting('update_check_frequency', 'startup', session) or 'startup'


def set_update_check_frequency(frequency: str, session: Session = None) -> AppSetting:
    """Set update check frequency ('startup', 'daily', 'weekly')"""
    if frequency not in ('startup', 'daily', 'weekly'):
        raise ValueError("Frequency must be 'startup', 'daily', or 'weekly'")
    return set_setting('update_check_frequency', frequency, 'Frissítés ellenőrzési gyakoriság', session)


def get_last_update_check(session: Session = None) -> Optional[str]:
    """Get last update check timestamp"""
    return get_setting('last_update_check', None, session)


def set_last_update_check(timestamp: str, session: Session = None) -> AppSetting:
    """Set last update check timestamp"""
    return set_setting('last_update_check', timestamp, 'Utolsó frissítés ellenőrzés időpontja', session)


def get_skip_version(session: Session = None) -> Optional[str]:
    """Get skipped version"""
    return get_setting('skip_version', None, session)


def set_skip_version(version: str, session: Session = None) -> AppSetting:
    """Set skipped version"""
    return set_setting('skip_version', version, 'Kihagyott verzió', session)


# GitHub Settings
def get_github_owner(session: Session = None) -> Optional[str]:
    """Get GitHub repository owner"""
    return get_setting('github_owner', None, session)


def set_github_owner(owner: str, session: Session = None) -> AppSetting:
    """Set GitHub repository owner"""
    return set_setting('github_owner', owner, 'GitHub repository tulajdonos', session)


def get_github_repo(session: Session = None) -> Optional[str]:
    """Get GitHub repository name"""
    return get_setting('github_repo', None, session)


def set_github_repo(repo: str, session: Session = None) -> AppSetting:
    """Set GitHub repository name"""
    return set_setting('github_repo', repo, 'GitHub repository név', session)


# PM Task Files Directory Settings
def get_pm_task_files_dir(session: Session = None) -> Optional[Path]:
    """Get the PM task files parent directory"""
    files_dir_str = get_setting('pm_task_files_dir', None, session)
    if files_dir_str:
        try:
            files_dir = Path(files_dir_str)
            if files_dir.exists() and files_dir.is_dir():
                return files_dir
        except Exception as e:
            logger.error(f"Error parsing PM task files directory: {e}")
    # Default to generated_pdfs/pm_tasks if not set
    from config.app_config import TEMPLATES_DIR
    default_dir = Path("generated_pdfs") / "pm_tasks"
    return default_dir


def set_pm_task_files_dir(files_dir: Path, session: Session = None) -> AppSetting:
    """Set the PM task files parent directory"""
    if not files_dir.exists():
        raise ValueError(f"Directory does not exist: {files_dir}")
    if not files_dir.is_dir():
        raise ValueError(f"Path must be a directory: {files_dir}")
    return set_setting('pm_task_files_dir', str(files_dir), 'PM task fájlok szülő könyvtára / PM task files parent directory', session)