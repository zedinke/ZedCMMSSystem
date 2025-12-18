"""
Comprehensive test runner for CMMS
Runs all tests and generates a summary report
"""
import sys
import os
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Disable problematic plugins
os.environ['PYTEST_PLUGINS'] = ''

# Import test modules
test_modules = [
    'tests.test_backend_changes',
    'tests.test_context_service',
    'tests.test_database_auth',
    'tests.test_integration',
    'tests.test_inventory_service',
    'tests.test_models',
    'tests.test_performance',
    'tests.test_pm_service',
    'tests.test_security',
    'tests.test_services',
    'tests.test_ui_localization',
    'tests.test_user_permissions',
    'tests.test_utils',
    'tests.test_worksheet_service',
]

def run_tests():
    """Run all tests and generate summary"""
    import unittest
    
    loader = unittest.TestLoader()
    all_results = []
    
    print("=" * 80)
    print("CMMS Test Suite")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    for module_name in test_modules:
        try:
            print(f"\n{'='*80}")
            print(f"Running: {module_name}")
            print('='*80)
            
            module = __import__(module_name, fromlist=[''])
            suite = loader.loadTestsFromModule(module)
            runner = unittest.TextTestRunner(verbosity=1, stream=sys.stdout)
            result = runner.run(suite)
            
            all_results.append({
                'module': module_name,
                'tests_run': result.testsRun,
                'failures': len(result.failures),
                'errors': len(result.errors),
                'success': result.wasSuccessful()
            })
            
        except Exception as e:
            print(f"ERROR loading {module_name}: {e}")
            all_results.append({
                'module': module_name,
                'tests_run': 0,
                'failures': 0,
                'errors': 1,
                'success': False,
                'error_msg': str(e)
            })
    
    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    total_tests = sum(r['tests_run'] for r in all_results)
    total_failures = sum(r['failures'] for r in all_results)
    total_errors = sum(r['errors'] for r in all_results)
    successful_modules = sum(1 for r in all_results if r['success'])
    
    print(f"\nTotal Modules: {len(all_results)}")
    print(f"Successful Modules: {successful_modules}")
    print(f"Total Tests Run: {total_tests}")
    print(f"Total Failures: {total_failures}")
    print(f"Total Errors: {total_errors}")
    
    print("\n" + "-" * 80)
    print("Module Details:")
    print("-" * 80)
    for result in all_results:
        status = "✓" if result['success'] else "✗"
        print(f"{status} {result['module']:40} Tests: {result['tests_run']:3}  Failures: {result['failures']:2}  Errors: {result['errors']:2}")
        if 'error_msg' in result:
            print(f"    Error: {result['error_msg']}")
    
    print("\n" + "=" * 80)
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Exit with error code if any failures
    if total_failures > 0 or total_errors > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == '__main__':
    run_tests()

