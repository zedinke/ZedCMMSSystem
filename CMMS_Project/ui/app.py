"""
Flet UI belépési pont
"""

import flet as ft
# Compatibility for flet 0.23.2 - Icons are strings, not ft.Icons
if not hasattr(ft, 'Icons'):
    from utils.flet_icons import Icons
    ft.Icons = Icons
import sys
import platform

from services import auth_service
from services.context_service import set_app_context, clear_app_context, get_app_context
from localization.translator import translator
from ui.screens.login_screen import LoginScreen
from ui.screens.dashboard_screen import DashboardScreen
from ui.screens.inventory_screen import InventoryScreen
from ui.screens.assets_screen import AssetsScreen
from ui.screens.service_records_screen import ServiceRecordsScreen
from ui.screens.pm_screen import PMScreen
from ui.screens.settings_screen import SettingsScreen
from ui.screens.worksheet_screen import WorksheetScreen
from ui.screens.user_management_screen import UserManagementScreen
from ui.screens.developer_tools_screen import DeveloperToolsScreen
from ui.screens.reports_screen import ReportsScreen
from ui.screens.documentation_screen import DocumentationScreen
from ui.screens.log_screen import LogScreen
from ui.screens.vacation_screen import VacationScreen
from ui.screens.shift_schedule_screen import ShiftScheduleScreen
from ui.screens.permissions_screen import PermissionsScreen
from ui.screens.inventory_audit_screen import InventoryAuditScreen
from ui.screens.storage_screen import StorageScreen
from ui.screens.production_line_screen import ProductionLineScreen
from utils.permissions import (
    can_view_dashboard,
    can_view_inventory,
    can_view_assets,
    can_view_worksheets,
    can_view_pm,
    can_view_settings,
    can_manage_users,
    can_view_developer_tools,
    can_manage_permissions,
    can_view_inventory_audit,
    can_view_storage,
)
from ui.theme import get_app_theme, get_dark_theme
from ui.components.modern_components import DesignSystem
from ui.components.modern_card import create_tailwind_card


class AppState:
    def __init__(self):
        self.view = "login"
        self.token = None
        self.theme_mode = ft.ThemeMode.SYSTEM
        self.database_mode = "production"  # "production" or "learning"

    def is_authenticated(self) -> bool:
        return self.view != "login" and self.token is not None


state = AppState()

def get_screen_size():
    """Get screen resolution"""
    try:
        if platform.system() == "Windows":
            import ctypes
            user32 = ctypes.windll.user32
            width = user32.GetSystemMetrics(0)  # SM_CXSCREEN
            height = user32.GetSystemMetrics(1)  # SM_CYSCREEN
            return width, height
        elif platform.system() == "Linux":
            try:
                import subprocess
                output = subprocess.check_output(['xrandr']).decode()
                for line in output.split('\n'):
                    if ' connected' in line:
                        parts = line.split()
                        for part in parts:
                            if 'x' in part and '+' in part:
                                res = part.split('+')[0]
                                width, height = map(int, res.split('x'))
                                return width, height
            except:
                pass
        elif platform.system() == "Darwin":  # macOS
            try:
                import subprocess
                output = subprocess.check_output(['system_profiler', 'SPDisplaysDataType']).decode()
                # Parse output to get resolution
                # This is a simplified version
                for line in output.split('\n'):
                    if 'Resolution:' in line:
                        parts = line.split('Resolution:')[1].strip().split()
                        if len(parts) >= 2:
                            width = int(parts[0])
                            height = int(parts[2] if 'x' in parts[1] else parts[1])
                            return width, height
            except:
                pass
    except Exception as e:
        print(f"Error getting screen size: {e}")
    
    # Fallback to default values
    return 1920, 1080


