"""
Run migration on remote server with pymysql - simplified version
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

def run_migration():
    """Run migration using pymysql"""
    config = get_database_config("production")
    
    # SQL content
    check_sql = f"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = '{config['database']}' AND table_name = 'pm_task_attachments'"
    
    create_sql = """CREATE TABLE IF NOT EXISTS pm_task_attachments (
    id INT NOT NULL AUTO_INCREMENT,
    pm_history_id INT NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_size INT,
    description TEXT,
    uploaded_at DATETIME,
    uploaded_by_user_id INT,
    PRIMARY KEY (id),
    FOREIGN KEY(pm_history_id) REFERENCES pm_histories (id) ON DELETE CASCADE,
    FOREIGN KEY(uploaded_by_user_id) REFERENCES users (id),
    INDEX idx_pm_attachment_history (pm_history_id),
    INDEX idx_pm_attachment_uploaded_at (uploaded_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"""
    
    # Escape for Python string
    create_sql_escaped = create_sql.replace('\\', '\\\\').replace('"', '\\"').replace("'", "\\'").replace('\n', '\\n')
    
    # Python script
    python_script = f"""import sys
import subprocess

# Try to import pymysql
try:
    import pymysql
except ImportError:
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--break-system-packages", "pymysql", "--quiet"], timeout=60)
        import pymysql
    except:
        print("ERROR: Could not install pymysql", file=sys.stderr)
        sys.exit(1)

# Connect to database
db_user = '{config['user']}'
db_password = '{config['password']}'
db_name = '{config['database']}'

hosts = ['127.0.0.1', 'localhost']
conn = None
last_err = None

for host in hosts:
    try:
        conn = pymysql.connect(host=host, user=db_user, password=db_password, database=db_name, charset='utf8mb4')
        break
    except Exception as e:
        last_err = str(e)
        continue

if conn is None:
    print(f"ERROR: Could not connect: {{last_err}}", file=sys.stderr)
    sys.exit(1)

try:
    cursor = conn.cursor()
    cursor.execute("{check_sql}")
    result = cursor.fetchone()
    if result and result[0] > 0:
        print("SKIP: Table already exists")
        sys.exit(0)
    
    create_table_sql = "{create_sql_escaped}"
    cursor.execute(create_table_sql)
    conn.commit()
    print("SUCCESS: Table created")
    cursor.close()
    conn.close()
    sys.exit(0)
except Exception as e:
    print(f"ERROR: {{str(e)}}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)
"""
    
    # Base64 encode
    script_encoded = base64.b64encode(python_script.encode('utf-8')).decode('utf-8')
    
    command = f"""python3 << 'PYEOF'
import base64
exec(base64.b64decode('{script_encoded}').decode('utf-8'))
PYEOF
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
        logger.info(f"[INFO] Running migration on remote server...")
        result = subprocess.run(
            ssh_cmd,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        stdout = result.stdout
        stderr = result.stderr
        
        if stdout:
            print(stdout)
        if stderr:
            print(stderr, file=sys.stderr)
        
        if result.returncode == 0:
            if "SUCCESS" in stdout or "SKIP" in stdout:
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
    if not os.path.exists(SSH_KEY):
        logger.error(f"[ERROR] SSH key not found: {SSH_KEY}")
        sys.exit(1)
    
    logger.info(f"[OK] SSH key found: {SSH_KEY}")
    
    success = run_migration()
    sys.exit(0 if success else 1)

