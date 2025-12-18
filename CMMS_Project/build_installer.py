"""
Build script for creating Windows executable and installer
Combines PyInstaller build with Inno Setup installer creation
"""

import os
import sys
import subprocess
from pathlib import Path

def check_prerequisites():
    """Check if all required tools are installed"""
    print("Checking prerequisites...")
    print("=" * 60)
    
    critical_errors = []
    warnings = []
    
    # Check PyInstaller (critical)
    try:
        import PyInstaller
        print("[OK] PyInstaller is installed")
    except ImportError:
        critical_errors.append("PyInstaller is not installed. Install with: pip install pyinstaller")
        print("[ERROR] PyInstaller is not installed")
    
    # Check Inno Setup (optional for installer, but needed for full build)
    inno_paths = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
    ]
    
    inno_found = False
    inno_path = None
    for path in inno_paths:
        if Path(path).exists():
            inno_found = True
            inno_path = path
            print(f"[OK] Inno Setup found at: {path}")
            break
    
    if not inno_found:
        warnings.append("Inno Setup is not installed. Installer build will be skipped. Download from: https://jrsoftware.org/isinfo.php")
        print("[WARNING] Inno Setup is not installed (installer build will be skipped)")
    
    # Check required files
    required_files = [
        "build.spec",
        "main.py",
        "version.txt",
    ]
    
    for file in required_files:
        if Path(file).exists():
            print(f"[OK] {file} exists")
        else:
            critical_errors.append(f"Required file not found: {file}")
            print(f"[ERROR] {file} not found")
    
    # Check installer.iss (optional if Inno Setup is not installed)
    if Path("installer.iss").exists():
        print("[OK] installer.iss exists")
    else:
        if inno_found:
            critical_errors.append("installer.iss not found")
            print(f"[ERROR] installer.iss not found")
        else:
            warnings.append("installer.iss not found (but Inno Setup is also not installed)")
            print("[WARNING] installer.iss not found")
    
    # Check icon file (optional but recommended)
    if Path("icon.ico").exists():
        print("[OK] icon.ico exists")
    else:
        print("[WARNING] icon.ico not found - creating placeholder...")
        try:
            # Try to create icon
            subprocess.run([sys.executable, "create_icon.py"], check=False, cwd=Path(__file__).parent)
            if Path("icon.ico").exists():
                print("[OK] icon.ico created")
            else:
                print("[WARNING] Could not create icon.ico - installer will work without it")
        except Exception as e:
            print(f"[WARNING] Could not create icon: {e}")
    
    print("=" * 60)
    
    if warnings:
        print("\nWARNINGS:")
        for warning in warnings:
            print(f"  - {warning}")
    
    if critical_errors:
        print("\nCRITICAL ERRORS:")
        for error in critical_errors:
            print(f"  - {error}")
        return False, None
    
    return True, inno_path

def read_version():
    """Read version from version.txt"""
    version_file = Path("version.txt")
    if version_file.exists():
        with open(version_file, 'r', encoding='utf-8') as f:
            version = f.read().strip()
        return version
    return "1.0.0"

def increment_version():
    """Increment version number in version.txt"""
    version_file = Path("version.txt")
    if not version_file.exists():
        # Create version file with 1.0.0
        with open(version_file, 'w', encoding='utf-8') as f:
            f.write("1.0.0\n")
        return "1.0.0"
    
    # Read current version
    with open(version_file, 'r', encoding='utf-8') as f:
        version_str = f.read().strip()
    
    # Parse version (format: MAJOR.MINOR.PATCH)
    try:
        parts = version_str.split('.')
        major = int(parts[0]) if len(parts) > 0 else 1
        minor = int(parts[1]) if len(parts) > 1 else 0
        patch = int(parts[2]) if len(parts) > 2 else 0
        
        # Increment patch version
        patch += 1
        
        # If patch exceeds 99, increment minor and reset patch
        if patch > 99:
            patch = 0
            minor += 1
            # If minor exceeds 99, increment major and reset minor
            if minor > 99:
                minor = 0
                major += 1
        
        new_version = f"{major}.{minor}.{patch}"
        
        # Write new version back to file
        with open(version_file, 'w', encoding='utf-8') as f:
            f.write(f"{new_version}\n")
        
        print(f"Version incremented: {version_str} -> {new_version}")
        return new_version
        
    except (ValueError, IndexError) as e:
        print(f"[WARNING] Could not parse version '{version_str}': {e}")
        print("  Using default version 1.0.0")
        # Reset to 1.0.0 if parsing fails
        with open(version_file, 'w', encoding='utf-8') as f:
            f.write("1.0.0\n")
        return "1.0.0"