def start_ui(page: ft.Page):
    page.title = translator.get_text("app.title")
    
    # Set window to maximized (fullscreen windowed mode)
    page.window.maximized = True
    page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
    page.vertical_alignment = ft.MainAxisAlignment.START
    
    # Apply modern theme
    page.theme = get_app_theme()
    page.dark_theme = get_dark_theme()
    page.theme_mode = state.theme_mode

    # Define _on_login_success here so it can access render()
    def _on_login_success(token: str, user_info: dict = None):
        print(f"[APP] _on_login_success called with token: {token[:20]}...")
        try:
            # If user_info not provided, validate session (shouldn't happen with new login)
            if user_info is None:
                print("[APP] User info not provided, validating session...")
                user_info = auth_service.validate_session(token)
            print(f"[APP] User info: {user_info.get('username')}")
            set_app_context(user_info, token)
            print("[APP] Context set")
            state.token = token
            state.view = "dashboard"
            print(f"[APP] State updated: token={bool(state.token)}, view={state.view}")
            
            # Load user's language preference
            user_lang = user_info.get("language", "hu")
            if user_lang in translator.get_available_languages():
                translator.set_current_language(user_lang)
            print(f"[APP] Language set to: {user_lang}")
            
            # Check for updates automatically on startup (if enabled)
            _check_updates_on_startup(page)
            
            print("[APP] Navigating to dashboard...")
            try:
                # Set route and manually trigger on_route_change since page.go() from background thread
                # might not trigger the event handler properly
                page.route = "/dashboard"
                print(f"[APP] Route set to: {page.route}")
                # Manually trigger route change handler
                # Create a simple event-like object for on_route_change
                class RouteEvent:
                    pass
                route_event = RouteEvent()
                on_route_change(route_event)
                print("[APP] on_route_change called, render should be triggered")
            except Exception as ex:
                print(f"[APP] Error navigating to dashboard: {ex}")
                import traceback
                traceback.print_exc()
                # Fallback: try to set route directly and render
                try:
                    print("[APP] Using fallback: setting state and calling render() directly...")
                    state.view = "dashboard"
                    page.route = "/dashboard"
                    render()
                except Exception as ex2:
                    print(f"[APP] Fallback also failed: {ex2}")
                    import traceback
                    traceback.print_exc()
        except Exception as ex:
            print(f"[APP] Error in _on_login_success: {ex}")
            import traceback
            traceback.print_exc()

    login_screen = LoginScreen(on_login_success=_on_login_success)
    dashboard = DashboardScreen(on_logout=lambda: _logout(page))
    inventory = InventoryScreen(page)
    assets = AssetsScreen(page)
    pm = PMScreen()
    worksheets = WorksheetScreen()
    service_records = ServiceRecordsScreen(page)
    reports = ReportsScreen()  # Create once and reuse
    settings = SettingsScreen(on_language_change=lambda lang: _on_language_change(page, lang), on_logout=lambda: _logout(page))
    user_management = UserManagementScreen(page)
    developer_tools = DeveloperToolsScreen(page)
    documentation = DocumentationScreen(page)
    log_screen = LogScreen(page)
    vacation_screen = VacationScreen(page)
    permissions_screen = PermissionsScreen(page)

    # Flag to prevent duplicate rendering (using list to allow modification in nested function)
    _is_rendering = [False]
    
    def render():
        # Prevent duplicate rendering
        if _is_rendering[0]:
            print("[UI] render() already in progress, skipping...")
            return
        _is_rendering[0] = True
        
        try:
            # Save current dialog state before clearing
            current_dialog = getattr(page, 'dialog', None)
            dialog_was_open = current_dialog is not None and getattr(current_dialog, 'open', False)
            
            # IMPORTANT: Always clear controls first to prevent duplication
            # This ensures that even if render() is called multiple times, we don't duplicate content
            page.controls.clear()
            
            # Clear floating action button before rendering new view
            page.floating_action_button = None
            # Clear dialog when going to login screen
            if state.view == "login":
                page.dialog = None
                dialog_was_open = False
            # Don't clear dialog - let it persist if it was open
            # page.dialog will be set by individual screens if needed
            try:
                print("[UI] render view=", state.view, "controls count before add:", len(page.controls))
                if state.view == "login":
                    page.add(login_screen.view(page))
                else:
                    inventory_audit = InventoryAuditScreen()
                    storage_screen = StorageScreen(page)
                    production_line_screen = ProductionLineScreen(page)
                    from ui.screens.system_documentation_screen import SystemDocumentationScreen
                    system_doc_screen = SystemDocumentationScreen(page)
                    page.add(_layout_with_nav(page, {
                        "dashboard": dashboard.view,
                        "production_line": lambda p: production_line_screen.view(p),
                        "assets": assets.view,
                        "pm": pm.view,
                        "worksheets": worksheets.view,
                        "service_records": service_records.view,
                        "inventory": inventory.view,
                        "storage": lambda p: storage_screen.view(p),
                        "inventory_audit": inventory_audit.view,
                        "reports": reports.view,
                        "vacation": vacation_screen.view,
                        "shift_schedule": lambda p: ShiftScheduleScreen(p).view(p),
                        "users": lambda p: user_management.build(),
                        "permissions": lambda p: permissions_screen.view(p),
                        "logs": log_screen.view,
                        "documentation": lambda p: system_doc_screen.view(p),
                        "developer": lambda p: developer_tools.view(p),
                        "settings": settings.view,
                    }))
                print("[UI] render completed, controls count after add:", len(page.controls))
            except Exception as ex:
                # Surface error instead of blank page
                import traceback
                traceback.print_exc()
                page.add(ft.Container(
                    content=ft.Text(f"UI error: {ex}", color="red"),
                    padding=20,
                ))
            # Restore dialog if it was open before render
            if dialog_was_open and current_dialog is not None:
                print(f"[UI] Restoring dialog after render - dialog.open={current_dialog.open}")
                page.dialog = current_dialog
                current_dialog.open = True
                print(f"[UI] Dialog restored - page.dialog exists={page.dialog is not None}, dialog.open={current_dialog.open}")
            page.update()
            # Double-check dialog after update
            if dialog_was_open and current_dialog is not None and page.dialog != current_dialog:
                print("[UI] WARNING: Dialog was lost after render update, restoring...")
                page.dialog = current_dialog
                current_dialog.open = True
                page.update()
        finally:
            _is_rendering[0] = False
    
    # Store render callback in page for theme toggle
    page._render_callback = render

    def on_route_change(e):
        print(f"[ROUTE] on_route_change triggered, event: {e}")
        print(f"[ROUTE] page.route: {page.route}")
        # route alap logika: /dashboard, /inventory, /assets, /pm, /login, /worksheets/*, /users, /developer
        route_str = page.route.lstrip("/") or "dashboard"
        # Handle route refresh bounce (e.g., vacation_refresh -> vacation)
        if route_str.endswith("_refresh"):
            route_str = route_str.replace("_refresh", "")
        route = route_str
        print(f"[UI] route change -> {route}")
        if route == "login":
            state.view = "login"
            state.token = None
            clear_app_context()
            # Clear page controls and dialogs when going to login
            page.controls.clear()
            page.dialog = None
            page.floating_action_button = None
        elif not state.is_authenticated():
            state.view = "login"
            # Clear page controls and dialogs when not authenticated
            page.controls.clear()
            page.dialog = None
            page.floating_action_button = None
        elif route.startswith("worksheets"):
            # Support sub-routes: worksheets, worksheets/create, worksheets/detail/<id>
            worksheets.set_mode_from_route(route)
            state.view = "worksheets"
        elif route in {"dashboard", "production_line", "inventory", "inventory_audit", "assets", "pm", "service_records", "reports", "settings", "users", "developer", "documentation", "logs", "vacation", "shift_schedule", "permissions", "storage"}:
            state.view = route
        else:
            state.view = "dashboard"
        render()

    page.on_route_change = on_route_change
    render()


