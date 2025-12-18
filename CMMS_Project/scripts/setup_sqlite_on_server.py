"""
Setup SQLite database on remote server via SSH
"""

import sys
import os
import subprocess
import tempfile
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.app_config import get_database_config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SSH_KEY = os.path.expanduser("~/.ssh/zedhosting_server")
SERVER_HOST = "116.203.226.140"
SSH_USER = "root"


def setup_sqlite_on_server(mode: str = "production"):
    """Setup SQLite database on remote server"""
    config = get_database_config(mode)
    db_path = config["path"]
    db_dir = str(Path(db_path).parent)
    
    # Commands to run on server
    commands = f"""
# Create directory if it doesn't exist
mkdir -p {db_dir}

# Set proper permissions
chmod 755 {db_dir}

# Create empty database file if it doesn't exist
if [ ! -f {db_path} ]; then
    touch {db_path}
    chmod 644 {db_path}
    echo "Database file created: {db_path}"
else
    echo "Database file already exists: {db_path}"
fi

# Verify file exists
ls -lh {db_path}
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
        logger.info(f"[INFO] Setting up SQLite database on server for mode: {mode}")
        logger.info(f"[INFO] Database path: {db_path}")
        
        result = subprocess.run(
            ssh_cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        
        if result.returncode == 0:
            logger.info("[OK] Database file created/verified on server")
            logger.info("[INFO] Next step: Run init_sqlite_database.py on the server to initialize schema")
            return True
        else:
            logger.error(f"[ERROR] Setup failed with return code {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("[ERROR] SSH command timed out")
        return False
    except Exception as e:
        logger.error(f"[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Setup SQLite database file on remote server")
    parser.add_argument(
        "--mode",
        choices=["production", "learning"],
        default="production",
        help="Database mode (default: production)"
    )
    
    args = parser.parse_args()
    
    # Check SSH key
    if not os.path.exists(SSH_KEY):
        logger.error(f"[ERROR] SSH key not found: {SSH_KEY}")
        sys.exit(1)
    
    logger.info(f"[OK] SSH key found: {SSH_KEY}")
    
    success = setup_sqlite_on_server(args.mode)
    sys.exit(0 if success else 1)