def build_exe():
    """Build executable using PyInstaller"""
    print("\n" + "=" * 60)
    print("Building CMMS executable with PyInstaller...")
    print("=" * 60)
    
    spec_file = Path("build.spec")
    if not spec_file.exists():
        print("ERROR: build.spec file not found!")
        return False
    
    try:
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--noconfirm",
            "build.spec"
        ]
        
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, cwd=Path(__file__).parent)
        
        exe_path = Path("dist") / "CMMS.exe"
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"\n[OK] Executable built successfully!")
            print(f"  Location: {exe_path}")
            print(f"  Size: {size_mb:.2f} MB")
            return True
        else:
            print(f"\n[ERROR] Executable not found at: {exe_path}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Build failed with error: {e}")
        return False
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

def build_updater():
    """Build Updater.exe using PyInstaller"""
    print("\n" + "=" * 60)
    print("Building Updater.exe with PyInstaller...")
    print("=" * 60)
    
    spec_file = Path("updater.spec")
    if not spec_file.exists():
        print("ERROR: updater.spec file not found!")
        return False
    
    try:
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--noconfirm",
            "updater.spec"
        ]
        
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, cwd=Path(__file__).parent)
        
        updater_path = Path("dist") / "Updater.exe"
        if updater_path.exists():
            size_mb = updater_path.stat().st_size / (1024 * 1024)
            print(f"\n[OK] Updater.exe built successfully!")
            print(f"  Location: {updater_path}")
            print(f"  Size: {size_mb:.2f} MB")
            return True
        else:
            print(f"\n[ERROR] Updater.exe not found at: {updater_path}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Updater build failed with error: {e}")
        return False
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

