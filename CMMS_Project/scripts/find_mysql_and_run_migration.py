"""
Find MySQL on remote server and run migration
"""

import sys
import os
import subprocess

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

def find_mysql_and_run_migration():
    """Find MySQL on server and run migration SQL"""
    config = get_database_config("production")
    
    # SQL commands
    check_table_sql = """
SELECT COUNT(*) as count
FROM information_schema.tables
WHERE table_schema = '{}'
AND table_name = 'pm_task_attachments';
    """.format(config['database']).strip()
    
    create_table_sql = """
CREATE TABLE IF NOT EXISTS pm_task_attachments (
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """.strip()
    
    # Try different approaches to run MySQL
    approaches = [
        # Approach 1: Direct mysql command with which
        f"which mysql && mysql -u{config['user']} -p'{config['password']}' {config['database']} -e \"{check_table_sql}\"",
        
        # Approach 2: Try /usr/bin/mysql
        f"/usr/bin/mysql -u{config['user']} -p'{config['password']}' {config['database']} -e \"{check_table_sql}\"",
        
        # Approach 3: Try docker exec
        f"docker ps -q | head -1 | xargs -I {{}} docker exec {{}} mysql -u{config['user']} -p'{config['password']}' {config['database']} -e \"{check_table_sql}\"",
        
        # Approach 4: Try python with pymysql if available
        f"""python3 -c "
import sys
try:
    import pymysql
    conn = pymysql.connect(host='localhost', user='{config['user']}', password='{config['password']}', database='{config['database']}')
    cursor = conn.cursor()
    cursor.execute('{check_table_sql}')
    result = cursor.fetchone()
    print('COUNT:', result[0] if result else 0)
    conn.close()
except Exception as e:
    print('ERROR:', str(e))
    sys.exit(1)
" """,
    ]
    
    ssh_cmd_base = [
        "ssh",
        "-i", SSH_KEY,
        "-o", "StrictHostKeyChecking=no",
        "-o", "ConnectTimeout=30",
        f"{SSH_USER}@{SERVER_HOST}",
    ]
    
    # Try to check if table exists
    logger.info("[INFO] Checking if table exists...")
    table_exists = False
    
    for i, cmd in enumerate(approaches):
        try:
            logger.info(f"[INFO] Trying approach {i+1}...")
            ssh_cmd = ssh_cmd_base + [cmd]
            
            result = subprocess.run(
                ssh_cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                output = result.stdout.strip()
                logger.info(f"[OK] Command succeeded: {output[:100]}")
                
                # Parse output to see if table exists
                if "COUNT:" in output:
                    count = int(output.split("COUNT:")[1].strip())
                    table_exists = count > 0
                elif output.isdigit():
                    table_exists = int(output) > 0
                
                if table_exists:
                    logger.info("[SKIP] Table pm_task_attachments already exists")
                    return True
                
                # Table doesn't exist, create it using the same approach
                logger.info("[INFO] Creating table...")
                create_cmd = cmd.replace(check_table_sql, create_table_sql)
                ssh_cmd_create = ssh_cmd_base + [create_cmd]
                
                result_create = subprocess.run(
                    ssh_cmd_create,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result_create.returncode == 0:
                    logger.info("[OK] Table pm_task_attachments created successfully")
                    return True
                else:
                    # Check if error is "already exists"
                    if "already exists" in result_create.stderr.lower() or "Duplicate" in result_create.stderr:
                        logger.info("[SKIP] Table already exists (detected from error)")
                        return True
                    logger.warning(f"[WARNING] Create failed: {result_create.stderr[:200]}")
                
            else:
                logger.warning(f"[WARNING] Approach {i+1} failed: {result.stderr[:200]}")
                
        except subprocess.TimeoutExpired:
            logger.warning(f"[WARNING] Approach {i+1} timed out")
            continue
        except Exception as e:
            logger.warning(f"[WARNING] Approach {i+1} error: {str(e)[:200]}")
            continue
    
    logger.error("[ERROR] All approaches failed")
    return False

if __name__ == "__main__":
    # Check SSH key
    if not os.path.exists(SSH_KEY):
        logger.error(f"[ERROR] SSH key not found: {SSH_KEY}")
        sys.exit(1)
    
    logger.info(f"[OK] SSH key found: {SSH_KEY}")
    
    success = find_mysql_and_run_migration()
    if success:
        print("\n[SUCCESS] Migration completed successfully!")
        sys.exit(0)
    else:
        print("\n[ERROR] Migration failed - please run manually")
        sys.exit(1)

