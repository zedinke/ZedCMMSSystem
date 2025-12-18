"""
Készlet képernyő (váz)
"""

import flet as ft
from services import inventory_service, asset_service
from localization.translator import translator
from utils.currency import format_price
from ui.components.modern_components import (
    create_modern_button,
    create_modern_text_field,
    create_modern_dropdown,
    create_modern_dialog,
    create_vibrant_badge,
    create_modern_icon_button,
    create_empty_state_card,
    DesignSystem,
)
from ui.components.modern_card import (
    create_tailwind_card,
)


class InventoryScreen:
    def __init__(self, page: ft.Page):
        self.page = page
    
    def view(self, page: ft.Page):
        # Use stored page reference for dialogs
        if not hasattr(self, 'page') or self.page is None:
            self.page = page
        
        # Pagination settings
        ITEMS_PER_PAGE = 50  # Show 50 items per page for better performance
        current_page_ref = {"value": 0}  # Use dict to allow modification in nested functions
        
        # Parts list container
        parts_list = ft.Column([], spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)
        
        # Group by selection (default: "all" - no grouping)
        group_by_ref = {"value": "all"}  # "all", "production_line", "machine"
        
        # Pagination controls (will be updated dynamically)
        page_info_text = ft.Text(
            "",
            size=12,
            color=DesignSystem.TEXT_SECONDARY,
        )
        
        def create_part_card(part, inv_level=None):
            """Helper function to create a part card"""
            # Get inventory level
            if inv_level:
                stock_qty = inv_level.quantity_on_hand
                bin_loc = inv_level.bin_location or "-"
            else:
                stock_qty = 0
                bin_loc = "-"
            
            # Compatible machines
            compatible_machines = part.compatible_machines if hasattr(part, 'compatible_machines') else []
            machines_text = ", ".join([m.name for m in compatible_machines[:3]])
            if len(compatible_machines) > 3:
                machines_text += f" +{len(compatible_machines) - 3} további"
            
            # Create Tailwind CSS card for each part
            stock_badge_variant = "emerald" if stock_qty > 0 else None
            
            card_content = ft.Column([
                ft.Row([
                    ft.Column([
                        ft.Row([
                            ft.Text(
                                part.name,
                                size=18,
                                weight=ft.FontWeight.W_600,
                                color=DesignSystem.TEXT_PRIMARY,
                            ),
                            create_vibrant_badge(
                                text=part.sku,
                                variant="blue",
                                size=11,
                            ) if part.sku else None,
                        ], spacing=DesignSystem.SPACING_2),
                        ft.Container(height=DesignSystem.SPACING_2),
                        ft.Row([
                            ft.Text(
                                f"{translator.get_text('inventory.category')}: {part.category or '-'}",
                                size=13,
                                color=DesignSystem.TEXT_SECONDARY,
                            ),
                            ft.Container(width=DesignSystem.SPACING_4),
                            create_vibrant_badge(
                                text=f"{stock_qty} {part.unit}",
                                variant=stock_badge_variant or "blue",
                                size=11,
                            ) if stock_qty > 0 else ft.Text(
                                f"{translator.get_text('inventory.on_hand')}: {stock_qty} {part.unit}",
                                size=13,
                                color=DesignSystem.TEXT_SECONDARY,
                            ),
                        ], spacing=DesignSystem.SPACING_2),
                        ft.Container(height=DesignSystem.SPACING_1),
                        ft.Row([
                            ft.Text(
                                f"{translator.get_text('inventory.location_bin')}: {bin_loc}",
                                size=13,
                                color=DesignSystem.TEXT_SECONDARY,
                            ),
                            ft.Container(width=DesignSystem.SPACING_4),
                            ft.Text(
                                f"{translator.get_text('inventory.buy_price_net')}: {format_price(part.buy_price)}",
                                size=13,
                                weight=ft.FontWeight.W_500,
                                color=DesignSystem.TEXT_PRIMARY,
                            ),
                        ], spacing=DesignSystem.SPACING_2),
                        ft.Container(height=DesignSystem.SPACING_1),
                        ft.Text(
                            f"{translator.get_text('inventory.compatible_machines')}: {machines_text or '-'}",
                            size=12,
                            color=DesignSystem.TEXT_TERTIARY,
                            italic=True,
                        ) if machines_text else None,
                    ], expand=True, spacing=0),
                    ft.Row([
                        create_modern_icon_button(
                            icon=ft.Icons.ADD,
                            tooltip=translator.get_text("inventory.receive_stock"),
                            on_click=lambda e, p=part: open_receive_stock_dialog(p),
                            color=DesignSystem.EMERALD_500,
                            vibrant=True,
                            variant="emerald",
                        ),
                        create_modern_icon_button(
                            icon=ft.Icons.EDIT,
                            tooltip=translator.get_text("common.buttons.edit"),
                            on_click=lambda e, p=part: open_edit_part_dialog(p),
                            color=DesignSystem.BLUE_500,
                            vibrant=True,
                            variant="blue",
                        ),
                        create_modern_icon_button(
                            icon=ft.Icons.DELETE,
                            tooltip=translator.get_text("common.buttons.delete"),
                            on_click=lambda e, p=part: open_delete_part_dialog(p),
                            color=DesignSystem.RED_500,
                            vibrant=True,
                            variant="red",
                        ),
                    ], spacing=DesignSystem.SPACING_2),
                ], spacing=DesignSystem.SPACING_3),
            ], spacing=0)
            
            # Filter None values
            card_content.controls = [c for c in card_content.controls if c is not None]
            if hasattr(card_content.controls[0], 'controls'):
                card_content.controls[0].controls = [c for c in card_content.controls[0].controls if c is not None]
            
            card = create_tailwind_card(
                content=card_content,
                padding=DesignSystem.SPACING_4,
                elevation=1,
                accent_color=DesignSystem.BLUE_500,
            )
            return card
        
        def refresh_parts_list(update_page=True, page_num=None):
            if page_num is None:
                page_num = current_page_ref["value"]
            else:
                current_page_ref["value"] = page_num
            # Don't update if dialog is open
            page_ref = self.page if hasattr(self, 'page') and self.page else page
            if hasattr(page_ref, 'dialog') and page_ref.dialog is not None:
                dialog_open = getattr(page_ref.dialog, 'open', False)
                if dialog_open:
                    print("[INVENTORY] Skipping refresh_parts_list update because dialog is open")
                    return
            
            # Check if we need to open a part dialog from search
            if hasattr(page_ref, '_open_part_dialog_id') and page_ref._open_part_dialog_id:
                part_id = page_ref._open_part_dialog_id
                page_ref._open_part_dialog_id = None  # Clear flag
                try:
                    part = inventory_service.get_part(part_id)
                    if part:
                        # Open edit dialog after a small delay to ensure list is rendered
                        import threading
                        def open_dialog():
                            import time
                            time.sleep(0.2)
                            try:
                                open_edit_part_dialog(part)
                            except Exception as e:
                                print(f"[INVENTORY] Error opening part dialog from search: {e}")
                        threading.Thread(target=open_dialog, daemon=True).start()
                except Exception as e:
                    print(f"[INVENTORY] Error loading part for search: {e}")
            
            # Clear parts list
            parts_list.controls.clear()
            
            group_by_mode = group_by_ref["value"]
            
            # Handle grouping by production line or machine
            if group_by_mode == "production_line" or group_by_mode == "machine":
                # Load all parts (no pagination when grouping)
                from database.session_manager import SessionLocal
                from database.models import ProductionLine, Machine
                from sqlalchemy.orm import joinedload
                
                session = SessionLocal()
                try:
                    # Load all parts with compatible machines and their production lines
                    from database.models import Part
                    parts = session.query(Part).options(
                        joinedload(Part.compatible_machines).joinedload(Machine.production_line),
                        joinedload(Part.inventory_level)
                    ).all()
                    
                    # Batch load inventory levels
                    part_ids = [p.id for p in parts]
                    inv_levels_dict = inventory_service.get_inventory_levels_batch(part_ids)
                    
                    if group_by_mode == "production_line":
                        # Group by production line
                        prod_line_parts = {}  # {production_line_id: {machine_id: {part_id: part}}}
                        no_prod_line_parts = set()  # Parts with no production line association
                        
                        for part in parts:
                            compatible_machines = part.compatible_machines if hasattr(part, 'compatible_machines') else []
                            if not compatible_machines:
                                no_prod_line_parts.add(part.id)
                            else:
                                # Use set to track which machines this part is already added to per production line
                                for machine in compatible_machines:
                                    prod_line = machine.production_line if hasattr(machine, 'production_line') and machine.production_line else None
                                    prod_line_id = prod_line.id if prod_line else None
                                    
                                    if prod_line_id not in prod_line_parts:
                                        prod_line_parts[prod_line_id] = {}
                                    if machine.id not in prod_line_parts[prod_line_id]:
                                        prod_line_parts[prod_line_id][machine.id] = {}
                                    # Only add part once per machine (even if it appears multiple times)
                                    prod_line_parts[prod_line_id][machine.id][part.id] = part
                        
                        # Create accordion structure: Production Line -> Machine -> Parts
                        # Need to get machine info - load machines
                        from database.models import Machine
                        machines_info = {}
                        for prod_line_id in prod_line_parts.keys():
                            for machine_id in prod_line_parts[prod_line_id].keys():
                                if machine_id not in machines_info:
                                    machine_obj = session.query(Machine).filter_by(id=machine_id).first()
                                    if machine_obj:
                                        machines_info[machine_id] = machine_obj
                        
                        for prod_line_id in sorted(prod_line_parts.keys(), key=lambda x: (x is None, x)):
                            machines_dict = prod_line_parts[prod_line_id]
                            prod_line_name = None
                            if prod_line_id:
                                # Get production line name from first machine
                                for machine_id in machines_dict:
                                    machine = machines_info.get(machine_id)
                                    if machine and hasattr(machine, 'production_line') and machine.production_line:
                                        prod_line_name = machine.production_line.name
                                        break
                            
                            if not prod_line_name:
                                prod_line_name = translator.get_text("inventory.no_production_line") if translator.get_text("inventory.no_production_line") != "inventory.no_production_line" else "Nincs termelési sor"
                            
                            # Production line header
                            machine_items = []
                            
                            for machine_id in sorted(machines_dict.keys()):
                                parts_dict_for_machine = machines_dict[machine_id]
                                machine = machines_info.get(machine_id)
                                machine_name = machine.name if machine else f"Gép ID: {machine_id}"
                                
                                # Machine parts
                                machine_parts_cards = []
                                for part_id, part in parts_dict_for_machine.items():
                                    inv_level = inv_levels_dict.get(part.id)
                                    card = create_part_card(part, inv_level)
                                    machine_parts_cards.append(card)
                                
                                # Machine section (collapsible)
                                machine_section = ft.ExpansionTile(
                                    title=ft.Text(f"{machine_name} ({len(machine_parts_cards)} {translator.get_text('inventory.parts') if translator.get_text('inventory.parts') != 'inventory.parts' else 'alkatrész'})", 
                                                 size=14, weight=ft.FontWeight.W_600),
                                    subtitle=ft.Text(f"{len(machine_parts_cards)} {translator.get_text('inventory.parts') if translator.get_text('inventory.parts') != 'inventory.parts' else 'alkatrész'}", 
                                                     size=12, color=DesignSystem.TEXT_SECONDARY),
                                    leading=ft.Icon(ft.Icons.PRECISION_MANUFACTURING if hasattr(ft.Icons, 'PRECISION_MANUFACTURING') else ft.Icons.FACTORY, 
                                                   size=20, color=DesignSystem.BLUE_500),
                                    controls=[ft.Container(
                                        content=ft.Column(machine_parts_cards, spacing=8),
                                        padding=ft.padding.only(left=20, top=8, bottom=8),
                                    )],
                                    initially_expanded=True,
                                )
                                machine_items.append(machine_section)
                            
                            # Production line section
                            if machine_items:
                                prod_line_section = ft.ExpansionTile(
                                    title=ft.Text(prod_line_name, size=16, weight=ft.FontWeight.BOLD),
                                    subtitle=ft.Text(f"{sum(len(machines_dict[m_id]) for m_id in machines_dict)} {translator.get_text('inventory.parts') if translator.get_text('inventory.parts') != 'inventory.parts' else 'alkatrész'}", 
                                                     size=13, color=DesignSystem.TEXT_SECONDARY),
                                    leading=ft.Icon(ft.Icons.SETTINGS_APPLICATIONS if hasattr(ft.Icons, 'SETTINGS_APPLICATIONS') else ft.Icons.TUNE, 
                                                   size=24, color=DesignSystem.PURPLE_500),
                                    controls=[ft.Container(
                                        content=ft.Column(machine_items, spacing=4),
                                        padding=ft.padding.only(left=20, top=8, bottom=8),
                                    )],
                                    initially_expanded=True,
                                )
                                parts_list.controls.append(prod_line_section)
                            
                        # Parts with no production line association
                        if no_prod_line_parts:
                            no_prod_line_cards = []
                            for part in parts:
                                if part.id in no_prod_line_parts:
                                    inv_level = inv_levels_dict.get(part.id)
                                    card = create_part_card(part, inv_level)
                                    no_prod_line_cards.append(card)
                            
                            no_prod_line_section = ft.ExpansionTile(
                                title=ft.Text(translator.get_text("inventory.no_production_line") if translator.get_text("inventory.no_production_line") != "inventory.no_production_line" else "Nincs termelési sor", 
                                             size=16, weight=ft.FontWeight.BOLD),
                                subtitle=ft.Text(f"{len(no_prod_line_cards)} {translator.get_text('inventory.parts') if translator.get_text('inventory.parts') != 'inventory.parts' else 'alkatrész'}", 
                                                 size=13, color=DesignSystem.TEXT_SECONDARY),
                                leading=ft.Icon(ft.Icons.INVENTORY_2, size=24, color=DesignSystem.GRAY_500),
                                controls=[ft.Container(
                                    content=ft.Column(no_prod_line_cards, spacing=8),
                                    padding=ft.padding.only(left=20, top=8, bottom=8),
                                )],
                                initially_expanded=True,
                            )
                            parts_list.controls.append(no_prod_line_section)
                    
                    elif group_by_mode == "machine":
                        # Group by machine (no production line grouping)
                        machine_parts_dict = {}  # {machine_id: {part_id: part}}
                        no_machine_parts = set()  # Parts with no machine association
                        
                        # Load machine info
                        from database.models import Machine
                        machines_info = {}
                        
                        for part in parts:
                            compatible_machines = part.compatible_machines if hasattr(part, 'compatible_machines') else []
                            if not compatible_machines:
                                no_machine_parts.add(part.id)
                            else:
                                for machine in compatible_machines:
                                    if machine.id not in machine_parts_dict:
                                        machine_parts_dict[machine.id] = {}
                                    # Only add part once per machine
                                    machine_parts_dict[machine.id][part.id] = part
                                    if machine.id not in machines_info:
                                        machines_info[machine.id] = machine
                        
                        # Create accordion structure: Machine -> Parts
                        for machine_id in sorted(machine_parts_dict.keys()):
                            parts_dict_for_machine = machine_parts_dict[machine_id]
                            machine = machines_info.get(machine_id)
                            machine_name = machine.name if machine else f"Gép ID: {machine_id}"
                            
                            machine_parts_cards = []
                            for part_id, part in parts_dict_for_machine.items():
                                inv_level = inv_levels_dict.get(part.id)
                                card = create_part_card(part, inv_level)
                                machine_parts_cards.append(card)
                            
                            machine_section = ft.ExpansionTile(
                                title=ft.Text(machine_name, size=16, weight=ft.FontWeight.W_600),
                                subtitle=ft.Text(f"{len(machine_parts_cards)} {translator.get_text('inventory.parts') if translator.get_text('inventory.parts') != 'inventory.parts' else 'alkatrész'}", 
                                                 size=13, color=DesignSystem.TEXT_SECONDARY),
                                leading=ft.Icon(ft.Icons.PRECISION_MANUFACTURING if hasattr(ft.Icons, 'PRECISION_MANUFACTURING') else ft.Icons.FACTORY, 
                                               size=24, color=DesignSystem.BLUE_500),
                                controls=[ft.Container(
                                    content=ft.Column(machine_parts_cards, spacing=8),
                                    padding=ft.padding.only(left=20, top=8, bottom=8),
                                )],
                                initially_expanded=True,
                            )
                            parts_list.controls.append(machine_section)
                        
                        # Parts with no machine association
                        if no_machine_parts:
                            no_machine_cards = []
                            for part in parts:
                                if part.id in no_machine_parts:
                                    inv_level = inv_levels_dict.get(part.id)
                                    card = create_part_card(part, inv_level)
                                    no_machine_cards.append(card)
                            
                            no_machine_section = ft.ExpansionTile(
                                title=ft.Text(translator.get_text("inventory.no_machine") if translator.get_text("inventory.no_machine") != "inventory.no_machine" else "Nincs gép", 
                                             size=16, weight=ft.FontWeight.BOLD),
                                subtitle=ft.Text(f"{len(no_machine_cards)} {translator.get_text('inventory.parts') if translator.get_text('inventory.parts') != 'inventory.parts' else 'alkatrész'}", 
                                                 size=13, color=DesignSystem.TEXT_SECONDARY),
                                leading=ft.Icon(ft.Icons.INVENTORY_2, size=24, color=DesignSystem.GRAY_500),
                                controls=[ft.Container(
                                    content=ft.Column(no_machine_cards, spacing=8),
                                    padding=ft.padding.only(left=20, top=8, bottom=8),
                                )],
                                initially_expanded=True,
                            )
                            parts_list.controls.append(no_machine_section)
                    
                    if not parts_list.controls:
                        parts_list.controls.append(
                            create_empty_state_card(
                                icon=ft.Icons.INVENTORY_2,
                                title=translator.get_text("empty_states.no_inventory"),
                                icon_color=DesignSystem.GRAY_400,
                            )
                        )
                    
                    # Update page info (no pagination when grouping)
                    total_parts_count = len(parts)
                    page_info_text.value = f"Összesen / Total: {total_parts_count}"
                    
                finally:
                    session.close()
            
            else:
                # Original behavior: no grouping, with pagination
                offset = page_num * ITEMS_PER_PAGE
                parts = inventory_service.list_parts(limit=ITEMS_PER_PAGE, offset=offset)
                
                # Update page info
                total_parts_count = inventory_service.count_parts()
                total_pages = (total_parts_count + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE if total_parts_count > 0 else 1
                if total_pages > 1:
                    page_info_text.value = f"Oldal / Page: {page_num + 1} / {total_pages} | Összesen / Total: {total_parts_count}"
                else:
                    page_info_text.value = f"Összesen / Total: {total_parts_count}"
                
                if not parts:
                    parts_list.controls.append(
                        create_empty_state_card(
                            icon=ft.Icons.INVENTORY_2,
                            title=translator.get_text("empty_states.no_inventory"),
                            icon_color=DesignSystem.GRAY_400,
                        )
                    )
                else:
                    # Batch load all inventory levels in one query (optimized)
                    part_ids = [p.id for p in parts]
                    inv_levels_dict = inventory_service.get_inventory_levels_batch(part_ids)
                    
                    for part in parts:
                        inv_level = inv_levels_dict.get(part.id)
                        card = create_part_card(part, inv_level)
                        parts_list.controls.append(card)
            
            if update_page:
                page.update()

        def open_add_part_dialog(e):
            print(f"[INVENTORY] open_add_part_dialog called, event: {e}")
            # Use stored page reference instead of parameter
            dialog_page = self.page if hasattr(self, 'page') and self.page else page
            print(f"[INVENTORY] page object: {dialog_page}, page type: {type(dialog_page)}")
            try:
                name_field = ft.TextField(label=translator.get_text("inventory.part_name"), autofocus=True)
                sku_field = ft.TextField(label=f"{translator.get_text('inventory.sku')}")
                category_field = ft.TextField(label=translator.get_text("inventory.category"), hint_text="opcionális")
                initial_quantity_field = ft.TextField(
                    label=translator.get_text("inventory.initial_quantity") if translator.get_text("inventory.initial_quantity") != "inventory.initial_quantity" else "Kezdeti mennyiség",
                    keyboard_type=ft.KeyboardType.NUMBER,
                    hint_text="pl. 10",
                    value="0",
                )
                safety_field = ft.TextField(
                    label=translator.get_text("inventory.safety_stock"),
                    keyboard_type=ft.KeyboardType.NUMBER,
                    hint_text="pl. 2",
                )
                unit_field = ft.TextField(
                    label=translator.get_text("inventory.unit"),
                    hint_text="pl. db / m / l / kg",
                )
                price_field = ft.TextField(
                    label=translator.get_text("inventory.buy_price_net"),
                    keyboard_type=ft.KeyboardType.NUMBER,
                    hint_text="pl. 1200",
                )
                supplier_field = ft.TextField(
                    label=translator.get_text("inventory.supplier_contact"),
                    hint_text="pl. Technik-Pro Kft. vagy telefonszám",
                )
                # Load machines for compatibility selection
                machines = asset_service.list_machines()
                machine_checkboxes = []
                for m in machines:
                    machine_checkboxes.append(
                        ft.Checkbox(label=f"{m.name} ({m.serial_number or '-'})", value=False, data=m.id)
                    )
                
                compatible_machines_column = ft.Column(
                    controls=machine_checkboxes,
                    scroll=ft.ScrollMode.AUTO,
                    height=150, # Limit height
                )

                compatible_section = ft.Column([
                    ft.Text(translator.get_text("inventory.compatible_machines"), size=12, color="#4B5563"),
                    ft.Container(
                        content=compatible_machines_column,
                        border=ft.border.all(1, "#9CA3AF"),
                        border_radius=5,
                        padding=5,
                    )
                ])
                
                # Storage location picker
                from ui.components.storage_location_picker import StorageLocationPicker
                storage_picker = StorageLocationPicker(page=dialog_page)
                storage_section = storage_picker.build(
                    label=translator.get_text("storage.assign_to_location") if translator.get_text("storage.assign_to_location") != "storage.assign_to_location" else "Tárhely hozzárendelése",
                    width=None,
                    part_id=None,  # None, mert új part
                )

                def submit(e):
                    print(f"[INVENTORY] Submit button clicked, event: {e}")
                    try:
                        if not name_field.value or not sku_field.value:
                            raise ValueError(translator.get_text("common.messages.required_field"))

                        def to_int(val: str, default: int = 0) -> int:
                            if val is None or val == "":
                                return default
                            return int(float(val))

                        def to_float(val: str, default: float = 0.0) -> float:
                            if val is None or val == "":
                                return default
                            return float(val)

                        initial_quantity_value = to_int(initial_quantity_field.value, 0)
                        safety_value = to_int(safety_field.value, 0)
                        buy_price_value = to_float(price_field.value, 0.0)

                        # Collect selected machine IDs
                        selected_machine_ids = [cb.data for cb in machine_checkboxes if cb.value]

                        description_parts = []
                        if supplier_field.value:
                            description_parts.append(f"Beszállító: {supplier_field.value}")

                        print(f"[INVENTORY] Creating part: sku={sku_field.value}, name={name_field.value}, initial_quantity={initial_quantity_value}")
                        new_part = inventory_service.create_part(
                            sku=sku_field.value,
                            name=name_field.value,
                            category=category_field.value or None,
                            supplier_id=None,
                            buy_price=buy_price_value,
                            sell_price=0.0,
                            safety_stock=safety_value,
                            reorder_quantity=0,
                            description="\n".join(description_parts) or None,
                            bin_location=None,  # No storage location assigned during part creation
                            unit=unit_field.value or "db",
                            compatible_machine_ids=selected_machine_ids,
                            initial_quantity=initial_quantity_value
                        )
                        print("[INVENTORY] Part created successfully")
                        
                        # Assign to storage location if selected
                        if storage_picker:
                            location_id, other_location = storage_picker.get_value()
                            if location_id and initial_quantity_value > 0:
                                try:
                                    from services.storage_service import assign_part_to_location
                                    assign_part_to_location(
                                        part_id=new_part.id,
                                        storage_location_id=location_id,
                                        quantity=initial_quantity_value,
                                        notes=None,
                                    )
                                    print(f"[INVENTORY] Part assigned to storage location {location_id}")
                                except Exception as storage_ex:
                                    print(f"[INVENTORY] Error assigning part to storage location: {storage_ex}")
                                    # Don't fail the whole operation, just log the error
                                    dialog_page.snack_bar = ft.SnackBar(
                                        content=ft.Text(f"{translator.get_text('inventory.part_added')}, de a tárhely hozzárendelése nem sikerült: {storage_ex}"),
                                        bgcolor=DesignSystem.WARNING
                                    )
                                    dialog_page.snack_bar.open = True
                        
                        # Close dialog - try both methods
                        try:
                            dialog_page.close(dialog)
                            print("[INVENTORY] Dialog closed using page.close()")
                        except (AttributeError, Exception):
                            dialog.open = False
                            dialog_page.update()
                            print("[INVENTORY] Dialog closed using dialog.open = False")
                        
                        dialog_page.snack_bar = ft.SnackBar(
                            content=ft.Text(translator.get_text("inventory.part_added")),
                            bgcolor="#10B981",
                        )
                        dialog_page.snack_bar.open = True
                        refresh_parts_list(update_page=True)
                        print("[INVENTORY] Snackbar shown and parts list refreshed")
                    except Exception as exc:
                        print(f"[INVENTORY] Error in submit: {exc}")
                        import traceback
                        traceback.print_exc()
                        dialog_page.snack_bar = ft.SnackBar(
                            content=ft.Text(f"{translator.get_text('inventory.part_add_error')}: {exc}"),
                            bgcolor="#EF4444",
                        )
                        dialog_page.snack_bar.open = True
                    dialog_page.update()

                # Modern, szép design a formhoz
                dialog = ft.AlertDialog(
                    modal=True,
                    title=ft.Row([
                        ft.Icon(ft.Icons.INVENTORY_2, color="#6366F1", size=24),
                        ft.Text(
                            translator.get_text("inventory.add_part_dialog_title"),
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color="#1F2937",
                        ),
                    ], spacing=10),
                    content=ft.Container(
                        content=ft.Column([
                            # Kötelező mezők csoportja
                            ft.Container(
                                content=ft.Column([
                                    ft.Text(
                                        translator.get_text("inventory.required_fields"),
                                        size=12,
                                        weight=ft.FontWeight.BOLD,
                                        color="#6B7280",
                                    ),
                                    name_field,
                                    sku_field,
                                ], spacing=8),
                                padding=ft.padding.only(bottom=10),
                            ),
                            ft.Divider(height=1, color="#E5E7EB"),
                            
                            # Alap információk
                            ft.Container(
                                content=ft.Column([
                                    ft.Text(
                                        translator.get_text("inventory.basic_info"),
                                        size=12,
                                        weight=ft.FontWeight.BOLD,
                                        color="#6B7280",
                                    ),
                                    ft.Row([
                                        ft.Container(content=category_field, expand=1),
                                        ft.Container(content=unit_field, expand=1, margin=ft.margin.only(left=10)),
                                    ]),
                                    ft.Row([
                                        ft.Container(content=initial_quantity_field, expand=1),
                                        ft.Container(content=safety_field, expand=1, margin=ft.margin.only(left=10)),
                                    ]),
                                    ft.Row([
                                        ft.Container(content=price_field, expand=1),
                                    ]),
                                ], spacing=8),
                                padding=ft.padding.only(top=10, bottom=10),
                            ),
                            ft.Divider(height=1, color="#E5E7EB"),
                            
                            # Tárhely hozzárendelés (ha van kezdeti mennyiség)
                            ft.Container(
                                content=ft.Column([
                                    ft.Text(
                                        translator.get_text("storage.assign_to_location") if translator.get_text("storage.assign_to_location") != "storage.assign_to_location" else "Tárhely hozzárendelése",
                                        size=12,
                                        weight=ft.FontWeight.BOLD,
                                        color="#6B7280",
                                    ),
                                    storage_section,
                                    ft.Text(
                                        translator.get_text("storage.assign_location_hint") if translator.get_text("storage.assign_location_hint") != "storage.assign_location_hint" else "Opcionális: ha megadsz kezdeti mennyiséget, hozzárendelhetsz tárhelyet is.",
                                        size=11,
                                        color="#9CA3AF",
                                        italic=True,
                                    ),
                                ], spacing=8),
                                padding=ft.padding.only(top=10, bottom=10),
                            ),
                            ft.Divider(height=1, color="#E5E7EB"),
                            
                            # Beszállító információ
                            ft.Container(
                                content=ft.Column([
                                    ft.Text(
                                        translator.get_text("inventory.supplier_contact"),
                                        size=12,
                                        weight=ft.FontWeight.BOLD,
                                        color="#6B7280",
                                    ),
                                    supplier_field,
                                ], spacing=8),
                                padding=ft.padding.only(top=10, bottom=10),
                            ),
                            ft.Divider(height=1, color="#E5E7EB"),
                            
                            # Kompatibilis gépek
                            compatible_section,
                        ], 
                        tight=False,
                        spacing=12,
                        scroll=ft.ScrollMode.AUTO,
                        ),
                        width=600,
                        height=500,
                        padding=15,
                    ),
                    actions=[
                        ft.TextButton(
                            translator.get_text("common.buttons.cancel"),
                            on_click=lambda _: close_dialog(),
                            style=ft.ButtonStyle(color="#6B7280"),
                        ),
                        ft.ElevatedButton(
                            translator.get_text("common.buttons.add"),
                            icon=ft.Icons.ADD,
                            on_click=submit,
                            style=ft.ButtonStyle(
                                bgcolor="#6366F1",
                                color="#FFFFFF",
                            ),
                        ),
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                )

                def close_dialog():
                    print("[INVENTORY] Close dialog called")
                    try:
                        dialog_page.close(dialog)
                        print("[INVENTORY] Dialog closed using page.close()")
                    except (AttributeError, Exception):
                        dialog.open = False
                        dialog_page.update()
                        print("[INVENTORY] Dialog closed using dialog.open = False")

                # Set dialog and show it using modern page.open() method
                print(f"[INVENTORY] Setting dialog on page: {dialog_page}")
                try:
                    # Modern Flet way: use page.open() instead of page.dialog + page.update()
                    dialog_page.open(dialog)
                    print(f"[INVENTORY] Dialog opened using page.open() - dialog.open={dialog.open}")
                except AttributeError:
                    # Fallback to old method if page.open() doesn't exist
                    print("[INVENTORY] page.open() not available, using fallback method")
                    dialog_page.dialog = dialog
                    dialog.open = True
                    dialog_page.update()
                    print(f"[INVENTORY] Dialog opened using fallback - dialog.open={dialog.open}, page.dialog exists={dialog_page.dialog is not None}")
                except Exception as open_error:
                    print(f"[INVENTORY] Error opening dialog: {open_error}")
                    import traceback
                    traceback.print_exc()
                    # Try fallback
                    try:
                        dialog_page.dialog = dialog
                        dialog.open = True
                        dialog_page.update()
                        print(f"[INVENTORY] Fallback successful - dialog.open={dialog.open}")
                    except Exception as fallback_error:
                        print(f"[INVENTORY] Fallback also failed: {fallback_error}")
                print(f"[INVENTORY] Final state - dialog.open={dialog.open}, page.dialog: {dialog_page.dialog}")
            except Exception as ex:
                print(f"Error opening inventory dialog: {ex}")
                dialog_page.snack_bar = ft.SnackBar(ft.Text(f"Hiba: {ex}"))
                dialog_page.snack_bar.open = True
                dialog_page.update()

        def open_edit_part_dialog(part):
            """Open edit dialog for part"""
            dialog_page = self.page if hasattr(self, 'page') and self.page else page
            
            # Pre-fill fields
            name_field = ft.TextField(label=translator.get_text("inventory.part_name"), value=part.name)
            sku_field = ft.TextField(label=translator.get_text("inventory.sku"), value=part.sku, disabled=True)
            category_field = ft.TextField(label=translator.get_text("inventory.category"), value=part.category or "")
            safety_field = ft.TextField(
                label=translator.get_text("inventory.safety_stock"),
                keyboard_type=ft.KeyboardType.NUMBER,
                value=str(part.safety_stock),
            )
            try:
                inv_level = inventory_service.get_inventory_level(part.id)
                location_field = ft.TextField(
                    label=translator.get_text("inventory.location_bin"),
                    value=inv_level.bin_location or "",
                )
            except:
                location_field = ft.TextField(label=translator.get_text("inventory.location_bin"), value="")
            
            unit_field = ft.TextField(label=translator.get_text("inventory.unit"), value=part.unit or "db")
            price_field = ft.TextField(
                label=translator.get_text("inventory.buy_price_net"),
                keyboard_type=ft.KeyboardType.NUMBER,
                value=str(part.buy_price),
            )
            
            # Load machines for compatibility selection
            machines = asset_service.list_machines()
            current_compatible_ids = [m.id for m in (part.compatible_machines if hasattr(part, 'compatible_machines') else [])]
            machine_checkboxes = []
            for m in machines:
                machine_checkboxes.append(
                    ft.Checkbox(label=f"{m.name} ({m.serial_number or '-'})", value=m.id in current_compatible_ids, data=m.id)
                )
            
            compatible_machines_column = ft.Column(controls=machine_checkboxes, scroll=ft.ScrollMode.AUTO, height=150)
            compatible_section = ft.Column([
                ft.Text(translator.get_text("inventory.compatible_machines"), size=12, color="#4B5563"),
                ft.Container(content=compatible_machines_column, border=ft.border.all(1, "#9CA3AF"), border_radius=5, padding=5)
            ])
            
            def submit_edit(e):
                try:
                    if not name_field.value:
                        raise ValueError(translator.get_text("common.messages.required_field"))
                    
                    def to_int(val: str, default: int = 0) -> int:
                        if val is None or val == "":
                            return default
                        return int(float(val))
                    
                    def to_float(val: str, default: float = 0.0) -> float:
                        if val is None or val == "":
                            return default
                        return float(val)
                    
                    selected_machine_ids = [cb.data for cb in machine_checkboxes if cb.value]
                    
                    # Show change reason dialog before updating
                    from ui.components.change_reason_dialog import show_change_reason_dialog
                    
                    def perform_update(change_reason: str):
                        try:
                            inventory_service.update_part(
                                part_id=part.id,
                                name=name_field.value,
                                category=category_field.value or None,
                                buy_price=to_float(price_field.value, 0.0),
                                safety_stock=to_int(safety_field.value, 0),
                                bin_location=location_field.value or None,
                                unit=unit_field.value or "db",
                                compatible_machine_ids=selected_machine_ids,
                                change_reason=change_reason,
                            )
                            
                            try:
                                dialog_page.close(dialog)
                            except:
                                dialog.open = False
                                dialog_page.update()
                            
                            dialog_page.snack_bar = ft.SnackBar(content=ft.Text("Alkatrész frissítve"), bgcolor="#10B981")
                            dialog_page.snack_bar.open = True
                            refresh_parts_list(update_page=True)
                        except Exception as exc:
                            dialog_page.snack_bar = ft.SnackBar(content=ft.Text(f"Hiba: {exc}"), bgcolor="#EF4444")
                            dialog_page.snack_bar.open = True
                            dialog_page.update()
                    
                    # Show change reason dialog
                    show_change_reason_dialog(
                        page=dialog_page,
                        entity_name=part.name,
                        entity_type=translator.get_text("inventory.part") if hasattr(translator, 'get_text') else "Alkatrész",
                        on_confirm=perform_update,
                    )
                except Exception as exc:
                    dialog_page.snack_bar = ft.SnackBar(content=ft.Text(f"Hiba: {exc}"), bgcolor="#EF4444")
                    dialog_page.snack_bar.open = True
                dialog_page.update()
            
            dialog = ft.AlertDialog(
                modal=True,
                title=ft.Row([ft.Icon(ft.Icons.EDIT, color="#6366F1", size=24), ft.Text("Alkatrész szerkesztése", size=20, weight=ft.FontWeight.BOLD)]),
                content=ft.Container(
                    content=ft.Column([
                        name_field, sku_field, category_field, safety_field,
                        location_field, unit_field, price_field, compatible_section,
                    ], tight=False, spacing=12, scroll=ft.ScrollMode.AUTO),
                    width=600, height=500, padding=15,
                ),
                actions=[
                    ft.TextButton("Mégse", on_click=lambda _: setattr(dialog, 'open', False) or dialog_page.update()),
                    ft.ElevatedButton("Mentés", icon=ft.Icons.SAVE, on_click=submit_edit, bgcolor="#6366F1", color="#FFFFFF"),
                ],
            )
            
            try:
                dialog_page.open(dialog)
            except:
                dialog_page.dialog = dialog
                dialog.open = True
                dialog_page.update()
        
        def open_delete_part_dialog(part):
            """Open delete confirmation dialog"""
            dialog_page = self.page if hasattr(self, 'page') and self.page else page
            
            def confirm_delete(e):
                try:
                    inventory_service.delete_part(part.id)
                    try:
                        dialog_page.close(dialog)
                    except:
                        dialog.open = False
                        dialog_page.update()
                    dialog_page.snack_bar = ft.SnackBar(content=ft.Text("Alkatrész törölve"), bgcolor="#10B981")
                    dialog_page.snack_bar.open = True
                    refresh_parts_list(update_page=True)
                except Exception as exc:
                    dialog_page.snack_bar = ft.SnackBar(content=ft.Text(f"Hiba: {exc}"), bgcolor="#EF4444")
                    dialog_page.snack_bar.open = True
                dialog_page.update()
            
            dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Alkatrész törlése"),
                content=ft.Text(f"Biztosan törölni szeretnéd az '{part.name}' ({part.sku}) alkatrészt?"),
                actions=[
                    ft.TextButton("Mégse", on_click=lambda _: setattr(dialog, 'open', False) or dialog_page.update()),
                    ft.ElevatedButton("Törlés", icon=ft.Icons.DELETE, on_click=confirm_delete, bgcolor="#EF4444", color="#FFFFFF"),
                ],
            )
            
            try:
                dialog_page.open(dialog)
            except:
                dialog_page.dialog = dialog
                dialog.open = True
                dialog_page.update()

        def open_receive_stock_dialog(part):
            dialog_page = self.page if hasattr(self, 'page') and self.page else page
            
            from datetime import datetime, date
            from services.context_service import get_current_user_id
            
            # Form fields
            quantity_field = ft.TextField(
                label=translator.get_text("inventory.quantity"),
                keyboard_type=ft.KeyboardType.NUMBER,
                autofocus=True,
                hint_text="pl. 10",
            )
            
            date_field = ft.TextField(
                label=translator.get_text("inventory.received_date"),
                hint_text="YYYY-MM-DD",
                value=date.today().strftime("%Y-%m-%d"),
            )
            
            unit_price_field = ft.TextField(
                label=translator.get_text("inventory.unit_price"),
                keyboard_type=ft.KeyboardType.NUMBER,
                hint_text="pl. 1200",
            )
            
            # Load suppliers for dropdown
            from database.session_manager import SessionLocal
            from database.models import Supplier
            session = SessionLocal()
            try:
                suppliers = session.query(Supplier).order_by(Supplier.name).all()
                supplier_options = [ft.dropdown.Option(key="", text=translator.get_text("common.none"))]
                for supplier in suppliers:
                    supplier_options.append(ft.dropdown.Option(key=str(supplier.id), text=supplier.name))
            finally:
                session.close()
            
            supplier_dropdown = ft.Dropdown(
                label=translator.get_text("inventory.supplier"),
                options=supplier_options,
                hint_text=translator.get_text("common.optional"),
            )
            
            invoice_number_field = ft.TextField(
                label=translator.get_text("inventory.invoice_number"),
                hint_text="pl. INV-2025-001",
            )
            
            notes_field = ft.TextField(
                label=translator.get_text("inventory.notes"),
                multiline=True,
                min_lines=2,
                max_lines=4,
                hint_text=translator.get_text("common.optional"),
            )
            
            # Create storage location picker (filtered to empty locations or locations with same SKU)
            from ui.components.storage_location_picker import StorageLocationPicker
            storage_picker = StorageLocationPicker(page=dialog_page)
            storage_location_picker = storage_picker.build(
                label=translator.get_text("storage.location"),
                width=None,
                part_id=part.id,  # Filter to empty locations or locations with same SKU
            )
            
            def submit_receive(e):
                try:
                    # Validate required fields
                    if not quantity_field.value:
                        raise ValueError(translator.get_text("common.messages.required_field") + ": " + translator.get_text("inventory.quantity"))
                    
                    quantity = int(float(quantity_field.value))
                    if quantity <= 0:
                        raise ValueError(translator.get_text("inventory.quantity") + " > 0")
                    
                    # Parse date
                    received_date = None
                    if date_field.value:
                        try:
                            received_date = datetime.strptime(date_field.value, "%Y-%m-%d")
                        except ValueError:
                            raise ValueError(translator.get_text("inventory.received_date") + " formátum: YYYY-MM-DD")
                    else:
                        received_date = datetime.now()
                    
                    # Parse optional fields
                    unit_price = 0.0
                    if unit_price_field.value:
                        try:
                            unit_price = float(unit_price_field.value)
                        except ValueError:
                            unit_price = 0.0
                    
                    supplier_id = None
                    if supplier_dropdown.value:
                        try:
                            supplier_id = int(supplier_dropdown.value)
                        except (ValueError, TypeError):
                            supplier_id = None
                    
                    invoice_number = invoice_number_field.value if invoice_number_field.value else None
                    notes = notes_field.value if notes_field.value else None
                    
                    user_id = get_current_user_id()
                    
                    # Get storage location
                    location_id, other_location = storage_picker.get_value()
                    storage_location_id = location_id if location_id else None
                    # Note: other_location is not stored in StockBatch, but could be stored in notes if needed
                    if other_location and not storage_location_id:
                        if notes:
                            notes = f"{notes}\nEgyéb hely: {other_location}"
                        else:
                            notes = f"Egyéb hely: {other_location}"
                    
                    # Call receive_stock
                    inventory_service.receive_stock(
                        part_id=part.id,
                        quantity=quantity,
                        unit_price=unit_price,
                        received_date=received_date,
                        supplier_id=supplier_id,
                        invoice_number=invoice_number,
                        notes=notes,
                        user_id=user_id,
                        storage_location_id=storage_location_id,
                    )
                    
                    # Close dialog
                    try:
                        dialog_page.close(dialog)
                    except (AttributeError, Exception):
                        dialog.open = False
                        dialog_page.update()
                    
                    # Show success message
                    dialog_page.snack_bar = ft.SnackBar(
                        content=ft.Text(translator.get_text("inventory.stock_received_success")),
                        bgcolor=DesignSystem.SUCCESS,
                    )
                    dialog_page.snack_bar.open = True
                    
                    # Refresh parts list
                    refresh_parts_list(update_page=True)
                except Exception as exc:
                    import traceback
                    traceback.print_exc()
                    dialog_page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"{translator.get_text('common.error')}: {exc}"),
                        bgcolor=DesignSystem.ERROR,
                    )
                    dialog_page.snack_bar.open = True
                dialog_page.update()
            
            dialog = ft.AlertDialog(
                modal=True,
                title=ft.Row([
                    ft.Icon(ft.Icons.INVENTORY_2, color=DesignSystem.EMERALD_500, size=24),
                    ft.Text(translator.get_text("inventory.receive_stock_dialog_title"), size=20, weight=ft.FontWeight.BOLD)
                ]),
                content=ft.Container(
                    content=ft.Column([
                        ft.Text(f"{translator.get_text('inventory.part_name')}: {part.name} ({part.sku})", size=14, weight=ft.FontWeight.W_500),
                        ft.Divider(height=1),
                        quantity_field,
                        date_field,
                        unit_price_field,
                        supplier_dropdown,
                        invoice_number_field,
                        storage_location_picker,
                        notes_field,
                    ], spacing=DesignSystem.SPACING_3, tight=True, scroll=ft.ScrollMode.AUTO),
                    width=500,
                    height=500,
                ),
                actions=[
                    ft.TextButton(
                        translator.get_text("common.buttons.cancel"),
                        on_click=lambda _: setattr(dialog, 'open', False) or dialog_page.update()
                    ),
                    ft.ElevatedButton(
                        translator.get_text("common.buttons.save"),
                        icon=ft.Icons.SAVE,
                        on_click=submit_receive,
                        bgcolor=DesignSystem.EMERALD_500,
                        color="#FFFFFF",
                    ),
                ],
            )
            
            try:
                dialog_page.open(dialog)
            except:
                dialog_page.dialog = dialog
                dialog.open = True
                dialog_page.update()

        # Initial load
        refresh_parts_list(update_page=False, page_num=0)
        
        # Get total count for pagination
        total_parts_count = inventory_service.count_parts()
        total_pages = (total_parts_count + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE if total_parts_count > 0 else 1
        
        # Pagination navigation functions
        def go_to_page(page_num):
            if 0 <= page_num < total_pages:
                current_page_ref["value"] = page_num
                refresh_parts_list(update_page=False, page_num=page_num)
                # Update pagination button states
                update_pagination_buttons()
                page.update()
        
        def next_page(e):
            current = current_page_ref["value"]
            total = (inventory_service.count_parts() + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE if inventory_service.count_parts() > 0 else 1
            if current < total - 1:
                go_to_page(current + 1)
        
        def prev_page(e):
            current = current_page_ref["value"]
            if current > 0:
                go_to_page(current - 1)
        
        def first_page(e):
            go_to_page(0)
        
        def last_page(e):
            total = (inventory_service.count_parts() + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE if inventory_service.count_parts() > 0 else 1
            go_to_page(total - 1)
        
        # Pagination buttons (will be updated)
        first_btn = create_modern_button(
            text="<<",
            tooltip="Első oldal / First page",
            on_click=first_page,
            disabled=True,
            width=50,
        )
        prev_btn = create_modern_button(
            text="<",
            tooltip="Előző oldal / Previous page",
            on_click=prev_page,
            disabled=True,
            width=50,
        )
        next_btn = create_modern_button(
            text=">",
            tooltip="Következő oldal / Next page",
            on_click=next_page,
            disabled=True,
            width=50,
        )
        last_btn = create_modern_button(
            text=">>",
            tooltip="Utolsó oldal / Last page",
            on_click=last_page,
            disabled=True,
            width=50,
        )
        
        def update_pagination_buttons():
            """Update pagination button states"""
            current = current_page_ref["value"]
            total = (inventory_service.count_parts() + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE if inventory_service.count_parts() > 0 else 1
            first_btn.disabled = current == 0
            prev_btn.disabled = current == 0
            next_btn.disabled = current >= total - 1
            last_btn.disabled = current >= total - 1
        
        # Pagination controls
        pagination_row = ft.Row([
            first_btn,
            prev_btn,
            page_info_text,
            next_btn,
            last_btn,
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=DesignSystem.SPACING_2) if total_pages > 1 else ft.Container()
        
        # Initial button state update
        update_pagination_buttons()

        # Create add button
        add_btn = create_modern_button(
            text="+ " + translator.get_text("inventory.add_part"),
            icon=ft.Icons.ADD,
            tooltip=translator.get_text("inventory.add_part"),
            on_click=open_add_part_dialog,
            bgcolor=DesignSystem.BLUE_500,
            color=DesignSystem.WHITE,
            height=40,
        )
        
        # Group by dropdown
        group_by_dropdown = create_modern_dropdown(
            label=translator.get_text("inventory.group_by") if translator.get_text("inventory.group_by") != "inventory.group_by" else "Csoportosítás",
            options=[
                ft.dropdown.Option("all", translator.get_text("inventory.group_all") if translator.get_text("inventory.group_all") != "inventory.group_all" else "Összes"),
                ft.dropdown.Option("production_line", translator.get_text("inventory.group_by_production_line") if translator.get_text("inventory.group_by_production_line") != "inventory.group_by_production_line" else "Termelési sorok szerint"),
                ft.dropdown.Option("machine", translator.get_text("inventory.group_by_machine") if translator.get_text("inventory.group_by_machine") != "inventory.group_by_machine" else "Eszközök szerint"),
            ],
            value="all",
            on_change=lambda e: (group_by_ref.update({"value": e.control.value}), refresh_parts_list(update_page=True)),
        )

        # Pagination row - only show when not grouping
        def get_pagination_row():
            if group_by_ref["value"] == "all":
                return pagination_row if total_pages > 1 else ft.Container()
            else:
                return ft.Container()
        
        return ft.Column([
            ft.Row([
                ft.Text(translator.get_text("inventory.parts"), size=18, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                group_by_dropdown,
                ft.Container(width=DesignSystem.SPACING_2),
                add_btn,
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            get_pagination_row(),
            parts_list,
            get_pagination_row(),
        ], spacing=12, expand=True)
