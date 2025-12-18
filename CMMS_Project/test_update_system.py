"""
Test script for update system functionality
Tests GitHub configuration, update checking, and related features
"""

import sys
import logging
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.logging_config import setup_logging
from config.app_config import APP_VERSION, LOG_FILE
from services.update_service import UpdateService, get_update_service
from services.settings_service import (
    get_github_owner, 
    get_github_repo, 
    set_github_owner, 
    set_github_repo,
    get_setting,
    get_skip_version,
    set_skip_version,
    get_auto_update_check,
    get_update_check_frequency,
    get_last_update_check
)
from utils.version_utils import normalize_version, is_newer_version, compare_versions

# Setup logging
setup_logging(log_level="INFO", log_file=LOG_FILE)
logger = logging.getLogger(__name__)


def test_github_configuration():
    """Test GitHub configuration loading"""
    print("\n" + "="*60)
    print("TEST 1: GitHub Configuration")
    print("="*60)
    
    # Get current configuration
    current_owner = get_github_owner()
    current_repo = get_github_repo()
    
    print(f"Current GitHub Owner: {current_owner}")
    print(f"Current GitHub Repo: {current_repo}")
    
    # Test UpdateService initialization
    service = UpdateService()
    print(f"\nUpdateService initialized:")
    print(f"  Owner: '{service.github_owner}'")
    print(f"  Repo: '{service.github_repo}'")
    print(f"  API URL: {service.latest_release_url}")
    
    # Check if configuration is valid
    if service.github_owner and service.github_repo:
        print(f"  [OK] Configuration is valid")
        return True
    else:
        print(f"  [FAIL] Configuration is missing")
        print(f"    Set GitHub owner/repo in Settings -> Updates or via environment variables")
        return False


def test_version_utils():
    """Test version comparison utilities"""
    print("\n" + "="*60)
    print("TEST 2: Version Utilities")
    print("="*60)
    
    test_cases = [
        ("1.0.0", "1.0.1", True),   # Patch update
        ("1.0.0", "1.1.0", True),   # Minor update
        ("1.0.0", "2.0.0", True),   # Major update
        ("1.0.1", "1.0.0", False),  # Older version
        ("1.0.0", "1.0.0", False),  # Same version
        ("1.0.6", "1.0.5", False),  # Current is newer
    ]
    
    all_passed = True
    for current, latest, expected_newer in test_cases:
        result = is_newer_version(latest, current)
        normalized_current = normalize_version(current)
        normalized_latest = normalize_version(latest)
        status = "[OK]" if result == expected_newer else "[FAIL]"
        if result != expected_newer:
            all_passed = False
        
        print(f"  {status} {current} -> {latest}: {result} (expected: {expected_newer})")
        print(f"      Normalized: {normalized_current} -> {normalized_latest}")
    
    print(f"\n  Current APP_VERSION: {APP_VERSION}")
    print(f"  Normalized: {normalize_version(APP_VERSION)}")
    
    return all_passed


def test_update_check():
    """Test update checking with GitHub API"""
    print("\n" + "="*60)
    print("TEST 3: Update Check")
    print("="*60)
    
    service = get_update_service()
    service.reload_config()
    
    if not service.github_owner or not service.github_repo:
        print("  [SKIP] Cannot test update check: GitHub not configured")
        print("    Configure GitHub owner/repo first")
        return False
    
    print(f"  Checking for updates (current: {APP_VERSION})...")
    print(f"  Repository: {service.github_owner}/{service.github_repo}")
    
    try:
        current_version = normalize_version(APP_VERSION)
        update_info = service.check_for_updates(current_version)
        
        if update_info:
            print(f"\n  [OK] Update available!")
            print(f"    Version: {update_info.version}")
            print(f"    Release Date: {update_info.release_date}")
            print(f"    Critical: {update_info.critical}")
            print(f"    Download URL: {update_info.download_url[:80]}...")
            if update_info.changelog:
                changelog_preview = update_info.changelog[:200].replace('\n', ' ')
                print(f"    Changelog: {changelog_preview}...")
        else:
            print(f"\n  [OK] No updates available (application is up to date)")
        
        return True
        
    except Exception as e:
        print(f"\n  [FAIL] Error during update check: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_settings():
    """Test update-related settings"""
    print("\n" + "="*60)
    print("TEST 4: Update Settings")
    print("="*60)
    
    auto_check = get_auto_update_check()
    frequency = get_update_check_frequency()
    last_check = get_last_update_check()
    skip_version = get_skip_version()
    
    print(f"  Auto Update Check: {auto_check}")
    print(f"  Check Frequency: {frequency}")
    print(f"  Last Check: {last_check or 'Never'}")
    print(f"  Skip Version: {skip_version or 'None'}")
    
    return True


def test_updater_paths():
    """Test Updater.exe path detection"""
    print("\n" + "="*60)
    print("TEST 5: Updater.exe Path Detection")
    print("="*60)
    
    import os
    import sys
    from pathlib import Path
    
    updater_paths = [
        Path(sys.executable).parent / "Updater.exe",
        Path("Updater.exe"),
        Path.cwd() / "Updater.exe",
        Path(os.getenv("ProgramFiles", "C:\\Program Files")) / "ArtenceCMMS" / "Updater.exe",
        Path(os.getenv("ProgramFiles(x86)", "C:\\Program Files (x86)")) / "ArtenceCMMS" / "Updater.exe",
        Path(os.getenv("LOCALAPPDATA", os.path.expanduser("~/.local/share"))) / "ArtenceCMMS" / "Updater.exe",
        PROJECT_ROOT / "dist" / "Updater.exe",
    ]
    
    found_paths = []
    for path in updater_paths:
        abs_path = path.resolve() if path.exists() else path
        exists = path.exists()
        status = "[OK]" if exists else "[NOT FOUND]"
        print(f"  {status} {abs_path}")
        if exists:
            found_paths.append(abs_path)
    
    if found_paths:
        print(f"\n  [OK] Found Updater.exe at: {found_paths[0]}")
        return True
    else:
        print(f"\n  [WARN] Updater.exe not found in any location")
        print(f"    Build Updater.exe first or ensure it's installed")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("UPDATE SYSTEM TEST SUITE")
    print("="*60)
    print(f"APP_VERSION: {APP_VERSION}")
    print(f"PROJECT_ROOT: {PROJECT_ROOT}")
    
    results = []
    
    # Run tests
    results.append(("GitHub Configuration", test_github_configuration()))
    results.append(("Version Utilities", test_version_utils()))
    results.append(("Update Check", test_update_check()))
    results.append(("Update Settings", test_settings()))
    results.append(("Updater.exe Paths", test_updater_paths()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  {status}: {name}")
    
    print(f"\n  Passed: {passed}/{total}")
    
    if passed == total:
        print("\n  [SUCCESS] All tests passed!")
        return 0
    else:
        print(f"\n  [FAILED] {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

