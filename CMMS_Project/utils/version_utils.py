"""
Version utilities for semantic versioning comparison
"""

from typing import Tuple, Optional
import re


def parse_version(version_string: str) -> Tuple[int, int, int, Optional[str]]:
    """
    Parse semantic version string into components
    
    Args:
        version_string: Version string (e.g., "1.0.0", "1.2.3-beta")
    
    Returns:
        Tuple of (major, minor, patch, prerelease)
    """
    # Remove 'v' prefix if present
    version_string = version_string.strip().lstrip('vV')
    
    # Match semantic version pattern: MAJOR.MINOR.PATCH[-PRERELEASE]
    pattern = r'^(\d+)\.(\d+)\.(\d+)(?:-([\w\.]+))?$'
    match = re.match(pattern, version_string)
    
    if not match:
        # Try to extract numbers if format is different
        numbers = re.findall(r'\d+', version_string)
        if len(numbers) >= 3:
            major, minor, patch = int(numbers[0]), int(numbers[1]), int(numbers[2])
            prerelease = version_string.split('-')[1] if '-' in version_string else None
            return major, minor, patch, prerelease
        elif len(numbers) >= 2:
            major, minor = int(numbers[0]), int(numbers[1])
            return major, minor, 0, None
        elif len(numbers) >= 1:
            major = int(numbers[0])
            return major, 0, 0, None
        else:
            # Fallback: return 0.0.0
            return 0, 0, 0, None
    
    major = int(match.group(1))
    minor = int(match.group(2))
    patch = int(match.group(3))
    prerelease = match.group(4) if match.group(4) else None
    
    return major, minor, patch, prerelease


def compare_versions(version1: str, version2: str) -> int:
    """
    Compare two semantic versions
    
    Args:
        version1: First version string
        version2: Second version string
    
    Returns:
        -1 if version1 < version2
         0 if version1 == version2
         1 if version1 > version2
    """
    v1_major, v1_minor, v1_patch, v1_prerelease = parse_version(version1)
    v2_major, v2_minor, v2_patch, v2_prerelease = parse_version(version2)
    
    # Compare major version
    if v1_major < v2_major:
        return -1
    elif v1_major > v2_major:
        return 1
    
    # Compare minor version
    if v1_minor < v2_minor:
        return -1
    elif v1_minor > v2_minor:
        return 1
    
    # Compare patch version
    if v1_patch < v2_patch:
        return -1
    elif v1_patch > v2_patch:
        return 1
    
    # If both have prerelease, compare them
    if v1_prerelease and v2_prerelease:
        if v1_prerelease < v2_prerelease:
            return -1
        elif v1_prerelease > v2_prerelease:
            return 1
        return 0
    elif v1_prerelease:
        # Version with prerelease is less than version without
        return -1
    elif v2_prerelease:
        # Version without prerelease is greater than version with
        return 1
    
    # Versions are equal
    return 0


def is_newer_version(latest_version: str, current_version: str) -> bool:
    """
    Check if latest_version is newer than current_version
    
    Args:
        latest_version: Latest version string
        current_version: Current version string
    
    Returns:
        True if latest_version > current_version
    """
    return compare_versions(latest_version, current_version) > 0


def normalize_version(version_string: str) -> str:
    """
    Normalize version string to standard format
    
    Args:
        version_string: Version string to normalize
    
    Returns:
        Normalized version string (e.g., "1.0.0")
    """
    major, minor, patch, prerelease = parse_version(version_string)
    
    if prerelease:
        return f"{major}.{minor}.{patch}-{prerelease}"
    else:
        return f"{major}.{minor}.{patch}"




