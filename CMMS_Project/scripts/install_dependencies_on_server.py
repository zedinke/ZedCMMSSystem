"""
Install Python dependencies on remote server via SSH
"""

import sys
import os
import subprocess

SSH_KEY = os.path.expanduser("~/.ssh/zedhosting_server")
SERVER_HOST = "116.203.226.140"
SSH_USER = "root"


def install_dependencies():
    """Install required Python packages on server"""
    
    # Commands to install dependencies
    commands = """
# Check Python version
python3 --version

# Install required packages
python3 -m pip install --break-system-packages --upgrade pip || true
python3 -m pip install --break-system-packages sqlalchemy alembic || python3 -m pip install sqlalchemy alembic

# Verify installation
python3 -c "import sqlalchemy; print('SQLAlchemy version:', sqlalchemy.__version__)"
"""
    
    ssh_cmd = [
        "ssh",
        "-i", SSH_KEY,
        "-o", "StrictHostKeyChecking=no",
        "-o", "ConnectTimeout=30",
        f"{SSH_USER}@{SERVER_HOST}",
        commands
    ]
    
    try:
        print("[INFO] Installing dependencies on server...")
        
        result = subprocess.run(
            ssh_cmd,
            capture_output=True,
            text=True,
            timeout=180
        )
        
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        
        if result.returncode == 0 or "version:" in result.stdout:
            print("[OK] Dependencies installed")
            return True
        else:
            print(f"[ERROR] Installation failed with return code {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        print("[ERROR] SSH command timed out")
        return False
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    if not os.path.exists(SSH_KEY):
        print(f"[ERROR] SSH key not found: {SSH_KEY}")
        sys.exit(1)
    
    success = install_dependencies()
    sys.exit(0 if success else 1)

