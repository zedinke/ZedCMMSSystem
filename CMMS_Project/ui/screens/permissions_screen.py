"""
Permissions Management Screen
Manage role-based permissions for all menu items and actions
"""

import flet as ft
# Compatibility for flet 0.23.2 - Icons are strings, not ft.Icons
if not hasattr(ft, 'Icons'):
    from utils.flet_icons import Icons
    ft.Icons = Icons
from services.permission_service import (
    get_permission_config,
    update_permission_config,
    can_manage_permissions,
    reset_to_default_permissions,
    get_permission_summary,
    get_roles_at_or_above
)
from services.context_service import get_app_context
from services.user_service import list_roles
from config.roles import ALL_ROLES, MENU_ITEMS, ROLE_HIERARCHY, ROLE_DEVELOPER
from localization.translator import translator
from database.session_manager import SessionLocal
from ui.components.modern_components import (
    create_modern_button,
    create_modern_card,
    create_modern_dropdown,
    create_vibrant_badge,
    DesignSystem,
)
from ui.components.modern_card import (
    create_tailwind_card,
    create_info_card,
)
import logging

logger = logging.getLogger(__name__)


class PermissionsScreen:
    def __init__(self, page: ft.Page):
        self.page = page
        self.config = {}
        self.dropdowns = {}  # Store dropdown references
        self.manage_permission_dropdown = None
        self.search_field = None
        self.summary_role_dropdown = None
        self.summary_content_container = None
        
    def view(self, page: ft.Page):
        self.page = page
        
        # Check permissions
        ctx = get_app_context()
        if not ctx.is_authenticated():
            page.go("/login")
            return
        
        session = SessionLocal()
        try:
            if not can_manage_permissions(ctx.role, session):
                page.snack_bar = ft.SnackBar(
                    ft.Text(translator.get_text("auth.permissions.access_denied"))
                )
                page.snack_bar.open = True
                page.go("/dashboard")
                return
        except Exception as e:
            logger.error(f"Error checking permissions: {e}", exc_info=True)
            page.snack_bar = ft.SnackBar(
                ft.Text(f"Error: {str(e)}")
            )
            page.snack_bar.open = True
            return ft.Text(f"Error loading permissions screen: {str(e)}")
        finally:
            session.close()
        
        # Load configuration
        try:
            self._load_config()
        except Exception as e:
            logger.error(f"Error loading config: {e}", exc_info=True)
            return ft.Text(f"Error loading configuration: {str(e)}")
        
        # Build UI
        try:
            return self._build_view()
        except Exception as e:
            logger.error(f"Error building permissions view: {e}", exc_info=True)
            import traceback
            traceback.print_exc()
            return ft.Text(f"Error building view: {str(e)}")
    
    def _load_config(self):
        """Load current permission configuration"""
        session = SessionLocal()
        try:
            self.config = get_permission_config(session)
        finally:
            session.close()
    
    def _build_view(self):
        """Build the permissions management view"""
        
        # Title
        title = ft.Text(
            translator.get_text("permissions_management.title"),
            size=24,
            weight=ft.FontWeight.BOLD,
            color="#111827"
        )
        
        # Info text
        info_text = ft.Text(
            translator.get_text("permissions_management.description"),
            size=14,
            color="#6B7280",
            italic=True
        )
        
        # Quick actions section
        quick_actions = self._build_quick_actions_section()
        
        # Role hierarchy visualization
        hierarchy_section = self._build_role_hierarchy_section()
        
        # Permission summary
        summary_section = self._build_summary_section()
        
        # Search field
        search_section = self._build_search_section()
        
        # Build table
        try:
            table = self._build_permissions_table()
            logger.info(f"Table built, type: {type(table)}")
            if table is None:
                logger.error("Table is None!")
                table = ft.Text("Hiba: A táblázat nem sikerült létrehozni.")
        except Exception as e:
            logger.error(f"Error building table in _build_view: {e}", exc_info=True)
            import traceback
            traceback.print_exc()
            table = ft.Container(
                content=ft.Text(f"Hiba a táblázat építésekor: {str(e)}", color="red"),
                padding=20
            )
        
        # Manage permission level section
        manage_section = self._build_manage_permission_section()
        
        # Action buttons
        save_button = create_modern_button(
            text=translator.get_text("permissions_management.save"),
            icon=ft.Icons.SAVE,
            on_click=self._handle_save,
            bgcolor="#10B981",
            color="#FFFFFF"
        )
        
        reset_button = create_modern_button(
            text=translator.get_text("permissions_management.reset_to_defaults"),
            icon=ft.Icons.RESTORE,
            on_click=self._handle_reset,
            bgcolor="#F59E0B",
            color="#FFFFFF"
        )
        
        # Main content
        content = ft.Column(
            controls=[
                title,
                info_text,
                ft.Divider(height=20, color="transparent"),
                # Summary and hierarchy in a row
                ft.Row(
                    controls=[
                        ft.Container(content=summary_section, expand=1),
                        ft.Container(width=20),
                        ft.Container(content=hierarchy_section, expand=1),
                    ],
                    spacing=10,
                ),
                ft.Divider(height=20, color="transparent"),
                quick_actions,
                ft.Divider(height=20, color="transparent"),
                search_section,
                ft.Divider(height=10, color="transparent"),
                # Table container - ensure it's visible
                ft.Container(
                    content=table,
                    border=ft.border.all(1, "#E5E7EB"),
                    border_radius=8,
                    padding=16,
                    bgcolor="#FFFFFF",
                    visible=True,
                ),
                ft.Divider(height=20, color="transparent"),
                manage_section,
                ft.Divider(height=20, color="transparent"),
                ft.Row(
                    controls=[
                        reset_button,
                        ft.Container(width=10),
                        save_button,
                    ],
                    alignment=ft.MainAxisAlignment.END
                )
            ],
            spacing=12,
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )
        
        return content
    
    def _build_permissions_table(self):
        """Build the permissions table with dropdowns"""
        try:
            logger.info("Starting to build permissions table...")
            # Sort roles by hierarchy (lowest first)
            roles_sorted = sorted(ALL_ROLES, key=lambda r: ROLE_HIERARCHY.get(r, 999))
            logger.info(f"Roles sorted: {roles_sorted}")
            
            # Table rows
            rows = []
            self.dropdowns = {}
            
            menu_items_list = list(MENU_ITEMS.items())
            menu_items_list.sort(key=lambda x: x[0])  # Sort by key
            
            logger.info(f"Building permissions table with {len(menu_items_list)} menu items")
            
            for menu_key, menu_info in menu_items_list:
                menu_name = translator.get_text(f"menu.{menu_key}")
                # If translation returns the key itself (not found), use fallback
                if menu_name == f"menu.{menu_key}":
                    menu_name = menu_key.replace("_", " ").title()
                
                # Create dropdowns for each action
                action_dropdowns = {}
                
                for action in ["view", "create", "edit", "delete"]:
                    if action not in menu_info["actions"]:
                        # Action not available for this menu item
                        cell_content = ft.Container(
                            content=ft.Text("—", color="#9CA3AF", text_align=ft.TextAlign.CENTER),
                            alignment=ft.alignment.center,
                            padding=ft.padding.symmetric(horizontal=8, vertical=4)
                        )
                    else:
                        # Create dropdown
                        dropdown_key = f"{menu_key}_{action}"
                        
                        # Get current value
                        current_role = None
                        if menu_key in self.config.get("menu_items", {}):
                            current_role = self.config["menu_items"][menu_key].get(action)
                        
                        # Create dropdown with roles - optimized width for better fit
                        dropdown = create_modern_dropdown(
                            label="",
                            value=current_role or "",
                            options=[ft.dropdown.Option("")] + [
                                ft.dropdown.Option(role) for role in roles_sorted
                            ],
                            on_change=lambda e, key=dropdown_key: self._on_dropdown_change(key, e.control.value),
                            width=150  # Optimized width for better column fit
                        )
                        
                        self.dropdowns[dropdown_key] = dropdown
                        
                        # Visual indicator for hierarchical permissions
                        # If a lower role is selected, show that higher roles also have access
                        hierarchy_indicator = self._get_hierarchy_indicator(menu_key, action, current_role, roles_sorted)
                        cell_content = ft.Container(
                            content=ft.Row(
                                controls=[
                                    dropdown,
                                    hierarchy_indicator
                                ],
                                spacing=4,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                tight=True,
                                wrap=False
                            ),
                            padding=ft.padding.symmetric(horizontal=4, vertical=2),
                            alignment=ft.alignment.center_left,
                            width=300  # Fixed width: 1.5x of menu column base width
                        )
                    
                    action_dropdowns[action] = cell_content
                
                # Create row with proper cell alignment
                row = ft.DataRow(
                    cells=[
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(menu_name, weight=ft.FontWeight.W_500, size=13),
                                padding=ft.padding.symmetric(horizontal=12, vertical=8),
                                alignment=ft.alignment.center_left
                            )
                        ),
                        ft.DataCell(action_dropdowns.get("view", ft.Container(
                            content=ft.Text("—", color="#9CA3AF", text_align=ft.TextAlign.CENTER, size=14),
                            alignment=ft.alignment.center,
                            padding=ft.padding.symmetric(horizontal=12, vertical=8),
                            width=300  # Fixed width: 1.5x of menu column base width
                        ))),
                        ft.DataCell(action_dropdowns.get("create", ft.Container(
                            content=ft.Text("—", color="#9CA3AF", text_align=ft.TextAlign.CENTER, size=14),
                            alignment=ft.alignment.center,
                            padding=ft.padding.symmetric(horizontal=12, vertical=8),
                            width=300  # Fixed width: 1.5x of menu column base width
                        ))),
                        ft.DataCell(action_dropdowns.get("edit", ft.Container(
                            content=ft.Text("—", color="#9CA3AF", text_align=ft.TextAlign.CENTER, size=14),
                            alignment=ft.alignment.center,
                            padding=ft.padding.symmetric(horizontal=12, vertical=8),
                            width=300  # Fixed width: 1.5x of menu column base width
                        ))),
                        ft.DataCell(action_dropdowns.get("delete", ft.Container(
                            content=ft.Text("—", color="#9CA3AF", text_align=ft.TextAlign.CENTER, size=14),
                            alignment=ft.alignment.center,
                            padding=ft.padding.symmetric(horizontal=12, vertical=8),
                            width=300  # Fixed width: 1.5x of menu column base width
                        ))),
                    ]
                )
                rows.append(row)
            
            # Define column widths: menu item column is flexible, others are 1.5x
            # Base width for menu item column (will be flexible)
            MENU_COLUMN_BASE_WIDTH = 200  # Reference width
            ACTION_COLUMN_WIDTH = int(MENU_COLUMN_BASE_WIDTH * 1.5)  # 300px
            
            # Create data table with improved styling
            table = ft.DataTable(
                columns=[
                    ft.DataColumn(
                        ft.Text(
                            translator.get_text("permissions_management.menu_item.label"),
                            weight=ft.FontWeight.BOLD,
                            size=13
                        ),
                        numeric=False,
                        tooltip=translator.get_text("permissions_management.menu_item.label"),
                    ),
                    ft.DataColumn(
                        ft.Text(
                            translator.get_text("permissions_management.menu_item.view"),
                            weight=ft.FontWeight.BOLD,
                            size=13
                        ),
                        numeric=False,
                        tooltip=translator.get_text("permissions_management.menu_item.view"),
                    ),
                    ft.DataColumn(
                        ft.Text(
                            translator.get_text("permissions_management.menu_item.create"),
                            weight=ft.FontWeight.BOLD,
                            size=13
                        ),
                        numeric=False,
                        tooltip=translator.get_text("permissions_management.menu_item.create"),
                    ),
                    ft.DataColumn(
                        ft.Text(
                            translator.get_text("permissions_management.menu_item.edit"),
                            weight=ft.FontWeight.BOLD,
                            size=13
                        ),
                        numeric=False,
                        tooltip=translator.get_text("permissions_management.menu_item.edit"),
                    ),
                    ft.DataColumn(
                        ft.Text(
                            translator.get_text("permissions_management.menu_item.delete"),
                            weight=ft.FontWeight.BOLD,
                            size=13
                        ),
                        numeric=False,
                        tooltip=translator.get_text("permissions_management.menu_item.delete"),
                    ),
                ],
                rows=rows,
                border=ft.border.all(1, "#E5E7EB"),
                border_radius=8,
                heading_row_color="#F9FAFB",
                heading_row_height=50,
                data_row_min_height=56,
                data_row_max_height=56,
                horizontal_lines=ft.BorderSide(1, "#E5E7EB"),
                vertical_lines=ft.BorderSide(1, "#E5E7EB"),
                column_spacing=16,
                divider_thickness=1,
                show_bottom_border=True,
                show_checkbox_column=False,
                sort_column_index=None,
                sort_ascending=True,
            )
            
            logger.info(f"Table created successfully with {len(rows)} rows, {len(table.columns)} columns")
            
            # Debug: Check if table has content
            if not rows:
                logger.warning("Table has no rows!")
                return ft.Text("Nincs adat a táblázathoz / No data for table", color="#6B7280", size=14)
            
            # Return table directly
            return table
        except Exception as e:
            logger.error(f"Error building permissions table: {e}", exc_info=True)
            import traceback
            traceback.print_exc()
            return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(f"Hiba a táblázat építésekor: {str(e)}", color="red", size=14),
                        ft.Text("Kérlek, nézd meg a log fájlt részletekért.", color="#6B7280", size=12)
                    ],
                    spacing=8
                ),
                padding=20,
                border=ft.border.all(1, "#EF4444"),
                border_radius=8
            )
    
    def _get_hierarchy_indicator(self, menu_key: str, action: str, current_role: str, roles_sorted: list):
        """Get visual indicator showing which roles have access"""
        if not current_role:
            return ft.Container(width=0)
        
        current_level = ROLE_HIERARCHY.get(current_role, 999)
        
        # Find roles at or above current role
        roles_with_access = [
            role for role in roles_sorted
            if ROLE_HIERARCHY.get(role, 999) >= current_level
        ]
        
        if len(roles_with_access) <= 1:
            return ft.Container(width=0)
        
        # Show tooltip with accessible roles
        return ft.Container(
            content=ft.Icon(
                ft.Icons.INFO_OUTLINE,
                size=16,
                color="#6366F1",
                tooltip=translator.get_text("permissions.hierarchical_access") + ": " + ", ".join(roles_with_access)
            ),
            width=24
        )
    
    def _build_manage_permission_section(self):
        """Build section for managing permission management level"""
        
        roles_sorted = sorted(ALL_ROLES, key=lambda r: ROLE_HIERARCHY.get(r, 999))
        
        current_value = self.config.get("manage_permission_level", "")
        
        self.manage_permission_dropdown = create_modern_dropdown(
            label=translator.get_text("permissions_management.manage_permission_level"),
            value=current_value or "",
            options=[ft.dropdown.Option("")] + [
                ft.dropdown.Option(role) for role in roles_sorted
            ],
            width=300
        )
        
        section = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        translator.get_text("permissions_management.manage_permission_section_title"),
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color="#111827"
                    ),
                    ft.Text(
                        translator.get_text("permissions_management.manage_permission_description"),
                        size=12,
                        color="#6B7280"
                    ),
                    self.manage_permission_dropdown
                ],
                spacing=8
            ),
            padding=16,
            border=ft.border.all(1, "#E5E7EB"),
            border_radius=8,
            bgcolor="#F9FAFB"
        )
        
        return section
    
    def _build_quick_actions_section(self):
        """Build quick actions section"""
        roles_sorted = sorted(ALL_ROLES, key=lambda r: ROLE_HIERARCHY.get(r, 999))
        
        def apply_to_all(role_name: str):
            """Apply a role to all permissions"""
            if not role_name:
                return
            
            for dropdown_key, dropdown in self.dropdowns.items():
                dropdown.value = role_name
            self.page.update()
        
        quick_action_buttons = []
        for role in roles_sorted:
            btn = ft.ElevatedButton(
                text=f"{translator.get_text('permissions_management.apply_to_all')}: {role}",
                icon=ft.Icons.DONE_ALL,
                on_click=lambda e, r=role: apply_to_all(r),
                bgcolor="#6366F1",
                color="#FFFFFF",
                height=36,
            )
            quick_action_buttons.append(btn)
        
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        translator.get_text("permissions_management.quick_actions"),
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color="#111827"
                    ),
                    ft.Text(
                        translator.get_text("permissions_management.quick_actions_description"),
                        size=12,
                        color="#6B7280"
                    ),
                    ft.Column(
                        controls=quick_action_buttons,
                        spacing=10,
                        horizontal_alignment=ft.CrossAxisAlignment.START,
                    )
                ],
                spacing=8
            ),
            padding=16,
            border=ft.border.all(1, "#E5E7EB"),
            border_radius=8,
            bgcolor="#F0F9FF"
        )
    
    def _build_role_hierarchy_section(self):
        """Build role hierarchy visualization section"""
        roles_sorted = sorted(ALL_ROLES, key=lambda r: ROLE_HIERARCHY.get(r, 999))
        
        hierarchy_items = []
        for role in roles_sorted:
            level = ROLE_HIERARCHY.get(role, 999)
            hierarchy_items.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text(f"{level}.", width=30, weight=ft.FontWeight.BOLD),
                            ft.Text(role, expand=True),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    padding=8,
                    bgcolor="#F9FAFB" if level % 2 == 0 else "#FFFFFF",
                    border_radius=4,
                )
            )
        
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        translator.get_text("permissions_management.role_hierarchy"),
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color="#111827"
                    ),
                    ft.Text(
                        translator.get_text("permissions_management.role_hierarchy_description"),
                        size=12,
                        color="#6B7280"
                    ),
                    ft.Container(
                        content=ft.Column(
                            controls=hierarchy_items,
                            spacing=4
                        ),
                        border=ft.border.all(1, "#E5E7EB"),
                        border_radius=4,
                        padding=8,
                    )
                ],
                spacing=8
            ),
            padding=16,
            border=ft.border.all(1, "#E5E7EB"),
            border_radius=8,
            bgcolor="#FFFFFF"
        )
    
    def _build_summary_section(self):
        """Build permission summary section with role dropdown"""
        session = SessionLocal()
        try:
            summary = get_permission_summary(session)
            from database.models import User, Role
            from sqlalchemy.orm import joinedload
            
            # Get user counts for each role
            roles_list = list_roles(session)
            user_counts = {}
            for role in roles_list:
                user_count = session.query(User).filter_by(role_id=role.id, is_active=True).count()
                user_counts[role.name] = user_count
        finally:
            session.close()
        
        # Create dropdown for role selection
        roles_sorted = sorted(ALL_ROLES, key=lambda r: ROLE_HIERARCHY.get(r, 999))
        dropdown_options = [ft.dropdown.Option("", translator.get_text("permissions_management.all_roles"))] + [
            ft.dropdown.Option(role) for role in roles_sorted
        ]
        
        self.summary_role_dropdown = create_modern_dropdown(
            label=translator.get_text("permissions_management.select_role"),
            value="",
            options=dropdown_options,
            width=300,
            on_change=self._on_summary_role_change
        )
        
        # Create container for summary content (will be updated when role changes)
        self.summary_content_container = ft.Container(
            content=self._build_summary_content(summary, user_counts, None),
            border=ft.border.all(1, "#E5E7EB"),
            border_radius=4,
            padding=8,
        )
        
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        translator.get_text("permissions_management.summary"),
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color="#111827"
                    ),
                    ft.Row(
                        controls=[
                            self.summary_role_dropdown,
                            ft.Container(expand=True),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    self.summary_content_container
                ],
                spacing=8
            ),
            padding=16,
            border=ft.border.all(1, "#E5E7EB"),
            border_radius=8,
            bgcolor="#FFFFFF"
        )
    
    def _build_summary_content(self, summary, user_counts, selected_role=None):
        """Build summary content - either all roles or details for selected role"""
        if selected_role:
            # Show detailed permissions for selected role
            return self._build_role_permissions_detail(selected_role, summary.get(selected_role, {}), user_counts.get(selected_role, 0))
        else:
            # Show all roles summary
            summary_items = []
            for role_name in sorted(summary.keys(), key=lambda r: ROLE_HIERARCHY.get(r, 999)):
                role_info = summary[role_name]
                user_count = user_counts.get(role_name, 0)
                
                summary_items.append(
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Text(role_name, expand=True, weight=ft.FontWeight.W_500),
                                ft.Text(
                                    f"{role_info['total_permissions']}",
                                    weight=ft.FontWeight.BOLD,
                                    color="#10B981"
                                ),
                                ft.Text(f"({user_count} {translator.get_text('permissions_management.users')})", size=12, color="#6B7280"),
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER
                        ),
                        padding=8,
                        bgcolor="#F9FAFB",
                        border_radius=4,
                    )
                )
            
            return ft.Column(
                controls=summary_items,
                spacing=4
            )
    
    def _build_role_permissions_detail(self, role_name, role_info, user_count):
        """Build detailed permissions list for a specific role"""
        session = SessionLocal()
        try:
            from database.models import Role
            role = session.query(Role).filter_by(name=role_name).first()
            if not role:
                return ft.Text(translator.get_text("permissions_management.role_not_found"), color="red")
            
            permissions = role.permissions or {}
            
            # Group permissions by menu item
            menu_permissions = {}
            for perm_key, perm_value in permissions.items():
                if perm_value:  # Only show enabled permissions
                    # Parse permission key: {menu_item}_{action}
                    parts = perm_key.split("_", 1)
                    if len(parts) == 2:
                        menu_key, action = parts
                        if menu_key not in menu_permissions:
                            menu_permissions[menu_key] = []
                        menu_permissions[menu_key].append(action)
            
            # Build permission items
            permission_items = []
            
            # Header with role info
            permission_items.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text(
                                role_name,
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color="#111827"
                            ),
                            ft.Container(expand=True),
                            ft.Text(
                                f"{role_info.get('total_permissions', 0)} {translator.get_text('permissions_management.permissions')}",
                                size=12,
                                color="#10B981",
                                weight=ft.FontWeight.W_600
                            ),
                            ft.Text(
                                f" • {user_count} {translator.get_text('permissions_management.users')}",
                                size=12,
                                color="#6B7280"
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    padding=ft.padding.only(bottom=12),
                    border=ft.border.only(bottom=ft.BorderSide(1, "#E5E7EB"))
                )
            )
            
            # Menu items and their permissions
            if menu_permissions:
                # Map permission keys to menu keys (handle differences like "developer" vs "developer_tools")
                menu_key_mapping = {
                    "developer": "developer_tools",
                    "developer_tools": "developer_tools",
                }
                
                for menu_key in sorted(menu_permissions.keys()):
                    # Use mapped key if exists, otherwise use original
                    display_key = menu_key_mapping.get(menu_key, menu_key)
                    menu_info = MENU_ITEMS.get(display_key, {})
                    menu_label = translator.get_text(f"menu.{display_key}")
                    # If translation returns the key itself (not found), use display_key as fallback
                    if menu_label == f"menu.{display_key}":
                        menu_label = display_key
                    actions = menu_permissions[menu_key]
                    
                    action_labels = []
                    for action in sorted(actions):
                        # Try to get translation using menu_item format first (existing keys)
                        action_key = f"permissions_management.menu_item.{action}"
                        action_label = translator.get_text(action_key)
                        # If translation returns the key itself (not found), try action_ format
                        if action_label == action_key:
                            action_key2 = f"permissions_management.action_{action}"
                            action_label = translator.get_text(action_key2)
                            # If still not found, use action name as fallback
                            if action_label == action_key2:
                                action_label = action
                        action_labels.append(action_label)
                    
                    permission_items.append(
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Row(
                                        controls=[
                                            ft.Text(
                                                menu_label,
                                                size=13,
                                                weight=ft.FontWeight.W_600,
                                                color="#111827"
                                            ),
                                            ft.Container(expand=True),
                                            ft.Text(
                                                ", ".join(action_labels),
                                                size=12,
                                                color="#6B7280"
                                            ),
                                        ],
                                        vertical_alignment=ft.CrossAxisAlignment.CENTER
                                    ),
                                ],
                                spacing=4,
                                tight=True
                            ),
                            padding=ft.padding.symmetric(vertical=6, horizontal=8),
                            bgcolor="#F9FAFB",
                            border_radius=4,
                        )
                    )
            else:
                permission_items.append(
                    ft.Text(
                        translator.get_text("permissions_management.no_permissions"),
                        size=12,
                        color="#9CA3AF",
                        italic=True
                    )
                )
        finally:
            session.close()
        
        return ft.Column(
            controls=permission_items,
            spacing=4
        )
    
    def _on_summary_role_change(self, e):
        """Handle role dropdown change in summary section"""
        if not self.summary_role_dropdown or not self.summary_content_container:
            return
        
        selected_role = self.summary_role_dropdown.value or None
        
        # Reload summary data
        session = SessionLocal()
        try:
            summary = get_permission_summary(session)
            from database.models import User
            roles_list = list_roles(session)
            user_counts = {}
            for role in roles_list:
                user_count = session.query(User).filter_by(role_id=role.id, is_active=True).count()
                user_counts[role.name] = user_count
        finally:
            session.close()
        
        # Update content
        self.summary_content_container.content = self._build_summary_content(summary, user_counts, selected_role)
        self.page.update()
    
    def _build_search_section(self):
        """Build search section"""
        from ui.components.modern_components import create_modern_text_field
        
        self.search_field = create_modern_text_field(
            label=translator.get_text("permissions_management.search_menu_items"),
            hint_text=translator.get_text("permissions_management.search_menu_items"),
            on_change=self._on_search_change,
            width=400
        )
        
        return ft.Row(
            controls=[
                ft.Icon(ft.Icons.SEARCH, color="#6B7280"),
                ft.Container(width=10),
                self.search_field,
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )
    
    def _on_search_change(self, e):
        """Handle search field change"""
        # Search functionality - filter table rows
        # This is a simplified version - full implementation would filter the table
        pass
    
    def _on_dropdown_change(self, dropdown_key: str, value: str):
        """Handle dropdown value change"""
        # The value is automatically stored in the dropdown
        # We'll collect all values when saving
        pass
    
    def _handle_reset(self, e):
        """Handle reset to defaults button click"""
        def confirm_reset():
            try:
                session = SessionLocal()
                try:
                    # Reset permissions (clear all menu item permissions)
                    reset_to_default_permissions(session)
                    
                    # Show success message
                    self.page.snack_bar = ft.SnackBar(
                        ft.Text(translator.get_text("permissions_management.reset_success")),
                        bgcolor="#10B981"
                    )
                    self.page.snack_bar.open = True
                    
                    # Reload config - this will clear all dropdowns
                    self._load_config()
                    
                    # Reset all dropdowns to empty
                    for dropdown_key, dropdown in self.dropdowns.items():
                        dropdown.value = ""
                    if self.manage_permission_dropdown:
                        self.manage_permission_dropdown.value = ""
                    
                finally:
                    session.close()
                
                # Close dialog first
                self.page.dialog.open = False
                self.page.update()
                
            except Exception as ex:
                logger.error(f"Error resetting permissions: {ex}")
                self.page.snack_bar = ft.SnackBar(
                    ft.Text(f"Error: {str(ex)}"),
                    bgcolor="#EF4444"
                )
                self.page.snack_bar.open = True
                self.page.dialog.open = False
                self.page.update()
        
        # Show confirmation dialog
        self.page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(translator.get_text("permissions_management.reset_confirmation_title")),
            content=ft.Text(translator.get_text("permissions_management.reset_confirmation_message")),
            actions=[
                ft.TextButton(
                    translator.get_text("common.buttons.cancel"),
                    on_click=lambda e: setattr(self.page.dialog, 'open', False) or self.page.update()
                ),
                ft.TextButton(
                    translator.get_text("permissions_management.reset"),
                    on_click=lambda e: confirm_reset(),
                ),
            ],
        )
        self.page.dialog.open = True
        self.page.update()
    
    def _handle_save(self, e):
        """Handle save button click"""
        try:
            # Collect all dropdown values
            new_config = {
                "menu_items": {},
                "manage_permission_level": self.manage_permission_dropdown.value if self.manage_permission_dropdown.value else None
            }
            
            # Collect menu item permissions
            for menu_key, menu_info in MENU_ITEMS.items():
                new_config["menu_items"][menu_key] = {}
                for action in menu_info["actions"]:
                    dropdown_key = f"{menu_key}_{action}"
                    if dropdown_key in self.dropdowns:
                        dropdown = self.dropdowns[dropdown_key]
                        value = dropdown.value if dropdown.value else None
                        new_config["menu_items"][menu_key][action] = value
            
            # Show change reason dialog before saving
            from ui.components.change_reason_dialog import show_change_reason_dialog
            
            def perform_save(change_reason: str):
                # Save to database
                session = SessionLocal()
                try:
                    update_permission_config(new_config, session, change_reason=change_reason)
                    
                    # Refresh context permissions for current user
                    # This ensures that permission changes take effect immediately
                    ctx = get_app_context()
                    if ctx.is_authenticated() and ctx.role:
                        from database.models import Role
                        role = session.query(Role).filter_by(name=ctx.role).first()
                        if role:
                            ctx.permissions = role.permissions or {}
                    
                    # Show success message
                    self.page.snack_bar = ft.SnackBar(
                        ft.Text(translator.get_text("permissions_management.saved")),
                        bgcolor="#10B981"
                    )
                    self.page.snack_bar.open = True
                    
                    # Reload config
                    self._load_config()
                    
                except Exception as ex:
                    logger.error(f"Error saving permissions: {ex}")
                    self.page.snack_bar = ft.SnackBar(
                        ft.Text(f"Error: {str(ex)}"),
                        bgcolor="#EF4444"
                    )
                    self.page.snack_bar.open = True
                finally:
                    session.close()
                
                self.page.update()
            
            # Show change reason dialog before saving
            show_change_reason_dialog(
                page=self.page,
                entity_name=translator.get_text("permissions_management.title") if hasattr(translator, 'get_text') else "Jogosultságok",
                entity_type=translator.get_text("permissions_management.entity_type") if hasattr(translator, 'get_text') else "Jogosultságok",
                on_confirm=perform_save,
            )
        except Exception as ex:
            logger.error(f"Error in save handler: {ex}")
            self.page.snack_bar = ft.SnackBar(
                ft.Text(f"Error: {str(ex)}"),
                bgcolor="#EF4444"
            )
            self.page.snack_bar.open = True
            self.page.update()
            
            # Show change reason dialog before saving
            from ui.components.change_reason_dialog import show_change_reason_dialog
            show_change_reason_dialog(
                page=self.page,
                entity_name=translator.get_text("permissions_management.title") if hasattr(translator, 'get_text') else "Jogosultságok",
                entity_type=translator.get_text("permissions_management.entity_type") if hasattr(translator, 'get_text') else "Jogosultságok",
                on_confirm=perform_save,
            )
        except Exception as ex:
            logger.error(f"Error in save handler: {ex}")
            self.page.snack_bar = ft.SnackBar(
                ft.Text(f"Error: {str(ex)}"),
                bgcolor="#EF4444"
            )
            self.page.snack_bar.open = True
            self.page.update()

