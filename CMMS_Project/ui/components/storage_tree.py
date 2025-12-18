"""
Storage Tree Component - SIMPLE WORKING VERSION
"""

import flet as ft
from services.storage_service import get_storage_location_tree
from database.session_manager import SessionLocal
from localization.translator import translator
from ui.components.modern_components import DesignSystem
import logging

logger = logging.getLogger(__name__)


class StorageTree:
    """Simple storage tree component"""
    
    def __init__(self, page: ft.Page, on_location_selected=None, on_location_create=None, on_location_edit=None, on_location_delete=None):
        self.page = page
        self.on_location_selected = on_location_selected
        self.on_location_create = on_location_create
        self.on_location_edit = on_location_edit
        self.on_location_delete = on_location_delete
        self.selected_location_id = None
        self.expanded_nodes = set()
        self.tree_list = None  # Will be a Column
    
    def build(self, root_id: int = None) -> ft.Control:
        """Build the tree - SIMPLE LIST APPROACH like inventory_screen"""
        # Create Column for tree items - SAME pattern as inventory_screen parts_list
        self.tree_list = ft.Column([], spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)
        
        # Load locations
        self._load_locations(root_id)
        
        return self.tree_list
    
    def _load_locations(self, root_id: int = None):
        """Load storage locations into the list"""
        session = SessionLocal()
        try:
            tree_data = get_storage_location_tree(root_id, session)
            logger.info(f"Loading {len(tree_data)} root locations")
            
            self.tree_list.controls.clear()
            
            if not tree_data:
                self.tree_list.controls.append(
                    ft.Container(
                        content=ft.Text(
                            translator.get_text("storage.no_locations") if translator.get_text("storage.no_locations") != "storage.no_locations" else "Nincs raktárhely",
                            size=14,
                            color=DesignSystem.TEXT_SECONDARY,
                            italic=True,
                        ),
                        padding=20,
                        alignment=ft.alignment.center,
                    )
                )
            else:
                # Add each location as a simple card
                for node in tree_data:
                    self._add_location_node(node, 0)
            
            if self.page:
                self.page.update()
        except Exception as e:
            logger.error(f"Error loading locations: {e}", exc_info=True)
            self.tree_list.controls.append(
                ft.Container(
                    content=ft.Text(f"Error: {e}", color="red", size=14),
                    padding=10,
                )
            )
        finally:
            session.close()
    
    def _add_location_node(self, node: dict, level: int):
        """Add a location node to the tree"""
        node_id = node['id']
        is_selected = self.selected_location_id == node_id
        has_children = len(node.get('children', [])) > 0
        is_expanded = node_id in self.expanded_nodes
        
        # Indentation
        indent = level * 20
        
        # Expand/collapse icon
        if has_children:
            # Use available icons - EXPAND_MORE for expanded, ARROW_FORWARD for collapsed
            if is_expanded:
                icon_name = ft.Icons.EXPAND_MORE if hasattr(ft.Icons, 'EXPAND_MORE') else "expand_more"
            else:
                icon_name = ft.Icons.ARROW_FORWARD if hasattr(ft.Icons, 'ARROW_FORWARD') else "arrow_forward"
            expand_icon = ft.Icon(
                icon_name,
                size=16,
                color=DesignSystem.TEXT_SECONDARY,
            )
        else:
            expand_icon = ft.Container(width=16)
        
        # Location icon
        location_icon = ft.Icon(
            ft.Icons.INVENTORY_2 if node.get('location_type') == 'warehouse' else ft.Icons.FOLDER,
            size=18,
            color=DesignSystem.BLUE_500 if is_selected else DesignSystem.TEXT_SECONDARY,
        )
        
        # Location name
        name_text = ft.Text(
            node['name'],
            size=14,
            weight=ft.FontWeight.W_600 if is_selected else ft.FontWeight.NORMAL,
            color=DesignSystem.BLUE_600 if is_selected else DesignSystem.TEXT_PRIMARY,
        )
        
        # Code badge
        code_badge = None
        if node.get('code'):
            code_badge = ft.Container(
                content=ft.Text(node['code'], size=10, color=DesignSystem.TEXT_SECONDARY),
                padding=ft.padding.symmetric(horizontal=6, vertical=2),
                bgcolor=DesignSystem.GRAY_100,
                border_radius=4,
            )
        
        # Menu button
        menu_button = ft.PopupMenuButton(
            items=[
                ft.PopupMenuItem(
                    text=translator.get_text("storage.add_child_location"),
                    icon=ft.Icons.ADD,
                    on_click=lambda e, nid=node_id: self._handle_create_child(nid),
                ),
                ft.PopupMenuItem(
                    text=translator.get_text("common.buttons.edit"),
                    icon=ft.Icons.EDIT,
                    on_click=lambda e, nid=node_id: self._handle_edit(nid),
                ),
                ft.PopupMenuItem(
                    text=translator.get_text("common.buttons.delete"),
                    icon=ft.Icons.DELETE,
                    on_click=lambda e, nid=node_id: self._handle_delete(nid),
                ),
            ],
        )
        
        # Build row controls
        row_controls = [location_icon, name_text]
        if code_badge:
            row_controls.append(code_badge)
        
        # Location card
        location_card = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(width=indent),
                    ft.GestureDetector(
                        content=expand_icon,
                        on_tap=lambda e, nid=node_id, has_children=has_children: self._toggle_expand(nid, has_children) if has_children else None,
                    ),
                    ft.GestureDetector(
                        content=ft.Row(controls=row_controls, spacing=8, tight=True),
                        on_tap=lambda e, nid=node_id: self._select_location(nid),
                    ),
                    ft.Container(expand=True),
                    menu_button,
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=4,
            ),
            padding=ft.padding.symmetric(horizontal=8, vertical=8),
            bgcolor=DesignSystem.BLUE_50 if is_selected else "#F5F5F5",
            border=ft.border.all(1, DesignSystem.BLUE_500 if is_selected else "#DDDDDD"),
            border_radius=DesignSystem.RADIUS_MD,
            on_click=lambda e, nid=node_id: self._select_location(nid),
        )
        
        self.tree_list.controls.append(location_card)
        
        # Add children if expanded
        if is_expanded and has_children:
            for child in node['children']:
                self._add_location_node(child, level + 1)
    
    def _toggle_expand(self, node_id: int, has_children: bool):
        """Toggle node expansion"""
        if not has_children:
            return
        
        if node_id in self.expanded_nodes:
            self.expanded_nodes.remove(node_id)
        else:
            self.expanded_nodes.add(node_id)
        
        self.refresh()
    
    def _select_location(self, location_id: int):
        """Select a location"""
        self.selected_location_id = location_id
        if self.on_location_selected:
            self.on_location_selected(location_id)
        self.refresh()
    
    def _handle_create_child(self, parent_id: int):
        """Handle create child location"""
        if self.on_location_create:
            self.on_location_create(parent_id)
    
    def _handle_edit(self, location_id: int):
        """Handle edit location"""
        if self.on_location_edit:
            self.on_location_edit(location_id)
    
    def _handle_delete(self, location_id: int):
        """Handle delete location"""
        if self.on_location_delete:
            self.on_location_delete(location_id)
    
    def refresh(self, root_id: int = None):
        """Refresh the tree"""
        self._load_locations(root_id)
