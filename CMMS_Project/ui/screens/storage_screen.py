"""
Storage Management Screen - COMPLETE REWRITE using inventory_screen pattern
"""

import flet as ft
from services.storage_service import (
    create_storage_location,
    update_storage_location,
    delete_storage_location,
    get_storage_location,
    get_storage_location_path,
    get_parts_at_location,
    assign_part_to_location,
    update_part_location,
    remove_part_from_location,
    search_parts_by_location,
    get_fifo_recommendation,
    get_all_storage_locations_flat,
    get_storage_location_tree,
)
from services.inventory_service import list_parts, validate_inventory_levels, fix_inventory_level_discrepancy
from database.session_manager import SessionLocal
from database.models import Part, InventoryLevel, PartLocation
from sqlalchemy.orm import joinedload
from sqlalchemy import and_
from localization.translator import translator
from ui.components.modern_components import (
    create_modern_button,
    create_modern_text_field,
    create_modern_dropdown,
    create_vibrant_badge,
    create_modern_icon_button,
    DesignSystem,
)
from utils.currency import format_price
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class StorageScreen:
    def __init__(self, page: ft.Page):
        self.page = page
    
    def view(self, page: ft.Page):
        # Use stored page reference for dialogs
        if not hasattr(self, 'page') or self.page is None:
            self.page = page
        
        # Store refresh function reference for external calls
        self._refresh_parts_without_location = None
        
        # Storage locations list container - SAME pattern as inventory_screen parts_list
        locations_list = ft.Column([], spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)
        
        # Selected location details container
        details_container = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        translator.get_text("storage.select_location"),
                        size=14,
                        color=DesignSystem.TEXT_SECONDARY,
                        italic=True,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
            ),
            alignment=ft.alignment.center,
            padding=20,
        )
        
        selected_location_id_ref = {"value": None}
        expanded_nodes_ref = {"value": set()}
        
        def refresh_locations_list():
            """Refresh the locations list - SAME pattern as inventory_screen refresh_parts_list"""
            # Don't update if dialog is open
            page_ref = self.page if hasattr(self, 'page') and self.page else page
            if hasattr(page_ref, 'dialog') and page_ref.dialog is not None:
                dialog_open = getattr(page_ref.dialog, 'open', False)
                if dialog_open:
                    return
            
            # Check if we need to select a storage location from search
            if hasattr(page_ref, '_select_storage_location_id') and page_ref._select_storage_location_id:
                location_id = page_ref._select_storage_location_id
                page_ref._select_storage_location_id = None  # Clear flag
                # Select the location after a small delay
                import threading
                def select_location_delayed():
                    import time
                    time.sleep(0.2)
                    try:
                        select_location(location_id)
                    except Exception as e:
                        logger.warning(f"Error selecting storage location from search: {e}")
                threading.Thread(target=select_location_delayed, daemon=True).start()
            
            session = SessionLocal()
            try:
                tree_data = get_storage_location_tree(None, session)
                locations_list.controls.clear()
                
                if not tree_data:
                    locations_list.controls.append(
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
                    # Add each location
                    def add_location_node(node, level=0):
                        node_id = node['id']
                        is_selected = selected_location_id_ref["value"] == node_id
                        has_children = len(node.get('children', [])) > 0
                        is_expanded = node_id in expanded_nodes_ref["value"]
                        
                        indent = level * 20
                        
                        # Expand icon
                        if has_children:
                            # Use available icons - EXPAND_MORE for expanded, ARROW_FORWARD for collapsed
                            if is_expanded:
                                icon_name = ft.Icons.EXPAND_MORE if hasattr(ft.Icons, 'EXPAND_MORE') else "expand_more"
                            else:
                                icon_name = ft.Icons.ARROW_RIGHT if hasattr(ft.Icons, 'ARROW_RIGHT') else (ft.Icons.SWAP_HORIZ if hasattr(ft.Icons, 'SWAP_HORIZ') else "arrow_forward")
                            expand_icon = ft.Icon(
                                icon_name,
                                size=16,
                                color=DesignSystem.TEXT_SECONDARY,
                            )
                        else:
                            expand_icon = ft.Container(width=16)
                        
                        # Location icon
                        loc_icon = ft.Icon(
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
                                    on_click=lambda e, nid=node_id: open_create_dialog(nid),
                                ),
                                ft.PopupMenuItem(
                                    text=translator.get_text("common.buttons.edit"),
                                    icon=ft.Icons.EDIT,
                                    on_click=lambda e, nid=node_id: open_edit_dialog(nid),
                                ),
                                ft.PopupMenuItem(
                                    text=translator.get_text("common.buttons.delete"),
                                    icon=ft.Icons.DELETE,
                                    on_click=lambda e, nid=node_id: open_delete_dialog(nid),
                                ),
                            ],
                        )
                        
                        # Build row
                        row_controls = [loc_icon, name_text]
                        if code_badge:
                            row_controls.append(code_badge)
                        
                        # Location card
                        location_card = ft.Container(
                            content=ft.Row(
                                controls=[
                                    ft.Container(width=indent),
                                    ft.GestureDetector(
                                        content=expand_icon,
                                        on_tap=lambda e, nid=node_id, has_children=has_children: toggle_expand(nid, has_children) if has_children else None,
                                    ),
                                    ft.GestureDetector(
                                        content=ft.Row(controls=row_controls, spacing=8, tight=True),
                                        on_tap=lambda e, nid=node_id: select_location(nid),
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
                            on_click=lambda e, nid=node_id: select_location(nid),
                        )
                        
                        locations_list.controls.append(location_card)
                        
                        # Add children if expanded
                        if is_expanded and has_children:
                            for child in node['children']:
                                add_location_node(child, level + 1)
                    
                    for node in tree_data:
                        add_location_node(node)
                
                if page_ref:
                    page_ref.update()
            except Exception as e:
                logger.error(f"Error refreshing locations: {e}", exc_info=True)
                locations_list.controls.append(
                    ft.Container(
                        content=ft.Text(f"Error: {e}", color="red", size=14),
                        padding=10,
                    )
                )
            finally:
                session.close()
        
        def toggle_expand(node_id, has_children):
            """Toggle node expansion"""
            if not has_children:
                return
            if node_id in expanded_nodes_ref["value"]:
                expanded_nodes_ref["value"].remove(node_id)
            else:
                expanded_nodes_ref["value"].add(node_id)
            refresh_locations_list()
        
        def select_location(location_id):
            """Select a location - update details immediately"""
            selected_location_id_ref["value"] = location_id
            # Update details FIRST for instant feedback
            update_details(location_id)
            # Then refresh list to highlight selected location
            refresh_locations_list()
        
        def update_details(location_id):
            """Update details section - with immediate UI update"""
            if not location_id:
                details_container.content = ft.Column(
                    controls=[
                        ft.Text(
                            translator.get_text("storage.select_location"),
                            size=14,
                            color=DesignSystem.TEXT_SECONDARY,
                            italic=True,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20,
                )
                if self.page:
                    self.page.update()
                return
            
            # Show loading state immediately for instant feedback
            details_container.content = ft.Column(
                controls=[
                    ft.ProgressRing(width=40, height=40),
                    ft.Text(
                        translator.get_text("common.loading") or "Betöltés...",
                        size=14,
                        color=DesignSystem.TEXT_SECONDARY,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
            )
            if self.page:
                self.page.update()
            
            session = SessionLocal()
            try:
                location = get_storage_location(location_id, session)
                if not location:
                    details_container.content = ft.Column(
                        controls=[
                            ft.Text(
                                translator.get_text("storage.location_not_found") or "Raktárhely nem található",
                                size=14,
                                color=DesignSystem.ERROR,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=20,
                    )
                    if self.page:
                        self.page.update()
                    return
                
                location_path = get_storage_location_path(location_id, session)
                # Get parts including children (deepest level locations)
                parts = get_parts_at_location(location_id, include_children=True, session=session)
                
                # Build parts list - group by location path to show hierarchy
                parts_by_location = {}
                for part_info in parts:
                    location_path = part_info.get('location_path', part_info.get('location_name', ''))
                    if location_path not in parts_by_location:
                        parts_by_location[location_path] = []
                    parts_by_location[location_path].append(part_info)
                
                # Build parts list with location grouping
                parts_rows = []
                for location_path, location_parts in sorted(parts_by_location.items()):
                    # Add location header if there are multiple locations or if it's different from selected location
                    if len(parts_by_location) > 1 or location_path != location.name:
                        parts_rows.append(
                            ft.DataRow(
                                cells=[
                                    ft.DataCell(
                                        ft.Container(
                                            content=ft.Text(
                                                location_path,
                                                size=13,
                                                weight=ft.FontWeight.BOLD,
                                                color=DesignSystem.BLUE_600,
                                            ),
                                            padding=ft.padding.only(left=10, top=8, bottom=4),
                                        ),
                                    ),
                                    ft.DataCell(ft.Container()),  # Empty cells to span across columns
                                    ft.DataCell(ft.Container()),
                                    ft.DataCell(ft.Container()),
                                    ft.DataCell(ft.Container()),
                                    ft.DataCell(ft.Container()),
                                    ft.DataCell(ft.Container()),
                                    ft.DataCell(ft.Container()),
                                ],
                            )
                        )
                    
                    # Add parts for this location
                    for part_info in location_parts:
                        fifo_info = None
                        fifo_badge = None
                        try:
                            # Get global FIFO info for this part (same SKU), regardless of storage location
                            # FIFO works globally across all storage locations for the same part
                            fifo_info = get_fifo_recommendation(part_info['part_id'], None, session=session)
                            if fifo_info and fifo_info.get('received_date'):
                                # Show where the oldest batch is located
                                location_info = ""
                                if fifo_info.get('location_path'):
                                    location_info = f" ({fifo_info['location_path']})"
                                fifo_badge = ft.Tooltip(
                                    message=(translator.get_text("storage.fifo_oldest") or "Legrégebbi batch") + f": {fifo_info['received_date'].strftime('%Y-%m-%d')}{location_info}",
                                    content=create_vibrant_badge(text="FIFO", variant="orange", size=10),
                                )
                            else:
                                # Check if there are any batches at all for this part
                                from database.models import StockBatch
                                batch_count = session.query(StockBatch).filter(
                                    StockBatch.part_id == part_info['part_id'],
                                    StockBatch.quantity_remaining > 0
                                ).count()
                                if batch_count == 0:
                                    # No batches at all for this part
                                    fifo_badge = None
                        except Exception as fifo_error:
                            logger.warning(f"Error getting FIFO recommendation: {fifo_error}")
                            fifo_info = None
                        
                        # Assigned by user info
                        assigned_by_text = part_info.get('assigned_by_username') or translator.get_text("common.unknown") or "Ismeretlen"
                        
                        # Last movement date
                        last_movement_text = ""
                        if part_info.get('last_movement_date'):
                            last_movement_text = part_info['last_movement_date'].strftime('%Y-%m-%d %H:%M')
                        else:
                            last_movement_text = "-"
                        
                        parts_rows.append(
                            ft.DataRow(
                                cells=[
                                    ft.DataCell(ft.Text(part_info['part_name'], weight=ft.FontWeight.W_500)),
                                    ft.DataCell(create_vibrant_badge(text=part_info['part_sku'], variant="blue", size=11)),
                                    ft.DataCell(ft.Text(f"{part_info['quantity']}", weight=ft.FontWeight.W_600)),
                                    ft.DataCell(ft.Text(part_info['assigned_date'].strftime('%Y-%m-%d'), size=12)),
                                    ft.DataCell(ft.Text(assigned_by_text, size=12, color=DesignSystem.TEXT_SECONDARY)),
                                    ft.DataCell(ft.Text(last_movement_text, size=12, color=DesignSystem.TEXT_SECONDARY)),
                                    ft.DataCell(fifo_badge if fifo_badge else ft.Container()),
                                    ft.DataCell(
                                        ft.Row(
                                            controls=[
                                                create_modern_icon_button(
                                                    icon=ft.Icons.SWAP_HORIZ if hasattr(ft.Icons, 'SWAP_HORIZ') else (ft.Icons.ARROW_RIGHT if hasattr(ft.Icons, 'ARROW_RIGHT') else "swap_horiz"),
                                                    tooltip=translator.get_text("storage.transfer") or "Áttárazás",
                                                    on_click=lambda e, pid=part_info['part_location_id']: open_transfer_part_dialog(pid),
                                                    color=DesignSystem.PURPLE_500,
                                                ),
                                                create_modern_icon_button(
                                                    icon=ft.Icons.EDIT,
                                                    tooltip=translator.get_text("common.buttons.edit"),
                                                    on_click=lambda e, pid=part_info['part_location_id']: open_edit_part_dialog(pid),
                                                    color=DesignSystem.BLUE_500,
                                                ),
                                                create_modern_icon_button(
                                                    icon=ft.Icons.DELETE,
                                                    tooltip=translator.get_text("common.buttons.delete"),
                                                    on_click=lambda e, pid=part_info['part_location_id']: open_remove_part_dialog(pid),
                                                    color=DesignSystem.RED_500,
                                                ),
                                            ],
                                            spacing=4,
                                        )
                                    ),
                                ]
                            )
                        )
                
                parts_table = ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text(translator.get_text("inventory.part_name"), weight=ft.FontWeight.BOLD)),
                        ft.DataColumn(ft.Text(translator.get_text("inventory.sku"), weight=ft.FontWeight.BOLD)),
                        ft.DataColumn(ft.Text(translator.get_text("inventory.quantity"), weight=ft.FontWeight.BOLD)),
                        ft.DataColumn(ft.Text(translator.get_text("storage.assigned_date"), weight=ft.FontWeight.BOLD)),
                        ft.DataColumn(ft.Text(translator.get_text("storage.assigned_by") or "Hozzárendelte", weight=ft.FontWeight.BOLD)),
                        ft.DataColumn(ft.Text(translator.get_text("storage.last_used") or "Utolsó használat", weight=ft.FontWeight.BOLD)),
                        ft.DataColumn(ft.Text("FIFO", weight=ft.FontWeight.BOLD)),
                        ft.DataColumn(ft.Text("", weight=ft.FontWeight.BOLD)),
                    ],
                    rows=parts_rows,
                    border=ft.border.all(1, DesignSystem.BORDER_COLOR),
                    border_radius=DesignSystem.RADIUS_MD,
                ) if parts_rows else ft.Container(
                    content=ft.Text(
                        translator.get_text("storage.no_parts_at_location"),
                        size=14,
                        color=DesignSystem.TEXT_SECONDARY,
                        italic=True,
                    ),
                    padding=20,
                    alignment=ft.alignment.center,
                )
                
                # Location info - filter out None values
                info_controls = [
                    ft.Text(location.name, size=20, weight=ft.FontWeight.BOLD, color=DesignSystem.TEXT_PRIMARY),
                ]
                
                if location_path != location.name:
                    info_controls.append(ft.Text(location_path, size=12, color=DesignSystem.TEXT_SECONDARY))
                
                badge_controls = []
                if location.code:
                    badge_controls.append(create_vibrant_badge(text=location.code, variant="blue", size=11))
                if location.location_type:
                    badge_controls.append(create_vibrant_badge(
                        text=location.location_type or translator.get_text("storage.location_type_unknown"),
                        variant="purple",
                        size=11,
                    ))
                
                if badge_controls:
                    info_controls.append(ft.Row(controls=badge_controls, spacing=8))
                
                if location.description:
                    info_controls.append(ft.Text(location.description, size=13, color=DesignSystem.TEXT_SECONDARY))
                
                info_section = ft.Column(
                    controls=info_controls,
                    spacing=8,
                )
                
                details_container.content = ft.Column(
                    controls=[
                        info_section,
                        ft.Divider(height=20, color="transparent"),
                        ft.Row(
                            controls=[
                                ft.Text(translator.get_text("storage.parts_at_location"), size=16, weight=ft.FontWeight.BOLD),
                                ft.Container(expand=True),
                                create_modern_button(
                                    text="+ " + translator.get_text("storage.assign_part"),
                                    icon=ft.Icons.ADD,
                                    on_click=lambda e: open_assign_part_dialog(),
                                    bgcolor=DesignSystem.EMERALD_500,
                                    color=DesignSystem.WHITE,
                                    height=36,
                                ),
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        parts_table,
                    ],
                    spacing=12,
                    scroll=ft.ScrollMode.AUTO,
                )
                
                if self.page:
                    self.page.update()
            except Exception as e:
                logger.error(f"Error updating storage location details: {e}", exc_info=True)
                # Show error message
                details_container.content = ft.Column(
                    controls=[
                        ft.Text(
                            translator.get_text("common.error") or "Hiba",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=DesignSystem.ERROR,
                        ),
                        ft.Text(
                            str(e),
                            size=14,
                            color=DesignSystem.TEXT_SECONDARY,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=12,
                )
                if self.page:
                    self.page.update()
            finally:
                session.close()
        
        def open_create_dialog(parent_id=None):
            """Open create location dialog"""
            session = SessionLocal()
            try:
                locations = get_all_storage_locations_flat(session)
                parent_options = [ft.dropdown.Option("", translator.get_text("storage.root_location"))]
                for loc in locations:
                    path = get_storage_location_path(loc.id, session)
                    display_text = f"{path}" if path else loc.name
                    parent_options.append(ft.dropdown.Option(str(loc.id), display_text))
            finally:
                session.close()
            
            parent_dropdown = create_modern_dropdown(
                label=translator.get_text("storage.parent_location"),
                options=parent_options,
                value=str(parent_id) if parent_id else "",
            )
            
            name_field = create_modern_text_field(label=translator.get_text("storage.location_name"))
            code_field = create_modern_text_field(label=translator.get_text("storage.location_code"), hint_text=translator.get_text("common.optional"))
            type_field = create_modern_dropdown(
                label=translator.get_text("storage.location_type"),
                options=[
                    ft.dropdown.Option("warehouse", translator.get_text("storage.type_warehouse")),
                    ft.dropdown.Option("cabinet", translator.get_text("storage.type_cabinet")),
                    ft.dropdown.Option("shelf", translator.get_text("storage.type_shelf")),
                    ft.dropdown.Option("bin", translator.get_text("storage.type_bin")),
                    ft.dropdown.Option("", translator.get_text("storage.type_other")),
                ],
            )
            description_field = create_modern_text_field(
                label=translator.get_text("storage.location_description"),
                multiline=True,
                hint_text=translator.get_text("common.optional"),
            )
            
            def submit(e):
                try:
                    if not name_field.value:
                        raise ValueError(translator.get_text("common.messages.required_field"))
                    
                    selected_parent_id = parent_id
                    if parent_dropdown.value:
                        try:
                            selected_parent_id = int(parent_dropdown.value)
                        except (ValueError, TypeError):
                            selected_parent_id = None
                    elif not parent_id:
                        selected_parent_id = None
                    
                    create_storage_location(
                        name=name_field.value,
                        parent_id=selected_parent_id,
                        location_type=type_field.value if type_field.value else None,
                        description=description_field.value if description_field.value else None,
                        code=code_field.value if code_field.value else None,
                    )
                    
                    try:
                        self.page.close(dialog)
                    except:
                        dialog.open = False
                        self.page.dialog = None
                        self.page.update()
                    refresh_locations_list()
                    
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(translator.get_text("storage.location_created")),
                        bgcolor=DesignSystem.SUCCESS,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
                except Exception as exc:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"{translator.get_text('common.error')}: {exc}"),
                        bgcolor=DesignSystem.ERROR,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
            
            dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text(translator.get_text("storage.create_location")),
                content=ft.Container(
                    content=ft.Column(
                        controls=[parent_dropdown, name_field, code_field, type_field, description_field],
                        spacing=12,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                    width=500,
                    height=450,
                ),
                actions=[
                    ft.TextButton(translator.get_text("common.buttons.cancel"), on_click=lambda e: setattr(dialog, 'open', False) or self.page.update()),
                    ft.ElevatedButton(translator.get_text("common.buttons.add"), on_click=submit, bgcolor=DesignSystem.BLUE_500, color=DesignSystem.WHITE),
                ],
            )
            
            # Modern Flet way: use page.open() instead of page.dialog + page.update()
            try:
                self.page.open(dialog)
            except AttributeError:
                # Fallback to old method if page.open() doesn't exist
                self.page.dialog = dialog
                dialog.open = True
                self.page.update()
            except Exception as open_error:
                # Try fallback
                try:
                    self.page.dialog = dialog
                    dialog.open = True
                    self.page.update()
                except Exception as fallback_error:
                    logger.error(f"Error opening dialog: {fallback_error}")
        
        def open_edit_dialog(location_id):
            """Open edit location dialog"""
            session = SessionLocal()
            try:
                location = get_storage_location(location_id, session)
                if not location:
                    return
                
                all_locations = get_all_storage_locations_flat(session)
                parent_options = [ft.dropdown.Option("", translator.get_text("storage.root_location"))]
                
                from services.storage_service import _get_descendants
                descendants = _get_descendants(session, location_id)
                descendant_ids = {desc.id for desc in descendants}
                descendant_ids.add(location_id)
                
                for loc in all_locations:
                    if loc.id not in descendant_ids:
                        path = get_storage_location_path(loc.id, session)
                        display_text = f"{path}" if path else loc.name
                        parent_options.append(ft.dropdown.Option(str(loc.id), display_text))
                
                parent_dropdown = create_modern_dropdown(
                    label=translator.get_text("storage.parent_location"),
                    options=parent_options,
                    value=str(location.parent_id) if location.parent_id else "",
                )
                
                name_field = create_modern_text_field(label=translator.get_text("storage.location_name"), value=location.name)
                code_field = create_modern_text_field(label=translator.get_text("storage.location_code"), value=location.code or "", hint_text=translator.get_text("common.optional"))
                type_field = create_modern_dropdown(
                    label=translator.get_text("storage.location_type"),
                    value=location.location_type or "",
                    options=[
                        ft.dropdown.Option("warehouse", translator.get_text("storage.type_warehouse")),
                        ft.dropdown.Option("cabinet", translator.get_text("storage.type_cabinet")),
                        ft.dropdown.Option("shelf", translator.get_text("storage.type_shelf")),
                        ft.dropdown.Option("bin", translator.get_text("storage.type_bin")),
                        ft.dropdown.Option("", translator.get_text("storage.type_other")),
                    ],
                )
                description_field = create_modern_text_field(
                    label=translator.get_text("storage.location_description"),
                    value=location.description or "",
                    multiline=True,
                )
                
                def submit(e):
                    try:
                        if not name_field.value:
                            raise ValueError(translator.get_text("common.messages.required_field"))
                        
                        selected_parent_id = None
                        if parent_dropdown.value:
                            try:
                                selected_parent_id = int(parent_dropdown.value)
                            except (ValueError, TypeError):
                                selected_parent_id = None
                        
                        update_storage_location(
                            location_id=location_id,
                            name=name_field.value,
                            parent_id=selected_parent_id,
                            code=code_field.value if code_field.value else None,
                            location_type=type_field.value if type_field.value else None,
                            description=description_field.value if description_field.value else None,
                        )
                        
                        try:
                            self.page.close(dialog)
                        except:
                            dialog.open = False
                            self.page.update()
                        refresh_locations_list()
                        if selected_location_id_ref["value"] == location_id:
                            update_details(location_id)
                        
                        self.page.snack_bar = ft.SnackBar(
                            content=ft.Text(translator.get_text("storage.location_updated")),
                            bgcolor=DesignSystem.SUCCESS,
                        )
                        self.page.snack_bar.open = True
                        self.page.update()
                    except Exception as exc:
                        self.page.snack_bar = ft.SnackBar(
                            content=ft.Text(f"{translator.get_text('common.error')}: {exc}"),
                            bgcolor=DesignSystem.ERROR,
                        )
                        self.page.snack_bar.open = True
                        self.page.update()
                
                dialog = ft.AlertDialog(
                    modal=True,
                    title=ft.Text(translator.get_text("storage.edit_location")),
                    content=ft.Container(
                        content=ft.Column(
                            controls=[parent_dropdown, name_field, code_field, type_field, description_field],
                            spacing=12,
                            scroll=ft.ScrollMode.AUTO,
                        ),
                        width=500,
                        height=450,
                    ),
                    actions=[
                        ft.TextButton(translator.get_text("common.buttons.cancel"), on_click=lambda e: setattr(dialog, 'open', False) or self.page.update()),
                        ft.ElevatedButton(translator.get_text("common.buttons.save"), on_click=submit, bgcolor=DesignSystem.BLUE_500, color=DesignSystem.WHITE),
                    ],
                )
                
                self.page.dialog = dialog
                dialog.open = True
                self.page.update()
            finally:
                session.close()
        
        def open_delete_dialog(location_id):
            """Open delete location dialog"""
            session = SessionLocal()
            try:
                location = get_storage_location(location_id, session)
                if not location:
                    return
                
                def confirm_delete(e):
                    try:
                        delete_storage_location(location_id)
                        try:
                            self.page.close(dialog)
                        except:
                            dialog.open = False
                            self.page.update()
                        refresh_locations_list()
                        if selected_location_id_ref["value"] == location_id:
                            selected_location_id_ref["value"] = None
                            update_details(None)
                        
                        self.page.snack_bar = ft.SnackBar(
                            content=ft.Text(translator.get_text("storage.location_deleted")),
                            bgcolor=DesignSystem.SUCCESS,
                        )
                        self.page.snack_bar.open = True
                        self.page.update()
                    except Exception as exc:
                        self.page.snack_bar = ft.SnackBar(
                            content=ft.Text(f"{translator.get_text('common.error')}: {exc}"),
                            bgcolor=DesignSystem.ERROR,
                        )
                        self.page.snack_bar.open = True
                        self.page.update()
                
                dialog = ft.AlertDialog(
                    modal=True,
                    title=ft.Text(translator.get_text("storage.delete_location")),
                    content=ft.Text(translator.get_text("storage.delete_location_confirm").format(name=location.name)),
                    actions=[
                        ft.TextButton(translator.get_text("common.buttons.cancel"), on_click=lambda e: setattr(dialog, 'open', False) or self.page.update()),
                        ft.ElevatedButton(translator.get_text("common.buttons.delete"), on_click=confirm_delete, bgcolor=DesignSystem.RED_500, color=DesignSystem.WHITE),
                    ],
                )
                
                self.page.dialog = dialog
                dialog.open = True
                self.page.update()
            finally:
                session.close()
        
        def open_assign_part_dialog(part_id_param=None):
            """Open assign part dialog (part_id_param is optional pre-selection)"""
            print(f"[STORAGE] ====== open_assign_part_dialog CALLED ======")
            print(f"[STORAGE] part_id_param: {part_id_param}")
            print(f"[STORAGE] selected_location_id_ref['value']: {selected_location_id_ref.get('value')}")
            
            # If part_id_param is provided, allow assignment even without selected location
            # User will need to select a location in the dialog
            if not selected_location_id_ref["value"] and not part_id_param:
                print(f"[STORAGE] EARLY RETURN: No selected_location_id_ref and no part_id_param")
                return
            
            dialog_page = self.page if hasattr(self, 'page') and self.page else page
            print(f"[STORAGE] dialog_page type: {type(dialog_page)}")
            print(f"[STORAGE] dialog_page exists: {dialog_page is not None}")
            
            session = SessionLocal()
            print(f"[STORAGE] Session created: {session}")
            try:
                # If part_id_param is provided, we only need the part info, not the full parts list
                if part_id_param:
                    print(f"[STORAGE] part_id_param provided: {part_id_param}, querying part from database...")
                    part = session.query(Part).filter_by(id=part_id_param).first()
                    print(f"[STORAGE] Part query result: {part}")
                    if not part:
                        print(f"[STORAGE] ERROR: Part not found for part_id={part_id_param}")
                        dialog_page.snack_bar = ft.SnackBar(
                            content=ft.Text(translator.get_text("common.error") + ": " + translator.get_text("inventory.part_not_found")),
                            bgcolor=DesignSystem.ERROR
                        )
                        dialog_page.snack_bar.open = True
                        dialog_page.update()
                        return
                    
                    # Get inventory level
                    inv_level = session.query(InventoryLevel).filter_by(part_id=part_id_param).first()
                    stock_qty = inv_level.quantity_on_hand if inv_level else 0
                    
                    # Get total assigned quantity to ALL locations
                    from services.storage_service import get_part_locations
                    part_locations = get_part_locations(part_id_param, session)
                    total_assigned = sum(pl['quantity'] for pl in part_locations)
                    available = stock_qty - total_assigned
                    
                    # Use StorageLocationPicker to filter locations (empty or same part_id)
                    print(f"[STORAGE] Creating StorageLocationPicker with part_id={part_id_param}...")
                    from ui.components.storage_location_picker import StorageLocationPicker
                    storage_picker = StorageLocationPicker(page=dialog_page)
                    print(f"[STORAGE] StorageLocationPicker created: {storage_picker}")
                    location_picker_container = storage_picker.build(
                        label=translator.get_text("storage.location"),
                        width=None,
                        part_id=part_id_param,  # Filter to empty locations or locations with same part
                    )
                    print(f"[STORAGE] location_picker_container created: {location_picker_container}")
                    print(f"[STORAGE] storage_picker.dropdown: {storage_picker.dropdown}")
                    
                    # Check if there are any available locations by examining the picker's dropdown options
                    # The picker has: "", "__OTHER__", and then location IDs
                    # Access the dropdown from the storage_picker instance
                    if storage_picker.dropdown and hasattr(storage_picker.dropdown, 'options'):
                        dropdown_options_count = len(storage_picker.dropdown.options)
                        print(f"[STORAGE] Dropdown options count: {dropdown_options_count}")
                        print(f"[STORAGE] Dropdown options: {[opt.key for opt in storage_picker.dropdown.options]}")
                        has_available_locations = dropdown_options_count > 2  # More than just "" and "__OTHER__"
                    else:
                        print(f"[STORAGE] WARNING: storage_picker.dropdown is None or has no options attribute")
                        has_available_locations = False
                    print(f"[STORAGE] has_available_locations: {has_available_locations}")
                    
                    # Create warning message if no available locations
                    no_location_warning = None
                    if not has_available_locations:
                        no_location_warning = ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Icon(
                                        ft.Icons.WARNING if hasattr(ft.Icons, 'WARNING') else ft.Icons.ERROR_OUTLINE,
                                        color=DesignSystem.ORANGE_600,
                                        size=20,
                                    ),
                                    ft.Text(
                                        translator.get_text("storage.no_available_locations") if translator.get_text("storage.no_available_locations") != "storage.no_available_locations" else "Nincs elérhető tárhely. Hozz létre egyet!",
                                        size=14,
                                        color=DesignSystem.ORANGE_600,
                                        weight=ft.FontWeight.W_600,
                                    ),
                                ], spacing=8),
                                ft.TextButton(
                                    text=translator.get_text("storage.create_location") + " →",
                                    icon=ft.Icons.ADD,
                                    on_click=lambda e: (
                                        setattr(dialog, 'open', False),
                                        dialog_page.update(),
                                        open_create_dialog(None),
                                    ),
                                ),
                            ], spacing=8),
                            padding=DesignSystem.SPACING_3,
                            border=ft.border.all(2, DesignSystem.ORANGE_500),
                            border_radius=DesignSystem.RADIUS_MD,
                            bgcolor=DesignSystem.ORANGE_50 if hasattr(DesignSystem, 'ORANGE_50') else "#FFF7ED",
                        )
                else:
                    # Original behavior when part_id_param is not provided
                    print(f"[STORAGE] part_id_param NOT provided, loading all parts...")
                    parts = list_parts(session)
                    print(f"[STORAGE] Loaded {len(parts)} parts")
                    location_picker_container = None
                    no_location_warning = None
                    part = None
                    stock_qty = 0
                    total_assigned = 0
                    available = 0
                    storage_picker = None  # Initialize to None
            finally:
                session.close()
            
            # Initialize parts to empty list if not set (to avoid UnboundLocalError)
            if 'parts' not in locals():
                print(f"[STORAGE] 'parts' not in locals, initializing to empty list")
                parts = []
            
            # Stock info display
            stock_info_text = ft.Text("", size=12, color=DesignSystem.TEXT_SECONDARY)
            available_quantity_text = ft.Text("", size=12, color=DesignSystem.EMERALD_600, weight=ft.FontWeight.W_600)
            
            # Quantity dropdown - will be populated when part is selected
            quantity_dropdown = create_modern_dropdown(
                label=translator.get_text("inventory.quantity"),
                options=[],
            )
            
            # If part_id_param is provided, we already have the part info, so populate quantity dropdown
            if part_id_param and part:
                # Update stock info display
                stock_info_text.value = f"{translator.get_text('inventory.on_hand') or 'Készleten'}: {stock_qty} | {translator.get_text('storage.assigned') or 'Hozzárendelve'}: {total_assigned}"
                available_quantity_text.value = f"{translator.get_text('storage.available') or 'Hozzárendelhető'}: {max(0, available)}"
                
                if available < 0:
                    available_quantity_text.color = DesignSystem.ERROR
                elif available == 0:
                    available_quantity_text.color = DesignSystem.ORANGE_500
                else:
                    available_quantity_text.color = DesignSystem.EMERALD_600
                
                # Update quantity dropdown with available quantities (1 to available)
                if available > 0:
                    quantity_dropdown.options = [
                        ft.dropdown.Option(str(i), str(i))
                        for i in range(1, available + 1)
                    ]
                    quantity_dropdown.value = "1"  # Default to 1
                else:
                    quantity_dropdown.options = []
                    quantity_dropdown.value = None
            
            # Part dropdown - only show if part_id_param is not provided
            part_dropdown = None
            if not part_id_param:
                print(f"[STORAGE] Creating part_dropdown with {len(parts)} parts...")
                # Original behavior: show part dropdown and update stock info when part is selected
                def update_stock_info(part_id_str):
                    """Update stock info and quantity dropdown when part is selected"""
                    if not part_id_str:
                        stock_info_text.value = ""
                        available_quantity_text.value = ""
                        quantity_dropdown.options = []
                        quantity_dropdown.value = None
                        if self.page:
                            self.page.update()
                        return
                    
                    try:
                        part_id = int(part_id_str)
                        session = SessionLocal()
                        try:
                            # Get inventory level
                            inv_level = session.query(InventoryLevel).filter_by(part_id=part_id).first()
                            stock_qty = inv_level.quantity_on_hand if inv_level else 0
                            
                            # Get total assigned quantity to ALL locations
                            from services.storage_service import get_part_locations
                            part_locations = get_part_locations(part_id, session)
                            total_assigned = sum(pl['quantity'] for pl in part_locations)
                            
                            # Available quantity = stock - total assigned (all locations)
                            # This gives us how much we can still assign to ANY location
                            available = stock_qty - total_assigned
                            
                            stock_info_text.value = f"{translator.get_text('inventory.on_hand') or 'Készleten'}: {stock_qty} | {translator.get_text('storage.assigned') or 'Hozzárendelve'}: {total_assigned}"
                            available_quantity_text.value = f"{translator.get_text('storage.available') or 'Hozzárendelhető'}: {max(0, available)}"
                            
                            if available < 0:
                                available_quantity_text.color = DesignSystem.ERROR
                            elif available == 0:
                                available_quantity_text.color = DesignSystem.ORANGE_500
                            else:
                                available_quantity_text.color = DesignSystem.EMERALD_600
                            
                            # Update quantity dropdown with available quantities (1 to available)
                            quantity_dropdown.options = [
                                ft.dropdown.Option(str(i), str(i))
                                for i in range(1, max(1, available + 1))
                            ]
                            if quantity_dropdown.options:
                                quantity_dropdown.value = "1"  # Default to 1
                        finally:
                            session.close()
                        
                        if self.page:
                            self.page.update()
                    except Exception as e:
                        logger.error(f"Error updating stock info: {e}")
                
                part_dropdown = create_modern_dropdown(
                    label=translator.get_text("inventory.part"),
                    options=[ft.dropdown.Option(str(p.id), f"{p.sku} - {p.name}") for p in parts],
                    value=None,
                    on_change=lambda e: update_stock_info(e.control.value),
                )
                print(f"[STORAGE] part_dropdown created")
            else:
                print(f"[STORAGE] part_id_param provided, skipping part_dropdown creation")
            
            notes_field = create_modern_text_field(
                label=translator.get_text("inventory.notes"),
                multiline=True,
                hint_text=translator.get_text("common.optional"),
            )
            
            def submit(e):
                try:
                    # Get part_id - either from part_id_param or from part_dropdown
                    if part_id_param:
                        part_id = part_id_param
                    else:
                        if not part_dropdown or not part_dropdown.value:
                            raise ValueError(translator.get_text("common.messages.required_field"))
                        part_id = int(part_dropdown.value)
                    
                    if not quantity_dropdown.value:
                        raise ValueError(translator.get_text("common.messages.required_field"))
                    
                    quantity = int(quantity_dropdown.value)
                    
                    if quantity <= 0:
                        raise ValueError(translator.get_text("storage.quantity_must_be_positive"))
                    
                    # Get location_id - either from selected_location_id_ref or from location_picker
                    location_id = None
                    if part_id_param and location_picker_container and storage_picker:
                        location_id, other_location = storage_picker.get_value()
                        if not location_id and not other_location:
                            raise ValueError(translator.get_text("storage.location") + " " + translator.get_text("common.messages.required_field"))
                    elif selected_location_id_ref["value"]:
                        location_id = selected_location_id_ref["value"]
                    else:
                        raise ValueError(translator.get_text("storage.location") + " " + translator.get_text("common.messages.required_field"))
                    
                    assign_part_to_location(
                        part_id=part_id,
                        location_id=location_id,
                        quantity=quantity,
                        notes=notes_field.value if notes_field.value else None,
                    )
                    
                    try:
                        self.page.close(dialog)
                    except:
                        dialog.open = False
                        self.page.dialog = None
                        self.page.update()
                    if selected_location_id_ref["value"]:
                        update_details(selected_location_id_ref["value"])
                    
                    # Refresh parts without location list
                    try:
                        refresh_parts_without_location()
                    except:
                        pass
                    
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(translator.get_text("storage.part_assigned")),
                        bgcolor=DesignSystem.SUCCESS,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
                except Exception as exc:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"{translator.get_text('common.error')}: {exc}"),
                        bgcolor=DesignSystem.ERROR,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
            
            # Build dialog content based on whether part_id_param is provided
            dialog_controls = []
            
            if part_id_param:
                # Show part info (read-only)
                dialog_controls.extend([
                    ft.Text(
                        f"{part.name} ({part.sku or '-'})",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=DesignSystem.TEXT_PRIMARY,
                    ),
                    stock_info_text,
                    available_quantity_text,
                ])
                
                # Show warning if no available locations
                if no_location_warning:
                    dialog_controls.append(no_location_warning)
                
                # Show location picker
                dialog_controls.append(location_picker_container)
            else:
                # Original behavior: show part dropdown
                dialog_controls.append(part_dropdown)
            
            # Common controls
            dialog_controls.extend([
                quantity_dropdown,
                notes_field,
            ])
            
            print(f"[STORAGE] Creating AlertDialog...")
            print(f"[STORAGE] dialog_controls count: {len(dialog_controls)}")
            for i, control in enumerate(dialog_controls):
                print(f"[STORAGE]   dialog_controls[{i}]: {type(control)}")
            
            dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text(translator.get_text("storage.assign_part")),
                content=ft.Container(
                    content=ft.Column(
                        controls=dialog_controls,
                        spacing=12,
                    ),
                    width=500,
                ),
                actions=[
                    ft.TextButton(translator.get_text("common.buttons.cancel"), on_click=lambda e: setattr(dialog, 'open', False) or self.page.update()),
                    ft.ElevatedButton(translator.get_text("common.buttons.add"), on_click=submit, bgcolor=DesignSystem.EMERALD_500, color=DesignSystem.WHITE),
                ],
            )
            print(f"[STORAGE] AlertDialog created: {dialog}")
            
            # Modern Flet way: use page.open() instead of page.dialog + page.update()
            print(f"[STORAGE] Attempting to open dialog...")
            print(f"[STORAGE] self.page type: {type(self.page)}")
            print(f"[STORAGE] self.page has 'open' method: {hasattr(self.page, 'open')}")
            try:
                print(f"[STORAGE] Trying self.page.open(dialog)...")
                self.page.open(dialog)
                print(f"[STORAGE] self.page.open(dialog) succeeded")
            except AttributeError as ae:
                print(f"[STORAGE] AttributeError in page.open(): {ae}")
                # Fallback to old method if page.open() doesn't exist
                print(f"[STORAGE] Falling back to page.dialog method...")
                try:
                    self.page.dialog = dialog
                    dialog.open = True
                    self.page.update()
                    print(f"[STORAGE] Dialog opened using fallback method")
                except Exception as fallback_error:
                    print(f"[STORAGE] ERROR in fallback method: {fallback_error}")
                    logger.error(f"Error opening dialog: {fallback_error}")
            except Exception as open_error:
                print(f"[STORAGE] Exception in page.open(): {open_error}")
                import traceback
                traceback.print_exc()
                # Try fallback
                try:
                    print(f"[STORAGE] Trying fallback method after exception...")
                    self.page.dialog = dialog
                    dialog.open = True
                    self.page.update()
                    print(f"[STORAGE] Dialog opened using fallback method after exception")
                except Exception as fallback_error:
                    print(f"[STORAGE] ERROR in fallback method: {fallback_error}")
                    import traceback
                    traceback.print_exc()
                    logger.error(f"Error opening dialog: {fallback_error}")
        
        def open_edit_part_dialog(part_location_id):
            """Open edit part location dialog"""
            session = SessionLocal()
            try:
                from database.models import PartLocation
                part_location = session.query(PartLocation).filter_by(id=part_location_id).first()
                if not part_location:
                    return
                
                quantity_field = create_modern_text_field(
                    label=translator.get_text("inventory.quantity"),
                    keyboard_type=ft.KeyboardType.NUMBER,
                    value=str(part_location.quantity),
                )
                notes_field = create_modern_text_field(
                    label=translator.get_text("inventory.notes"),
                    value=part_location.notes or "",
                    multiline=True,
                )
                
                def submit(e):
                    try:
                        if not quantity_field.value:
                            raise ValueError(translator.get_text("common.messages.required_field"))
                        
                        quantity = int(quantity_field.value)
                        if quantity < 0:
                            raise ValueError(translator.get_text("storage.quantity_cannot_be_negative"))
                        
                        update_part_location(
                            part_location_id=part_location_id,
                            quantity=quantity,
                            notes=notes_field.value if notes_field.value else None,
                        )
                        
                        try:
                            self.page.close(dialog)
                        except:
                            dialog.open = False
                            self.page.update()
                        update_details(selected_location_id_ref["value"])
                        
                        self.page.snack_bar = ft.SnackBar(
                            content=ft.Text(translator.get_text("storage.part_location_updated")),
                            bgcolor=DesignSystem.SUCCESS,
                        )
                        self.page.snack_bar.open = True
                        self.page.update()
                    except Exception as exc:
                        self.page.snack_bar = ft.SnackBar(
                            content=ft.Text(f"{translator.get_text('common.error')}: {exc}"),
                            bgcolor=DesignSystem.ERROR,
                        )
                        self.page.snack_bar.open = True
                        self.page.update()
                
                dialog = ft.AlertDialog(
                    modal=True,
                    title=ft.Text(translator.get_text("storage.edit_part_location")),
                    content=ft.Container(
                        content=ft.Column(controls=[quantity_field, notes_field], spacing=12),
                        width=500,
                    ),
                    actions=[
                        ft.TextButton(translator.get_text("common.buttons.cancel"), on_click=lambda e: setattr(dialog, 'open', False) or self.page.update()),
                        ft.ElevatedButton(translator.get_text("common.buttons.save"), on_click=submit, bgcolor=DesignSystem.BLUE_500, color=DesignSystem.WHITE),
                    ],
                )
                
                self.page.dialog = dialog
                dialog.open = True
                self.page.update()
            finally:
                session.close()
        
        def open_transfer_part_dialog(part_location_id):
            """Open transfer part to another location dialog"""
            session = SessionLocal()
            try:
                from database.models import PartLocation
                from services.storage_service import get_all_storage_locations_flat, get_storage_location_path, transfer_part_location
                
                part_location = session.query(PartLocation).filter_by(id=part_location_id).first()
                if not part_location:
                    return
                
                # Get all locations except current, but only leaf nodes (locations without children)
                from database.models import StorageLocation
                all_locations = get_all_storage_locations_flat(session)
                target_location_options = []
                for loc in all_locations:
                    if loc.id != part_location.storage_location_id:
                        # Check if this location has children (if it does, it's not a leaf node)
                        children_count = session.query(StorageLocation).filter_by(
                            parent_id=loc.id,
                            is_active=True
                        ).count()
                        
                        # Only include leaf nodes (locations without children)
                        if children_count == 0:
                            path = get_storage_location_path(loc.id, session)
                            display_text = f"{path}" if path else loc.name
                            target_location_options.append(ft.dropdown.Option(str(loc.id), display_text))
                
                if not target_location_options:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(translator.get_text("storage.no_other_locations") or "Nincs másik tárhely"),
                        bgcolor=DesignSystem.WARNING,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
                    return
                
                target_location_dropdown = create_modern_dropdown(
                    label=translator.get_text("storage.target_location") or "Cél tárhely",
                    options=target_location_options,
                )
                
                quantity_dropdown = create_modern_dropdown(
                    label=translator.get_text("inventory.quantity"),
                    options=[
                        ft.dropdown.Option(str(i), str(i))
                        for i in range(1, part_location.quantity + 1)
                    ],
                )
                if quantity_dropdown.options:
                    quantity_dropdown.value = str(part_location.quantity)  # Default to all
                
                notes_field = create_modern_text_field(
                    label=translator.get_text("inventory.notes"),
                    multiline=True,
                    hint_text=translator.get_text("common.required"),
                )
                
                def submit(e):
                    try:
                        if not target_location_dropdown.value:
                            raise ValueError(translator.get_text("common.messages.required_field"))
                        if not quantity_dropdown.value:
                            raise ValueError(translator.get_text("common.messages.required_field"))
                        if not notes_field.value or not notes_field.value.strip():
                            raise ValueError(translator.get_text("common.messages.required_field") + ": " + translator.get_text("inventory.notes"))
                        
                        target_location_id = int(target_location_dropdown.value)
                        quantity = int(quantity_dropdown.value)
                        notes = notes_field.value.strip()
                        
                        if quantity <= 0:
                            raise ValueError(translator.get_text("storage.quantity_must_be_positive"))
                        
                        if quantity > part_location.quantity:
                            raise ValueError(f"Cannot transfer {quantity} units, only {part_location.quantity} available")
                        
                        transfer_part_location(
                            part_location_id=part_location_id,
                            target_location_id=target_location_id,
                            quantity=quantity,
                            notes=notes,
                        )
                        
                        try:
                            self.page.close(dialog)
                        except:
                            dialog.open = False
                            self.page.dialog = None
                            self.page.update()
                        
                        # Refresh details
                        update_details(selected_location_id_ref["value"])
                        
                        self.page.snack_bar = ft.SnackBar(
                            content=ft.Text(translator.get_text("storage.part_transferred") or "Alkatrész sikeresen áttárazva"),
                            bgcolor=DesignSystem.SUCCESS,
                        )
                        self.page.snack_bar.open = True
                        self.page.update()
                    except Exception as exc:
                        self.page.snack_bar = ft.SnackBar(
                            content=ft.Text(f"{translator.get_text('common.error')}: {exc}"),
                            bgcolor=DesignSystem.ERROR,
                        )
                        self.page.snack_bar.open = True
                        self.page.update()
                
                dialog = ft.AlertDialog(
                    modal=True,
                    title=ft.Text(translator.get_text("storage.transfer_part") or "Alkatrész áttárazása"),
                    content=ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text(
                                    f"{part_location.part.name if part_location.part else 'N/A'} ({part_location.quantity} db)",
                                    size=14,
                                    weight=ft.FontWeight.W_600,
                                ),
                                target_location_dropdown,
                                quantity_dropdown,
                                notes_field,
                            ],
                            spacing=12,
                        ),
                        width=500,
                    ),
                    actions=[
                        ft.TextButton(
                            translator.get_text("common.buttons.cancel"),
                            on_click=lambda e: setattr(dialog, 'open', False) or self.page.update(),
                        ),
                        ft.ElevatedButton(
                            translator.get_text("storage.transfer") or "Áttárazás",
                            on_click=submit,
                            bgcolor=DesignSystem.PURPLE_500,
                            color=DesignSystem.WHITE,
                        ),
                    ],
                )
                
                try:
                    self.page.open(dialog)
                except:
                    self.page.dialog = dialog
                    dialog.open = True
                    self.page.update()
            finally:
                session.close()
        
        def open_remove_part_dialog(part_location_id):
            """Open remove part dialog"""
            def confirm_remove(e):
                try:
                    remove_part_from_location(part_location_id)
                    try:
                        self.page.close(dialog)
                    except:
                        dialog.open = False
                        self.page.dialog = None
                        self.page.update()
                    update_details(selected_location_id_ref["value"])
                    
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(translator.get_text("storage.part_removed")),
                        bgcolor=DesignSystem.SUCCESS,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
                except Exception as exc:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"{translator.get_text('common.error')}: {exc}"),
                        bgcolor=DesignSystem.ERROR,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
            
            dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text(translator.get_text("storage.remove_part")),
                content=ft.Text(translator.get_text("storage.remove_part_confirm")),
                actions=[
                    ft.TextButton(translator.get_text("common.buttons.cancel"), on_click=lambda e: setattr(dialog, 'open', False) or self.page.update()),
                    ft.ElevatedButton(translator.get_text("common.buttons.delete"), on_click=confirm_remove, bgcolor=DesignSystem.RED_500, color=DesignSystem.WHITE),
                ],
            )
            
            # Modern Flet way: use page.open() instead of page.dialog + page.update()
            try:
                self.page.open(dialog)
            except AttributeError:
                # Fallback to old method if page.open() doesn't exist
                self.page.dialog = dialog
                dialog.open = True
                self.page.update()
            except Exception as open_error:
                # Try fallback
                try:
                    self.page.dialog = dialog
                    dialog.open = True
                    self.page.update()
                except Exception as fallback_error:
                    logger.error(f"Error opening dialog: {fallback_error}")
        
        # Search section
        search_field = create_modern_text_field(
            label=translator.get_text("storage.search_parts"),
            hint_text=translator.get_text("storage.search_parts_hint"),
            width=400,
        )
        
        search_results_container = ft.Container(
            visible=False,
            content=ft.Column([], spacing=8),
        )
        
        def on_search_change(e):
            search_term = e.control.value.strip()
            if not search_term or len(search_term) < 2:
                search_results_container.visible = False
                self.page.update()
                return
            
            session = SessionLocal()
            try:
                results = search_parts_by_location(search_term, session)
                
                if not results:
                    search_results_container.content = ft.Text(
                        translator.get_text("storage.no_search_results"),
                        size=14,
                        color=DesignSystem.TEXT_SECONDARY,
                    )
                else:
                    result_items = []
                    for result in results:
                        locations_text = "\n".join([
                            f"  • {loc['location_path']}: {loc['quantity']}"
                            for loc in result['locations']
                        ])
                        
                        result_items.append(
                            ft.Container(
                                content=ft.Column(
                                    controls=[
                                        ft.Row(
                                            controls=[
                                                ft.Text(result['part_name'], size=14, weight=ft.FontWeight.W_600),
                                                create_vibrant_badge(text=result['part_sku'], variant="blue", size=11),
                                                ft.Text(f"{translator.get_text('inventory.total')}: {result['total_quantity']}", size=12, color=DesignSystem.TEXT_SECONDARY),
                                            ],
                                            spacing=8,
                                        ),
                                        ft.Text(locations_text, size=12, color=DesignSystem.TEXT_SECONDARY),
                                    ],
                                    spacing=4,
                                ),
                                padding=DesignSystem.SPACING_3,
                                border=ft.border.all(1, DesignSystem.BORDER_COLOR),
                                border_radius=DesignSystem.RADIUS_MD,
                                bgcolor=DesignSystem.BG_SECONDARY,
                            )
                        )
                    
                    search_results_container.content = ft.Column(controls=result_items, spacing=8)
                
                search_results_container.visible = True
                self.page.update()
            finally:
                session.close()
        
        search_field.on_change = on_search_change
        
        search_section = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.SEARCH, color=DesignSystem.TEXT_SECONDARY),
                        ft.Container(width=10),
                        search_field,
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Container(height=10),
                search_results_container,
            ],
            spacing=8,
        )
        
        # Tree section with title
        tree_title_row = ft.Row(
            controls=[
                ft.Text(translator.get_text("storage.locations"), size=16, weight=ft.FontWeight.BOLD, color=DesignSystem.TEXT_PRIMARY),
                ft.Container(expand=True),
                create_modern_button(
                    text="+ " + translator.get_text("storage.add_root_location"),
                    icon=ft.Icons.ADD,
                    on_click=lambda e: open_create_dialog(None),
                    bgcolor=DesignSystem.BLUE_500,
                    color=DesignSystem.WHITE,
                    height=36,
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        
        # Parts without storage location section
        parts_without_location_list = ft.Column([], spacing=8, scroll=ft.ScrollMode.AUTO)
        
        def refresh_parts_without_location():
            """Refresh the list of parts without storage location"""
            session = SessionLocal()
            try:
                # Get all parts that have inventory level (even if quantity is 0)
                # Filter out parts that have PartLocation
                parts_with_location_ids = session.query(PartLocation.part_id).distinct().all()
                parts_with_location_ids_set = {pl[0] for pl in parts_with_location_ids}
                
                # Get all parts that have an inventory level, but no PartLocation
                parts_with_inventory = session.query(Part).join(
                    InventoryLevel, Part.id == InventoryLevel.part_id
                ).all()
                
                parts_without_location = [p for p in parts_with_inventory if p.id not in parts_with_location_ids_set]
                
                parts_without_location_list.controls.clear()
                
                if not parts_without_location:
                    parts_without_location_list.controls.append(
                        ft.Container(
                            content=ft.Text(
                                translator.get_text("storage.no_parts_without_location") if translator.get_text("storage.no_parts_without_location") != "storage.no_parts_without_location" else "Nincs tárhely nélküli alkatrész",
                                size=14,
                                color=DesignSystem.TEXT_SECONDARY,
                                italic=True,
                            ),
                            padding=20,
                            alignment=ft.alignment.center,
                        )
                    )
                else:
                    for part in parts_without_location:
                        inv_level = session.query(InventoryLevel).filter_by(part_id=part.id).first()
                        stock_qty = inv_level.quantity_on_hand if inv_level else 0
                        
                        # Build row controls, filtering out None values
                        row_controls = [
                            ft.Text(
                                part.name,
                                size=14,
                                weight=ft.FontWeight.W_600,
                                color=DesignSystem.TEXT_PRIMARY,
                            ),
                        ]
                        if part.sku:
                            row_controls.append(create_vibrant_badge(
                                text=part.sku or "-",
                                variant="blue",
                                size=11,
                            ))
                        if stock_qty > 0:
                            row_controls.append(create_vibrant_badge(
                                text=f"{stock_qty} {part.unit}",
                                variant="emerald",
                                size=11,
                            ))
                        
                        # Build column controls, filtering out None values
                        column_controls = [
                            ft.Row(row_controls, spacing=8),
                        ]
                        if part.category:
                            column_controls.append(ft.Text(
                                part.category or "-",
                                size=12,
                                color=DesignSystem.TEXT_SECONDARY,
                            ))
                        
                        def create_assign_button_click_handler(part_id):
                            """Create a click handler for the assign button with proper closure"""
                            def button_click_handler(e):
                                print(f"[STORAGE] ====== ASSIGN BUTTON CLICKED ======")
                                print(f"[STORAGE] Event: {e}")
                                print(f"[STORAGE] Event type: {type(e)}")
                                print(f"[STORAGE] Event control: {e.control if hasattr(e, 'control') else 'N/A'}")
                                print(f"[STORAGE] part_id from closure: {part_id}")
                                print(f"[STORAGE] part_id type: {type(part_id)}")
                                try:
                                    print(f"[STORAGE] Calling open_assign_part_dialog_for_part({part_id})...")
                                    open_assign_part_dialog_for_part(part_id)
                                    print(f"[STORAGE] open_assign_part_dialog_for_part returned")
                                except Exception as btn_exc:
                                    print(f"[STORAGE] ERROR in button click handler: {btn_exc}")
                                    import traceback
                                    traceback.print_exc()
                                    if hasattr(self, 'page') and self.page:
                                        self.page.snack_bar = ft.SnackBar(
                                            content=ft.Text(f"Hiba a gomb kattintásnál: {str(btn_exc)}"),
                                            bgcolor=DesignSystem.ERROR,
                                        )
                                        self.page.snack_bar.open = True
                                        self.page.update()
                            return button_click_handler
                        
                        assign_button = create_modern_button(
                            text=translator.get_text("storage.assign_to_location") if translator.get_text("storage.assign_to_location") != "storage.assign_to_location" else "Tárhelyhez rendelés",
                            icon=ft.Icons.ASSIGNMENT if hasattr(ft.Icons, 'ASSIGNMENT') else ft.Icons.ADD,
                            on_click=create_assign_button_click_handler(part.id),
                            bgcolor=DesignSystem.ORANGE_500,
                            color=DesignSystem.WHITE,
                            height=48,  # Taller button for better spacing
                        )
                        print(f"[STORAGE] Assign button created for part.id={part.id}")
                        
                        part_card = ft.Container(
                            content=ft.Row([
                                ft.Column(column_controls, spacing=4, expand=True),
                                assign_button,
                            ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                            padding=ft.padding.symmetric(horizontal=DesignSystem.SPACING_4, vertical=DesignSystem.SPACING_4),
                            border=ft.border.all(1, DesignSystem.BORDER_COLOR),
                            border_radius=DesignSystem.RADIUS_MD,
                            bgcolor=DesignSystem.BG_SECONDARY,
                        )
                        parts_without_location_list.controls.append(part_card)
                    
                    if self.page:
                        self.page.update()
            except Exception as e:
                logger.error(f"Error refreshing parts without location: {e}", exc_info=True)
            finally:
                session.close()
        
        def open_assign_part_dialog_for_part(part_id_param):
            """Open assign part dialog with pre-selected part (for parts without location list)"""
            print(f"[STORAGE] ====== open_assign_part_dialog_for_part CALLED ======")
            print(f"[STORAGE] part_id_param: {part_id_param}, type: {type(part_id_param)}")
            print(f"[STORAGE] self.page exists: {hasattr(self, 'page')}")
            if hasattr(self, 'page'):
                print(f"[STORAGE] self.page type: {type(self.page)}")
            try:
                # Call the existing open_assign_part_dialog with part_id_param
                print(f"[STORAGE] Calling open_assign_part_dialog({part_id_param})...")
                open_assign_part_dialog(part_id_param)
                print(f"[STORAGE] open_assign_part_dialog returned successfully")
            except Exception as e:
                print(f"[STORAGE] ERROR in open_assign_part_dialog_for_part: {e}")
                import traceback
                traceback.print_exc()
                # Show error to user
                if hasattr(self, 'page') and self.page:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"Hiba: {str(e)}"),
                        bgcolor=DesignSystem.ERROR,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
        
        tree_section = ft.Column(
            controls=[
                tree_title_row,
                ft.Divider(height=10, color="transparent"),
                locations_list,  # Direct list - SAME as inventory_screen parts_list
            ],
            spacing=8,
            expand=True,
        )
        
        # Initial load
        refresh_locations_list()
        
        # Create add button
        add_btn = create_modern_button(
            text=translator.get_text("storage.create_location"),
            icon=ft.Icons.ADD,
            on_click=lambda e: open_create_dialog(None),
            bgcolor=DesignSystem.EMERALD_500,
            color=DesignSystem.WHITE,
            height=40,
        )
        
        # Create history button
        def open_history(e):
            """Open storage history screen"""
            from ui.screens.storage_history_screen import StorageHistoryScreen
            history_screen = StorageHistoryScreen(self.page)
            # Replace current view with history view
            page.views.append(
                ft.View(
                    route="/storage/history",
                    controls=[history_screen.view(page)],
                    appbar=ft.AppBar(
                        title=ft.Text(translator.get_text("storage.history") or "Raktártörténet"),
                        leading=ft.IconButton(
                            icon=ft.Icons.ARROW_BACK,
                            on_click=lambda e: page.views.pop() or page.update(),
                        ),
                    ),
                )
            )
            page.update()
        
        history_btn = create_modern_button(
            text=translator.get_text("storage.history") or "Raktártörténet",
            icon=ft.Icons.HISTORY,
            on_click=open_history,
            bgcolor=DesignSystem.PURPLE_500,
            color=DesignSystem.WHITE,
            height=40,
        )
        
        # Main content: Tree + Details
        main_content = ft.Row(
            controls=[
                # Left: Tree
                ft.Container(
                    content=tree_section,
                    width=350,
                    border=ft.border.all(1, DesignSystem.BORDER_COLOR),
                    border_radius=DesignSystem.RADIUS_LG,
                    padding=DesignSystem.SPACING_4,
                    bgcolor=DesignSystem.BG_SECONDARY,
                    expand=False,
                ),
                # Center: Details
                ft.Container(
                    content=details_container,
                    expand=True,
                    border=ft.border.all(1, DesignSystem.BORDER_COLOR),
                    border_radius=DesignSystem.RADIUS_LG,
                    padding=DesignSystem.SPACING_4,
                    bgcolor=DesignSystem.BG_SECONDARY,
                    margin=ft.margin.only(left=DesignSystem.SPACING_4),
                ),
            ],
            spacing=DesignSystem.SPACING_4,
            expand=True,
        )
        
        # Parts without location section
        parts_without_location_section = ft.ExpansionTile(
            title=ft.Text(
                translator.get_text("storage.parts_without_location") if translator.get_text("storage.parts_without_location") != "storage.parts_without_location" else "Tárhely nélküli alkatrészek",
                size=16,
                weight=ft.FontWeight.BOLD,
                color=DesignSystem.ORANGE_600,
            ),
            subtitle=ft.Text(
                translator.get_text("storage.parts_without_location_warning") if translator.get_text("storage.parts_without_location_warning") != "storage.parts_without_location_warning" else "Figyelmeztetés: ezeket az alkatrészeket tárhelyhez kellene rendelni!",
                size=12,
                color=DesignSystem.ORANGE_600,
                italic=True,
            ),
            leading=ft.Icon(
                ft.Icons.WARNING if hasattr(ft.Icons, 'WARNING') else ft.Icons.ERROR_OUTLINE,
                size=24,
                color=DesignSystem.ORANGE_600,
            ),
            controls=[
                ft.Container(
                    content=parts_without_location_list,
                    padding=DesignSystem.SPACING_3,
                ),
            ],
            initially_expanded=False,
        )
        
        # Store refresh function reference for external calls
        self._refresh_parts_without_location = refresh_parts_without_location
        
        # Initial load of parts without location
        refresh_parts_without_location()
        
        # Validation button
        def open_validation_dialog(e):
            dialog_page = self.page if hasattr(self, 'page') and self.page else page
            discrepancies = validate_inventory_levels()
            
            if not discrepancies:
                # No discrepancies - show success message
                dialog_page.snack_bar = ft.SnackBar(
                    content=ft.Text(translator.get_text("storage.validation_no_errors") if translator.get_text("storage.validation_no_errors") != "storage.validation_no_errors" else "Nincs eltérés az adatok között."),
                    bgcolor=DesignSystem.SUCCESS
                )
                dialog_page.snack_bar.open = True
                dialog_page.update()
                return
            
            # Show discrepancies
            discrepancies_list = ft.Column([], spacing=8, scroll=ft.ScrollMode.AUTO)
            for disc in discrepancies:
                card = ft.Card(
                    elevation=1,
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text(disc['part_name'], size=14, weight=ft.FontWeight.BOLD, expand=True),
                                ft.Container(
                                    content=ft.Text(
                                        f"Eltérés: {disc['difference']:+d}",
                                        size=12,
                                        weight=ft.FontWeight.BOLD,
                                        color="#FFFFFF"
                                    ),
                                    bgcolor=DesignSystem.ERROR if abs(disc['difference']) > 0 else DesignSystem.SUCCESS,
                                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                    border_radius=4,
                                ),
                            ], spacing=8),
                            ft.Text(f"InventoryLevel: {disc['inventory_level']}", size=11, color="#6B7280"),
                            ft.Text(f"PartLocation[] összeg: {disc['total_in_locations']}", size=11, color="#6B7280"),
                            ft.Row([
                                ft.TextButton(
                                    "Javítás",
                                    on_click=lambda _, pid=disc['part_id']: fix_discrepancy(pid),
                                    style=ft.ButtonStyle(color=DesignSystem.PRIMARY),
                                ),
                            ], spacing=8),
                        ], spacing=6),
                        padding=12,
                    ),
                )
                discrepancies_list.controls.append(card)
            
            def fix_discrepancy(part_id_val):
                try:
                    fix_inventory_level_discrepancy(part_id_val)
                    dialog_page.snack_bar = ft.SnackBar(
                        content=ft.Text(translator.get_text("storage.validation_fixed") if translator.get_text("storage.validation_fixed") != "storage.validation_fixed" else "Eltérés javítva."),
                        bgcolor=DesignSystem.SUCCESS
                    )
                    dialog_page.snack_bar.open = True
                    # Refresh dialog
                    open_validation_dialog(None)
                    dialog_page.update()
                except Exception as ex:
                    dialog_page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"Hiba: {ex}"),
                        bgcolor=DesignSystem.ERROR
                    )
                    dialog_page.snack_bar.open = True
                    dialog_page.update()
            
            validation_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Row([
                    ft.Icon(ft.Icons.VERIFIED if hasattr(ft.Icons, 'VERIFIED') else ft.Icons.CHECK_CIRCLE, color="#6366F1", size=24),
                    ft.Text(
                        translator.get_text("storage.validation_title") if translator.get_text("storage.validation_title") != "storage.validation_title" else "Készlet validáció",
                        size=20,
                        weight=ft.FontWeight.BOLD
                    ),
                ], spacing=10),
                content=ft.Container(
                    content=ft.Column([
                        ft.Text(
                            translator.get_text("storage.validation_description") if translator.get_text("storage.validation_description") != "storage.validation_description" else f"{len(discrepancies)} eltérés található.",
                            size=14,
                            color=DesignSystem.TEXT_SECONDARY
                        ),
                        ft.Divider(),
                        discrepancies_list,
                    ], spacing=12),
                    width=700,
                    height=500,
                    padding=20,
                ),
                actions=[
                    ft.TextButton(
                        translator.get_text("common.buttons.close"),
                        on_click=lambda _: (setattr(validation_dialog, 'open', False), dialog_page.update()),
                    ),
                ],
            )
            
            try:
                dialog_page.open(validation_dialog)
            except:
                dialog_page.dialog = validation_dialog
                validation_dialog.open = True
                dialog_page.update()
        
        validation_btn = create_modern_button(
            text=translator.get_text("storage.validate") if translator.get_text("storage.validate") != "storage.validate" else "Validáció",
            icon=ft.Icons.VERIFIED if hasattr(ft.Icons, 'VERIFIED') else ft.Icons.CHECK_CIRCLE,
            on_click=open_validation_dialog,
            variant="outlined",
        )
        
        # Return simple Column - EXACTLY like inventory_screen.py
        return ft.Column([
            ft.Row([
                ft.Text(translator.get_text("storage.title"), size=24, weight=ft.FontWeight.BOLD, color=DesignSystem.TEXT_PRIMARY),
                ft.Container(expand=True),
                validation_btn,
                ft.Container(width=10),
                history_btn,
                ft.Container(width=10),
                add_btn,
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Divider(height=20, color="transparent"),
            search_section,
            ft.Divider(height=10, color="transparent"),
            parts_without_location_section,
            ft.Divider(height=10, color="transparent"),
            main_content,
        ], spacing=12, expand=True)
