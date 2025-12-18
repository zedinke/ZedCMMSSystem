"""
Migration script to create pm_task_attachments table via SSH tunnel
"""

import sys
import os
import subprocess
import time
import signal

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from config.app_config import get_database_config
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SSH_KEY = os.path.expanduser("~/.ssh/zedhosting_server")
SERVER_HOST = "116.203.226.140"
SSH_USER = "root"
LOCAL_PORT = 3307
REMOTE_HOST = "116.203.226.140"
REMOTE_PORT = 3306

def start_ssh_tunnel():
    """Start SSH tunnel in background"""
    logger.info(f"Starting SSH tunnel...")
    logger.info(f"  Local port: {LOCAL_PORT}")
    logger.info(f"  Remote server: {REMOTE_HOST}:{REMOTE_PORT}")
    
    # Check if tunnel already exists
    try:
        # Try to check if port is already in use
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', LOCAL_PORT))
        sock.close()
        if result == 0:
            logger.info(f"[SKIP] Port {LOCAL_PORT} already in use, assuming tunnel exists")
            return True
    except:
        pass
    
    ssh_cmd = [
        "ssh",
        "-i", SSH_KEY,
        "-o", "StrictHostKeyChecking=no",
        "-o", "ConnectTimeout=10",
        "-L", f"{LOCAL_PORT}:{REMOTE_HOST}:{REMOTE_PORT}",
        "-N",  # Don't execute command, just tunnel
        "-f",  # Run in background
        f"{SSH_USER}@{SERVER_HOST}"
    ]
    
    try:
        result = subprocess.run(
            ssh_cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            logger.info(f"[OK] SSH tunnel started")
            time.sleep(2)  # Wait for tunnel to establish
            return True
        else:
            logger.error(f"[ERROR] SSH tunnel start failed")
            logger.error(f"  STDOUT: {result.stdout}")
            logger.error(f"  STDERR: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"[ERROR] SSH tunnel error: {e}")
        return False

def stop_ssh_tunnel():
    """Stop SSH tunnel"""
    logger.info("Stopping SSH tunnel...")
    # On Windows, find and kill SSH process
    if os.name == 'nt':  # Windows
        try:
            subprocess.run(
                ["taskkill", "/F", "/IM", "ssh.exe"],
                capture_output=True
            )
        except:
            pass
    else:  # Unix/Linux
        try:
            subprocess.run(["pkill", "-f", f"ssh.*{LOCAL_PORT}"], capture_output=True)
        except:
            pass

def migrate():
    """Create pm_task_attachments table if it doesn't exist"""
    # Check SSH key
    if not os.path.exists(SSH_KEY):
        logger.error(f"[ERROR] SSH key not found: {SSH_KEY}")
        return False
    
    logger.info(f"[OK] SSH key found: {SSH_KEY}")
    
    # Start SSH tunnel
    tunnel_started = start_ssh_tunnel()
    if not tunnel_started:
        logger.error("[ERROR] Could not start SSH tunnel")
        return False
    
    try:
        # Get database config
        config = get_database_config("production")
        
        # Create connection URL through tunnel
        encoded_password = quote_plus(config["password"])
        local_url = f"mysql+pymysql://{config['user']}:{encoded_password}@127.0.0.1:{LOCAL_PORT}/{config['database']}"
        
        logger.info(f"[INFO] Connecting through SSH tunnel to database: {config['database']}")
        
        # Create engine for tunnel
        engine = create_engine(
            local_url,
            pool_pre_ping=True,
            connect_args={
                "connect_timeout": 10,
                "read_timeout": 30,
                "write_timeout": 30,
            }
        )
        
        with engine.connect() as conn:
            # Check if table exists
            check_table_query = text("""
                SELECT COUNT(*) as count
                FROM information_schema.tables
                WHERE table_schema = DATABASE()
                AND table_name = 'pm_task_attachments'
            """)
            result = conn.execute(check_table_query)
            table_exists = result.fetchone()[0] > 0
            
            if table_exists:
                logger.info("[SKIP] Table pm_task_attachments already exists")
                return True
            
            # Create table
            create_table_query = text("""
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
            """)
            
            conn.execute(create_table_query)
            conn.commit()
            logger.info("[OK] Table pm_task_attachments created successfully")
            return True
            
    except Exception as e:
        logger.error(f"[ERROR] Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        engine.dispose()
        # Optionally stop tunnel (comment out if you want to keep it)
        # stop_ssh_tunnel()


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
        stop_ssh_tunnel()
        sys.exit(1)
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        import traceback
        traceback.print_exc()
        stop_ssh_tunnel()
        sys.exit(1)

