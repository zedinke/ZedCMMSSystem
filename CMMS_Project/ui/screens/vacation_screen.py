"""
Vacation Management Screen
Handles vacation requests, calendar view, and approval workflow
"""

import flet as ft
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from calendar import monthcalendar, monthrange

from services.vacation_service import (
    create_vacation_request, approve_vacation_request, reject_vacation_request,
    get_vacation_requests, get_vacation_calendar, get_user_vacation_summary,
    VacationServiceError
)
from services.context_service import get_current_user_id, get_user, get_app_context
from database.session_manager import SessionLocal
from database.models import User, VacationRequest, Role
from localization.translator import translator
from services import pdf_service
from ui.components.modern_components import (
    create_modern_card, create_modern_button, create_modern_text_field,
    create_modern_dropdown, create_modern_date_field,
    create_vibrant_badge,
    create_empty_state_card,
    DesignSystem as DS,
    DesignSystem,
)
from ui.components.modern_card import (
    create_tailwind_card,
    create_info_card,
)
from ui.components.pagination import PaginationController, create_pagination_controls, create_items_per_page_selector
from ui.components.selectable_list import SelectableList
from ui.components.batch_actions_bar import create_batch_actions_bar
from services.export_service import ExportService
from services.autosave_service import get_autosave_service

import logging

logger = logging.getLogger(__name__)


