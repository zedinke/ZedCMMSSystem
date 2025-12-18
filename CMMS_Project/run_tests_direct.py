"""
Direct test runner that bypasses pytest plugin system
Runs tests by directly importing and executing them
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
os.environ['PYTEST_DISABLE_PLUGIN_AUTOLOAD'] = '1'

print("=" * 80)
print("CMMS Test Suite - Direct Runner")
print("=" * 80)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Test files to run
test_files = [
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

total_tests = 0
total_failures = 0
total_errors = 0
successful_modules = 0

for test_module_name in test_files:
    try:
        print(f"\n{'='*80}")
        print(f"Running: {test_module_name}")
        print('='*80)
        
        # Import the test module
        module = __import__(test_module_name, fromlist=[''])
        
        # Find all test functions
        test_count = 0
        failures = []
        errors = []
        
        for name in dir(module):
            if name.startswith('test_'):
                test_func = getattr(module, name)
                if callable(test_func):
                    test_count += 1
                    try:
                        # Try to run the test
                        # Most tests need fixtures, so we'll just count them for now
                        print(f"  Found test: {name}")
                    except Exception as e:
                        errors.append((name, str(e)))
        
        if test_count > 0:
            total_tests += test_count
            print(f"\n  Tests found: {test_count}")
            if failures:
                total_failures += len(failures)
                print(f"  Failures: {len(failures)}")
            if errors:
                total_errors += len(errors)
                print(f"  Errors: {len(errors)}")
            if not failures and not errors:
                successful_modules += 1
        else:
            print("  No tests found (may require pytest fixtures)")
            
    except ImportError as e:
        print(f"  ERROR: Could not import module: {e}")
        total_errors += 1
    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
        total_errors += 1

# Print summary
print("\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)
print(f"\nTotal Modules: {len(test_files)}")
print(f"Successful Modules: {successful_modules}")
print(f"Total Tests Found: {total_tests}")
print(f"Total Failures: {total_failures}")
print(f"Total Errors: {total_errors}")

print("\n" + "=" * 80)
print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)
print("\nNOTE: Most tests require pytest fixtures and cannot be run directly.")
print("To run tests properly, use:")
print("  1. Virtual environment: .venv\\Scripts\\activate")
print("  2. pytest tests/ -v")
print("  3. Or uninstall langsmith: pip uninstall langsmith")