def build_installer(inno_path):
    """Build installer using Inno Setup"""
    print("\n" + "=" * 60)
    print("Building installer with Inno Setup...")
    print("=" * 60)
    
    version = read_version()
    installer_script = Path("installer.iss")
    
    if not installer_script.exists():
        print("ERROR: installer.iss file not found!")
        return False
    
    # Check if dist/CMMS.exe exists
    exe_path = Path("dist") / "CMMS.exe"
    if not exe_path.exists():
        print("ERROR: dist/CMMS.exe not found! Run build_exe() first.")
        return False
    
    try:
        # Create installer directory if it doesn't exist
        installer_dir = Path("installer")
        installer_dir.mkdir(exist_ok=True)
        
        # Pass version to Inno Setup compiler
        cmd = [str(inno_path), str(installer_script), f'/DVersionString={version}']
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, cwd=Path(__file__).parent)
        
        installer_file = installer_dir / f"ZedCMMS_Setup_v{version}.exe"
        if installer_file.exists():
            size_mb = installer_file.stat().st_size / (1024 * 1024)
            print(f"\n[OK] Installer built successfully!")
            print(f"  Location: {installer_file}")
            print(f"  Size: {size_mb:.2f} MB")
            return True
        else:
            # Try to find any .exe file in installer directory
            installer_files = list(installer_dir.glob("*.exe"))
            if installer_files:
                installer_file = installer_files[0]
                size_mb = installer_file.stat().st_size / (1024 * 1024)
                print(f"\n[OK] Installer built successfully!")
                print(f"  Location: {installer_file}")
                print(f"  Size: {size_mb:.2f} MB")
                return True
            else:
                print(f"\n[ERROR] Installer file not found in {installer_dir}")
                return False
            
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Installer build failed with error: {e}")
        return False
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_build():
    """Verify that build artifacts exist"""
    print("\n" + "=" * 60)
    print("Verifying build artifacts...")
    print("=" * 60)
    
    exe_path = Path("dist") / "CMMS.exe"
    updater_path = Path("dist") / "Updater.exe"
    version = read_version()
    installer_file = Path("installer") / f"ZedCMMS_Setup_v{version}.exe"
    
    all_good = True
    
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"[OK] CMMS.exe exists ({size_mb:.2f} MB)")
    else:
        print(f"[ERROR] CMMS.exe not found")
        all_good = False
    
    if updater_path.exists():
        size_mb = updater_path.stat().st_size / (1024 * 1024)
        print(f"[OK] Updater.exe exists ({size_mb:.2f} MB)")
    else:
        print(f"[WARNING] Updater.exe not found (optional)")
    
    # Check for any installer file
    installer_files = list(Path("installer").glob("*.exe")) if Path("installer").exists() else []
    if installer_files:
        installer_file = installer_files[0]
        size_mb = installer_file.stat().st_size / (1024 * 1024)
        print(f"[OK] Installer exists: {installer_file.name} ({size_mb:.2f} MB)")
    else:
        print(f"[ERROR] Installer not found")
        all_good = False
    
    print("=" * 60)
    return all_good

def main():
    """Main build function"""
    print("\n" + "=" * 60)
    print("Zed CMMS System - Build Installer Script")
    print("=" * 60)
    
    # Increment version before building
    print("Incrementing version...")
    version = increment_version()
    print(f"Building version: {version}\n")
    
    # Check prerequisites
    prerequisites_ok, inno_path = check_prerequisites()
    if not prerequisites_ok:
        print("\n[ERROR] Prerequisites check failed. Please install missing tools.")
        sys.exit(1)
    
    # Build executable
    if not build_exe():
        print("\n[ERROR] Executable build failed. Aborting.")
        sys.exit(1)
    
    # Build updater
    if not build_updater():
        print("\n[WARNING] Updater.exe build failed, but continuing...")
        print("   Updater.exe is optional for update functionality")
    
    # Build installer (only if Inno Setup is available)
    if inno_path:
        if not build_installer(inno_path):
            print("\n[ERROR] Installer build failed. Aborting.")
            sys.exit(1)
    else:
        print("\n[WARNING] Skipping installer build - Inno Setup is not installed")
        print("   CMMS.exe and Updater.exe have been built successfully")
        print("   To build the installer, install Inno Setup from: https://jrsoftware.org/isinfo.php")
    
    # Verify build
    if not verify_build():
        print("\n[WARNING] Build verification found issues, but build completed.")
    
    print("\n" + "=" * 60)
    print("[OK] Build process completed successfully!")
    print("=" * 60)
    
    installer_files = list(Path("installer").glob("*.exe")) if Path("installer").exists() else []
    if installer_files:
        print(f"\nNext steps:")
        print(f"  1. Test the installer: installer\\{installer_files[0].name}")
        print(f"  2. Install on a clean Windows machine")
        print(f"  3. Verify all features work correctly")
    else:
        print(f"\nBuild completed, but installer was not created.")
        print(f"  - CMMS.exe: dist\\CMMS.exe")
        if Path("dist/Updater.exe").exists():
            print(f"  - Updater.exe: dist\\Updater.exe")
        print(f"\nTo create the installer, install Inno Setup from: https://jrsoftware.org/isinfo.php")
        print(f"Then run this script again.")
    print()

if __name__ == "__main__":
    main()

