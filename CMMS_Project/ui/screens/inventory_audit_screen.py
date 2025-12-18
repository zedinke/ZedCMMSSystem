"""
Inventory Audit Screen - Készletellenőrzés/Leltás
"""

import flet as ft
# Compatibility for flet 0.23.2 - Icons are strings, not ft.Icons
if not hasattr(ft, 'Icons'):
    from utils.flet_icons import Icons
    ft.Icons = Icons
from datetime import datetime, timedelta
from typing import Optional
import threading

from localization.translator import translator
from services.inventory_audit_service import (
    get_inventory_overview,
    get_usage_report,
    get_value_change_report,
    get_stock_quantity_report,
    get_stock_change_report,
    get_machine_usage_trend,
    get_maintenance_trend_report,
    list_thresholds,
    create_threshold,
    update_threshold,
    delete_threshold,
)
from services.inventory_audit_excel_service import (
    export_inventory_overview_to_excel,
    export_usage_report_to_excel,
    export_value_change_report_to_excel,
    export_stock_quantity_report_to_excel,
    export_stock_change_report_to_excel,
    export_machine_usage_trend_to_excel,
    export_maintenance_trend_to_excel,
    export_full_inventory_to_excel,
)
from services import asset_service, inventory_service
from services.context_service import get_app_context
from services.log_service import get_logs
from pathlib import Path
import threading
from ui.components.modern_components import (
    create_modern_button,
    create_modern_card,
    create_vibrant_badge,
    create_empty_state_card,
    create_modern_text_field,
    create_modern_dropdown,
    create_modern_dialog,
    DesignSystem,
)
from ui.components.modern_card import (
    create_tailwind_card,
    create_metric_card,
)
from ui.components.modern_card import (
    create_tailwind_card,
    create_info_card,
    create_metric_card,
)
from utils.currency import format_price
import logging

logger = logging.getLogger(__name__)


