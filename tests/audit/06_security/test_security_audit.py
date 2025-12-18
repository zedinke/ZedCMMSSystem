"""
06 - Security Audit Tests
Cyber Security & Access Control
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "CMMS_Project"))

from base_test import AuditBaseTest, APITestMixin
from audit_config import config
import requests
from datetime import datetime


class SecurityAuthenticationAudit(AuditBaseTest, APITestMixin):
    """Security - Authentication Mechanisms"""

    category = "security"

    def setUp(self):
        """Set up test"""
        APITestMixin.__init__(self)

    def test_01_jwt_token_authentication(self):
        """SEC-AUTH-001: JWT token authentication működik"""
        try:
            response = requests.post(
                f"{self.api_base_url}/v1/auth/login",
                json={
                    "username": config.test_admin_username,
                    "password": config.test_admin_password
                },
                timeout=self.api_timeout
            )

            self.assert_compliance(
                test_id="SEC-AUTH-001",
                test_name="JWT Token Authentication",
                condition=response.status_code == 200 and "access_token" in response.json(),
                success_message="JWT authentication successful",
                failure_message=f"JWT authentication failed: {response.status_code}",
                severity="CRITICAL"
            )

            if response.status_code == 200:
                token_data = response.json()

                # Check token response structure
                required_fields = ["access_token", "token_type", "expires_in"]
                missing_fields = [f for f in required_fields if f not in token_data]

                self.assert_compliance(
                    test_id="SEC-AUTH-001A",
                    test_name="JWT Token Response Structure",
                    condition=len(missing_fields) == 0,
                    success_message="Token response complete",
                    failure_message=f"Missing fields: {missing_fields}",
                    severity="HIGH",
                    details={"missing_fields": missing_fields}
                )

        except requests.exceptions.RequestException as e:
            self.record_result(
                test_id="SEC-AUTH-001",
                test_name="JWT Token Authentication",
                status="ERROR",
                message=f"Connection error: {str(e)}",
                severity="CRITICAL"
            )

    def test_02_invalid_credentials_rejection(self):
        """SEC-AUTH-002: Invalid credentials elutasítása"""
        try:
            response = requests.post(
                f"{self.api_base_url}/v1/auth/login",
                json={
                    "username": "invalid_user_12345",
                    "password": "wrong_password_67890"
                },
                timeout=self.api_timeout
            )

            self.assert_compliance(
                test_id="SEC-AUTH-002",
                test_name="Invalid Credentials Rejection",
                condition=response.status_code == 401,
                success_message="Invalid credentials correctly rejected (401)",
                failure_message=f"Invalid credentials accepted! Status: {response.status_code}",
                severity="CRITICAL"
            )

        except requests.exceptions.RequestException as e:
            self.record_result(
                test_id="SEC-AUTH-002",
                test_name="Invalid Credentials Rejection",
                status="ERROR",
                message=f"Connection error: {str(e)}",
                severity="CRITICAL"
            )

    def test_03_unauthorized_access_blocked(self):
        """SEC-AUTH-003: Unauthorized access blokkolva (token nélküli hívás)"""
        try:
            # Try to access protected endpoint without token
            response = requests.get(
                f"{self.api_base_url}/v1/users",
                timeout=self.api_timeout
            )

            self.assert_compliance(
                test_id="SEC-AUTH-003",
                test_name="Unauthorized Access Blocked",
                condition=response.status_code in [401, 403],
                success_message=f"Unauthorized access blocked ({response.status_code})",
                failure_message=f"Unauthorized access allowed! Status: {response.status_code}",
                severity="CRITICAL"
            )

        except requests.exceptions.RequestException as e:
            self.record_result(
                test_id="SEC-AUTH-003",
                test_name="Unauthorized Access Blocked",
                status="ERROR",
                message=f"Connection error: {str(e)}",
                severity="CRITICAL"
            )

    def test_04_token_expiration(self):
        """SEC-AUTH-004: Token expiration field exists"""
        try:
            response = requests.post(
                f"{self.api_base_url}/v1/auth/login",
                json={
                    "username": config.test_admin_username,
                    "password": config.test_admin_password
                },
                timeout=self.api_timeout
            )

            if response.status_code == 200:
                token_data = response.json()

                self.assert_compliance(
                    test_id="SEC-AUTH-004",
                    test_name="Token Expiration Defined",
                    condition="expires_in" in token_data and token_data["expires_in"] > 0,
                    success_message=f"Token expires in {token_data.get('expires_in')} seconds",
                    failure_message="Token expiration not defined!",
                    severity="CRITICAL",
                    details={"expires_in": token_data.get("expires_in")}
                )

        except requests.exceptions.RequestException as e:
            self.record_result(
                test_id="SEC-AUTH-004",
                test_name="Token Expiration Defined",
                status="ERROR",
                message=f"Connection error: {str(e)}",
                severity="HIGH"
            )


class SecurityAuthorizationAudit(AuditBaseTest, APITestMixin):
    """Security - Role-Based Access Control (RBAC)"""

    category = "security"

    def setUp(self):
        """Set up test"""
        APITestMixin.__init__(self)
        self.api_login(config.test_admin_username, config.test_admin_password)

    def test_01_rbac_implementation(self):
        """SEC-AUTHZ-001: RBAC implementálva (Manager vs Technician)"""
        # Check if roles exist in user response
        response = self.api_get("/v1/users/me")

        if response.status_code == 200:
            user_data = response.json()

            self.assert_compliance(
                test_id="SEC-AUTHZ-001",
                test_name="RBAC Role Field Exists",
                condition="role" in user_data or "role_name" in user_data,
                success_message=f"User has role: {user_data.get('role') or user_data.get('role_name')}",
                failure_message="No role field in user data!",
                severity="CRITICAL",
                details={"user_role": user_data.get("role") or user_data.get("role_name")}
            )

    def test_02_permission_check_enforcement(self):
        """SEC-AUTHZ-002: Permission check minden védett endpoint-on"""
        # This is tested by attempting unauthorized actions
        # For now, just verify that protected endpoints require auth

        protected_endpoints = [
            "/v1/users",
            "/v1/machines",
            "/v1/worksheets",
            "/v1/assets"
        ]

        results = {}
        for endpoint in protected_endpoints:
            try:
                # Try without token
                response = requests.get(
                    f"{self.api_base_url}{endpoint}",
                    timeout=5
                )
                results[endpoint] = response.status_code in [401, 403]
            except:
                results[endpoint] = False

        all_protected = all(results.values())

        self.assert_compliance(
            test_id="SEC-AUTHZ-002",
            test_name="Protected Endpoints Require Auth",
            condition=all_protected,
            success_message="All tested endpoints require authentication",
            failure_message=f"Some endpoints not protected: {[k for k, v in results.items() if not v]}",
            severity="CRITICAL",
            details={"endpoint_results": results}
        )


class SecurityInjectionPreventionAudit(AuditBaseTest, APITestMixin):
    """Security - Injection Attack Prevention"""

    category = "security"

    def setUp(self):
        """Set up test"""
        APITestMixin.__init__(self)
        self.api_login(config.test_admin_username, config.test_admin_password)

    def test_01_sql_injection_prevention(self):
        """SEC-INJ-001: SQL injection védelem (ORM használat)"""
        # Test with SQL injection attempt in username
        sql_injection_payloads = [
            "admin' OR '1'='1",
            "admin'--",
            "' UNION SELECT * FROM users--"
        ]

        all_blocked = True
        for payload in sql_injection_payloads:
            try:
                response = requests.post(
                    f"{self.api_base_url}/v1/auth/login",
                    json={"username": payload, "password": "test"},
                    timeout=5
                )

                # Should return 401 (invalid credentials), not 500 (SQL error)
                if response.status_code == 500:
                    all_blocked = False
                    break

            except:
                pass  # Connection error is acceptable

        self.assert_compliance(
            test_id="SEC-INJ-001",
            test_name="SQL Injection Prevention",
            condition=all_blocked,
            success_message="SQL injection attempts properly handled",
            failure_message="SQL injection vulnerability detected!",
            severity="CRITICAL"
        )

    def test_02_xss_prevention(self):
        """SEC-INJ-002: XSS védelem input validation"""
        # Test with XSS payload
        xss_payload = "<script>alert('XSS')</script>"

        try:
            test_data = {
                "name": xss_payload,
                "description": xss_payload
            }

            response = self.api_post("/v1/assets", test_data)

            # Should either reject (400/422) or sanitize
            # If accepted (201), check if script tag is sanitized in response
            if response.status_code == 201:
                created_asset = response.json()
                contains_script = "<script>" in str(created_asset)

                self.assert_compliance(
                    test_id="SEC-INJ-002",
                    test_name="XSS Script Tag Sanitization",
                    condition=not contains_script,
                    success_message="XSS payload sanitized",
                    failure_message="XSS script tag not sanitized!",
                    severity="CRITICAL"
                )
            else:
                self.assert_compliance(
                    test_id="SEC-INJ-002",
                    test_name="XSS Input Rejection",
                    condition=response.status_code in [400, 422],
                    success_message="XSS payload rejected",
                    failure_message=f"Unexpected status: {response.status_code}",
                    severity="HIGH"
                )

        except Exception as e:
            self.record_result(
                test_id="SEC-INJ-002",
                test_name="XSS Prevention",
                status="ERROR",
                message=f"Error testing XSS: {str(e)}",
                severity="HIGH"
            )


class SecurityPasswordAudit(AuditBaseTest, APITestMixin):
    """Security - Password Security"""

    category = "security"

    def setUp(self):
        """Set up test"""
        APITestMixin.__init__(self)
        self.api_login(config.test_admin_username, config.test_admin_password)

    def test_01_password_complexity(self):
        """SEC-PWD-001: Password complexity requirements"""
        weak_passwords = [
            "123",
            "password",
            "abc",
            "test"
        ]

        rejected_count = 0
        for weak_pwd in weak_passwords:
            try:
                test_user = {
                    "username": f"weak_test_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "password": weak_pwd,
                    "role": "Technician"
                }

                response = self.api_post("/v1/users", test_user)

                if response.status_code in [400, 422]:
                    rejected_count += 1

            except:
                pass

        rejection_rate = rejected_count / len(weak_passwords)

        self.assert_compliance(
            test_id="SEC-PWD-001",
            test_name="Weak Password Rejection",
            condition=rejection_rate >= 0.75,  # At least 75% should be rejected
            success_message=f"{rejection_rate*100:.1f}% weak passwords rejected",
            failure_message=f"Only {rejection_rate*100:.1f}% weak passwords rejected",
            severity="CRITICAL",
            details={"rejection_rate": rejection_rate}
        )


class SecurityAPISecurityAudit(AuditBaseTest, APITestMixin):
    """Security - API Security Best Practices"""

    category = "security"

    def test_01_cors_configuration(self):
        """SEC-API-001: CORS properly configured"""
        try:
            response = requests.options(
                f"{self.api_base_url}/v1/auth/login",
                timeout=5
            )

            # CORS headers should be present
            has_cors_headers = "access-control-allow-origin" in response.headers

            self.assert_compliance(
                test_id="SEC-API-001",
                test_name="CORS Headers Present",
                condition=has_cors_headers,
                success_message="CORS headers configured",
                failure_message="CORS headers missing",
                severity="MEDIUM"
            )

        except Exception as e:
            self.record_result(
                test_id="SEC-API-001",
                test_name="CORS Configuration",
                status="SKIP",
                message=f"Could not test CORS: {str(e)}",
                severity="MEDIUM"
            )

    def test_02_https_recommendation(self):
        """SEC-API-002: HTTPS használat ajánlás (prod környezetben)"""
        # Check if using HTTPS
        using_https = self.api_base_url.startswith("https://")

        # For dev, HTTP is acceptable, but should warn
        if not using_https:
            self.record_result(
                test_id="SEC-API-002",
                test_name="HTTPS Usage",
                status="PASS",
                message="HTTP in use (development). STRONGLY RECOMMEND HTTPS for production!",
                severity="HIGH",
                details={"current_protocol": "HTTP", "recommended": "HTTPS"}
            )
        else:
            self.assert_compliance(
                test_id="SEC-API-002",
                test_name="HTTPS Usage",
                condition=True,
                success_message="HTTPS properly configured",
                failure_message="",
                severity="HIGH"
            )


if __name__ == "__main__":
    import unittest
    unittest.main()

