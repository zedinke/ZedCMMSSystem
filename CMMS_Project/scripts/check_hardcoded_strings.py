"""
Hardcoded String Detector Script
Scans the codebase for hardcoded strings that should be localized
"""

import os
import re
from pathlib import Path
from typing import List, Tuple

# Patterns to detect hardcoded strings
PATTERNS = [
    (r'ft\.Text\(["\']([^"\']+)["\']\)', 'Flet Text widget'),
    (r'SnackBar.*content.*ft\.Text\(["\']([^"\']+)["\']\)', 'SnackBar message'),
    (r'raise.*Error\(["\']([^"\']+)["\']\)', 'Exception message'),
    (r'raise HTTPException.*detail=["\']([^"\']+)["\']', 'HTTPException detail'),
    (r'logger\.(info|error|warning|debug)\(["\']([^"\']+)["\']', 'Logger message'),
]

# Exclude patterns (these are OK)
EXCLUDE_PATTERNS = [
    r'^[A-Z_]+$',  # Constants like STATUS_OPEN
    r'^\d+$',  # Numbers
    r'^[a-z_]+$',  # Variable names
    r'^translator\.get_text',  # Already localized
    r'^get_localized_error',  # Already localized
    r'^get_localized_message',  # Already localized
    r'^#.*',  # Comments
    r'^""".*"""',  # Docstrings
    r'^\s*$',  # Empty strings
]

# Directories to scan
SCAN_DIRS = [
    'ui/screens',
    'services',
    'api/routers',
]

# Files to exclude
EXCLUDE_FILES = [
    '__pycache__',
    '.pyc',
    'check_hardcoded_strings.py',
    'translator.py',  # Translation file itself
]


def should_exclude_string(text: str) -> bool:
    """Check if a string should be excluded from detection"""
    for pattern in EXCLUDE_PATTERNS:
        if re.match(pattern, text, re.IGNORECASE | re.DOTALL):
            return True
    return False


def scan_file(file_path: Path) -> List[Tuple[str, int, str, str]]:
    """Scan a single file for hardcoded strings"""
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for line_num, line in enumerate(lines, 1):
            for pattern, issue_type in PATTERNS:
                matches = re.finditer(pattern, line)
                for match in matches:
                    # Extract the string content
                    if len(match.groups()) > 0:
                        string_content = match.group(1)
                        if not should_exclude_string(string_content):
                            # Check if it's not already using translator
                            if 'translator.get_text' not in line and 'get_localized_error' not in line:
                                issues.append((
                                    str(file_path),
                                    line_num,
                                    issue_type,
                                    string_content[:100]  # Truncate long strings
                                ))
    except Exception as e:
        print(f"Error scanning {file_path}: {e}")
    
    return issues


def main():
    """Main function to scan codebase"""
    project_root = Path(__file__).parent.parent
    all_issues = []
    
    print("Scanning for hardcoded strings...")
    print("=" * 80)
    
    for scan_dir in SCAN_DIRS:
        dir_path = project_root / scan_dir
        if not dir_path.exists():
            continue
            
        for file_path in dir_path.rglob('*.py'):
            # Skip excluded files
            if any(exclude in str(file_path) for exclude in EXCLUDE_FILES):
                continue
                
            issues = scan_file(file_path)
            all_issues.extend(issues)
    
    # Print results
    if all_issues:
        print(f"\nFound {len(all_issues)} potential hardcoded strings:\n")
        
        current_file = None
        for file_path, line_num, issue_type, content in sorted(all_issues):
            if file_path != current_file:
                current_file = file_path
                print(f"\n{file_path}:")
            print(f"  Line {line_num:4d} [{issue_type:20s}]: {content}")
        
        print("\n" + "=" * 80)
        print(f"Total issues found: {len(all_issues)}")
        return 1
    else:
        print("\n✓ No hardcoded strings found!")
        return 0


if __name__ == '__main__':
    exit(main())

