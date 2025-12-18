"""
Initialize SQLite database schema on remote server via SSH
"""

import sys
import os
import subprocess
import base64
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


def init_sqlite_on_server(mode: str = "production"):
    """Initialize SQLite database schema on remote server"""
    config = get_database_config(mode)
    db_path = config["path"]
    
    # Direct Python command to initialize SQLite database
    python_command = f"""python3 << 'PYEOF'
import sys
import os
from pathlib import Path

# Set up the environment
os.chdir('/opt/cmms-backend')
sys.path.insert(0, '/opt/cmms-backend')

from sqlalchemy import create_engine, event
from database.models import Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db_path = '{db_path}'

try:
    logger.info(f"Initializing SQLite database at: {{db_path}}")
    
    # Ensure parent directory exists
    db_path_obj = Path(db_path)
    db_path_obj.parent.mkdir(parents=True, exist_ok=True)
    
    # Create SQLite engine directly
    database_url = f"sqlite:///{{db_path}}"
    
    connect_args = {{
        "check_same_thread": False,
        "timeout": 30,
    }}
    
    engine = create_engine(
        database_url,
        connect_args=connect_args,
        echo=False,
        future=True,
        pool_pre_ping=True,
    )
    
    # Enable foreign key constraints for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA cache_size=-64000")
        cursor.execute("PRAGMA temp_store=MEMORY")
        cursor.close()
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    logger.info("✓ Database schema created")
    
    # Initialize default data (roles)
    from database.models import Role
    from config.roles import ALL_ROLES
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.exc import IntegrityError
    
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    
    # Initialize roles
    session = SessionLocal()
    try:
        for role_name in ALL_ROLES:
            existing_role = session.query(Role).filter_by(name=role_name).first()
            if not existing_role:
                role = Role(name=role_name)
                session.add(role)
                logger.info(f"✓ Role created: {{role_name}}")
        session.commit()
        logger.info("✓ All roles initialized")
        logger.info("⚠ Note: Admin user creation skipped - will be created on first login or via admin tools")
    except IntegrityError:
        session.rollback()
        logger.info("⚠ Roles already exist")
    finally:
        session.close()
    
    logger.info(f"✓ SQLite database successfully initialized at {{db_path}}")
    sys.exit(0)
    
except Exception as e:
    logger.error(f"✗ Error initializing database: {{e}}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
PYEOF
"""
    
    ssh_cmd = [
        "ssh",
        "-i", SSH_KEY,
        "-o", "StrictHostKeyChecking=no",
        "-o", "ConnectTimeout=30",
        f"{SSH_USER}@{SERVER_HOST}",
        python_command
    ]
    
    try:
        logger.info(f"[INFO] Initializing SQLite database schema on server for mode: {mode}")
        logger.info(f"[INFO] Database path: {db_path}")
        
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
            if "successfully initialized" in stdout.lower() or "✓ Database schema created" in stdout:
                logger.info("[OK] Database schema initialized successfully")
                return True
            else:
                # Even if no explicit success message, return code 0 means success
                logger.info("[OK] Database initialization completed (exit code 0)")
                return True
        
        logger.error(f"[ERROR] Initialization failed with return code {result.returncode}")
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
    
    parser = argparse.ArgumentParser(description="Initialize SQLite database schema on remote server")
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
    
    success = init_sqlite_on_server(args.mode)
    sys.exit(0 if success else 1)

