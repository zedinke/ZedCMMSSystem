"""
Inventory Count Screen - Leltár kezelés
"""
import flet as ft
# Compatibility for flet 0.23.2 - Icons are strings, not ft.Icons
if not hasattr(ft, 'Icons'):
    from utils.flet_icons import Icons
    ft.Icons = Icons
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import requests
from pathlib import Path

from localization.translator import translator
from services.context_service import get_app_context
from ui.services.websocket_client import PollingClient
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
    create_info_card,
    create_metric_card,
)
from ui.components.pagination import PaginationController, create_pagination_controls, create_items_per_page_selector
from ui.components.selectable_list import SelectableList
from ui.components.batch_actions_bar import create_batch_actions_bar
from services.export_service import ExportService
from services.autosave_service import get_autosave_service
from services.context_service import get_current_user_id
import logging

logger = logging.getLogger(__name__)


class InventoryCountScreen:
    def __init__(self):
        self.current_view = "list"  # "list", "detail", "create"
        self.selected_count_id = None
        self.counts_list = []
        self.count_detail = None
        self.content_container = None
        self.page = None
    
    def _create_view_details_handler(self, count_id):
        """Create a handler function for view details click to avoid lambda closure issues"""
        def handle_click(e):
            self._on_view_details(e, count_id)
        return handle_click
    
    def _create_approve_correction_handler(self, correction_id):
        """Create a handler function for approve correction click to avoid lambda closure issues"""
        def handle_click(e):
            self._on_approve_correction(e, correction_id)
        return handle_click
    
    def _create_reject_correction_handler(self, correction_id):
        """Create a handler function for reject correction click to avoid lambda closure issues"""
        def handle_click(e):
            self._on_reject_correction(e, correction_id)
        return handle_click
    
    def _create_download_document_handler(self, file_path):
        """Create a handler function for download document click to avoid lambda closure issues"""
        def handle_click(e):
            self._on_download_document(e, file_path)
        return handle_click
    
    def _create_generate_document_handler(self, doc_type):
        """Create a handler function for generate document click to avoid lambda closure issues"""
        def handle_click(e):
            self._on_generate_document(e, doc_type)
        return handle_click
        self.filter_status = None
        self.filter_start_date = None
        self.filter_end_date = None
        self.search_query = ""
        self.selected_items = []  # For batch operations
        self.pagination_controller = None
        self.polling_client = None
    
    def view(self, page: ft.Page):
        """Main view for inventory count screen"""
        self.page = page
        
        # Initialize real-time updates with HTTP polling
        ctx = get_app_context()
        if ctx and ctx.token:
            try:
                api_url = "http://localhost:8000"
                if hasattr(ctx, 'api_url') and ctx.api_url:
                    api_url = ctx.api_url
                
                def on_realtime_message(message: dict):
                    """Handle real-time update message"""
                    event_type = message.get("event_type")
                    data = message.get("data", {})
                    
                    if event_type == "inventory_count_update":
                        # Refresh counts list if on list view
                        if self.current_view == "list":
                            self._load_counts_list()
                            if self.content_container:
                                self.content_container.content = self._build_list_view()
                                if self.page:
                                    self.page.update()
                    elif event_type == "inventory_count_item_update" and data.get("count_id") == self.selected_count_id:
                        # Refresh detail view if viewing the updated count
                        if self.current_view == "detail" and self.selected_count_id:
                            self._load_count_detail(self.selected_count_id)
                            if self.content_container:
                                self.content_container.content = self._build_detail_view()
                                if self.page:
                                    self.page.update()
                
                # Create polling client for real-time updates
                polling_client = PollingClient(
                    api_url=api_url,
                    token=ctx.token,
                    on_message=on_realtime_message,
                    poll_interval=5.0,  # Poll every 5 seconds
                )
                polling_client.start_polling()
                self.polling_client = polling_client
            except Exception as e:
                logger.error(f"Error initializing real-time updates: {e}")
                self.polling_client = None
        
        if self.current_view == "list":
            return self._build_list_view()
        elif self.current_view == "detail":
            return self._build_detail_view()
        elif self.current_view == "create":
            return self._build_create_view()
        else:
            return self._build_list_view()
    
    def _get_api_url(self) -> str:
        """Get API base URL"""
        # Desktop app always uses localhost
        return "http://localhost:8000/api/inventory-counts"
    
    def _get_auth_headers(self) -> dict:
        """Get authentication headers"""
        context = get_app_context()
        token = context.token
        if not token:
            logger.warning("No token found in context")
            return {}
        headers = {"Authorization": f"Bearer {token}"}
        logger.debug(f"Auth headers prepared, token length: {len(token) if token else 0}")
        return headers
    
    def _load_counts_list(self):
        """Load inventory counts list from API"""
        try:
            url = self._get_api_url()
            params = {}
            if self.filter_status:
                params["status_filter"] = self.filter_status
            if self.filter_start_date:
                params["start_date"] = self.filter_start_date.isoformat()
            if self.filter_end_date:
                params["end_date"] = self.filter_end_date.isoformat()
            
            headers = self._get_auth_headers()
            logger.debug(f"Making GET request to {url} with headers: {list(headers.keys())}")
            response = requests.get(url, headers=headers, params=params)
            logger.debug(f"Response status: {response.status_code}")
            if response.status_code == 200:
                self.counts_list = response.json()
            elif response.status_code == 401:
                logger.error(f"Unauthorized (401) - token may be invalid or expired. Response: {response.text[:200]}")
                self.counts_list = []
            else:
                logger.error(f"Error loading counts: {response.status_code}, Response: {response.text[:200]}")
                self.counts_list = []
        except Exception as e:
            logger.error(f"Error loading inventory counts: {e}", exc_info=True)
            self.counts_list = []
    
    def _load_count_detail(self, count_id: int):
        """Load inventory count detail from API"""
        try:
            url = f"{self._get_api_url()}/{count_id}"
            response = requests.get(url, headers=self._get_auth_headers())
            if response.status_code == 200:
                self.count_detail = response.json()
                self.selected_count_id = count_id
            else:
                logger.error(f"Error loading count detail: {response.status_code}")
                self.count_detail = None
        except Exception as e:
            logger.error(f"Error loading inventory count detail: {e}", exc_info=True)
            self.count_detail = None
    
    def _build_list_view(self):
        """Build the list view"""
        # Load data
        self._load_counts_list()
        
        # Search field
        search_field = create_modern_text_field(
            label=translator.get_text("common.search") if hasattr(translator, 'get_text') else "Keresés / Search",
            hint_text=translator.get_text("common.search_hint") if hasattr(translator, 'get_text') else "Keresés...",
            value=self.search_query,
            on_change=lambda e: self._on_search_change(e),
            width=300,
        )
        
        # Status filter dropdown
        status_filter = create_modern_dropdown(
            label="Státusz szűrő / Status Filter",
            options=[
                ft.dropdown.Option("", "Összes / All"),
                ft.dropdown.Option("planned", "Tervezett / Planned"),
                ft.dropdown.Option("in_progress", "Folyamatban / In Progress"),
                ft.dropdown.Option("first_round_complete", "Első kör befejezve / First Round Complete"),
                ft.dropdown.Option("second_round_complete", "Második kör befejezve / Second Round Complete"),
                ft.dropdown.Option("awaiting_corrections", "Korrekciókra vár / Awaiting Corrections"),
                ft.dropdown.Option("completed", "Befejezett / Completed"),
                ft.dropdown.Option("approved", "Jóváhagyott / Approved"),
            ],
            value=self.filter_status or "",
            on_change=lambda e: self._on_status_filter_change(e),
        )
        
        # Create button - use direct ElevatedButton to ensure click events work
        def on_create_button_click(e):
            logger.info("[INVENTORY_COUNT] ========== Create button clicked! ==========")
            logger.info(f"[INVENTORY_COUNT] Event: {e}")
            logger.info(f"[INVENTORY_COUNT] Event type: {type(e)}")
            print("[INVENTORY_COUNT] Create button clicked - PRINT STATEMENT")
            try:
                self._on_create_click(e)
            except Exception as ex:
                logger.error(f"[INVENTORY_COUNT] Error in _on_create_click: {ex}", exc_info=True)
                print(f"[INVENTORY_COUNT] ERROR: {ex}")
        
        # Try using ElevatedButton directly instead of create_modern_button
        create_btn = ft.ElevatedButton(
            text="Új leltár / New Count",
            icon=ft.Icons.ADD if hasattr(ft.Icons, 'ADD') else ft.Icons.ADD_CIRCLE,
            on_click=on_create_button_click,
            bgcolor=DesignSystem.SUCCESS,
            color=DesignSystem.WHITE,
            height=40,
        )
        logger.info(f"[INVENTORY_COUNT] Create button created: {create_btn}")
        logger.info(f"[INVENTORY_COUNT] Create button type: {type(create_btn)}")
        logger.info(f"[INVENTORY_COUNT] Create button on_click: {getattr(create_btn, 'on_click', 'N/A')}")
        print(f"[INVENTORY_COUNT] Create button created - PRINT: {type(create_btn)}")
        
        # Apply search filter
        filtered_counts = self.counts_list
        if self.search_query:
            search_lower = self.search_query.lower()
            filtered_counts = [
                count for count in self.counts_list
                if search_lower in (count.get("inventory_number", "") or "").lower()
                or search_lower in (count.get("status", "") or "").lower()
                or search_lower in (count.get("first_round_checker1_name", "") or "").lower()
                or search_lower in (count.get("second_round_checker1_name", "") or "").lower()
            ]
        
        # Initialize pagination controller
        if self.pagination_controller is None:
            self.pagination_controller = PaginationController(
                total_items=len(filtered_counts),
                items_per_page=20,
                on_page_change=lambda page_num: self._refresh_list_view()
            )
        else:
            self.pagination_controller.update_total_items(len(filtered_counts))
        
        # Get items for current page
        start_idx = (self.pagination_controller.current_page - 1) * self.pagination_controller.items_per_page
        end_idx = start_idx + self.pagination_controller.items_per_page
        paginated_counts = filtered_counts[start_idx:end_idx]
        
        # Build table
        table_rows = []
        if paginated_counts:
            for count in paginated_counts:
                status_badge = self._get_status_badge(count.get("status", ""))
                table_rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(count.get("inventory_number", "-"))),
                            ft.DataCell(ft.Text(self._format_date(count.get("planned_date")))),
                            ft.DataCell(status_badge),
                            ft.DataCell(ft.Text(count.get("first_round_checker1_name", "-"))),
                            ft.DataCell(ft.Text(count.get("second_round_checker1_name", "-"))),
                            ft.DataCell(
                                # Create wrapper function to avoid lambda closure issues in PyInstaller
                                create_modern_button(
                                    text="Részletek / Details",
                                    icon=ft.Icons.VISIBILITY if hasattr(ft.Icons, 'VISIBILITY') else ft.Icons.INFO,
                                    on_click=self._create_view_details_handler(count.get("id")),
                                    variant="outlined",
                                )
                            ),
                        ],
                        on_select_changed=lambda e, cid=count.get("id"): self._on_view_details(None, cid),  # This is fine, no closure issue
                    )
                )
        
        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Sorszám / Number")),
                ft.DataColumn(ft.Text("Tervezett dátum / Planned Date")),
                ft.DataColumn(ft.Text("Státusz / Status")),
                ft.DataColumn(ft.Text("1. kör ellenőrző 1 / Round 1 Checker 1")),
                ft.DataColumn(ft.Text("2. kör ellenőrző 1 / Round 2 Checker 1")),
                ft.DataColumn(ft.Text("Műveletek / Actions")),
            ],
            rows=table_rows,
        )
        
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text("Leltár / Inventory Count", size=24, weight=ft.FontWeight.BOLD),
                            create_btn,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Divider(),
                    ft.Row([
                        search_field,
                        status_filter,
                        create_modern_button(
                            text=translator.get_text("common.export_csv"),
                            icon=ft.Icons.FILE_DOWNLOAD,
                            on_click=self._handle_export_csv,
                            bgcolor=DesignSystem.SUCCESS,
                            color=DesignSystem.WHITE,
                        ),
                        create_modern_button(
                            text=translator.get_text("common.export_excel"),
                            icon=ft.Icons.FILE_DOWNLOAD,
                            on_click=self._handle_export_excel,
                            bgcolor=DesignSystem.SUCCESS,
                            color=DesignSystem.WHITE,
                        ),
                    ], spacing=DesignSystem.SPACING_4, wrap=True),
                    ft.Container(
                        content=table if table_rows else create_empty_state_card(
                            icon=ft.Icons.INVENTORY_2 if hasattr(ft.Icons, 'INVENTORY_2') else ft.Icons.INVENTORY,
                            title="Nincs leltár / No Inventory Counts",
                            description="Még nincs létrehozva leltár. Kattintson az 'Új leltár' gombra a létrehozáshoz.",
                        ),
                        expand=True,
                    ),
                    # Pagination controls
                    *([ft.Row([
                        create_pagination_controls(self.pagination_controller) if self.pagination_controller else ft.Container(),
                        create_items_per_page_selector(self.pagination_controller) if self.pagination_controller else ft.Container(),
                    ], spacing=DesignSystem.SPACING_4, alignment=ft.MainAxisAlignment.SPACE_BETWEEN)] if self.pagination_controller and table_rows else []),
                ],
                spacing=DesignSystem.SPACING_4,
                expand=True,
            ),
            padding=DesignSystem.SPACING_4,
            expand=True,
        )
    
    def _build_detail_view(self):
        """Build the detail view"""
        if not self.count_detail:
            return ft.Container(
                content=ft.Text("Leltár nem található / Inventory count not found"),
                alignment=ft.alignment.center,
            )
        
        count = self.count_detail
        
        # Header with back button
        header = ft.Row(
            controls=[
                create_modern_button(
                    text="Vissza / Back",
                    icon=ft.Icons.ARROW_BACK if hasattr(ft.Icons, 'ARROW_BACK') else ft.Icons.ARROW_LEFT,
                    on_click=self._on_back_to_list,
                    variant="outlined",
                ),
                ft.Text(f"Leltár: {count.get('inventory_number', '-')}", size=20, weight=ft.FontWeight.BOLD),
                self._get_status_badge(count.get("status", "")),
            ],
            spacing=DesignSystem.SPACING_3,
        )
        
        # Info card
        info_card = create_tailwind_card(
            content=ft.Column(
                controls=[
                    ft.Text("Alapinformációk / Basic Information", size=16, weight=ft.FontWeight.W_600),
                    ft.Text(f"Sorszám / Number: {count.get('inventory_number', '-')}"),
                    ft.Text(f"Státusz / Status: {count.get('status', '-')}"),
                    ft.Text(f"Tervezett dátum / Planned Date: {self._format_date(count.get('planned_date'))}"),
                    ft.Text(f"Kezdés / Started: {self._format_date(count.get('started_at'))}"),
                    ft.Text(f"Első kör befejezve / First Round Complete: {self._format_date(count.get('first_round_completed_at'))}"),
                    ft.Text(f"Második kör befejezve / Second Round Complete: {self._format_date(count.get('second_round_completed_at'))}"),
                    ft.Text(f"Befejezve / Completed: {self._format_date(count.get('completed_at'))}"),
                    ft.Text(f"Jóváhagyva / Approved: {self._format_date(count.get('approved_at'))}"),
                    ft.Text(f"1. kör ellenőrző 1 / Round 1 Checker 1: {count.get('first_round_checker1_name', '-')}"),
                    ft.Text(f"1. kör ellenőrző 2 / Round 1 Checker 2: {count.get('first_round_checker2_name', '-')}"),
                    ft.Text(f"2. kör ellenőrző 1 / Round 2 Checker 1: {count.get('second_round_checker1_name', '-')}"),
                    ft.Text(f"2. kör ellenőrző 2 / Round 2 Checker 2: {count.get('second_round_checker2_name', '-')}"),
                ],
                spacing=DesignSystem.SPACING_2,
            ),
            padding=DesignSystem.SPACING_4,
        )
        
        # Items table
        items_table = self._build_items_table()
        
        # Corrections section
        corrections_section = self._build_corrections_section()
        
        # Documents section
        documents_section = self._build_documents_section()
        
        # Action buttons
        action_buttons = self._build_action_buttons()
        
        return ft.Container(
            content=ft.Column(
                controls=[
                    header,
                    ft.Divider(),
                    info_card,
                    ft.Divider(),
                    ft.Text("Tételek / Items", size=18, weight=ft.FontWeight.BOLD),
                    items_table,
                    ft.Divider(),
                    corrections_section,
                    ft.Divider(),
                    documents_section,
                    ft.Divider(),
                    action_buttons,
                ],
                spacing=DesignSystem.SPACING_4,
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=DesignSystem.SPACING_4,
            expand=True,
        )
    
    def _build_items_table(self):
        """Build items table"""
        if not self.count_detail or not self.count_detail.get("items"):
            return create_empty_state_card(
                icon=ft.Icons.INVENTORY_2 if hasattr(ft.Icons, 'INVENTORY_2') else ft.Icons.INVENTORY,
                title="Nincsenek tételek / No Items",
                description="Még nincsenek tételek a leltárban.",
            )
        
        items = self.count_detail.get("items", [])
        table_rows = []
        
        for item in items:
            table_rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(item.get("part_sku", "-"))),
                        ft.DataCell(ft.Text(item.get("part_name", "-"))),
                        ft.DataCell(ft.Text(item.get("storage_location_name", "-"))),
                        ft.DataCell(ft.Text(str(item.get("system_quantity", 0)))),
                        ft.DataCell(ft.Text(str(item.get("first_round_counted_quantity", "-")))),
                        ft.DataCell(ft.Text(str(item.get("second_round_counted_quantity", "-")))),
                        ft.DataCell(ft.Text(str(item.get("final_quantity", "-")))),
                        ft.DataCell(ft.Text(str(item.get("difference", 0)))),
                        ft.DataCell(self._get_item_status_badge(item.get("status", ""))),
                    ]
                )
            )
        
        return ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("SKU")),
                ft.DataColumn(ft.Text("Név / Name")),
                ft.DataColumn(ft.Text("Raktári hely / Storage Location")),
                ft.DataColumn(ft.Text("Rendszer / System")),
                ft.DataColumn(ft.Text("1. kör / Round 1")),
                ft.DataColumn(ft.Text("2. kör / Round 2")),
                ft.DataColumn(ft.Text("Végleges / Final")),
                ft.DataColumn(ft.Text("Különbség / Difference")),
                ft.DataColumn(ft.Text("Státusz / Status")),
            ],
            rows=table_rows,
        )
    
    def _build_corrections_section(self):
        """Build corrections section"""
        if not self.count_detail or not self.count_detail.get("corrections"):
            return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("Korrekciók / Corrections", size=18, weight=ft.FontWeight.BOLD),
                        ft.Text("Nincsenek korrekciók / No corrections"),
                    ],
                    spacing=DesignSystem.SPACING_2,
                ),
            )
        
        corrections = self.count_detail.get("corrections", [])
        correction_rows = []
        
        for corr in corrections:
            status_badge = self._get_correction_status_badge(corr.get("status", ""))
            correction_rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(corr.get("part_sku", "-"))),
                        ft.DataCell(ft.Text(corr.get("part_name", "-"))),
                        ft.DataCell(ft.Text(f"{corr.get('correction_type', '-')} {corr.get('quantity', 0)}")),
                        ft.DataCell(ft.Text(corr.get("reason", "-"))),
                        ft.DataCell(status_badge),
                        ft.DataCell(
                            ft.Row(
                                controls=[
                                    create_modern_button(
                                        text="Jóváhagyás / Approve",
                                        icon=ft.Icons.CHECK if hasattr(ft.Icons, 'CHECK') else ft.Icons.CHECK_CIRCLE,
                                        on_click=self._create_approve_correction_handler(corr.get("id")),
                                        bgcolor=DesignSystem.SUCCESS,
                                        color=DesignSystem.WHITE,
                                    ) if corr.get("status") == "pending" else ft.Container(),
                                    create_modern_button(
                                        text="Elutasítás / Reject",
                                        icon=ft.Icons.CLOSE if hasattr(ft.Icons, 'CLOSE') else ft.Icons.CANCEL,
                                        on_click=self._create_reject_correction_handler(corr.get("id")),
                                        bgcolor=DesignSystem.ERROR,
                                        color=DesignSystem.WHITE,
                                    ) if corr.get("status") == "pending" else ft.Container(),
                                ],
                                spacing=DesignSystem.SPACING_2,
                            )
                        ),
                    ]
                )
            )
        
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Korrekciók / Corrections", size=18, weight=ft.FontWeight.BOLD),
                    ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text("SKU")),
                            ft.DataColumn(ft.Text("Név / Name")),
                            ft.DataColumn(ft.Text("Korrekció / Correction")),
                            ft.DataColumn(ft.Text("Indoklás / Reason")),
                            ft.DataColumn(ft.Text("Státusz / Status")),
                            ft.DataColumn(ft.Text("Műveletek / Actions")),
                        ],
                        rows=correction_rows,
                    ),
                ],
                spacing=DesignSystem.SPACING_2,
            ),
        )
    
    def _build_documents_section(self):
        """Build documents section"""
        if not self.count_detail or not self.count_detail.get("documents"):
            return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("Dokumentumok / Documents", size=18, weight=ft.FontWeight.BOLD),
                        ft.Text("Nincsenek dokumentumok / No documents"),
                    ],
                    spacing=DesignSystem.SPACING_2,
                ),
            )
        
        documents = self.count_detail.get("documents", [])
        doc_buttons = []
        
        for doc in documents:
            doc_type_text = "Leltárlap / Count Sheet" if doc.get("document_type") == "count_sheet" else "Korrekciós lap / Correction Sheet"
            doc_buttons.append(
                create_modern_button(
                    text=f"{doc_type_text} - {self._format_date(doc.get('generated_at'))}",
                    icon=ft.Icons.DOWNLOAD if hasattr(ft.Icons, 'DOWNLOAD') else ft.Icons.FILE_DOWNLOAD,
                    on_click=self._create_download_document_handler(doc.get("file_path")),
                    variant="outlined",
                )
            )
        
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Dokumentumok / Documents", size=18, weight=ft.FontWeight.BOLD),
                    ft.Row(
                        controls=doc_buttons,
                        wrap=True,
                    ),
                    create_modern_button(
                        text="Leltárlap generálása / Generate Count Sheet",
                        icon=ft.Icons.PRINT if hasattr(ft.Icons, 'PRINT') else ft.Icons.DESCRIPTION,
                        on_click=self._create_generate_document_handler("count_sheet"),
                        bgcolor=DesignSystem.BLUE_500,
                        color=DesignSystem.WHITE,
                    ),
                    create_modern_button(
                        text="Korrekciós lap generálása / Generate Correction Sheet",
                        icon=ft.Icons.PRINT if hasattr(ft.Icons, 'PRINT') else ft.Icons.DESCRIPTION,
                        on_click=self._create_generate_document_handler("correction_sheet"),
                        bgcolor=DesignSystem.PURPLE_500,
                        color=DesignSystem.WHITE,
                    ),
                ],
                spacing=DesignSystem.SPACING_2,
            ),
        )
    
    def _build_action_buttons(self):
        """Build action buttons based on status"""
        if not self.count_detail:
            return ft.Container()
        
        status = self.count_detail.get("status", "")
        buttons = []
        
        if status == "planned":
            buttons.append(
                create_modern_button(
                    text="Indítás / Start",
                    icon=ft.Icons.PLAY_ARROW if hasattr(ft.Icons, 'PLAY_ARROW') else ft.Icons.PLAY_CIRCLE,
                    on_click=self._on_start_count,
                    bgcolor=DesignSystem.SUCCESS,
                    color=DesignSystem.WHITE,
                )
            )
        elif status == "in_progress":
            buttons.append(
                create_modern_button(
                    text="Első kör befejezése / Complete First Round",
                    icon=ft.Icons.CHECK if hasattr(ft.Icons, 'CHECK') else ft.Icons.CHECK_CIRCLE,
                    on_click=lambda e: self._on_complete_round(e, 1),  # This is fine, no closure issue
                    bgcolor=DesignSystem.BLUE_500,
                    color=DesignSystem.WHITE,
                )
            )
        elif status == "first_round_complete":
            buttons.append(
                create_modern_button(
                    text="Második kör befejezése / Complete Second Round",
                    icon=ft.Icons.CHECK if hasattr(ft.Icons, 'CHECK') else ft.Icons.CHECK_CIRCLE,
                    on_click=lambda e: self._on_complete_round(e, 2),  # This is fine, no closure issue
                    bgcolor=DesignSystem.BLUE_500,
                    color=DesignSystem.WHITE,
                )
            )
        elif status in ["completed", "second_round_complete"]:
            buttons.append(
                create_modern_button(
                    text="Jóváhagyás / Approve",
                    icon=ft.Icons.CHECK if hasattr(ft.Icons, 'CHECK') else ft.Icons.CHECK_CIRCLE,
                    on_click=self._on_approve_count,
                    bgcolor=DesignSystem.SUCCESS,
                    color=DesignSystem.WHITE,
                )
            )
        
        return ft.Row(
            controls=buttons,
            spacing=DesignSystem.SPACING_3,
        )
    
    def _build_create_view(self):
        """Build create view"""
        planned_date_field = create_modern_text_field(
            label="Tervezett dátum / Planned Date",
            hint_text="YYYY-MM-DD",
        )
        
        checker1_round1_field = create_modern_text_field(
            label="1. kör ellenőrző 1 / Round 1 Checker 1",
        )
        
        checker2_round1_field = create_modern_text_field(
            label="1. kör ellenőrző 2 / Round 1 Checker 2",
        )
        
        checker1_round2_field = create_modern_text_field(
            label="2. kör ellenőrző 1 / Round 2 Checker 1",
        )
        
        checker2_round2_field = create_modern_text_field(
            label="2. kör ellenőrző 2 / Round 2 Checker 2",
        )
        
        # Use ft.TextField directly for multiline with min_lines
        notes_field = ft.TextField(
            label="Megjegyzések / Notes",
            multiline=True,
            min_lines=3,
            max_lines=5,
        )
        
        # Initialize autosave service
        autosave_service = get_autosave_service()
        user_id = get_current_user_id()
        autosave_timer_ref = {"value": None}
        autosave_enabled = True
        
        # Load draft if exists (for create, entity_id is None)
        if user_id:
            draft = autosave_service.load_draft("inventory_count", user_id, entity_id=None)
            if draft and draft.get("form_data"):
                form_data = draft.get("form_data", {})
                if "planned_date" in form_data and form_data["planned_date"]:
                    planned_date_field.value = form_data["planned_date"]
                if "first_round_checker1_name" in form_data and form_data["first_round_checker1_name"]:
                    checker1_round1_field.value = form_data["first_round_checker1_name"]
                if "first_round_checker2_name" in form_data and form_data["first_round_checker2_name"]:
                    checker2_round1_field.value = form_data["first_round_checker2_name"]
                if "second_round_checker1_name" in form_data and form_data["second_round_checker1_name"]:
                    checker1_round2_field.value = form_data["second_round_checker1_name"]
                if "second_round_checker2_name" in form_data and form_data["second_round_checker2_name"]:
                    checker2_round2_field.value = form_data["second_round_checker2_name"]
                if "notes" in form_data and form_data["notes"]:
                    notes_field.value = form_data["notes"]
        
        # Auto-save function
        def save_draft():
            """Save current form state as draft"""
            if not autosave_enabled or not user_id:
                return
            
            try:
                form_data = {
                    "planned_date": planned_date_field.value or "",
                    "first_round_checker1_name": checker1_round1_field.value or "",
                    "first_round_checker2_name": checker2_round1_field.value or "",
                    "second_round_checker1_name": checker1_round2_field.value or "",
                    "second_round_checker2_name": checker2_round2_field.value or "",
                    "notes": notes_field.value or "",
                }
                
                autosave_service.save_draft(
                    entity_type="inventory_count",
                    form_data=form_data,
                    user_id=user_id,
                    entity_id=None,  # None for create
                )
                logger.debug("Auto-saved draft for inventory count (create)")
            except Exception as e:
                logger.error(f"Error auto-saving draft: {e}")
        
        # Auto-save on field changes
        def on_field_change(e):
            """Handle field change and trigger auto-save"""
            if autosave_timer_ref["value"]:
                autosave_timer_ref["value"].cancel()
            
            # Schedule auto-save after 2 seconds of inactivity
            def delayed_save():
                save_draft()
            
            timer = threading.Timer(2.0, delayed_save)
            timer.daemon = True
            autosave_timer_ref["value"] = timer
            timer.start()
        
        # Attach change handlers
        planned_date_field.on_change = on_field_change
        checker1_round1_field.on_change = on_field_change
        checker2_round1_field.on_change = on_field_change
        checker1_round2_field.on_change = on_field_change
        checker2_round2_field.on_change = on_field_change
        notes_field.on_change = on_field_change
        
        def on_create(e):
            try:
                planned_date = datetime.fromisoformat(planned_date_field.value)
            except:
                self.page.snack_bar = ft.SnackBar(
                    ft.Text("Érvénytelen dátum formátum / Invalid date format"),
                    bgcolor=DesignSystem.ERROR,
                )
                self.page.snack_bar.open = True
                self.page.update()
                return
            
            data = {
                "planned_date": planned_date.isoformat(),
                "first_round_checker1_name": checker1_round1_field.value,
                "first_round_checker2_name": checker2_round1_field.value,
                "second_round_checker1_name": checker1_round2_field.value,
                "second_round_checker2_name": checker2_round2_field.value,
                "notes": notes_field.value or None,
            }
            
            try:
                response = requests.post(
                    self._get_api_url(),
                    json=data,
                    headers=self._get_auth_headers(),
                )
                if response.status_code == 201:
                    count = response.json()
                    
                    # Clear draft after successful creation
                    if user_id:
                        try:
                            autosave_service.clear_draft("inventory_count", user_id, entity_id=None)
                        except Exception as e:
                            logger.error(f"Error clearing draft: {e}")
                    
                    self.page.snack_bar = ft.SnackBar(
                        ft.Text("Leltár létrehozva / Inventory count created"),
                        bgcolor=DesignSystem.SUCCESS,
                    )
                    self.page.snack_bar.open = True
                    self.current_view = "detail"
                    self._load_count_detail(count.get("id"))
                    self.page.update()
                else:
                    self.page.snack_bar = ft.SnackBar(
                        ft.Text(f"Hiba / Error: {response.status_code}"),
                        bgcolor=DesignSystem.ERROR,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
            except Exception as ex:
                logger.error(f"Error creating inventory count: {ex}", exc_info=True)
                self.page.snack_bar = ft.SnackBar(
                    ft.Text(f"Hiba / Error: {str(ex)}"),
                    bgcolor=DesignSystem.ERROR,
                )
                self.page.snack_bar.open = True
                self.page.update()
        
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            create_modern_button(
                                text="Vissza / Back",
                                icon=ft.Icons.ARROW_BACK if hasattr(ft.Icons, 'ARROW_BACK') else ft.Icons.ARROW_LEFT,
                                on_click=self._on_back_to_list,
                                variant="outlined",
                            ),
                            ft.Text("Új leltár / New Inventory Count", size=20, weight=ft.FontWeight.BOLD),
                        ],
                        spacing=DesignSystem.SPACING_3,
                    ),
                    ft.Divider(),
                    create_tailwind_card(
                        content=ft.Column(
                            controls=[
                                planned_date_field,
                                checker1_round1_field,
                                checker2_round1_field,
                                checker1_round2_field,
                                checker2_round2_field,
                                notes_field,
                                create_modern_button(
                                    text="Létrehozás / Create",
                                    icon=ft.Icons.SAVE if hasattr(ft.Icons, 'SAVE') else ft.Icons.CHECK,
                                    on_click=on_create,
                                    bgcolor=DesignSystem.SUCCESS,
                                    color=DesignSystem.WHITE,
                                ),
                            ],
                            spacing=DesignSystem.SPACING_3,
                        ),
                        padding=DesignSystem.SPACING_4,
                    ),
                ],
                spacing=DesignSystem.SPACING_4,
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=DesignSystem.SPACING_4,
            expand=True,
        )
    
    def _get_status_badge(self, status: str):
        """Get status badge"""
        status_colors = {
            "planned": DesignSystem.GRAY_500,
            "in_progress": DesignSystem.BLUE_500,
            "first_round_complete": DesignSystem.ORANGE_500,
            "second_round_complete": DesignSystem.PURPLE_500,
            "awaiting_corrections": DesignSystem.AMBER_500,
            "completed": DesignSystem.CYAN_500,
            "approved": DesignSystem.SUCCESS,
        }
        color = status_colors.get(status, DesignSystem.GRAY_500)
        return create_vibrant_badge(status, color=color)
    
    def _get_item_status_badge(self, status: str):
        """Get item status badge"""
        status_colors = {
            "match": DesignSystem.SUCCESS,
            "discrepancy": DesignSystem.WARNING,
            "corrected": DesignSystem.INFO,
        }
        color = status_colors.get(status, DesignSystem.GRAY_500)
        return create_vibrant_badge(status, color=color)
    
    def _get_correction_status_badge(self, status: str):
        """Get correction status badge"""
        status_colors = {
            "pending": DesignSystem.AMBER_500,
            "approved": DesignSystem.SUCCESS,
            "rejected": DesignSystem.ERROR,
        }
        color = status_colors.get(status, DesignSystem.GRAY_500)
        return create_vibrant_badge(status, color=color)
    
    def _format_date(self, date_str: Optional[str]) -> str:
        """Format date string"""
        if not date_str:
            return "-"
        try:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.strftime("%Y-%m-%d %H:%M")
        except:
            return date_str
    
    def _on_search_change(self, e):
        """Handle search field change"""
        self.search_query = e.control.value or ""
        # Reset pagination to first page when search changes
        if self.pagination_controller:
            self.pagination_controller.go_to_page(1)
        self._refresh_list_view()
    
    def _refresh_list_view(self):
        """Refresh the list view"""
        if self.content_container:
            self.content_container.content = self._build_list_view()
            self.page.update()
        else:
            # Fallback: rebuild entire view
            self.page.go("/inventory_count")
    
    def _on_status_filter_change(self, e):
        """Handle status filter change"""
        self.filter_status = e.control.value if e.control.value else None
        # Reset pagination to first page when filter changes
        if self.pagination_controller:
            self.pagination_controller.go_to_page(1)
        self._load_counts_list()
        if self.content_container:
            self.content_container.content = self._build_list_view()
            self.page.update()
    
    def _handle_export_csv(self, e):
        """Handle CSV export"""
        try:
            # Get all counts (apply filters but not pagination)
            self._load_counts_list()
            
            # Apply search filter
            filtered_counts = self.counts_list
            if self.search_query:
                search_lower = self.search_query.lower()
                filtered_counts = [
                    count for count in self.counts_list
                    if search_lower in (count.get("inventory_number", "") or "").lower()
                    or search_lower in (count.get("status", "") or "").lower()
                    or search_lower in (count.get("first_round_checker1_name", "") or "").lower()
                    or search_lower in (count.get("second_round_checker1_name", "") or "").lower()
                ]
            
            export_data = []
            headers = [
                "Inventory Number",
                "Planned Date",
                "Status",
                "Round 1 Checker 1",
                "Round 2 Checker 1",
            ]
            
            for count in filtered_counts:
                export_data.append([
                    count.get("inventory_number", ""),
                    self._format_date(count.get("planned_date")),
                    count.get("status", ""),
                    count.get("first_round_checker1_name", ""),
                    count.get("second_round_checker1_name", ""),
                ])
            
            def on_save_result(e: ft.FilePickerResultEvent):
                if e.path:
                    from pathlib import Path
                    from datetime import datetime
                    save_path = Path(e.path).with_suffix('.csv')
                    csv_data = ExportService.export_table_to_csv(
                        table_data=export_data,
                        headers=headers
                    )
                    with open(save_path, 'wb') as f:
                        f.write(csv_data)
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(translator.get_text("common.export_success") if hasattr(translator, 'get_text') else "Export successful"),
                        bgcolor=DesignSystem.SUCCESS,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
            
            file_picker = ft.FilePicker(on_result=on_save_result)
            self.page.overlay.append(file_picker)
            file_picker.save_file(
                dialog_title=translator.get_text("common.export_csv"),
                file_name=f"inventory_counts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["csv"],
            )
        except Exception as ex:
            logger.error(f"Error exporting CSV: {ex}")
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"{translator.get_text('common.error')}: {str(ex)}"),
                bgcolor=DesignSystem.ERROR,
            )
            self.page.snack_bar.open = True
            self.page.update()
    
    def _handle_export_excel(self, e):
        """Handle Excel export"""
        try:
            # Get all counts (apply filters but not pagination)
            self._load_counts_list()
            
            # Apply search filter
            filtered_counts = self.counts_list
            if self.search_query:
                search_lower = self.search_query.lower()
                filtered_counts = [
                    count for count in self.counts_list
                    if search_lower in (count.get("inventory_number", "") or "").lower()
                    or search_lower in (count.get("status", "") or "").lower()
                    or search_lower in (count.get("first_round_checker1_name", "") or "").lower()
                    or search_lower in (count.get("second_round_checker1_name", "") or "").lower()
                ]
            
            export_data = []
            for count in filtered_counts:
                export_data.append({
                    "Inventory Number": count.get("inventory_number", ""),
                    "Planned Date": self._format_date(count.get("planned_date")),
                    "Status": count.get("status", ""),
                    "Round 1 Checker 1": count.get("first_round_checker1_name", ""),
                    "Round 2 Checker 1": count.get("second_round_checker1_name", ""),
                })
            
            def on_save_result(e: ft.FilePickerResultEvent):
                if e.path:
                    from pathlib import Path
                    from datetime import datetime
                    save_path = Path(e.path).with_suffix('.xlsx')
                    excel_data = ExportService.export_to_excel(
                        data=export_data,
                        filename=save_path.name,
                        sheet_name="Inventory Counts"
                    )
                    with open(save_path, 'wb') as f:
                        f.write(excel_data)
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(translator.get_text("common.export_success") if hasattr(translator, 'get_text') else "Export successful"),
                        bgcolor=DesignSystem.SUCCESS,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
            
            file_picker = ft.FilePicker(on_result=on_save_result)
            self.page.overlay.append(file_picker)
            file_picker.save_file(
                dialog_title=translator.get_text("common.export_excel"),
                file_name=f"inventory_counts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["xlsx"],
            )
        except Exception as ex:
            logger.error(f"Error exporting Excel: {ex}")
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"{translator.get_text('common.error')}: {str(ex)}"),
                bgcolor=DesignSystem.ERROR,
            )
            self.page.snack_bar.open = True
            self.page.update()
    
    def _on_create_click(self, e):
        """Handle create button click"""
        logger.info("[INVENTORY_COUNT] ========== _on_create_click START ==========")
        print("[INVENTORY_COUNT] ========== _on_create_click START ==========")
        logger.info(f"[INVENTORY_COUNT] Current view before: {self.current_view}")
        print(f"[INVENTORY_COUNT] Current view before: {self.current_view}")
        
        try:
            # Set current_view first
            self.current_view = "create"
            logger.info(f"[INVENTORY_COUNT] Current view set to: {self.current_view}")
            print(f"[INVENTORY_COUNT] Current view set to: {self.current_view}")
            
            # Use page.go() to trigger route change and re-render (like other screens do)
            if self.page:
                logger.info("[INVENTORY_COUNT] Using page.go() to trigger re-render...")
                print("[INVENTORY_COUNT] Using page.go() to trigger re-render...")
                
                # Use page.go() which will trigger route change and render()
                self.page.go("/inventory_count/create")
                logger.info("[INVENTORY_COUNT] page.go() called with /inventory_count/create")
                print("[INVENTORY_COUNT] page.go() called with /inventory_count/create")
            else:
                logger.error("[INVENTORY_COUNT] page is None, cannot navigate!")
                print("[INVENTORY_COUNT] page is None, cannot navigate!")
                
        except Exception as ex:
            logger.error(f"[INVENTORY_COUNT] Error in _on_create_click: {ex}", exc_info=True)
            print(f"[INVENTORY_COUNT] ERROR: {ex}")
            import traceback
            traceback.print_exc()
            if self.page:
                try:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"Hiba / Error: {str(ex)}"),
                        bgcolor=DesignSystem.ERROR,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
                except Exception as snack_ex:
                    logger.error(f"[INVENTORY_COUNT] Could not show error snackbar: {snack_ex}")
        
        logger.info("[INVENTORY_COUNT] ========== _on_create_click END ==========")
        print("[INVENTORY_COUNT] ========== _on_create_click END ==========")
    
    def _on_back_to_list(self, e):
        """Handle back to list"""
        self.current_view = "list"
        self.selected_count_id = None
        self.count_detail = None
        if self.content_container:
            self.content_container.content = self._build_list_view()
            self.page.update()
    
    def _on_view_details(self, e, count_id: int):
        """Handle view details"""
        self.current_view = "detail"
        self._load_count_detail(count_id)
        if self.content_container:
            self.content_container.content = self._build_detail_view()
            self.page.update()
    
    def _on_start_count(self, e):
        """Handle start count"""
        try:
            response = requests.post(
                f"{self._get_api_url()}/{self.selected_count_id}/start",
                headers=self._get_auth_headers(),
            )
            if response.status_code == 200:
                self._load_count_detail(self.selected_count_id)
                self.page.snack_bar = ft.SnackBar(
                    ft.Text("Leltár elindítva / Count started"),
                    bgcolor=DesignSystem.SUCCESS,
                )
                self.page.snack_bar.open = True
                if self.content_container:
                    self.content_container.content = self._build_detail_view()
                self.page.update()
            else:
                self.page.snack_bar = ft.SnackBar(
                    ft.Text(f"Hiba / Error: {response.status_code}"),
                    bgcolor=DesignSystem.ERROR,
                )
                self.page.snack_bar.open = True
                self.page.update()
        except Exception as ex:
            logger.error(f"Error starting count: {ex}", exc_info=True)
            self.page.snack_bar = ft.SnackBar(
                ft.Text(f"Hiba / Error: {str(ex)}"),
                bgcolor=DesignSystem.ERROR,
            )
            self.page.snack_bar.open = True
            self.page.update()
    
    def _on_complete_round(self, e, round_number: int):
        """Handle complete round"""
        try:
            endpoint = "complete-first-round" if round_number == 1 else "complete-second-round"
            response = requests.post(
                f"{self._get_api_url()}/{self.selected_count_id}/{endpoint}",
                headers=self._get_auth_headers(),
            )
            if response.status_code == 200:
                self._load_count_detail(self.selected_count_id)
                self.page.snack_bar = ft.SnackBar(
                    ft.Text(f"{round_number}. kör befejezve / Round {round_number} completed"),
                    bgcolor=DesignSystem.SUCCESS,
                )
                self.page.snack_bar.open = True
                if self.content_container:
                    self.content_container.content = self._build_detail_view()
                self.page.update()
            else:
                self.page.snack_bar = ft.SnackBar(
                    ft.Text(f"Hiba / Error: {response.status_code}"),
                    bgcolor=DesignSystem.ERROR,
                )
                self.page.snack_bar.open = True
                self.page.update()
        except Exception as ex:
            logger.error(f"Error completing round: {ex}", exc_info=True)
            self.page.snack_bar = ft.SnackBar(
                ft.Text(f"Hiba / Error: {str(ex)}"),
                bgcolor=DesignSystem.ERROR,
            )
            self.page.snack_bar.open = True
            self.page.update()
    
    def _on_approve_count(self, e):
        """Handle approve count"""
        try:
            response = requests.post(
                f"{self._get_api_url()}/{self.selected_count_id}/approve",
                headers=self._get_auth_headers(),
            )
            if response.status_code == 200:
                self._load_count_detail(self.selected_count_id)
                self.page.snack_bar = ft.SnackBar(
                    ft.Text("Leltár jóváhagyva / Count approved"),
                    bgcolor=DesignSystem.SUCCESS,
                )
                self.page.snack_bar.open = True
                if self.content_container:
                    self.content_container.content = self._build_detail_view()
                self.page.update()
            else:
                self.page.snack_bar = ft.SnackBar(
                    ft.Text(f"Hiba / Error: {response.status_code}"),
                    bgcolor=DesignSystem.ERROR,
                )
                self.page.snack_bar.open = True
                self.page.update()
        except Exception as ex:
            logger.error(f"Error approving count: {ex}", exc_info=True)
            self.page.snack_bar = ft.SnackBar(
                ft.Text(f"Hiba / Error: {str(ex)}"),
                bgcolor=DesignSystem.ERROR,
            )
            self.page.snack_bar.open = True
            self.page.update()
    
    def _on_approve_correction(self, e, correction_id: int):
        """Handle approve correction"""
        try:
            response = requests.post(
                f"{self._get_api_url()}/{self.selected_count_id}/corrections/{correction_id}/approve",
                headers=self._get_auth_headers(),
            )
            if response.status_code == 200:
                self._load_count_detail(self.selected_count_id)
                self.page.snack_bar = ft.SnackBar(
                    ft.Text("Korrekció jóváhagyva / Correction approved"),
                    bgcolor=DesignSystem.SUCCESS,
                )
                self.page.snack_bar.open = True
                if self.content_container:
                    self.content_container.content = self._build_detail_view()
                self.page.update()
            else:
                self.page.snack_bar = ft.SnackBar(
                    ft.Text(f"Hiba / Error: {response.status_code}"),
                    bgcolor=DesignSystem.ERROR,
                )
                self.page.snack_bar.open = True
                self.page.update()
        except Exception as ex:
            logger.error(f"Error approving correction: {ex}", exc_info=True)
            self.page.snack_bar = ft.SnackBar(
                ft.Text(f"Hiba / Error: {str(ex)}"),
                bgcolor=DesignSystem.ERROR,
            )
            self.page.snack_bar.open = True
            self.page.update()
    
    def _on_reject_correction(self, e, correction_id: int):
        """Handle reject correction"""
        try:
            response = requests.post(
                f"{self._get_api_url()}/{self.selected_count_id}/corrections/{correction_id}/reject",
                headers=self._get_auth_headers(),
            )
            if response.status_code == 200:
                self._load_count_detail(self.selected_count_id)
                self.page.snack_bar = ft.SnackBar(
                    ft.Text("Korrekció elutasítva / Correction rejected"),
                    bgcolor=DesignSystem.WARNING,
                )
                self.page.snack_bar.open = True
                if self.content_container:
                    self.content_container.content = self._build_detail_view()
                self.page.update()
            else:
                self.page.snack_bar = ft.SnackBar(
                    ft.Text(f"Hiba / Error: {response.status_code}"),
                    bgcolor=DesignSystem.ERROR,
                )
                self.page.snack_bar.open = True
                self.page.update()
        except Exception as ex:
            logger.error(f"Error rejecting correction: {ex}", exc_info=True)
            self.page.snack_bar = ft.SnackBar(
                ft.Text(f"Hiba / Error: {str(ex)}"),
                bgcolor=DesignSystem.ERROR,
            )
            self.page.snack_bar.open = True
            self.page.update()
    
    def _on_generate_document(self, e, document_type: str):
        """Handle generate document"""
        try:
            response = requests.post(
                f"{self._get_api_url()}/{self.selected_count_id}/generate-document",
                params={"document_type": document_type},
                headers=self._get_auth_headers(),
            )
            if response.status_code == 200:
                result = response.json()
                self._load_count_detail(self.selected_count_id)
                self.page.snack_bar = ft.SnackBar(
                    ft.Text("Dokumentum generálva / Document generated"),
                    bgcolor=DesignSystem.SUCCESS,
                )
                self.page.snack_bar.open = True
                if self.content_container:
                    self.content_container.content = self._build_detail_view()
                self.page.update()
            else:
                self.page.snack_bar = ft.SnackBar(
                    ft.Text(f"Hiba / Error: {response.status_code}"),
                    bgcolor=DesignSystem.ERROR,
                )
                self.page.snack_bar.open = True
                self.page.update()
        except Exception as ex:
            logger.error(f"Error generating document: {ex}", exc_info=True)
            self.page.snack_bar = ft.SnackBar(
                ft.Text(f"Hiba / Error: {str(ex)}"),
                bgcolor=DesignSystem.ERROR,
            )
            self.page.snack_bar.open = True
            self.page.update()
    
    def _on_download_document(self, e, file_path: str):
        """Handle download document"""
        # Open file in default application
        import os
        if os.path.exists(file_path):
            os.startfile(file_path)
        else:
            self.page.snack_bar = ft.SnackBar(
                ft.Text("Fájl nem található / File not found"),
                bgcolor=DesignSystem.ERROR,
            )
            self.page.snack_bar.open = True
            self.page.update()

