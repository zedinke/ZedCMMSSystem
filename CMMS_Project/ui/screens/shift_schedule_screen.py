"""
Shift Schedule Screen
Allows users to view and manage their shift schedules with full year calendar
"""

import flet as ft
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict
from calendar import monthcalendar, monthrange

from services.shift_service import (
    set_user_shift_schedule, get_user_shift_schedule, get_all_shift_schedules,
    calculate_shift_for_date, get_shift_calendar, create_shift_override,
    delete_shift_override, get_shift_override,
    ShiftServiceError
)
from services.context_service import get_current_user_id, get_user, get_app_context
from services.user_service import list_all_users
from services.vacation_service import get_vacation_requests
from localization.translator import translator
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
from config.roles import ROLE_MAINTENANCE_TECH, ROLE_MANAGER, ROLE_MAINTENANCE_SUPERVISOR, ROLE_DEVELOPER

import logging

logger = logging.getLogger(__name__)


class ShiftScheduleScreen:
    """Shift schedule management screen with full year calendar"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.current_user_id = get_current_user_id()
        self.current_user = get_user(self.current_user_id) if self.current_user_id else None
        self.current_year = datetime.now().year
        self.view_mode = "calendar"  # "calendar" or "table"
        self.role_filter = ROLE_MAINTENANCE_TECH  # Default: only maintenance techs
        self.main_column = None
        self.search_query = ""  # Search query for filtering users
        self.selected_user_ids = set()  # Selected user IDs for batch operations
        self.items_per_page = 20  # Default items per page
        self.pagination_controller = None  # Will be initialized in view
        
    def view(self, page: ft.Page = None) -> ft.Control:
        """Build the shift schedule screen view"""
        # Use provided page or stored page
        if page:
            self.page = page
        
        # Get calendar data
        calendar_data = get_shift_calendar(self.current_year, role_filter=self.role_filter)
        
        # Header
        header = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text(
                        translator.get_text("shift_schedule.calendar_title"),
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=DS.PRIMARY,
                    ),
                    ft.Container(expand=True),
                    # Export button (only for table view)
                    create_modern_button(
                        text=translator.get_text("common.buttons.export"),
                        icon=ft.icons.DOWNLOAD,
                        on_click=self._on_export_click,
                        bgcolor=DS.INFO,
                        width=150,
                    ) if self.view_mode == "table" else ft.Container(width=0),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.padding.only(bottom=20),
        )
        
        # Year navigation
        year_text = ft.Text(
            str(self.current_year),
            size=20,
            weight=ft.FontWeight.BOLD,
            key="year_text",  # Add key for easy reference
        )
        
        # Create wrapper functions to avoid lambda closure issues in PyInstaller
        def handle_prev_year(e):
            self._change_year(-1)
        
        def handle_next_year(e):
            self._change_year(1)
        
        year_nav = ft.Row(
            controls=[
                create_modern_button(
                    text="<",
                    on_click=handle_prev_year,
                    width=50,
                ),
                year_text,
                create_modern_button(
                    text=">",
                    on_click=handle_next_year,
                    width=50,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
        )
        # Store reference to year text for updates
        self.year_text = year_text
        
        # Role filter (only for managers and supervisors)
        ctx = get_app_context()
        can_manage = False
        if ctx.is_authenticated():
            user = get_user(ctx.user_id)
            if user and user.role:
                role_name = user.role.name
                can_manage = role_name in [ROLE_MANAGER, ROLE_MAINTENANCE_SUPERVISOR, ROLE_DEVELOPER]
        
        role_filter_control = None
        if can_manage:
            role_filter_control = ft.Row(
                controls=[
                    ft.Checkbox(
                        label=translator.get_text("shift_schedule.all_roles") if hasattr(translator, 'get_text') else "Összes szerepkör / All Roles",
                        value=(self.role_filter is None),
                        on_change=lambda e: self._toggle_role_filter(e.control.value),
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            )
        
        # View mode toggle
        # Create wrapper functions to avoid lambda closure issues in PyInstaller
        def handle_switch_to_calendar(e):
            self._switch_view("calendar")
        
        def handle_switch_to_table(e):
            self._switch_view("table")
        
        view_mode_toggle = ft.Row(
            controls=[
                create_modern_button(
                    text=translator.get_text("shift_schedule.calendar_view") if hasattr(translator, 'get_text') else "Naptár / Calendar",
                    on_click=handle_switch_to_calendar,
                    bgcolor=DS.PRIMARY if self.view_mode == "calendar" else DS.BG_SECONDARY,
                ),
                create_modern_button(
                    text=translator.get_text("shift_schedule.table_view") if hasattr(translator, 'get_text') else "Táblázat / Table",
                    on_click=handle_switch_to_table,
                    bgcolor="#FFA500" if self.view_mode == "table" else "#FFA500",  # Orange color
                    color="#000000" if self.view_mode == "table" else "#000000",  # Black text
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
        )
        
        # Search field (only for table view)
        search_field = None
        if self.view_mode == "table":
            search_field = ft.Row(
                controls=[
                    create_modern_text_field(
                        label=translator.get_text("common.search"),
                        hint_text=translator.get_text("common.search_hint") if hasattr(translator, 'get_text') else "Keresés...",
                        value=self.search_query,
                        on_change=self._on_search_change,
                        width=300,
                        icon=ft.icons.SEARCH,
                    ),
                ],
                spacing=10,
            )
        
        # Build content based on view mode
        if self.view_mode == "calendar":
            content = self._build_calendar_view(calendar_data)
        else:
            content = self._build_table_view()
        
        # Current user's shift schedule card (for settings)
        current_schedule_card = self._build_current_schedule_card()
        
        # Build main column controls list (filter out None values)
        main_controls = [
            header,
            year_nav,
            ft.Container(height=10),
            view_mode_toggle,
            ft.Container(height=10),
        ]
        
        # Add role filter if it exists
        if role_filter_control is not None:
            main_controls.append(role_filter_control)
        
        # Add search field if in table view
        if search_field:
            main_controls.append(search_field)
            main_controls.append(ft.Container(height=10))
        
        main_controls.extend([
            current_schedule_card,
            ft.Divider(),
            content,
        ])
        
        # Filter out any None values to prevent _build_add_commands errors
        main_controls = [c for c in main_controls if c is not None]
        
        # Build main column
        main_column = ft.Column(
            controls=main_controls,
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        
        self.main_column = main_column
        
        # Return Container
        return ft.Container(
            content=main_column,
            padding=20,
            expand=True,
        )
    
    def _change_year(self, delta: int):
        """Change the displayed year"""
        self.current_year += delta
        self._refresh_view()
    
    def _toggle_role_filter(self, show_all: bool):
        """Toggle role filter"""
        self.role_filter = None if show_all else ROLE_MAINTENANCE_TECH
        self._refresh_view()
    
    def _switch_view(self, mode: str):
        """Switch between calendar and table view"""
        if self.view_mode != mode:
            self.view_mode = mode
            self._refresh_view()
    
    def _refresh_view(self):
        """Refresh the view with loading indicator"""
        if self.main_column is not None:
            # Update year text if it exists
            if hasattr(self, 'year_text'):
                self.year_text.value = str(self.current_year)
            
            # Show loading indicator
            loading_indicator = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.ProgressRing(width=50, height=50),
                        ft.Text(
                            translator.get_text("common.loading") if hasattr(translator, 'get_text') else "Betöltés...",
                            size=14,
                            color=DS.TEXT_SECONDARY,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10,
                ),
                alignment=ft.alignment.center,
                padding=40,
            )
            
            # Replace content with loading indicator temporarily
            # Get all non-None controls from the main column
            base_controls = [c for c in self.main_column.controls if c is not None]
            # Keep only the first 7 (header, year_nav, etc.) and add loading indicator
            base_controls = [c for c in base_controls[:7] if c is not None]
            # Ensure loading_indicator is not None
            if loading_indicator is not None:
                self.main_column.controls = base_controls + [loading_indicator]
            else:
                self.main_column.controls = base_controls
            # Filter out any None values before updating
            self.main_column.controls = [c for c in self.main_column.controls if c is not None]
            self.page.update()
            
            # Load data in background thread to avoid blocking UI
            import threading
            def load_data():
                try:
                    # Rebuild content
                    calendar_data = get_shift_calendar(self.current_year, role_filter=self.role_filter)
                    if self.view_mode == "calendar":
                        content = self._build_calendar_view(calendar_data)
                    else:
                        content = self._build_table_view()
                    
                    # Update main column controls (Flet handles thread safety)
                    base_controls = [c for c in self.main_column.controls[:7] if c is not None]
                    # Ensure content is not None
                    if content is not None:
                        self.main_column.controls = base_controls + [content]
                    else:
                        self.main_column.controls = base_controls
                    # Filter out any None values before updating
                    self.main_column.controls = [c for c in self.main_column.controls if c is not None]
                    self.page.update()
                except Exception as e:
                    logger.error(f"Error loading shift calendar: {e}")
                    import traceback
                    traceback.print_exc()
                    # Show error message
                    error_content = ft.Container(
                        content=ft.Text(
                            f"Hiba történt a betöltés során: {str(e)}",
                            size=14,
                            color=DS.ERROR,
                        ),
                        alignment=ft.alignment.center,
                        padding=40,
                    )
                    base_controls = [c for c in self.main_column.controls[:7] if c is not None]
                    # Ensure error_content is not None
                    if error_content is not None:
                        self.main_column.controls = base_controls + [error_content]
                    else:
                        self.main_column.controls = base_controls
                    # Filter out any None values before updating
                    self.main_column.controls = [c for c in self.main_column.controls if c is not None]
                    self.page.update()
            
            thread = threading.Thread(target=load_data, daemon=True)
            thread.start()
        else:
            # Fallback: route bounce
            try:
                self.page.go("/shift_schedule_refresh")
                self.page.go("/shift_schedule")
                self.page.update()
            except Exception:
                self.page.update()
    
    def _build_calendar_view(self, calendar_data: Dict[str, Dict]) -> ft.Control:
        """Build full year calendar view"""
        # Legend
        legend = ft.Row(
            controls=[
                ft.Container(
                    content=ft.Row([
                        ft.Container(width=20, height=20, bgcolor="#10B981", border_radius=4),  # Green for DE
                        ft.Text(translator.get_text("shift_schedule.shift_morning"), size=12),
                    ], spacing=10),
                ),
                ft.Container(
                    content=ft.Row([
                        ft.Container(width=20, height=20, bgcolor="#F59E0B", border_radius=4),  # Orange for DU
                        ft.Text(translator.get_text("shift_schedule.shift_afternoon"), size=12),
                    ], spacing=10),
                ),
                ft.Container(
                    content=ft.Row([
                        ft.Container(width=20, height=20, bgcolor="#3B82F6", border_radius=4),  # Blue for ÉJ
                        ft.Text(translator.get_text("shift_schedule.shift_night"), size=12),
                    ], spacing=10),
                ),
                ft.Container(
                    content=ft.Row([
                        ft.Container(width=20, height=20, bgcolor="#EF4444", border_radius=4, border=ft.border.all(2, "#FFFFFF")),  # Red border for vacation
                        ft.Text(translator.get_text("shift_schedule.vacation_indicator"), size=12),
                    ], spacing=10),
                ),
            ],
            spacing=20,
            alignment=ft.MainAxisAlignment.CENTER,
        )
        
        # Build calendar grid (12 months)
        months_grid = ft.GridView(
            runs_count=3,  # 3 columns
            max_extent=420,  # Increased from 350 to make calendars bigger
            spacing=20,
            run_spacing=20,
            child_aspect_ratio=1.0,  # Adjusted for larger calendars
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
        
        return ft.Column(
            controls=[
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
        from services.user_service import get_user
        
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
                width=36,  # Increased from 28 to match day cell width
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
                    week_row.controls.append(ft.Container(width=36, height=36))  # Increased to match day cell
                else:
                    # Day cell
                    current_date = date(self.current_year, month, day)
                    date_str = current_date.isoformat()
                    
                    # Get shift info for this day
                    day_info = calendar_data.get(date_str, {"users": []})
                    users_info = day_info.get("users", [])
                    
                    # Determine cell color and content based on shifts
                    bg_color = "#E5E7EB"  # Gray - no shift
                    border_color = None
                    shift_text = ""
                    user_names_text = ""
                    
                    # Collect unique shifts for this day
                    shifts = set()
                    has_vacation = False
                    for user_info in users_info:
                        if user_info.get("shift"):
                            shifts.add(user_info["shift"])
                        if user_info.get("is_vacation"):
                            has_vacation = True
                    
                    if shifts:
                        # Determine color based on shifts (prioritize first shift if multiple)
                        shift_list = sorted(list(shifts))
                        primary_shift = shift_list[0]
                        
                        if primary_shift == "DE":
                            bg_color = "#10B981"  # Green
                        elif primary_shift == "DU":
                            bg_color = "#F59E0B"  # Orange
                        elif primary_shift == "ÉJ":
                            bg_color = "#3B82F6"  # Blue
                        
                        # Show shift abbreviations
                        if len(shifts) <= 2:
                            shift_text = ", ".join(shift_list)
                        else:
                            shift_text = f"{len(shifts)}"
                    
                    # Collect user names/initials
                    if users_info:
                        user_names = []
                        for user_info in users_info:
                            user_id = user_info.get("user_id")
                            user = get_user(user_id) if user_id else None
                            if user:
                                # Use first letter of first name and last name initial, or just first name
                                if user.full_name:
                                    parts = user.full_name.split()
                                    if len(parts) >= 2:
                                        initial = f"{parts[0][0]}. {parts[-1][0]}."
                                    else:
                                        initial = parts[0][:3]
                                    user_names.append(initial)
                                elif user.username:
                                    user_names.append(user.username[:3])
                        
                        if user_names:
                            user_names_text = ", ".join(user_names[:2])  # Show max 2 users
                            if len(user_names) > 2:
                                user_names_text += "..."
                    
                    # Add red border if vacation
                    if has_vacation:
                        border_color = "#EF4444"
                    
                    # Build day cell with larger size
                    day_cell = ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text(
                                    str(day),
                                    size=10,
                                    color="#FFFFFF" if bg_color != "#E5E7EB" else DS.TEXT_PRIMARY,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Text(
                                    shift_text,
                                    size=8,
                                    color="#FFFFFF" if bg_color != "#E5E7EB" else DS.TEXT_SECONDARY,
                                    weight=ft.FontWeight.BOLD,
                                ) if shift_text else ft.Container(height=0),
                                ft.Text(
                                    user_names_text,
                                    size=6,
                                    color="#FFFFFF" if bg_color != "#E5E7EB" else DS.TEXT_SECONDARY,
                                ) if user_names_text else ft.Container(height=0),
                            ],
                            spacing=1,
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            tight=True,
                        ),
                        width=36,  # Increased from 28
                        height=50,  # Increased from 40
                        bgcolor=bg_color,
                        border_radius=4,
                        border=ft.border.all(2, border_color) if border_color else None,
                        alignment=ft.alignment.center,
                        on_click=self._create_day_details_handler(current_date, users_info),
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
    
    def _create_day_details_handler(self, day: date, users_info: List[Dict]):
        """Create a handler function for day details click to avoid lambda closure issues"""
        def handle_click(e):
            self._show_day_details(day, users_info)
        return handle_click
    
    def _show_day_details(self, day: date, users_info: List[Dict]):
        """Show details dialog for a specific day"""
        from services.user_service import get_user
        
        # Build users list
        details_rows = []
        for user_info in users_info:
            user_id = user_info.get("user_id")
            user = get_user(user_id) if user_id else None
            user_name = user.full_name if user and user.full_name else (user.username if user else f"User {user_id}")
            
            shift = user_info.get("shift", "-")
            is_vacation = user_info.get("is_vacation", False)
            vacation_status = user_info.get("vacation_status")
            
            # Shift time display
            shift_times = {
                "DE": translator.get_text("shift_schedule.shift_times.morning"),
                "DU": translator.get_text("shift_schedule.shift_times.afternoon"),
                "ÉJ": translator.get_text("shift_schedule.shift_times.night"),
            }
            shift_time_text = shift_times.get(shift, "-")
            
            # Build status text
            status_parts = [f"{shift} ({shift_time_text})"]
            if is_vacation:
                if vacation_status == "approved":
                    status_parts.append(f"[{translator.get_text('shift_schedule.vacation_indicator')}]")
                elif vacation_status == "pending":
                    status_parts.append(f"[{translator.get_text('vacation.status.pending')}]")
            
            details_rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(user_name)),
                        ft.DataCell(ft.Text(" / ".join(status_parts))),
                        ft.DataCell(
                            create_modern_button(
                                text=translator.get_text("shift_schedule.change_shift_for_day"),
                                on_click=self._create_shift_override_handler(day, user_id) if user_id else None,
                                width=150,
                            ) if user_id else ft.Container()
                        ),
                    ]
                )
            )
        
        if not details_rows:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"{day.strftime('%Y-%m-%d')}: {translator.get_text('shift_schedule.no_shift')}"),
                bgcolor=DS.INFO,
            )
            self.page.snack_bar.open = True
            self.page.update()
            return
        
        details_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text(translator.get_text("shift_schedule.user") if hasattr(translator, 'get_text') else "Felhasználó / User")),
                ft.DataColumn(ft.Text(translator.get_text("shift_schedule.shift_type"))),
                ft.DataColumn(ft.Text(translator.get_text("shift_schedule.actions") if hasattr(translator, 'get_text') else "Műveletek / Actions")),
            ],
            rows=details_rows,
        )
        
        dialog = ft.AlertDialog(
            title=ft.Text(f"{day.strftime('%Y-%m-%d')} - {translator.get_text('shift_schedule.calendar_title')}"),
            content=ft.Container(
                content=details_table,
                width=600,
                height=400,
            ),
            actions=[
                ft.TextButton(
                    text=translator.get_text("common.buttons.close") if hasattr(translator, 'get_text') else "Bezárás / Close",
                    on_click=lambda _: setattr(self.page.dialog, "open", False) or self.page.update(),
                ),
            ],
        )
        
        self.page.dialog = dialog
        self.page.dialog.open = True
        self.page.update()
    
    def _open_shift_override_dialog(self, day: date, user_id: int):
        """Open dialog to override shift for a specific day"""
        from services.user_service import get_user
        
        user = get_user(user_id)
        if not user:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Felhasználó nem található / User not found"),
                bgcolor=DS.ERROR,
            )
            self.page.snack_bar.open = True
            self.page.update()
            return
        
        # Check if override already exists
        existing_override = get_shift_override(user_id, day)
        
        # Get current shift for this day
        current_shift = calculate_shift_for_date(user_id, day) or "-"
        
        # Shift dropdown
        shift_dropdown = create_modern_dropdown(
            label=translator.get_text("shift_schedule.shift_type"),
            options=[
                ft.dropdown.Option("DE", translator.get_text("shift_schedule.shift_morning")),
                ft.dropdown.Option("ÉJ", translator.get_text("shift_schedule.shift_night")),
                ft.dropdown.Option("DU", translator.get_text("shift_schedule.shift_afternoon")),
            ],
            value=existing_override.shift_type if existing_override else current_shift if current_shift != "-" else "DE",
            width=300,
        )
        
        # Notes field
        notes_field = create_modern_text_field(
            label=translator.get_text("shift_schedule.notes") if hasattr(translator, 'get_text') else "Megjegyzés / Notes",
            multiline=True,
            max_lines=3,
            value=existing_override.notes if existing_override else "",
            width=300,
        )
        
        def save_override(e):
            try:
                current_user_id = get_current_user_id()
                if not current_user_id:
                    raise ShiftServiceError("Nincs bejelentkezve felhasználó / No user logged in")
                
                create_shift_override(
                    user_id=user_id,
                    override_date=day,
                    shift_type=shift_dropdown.value,
                    created_by_user_id=current_user_id,
                    notes=notes_field.value or None,
                )
                
                # Close dialog
                self.page.dialog.open = False
                self.page.update()
                
                # Refresh view
                self._refresh_view()
                
                # Show success message
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(translator.get_text("shift_schedule.schedule_saved")),
                    bgcolor=DS.SUCCESS,
                )
                self.page.snack_bar.open = True
                self.page.update()
            except ShiftServiceError as err:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(str(err)),
                    bgcolor=DS.ERROR,
                )
                self.page.snack_bar.open = True
                self.page.update()
            except Exception as err:
                import traceback
                logger.error(f"Error saving shift schedule: {err}\n{traceback.format_exc()}")
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Hiba történt: {str(err)}"),
                    bgcolor=DS.ERROR,
                )
                self.page.snack_bar.open = True
                self.page.update()
        
        def delete_override(e):
            try:
                if not existing_override:
                    return
                
                current_user_id = get_current_user_id()
                if not current_user_id:
                    raise ShiftServiceError("Nincs bejelentkezve felhasználó / No user logged in")
                
                delete_shift_override(existing_override.id, current_user_id)
                
                # Close dialog
                self.page.dialog.open = False
                self.page.update()
                
                # Refresh view
                self._refresh_view()
                
                # Show success message
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Műszak felülírás törölve / Shift override deleted"),
                    bgcolor=DS.SUCCESS,
                )
                self.page.snack_bar.open = True
                self.page.update()
            except ShiftServiceError as err:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(str(err)),
                    bgcolor=DS.ERROR,
                )
                self.page.snack_bar.open = True
                self.page.update()
            except Exception as err:
                import traceback
                logger.error(f"Error saving shift schedule: {err}\n{traceback.format_exc()}")
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Hiba történt: {str(err)}"),
                    bgcolor=DS.ERROR,
                )
                self.page.snack_bar.open = True
                self.page.update()
        
        dialog_content = ft.Column(
            controls=[
                ft.Text(f"{translator.get_text('shift_schedule.user')}: {user.full_name or user.username}", size=14, weight=ft.FontWeight.BOLD),
                ft.Text(f"{translator.get_text('shift_schedule.date') if hasattr(translator, 'get_text') else 'Dátum / Date'}: {day.strftime('%Y-%m-%d')}", size=12),
                ft.Text(f"{translator.get_text('shift_schedule.current_shift') if hasattr(translator, 'get_text') else 'Jelenlegi műszak / Current Shift'}: {current_shift}", size=12),
                ft.Divider(),
                shift_dropdown,
                notes_field,
            ],
            spacing=15,
            width=400,
        )
        
        actions = [
            ft.TextButton(
                text=translator.get_text("common.buttons.cancel"),
                on_click=lambda _: setattr(self.page.dialog, "open", False) or self.page.update(),
            ),
            create_modern_button(
                text=translator.get_text("shift_schedule.save"),
                on_click=save_override,
                bgcolor=DS.SUCCESS,
            ),
        ]
        
        if existing_override:
            actions.insert(-1, create_modern_button(
                text=translator.get_text("common.buttons.delete"),
                on_click=delete_override,
                bgcolor=DS.ERROR,
            ))
        
        dialog = ft.AlertDialog(
            title=ft.Text(translator.get_text("shift_schedule.override_shift")),
            content=dialog_content,
            actions=actions,
        )
        
        self.page.dialog = dialog
        self.page.dialog.open = True
        self.page.update()
    
    def _build_table_view(self) -> ft.Control:
        """Build card-based view showing all users' shift schedules with pagination, search, and batch operations"""
        from services.user_service import get_user
        
        # Get all users
        all_users = list_all_users()
        
        # Filter by role if needed
        if self.role_filter:
            all_users = [u for u in all_users if u.role and u.role.name == self.role_filter]
        
        # Apply search filter
        if self.search_query:
            search_lower = self.search_query.lower()
            filtered_users = []
            for user in all_users:
                user_name = (user.full_name or user.username or "").lower()
                if search_lower in user_name:
                    filtered_users.append(user)
            all_users = filtered_users
        
        # Initialize pagination controller if not exists or total changed
        total_users = len(all_users)
        if self.pagination_controller is None or self.pagination_controller.total_items != total_users:
            self.pagination_controller = PaginationController(
                total_items=total_users,
                items_per_page=self.items_per_page,
                on_page_change=lambda: self._refresh_view(),
            )
        else:
            self.pagination_controller.total_items = total_users
        
        # Get paginated users
        start_idx = self.pagination_controller.start_index
        end_idx = self.pagination_controller.end_index
        users = all_users[start_idx:end_idx]
        
        if not users and total_users == 0:
            return create_empty_state_card(
                icon=ft.Icons.SCHEDULE,
                title="Nincs felhasználó / No users",
                icon_color=DS.GRAY_400,
            )
        
        # Check if current user can manage shifts
        ctx = get_app_context()
        can_manage_shifts = False
        if ctx.is_authenticated():
            try:
                current_user = get_user(ctx.user_id)
                if current_user and current_user.role:
                    role_name = current_user.role.name
                    can_manage_shifts = role_name in [ROLE_MANAGER, ROLE_MAINTENANCE_SUPERVISOR, ROLE_DEVELOPER]
            except Exception as e:
                logger.warning(f"Error checking user permissions: {e}")
                can_manage_shifts = False
        
        # Batch actions bar
        batch_actions_bar = None
        if can_manage_shifts and self.selected_user_ids:
            def on_batch_set_rotation():
                self._batch_set_rotation()
            
            batch_actions_bar = create_batch_actions_bar(
                selected_count=len(self.selected_user_ids),
                actions=[
                    {
                        "text": translator.get_text("shift_schedule.set_rotation") if hasattr(translator, 'get_text') else "Rotáció beállítása",
                        "icon": ft.icons.SCHEDULE,
                        "on_click": on_batch_set_rotation,
                        "bgcolor": DS.ORANGE_500,
                    },
                ],
            )
        
        # Build cards grid
        cards_grid = ft.GridView(
            runs_count=3,  # 3 columns
            max_extent=400,
            spacing=DesignSystem.SPACING_4,
            run_spacing=DesignSystem.SPACING_4,
            child_aspect_ratio=1.1,
        )
        
        for user in users:
            # Get current schedule
            schedule = get_user_shift_schedule(user.id, date.today())
            
            shift_type_display = "-"
            shift_time_display = "-"
            rotation_info = "-"
            shift_type_key = None
            
            if schedule:
                # Map shift_type values to translation keys
                shift_type_key = schedule.shift_type
                if shift_type_key == "triple":
                    shift_type_key = "3_shift"
                elif shift_type_key == "double":
                    shift_type_key = "4_shift"
                
                # Normalize shift_type for comparison
                normalized_shift_type = shift_type_key
                
                if normalized_shift_type == "single":
                    shift_type_display = translator.get_text("shift_schedule.single_shift")
                elif normalized_shift_type in ["3_shift", "4_shift"]:
                    shift_type_display = translator.get_text(f"shift_schedule.{normalized_shift_type}")
                else:
                    shift_type_display = schedule.shift_type or "-"
                
                if normalized_shift_type == "single" and schedule.start_time and schedule.end_time:
                    shift_time_display = f"{schedule.start_time} - {schedule.end_time}"
                
                # Show rotation info for 3_shift
                if normalized_shift_type == "3_shift" and schedule.rotation_start_date and schedule.initial_shift:
                    rotation_info = f"{schedule.rotation_start_date.strftime('%Y-%m-%d')} ({schedule.initial_shift})"
            elif user.shift_type:
                shift_type_key = user.shift_type
                if shift_type_key == "triple":
                    shift_type_key = "3_shift"
                elif shift_type_key == "double":
                    shift_type_key = "4_shift"
                
                if user.shift_type == "single":
                    shift_type_display = translator.get_text("shift_schedule.single_shift")
                elif shift_type_key in ["3_shift", "4_shift"]:
                    shift_type_display = translator.get_text(f"shift_schedule.{shift_type_key}")
                else:
                    shift_type_display = user.shift_type or "-"
                
                if user.shift_type == "single" and user.shift_start_time and user.shift_end_time:
                    shift_time_display = f"{user.shift_start_time} - {user.shift_end_time}"
            
            user_name = user.full_name or user.username
            
            # Determine color based on shift type
            shift_color = DS.ORANGE_500
            if shift_type_key == "single":
                shift_color = DS.BLUE_500
            elif shift_type_key == "3_shift":
                shift_color = DS.PURPLE_500
            elif shift_type_key == "4_shift":
                shift_color = DS.CYAN_500
            
            # Selection checkbox and action button if user can manage shifts
            checkbox = None
            if can_manage_shifts:
                is_selected = user.id in self.selected_user_ids
                checkbox = ft.Checkbox(
                    value=is_selected,
                    on_change=lambda e, uid=user.id: self._on_user_selection_change(uid, e),
                )
            
            # Build card content
            header_row_controls = []
            if checkbox:
                header_row_controls.append(checkbox)
            
            header_row_controls.extend([
                ft.Container(
                    content=ft.Icon(ft.Icons.SCHEDULE, size=24, color=shift_color),
                    padding=ft.padding.all(DesignSystem.SPACING_2),
                    bgcolor=f"{shift_color}15",
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
                        text=shift_type_display,
                        variant="blue",
                        size=12,
                    ),
                ], spacing=DesignSystem.SPACING_1, tight=True, expand=True),
            ])
            
            card_content_items = [
                ft.Row(header_row_controls, spacing=DesignSystem.SPACING_3),
                ft.Container(height=DesignSystem.SPACING_3),
                ft.Column([
                    ft.Row([
                        ft.Text(
                            translator.get_text("shift_schedule.shift_type"),
                            size=11,
                            color=DesignSystem.TEXT_SECONDARY,
                        ),
                        ft.Container(width=DesignSystem.SPACING_2),
                        ft.Text(
                            shift_type_display,
                            size=14,
                            weight=ft.FontWeight.W_500,
                            color=DesignSystem.TEXT_PRIMARY,
                        ),
                    ], spacing=DesignSystem.SPACING_2),
                    ft.Container(height=DesignSystem.SPACING_2),
                    ft.Row([
                        ft.Text(
                            "Időszak / Time Period",
                            size=11,
                            color=DesignSystem.TEXT_SECONDARY,
                        ),
                        ft.Container(width=DesignSystem.SPACING_2),
                        ft.Text(
                            shift_time_display,
                            size=14,
                            weight=ft.FontWeight.W_500,
                            color=DesignSystem.TEXT_PRIMARY,
                        ),
                    ], spacing=DesignSystem.SPACING_2),
                    ft.Container(height=DesignSystem.SPACING_2),
                    ft.Row([
                        ft.Text(
                            translator.get_text("shift_schedule.rotation_info") if hasattr(translator, 'get_text') else "Forgás / Rotation",
                            size=11,
                            color=DesignSystem.TEXT_SECONDARY,
                        ),
                        ft.Container(width=DesignSystem.SPACING_2),
                        ft.Text(
                            rotation_info,
                            size=14,
                            weight=ft.FontWeight.W_500,
                            color=DesignSystem.TEXT_PRIMARY,
                        ),
                    ], spacing=DesignSystem.SPACING_2),
                ], spacing=0, tight=True),
            ]
            
            # Action button if user can manage shifts
            if can_manage_shifts:
                action_button = create_modern_button(
                    text=translator.get_text("shift_schedule.set_rotation") if hasattr(translator, 'get_text') else "Rotáció beállítása",
                    on_click=self._create_rotation_handler(user.id),
                    width=180,
                    bgcolor=DS.ORANGE_500,
                )
                
                card_content_items.append(
                    ft.Container(
                        content=action_button,
                        padding=ft.padding.only(top=DesignSystem.SPACING_3),
                    )
                )
            
            card_content = ft.Column(card_content_items, spacing=DesignSystem.SPACING_2)
            card_content.controls = [c for c in card_content.controls if c is not None]
            
            card = create_tailwind_card(
                content=card_content,
                padding=DesignSystem.SPACING_4,
                elevation=1,
                accent_color=shift_color,
            )
            cards_grid.controls.append(card)
        
        # Build pagination controls
        pagination_controls = create_pagination_controls(
            controller=self.pagination_controller,
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
    
    def _open_rotation_dialog(self, user_id: int):
        """Open dialog to set rotation for a specific user"""
        from services.user_service import get_user
        
        user = get_user(user_id)
        if not user:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Felhasználó nem található / User not found"),
                bgcolor=DS.ERROR,
            )
            self.page.snack_bar.open = True
            self.page.update()
            return
        
        # Get current schedule
        current_schedule = get_user_shift_schedule(user_id, date.today())
        
        # Get current values
        shift_type = user.shift_type or "single"
        shift_start = user.shift_start_time or ""
        shift_end = user.shift_end_time or ""
        rotation_start_date = None
        initial_shift = None
        
        # Convert old shift_type values to new format
        if shift_type == "triple":
            shift_type = "3_shift"
        elif shift_type == "double":
            shift_type = "4_shift"
        
        if current_schedule:
            shift_type = current_schedule.shift_type
            shift_start = current_schedule.start_time or ""
            shift_end = current_schedule.end_time or ""
            rotation_start_date = current_schedule.rotation_start_date
            initial_shift = current_schedule.initial_shift
            
            # Convert old shift_type values to new format
            if shift_type == "triple":
                shift_type = "3_shift"
            elif shift_type == "double":
                shift_type = "4_shift"
        
        # Build form fields
        shift_type_field = create_modern_dropdown(
            label=translator.get_text("shift_schedule.shift_type"),
            options=[
                ft.dropdown.Option(key="single", text=translator.get_text("shift_schedule.single_shift")),
                ft.dropdown.Option(key="3_shift", text=translator.get_text("shift_schedule.3_shift")),
                ft.dropdown.Option(key="4_shift", text=translator.get_text("shift_schedule.4_shift")),
            ],
            value=shift_type,
            width=300,
        )
        
        start_time_field = create_modern_text_field(
            label=translator.get_text("shift_schedule.start_time"),
            value=shift_start,
            hint_text="06:00",
            width=150,
        )
        
        end_time_field = create_modern_text_field(
            label=translator.get_text("shift_schedule.end_time"),
            value=shift_end,
            hint_text="14:00",
            width=150,
        )
        
        # Rotation fields (only for 3_shift)
        default_date_str = rotation_start_date.strftime("%Y-%m-%d") if rotation_start_date else date.today().strftime("%Y-%m-%d")
        rotation_start_date_container, rotation_start_date_field = create_modern_date_field(
            label=translator.get_text("shift_schedule.rotation_start_date"),
            value=default_date_str,
            page=self.page,
        )
        
        initial_shift_field = create_modern_dropdown(
            label=translator.get_text("shift_schedule.initial_shift"),
            options=[
                ft.dropdown.Option("DE", translator.get_text("shift_schedule.shift_morning")),
                ft.dropdown.Option("ÉJ", translator.get_text("shift_schedule.shift_night")),
                ft.dropdown.Option("DU", translator.get_text("shift_schedule.shift_afternoon")),
            ],
            value=initial_shift if initial_shift in ["DE", "ÉJ", "DU"] else "DE",
            width=200,
        )
        
        # Show/hide fields based on shift type
        def on_shift_type_change(e):
            is_single = e.control.value == "single"
            is_3_shift = e.control.value == "3_shift"
            start_time_field.visible = is_single
            end_time_field.visible = is_single
            rotation_start_date_container.visible = is_3_shift
            initial_shift_field.visible = is_3_shift
            # Set default date if switching to 3_shift and date is empty
            if is_3_shift and (not rotation_start_date_field.value or not rotation_start_date_field.value.strip()):
                rotation_start_date_field.value = date.today().strftime("%Y-%m-%d")
                rotation_start_date_field.update()
            self.page.update()
        
        shift_type_field.on_change = on_shift_type_change
        start_time_field.visible = (shift_type == "single")
        end_time_field.visible = (shift_type == "single")
        rotation_start_date_container.visible = (shift_type == "3_shift")
        initial_shift_field.visible = (shift_type == "3_shift")
        
        def save_schedule(e):
            try:
                shift_type_val = shift_type_field.value
                start_time_val = start_time_field.value if shift_type_val == "single" else None
                end_time_val = end_time_field.value if shift_type_val == "single" else None
                
                # Parse rotation parameters for 3_shift
                rotation_start_date_val = None
                initial_shift_val = None
                if shift_type_val == "3_shift":
                    rotation_start_str = rotation_start_date_field.value or ""
                    rotation_start_str = rotation_start_str.strip()
                    if not rotation_start_str:
                        # Default to today if not provided
                        rotation_start_date_val = date.today()
                    else:
                        try:
                            rotation_start_date_val = datetime.strptime(rotation_start_str, "%Y-%m-%d").date()
                        except ValueError:
                            raise ShiftServiceError(f"Érvénytelen dátum formátum: {rotation_start_str}. Használja az YYYY-MM-DD formátumot.")
                    
                    initial_shift_val = initial_shift_field.value
                    if not initial_shift_val or initial_shift_val not in ["DE", "ÉJ", "DU"]:
                        raise ShiftServiceError("Kezdő műszak megadása kötelező 3 műszakos rendszerhez. Válasszon DE, ÉJ vagy DU közül.")
                
                set_user_shift_schedule(
                    user_id=user_id,
                    shift_type=shift_type_val,
                    start_time=start_time_val,
                    end_time=end_time_val,
                    effective_from=datetime.now(),
                    rotation_start_date=rotation_start_date_val,
                    initial_shift=initial_shift_val,
                )
                
                # Close dialog
                self.page.dialog.open = False
                self.page.update()
                
                # Refresh view
                self._refresh_view()
                
                # Show success message
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"{translator.get_text('shift_schedule.schedule_saved')}: {user.full_name or user.username}"),
                    bgcolor=DS.SUCCESS,
                )
                self.page.snack_bar.open = True
                self.page.update()
            except ShiftServiceError as err:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(str(err)),
                    bgcolor=DS.ERROR,
                )
                self.page.snack_bar.open = True
                self.page.update()
            except Exception as err:
                import traceback
                logger.error(f"Error saving shift schedule: {err}\n{traceback.format_exc()}")
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Hiba történt: {str(err)}"),
                    bgcolor=DS.ERROR,
                )
                self.page.snack_bar.open = True
                self.page.update()
        
        dialog_content = ft.Column(
            controls=[
                ft.Text(
                    f"{translator.get_text('shift_schedule.user')}: {user.full_name or user.username}",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Divider(),
                shift_type_field,
                ft.Row(
                    controls=[start_time_field, end_time_field],
                    spacing=10,
                ),
                ft.Row(
                    controls=[
                        ft.Container(content=rotation_start_date_container, expand=True),
                        ft.Container(content=initial_shift_field, width=200),
                    ],
                    spacing=10,
                ),
            ],
            spacing=15,
            width=500,
        )
        
        dialog = ft.AlertDialog(
            title=ft.Text(translator.get_text("shift_schedule.set_rotation_for_user") if hasattr(translator, 'get_text') else "Műszak rotáció beállítása"),
            content=dialog_content,
            actions=[
                ft.TextButton(
                    text=translator.get_text("common.buttons.cancel"),
                    on_click=lambda _: setattr(self.page.dialog, "open", False) or self.page.update(),
                ),
                create_modern_button(
                    text=translator.get_text("shift_schedule.save"),
                    on_click=save_schedule,
                    bgcolor=DS.SUCCESS,
                ),
            ],
        )
        
        self.page.dialog = dialog
        self.page.dialog.open = True
        self.page.update()
    
    def _build_current_schedule_card(self) -> ft.Control:
        """Build card showing current user's shift schedule with rotation settings and autosave"""
        if not self.current_user:
            return ft.Container(
                content=ft.Text(
                    "Nincs bejelentkezve / Not logged in",
                    size=16,
                    color=DS.TEXT_SECONDARY,
                ),
                alignment=ft.alignment.center,
                padding=40,
            )
        
        # Load draft if exists
        autosave_service = get_autosave_service()
        draft = autosave_service.load_draft("shift_schedule", self.current_user_id) if self.current_user_id else None
        if draft:
            draft = draft.get("form_data", {})
        
        # Get current schedule
        current_schedule = get_user_shift_schedule(self.current_user_id, date.today())
        
        # Get user's shift info - prioritize draft > current_schedule > user defaults
        shift_type = "single"
        shift_start = ""
        shift_end = ""
        rotation_start_date = None
        initial_shift = None
        
        if draft:
            # Use values from draft if available
            shift_type = draft.get("shift_type", "single")
            shift_start = draft.get("start_time", "")
            shift_end = draft.get("end_time", "")
            rotation_start_date_str = draft.get("rotation_start_date", "")
            if rotation_start_date_str:
                try:
                    rotation_start_date = datetime.strptime(rotation_start_date_str, "%Y-%m-%d").date()
                except ValueError:
                    rotation_start_date = None
            initial_shift = draft.get("initial_shift", None)
        elif current_schedule:
            # Use values from current_schedule if available
            shift_type = current_schedule.shift_type or "single"
            shift_start = current_schedule.start_time or ""
            shift_end = current_schedule.end_time or ""
            rotation_start_date = current_schedule.rotation_start_date
            initial_shift = current_schedule.initial_shift
        else:
            # Fall back to user defaults
            shift_type = self.current_user.shift_type or "single"
            shift_start = self.current_user.shift_start_time or ""
            shift_end = self.current_user.shift_end_time or ""
        
        # Convert old shift_type values to new format
        if shift_type == "triple":
            shift_type = "3_shift"
        elif shift_type == "double":
            shift_type = "4_shift"
        
        # Build form fields
        shift_type_field = create_modern_dropdown(
            label=translator.get_text("shift_schedule.shift_type"),
            options=[
                ft.dropdown.Option(key="single", text=translator.get_text("shift_schedule.single_shift")),
                ft.dropdown.Option(key="3_shift", text=translator.get_text("shift_schedule.3_shift")),
                ft.dropdown.Option(key="4_shift", text=translator.get_text("shift_schedule.4_shift")),
            ],
            value=shift_type,
            width=200,
        )
        
        start_time_field = create_modern_text_field(
            label=translator.get_text("shift_schedule.start_time"),
            value=shift_start,
            hint_text="06:00",
            width=150,
        )
        
        end_time_field = create_modern_text_field(
            label=translator.get_text("shift_schedule.end_time"),
            value=shift_end,
            hint_text="14:00",
            width=150,
        )
        
        # Rotation fields (only for 3_shift)
        default_date_str = rotation_start_date.strftime("%Y-%m-%d") if rotation_start_date else date.today().strftime("%Y-%m-%d")
        rotation_start_date_container, rotation_start_date_field = create_modern_date_field(
            label=translator.get_text("shift_schedule.rotation_start_date"),
            value=default_date_str,
            page=self.page,
        )
        
        initial_shift_field = create_modern_dropdown(
            label=translator.get_text("shift_schedule.initial_shift"),
            options=[
                ft.dropdown.Option("DE", translator.get_text("shift_schedule.shift_morning")),
                ft.dropdown.Option("ÉJ", translator.get_text("shift_schedule.shift_night")),
                ft.dropdown.Option("DU", translator.get_text("shift_schedule.shift_afternoon")),
            ],
            value=initial_shift or "DE",
            width=200,
        )
        
        # Show/hide fields based on shift type
        def on_shift_type_change(e):
            is_single = e.control.value == "single"
            is_3_shift = e.control.value == "3_shift"
            start_time_field.visible = is_single
            end_time_field.visible = is_single
            rotation_start_date_container.visible = is_3_shift
            initial_shift_field.visible = is_3_shift
            # Set default date if switching to 3_shift and date is empty
            if is_3_shift and (not rotation_start_date_field.value or not rotation_start_date_field.value.strip()):
                rotation_start_date_field.value = date.today().strftime("%Y-%m-%d")
            # Set default initial shift if switching to 3_shift and not set
            if is_3_shift and not initial_shift_field.value:
                initial_shift_field.value = "DE"
            self.page.update()
        
        shift_type_field.on_change = on_shift_type_change
        
        # Set initial visibility based on current shift_type
        is_single = (shift_type == "single")
        is_3_shift = (shift_type == "3_shift")
        start_time_field.visible = is_single
        end_time_field.visible = is_single
        rotation_start_date_container.visible = is_3_shift
        initial_shift_field.visible = is_3_shift
        
        # Autosave handler
        def on_field_change():
            """Handle field change for autosave"""
            if not self.current_user_id:
                return
            draft_data = {
                "shift_type": shift_type_field.value or "single",
                "start_time": start_time_field.value or "",
                "end_time": end_time_field.value or "",
                "rotation_start_date": rotation_start_date_field.value or "",
                "initial_shift": initial_shift_field.value or "DE",
            }
            autosave_service.save_draft("shift_schedule", draft_data, self.current_user_id)
        
        # Attach autosave handlers
        shift_type_field.on_change = lambda e: (on_shift_type_change(e), on_field_change())
        start_time_field.on_change = lambda e: on_field_change()
        end_time_field.on_change = lambda e: on_field_change()
        rotation_start_date_field.on_change = lambda e: on_field_change()
        initial_shift_field.on_change = lambda e: on_field_change()
        
        def save_schedule(e):
            try:
                shift_type_val = shift_type_field.value
                start_time_val = start_time_field.value if shift_type_val == "single" else None
                end_time_val = end_time_field.value if shift_type_val == "single" else None
                
                # Parse rotation parameters for 3_shift
                rotation_start_date_val = None
                initial_shift_val = None
                if shift_type_val == "3_shift":
                    rotation_start_str = rotation_start_date_field.value or ""
                    rotation_start_str = rotation_start_str.strip()
                    if not rotation_start_str:
                        # Default to today if not provided
                        rotation_start_date_val = date.today()
                    else:
                        try:
                            rotation_start_date_val = datetime.strptime(rotation_start_str, "%Y-%m-%d").date()
                        except ValueError:
                            raise ShiftServiceError(f"Érvénytelen dátum formátum: {rotation_start_str}. Használja az YYYY-MM-DD formátumot.")
                    
                    initial_shift_val = initial_shift_field.value
                    if not initial_shift_val or initial_shift_val not in ["DE", "ÉJ", "DU"]:
                        raise ShiftServiceError("Kezdő műszak megadása kötelező 3 műszakos rendszerhez. Válasszon DE, ÉJ vagy DU közül.")
                
                set_user_shift_schedule(
                    user_id=self.current_user_id,
                    shift_type=shift_type_val,
                    start_time=start_time_val,
                    end_time=end_time_val,
                    effective_from=datetime.now(),
                    rotation_start_date=rotation_start_date_val,
                    initial_shift=initial_shift_val,
                )
                
                # Clear draft after successful save
                autosave_service.delete_draft("shift_schedule", self.current_user_id)
                
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(translator.get_text("shift_schedule.schedule_saved")),
                    bgcolor=DS.SUCCESS,
                )
                self.page.snack_bar.open = True
                self.page.update()
                
                # Refresh view
                self._refresh_view()
            except ShiftServiceError as err:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(str(err)),
                    bgcolor=DS.ERROR,
                )
                self.page.snack_bar.open = True
                self.page.update()
            except Exception as err:
                import traceback
                logger.error(f"Error saving shift schedule: {err}\n{traceback.format_exc()}")
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Hiba történt: {str(err)}"),
                    bgcolor=DS.ERROR,
                )
                self.page.snack_bar.open = True
                self.page.update()
        
        save_button = create_modern_button(
            text=translator.get_text("shift_schedule.save"),
            icon=ft.icons.SAVE,
            on_click=save_schedule,
            bgcolor=DS.SUCCESS,
        )
        
        return create_modern_card(
            content=ft.Column(
                controls=[
                    ft.Text(
                        translator.get_text("shift_schedule.my_shift_schedule") if hasattr(translator, 'get_text') else "Saját műszak beosztás / My Shift Schedule",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Divider(height=1),
                    ft.Row(
                        controls=[shift_type_field],
                        spacing=10,
                    ),
                    ft.Row(
                        controls=[start_time_field, end_time_field],
                        spacing=10,
                    ),
                    ft.Row(
                        controls=[rotation_start_date_container, initial_shift_field],
                        spacing=10,
                    ),
                    ft.Container(height=10),
                    ft.Row(
                        controls=[save_button],
                        alignment=ft.MainAxisAlignment.END,
                    ),
                ],
                spacing=15,
            ),
            padding=20,
        )
    
    def _on_search_change(self, e):
        """Handle search query change"""
        self.search_query = e.control.value or ""
        # Reset to first page when searching
        if self.pagination_controller:
            self.pagination_controller.current_page = 1
        self._refresh_view()
    
    def _on_items_per_page_change(self, value: int):
        """Handle items per page change"""
        self.items_per_page = value
        if self.pagination_controller:
            self.pagination_controller.items_per_page = value
            self.pagination_controller.current_page = 1
        self._refresh_view()
    
    def _on_user_selection_change(self, user_id: int, e):
        """Handle user selection checkbox change"""
        if e.control.value:
            self.selected_user_ids.add(user_id)
        else:
            self.selected_user_ids.discard(user_id)
        self._refresh_view()
    
    def _batch_set_rotation(self):
        """Batch set rotation for selected users"""
        if not self.selected_user_ids:
            return
        
        # Open dialog to set rotation for multiple users
        shift_type_field = create_modern_dropdown(
            label=translator.get_text("shift_schedule.shift_type"),
            options=[
                ft.dropdown.Option(key="single", text=translator.get_text("shift_schedule.single_shift")),
                ft.dropdown.Option(key="3_shift", text=translator.get_text("shift_schedule.3_shift")),
                ft.dropdown.Option(key="4_shift", text=translator.get_text("shift_schedule.4_shift")),
            ],
            value="3_shift",
            width=300,
        )
        
        start_time_field = create_modern_text_field(
            label=translator.get_text("shift_schedule.start_time"),
            hint_text="06:00",
            width=150,
        )
        
        end_time_field = create_modern_text_field(
            label=translator.get_text("shift_schedule.end_time"),
            hint_text="14:00",
            width=150,
        )
        
        default_date_str = date.today().strftime("%Y-%m-%d")
        rotation_start_date_container, rotation_start_date_field = create_modern_date_field(
            label=translator.get_text("shift_schedule.rotation_start_date"),
            value=default_date_str,
            page=self.page,
        )
        
        initial_shift_field = create_modern_dropdown(
            label=translator.get_text("shift_schedule.initial_shift"),
            options=[
                ft.dropdown.Option("DE", translator.get_text("shift_schedule.shift_morning")),
                ft.dropdown.Option("ÉJ", translator.get_text("shift_schedule.shift_night")),
                ft.dropdown.Option("DU", translator.get_text("shift_schedule.shift_afternoon")),
            ],
            value="DE",
            width=200,
        )
        
        # Show/hide fields based on shift type
        def on_shift_type_change(e):
            is_single = e.control.value == "single"
            is_3_shift = e.control.value == "3_shift"
            start_time_field.visible = is_single
            end_time_field.visible = is_single
            rotation_start_date_container.visible = is_3_shift
            initial_shift_field.visible = is_3_shift
            self.page.update()
        
        shift_type_field.on_change = on_shift_type_change
        start_time_field.visible = False
        end_time_field.visible = False
        rotation_start_date_container.visible = True
        initial_shift_field.visible = True
        
        def save_batch_rotation(e):
            try:
                shift_type_val = shift_type_field.value
                start_time_val = start_time_field.value if shift_type_val == "single" else None
                end_time_val = end_time_field.value if shift_type_val == "single" else None
                
                # Parse rotation parameters for 3_shift
                rotation_start_date_val = None
                initial_shift_val = None
                if shift_type_val == "3_shift":
                    rotation_start_str = rotation_start_date_field.value or ""
                    rotation_start_str = rotation_start_str.strip()
                    if not rotation_start_str:
                        rotation_start_date_val = date.today()
                    else:
                        try:
                            rotation_start_date_val = datetime.strptime(rotation_start_str, "%Y-%m-%d").date()
                        except ValueError:
                            raise ShiftServiceError(f"Érvénytelen dátum formátum: {rotation_start_str}. Használja az YYYY-MM-DD formátumot.")
                    
                    initial_shift_val = initial_shift_field.value
                    if not initial_shift_val or initial_shift_val not in ["DE", "ÉJ", "DU"]:
                        raise ShiftServiceError("Kezdő műszak megadása kötelező 3 műszakos rendszerhez. Válasszon DE, ÉJ vagy DU közül.")
                
                # Apply to all selected users
                success_count = 0
                failed_count = 0
                for user_id in list(self.selected_user_ids):
                    try:
                        set_user_shift_schedule(
                            user_id=user_id,
                            shift_type=shift_type_val,
                            start_time=start_time_val,
                            end_time=end_time_val,
                            effective_from=datetime.now(),
                            rotation_start_date=rotation_start_date_val,
                            initial_shift=initial_shift_val,
                        )
                        success_count += 1
                    except Exception as err:
                        logger.error(f"Error setting shift schedule for user {user_id}: {err}")
                        failed_count += 1
                
                self.selected_user_ids.clear()
                self.page.dialog.open = False
                self.page.update()
                self._refresh_view()
                
                message = f"{success_count} {translator.get_text('shift_schedule.schedule_saved')}"
                if failed_count > 0:
                    message += f", {failed_count} {translator.get_text('common.messages.operation_failed')}"
                
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(message),
                    bgcolor=DS.SUCCESS if failed_count == 0 else DS.WARNING,
                )
                self.page.snack_bar.open = True
                self.page.update()
            except ShiftServiceError as err:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(str(err)),
                    bgcolor=DS.ERROR,
                )
                self.page.snack_bar.open = True
                self.page.update()
            except Exception as err:
                import traceback
                logger.error(f"Error saving batch shift schedule: {err}\n{traceback.format_exc()}")
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Hiba történt: {str(err)}"),
                    bgcolor=DS.ERROR,
                )
                self.page.snack_bar.open = True
                self.page.update()
        
        dialog_content = ft.Column(
            controls=[
                ft.Text(
                    f"{len(self.selected_user_ids)} {translator.get_text('shift_schedule.user') if hasattr(translator, 'get_text') else 'Felhasználó'}",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Divider(),
                shift_type_field,
                ft.Row(
                    controls=[start_time_field, end_time_field],
                    spacing=10,
                ),
                ft.Row(
                    controls=[
                        ft.Container(content=rotation_start_date_container, expand=True),
                        ft.Container(content=initial_shift_field, width=200),
                    ],
                    spacing=10,
                ),
            ],
            spacing=15,
            width=500,
        )
        
        dialog = ft.AlertDialog(
            title=ft.Text(translator.get_text("shift_schedule.set_rotation") if hasattr(translator, 'get_text') else "Műszak rotáció beállítása"),
            content=dialog_content,
            actions=[
                ft.TextButton(
                    text=translator.get_text("common.buttons.cancel"),
                    on_click=lambda _: setattr(self.page.dialog, "open", False) or self.page.update(),
                ),
                create_modern_button(
                    text=translator.get_text("shift_schedule.save"),
                    on_click=save_batch_rotation,
                    bgcolor=DS.SUCCESS,
                ),
            ],
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def _on_export_click(self, e):
        """Handle export button click"""
        try:
            # Get all users (not just current page)
            all_users = list_all_users()
            
            # Filter by role if needed
            if self.role_filter:
                all_users = [u for u in all_users if u.role and u.role.name == self.role_filter]
            
            # Apply search filter if exists
            if self.search_query:
                search_lower = self.search_query.lower()
                filtered_users = []
                for user in all_users:
                    user_name = (user.full_name or user.username or "").lower()
                    if search_lower in user_name:
                        filtered_users.append(user)
                all_users = filtered_users
            
            # Prepare data for export
            export_data = []
            for user in all_users:
                schedule = get_user_shift_schedule(user.id, date.today())
                user_name = user.full_name or user.username
                
                shift_type_display = "-"
                shift_time_display = "-"
                rotation_info = "-"
                
                if schedule:
                    shift_type_key = schedule.shift_type
                    if shift_type_key == "triple":
                        shift_type_key = "3_shift"
                    elif shift_type_key == "double":
                        shift_type_key = "4_shift"
                    
                    if shift_type_key == "single":
                        shift_type_display = translator.get_text("shift_schedule.single_shift")
                    elif shift_type_key in ["3_shift", "4_shift"]:
                        shift_type_display = translator.get_text(f"shift_schedule.{shift_type_key}")
                    
                    if shift_type_key == "single" and schedule.start_time and schedule.end_time:
                        shift_time_display = f"{schedule.start_time} - {schedule.end_time}"
                    
                    if shift_type_key == "3_shift" and schedule.rotation_start_date and schedule.initial_shift:
                        rotation_info = f"{schedule.rotation_start_date.strftime('%Y-%m-%d')} ({schedule.initial_shift})"
                
                export_data.append({
                    "ID": user.id,
                    translator.get_text("shift_schedule.user"): user_name,
                    translator.get_text("shift_schedule.shift_type"): shift_type_display,
                    "Időszak / Time Period": shift_time_display,
                    translator.get_text("shift_schedule.rotation_info") if hasattr(translator, 'get_text') else "Forgás / Rotation": rotation_info,
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
            default_filename = f"shift_schedules_{self.current_year}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            file_picker.save_file(
                dialog_title=translator.get_text("common.buttons.export"),
                file_name=default_filename,
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["csv"]
            )
        except Exception as ex:
            logger.error(f"Error exporting shift schedules: {ex}", exc_info=True)
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"{translator.get_text('common.messages.error_occurred')}: {str(ex)}"),
                bgcolor=DS.ERROR,
            )
            self.page.snack_bar.open = True
            self.page.update()
