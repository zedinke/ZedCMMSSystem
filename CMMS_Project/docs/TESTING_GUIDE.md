# Testing Guide

## Overview

This document describes how to run the CMMS test suite and troubleshoot common issues.

## Test Structure

The test suite is located in the `tests/` directory and includes:

- **test_models.py**: Unit tests for database models
- **test_services.py**: Unit tests for service functions
- **test_utils.py**: Unit tests for utility functions
- **test_integration.py**: Integration tests for complete workflows
- **test_security.py**: Security tests (SQL injection, file upload, authorization)
- **test_performance.py**: Performance tests (database queries, PDF generation, Excel export)
- **test_asset_service.py**: Asset service specific tests
- **test_inventory_service.py**: Inventory service specific tests
- **test_worksheet_service.py**: Worksheet service specific tests
- **test_pm_service.py**: PM service specific tests
- **test_backend_changes.py**: Backend compatibility tests
- **test_context_service.py**: Context service tests
- **test_database_auth.py**: Database authentication tests
- **test_ui_localization.py**: UI localization tests
- **test_user_permissions.py**: User permission tests

## Running Tests

### Prerequisites

1. **Virtual Environment**: Activate the virtual environment
   ```bash
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/Mac
   ```

2. **Dependencies**: Ensure all test dependencies are installed
   ```bash
   pip install pytest pytest-cov pytest-asyncio
   ```

### Method 1: Using pytest (Recommended if no plugin conflicts)

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_models.py -v

# Run with coverage
pytest --cov=services --cov=models --cov=utils --cov-report=html tests/

# Run specific test
pytest tests/test_models.py::test_user_creation -v
```

### Method 2: Using unittest (Fallback if pytest has plugin issues)

```bash
# Run all tests
python -m unittest discover tests -v

# Run specific test file
python -m unittest tests.test_models -v
```

### Method 3: Using Custom Test Runner

```bash
# Run all tests with custom runner (bypasses plugin issues)
python run_tests.py
```

## Known Issues

### Langsmith Plugin Conflict

**Problem**: If you have `langsmith` installed globally, pytest may fail with:
```
TypeError: ForwardRef._evaluate() missing 1 required keyword-only argument: 'recursive_guard'
```

**Solutions**:

1. **Use Virtual Environment**: Always use the project's virtual environment
   ```bash
   .venv\Scripts\activate
   pytest tests/ -v
   ```

2. **Disable Plugin**: Use pytest with plugin disabled
   ```bash
   pytest tests/ -v -p no:langsmith
   ```

3. **Use Custom Runner**: Use the provided `run_tests.py` script
   ```bash
   python run_tests.py
   ```

4. **Uninstall Langsmith** (if not needed):
   ```bash
   pip uninstall langsmith
   ```

## Test Coverage

### Current Coverage

- **Models**: ~80% coverage
- **Services**: ~70% coverage
- **Utils**: ~80% coverage

### Generate Coverage Report

```bash
pytest --cov=services --cov=models --cov=utils --cov-report=html --cov-report=term tests/
```

The HTML report will be generated in `htmlcov/index.html`.

## Test Categories

### Unit Tests

Test individual components in isolation:
- Model creation and relationships
- Service function logic
- Utility function behavior

### Integration Tests

Test complete workflows:
- Worksheet creation → completion workflow
- PM task execution workflow
- Vacation request → approval workflow
- Inventory import workflow

### Security Tests

Test security measures:
- SQL injection prevention
- File upload validation
- Password hashing (bcrypt)
- Authorization checks
- Audit logging

### Performance Tests

Test performance characteristics:
- Database query performance
- PDF generation performance
- Excel export performance
- Memory profiling

## Test Fixtures

The test suite uses pytest fixtures defined in `tests/conftest.py`:

- **`test_session`**: In-memory SQLite database session for each test
- **`unique_id`**: Unique identifier generator
- **`unique_timestamp`**: Unique timestamp generator

## Troubleshooting

### Import Errors

If you see import errors:
1. Ensure you're in the project root directory
2. Activate the virtual environment
3. Check that all dependencies are installed

### Database Errors

If you see database errors:
1. Ensure the test database is properly initialized
2. Check that migrations are up to date
3. Verify database permissions

### Plugin Conflicts

If pytest fails due to plugin conflicts:
1. Use the virtual environment
2. Use the custom test runner (`run_tests.py`)
3. Disable problematic plugins with `-p no:plugin_name`

## Continuous Integration

For CI/CD pipelines, use:

```bash
# Install dependencies
pip install -r requirements.txt
pip install pytest pytest-cov

# Run tests with coverage
pytest --cov=services --cov=models --cov=utils --cov-report=xml --cov-report=term tests/

# Check coverage threshold
pytest --cov=services --cov=models --cov=utils --cov-fail-under=70 tests/
```

## Test Maintenance

### Adding New Tests

1. Create test file in `tests/` directory
2. Follow naming convention: `test_*.py`
3. Use pytest fixtures from `conftest.py`
4. Follow existing test patterns

### Updating Tests

When models or services change:
1. Update corresponding test files
2. Ensure all tests pass
3. Update test coverage if needed

## Test Results

Test results are displayed in the terminal. For detailed results:

```bash
# Verbose output
pytest tests/ -v -s

# Show print statements
pytest tests/ -v -s --capture=no

# Show local variables on failure
pytest tests/ -v --tb=long
```

---

**Last Updated**: 2025-12-14  
**Test Framework**: pytest  
**Python Version**: 3.10+

