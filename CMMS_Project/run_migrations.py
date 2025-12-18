"""
Run Alembic database migrations manually
Usage: python run_migrations.py
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from alembic import command
from alembic.config import Config

def main():
    """Run database migrations"""
    alembic_ini_path = PROJECT_ROOT / "alembic.ini"
    
    if not alembic_ini_path.exists():
        print(f"Error: alembic.ini not found at {alembic_ini_path}")
        sys.exit(1)
    
    print("Running database migrations...")
    alembic_cfg = Config(str(alembic_ini_path))
    
    try:
        command.upgrade(alembic_cfg, "head")
        print("✓ Migrations applied successfully")
    except Exception as e:
        print(f"✗ Error running migrations: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

