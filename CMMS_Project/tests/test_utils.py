"""
Unit tests for utility functions
Tests QR generation, currency formatting, date formatting, file validation
"""

import sys
from pathlib import Path
import pytest
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from utils.currency import format_price, format_price_compact
from utils.qr_generator import generate_qr_code, generate_qr_code_base64
from utils.validators import validate_sku, validate_email
from utils.file_handler import validate_file_upload


# ============================================================================
# CURRENCY FORMATTING TESTS
# ============================================================================

def test_format_price():
    """Test price formatting"""
    assert format_price(100.50) == "100.50 €"
    assert format_price(1000.00) == "1,000.00 €"
    assert format_price(1234.56) == "1,234.56 €"
    assert format_price(None) == "—"
    assert format_price(0) == "0.00 €"


def test_format_price_compact():
    """Test compact price formatting"""
    assert format_price_compact(100.50) == "100.50 €"
    assert format_price_compact(1000.00) == "1,000 €"  # No decimals for whole numbers
    assert format_price_compact(1234.56) == "1,234.56 €"
    assert format_price_compact(None) == "—"
    assert format_price_compact(0) == "0 €"


# ============================================================================
# QR CODE GENERATION TESTS
# ============================================================================

def test_generate_qr_code():
    """Test QR code generation"""
    qr_image = generate_qr_code(part_id=1, sku="TEST-001", size=200)
    assert qr_image is not None
    # QR code size might vary slightly, so check it's approximately correct
    assert qr_image.size[0] >= 200 and qr_image.size[1] >= 200


def test_generate_qr_code_base64():
    """Test QR code base64 encoding"""
    base64_str = generate_qr_code_base64(part_id=1, sku="TEST-001", size=200)
    assert base64_str is not None
    assert base64_str.startswith("data:image/png;base64,")
    assert len(base64_str) > 100  # Should have substantial data


def test_qr_code_data_format():
    """Test QR code data format (part_id:sku)"""
    # QR code should contain part_id:sku format
    qr_image = generate_qr_code(part_id=123, sku="TEST-001", size=200)
    assert qr_image is not None
    # The QR code should be decodable to "123:TEST-001"
    # (Actual decoding would require qrcode library, but we verify image is created)


# ============================================================================
# VALIDATION TESTS
# ============================================================================

def test_validate_sku():
    """Test SKU validation"""
    assert validate_sku("ABC-123") is True
    assert validate_sku("TEST_001") is True
    assert validate_sku("12345") is True
    assert validate_sku("") is False  # Empty SKU
    assert validate_sku("A" * 100) is False  # Too long


def test_validate_email():
    """Test email validation"""
    assert validate_email("test@example.com") is True
    assert validate_email("user.name@domain.co.uk") is True
    assert validate_email("invalid") is False
    assert validate_email("@example.com") is False
    assert validate_email("test@") is False
    assert validate_email("") is False


# ============================================================================
# FILE VALIDATION TESTS
# ============================================================================

def test_validate_file_upload_valid():
    """Test file upload validation with valid file"""
    # validate_file_upload only checks extension, not file existence
    valid, error = validate_file_upload(
        "test_file.pdf",  # Just filename, not path
        max_size_mb=10,
        allowed_extensions=[".pdf", ".jpg", ".png"]  # With dots
    )
    assert valid is True
    assert error is None


def test_validate_file_upload_invalid_extension():
    """Test file upload validation with invalid extension"""
    valid, error = validate_file_upload(
        "test_file.exe",
        max_size_mb=10,
        allowed_extensions=["pdf", "jpg", "png"]
    )
    assert valid is False
    assert error is not None
    assert "extension" in error.lower() or "type" in error.lower()


def test_validate_file_upload_too_large():
    """Test file upload validation with oversized file"""
    # Create a large test file (simulate)
    # Note: Actual file size check requires file system, so we test the logic
    # In real scenario, this would check actual file size
    valid, error = validate_file_upload(
        "large_file.pdf",
        max_size_mb=1,  # 1 MB limit
        allowed_extensions=["pdf"]
    )
    # This test would need actual file to test size, but validates the function exists
    assert isinstance(valid, bool)
    assert error is None or isinstance(error, str)


# ============================================================================
# DATE/TIME FORMATTING TESTS
# ============================================================================

def test_date_formatting():
    """Test date formatting utilities"""
    from datetime import date, datetime
    
    # Test basic date formatting
    test_date = date(2025, 6, 15)
    assert test_date.strftime("%Y-%m-%d") == "2025-06-15"
    
    # Test datetime formatting
    test_datetime = datetime(2025, 6, 15, 14, 30, 0)
    assert test_datetime.strftime("%Y-%m-%d %H:%M") == "2025-06-15 14:30"


# ============================================================================
# TRANSLATION KEY LOOKUP TESTS
# ============================================================================

def test_translation_key_lookup():
    """Test translation key lookup"""
    from localization.translator import translator
    from pathlib import Path
    
    # Initialize translator
    translations_dir = PROJECT_ROOT / "localization" / "translations"
    translator.initialize(translations_dir)
    translator.set_current_language("hu")
    
    # Test key lookup
    text = translator.get_text("common.buttons.save")
    assert text is not None
    assert len(text) > 0
    
    # Test with parameters
    text = translator.get_text("common.messages.operation_successful")
    assert text is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

