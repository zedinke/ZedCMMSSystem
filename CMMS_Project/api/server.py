"""
FastAPI Server Entry Point
Start REST API server with Uvicorn
"""

import uvicorn
import logging
import sys
from pathlib import Path

# Add project root to path - CRITICAL FOR SERVER DEPLOYMENT
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "api"))
sys.path.insert(0, str(PROJECT_ROOT / "services"))
sys.path.insert(0, str(PROJECT_ROOT / "database"))
sys.path.insert(0, str(PROJECT_ROOT / "utils"))
sys.path.insert(0, str(PROJECT_ROOT / "config"))
sys.path.insert(0, str(PROJECT_ROOT / "localization"))

from api.app import create_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Start FastAPI server"""
    print(f"\n{'='*60}")
    print(f"CMMS REST API v1.0.0")
    print(f"{'='*60}\n")
    
    try:
        app = create_app()
        
        print("Starting FastAPI server...")
        print("  📍 API URL: http://localhost:8000")
        print("  📚 Swagger UI: http://localhost:8000/api/docs")
        print("  📖 ReDoc: http://localhost:8000/api/redoc")
        print("  💚 Health Check: http://localhost:8000/api/health/")
        print("\n✅ Server ready. Press Ctrl+C to stop.\n")
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n\n❌ Server stopped.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
