"""
Run SQL migration file on remote server via SSH
"""

import sys
import os
import subprocess
import base64

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

def run_sql_migration():
    """Upload SQL file and run it on remote server"""
    config = get_database_config("production")
    
    # Read SQL file
    sql_file_path = os.path.join(os.path.dirname(__file__), "migrate_pm_task_attachments.sql")
    with open(sql_file_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # Base64 encode the SQL to avoid shell escaping issues
    sql_encoded = base64.b64encode(sql_content.encode('utf-8')).decode('utf-8')
    
    # Build command that decodes and runs SQL
    # Try multiple methods to find MySQL
    command = f"""python3 << 'PYTHONEOF'
import base64
import subprocess
import sys

sql_content = base64.b64decode('{sql_encoded}').decode('utf-8')

# Try different MySQL commands
mysql_cmds = [
    'mysql',
    '/usr/bin/mysql',
    'docker exec -i $(docker ps -q | head -1) mysql',
]

db_user = '{config['user']}'
db_password = '{config['password']}'
db_name = '{config['database']}'

for mysql_cmd in mysql_cmds:
    try:
        # Write SQL to temp file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as f:
            f.write(sql_content)
            sql_file = f.name
        
        # Try to run MySQL
        cmd = f"{{mysql_cmd}} -u{{db_user}} -p{{db_password}} {{db_name}} < {{sql_file}}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        
        # Clean up temp file
        import os
        os.unlink(sql_file)
        
        if result.returncode == 0:
            print("SUCCESS: Migration completed")
            sys.exit(0)
        elif "already exists" in result.stderr.lower() or "Duplicate" in result.stderr:
            print("SKIP: Table already exists")
            sys.exit(0)
        else:
            print(f"Failed with {{mysql_cmd}}: {{result.stderr[:200]}}")
    except Exception as e:
        print(f"Error with {{mysql_cmd}}: {{str(e)[:200]}}")
        continue

print("ERROR: All MySQL commands failed")
sys.exit(1)
PYTHONEOF
"""
    
    ssh_cmd = [
        "ssh",
        "-i", SSH_KEY,
        "-o", "StrictHostKeyChecking=no",
        "-o", "ConnectTimeout=30",
        f"{SSH_USER}@{SERVER_HOST}",
        command
    ]
    
    try:
        logger.info(f"[INFO] Running SQL migration on remote server...")
        result = subprocess.run(
            ssh_cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        output = result.stdout + result.stderr
        print(output)
        
        if result.returncode == 0:
            if "SUCCESS" in output or "SKIP" in output:
                logger.info("[OK] Migration completed successfully")
                return True
        
        logger.error(f"[ERROR] Migration failed")
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
    
    success = run_sql_migration()
    sys.exit(0 if success else 1)

