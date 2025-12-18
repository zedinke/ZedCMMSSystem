"""
Run migration script on remote server via SSH
"""

import sys
import os
import subprocess
import tempfile

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from config.app_config import get_database_config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SSH_KEY = os.path.expanduser("~/.ssh/zedhosting_server")
SERVER_HOST = "116.203.226.140"
SSH_USER = "root"

def run_migration_via_ssh():
    """Upload and run migration script on remote server"""
    config = get_database_config("production")
    
    # Read the remote migration script
    remote_script_path = os.path.join(os.path.dirname(__file__), "migrate_add_pm_task_attachments_table_remote.py")
    with open(remote_script_path, 'r', encoding='utf-8') as f:
        script_content = f.read()
    
    # Create a temporary file on remote server with the script
    # Use heredoc to create the file and then execute it
    python_command = f"""python3 << 'ENDOFSCRIPT'
{script_content}
ENDOFSCRIPT
"""
    
    # Set environment variables for database connection
    env_vars = f"""export DB_HOST='localhost' DB_USER='{config['user']}' DB_PASSWORD='{config['password']}' DB_NAME='{config['database']}' && """
    
    full_command = env_vars + python_command
    
    ssh_cmd = [
        "ssh",
        "-i", SSH_KEY,
        "-o", "StrictHostKeyChecking=no",
        "-o", "ConnectTimeout=30",
        f"{SSH_USER}@{SERVER_HOST}",
        full_command
    ]
    
    try:
        logger.info(f"[INFO] Running migration on remote server...")
        result = subprocess.run(
            ssh_cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        
        if result.returncode == 0:
            if "SUCCESS" in result.stdout or "SKIP" in result.stdout:
                logger.info("[OK] Migration completed successfully")
                return True
        
        logger.error(f"[ERROR] Migration failed with return code {result.returncode}")
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
    # Check SSH key
    if not os.path.exists(SSH_KEY):
        logger.error(f"[ERROR] SSH key not found: {SSH_KEY}")
        sys.exit(1)
    
    logger.info(f"[OK] SSH key found: {SSH_KEY}")
    
    success = run_migration_via_ssh()
    sys.exit(0 if success else 1)

