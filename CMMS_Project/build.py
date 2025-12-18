"""
Build script for creating Windows executable
"""

import os
import sys
import subprocess
from pathlib import Path

def build_exe():
    """Build executable using PyInstaller"""
    print("Building CMMS executable...")
    print("=" * 60)
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("ERROR: PyInstaller is not installed!")
        print("Install it with: pip install pyinstaller")
        sys.exit(1)
    
    # Check if spec file exists
    spec_file = Path("build.spec")
    if not spec_file.exists():
        print("ERROR: build.spec file not found!")
        sys.exit(1)
    
    # Run PyInstaller
    try:
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--noconfirm",
            "build.spec"
        ]
        
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, cwd=Path(__file__).parent)
        
        print("\n" + "=" * 60)
        print("✓ Build completed successfully!")
        print(f"Executable location: dist/CMMS.exe")
        print("=" * 60)
        
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Build failed with error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    build_exe()

