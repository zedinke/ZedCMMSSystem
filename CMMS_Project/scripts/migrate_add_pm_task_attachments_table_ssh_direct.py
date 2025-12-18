"""
Migration script to create pm_task_attachments table via direct SSH MySQL command
"""

import sys
import os
import subprocess
import json

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

def run_mysql_via_ssh(sql_command):
    """Run MySQL command via SSH"""
    config = get_database_config("production")
    
    # Try different MySQL paths
    mysql_paths = [
        "mysql",
        "/usr/bin/mysql",
        "/usr/local/bin/mysql",
        "docker exec -i $(docker ps -q -f name=mysql) mysql",
        "docker exec -i $(docker ps -q -f name=mariadb) mysql",
    ]
    
    # Escape SQL command for shell
    escaped_sql = sql_command.replace('"', '\\"').replace('$', '\\$')
    
    # Build MySQL command - try each path
    for mysql_path in mysql_paths:
        if "docker" in mysql_path:
            mysql_cmd = f"""{mysql_path} -u{config['user']} -p'{config['password']}' {config['database']} -e "{escaped_sql}" """
        else:
            mysql_cmd = f"""{mysql_path} -u{config['user']} -p'{config['password']}' {config['database']} -e "{escaped_sql}" """
        
        # Build SSH command
        ssh_cmd = [
            "ssh",
            "-i", SSH_KEY,
            "-o", "StrictHostKeyChecking=no",
            "-o", "ConnectTimeout=30",
            f"{SSH_USER}@{SERVER_HOST}",
            mysql_cmd
        ]
    
        try:
            result = subprocess.run(
                ssh_cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return True, result.stdout
            elif "command not found" not in result.stderr:
                # If it's not a "command not found" error, return it
                return False, result.stderr
            # Otherwise, try next path
        except subprocess.TimeoutExpired:
            continue
        except Exception as e:
            if "command not found" not in str(e):
                return False, str(e)
            continue
    
    # If we get here, none of the paths worked
    return False, "MySQL command not found in any expected location"

def migrate():
    """Create pm_task_attachments table if it doesn't exist"""
    # Check SSH key
    if not os.path.exists(SSH_KEY):
        logger.error(f"[ERROR] SSH key not found: {SSH_KEY}")
        return False
    
    logger.info(f"[OK] SSH key found: {SSH_KEY}")
    
    config = get_database_config("production")
    logger.info(f"[INFO] Connecting to database: {config['database']}")
    
    # Check if table exists
    check_sql = """
        SELECT COUNT(*) as count
        FROM information_schema.tables
        WHERE table_schema = DATABASE()
        AND table_name = 'pm_task_attachments'
    """
    
    logger.info("[INFO] Checking if table exists...")
    success, output = run_mysql_via_ssh(check_sql)
    
    if not success:
        logger.error(f"[ERROR] Failed to check table existence: {output}")
        return False
    
    # Parse output to check count
    try:
        # MySQL output format: "count\n1" or "count\n0"
        lines = output.strip().split('\n')
        if len(lines) >= 2:
            count = int(lines[1])
            if count > 0:
                logger.info("[SKIP] Table pm_task_attachments already exists")
                return True
    except:
        # If we can't parse, assume it doesn't exist and try to create
        pass
    
    # Create table
    create_sql = """
        CREATE TABLE pm_task_attachments (
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
        )
    """
    
    logger.info("[INFO] Creating table pm_task_attachments...")
    success, output = run_mysql_via_ssh(create_sql)
    
    if success:
        logger.info("[OK] Table pm_task_attachments created successfully")
        return True
    else:
        logger.error(f"[ERROR] Failed to create table: {output}")
        # Check if error is because table already exists
        if "already exists" in output.lower() or "Duplicate" in output:
            logger.info("[SKIP] Table already exists (detected from error message)")
            return True
        return False


if __name__ == "__main__":
    try:
        success = migrate()
        if success:
            print("\n[SUCCESS] Migration completed successfully!")
            sys.exit(0)
        else:
            print("\n[ERROR] Migration failed")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n[INFO] Migration interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

