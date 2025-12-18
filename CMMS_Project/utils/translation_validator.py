"""
Translation Validator
Validates translation completeness and consistency
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple, Set
import re

import logging

logger = logging.getLogger(__name__)


def validate_translation_completeness(translations_dir: Path) -> Dict:
    """
    Validate that all translation keys exist in all languages
    
    Args:
        translations_dir: Directory containing translation JSON files
    
    Returns:
        Dictionary with validation results
    """
    try:
        # Find all translation files
        translation_files = list(translations_dir.glob("*.json"))
        
        if not translation_files:
            return {
                'valid': False,
                'error': 'No translation files found'
            }
        
        # Load all translations
        translations = {}
        for file_path in translation_files:
            lang_code = file_path.stem
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    translations[lang_code] = json.load(f)
            except Exception as e:
                logger.error(f"Error loading {file_path}: {e}")
                return {
                    'valid': False,
                    'error': f'Error loading {file_path}: {e}'
                }
        
        # Get all keys from all languages
        all_keys = set()
        for lang_data in translations.values():
            all_keys.update(_get_all_keys(lang_data))
        
        # Check for missing keys
        missing_keys = {}
        for lang_code, lang_data in translations.items():
            lang_keys = set(_get_all_keys(lang_data))
            missing = all_keys - lang_keys
            if missing:
                missing_keys[lang_code] = sorted(list(missing))
        
        # Check for extra keys (keys that exist in one language but not others)
        extra_keys = {}
        for lang_code, lang_data in translations.items():
            lang_keys = set(_get_all_keys(lang_data))
            for other_lang_code, other_lang_data in translations.items():
                if lang_code != other_lang_code:
                    other_keys = set(_get_all_keys(other_lang_data))
                    extra = lang_keys - other_keys
                    if extra:
                        if lang_code not in extra_keys:
                            extra_keys[lang_code] = {}
                        extra_keys[lang_code][other_lang_code] = sorted(list(extra))
        
        return {
            'valid': len(missing_keys) == 0,
            'missing_keys': missing_keys,
            'extra_keys': extra_keys,
            'total_keys': len(all_keys),
            'languages': list(translations.keys())
        }
        
    except Exception as e:
        logger.error(f"Error validating translations: {e}")
        return {
            'valid': False,
            'error': str(e)
        }


def validate_placeholders(translations_dir: Path) -> Dict:
    """
    Validate that placeholders are consistent across languages
    
    Args:
        translations_dir: Directory containing translation JSON files
    
    Returns:
        Dictionary with validation results
    """
    try:
        translation_files = list(translations_dir.glob("*.json"))
        translations = {}
        
        for file_path in translation_files:
            lang_code = file_path.stem
            with open(file_path, 'r', encoding='utf-8') as f:
                translations[lang_code] = json.load(f)
        
        # Find all placeholders in all translations
        placeholder_pattern = re.compile(r'\{(\w+)\}')
        inconsistencies = []
        
        all_keys = set()
        for lang_data in translations.values():
            all_keys.update(_get_all_keys(lang_data))
        
        for key in all_keys:
            placeholders = {}
            for lang_code, lang_data in translations.items():
                value = _get_nested_value(lang_data, key)
                if value and isinstance(value, str):
                    found_placeholders = set(placeholder_pattern.findall(value))
                    placeholders[lang_code] = found_placeholders
            
            # Check if placeholders are consistent
            if len(set(tuple(sorted(pl)) for pl in placeholders.values())) > 1:
                inconsistencies.append({
                    'key': key,
                    'placeholders': placeholders
                })
        
        return {
            'valid': len(inconsistencies) == 0,
            'inconsistencies': inconsistencies
        }
        
    except Exception as e:
        logger.error(f"Error validating placeholders: {e}")
        return {
            'valid': False,
            'error': str(e)
        }


def _get_all_keys(data: Dict, prefix: str = '') -> List[str]:
    """Recursively get all keys from nested dictionary"""
    keys = []
    for key, value in data.items():
        full_key = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            keys.extend(_get_all_keys(value, full_key))
        else:
            keys.append(full_key)
    return keys


def _get_nested_value(data: Dict, key: str):
    """Get value from nested dictionary using dot notation"""
    keys = key.split('.')
    value = data
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            return None
    return value


def validate_all(translations_dir: Path) -> Dict:
    """
    Run all validation checks
    
    Args:
        translations_dir: Directory containing translation JSON files
    
    Returns:
        Combined validation results
    """
    completeness = validate_translation_completeness(translations_dir)
    placeholders = validate_placeholders(translations_dir)
    
    return {
        'completeness': completeness,
        'placeholders': placeholders,
        'valid': completeness.get('valid', False) and placeholders.get('valid', False)
    }

