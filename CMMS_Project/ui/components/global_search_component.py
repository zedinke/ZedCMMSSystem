"""
Global Search Component
Provides a search field that appears in the topbar on all pages
"""
import flet as ft
from services.search_service import global_search
from localization.translator import translator
from ui.components.modern_components import DesignSystem, create_modern_text_field
import logging

logger = logging.getLogger(__name__)


def create_global_search_field(page: ft.Page) -> ft.Container:
    """
    Create a global search field component for the topbar
    
    Args:
        page: Flet page instance
    
    Returns:
        Container with search field and results dropdown
    """
    def on_search_change(e):
        """Wrapper for search change handler"""
        query = e.control.value if e.control.value else ""
        _on_search_change(page, query)
    
    def on_search_submit(e):
        """Wrapper for search submit handler"""
        query = e.control.value if e.control.value else ""
        _on_search_submit(page, query)
    
    search_field = ft.TextField(
        label=translator.get_text("common.search") if hasattr(translator, 'get_text') else "Keresés...",
        hint_text=translator.get_text("common.search_hint") if hasattr(translator, 'get_text') else "Keresés gépekben, alkatrészekben, munkalapokban...",
        prefix_icon=ft.Icons.SEARCH if hasattr(ft.Icons, 'SEARCH') else ft.Icons.SEARCH_OUTLINED,
        width=400,
        height=40,
        border_radius=8,
        bgcolor=DesignSystem.BG_PRIMARY,
        border_color=DesignSystem.BORDER_COLOR,
        focused_border_color=DesignSystem.PRIMARY,
        on_change=on_search_change,
        on_submit=on_search_submit,
    )
    
    # Results container (initially hidden)
    results_container = ft.Container(
        content=ft.Column(
            controls=[],
            spacing=4,
            scroll=ft.ScrollMode.AUTO,
            height=400,  # Fixed height instead of max_height
        ),
        bgcolor=DesignSystem.BG_SECONDARY,
        border=ft.border.all(1, DesignSystem.BORDER_COLOR),
        border_radius=8,
        padding=8,
        visible=False,
        width=500,
    )
    
    # Main container with search field and results
    search_container = ft.Container(
        content=ft.Column(
            controls=[
                search_field,
                results_container,
            ],
            spacing=4,
            tight=True,
        ),
        padding=0,
    )
    
    # Store references in page for later access
    if not hasattr(page, '_global_search'):
        page._global_search = {
            'field': search_field,
            'results': results_container,
            'search_container': search_container,
            'parent_column': search_container.content,  # Store reference to parent Column
        }
    else:
        # Update references if they already exist
        page._global_search['field'] = search_field
        page._global_search['results'] = results_container
        page._global_search['search_container'] = search_container
        page._global_search['parent_column'] = search_container.content
    
    return search_container


def _on_search_change(page: ft.Page, query: str):
    """Handle search field change - show results as user types"""
    print(f"[SEARCH DEBUG] _on_search_change called with query: '{query}'")
    print(f"[SEARCH DEBUG] Query type: {type(query)}, length: {len(query) if query else 0}")
    
    if not query:
        print("[SEARCH DEBUG] Query is empty, hiding results")
        _hide_results(page)
        return
    
    query = query.strip()
    if len(query) < 2:
        print(f"[SEARCH DEBUG] Query too short ({len(query)} chars), hiding results")
        _hide_results(page)
        return
    
    try:
        print(f"[SEARCH DEBUG] Performing search for: '{query}'")
        # Always perform fresh search
        results = global_search(query, limit=5)
        print(f"[SEARCH DEBUG] Search returned {sum(len(v) for v in results.values())} total results")
        print(f"[SEARCH DEBUG] Results breakdown: machines={len(results.get('machines', []))}, parts={len(results.get('parts', []))}, worksheets={len(results.get('worksheets', []))}, users={len(results.get('users', []))}, storage={len(results.get('storage_locations', []))}")
        _display_results(page, results, query)
        print(f"[SEARCH DEBUG] _display_results completed")
    except Exception as e:
        print(f"[SEARCH DEBUG] Error in _on_search_change: {e}")
        logger.error(f"Error performing search: {e}", exc_info=True)
        _hide_results(page)