class InventoryAuditScreen:
    def __init__(self):
        self.current_tab = 0  # 0=overview, 1=usage, 2=value_change, 3=stock_quantity, 4=stock_change, 5=machine_trend, 6=maintenance_trend, 7=thresholds
        self.current_period = "monthly"  # weekly, monthly, yearly
        self.start_date = None
        self.end_date = None
        self.filter_machine_id = None
        self.filter_part_id = None
        self.content_container = None
        self.page = None
    
    def view(self, page: ft.Page):
        """Main view for inventory audit screen"""
        self.page = page  # Store page reference
        
        # Create tabs
        tabs = ft.Tabs(
            selected_index=self.current_tab,
            on_change=lambda e: self._on_tab_change(e, page),
            tabs=[
                ft.Tab(
                    text=translator.get_text("inventory_audit.overview"),
                    icon=ft.Icons.DASHBOARD if hasattr(ft.Icons, 'DASHBOARD') else (ft.Icons.VIEW_DASHBOARD if hasattr(ft.Icons, 'VIEW_DASHBOARD') else ft.Icons.GRID_VIEW),
                ),
                ft.Tab(
                    text=translator.get_text("inventory_audit.usage_report"),
                    icon=ft.Icons.TRENDING_UP if hasattr(ft.Icons, 'TRENDING_UP') else (ft.Icons.ARROW_UPWARD if hasattr(ft.Icons, 'ARROW_UPWARD') else ft.Icons.ARROW_UP),
                ),
                ft.Tab(
                    text=translator.get_text("inventory_audit.value_change_report"),
                    icon=ft.Icons.ACCOUNT_BALANCE if hasattr(ft.Icons, 'ACCOUNT_BALANCE') else (ft.Icons.ACCOUNT_CIRCLE if hasattr(ft.Icons, 'ACCOUNT_CIRCLE') else ft.Icons.ATTACH_MONEY),
                ),
                ft.Tab(
                    text=translator.get_text("inventory_audit.stock_quantity_report"),
                    icon=ft.Icons.INVENTORY_2 if hasattr(ft.Icons, 'INVENTORY_2') else (ft.Icons.INVENTORY if hasattr(ft.Icons, 'INVENTORY') else ft.Icons.STORAGE),
                ),
                ft.Tab(
                    text=translator.get_text("inventory_audit.stock_change_report"),
                    icon=ft.Icons.CHANGE_CIRCLE if hasattr(ft.Icons, 'CHANGE_CIRCLE') else (ft.Icons.SYNC if hasattr(ft.Icons, 'SYNC') else ft.Icons.REFRESH),
                ),
                ft.Tab(
                    text=translator.get_text("inventory_audit.machine_usage_trend"),
                    icon=ft.Icons.TRENDING_UP if hasattr(ft.Icons, 'TRENDING_UP') else ft.Icons.ARROW_UPWARD,
                ),
                ft.Tab(
                    text=translator.get_text("inventory_audit.maintenance_trend"),
                    icon=ft.Icons.BUILD if hasattr(ft.Icons, 'BUILD') else (ft.Icons.CONSTRUCTION if hasattr(ft.Icons, 'CONSTRUCTION') else ft.Icons.SETTINGS),
                ),
                ft.Tab(
                    text=translator.get_text("inventory_audit.thresholds"),
                    icon=ft.Icons.WARNING if hasattr(ft.Icons, 'WARNING') else (ft.Icons.ALERT if hasattr(ft.Icons, 'ALERT') else ft.Icons.ERROR),
                ),
            ],
        )
        
        # Filter section
        filter_section = self._build_filter_section(page)
        
        # Content based on selected tab
        content = self._build_tab_content(page)
        
        # Store content container reference for dynamic updates
        self.content_container = ft.Container(
            content=content,
            expand=True,
            padding=ft.padding.all(DesignSystem.SPACING_4),
        )
        
        # Store main column reference for updates
        self.main_column = ft.Column([
            filter_section,
            tabs,
            self.content_container,
        ], expand=True, spacing=DesignSystem.SPACING_4)
        
        return self.main_column
    
    def _build_filter_section(self, page: ft.Page):
        """Build filter section with period selector and date range"""
        period_dropdown = ft.Dropdown(
            label=translator.get_text("inventory_audit.period"),
            options=[
                ft.dropdown.Option("weekly", translator.get_text("inventory_audit.weekly")),
                ft.dropdown.Option("monthly", translator.get_text("inventory_audit.monthly")),
                ft.dropdown.Option("yearly", translator.get_text("inventory_audit.yearly")),
            ],
            value=self.current_period,
            width=200,
            on_change=lambda e: self._on_period_change(e, page),
        )
        
        return ft.Container(
            content=ft.Row([
                period_dropdown,
                ft.VerticalDivider(),
                create_modern_button(
                    text=translator.get_text("inventory_audit.export_excel"),
                    icon=ft.Icons.DOWNLOAD if hasattr(ft.Icons, 'DOWNLOAD') else (ft.Icons.FILE_DOWNLOAD if hasattr(ft.Icons, 'FILE_DOWNLOAD') else ft.Icons.GET_APP),
                    on_click=lambda e: self._on_export_excel(e, page),
                    bgcolor=DesignSystem.SUCCESS,
                    color=DesignSystem.WHITE,
                ),
            ], spacing=DesignSystem.SPACING_4),
            padding=ft.padding.all(DesignSystem.SPACING_4),
            bgcolor=DesignSystem.BG_SECONDARY,
            border_radius=DesignSystem.RADIUS_LG,
        )
    
    def _build_tab_content(self, page: ft.Page):
        """Build content for current tab"""
        if self.current_tab == 0:
            return self._build_overview_tab(page)
        elif self.current_tab == 1:
            return self._build_usage_report_tab(page)
        elif self.current_tab == 2:
            return self._build_value_change_report_tab(page)
        elif self.current_tab == 3:
            return self._build_stock_quantity_report_tab(page)
        elif self.current_tab == 4:
            return self._build_stock_change_report_tab(page)
        elif self.current_tab == 5:
            return self._build_machine_usage_trend_tab(page)
        elif self.current_tab == 6:
            return self._build_maintenance_trend_tab(page)
        elif self.current_tab == 7:
            return self._build_thresholds_tab(page)
        else:
            return ft.Text("Unknown tab")
    
    def _build_overview_tab(self, page: ft.Page):
        """Build overview tab with key metrics"""
        try:
            overview_data = get_inventory_overview(
                period=self.current_period,
                start_date=self.start_date,
                end_date=self.end_date,
                machine_id=self.filter_machine_id,
            )
            
            metrics_row = ft.Row([
                create_metric_card(
                    value=format_price(overview_data.get("total_stock_value", 0.0)),
                    label=translator.get_text("inventory_audit.total_stock_value"),
                    icon=ft.Icons.ACCOUNT_BALANCE if hasattr(ft.Icons, 'ACCOUNT_BALANCE') else (ft.Icons.ACCOUNT_CIRCLE if hasattr(ft.Icons, 'ACCOUNT_CIRCLE') else ft.Icons.ATTACH_MONEY),
                    color=DesignSystem.EMERALD_500,
                ),
                create_metric_card(
                    value=f"{overview_data.get('total_stock_quantity', 0)} db",
                    label=translator.get_text("inventory_audit.total_stock_quantity"),
                    icon=ft.Icons.INVENTORY_2 if hasattr(ft.Icons, 'INVENTORY_2') else (ft.Icons.INVENTORY if hasattr(ft.Icons, 'INVENTORY') else ft.Icons.STORAGE),
                    color=DesignSystem.BLUE_500,
                ),
                create_metric_card(
                    value=f"{overview_data.get('active_parts', 0)} db",
                    label=translator.get_text("inventory_audit.active_parts"),
                    icon=ft.Icons.CHECK_CIRCLE if hasattr(ft.Icons, 'CHECK_CIRCLE') else ft.Icons.CHECK,
                    color=DesignSystem.EMERALD_500,
                ),
                create_metric_card(
                    value=f"{overview_data.get('low_stock_parts', 0)} db",
                    label=translator.get_text("inventory_audit.low_stock_parts"),
                    icon=ft.Icons.WARNING if hasattr(ft.Icons, 'WARNING') else (ft.Icons.ALERT if hasattr(ft.Icons, 'ALERT') else ft.Icons.ERROR),
                    color=DesignSystem.AMBER_500,
                ),
            ], spacing=DesignSystem.SPACING_4, wrap=True)
            
            # Additional details section
            details_cards = []
            
            # Top used parts
            if overview_data.get("top_used_parts"):
                top_used_items = []
                for part in overview_data.get("top_used_parts", [])[:5]:
                    top_used_items.append(
                        ft.Row([
                            ft.Text(f"• {part.get('name', '')} ({part.get('sku', '')})", size=12, expand=True),
                            ft.Text(f"{part.get('total_used', 0)} db", size=12, weight=ft.FontWeight.W_500),
                        ], spacing=DesignSystem.SPACING_2)
                    )
                if top_used_items:
                    details_cards.append(
                        create_tailwind_card(
                            content=ft.Column([
                                ft.Text("Legtöbbet felhasznált alkatrészek", size=14, weight=ft.FontWeight.W_600),
                                ft.Divider(height=1),
                            ] + top_used_items, spacing=DesignSystem.SPACING_2),
                            padding=DesignSystem.SPACING_4,
                        )
                    )
            
            # Period info
            period_info = create_tailwind_card(
                content=ft.Column([
                    ft.Text("Időszak információ", size=14, weight=ft.FontWeight.W_600),
                    ft.Divider(height=1),
                    ft.Text(f"Kezdés: {overview_data.get('period_start', '').strftime('%Y-%m-%d') if overview_data.get('period_start') else 'N/A'}", size=12),
                    ft.Text(f"Vég: {overview_data.get('period_end', '').strftime('%Y-%m-%d') if overview_data.get('period_end') else 'N/A'}", size=12),
                    ft.Text(f"Készlet változás: {overview_data.get('stock_change', 0):.2f} ({overview_data.get('stock_change_percent', 0.0):.2f}%)", size=12),
                ], spacing=DesignSystem.SPACING_2),
                padding=DesignSystem.SPACING_4,
            )
            details_cards.append(period_info)
            
            return ft.Column([
                metrics_row,
                ft.Divider(height=DesignSystem.SPACING_4),
                ft.Row([
                    create_tailwind_card(
                        content=ft.Column([
                            ft.Text("Készlet státusz", size=14, weight=ft.FontWeight.W_600),
                            ft.Divider(height=1),
                            ft.Text(f"Rendben: {overview_data.get('active_parts', 0) - overview_data.get('low_stock_parts', 0) - overview_data.get('out_of_stock_parts', 0)} db", size=12, color=DesignSystem.EMERALD_600),
                            ft.Text(f"Alacsony készlet: {overview_data.get('low_stock_parts', 0)} db", size=12, color=DesignSystem.AMBER_600),
                            ft.Text(f"Kifogyott: {overview_data.get('out_of_stock_parts', 0)} db", size=12, color=DesignSystem.RED_600),
                        ], spacing=DesignSystem.SPACING_2),
                        padding=DesignSystem.SPACING_4,
                    ),
                ] + details_cards, spacing=DesignSystem.SPACING_4, wrap=True),
            ], spacing=DesignSystem.SPACING_4, scroll=ft.ScrollMode.AUTO, expand=True)
        except Exception as e:
            logger.error(f"Error loading inventory overview: {e}", exc_info=True)
            return create_empty_state_card(
                icon=ft.Icons.ERROR if hasattr(ft.Icons, 'ERROR') else (ft.Icons.WARNING if hasattr(ft.Icons, 'WARNING') else ft.Icons.ALERT),
                title="Hiba",
                description=f"Az adatok betöltése során hiba történt: {str(e)}",
            )
    
    def _build_usage_report_tab(self, page: ft.Page):
        """Build usage report tab"""
        try:
            data = get_usage_report(
                period=self.current_period,
                start_date=self.start_date,
                end_date=self.end_date,
                machine_id=self.filter_machine_id,
                part_id=self.filter_part_id,
            )
            
            # Create cards for each usage item
            cards = []
            for item in data.get("usage_data", [])[:50]:  # Limit to 50 items for performance
                trend_badge_variant = {
                    "increasing": "red",
                    "decreasing": "green",
                    "stable": "blue",
                    "new": "purple",
                }.get(item.get("trend", "stable"), "blue")
                
                card = create_tailwind_card(
                    content=ft.Column([
                        ft.Row([
                            ft.Column([
                                ft.Text(item.get("part_name", ""), size=16, weight=ft.FontWeight.W_600),
                                ft.Text(f"SKU: {item.get('sku', '')}", size=12, color=DesignSystem.TEXT_SECONDARY),
                            ], spacing=DesignSystem.SPACING_1, expand=True),
                            create_vibrant_badge(
                                text=item.get("trend", ""),
                                variant=trend_badge_variant,
                                size=11,
                            ),
                        ], spacing=DesignSystem.SPACING_2),
                        ft.Divider(height=1),
                        ft.Row([
                            ft.Column([
                                ft.Text("Felhasznált mennyiség", size=11, color=DesignSystem.TEXT_SECONDARY),
                                ft.Text(f"{item.get('total_used', 0)} {item.get('unit', 'db')}", size=14, weight=ft.FontWeight.W_500),
                            ], spacing=DesignSystem.SPACING_1),
                            ft.Column([
                                ft.Text("Összes költség", size=11, color=DesignSystem.TEXT_SECONDARY),
                                ft.Text(format_price(item.get('total_cost', 0.0)), size=14, weight=ft.FontWeight.W_500),
                            ], spacing=DesignSystem.SPACING_1),
                        ], spacing=DesignSystem.SPACING_4),
                        ft.Row([
                            ft.Column([
                                ft.Text("Munkalapok száma", size=11, color=DesignSystem.TEXT_SECONDARY),
                                ft.Text(f"{item.get('worksheet_count', 0)} db", size=12),
                            ], spacing=DesignSystem.SPACING_1),
                            ft.Column([
                                ft.Text("Átlagos havi", size=11, color=DesignSystem.TEXT_SECONDARY),
                                ft.Text(f"{item.get('avg_monthly_usage', 0):.2f} {item.get('unit', 'db')}", size=12),
                            ], spacing=DesignSystem.SPACING_1),
                        ], spacing=DesignSystem.SPACING_4),
                        ft.Text(
                            f"Trend: {item.get('trend_percent', 0.0):.1f}%",
                            size=11,
                            color=DesignSystem.TEXT_SECONDARY,
                            italic=True,
                        ) if item.get('trend_percent') else None,
                    ], spacing=DesignSystem.SPACING_2),
                    padding=DesignSystem.SPACING_4,
                )
                cards.append(card)
            
            if not cards:
                return create_empty_state_card(
                    icon=ft.Icons.INFO_OUTLINE if hasattr(ft.Icons, 'INFO_OUTLINE') else (ft.Icons.INFO if hasattr(ft.Icons, 'INFO') else ft.Icons.HELP_OUTLINE),
                    title="Nincs adat",
                    description="Nincs felhasználási adat a kiválasztott időszakban.",
                )
            
            # Summary card
            summary_card = create_tailwind_card(
                content=ft.Column([
                    ft.Text("Összesítés", size=16, weight=ft.FontWeight.W_600),
                    ft.Divider(height=1),
                    ft.Row([
                        ft.Column([
                            ft.Text("Összes alkatrész", size=12, color=DesignSystem.TEXT_SECONDARY),
                            ft.Text(f"{data.get('total_parts_used', 0)} db", size=14, weight=ft.FontWeight.W_500),
                        ], spacing=DesignSystem.SPACING_1),
                        ft.Column([
                            ft.Text("Összes mennyiség", size=12, color=DesignSystem.TEXT_SECONDARY),
                            ft.Text(f"{data.get('total_quantity_used', 0):.2f}", size=14, weight=ft.FontWeight.W_500),
                        ], spacing=DesignSystem.SPACING_1),
                        ft.Column([
                            ft.Text("Összes költség", size=12, color=DesignSystem.TEXT_SECONDARY),
                            ft.Text(format_price(data.get('total_cost', 0.0)), size=14, weight=ft.FontWeight.W_500),
                        ], spacing=DesignSystem.SPACING_1),
                    ], spacing=DesignSystem.SPACING_4),
                    ft.Text(
                        f"Időszak: {data.get('period_start', '').strftime('%Y-%m-%d') if data.get('period_start') else 'N/A'} - {data.get('period_end', '').strftime('%Y-%m-%d') if data.get('period_end') else 'N/A'}",
                        size=11,
                        color=DesignSystem.TEXT_SECONDARY,
                    ),
                ], spacing=DesignSystem.SPACING_2),
                padding=DesignSystem.SPACING_4,
            )
            
            return ft.Column([
                ft.Row([
                    create_modern_button(
                        text=translator.get_text("inventory_audit.export_excel"),
                        icon=ft.Icons.DOWNLOAD if hasattr(ft.Icons, 'DOWNLOAD') else (ft.Icons.FILE_DOWNLOAD if hasattr(ft.Icons, 'FILE_DOWNLOAD') else ft.Icons.GET_APP),
                        on_click=lambda e: self._on_export_usage_excel(e, page),
                        bgcolor=DesignSystem.SUCCESS,
                        color=DesignSystem.WHITE,
                    ),
                ], spacing=DesignSystem.SPACING_2),
                summary_card,
                ft.GridView(
                    controls=cards,
                    runs_count=3,
                    max_extent=400,
                    spacing=DesignSystem.SPACING_4,
                    run_spacing=DesignSystem.SPACING_4,
                ),
            ], spacing=DesignSystem.SPACING_4, scroll=ft.ScrollMode.AUTO, expand=True)
        except Exception as e:
            logger.error(f"Error loading usage report: {e}", exc_info=True)
            return create_empty_state_card(
                icon=ft.Icons.ERROR if hasattr(ft.Icons, 'ERROR') else (ft.Icons.WARNING if hasattr(ft.Icons, 'WARNING') else ft.Icons.ALERT),
                title="Hiba",
                description=f"Az adatok betöltése során hiba történt: {str(e)}",
            )
    
    def _build_value_change_report_tab(self, page: ft.Page):
        """Build value change report tab"""
        try:
            data = get_value_change_report(
                period=self.current_period,
                start_date=self.start_date,
                end_date=self.end_date,
            )
            
            cards = []
            for part_data in data.get("parts", [])[:50]:
                value_change = part_data.get('value_change', 0.0)
                value_change_percent = part_data.get('value_change_percent', 0.0)
                change_color = DesignSystem.EMERALD_600 if value_change >= 0 else DesignSystem.RED_600
                
                card = create_tailwind_card(
                    content=ft.Column([
                        ft.Row([
                            ft.Column([
                                ft.Text(part_data.get("part_name", ""), size=16, weight=ft.FontWeight.W_600),
                                ft.Text(f"SKU: {part_data.get('sku', '')}", size=12, color=DesignSystem.TEXT_SECONDARY),
                            ], spacing=DesignSystem.SPACING_1, expand=True),
                        ], spacing=DesignSystem.SPACING_2),
                        ft.Divider(height=1),
                        ft.Row([
                            ft.Column([
                                ft.Text("Kezdeti érték", size=11, color=DesignSystem.TEXT_SECONDARY),
                                ft.Text(format_price(part_data.get('initial_value', 0.0)), size=14, weight=ft.FontWeight.W_500),
                            ], spacing=DesignSystem.SPACING_1),
                            ft.Column([
                                ft.Text("Végkészlet érték", size=11, color=DesignSystem.TEXT_SECONDARY),
                                ft.Text(format_price(part_data.get('final_value', 0.0)), size=14, weight=ft.FontWeight.W_500),
                            ], spacing=DesignSystem.SPACING_1),
                        ], spacing=DesignSystem.SPACING_4),
                        ft.Row([
                            ft.Column([
                                ft.Text("Beérkezett érték", size=11, color=DesignSystem.TEXT_SECONDARY),
                                ft.Text(format_price(part_data.get('received_value', 0.0)), size=12),
                            ], spacing=DesignSystem.SPACING_1),
                            ft.Column([
                                ft.Text("Kiadott érték", size=11, color=DesignSystem.TEXT_SECONDARY),
                                ft.Text(format_price(part_data.get('issued_value', 0.0)), size=12),
                            ], spacing=DesignSystem.SPACING_1),
                        ], spacing=DesignSystem.SPACING_4),
                        ft.Divider(height=1),
                        ft.Row([
                            ft.Column([
                                ft.Text("Értékváltozás", size=12, weight=ft.FontWeight.W_600),
                                ft.Text(
                                    f"{format_price(value_change)} ({value_change_percent:.2f}%)",
                                    size=14,
                                    weight=ft.FontWeight.W_600,
                                    color=change_color,
                                ),
                            ], spacing=DesignSystem.SPACING_1, expand=True),
                        ], spacing=DesignSystem.SPACING_2),
                        ft.Text(
                            f"Forgalom: {part_data.get('turnover_rate', 0.0):.2f}x",
                            size=11,
                            color=DesignSystem.TEXT_SECONDARY,
                            italic=True,
                        ) if part_data.get('turnover_rate') else None,
                    ], spacing=DesignSystem.SPACING_2),
                    padding=DesignSystem.SPACING_4,
                )
                cards.append(card)
            
            if not cards:
                return create_empty_state_card(
                    icon=ft.Icons.INFO_OUTLINE if hasattr(ft.Icons, 'INFO_OUTLINE') else (ft.Icons.INFO if hasattr(ft.Icons, 'INFO') else ft.Icons.HELP_OUTLINE),
                    title="Nincs adat",
                    description="Nincs értékváltozási adat a kiválasztott időszakban.",
                )
            
            return ft.Column([
                create_modern_button(
                    text=translator.get_text("inventory_audit.export_excel"),
                    icon=ft.Icons.DOWNLOAD if hasattr(ft.Icons, 'DOWNLOAD') else (ft.Icons.FILE_DOWNLOAD if hasattr(ft.Icons, 'FILE_DOWNLOAD') else ft.Icons.GET_APP),
                    on_click=lambda e: self._on_export_value_change_excel(e, page),
                    bgcolor=DesignSystem.SUCCESS,
                    color=DesignSystem.WHITE,
                ),
                ft.GridView(
                    controls=cards,
                    runs_count=3,
                    max_extent=400,
                    spacing=DesignSystem.SPACING_4,
                    run_spacing=DesignSystem.SPACING_4,
                ),
            ], spacing=DesignSystem.SPACING_4, scroll=ft.ScrollMode.AUTO, expand=True)
        except Exception as e:
            logger.error(f"Error loading value change report: {e}", exc_info=True)
            return create_empty_state_card(
                icon=ft.Icons.ERROR if hasattr(ft.Icons, 'ERROR') else (ft.Icons.WARNING if hasattr(ft.Icons, 'WARNING') else ft.Icons.ALERT),
                title="Hiba",
                description=f"Az adatok betöltése során hiba történt: {str(e)}",
            )
    
    def _build_stock_quantity_report_tab(self, page: ft.Page):
        """Build stock quantity report tab"""
        try:
            data = get_stock_quantity_report(
                machine_id=self.filter_machine_id,
                include_zero=False,
            )
            
            cards = []
            for part_data in data[:100]:  # Limit for performance
                status_badge_variant = {
                    "ok": "emerald",
                    "low_stock": "amber",
                    "out_of_stock": "red",
                }.get(part_data.get("status", "ok"), "blue")
                
                card = create_tailwind_card(
                    content=ft.Column([
                        ft.Row([
                            ft.Column([
                                ft.Text(part_data.get("part_name", ""), size=16, weight=ft.FontWeight.W_600),
                                ft.Text(f"SKU: {part_data.get('sku', '')}", size=12, color=DesignSystem.TEXT_SECONDARY),
                                ft.Text(f"Kategória: {part_data.get('category', 'Nincs')}", size=11, color=DesignSystem.TEXT_SECONDARY) if part_data.get('category') else None,
                            ], spacing=DesignSystem.SPACING_1, expand=True),
                            create_vibrant_badge(
                                text=part_data.get("status", ""),
                                variant=status_badge_variant,
                                size=11,
                            ),
                        ], spacing=DesignSystem.SPACING_2),
                        ft.Divider(height=1),
                        ft.Row([
                            ft.Column([
                                ft.Text("Jelenlegi készlet", size=11, color=DesignSystem.TEXT_SECONDARY),
                                ft.Text(f"{part_data.get('current_quantity', 0)} {part_data.get('unit', 'db')}", size=14, weight=ft.FontWeight.W_500),
                            ], spacing=DesignSystem.SPACING_1),
                            ft.Column([
                                ft.Text("Készlet érték", size=11, color=DesignSystem.TEXT_SECONDARY),
                                ft.Text(format_price(part_data.get('stock_value', 0.0)), size=14, weight=ft.FontWeight.W_500),
                            ], spacing=DesignSystem.SPACING_1),
                        ], spacing=DesignSystem.SPACING_4),
                        ft.Row([
                            ft.Column([
                                ft.Text("Biztonsági készlet", size=11, color=DesignSystem.TEXT_SECONDARY),
                                ft.Text(f"{part_data.get('safety_stock', 0)} {part_data.get('unit', 'db')}", size=12),
                            ], spacing=DesignSystem.SPACING_1),
                            ft.Column([
                                ft.Text("Újrarendelési mennyiség", size=11, color=DesignSystem.TEXT_SECONDARY),
                                ft.Text(f"{part_data.get('reorder_quantity', 0)} {part_data.get('unit', 'db')}", size=12),
                            ], spacing=DesignSystem.SPACING_1),
                        ], spacing=DesignSystem.SPACING_4),
                        ft.Divider(height=1),
                        ft.Row([
                            ft.Column([
                                ft.Text("Beszállító", size=11, color=DesignSystem.TEXT_SECONDARY),
                                ft.Text(part_data.get('supplier_name', 'Nincs') or 'Nincs', size=12),
                            ], spacing=DesignSystem.SPACING_1),
                            ft.Column([
                                ft.Text("Egységár (FIFO)", size=11, color=DesignSystem.TEXT_SECONDARY),
                                ft.Text(format_price(part_data.get('fifo_unit_cost', 0.0)), size=12),
                            ], spacing=DesignSystem.SPACING_1),
                        ], spacing=DesignSystem.SPACING_4),
                        ft.Row([
                            ft.Text(
                                f"Utolsó beérkezés: {part_data.get('last_receipt_date', '').strftime('%Y-%m-%d') if part_data.get('last_receipt_date') else 'Nincs'}",
                                size=11,
                                color=DesignSystem.TEXT_SECONDARY,
                            ),
                            ft.Text(
                                f"Utolsó kiadás: {part_data.get('last_issue_date', '').strftime('%Y-%m-%d') if part_data.get('last_issue_date') else 'Nincs'}",
                                size=11,
                                color=DesignSystem.TEXT_SECONDARY,
                            ),
                        ], spacing=DesignSystem.SPACING_4, wrap=True),
                    ], spacing=DesignSystem.SPACING_2),
                    padding=DesignSystem.SPACING_4,
                )
                cards.append(card)
            
            if not cards:
                return create_empty_state_card(
                    icon=ft.Icons.INFO_OUTLINE if hasattr(ft.Icons, 'INFO_OUTLINE') else (ft.Icons.INFO if hasattr(ft.Icons, 'INFO') else ft.Icons.HELP_OUTLINE),
                    title="Nincs adat",
                    description="Nincs készlet adat.",
                )
            
            return ft.Column([
                create_modern_button(
                    text=translator.get_text("inventory_audit.export_excel"),
                    icon=ft.Icons.DOWNLOAD if hasattr(ft.Icons, 'DOWNLOAD') else (ft.Icons.FILE_DOWNLOAD if hasattr(ft.Icons, 'FILE_DOWNLOAD') else ft.Icons.GET_APP),
                    on_click=lambda e: self._on_export_stock_quantity_excel(e, page),
                    bgcolor=DesignSystem.SUCCESS,
                    color=DesignSystem.WHITE,
                ),
                ft.GridView(
                    controls=cards,
                    runs_count=3,
                    max_extent=400,
                    spacing=DesignSystem.SPACING_4,
                    run_spacing=DesignSystem.SPACING_4,
                ),
            ], spacing=DesignSystem.SPACING_4, scroll=ft.ScrollMode.AUTO, expand=True)
        except Exception as e:
            logger.error(f"Error loading stock quantity report: {e}", exc_info=True)
            return create_empty_state_card(
                icon=ft.Icons.ERROR if hasattr(ft.Icons, 'ERROR') else (ft.Icons.WARNING if hasattr(ft.Icons, 'WARNING') else ft.Icons.ALERT),
                title="Hiba",
                description=f"Az adatok betöltése során hiba történt: {str(e)}",
            )
    
    def _build_stock_change_report_tab(self, page: ft.Page):
        """Build stock change report tab"""
        try:
            data = get_stock_change_report(
                period=self.current_period,
                start_date=self.start_date,
                end_date=self.end_date,
                part_id=self.filter_part_id,
            )
            
            cards = []
            for part_data in data.get("parts", [])[:50]:
                qty_change = part_data.get('quantity_change', 0)
                qty_change_percent = part_data.get('quantity_change_percent', 0.0)
                change_color = DesignSystem.EMERALD_600 if qty_change >= 0 else DesignSystem.RED_600
                
                card = create_tailwind_card(
                    content=ft.Column([
                        ft.Row([
                            ft.Column([
                                ft.Text(part_data.get("part_name", ""), size=16, weight=ft.FontWeight.W_600),
                                ft.Text(f"SKU: {part_data.get('sku', '')}", size=12, color=DesignSystem.TEXT_SECONDARY),
                            ], spacing=DesignSystem.SPACING_1, expand=True),
                        ], spacing=DesignSystem.SPACING_2),
                        ft.Divider(height=1),
                        ft.Row([
                            ft.Column([
                                ft.Text("Kezdeti mennyiség", size=11, color=DesignSystem.TEXT_SECONDARY),
                                ft.Text(f"{part_data.get('initial_quantity', 0)}", size=14, weight=ft.FontWeight.W_500),
                            ], spacing=DesignSystem.SPACING_1),
                            ft.Column([
                                ft.Text("Végkészlet mennyiség", size=11, color=DesignSystem.TEXT_SECONDARY),
                                ft.Text(f"{part_data.get('final_quantity', 0)}", size=14, weight=ft.FontWeight.W_500),
                            ], spacing=DesignSystem.SPACING_1),
                        ], spacing=DesignSystem.SPACING_4),
                        ft.Row([
                            ft.Column([
                                ft.Text("Beérkezett", size=11, color=DesignSystem.TEXT_SECONDARY),
                                ft.Text(f"{part_data.get('received_quantity', 0)}", size=12, color=DesignSystem.EMERALD_600),
                            ], spacing=DesignSystem.SPACING_1),
                            ft.Column([
                                ft.Text("Kiadott", size=11, color=DesignSystem.TEXT_SECONDARY),
                                ft.Text(f"{part_data.get('issued_quantity', 0)}", size=12, color=DesignSystem.RED_600),
                            ], spacing=DesignSystem.SPACING_1),
                        ], spacing=DesignSystem.SPACING_4),
                        ft.Divider(height=1),
                        ft.Row([
                            ft.Column([
                                ft.Text("Mennyiség változás", size=12, weight=ft.FontWeight.W_600),
                                ft.Text(
                                    f"{qty_change} ({qty_change_percent:.2f}%)",
                                    size=14,
                                    weight=ft.FontWeight.W_600,
                                    color=change_color,
                                ),
                            ], spacing=DesignSystem.SPACING_1, expand=True),
                        ], spacing=DesignSystem.SPACING_2),
                        ft.Row([
                            ft.Text(
                                f"Átlagos készlet: {part_data.get('avg_quantity', 0):.2f}",
                                size=11,
                                color=DesignSystem.TEXT_SECONDARY,
                            ),
                            ft.Text(
                                f"Forgalom napok: {part_data.get('turnover_days', 0):.1f}",
                                size=11,
                                color=DesignSystem.TEXT_SECONDARY,
                            ),
                        ], spacing=DesignSystem.SPACING_4, wrap=True),
                    ], spacing=DesignSystem.SPACING_2),
                    padding=DesignSystem.SPACING_4,
                )
                cards.append(card)
            
            if not cards:
                return create_empty_state_card(
                    icon=ft.Icons.INFO_OUTLINE if hasattr(ft.Icons, 'INFO_OUTLINE') else (ft.Icons.INFO if hasattr(ft.Icons, 'INFO') else ft.Icons.HELP_OUTLINE),
                    title="Nincs adat",
                    description="Nincs készlet változási adat a kiválasztott időszakban.",
                )
            
            # Summary card
            summary = data.get("summary", {})
            summary_card = create_tailwind_card(
                content=ft.Column([
                    ft.Text("Összesítés", size=16, weight=ft.FontWeight.W_600),
                    ft.Divider(height=1),
                    ft.Row([
                        ft.Column([
                            ft.Text("Összes kezdeti", size=12, color=DesignSystem.TEXT_SECONDARY),
                            ft.Text(f"{summary.get('total_initial_quantity', 0)}", size=14, weight=ft.FontWeight.W_500),
                        ], spacing=DesignSystem.SPACING_1),
                        ft.Column([
                            ft.Text("Összes végkészlet", size=12, color=DesignSystem.TEXT_SECONDARY),
                            ft.Text(f"{summary.get('total_final_quantity', 0)}", size=14, weight=ft.FontWeight.W_500),
                        ], spacing=DesignSystem.SPACING_1),
                        ft.Column([
                            ft.Text("Összes beérkezett", size=12, color=DesignSystem.TEXT_SECONDARY),
                            ft.Text(f"{summary.get('total_received', 0)}", size=14, weight=ft.FontWeight.W_500, color=DesignSystem.EMERALD_600),
                        ], spacing=DesignSystem.SPACING_1),
                        ft.Column([
                            ft.Text("Összes kiadott", size=12, color=DesignSystem.TEXT_SECONDARY),
                            ft.Text(f"{summary.get('total_issued', 0)}", size=14, weight=ft.FontWeight.W_500, color=DesignSystem.RED_600),
                        ], spacing=DesignSystem.SPACING_1),
                    ], spacing=DesignSystem.SPACING_4),
                    ft.Text(
                        f"Időszak: {data.get('period_start', '').strftime('%Y-%m-%d') if data.get('period_start') else 'N/A'} - {data.get('period_end', '').strftime('%Y-%m-%d') if data.get('period_end') else 'N/A'}",
                        size=11,
                        color=DesignSystem.TEXT_SECONDARY,
                    ),
                ], spacing=DesignSystem.SPACING_2),
                padding=DesignSystem.SPACING_4,
            )
            
            return ft.Column([
                ft.Row([
                    create_modern_button(
                        text=translator.get_text("inventory_audit.export_excel"),
                        icon=ft.Icons.DOWNLOAD if hasattr(ft.Icons, 'DOWNLOAD') else (ft.Icons.FILE_DOWNLOAD if hasattr(ft.Icons, 'FILE_DOWNLOAD') else ft.Icons.GET_APP),
                        on_click=lambda e: self._on_export_stock_change_excel(e, page),
                        bgcolor=DesignSystem.SUCCESS,
                        color=DesignSystem.WHITE,
                    ),
                ], spacing=DesignSystem.SPACING_2),
                summary_card,
                ft.GridView(
                    controls=cards,
                    runs_count=3,
                    max_extent=400,
                    spacing=DesignSystem.SPACING_4,
                    run_spacing=DesignSystem.SPACING_4,
                ),
            ], spacing=DesignSystem.SPACING_4, scroll=ft.ScrollMode.AUTO, expand=True)
        except Exception as e:
            logger.error(f"Error loading stock change report: {e}", exc_info=True)
            return create_empty_state_card(
                icon=ft.Icons.ERROR if hasattr(ft.Icons, 'ERROR') else (ft.Icons.WARNING if hasattr(ft.Icons, 'WARNING') else ft.Icons.ALERT),
                title="Hiba",
                description=f"Az adatok betöltése során hiba történt: {str(e)}",
            )
    
    def _build_machine_usage_trend_tab(self, page: ft.Page):
        """Build machine usage trend tab"""
        # Machine selector needed
        machines = asset_service.list_machines()
        if not machines:
            return create_empty_state_card(
                icon=ft.Icons.INFO_OUTLINE if hasattr(ft.Icons, 'INFO_OUTLINE') else (ft.Icons.INFO if hasattr(ft.Icons, 'INFO') else ft.Icons.HELP_OUTLINE),
                title="Nincs eszköz",
                description="Nincs elérhető eszköz a trend elemzéshez.",
            )
        
        machine_options = [ft.dropdown.Option(str(m.id), m.name) for m in machines]
        # Use filter_machine_id if set, otherwise default to first machine
        default_machine_id = self.filter_machine_id if self.filter_machine_id else (machines[0].id if machines else None)
        machine_dropdown = ft.Dropdown(
            label="Eszköz",
            options=machine_options,
            value=str(default_machine_id) if default_machine_id else None,
            width=300,
            on_change=lambda e: self._on_machine_select(e, page),
        )
        
        selected_machine_id = self.filter_machine_id if self.filter_machine_id else (int(machine_dropdown.value) if machine_dropdown.value else None)
        
        try:
            if selected_machine_id:
                data = get_machine_usage_trend(
                    machine_id=selected_machine_id,
                    period=self.current_period,
                    breakdown="monthly" if self.current_period == "yearly" else self.current_period,
                )
                
                cards = []
                for breakdown_item in data.get("breakdown_data", []):
                    card = create_tailwind_card(
                        content=ft.Column([
                            ft.Text(breakdown_item.get("period", ""), size=16, weight=ft.FontWeight.W_600),
                            ft.Divider(height=1),
                            ft.Row([
                                ft.Column([
                                    ft.Text("Felhasznált mennyiség", size=11, color=DesignSystem.TEXT_SECONDARY),
                                    ft.Text(f"{breakdown_item.get('quantity_used', 0):.2f}", size=14, weight=ft.FontWeight.W_500),
                                ], spacing=DesignSystem.SPACING_1),
                                ft.Column([
                                    ft.Text("Költség", size=11, color=DesignSystem.TEXT_SECONDARY),
                                    ft.Text(format_price(breakdown_item.get('cost', 0.0)), size=14, weight=ft.FontWeight.W_500),
                                ], spacing=DesignSystem.SPACING_1),
                            ], spacing=DesignSystem.SPACING_4),
                            ft.Row([
                                ft.Column([
                                    ft.Text("Munkalapok száma", size=11, color=DesignSystem.TEXT_SECONDARY),
                                    ft.Text(f"{breakdown_item.get('worksheet_count', 0)} db", size=12),
                                ], spacing=DesignSystem.SPACING_1),
                            ], spacing=DesignSystem.SPACING_4),
                        ], spacing=DesignSystem.SPACING_2),
                        padding=DesignSystem.SPACING_4,
                    )
                    cards.append(card)
                
                # Summary card
                summary_card = create_tailwind_card(
                    content=ft.Column([
                        ft.Text(f"Összesítés - {data.get('machine_name', '')}", size=16, weight=ft.FontWeight.W_600),
                        ft.Text(f"Gyártási szám: {data.get('serial_number', 'Nincs')}", size=12, color=DesignSystem.TEXT_SECONDARY),
                        ft.Divider(height=1),
                        ft.Row([
                            ft.Column([
                                ft.Text("Összes munkalap", size=12, color=DesignSystem.TEXT_SECONDARY),
                                ft.Text(f"{data.get('total_worksheets', 0)} db", size=14, weight=ft.FontWeight.W_500),
                            ], spacing=DesignSystem.SPACING_1),
                            ft.Column([
                                ft.Text("Felhasznált alkatrészek", size=12, color=DesignSystem.TEXT_SECONDARY),
                                ft.Text(f"{data.get('total_parts_used', 0)} db", size=14, weight=ft.FontWeight.W_500),
                            ], spacing=DesignSystem.SPACING_1),
                        ], spacing=DesignSystem.SPACING_4),
                        ft.Text(
                            f"Trend: {data.get('trend', '')} ({data.get('trend_percent', 0.0):.1f}%)",
                            size=12,
                            color=DesignSystem.TEXT_SECONDARY,
                        ) if data.get('trend') else None,
                    ], spacing=DesignSystem.SPACING_2),
                    padding=DesignSystem.SPACING_4,
                )
                
                return ft.Column([
                    machine_dropdown,
                    ft.Row([
                        create_modern_button(
                            text=translator.get_text("inventory_audit.export_excel"),
                            icon=ft.Icons.DOWNLOAD if hasattr(ft.Icons, 'DOWNLOAD') else (ft.Icons.FILE_DOWNLOAD if hasattr(ft.Icons, 'FILE_DOWNLOAD') else ft.Icons.GET_APP),
                            on_click=lambda e: self._on_export_machine_trend_excel(e, page, selected_machine_id),
                            bgcolor=DesignSystem.SUCCESS,
                            color=DesignSystem.WHITE,
                        ),
                    ], spacing=DesignSystem.SPACING_2),
                    summary_card,
                    ft.GridView(
                        controls=cards,
                        runs_count=3,
                        max_extent=400,
                        spacing=DesignSystem.SPACING_4,
                        run_spacing=DesignSystem.SPACING_4,
                    ),
                ], spacing=DesignSystem.SPACING_4, scroll=ft.ScrollMode.AUTO, expand=True)
            else:
                return ft.Column([machine_dropdown], spacing=DesignSystem.SPACING_4)
        except Exception as e:
            logger.error(f"Error loading machine usage trend: {e}", exc_info=True)
            return ft.Column([
                machine_dropdown,
                create_empty_state_card(
                    icon=ft.Icons.ERROR if hasattr(ft.Icons, 'ERROR') else (ft.Icons.WARNING if hasattr(ft.Icons, 'WARNING') else ft.Icons.ALERT),
                    title="Hiba",
                    description=f"Az adatok betöltése során hiba történt: {str(e)}",
                ),
            ], spacing=DesignSystem.SPACING_4)
    
    def _build_maintenance_trend_tab(self, page: ft.Page):
        """Build maintenance trend tab"""
        try:
            data = get_maintenance_trend_report(
                machine_id=self.filter_machine_id,
                period=self.current_period,
                breakdown="monthly" if self.current_period == "yearly" else self.current_period,
            )
            
            cards = []
            for breakdown_item in data.get("breakdown_data", []):
                card = create_tailwind_card(
                    content=ft.Column([
                        ft.Text(breakdown_item.get("period", ""), size=16, weight=ft.FontWeight.W_600),
                        ft.Divider(height=1),
                        ft.Row([
                            ft.Column([
                                ft.Text("Összes karbantartás", size=11, color=DesignSystem.TEXT_SECONDARY),
                                ft.Text(f"{breakdown_item.get('maintenance_count', 0)} db", size=14, weight=ft.FontWeight.W_500),
                            ], spacing=DesignSystem.SPACING_1),
                            ft.Column([
                                ft.Text("Preventív", size=11, color=DesignSystem.TEXT_SECONDARY),
                                ft.Text(f"{breakdown_item.get('preventive_count', 0)} db", size=12, color=DesignSystem.EMERALD_600),
                            ], spacing=DesignSystem.SPACING_1),
                            ft.Column([
                                ft.Text("Korrekciós", size=11, color=DesignSystem.TEXT_SECONDARY),
                                ft.Text(f"{breakdown_item.get('corrective_count', 0)} db", size=12, color=DesignSystem.RED_600),
                            ], spacing=DesignSystem.SPACING_1),
                        ], spacing=DesignSystem.SPACING_4),
                        ft.Divider(height=1),
                        ft.Row([
                            ft.Column([
                                ft.Text("Költség", size=11, color=DesignSystem.TEXT_SECONDARY),
                                ft.Text(format_price(breakdown_item.get('maintenance_cost', 0.0)), size=14, weight=ft.FontWeight.W_500),
                            ], spacing=DesignSystem.SPACING_1),
                            ft.Column([
                                ft.Text("Leállási idő", size=11, color=DesignSystem.TEXT_SECONDARY),
                                ft.Text(f"{breakdown_item.get('downtime_hours', 0.0):.2f} óra", size=12),
                            ], spacing=DesignSystem.SPACING_1),
                        ], spacing=DesignSystem.SPACING_4),
                    ], spacing=DesignSystem.SPACING_2),
                    padding=DesignSystem.SPACING_4,
                )
                cards.append(card)
            
            summary = data.get("summary", {})
            summary_card = create_tailwind_card(
                content=ft.Column([
                    ft.Text("Összesítő metrikák", size=16, weight=ft.FontWeight.W_600),
                    ft.Divider(height=1),
                    ft.Row([
                        ft.Column([
                            ft.Text("Összes karbantartás", size=12, color=DesignSystem.TEXT_SECONDARY),
                            ft.Text(f"{summary.get('total_maintenances', 0)} db", size=14, weight=ft.FontWeight.W_500),
                        ], spacing=DesignSystem.SPACING_1),
                        ft.Column([
                            ft.Text("Preventív", size=12, color=DesignSystem.TEXT_SECONDARY),
                            ft.Text(f"{summary.get('preventive_count', 0)} db", size=14, weight=ft.FontWeight.W_500, color=DesignSystem.EMERALD_600),
                        ], spacing=DesignSystem.SPACING_1),
                        ft.Column([
                            ft.Text("Korrekciós", size=12, color=DesignSystem.TEXT_SECONDARY),
                            ft.Text(f"{summary.get('corrective_count', 0)} db", size=14, weight=ft.FontWeight.W_500, color=DesignSystem.RED_600),
                        ], spacing=DesignSystem.SPACING_1),
                    ], spacing=DesignSystem.SPACING_4),
                    ft.Divider(height=1),
                    ft.Row([
                        ft.Column([
                            ft.Text("MTBF", size=12, color=DesignSystem.TEXT_SECONDARY),
                            ft.Text(f"{summary.get('mtbf_hours', 0.0):.2f} óra", size=14, weight=ft.FontWeight.W_500),
                            ft.Text("(Átlagos hibák közötti idő)", size=10, color=DesignSystem.TEXT_SECONDARY, italic=True),
                        ], spacing=DesignSystem.SPACING_1),
                        ft.Column([
                            ft.Text("MTTR", size=12, color=DesignSystem.TEXT_SECONDARY),
                            ft.Text(f"{summary.get('mttr_hours', 0.0):.2f} óra", size=14, weight=ft.FontWeight.W_500),
                            ft.Text("(Átlagos javítási idő)", size=10, color=DesignSystem.TEXT_SECONDARY, italic=True),
                        ], spacing=DesignSystem.SPACING_1),
                        ft.Column([
                            ft.Text("Rendelkezésre állás", size=12, color=DesignSystem.TEXT_SECONDARY),
                            ft.Text(f"{summary.get('availability_percent', 0.0):.2f}%", size=14, weight=ft.FontWeight.W_500, color=DesignSystem.EMERALD_600),
                        ], spacing=DesignSystem.SPACING_1),
                    ], spacing=DesignSystem.SPACING_4),
                    ft.Divider(height=1),
                    ft.Row([
                        ft.Column([
                            ft.Text("Összes költség", size=12, color=DesignSystem.TEXT_SECONDARY),
                            ft.Text(format_price(summary.get('total_cost', 0.0)), size=14, weight=ft.FontWeight.W_500),
                        ], spacing=DesignSystem.SPACING_1),
                        ft.Column([
                            ft.Text("Preventív költség", size=12, color=DesignSystem.TEXT_SECONDARY),
                            ft.Text(format_price(summary.get('preventive_cost', 0.0)), size=12, color=DesignSystem.EMERALD_600),
                        ], spacing=DesignSystem.SPACING_1),
                        ft.Column([
                            ft.Text("Korrekciós költség", size=12, color=DesignSystem.TEXT_SECONDARY),
                            ft.Text(format_price(summary.get('corrective_cost', 0.0)), size=12, color=DesignSystem.RED_600),
                        ], spacing=DesignSystem.SPACING_1),
                        ft.Column([
                            ft.Text("Összes leállási idő", size=12, color=DesignSystem.TEXT_SECONDARY),
                            ft.Text(f"{summary.get('total_downtime_hours', 0.0):.2f} óra", size=12),
                        ], spacing=DesignSystem.SPACING_1),
                    ], spacing=DesignSystem.SPACING_4),
                ], spacing=DesignSystem.SPACING_2),
                padding=DesignSystem.SPACING_4,
            )
            
            if not cards:
                return create_empty_state_card(
                    icon=ft.Icons.INFO_OUTLINE if hasattr(ft.Icons, 'INFO_OUTLINE') else (ft.Icons.INFO if hasattr(ft.Icons, 'INFO') else ft.Icons.HELP_OUTLINE),
                    title="Nincs adat",
                    description="Nincs karbantartási adat a kiválasztott időszakban.",
                )
            
            return ft.Column([
                create_modern_button(
                    text=translator.get_text("inventory_audit.export_excel"),
                    icon=ft.Icons.DOWNLOAD if hasattr(ft.Icons, 'DOWNLOAD') else (ft.Icons.FILE_DOWNLOAD if hasattr(ft.Icons, 'FILE_DOWNLOAD') else ft.Icons.GET_APP),
                    on_click=lambda e: self._on_export_maintenance_trend_excel(e, page),
                    bgcolor=DesignSystem.SUCCESS,
                    color=DesignSystem.WHITE,
                ),
                summary_card,
                ft.GridView(
                    controls=cards,
                    runs_count=3,
                    max_extent=400,
                    spacing=DesignSystem.SPACING_4,
                    run_spacing=DesignSystem.SPACING_4,
                ),
            ], spacing=DesignSystem.SPACING_4, scroll=ft.ScrollMode.AUTO, expand=True)
        except Exception as e:
            logger.error(f"Error loading maintenance trend: {e}", exc_info=True)
            return create_empty_state_card(
                icon=ft.Icons.ERROR if hasattr(ft.Icons, 'ERROR') else (ft.Icons.WARNING if hasattr(ft.Icons, 'WARNING') else ft.Icons.ALERT),
                title="Hiba",
                description=f"Az adatok betöltése során hiba történt: {str(e)}",
            )
    
    def _build_thresholds_tab(self, page: ft.Page):
        """Build thresholds tab"""
        try:
            thresholds = list_thresholds(is_active=None)  # Get all thresholds
            
            cards = []
            for threshold in thresholds:
                # Get part name
                try:
                    part = inventory_service.get_part(threshold.part_id)
                    part_name = part.name if part else f"ID: {threshold.part_id}"
                    part_sku = part.sku if part else None
                    part_category = part.category if part else None
                except:
                    part_name = f"ID: {threshold.part_id}"
                    part_sku = None
                    part_category = None
                
                # Get machine name if applicable
                machine_name = None
                machine_serial = None
                if threshold.machine_id:
                    try:
                        machine = asset_service.get_machine(threshold.machine_id)
                        machine_name = machine.name if machine else None
                        machine_serial = machine.serial_number if machine else None
                    except:
                        pass
                
                # Get audit trail (logs) for this threshold
                audit_logs = []
                try:
                    logs = get_logs(
                        entity_type="InventoryThreshold",
                        entity_id=threshold.id,
                        limit=5
                    )
                    for log in logs:
                        user_name = "Ismeretlen"
                        if log.user_id:
                            try:
                                from database.models import User
                                from database.session_manager import SessionLocal
                                session = SessionLocal()
                                user = session.query(User).filter_by(id=log.user_id).first()
                                if user:
                                    user_name = user.full_name or user.username
                                session.close()
                            except:
                                pass
                        action_text = {
                            "create": "Létrehozva",
                            "update": "Módosítva",
                            "delete": "Törölve"
                        }.get(log.action_type, log.action_type)
                        audit_logs.append({
                            "action": action_text,
                            "user": user_name,
                            "timestamp": log.timestamp.strftime("%Y-%m-%d %H:%M:%S") if log.timestamp else "",
                            "description": log.description or ""
                        })
                except Exception as e:
                    logger.warning(f"Error loading audit logs for threshold {threshold.id}: {e}")
                
                status_badge_variant = "emerald" if threshold.is_active else "gray"
                
                card_content_items = [
                    ft.Row([
                        ft.Column([
                            ft.Text(part_name, size=16, weight=ft.FontWeight.W_600),
                            ft.Row([
                                ft.Text(f"SKU: {part_sku}", size=12, color=DesignSystem.TEXT_SECONDARY) if part_sku else None,
                                ft.Text(f"Kategória: {part_category}", size=12, color=DesignSystem.TEXT_SECONDARY) if part_category else None,
                            ], spacing=DesignSystem.SPACING_2, wrap=True),
                        ], spacing=DesignSystem.SPACING_1, expand=True),
                        create_vibrant_badge(
                            text="Aktív" if threshold.is_active else "Inaktív",
                            variant=status_badge_variant,
                            size=11,
                        ),
                    ], spacing=DesignSystem.SPACING_2),
                    ft.Divider(height=1),
                    ft.Row([
                        create_vibrant_badge(
                            text=threshold.threshold_type,
                            variant="blue",
                            size=11,
                        ),
                        create_vibrant_badge(
                            text=threshold.period,
                            variant="purple",
                            size=11,
                        ),
                    ], spacing=DesignSystem.SPACING_2),
                    ft.Text(f"Értesítési határ: {threshold.notification_threshold}", size=14, weight=ft.FontWeight.W_500),
                    ft.Text(f"Beavatkozási határ: {threshold.intervention_threshold or 'Nincs'}", size=14),
                ]
                
                if machine_name or threshold.machine_id:
                    machine_info = f"Eszköz: {machine_name or f'ID: {threshold.machine_id}'}"
                    if machine_serial:
                        machine_info += f" ({machine_serial})"
                    card_content_items.append(ft.Text(machine_info, size=13))
                
                if threshold.notes:
                    card_content_items.append(
                        ft.Container(
                            content=ft.Text(f"Megjegyzés: {threshold.notes}", size=12, color=DesignSystem.TEXT_SECONDARY),
                            padding=ft.padding.all(DesignSystem.SPACING_2),
                            bgcolor=DesignSystem.BG_TERTIARY,
                            border_radius=DesignSystem.RADIUS_MD,
                        )
                    )
                
                # Audit trail section
                if audit_logs:
                    card_content_items.append(ft.Divider(height=1))
                    card_content_items.append(
                        ft.Text("Nyomonkövethetőség:", size=12, weight=ft.FontWeight.W_600, color=DesignSystem.TEXT_SECONDARY)
                    )
                    for log_entry in audit_logs[:3]:  # Show last 3 entries
                        card_content_items.append(
                            ft.Text(
                                f"• {log_entry['action']} - {log_entry['user']} ({log_entry['timestamp']})",
                                size=11,
                                color=DesignSystem.TEXT_SECONDARY,
                            )
                        )
                    if len(audit_logs) > 3:
                        card_content_items.append(
                            ft.Text(f"... és még {len(audit_logs) - 3} esemény", size=11, color=DesignSystem.TEXT_SECONDARY, italic=True)
                        )
                else:
                    # Show creation date if no logs
                    if threshold.created_at:
                        card_content_items.append(ft.Divider(height=1))
                        card_content_items.append(
                            ft.Text(
                                f"Létrehozva: {threshold.created_at.strftime('%Y-%m-%d %H:%M:%S') if threshold.created_at else 'N/A'}",
                                size=11,
                                color=DesignSystem.TEXT_SECONDARY,
                            )
                        )
                
                card_content_items.append(
                    ft.Row([
                        create_modern_button(
                            text="Szerkesztés",
                            on_click=lambda e, t=threshold: self._on_edit_threshold(e, page, t),
                            variant="outlined",
                        ),
                        create_modern_button(
                            text="Törlés",
                            on_click=lambda e, t=threshold: self._on_delete_threshold(e, page, t),
                            variant="outlined",
                            bgcolor=DesignSystem.ERROR,
                            color=DesignSystem.WHITE,
                        ),
                    ], spacing=DesignSystem.SPACING_2)
                )
                
                # Filter None values
                card_content_items = [item for item in card_content_items if item is not None]
                
                card = create_tailwind_card(
                    content=ft.Column(card_content_items, spacing=DesignSystem.SPACING_2),
                    padding=DesignSystem.SPACING_4,
                )
                cards.append(card)
            
            add_button = create_modern_button(
                text="Új határ hozzáadása",
                icon=ft.Icons.ADD if hasattr(ft.Icons, 'ADD') else (ft.Icons.ADD_CIRCLE if hasattr(ft.Icons, 'ADD_CIRCLE') else ft.Icons.ADD_BOX),
                on_click=lambda e: self._on_add_threshold(e, page),
                bgcolor=DesignSystem.SUCCESS,
                color=DesignSystem.WHITE,
            )
            
            if not cards:
                return ft.Column([
                    add_button,
                    create_empty_state_card(
                        icon=ft.Icons.INFO_OUTLINE if hasattr(ft.Icons, 'INFO_OUTLINE') else (ft.Icons.INFO if hasattr(ft.Icons, 'INFO') else ft.Icons.HELP_OUTLINE),
                        title="Nincs határ",
                        description="Nincs beállított limitálási határ.",
                    ),
                ], spacing=DesignSystem.SPACING_4)
            
            return ft.Column([
                add_button,
                ft.GridView(
                    controls=cards,
                    runs_count=3,
                    max_extent=400,
                    spacing=DesignSystem.SPACING_4,
                    run_spacing=DesignSystem.SPACING_4,
                ),
            ], spacing=DesignSystem.SPACING_4, scroll=ft.ScrollMode.AUTO, expand=True)
        except Exception as e:
            logger.error(f"Error loading thresholds: {e}", exc_info=True)
            return create_empty_state_card(
                icon=ft.Icons.ERROR if hasattr(ft.Icons, 'ERROR') else (ft.Icons.WARNING if hasattr(ft.Icons, 'WARNING') else ft.Icons.ALERT),
                title="Hiba",
                description=f"Az adatok betöltése során hiba történt: {str(e)}",
            )
    
    def _on_machine_select(self, e, page: ft.Page):
        """Handle machine selection"""
        self.filter_machine_id = int(e.control.value) if e.control.value else None
        # Rebuild content for machine usage trend tab
        if hasattr(self, 'content_container') and self.current_tab == 5:
            self.content_container.content = self._build_tab_content(page)
        page.update()
    
    def _on_add_threshold(self, e, page: ft.Page):
        """Handle add threshold"""
        dialog_page = self.page if hasattr(self, 'page') and self.page else page
        
        # Load parts and machines
        parts = inventory_service.list_parts()
        machines = asset_service.list_machines()
        
        # Part dropdown
        part_options = [ft.dropdown.Option(str(p.id), f"{p.name} ({p.sku})") for p in parts]
        part_dropdown = create_modern_dropdown(
            label=translator.get_text("inventory.part"),
            options=part_options,
        )
        
        # Machine dropdown (optional)
        machine_options = [ft.dropdown.Option("", "Nincs (általános)")]
        machine_options.extend([ft.dropdown.Option(str(m.id), f"{m.name} ({m.serial_number or '-'})") for m in machines])
        machine_dropdown = create_modern_dropdown(
            label="Eszköz (opcionális)",
            options=machine_options,
        )
        
        # Auto-fill machine when part is selected
        def on_part_change(e):
            """Auto-fill machine dropdown when part is selected"""
            if part_dropdown.value:
                try:
                    part_id = int(part_dropdown.value)
                    part = inventory_service.get_part(part_id)
                    if part and part.compatible_machines:
                        # If part has exactly one compatible machine, auto-select it
                        if len(part.compatible_machines) == 1:
                            machine_dropdown.value = str(part.compatible_machines[0].id)
                            dialog_page.update()
                        # If part has multiple compatible machines, keep current selection or leave empty
                        # If part has no compatible machines, clear selection
                        elif len(part.compatible_machines) == 0:
                            machine_dropdown.value = ""
                            dialog_page.update()
                except Exception as exc:
                    logger.error(f"Error auto-filling machine for part: {exc}", exc_info=True)
        
        part_dropdown.on_change = on_part_change
        
        # Threshold type dropdown
        threshold_type_options = [
            ft.dropdown.Option("usage", translator.get_text("inventory_audit.threshold_type") + " - Felhasználás"),
            ft.dropdown.Option("value", translator.get_text("inventory_audit.threshold_type") + " - Érték"),
            ft.dropdown.Option("quantity", translator.get_text("inventory_audit.threshold_type") + " - Mennyiség"),
            ft.dropdown.Option("cost", translator.get_text("inventory_audit.threshold_type") + " - Költség"),
        ]
        threshold_type_dropdown = create_modern_dropdown(
            label=translator.get_text("inventory_audit.threshold_type"),
            options=threshold_type_options,
            value="usage",
        )
        
        # Period dropdown
        period_options = [
            ft.dropdown.Option("weekly", translator.get_text("inventory_audit.weekly")),
            ft.dropdown.Option("monthly", translator.get_text("inventory_audit.monthly")),
            ft.dropdown.Option("yearly", translator.get_text("inventory_audit.yearly")),
        ]
        period_dropdown = create_modern_dropdown(
            label=translator.get_text("inventory_audit.period"),
            options=period_options,
            value="monthly",
        )
        
        # Notification threshold
        notification_threshold_field = create_modern_text_field(
            label=translator.get_text("inventory_audit.notification_threshold"),
            keyboard_type=ft.KeyboardType.NUMBER,
            hint_text="pl. 100",
        )
        
        # Intervention threshold (optional)
        intervention_threshold_field = create_modern_text_field(
            label=translator.get_text("inventory_audit.intervention_threshold") + " (opcionális)",
            keyboard_type=ft.KeyboardType.NUMBER,
            hint_text="pl. 200",
        )
        
        # Notes
        notes_field = create_modern_text_field(
            label=translator.get_text("inventory.notes"),
            multiline=True,
            max_lines=4,
        )
        
        def submit_add(e):
            try:
                if not part_dropdown.value:
                    raise ValueError(translator.get_text("common.messages.required_field"))
                if not notification_threshold_field.value:
                    raise ValueError(translator.get_text("common.messages.required_field"))
                
                part_id = int(part_dropdown.value)
                machine_id = int(machine_dropdown.value) if machine_dropdown.value else None
                threshold_type = threshold_type_dropdown.value
                period = period_dropdown.value
                notification_threshold = float(notification_threshold_field.value)
                intervention_threshold = float(intervention_threshold_field.value) if intervention_threshold_field.value else None
                notes = notes_field.value if notes_field.value else None
                
                create_threshold(
                    part_id=part_id,
                    machine_id=machine_id,
                    notification_threshold=notification_threshold,
                    intervention_threshold=intervention_threshold,
                    threshold_type=threshold_type,
                    period=period,
                    notes=notes,
                )
                
                dialog_page.close(dialog)
                dialog_page.snack_bar = ft.SnackBar(
                    content=ft.Text("Határ sikeresen létrehozva"),
                    bgcolor=DesignSystem.SUCCESS,
                )
                dialog_page.snack_bar.open = True
                # Refresh thresholds tab
                if hasattr(self, 'content_container') and self.current_tab == 7:
                    self.content_container.content = self._build_tab_content(page)
                dialog_page.update()
            except Exception as exc:
                dialog_page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Hiba: {exc}"),
                    bgcolor=DesignSystem.ERROR,
                )
                dialog_page.snack_bar.open = True
                dialog_page.update()
        
        dialog = create_modern_dialog(
            title="Új limitálási határ hozzáadása",
            content=ft.Column([
                part_dropdown,
                machine_dropdown,
                threshold_type_dropdown,
                period_dropdown,
                notification_threshold_field,
                intervention_threshold_field,
                notes_field,
            ], spacing=DesignSystem.SPACING_3, scroll=ft.ScrollMode.AUTO),
            actions=[
                create_modern_button(
                    text=translator.get_text("common.buttons.cancel"),
                    on_click=lambda _: dialog_page.close(dialog),
                    variant="text",
                ),
                create_modern_button(
                    text=translator.get_text("common.buttons.add"),
                    icon=ft.Icons.ADD if hasattr(ft.Icons, 'ADD') else (ft.Icons.ADD_CIRCLE if hasattr(ft.Icons, 'ADD_CIRCLE') else ft.Icons.ADD_BOX),
                    on_click=submit_add,
                    bgcolor=DesignSystem.SUCCESS,
                    color=DesignSystem.WHITE,
                ),
            ],
        )
        dialog_page.dialog = dialog
        dialog.open = True
        dialog_page.update()
    
    def _on_edit_threshold(self, e, page: ft.Page, threshold):
        """Handle edit threshold"""
        dialog_page = self.page if hasattr(self, 'page') and self.page else page
        
        # Notification threshold
        notification_threshold_field = create_modern_text_field(
            label=translator.get_text("inventory_audit.notification_threshold"),
            keyboard_type=ft.KeyboardType.NUMBER,
            value=str(threshold.notification_threshold),
        )
        
        # Intervention threshold
        intervention_threshold_field = create_modern_text_field(
            label=translator.get_text("inventory_audit.intervention_threshold") + " (opcionális)",
            keyboard_type=ft.KeyboardType.NUMBER,
            value=str(threshold.intervention_threshold) if threshold.intervention_threshold else "",
        )
        
        # Active checkbox
        is_active_checkbox = ft.Checkbox(
            label="Aktív",
            value=threshold.is_active,
        )
        
        # Notes
        notes_field = create_modern_text_field(
            label=translator.get_text("inventory.notes"),
            multiline=True,
            max_lines=4,
            value=threshold.notes or "",
        )
        
        def submit_edit(e):
            try:
                if not notification_threshold_field.value:
                    raise ValueError(translator.get_text("common.messages.required_field"))
                
                notification_threshold = float(notification_threshold_field.value)
                intervention_threshold = float(intervention_threshold_field.value) if intervention_threshold_field.value else None
                is_active = is_active_checkbox.value
                notes = notes_field.value if notes_field.value else None
                
                update_threshold(
                    threshold_id=threshold.id,
                    notification_threshold=notification_threshold,
                    intervention_threshold=intervention_threshold,
                    is_active=is_active,
                    notes=notes,
                )
                
                dialog_page.close(dialog)
                dialog_page.snack_bar = ft.SnackBar(
                    content=ft.Text("Határ sikeresen frissítve"),
                    bgcolor=DesignSystem.SUCCESS,
                )
                dialog_page.snack_bar.open = True
                # Refresh thresholds tab
                if hasattr(self, 'content_container') and self.current_tab == 7:
                    self.content_container.content = self._build_tab_content(page)
                dialog_page.update()
            except Exception as exc:
                dialog_page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Hiba: {exc}"),
                    bgcolor=DesignSystem.ERROR,
                )
                dialog_page.snack_bar.open = True
                dialog_page.update()
        
        dialog = create_modern_dialog(
            title="Limitálási határ szerkesztése",
            content=ft.Column([
                ft.Text(f"Alkatrész ID: {threshold.part_id}", weight=ft.FontWeight.W_600),
                ft.Text(f"Típus: {threshold.threshold_type}"),
                ft.Text(f"Időszak: {threshold.period}"),
                notification_threshold_field,
                intervention_threshold_field,
                is_active_checkbox,
                notes_field,
            ], spacing=DesignSystem.SPACING_3, scroll=ft.ScrollMode.AUTO),
            actions=[
                create_modern_button(
                    text=translator.get_text("common.buttons.cancel"),
                    on_click=lambda _: dialog_page.close(dialog),
                    variant="text",
                ),
                create_modern_button(
                    text=translator.get_text("common.buttons.save"),
                    icon=ft.Icons.SAVE if hasattr(ft.Icons, 'SAVE') else ft.Icons.CHECK,
                    on_click=submit_edit,
                    bgcolor=DesignSystem.SUCCESS,
                    color=DesignSystem.WHITE,
                ),
            ],
        )
        dialog_page.dialog = dialog
        dialog.open = True
        dialog_page.update()
    
    def _on_delete_threshold(self, e, page: ft.Page, threshold):
        """Handle delete threshold"""
        dialog_page = self.page if hasattr(self, 'page') and self.page else page
        
        def confirm_delete(e):
            try:
                delete_threshold(threshold.id)
                dialog_page.close(confirm_dialog)
                dialog_page.snack_bar = ft.SnackBar(
                    content=ft.Text("Határ törölve"),
                    bgcolor=DesignSystem.SUCCESS,
                )
                dialog_page.snack_bar.open = True
                # Refresh thresholds tab
                if hasattr(self, 'content_container') and self.current_tab == 7:
                    self.content_container.content = self._build_tab_content(page)
                dialog_page.update()
            except Exception as exc:
                dialog_page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Hiba: {exc}"),
                    bgcolor=DesignSystem.ERROR,
                )
                dialog_page.snack_bar.open = True
                dialog_page.update()
        
        confirm_dialog = create_modern_dialog(
            title="Határ törlése",
            content=ft.Text(f"Biztosan törölni szeretnéd ezt a határt?\nAlkatrész ID: {threshold.part_id}\nTípus: {threshold.threshold_type}"),
            actions=[
                create_modern_button(
                    text=translator.get_text("common.buttons.cancel"),
                    on_click=lambda _: dialog_page.close(confirm_dialog),
                    variant="text",
                ),
                create_modern_button(
                    text=translator.get_text("common.buttons.delete"),
                    icon=ft.Icons.DELETE if hasattr(ft.Icons, 'DELETE') else (ft.Icons.DELETE_OUTLINE if hasattr(ft.Icons, 'DELETE_OUTLINE') else ft.Icons.DELETE_FOREVER),
                    on_click=confirm_delete,
                    bgcolor=DesignSystem.ERROR,
                    color=DesignSystem.WHITE,
                ),
            ],
        )
        dialog_page.dialog = confirm_dialog
        confirm_dialog.open = True
        dialog_page.update()
    
    def _on_tab_change(self, e, page: ft.Page):
        """Handle tab change"""
        self.current_tab = e.control.selected_index
        # Rebuild content
        if hasattr(self, 'content_container') and self.content_container is not None:
            try:
                self.content_container.content = self._build_tab_content(page)
                page.update()
            except Exception as exc:
                logger.error(f"Error updating tab content: {exc}", exc_info=True)
                # Fallback: rebuild entire view
                page.go("/inventory_audit")
        else:
            # Fallback: rebuild entire view
            page.go("/inventory_audit")
    
    def _on_period_change(self, e, page: ft.Page):
        """Handle period change"""
        self.current_period = e.control.value
        # Rebuild content
        if hasattr(self, 'content_container') and self.content_container is not None:
            try:
                self.content_container.content = self._build_tab_content(page)
                page.update()
            except Exception as exc:
                logger.error(f"Error updating period content: {exc}", exc_info=True)
                # Fallback: rebuild entire view
                page.go("/inventory_audit")
        else:
            # Fallback: rebuild entire view
            page.go("/inventory_audit")
    
    def _on_export_excel(self, e, page: ft.Page):
        """Handle Excel export for current tab"""
        export_funcs = {
            0: lambda: export_inventory_overview_to_excel(
                period=self.current_period,
                start_date=self.start_date,
                end_date=self.end_date,
                machine_id=self.filter_machine_id,
            ),
            1: lambda: export_usage_report_to_excel(
                period=self.current_period,
                start_date=self.start_date,
                end_date=self.end_date,
                machine_id=self.filter_machine_id,
                part_id=self.filter_part_id,
            ),
            2: lambda: export_value_change_report_to_excel(
                period=self.current_period,
                start_date=self.start_date,
                end_date=self.end_date,
            ),
            3: lambda: export_stock_quantity_report_to_excel(
                machine_id=self.filter_machine_id,
                include_zero=False,
            ),
            4: lambda: export_stock_change_report_to_excel(
                period=self.current_period,
                start_date=self.start_date,
                end_date=self.end_date,
                part_id=self.filter_part_id,
            ),
            5: lambda: None,  # Machine trend - needs machine_id
            6: lambda: export_maintenance_trend_to_excel(
                machine_id=self.filter_machine_id,
                period=self.current_period,
                breakdown="monthly" if self.current_period == "yearly" else self.current_period,
            ),
            7: lambda: export_full_inventory_to_excel(),  # Thresholds tab - export full inventory
        }
        
        def on_save_result(e: ft.FilePickerResultEvent):
            if e.path is None:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(translator.get_text("worksheets.download_cancelled")),
                    bgcolor=DesignSystem.TEXT_SECONDARY,
                )
                page.snack_bar.open = True
                page.update()
                return
            
            def export_thread():
                try:
                    save_path = Path(e.path)
                    if not save_path.suffix.lower() == '.xlsx':
                        save_path = save_path.with_suffix('.xlsx')
                    
                    export_func = export_funcs.get(self.current_tab)
                    if export_func:
                        output_path = export_func()
                        if output_path and output_path.exists():
                            # Copy to user-selected location
                            import shutil
                            shutil.copy2(output_path, save_path)
                            
                            page.snack_bar = ft.SnackBar(
                                content=ft.Text(translator.get_text("inventory_audit.export_success")),
                                bgcolor=DesignSystem.SUCCESS,
                            )
                        else:
                            page.snack_bar = ft.SnackBar(
                                content=ft.Text(translator.get_text("inventory_audit.export_error")),
                                bgcolor=DesignSystem.ERROR,
                            )
                    else:
                        page.snack_bar = ft.SnackBar(
                            content=ft.Text("Export nem elérhető erre a fülre"),
                            bgcolor=DesignSystem.ERROR,
                        )
                    page.snack_bar.open = True
                    page.update()
                except Exception as exc:
                    logger.error(f"Error exporting to Excel: {exc}", exc_info=True)
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"{translator.get_text('inventory_audit.export_error')}: {exc}"),
                        bgcolor=DesignSystem.ERROR,
                    )
                    page.snack_bar.open = True
                    page.update()
            
            threading.Thread(target=export_thread, daemon=True).start()
        
        file_picker = ft.FilePicker(on_result=on_save_result)
        page.overlay.append(file_picker)
        file_picker.save_file(
            dialog_title=translator.get_text("inventory_audit.export_excel"),
            file_name=f"inventory_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["xlsx"],
        )
        page.update()
    
    def _on_export_usage_excel(self, e, page: ft.Page):
        """Handle usage report Excel export"""
        self.current_tab = 1
        self._on_export_excel(e, page)
    
    def _on_export_value_change_excel(self, e, page: ft.Page):
        """Handle value change report Excel export"""
        self.current_tab = 2
        self._on_export_excel(e, page)
    
    def _on_export_stock_quantity_excel(self, e, page: ft.Page):
        """Handle stock quantity report Excel export"""
        self.current_tab = 3
        self._on_export_excel(e, page)
    
    def _on_export_stock_change_excel(self, e, page: ft.Page):
        """Handle stock change report Excel export"""
        self.current_tab = 4
        self._on_export_excel(e, page)
    
    def _on_export_machine_trend_excel(self, e, page: ft.Page, machine_id: int):
        """Handle machine usage trend Excel export"""
        def on_save_result(e: ft.FilePickerResultEvent):
            if e.path is None:
                return
            
            def export_thread():
                try:
                    save_path = Path(e.path)
                    if not save_path.suffix.lower() == '.xlsx':
                        save_path = save_path.with_suffix('.xlsx')
                    
                    output_path = export_machine_usage_trend_to_excel(
                        machine_id=machine_id,
                        period=self.current_period,
                        breakdown="monthly" if self.current_period == "yearly" else self.current_period,
                    )
                    
                    if output_path and output_path.exists():
                        import shutil
                        shutil.copy2(output_path, save_path)
                        page.snack_bar = ft.SnackBar(
                            content=ft.Text(translator.get_text("inventory_audit.export_success")),
                            bgcolor=DesignSystem.SUCCESS,
                        )
                    else:
                        page.snack_bar = ft.SnackBar(
                            content=ft.Text(translator.get_text("inventory_audit.export_error")),
                            bgcolor=DesignSystem.ERROR,
                        )
                    page.snack_bar.open = True
                    page.update()
                except Exception as exc:
                    logger.error(f"Error exporting machine trend: {exc}", exc_info=True)
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"{translator.get_text('inventory_audit.export_error')}: {exc}"),
                        bgcolor=DesignSystem.ERROR,
                    )
                    page.snack_bar.open = True
                    page.update()
            
            threading.Thread(target=export_thread, daemon=True).start()
        
        file_picker = ft.FilePicker(on_result=on_save_result)
        page.overlay.append(file_picker)
        file_picker.save_file(
            dialog_title=translator.get_text("inventory_audit.export_excel"),
            file_name=f"machine_usage_trend_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["xlsx"],
        )
        page.update()
    
    def _on_export_maintenance_trend_excel(self, e, page: ft.Page):
        """Handle maintenance trend Excel export"""
        self.current_tab = 6
        self._on_export_excel(e, page)

