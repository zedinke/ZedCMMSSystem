"""
Script to automatically add missing translation keys
Adds missing keys from reference language (en) to target language (hu)
"""

import json
from pathlib import Path
from typing import Any, Dict


def get_all_keys(d: Dict[str, Any], prefix: str = '') -> Dict[str, Any]:
    """Recursively get all keys from nested dict with their values"""
    result = {}
    for k, v in d.items():
        full_key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            result[full_key] = v
            result.update(get_all_keys(v, full_key))
        else:
            result[full_key] = v
    return result


def set_nested_value(d: Dict[str, Any], key: str, value: Any):
    """Set a nested value in dict using dot notation"""
    keys = key.split('.')
    current = d
    for k in keys[:-1]:
        if k not in current:
            current[k] = {}
        current = current[k]
    current[keys[-1]] = value


def add_missing_keys(target: Dict[str, Any], reference: Dict[str, Any], lang: str):
    """Add missing keys from reference to target"""
    reference_keys = get_all_keys(reference)
    target_keys = get_all_keys(target)
    
    missing = set(reference_keys.keys()) - set(target_keys.keys())
    
    if not missing:
        print(f"   [OK] No missing keys in {lang}")
        return 0
    
    print(f"   Adding {len(missing)} missing keys to {lang}...")
    
    # Handle nested dicts properly
    def add_nested_dict(ref_dict: Dict, target_dict: Dict, path: str = ""):
        added_count = 0
        for k, v in ref_dict.items():
            current_path = f"{path}.{k}" if path else k
            if isinstance(v, dict):
                if k not in target_dict:
                    target_dict[k] = {}
                added_count += add_nested_dict(v, target_dict[k], current_path)
            elif k not in target_dict:
                target_dict[k] = v
                added_count += 1
        return added_count
    
    added = add_nested_dict(reference, target)
    
    return added


def main():
    """Main function"""
    translations_dir = Path(__file__).parent.parent / "localization" / "translations"
    
    en_file = translations_dir / "en.json"
    hu_file = translations_dir / "hu.json"
    
    # Load files
    with open(en_file, 'r', encoding='utf-8') as f:
        en_data = json.load(f)
    
    with open(hu_file, 'r', encoding='utf-8') as f:
        hu_data = json.load(f)
    
    print("Fixing missing translation keys...")
    print(f"Reference: en.json ({len(get_all_keys(en_data))} keys)")
    print(f"Target: hu.json ({len(get_all_keys(hu_data))} keys)")
    
    # Add missing keys to Hungarian
    added_hu = add_missing_keys(hu_data, en_data, "hu")
    
    # Add missing keys to English (from Hungarian)
    added_en = add_missing_keys(en_data, hu_data, "en")
    
    # Save files
    if added_hu > 0:
        with open(hu_file, 'w', encoding='utf-8') as f:
            json.dump(hu_data, f, ensure_ascii=False, indent=2)
        print(f"   [OK] Saved hu.json with {added_hu} new keys")
    
    if added_en > 0:
        with open(en_file, 'w', encoding='utf-8') as f:
            json.dump(en_data, f, ensure_ascii=False, indent=2)
        print(f"   [OK] Saved en.json with {added_en} new keys")
    
    if added_hu == 0 and added_en == 0:
        print("   [OK] All translations are complete!")
    
    return 0


if __name__ == "__main__":
    exit(main())