def _on_search_submit(page: ft.Page, query: str):
    """Handle search field submit (Enter key)"""
    if not query or len(query.strip()) < 2:
        return
    
    try:
        results = global_search(query, limit=10)
        _display_results(page, results, query)
    except Exception as e:
        logger.error(f"Error performing search: {e}", exc_info=True)


def _display_results(page: ft.Page, results: dict, query: str):
    """Display search results in a dropdown"""
    print(f"[SEARCH DEBUG] _display_results called with query: '{query}'")
    print(f"[SEARCH DEBUG] Results count: {sum(len(v) for v in results.values())}")
    logger.debug(f"_display_results called with query: '{query}', results count: {sum(len(v) for v in results.values())}")
    
    if not hasattr(page, '_global_search'):
        print("[SEARCH DEBUG] ERROR: _global_search not found on page")
        logger.warning("_global_search not found on page")
        return
    
    print(f"[SEARCH DEBUG] _global_search found, keys: {list(page._global_search.keys())}")
    results_container = page._global_search.get('results')
    if not results_container:
        print("[SEARCH DEBUG] ERROR: results_container not found in _global_search")
        logger.warning("results_container not found in _global_search")
        return
    
    print(f"[SEARCH DEBUG] Results container found, type: {type(results_container)}")
    print(f"[SEARCH DEBUG] Results container visible: {results_container.visible}")
    print(f"[SEARCH DEBUG] Results container content type: {type(results_container.content)}")
    logger.debug(f"Results container found, visible: {results_container.visible}")
    
    # Always create fresh result items list
    result_items = []
    print(f"[SEARCH DEBUG] Starting to build result_items list")
    
    try:
        # Machines
        if results.get("machines"):
            print(f"[SEARCH DEBUG] Processing {len(results.get('machines', []))} machines")
            result_items.append(
                ft.Container(
                    content=ft.Text(
                        translator.get_text("menu.assets") if hasattr(translator, 'get_text') else "Gépek",
                        size=12,
                        weight=ft.FontWeight.BOLD,
                        color=DesignSystem.TEXT_SECONDARY,
                    ),
                    padding=ft.padding.only(bottom=4),
                )
            )
            for item in results["machines"]:
                result_items.append(_create_result_item(page, item, "assets"))
            print(f"[SEARCH DEBUG] Added {len(results.get('machines', []))} machine items")
        
        # Parts
        if results.get("parts"):
            print(f"[SEARCH DEBUG] Processing {len(results.get('parts', []))} parts")
            if result_items:
                result_items.append(ft.Divider(height=8, color="transparent"))
            result_items.append(
                ft.Container(
                    content=ft.Text(
                        translator.get_text("menu.inventory") if hasattr(translator, 'get_text') else "Alkatrészek",
                        size=12,
                        weight=ft.FontWeight.BOLD,
                        color=DesignSystem.TEXT_SECONDARY,
                    ),
                    padding=ft.padding.only(bottom=4),
                )
            )
            for item in results["parts"]:
                result_items.append(_create_result_item(page, item, "inventory"))
            print(f"[SEARCH DEBUG] Added {len(results.get('parts', []))} part items")
        
        # Worksheets
        if results.get("worksheets"):
            print(f"[SEARCH DEBUG] Processing {len(results.get('worksheets', []))} worksheets")
            if result_items:
                result_items.append(ft.Divider(height=8, color="transparent"))
            result_items.append(
                ft.Container(
                    content=ft.Text(
                        translator.get_text("menu.worksheets") if hasattr(translator, 'get_text') else "Munkalapok",
                        size=12,
                        weight=ft.FontWeight.BOLD,
                        color=DesignSystem.TEXT_SECONDARY,
                    ),
                    padding=ft.padding.only(bottom=4),
                )
            )
            for item in results["worksheets"]:
                result_items.append(_create_result_item(page, item, "worksheets"))
            print(f"[SEARCH DEBUG] Added {len(results.get('worksheets', []))} worksheet items")
        
        # Users
        if results.get("users"):
            print(f"[SEARCH DEBUG] Processing {len(results.get('users', []))} users")
            if result_items:
                result_items.append(ft.Divider(height=8, color="transparent"))
            result_items.append(
                ft.Container(
                    content=ft.Text(
                        translator.get_text("menu.users") if hasattr(translator, 'get_text') else "Felhasználók",
                        size=12,
                        weight=ft.FontWeight.BOLD,
                        color=DesignSystem.TEXT_SECONDARY,
                    ),
                    padding=ft.padding.only(bottom=4),
                )
            )
            for item in results["users"]:
                result_items.append(_create_result_item(page, item, "users"))
            print(f"[SEARCH DEBUG] Added {len(results.get('users', []))} user items")
        
        # Storage locations
        if results.get("storage_locations"):
            print(f"[SEARCH DEBUG] Processing {len(results.get('storage_locations', []))} storage locations")
            if result_items:
                result_items.append(ft.Divider(height=8, color="transparent"))
            result_items.append(
                ft.Container(
                    content=ft.Text(
                        translator.get_text("menu.storage") if hasattr(translator, 'get_text') else "Raktározás",
                        size=12,
                        weight=ft.FontWeight.BOLD,
                        color=DesignSystem.TEXT_SECONDARY,
                    ),
                    padding=ft.padding.only(bottom=4),
                )
            )
            for item in results["storage_locations"]:
                result_items.append(_create_result_item(page, item, "storage"))
            print(f"[SEARCH DEBUG] Added {len(results.get('storage_locations', []))} storage location items")
        
        if not result_items:
            print(f"[SEARCH DEBUG] No result items, adding 'no results' message")
            result_items.append(
                ft.Container(
                    content=ft.Text(
                        translator.get_text("common.no_results") if hasattr(translator, 'get_text') else "Nincs találat",
                        size=12,
                        color=DesignSystem.TEXT_SECONDARY,
                        italic=True,
                    ),
                    padding=8,
                )
            )
        
        print(f"[SEARCH DEBUG] Built {len(result_items)} result items total")
    except Exception as e:
        print(f"[SEARCH DEBUG] ERROR building result_items: {e}")
        import traceback
        traceback.print_exc()
        logger.error(f"Error building result items: {e}", exc_info=True)
        result_items = []
    
    # Update results container content - remove and re-add to parent to force Flet update
    try:
        print(f"[SEARCH DEBUG] Updating results container with {len(result_items)} items")
        logger.debug(f"Updating results container with {len(result_items)} items")
        
        # Get parent column from stored reference
        parent_column = None
        if hasattr(page, '_global_search') and 'parent_column' in page._global_search:
            parent_column = page._global_search['parent_column']
            print(f"[SEARCH DEBUG] Found parent column: {type(parent_column).__name__}")
        
        should_be_visible = len(result_items) > 0
        
        # If we have parent column, remove and re-add results_container to force update
        if parent_column and isinstance(parent_column, ft.Column):
            print(f"[SEARCH DEBUG] Removing results_container from parent column")
            if results_container in parent_column.controls:
                parent_column.controls.remove(results_container)
                page.update()  # Update after removal
        
        # Create a completely new Column with fresh controls
        new_column = ft.Column(
            controls=result_items,
            spacing=4,
            scroll=ft.ScrollMode.AUTO,
            height=400,
        )
        
        print(f"[SEARCH DEBUG] Created new Column with {len(result_items)} items")
        
        # Set the new Column as the content
        results_container.content = new_column
        results_container.visible = should_be_visible
        print(f"[SEARCH DEBUG] Results container visible set to: {results_container.visible}")
        logger.debug(f"Results container visible set to: {results_container.visible}")
        
        # Re-add to parent if we removed it
        if parent_column and isinstance(parent_column, ft.Column):
            print(f"[SEARCH DEBUG] Re-adding results_container to parent column")
            if results_container not in parent_column.controls:
                parent_column.controls.append(results_container)
        
        # Update the page - this will refresh the entire UI including the results container
        print(f"[SEARCH DEBUG] Calling page.update()")
        page.update()
        print(f"[SEARCH DEBUG] page.update() completed successfully")
        logger.debug("Page updated successfully")
    except Exception as e:
        print(f"[SEARCH DEBUG] ERROR updating results container: {e}")
        import traceback
        traceback.print_exc()
        logger.error(f"Error updating results container: {e}", exc_info=True)


