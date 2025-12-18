"""
Check translation completeness between hu.json and en.json
"""
import json
from pathlib import Path

def get_all_keys(d, prefix=''):
    """Recursively get all keys from nested dict"""
    keys = []
    for k, v in d.items():
        full_key = f"{prefix}.{k}" if prefix else k
        keys.append(full_key)
        if isinstance(v, dict):
            keys.extend(get_all_keys(v, full_key))
    return keys

def main():
    translations_dir = Path(__file__).parent.parent / "localization" / "translations"
    hu_file = translations_dir / "hu.json"
    en_file = translations_dir / "en.json"
    
    with open(hu_file, encoding='utf-8') as f:
        hu_data = json.load(f)
    with open(en_file, encoding='utf-8') as f:
        en_data = json.load(f)
    
    hu_keys = set(get_all_keys(hu_data))
    en_keys = set(get_all_keys(en_data))
    
    missing_hu = en_keys - hu_keys
    missing_en = hu_keys - en_keys
    
    print(f"Total HU keys: {len(hu_keys)}")
    print(f"Total EN keys: {len(en_keys)}")
    print(f"\nMissing in HU: {len(missing_hu)}")
    if missing_hu:
        for key in sorted(missing_hu)[:20]:
            print(f"  - {key}")
    
    print(f"\nMissing in EN: {len(missing_en)}")
    if missing_en:
        for key in sorted(missing_en)[:20]:
            print(f"  - {key}")
    
    if not missing_hu and not missing_en:
        print("\n[OK] All translations are complete!")
        return 0
    else:
        print(f"\n[WARNING] Translation completeness issues found")
        return 1

if __name__ == "__main__":
    exit(main())

