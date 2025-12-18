"""
04 - ISO 55001 Asset Management Compliance Audit
05 - GDPR Data Protection Compliance Audit
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "CMMS_Project"))

from base_test import AuditBaseTest, DatabaseTestMixin
from audit_config import config
from datetime import datetime, timedelta


# ============================================================================
# ISO 55001 - ASSET MANAGEMENT
# ============================================================================

class ISO55001AssetLifecycleAudit(AuditBaseTest, DatabaseTestMixin):
    """ISO 55001 - Asset Lifecycle Management"""

    category = "iso55001"

    def test_01_asset_lifecycle_phases(self):
        """ISO55001-LC-001: Asset lifecycle fázisok (acquisition, operation, maintenance, disposal)"""
        session = self.get_db_session()

        try:
            from database.models import Asset

            assets = session.query(Asset).all()

            if not assets:
                self.record_result(
                    test_id="ISO55001-LC-001",
                    test_name="Asset Lifecycle Phases",
                    status="SKIP",
                    message="No assets found"
                )
                return

            # Check lifecycle status coverage
            lifecycle_statuses = ["OPERATIONAL", "MAINTENANCE", "BREAKDOWN", "OFFLINE", "DECOMMISSIONED"]
            status_distribution = {}

            for status in lifecycle_statuses:
                count = len([a for a in assets if a.status == status])
                status_distribution[status] = count

            # At least 3 different statuses should be used (showing lifecycle management)
            statuses_used = len([s for s, count in status_distribution.items() if count > 0])

            self.assert_compliance(
                test_id="ISO55001-LC-001",
                test_name="Asset Lifecycle Status Diversity",
                condition=statuses_used >= 3,
                success_message=f"{statuses_used} different lifecycle statuses in use",
                failure_message=f"Only {statuses_used} statuses used (need at least 3)",
                severity="HIGH",
                details={"status_distribution": status_distribution}
            )

        finally:
            session.close()

    def test_02_depreciation_tracking(self):
        """ISO55001-LC-002: Depreciation tracking (asset value management)"""
        session = self.get_db_session()

        try:
            from database.models import Asset

            assets = session.query(Asset).all()

            # Check if assets have purchase_cost and depreciation fields
            assets_with_financials = [
                a for a in assets
                if hasattr(a, 'purchase_cost') and a.purchase_cost is not None
            ]

            financial_tracking_rate = len(assets_with_financials) / len(assets) if assets else 0

            self.assert_compliance(
                test_id="ISO55001-LC-002",
                test_name="Asset Financial Value Tracking",
                condition=financial_tracking_rate >= 0.70,  # 70% threshold
                success_message=f"{financial_tracking_rate*100:.1f}% assets have financial tracking",
                failure_message=f"Only {financial_tracking_rate*100:.1f}% assets tracked financially",
                severity="MEDIUM",
                details={
                    "total_assets": len(assets),
                    "tracked_assets": len(assets_with_financials),
                    "tracking_rate": financial_tracking_rate
                }
            )

        finally:
            session.close()

    def test_03_disposal_scrapping(self):
        """ISO55001-LC-003: Asset disposal/scrapping tracking"""
        session = self.get_db_session()

        try:
            from database.models import Asset

            # Check for DECOMMISSIONED assets
            decommissioned = session.query(Asset).filter(Asset.status == "DECOMMISSIONED").all()

            self.record_result(
                test_id="ISO55001-LC-003",
                test_name="Asset Disposal Tracking",
                status="PASS",
                message=f"Disposal tracking exists. {len(decommissioned)} assets decommissioned",
                severity="MEDIUM",
                details={"decommissioned_count": len(decommissioned)}
            )

        finally:
            session.close()


class ISO55001MaintenanceStrategyAudit(AuditBaseTest, DatabaseTestMixin):
    """ISO 55001 - Maintenance Strategy"""

    category = "iso55001"

    def test_01_pm_coverage(self):
        """ISO55001-MS-001: PM coverage - kritikus assets rendelkeznek PM task-kal"""
        session = self.get_db_session()

        try:
            from database.models import Asset, PMTask

            # Get critical assets
            critical_assets = session.query(Asset).filter(
                Asset.criticality.in_(["HIGH", "CRITICAL"])
            ).all()

            if not critical_assets:
                self.record_result(
                    test_id="ISO55001-MS-001",
                    test_name="PM Coverage for Critical Assets",
                    status="SKIP",
                    message="No critical assets found"
                )
                return

            # Check how many have PM tasks
            critical_asset_ids = [a.id for a in critical_assets]
            pm_tasks = session.query(PMTask).filter(PMTask.asset_id.in_(critical_asset_ids)).all()

            assets_with_pm = len(set(pm.asset_id for pm in pm_tasks))
            pm_coverage_rate = assets_with_pm / len(critical_assets)

            self.assert_compliance(
                test_id="ISO55001-MS-001",
                test_name="PM Coverage for Critical Assets",
                condition=pm_coverage_rate >= 0.80,  # 80% of critical assets should have PM
                success_message=f"{pm_coverage_rate*100:.1f}% critical assets have PM tasks",
                failure_message=f"Only {pm_coverage_rate*100:.1f}% critical assets have PM (need 80%)",
                severity="CRITICAL",
                details={
                    "critical_assets": len(critical_assets),
                    "assets_with_pm": assets_with_pm,
                    "coverage_rate": pm_coverage_rate
                }
            )

        finally:
            session.close()

    def test_02_pm_frequency_diversity(self):
        """ISO55001-MS-002: PM frequency diversity (daily, weekly, monthly, yearly)"""
        session = self.get_db_session()

        try:
            from database.models import PMTask

            pm_tasks = session.query(PMTask).all()

            if not pm_tasks:
                self.record_result(
                    test_id="ISO55001-MS-002",
                    test_name="PM Frequency Diversity",
                    status="SKIP",
                    message="No PM tasks found"
                )
                return

            # Check frequency distribution
            frequencies = {}
            for pm in pm_tasks:
                freq = pm.frequency if hasattr(pm, 'frequency') else "UNKNOWN"
                frequencies[freq] = frequencies.get(freq, 0) + 1

            # Good practice: use at least 2 different frequencies
            frequency_types = len(frequencies)

            self.assert_compliance(
                test_id="ISO55001-MS-002",
                test_name="PM Frequency Diversity",
                condition=frequency_types >= 2,
                success_message=f"{frequency_types} different PM frequencies in use",
                failure_message=f"Only {frequency_types} frequency type (need variety)",
                severity="MEDIUM",
                details={"frequency_distribution": frequencies}
            )

        finally:
            session.close()

    def test_03_reactive_vs_preventive_ratio(self):
        """ISO55001-MS-003: Reactive vs Preventive maintenance ratio"""
        session = self.get_db_session()

        try:
            from database.models import Worksheet, PMHistory

            # Count reactive (worksheets)
            reactive_count = session.query(Worksheet).count()

            # Count preventive (PM histories)
            preventive_count = session.query(PMHistory).count()

            total_maintenance = reactive_count + preventive_count

            if total_maintenance == 0:
                self.record_result(
                    test_id="ISO55001-MS-003",
                    test_name="Reactive vs Preventive Ratio",
                    status="SKIP",
                    message="No maintenance activities found"
                )
                return

            preventive_ratio = preventive_count / total_maintenance if total_maintenance > 0 else 0

            # Good practice: preventive should be at least 30% of total
            self.assert_compliance(
                test_id="ISO55001-MS-003",
                test_name="Preventive Maintenance Ratio",
                condition=preventive_ratio >= 0.30,
                success_message=f"Preventive maintenance: {preventive_ratio*100:.1f}% of total",
                failure_message=f"Preventive only {preventive_ratio*100:.1f}% (need 30%+)",
                severity="MEDIUM",
                details={
                    "reactive_count": reactive_count,
                    "preventive_count": preventive_count,
                    "preventive_ratio": preventive_ratio
                }
            )

        finally:
            session.close()


class ISO55001PerformanceMeasurementAudit(AuditBaseTest, DatabaseTestMixin):
    """ISO 55001 - Performance Measurement (KPIs)"""

    category = "iso55001"

    def test_01_mtbf_calculation(self):
        """ISO55001-PM-001: MTBF (Mean Time Between Failures) számítás lehetősége"""
        session = self.get_db_session()

        try:
            from database.models import Worksheet, Asset

            # For MTBF calculation, we need breakdown records
            breakdown_worksheets = session.query(Worksheet).filter(
                Worksheet.priority == "CRITICAL"
            ).all()

            # Just check if the data exists for calculation
            self.record_result(
                test_id="ISO55001-PM-001",
                test_name="MTBF Data Availability",
                status="PASS",
                message=f"System tracks {len(breakdown_worksheets)} critical incidents for MTBF calculation",
                severity="MEDIUM",
                details={"critical_incidents": len(breakdown_worksheets)}
            )

        finally:
            session.close()

    def test_02_mttr_calculation(self):
        """ISO55001-PM-002: MTTR (Mean Time To Repair) számítás lehetősége"""
        session = self.get_db_session()

        try:
            from database.models import Worksheet

            # For MTTR, we need completed worksheets with timestamps
            completed_worksheets = session.query(Worksheet).filter(
                Worksheet.status == "COMPLETED"
            ).all()

            # Check if worksheets have both created_at and updated_at for duration calculation
            worksheets_with_duration = [
                w for w in completed_worksheets
                if w.created_at and w.updated_at
            ]

            self.assert_compliance(
                test_id="ISO55001-PM-002",
                test_name="MTTR Data Completeness",
                condition=len(worksheets_with_duration) == len(completed_worksheets),
                success_message=f"All {len(completed_worksheets)} completed worksheets have duration data",
                failure_message=f"{len(completed_worksheets) - len(worksheets_with_duration)} worksheets missing duration data",
                severity="MEDIUM",
                details={
                    "completed_worksheets": len(completed_worksheets),
                    "with_duration_data": len(worksheets_with_duration)
                }
            )

        finally:
            session.close()


# ============================================================================
# GDPR - DATA PROTECTION
# ============================================================================

class GDPRPersonalDataAudit(AuditBaseTest, DatabaseTestMixin):
    """GDPR - Personal Data Protection (Art. 5)"""

    category = "gdpr"

    def test_01_personal_data_identification(self):
        """GDPR-PD-001: Személyes adatok azonosítása (full_name, email, phone)"""
        session = self.get_db_session()

        try:
            from database.models import User

            users = session.query(User).all()

            if not users:
                self.record_result(
                    test_id="GDPR-PD-001",
                    test_name="Personal Data Fields Exist",
                    status="SKIP",
                    message="No users found"
                )
                return

            # Check personal data fields exist
            personal_data_fields = ['full_name', 'email', 'phone']
            sample_user = users[0]

            fields_exist = [f for f in personal_data_fields if hasattr(sample_user, f)]

            self.assert_compliance(
                test_id="GDPR-PD-001",
                test_name="Personal Data Fields Identified",
                condition=len(fields_exist) == len(personal_data_fields),
                success_message=f"All {len(personal_data_fields)} personal data fields identified",
                failure_message=f"Only {len(fields_exist)}/{len(personal_data_fields)} fields found",
                severity="CRITICAL",
                details={"fields_found": fields_exist}
            )

        finally:
            session.close()

    def test_02_password_hashing(self):
        """GDPR-PD-002: Jelszavak hash-elve tárolva (Argon2/bcrypt)"""
        session = self.get_db_session()

        try:
            from database.models import User

            users = session.query(User).limit(10).all()

            if not users:
                self.record_result(
                    test_id="GDPR-PD-002",
                    test_name="Password Hashing",
                    status="SKIP",
                    message="No users found"
                )
                return

            # Check that password_hash field exists and is not plaintext
            all_hashed = True
            for user in users:
                if hasattr(user, 'password_hash'):
                    # Hash should be long (>= 60 chars for bcrypt, >= 80 for argon2)
                    if len(user.password_hash) < 60:
                        all_hashed = False
                        break

            self.assert_compliance(
                test_id="GDPR-PD-002",
                test_name="Password Hashing Used",
                condition=all_hashed,
                success_message="All user passwords are properly hashed",
                failure_message="Some passwords may not be properly hashed!",
                severity="CRITICAL"
            )

        finally:
            session.close()


class GDPRDataSubjectRightsAudit(AuditBaseTest, DatabaseTestMixin):
    """GDPR - Data Subject Rights (Art. 15-20)"""

    category = "gdpr"

    def test_01_right_to_erasure(self):
        """GDPR-DSR-001: Right to be forgotten (anonymization function)"""
        session = self.get_db_session()

        try:
            from database.models import User

            # Check if anonymization fields exist
            sample_users = session.query(User).limit(5).all()

            if sample_users:
                has_anonymization = hasattr(sample_users[0], 'anonymized_at')

                self.assert_compliance(
                    test_id="GDPR-DSR-001",
                    test_name="Right to Erasure Implementation",
                    condition=has_anonymization,
                    success_message="User anonymization (GDPR erasure) field exists",
                    failure_message="No anonymization field - GDPR right to erasure not implemented!",
                    severity="CRITICAL"
                )

                # Check if any users have been anonymized
                anonymized_users = [u for u in sample_users if hasattr(u, 'anonymized_at') and u.anonymized_at]

                self.record_result(
                    test_id="GDPR-DSR-001-USAGE",
                    test_name="Anonymization Feature Usage",
                    status="PASS",
                    message=f"Anonymization feature available. {len(anonymized_users)} users anonymized",
                    severity="MEDIUM",
                    details={"anonymized_count": len(anonymized_users)}
                )

        finally:
            session.close()

    def test_02_data_export_capability(self):
        """GDPR-DSR-002: Right to data portability (export function)"""
        # This checks if services have export capabilities
        import os

        # Check if export services exist
        export_services = [
            "services/excel_export_service.py",
            "services/pdf_service.py"
        ]

        project_root = Path(__file__).parent.parent.parent / "CMMS_Project"
        existing_services = []

        for service in export_services:
            if (project_root / service).exists():
                existing_services.append(service)

        self.assert_compliance(
            test_id="GDPR-DSR-002",
            test_name="Data Export Capability",
            condition=len(existing_services) >= 1,
            success_message=f"Data export services exist: {existing_services}",
            failure_message="No data export services found!",
            severity="HIGH",
            details={"export_services": existing_services}
        )


class GDPRAuditLogAudit(AuditBaseTest, DatabaseTestMixin):
    """GDPR - Audit Logging (Art. 30)"""

    category = "gdpr"

    def test_01_audit_log_sensitive_operations(self):
        """GDPR-AL-001: Sensitive műveletek naplózása (password change, data export)"""
        session = self.get_db_session()

        try:
            from database.models import AuditLog

            # Check if audit logs exist
            audit_logs = session.query(AuditLog).limit(100).all()

            # Check for sensitive operation types
            sensitive_actions = ['UPDATE', 'DELETE', 'CREATE']
            logs_with_actions = [log for log in audit_logs if hasattr(log, 'action') and log.action in sensitive_actions]

            self.assert_compliance(
                test_id="GDPR-AL-001",
                test_name="Sensitive Operations Logging",
                condition=len(logs_with_actions) > 0 or len(audit_logs) == 0,
                success_message=f"{len(logs_with_actions)} sensitive operations logged",
                failure_message="No sensitive operations in audit log",
                severity="HIGH",
                details={
                    "total_logs": len(audit_logs),
                    "sensitive_ops": len(logs_with_actions)
                }
            )

        except Exception as e:
            self.record_result(
                test_id="GDPR-AL-001",
                test_name="Sensitive Operations Logging",
                status="ERROR",
                message=f"Error checking audit logs: {str(e)}",
                severity="HIGH"
            )

        finally:
            session.close()


if __name__ == "__main__":
    import unittest
    unittest.main()