def _create_result_item(page: ft.Page, item: dict, route: str) -> ft.Container:
    """Create a clickable result item"""
    def on_click(e):
        _navigate_to_result(page, item, route)
        _hide_results(page)
    
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(
                    item.get("display", item.get("name", "")),
                    size=13,
                    weight=ft.FontWeight.W_500,
                    color=DesignSystem.TEXT_PRIMARY,
                ),
                ft.Text(
                    item.get("subtitle", ""),
                    size=11,
                    color=DesignSystem.TEXT_SECONDARY,
                    visible=bool(item.get("subtitle")),
                ) if item.get("subtitle") else ft.Container(height=0),
            ],
            spacing=2,
            tight=True,
        ),
        padding=ft.padding.symmetric(horizontal=12, vertical=8),
        bgcolor=DesignSystem.BG_PRIMARY,
        border_radius=4,
        on_click=on_click,
        on_hover=lambda e: setattr(e.control, 'bgcolor', DesignSystem.BG_SECONDARY if e.data == "true" else DesignSystem.BG_PRIMARY) or page.update(),
    )


def _navigate_to_result(page: ft.Page, item: dict, route: str):
    """Navigate to the result item and open its details/edit dialog"""
    try:
        from ui.app import state
        
        # Store selection info for the target page to handle
        if not hasattr(page, '_search_selection'):
            page._search_selection = {}
        page._search_selection = {
            'route': route,
            'item_id': item.get("id"),
            'item_type': item.get("type"),
            'action': 'open',  # Action to take: 'open' means open edit/details dialog
        }
        
        # Set the view
        state.view = route
        
        # Navigate to the page
        page.go(f"/{route}")
        
        # Update page - this will trigger a re-render
        page.update()
        
        # After navigation, trigger the action (open dialog)
        # Use a small delay to ensure the page has rendered
        import threading
        def delayed_action():
            import time
            time.sleep(0.3)  # Wait for page to render
            try:
                if hasattr(page, '_search_selection') and page._search_selection:
                    _handle_search_selection(page, page._search_selection)
                    # Clear after use
                    page._search_selection = {}
            except Exception as e:
                logger.warning(f"Error handling search selection: {e}")
        
        threading.Thread(target=delayed_action, daemon=True).start()
        
    except Exception as e:
        logger.error(f"Error navigating to result: {e}", exc_info=True)


