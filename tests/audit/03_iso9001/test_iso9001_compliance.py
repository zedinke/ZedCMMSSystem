"""
03 - ISO 9001 Compliance Audit Tests
Quality Management System Requirements
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "CMMS_Project"))

from base_test import AuditBaseTest, DatabaseTestMixin, APITestMixin
from audit_config import config, ISO_9001_CHECKLIST
from datetime import datetime


class ISO9001DocumentControlAudit(AuditBaseTest, DatabaseTestMixin):
    """ISO 9001 - Document Control (4.2.3)"""

    category = "iso9001"

    def test_01_unique_identifiers(self):
        """ISO9001-DOC-001: Minden dokumentum egyedi azonosítóval rendelkezik"""
        session = self.get_db_session()

        try:
            # Check Assets
            from database.models import Asset
            assets = session.query(Asset).all()

            asset_ids = [a.id for a in assets]
            unique_ids = set(asset_ids)

            self.assert_compliance(
                test_id="ISO9001-DOC-001-ASSET",
                test_name="Asset Unique ID Constraint",
                condition=len(asset_ids) == len(unique_ids),
                success_message=f"All {len(assets)} assets have unique IDs",
                failure_message=f"Duplicate asset IDs found!",
                severity="CRITICAL",
                details={"total_assets": len(assets), "unique_ids": len(unique_ids)}
            )

            # Check Worksheets
            from database.models import Worksheet
            worksheets = session.query(Worksheet).all()

            ws_ids = [w.id for w in worksheets]
            unique_ws_ids = set(ws_ids)

            self.assert_compliance(
                test_id="ISO9001-DOC-001-WS",
                test_name="Worksheet Unique ID Constraint",
                condition=len(ws_ids) == len(unique_ws_ids),
                success_message=f"All {len(worksheets)} worksheets have unique IDs",
                failure_message=f"Duplicate worksheet IDs found!",
                severity="CRITICAL",
                details={"total_worksheets": len(worksheets), "unique_ids": len(unique_ws_ids)}
            )

        finally:
            session.close()

    def test_02_version_control(self):
        """ISO9001-DOC-002: Verziókezelés (updated_at mező)"""
        session = self.get_db_session()

        try:
            from database.models import Asset, Worksheet, User

            tables_to_check = [
                (Asset, "assets"),
                (Worksheet, "worksheets"),
                (User, "users")
            ]

            for model, table_name in tables_to_check:
                # Check if updated_at column exists
                has_updated_at = hasattr(model, 'updated_at')

                self.assert_compliance(
                    test_id=f"ISO9001-DOC-002-{table_name.upper()}",
                    test_name=f"{table_name.capitalize()} Version Control (updated_at)",
                    condition=has_updated_at,
                    success_message=f"{table_name} has updated_at field for version tracking",
                    failure_message=f"{table_name} missing updated_at field!",
                    severity="CRITICAL"
                )

                if has_updated_at:
                    # Check if records have valid timestamps
                    records = session.query(model).limit(10).all()
                    records_with_timestamp = [r for r in records if r.updated_at is not None]

                    self.assert_compliance(
                        test_id=f"ISO9001-DOC-002-{table_name.upper()}-DATA",
                        test_name=f"{table_name.capitalize()} Records Have Timestamps",
                        condition=len(records_with_timestamp) == len(records),
                        success_message=f"All {len(records)} records have valid timestamps",
                        failure_message=f"{len(records) - len(records_with_timestamp)} records missing timestamps",
                        severity="HIGH"
                    )

        finally:
            session.close()

    def test_03_audit_trail(self):
        """ISO9001-DOC-003: Audit trail (AuditLog tábla)"""
        session = self.get_db_session()

        try:
            from database.models import AuditLog

            # Check if AuditLog table exists
            audit_logs = session.query(AuditLog).limit(10).all()

            self.assert_compliance(
                test_id="ISO9001-DOC-003",
                test_name="Audit Log Table Exists",
                condition=True,  # If query succeeds, table exists
                success_message=f"Audit log table exists with {len(audit_logs)} sample records",
                failure_message="Audit log table missing!",
                severity="CRITICAL",
                details={"sample_records": len(audit_logs)}
            )

            # Check required fields
            if audit_logs:
                required_fields = ['user_id', 'action', 'table_name', 'timestamp']
                sample_log = audit_logs[0]

                missing_fields = [f for f in required_fields if not hasattr(sample_log, f)]

                self.assert_compliance(
                    test_id="ISO9001-DOC-003-FIELDS",
                    test_name="Audit Log Required Fields",
                    condition=len(missing_fields) == 0,
                    success_message="Audit log has all required fields",
                    failure_message=f"Audit log missing fields: {missing_fields}",
                    severity="CRITICAL",
                    details={"missing_fields": missing_fields}
                )

        except Exception as e:
            self.record_result(
                test_id="ISO9001-DOC-003",
                test_name="Audit Log Table Exists",
                status="FAIL",
                message=f"Audit log table not found or error: {str(e)}",
                severity="CRITICAL"
            )

        finally:
            session.close()


class ISO9001TraceabilityAudit(AuditBaseTest, DatabaseTestMixin):
    """ISO 9001 - Traceability Requirements (7.5.3)"""

    category = "iso9001"

    def test_01_asset_traceability(self):
        """ISO9001-TRACE-001: Asset nyomon követhetőség"""
        session = self.get_db_session()

        try:
            from database.models import Asset

            assets = session.query(Asset).limit(50).all()

            # Check required traceability fields
            required_fields = ['id', 'name', 'created_at', 'updated_at']

            assets_with_complete_info = [
                a for a in assets
                if all(getattr(a, field, None) is not None for field in required_fields)
            ]

            compliance_rate = len(assets_with_complete_info) / len(assets) if assets else 1.0

            self.assert_compliance(
                test_id="ISO9001-TRACE-001",
                test_name="Asset Traceability Completeness",
                condition=compliance_rate >= 0.95,  # 95% threshold
                success_message=f"{compliance_rate*100:.1f}% assets have complete traceability info",
                failure_message=f"Only {compliance_rate*100:.1f}% assets have complete info (required: 95%)",
                severity="CRITICAL",
                details={
                    "total_assets": len(assets),
                    "compliant_assets": len(assets_with_complete_info),
                    "compliance_rate": compliance_rate
                }
            )

        finally:
            session.close()

    def test_02_worksheet_traceability(self):
        """ISO9001-TRACE-002: Worksheet nyomon követhetőség"""
        session = self.get_db_session()

        try:
            from database.models import Worksheet

            worksheets = session.query(Worksheet).limit(50).all()

            if not worksheets:
                self.record_result(
                    test_id="ISO9001-TRACE-002",
                    test_name="Worksheet Traceability",
                    status="SKIP",
                    message="No worksheets found for testing"
                )
                return

            # Check worksheet-asset linkage
            worksheets_with_asset = [w for w in worksheets if w.asset_id is not None]

            linkage_rate = len(worksheets_with_asset) / len(worksheets)

            self.assert_compliance(
                test_id="ISO9001-TRACE-002",
                test_name="Worksheet-Asset Linkage",
                condition=linkage_rate >= 0.80,  # 80% threshold (some worksheets may be general)
                success_message=f"{linkage_rate*100:.1f}% worksheets linked to assets",
                failure_message=f"Only {linkage_rate*100:.1f}% worksheets linked to assets",
                severity="HIGH",
                details={
                    "total_worksheets": len(worksheets),
                    "linked_worksheets": len(worksheets_with_asset),
                    "linkage_rate": linkage_rate
                }
            )

        finally:
            session.close()

    def test_03_pm_history_tracking(self):
        """ISO9001-TRACE-003: PM History nyomon követés"""
        session = self.get_db_session()

        try:
            from database.models import PMHistory

            pm_histories = session.query(PMHistory).limit(50).all()

            # PM history is optional if no PM tasks completed yet
            self.assert_compliance(
                test_id="ISO9001-TRACE-003",
                test_name="PM History Tracking System",
                condition=True,  # System exists even if no data
                success_message=f"PM history tracking exists with {len(pm_histories)} records",
                failure_message="PM history tracking missing",
                severity="MEDIUM",
                details={"pm_history_records": len(pm_histories)}
            )

            # If histories exist, check completeness
            if pm_histories:
                complete_histories = [
                    h for h in pm_histories
                    if h.completed_at is not None and h.completed_by_user_id is not None
                ]

                completeness_rate = len(complete_histories) / len(pm_histories)

                self.assert_compliance(
                    test_id="ISO9001-TRACE-003-COMPLETE",
                    test_name="PM History Completeness",
                    condition=completeness_rate >= 0.90,
                    success_message=f"{completeness_rate*100:.1f}% PM histories are complete",
                    failure_message=f"Only {completeness_rate*100:.1f}% PM histories complete",
                    severity="HIGH",
                    details={"completeness_rate": completeness_rate}
                )

        except Exception as e:
            self.record_result(
                test_id="ISO9001-TRACE-003",
                test_name="PM History Tracking System",
                status="ERROR",
                message=f"Error checking PM history: {str(e)}",
                severity="MEDIUM"
            )

        finally:
            session.close()


class ISO9001RiskManagementAudit(AuditBaseTest, DatabaseTestMixin):
    """ISO 9001 - Risk Management (6.1)"""

    category = "iso9001"

    def test_01_asset_criticality(self):
        """ISO9001-RISK-001: Asset criticality classification"""
        session = self.get_db_session()

        try:
            from database.models import Asset

            assets = session.query(Asset).all()

            if not assets:
                self.record_result(
                    test_id="ISO9001-RISK-001",
                    test_name="Asset Criticality Classification",
                    status="SKIP",
                    message="No assets found"
                )
                return

            # Check if criticality field exists and is used
            assets_with_criticality = [a for a in assets if hasattr(a, 'criticality') and a.criticality is not None]

            classification_rate = len(assets_with_criticality) / len(assets)

            self.assert_compliance(
                test_id="ISO9001-RISK-001",
                test_name="Asset Criticality Classification",
                condition=classification_rate >= 0.80,
                success_message=f"{classification_rate*100:.1f}% assets have criticality classification",
                failure_message=f"Only {classification_rate*100:.1f}% assets classified",
                severity="HIGH",
                details={
                    "total_assets": len(assets),
                    "classified_assets": len(assets_with_criticality),
                    "classification_rate": classification_rate
                }
            )

        finally:
            session.close()

    def test_02_priority_system(self):
        """ISO9001-RISK-002: Priority system használat (worksheets)"""
        session = self.get_db_session()

        try:
            from database.models import Worksheet

            worksheets = session.query(Worksheet).all()

            if not worksheets:
                self.record_result(
                    test_id="ISO9001-RISK-002",
                    test_name="Priority System Usage",
                    status="SKIP",
                    message="No worksheets found"
                )
                return

            # Check priority field usage
            worksheets_with_priority = [w for w in worksheets if hasattr(w, 'priority') and w.priority is not None]

            priority_usage_rate = len(worksheets_with_priority) / len(worksheets)

            self.assert_compliance(
                test_id="ISO9001-RISK-002",
                test_name="Worksheet Priority System Usage",
                condition=priority_usage_rate >= 0.90,
                success_message=f"{priority_usage_rate*100:.1f}% worksheets have priority set",
                failure_message=f"Only {priority_usage_rate*100:.1f}% worksheets have priority",
                severity="HIGH",
                details={
                    "total_worksheets": len(worksheets),
                    "with_priority": len(worksheets_with_priority),
                    "usage_rate": priority_usage_rate
                }
            )

            # Check for critical priority items
            critical_worksheets = [w for w in worksheets_with_priority if w.priority == "CRITICAL"]

            self.record_result(
                test_id="ISO9001-RISK-002-CRITICAL",
                test_name="Critical Priority Items Identified",
                status="PASS",
                message=f"Found {len(critical_worksheets)} CRITICAL priority worksheets",
                severity="MEDIUM",
                details={"critical_count": len(critical_worksheets)}
            )

        finally:
            session.close()

    def test_03_breakdown_tracking(self):
        """ISO9001-RISK-003: Asset breakdown rögzítés"""
        session = self.get_db_session()

        try:
            from database.models import Asset

            # Check for assets in BREAKDOWN status
            breakdown_assets = session.query(Asset).filter(Asset.status == "BREAKDOWN").all()

            self.record_result(
                test_id="ISO9001-RISK-003",
                test_name="Asset Breakdown Tracking",
                status="PASS",
                message=f"Breakdown tracking system exists. Currently {len(breakdown_assets)} assets in BREAKDOWN status",
                severity="MEDIUM",
                details={"breakdown_count": len(breakdown_assets)}
            )

            # If breakdown assets exist, verify they have associated worksheets
            if breakdown_assets:
                from database.models import Worksheet

                breakdown_asset_ids = [a.id for a in breakdown_assets]
                related_worksheets = session.query(Worksheet).filter(
                    Worksheet.asset_id.in_(breakdown_asset_ids)
                ).all()

                coverage_rate = len(related_worksheets) / len(breakdown_assets) if breakdown_assets else 0

                self.assert_compliance(
                    test_id="ISO9001-RISK-003-WS",
                    test_name="Breakdown Assets Have Worksheets",
                    condition=coverage_rate >= 0.50,  # At least 50% should have worksheets
                    success_message=f"{coverage_rate*100:.1f}% breakdown assets have associated worksheets",
                    failure_message=f"Only {coverage_rate*100:.1f}% breakdown assets tracked with worksheets",
                    severity="MEDIUM",
                    details={"coverage_rate": coverage_rate}
                )

        finally:
            session.close()


if __name__ == "__main__":
    import unittest
    unittest.main()