def _layout_with_nav(page: ft.Page, views: dict):
    print("[UI] build layout for view=", state.view)
    
    # Build navigation items based on permissions (using context, not user object)
    nav_data = []  # List of (route, label, icon) tuples
    
    labels = {
        "dashboard": translator.get_text("menu.dashboard"),
        "production_line": translator.get_text("menu.production_line"),
        "inventory": translator.get_text("menu.inventory"),
        "inventory_audit": translator.get_text("menu.inventory_audit"),
        "assets": translator.get_text("menu.assets"),
        "pm": translator.get_text("menu.preventive_maintenance"),
        "worksheets": translator.get_text("menu.worksheets"),
        "reports": translator.get_text("menu.reports"),
        "users": "Felhasználók / Users",
        "developer": "Fejlesztői Eszközök / Developer Tools",
        "settings": translator.get_text("menu.settings"),
        "documentation": translator.get_text("menu.documentation"),
        "logs": translator.get_text("menu.log"),
        "vacation": translator.get_text("menu.vacation"),
        "shift_schedule": translator.get_text("menu.shift_schedule"),
        "permissions": translator.get_text("menu.permissions"),
        "service_records": translator.get_text("menu.service_records"),
        "storage": translator.get_text("menu.storage"),
    }
    
    icons_map = {
        "dashboard": ft.Icons.DASHBOARD,
        "production_line": ft.Icons.SETTINGS_APPLICATIONS if hasattr(ft.Icons, 'SETTINGS_APPLICATIONS') else (ft.Icons.TUNE if hasattr(ft.Icons, 'TUNE') else ft.Icons.SETTINGS),
        "inventory": ft.Icons.INVENTORY_2,
        "inventory_audit": ft.Icons.ASSESSMENT if hasattr(ft.Icons, 'ASSESSMENT') else (ft.Icons.CHECKLIST if hasattr(ft.Icons, 'CHECKLIST') else ft.Icons.INVENTORY_2),
        "assets": ft.Icons.PRECISION_MANUFACTURING if hasattr(ft.Icons, 'PRECISION_MANUFACTURING') else ft.Icons.FACTORY,
        "pm": ft.Icons.CONSTRUCTION if hasattr(ft.Icons, 'CONSTRUCTION') else ft.Icons.BUILD,
        "worksheets": ft.Icons.ASSIGNMENT if hasattr(ft.Icons, 'ASSIGNMENT') else ft.Icons.DESCRIPTION,
        "reports": ft.Icons.BAR_CHART if hasattr(ft.Icons, 'BAR_CHART') else ft.Icons.ANALYTICS,
        "users": ft.Icons.GROUP if hasattr(ft.Icons, 'GROUP') else ft.Icons.PEOPLE,
        "developer": ft.Icons.DEVELOPER_MODE if hasattr(ft.Icons, 'DEVELOPER_MODE') else ft.Icons.CODE,
        "documentation": ft.Icons.DESCRIPTION if hasattr(ft.Icons, 'DESCRIPTION') else ft.Icons.ASSIGNMENT,
        "logs": ft.Icons.HISTORY if hasattr(ft.Icons, 'HISTORY') else ft.Icons.LIST,
        "vacation": ft.Icons.CALENDAR_MONTH if hasattr(ft.Icons, 'CALENDAR_MONTH') else ft.Icons.CALENDAR_TODAY,
        "shift_schedule": ft.Icons.SCHEDULE if hasattr(ft.Icons, 'SCHEDULE') else ft.Icons.ACCESS_TIME,
        "permissions": ft.Icons.LOCK if hasattr(ft.Icons, 'LOCK') else ft.Icons.SECURITY,
        "settings": ft.Icons.TUNE if hasattr(ft.Icons, 'TUNE') else ft.Icons.SETTINGS,
        "storage": ft.Icons.WAREHOUSE if hasattr(ft.Icons, 'WAREHOUSE') else ft.Icons.INVENTORY_2,
        "service_records": ft.Icons.BUILD_CIRCLE if hasattr(ft.Icons, 'BUILD_CIRCLE') else (ft.Icons.SETTINGS_APPLICATIONS if hasattr(ft.Icons, 'SETTINGS_APPLICATIONS') else ft.Icons.BUILD),
    }
    
    # ========================================================================
    # 1. ÁTTEKINTÉS / OVERVIEW
    # ========================================================================
    if can_view_dashboard():
        nav_data.append(("dashboard", labels["dashboard"], icons_map["dashboard"]))
    
        # ========================================================================
        # 2. ESZKÖZKEZELÉS / ASSET MANAGEMENT
        # ========================================================================
        if can_view_assets():
            nav_data.append(("production_line", labels["production_line"], icons_map["production_line"]))
            nav_data.append(("assets", labels["assets"], icons_map["assets"]))
        if can_view_inventory():
            nav_data.append(("inventory", labels["inventory"], icons_map["inventory"]))
    if can_view_pm():
        nav_data.append(("pm", labels["pm"], icons_map["pm"]))
    if can_view_worksheets():
        nav_data.append(("worksheets", labels["worksheets"], icons_map["worksheets"]))
    # Service Records - szerviz feljegyzések
    nav_data.append(("service_records", labels["service_records"], icons_map["service_records"]))
    
    # ========================================================================
    # 3. KÉSZLETKEZELÉS / INVENTORY MANAGEMENT
    # ========================================================================
    # Storage - show if user has inventory view permission (storage is part of inventory)
    if can_view_inventory() or can_view_storage():
        nav_data.append(("storage", labels["storage"], icons_map["storage"]))
    # Inventory Audit
    try:
        has_perm = can_view_inventory_audit()
        if has_perm:
            nav_data.append(("inventory_audit", labels["inventory_audit"], icons_map["inventory_audit"]))
    except Exception as e:
        # Show anyway if there's an error (backward compatibility)
        nav_data.append(("inventory_audit", labels["inventory_audit"], icons_map["inventory_audit"]))
    
    # ========================================================================
    # 4. JELENTÉSEK / REPORTS
    # ========================================================================
    if can_view_dashboard():
        nav_data.append(("reports", labels["reports"], icons_map["reports"]))
    
    # ========================================================================
    # 5. EMBERI ERŐFORRÁSOK / HUMAN RESOURCES
    # ========================================================================
    nav_data.append(("vacation", labels["vacation"], icons_map["vacation"]))
    nav_data.append(("shift_schedule", labels["shift_schedule"], icons_map["shift_schedule"]))
    
    # ========================================================================
    # 6. RENDSZERKEZELÉS / SYSTEM ADMINISTRATION
    # ========================================================================
    if can_manage_users():
        nav_data.append(("users", labels["users"], icons_map["users"]))
    if can_manage_permissions():
        nav_data.append(("permissions", labels["permissions"], icons_map["permissions"]))
    nav_data.append(("logs", labels["logs"], icons_map["logs"]))
    if can_view_settings():
        nav_data.append(("settings", labels["settings"], icons_map["settings"]))
    
    # ========================================================================
    # 7. FEJLESZTŐI ESZKÖZÖK / DEVELOPER TOOLS
    # ========================================================================
    if can_view_dashboard():
        nav_data.append(("documentation", labels["documentation"], icons_map["documentation"]))
    if can_view_developer_tools():
        nav_data.append(("developer", labels["developer"], icons_map["developer"]))
    
    # Extract routes
    nav_routes = [route for route, _, _ in nav_data]
    
    # Find selected index
    try:
        selected_index = nav_routes.index(state.view) if state.view in nav_routes else 0
    except ValueError:
        selected_index = 0
    
    # Color mapping for menu items - vibrant Tailwind CSS colors
    menu_colors = {
        "dashboard": (DesignSystem.EMERALD_500, DesignSystem.EMERALD_100, "emerald"),
        "production_line": (DesignSystem.BLUE_600, DesignSystem.BLUE_100, "blue"),
        "inventory": (DesignSystem.BLUE_500, DesignSystem.BLUE_100, "blue"),
        "inventory_audit": (DesignSystem.AMBER_500, DesignSystem.AMBER_100, "amber"),
        "assets": (DesignSystem.PURPLE_500, DesignSystem.PURPLE_100, "purple"),
        "pm": (DesignSystem.ORANGE_500, DesignSystem.ORANGE_100, "orange"),
        "worksheets": (DesignSystem.CYAN_500, DesignSystem.CYAN_100, "cyan"),
        "reports": (DesignSystem.PINK_500, DesignSystem.PINK_100, "pink"),
        "users": (DesignSystem.BLUE_600, DesignSystem.BLUE_100, "blue"),
        "developer": (DesignSystem.PURPLE_600, DesignSystem.PURPLE_100, "purple"),
        "documentation": (DesignSystem.EMERALD_600, DesignSystem.EMERALD_100, "emerald"),
        "logs": (DesignSystem.GRAY_600, DesignSystem.GRAY_100, None),
        "vacation": (DesignSystem.CYAN_600, DesignSystem.CYAN_100, "cyan"),
        "shift_schedule": (DesignSystem.ORANGE_600, DesignSystem.ORANGE_100, "orange"),
        "permissions": (DesignSystem.PINK_600, DesignSystem.PINK_100, "pink"),
        "settings": (DesignSystem.GRAY_700, DesignSystem.GRAY_100, None),
    }
    
    # Define menu categories with their items
    menu_categories = {
        "overview": {
            "label": translator.get_text("menu.category.overview", default="Áttekintés / Overview"),
            "items": []
        },
        "asset_management": {
            "label": translator.get_text("menu.category.asset_management", default="Eszközkezelés / Asset Management"),
            "items": []
        },
        "inventory_management": {
            "label": translator.get_text("menu.category.inventory_management", default="Készletkezelés / Inventory Management"),
            "items": []
        },
        "reports": {
            "label": translator.get_text("menu.category.reports", default="Jelentések / Reports"),
            "items": []
        },
        "human_resources": {
            "label": translator.get_text("menu.category.human_resources", default="Emberi Erőforrások / Human Resources"),
            "items": []
        },
        "system_admin": {
            "label": translator.get_text("menu.category.system_admin", default="Rendszerkezelés / System Administration"),
            "items": []
        },
        "developer_tools": {
            "label": translator.get_text("menu.category.developer_tools", default="Fejlesztői Eszközök / Developer Tools"),
            "items": []
        }
    }
    
    # Categorize menu items
    for route, label, icon in nav_data:
        if route == "dashboard":
            menu_categories["overview"]["items"].append((route, label, icon))
        elif route in ["production_line", "assets", "inventory", "pm", "worksheets", "service_records"]:
            menu_categories["asset_management"]["items"].append((route, label, icon))
        elif route in ["storage", "inventory_audit"]:
            menu_categories["inventory_management"]["items"].append((route, label, icon))
        elif route == "reports":
            menu_categories["reports"]["items"].append((route, label, icon))
        elif route in ["vacation", "shift_schedule"]:
            menu_categories["human_resources"]["items"].append((route, label, icon))
        elif route in ["users", "permissions", "logs", "settings"]:
            menu_categories["system_admin"]["items"].append((route, label, icon))
        elif route in ["documentation", "developer"]:
            menu_categories["developer_tools"]["items"].append((route, label, icon))
    
    # Build categorized navigation with collapsible sections
    nav_controls = []
    
    # Store expanded state in page
    if not hasattr(page, '_menu_expanded'):
        page._menu_expanded = {
            "overview": True,
            "asset_management": True,
            "inventory_management": True,
            "reports": True,
            "human_resources": True,
            "system_admin": True,
            "developer_tools": True,
        }
    
    def create_category_section(category_key: str, category_data: dict):
        """Create a collapsible category section"""
        items = category_data["items"]
        if not items:
            return None
        
        label = category_data["label"]
        is_expanded = page._menu_expanded.get(category_key, True)
        
        # Category header
        expand_icon = ft.Icons.EXPAND_LESS if is_expanded else ft.Icons.EXPAND_MORE
        if not hasattr(ft.Icons, 'EXPAND_LESS'):
            expand_icon = ft.Icons.KEYBOARD_ARROW_UP if is_expanded else ft.Icons.KEYBOARD_ARROW_DOWN
        
        category_items_column = ft.Column(
            controls=[],
            spacing=DesignSystem.SPACING_2,
            visible=is_expanded,
        )
        
        # Build items for this category
        for route, item_label, icon in items:
            item_idx = nav_routes.index(route) if route in nav_routes else -1
            is_selected = (item_idx == selected_index)
            color, bg_color, variant = menu_colors.get(route, (DesignSystem.GRAY_500, DesignSystem.GRAY_100, None))
            
            # Create card for menu item
            nav_card = create_tailwind_card(
                content=ft.Row([
                    ft.Container(
                        content=ft.Icon(icon, size=20, color=color),
                        padding=ft.padding.all(DesignSystem.SPACING_2),
                        bgcolor=bg_color,
                        border_radius=DesignSystem.RADIUS_MD,
                    ),
                    ft.Text(
                        item_label,
                        size=13,
                        weight=ft.FontWeight.W_600 if is_selected else ft.FontWeight.W_500,
                        color=DesignSystem.TEXT_PRIMARY,
                    ),
                ], spacing=DesignSystem.SPACING_2),
                padding=DesignSystem.SPACING_2,
                elevation=2 if is_selected else 1,
                accent_color=color,
                border_accent=is_selected,
                on_click=lambda e, r=route: _nav_change_by_route(page, r, nav_routes),
            )
            
            # Add selected state styling
            if is_selected:
                nav_card.border = ft.border.all(2, color)
                nav_card.bgcolor = bg_color
            
            category_items_column.controls.append(nav_card)
        
        # Category header with toggle
        expand_btn = ft.IconButton(
            icon=expand_icon,
            icon_size=18,
            tooltip="Összecsuk / Kinyit" if is_expanded else "Kinyit / Expand",
        )
        
        def toggle_category(e, key=category_key, items_col=category_items_column, btn=expand_btn):
            page._menu_expanded[key] = not page._menu_expanded[key]
            items_col.visible = page._menu_expanded[key]
            # Update expand icon
            new_expand_icon = ft.Icons.EXPAND_LESS if page._menu_expanded[key] else ft.Icons.EXPAND_MORE
            if not hasattr(ft.Icons, 'EXPAND_LESS'):
                new_expand_icon = ft.Icons.KEYBOARD_ARROW_UP if page._menu_expanded[key] else ft.Icons.KEYBOARD_ARROW_DOWN
            btn.icon = new_expand_icon
            btn.tooltip = "Összecuk / Collapse" if page._menu_expanded[key] else "Kinyit / Expand"
            page.update()
        
        expand_btn.on_click = lambda e: toggle_category(e, category_key, category_items_column, expand_btn)
        
        category_header = ft.Container(
            content=ft.Row([
                ft.Text(
                    label,
                    size=12,
                    weight=ft.FontWeight.W_700,
                    color=DesignSystem.TEXT_SECONDARY,
                    expand=True,
                ),
                expand_btn,
            ], spacing=DesignSystem.SPACING_1),
            padding=ft.padding.symmetric(horizontal=DesignSystem.SPACING_2, vertical=DesignSystem.SPACING_1),
        )
        
        # Category container
        category_section = ft.Column(
            controls=[
                category_header,
                ft.Container(
                    content=category_items_column,
                    padding=ft.padding.only(left=DesignSystem.SPACING_2),
                ),
            ],
            spacing=DesignSystem.SPACING_1,
            tight=True,
        )
        
        return category_section
    
    # Build all category sections
    for category_key, category_data in menu_categories.items():
        section = create_category_section(category_key, category_data)
        if section:
            nav_controls.append(section)
            nav_controls.append(ft.Container(height=DesignSystem.SPACING_2))  # Spacing between categories
    
    # Create scrollable navigation column
    nav_column = ft.Column(
        controls=nav_controls,
        spacing=DesignSystem.SPACING_1,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )
    
    nav = ft.Container(
        content=nav_column,
        width=286,  # 220 * 1.3 = 286 (30% szélesebb)
        padding=ft.padding.all(DesignSystem.SPACING_3),
        bgcolor=DesignSystem.BG_SECONDARY,
        border=ft.border.only(right=ft.BorderSide(1, DesignSystem.BORDER_COLOR)),
        expand=True,
    )

    try:
        content_view = views.get(state.view, views.get("dashboard"))
        if content_view is None:
            content_view = views.get("dashboard")
        if content_view:
            content = content_view(page)
        else:
            content = ft.Container(
                content=ft.Text("View not found", color="red"),
                padding=20,
            )
    except Exception as ex:
        content = ft.Container(
            content=ft.Text(f"Content error: {ex}", color="red"),
            padding=20,
        )
    
    # Ensure content is not None
    if content is None:
        content = ft.Container(
            content=ft.Text("Content is None", color="red"),
            padding=20,
        )

    # Import global search component and notification bell
    from ui.components.global_search_component import create_global_search_field
    from ui.components.notification_bell_component import create_notification_bell

    # Build topbar Row controls, filtering out None values
    topbar_controls = [
        ft.Text(
            labels.get(state.view, ""), 
            size=24, 
            weight=ft.FontWeight.W_700, 
            color=DesignSystem.TEXT_PRIMARY
        ),
        ft.Column(expand=True),  # Spacer replacement
        create_global_search_field(page),
        ft.Container(width=10),  # Spacing
        create_notification_bell(page),
    ]
    # Filter out None values
    topbar_controls = [c for c in topbar_controls if c is not None]

    topbar = ft.Container(
        content=ft.Row(
            controls=topbar_controls,
            alignment=ft.MainAxisAlignment.START
        ),
        padding=ft.padding.symmetric(horizontal=DesignSystem.SPACING_8, vertical=DesignSystem.SPACING_6),
        bgcolor=DesignSystem.BG_SECONDARY,
        border=ft.border.only(bottom=ft.BorderSide(1, DesignSystem.BORDER_COLOR)),
    )
    
    # Ensure nav is not None
    if nav is None:
        nav = ft.Container(
            content=ft.Column(controls=[], spacing=DesignSystem.SPACING_2),
            width=286,  # 220 * 1.3 = 286 (30% szélesebb)
            padding=ft.padding.all(DesignSystem.SPACING_3),
            bgcolor=DesignSystem.BG_SECONDARY,
        )

    # Build main Column controls, filtering out None values
    main_column_controls = [
        topbar,
        ft.Container(
            content=content,
            expand=True,
            padding=ft.padding.all(DesignSystem.SPACING_8),
            bgcolor=DesignSystem.BG_PRIMARY,
        ),
    ]
    # Filter out None values
    main_column_controls = [c for c in main_column_controls if c is not None]

    # Build main Row controls, filtering out None values
    main_row_controls = [
        ft.Container(
            content=nav,
            bgcolor=DesignSystem.BG_SECONDARY,
            border=ft.border.only(right=ft.BorderSide(1, DesignSystem.BORDER_COLOR)),
            expand=False,  # Fixed width sidebar
        ),
        ft.Container(
            content=ft.Column(
                controls=main_column_controls,
                spacing=0,
                expand=True
            ),
            expand=True,
            bgcolor=DesignSystem.BG_PRIMARY,
        ),
    ]
    # Filter out None values
    main_row_controls = [c for c in main_row_controls if c is not None]

    return ft.Row(
        controls=main_row_controls,
        expand=True,
        spacing=0,
    )


