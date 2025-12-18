"""
Log Screen - Detailed system logging view
"""

import flet as ft
from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# Compatibility for flet 0.23.2 - Icons are strings, not ft.Icons
if not hasattr(ft, 'Icons'):
    from utils.flet_icons import Icons
    ft.Icons = Icons

from services.log_service import get_logs, get_log_statistics
from services.context_service import get_current_user_id
from localization.translator import translator
from ui.components.modern_components import (
    create_modern_button,
    create_modern_card,
    create_modern_text_field,
    create_modern_dropdown,
    create_modern_icon_button,
    create_modern_divider,
    create_vibrant_badge,
    create_empty_state_card,
    DesignSystem,
)
from ui.components.modern_card import (
    create_tailwind_card,
    create_info_card,
)
from database.session_manager import SessionLocal
from database.models import SystemLog

import logging

logger = logging.getLogger(__name__)


class LogScreen:
    def __init__(self, page: ft.Page):
        self.page = page
        self.current_category = None
        self.current_year = None
        self.current_month = None
        self.current_week = None
        self.current_day = None
        self.expanded_logs = {}  # Track which logs are expanded
        
    def view(self, page: ft.Page):
        """Main view for log screen"""
        if not hasattr(self, 'page') or self.page is None:
            self.page = page
        
        # Main container
        main_container = ft.Container(
            content=ft.Row([
                # Sidebar with categories
                self._build_sidebar(),
                # Main content area
                self._build_main_content(),
            ], spacing=0, expand=True),
            expand=True,
            padding=DesignSystem.SPACING_MD,
        )
        
        return main_container
    
    def _build_sidebar(self) -> ft.Container:
        """Build sidebar with date and category filters"""
        # Get current date for default selection
        now = datetime.now()
        current_year = now.year
        current_month = now.month
        
        # Get available years from logs
        session = SessionLocal()
        try:
            years = session.query(SystemLog.year).distinct().order_by(SystemLog.year.desc()).all()
            years_list = [str(y[0]) for y in years if y[0] is not None]
        except:
            years_list = [str(current_year)]
        finally:
            session.close()
        
        # Year selector
        year_dropdown = create_modern_dropdown(
            label=translator.get_text("logs.filters.year") if hasattr(translator, 'get_text') else "Év / Year",
            options=[ft.dropdown.Option(y) for y in years_list] if years_list else [],
            value=str(current_year) if str(current_year) in years_list else (years_list[0] if years_list else None),
            on_change=lambda e: self._on_year_change(e.control.value),
            width=150,
        )
        
        # Month selector
        month_options = [
            ft.dropdown.Option("1", "Január / January"),
            ft.dropdown.Option("2", "Február / February"),
            ft.dropdown.Option("3", "Március / March"),
            ft.dropdown.Option("4", "Április / April"),
            ft.dropdown.Option("5", "Május / May"),
            ft.dropdown.Option("6", "Június / June"),
            ft.dropdown.Option("7", "Július / July"),
            ft.dropdown.Option("8", "Augusztus / August"),
            ft.dropdown.Option("9", "Szeptember / September"),
            ft.dropdown.Option("10", "Október / October"),
            ft.dropdown.Option("11", "November / November"),
            ft.dropdown.Option("12", "December / December"),
        ]
        
        month_dropdown = create_modern_dropdown(
            label=translator.get_text("logs.filters.month") if hasattr(translator, 'get_text') else "Hónap / Month",
            options=month_options,
            value=str(current_month),
            on_change=lambda e: self._on_month_change(e.control.value),
            width=200,
        )
        
        # Category filter
        category_options = [
            ft.dropdown.Option("", translator.get_text("logs.filters.all_categories") if hasattr(translator, 'get_text') else "Összes kategória / All Categories"),
            ft.dropdown.Option("document", translator.get_text("logs.categories.document") if hasattr(translator, 'get_text') else "Dokumentumok / Documents"),
            ft.dropdown.Option("worksheet", translator.get_text("logs.categories.worksheet") if hasattr(translator, 'get_text') else "Munkalapok / Worksheets"),
            ft.dropdown.Option("work_request", translator.get_text("logs.categories.work_request") if hasattr(translator, 'get_text') else "Munkaigénylők / Work Requests"),
            ft.dropdown.Option("scrapping", translator.get_text("logs.categories.scrapping") if hasattr(translator, 'get_text') else "Selejtezési lapok / Scrapping Documents"),
            ft.dropdown.Option("task", translator.get_text("logs.categories.task") if hasattr(translator, 'get_text') else "Feladatok / Tasks"),
            ft.dropdown.Option("assignment", translator.get_text("logs.categories.assignment") if hasattr(translator, 'get_text') else "Kiosztások / Assignments"),
            ft.dropdown.Option("inventory", translator.get_text("logs.categories.inventory") if hasattr(translator, 'get_text') else "Készlet / Inventory"),
            ft.dropdown.Option("asset", translator.get_text("logs.categories.asset") if hasattr(translator, 'get_text') else "Eszközök / Assets"),
            ft.dropdown.Option("user", translator.get_text("logs.categories.user") if hasattr(translator, 'get_text') else "Felhasználók / Users"),
            ft.dropdown.Option("vacation", translator.get_text("logs.categories.vacation") if hasattr(translator, 'get_text') else "Szabadság / Vacation"),
            ft.dropdown.Option("shift", translator.get_text("logs.categories.shift") if hasattr(translator, 'get_text') else "Munkabeosztás / Shift Schedule"),
        ]
        
        category_dropdown = create_modern_dropdown(
            label=translator.get_text("logs.filters.category") if hasattr(translator, 'get_text') else "Kategória / Category",
            options=category_options,
            value="",
            on_change=lambda e: self._on_category_change(e.control.value),
            width=200,
        )
        
        # Search field
        search_field = create_modern_text_field(
            label=translator.get_text("logs.filters.search") if hasattr(translator, 'get_text') else "Keresés / Search",
            hint_text=translator.get_text("logs.filters.search_hint") if hasattr(translator, 'get_text') else "Keresés leírásban...",
            on_change=lambda e: self._on_search_change(e.control.value),
            width=200,
        )
        
        sidebar_content = ft.Column([
            ft.Text(
                translator.get_text("logs.title") if hasattr(translator, 'get_text') else "Rendszer naplók / System Logs",
                size=20,
                weight=ft.FontWeight.W_600,
                color=DesignSystem.TEXT_PRIMARY,
            ),
            create_modern_divider(),
            ft.Container(height=DesignSystem.SPACING_MD),
            year_dropdown,
            month_dropdown,
            category_dropdown,
            search_field,
            create_modern_divider(),
            ft.Container(height=DesignSystem.SPACING_MD),
            create_modern_button(
                text=translator.get_text("logs.filters.reset") if hasattr(translator, 'get_text') else "Szűrők törlése / Reset Filters",
                icon=ft.Icons.REFRESH,
                on_click=self._reset_filters,
                variant="outlined",
                width=200,
            ),
        ], spacing=DesignSystem.SPACING_MD, scroll=ft.ScrollMode.AUTO)
        
        return ft.Container(
            content=sidebar_content,
            width=250,
            padding=DesignSystem.SPACING_MD,
            bgcolor=DesignSystem.BG_TERTIARY,
            border_radius=DesignSystem.RADIUS_LG,
            margin=ft.margin.only(right=DesignSystem.SPACING_MD),
        )
    
    def _build_main_content(self) -> ft.Container:
        """Build main content area with log list in grid layout"""
        self.log_list = ft.GridView(
            runs_count=2,  # 2 columns for better information display
            max_extent=600,
            spacing=DesignSystem.SPACING_4,
            run_spacing=DesignSystem.SPACING_4,
            child_aspect_ratio=1.3,
        )
        
        # Use Column wrapper to handle empty state
        self.main_content_wrapper = ft.Column(
            controls=[self.log_list],
            spacing=0,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )
        
        # Load initial logs (after wrapper is created)
        self._load_logs()
        
        return ft.Container(
            content=self.main_content_wrapper,
            expand=True,
            padding=DesignSystem.SPACING_MD,
        )
    
    def _load_logs(self):
        """Load logs based on current filters"""
        session = SessionLocal()
        try:
            logs = get_logs(
                category=self.current_category if self.current_category else None,
                year=int(self.current_year) if self.current_year else None,
                month=int(self.current_month) if self.current_month else None,
                week=int(self.current_week) if self.current_week else None,
                day=int(self.current_day) if self.current_day else None,
                limit=100,
                session=session
            )
            
            # Ensure main_content_wrapper exists
            if not hasattr(self, 'main_content_wrapper') or self.main_content_wrapper is None:
                self.main_content_wrapper = ft.Column(
                    controls=[self.log_list] if hasattr(self, 'log_list') else [],
                    spacing=0,
                    expand=True,
                    scroll=ft.ScrollMode.AUTO,
                )
            
            if not logs:
                # Empty state - replace GridView with empty state card
                empty_card = create_empty_state_card(
                    icon=ft.Icons.INFO,
                    title=translator.get_text("logs.no_logs") if hasattr(translator, 'get_text') else "Nincsenek log bejegyzések / No log entries",
                    icon_color=DesignSystem.GRAY_400,
                )
                self.main_content_wrapper.controls.clear()
                self.main_content_wrapper.controls.append(
                    ft.Container(
                        content=empty_card,
                        alignment=ft.alignment.center,
                        expand=True,
                    )
                )
            else:
                # Clear wrapper and add GridView with logs
                self.main_content_wrapper.controls.clear()
                self.log_list.controls.clear()
                for log in logs:
                    self.log_list.controls.append(self._build_log_card(log, session))
                self.main_content_wrapper.controls.append(self.log_list)
        except Exception as e:
            logger.error(f"Error loading logs: {e}", exc_info=True)
            if hasattr(self, 'main_content_wrapper'):
                self.main_content_wrapper.controls.clear()
                self.main_content_wrapper.controls.append(
                    ft.Container(
                        content=ft.Text(
                            f"Error loading logs: {e}",
                            color=DesignSystem.ERROR,
                        ),
                        padding=DesignSystem.SPACING_MD,
                        alignment=ft.alignment.center,
                    )
                )
            else:
                # Fallback if wrapper doesn't exist yet
                self.log_list.controls.clear()
                self.log_list.controls.append(
                    ft.Container(
                        content=ft.Text(
                            f"Error loading logs: {e}",
                            color=DesignSystem.ERROR,
                        ),
                        padding=DesignSystem.SPACING_MD,
                    )
                )
        finally:
            session.close()
        
        if hasattr(self, 'page') and self.page:
            self.page.update()
    
    def _build_log_card(self, log: SystemLog, session: Session) -> ft.Container:
        """Build a detailed log card with comprehensive information"""
        is_expanded = self.expanded_logs.get(log.id, False)
        
        # Determine colors based on category and action
        category_colors = {
            "document": DesignSystem.BLUE_500,
            "worksheet": DesignSystem.EMERALD_500,
            "work_request": DesignSystem.ORANGE_500,
            "scrapping": DesignSystem.RED_500,
            "task": DesignSystem.PURPLE_500,
            "assignment": DesignSystem.CYAN_500,
            "inventory": DesignSystem.PINK_500,
            "asset": DesignSystem.PURPLE_500,
            "user": DesignSystem.BLUE_500,
            "vacation": DesignSystem.CYAN_500,
            "shift": DesignSystem.ORANGE_500,
        }
        
        action_colors = {
            "create": DesignSystem.SUCCESS,
            "update": DesignSystem.INFO,
            "delete": DesignSystem.ERROR,
            "approve": DesignSystem.SUCCESS,
            "reject": DesignSystem.ERROR,
            "assign": DesignSystem.INFO,
            "complete": DesignSystem.SUCCESS,
        }
        
        category_color = category_colors.get(log.log_category, DesignSystem.GRAY_500)
        action_color = action_colors.get(log.action_type.lower(), DesignSystem.GRAY_500)
        
        # Timestamp formatting
        timestamp_str = log.timestamp.strftime("%Y-%m-%d %H:%M:%S") if log.timestamp else "-"
        date_str = log.timestamp.strftime("%Y-%m-%d") if log.timestamp else "-"
        time_str = log.timestamp.strftime("%H:%M:%S") if log.timestamp else "-"
        
        # User info
        user_info = "-"
        user_username = "-"
        if log.user:
            user_info = log.user.full_name if log.user.full_name else log.user.username
            user_username = log.user.username
        
        # Entity info
        entity_display = f"{log.entity_type} #{log.entity_id}" if log.entity_id else log.entity_type or "-"
        
        # Format metadata for display (exclude changes as they will be shown separately)
        metadata_without_changes = {}
        if log.log_metadata and isinstance(log.log_metadata, dict):
            metadata_without_changes = {k: v for k, v in log.log_metadata.items() if k != "changes"}
        formatted_metadata = self._format_metadata(metadata_without_changes, session) if metadata_without_changes else None
        
        # Build card content
        card_content_items = [
            # Header row with icon, category, and action badges
            ft.Row([
                ft.Container(
                    content=ft.Icon(
                        self._get_category_icon(log.log_category),
                        size=28,
                        color=category_color,
                    ),
                    padding=ft.padding.all(DesignSystem.SPACING_2),
                    bgcolor=f"{category_color}15",
                    border_radius=DesignSystem.RADIUS_LG,
                ),
                ft.Column([
                    ft.Row([
                        create_vibrant_badge(
                            text=log.log_category.upper() if log.log_category else "UNKNOWN",
                            variant=self._get_category_variant(log.log_category),
                            size=11,
                        ),
                        create_vibrant_badge(
                            text=log.action_type.upper() if log.action_type else "UNKNOWN",
                            variant=self._get_action_variant(log.action_type),
                            size=11,
                        ),
                    ], spacing=DesignSystem.SPACING_2),
                    ft.Text(
                        entity_display,
                        size=16,
                        weight=ft.FontWeight.W_600,
                        color=DesignSystem.TEXT_PRIMARY,
                    ),
                ], spacing=DesignSystem.SPACING_1, tight=True, expand=True),
                ft.Column([
                    ft.Text(
                        f"ID: {log.id}",
                        size=11,
                        weight=ft.FontWeight.W_500,
                        color=DesignSystem.TEXT_SECONDARY,
                    ),
                    ft.Text(
                        date_str,
                        size=12,
                        weight=ft.FontWeight.W_500,
                        color=DesignSystem.TEXT_PRIMARY,
                    ),
                    ft.Text(
                        time_str,
                        size=11,
                        color=DesignSystem.TEXT_SECONDARY,
                    ),
                ], spacing=0, tight=True, horizontal_alignment=ft.CrossAxisAlignment.END),
            ], spacing=DesignSystem.SPACING_3),
            
            # Description section
            ft.Container(
                content=ft.Column([
                    ft.Text(
                        translator.get_text("logs.details.description") if hasattr(translator, 'get_text') else "Leírás / Description",
                        size=11,
                        weight=ft.FontWeight.W_600,
                        color=DesignSystem.TEXT_SECONDARY,
                    ),
                    ft.Text(
                        log.description or "-",
                        size=13,
                        color=DesignSystem.TEXT_PRIMARY,
                        max_lines=3 if not is_expanded else None,
                    ),
                ], spacing=DesignSystem.SPACING_1, tight=True),
                padding=ft.padding.all(DesignSystem.SPACING_3),
                bgcolor=DesignSystem.GRAY_50,
                border_radius=DesignSystem.RADIUS_MD,
            ),
            
            # Info grid - always visible
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Column([
                            ft.Text(
                                translator.get_text("logs.details.user") if hasattr(translator, 'get_text') else "Felhasználó / User",
                                size=10,
                                color=DesignSystem.TEXT_SECONDARY,
                            ),
                            ft.Row([
                                ft.Icon(ft.Icons.PERSON, size=14, color=DesignSystem.TEXT_SECONDARY),
                                ft.Text(
                                    user_info,
                                    size=12,
                                    weight=ft.FontWeight.W_500,
                                    color=DesignSystem.TEXT_PRIMARY,
                                ),
                            ], spacing=DesignSystem.SPACING_1, tight=True),
                        ], spacing=2, tight=True, expand=True),
                        ft.Column([
                            ft.Text(
                                translator.get_text("logs.details.entity") if hasattr(translator, 'get_text') else "Entitás / Entity",
                                size=10,
                                color=DesignSystem.TEXT_SECONDARY,
                            ),
                            ft.Text(
                                entity_display,
                                size=12,
                                weight=ft.FontWeight.W_500,
                                color=DesignSystem.TEXT_PRIMARY,
                            ),
                        ], spacing=2, tight=True, expand=True),
                    ], spacing=DesignSystem.SPACING_4),
                ], spacing=DesignSystem.SPACING_2, tight=True),
                padding=ft.padding.all(DesignSystem.SPACING_3),
                bgcolor=DesignSystem.BG_SECONDARY,
                border_radius=DesignSystem.RADIUS_MD,
            ),
        ]
        
        # Expanded content with detailed metadata
        if is_expanded:
            expanded_items = []
            
            # Changes section (if available)
            if log.log_metadata and isinstance(log.log_metadata, dict) and "changes" in log.log_metadata:
                changes = log.log_metadata["changes"]
                if isinstance(changes, dict) and changes:
                    changes_text_items = []
                    
                    # Field name translations
                    field_translations = {
                        "name": "Név / Name",
                        "sku": "Cikkszám / SKU",
                        "serial_number": "Sorozatszám / Serial Number",
                        "model": "Modell / Model",
                        "manufacturer": "Gyártó / Manufacturer",
                        "category": "Kategória / Category",
                        "buy_price": "Vételár / Buy Price",
                        "sell_price": "Eladási ár / Sell Price",
                        "safety_stock": "Biztonsági készlet / Safety Stock",
                        "reorder_quantity": "Újrarendelési mennyiség / Reorder Quantity",
                        "description": "Leírás / Description",
                        "unit": "Mértékegység / Unit",
                        "bin_location": "Helyszín / Location",
                        "status": "Státusz / Status",
                        "operating_hours": "Üzemóra / Operating Hours",
                        "asset_tag": "Eszköz azonosító / Asset Tag",
                        "production_line_id": "Termelési sor / Production Line",
                        "maintenance_interval": "Karbantartási intervallum / Maintenance Interval",
                        "install_date": "Telepítés dátuma / Install Date",
                        "purchase_date": "Vásárlás dátuma / Purchase Date",
                        "purchase_price": "Vételár / Purchase Price",
                        "warranty_expiry_date": "Jótállás lejárat / Warranty Expiry",
                        "supplier": "Beszállító / Supplier",
                        "last_service_date": "Utolsó szerviz / Last Service",
                        "next_service_date": "Következő szerviz / Next Service",
                        "criticality_level": "Kritikussági szint / Criticality Level",
                        "energy_consumption": "Energiafogyasztás / Energy Consumption",
                        "power_requirements": "Teljesítmény igény / Power Requirements",
                        "operating_temperature_range": "Működési hőmérséklet / Operating Temperature",
                        "weight": "Súly / Weight",
                        "dimensions": "Méretek / Dimensions",
                        "notes": "Megjegyzések / Notes",
                        "compatible_machine_ids": "Kompatibilis gépek / Compatible Machines",
                        "operating_hours_update_frequency_type": "Üzemóra frissítési típus / Operating Hours Update Frequency Type",
                        "operating_hours_update_frequency_value": "Üzemóra frissítési érték / Operating Hours Update Frequency Value",
                    }
                    
                    for field, change_data in changes.items():
                        if isinstance(change_data, dict) and "old" in change_data and "new" in change_data:
                            old_val = change_data.get("old", "Nincs / None")
                            new_val = change_data.get("new", "Nincs / None")
                            
                            # Handle None values
                            if old_val == "None" or old_val is None:
                                old_val = "Nincs / None"
                            if new_val == "None" or new_val is None:
                                new_val = "Nincs / None"
                            
                            # Get translated field name
                            field_display = field_translations.get(field, field.replace("_", " ").title())
                            
                            # Format: Field Name: Old Value → New Value
                            changes_text_items.append(f"{field_display}: {old_val} → {new_val}")
                    
                    if changes_text_items:
                        expanded_items.append(
                            ft.Container(
                                content=ft.Column([
                                    ft.Text(
                                        translator.get_text("logs.details.changes") if hasattr(translator, 'get_text') else "Változtatások / Changes",
                                        size=11,
                                        weight=ft.FontWeight.W_600,
                                        color=DesignSystem.TEXT_SECONDARY,
                                    ),
                                    ft.Text(
                                        "\n".join(changes_text_items),
                                        size=11,
                                        color=DesignSystem.TEXT_PRIMARY,
                                    ),
                                ], spacing=DesignSystem.SPACING_1, tight=True),
                                padding=ft.padding.all(DesignSystem.SPACING_2),
                                bgcolor=DesignSystem.ORANGE_50,
                                border_radius=DesignSystem.RADIUS_MD,
                            )
                        )
            
            # User details
            if log.user:
                expanded_items.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Text(
                                translator.get_text("logs.details.user_info") if hasattr(translator, 'get_text') else "Felhasználó információk / User Info",
                                size=11,
                                weight=ft.FontWeight.W_600,
                                color=DesignSystem.TEXT_SECONDARY,
                            ),
                            ft.Row([
                                ft.Text("Név / Name:", size=11, color=DesignSystem.TEXT_SECONDARY, width=100),
                                ft.Text(user_info, size=11, color=DesignSystem.TEXT_PRIMARY, expand=True),
                            ]),
                            ft.Row([
                                ft.Text("Felhasználónév / Username:", size=11, color=DesignSystem.TEXT_SECONDARY, width=100),
                                ft.Text(user_username, size=11, color=DesignSystem.TEXT_PRIMARY, expand=True),
                            ]),
                        ], spacing=DesignSystem.SPACING_1, tight=True),
                        padding=ft.padding.all(DesignSystem.SPACING_2),
                        bgcolor=DesignSystem.BLUE_50,
                        border_radius=DesignSystem.RADIUS_MD,
                    )
                )
            
            # Metadata details
            if formatted_metadata:
                expanded_items.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Text(
                                translator.get_text("logs.details.metadata") if hasattr(translator, 'get_text') else "Metaadatok / Metadata",
                                size=11,
                                weight=ft.FontWeight.W_600,
                                color=DesignSystem.TEXT_SECONDARY,
                            ),
                            ft.Text(
                                formatted_metadata,
                                size=11,
                                color=DesignSystem.TEXT_PRIMARY,
                            ),
                        ], spacing=DesignSystem.SPACING_1, tight=True),
                        padding=ft.padding.all(DesignSystem.SPACING_2),
                        bgcolor=DesignSystem.PURPLE_50,
                        border_radius=DesignSystem.RADIUS_MD,
                    )
                )
            
            # Raw metadata (if available and different from formatted)
            if log.log_metadata and isinstance(log.log_metadata, dict):
                import json
                raw_metadata_str = json.dumps(log.log_metadata, indent=2, ensure_ascii=False)
                expanded_items.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Text(
                                translator.get_text("logs.details.raw_metadata") if hasattr(translator, 'get_text') else "Nyers metaadatok / Raw Metadata",
                                size=11,
                                weight=ft.FontWeight.W_600,
                                color=DesignSystem.TEXT_SECONDARY,
                            ),
                            ft.Text(
                                raw_metadata_str,
                                size=10,
                                color=DesignSystem.TEXT_SECONDARY,
                                font_family="monospace",
                                max_lines=10,
                            ),
                        ], spacing=DesignSystem.SPACING_1, tight=True),
                        padding=ft.padding.all(DesignSystem.SPACING_2),
                        bgcolor=DesignSystem.GRAY_50,
                        border_radius=DesignSystem.RADIUS_MD,
                    )
                )
            
            if expanded_items:
                card_content_items.append(
                    ft.Container(
                        content=ft.Column(expanded_items, spacing=DesignSystem.SPACING_2),
                        padding=ft.padding.only(top=DesignSystem.SPACING_3),
                    )
                )
        
        # View details button - opens dialog instead of expanding inline
        view_details_button = ft.Row([
            ft.Container(expand=True),
            create_modern_button(
                text=translator.get_text("logs.view_details") if hasattr(translator, 'get_text') else "Részletek megtekintése",
                icon=ft.Icons.INFO_OUTLINE if hasattr(ft.Icons, 'INFO_OUTLINE') else ft.Icons.INFO,
                on_click=lambda e, log_id=log.id: self._open_log_details_dialog(log_id, session),
                variant="outlined",
                width=180,
            ),
        ], alignment=ft.MainAxisAlignment.END)
        
        card_content_items.append(view_details_button)
        
        # Build final card content
        card_content = ft.Column(card_content_items, spacing=DesignSystem.SPACING_3)
        card_content.controls = [c for c in card_content.controls if c is not None]
        
        card = create_tailwind_card(
            content=card_content,
            padding=DesignSystem.SPACING_4,
            elevation=1,
            accent_color=category_color,
        )
        
        return card
    
    def _get_category_icon(self, category: str) -> str:
        """Get icon for log category - using safe icon names that exist in Flet"""
        # Helper function to safely get icon with fallbacks
        def get_safe_icon(*icon_names):
            for icon_name in icon_names:
                try:
                    if hasattr(ft.Icons, icon_name):
                        return getattr(ft.Icons, icon_name)
                except (AttributeError, TypeError):
                    continue
            # Ultimate fallback
            try:
                return ft.Icons.INFO if hasattr(ft.Icons, 'INFO') else "info"
            except:
                return "info"
        
        # Map categories to icons with fallbacks
        icon_map = {
            "document": lambda: get_safe_icon("DESCRIPTION", "INSERT_DRIVE_FILE"),
            "worksheet": lambda: get_safe_icon("ASSIGNMENT", "DESCRIPTION"),
            "work_request": lambda: get_safe_icon("BUILD", "CONSTRUCTION", "DESCRIPTION"),
            "scrapping": lambda: get_safe_icon("DELETE", "CLOSE", "CANCEL"),
            "task": lambda: get_safe_icon("CHECK_CIRCLE", "CHECK", "DONE"),
            "assignment": lambda: get_safe_icon("ASSIGNMENT", "DESCRIPTION"),
            "inventory": lambda: get_safe_icon("INVENTORY_2", "INVENTORY", "STORAGE", "SHOPPING_CART"),
            "asset": lambda: get_safe_icon("PRECISION_MANUFACTURING", "FACTORY", "BUILD", "SETTINGS"),
            "user": lambda: get_safe_icon("PERSON", "ACCOUNT_CIRCLE", "PERSON_OUTLINE"),
            "vacation": lambda: get_safe_icon("CALENDAR_MONTH", "CALENDAR_TODAY", "EVENT"),
            "shift": lambda: get_safe_icon("SCHEDULE", "ACCESS_TIME", "CLOCK"),
        }
        
        # Get icon function and call it
        icon_func = icon_map.get(category)
        if icon_func:
            return icon_func()
        else:
            return get_safe_icon("INFO")
    
    def _get_category_variant(self, category: str) -> str:
        """Get badge variant for category"""
        variant_map = {
            "document": "blue",
            "worksheet": "emerald",
            "work_request": "orange",
            "scrapping": "red",
            "task": "purple",
            "assignment": "cyan",
            "inventory": "pink",
            "asset": "purple",
            "user": "blue",
            "vacation": "cyan",
            "shift": "orange",
        }
        return variant_map.get(category, None)
    
    def _get_action_variant(self, action: str) -> str:
        """Get badge variant for action"""
        action_lower = action.lower() if action else ""
        if action_lower in ["create", "approve", "complete"]:
            return "emerald"
        elif action_lower in ["update", "assign"]:
            return "blue"
        elif action_lower in ["delete", "reject"]:
            return "red"
        return None
    
    def _toggle_log_expand(self, log_id: int):
        """Toggle log expansion"""
        self.expanded_logs[log_id] = not self.expanded_logs.get(log_id, False)
        self._load_logs()
    
    def _open_log_details_dialog(self, log_id: int, session: Session):
        """Open a dialog with full log details"""
        try:
            log = session.query(SystemLog).filter_by(id=log_id).first()
            if not log:
                return
            
            # Format metadata (exclude changes as they will be shown separately)
            metadata_without_changes = {}
            if log.log_metadata and isinstance(log.log_metadata, dict):
                metadata_without_changes = {k: v for k, v in log.log_metadata.items() if k != "changes"}
            formatted_metadata = self._format_metadata(metadata_without_changes, session) if metadata_without_changes else None
            
            # User info
            user_info = "-"
            user_username = "-"
            if log.user:
                user_info = log.user.full_name if log.user.full_name else log.user.username
                user_username = log.user.username
            
            # Timestamp
            timestamp_str = log.timestamp.strftime("%Y-%m-%d %H:%M:%S") if log.timestamp else "-"
            
            # Entity info
            entity_display = f"{log.entity_type} #{log.entity_id}" if log.entity_id else log.entity_type or "-"
            
            # Build dialog content items list
            dialog_content_items = [
                # Header
                ft.Container(
                    content=ft.Row([
                        ft.Icon(
                            self._get_category_icon(log.log_category),
                            size=32,
                            color=DesignSystem.BLUE_500,
                        ),
                        ft.Column([
                            ft.Text(
                                translator.get_text("logs.details.title") if hasattr(translator, 'get_text') else "Napló részletei",
                                size=20,
                                weight=ft.FontWeight.W_600,
                                color=DesignSystem.TEXT_PRIMARY,
                            ),
                            ft.Text(
                                f"ID: {log.id}",
                                size=12,
                                color=DesignSystem.TEXT_SECONDARY,
                            ),
                        ], spacing=4, tight=True, expand=True),
                    ], spacing=DesignSystem.SPACING_3),
                    padding=ft.padding.all(DesignSystem.SPACING_4),
                ),
                ft.Divider(),
                
                # Basic info
                ft.Container(
                    content=ft.Column([
                        ft.Text(
                            translator.get_text("common.basic_info") if hasattr(translator, 'get_text') else "Alapadatok",
                            size=14,
                            weight=ft.FontWeight.W_600,
                            color=DesignSystem.TEXT_PRIMARY,
                        ),
                        ft.Row([
                            ft.Text(
                                translator.get_text("logs.details.entity") if hasattr(translator, 'get_text') else "Entitás:",
                                size=12,
                                color=DesignSystem.TEXT_SECONDARY,
                                width=120,
                            ),
                            ft.Text(
                                entity_display,
                                size=12,
                                color=DesignSystem.TEXT_PRIMARY,
                                expand=True,
                            ),
                        ]),
                        ft.Row([
                            ft.Text(
                                translator.get_text("logs.details.user") if hasattr(translator, 'get_text') else "Felhasználó:",
                                size=12,
                                color=DesignSystem.TEXT_SECONDARY,
                                width=120,
                            ),
                            ft.Text(
                                user_info,
                                size=12,
                                color=DesignSystem.TEXT_PRIMARY,
                                expand=True,
                            ),
                        ]),
                        ft.Row([
                            ft.Text(
                                translator.get_text("logs.details.timestamp") if hasattr(translator, 'get_text') else "Időpont:",
                                size=12,
                                color=DesignSystem.TEXT_SECONDARY,
                                width=120,
                            ),
                            ft.Text(
                                timestamp_str,
                                size=12,
                                color=DesignSystem.TEXT_PRIMARY,
                                expand=True,
                            ),
                        ]),
                        ft.Row([
                            ft.Text(
                                translator.get_text("logs.details.category") if hasattr(translator, 'get_text') else "Kategória:",
                                size=12,
                                color=DesignSystem.TEXT_SECONDARY,
                                width=120,
                            ),
                            create_vibrant_badge(
                                text=log.log_category.upper() if log.log_category else "UNKNOWN",
                                variant=self._get_category_variant(log.log_category),
                                size=11,
                            ),
                        ]),
                        ft.Row([
                            ft.Text(
                                translator.get_text("logs.details.action") if hasattr(translator, 'get_text') else "Művelet:",
                                size=12,
                                color=DesignSystem.TEXT_SECONDARY,
                                width=120,
                            ),
                            create_vibrant_badge(
                                text=log.action_type.upper() if log.action_type else "UNKNOWN",
                                variant=self._get_action_variant(log.action_type),
                                size=11,
                            ),
                        ]),
                    ], spacing=DesignSystem.SPACING_2, tight=True),
                    padding=ft.padding.all(DesignSystem.SPACING_3),
                    bgcolor=DesignSystem.BG_SECONDARY,
                    border_radius=DesignSystem.RADIUS_MD,
                ),
                
                # Description
                ft.Container(
                    content=ft.Column([
                        ft.Text(
                            translator.get_text("logs.details.description") if hasattr(translator, 'get_text') else "Leírás",
                            size=14,
                            weight=ft.FontWeight.W_600,
                            color=DesignSystem.TEXT_PRIMARY,
                        ),
                        ft.Text(
                            log.description or "-",
                            size=12,
                            color=DesignSystem.TEXT_PRIMARY,
                        ),
                    ], spacing=DesignSystem.SPACING_2, tight=True),
                    padding=ft.padding.all(DesignSystem.SPACING_3),
                    bgcolor=DesignSystem.GRAY_50,
                    border_radius=DesignSystem.RADIUS_MD,
                ),
                
                # Change reason (if available)
                ft.Container(
                    content=ft.Column([
                        ft.Text(
                            translator.get_text("common.change_reason") if hasattr(translator, 'get_text') else "Változtatás oka",
                            size=14,
                            weight=ft.FontWeight.W_600,
                            color=DesignSystem.TEXT_PRIMARY,
                        ),
                        ft.Text(
                            (log.log_metadata.get("change_reason") or log.log_metadata.get("change_description") or "-") if log.log_metadata and isinstance(log.log_metadata, dict) else "-",
                            size=12,
                            color=DesignSystem.TEXT_PRIMARY,
                        ),
                    ], spacing=DesignSystem.SPACING_2, tight=True),
                    padding=ft.padding.all(DesignSystem.SPACING_3),
                    bgcolor=DesignSystem.ORANGE_50,
                    border_radius=DesignSystem.RADIUS_MD,
                    visible=(log.log_metadata and isinstance(log.log_metadata, dict) and (log.log_metadata.get("change_reason") or log.log_metadata.get("change_description"))) if log.log_metadata else False,
                ),
                
                # User details
                ft.Container(
                    content=ft.Column([
                        ft.Text(
                            translator.get_text("logs.details.user_info") if hasattr(translator, 'get_text') else "Felhasználó információk",
                            size=14,
                            weight=ft.FontWeight.W_600,
                            color=DesignSystem.TEXT_PRIMARY,
                        ),
                        ft.Row([
                            ft.Text(
                                translator.get_text("logs.details.name") if hasattr(translator, 'get_text') else "Név:",
                                size=12,
                                color=DesignSystem.TEXT_SECONDARY,
                                width=120,
                            ),
                            ft.Text(
                                user_info,
                                size=12,
                                color=DesignSystem.TEXT_PRIMARY,
                                expand=True,
                            ),
                        ]),
                        ft.Row([
                            ft.Text(
                                translator.get_text("logs.details.username") if hasattr(translator, 'get_text') else "Felhasználónév:",
                                size=12,
                                color=DesignSystem.TEXT_SECONDARY,
                                width=120,
                            ),
                            ft.Text(
                                user_username,
                                size=12,
                                color=DesignSystem.TEXT_PRIMARY,
                                expand=True,
                            ),
                        ]),
                    ], spacing=DesignSystem.SPACING_2, tight=True),
                    padding=ft.padding.all(DesignSystem.SPACING_3),
                    bgcolor=DesignSystem.BLUE_50,
                    border_radius=DesignSystem.RADIUS_MD,
                ),
            ]
            
            # Add changes section if available - MUST be before metadata section
            if log.log_metadata and isinstance(log.log_metadata, dict) and "changes" in log.log_metadata:
                changes = log.log_metadata["changes"]
                if isinstance(changes, dict) and changes:
                    changes_items = []
                    
                    # Field name translations
                    field_translations = {
                        "name": "Név / Name",
                        "sku": "Cikkszám / SKU",
                        "serial_number": "Sorozatszám / Serial Number",
                        "model": "Modell / Model",
                        "manufacturer": "Gyártó / Manufacturer",
                        "category": "Kategória / Category",
                        "buy_price": "Vételár / Buy Price",
                        "sell_price": "Eladási ár / Sell Price",
                        "safety_stock": "Biztonsági készlet / Safety Stock",
                        "reorder_quantity": "Újrarendelési mennyiség / Reorder Quantity",
                        "description": "Leírás / Description",
                        "unit": "Mértékegység / Unit",
                        "bin_location": "Helyszín / Location",
                        "status": "Státusz / Status",
                        "operating_hours": "Üzemóra / Operating Hours",
                        "asset_tag": "Eszköz azonosító / Asset Tag",
                        "production_line_id": "Termelési sor / Production Line",
                        "maintenance_interval": "Karbantartási intervallum / Maintenance Interval",
                        "install_date": "Telepítés dátuma / Install Date",
                        "purchase_date": "Vásárlás dátuma / Purchase Date",
                        "purchase_price": "Vételár / Purchase Price",
                        "warranty_expiry_date": "Jótállás lejárat / Warranty Expiry",
                        "supplier": "Beszállító / Supplier",
                        "last_service_date": "Utolsó szerviz / Last Service",
                        "next_service_date": "Következő szerviz / Next Service",
                        "criticality_level": "Kritikussági szint / Criticality Level",
                        "energy_consumption": "Energiafogyasztás / Energy Consumption",
                        "power_requirements": "Teljesítmény igény / Power Requirements",
                        "operating_temperature_range": "Működési hőmérséklet / Operating Temperature",
                        "weight": "Súly / Weight",
                        "dimensions": "Méretek / Dimensions",
                        "notes": "Megjegyzések / Notes",
                        "compatible_machine_ids": "Kompatibilis gépek / Compatible Machines",
                        "operating_hours_update_frequency_type": "Üzemóra frissítési típus / Operating Hours Update Frequency Type",
                        "operating_hours_update_frequency_value": "Üzemóra frissítési érték / Operating Hours Update Frequency Value",
                    }
                    
                    for field, change_data in changes.items():
                        if isinstance(change_data, dict) and "old" in change_data and "new" in change_data:
                            old_val = change_data.get("old", "Nincs / None")
                            new_val = change_data.get("new", "Nincs / None")
                            
                            # Handle None values
                            if old_val == "None" or old_val is None:
                                old_val = "Nincs / None"
                            if new_val == "None" or new_val is None:
                                new_val = "Nincs / None"
                            
                            # Get translated field name
                            field_display = field_translations.get(field, field.replace("_", " ").title())
                            
                            changes_items.append(
                                ft.Container(
                                    content=ft.Column([
                                        ft.Text(
                                            field_display,
                                            size=12,
                                            weight=ft.FontWeight.W_600,
                                            color=DesignSystem.TEXT_PRIMARY,
                                        ),
                                        ft.Row([
                                            ft.Column([
                                                ft.Text(
                                                    translator.get_text("logs.details.old_value") if hasattr(translator, 'get_text') else "Régi érték:",
                                                    size=10,
                                                    color=DesignSystem.TEXT_SECONDARY,
                                                ),
                                                ft.Text(
                                                    str(old_val),
                                                    size=11,
                                                    color=DesignSystem.ERROR,
                                                    weight=ft.FontWeight.W_500,
                                                ),
                                            ], spacing=2, tight=True, expand=True),
                                            ft.Container(
                                                content=ft.Text(
                                                    "→",
                                                    size=20,
                                                    color=DesignSystem.TEXT_SECONDARY,
                                                    weight=ft.FontWeight.W_600,
                                                ),
                                                padding=ft.padding.symmetric(horizontal=DesignSystem.SPACING_2),
                                            ),
                                            ft.Column([
                                                ft.Text(
                                                    translator.get_text("logs.details.new_value") if hasattr(translator, 'get_text') else "Új érték:",
                                                    size=10,
                                                    color=DesignSystem.TEXT_SECONDARY,
                                                ),
                                                ft.Text(
                                                    str(new_val),
                                                    size=11,
                                                    color=DesignSystem.SUCCESS,
                                                    weight=ft.FontWeight.W_500,
                                                ),
                                            ], spacing=2, tight=True, expand=True),
                                        ], spacing=DesignSystem.SPACING_2),
                                    ], spacing=DesignSystem.SPACING_1, tight=True),
                                    padding=ft.padding.all(DesignSystem.SPACING_3),
                                    bgcolor=DesignSystem.GRAY_50,
                                    border_radius=DesignSystem.RADIUS_SM,
                                    border=ft.border.all(1, DesignSystem.GRAY_200),
                                )
                            )
                    
                    if changes_items:
                        dialog_content_items.append(
                            ft.Container(
                                content=ft.Column([
                                    ft.Text(
                                        translator.get_text("logs.details.changes") if hasattr(translator, 'get_text') else "Változtatások",
                                        size=16,
                                        weight=ft.FontWeight.W_600,
                                        color=DesignSystem.TEXT_PRIMARY,
                                    ),
                                    ft.Divider(),
                                    ft.Column(changes_items, spacing=DesignSystem.SPACING_2),
                                ], spacing=DesignSystem.SPACING_2, tight=True),
                                padding=ft.padding.all(DesignSystem.SPACING_4),
                                bgcolor=DesignSystem.ORANGE_50,
                                border_radius=DesignSystem.RADIUS_MD,
                                border=ft.border.all(2, DesignSystem.ORANGE_200),
                            )
                        )
            
            # Add metadata if available
            if formatted_metadata:
                dialog_content_items.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Text(
                                translator.get_text("logs.details.metadata") if hasattr(translator, 'get_text') else "Metaadatok",
                                size=14,
                                weight=ft.FontWeight.W_600,
                                color=DesignSystem.TEXT_PRIMARY,
                            ),
                            ft.Text(
                                formatted_metadata,
                                size=11,
                                color=DesignSystem.TEXT_PRIMARY,
                            ),
                        ], spacing=DesignSystem.SPACING_2, tight=True),
                        padding=ft.padding.all(DesignSystem.SPACING_3),
                        bgcolor=DesignSystem.PURPLE_50,
                        border_radius=DesignSystem.RADIUS_MD,
                    )
                )
            
            # Add raw metadata if available
            if log.log_metadata and isinstance(log.log_metadata, dict):
                import json
                raw_metadata_str = json.dumps(log.log_metadata, indent=2, ensure_ascii=False)
                dialog_content_items.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Text(
                                translator.get_text("logs.details.raw_metadata") if hasattr(translator, 'get_text') else "Nyers metaadatok",
                                size=14,
                                weight=ft.FontWeight.W_600,
                                color=DesignSystem.TEXT_PRIMARY,
                            ),
                            ft.Container(
                                content=ft.Text(
                                    raw_metadata_str,
                                    size=10,
                                    color=DesignSystem.TEXT_SECONDARY,
                                    font_family="monospace",
                                ),
                                padding=ft.padding.all(DesignSystem.SPACING_2),
                                bgcolor=DesignSystem.GRAY_100,
                                border_radius=DesignSystem.RADIUS_SM,
                            ),
                        ], spacing=DesignSystem.SPACING_2, tight=True),
                        padding=ft.padding.all(DesignSystem.SPACING_3),
                        bgcolor=DesignSystem.GRAY_50,
                        border_radius=DesignSystem.RADIUS_MD,
                    )
                )
            
            # Create dialog content column with dynamic sizing
            dialog_content_column = ft.Column(
                dialog_content_items, 
                spacing=DesignSystem.SPACING_3, 
                scroll=ft.ScrollMode.AUTO,
                tight=False,
            )
            
            # Wrap in container with dynamic sizing
            # Max height: 80% of page height, min height: auto, width: 80% of page width
            dialog_content = ft.Container(
                content=dialog_content_column,
                width=min(900, self.page.width * 0.85) if hasattr(self.page, 'width') and self.page.width else 900,
                height=min(700, self.page.height * 0.85) if hasattr(self.page, 'height') and self.page.height else 700,
                padding=ft.padding.all(0),
            )
            
            # Create dialog
            dialog = ft.AlertDialog(
                title=None,
                content=dialog_content,
                actions=[
                    ft.TextButton(
                        translator.get_text("common.buttons.close") if hasattr(translator, 'get_text') else "Bezárás",
                        on_click=lambda e: setattr(dialog, 'open', False) or self.page.update(),
                    ),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
                modal=True,
                shape=ft.RoundedRectangleBorder(radius=DesignSystem.RADIUS_LG),
            )
            
            # Open dialog
            self.page.dialog = dialog
            dialog.open = True
            self.page.update()
        except Exception as e:
            logger.error(f"Error opening log details dialog: {e}", exc_info=True)
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Hiba a részletek megnyitásakor: {e}"),
                bgcolor=DesignSystem.ERROR,
            )
            self.page.snack_bar.open = True
            self.page.update()
    
    def _on_year_change(self, year: Optional[str]):
        """Handle year filter change"""
        self.current_year = year
        self._load_logs()
    
    def _on_month_change(self, month: Optional[str]):
        """Handle month filter change"""
        self.current_month = month
        self._load_logs()
    
    def _on_category_change(self, category: Optional[str]):
        """Handle category filter change"""
        self.current_category = category if category else None
        self._load_logs()
    
    def _on_search_change(self, search_text: Optional[str]):
        """Handle search text change"""
        # TODO: Implement search functionality
        pass
    
    def _reset_filters(self, e):
        """Reset all filters"""
        self.current_category = None
        self.current_year = None
        self.current_month = None
        self.current_week = None
        self.current_day = None
        self._load_logs()
    
    def _format_metadata(self, metadata: dict, session: Session) -> str:
        """Format metadata dictionary into readable string, replacing IDs with actual names"""
        if not metadata:
            return "-"
        
        try:
            from database.models import Worksheet, PMHistory, PMTask, Part, Machine, User
            from sqlalchemy.orm import joinedload
            
            formatted_items = []
            
            # Special handling for changes dictionary - format it nicely
            if "changes" in metadata and isinstance(metadata["changes"], dict):
                changes = metadata["changes"]
                formatted_items.append(translator.get_text("logs.details.changes") if hasattr(translator, 'get_text') else "Változtatások:")
                formatted_items.append("")  # Empty line for spacing
                
                # Field name translations
                field_translations = {
                    "name": "Név / Name",
                    "sku": "Cikkszám / SKU",
                    "serial_number": "Sorozatszám / Serial Number",
                    "model": "Modell / Model",
                    "manufacturer": "Gyártó / Manufacturer",
                    "category": "Kategória / Category",
                    "buy_price": "Vételár / Buy Price",
                    "sell_price": "Eladási ár / Sell Price",
                    "safety_stock": "Biztonsági készlet / Safety Stock",
                    "reorder_quantity": "Újrarendelési mennyiség / Reorder Quantity",
                    "description": "Leírás / Description",
                    "unit": "Mértékegység / Unit",
                    "bin_location": "Helyszín / Location",
                    "status": "Státusz / Status",
                    "operating_hours": "Üzemóra / Operating Hours",
                    "asset_tag": "Eszköz azonosító / Asset Tag",
                    "production_line_id": "Termelési sor / Production Line",
                    "maintenance_interval": "Karbantartási intervallum / Maintenance Interval",
                    "install_date": "Telepítés dátuma / Install Date",
                    "purchase_date": "Vásárlás dátuma / Purchase Date",
                    "purchase_price": "Vételár / Purchase Price",
                    "warranty_expiry_date": "Jótállás lejárat / Warranty Expiry",
                    "supplier": "Beszállító / Supplier",
                    "last_service_date": "Utolsó szerviz / Last Service",
                    "next_service_date": "Következő szerviz / Next Service",
                    "criticality_level": "Kritikussági szint / Criticality Level",
                    "energy_consumption": "Energiafogyasztás / Energy Consumption",
                    "power_requirements": "Teljesítmény igény / Power Requirements",
                    "operating_temperature_range": "Működési hőmérséklet / Operating Temperature",
                    "weight": "Súly / Weight",
                    "dimensions": "Méretek / Dimensions",
                    "notes": "Megjegyzések / Notes",
                    "compatible_machine_ids": "Kompatibilis gépek / Compatible Machines",
                    "operating_hours_update_frequency_type": "Üzemóra frissítési típus / Operating Hours Update Frequency Type",
                    "operating_hours_update_frequency_value": "Üzemóra frissítési érték / Operating Hours Update Frequency Value",
                }
                
                for field, change_data in changes.items():
                    if isinstance(change_data, dict) and "old" in change_data and "new" in change_data:
                        old_val = change_data.get("old", "Nincs / None")
                        new_val = change_data.get("new", "Nincs / None")
                        
                        # Handle None values
                        if old_val == "None" or old_val is None:
                            old_val = "Nincs / None"
                        if new_val == "None" or new_val is None:
                            new_val = "Nincs / None"
                        
                        # Get translated field name
                        field_display = field_translations.get(field, field.replace("_", " ").title())
                        
                        # Format: Field Name: Old Value → New Value
                        formatted_items.append(f"{field_display}: {old_val} → {new_val}")
                    else:
                        field_display = field_translations.get(field, field.replace("_", " ").title())
                        formatted_items.append(f"{field_display}: {change_data}")
            
            for key, value in metadata.items():
                if value is None or key == "changes":
                    continue
                
                # Format worksheet_id
                if key == "worksheet_id" and value:
                    try:
                        worksheet = session.query(Worksheet).filter_by(id=value).first()
                        if worksheet:
                            formatted_items.append(f"Munkalap: {worksheet.title or f'Munkalap #{worksheet.id}'}")
                        else:
                            formatted_items.append(f"Munkalap ID: {value}")
                    except Exception as e:
                        logger.warning(f"Error loading worksheet {value}: {e}")
                        formatted_items.append(f"Munkalap ID: {value}")
                
                # Format pm_history_id
                elif key == "pm_history_id" and value:
                    try:
                        pm_history = session.query(PMHistory).options(
                            joinedload(PMHistory.pm_task)
                        ).filter_by(id=value).first()
                        if pm_history and pm_history.pm_task:
                            formatted_items.append(f"PM feladat: {pm_history.pm_task.task_name}")
                        else:
                            formatted_items.append(f"PM History ID: {value}")
                    except Exception as e:
                        logger.warning(f"Error loading PM history {value}: {e}")
                        formatted_items.append(f"PM History ID: {value}")
                
                # Format pm_task_id
                elif key == "pm_task_id" and value:
                    try:
                        pm_task = session.query(PMTask).filter_by(id=value).first()
                        if pm_task:
                            formatted_items.append(f"PM feladat: {pm_task.task_name}")
                        else:
                            formatted_items.append(f"PM Task ID: {value}")
                    except Exception as e:
                        logger.warning(f"Error loading PM task {value}: {e}")
                        formatted_items.append(f"PM Task ID: {value}")
                
                # Format entity_id with entity_type
                elif key == "entity_id" and value:
                    entity_type = metadata.get("entity_type", "")
                    try:
                        if entity_type == "Part":
                            part = session.query(Part).filter_by(id=value).first()
                            if part:
                                formatted_items.append(f"Alkatrész: {part.name} (SKU: {part.sku})")
                            else:
                                formatted_items.append(f"Alkatrész ID: {value}")
                        elif entity_type == "Machine":
                            machine = session.query(Machine).filter_by(id=value).first()
                            if machine:
                                formatted_items.append(f"Gép: {machine.name}")
                            else:
                                formatted_items.append(f"Gép ID: {value}")
                        else:
                            formatted_items.append(f"{entity_type} ID: {value}")
                    except Exception as e:
                        logger.warning(f"Error loading entity {entity_type} {value}: {e}")
                        formatted_items.append(f"{entity_type} ID: {value}")
                
                # Format machine_id
                elif key == "machine_id" and value:
                    try:
                        machine = session.query(Machine).filter_by(id=value).first()
                        if machine:
                            formatted_items.append(f"Gép: {machine.name}")
                        else:
                            formatted_items.append(f"Gép ID: {value}")
                    except Exception as e:
                        logger.warning(f"Error loading machine {value}: {e}")
                        formatted_items.append(f"Gép ID: {value}")
                
                # Format assigned_to_user_id
                elif key == "assigned_to_user_id" and value:
                    try:
                        user = session.query(User).filter_by(id=value).first()
                        if user:
                            formatted_items.append(f"Kiosztva: {user.full_name or user.username}")
                        else:
                            formatted_items.append(f"Felhasználó ID: {value}")
                    except Exception as e:
                        logger.warning(f"Error loading user {value}: {e}")
                        formatted_items.append(f"Felhasználó ID: {value}")
                
                # Format other fields
                elif key not in ["worksheet_id", "pm_history_id", "pm_task_id", "entity_id", "entity_type", "machine_id", "assigned_to_user_id"]:
                    # Translate common keys
                    key_translations = {
                        "reason": "Ok / Reason",
                        "task_name": "Feladat neve / Task Name",
                        "task_type": "Feladat típusa / Task Type",
                        "duration_minutes": "Időtartam (perc) / Duration (minutes)",
                        "location": "Helyszín / Location",
                        "change_description": "Változtatás leírása / Change Description",
                    }
                    display_key = key_translations.get(key, key.replace("_", " ").title())
                    formatted_items.append(f"{display_key}: {value}")
            
            return "\n".join(formatted_items) if formatted_items else "-"
        except Exception as e:
            logger.error(f"Error formatting metadata: {e}", exc_info=True)
            # Fallback to simple string representation
            return str(metadata)