class VacationScreen:
    """Vacation management screen"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.current_user_id = get_current_user_id()
        self.current_year = datetime.now().year
        self.view_mode = "list"  # "list" or "calendar"
        self.selected_status = None  # None = all, "pending", "approved", "rejected"
        self.main_column = None  # Store reference to main column for direct updates
        self.search_query = ""  # Search query for filtering requests
        self.selected_request_ids = set()  # Selected request IDs for batch operations
        self.items_per_page = 20  # Default items per page
        self.pagination_controller = None  # Will be initialized in view
    
    def _create_day_details_handler(self, date, status, users):
        """Create a handler function for day details click to avoid lambda closure issues"""
        def handle_click(e):
            self._show_day_details(date, status, users)
        return handle_click
        
    def _refresh_view(self):
        """Force immediate refresh by rebuilding the main column content directly (like documentation_screen)"""
        if self.main_column is not None:
            # Rebuild the content
            from config.roles import ROLE_MANAGER, ROLE_DEVELOPER, ROLE_MAINTENANCE_SUPERVISOR
            can_approve = False
            ctx = get_app_context()
            if ctx.role:
                role_name = ctx.role
                can_approve = role_name in [ROLE_MANAGER, ROLE_DEVELOPER, ROLE_MAINTENANCE_SUPERVISOR]
            
            # Rebuild header
            header = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Text(
                            translator.get_text("vacation.title"),
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color=DS.PRIMARY,
                        ),
                        ft.Container(expand=True),
                        create_modern_button(
                            text=translator.get_text("vacation.request_vacation"),
                            icon=ft.icons.ADD,
                            on_click=self._open_request_dialog,
                            bgcolor=DS.SUCCESS,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                padding=ft.padding.only(bottom=20),
            )
            
            # Rebuild summary - get fresh user_id from context
            current_user_id = get_current_user_id()
            summary = get_user_vacation_summary(current_user_id, self.current_year) if current_user_id else None
            summary_row = None
            if summary:
                summary_row = ft.Row(
                    controls=[
                        create_modern_card(
                            content=ft.Column(
                                controls=[
                                    ft.Text(
                                        translator.get_text("vacation.days_per_year"),
                                        size=12,
                                        color=DS.TEXT_SECONDARY,
                                    ),
                                    ft.Text(
                                        str(summary["days_per_year"]),
                                        size=24,
                                        weight=ft.FontWeight.BOLD,
                                        color=DS.PRIMARY,
                                    ),
                                ],
                                spacing=5,
                            ),
                            padding=20,
                        ),
                        create_modern_card(
                            content=ft.Column(
                                controls=[
                                    ft.Text(
                                        translator.get_text("vacation.days_used"),
                                        size=12,
                                        color=DS.TEXT_SECONDARY,
                                    ),
                                    ft.Text(
                                        str(summary["days_used"]),
                                        size=24,
                                        weight=ft.FontWeight.BOLD,
                                        color=DS.WARNING,
                                    ),
                                ],
                                spacing=5,
                            ),
                            padding=20,
                        ),
                        create_modern_card(
                            content=ft.Column(
                                controls=[
                                    ft.Text(
                                        translator.get_text("vacation.days_remaining"),
                                        size=12,
                                        color=DS.TEXT_SECONDARY,
                                    ),
                                    ft.Text(
                                        str(summary["days_remaining"]),
                                        size=24,
                                        weight=ft.FontWeight.BOLD,
                                        color=DS.SUCCESS,
                                    ),
                                ],
                                spacing=5,
                            ),
                            padding=20,
                        ),
                    ],
                    spacing=15,
                )
            
            # Create wrapper functions to avoid lambda closure issues in PyInstaller
            def handle_switch_to_list(e):
                self._switch_view("list")
            
            def handle_switch_to_calendar(e):
                self._switch_view("calendar")
            
            # Rebuild view switcher
            view_switcher = ft.Row(
                controls=[
                    create_modern_button(
                        text=translator.get_text("vacation.my_requests"),
                        icon=ft.icons.LIST,
                        on_click=handle_switch_to_list,
                        bgcolor=DS.PRIMARY if self.view_mode == "list" else DS.BG_SECONDARY,
                    ),
                    create_modern_button(
                        text=translator.get_text("vacation.calendar"),
                        icon=ft.icons.CALENDAR_MONTH,
                        on_click=handle_switch_to_calendar,
                        bgcolor="#FF9800" if self.view_mode == "calendar" else "#FFB74D",  # Orange colors
                    ),
                ],
                spacing=10,
            )
            
            # Rebuild filters
            filters = None
            if self.view_mode == "list":
                filters = ft.Row(
                    controls=[
                        create_modern_dropdown(
                            label=translator.get_text("vacation.status.label"),
                            options=[
                                ft.dropdown.Option(key="", text=translator.get_text("vacation.status.all")),
                                ft.dropdown.Option(key="pending", text=translator.get_text("vacation.status.pending")),
                                ft.dropdown.Option(key="approved", text=translator.get_text("vacation.status.approved")),
                                ft.dropdown.Option(key="rejected", text=translator.get_text("vacation.status.rejected")),
                            ],
                            value="" if (self.selected_status is None or self.selected_status == "") else self.selected_status,
                            on_change=self._on_status_filter_change,
                            width=200,
                        ),
                    ],
                    spacing=10,
                )
            
            # Rebuild content - this is where the filtered requests are built
            content = self._build_content(can_approve)
            
            # Rebuild main controls
            main_controls = [header]
            if summary_row:
                main_controls.append(summary_row)
            main_controls.append(view_switcher)
            if filters:
                main_controls.append(filters)
            main_controls.append(content)
            
            # Directly update the stored column reference (like documentation_screen does with content_container)
            # Clear and rebuild controls to ensure proper refresh
            self.main_column.controls.clear()
            self.main_column.controls.extend(main_controls)
            self.page.update()
        else:
            # Fallback: rebuild entire view if reference not available
            try:
                self.page.route = "/vacation_refresh"
                self.page.update()
                self.page.route = "/vacation"
                self.page.update()
            except Exception:
                self.page.update()
        
    def view(self, page: ft.Page = None) -> ft.Control:
        """Build the vacation screen view"""
        # Use provided page or stored page
        if page:
            self.page = page
        # Check if user can approve (Manager, Developer, or Maintenance Supervisor)
        # Use context role to avoid DetachedInstanceError
        from config.roles import ROLE_MANAGER, ROLE_DEVELOPER, ROLE_MAINTENANCE_SUPERVISOR
        can_approve = False
        ctx = get_app_context()
        if ctx.role:
            role_name = ctx.role
            can_approve = role_name in [ROLE_MANAGER, ROLE_DEVELOPER, ROLE_MAINTENANCE_SUPERVISOR]
        
        # Get vacation summary
        summary = get_user_vacation_summary(self.current_user_id, self.current_year) if self.current_user_id else None
        
        # Build header
        header = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text(
                        translator.get_text("vacation.title"),
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=DS.PRIMARY,
                    ),
                    ft.Container(expand=True),
                    create_modern_button(
                        text=translator.get_text("vacation.request_vacation"),
                        icon=ft.icons.ADD,
                        on_click=self._open_request_dialog,
                        bgcolor=DS.SUCCESS,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.padding.only(bottom=20),
        )
        
        # Summary cards
        summary_row = None
        if summary:
            summary_row = ft.Row(
                controls=[
                    create_modern_card(
                        content=ft.Column(
                            controls=[
                                ft.Text(
                                    translator.get_text("vacation.days_per_year"),
                                    size=12,
                                    color=DS.TEXT_SECONDARY,
                                ),
                                ft.Text(
                                    str(summary["days_per_year"]),
                                    size=24,
                                    weight=ft.FontWeight.BOLD,
                                    color=DS.PRIMARY,
                                ),
                            ],
                            spacing=5,
                        ),
                        padding=20,
                    ),
                    create_modern_card(
                        content=ft.Column(
                            controls=[
                                ft.Text(
                                    translator.get_text("vacation.days_used"),
                                    size=12,
                                    color=DS.TEXT_SECONDARY,
                                ),
                                ft.Text(
                                    str(summary["days_used"]),
                                    size=24,
                                    weight=ft.FontWeight.BOLD,
                                    color=DS.WARNING,
                                ),
                            ],
                            spacing=5,
                        ),
                        padding=20,
                    ),
                    create_modern_card(
                        content=ft.Column(
                            controls=[
                                ft.Text(
                                    translator.get_text("vacation.days_remaining"),
                                    size=12,
                                    color=DS.TEXT_SECONDARY,
                                ),
                                ft.Text(
                                    str(summary["days_remaining"]),
                                    size=24,
                                    weight=ft.FontWeight.BOLD,
                                    color=DS.SUCCESS,
                                ),
                            ],
                            spacing=5,
                        ),
                        padding=20,
                    ),
                ],
                spacing=15,
            )
        
        # Create wrapper functions to avoid lambda closure issues in PyInstaller
        def handle_switch_to_list(e):
            self._switch_view("list")
        
        def handle_switch_to_calendar(e):
            self._switch_view("calendar")
        
        # View mode switcher
        view_switcher = ft.Row(
            controls=[
                create_modern_button(
                    text=translator.get_text("vacation.my_requests"),
                    icon=ft.icons.LIST,
                    on_click=handle_switch_to_list,
                    bgcolor=DS.PRIMARY if self.view_mode == "list" else DS.BG_SECONDARY,
                ),
                create_modern_button(
                    text=translator.get_text("vacation.calendar"),
                    icon=ft.icons.CALENDAR_MONTH,
                    on_click=handle_switch_to_calendar,
                    bgcolor="#FF9800" if self.view_mode == "calendar" else "#FFB74D",  # Orange colors
                ),
            ],
            spacing=10,
        )
        
        # Filters (for list view)
        filters = None
        if self.view_mode == "list":
            # Search field
            search_field = create_modern_text_field(
                label=translator.get_text("common.search"),
                hint_text=translator.get_text("common.search_hint") if hasattr(translator, 'get_text') else "Keresés...",
                value=self.search_query,
                on_change=self._on_search_change,
                width=300,
            )
            
            # Year filter
            year_options = []
            current_year = datetime.now().year
            for y in range(current_year - 2, current_year + 3):
                year_options.append(ft.dropdown.Option(key=str(y), text=str(y)))
            
            year_filter = create_modern_dropdown(
                label=translator.get_text("common.year") if hasattr(translator, 'get_text') else "Év",
                options=year_options,
                value=str(self.current_year),
                on_change=self._on_year_filter_change,
                width=120,
            )
            
            # Status filter
            status_filter = create_modern_dropdown(
                label=translator.get_text("vacation.status.label"),
                options=[
                    ft.dropdown.Option(key="", text=translator.get_text("vacation.status.all")),
                    ft.dropdown.Option(key="pending", text=translator.get_text("vacation.status.pending")),
                    ft.dropdown.Option(key="approved", text=translator.get_text("vacation.status.approved")),
                    ft.dropdown.Option(key="rejected", text=translator.get_text("vacation.status.rejected")),
                ],
                value="" if (self.selected_status is None or self.selected_status == "") else self.selected_status,
                on_change=self._on_status_filter_change,
                width=200,
            )
            
            # Export button
            export_button = create_modern_button(
                text=translator.get_text("common.buttons.export"),
                icon=ft.icons.DOWNLOAD,
                on_click=self._on_export_click,
                bgcolor=DS.INFO,
                width=150,
            )
            
            filters = ft.Row(
                controls=[
                    search_field,
                    year_filter,
                    status_filter,
                    export_button,
                ],
                spacing=10,
            )
        
        # Content area
        content = self._build_content(can_approve)
        
        # Build main column - filter out None values
        main_controls = [header]
        if summary_row:
            main_controls.append(summary_row)
        main_controls.append(view_switcher)
        if filters:
            main_controls.append(filters)
        main_controls.append(content)
        
        # Create main column and store reference for direct updates (like documentation_screen)
        self.main_column = ft.Column(
            controls=main_controls,
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        
        return ft.Container(
            content=self.main_column,
            padding=20,
            expand=True,
        )
    
    def _build_content(self, can_approve: bool) -> ft.Control:
        """Build content based on view mode"""
        if self.view_mode == "calendar":
            return self._build_calendar_view()
        else:
            return self._build_list_view(can_approve)
    
    def _build_list_view(self, can_approve: bool) -> ft.Control:
        """Build list view of vacation requests with card-based layout, pagination, search, and batch operations"""
        # Get fresh user_id from context
        current_user_id = get_current_user_id()
        # If user can approve, show all users' requests; otherwise show only own requests
        filter_user_id = None if can_approve else current_user_id
        
        # When filter is set to "all" (selected_status is None or empty string), show all statuses
        # IMPORTANT: Pass None to get_vacation_requests to get all statuses (not empty string!)
        # This ensures "All" option works the same as initial load (when selected_status is None)
        # Normalize selected_status: convert empty string to None
        normalized_status = None if (self.selected_status is None or self.selected_status == "") else self.selected_status
        
        # Get all requests with normalized_status (None = all statuses, "pending"/"approved"/"rejected" = specific status)
        all_requests = get_vacation_requests(
            user_id=filter_user_id,
            status=normalized_status,  # None means no status filter = all statuses
            year=self.current_year
        )
        
        # Apply search filter
        if self.search_query:
            search_lower = self.search_query.lower()
            filtered_requests = []
            for req in all_requests:
                user = get_user(req.user_id)
                user_name = (user.full_name or user.username or "").lower() if user else ""
                reason = (req.reason or "").lower()
                start_date_str = (req.start_date.date() if isinstance(req.start_date, datetime) else req.start_date).strftime("%Y-%m-%d")
                end_date_str = (req.end_date.date() if isinstance(req.end_date, datetime) else req.end_date).strftime("%Y-%m-%d")
                
                if (search_lower in user_name or 
                    search_lower in reason or 
                    search_lower in start_date_str or 
                    search_lower in end_date_str):
                    filtered_requests.append(req)
            all_requests = filtered_requests
        
        # Initialize pagination controller if not exists or total changed
        total_requests = len(all_requests)
        if self.pagination_controller is None or self.pagination_controller.total_items != total_requests:
            self.pagination_controller = PaginationController(
                total_items=total_requests,
                items_per_page=self.items_per_page,
                on_page_change=lambda: self._refresh_view(),
            )
        else:
            self.pagination_controller.total_items = total_requests
        
        # Get paginated requests
        start_idx = self.pagination_controller.start_index
        end_idx = self.pagination_controller.end_index
        requests = all_requests[start_idx:end_idx]
        
        if not requests and total_requests == 0:
            return create_empty_state_card(
                icon=ft.Icons.CALENDAR_MONTH,
                title=translator.get_text("vacation.no_requests"),
                icon_color=DS.GRAY_400,
            )
        
        # Batch actions bar
        batch_actions_bar = None
        if can_approve and self.selected_request_ids:
            def on_batch_approve():
                self._batch_approve_requests()
            
            def on_batch_reject():
                self._batch_reject_requests()
            
            batch_actions_bar = create_batch_actions_bar(
                selected_count=len(self.selected_request_ids),
                actions=[
                    {
                        "text": translator.get_text("vacation.approve"),
                        "icon": ft.icons.CHECK,
                        "on_click": on_batch_approve,
                        "bgcolor": DS.SUCCESS,
                    },
                    {
                        "text": translator.get_text("vacation.reject"),
                        "icon": ft.icons.CLOSE,
                        "on_click": on_batch_reject,
                        "bgcolor": DS.ERROR,
                    },
                ],
            )
        
        # Build cards grid
        cards_grid = ft.GridView(
            runs_count=3,  # 3 columns
            max_extent=400,
            spacing=DesignSystem.SPACING_4,
            run_spacing=DesignSystem.SPACING_4,
            child_aspect_ratio=1.2,
        )
        
        for req in requests:
            # Get user info
            user = get_user(req.user_id)
            user_name = user.full_name if user and user.full_name else (user.username if user else "-")
            
            # Format dates
            start_date = req.start_date.date() if isinstance(req.start_date, datetime) else req.start_date
            end_date = req.end_date.date() if isinstance(req.end_date, datetime) else req.end_date
            
            # Status color and variant
            status_config = {
                "pending": (DS.WARNING, "amber"),
                "approved": (DS.SUCCESS, "emerald"),
                "rejected": (DS.ERROR, "red"),
            }.get(req.status, (DS.TEXT_SECONDARY, None))
            status_color, status_variant = status_config
            
            # Selection checkbox (only for approvers and pending requests)
            is_selected = req.id in self.selected_request_ids
            checkbox = None
            if can_approve and req.status == "pending":
                checkbox = ft.Checkbox(
                    value=is_selected,
                    on_change=lambda e, r=req: self._on_request_selection_change(r.id, e),
                )
            
            # Build card content
            card_content_items = [
                ft.Row([
                    checkbox if checkbox else ft.Container(width=0),
                    ft.Container(
                        content=ft.Icon(ft.Icons.CALENDAR_MONTH, size=24, color=status_color),
                        padding=ft.padding.all(DesignSystem.SPACING_2),
                        bgcolor=f"{status_color}15",
                        border_radius=DesignSystem.RADIUS_LG,
                    ),
                    ft.Column([
                        ft.Text(
                            user_name,
                            size=18,
                            weight=ft.FontWeight.W_600,
                            color=DesignSystem.TEXT_PRIMARY,
                        ),
                        create_vibrant_badge(
                            text=translator.get_text(f"vacation.status.{req.status}"),
                            variant=status_variant or "blue",
                            size=12,
                        ),
                    ], spacing=DesignSystem.SPACING_1, tight=True, expand=True),
                ], spacing=DesignSystem.SPACING_3),
                ft.Container(height=DesignSystem.SPACING_3),
                ft.Row([
                    ft.Column([
                        ft.Text(
                            translator.get_text("vacation.start_date"),
                            size=11,
                            color=DesignSystem.TEXT_SECONDARY,
                        ),
                        ft.Text(
                            start_date.strftime("%Y-%m-%d"),
                            size=14,
                            weight=ft.FontWeight.W_500,
                            color=DesignSystem.TEXT_PRIMARY,
                        ),
                    ], spacing=2, tight=True, expand=True),
                    ft.Column([
                        ft.Text(
                            translator.get_text("vacation.end_date"),
                            size=11,
                            color=DesignSystem.TEXT_SECONDARY,
                        ),
                        ft.Text(
                            end_date.strftime("%Y-%m-%d"),
                            size=14,
                            weight=ft.FontWeight.W_500,
                            color=DesignSystem.TEXT_PRIMARY,
                        ),
                    ], spacing=2, tight=True, expand=True),
                ], spacing=DesignSystem.SPACING_4),
                ft.Container(height=DesignSystem.SPACING_2),
                ft.Row([
                    ft.Text(
                        translator.get_text("vacation.days_count"),
                        size=12,
                        color=DesignSystem.TEXT_SECONDARY,
                    ),
                    ft.Container(width=DesignSystem.SPACING_2),
                    ft.Text(
                        f"{req.days_count or 0} {translator.get_text('vacation.days') if hasattr(translator, 'get_text') else 'nap'}",
                        size=14,
                        weight=ft.FontWeight.W_600,
                        color=DesignSystem.TEXT_PRIMARY,
                    ),
                ], spacing=DesignSystem.SPACING_2),
            ]
            
            # Add reason if available
            if req.reason:
                card_content_items.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Text(
                                translator.get_text("vacation.reason"),
                                size=11,
                                color=DesignSystem.TEXT_SECONDARY,
                            ),
                            ft.Text(
                                req.reason[:100] + "..." if len(req.reason) > 100 else req.reason,
                                size=12,
                                color=DesignSystem.TEXT_SECONDARY,
                                max_lines=2,
                            ),
                        ], spacing=2, tight=True),
                        padding=ft.padding.all(DesignSystem.SPACING_2),
                        bgcolor=DesignSystem.GRAY_50,
                        border_radius=DesignSystem.RADIUS_MD,
                    )
                )
            
            # Create wrapper functions to avoid lambda closure issues in PyInstaller
            def create_request_handlers(request):
                def handle_approve(e):
                    self._approve_request(request.id)
                
                def handle_reject(e):
                    self._open_reject_dialog(request)
                
                def handle_download(e):
                    self._download_vacation_document(request.id)
                
                return handle_approve, handle_reject, handle_download
            
            handle_approve, handle_reject, handle_download = create_request_handlers(req)
            
            # Action buttons
            action_buttons = []
            if can_approve and req.status == "pending":
                action_buttons.append(
                    create_modern_button(
                        text=translator.get_text("vacation.approve"),
                        icon=ft.icons.CHECK,
                        on_click=handle_approve,
                        bgcolor=DS.SUCCESS,
                        width=120,
                    )
                )
                action_buttons.append(
                    create_modern_button(
                        text=translator.get_text("vacation.reject"),
                        icon=ft.icons.CLOSE,
                        on_click=handle_reject,
                        bgcolor=DS.ERROR,
                        width=120,
                    )
                )
            # Add download button for approved requests
            if req.status == "approved":
                action_buttons.append(
                    create_modern_button(
                        text=translator.get_text("common.buttons.download"),
                        icon=ft.icons.DOWNLOAD,
                        on_click=handle_download,
                        bgcolor=DS.INFO,
                        width=140,
                    )
                )
            
            if action_buttons:
                card_content_items.append(
                    ft.Container(
                        content=ft.Row(action_buttons, spacing=DesignSystem.SPACING_2),
                        padding=ft.padding.only(top=DesignSystem.SPACING_3),
                    )
                )
            
            card_content = ft.Column(card_content_items, spacing=DesignSystem.SPACING_2)
            card_content.controls = [c for c in card_content.controls if c is not None]
            
            card = create_tailwind_card(
                content=card_content,
                padding=DesignSystem.SPACING_4,
                elevation=1,
                accent_color=status_color,
            )
            cards_grid.controls.append(card)
        
        # Build pagination controls
        pagination_controls = create_pagination_controls(
            controller=self.pagination_controller,
            on_page_change=lambda: self._refresh_view(),
        )
        
        items_per_page_selector = create_items_per_page_selector(
            current_value=self.items_per_page,
            on_change=self._on_items_per_page_change,
        )
        
        # Build main content column
        content_column = ft.Column(
            controls=[
                batch_actions_bar if batch_actions_bar else ft.Container(height=0),
                cards_grid,
                ft.Row(
                    controls=[
                        items_per_page_selector,
                        ft.Container(expand=True),
                        pagination_controls,
                    ],
                    spacing=10,
                ),
            ],
            spacing=10,
        )
        
        return ft.Container(
            content=content_column,
            expand=True,
        )
    
    def _build_calendar_view(self) -> ft.Control:
        """Build calendar view with colored days"""
        # Get calendar data
        calendar_data = get_vacation_calendar(self.current_year)
        
        # Year navigation
        year_nav = ft.Row(
            controls=[
                # Create wrapper functions to avoid lambda closure issues in PyInstaller
                def handle_prev_year(e):
                    self._change_year(-1)
                
                def handle_next_year(e):
                    self._change_year(1)
                
                create_modern_button(
                    text="◀",
                    icon=None,
                    on_click=handle_prev_year,
                    bgcolor=DS.PRIMARY,
                    width=50,
                ),
                ft.Text(
                    str(self.current_year),
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=DS.PRIMARY,
                ),
                create_modern_button(
                    text="▶",
                    icon=None,
                    on_click=handle_next_year,
                    bgcolor=DS.PRIMARY,
                    width=50,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
        )
        
        # Build calendar grid (12 months)
        months_grid = ft.GridView(
            runs_count=3,  # 3 columns
            max_extent=300,
            spacing=20,
            run_spacing=20,
            child_aspect_ratio=1.2,
        )
        
        # Month names
        month_names = [
            "Január", "Február", "Március", "Április", "Május", "Június",
            "Július", "Augusztus", "Szeptember", "Október", "November", "December"
        ] if translator.get_current_language() == "hu" else [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        
        for month in range(1, 13):
            month_card = self._build_month_calendar(month, month_names[month - 1], calendar_data)
            months_grid.controls.append(month_card)
        
        # Legend
        legend = ft.Row(
            controls=[
                ft.Container(
                    content=ft.Row([
                        ft.Container(width=20, height=20, bgcolor="#E5E7EB", border_radius=4),
                        ft.Text("Nincs szabadság / No vacation", size=12),
                    ], spacing=10),
                ),
                ft.Container(
                    content=ft.Row([
                        ft.Container(width=20, height=20, bgcolor=DS.SUCCESS, border_radius=4),
                        ft.Text(translator.get_text("vacation.status.approved"), size=12),
                    ], spacing=10),
                ),
                ft.Container(
                    content=ft.Row([
                        ft.Container(width=20, height=20, bgcolor=DS.WARNING, border_radius=4),  # Dark orange
                        ft.Text(translator.get_text("vacation.status.pending"), size=12),
                    ], spacing=10),
                ),
            ],
            spacing=30,
            alignment=ft.MainAxisAlignment.CENTER,
        )
        
        return ft.Column(
            controls=[
                year_nav,
                ft.Container(height=20),
                legend,
                ft.Container(height=20),
                months_grid,
            ],
            spacing=10,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
    
    def _build_month_calendar(self, month: int, month_name: str, calendar_data: dict) -> ft.Control:
        """Build a single month calendar"""
        
        # Get first day of month
        first_day = date(self.current_year, month, 1)
        last_day = date(self.current_year, month, monthrange(self.current_year, month)[1])
        
        # Get calendar grid for the month
        cal = monthcalendar(self.current_year, month)
        
        # Day names
        day_names = ["H", "K", "Sz", "Cs", "P", "Sz", "V"] if translator.get_current_language() == "hu" else ["M", "T", "W", "T", "F", "S", "S"]
        
        # Build day cells
        day_cells = []
        
        # Header row
        header_row = ft.Row(
            controls=[ft.Container(
                content=ft.Text(name, size=10, weight=ft.FontWeight.BOLD, color=DS.TEXT_SECONDARY),
                width=30,
                alignment=ft.alignment.center,
            ) for name in day_names],
            spacing=2,
        )
        day_cells.append(header_row)
        
        # Calendar rows
        for week in cal:
            week_row = ft.Row(
                controls=[],
                spacing=2,
            )
            
            for day in week:
                if day == 0:
                    # Empty cell
                    week_row.controls.append(ft.Container(width=30, height=30))
                else:
                    # Day cell
                    current_date = date(self.current_year, month, day)
                    date_str = current_date.isoformat()
                    
                    # Get status from calendar data
                    day_info = calendar_data.get(date_str, {"status": "free", "users": []})
                    status = day_info["status"]
                    
                    # Color based on status
                    bg_color = "#E5E7EB"  # Gray - free
                    if status == "approved":
                        bg_color = DS.SUCCESS  # Green
                    elif status == "pending":
                        bg_color = DS.WARNING  # Dark orange - pending approval
                    
                    # Build day cell
                    # Create handler to avoid lambda closure issues in PyInstaller
                    day_handler = self._create_day_details_handler(current_date, status, day_info.get("users", []))
                    day_cell = ft.Container(
                        content=ft.Text(
                            str(day),
                            size=10,
                            color=DS.TEXT_PRIMARY if status == "free" else "#FFFFFF",
                        ),
                        width=30,
                        height=30,
                        bgcolor=bg_color,
                        border_radius=4,
                        alignment=ft.alignment.center,
                        on_click=day_handler,
                    )
                    week_row.controls.append(day_cell)
            
            day_cells.append(week_row)
        
        # Build month card
        return create_modern_card(
            content=ft.Column(
                controls=[
                    ft.Text(
                        month_name,
                        size=14,
                        weight=ft.FontWeight.BOLD,
                        color=DS.PRIMARY,
                    ),
                    ft.Container(height=10),
                    ft.Column(controls=day_cells, spacing=2),
                ],
                spacing=5,
            ),
            padding=15,
        )
    
    def _change_year(self, delta: int):
        """Change the displayed year"""
        self.current_year += delta
        # Force immediate refresh
        self._refresh_view()
    
    def _show_day_details(self, day: date, status: str, user_ids: List[int]):
        """Show details for a specific day"""
        # Get vacation requests for this day
        requests = get_vacation_requests(
            user_id=None,
            status=None,
            year=self.current_year
        )
        
        # Filter requests for this day
        day_requests = []
        for req in requests:
            start = req.start_date.date() if isinstance(req.start_date, datetime) else req.start_date
            end = req.end_date.date() if isinstance(req.end_date, datetime) else req.end_date
            if start <= day <= end:
                day_requests.append(req)
        
        if not day_requests:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"{day.strftime('%Y-%m-%d')}: {translator.get_text('vacation.no_requests')}"),
                bgcolor=DS.INFO,
            )
            self.page.snack_bar.open = True
            self.page.update()
            return
        
        # Build details dialog
        details_rows = []
        for req in day_requests:
            user = get_user(req.user_id)
            user_name = user.full_name if user and user.full_name else (user.username if user else "-")
            
            status_color = {
                "pending": DS.WARNING,
                "approved": DS.SUCCESS,
                "rejected": DS.ERROR,
            }.get(req.status, DS.TEXT_SECONDARY)
            
            details_rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(user_name)),
                        ft.DataCell(ft.Text(
                            translator.get_text(f"vacation.status.{req.status}"),
                            color=status_color,
                            weight=ft.FontWeight.BOLD,
                        )),
                    ]
                )
            )
        
        details_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text(translator.get_text("vacation.user"))),
                ft.DataColumn(ft.Text(translator.get_text("vacation.status.label"))),
            ],
            rows=details_rows,
        )
        
        dialog = ft.AlertDialog(
            title=ft.Text(f"{day.strftime('%Y-%m-%d')} - {translator.get_text('vacation.calendar')}"),
            content=ft.Container(
                content=details_table,
                width=400,
                height=300,
            ),
            actions=[
                ft.TextButton(
                    text=translator.get_text("common.buttons.close"),
                    on_click=lambda _: setattr(self.page.dialog, "open", False) or self.page.update(),
                ),
            ],
        )
        
        self.page.dialog = dialog
        self.page.dialog.open = True
        self.page.update()
    
    def _switch_view(self, mode: str):
        """Switch between list and calendar view"""
        if self.view_mode != mode:
            self.view_mode = mode
            # Force immediate refresh
            self._refresh_view()
    
    def _on_status_filter_change(self, e):
        """Handle status filter change"""
        # Get the selected value from dropdown
        selected_value = e.control.value
        
        # IMPORTANT: The dropdown value can be either the key (empty string for "all") 
        # or the text value (translated "Összes" or "All"). We need to check both.
        # Get the translated "all" text to compare
        all_text = translator.get_text("vacation.status.all")
        
        # Convert empty string, None, or translated "all" text to None for "all" option
        # This handles both cases: when dropdown returns key ("") or text ("Összes"/"All")
        # Also check against known valid status values - if it's not one of them, treat as "all"
        valid_statuses = ["pending", "approved", "rejected"]
        
        if (selected_value == "" or 
            selected_value is None or 
            selected_value == all_text or
            selected_value == "All" or  # Fallback for English
            selected_value not in valid_statuses):  # If it's not a valid status, treat as "all"
            self.selected_status = None
        else:
            self.selected_status = selected_value
        
        # Debug: print current state
        print(f"[DEBUG] _on_status_filter_change: selected_value={selected_value!r}, all_text={all_text!r}, self.selected_status={self.selected_status}")
        
        # Force immediate refresh to show filtered results
        # This will rebuild the content with the new filter
        self._refresh_view()
    
    def _open_request_dialog(self, e):
        """Open vacation request dialog with autosave and vacation type support"""
        # Load draft if exists
        autosave_service = get_autosave_service()
        current_user_id = get_current_user_id()
        draft_obj = autosave_service.load_draft("vacation_request", current_user_id) if current_user_id else None
        draft = draft_obj.get("form_data", {}) if draft_obj else {}
        
        start_date_row, start_date_field = create_modern_date_field(
            label=translator.get_text("vacation.start_date"),
            hint_text="YYYY-MM-DD",
            required=True,
            min_date=date.today(),
            max_date=date.today() + timedelta(days=365),
            page=self.page,
            value=draft.get("start_date", "") if draft else "",
        )
        end_date_row, end_date_field = create_modern_date_field(
            label=translator.get_text("vacation.end_date"),
            hint_text="YYYY-MM-DD",
            required=True,
            min_date=date.today(),
            max_date=date.today() + timedelta(days=365),
            page=self.page,
            value=draft.get("end_date", "") if draft else "",
        )
        reason_field = create_modern_text_field(
            label=translator.get_text("vacation.reason"),
            multiline=True,
            max_lines=5,
            value=draft.get("reason", "") if draft else "",
        )
        
        # Vacation type dropdown
        vacation_type_field = create_modern_dropdown(
            label=translator.get_text("vacation.vacation_type") if hasattr(translator, 'get_text') and translator.get_text("vacation.vacation_type") != "vacation.vacation_type" else "Szabadság típusa",
            options=[
                ft.dropdown.Option(key="annual", text=translator.get_text("vacation.type.annual") if hasattr(translator, 'get_text') and translator.get_text("vacation.type.annual") != "vacation.type.annual" else "Éves szabadság"),
                ft.dropdown.Option(key="child_care", text=translator.get_text("vacation.type.child_care") if hasattr(translator, 'get_text') and translator.get_text("vacation.type.child_care") != "vacation.type.child_care" else "Gyermekgondozási"),
                ft.dropdown.Option(key="sick_leave", text=translator.get_text("vacation.type.sick_leave") if hasattr(translator, 'get_text') and translator.get_text("vacation.type.sick_leave") != "vacation.type.sick_leave" else "Betegszabadság"),
                ft.dropdown.Option(key="unpaid", text=translator.get_text("vacation.type.unpaid") if hasattr(translator, 'get_text') and translator.get_text("vacation.type.unpaid") != "vacation.type.unpaid" else "Fizetés nélküli"),
                ft.dropdown.Option(key="other", text=translator.get_text("vacation.type.other") if hasattr(translator, 'get_text') and translator.get_text("vacation.type.other") != "vacation.type.other" else "Egyéb"),
            ],
            value=draft.get("vacation_type", "annual") if draft else "annual",
            width=300,
        )
        
        # Autosave handler
        autosave_timer_ref = {"value": None}
        
        def on_field_change():
            """Handle field change for autosave"""
            if not current_user_id:
                return
            # Save draft
            draft_data = {
                "start_date": start_date_field.value or "",
                "end_date": end_date_field.value or "",
                "reason": reason_field.value or "",
                "vacation_type": vacation_type_field.value or "annual",
            }
            autosave_service.save_draft("vacation_request", draft_data, current_user_id)
        
        # Attach autosave handlers
        start_date_field.on_change = lambda e: on_field_change()
        end_date_field.on_change = lambda e: on_field_change()
        reason_field.on_change = lambda e: on_field_change()
        vacation_type_field.on_change = lambda e: on_field_change()
        
        def submit_request(e):
            try:
                # Validate date format
                if not start_date_field.value:
                    raise ValueError(translator.get_text("vacation.start_date_required"))
                if not end_date_field.value:
                    raise ValueError(translator.get_text("vacation.end_date_required"))
                
                try:
                    start_date = datetime.strptime(start_date_field.value, "%Y-%m-%d")
                    end_date = datetime.strptime(end_date_field.value, "%Y-%m-%d")
                except ValueError:
                    raise ValueError(translator.get_text("vacation.invalid_date_format"))
                
                if start_date > end_date:
                    raise ValueError(translator.get_text("vacation.end_date_before_start"))
                
                # Validate that start date is not in the past
                if start_date.date() < date.today():
                    raise ValueError(translator.get_text("vacation.start_date_past") if hasattr(translator, 'get_text') and translator.get_text("vacation.start_date_past") != "vacation.start_date_past" else "A kezdő dátum nem lehet a múltban")
                
                reason = reason_field.value
                vacation_type = vacation_type_field.value or "annual"
                
                # Get fresh user_id from context (don't rely on cached value)
                current_user_id = get_current_user_id()
                if not current_user_id:
                    raise ValueError("Nincs bejelentkezve felhasználó / No user logged in")
                
                create_vacation_request(
                    user_id=current_user_id,
                    start_date=start_date,
                    end_date=end_date,
                    vacation_type=vacation_type,
                    reason=reason,
                )
                
                # Clear draft after successful submission
                autosave_service.delete_draft("vacation_request", current_user_id)
                
                # Close dialog first
                self.page.dialog.open = False
                self.page.update()
                
                # Refresh the page to show new request in list
                self._refresh_view()
                
                # Show success message after refresh
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(translator.get_text("vacation.request_created")),
                    bgcolor=DS.SUCCESS,
                )
                self.page.snack_bar.open = True
                self.page.update()
            except (VacationServiceError, ValueError) as err:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(str(err)),
                    bgcolor=DS.ERROR,
                )
                self.page.snack_bar.open = True
                self.page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text(translator.get_text("vacation.request_vacation")),
            content=ft.Column(
                controls=[
                    vacation_type_field,
                    start_date_row,
                    end_date_row,
                    reason_field,
                ],
                tight=True,
                scroll=ft.ScrollMode.AUTO,
            ),
            actions=[
                ft.TextButton(
                    text=translator.get_text("common.buttons.cancel"),
                    on_click=lambda _: (autosave_service.delete_draft("vacation_request", current_user_id) if current_user_id else None) or setattr(self.page.dialog, "open", False) or self.page.update(),
                ),
                ft.TextButton(
                    text=translator.get_text("common.buttons.submit"),
                    on_click=submit_request,
                ),
            ],
        )
        
        self.page.dialog = dialog
        self.page.dialog.open = True
        self.page.update()
    
    def _approve_request(self, request_id: int):
        """Approve a vacation request"""
        try:
            # Get fresh user_id from context (don't rely on cached value)
            current_user_id = get_current_user_id()
            if not current_user_id:
                raise VacationServiceError("Nincs bejelentkezve felhasználó / No user logged in")
            approve_vacation_request(request_id, current_user_id)
            # Refresh the page to show updated request status
            self._refresh_view()
            # Show success message after refresh
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(translator.get_text("vacation.request_approved")),
                bgcolor=DS.SUCCESS,
            )
            self.page.snack_bar.open = True
            self.page.update()
        except VacationServiceError as err:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(str(err)),
                bgcolor=DS.ERROR,
            )
            self.page.snack_bar.open = True
            self.page.update()
    
    def _open_reject_dialog(self, request: VacationRequest):
        """Open rejection dialog"""
        reason_field = create_modern_text_field(
            label=translator.get_text("vacation.rejection_reason"),
            multiline=True,
            max_lines=5,
        )
        
        def submit_rejection(e):
            try:
                # Get fresh user_id from context (don't rely on cached value)
                current_user_id = get_current_user_id()
                if not current_user_id:
                    raise VacationServiceError("Nincs bejelentkezve felhasználó / No user logged in")
                reject_vacation_request(
                    request.id,
                    current_user_id,
                    reason_field.value or "",
                )
                # Close dialog first
                self.page.dialog.open = False
                self.page.update()
                
                # Refresh the page to show updated request status
                self._refresh_view()
                
                # Show success message after refresh
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(translator.get_text("vacation.request_rejected")),
                    bgcolor=DS.ERROR,
                )
                self.page.snack_bar.open = True
                self.page.update()
            except VacationServiceError as err:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(str(err)),
                    bgcolor=DS.ERROR,
                )
                self.page.snack_bar.open = True
                self.page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text(translator.get_text("vacation.reject")),
            content=reason_field,
            actions=[
                ft.TextButton(
                    text=translator.get_text("common.cancel"),
                    on_click=lambda _: setattr(self.page.dialog, "open", False) or self.page.update(),
                ),
                ft.TextButton(
                    text=translator.get_text("common.submit"),
                    on_click=submit_rejection,
                ),
            ],
        )
        
        self.page.dialog = dialog
        self.page.dialog.open = True
        self.page.update()
    
    def _download_vacation_document(self, request_id: int):
        """Download vacation request document (DOCX)"""
        import os
        import shutil
        from pathlib import Path
        
        try:
            # Generate document
            docx_path = pdf_service.generate_vacation_document(request_id)
            
            # Create default filename
            default_filename = f"vacation_request_{request_id}_{datetime.now().strftime('%Y%m%d')}.docx"
            
            def on_save_result(e: ft.FilePickerResultEvent):
                try:
                    if e.path:
                        dest_path = e.path
                        if not dest_path.endswith('.docx'):
                            dest_path = dest_path + '.docx'
                        
                        # Copy file to user-selected location
                        shutil.copy2(str(docx_path), dest_path)
                        
                        self.page.snack_bar = ft.SnackBar(
                            content=ft.Text(f"Szabadságigénylő lap letöltve ide: {dest_path}"),
                            bgcolor=DS.SUCCESS,
                        )
                        self.page.snack_bar.open = True
                        self.page.update()
                    else:
                        # User cancelled
                        self.page.snack_bar = ft.SnackBar(
                            content=ft.Text("Letöltés megszakítva / Download cancelled"),
                            bgcolor=DS.INFO,
                        )
                        self.page.snack_bar.open = True
                        self.page.update()
                except Exception as ex:
                    logger.error(f"Error saving vacation document: {ex}", exc_info=True)
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"Hiba a mentéskor: {str(ex)}"),
                        bgcolor=DS.ERROR,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
            
            # Create file picker for save dialog
            file_picker = ft.FilePicker(
                on_result=on_save_result
            )
            self.page.overlay.append(file_picker)
            self.page.update()
            
            # Open save dialog
            file_picker.save_file(
                dialog_title="Szabadságigénylő lap mentése / Save Vacation Request",
                file_name=default_filename,
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["docx"]
            )
        except Exception as ex:
            logger.error(f"Error generating vacation document: {ex}", exc_info=True)
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Hiba a dokumentum generálásakor: {str(ex)}"),
                bgcolor=DS.ERROR,
            )
            self.page.snack_bar.open = True
            self.page.update()
    
    def _on_search_change(self, e):
        """Handle search query change"""
        self.search_query = e.control.value or ""
        # Reset to first page when searching
        if self.pagination_controller:
            self.pagination_controller.current_page = 1
        self._refresh_view()
    
    def _on_year_filter_change(self, e):
        """Handle year filter change"""
        try:
            self.current_year = int(e.control.value)
            # Reset to first page when changing year
            if self.pagination_controller:
                self.pagination_controller.current_page = 1
            self._refresh_view()
        except (ValueError, TypeError):
            pass
    
    def _on_items_per_page_change(self, value: int):
        """Handle items per page change"""
        self.items_per_page = value
        if self.pagination_controller:
            self.pagination_controller.items_per_page = value
            self.pagination_controller.current_page = 1
        self._refresh_view()
    
    def _on_request_selection_change(self, request_id: int, e):
        """Handle request selection checkbox change"""
        if e.control.value:
            self.selected_request_ids.add(request_id)
        else:
            self.selected_request_ids.discard(request_id)
        self._refresh_view()
    
    def _batch_approve_requests(self):
        """Batch approve selected requests"""
        if not self.selected_request_ids:
            return
        
        from ui.components.confirmation_dialogs import create_modify_confirmation_dialog
        
        def confirm_approve():
            try:
                current_user_id = get_current_user_id()
                if not current_user_id:
                    raise VacationServiceError("Nincs bejelentkezve felhasználó / No user logged in")
                
                approved_count = 0
                failed_count = 0
                for request_id in list(self.selected_request_ids):
                    try:
                        approve_vacation_request(request_id, current_user_id)
                        approved_count += 1
                    except Exception as err:
                        logger.error(f"Error approving request {request_id}: {err}")
                        failed_count += 1
                
                self.selected_request_ids.clear()
                self._refresh_view()
                
                message = f"{approved_count} {translator.get_text('vacation.request_approved')}"
                if failed_count > 0:
                    message += f", {failed_count} {translator.get_text('common.messages.operation_failed')}"
                
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(message),
                    bgcolor=DS.SUCCESS if failed_count == 0 else DS.WARNING,
                )
                self.page.snack_bar.open = True
                self.page.update()
            except Exception as err:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(str(err)),
                    bgcolor=DS.ERROR,
                )
                self.page.snack_bar.open = True
                self.page.update()
        
        dialog = create_modify_confirmation_dialog(
            page=self.page,
            title=translator.get_text("vacation.approve"),
            entity_name=f"{len(self.selected_request_ids)} {translator.get_text('vacation.request_vacation')}",
            changes={"status": {"old": translator.get_text("vacation.status.pending"), "new": translator.get_text("vacation.status.approved")}},
            on_confirm=confirm_approve,
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def _batch_reject_requests(self):
        """Batch reject selected requests"""
        if not self.selected_request_ids:
            return
        
        # Open dialog to get rejection reason
        reason_field = create_modern_text_field(
            label=translator.get_text("vacation.rejection_reason"),
            multiline=True,
            max_lines=5,
        )
        
        def submit_rejection(e):
            try:
                current_user_id = get_current_user_id()
                if not current_user_id:
                    raise VacationServiceError("Nincs bejelentkezve felhasználó / No user logged in")
                
                rejection_reason = reason_field.value or ""
                rejected_count = 0
                failed_count = 0
                
                for request_id in list(self.selected_request_ids):
                    try:
                        reject_vacation_request(
                            request_id,
                            current_user_id,
                            rejection_reason,
                        )
                        rejected_count += 1
                    except Exception as err:
                        logger.error(f"Error rejecting request {request_id}: {err}")
                        failed_count += 1
                
                self.selected_request_ids.clear()
                self.page.dialog.open = False
                self.page.update()
                self._refresh_view()
                
                message = f"{rejected_count} {translator.get_text('vacation.request_rejected')}"
                if failed_count > 0:
                    message += f", {failed_count} {translator.get_text('common.messages.operation_failed')}"
                
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(message),
                    bgcolor=DS.SUCCESS if failed_count == 0 else DS.WARNING,
                )
                self.page.snack_bar.open = True
                self.page.update()
            except Exception as err:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(str(err)),
                    bgcolor=DS.ERROR,
                )
                self.page.snack_bar.open = True
                self.page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text(translator.get_text("vacation.reject")),
            content=reason_field,
            actions=[
                ft.TextButton(
                    text=translator.get_text("common.buttons.cancel"),
                    on_click=lambda _: setattr(self.page.dialog, "open", False) or self.page.update(),
                ),
                ft.TextButton(
                    text=translator.get_text("common.buttons.submit"),
                    on_click=submit_rejection,
                ),
            ],
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def _on_export_click(self, e):
        """Handle export button click"""
        try:
            # Get all requests (not just current page)
            current_user_id = get_current_user_id()
            from config.roles import ROLE_MANAGER, ROLE_DEVELOPER, ROLE_MAINTENANCE_SUPERVISOR
            can_approve = False
            ctx = get_app_context()
            if ctx.role:
                role_name = ctx.role
                can_approve = role_name in [ROLE_MANAGER, ROLE_DEVELOPER, ROLE_MAINTENANCE_SUPERVISOR]
            
            filter_user_id = None if can_approve else current_user_id
            normalized_status = None if (self.selected_status is None or self.selected_status == "") else self.selected_status
            
            all_requests = get_vacation_requests(
                user_id=filter_user_id,
                status=normalized_status,
                year=self.current_year
            )
            
            # Apply search filter if exists
            if self.search_query:
                search_lower = self.search_query.lower()
                filtered_requests = []
                for req in all_requests:
                    user = get_user(req.user_id)
                    user_name = (user.full_name or user.username or "").lower() if user else ""
                    reason = (req.reason or "").lower()
                    start_date_str = (req.start_date.date() if isinstance(req.start_date, datetime) else req.start_date).strftime("%Y-%m-%d")
                    end_date_str = (req.end_date.date() if isinstance(req.end_date, datetime) else req.end_date).strftime("%Y-%m-%d")
                    
                    if (search_lower in user_name or 
                        search_lower in reason or 
                        search_lower in start_date_str or 
                        search_lower in end_date_str):
                        filtered_requests.append(req)
                all_requests = filtered_requests
            
            # Prepare data for export
            export_data = []
            for req in all_requests:
                user = get_user(req.user_id)
                user_name = user.full_name if user and user.full_name else (user.username if user else "-")
                start_date = req.start_date.date() if isinstance(req.start_date, datetime) else req.start_date
                end_date = req.end_date.date() if isinstance(req.end_date, datetime) else req.end_date
                
                export_data.append({
                    "ID": req.id,
                    translator.get_text("vacation.user"): user_name,
                    translator.get_text("vacation.start_date"): start_date.strftime("%Y-%m-%d"),
                    translator.get_text("vacation.end_date"): end_date.strftime("%Y-%m-%d"),
                    translator.get_text("vacation.days_count"): req.days_count or 0,
                    translator.get_text("vacation.status.label"): translator.get_text(f"vacation.status.{req.status}"),
                    translator.get_text("vacation.reason"): req.reason or "",
                    translator.get_text("vacation.vacation_type"): req.vacation_type or "annual",
                })
            
            # Export to CSV
            csv_data = ExportService.export_to_csv(
                data=export_data,
                headers=list(export_data[0].keys()) if export_data else [],
            )
            
            # Save file
            def on_save_result(e: ft.FilePickerResultEvent):
                try:
                    if e.path:
                        dest_path = e.path
                        if not dest_path.endswith('.csv'):
                            dest_path = dest_path + '.csv'
                        
                        with open(dest_path, 'wb') as f:
                            f.write(csv_data)
                        
                        self.page.snack_bar = ft.SnackBar(
                            content=ft.Text(f"{translator.get_text('common.buttons.export')} {translator.get_text('common.messages.operation_successful')}: {dest_path}"),
                            bgcolor=DS.SUCCESS,
                        )
                        self.page.snack_bar.open = True
                        self.page.update()
                    else:
                        self.page.snack_bar = ft.SnackBar(
                            content=ft.Text(translator.get_text("worksheets.download_cancelled")),
                            bgcolor=DS.INFO,
                        )
                        self.page.snack_bar.open = True
                        self.page.update()
                except Exception as ex:
                    logger.error(f"Error saving export file: {ex}", exc_info=True)
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"{translator.get_text('common.messages.error_occurred')}: {str(ex)}"),
                        bgcolor=DS.ERROR,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
            
            # Create file picker for save dialog
            file_picker = ft.FilePicker(
                on_result=on_save_result
            )
            self.page.overlay.append(file_picker)
            self.page.update()
            
            # Open save dialog
            default_filename = f"vacation_requests_{self.current_year}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            file_picker.save_file(
                dialog_title=translator.get_text("common.buttons.export"),
                file_name=default_filename,
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["csv"]
            )
        except Exception as ex:
            logger.error(f"Error exporting vacation requests: {ex}", exc_info=True)
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"{translator.get_text('common.messages.error_occurred')}: {str(ex)}"),
                bgcolor=DS.ERROR,
            )
            self.page.snack_bar.open = True
            self.page.update()
