"""
Localization Helper for Services Layer
Provides helper functions for getting localized error and info messages
"""

from typing import Optional
from localization.translator import translator


def get_localized_error(key: str, lang_code: Optional[str] = None, **params) -> str:
    """
    Get localized error message from services
    
    Args:
        key: Error key (e.g., "user_not_found")
        lang_code: Language code (en/hu), uses current if None
        **params: Format parameters for string interpolation
    
    Returns:
        Localized error message
    """
    return translator.get_text(f"errors.{key}", lang_code=lang_code, **params)


def get_localized_message(key: str, lang_code: Optional[str] = None, **params) -> str:
    """
    Get localized success/info message
    
    Args:
        key: Message key (e.g., "user_anonymized")
        lang_code: Language code (en/hu), uses current if None
        **params: Format parameters for string interpolation
    
    Returns:
        Localized message
    """
    return translator.get_text(f"messages.{key}", lang_code=lang_code, **params)

