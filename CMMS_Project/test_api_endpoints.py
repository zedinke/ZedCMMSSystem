#!/usr/bin/env python
"""
API Integration Test Script
Tests all REST API endpoints with actual database
"""

import requests
import json
from typing import Optional
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

BASE_URL = "http://localhost:8000/api"
TEST_RESULTS = {
    "passed": 0,
    "failed": 0,
    "errors": []
}


def print_header(text: str):
    """Print formatted header"""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")


def print_test(name: str, passed: bool, details: str = ""):
    """Print test result"""
    global TEST_RESULTS
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {name}")
    if details:
        print(f"       {details}")
    
    if passed:
        TEST_RESULTS["passed"] += 1
    else:
        TEST_RESULTS["failed"] += 1
        TEST_RESULTS["errors"].append(f"{name}: {details}")


class APITester:
    def __init__(self):
        self.token: Optional[str] = None
        self.user_id: Optional[int] = None
        self.machine_id: Optional[int] = None
        self.worksheet_id: Optional[int] = None
        self.asset_id: Optional[int] = None
    
    def test_health(self):
        """Test health endpoint"""
        print_header("HEALTH CHECK")
        try:
            resp = requests.get(f"{BASE_URL}/health/", timeout=5)
            passed = resp.status_code == 200
            print_test(
                "GET /health/",
                passed,
                f"Status: {resp.status_code}"
            )
            return passed
        except Exception as e:
            print_test("GET /health/", False, str(e))
            return False
    
    def test_login(self):
        """Test login endpoint"""
        print_header("AUTHENTICATION")
        try:
            # Try default admin login
            resp = requests.post(
                f"{BASE_URL}/auth/login",
                json={"username": "admin", "password": "admin"}
            )
            
            passed = resp.status_code == 200
            print_test(
                "POST /auth/login (admin)",
                passed,
                f"Status: {resp.status_code}"
            )
            
            if passed:
                data = resp.json()
                self.token = data["access_token"]
                self.user_id = data["user_id"]
                print(f"       Token obtained for user: {data['username']} ({data['role_name']})")
            else:
                print(f"       Response: {resp.text}")
            
            return passed
        except Exception as e:
            print_test("POST /auth/login", False, str(e))
            return False
    
    def get_headers(self):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.token}"}
    
    def test_list_users(self):
        """Test list users endpoint"""
        print_header("USERS ENDPOINTS")
        try:
            resp = requests.get(
                f"{BASE_URL}/users/",
                headers=self.get_headers(),
                params={"skip": 0, "limit": 10}
            )
            
            passed = resp.status_code == 200
            print_test(
                "GET /users/",
                passed,
                f"Status: {resp.status_code}"
            )
            
            if passed:
                data = resp.json()
                print(f"       Found {data['total']} users, showing {len(data['items'])} items")
            
            return passed
        except Exception as e:
            print_test("GET /users/", False, str(e))
            return False
    
    def test_get_user(self):
        """Test get user endpoint"""
        try:
            resp = requests.get(
                f"{BASE_URL}/users/{self.user_id}",
                headers=self.get_headers()
            )
            
            passed = resp.status_code == 200
            print_test(
                f"GET /users/{self.user_id}",
                passed,
                f"Status: {resp.status_code}"
            )
            
            if passed:
                data = resp.json()
                print(f"       User: {data['username']} ({data['role']['name']})")
            
            return passed
        except Exception as e:
            print_test(f"GET /users/{self.user_id}", False, str(e))
            return False
    
    def test_list_machines(self):
        """Test list machines endpoint"""
        print_header("MACHINES ENDPOINTS")
        try:
            resp = requests.get(
                f"{BASE_URL}/machines/",
                headers=self.get_headers(),
                params={"skip": 0, "limit": 10}
            )
            
            passed = resp.status_code == 200
            print_test(
                "GET /machines/",
                passed,
                f"Status: {resp.status_code}"
            )
            
            if passed:
                data = resp.json()
                print(f"       Found {data['total']} machines, showing {len(data['items'])} items")
                if data['items']:
                    self.machine_id = data['items'][0]['id']
            
            return passed
        except Exception as e:
            print_test("GET /machines/", False, str(e))
            return False
    
    def test_get_machine(self):
        """Test get machine endpoint"""
        if not self.machine_id:
            print_test(f"GET /machines/1", False, "No machine ID available")
            return False
        
        try:
            resp = requests.get(
                f"{BASE_URL}/machines/{self.machine_id}",
                headers=self.get_headers()
            )
            
            passed = resp.status_code == 200
            print_test(
                f"GET /machines/{self.machine_id}",
                passed,
                f"Status: {resp.status_code}"
            )
            
            if passed:
                data = resp.json()
                print(f"       Machine: {data['name']} (Status: {data['status']})")
            
            return passed
        except Exception as e:
            print_test(f"GET /machines/{self.machine_id}", False, str(e))
            return False
    
    def test_list_worksheets(self):
        """Test list worksheets endpoint"""
        print_header("WORKSHEETS ENDPOINTS")
        try:
            resp = requests.get(
                f"{BASE_URL}/worksheets/",
                headers=self.get_headers(),
                params={"skip": 0, "limit": 10}
            )
            
            passed = resp.status_code == 200
            print_test(
                "GET /worksheets/",
                passed,
                f"Status: {resp.status_code}"
            )
            
            if passed:
                data = resp.json()
                print(f"       Found {data['total']} worksheets, showing {len(data['items'])} items")
                if data['items']:
                    self.worksheet_id = data['items'][0]['id']
            
            return passed
        except Exception as e:
            print_test("GET /worksheets/", False, str(e))
            return False
    
    def test_list_assets(self):
        """Test list assets endpoint"""
        print_header("ASSETS ENDPOINTS")
        try:
            resp = requests.get(
                f"{BASE_URL}/assets/",
                headers=self.get_headers(),
                params={"skip": 0, "limit": 10}
            )
            
            passed = resp.status_code == 200
            print_test(
                "GET /assets/",
                passed,
                f"Status: {resp.status_code}"
            )
            
            if passed:
                data = resp.json()
                print(f"       Found {data['total']} assets, showing {len(data['items'])} items")
                if data['items']:
                    self.asset_id = data['items'][0]['id']
            
            return passed
        except Exception as e:
            print_test("GET /assets/", False, str(e))
            return False
    
    def test_invalid_token(self):
        """Test invalid token rejection"""
        print_header("ERROR HANDLING")
        try:
            resp = requests.get(
                f"{BASE_URL}/users/",
                headers={"Authorization": "Bearer invalid_token"}
            )
            
            passed = resp.status_code == 401
            print_test(
                "Invalid token rejection",
                passed,
                f"Status: {resp.status_code}"
            )
            
            return passed
        except Exception as e:
            print_test("Invalid token rejection", False, str(e))
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*60)
        print("  CMMS REST API - INTEGRATION TEST SUITE")
        print("="*60)
        
        tests = [
            ("Health Check", self.test_health),
            ("Login", self.test_login),
            ("List Users", self.test_list_users),
            ("Get User", self.test_get_user),
            ("List Machines", self.test_list_machines),
            ("Get Machine", self.test_get_machine),
            ("List Worksheets", self.test_list_worksheets),
            ("List Assets", self.test_list_assets),
            ("Invalid Token", self.test_invalid_token),
        ]
        
        for name, test_func in tests:
            try:
                test_func()
            except Exception as e:
                print_test(name, False, str(e))
        
        # Summary
        print("\n" + "="*60)
        print(f"  TEST SUMMARY")
        print("="*60)
        print(f"✅ Passed: {TEST_RESULTS['passed']}")
        print(f"❌ Failed: {TEST_RESULTS['failed']}")
        print(f"📊 Total:  {TEST_RESULTS['passed'] + TEST_RESULTS['failed']}")
        
        if TEST_RESULTS['errors']:
            print("\n⚠️  Failures:")
            for error in TEST_RESULTS['errors']:
                print(f"   - {error}")
        
        print("\n✨ API Testing Complete!\n")
        
        return TEST_RESULTS['failed'] == 0


if __name__ == "__main__":
    tester = APITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
