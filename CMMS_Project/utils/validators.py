"""
Validation utilities
"""

import re

USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_]{3,20}$")
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
SKU_PATTERN = re.compile(r"^[A-Za-z0-9_-]{2,50}$")


def validate_username(username: str) -> bool:
    return bool(USERNAME_PATTERN.match(username))


def validate_email(email: str) -> bool:
    return bool(EMAIL_PATTERN.match(email))


def validate_password_strength(password: str) -> bool:
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    return True


def validate_sku(sku: str) -> bool:
    return bool(SKU_PATTERN.match(sku))
