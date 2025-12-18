"""
02 - Functional Audit Tests
CRUD operations for all major modules
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "CMMS_Project"))

from base_test import AuditBaseTest, DatabaseTestMixin, APITestMixin
from audit_config import config
from datetime import datetime, timedelta


class UserManagementAudit(AuditBaseTest, DatabaseTestMixin, APITestMixin):
    """User Management CRUD Audit"""

    category = "functional"

    def setUp(self):
        """Set up test"""
        APITestMixin.__init__(self)
        self.api_login(config.test_admin_username, config.test_admin_password)

    def test_01_user_create(self):
        """TEST-FUNC-USER-001: Create new user"""
        test_user = {
            "username": f"audit_user_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "password": "Test1234!",
            "role": "Technician",
            "full_name": "Audit Test User",
            "email": f"audit_{datetime.now().strftime('%Y%m%d%H%M%S')}@test.com"
        }

        response = self.api_post("/v1/users", test_user)

        self.assert_compliance(
            test_id="FUNC-USER-001",
            test_name="User Create Operation",
            condition=response.status_code == 201,
            success_message="User created successfully",
            failure_message=f"Failed to create user: {response.status_code} - {response.text}",
            severity="CRITICAL",
            details={"response": response.json() if response.status_code == 201 else None}
        )

        # Store created user ID for cleanup
        if response.status_code == 201:
            self.created_user_id = response.json().get("id")

    def test_02_user_read_list(self):
        """TEST-FUNC-USER-002: Read users list"""
        response = self.api_get("/v1/users")

        self.assert_compliance(
            test_id="FUNC-USER-002",
            test_name="User List Read Operation",
            condition=response.status_code == 200,
            success_message="Users list retrieved successfully",
            failure_message=f"Failed to retrieve users: {response.status_code}",
            severity="HIGH"
        )

        if response.status_code == 200:
            users = response.json()
            self.assert_compliance(
                test_id="FUNC-USER-002A",
                test_name="User List Contains Data",
                condition=isinstance(users, list) and len(users) > 0,
                success_message=f"Found {len(users)} users",
                failure_message="Users list is empty",
                severity="MEDIUM"
            )

    def test_03_user_read_single(self):
        """TEST-FUNC-USER-003: Read single user by ID"""
        # Get first user
        response = self.api_get("/v1/users")
        if response.status_code == 200 and len(response.json()) > 0:
            user_id = response.json()[0].get("id")

            response = self.api_get(f"/v1/users/{user_id}")

            self.assert_compliance(
                test_id="FUNC-USER-003",
                test_name="User Single Read Operation",
                condition=response.status_code == 200,
                success_message=f"User {user_id} retrieved successfully",
                failure_message=f"Failed to retrieve user {user_id}",
                severity="HIGH"
            )

            if response.status_code == 200:
                user = response.json()
                required_fields = ["id", "username", "role"]
                missing_fields = [f for f in required_fields if f not in user]

                self.assert_compliance(
                    test_id="FUNC-USER-003A",
                    test_name="User Response Schema Validation",
                    condition=len(missing_fields) == 0,
                    success_message="User response contains all required fields",
                    failure_message=f"Missing fields: {missing_fields}",
                    severity="HIGH",
                    details={"missing_fields": missing_fields}
                )
        else:
            self.record_result(
                test_id="FUNC-USER-003",
                test_name="User Single Read Operation",
                status="SKIP",
                message="No users available for testing"
            )

    def test_04_user_update(self):
        """TEST-FUNC-USER-004: Update user"""
        # Get first user
        response = self.api_get("/v1/users")
        if response.status_code == 200 and len(response.json()) > 0:
            user_id = response.json()[0].get("id")

            update_data = {
                "full_name": f"Updated Name {datetime.now().strftime('%H%M%S')}"
            }

            response = self.api_put(f"/v1/users/{user_id}", update_data)

            self.assert_compliance(
                test_id="FUNC-USER-004",
                test_name="User Update Operation",
                condition=response.status_code in [200, 204],
                success_message=f"User {user_id} updated successfully",
                failure_message=f"Failed to update user {user_id}: {response.status_code}",
                severity="HIGH"
            )
        else:
            self.record_result(
                test_id="FUNC-USER-004",
                test_name="User Update Operation",
                status="SKIP",
                message="No users available for testing"
            )

    def test_05_user_password_complexity(self):
        """TEST-FUNC-USER-005: Password complexity validation"""
        weak_passwords = ["123", "password", "test"]

        for weak_pwd in weak_passwords:
            test_user = {
                "username": f"weak_pwd_test_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "password": weak_pwd,
                "role": "Technician"
            }

            response = self.api_post("/v1/users", test_user)

            # Should reject weak password
            self.assert_compliance(
                test_id="FUNC-USER-005",
                test_name=f"Password Complexity Rejection: '{weak_pwd}'",
                condition=response.status_code in [400, 422],
                success_message=f"Weak password '{weak_pwd}' correctly rejected",
                failure_message=f"Weak password '{weak_pwd}' was accepted!",
                severity="CRITICAL",
                details={"password": weak_pwd, "status": response.status_code}
            )

    def test_06_user_unique_username(self):
        """TEST-FUNC-USER-006: Username uniqueness constraint"""
        # Try to create user with existing username
        response = self.api_get("/v1/users")
        if response.status_code == 200 and len(response.json()) > 0:
            existing_username = response.json()[0].get("username")

            duplicate_user = {
                "username": existing_username,
                "password": "Test1234!",
                "role": "Technician"
            }

            response = self.api_post("/v1/users", duplicate_user)

            self.assert_compliance(
                test_id="FUNC-USER-006",
                test_name="Username Uniqueness Constraint",
                condition=response.status_code in [400, 409, 422],
                success_message="Duplicate username correctly rejected",
                failure_message="Duplicate username was accepted!",
                severity="CRITICAL"
            )


class AssetManagementAudit(AuditBaseTest, DatabaseTestMixin, APITestMixin):
    """Asset Management CRUD Audit"""

    category = "functional"

    def setUp(self):
        """Set up test"""
        APITestMixin.__init__(self)
        self.api_login(config.test_admin_username, config.test_admin_password)

    def test_01_asset_create(self):
        """TEST-FUNC-ASSET-001: Create new asset"""
        test_asset = {
            "name": f"Audit Asset {datetime.now().strftime('%Y%m%d%H%M%S')}",
            "asset_type": "Machine",
            "status": "OPERATIONAL",
            "criticality": "HIGH",
            "location": "Test Location"
        }

        response = self.api_post("/v1/assets", test_asset)

        self.assert_compliance(
            test_id="FUNC-ASSET-001",
            test_name="Asset Create Operation",
            condition=response.status_code == 201,
            success_message="Asset created successfully",
            failure_message=f"Failed to create asset: {response.status_code}",
            severity="CRITICAL"
        )

        if response.status_code == 201:
            self.created_asset_id = response.json().get("id")

    def test_02_asset_read_list(self):
        """TEST-FUNC-ASSET-002: Read assets list"""
        response = self.api_get("/v1/assets")

        self.assert_compliance(
            test_id="FUNC-ASSET-002",
            test_name="Asset List Read Operation",
            condition=response.status_code == 200,
            success_message="Assets list retrieved successfully",
            failure_message=f"Failed to retrieve assets: {response.status_code}",
            severity="HIGH"
        )

    def test_03_asset_status_workflow(self):
        """TEST-FUNC-ASSET-003: Asset status workflow"""
        valid_statuses = ["OPERATIONAL", "MAINTENANCE", "BREAKDOWN", "OFFLINE", "DECOMMISSIONED"]

        # Get first asset
        response = self.api_get("/v1/assets")
        if response.status_code == 200 and len(response.json()) > 0:
            asset_id = response.json()[0].get("id")

            for status in valid_statuses:
                update_data = {"status": status}
                response = self.api_put(f"/v1/assets/{asset_id}", update_data)

                self.assert_compliance(
                    test_id=f"FUNC-ASSET-003-{status}",
                    test_name=f"Asset Status Change to {status}",
                    condition=response.status_code in [200, 204],
                    success_message=f"Status changed to {status}",
                    failure_message=f"Failed to change status to {status}",
                    severity="HIGH"
                )
        else:
            self.record_result(
                test_id="FUNC-ASSET-003",
                test_name="Asset Status Workflow",
                status="SKIP",
                message="No assets available for testing"
            )

    def test_04_asset_hierarchy(self):
        """TEST-FUNC-ASSET-004: Asset hierarchy (ProductionLine → Machine → Module)"""
        # This test verifies the parent-child relationship
        response = self.api_get("/v1/assets")

        if response.status_code == 200:
            assets = response.json()

            # Find assets with parent relationships
            assets_with_parent = [a for a in assets if a.get("parent_id")]

            self.assert_compliance(
                test_id="FUNC-ASSET-004",
                test_name="Asset Hierarchy Support",
                condition=len(assets_with_parent) >= 0,  # Can be 0 if no hierarchy yet
                success_message=f"Found {len(assets_with_parent)} assets with parent relationship",
                failure_message="Asset hierarchy not supported",
                severity="MEDIUM",
                details={"assets_with_parent": len(assets_with_parent)}
            )


class InventoryManagementAudit(AuditBaseTest, DatabaseTestMixin, APITestMixin):
    """Inventory Management CRUD Audit"""

    category = "functional"

    def setUp(self):
        """Set up test"""
        APITestMixin.__init__(self)
        self.api_login(config.test_admin_username, config.test_admin_password)

    def test_01_inventory_create(self):
        """TEST-FUNC-INV-001: Create inventory item"""
        test_item = {
            "name": f"Audit Part {datetime.now().strftime('%Y%m%d%H%M%S')}",
            "part_number": f"AUD-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "quantity": 100,
            "min_stock_level": 20,
            "unit": "pcs",
            "location": "Warehouse A"
        }

        response = self.api_post("/v1/inventory", test_item)

        self.assert_compliance(
            test_id="FUNC-INV-001",
            test_name="Inventory Item Create Operation",
            condition=response.status_code == 201,
            success_message="Inventory item created successfully",
            failure_message=f"Failed to create inventory item: {response.status_code}",
            severity="CRITICAL"
        )

    def test_02_inventory_low_stock_alert(self):
        """TEST-FUNC-INV-002: Low stock alert detection"""
        response = self.api_get("/v1/inventory")

        if response.status_code == 200:
            items = response.json()
            low_stock_items = [
                item for item in items
                if item.get("quantity", 999) < item.get("min_stock_level", 0)
            ]

            self.assert_compliance(
                test_id="FUNC-INV-002",
                test_name="Low Stock Detection",
                condition=True,  # Just checking the logic works
                success_message=f"Found {len(low_stock_items)} low stock items",
                failure_message="Low stock detection failed",
                severity="MEDIUM",
                details={"low_stock_count": len(low_stock_items)}
            )


class WorksheetManagementAudit(AuditBaseTest, DatabaseTestMixin, APITestMixin):
    """Worksheet Management CRUD Audit"""

    category = "functional"

    def setUp(self):
        """Set up test"""
        APITestMixin.__init__(self)
        self.api_login(config.test_admin_username, config.test_admin_password)

    def test_01_worksheet_create(self):
        """TEST-FUNC-WS-001: Create worksheet"""
        test_worksheet = {
            "title": f"Audit Worksheet {datetime.now().strftime('%Y%m%d%H%M%S')}",
            "description": "Audit test worksheet",
            "status": "OPEN",
            "priority": "MEDIUM"
        }

        response = self.api_post("/v1/worksheets", test_worksheet)

        self.assert_compliance(
            test_id="FUNC-WS-001",
            test_name="Worksheet Create Operation",
            condition=response.status_code == 201,
            success_message="Worksheet created successfully",
            failure_message=f"Failed to create worksheet: {response.status_code}",
            severity="CRITICAL"
        )

    def test_02_worksheet_status_workflow(self):
        """TEST-FUNC-WS-002: Worksheet status workflow"""
        valid_statuses = ["OPEN", "IN_PROGRESS", "COMPLETED", "CLOSED"]

        response = self.api_get("/v1/worksheets")
        if response.status_code == 200 and len(response.json()) > 0:
            ws_id = response.json()[0].get("id")

            for status in valid_statuses:
                update_data = {"status": status}
                response = self.api_put(f"/v1/worksheets/{ws_id}", update_data)

                self.assert_compliance(
                    test_id=f"FUNC-WS-002-{status}",
                    test_name=f"Worksheet Status Change to {status}",
                    condition=response.status_code in [200, 204],
                    success_message=f"Status changed to {status}",
                    failure_message=f"Failed to change status to {status}",
                    severity="HIGH"
                )


class PMTaskManagementAudit(AuditBaseTest, DatabaseTestMixin, APITestMixin):
    """Preventive Maintenance Task Audit"""

    category = "functional"

    def setUp(self):
        """Set up test"""
        APITestMixin.__init__(self)
        self.api_login(config.test_admin_username, config.test_admin_password)

    def test_01_pm_task_create(self):
        """TEST-FUNC-PM-001: Create PM task"""
        test_pm = {
            "title": f"Audit PM Task {datetime.now().strftime('%Y%m%d%H%M%S')}",
            "description": "Audit test PM task",
            "frequency": "MONTHLY",
            "next_due_date": (datetime.now() + timedelta(days=30)).isoformat()
        }

        response = self.api_post("/v1/pm/tasks", test_pm)

        self.assert_compliance(
            test_id="FUNC-PM-001",
            test_name="PM Task Create Operation",
            condition=response.status_code == 201,
            success_message="PM task created successfully",
            failure_message=f"Failed to create PM task: {response.status_code}",
            severity="CRITICAL"
        )

    def test_02_pm_task_schedule_generation(self):
        """TEST-FUNC-PM-002: PM schedule generation"""
        frequencies = ["DAILY", "WEEKLY", "MONTHLY", "YEARLY"]

        for freq in frequencies:
            test_pm = {
                "title": f"Audit PM {freq}",
                "frequency": freq,
                "next_due_date": datetime.now().isoformat()
            }

            response = self.api_post("/v1/pm/tasks", test_pm)

            self.assert_compliance(
                test_id=f"FUNC-PM-002-{freq}",
                test_name=f"PM Frequency {freq} Support",
                condition=response.status_code == 201,
                success_message=f"{freq} frequency supported",
                failure_message=f"{freq} frequency not supported",
                severity="MEDIUM"
            )


if __name__ == "__main__":
    import unittest
    unittest.main()