def _handle_search_selection(page: ft.Page, selection: dict):
    """Handle search selection by opening the appropriate dialog"""
    try:
        route = selection.get('route')
        item_id = selection.get('item_id')
        item_type = selection.get('item_type')
        
        if not item_id:
            return
        
        # Import services
        from services import asset_service, inventory_service, worksheet_service
        
        if route == "assets" and item_type == "machine":
            # Open machine edit dialog
            try:
                machine = asset_service.get_machine(item_id)
                if machine:
                    # Trigger the edit dialog by calling a function on the assets screen
                    # We'll use a page event to signal the screen
                    if not hasattr(page, '_open_machine_dialog_id'):
                        page._open_machine_dialog_id = None
                    page._open_machine_dialog_id = item_id
                    page.update()
            except Exception as e:
                logger.warning(f"Error opening machine dialog: {e}")
        
        elif route == "inventory" and item_type == "part":
            # Open part edit dialog
            try:
                part = inventory_service.get_part(item_id)
                if part:
                    if not hasattr(page, '_open_part_dialog_id'):
                        page._open_part_dialog_id = None
                    page._open_part_dialog_id = item_id
                    page.update()
            except Exception as e:
                logger.warning(f"Error opening part dialog: {e}")
        
        elif route == "worksheets" and item_type == "worksheet":
            # Navigate to worksheet detail
            try:
                page.go(f"/worksheets/detail/{item_id}")
                page.update()
            except Exception as e:
                logger.warning(f"Error navigating to worksheet: {e}")
        
        elif route == "users" and item_type == "user":
            # For users, just navigate (user management screen will handle it)
            pass
        
        elif route == "storage" and item_type == "storage_location":
            # For storage, navigate and select the location
            if not hasattr(page, '_select_storage_location_id'):
                page._select_storage_location_id = None
            page._select_storage_location_id = item_id
            page.update()
        
    except Exception as e:
        logger.error(f"Error handling search selection: {e}", exc_info=True)


def _hide_results(page: ft.Page):
    """Hide search results"""
    if hasattr(page, '_global_search'):
        results_container = page._global_search['results']
        results_container.visible = False
        page.update()