def _nav_change(page: ft.Page, e, nav_routes):
    idx = e.control.selected_index
    if idx < len(nav_routes):
        state.view = nav_routes[idx]
        page.go(f"/{state.view}")


def _nav_change_by_route(page: ft.Page, route: str, nav_routes: list):
    """Navigate to route by clicking on navigation card"""
    if route in nav_routes:
        state.view = route
        page.go(f"/{route}")


def _logout(page: ft.Page):
    """Fast logout - clear local state immediately, logout from server in background"""
    ctx = get_app_context()
    token = ctx.token if ctx else None
    
    # Clear local state immediately (don't wait for server)
    clear_app_context()
    state.token = None
    state.view = "login"
    
    # Clear page controls and dialogs before going to login
    page.controls.clear()
    page.dialog = None
    page.floating_action_button = None
    page.go("/login")
    page.update()  # Update immediately to show login screen
    
    # Logout from server in background thread (non-blocking)
    if token:
        import threading
        def logout_background():
            try:
                auth_service.logout_session(token)
            except Exception as e:
                # Log error but don't block user
                import logging
                logging.getLogger(__name__).warning(f"Background logout failed: {e}")
        
        thread = threading.Thread(target=logout_background, daemon=True)
        thread.start()


def _toggle_theme(page: ft.Page):
    """Toggle theme mode between LIGHT and DARK"""
    import logging
    logger = logging.getLogger(__name__)
    
    # Toggle theme mode
    if state.theme_mode == ft.ThemeMode.LIGHT:
        state.theme_mode = ft.ThemeMode.DARK
    elif state.theme_mode == ft.ThemeMode.DARK:
        state.theme_mode = ft.ThemeMode.LIGHT
    else:
        # If SYSTEM, default to DARK
        state.theme_mode = ft.ThemeMode.DARK
    
    # Update page theme mode
    page.theme_mode = state.theme_mode
    
    # Trigger re-render to update all UI components with new theme
    if hasattr(page, '_render_callback') and page._render_callback:
        try:
            page._render_callback()
        except Exception as e:
            logger.error(f"Error re-rendering after theme change: {e}")
            # Fallback: just update the page
            page.update()
    else:
        # Fallback: just update the page
        page.update()


