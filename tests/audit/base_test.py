"""
Base Test Class for CMMS Audit Tests
"""

import unittest
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import json


class AuditTestResult:
    """Individual test result"""

    def __init__(
        self,
        test_id: str,
        test_name: str,
        category: str,
        status: str,
        message: str = "",
        details: Optional[Dict[str, Any]] = None,
        severity: str = "MEDIUM"
    ):
        self.test_id = test_id
        self.test_name = test_name
        self.category = category
        self.status = status
        self.message = message
        self.details = details or {}
        self.severity = severity
        self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_id": self.test_id,
            "test_name": self.test_name,
            "category": self.category,
            "status": self.status,
            "message": self.message,
            "details": self.details,
            "severity": self.severity,
            "timestamp": self.timestamp.isoformat()
        }


class AuditBaseTest(unittest.TestCase):
    """Base class for all audit tests"""

    category = "general"

    @classmethod
    def setUpClass(cls):
        cls.results: List[AuditTestResult] = []
        cls.logger = logging.getLogger(cls.__name__)

    def record_result(
        self,
        test_id: str,
        test_name: str,
        status: str,
        message: str = "",
        details: Optional[Dict[str, Any]] = None,
        severity: str = "MEDIUM"
    ):
        result = AuditTestResult(
            test_id=test_id,
            test_name=test_name,
            category=self.category,
            status=status,
            message=message,
            details=details,
            severity=severity
        )
        self.results.append(result)
        print(f"[{status}] {test_name}: {message}")

    def assert_compliance(
        self,
        test_id: str,
        test_name: str,
        condition: bool,
        success_message: str,
        failure_message: str,
        severity: str = "HIGH",
        details: Optional[Dict[str, Any]] = None
    ):
        if condition:
            self.record_result(test_id, test_name, "PASS", success_message, details, severity)
        else:
            self.record_result(test_id, test_name, "FAIL", failure_message, details, severity)


class DatabaseTestMixin:
    """Mixin for database tests"""

    def get_db_session(self):
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / "CMMS_Project"))
        from database.connection import get_session
        return get_session()


class APITestMixin:
    """Mixin for API tests"""

    def __init__(self):
        from audit_config import config
        self.api_base_url = config.api_base_url
        self.api_timeout = config.api_timeout
        self.auth_token = None

    def get_auth_headers(self) -> Dict[str, str]:
        if self.auth_token:
            return {"Authorization": f"Bearer {self.auth_token}", "Content-Type": "application/json"}
        return {"Content-Type": "application/json"}

    def api_login(self, username: str, password: str) -> bool:
        import requests
        try:
            response = requests.post(
                f"{self.api_base_url}/v1/auth/login",
                json={"username": username, "password": password},
                timeout=self.api_timeout
            )
            if response.status_code == 200:
                self.auth_token = response.json().get("access_token")
                return True
            return False
        except Exception as e:
            print(f"API login failed: {e}")
            return False

    def api_get(self, endpoint: str, params=None):
        import requests
        return requests.get(f"{self.api_base_url}{endpoint}", params=params,
                          headers=self.get_auth_headers(), timeout=self.api_timeout)

    def api_post(self, endpoint: str, data: Dict):
        import requests
        return requests.post(f"{self.api_base_url}{endpoint}", json=data,
                           headers=self.get_auth_headers(), timeout=self.api_timeout)

    def api_put(self, endpoint: str, data: Dict):
        import requests
        return requests.put(f"{self.api_base_url}{endpoint}", json=data,
                          headers=self.get_auth_headers(), timeout=self.api_timeout)

    def api_delete(self, endpoint: str):
        import requests
        return requests.delete(f"{self.api_base_url}{endpoint}",
                             headers=self.get_auth_headers(), timeout=self.api_timeout)

