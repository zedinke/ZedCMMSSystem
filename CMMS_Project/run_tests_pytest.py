"""
Pytest test runner that bypasses problematic plugins
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Disable langsmith plugin
os.environ['PYTEST_PLUGINS'] = ''

# Try to import and run pytest
try:
    import pytest
    
    # Run pytest with plugin disabled
    exit_code = pytest.main([
        'tests/',
        '-v',
        '--tb=short',
        '-p', 'no:langsmith',
        '--ignore-glob=*langsmith*',
    ])
    sys.exit(exit_code)
    
except ImportError:
    print("ERROR: pytest is not installed!")
    print("Install it with: pip install pytest pytest-cov")
    sys.exit(1)
except Exception as e:
    print(f"ERROR running tests: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