def _on_language_change(page: ft.Page, lang_code: str):
    """Handle language change: re-render UI with new language"""
    state.view = state.view  # Keep current view
    page.clean()  # Clear page
    start_ui(page)  # Re-render with new language


def _check_updates_on_startup(page: ft.Page):
    """
    Check for updates automatically on startup if enabled
    This runs silently in the background and only shows dialog if update is available
    """
    import threading
    import logging
    from datetime import datetime, timedelta
    from services.update_service import get_update_service
    from services.settings_service import get_setting, get_last_update_check, get_skip_version, set_last_update_check
    from config.app_config import APP_VERSION, UPDATE_CHECK_ENABLED
    from utils.version_utils import normalize_version
    from ui.components.modern_components import DesignSystem
    
    logger = logging.getLogger(__name__)
    
    def check_thread():
        try:
            # Check if auto-update check is enabled
            auto_check_enabled = get_setting("auto_update_check", "true" if UPDATE_CHECK_ENABLED else "false") == "true"
            if not auto_check_enabled:
                logger.debug("Automatic update check is disabled")
                return
            
            # Check frequency setting
            frequency = get_setting("update_check_frequency", "startup")
            if frequency != "startup":
                # For daily/weekly, check last update check time
                last_check_str = get_last_update_check()
                if last_check_str:
                    try:
                        last_check = datetime.fromisoformat(last_check_str)
                        now = datetime.now()
                        
                        if frequency == "daily":
                            # Check if 24 hours have passed
                            if (now - last_check) < timedelta(days=1):
                                logger.debug(f"Daily update check: last check was {(now - last_check).total_seconds() / 3600:.1f} hours ago, skipping")
                                return
                        elif frequency == "weekly":
                            # Check if 7 days have passed
                            if (now - last_check) < timedelta(days=7):
                                logger.debug(f"Weekly update check: last check was {(now - last_check).days} days ago, skipping")
                                return
                    except Exception as e:
                        logger.warning(f"Error parsing last update check time: {e}")
                        # Continue with check if parsing fails
            
            logger.info("Starting automatic update check...")
            
            # Get update service and reload config
            update_service = get_update_service()
            update_service.reload_config()
            
            # Check if GitHub is configured
            if not update_service.github_owner or not update_service.github_repo:
                logger.debug("GitHub repository not configured, skipping automatic update check")
                return
            
            # Get skip version setting
            skip_version = get_skip_version()
            
            # Check for updates
            current_version = normalize_version(APP_VERSION)
            update_info = update_service.check_for_updates(current_version)
            
            # Update last check time
            set_last_update_check(datetime.now().isoformat())
            
            if update_info:
                # Check if this version should be skipped
                if skip_version and skip_version == update_info.version:
                    logger.info(f"Update to version {update_info.version} is skipped (user preference)")
                    return
                
                logger.info(f"Update available: {update_info.version}")
                
                # Show update dialog (Flet handles thread safety for UI updates)
                try:
                    from ui.components.update_dialog import create_update_dialog
                    from services.settings_service import set_skip_version
                    import subprocess
                    import sys
                    from pathlib import Path
                    import os
                    
                    def on_update_now():
                        page.close(dialog)
                        page.update()
                        
                        try:
                            # Find updater.exe (same logic as in settings_screen)
                            updater_paths = [
                                Path(sys.executable).parent / "Updater.exe",
                                Path("Updater.exe"),
                                Path(os.getenv("ProgramFiles", "C:\\Program Files")) / "ArtenceCMMS" / "Updater.exe",
                            ]
                            
                            updater_exe = None
                            for path in updater_paths:
                                if path.exists():
                                    updater_exe = path
                                    break
                            
                            if updater_exe:
                                subprocess.Popen([
                                    str(updater_exe),
                                    "--update",
                                    "--version", update_info.version,
                                    "--url", update_info.download_url,
                                    "--restart",
                                ])
                                page.window_close()
                            else:
                                # Show error snackbar
                                page.snack_bar = ft.SnackBar(
                                    ft.Text("Updater.exe nem található / Updater.exe not found"),
                                    bgcolor=DesignSystem.ERROR
                                )
                                page.snack_bar.open = True
                                page.update()
                        except Exception as ex:
                            logger.error(f"Error starting updater: {ex}", exc_info=True)
                            page.snack_bar = ft.SnackBar(
                                ft.Text(f"Frissítés indítása sikertelen: {ex} / Failed to start update: {ex}"),
                                bgcolor=DesignSystem.ERROR
                            )
                            page.snack_bar.open = True
                            page.update()
                    
                    def on_later():
                        page.close(dialog)
                        page.update()
                    
                    def on_skip():
                        set_skip_version(update_info.version)
                        page.close(dialog)
                        page.update()
                    
                    dialog = create_update_dialog(
                        update_info=update_info,
                        on_update_now=on_update_now,
                        on_later=on_later,
                        on_skip=on_skip if not update_info.critical else None,
                    )
                    page.open(dialog)
                    page.update()
                except Exception as ex:
                    logger.error(f"Error showing update dialog: {ex}", exc_info=True)
            else:
                logger.debug("No updates available")
                
        except Exception as ex:
            logger.error(f"Error during automatic update check: {ex}", exc_info=True)
            # Don't show error to user for automatic checks
    
    # Run check in background thread
    threading.Thread(target=check_thread, daemon=True).start()

