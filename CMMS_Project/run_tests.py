"""
Test runner script that bypasses problematic plugins
"""
import sys
import os

# Disable langsmith plugin before importing pytest
os.environ['PYTEST_PLUGINS'] = ''

# Remove langsmith from entry points
import importlib.metadata
try:
    dist = importlib.metadata.distribution('langsmith')
    # This is a workaround - we'll use unittest instead
    pass
except:
    pass

# Use unittest instead of pytest to avoid plugin issues
import unittest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Discover and run tests
if __name__ == '__main__':
    loader = unittest.TestLoader()
    suite = loader.discover('tests', pattern='test_*.py')
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)

