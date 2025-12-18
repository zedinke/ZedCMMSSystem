"""
CMMS Audit Test Suite - Main Configuration
"""

import os
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Any

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
CMMS_PROJECT = PROJECT_ROOT / "CMMS_Project"
ANDROID_APP = PROJECT_ROOT / "AndroidApp"
AUDIT_ROOT = Path(__file__).parent
REPORTS_DIR = AUDIT_ROOT / "reports"
LOGS_DIR = AUDIT_ROOT / "logs"
TEST_DATA_DIR = AUDIT_ROOT / "test_data"

# Create necessary directories
for directory in [REPORTS_DIR, LOGS_DIR, TEST_DATA_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


@dataclass
class AuditConfig:
    """Main audit configuration"""

    # Database settings
    database_path: str = str(CMMS_PROJECT / "data" / "cmms.db")
    database_backup_path: str = str(CMMS_PROJECT / "data" / "system_backups")

    # API settings
    api_base_url: str = "http://116.203.226.140:8000/api"
    api_timeout: int = 30
    api_health_endpoint: str = "/health/"

    # Authentication
    test_admin_username: str = "a.geleta"
    test_admin_password: str = "Gele007ta"
    test_tech_username: str = "technician_test"
    test_tech_password: str = "Test1234!"

    # Android app settings
    android_package: str = "com.artence.cmms"
    android_apk_path: str = str(ANDROID_APP / "app" / "build" / "outputs" / "apk" / "debug" / "app-debug.apk")

    # Performance thresholds
    api_response_time_max: float = 2.0  # seconds
    ui_load_time_max: float = 1.0  # seconds
    db_query_time_max: float = 0.5  # seconds

    # Compliance thresholds
    min_pass_rate_functional: float = 0.95  # 95%
    min_pass_rate_iso9001: float = 1.0  # 100%
    min_pass_rate_iso55001: float = 1.0  # 100%
    min_pass_rate_gdpr: float = 1.0  # 100%
    min_pass_rate_security: float = 0.98  # 98%
    min_pass_rate_database: float = 1.0  # 100%
    min_pass_rate_performance: float = 0.90  # 90%
    min_pass_rate_ui_ux: float = 0.85  # 85%

    # Test settings
    parallel_execution: bool = False
    verbose_output: bool = True
    generate_html_report: bool = True
    generate_pdf_report: bool = False
    generate_excel_report: bool = False

    # Email notification (optional)
    send_email_on_failure: bool = False
    email_recipients: List[str] = None

    def __post_init__(self):
        if self.email_recipients is None:
            self.email_recipients = []


@dataclass
class TestCategory:
    """Test category definition"""
    id: str
    name: str
    description: str
    priority: int  # 1=Critical, 2=High, 3=Medium, 4=Low
    enabled: bool = True
    min_pass_rate: float = 0.95


# Audit test categories
AUDIT_CATEGORIES = {
    "functional": TestCategory(
        id="functional",
        name="Funkcionális Audit",
        description="Teljes CRUD funkcionális tesztelés minden modulra",
        priority=1,
        min_pass_rate=0.95
    ),
    "iso9001": TestCategory(
        id="iso9001",
        name="ISO 9001 Megfelelőség",
        description="Minőségirányítási rendszer követelmények",
        priority=1,
        min_pass_rate=1.0
    ),
    "iso55001": TestCategory(
        id="iso55001",
        name="ISO 55001 Megfelelőség",
        description="Eszközgazdálkodási rendszer követelmények",
        priority=1,
        min_pass_rate=1.0
    ),
    "gdpr": TestCategory(
        id="gdpr",
        name="GDPR Megfelelőség",
        description="Adatvédelmi rendelet megfelelőség",
        priority=1,
        min_pass_rate=1.0
    ),
    "security": TestCategory(
        id="security",
        name="Biztonsági Audit",
        description="Cyber security és access control tesztek",
        priority=1,
        min_pass_rate=0.98
    )
}


# Export config instance
config = AuditConfig()

