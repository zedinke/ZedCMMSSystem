"""
Main Application Entry Point
CMMS - Computerized Maintenance Management System
"""

import sys
import logging
from pathlib import Path
import flet as ft

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.app_config import APP_NAME, APP_VERSION, DEFAULT_LANGUAGE, LOG_LEVEL, LOG_FILE
from config.logging_config import setup_logging
from localization.translator import translator
from database.database import init_database
from services.auth_service import cleanup_expired_sessions
from services.scheduler_service import start_scheduler
from ui.app import start_ui

# Configure logging with rotation - use LOG_FILE from app_config to ensure correct path
setup_logging(log_level=LOG_LEVEL, log_file=LOG_FILE)
logger = logging.getLogger(__name__)


def initialize_app():
    """Initialize application"""
    print(f"\n{'='*60}")
    print(f"{APP_NAME} v{APP_VERSION}")
    print(f"{'='*60}")
    
    try:
        # Initialize translations
        print("\n1. Initializing translations...")
        translations_dir = PROJECT_ROOT / "localization" / "translations"
        translator.initialize(translations_dir)
        
        # Validate translations
        validation = translator.validate_translations()
        if not validation['valid']:
            print(f"   ⚠️  Translation validation issues:")
            if 'missing_keys' in validation:
                for lang, keys in validation['missing_keys'].items():
                    print(f"      Missing in {lang}: {len(keys)} keys")
        else:
            print(f"   ✓ Translations loaded: {', '.join(translator.get_available_languages())}")
        
        # Set default language
        translator.set_current_language(DEFAULT_LANGUAGE)
        print(f"   ✓ Default language set to: {DEFAULT_LANGUAGE}")
        
        # Test translations
        test_key = "common.buttons.save"
        test_en = translator.get_text(test_key, 'en')
        test_hu = translator.get_text(test_key, 'hu')
        print(f"   ✓ Translation test: '{test_en}' / '{test_hu}'")
        
        # Initialize database
        print("\n2. Initializing database...")
        db_init_success = init_database()
        if not db_init_success:
            # Warning is already printed by init_database(), just note it was skipped
            pass
        
        # Cleanup expired sessions
        print("\n3. Cleaning up expired sessions...")
        cleanup_expired_sessions()
        print("   ✓ Cleanup complete")
        
        # Start background scheduler
        print("\n4. Starting background scheduler...")
        try:
            start_scheduler()
            print("   ✓ Background scheduler initialized")
            logger.info("Background scheduler initialized")
        except Exception as e:
            print(f"   ⚠️  Failed to start scheduler: {e}")
            logger.error(f"Failed to start scheduler: {e}")
        
        print(f"\n{'='*60}")
        print("✓ Application initialized successfully!")
        print(f"{'='*60}\n")
        
        logger.info("Application initialized successfully")
        return True
        
    except Exception as e:
        print(f"\n✗ Initialization failed: {e}")
        logger.error(f"Initialization failed: {e}", exc_info=True)
        return False


def main():
    """Main application entry point"""
    if not initialize_app():
        sys.exit(1)
    
    # Indítjuk a Flet UI-t
    logger.info("Starting Flet UI...")
    ft.app(target=start_ui)


if __name__ == "__main__":
    main()
