"""
Developer Tools Screen
Administrative tools for Developer role only
"""
import flet as ft
# Compatibility for flet 0.23.2 - Icons are strings, not ft.Icons
if not hasattr(ft, 'Icons'):
    from utils.flet_icons import Icons
    ft.Icons = Icons
from services import context_service
from utils.permissions import can_view_developer_tools
from database.connection import engine
from sqlalchemy import inspect
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from pathlib import Path
from config.app_config import PROJECT_ROOT, get_database_config
from localization.translator import translator
from urllib.parse import quote_plus
from ui.components.modern_components import (
    create_modern_button,
    create_modern_text_field,
    DesignSystem,
)
from ui.components.modern_card import create_tailwind_card
import os


class DeveloperToolsScreen:
    """Screen with developer/admin tools (Developer role only)"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        
        # Database info
        self.db_info_text = ft.Text("", selectable=True)
        
        # .env file path
        self.env_file_path = PROJECT_ROOT / ".env"
        
        # Production database MySQL fields - using modern components
        self.prod_db_host_field = create_modern_text_field(
            label=translator.get_text("developer.env.db_host"),
        )
        self.prod_db_port_field = create_modern_text_field(
            label=translator.get_text("developer.env.db_port"),
        )
        self.prod_db_user_field = create_modern_text_field(
            label=translator.get_text("developer.env.db_user"),
        )
        self.prod_db_password_field = create_modern_text_field(
            label=translator.get_text("developer.env.db_password"),
            password=True,
            can_reveal_password=True,
        )
        self.prod_db_name_field = create_modern_text_field(
            label=translator.get_text("developer.env.db_name"),
        )
        self.prod_db_url_display = create_modern_text_field(
            label=translator.get_text("developer.env.db_url"),
            read_only=True,
            multiline=True,
            height=60,
        )
        
        # Learning database MySQL fields
        self.learn_db_host_field = create_modern_text_field(
            label=translator.get_text("developer.env.db_host"),
        )
        self.learn_db_port_field = create_modern_text_field(
            label=translator.get_text("developer.env.db_port"),
        )
        self.learn_db_user_field = create_modern_text_field(
            label=translator.get_text("developer.env.db_user"),
        )
        self.learn_db_password_field = create_modern_text_field(
            label=translator.get_text("developer.env.db_password"),
            password=True,
            can_reveal_password=True,
        )
        self.learn_db_name_field = create_modern_text_field(
            label=translator.get_text("developer.env.db_name"),
        )
        self.learn_db_url_display = create_modern_text_field(
            label=translator.get_text("developer.env.db_url"),
            read_only=True,
            multiline=True,
            height=60,
        )
        
        # Other settings
        self.env_debug_field = ft.Switch(
            label=translator.get_text("developer.env.debug_mode"),
        )
        self.env_redis_url_field = create_modern_text_field(
            label=translator.get_text("developer.env.redis_url"),
        )
        self.env_cache_ttl_field = create_modern_text_field(
            label=translator.get_text("developer.env.cache_ttl"),
        )
        
        # Set up event handlers
        for field in [self.prod_db_host_field, self.prod_db_port_field, self.prod_db_user_field, 
                     self.prod_db_password_field, self.prod_db_name_field]:
            field.on_change = self._on_prod_mysql_field_change
        
        for field in [self.learn_db_host_field, self.learn_db_port_field, self.learn_db_user_field,
                     self.learn_db_password_field, self.learn_db_name_field]:
            field.on_change = self._on_learn_mysql_field_change
        
        # Don't check permissions or load data in __init__
        # This will be done in view() method when screen is actually displayed
    
    def _load_db_info(self):
        """Load database information"""
        try:
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            info = "=== Adatbázis Információk / Database Information ===\n\n"
            info += f"Engine: {engine.url}\n"
            info += f"Driver: {engine.driver}\n"
            info += f"Database: {engine.url.database}\n\n"
            info += f"Táblák / Tables ({len(tables)}):\n"
            
            for table_name in tables:
                columns = inspector.get_columns(table_name)
                info += f"\n  📊 {table_name}\n"
                for col in columns:
                    info += f"     - {col['name']}: {col['type']}\n"
            
            self.db_info_text.value = info
        except Exception as ex:
            self.db_info_text.value = f"Hiba az adatbázis információk betöltésekor / Error loading DB info: {str(ex)}"
    
    def _backup_database(self, e):
        """Create database backup"""
        try:
            import shutil
            from datetime import datetime
            
            # Get database path
            db_path = str(engine.url.database)
            
            # Create backup filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{db_path}.backup_{timestamp}"
            
            # Copy database file
            shutil.copy2(db_path, backup_path)
            
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Biztonsági mentés létrehozva / Backup created: {backup_path}"),
                bgcolor="green",
            )
            self.page.snack_bar.open = True
            self.page.update()
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Hiba / Error: {str(ex)}"),
                bgcolor="red",
            )
            self.page.snack_bar.open = True
            self.page.update()
    
    def _refresh_db_info(self, e):
        """Refresh database information"""
        self._load_db_info()
        self.page.update()
    
    def _build_mysql_url(self, mode="production"):
        """Build MySQL connection string from fields"""
        if mode == "production":
            host = self.prod_db_host_field.value or ""
            port = self.prod_db_port_field.value or "3306"
            user = self.prod_db_user_field.value or ""
            password = self.prod_db_password_field.value or ""
            database = self.prod_db_name_field.value or ""
        else:  # learning
            host = self.learn_db_host_field.value or ""
            port = self.learn_db_port_field.value or "3306"
            user = self.learn_db_user_field.value or ""
            password = self.learn_db_password_field.value or ""
            database = self.learn_db_name_field.value or ""
        
        if not all([host, port, user, password, database]):
            return ""
        
        try:
            port_int = int(port)
            encoded_password = quote_plus(password)
            url = f"mysql+pymysql://{user}:{encoded_password}@{host}:{port_int}/{database}"
            return url
        except (ValueError, Exception):
            return ""
    
    def _on_prod_mysql_field_change(self, e):
        """Update production database URL when fields change"""
        url = self._build_mysql_url("production")
        self.prod_db_url_display.value = url
        self.page.update()
    
    def _on_learn_mysql_field_change(self, e):
        """Update learning database URL when fields change"""
        url = self._build_mysql_url("learning")
        self.learn_db_url_display.value = url
        self.page.update()
    
    def _load_env_settings(self):
        """Load current .env settings"""
        try:
            if self.env_file_path.exists():
                with open(self.env_file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    # Parse .env file
                    env_vars = {}
                    for line in content.split("\n"):
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, value = line.split("=", 1)
                            env_vars[key.strip()] = value.strip().strip('"').strip("'")
                    
                    # Production database
                    self.prod_db_host_field.value = env_vars.get("DB_PROD_HOST", "")
                    self.prod_db_port_field.value = env_vars.get("DB_PROD_PORT", "")
                    self.prod_db_user_field.value = env_vars.get("DB_PROD_USER", "")
                    self.prod_db_password_field.value = env_vars.get("DB_PROD_PASSWORD", "")
                    self.prod_db_name_field.value = env_vars.get("DB_PROD_NAME", "")
                    
                    # Learning database
                    self.learn_db_host_field.value = env_vars.get("DB_LEARN_HOST", "")
                    self.learn_db_port_field.value = env_vars.get("DB_LEARN_PORT", "")
                    self.learn_db_user_field.value = env_vars.get("DB_LEARN_USER", "")
                    self.learn_db_password_field.value = env_vars.get("DB_LEARN_PASSWORD", "")
                    self.learn_db_name_field.value = env_vars.get("DB_LEARN_NAME", "")
                    
                    # Other settings
                    self.env_debug_field.value = env_vars.get("DEBUG", "False").lower() == "true"
                    self.env_redis_url_field.value = env_vars.get("REDIS_URL", "")
                    self.env_cache_ttl_field.value = env_vars.get("CACHE_DEFAULT_TTL", "")
            else:
                # Set defaults from current config
                prod_config = get_database_config("production")
                learn_config = get_database_config("learning")
                
                self.prod_db_host_field.value = prod_config["host"]
                self.prod_db_port_field.value = str(prod_config["port"])
                self.prod_db_user_field.value = prod_config["user"]
                self.prod_db_password_field.value = prod_config["password"]
                self.prod_db_name_field.value = prod_config["database"]
                
                self.learn_db_host_field.value = learn_config["host"]
                self.learn_db_port_field.value = str(learn_config["port"])
                self.learn_db_user_field.value = learn_config["user"]
                self.learn_db_password_field.value = learn_config["password"]
                self.learn_db_name_field.value = learn_config["database"]
                
                from config.app_config import DEBUG, REDIS_URL, CACHE_DEFAULT_TTL
                self.env_debug_field.value = DEBUG
                self.env_redis_url_field.value = REDIS_URL or ""
                self.env_cache_ttl_field.value = str(CACHE_DEFAULT_TTL)
            
            # Generate URLs
            self._on_prod_mysql_field_change(None)
            self._on_learn_mysql_field_change(None)
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(translator.get_text("developer.env.load_error") + f": {str(ex)}"),
                bgcolor="red",
            )
            self.page.snack_bar.open = True
            self.page.update()
    
    def _save_env_settings(self, e):
        """Save .env settings to file"""
        try:
            # Validate fields
            errors = []
            
            # Validate production database
            if not self.prod_db_host_field.value:
                errors.append("Éles adatbázis: Host kötelező / Production DB: Host required")
            if not self.prod_db_port_field.value:
                errors.append("Éles adatbázis: Port kötelező / Production DB: Port required")
            else:
                try:
                    port = int(self.prod_db_port_field.value)
                    if port < 1 or port > 65535:
                        errors.append("Éles adatbázis: Port 1-65535 között kell legyen / Production DB: Port must be 1-65535")
                except ValueError:
                    errors.append("Éles adatbázis: Port szám kell legyen / Production DB: Port must be a number")
            if not self.prod_db_user_field.value:
                errors.append("Éles adatbázis: Felhasználónév kötelező / Production DB: Username required")
            if not self.prod_db_password_field.value:
                errors.append("Éles adatbázis: Jelszó kötelező / Production DB: Password required")
            if not self.prod_db_name_field.value:
                errors.append("Éles adatbázis: Adatbázis név kötelező / Production DB: Database name required")
            
            # Validate learning database
            if not self.learn_db_host_field.value:
                errors.append("Tanuló adatbázis: Host kötelező / Learning DB: Host required")
            if not self.learn_db_port_field.value:
                errors.append("Tanuló adatbázis: Port kötelező / Learning DB: Port required")
            else:
                try:
                    port = int(self.learn_db_port_field.value)
                    if port < 1 or port > 65535:
                        errors.append("Tanuló adatbázis: Port 1-65535 között kell legyen / Learning DB: Port must be 1-65535")
                except ValueError:
                    errors.append("Tanuló adatbázis: Port szám kell legyen / Learning DB: Port must be a number")
            if not self.learn_db_user_field.value:
                errors.append("Tanuló adatbázis: Felhasználónév kötelező / Learning DB: Username required")
            if not self.learn_db_password_field.value:
                errors.append("Tanuló adatbázis: Jelszó kötelező / Learning DB: Password required")
            if not self.learn_db_name_field.value:
                errors.append("Tanuló adatbázis: Adatbázis név kötelező / Learning DB: Database name required")
            
            if errors:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("\n".join(errors)),
                    bgcolor="red",
                )
                self.page.snack_bar.open = True
                self.page.update()
                return
            
            # Build .env content
            lines = [
                "# CMMS Environment Configuration",
                "# Generated by Developer Tools",
                "# MySQL Database Connections",
                "",
                "# Production Database (Éles adatbázis)",
                f"DB_PROD_HOST={self.prod_db_host_field.value}",
                f"DB_PROD_PORT={self.prod_db_port_field.value}",
                f"DB_PROD_USER={self.prod_db_user_field.value}",
                f"DB_PROD_PASSWORD={self.prod_db_password_field.value}",
                f"DB_PROD_NAME={self.prod_db_name_field.value}",
                f"DB_PROD_URL={self._build_mysql_url('production')}",
                "",
                "# Learning Database (Tanuló adatbázis)",
                f"DB_LEARN_HOST={self.learn_db_host_field.value}",
                f"DB_LEARN_PORT={self.learn_db_port_field.value}",
                f"DB_LEARN_USER={self.learn_db_user_field.value}",
                f"DB_LEARN_PASSWORD={self.learn_db_password_field.value}",
                f"DB_LEARN_NAME={self.learn_db_name_field.value}",
                f"DB_LEARN_URL={self._build_mysql_url('learning')}",
                "",
                "# Other Settings",
                f"DEBUG={'true' if self.env_debug_field.value else 'false'}",
            ]
            
            if self.env_redis_url_field.value:
                lines.append(f"REDIS_URL={self.env_redis_url_field.value}")
            
            if self.env_cache_ttl_field.value:
                lines.append(f"CACHE_DEFAULT_TTL={self.env_cache_ttl_field.value}")
            
            # Write to file
            with open(self.env_file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(translator.get_text("developer.env.saved_successfully")),
                bgcolor="green",
            )
            self.page.snack_bar.open = True
            self.page.update()
            
            # Show warning about restart
            self._show_restart_warning()
            
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(translator.get_text("developer.env.save_error") + f": {str(ex)}"),
                bgcolor="red",
            )
            self.page.snack_bar.open = True
            self.page.update()
    
    def _test_mysql_connection(self, e, mode="production"):
        """Test MySQL connection"""
        try:
            url = self._build_mysql_url(mode)
            if not url:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(translator.get_text("developer.env.connection_failed") + ": " + translator.get_text("developer.env.load_error")),
                    bgcolor="red",
                )
                self.page.snack_bar.open = True
                self.page.update()
                return
            
            # Create temporary engine
            test_engine = create_engine(url, pool_pre_ping=True)
            
            # Test connection
            with test_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            test_engine.dispose()
            
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(translator.get_text("developer.env.connection_success")),
                bgcolor="green",
            )
            self.page.snack_bar.open = True
            self.page.update()
        except SQLAlchemyError as ex:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(translator.get_text("developer.env.connection_failed") + f": {str(ex)}"),
                bgcolor="red",
            )
            self.page.snack_bar.open = True
            self.page.update()
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(translator.get_text("developer.env.connection_failed") + f": {str(ex)}"),
                bgcolor="red",
            )
            self.page.snack_bar.open = True
            self.page.update()
    
    def _reset_env_fields(self, e):
        """Reset fields to current app_config values"""
        self._load_env_settings()
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text("Mezők visszaállítva / Fields reset"),
            bgcolor="blue",
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def _show_restart_warning(self):
        """Show dialog warning about restart requirement"""
        def close_dialog(e):
            dialog.open = False
            self.page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(translator.get_text("developer.env.restart_warning_title")),
            content=ft.Text(translator.get_text("developer.env.restart_warning_message")),
            actions=[
                ft.TextButton(translator.get_text("common.buttons.ok"), on_click=close_dialog),
            ],
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def _show_environment_info(self):
        """Get environment information"""
        import sys
        import platform
        
        info = "=== Környezeti Információk / Environment Information ===\n\n"
        info += f"Python verzió / version: {sys.version}\n"
        info += f"Platform: {platform.platform()}\n"
        info += f"Architecture: {platform.architecture()}\n"
        info += f"Machine: {platform.machine()}\n"
        info += f"Processor: {platform.processor()}\n\n"
        info += f"Munkamappa / Working directory: {os.getcwd()}\n"
        info += f"Python executable: {sys.executable}\n"
        
        return info
    
    def view(self, page: ft.Page = None):
        """View method for developer tools screen (compatible with app.py routing)"""
        if page:
            self.page = page
        
        # Check permissions here instead of __init__
        if not can_view_developer_tools():
            return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(
                            "Hozzáférés megtagadva / Access Denied",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color="red",
                        ),
                        ft.Text(
                            "Csak Developer szerepkörrel elérhető / Developer role only",
                            size=16,
                            color="grey600",
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20,
                ),
                padding=40,
                alignment=ft.alignment.center,
            )
        
        # Load data when view is called
        self._load_db_info()
        self._load_env_settings()
        
        return self.build()
    
    def build(self):
        """Build the developer tools screen"""
        # Ensure page is set
        if not self.page:
            return ft.Container(
                content=ft.Text("Hiba: Page nincs beállítva / Error: Page not set"),
                padding=20,
            )
        
        # Don't include title here - it's already in the topbar
        return ft.Column(
            controls=[
                # .env Configuration section
                create_tailwind_card(
                    content=ft.Column(
                        controls=[
                            ft.Row([
                                ft.Icon(
                                    ft.Icons.SETTINGS if hasattr(ft.Icons, 'SETTINGS') else ft.Icons.SETTINGS_APPLICATIONS,
                                    size=32,
                                    color=DesignSystem.PURPLE_500,
                                ),
                                ft.Text(
                                    translator.get_text("developer.env.title"),
                                    size=20,
                                    weight=ft.FontWeight.W_700,
                                ),
                            ], spacing=DesignSystem.SPACING_3),
                            ft.Divider(height=1),
                            ft.Text(
                                translator.get_text("developer.env.description"),
                                size=13,
                                color=DesignSystem.TEXT_SECONDARY,
                            ),
                            
                            # Production Database Section
                            create_tailwind_card(
                                content=ft.Column(
                                    controls=[
                                        ft.Text(
                                            translator.get_text("developer.env.production_db"),
                                            size=16,
                                            weight=ft.FontWeight.W_600,
                                            color=DesignSystem.EMERALD_700,
                                        ),
                                        ft.Row(
                                            controls=[
                                                ft.Container(self.prod_db_host_field, expand=True),
                                                ft.Container(self.prod_db_port_field, width=150),
                                            ],
                                            spacing=DesignSystem.SPACING_3,
                                        ),
                                        ft.Row(
                                            controls=[
                                                ft.Container(self.prod_db_user_field, expand=True),
                                                ft.Container(self.prod_db_password_field, expand=True),
                                            ],
                                            spacing=DesignSystem.SPACING_3,
                                        ),
                                        self.prod_db_name_field,
                                        self.prod_db_url_display,
                                        create_modern_button(
                                            text=translator.get_text("developer.env.test_connection_button"),
                                            icon=ft.Icons.CHECK_CIRCLE if hasattr(ft.Icons, 'CHECK_CIRCLE') else ft.Icons.CHECK,
                                            on_click=lambda e: self._test_mysql_connection(e, "production"),
                                            bgcolor=DesignSystem.EMERALD_500,
                                            color=DesignSystem.WHITE,
                                        ),
                                    ],
                                    spacing=DesignSystem.SPACING_3,
                                ),
                                padding=DesignSystem.SPACING_4,
                                accent_color=DesignSystem.EMERALD_500,
                            ),
                            
                            ft.Divider(height=DesignSystem.SPACING_2),
                            
                            # Learning Database Section
                            create_tailwind_card(
                                content=ft.Column(
                                    controls=[
                                        ft.Text(
                                            translator.get_text("developer.env.learning_db"),
                                            size=16,
                                            weight=ft.FontWeight.W_600,
                                            color=DesignSystem.ORANGE_700,
                                        ),
                                        ft.Row(
                                            controls=[
                                                ft.Container(self.learn_db_host_field, expand=True),
                                                ft.Container(self.learn_db_port_field, width=150),
                                            ],
                                            spacing=DesignSystem.SPACING_3,
                                        ),
                                        ft.Row(
                                            controls=[
                                                ft.Container(self.learn_db_user_field, expand=True),
                                                ft.Container(self.learn_db_password_field, expand=True),
                                            ],
                                            spacing=DesignSystem.SPACING_3,
                                        ),
                                        self.learn_db_name_field,
                                        self.learn_db_url_display,
                                        create_modern_button(
                                            text=translator.get_text("developer.env.test_connection_button"),
                                            icon=ft.Icons.CHECK_CIRCLE if hasattr(ft.Icons, 'CHECK_CIRCLE') else ft.Icons.CHECK,
                                            on_click=lambda e: self._test_mysql_connection(e, "learning"),
                                            bgcolor=DesignSystem.EMERALD_500,
                                            color=DesignSystem.WHITE,
                                        ),
                                    ],
                                    spacing=DesignSystem.SPACING_3,
                                ),
                                padding=DesignSystem.SPACING_4,
                                accent_color=DesignSystem.ORANGE_500,
                            ),
                            
                            ft.Divider(height=DesignSystem.SPACING_2),
                            
                            # Other Settings
                            ft.Text(
                                "Egyéb beállítások / Other Settings",
                                size=16,
                                weight=ft.FontWeight.W_600,
                            ),
                            ft.Row(
                                controls=[
                                    self.env_debug_field,
                                ],
                            ),
                            self.env_redis_url_field,
                            self.env_cache_ttl_field,
                            
                            # Action Buttons
                            ft.Row(
                                controls=[
                                    create_modern_button(
                                        text=translator.get_text("developer.env.save_button"),
                                        icon=ft.Icons.SAVE if hasattr(ft.Icons, 'SAVE') else ft.Icons.SAVE_ALT,
                                        on_click=self._save_env_settings,
                                        bgcolor=DesignSystem.SUCCESS,
                                        color=DesignSystem.WHITE,
                                    ),
                                    create_modern_button(
                                        text=translator.get_text("developer.env.reset_button"),
                                        icon=ft.Icons.REFRESH if hasattr(ft.Icons, 'REFRESH') else ft.Icons.REFRESH,
                                        on_click=self._reset_env_fields,
                                        variant="outlined",
                                    ),
                                ],
                                spacing=DesignSystem.SPACING_3,
                            ),
                        ],
                        spacing=DesignSystem.SPACING_4,
                    ),
                    padding=DesignSystem.SPACING_6,
                ),
                
                # Database section
                create_tailwind_card(
                    content=ft.Column(
                        controls=[
                            ft.Row([
                                ft.Icon(
                                    ft.Icons.STORAGE if hasattr(ft.Icons, 'STORAGE') else (ft.Icons.DATABASE if hasattr(ft.Icons, 'DATABASE') else ft.Icons.FOLDER),
                                    size=32,
                                    color=DesignSystem.BLUE_500,
                                ),
                                ft.Text("Adatbázis / Database", size=20, weight=ft.FontWeight.W_700),
                            ], spacing=DesignSystem.SPACING_3),
                            ft.Divider(height=1),
                            ft.Row(
                                controls=[
                                    create_modern_button(
                                        text="Frissítés / Refresh",
                                        icon=ft.Icons.REFRESH if hasattr(ft.Icons, 'REFRESH') else ft.Icons.REFRESH,
                                        on_click=self._refresh_db_info,
                                        variant="outlined",
                                    ),
                                    create_modern_button(
                                        text="Biztonsági mentés / Backup",
                                        icon=ft.Icons.BACKUP if hasattr(ft.Icons, 'BACKUP') else (ft.Icons.SAVE if hasattr(ft.Icons, 'SAVE') else ft.Icons.SAVE_ALT),
                                        on_click=self._backup_database,
                                        bgcolor=DesignSystem.BLUE_500,
                                        color=DesignSystem.WHITE,
                                    ),
                                ],
                                spacing=DesignSystem.SPACING_3,
                            ),
                            ft.Container(
                                content=ft.Column(
                                    controls=[
                                        self.db_info_text,
                                    ],
                                    scroll=ft.ScrollMode.AUTO,
                                ),
                                bgcolor=DesignSystem.BG_SECONDARY,
                                padding=DesignSystem.SPACING_4,
                                border_radius=DesignSystem.RADIUS_MD,
                                height=300,
                            ),
                        ],
                        spacing=DesignSystem.SPACING_4,
                    ),
                    padding=DesignSystem.SPACING_6,
                ),
                
                # Environment section
                create_tailwind_card(
                    content=ft.Column(
                        controls=[
                            ft.Row([
                                ft.Icon(
                                    ft.Icons.COMPUTER if hasattr(ft.Icons, 'COMPUTER') else (ft.Icons.DESKTOP_WINDOWS if hasattr(ft.Icons, 'DESKTOP_WINDOWS') else ft.Icons.SETTINGS),
                                    size=32,
                                    color=DesignSystem.CYAN_500,
                                ),
                                ft.Text("Környezet / Environment", size=20, weight=ft.FontWeight.W_700),
                            ], spacing=DesignSystem.SPACING_3),
                            ft.Divider(height=1),
                            ft.Container(
                                content=ft.Text(
                                    self._show_environment_info(),
                                    selectable=True,
                                    size=12,
                                    font_family="monospace",
                                ),
                                bgcolor=DesignSystem.BG_SECONDARY,
                                padding=DesignSystem.SPACING_4,
                                border_radius=DesignSystem.RADIUS_MD,
                            ),
                        ],
                        spacing=DesignSystem.SPACING_4,
                    ),
                    padding=DesignSystem.SPACING_6,
                ),
            ],
            expand=True,
            spacing=15,
            scroll=ft.ScrollMode.AUTO,
        )
