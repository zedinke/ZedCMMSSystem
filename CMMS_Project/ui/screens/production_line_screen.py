"""
Production Line Management Screen
"""

import flet as ft
from services import asset_service, inventory_service, pm_service, user_service
from services.context_service import get_app_context
from database.session_manager import SessionLocal
from database.models import Machine, PMTask, PMHistory
from localization.translator import translator
from utils.currency import format_price
from ui.components.modern_components import (
    create_modern_button,
    create_modern_text_field,
    create_modern_dropdown,
    create_modern_date_field,
    create_vibrant_badge,
    create_modern_icon_button,
    create_empty_state_card,
    DesignSystem,
)
from datetime import datetime
from ui.components.modern_card import create_tailwind_card
import logging

logger = logging.getLogger(__name__)


class ProductionLineScreen:
    def __init__(self, page: ft.Page):
        self.page = page
    
    def view(self, page: ft.Page):
        if not hasattr(self, 'page') or self.page is None:
            self.page = page
        
        # Production lines list container
        production_lines_list = ft.Column([], spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)
        
        # Selected production line details container
        details_container = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        translator.get_text("production_line.select_line") if translator.get_text("production_line.select_line") != "production_line.select_line" else "Válassz termelési sort",
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
        
        selected_production_line_id_ref = {"value": None}
        
        def refresh_production_lines_list():
            """Refresh the production lines list"""
            page_ref = self.page if hasattr(self, 'page') and self.page else page
            if hasattr(page_ref, 'dialog') and page_ref.dialog is not None:
                dialog_open = getattr(page_ref.dialog, 'open', False)
                if dialog_open:
                    return
            
            session = SessionLocal()
            try:
                production_lines = asset_service.list_production_lines(session)
                production_lines_list.controls.clear()
                
                if not production_lines:
                    production_lines_list.controls.append(
                        ft.Container(
                            content=ft.Text(
                                translator.get_text("production_line.no_lines") if translator.get_text("production_line.no_lines") != "production_line.no_lines" else "Nincs termelési sor",
                                size=14,
                                color=DesignSystem.TEXT_SECONDARY,
                                italic=True,
                            ),
                            padding=20,
                            alignment=ft.alignment.center,
                        )
                    )
                else:
                    for pl in production_lines:
                        is_selected = selected_production_line_id_ref["value"] == pl.id
                        
                        # Get machine count
                        machine_count = session.query(Machine).filter_by(production_line_id=pl.id).count()
                        
                        # Create production line card
                        row_items = [
                            ft.Icon(
                                ft.Icons.PRECISION_MANUFACTURING if hasattr(ft.Icons, 'PRECISION_MANUFACTURING') else ft.Icons.FACTORY,
                                size=24,
                                color=DesignSystem.BLUE_500 if is_selected else DesignSystem.TEXT_SECONDARY,
                            ),
                            ft.Text(
                                pl.name,
                                size=16,
                                weight=ft.FontWeight.W_600 if is_selected else ft.FontWeight.W_500,
                                color=DesignSystem.TEXT_PRIMARY,
                                expand=True,
                            ),
                        ]
                        if machine_count > 0:
                            row_items.append(
                                create_vibrant_badge(
                                    text=f"{machine_count} {translator.get_text('production_line.machines') if translator.get_text('production_line.machines') != 'production_line.machines' else 'Gép'}",
                                    variant="blue",
                                )
                            )
                        
                        column_items = [
                            ft.Row(row_items, spacing=DesignSystem.SPACING_3),
                        ]
                        
                        if pl.description:
                            column_items.append(
                                ft.Text(
                                    pl.description,
                                    size=13,
                                    color=DesignSystem.TEXT_PRIMARY,
                                )
                            )
                        else:
                            column_items.append(
                                ft.Text(
                                    translator.get_text("production_line.no_description") if translator.get_text("production_line.no_description") != "production_line.no_description" else "Nincs leírás",
                                    size=13,
                                    color=DesignSystem.TEXT_SECONDARY,
                                    italic=True,
                                )
                            )
                        
                        if pl.location:
                            column_items.append(
                                ft.Text(
                                    f"{translator.get_text('production_line.location') if translator.get_text('production_line.location') != 'production_line.location' else 'Helyszín'}: {pl.location}",
                                    size=12,
                                    color=DesignSystem.TEXT_TERTIARY,
                                )
                            )
                        
                        pl_card = create_tailwind_card(
                            content=ft.Column(column_items, spacing=DesignSystem.SPACING_2, tight=True),
                            padding=DesignSystem.SPACING_4,
                            elevation=2 if is_selected else 1,
                            accent_color=DesignSystem.BLUE_500 if is_selected else None,
                            border_accent=is_selected,
                            on_click=lambda e, pl_id=pl.id: select_production_line(pl_id),
                        )
                        
                        if is_selected:
                            pl_card.border = ft.border.all(2, DesignSystem.BLUE_500)
                            pl_card.bgcolor = DesignSystem.BLUE_50 if hasattr(DesignSystem, 'BLUE_50') else "#EFF6FF"
                        
                        production_lines_list.controls.append(pl_card)
            except Exception as e:
                logger.error(f"Error loading production lines: {e}", exc_info=True)
                production_lines_list.controls.clear()
                production_lines_list.controls.append(
                    create_empty_state_card(
                        icon=ft.Icons.ERROR if hasattr(ft.Icons, 'ERROR') else ft.Icons.WARNING,
                        title=translator.get_text("common.error") if translator.get_text("common.error") != "common.error" else "Hiba",
                        description=str(e),
                    )
                )
            finally:
                session.close()
            
            page_ref.update()
        
        def select_production_line(production_line_id: int):
            """Select a production line and show its details"""
            selected_production_line_id_ref["value"] = production_line_id
            
            session = SessionLocal()
            try:
                production_line = asset_service.list_production_lines(session)
                production_line = next((pl for pl in production_line if pl.id == production_line_id), None)
                
                if not production_line:
                    return
                
                # Get machines for this production line with compatible parts loaded (including supplier)
                from sqlalchemy.orm import joinedload
                from database.models import Part
                machines_query = session.query(Machine).options(
                    joinedload(Machine.id_compatible_parts).joinedload(Part.supplier)
                ).filter_by(production_line_id=production_line_id)
                machines = machines_query.all()
                
                # Define open_part_details_dialog function (shared between Machines and Parts tabs)
                def open_part_details_dialog(part, inv_level_dict_item):
                    """Open detailed dialog for part"""
                    dialog_page = self.page if hasattr(self, 'page') and self.page else page
                    
                    inv_level = inv_level_dict_item
                    stock_qty = inv_level.quantity_on_hand if inv_level else 0
                    stock_reserved = inv_level.quantity_reserved if inv_level else 0
                    stock_available = stock_qty - stock_reserved
                    bin_location = inv_level.bin_location if inv_level else None
                    
                    # Build detailed content for dialog
                    dialog_content_items = []
                    
                    # Part header
                    dialog_content_items.append(
                        ft.Row([
                            ft.Text(
                                part.name,
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                color=DesignSystem.TEXT_PRIMARY,
                                expand=True,
                            ),
                            create_vibrant_badge(
                                text=part.sku,
                                variant="blue",
                                size=12,
                            ) if part.sku else None,
                        ], spacing=DesignSystem.SPACING_2)
                    )
                    dialog_content_items.append(ft.Container(height=DesignSystem.SPACING_3))
                    dialog_content_items.append(ft.Divider(height=1, color=DesignSystem.BORDER_COLOR))
                    dialog_content_items.append(ft.Container(height=DesignSystem.SPACING_3))
                    
                    # Basic information
                    basic_info_items = []
                    basic_info_items.append(
                        ft.Text(
                            translator.get_text("assets.basic_info") if translator.get_text("assets.basic_info") != "assets.basic_info" else "Alapinformációk",
                            size=16,
                            weight=ft.FontWeight.W_600,
                            color=DesignSystem.TEXT_PRIMARY,
                        )
                    )
                    basic_info_items.append(ft.Container(height=DesignSystem.SPACING_2))
                    
                    basic_grid = []
                    if part.category:
                        basic_grid.append(ft.Column([
                            ft.Text(f"{translator.get_text('inventory.category') if translator.get_text('inventory.category') != 'inventory.category' else 'Kategória'}:", size=13, weight=ft.FontWeight.W_500, color=DesignSystem.TEXT_SECONDARY),
                            ft.Text(part.category, size=14, color=DesignSystem.TEXT_PRIMARY),
                        ], spacing=2, expand=True))
                    if part.unit:
                        basic_grid.append(ft.Column([
                            ft.Text(f"{translator.get_text('inventory.unit') if translator.get_text('inventory.unit') != 'inventory.unit' else 'Mértékegység'}:", size=13, weight=ft.FontWeight.W_500, color=DesignSystem.TEXT_SECONDARY),
                            ft.Text(part.unit, size=14, color=DesignSystem.TEXT_PRIMARY),
                        ], spacing=2, expand=True))
                    
                    if basic_grid:
                        for i in range(0, len(basic_grid), 2):
                            row_items = [item for item in basic_grid[i:i+2] if item is not None]
                            if row_items:
                                basic_info_items.append(ft.Row(row_items, spacing=DesignSystem.SPACING_4))
                    
                    if part.description:
                        basic_info_items.append(ft.Container(height=DesignSystem.SPACING_2))
                        basic_info_items.append(
                            ft.Column([
                                ft.Text(f"{translator.get_text('production_line.description') if translator.get_text('production_line.description') != 'production_line.description' else 'Leírás'}:", size=13, weight=ft.FontWeight.W_500, color=DesignSystem.TEXT_SECONDARY),
                                ft.Text(part.description, size=14, color=DesignSystem.TEXT_PRIMARY),
                            ], spacing=2)
                        )
                    
                    dialog_content_items.append(ft.Column(basic_info_items, spacing=DesignSystem.SPACING_2))
                    dialog_content_items.append(ft.Container(height=DesignSystem.SPACING_4))
                    
                    # Stock information
                    stock_info_items = []
                    stock_info_items.append(
                        ft.Text(
                            translator.get_text("inventory.stock_info") if translator.get_text("inventory.stock_info") != "inventory.stock_info" else "Készlet információk",
                            size=16,
                            weight=ft.FontWeight.W_600,
                            color=DesignSystem.TEXT_PRIMARY,
                        )
                    )
                    stock_info_items.append(ft.Container(height=DesignSystem.SPACING_2))
                    
                    stock_row1 = ft.Row([
                        ft.Column([
                            ft.Text(f"{translator.get_text('inventory.on_hand') if translator.get_text('inventory.on_hand') != 'inventory.on_hand' else 'Raktáron'}:", size=13, weight=ft.FontWeight.W_500, color=DesignSystem.TEXT_SECONDARY),
                            ft.Text(f"{stock_qty} {part.unit}", size=14, color=DesignSystem.TEXT_PRIMARY),
                        ], expand=True),
                        ft.Column([
                            ft.Text(f"{translator.get_text('inventory.quantity_reserved') if translator.get_text('inventory.quantity_reserved') != 'inventory.quantity_reserved' else 'Foglalt'}:", size=13, weight=ft.FontWeight.W_500, color=DesignSystem.TEXT_SECONDARY),
                            ft.Text(f"{stock_reserved} {part.unit}", size=14, color=DesignSystem.TEXT_PRIMARY),
                        ], expand=True),
                        ft.Column([
                            ft.Text(f"{translator.get_text('inventory.quantity_available') if translator.get_text('inventory.quantity_available') != 'inventory.quantity_available' else 'Elérhető'}:", size=13, weight=ft.FontWeight.W_500, color=DesignSystem.TEXT_SECONDARY),
                            ft.Text(f"{stock_available} {part.unit}", size=14, color=DesignSystem.TEXT_PRIMARY, weight=ft.FontWeight.W_600),
                        ], expand=True),
                    ], spacing=DesignSystem.SPACING_4)
                    stock_info_items.append(stock_row1)
                    
                    if bin_location:
                        stock_info_items.append(ft.Container(height=DesignSystem.SPACING_2))
                        stock_info_items.append(
                            ft.Text(
                                f"{translator.get_text('inventory.bin_location') if translator.get_text('inventory.bin_location') != 'inventory.bin_location' else 'Raktárhely'}: {bin_location}",
                                size=13,
                                color=DesignSystem.TEXT_SECONDARY,
                            )
                        )
                    
                    if part.safety_stock is not None and part.safety_stock > 0:
                        stock_info_items.append(ft.Container(height=DesignSystem.SPACING_2))
                        stock_info_items.append(
                            ft.Row([
                                ft.Text(f"{translator.get_text('inventory.safety_stock') if translator.get_text('inventory.safety_stock') != 'inventory.safety_stock' else 'Minimális készlet'}:", size=13, weight=ft.FontWeight.W_500, color=DesignSystem.TEXT_SECONDARY),
                                ft.Text(f"{part.safety_stock} {part.unit}", size=13, color=DesignSystem.TEXT_PRIMARY),
                                create_vibrant_badge(
                                    text=translator.get_text("inventory.low_stock") if stock_qty <= part.safety_stock else translator.get_text("inventory.ok_stock") if translator.get_text("inventory.ok_stock") != "inventory.ok_stock" else "Rendben",
                                    variant="red" if stock_qty <= part.safety_stock else "emerald",
                                    size=11,
                                ),
                            ], spacing=DesignSystem.SPACING_2)
                        )
                    
                    dialog_content_items.append(ft.Column(stock_info_items, spacing=DesignSystem.SPACING_2))
                    dialog_content_items.append(ft.Container(height=DesignSystem.SPACING_4))
                    
                    # Financial information
                    financial_items = []
                    financial_items.append(
                        ft.Text(
                            translator.get_text("inventory.financial_info") if translator.get_text("inventory.financial_info") != "inventory.financial_info" else "Pénzügyi információk",
                            size=16,
                            weight=ft.FontWeight.W_600,
                            color=DesignSystem.TEXT_PRIMARY,
                        )
                    )
                    financial_items.append(ft.Container(height=DesignSystem.SPACING_2))
                    
                    financial_grid = []
                    financial_grid.append(ft.Column([
                        ft.Text(f"{translator.get_text('inventory.buy_price') if translator.get_text('inventory.buy_price') != 'inventory.buy_price' else 'Vételár (nettó)'}:", size=13, weight=ft.FontWeight.W_500, color=DesignSystem.TEXT_SECONDARY),
                        ft.Text(format_price(part.buy_price), size=14, color=DesignSystem.TEXT_PRIMARY),
                    ], spacing=2, expand=True))
                    
                    if part.sell_price:
                        financial_grid.append(ft.Column([
                            ft.Text(f"{translator.get_text('inventory.sell_price') if translator.get_text('inventory.sell_price') != 'inventory.sell_price' else 'Eladási ár'}:", size=13, weight=ft.FontWeight.W_500, color=DesignSystem.TEXT_SECONDARY),
                            ft.Text(format_price(part.sell_price), size=14, color=DesignSystem.TEXT_PRIMARY),
                        ], spacing=2, expand=True))
                    
                    if part.reorder_quantity:
                        financial_grid.append(ft.Column([
                            ft.Text(f"{translator.get_text('inventory.reorder_quantity') if translator.get_text('inventory.reorder_quantity') != 'inventory.reorder_quantity' else 'Újrarendelési mennyiség'}:", size=13, weight=ft.FontWeight.W_500, color=DesignSystem.TEXT_SECONDARY),
                            ft.Text(f"{part.reorder_quantity} {part.unit}", size=14, color=DesignSystem.TEXT_PRIMARY),
                        ], spacing=2, expand=True))
                    
                    if financial_grid:
                        for i in range(0, len(financial_grid), 2):
                            row_items = [item for item in financial_grid[i:i+2] if item is not None]
                            if row_items:
                                financial_items.append(ft.Row(row_items, spacing=DesignSystem.SPACING_4))
                    
                    # Try to get supplier safely (it may be detached from session)
                    try:
                        supplier = getattr(part, 'supplier', None)
                        if supplier:
                            try:
                                supplier_name = supplier.name if hasattr(supplier, 'name') else str(supplier)
                            except:
                                supplier_id = getattr(part, 'supplier_id', None)
                                if supplier_id:
                                    try:
                                        temp_session = SessionLocal()
                                        from database.models import Supplier
                                        supplier_obj = temp_session.query(Supplier).filter_by(id=supplier_id).first()
                                        supplier_name = supplier_obj.name if supplier_obj else f"Supplier ID: {supplier_id}"
                                        temp_session.close()
                                    except:
                                        supplier_name = f"Supplier ID: {supplier_id}"
                                else:
                                    supplier_name = translator.get_text("inventory.unknown_supplier") if translator.get_text("inventory.unknown_supplier") != "inventory.unknown_supplier" else "Ismeretlen beszállító"
                            
                            financial_items.append(ft.Container(height=DesignSystem.SPACING_2))
                            financial_items.append(
                                ft.Text(
                                    f"{translator.get_text('inventory.supplier') if translator.get_text('inventory.supplier') != 'inventory.supplier' else 'Beszállító'}: {supplier_name}",
                                    size=13,
                                    color=DesignSystem.TEXT_SECONDARY,
                                )
                            )
                    except Exception as supplier_err:
                        logger.warning(f"Error getting supplier: {supplier_err}")
                    
                    dialog_content_items.append(ft.Column(financial_items, spacing=DesignSystem.SPACING_2))
                    
                    # Filter None values
                    dialog_content_items = [item for item in dialog_content_items if item is not None]
                    
                    dialog = ft.AlertDialog(
                        modal=True,
                        title=ft.Row([
                            ft.Icon(ft.Icons.INVENTORY_2, color=DesignSystem.BLUE_500, size=24),
                            ft.Text(
                                translator.get_text("inventory.part_details") if translator.get_text("inventory.part_details") != "inventory.part_details" else "Alkatrész részletek",
                                size=18,
                                weight=ft.FontWeight.BOLD
                            )
                        ]),
                        content=ft.Container(
                            content=ft.Column(dialog_content_items, spacing=DesignSystem.SPACING_2, scroll=ft.ScrollMode.AUTO),
                            width=600,
                            height=600,
                        ),
                        actions=[
                            ft.TextButton(
                                translator.get_text("common.buttons.close") if translator.get_text("common.buttons.close") != "common.buttons.close" else "Bezárás",
                                on_click=lambda _: (setattr(dialog, 'open', False), dialog_page.update())
                            ),
                        ],
                    )
                    
                    try:
                        dialog_page.open(dialog)
                    except:
                        dialog_page.dialog = dialog
                        dialog.open = True
                        dialog_page.update()
                
                # Build production line header
                header_content = ft.Column([
                    ft.Text(
                        production_line.name,
                        size=22,
                        weight=ft.FontWeight.BOLD,
                        color=DesignSystem.TEXT_PRIMARY,
                    ),
                    ft.Divider(height=1, color=DesignSystem.BORDER_COLOR),
                    ft.Container(height=DesignSystem.SPACING_2),
                    ft.Row([
                        ft.Column([
                            ft.Text(
                                f"{translator.get_text('production_line.description') if translator.get_text('production_line.description') != 'production_line.description' else 'Leírás'}:",
                                size=12,
                                weight=ft.FontWeight.W_600,
                                color=DesignSystem.TEXT_SECONDARY,
                            ),
                            ft.Text(
                                production_line.description or translator.get_text("production_line.no_description") if translator.get_text("production_line.no_description") != "production_line.no_description" else "Nincs leírás",
                                size=14,
                                color=DesignSystem.TEXT_PRIMARY,
                            ),
                        ], expand=True, spacing=4),
                        ft.Column([
                            ft.Text(
                                f"{translator.get_text('production_line.location') if translator.get_text('production_line.location') != 'production_line.location' else 'Helyszín'}:",
                                size=12,
                                weight=ft.FontWeight.W_600,
                                color=DesignSystem.TEXT_SECONDARY,
                            ),
                            ft.Text(
                                production_line.location or "-",
                                size=14,
                                color=DesignSystem.TEXT_PRIMARY,
                            ),
                        ], expand=True, spacing=4),
                    ], spacing=DesignSystem.SPACING_4),
                ], spacing=DesignSystem.SPACING_2)
                
                # Build machines list with details
                machines_column_items = []
                
                if not machines:
                    machines_column_items.append(
                        create_empty_state_card(
                            icon=ft.Icons.PRECISION_MANUFACTURING if hasattr(ft.Icons, 'PRECISION_MANUFACTURING') else ft.Icons.FACTORY,
                            title=translator.get_text("production_line.no_machines") if translator.get_text("production_line.no_machines") != "production_line.no_machines" else "Nincs gép",
                            icon_color=DesignSystem.GRAY_400,
                        )
                    )
                else:
                    # Get all part IDs for batch loading inventory levels
                    all_part_ids = []
                    for machine in machines:
                        compatible_parts = machine.id_compatible_parts if hasattr(machine, 'id_compatible_parts') else []
                        all_part_ids.extend([p.id for p in compatible_parts])
                    
                    # Batch load inventory levels
                    inv_levels_dict = {}
                    if all_part_ids:
                        inv_levels_dict = inventory_service.get_inventory_levels_batch(all_part_ids)
                    
                    for machine in machines:
                        compatible_parts = machine.id_compatible_parts if hasattr(machine, 'id_compatible_parts') else []
                        
                        # Build machine details card with comprehensive information
                        machine_details_items = []
                        
                        # Machine header with name and status
                        machine_header_items = [
                            ft.Text(
                                machine.name,
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                color=DesignSystem.TEXT_PRIMARY,
                                expand=True,
                            ),
                        ]
                        if machine.status:
                            machine_header_items.append(
                                create_vibrant_badge(
                                    text=machine.status or "Active",
                                    variant="emerald" if (machine.status or "Active") == "Active" else ("orange" if (machine.status or "") == "Stopped" else "red"),
                                    size=12,
                                )
                            )
                        if machine.criticality_level:
                            machine_header_items.append(
                                create_vibrant_badge(
                                    text=machine.criticality_level or "Medium",
                                    variant="red" if (machine.criticality_level or "").lower() == "critical" else ("orange" if (machine.criticality_level or "").lower() == "high" else "blue"),
                                    size=11,
                                )
                            )
                        machine_details_items.append(ft.Row(machine_header_items, spacing=DesignSystem.SPACING_2))
                        machine_details_items.append(ft.Container(height=DesignSystem.SPACING_3))
                        machine_details_items.append(ft.Divider(height=1, color=DesignSystem.BORDER_COLOR))
                        machine_details_items.append(ft.Container(height=DesignSystem.SPACING_3))
                        
                        # Basic Information Section
                        basic_info_items = []
                        basic_info_items.append(
                            ft.Text(
                                translator.get_text("assets.basic_info") if translator.get_text("assets.basic_info") != "assets.basic_info" else "Alapinformációk",
                                size=14,
                                weight=ft.FontWeight.W_600,
                                color=DesignSystem.TEXT_PRIMARY,
                            )
                        )
                        basic_info_items.append(ft.Container(height=DesignSystem.SPACING_2))
                        
                        # First row of basic info
                        basic_row1 = ft.Row([
                            ft.Column([
                                ft.Text(
                                    f"{translator.get_text('assets.serial_number') if translator.get_text('assets.serial_number') != 'assets.serial_number' else 'Sorozatszám'}:",
                                    size=12,
                                    weight=ft.FontWeight.W_500,
                                    color=DesignSystem.TEXT_SECONDARY,
                                ),
                                ft.Text(
                                    machine.serial_number or "-",
                                    size=14,
                                    color=DesignSystem.TEXT_PRIMARY,
                                ),
                            ], expand=True, spacing=2),
                            ft.Column([
                                ft.Text(
                                    f"{translator.get_text('assets.model') if translator.get_text('assets.model') != 'assets.model' else 'Modell'}:",
                                    size=12,
                                    weight=ft.FontWeight.W_500,
                                    color=DesignSystem.TEXT_SECONDARY,
                                ),
                                ft.Text(
                                    machine.model or "-",
                                    size=14,
                                    color=DesignSystem.TEXT_PRIMARY,
                                ),
                            ], expand=True, spacing=2),
                            ft.Column([
                                ft.Text(
                                    f"{translator.get_text('assets.manufacturer') if translator.get_text('assets.manufacturer') != 'assets.manufacturer' else 'Gyártó'}:",
                                    size=12,
                                    weight=ft.FontWeight.W_500,
                                    color=DesignSystem.TEXT_SECONDARY,
                                ),
                                ft.Text(
                                    machine.manufacturer or "-",
                                    size=14,
                                    color=DesignSystem.TEXT_PRIMARY,
                                ),
                            ], expand=True, spacing=2),
                        ], spacing=DesignSystem.SPACING_4)
                        basic_info_items.append(basic_row1)
                        
                        # Asset tag
                        if machine.asset_tag:
                            basic_info_items.append(ft.Container(height=DesignSystem.SPACING_2))
                            basic_info_items.append(
                                ft.Text(
                                    f"{translator.get_text('assets.asset_tag') if translator.get_text('assets.asset_tag') != 'assets.asset_tag' else 'Eszköz azonosító'}: {machine.asset_tag}",
                                    size=13,
                                    color=DesignSystem.TEXT_SECONDARY,
                                )
                            )
                        
                        # Filter None values before creating Column
                        basic_info_items = [item for item in basic_info_items if item is not None]
                        if basic_info_items:
                            machine_details_items.append(ft.Column(basic_info_items, spacing=DesignSystem.SPACING_2))
                            machine_details_items.append(ft.Container(height=DesignSystem.SPACING_4))
                        
                        # Dates & Lifecycle Section
                        dates_items = []
                        dates_items.append(
                            ft.Text(
                                translator.get_text("assets.dates_lifecycle") if translator.get_text("assets.dates_lifecycle") != "assets.dates_lifecycle" else "Dátumok és életciklus",
                                size=14,
                                weight=ft.FontWeight.W_600,
                                color=DesignSystem.TEXT_PRIMARY,
                            )
                        )
                        dates_items.append(ft.Container(height=DesignSystem.SPACING_2))
                        
                        dates_grid = []
                        if machine.install_date:
                            dates_grid.append(ft.Column([
                                ft.Text("Telepítés:", size=12, weight=ft.FontWeight.W_500, color=DesignSystem.TEXT_SECONDARY),
                                ft.Text(machine.install_date.strftime('%Y-%m-%d'), size=13, color=DesignSystem.TEXT_PRIMARY),
                            ], spacing=2, expand=True))
                        if machine.purchase_date:
                            dates_grid.append(ft.Column([
                                ft.Text("Vásárlás:", size=12, weight=ft.FontWeight.W_500, color=DesignSystem.TEXT_SECONDARY),
                                ft.Text(machine.purchase_date.strftime('%Y-%m-%d'), size=13, color=DesignSystem.TEXT_PRIMARY),
                            ], spacing=2, expand=True))
                        if machine.last_service_date:
                            dates_grid.append(ft.Column([
                                ft.Text("Utolsó karbantartás:", size=12, weight=ft.FontWeight.W_500, color=DesignSystem.TEXT_SECONDARY),
                                ft.Text(machine.last_service_date.strftime('%Y-%m-%d'), size=13, color=DesignSystem.TEXT_PRIMARY),
                            ], spacing=2, expand=True))
                        if machine.next_service_date:
                            dates_grid.append(ft.Column([
                                ft.Text("Következő karbantartás:", size=12, weight=ft.FontWeight.W_500, color=DesignSystem.TEXT_SECONDARY),
                                ft.Text(machine.next_service_date.strftime('%Y-%m-%d'), size=13, color=DesignSystem.TEXT_PRIMARY),
                            ], spacing=2, expand=True))
                        if machine.warranty_expiry_date:
                            dates_grid.append(ft.Column([
                                ft.Text("Garancia lejárta:", size=12, weight=ft.FontWeight.W_500, color=DesignSystem.TEXT_SECONDARY),
                                ft.Text(machine.warranty_expiry_date.strftime('%Y-%m-%d'), size=13, color=DesignSystem.TEXT_PRIMARY),
                            ], spacing=2, expand=True))
                        
                        if dates_grid:
                            # Arrange in rows of 2
                            for i in range(0, len(dates_grid), 2):
                                row_items = [item for item in dates_grid[i:i+2] if item is not None]
                                if row_items:
                                    dates_items.append(ft.Row(row_items, spacing=DesignSystem.SPACING_4))
                        
                        # Filter None values before creating Column
                        dates_items = [item for item in dates_items if item is not None]
                        if dates_items:
                            machine_details_items.append(ft.Column(dates_items, spacing=DesignSystem.SPACING_2))
                        machine_details_items.append(ft.Container(height=DesignSystem.SPACING_4))
                        
                        # Operational Information Section
                        operational_items = []
                        operational_items.append(
                            ft.Text(
                                translator.get_text("assets.operational_info") if translator.get_text("assets.operational_info") != "assets.operational_info" else "Működési információk",
                                size=14,
                                weight=ft.FontWeight.W_600,
                                color=DesignSystem.TEXT_PRIMARY,
                            )
                        )
                        operational_items.append(ft.Container(height=DesignSystem.SPACING_2))
                        
                        operational_grid = []
                        if machine.operating_hours is not None:
                            operational_grid.append(ft.Column([
                                ft.Text("Üzemóra:", size=12, weight=ft.FontWeight.W_500, color=DesignSystem.TEXT_SECONDARY),
                                ft.Text(f"{machine.operating_hours:.1f} óra", size=13, color=DesignSystem.TEXT_PRIMARY),
                            ], spacing=2, expand=True))
                        if machine.maintenance_interval:
                            operational_grid.append(ft.Column([
                                ft.Text("Karbantartási intervallum:", size=12, weight=ft.FontWeight.W_500, color=DesignSystem.TEXT_SECONDARY),
                                ft.Text(machine.maintenance_interval, size=13, color=DesignSystem.TEXT_PRIMARY),
                            ], spacing=2, expand=True))
                        if machine.energy_consumption:
                            operational_grid.append(ft.Column([
                                ft.Text("Energiafogyasztás:", size=12, weight=ft.FontWeight.W_500, color=DesignSystem.TEXT_SECONDARY),
                                ft.Text(machine.energy_consumption, size=13, color=DesignSystem.TEXT_PRIMARY),
                            ], spacing=2, expand=True))
                        if machine.power_requirements:
                            operational_grid.append(ft.Column([
                                ft.Text("Teljesítmény igények:", size=12, weight=ft.FontWeight.W_500, color=DesignSystem.TEXT_SECONDARY),
                                ft.Text(machine.power_requirements, size=13, color=DesignSystem.TEXT_PRIMARY),
                            ], spacing=2, expand=True))
                        if machine.operating_temperature_range:
                            operational_grid.append(ft.Column([
                                ft.Text("Működési hőmérséklet:", size=12, weight=ft.FontWeight.W_500, color=DesignSystem.TEXT_SECONDARY),
                                ft.Text(machine.operating_temperature_range, size=13, color=DesignSystem.TEXT_PRIMARY),
                            ], spacing=2, expand=True))
                        
                        if operational_grid:
                            for i in range(0, len(operational_grid), 2):
                                row_items = [item for item in operational_grid[i:i+2] if item is not None]
                                if row_items:
                                    operational_items.append(ft.Row(row_items, spacing=DesignSystem.SPACING_4))
                        
                        # Filter None values before creating Column
                        operational_items = [item for item in operational_items if item is not None]
                        if operational_items:
                            machine_details_items.append(ft.Column(operational_items, spacing=DesignSystem.SPACING_2))
                            machine_details_items.append(ft.Container(height=DesignSystem.SPACING_4))
                        
                        # Physical & Financial Information Section
                        physical_financial_items = []
                        physical_financial_items.append(
                            ft.Text(
                                translator.get_text("assets.physical_financial") if translator.get_text("assets.physical_financial") != "assets.physical_financial" else "Fizikai és pénzügyi információk",
                                size=14,
                                weight=ft.FontWeight.W_600,
                                color=DesignSystem.TEXT_PRIMARY,
                            )
                        )
                        physical_financial_items.append(ft.Container(height=DesignSystem.SPACING_2))
                        
                        pf_grid = []
                        if machine.weight:
                            pf_grid.append(ft.Column([
                                ft.Text("Súly:", size=12, weight=ft.FontWeight.W_500, color=DesignSystem.TEXT_SECONDARY),
                                ft.Text(f"{machine.weight:.2f} kg", size=13, color=DesignSystem.TEXT_PRIMARY),
                            ], spacing=2, expand=True))
                        if machine.dimensions:
                            pf_grid.append(ft.Column([
                                ft.Text("Méretek:", size=12, weight=ft.FontWeight.W_500, color=DesignSystem.TEXT_SECONDARY),
                                ft.Text(machine.dimensions, size=13, color=DesignSystem.TEXT_PRIMARY),
                            ], spacing=2, expand=True))
                        if machine.purchase_price:
                            pf_grid.append(ft.Column([
                                ft.Text("Vételár:", size=12, weight=ft.FontWeight.W_500, color=DesignSystem.TEXT_SECONDARY),
                                ft.Text(format_price(machine.purchase_price), size=13, color=DesignSystem.TEXT_PRIMARY),
                            ], spacing=2, expand=True))
                        if machine.supplier:
                            pf_grid.append(ft.Column([
                                ft.Text("Beszállító:", size=12, weight=ft.FontWeight.W_500, color=DesignSystem.TEXT_SECONDARY),
                                ft.Text(machine.supplier, size=13, color=DesignSystem.TEXT_PRIMARY),
                            ], spacing=2, expand=True))
                        
                        if pf_grid:
                            for i in range(0, len(pf_grid), 2):
                                row_items = [item for item in pf_grid[i:i+2] if item is not None]
                                if row_items:
                                    physical_financial_items.append(ft.Row(row_items, spacing=DesignSystem.SPACING_4))
                        
                        # Filter None values before creating Column
                        physical_financial_items = [item for item in physical_financial_items if item is not None]
                        if physical_financial_items:
                            machine_details_items.append(ft.Column(physical_financial_items, spacing=DesignSystem.SPACING_2))
                        
                        # Notes section
                        if machine.notes:
                            machine_details_items.append(ft.Container(height=DesignSystem.SPACING_4))
                            machine_details_items.append(ft.Divider(height=1, color=DesignSystem.BORDER_COLOR))
                            machine_details_items.append(ft.Container(height=DesignSystem.SPACING_2))
                            machine_details_items.append(
                                ft.Column([
                                    ft.Text(
                                        translator.get_text("assets.notes") if translator.get_text("assets.notes") != "assets.notes" else "Megjegyzések",
                                        size=14,
                                        weight=ft.FontWeight.W_600,
                                        color=DesignSystem.TEXT_PRIMARY,
                                    ),
                                    ft.Text(
                                        machine.notes,
                                        size=13,
                                        color=DesignSystem.TEXT_PRIMARY,
                                    ),
                                ], spacing=DesignSystem.SPACING_2)
                            )
                        
                        # Maintenance request button
                        def open_maintenance_request_dialog(machine_instance):
                            """Open dialog to request maintenance for machine"""
                            dialog_page = self.page if hasattr(self, 'page') and self.page else page
                            
                            # Get current user ID
                            ctx = get_app_context()
                            dialog_user_id = ctx.user_id if ctx.is_authenticated() else None
                            
                            # Get users for assignment
                            users = user_service.list_all_users()
                            
                            # Pre-fill task name
                            task_name_field = create_modern_text_field(
                                label=translator.get_text("preventive_maintenance.task_name") if translator.get_text("preventive_maintenance.task_name") != "preventive_maintenance.task_name" else "Feladat neve",
                                value=f"Karbantartás - {machine_instance.name}",
                                width=400,
                            )
                            
                            # Task description
                            task_description_field = create_modern_text_field(
                                label=translator.get_text("preventive_maintenance.task_description") if translator.get_text("preventive_maintenance.task_description") != "preventive_maintenance.task_description" else "Feladat leírása",
                                multiline=True,
                                max_lines=3,
                                width=400,
                                hint_text=translator.get_text("preventive_maintenance.task_description_hint") if translator.get_text("preventive_maintenance.task_description_hint") != "preventive_maintenance.task_description_hint" else "Részletes leírás...",
                            )
                            
                            # Assignment options
                            assignment_radio = ft.RadioGroup(
                                content=ft.Column([
                                    ft.Radio(value="global", label=translator.get_text("preventive_maintenance.global_assignment") if translator.get_text("preventive_maintenance.global_assignment") != "preventive_maintenance.global_assignment" else "Globális kiosztás"),
                                    ft.Radio(value="assigned", label=translator.get_text("preventive_maintenance.assigned_to_user") if translator.get_text("preventive_maintenance.assigned_to_user") != "preventive_maintenance.assigned_to_user" else "Felhasználóhoz rendelés"),
                                ], spacing=4),
                                value="global",
                            )
                            
                            # User dropdown (initially disabled)
                            user_options = [ft.dropdown.Option(str(u.id), f"{u.full_name or u.username} ({u.username})") for u in users] if users else []
                            assigned_user_dropdown = ft.Dropdown(
                                label=translator.get_text("preventive_maintenance.assigned_user") if translator.get_text("preventive_maintenance.assigned_user") != "preventive_maintenance.assigned_user" else "Hozzárendelt felhasználó",
                                prefix_icon=ft.Icons.PERSON,
                                options=user_options,
                                width=300,
                                disabled=True,
                            )
                            
                            def on_assignment_change(_):
                                assigned_user_dropdown.disabled = (assignment_radio.value != "assigned")
                                dialog_page.update()
                            
                            assignment_radio.on_change = on_assignment_change
                            
                            # Priority dropdown
                            priority_dropdown = create_modern_dropdown(
                                label=translator.get_text("preventive_maintenance.priority") if translator.get_text("preventive_maintenance.priority") != "preventive_maintenance.priority" else "Prioritás",
                                options=[
                                    ft.dropdown.Option("low", translator.get_text("preventive_maintenance.priority_low") if translator.get_text("preventive_maintenance.priority_low") != "preventive_maintenance.priority_low" else "Alacsony"),
                                    ft.dropdown.Option("normal", translator.get_text("preventive_maintenance.priority_normal") if translator.get_text("preventive_maintenance.priority_normal") != "preventive_maintenance.priority_normal" else "Normál"),
                                    ft.dropdown.Option("high", translator.get_text("preventive_maintenance.priority_high") if translator.get_text("preventive_maintenance.priority_high") != "preventive_maintenance.priority_high" else "Magas"),
                                    ft.dropdown.Option("urgent", translator.get_text("preventive_maintenance.priority_urgent") if translator.get_text("preventive_maintenance.priority_urgent") != "preventive_maintenance.priority_urgent" else "Sürgős"),
                                ],
                                value="normal",
                            )
                            
                            # Due date field
                            from datetime import timedelta
                            default_due_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
                            due_date_field = create_modern_text_field(
                                label=translator.get_text("preventive_maintenance.due_date") if translator.get_text("preventive_maintenance.due_date") != "preventive_maintenance.due_date" else "Esedékesség",
                                value=default_due_date,
                                hint_text="YYYY-MM-DD",
                                width=200,
                            )
                            
                            def submit_request(_):
                                try:
                                    if not task_name_field.value:
                                        raise ValueError(f"{translator.get_text('preventive_maintenance.task_name') if translator.get_text('preventive_maintenance.task_name') != 'preventive_maintenance.task_name' else 'Feladat neve'} {translator.get_text('common.messages.required_field') if translator.get_text('common.messages.required_field') != 'common.messages.required_field' else 'kötelező'}")
                                    
                                    machine_id = machine_instance.id
                                    
                                    # Parse due date
                                    due_date_value = None
                                    if due_date_field.value:
                                        try:
                                            due_date_value = datetime.strptime(due_date_field.value, '%Y-%m-%d')
                                        except ValueError:
                                            raise ValueError(translator.get_text("common.messages.invalid_date_format") if translator.get_text("common.messages.invalid_date_format") != "common.messages.invalid_date_format" else "Érvénytelen dátum formátum")
                                    
                                    assigned_to_user_id = None
                                    if assignment_radio.value == "assigned":
                                        if not assigned_user_dropdown.value:
                                            raise ValueError(f"{translator.get_text('preventive_maintenance.assignment') if translator.get_text('preventive_maintenance.assignment') != 'preventive_maintenance.assignment' else 'Kiosztás'} {translator.get_text('common.messages.required_field') if translator.get_text('common.messages.required_field') != 'common.messages.required_field' else 'kötelező'}")
                                        assigned_to_user_id = int(assigned_user_dropdown.value)
                                    
                                    # Create one-time PM task for maintenance request
                                    pm_service.create_pm_task(
                                        machine_id=machine_id,
                                        task_name=task_name_field.value,
                                        frequency_days=None,
                                        task_description=task_description_field.value or None,
                                        assigned_to_user_id=assigned_to_user_id,
                                        priority=priority_dropdown.value if hasattr(priority_dropdown, 'value') else "normal",
                                        status="pending",
                                        due_date=due_date_value,
                                        estimated_duration_minutes=60,  # Default 1 hour
                                        created_by_user_id=dialog_user_id,
                                        location=None,
                                        task_type="one_time",
                                    )
                                    
                                    # Close dialog
                                    try:
                                        dialog_page.close(dialog)
                                    except Exception as close_err:
                                        dialog.open = False
                                        dialog_page.update()
                                    
                                    # Show success message
                                    dialog_page.snack_bar = ft.SnackBar(
                                        content=ft.Text(translator.get_text("preventive_maintenance.task_created") if translator.get_text("preventive_maintenance.task_created") != "preventive_maintenance.task_created" else "Karbantartási feladat létrehozva"),
                                        bgcolor=DesignSystem.SUCCESS
                                    )
                                    dialog_page.snack_bar.open = True
                                    dialog_page.update()
                                except Exception as exc:
                                    dialog_page.snack_bar = ft.SnackBar(
                                        content=ft.Text(f"{translator.get_text('common.messages.error_occurred') if translator.get_text('common.messages.error_occurred') != 'common.messages.error_occurred' else 'Hiba történt'}: {str(exc)}"),
                                        bgcolor=DesignSystem.ERROR
                                    )
                                    dialog_page.snack_bar.open = True
                                    dialog_page.update()
                            
                            dialog = ft.AlertDialog(
                                modal=True,
                                title=ft.Row([
                                    ft.Icon(ft.Icons.BUILD, color=DesignSystem.BLUE_500, size=24),
                                    ft.Text(
                                        translator.get_text("preventive_maintenance.request_maintenance") if translator.get_text("preventive_maintenance.request_maintenance") != "preventive_maintenance.request_maintenance" else "Karbantartás igénylése",
                                        size=20,
                                        weight=ft.FontWeight.BOLD,
                                    )
                                ], spacing=10),
                                content=ft.Container(
                                    content=ft.Column([
                                        # Machine info card
                                        create_tailwind_card(
                                            content=ft.Column([
                                                ft.Row([
                                                    ft.Icon(ft.Icons.PRECISION_MANUFACTURING if hasattr(ft.Icons, 'PRECISION_MANUFACTURING') else ft.Icons.FACTORY, size=24, color=DesignSystem.BLUE_500),
                                                    ft.Text(machine_instance.name, size=16, weight=ft.FontWeight.BOLD, color=DesignSystem.TEXT_PRIMARY),
                                                ], spacing=8),
                                                ft.Text(f"Sorozatszám: {machine_instance.serial_number or '-'}", size=12, color=DesignSystem.TEXT_SECONDARY),
                                                ft.Text(f"Modell: {machine_instance.model or '-'}", size=12, color=DesignSystem.TEXT_SECONDARY),
                                                ft.Text(f"Gyártó: {machine_instance.manufacturer or '-'}", size=12, color=DesignSystem.TEXT_SECONDARY),
                                            ], spacing=4),
                                            padding=DesignSystem.SPACING_3,
                                            elevation=0,
                                        ),
                                        ft.Container(height=DesignSystem.SPACING_3),
                                        task_name_field,
                                        task_description_field,
                                        assignment_radio,
                                        assigned_user_dropdown,
                                        ft.Row([
                                            priority_dropdown,
                                            due_date_field,
                                        ], spacing=DesignSystem.SPACING_3),
                                    ], spacing=DesignSystem.SPACING_2, scroll=ft.ScrollMode.AUTO),
                                    width=500,
                                    height=500,
                                ),
                                actions=[
                                    ft.TextButton(
                                        translator.get_text("common.buttons.cancel") if translator.get_text("common.buttons.cancel") != "common.buttons.cancel" else "Mégse",
                                        on_click=lambda _: (setattr(dialog, 'open', False), dialog_page.update())
                                    ),
                                    create_modern_button(
                                        text=translator.get_text("preventive_maintenance.create_task") if translator.get_text("preventive_maintenance.create_task") != "preventive_maintenance.create_task" else "Feladat létrehozása",
                                        icon=ft.Icons.CHECK,
                                        on_click=submit_request,
                                        bgcolor=DesignSystem.PRIMARY,
                                    ),
                                ],
                            )
                            
                            try:
                                dialog_page.open(dialog)
                            except:
                                dialog_page.dialog = dialog
                                dialog.open = True
                                dialog_page.update()
                        
                        # Add maintenance request button
                        machine_details_items.append(ft.Container(height=DesignSystem.SPACING_3))
                        machine_details_items.append(ft.Divider(height=1, color=DesignSystem.BORDER_COLOR))
                        machine_details_items.append(ft.Container(height=DesignSystem.SPACING_2))
                        machine_details_items.append(
                            create_modern_button(
                                text=translator.get_text("preventive_maintenance.request_maintenance") if translator.get_text("preventive_maintenance.request_maintenance") != "preventive_maintenance.request_maintenance" else "Karbantartás igénylése",
                                icon=ft.Icons.BUILD,
                                on_click=lambda e, m=machine: open_maintenance_request_dialog(m),
                                bgcolor=DesignSystem.BLUE_500,
                                variant="filled",
                            )
                        )
                        
                        # Compatible parts section - simplified list with dialog
                        if compatible_parts:
                            def create_part_details_handler(part_instance, inv_level_instance):
                                """Create a closure for part details dialog handler"""
                                def handler(e):
                                    print(f"[PRODUCTION_LINE] Part details button clicked!")
                                    print(f"[PRODUCTION_LINE] Event: {e}, type: {type(e)}")
                                    print(f"[PRODUCTION_LINE] Part instance: {part_instance}, ID: {getattr(part_instance, 'id', 'NO_ID')}, Name: {getattr(part_instance, 'name', 'NO_NAME')}")
                                    print(f"[PRODUCTION_LINE] Inv level instance: {inv_level_instance}")
                                    try:
                                        open_part_details_dialog(part_instance, inv_level_instance)
                                    except Exception as ex:
                                        print(f"[PRODUCTION_LINE] ERROR in handler: {ex}")
                                        import traceback
                                        traceback.print_exc()
                                return handler
                            
                            def open_part_details_dialog(part, inv_level_dict_item):
                                """Open detailed dialog for part"""
                                print(f"[PRODUCTION_LINE] ====== open_part_details_dialog called ======")
                                print(f"[PRODUCTION_LINE] Part: {part}, ID: {getattr(part, 'id', 'NO_ID')}, Name: {getattr(part, 'name', 'NO_NAME')}")
                                print(f"[PRODUCTION_LINE] Inv level dict item: {inv_level_dict_item}")
                                
                                dialog_page = self.page if hasattr(self, 'page') and self.page else page
                                print(f"[PRODUCTION_LINE] Dialog page: {dialog_page}, type: {type(dialog_page)}")
                                
                                inv_level = inv_level_dict_item
                                stock_qty = inv_level.quantity_on_hand if inv_level else 0
                                stock_reserved = inv_level.quantity_reserved if inv_level else 0
                                stock_available = stock_qty - stock_reserved
                                bin_location = inv_level.bin_location if inv_level else None
                                
                                # Build detailed content for dialog
                                dialog_content_items = []
                                
                                # Part header
                                dialog_content_items.append(
                                    ft.Row([
                                        ft.Text(
                                            part.name,
                                            size=20,
                                            weight=ft.FontWeight.BOLD,
                                            color=DesignSystem.TEXT_PRIMARY,
                                            expand=True,
                                        ),
                                        create_vibrant_badge(
                                            text=part.sku,
                                            variant="blue",
                                            size=12,
                                        ) if part.sku else None,
                                    ], spacing=DesignSystem.SPACING_2)
                                )
                                dialog_content_items.append(ft.Container(height=DesignSystem.SPACING_3))
                                dialog_content_items.append(ft.Divider(height=1, color=DesignSystem.BORDER_COLOR))
                                dialog_content_items.append(ft.Container(height=DesignSystem.SPACING_3))
                                
                                # Basic information
                                basic_info_items = []
                                basic_info_items.append(
                                    ft.Text(
                                        "Alapinformációk",
                                        size=16,
                                        weight=ft.FontWeight.W_600,
                                        color=DesignSystem.TEXT_PRIMARY,
                                    )
                                )
                                basic_info_items.append(ft.Container(height=DesignSystem.SPACING_2))
                                
                                basic_grid = []
                                if part.category:
                                    basic_grid.append(ft.Column([
                                        ft.Text("Kategória:", size=13, weight=ft.FontWeight.W_500, color=DesignSystem.TEXT_SECONDARY),
                                        ft.Text(part.category, size=14, color=DesignSystem.TEXT_PRIMARY),
                                    ], spacing=2, expand=True))
                                if part.unit:
                                    basic_grid.append(ft.Column([
                                        ft.Text("Mértékegység:", size=13, weight=ft.FontWeight.W_500, color=DesignSystem.TEXT_SECONDARY),
                                        ft.Text(part.unit, size=14, color=DesignSystem.TEXT_PRIMARY),
                                    ], spacing=2, expand=True))
                                
                                if basic_grid:
                                    for i in range(0, len(basic_grid), 2):
                                        row_items = [item for item in basic_grid[i:i+2] if item is not None]
                                        if row_items:
                                            basic_info_items.append(ft.Row(row_items, spacing=DesignSystem.SPACING_4))
                                
                                if part.description:
                                    basic_info_items.append(ft.Container(height=DesignSystem.SPACING_2))
                                    basic_info_items.append(
                                        ft.Column([
                                            ft.Text("Leírás:", size=13, weight=ft.FontWeight.W_500, color=DesignSystem.TEXT_SECONDARY),
                                            ft.Text(part.description, size=14, color=DesignSystem.TEXT_PRIMARY),
                                        ], spacing=2)
                                    )
                                
                                dialog_content_items.append(ft.Column(basic_info_items, spacing=DesignSystem.SPACING_2))
                                dialog_content_items.append(ft.Container(height=DesignSystem.SPACING_4))
                                
                                # Stock information
                                stock_info_items = []
                                stock_info_items.append(
                                    ft.Text(
                                        "Készlet információk",
                                        size=16,
                                        weight=ft.FontWeight.W_600,
                                        color=DesignSystem.TEXT_PRIMARY,
                                    )
                                )
                                stock_info_items.append(ft.Container(height=DesignSystem.SPACING_2))
                                
                                stock_row1 = ft.Row([
                                    ft.Column([
                                        ft.Text("Raktáron:", size=13, weight=ft.FontWeight.W_500, color=DesignSystem.TEXT_SECONDARY),
                                        ft.Text(f"{stock_qty} {part.unit}", size=14, color=DesignSystem.TEXT_PRIMARY),
                                    ], expand=True),
                                    ft.Column([
                                        ft.Text("Foglalt:", size=13, weight=ft.FontWeight.W_500, color=DesignSystem.TEXT_SECONDARY),
                                        ft.Text(f"{stock_reserved} {part.unit}", size=14, color=DesignSystem.TEXT_PRIMARY),
                                    ], expand=True),
                                    ft.Column([
                                        ft.Text("Elérhető:", size=13, weight=ft.FontWeight.W_500, color=DesignSystem.TEXT_SECONDARY),
                                        ft.Text(f"{stock_available} {part.unit}", size=14, color=DesignSystem.TEXT_PRIMARY, weight=ft.FontWeight.W_600),
                                    ], expand=True),
                                ], spacing=DesignSystem.SPACING_4)
                                stock_info_items.append(stock_row1)
                                
                                if bin_location:
                                    stock_info_items.append(ft.Container(height=DesignSystem.SPACING_2))
                                    stock_info_items.append(
                                        ft.Text(
                                            f"Raktárhely: {bin_location}",
                                            size=13,
                                            color=DesignSystem.TEXT_SECONDARY,
                                        )
                                    )
                                
                                if part.safety_stock is not None and part.safety_stock > 0:
                                    stock_info_items.append(ft.Container(height=DesignSystem.SPACING_2))
                                    stock_info_items.append(
                                        ft.Row([
                                            ft.Text("Minimális készlet:", size=13, weight=ft.FontWeight.W_500, color=DesignSystem.TEXT_SECONDARY),
                                            ft.Text(f"{part.safety_stock} {part.unit}", size=13, color=DesignSystem.TEXT_PRIMARY),
                                            create_vibrant_badge(
                                                text="Alacsony készlet" if stock_qty <= part.safety_stock else "Rendben",
                                                variant="red" if stock_qty <= part.safety_stock else "emerald",
                                                size=11,
                                            ),
                                        ], spacing=DesignSystem.SPACING_2)
                                    )
                                
                                dialog_content_items.append(ft.Column(stock_info_items, spacing=DesignSystem.SPACING_2))
                                dialog_content_items.append(ft.Container(height=DesignSystem.SPACING_4))
                                
                                # Financial information
                                financial_items = []
                                financial_items.append(
                                    ft.Text(
                                        "Pénzügyi információk",
                                        size=16,
                                        weight=ft.FontWeight.W_600,
                                        color=DesignSystem.TEXT_PRIMARY,
                                    )
                                )
                                financial_items.append(ft.Container(height=DesignSystem.SPACING_2))
                                
                                financial_grid = []
                                financial_grid.append(ft.Column([
                                    ft.Text("Vételár (nettó):", size=13, weight=ft.FontWeight.W_500, color=DesignSystem.TEXT_SECONDARY),
                                    ft.Text(format_price(part.buy_price), size=14, color=DesignSystem.TEXT_PRIMARY),
                                ], spacing=2, expand=True))
                                
                                if part.sell_price:
                                    financial_grid.append(ft.Column([
                                        ft.Text("Eladási ár:", size=13, weight=ft.FontWeight.W_500, color=DesignSystem.TEXT_SECONDARY),
                                        ft.Text(format_price(part.sell_price), size=14, color=DesignSystem.TEXT_PRIMARY),
                                    ], spacing=2, expand=True))
                                
                                if part.reorder_quantity:
                                    financial_grid.append(ft.Column([
                                        ft.Text("Újrarendelési mennyiség:", size=13, weight=ft.FontWeight.W_500, color=DesignSystem.TEXT_SECONDARY),
                                        ft.Text(f"{part.reorder_quantity} {part.unit}", size=14, color=DesignSystem.TEXT_PRIMARY),
                                    ], spacing=2, expand=True))
                                
                                if financial_grid:
                                    for i in range(0, len(financial_grid), 2):
                                        row_items = [item for item in financial_grid[i:i+2] if item is not None]
                                        if row_items:
                                            financial_items.append(ft.Row(row_items, spacing=DesignSystem.SPACING_4))
                                
                                # Try to get supplier safely (it may be detached from session)
                                try:
                                    supplier = getattr(part, 'supplier', None)
                                    if supplier:
                                        # Try to get supplier name, handle detached instance
                                        try:
                                            supplier_name = supplier.name if hasattr(supplier, 'name') else str(supplier)
                                        except:
                                            # If supplier is detached, try to get from supplier_id
                                            supplier_id = getattr(part, 'supplier_id', None)
                                            if supplier_id:
                                                # Load supplier from new session
                                                from services import inventory_service
                                                from database.session_manager import SessionLocal
                                                try:
                                                    temp_session = SessionLocal()
                                                    from database.models import Supplier
                                                    supplier_obj = temp_session.query(Supplier).filter_by(id=supplier_id).first()
                                                    supplier_name = supplier_obj.name if supplier_obj else f"Supplier ID: {supplier_id}"
                                                    temp_session.close()
                                                except:
                                                    supplier_name = f"Supplier ID: {supplier_id}"
                                            else:
                                                supplier_name = "Ismeretlen beszállító"
                                        
                                        financial_items.append(ft.Container(height=DesignSystem.SPACING_2))
                                        financial_items.append(
                                            ft.Text(
                                                f"Beszállító: {supplier_name}",
                                                size=13,
                                                color=DesignSystem.TEXT_SECONDARY,
                                            )
                                        )
                                except Exception as supplier_err:
                                    print(f"[PRODUCTION_LINE] Error getting supplier: {supplier_err}")
                                    # Ignore supplier if we can't access it
                                
                                dialog_content_items.append(ft.Column(financial_items, spacing=DesignSystem.SPACING_2))
                                
                                # Filter None values
                                dialog_content_items = [item for item in dialog_content_items if item is not None]
                                
                                dialog = ft.AlertDialog(
                                    modal=True,
                                    title=ft.Row([
                                        ft.Icon(ft.Icons.INVENTORY_2, color=DesignSystem.BLUE_500, size=24),
                                        ft.Text(
                                            translator.get_text("inventory.part_details") if translator.get_text("inventory.part_details") != "inventory.part_details" else "Alkatrész részletek",
                                            size=18,
                                            weight=ft.FontWeight.BOLD
                                        )
                                    ]),
                                    content=ft.Container(
                                        content=ft.Column(dialog_content_items, spacing=DesignSystem.SPACING_2, scroll=ft.ScrollMode.AUTO),
                                        width=600,
                                        height=600,
                                    ),
                                    actions=[
                                        ft.TextButton(
                                            translator.get_text("common.buttons.close") if translator.get_text("common.buttons.close") != "common.buttons.close" else "Bezárás",
                                            on_click=lambda _: (setattr(dialog, 'open', False), dialog_page.update())
                                        ),
                                    ],
                                )
                                
                                print(f"[PRODUCTION_LINE] Attempting to open dialog...")
                                try:
                                    dialog_page.open(dialog)
                                    print(f"[PRODUCTION_LINE] Dialog opened successfully via dialog_page.open()")
                                except Exception as open_err:
                                    print(f"[PRODUCTION_LINE] Error with dialog_page.open(): {open_err}")
                                    import traceback
                                    traceback.print_exc()
                                    try:
                                        dialog_page.dialog = dialog
                                        dialog.open = True
                                        dialog_page.update()
                                        print(f"[PRODUCTION_LINE] Dialog opened successfully via dialog_page.dialog")
                                    except Exception as dialog_err:
                                        print(f"[PRODUCTION_LINE] Error with dialog_page.dialog: {dialog_err}")
                                        traceback.print_exc()
                            
                            # Simplified parts list - just name, SKU, stock, and button to view details
                            parts_list_items = []
                            for idx, part in enumerate(compatible_parts):
                                print(f"[PRODUCTION_LINE] Creating part list item {idx}: {part.name} (ID: {part.id})")
                                inv_level = inv_levels_dict.get(part.id)
                                stock_qty = inv_level.quantity_on_hand if inv_level else 0
                                
                                # Create handler for this specific part
                                part_handler = create_part_details_handler(part, inv_level)
                                print(f"[PRODUCTION_LINE] Created handler for part {part.name}: {part_handler}")
                                
                                info_button = create_modern_icon_button(
                                    icon=ft.Icons.INFO_OUTLINE if hasattr(ft.Icons, 'INFO_OUTLINE') else ft.Icons.INFO,
                                    tooltip=translator.get_text("common.buttons.view_details") if translator.get_text("common.buttons.view_details") != "common.buttons.view_details" else "Részletek",
                                    on_click=part_handler,
                                    color=DesignSystem.BLUE_500,
                                    vibrant=True,
                                    variant="blue",
                                )
                                print(f"[PRODUCTION_LINE] Created info button for part {part.name}: {info_button}, on_click: {getattr(info_button, 'on_click', 'NO_ON_CLICK')}")
                                
                                part_row_items = [
                                    ft.Column([
                                        ft.Text(
                                            part.name,
                                            size=14,
                                            weight=ft.FontWeight.W_600,
                                            color=DesignSystem.TEXT_PRIMARY,
                                        ),
                                        ft.Text(
                                            part.sku or "-",
                                            size=12,
                                            color=DesignSystem.TEXT_SECONDARY,
                                        ) if part.sku else None,
                                    ], spacing=2, expand=True),
                                    create_vibrant_badge(
                                        text=f"{stock_qty} {part.unit}",
                                        variant="emerald" if stock_qty > 0 else "gray",
                                        size=11,
                                    ),
                                    info_button,
                                ]
                                # Filter None values
                                part_row_items = [item for item in part_row_items if item is not None]
                                
                                parts_list_items.append(
                                    ft.Container(
                                        content=ft.Row(part_row_items, spacing=DesignSystem.SPACING_3, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                                        padding=ft.padding.symmetric(vertical=8, horizontal=12),
                                        bgcolor=DesignSystem.BG_SECONDARY,
                                        border_radius=DesignSystem.RADIUS_MD,
                                    )
                                )
                            
                            parts_list_column = ft.Column(parts_list_items, spacing=DesignSystem.SPACING_2)
                            
                            # Add parts section to machine details (will be in expansion tile)
                            parts_section_content = parts_list_column
                        else:
                            parts_section_content = None
                        
                        # Filter None values from machine_details_items before creating card
                        machine_details_items = [item for item in machine_details_items if item is not None]
                        
                        # Create expansion tile for machine with parts section
                        expansion_controls = []
                        if machine_details_items:
                            expansion_controls.append(
                                create_tailwind_card(
                                    content=ft.Column(machine_details_items, spacing=DesignSystem.SPACING_2),
                                    padding=DesignSystem.SPACING_4,
                                    elevation=0,
                                    accent_color=DesignSystem.PURPLE_500,
                                )
                            )
                        
                        if parts_section_content:
                            expansion_controls.append(ft.Container(height=DesignSystem.SPACING_2))
                            expansion_controls.append(
                                ft.Container(
                                    content=ft.Column([
                                        ft.Text(
                                            f"{translator.get_text('inventory.compatible_machines') if translator.get_text('inventory.compatible_machines') != 'inventory.compatible_machines' else 'Kompatibilis alkatrészek'}: {len(compatible_parts)}",
                                            size=14,
                                            weight=ft.FontWeight.W_600,
                                            color=DesignSystem.TEXT_PRIMARY,
                                        ),
                                        ft.Container(height=DesignSystem.SPACING_2),
                                        parts_section_content,
                                    ], spacing=DesignSystem.SPACING_2),
                                    padding=DesignSystem.SPACING_3,
                                )
                            )
                        
                        expansion_controls = [item for item in expansion_controls if item is not None]
                        
                        machine_expansion = ft.ExpansionTile(
                            title=ft.Text(
                                machine.name,
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=DesignSystem.TEXT_PRIMARY,
                            ),
                            subtitle=ft.Text(
                                f"{machine.model or ''} {machine.manufacturer or ''}".strip() or "-",
                                size=13,
                                color=DesignSystem.TEXT_SECONDARY,
                            ),
                            leading=ft.Icon(
                                ft.Icons.PRECISION_MANUFACTURING if hasattr(ft.Icons, 'PRECISION_MANUFACTURING') else ft.Icons.FACTORY,
                                size=28,
                                color=DesignSystem.PURPLE_500,
                            ),
                            controls=expansion_controls,
                            initially_expanded=False,
                        )
                        
                        machines_column_items.append(machine_expansion)
                
                machines_column = ft.Column(
                    machines_column_items,
                    spacing=DesignSystem.SPACING_3,
                    scroll=ft.ScrollMode.AUTO,
                    expand=True,
                )
                
                # Build Parts tab - collect all parts from all machines
                all_parts_set = set()
                for machine in machines:
                    compatible_parts = machine.id_compatible_parts if hasattr(machine, 'id_compatible_parts') else []
                    all_parts_set.update(compatible_parts)
                
                all_parts_list = list(all_parts_set)
                
                parts_tab_items = []
                if not all_parts_list:
                    parts_tab_items.append(
                        create_empty_state_card(
                            icon=ft.Icons.INVENTORY_2 if hasattr(ft.Icons, 'INVENTORY_2') else ft.Icons.INVENTORY,
                            title=translator.get_text("production_line.no_parts") if translator.get_text("production_line.no_parts") != "production_line.no_parts" else "Nincsenek alkatrészek",
                            icon_color=DesignSystem.GRAY_400,
                        )
                    )
                else:
                    # Use existing inventory levels dict
                    parts_list_items = []
                    for part in all_parts_list:
                        inv_level = inv_levels_dict.get(part.id)
                        stock_qty = inv_level.quantity_on_hand if inv_level else 0
                        
                        def create_part_details_handler_for_tab(part_instance, inv_level_instance):
                            """Create a closure for part details dialog handler"""
                            def handler(e):
                                try:
                                    open_part_details_dialog(part_instance, inv_level_instance)
                                except Exception as ex:
                                    logger.error(f"Error opening part details dialog: {ex}", exc_info=True)
                            return handler
                        
                        info_button = create_modern_icon_button(
                            icon=ft.Icons.INFO_OUTLINE if hasattr(ft.Icons, 'INFO_OUTLINE') else ft.Icons.INFO,
                            tooltip=translator.get_text("common.buttons.view_details") if translator.get_text("common.buttons.view_details") != "common.buttons.view_details" else "Részletek",
                            on_click=create_part_details_handler_for_tab(part, inv_level),
                            color=DesignSystem.BLUE_500,
                            vibrant=True,
                            variant="blue",
                        )
                        
                        part_row_items = [
                            ft.Column([
                                ft.Text(
                                    part.name,
                                    size=14,
                                    weight=ft.FontWeight.W_600,
                                    color=DesignSystem.TEXT_PRIMARY,
                                ),
                                ft.Text(
                                    part.sku or "-",
                                    size=12,
                                    color=DesignSystem.TEXT_SECONDARY,
                                ) if part.sku else None,
                            ], spacing=2, expand=True),
                            create_vibrant_badge(
                                text=f"{stock_qty} {part.unit}",
                                variant="emerald" if stock_qty > 0 else "gray",
                                size=11,
                            ),
                            info_button,
                        ]
                        part_row_items = [item for item in part_row_items if item is not None]
                        
                        parts_list_items.append(
                            create_tailwind_card(
                                content=ft.Row(part_row_items, spacing=DesignSystem.SPACING_3, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                                padding=DesignSystem.SPACING_3,
                                elevation=0,
                            )
                        )
                    
                    parts_tab_items = parts_list_items
                
                parts_tab_column = ft.Column(
                    parts_tab_items,
                    spacing=DesignSystem.SPACING_2,
                    scroll=ft.ScrollMode.AUTO,
                    expand=True,
                )
                
                # Build PM Tasks tab - get PM tasks for all machines in this production line
                machine_ids = [m.id for m in machines]
                pm_tasks_tab_items = []
                
                if not machine_ids:
                    pm_tasks_tab_items.append(
                        create_empty_state_card(
                            icon=ft.Icons.BUILD if hasattr(ft.Icons, 'BUILD') else ft.Icons.SETTINGS,
                            title=translator.get_text("production_line.no_pm_tasks") if translator.get_text("production_line.no_pm_tasks") != "production_line.no_pm_tasks" else "Nincsenek karbantartási feladatok",
                            icon_color=DesignSystem.GRAY_400,
                        )
                    )
                else:
                    # Get PM tasks for all machines
                    all_pm_tasks = []
                    for machine_id in machine_ids:
                        machine_pm_tasks = pm_service.list_pm_tasks(machine_id=machine_id, session=session)
                        all_pm_tasks.extend(machine_pm_tasks)
                    
                    if not all_pm_tasks:
                        pm_tasks_tab_items.append(
                            create_empty_state_card(
                                icon=ft.Icons.BUILD if hasattr(ft.Icons, 'BUILD') else ft.Icons.SETTINGS,
                                title=translator.get_text("production_line.no_pm_tasks") if translator.get_text("production_line.no_pm_tasks") != "production_line.no_pm_tasks" else "Nincsenek karbantartási feladatok",
                                icon_color=DesignSystem.GRAY_400,
                            )
                        )
                    else:
                        # Create cards for each PM task
                        for pm_task in all_pm_tasks:
                            machine_name = pm_task.machine.name if pm_task.machine else "-"
                            assigned_user_name = pm_task.assigned_user.full_name if pm_task.assigned_user else (translator.get_text("preventive_maintenance.global") if translator.get_text("preventive_maintenance.global") != "preventive_maintenance.global" else "Globális")
                            
                            status_badge = create_vibrant_badge(
                                text=pm_task.status or "pending",
                                variant="emerald" if pm_task.status == "completed" else ("orange" if pm_task.status in ["due_today", "overdue"] else "blue"),
                                size=11,
                            )
                            
                            pm_task_card_items = [
                                ft.Row([
                                    ft.Text(
                                        pm_task.task_name,
                                        size=16,
                                        weight=ft.FontWeight.BOLD,
                                        color=DesignSystem.TEXT_PRIMARY,
                                        expand=True,
                                    ),
                                    status_badge,
                                ], spacing=DesignSystem.SPACING_2),
                                ft.Container(height=DesignSystem.SPACING_2),
                                ft.Text(
                                    f"{translator.get_text('assets.machine') if translator.get_text('assets.machine') != 'assets.machine' else 'Gép'}: {machine_name}",
                                    size=13,
                                    color=DesignSystem.TEXT_SECONDARY,
                                ),
                                ft.Text(
                                    f"{translator.get_text('preventive_maintenance.assigned_user') if translator.get_text('preventive_maintenance.assigned_user') != 'preventive_maintenance.assigned_user' else 'Hozzárendelve'}: {assigned_user_name}",
                                    size=13,
                                    color=DesignSystem.TEXT_SECONDARY,
                                ),
                            ]
                            
                            if pm_task.next_due_date:
                                pm_task_card_items.append(
                                    ft.Text(
                                        f"{translator.get_text('preventive_maintenance.next_due_date') if translator.get_text('preventive_maintenance.next_due_date') != 'preventive_maintenance.next_due_date' else 'Következő esedékesség'}: {pm_task.next_due_date.strftime('%Y-%m-%d')}",
                                        size=13,
                                        color=DesignSystem.TEXT_SECONDARY,
                                    )
                                )
                            
                            pm_tasks_tab_items.append(
                                create_tailwind_card(
                                    content=ft.Column(pm_task_card_items, spacing=DesignSystem.SPACING_2),
                                    padding=DesignSystem.SPACING_3,
                                    elevation=0,
                                )
                            )
                
                pm_tasks_tab_column = ft.Column(
                    pm_tasks_tab_items,
                    spacing=DesignSystem.SPACING_2,
                    scroll=ft.ScrollMode.AUTO,
                    expand=True,
                )
                
                # Create tabs
                tabs = ft.Tabs(
                    selected_index=0,
                    tabs=[
                        ft.Tab(
                            text=translator.get_text("production_line.tab_machines") if translator.get_text("production_line.tab_machines") != "production_line.tab_machines" else "Gépek",
                            icon=ft.Icons.PRECISION_MANUFACTURING if hasattr(ft.Icons, 'PRECISION_MANUFACTURING') else ft.Icons.FACTORY,
                            content=ft.Container(
                                content=machines_column,
                                padding=DesignSystem.SPACING_2,
                                expand=True,
                            ),
                        ),
                        ft.Tab(
                            text=translator.get_text("production_line.tab_parts") if translator.get_text("production_line.tab_parts") != "production_line.tab_parts" else "Alkatrészek",
                            icon=ft.Icons.INVENTORY_2 if hasattr(ft.Icons, 'INVENTORY_2') else ft.Icons.INVENTORY,
                            content=ft.Container(
                                content=parts_tab_column,
                                padding=DesignSystem.SPACING_2,
                                expand=True,
                            ),
                        ),
                        ft.Tab(
                            text=translator.get_text("production_line.tab_pm_tasks") if translator.get_text("production_line.tab_pm_tasks") != "production_line.tab_pm_tasks" else "Karbantartási feladatok",
                            icon=ft.Icons.BUILD if hasattr(ft.Icons, 'BUILD') else ft.Icons.SETTINGS,
                            content=ft.Container(
                                content=pm_tasks_tab_column,
                                padding=DesignSystem.SPACING_2,
                                expand=True,
                            ),
                        ),
                    ],
                    expand=True,
                )
                
                # Combine header and tabs
                details_content = ft.Column([
                    header_content,
                    ft.Container(height=DesignSystem.SPACING_4),
                    tabs,
                ], spacing=DesignSystem.SPACING_2, scroll=ft.ScrollMode.AUTO, expand=True)
                
                details_container.content = details_content
                details_container.padding = 20
                
                # Update the page to reflect changes
                page_ref = self.page if hasattr(self, 'page') and self.page else page
                page_ref.update()
                
            except Exception as e:
                logger.error(f"Error loading production line details: {e}", exc_info=True)
                details_container.content = create_empty_state_card(
                    icon=ft.Icons.ERROR if hasattr(ft.Icons, 'ERROR') else ft.Icons.WARNING,
                    title=translator.get_text("common.error") if translator.get_text("common.error") != "common.error" else "Hiba",
                    description=str(e),
                )
                page_ref = self.page if hasattr(self, 'page') and self.page else page
                page_ref.update()
            finally:
                session.close()
            
            refresh_production_lines_list()
        
        def navigate_to_assets(production_line_id: int):
            """Navigate to assets screen filtered by production line"""
            from ui.app import state
            state.view = "assets"
            state._production_line_filter = production_line_id
            page_ref = self.page if hasattr(self, 'page') and self.page else page
            if hasattr(page_ref, '_render_callback'):
                page_ref._render_callback()
        
        def open_create_dialog():
            """Open dialog to create a new production line"""
            print("[PRODUCTION_LINE] ========================================")
            print("[PRODUCTION_LINE] open_create_dialog() called")
            logger.debug("open_create_dialog() called")
            try:
                dialog_page = self.page if hasattr(self, 'page') and self.page else page
                print(f"[PRODUCTION_LINE] dialog_page: {dialog_page}, type: {type(dialog_page)}")
                print(f"[PRODUCTION_LINE] hasattr(self, 'page'): {hasattr(self, 'page')}")
                if hasattr(self, 'page'):
                    print(f"[PRODUCTION_LINE] self.page: {self.page}, type: {type(self.page)}")
                print(f"[PRODUCTION_LINE] page parameter: {page}, type: {type(page)}")
            except Exception as e:
                print(f"[PRODUCTION_LINE] Error getting dialog_page: {e}")
                import traceback
                traceback.print_exc()
                return
            
            print("[PRODUCTION_LINE] Creating form fields...")
            try:
                print("[PRODUCTION_LINE] Creating name_field...")
                name_label = translator.get_text("production_line.name") if translator.get_text("production_line.name") != "production_line.name" else "Név"
                print(f"[PRODUCTION_LINE] name_label: {name_label}")
                name_field = create_modern_text_field(
                    label=name_label,
                )
                print(f"[PRODUCTION_LINE] name_field created: {name_field}, type: {type(name_field)}")
            except Exception as e:
                print(f"[PRODUCTION_LINE] ERROR creating name_field: {e}")
                import traceback
                traceback.print_exc()
                return
            
            try:
                print("[PRODUCTION_LINE] Creating description_field...")
                description_label = translator.get_text("production_line.description") if translator.get_text("production_line.description") != "production_line.description" else "Leírás"
                print(f"[PRODUCTION_LINE] description_label: {description_label}")
                description_field = create_modern_text_field(
                    label=description_label,
                    multiline=True,
                    max_lines=5,
                )
                print(f"[PRODUCTION_LINE] description_field created: {description_field}, type: {type(description_field)}")
            except Exception as e:
                print(f"[PRODUCTION_LINE] ERROR creating description_field: {e}")
                import traceback
                traceback.print_exc()
                return
            
            try:
                print("[PRODUCTION_LINE] Creating location_field...")
                location_field = create_modern_text_field(
                    label=translator.get_text("production_line.location") if translator.get_text("production_line.location") != "production_line.location" else "Helyszín",
                )
                print(f"[PRODUCTION_LINE] location_field created: {location_field}, type: {type(location_field)}")
            except Exception as e:
                print(f"[PRODUCTION_LINE] ERROR creating location_field: {e}")
                import traceback
                traceback.print_exc()
                return
            
            try:
                print("[PRODUCTION_LINE] Creating code_field...")
                code_field = create_modern_text_field(
                    label=translator.get_text("production_line.code") if translator.get_text("production_line.code") != "production_line.code" else "Kód",
                )
                print(f"[PRODUCTION_LINE] code_field created: {code_field}, type: {type(code_field)}")
            except Exception as e:
                print(f"[PRODUCTION_LINE] ERROR creating code_field: {e}")
                import traceback
                traceback.print_exc()
                return
            
            try:
                print("[PRODUCTION_LINE] Creating status_field...")
                status_options = [
                    ft.dropdown.Option(
                        "Active",
                        translator.get_text("production_line.status_active") if translator.get_text("production_line.status_active") != "production_line.status_active" else "Aktív"
                    ),
                    ft.dropdown.Option(
                        "Inactive",
                        translator.get_text("production_line.status_inactive") if translator.get_text("production_line.status_inactive") != "production_line.status_inactive" else "Inaktív"
                    ),
                    ft.dropdown.Option(
                        "Maintenance",
                        translator.get_text("production_line.status_maintenance") if translator.get_text("production_line.status_maintenance") != "production_line.status_maintenance" else "Karbantartás"
                    ),
                ]
                status_field = create_modern_dropdown(
                    label=translator.get_text("production_line.status") if translator.get_text("production_line.status") != "production_line.status" else "Státusz",
                    options=status_options,
                    value="Active",
                )
                print(f"[PRODUCTION_LINE] status_field created: {status_field}, type: {type(status_field)}")
            except Exception as e:
                print(f"[PRODUCTION_LINE] ERROR creating status_field: {e}")
                import traceback
                traceback.print_exc()
                return
            
            try:
                print("[PRODUCTION_LINE] Creating capacity_field...")
                capacity_field = create_modern_text_field(
                    label=translator.get_text("production_line.capacity") if translator.get_text("production_line.capacity") != "production_line.capacity" else "Kapacitás",
                )
                print(f"[PRODUCTION_LINE] capacity_field created: {capacity_field}, type: {type(capacity_field)}")
            except Exception as e:
                print(f"[PRODUCTION_LINE] ERROR creating capacity_field: {e}")
                import traceback
                traceback.print_exc()
                return
            
            try:
                print("[PRODUCTION_LINE] Creating responsible_person_field...")
                responsible_person_field = create_modern_text_field(
                    label=translator.get_text("production_line.responsible_person") if translator.get_text("production_line.responsible_person") != "production_line.responsible_person" else "Felelős személy",
                )
                print(f"[PRODUCTION_LINE] responsible_person_field created: {responsible_person_field}, type: {type(responsible_person_field)}")
            except Exception as e:
                print(f"[PRODUCTION_LINE] ERROR creating responsible_person_field: {e}")
                import traceback
                traceback.print_exc()
                return
            
            try:
                print("[PRODUCTION_LINE] Creating commission_date_field...")
                commission_date_row, commission_date_field = create_modern_date_field(
                    label=translator.get_text("production_line.commission_date") if translator.get_text("production_line.commission_date") != "production_line.commission_date" else "Üzembe helyezési dátum",
                    page=dialog_page,
                )
                print(f"[PRODUCTION_LINE] commission_date_field created: {commission_date_field}, type: {type(commission_date_field)}")
            except Exception as e:
                print(f"[PRODUCTION_LINE] ERROR creating commission_date_field: {e}")
                import traceback
                traceback.print_exc()
                return
            
            try:
                print("[PRODUCTION_LINE] Creating notes_field...")
                notes_field = create_modern_text_field(
                    label=translator.get_text("production_line.notes") if translator.get_text("production_line.notes") != "production_line.notes" else "Jegyzetek",
                    multiline=True,
                    max_lines=4,
                )
                print(f"[PRODUCTION_LINE] notes_field created: {notes_field}, type: {type(notes_field)}")
            except Exception as e:
                print(f"[PRODUCTION_LINE] ERROR creating notes_field: {e}")
                import traceback
                traceback.print_exc()
                return
            
            print("[PRODUCTION_LINE] All form fields created successfully")
            
            # Create dialog first (will be referenced in submit_create)
            print("[PRODUCTION_LINE] Creating AlertDialog object (before submit_create)...")
            dialog = ft.AlertDialog(
                modal=True,
                title=ft.Row([
                    ft.Icon(ft.Icons.ADD, color=DesignSystem.PRIMARY, size=24),
                    ft.Text(translator.get_text("production_line.create") if translator.get_text("production_line.create") != "production_line.create" else "Új termelési sor", size=20, weight=ft.FontWeight.BOLD)
                ]),
                content=ft.Container(
                    content=ft.Column([
                        ft.Text(
                            translator.get_text("production_line.basic_information") if translator.get_text("production_line.basic_information") != "production_line.basic_information" else "Alapinformációk",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=DesignSystem.PRIMARY,
                        ),
                        name_field,
                        ft.Row([
                            code_field,
                            status_field,
                        ], spacing=DesignSystem.SPACING_2),
                        location_field,
                        ft.Divider(height=1, color=DesignSystem.BORDER_COLOR),
                        ft.Text(
                            translator.get_text("production_line.description_label") if translator.get_text("production_line.description_label") != "production_line.description_label" else "Leírás",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=DesignSystem.PRIMARY,
                        ),
                        description_field,
                        ft.Divider(height=1, color=DesignSystem.BORDER_COLOR),
                        ft.Text(
                            translator.get_text("production_line.details") if translator.get_text("production_line.details") != "production_line.details" else "Részletek",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=DesignSystem.PRIMARY,
                        ),
                        ft.Row([
                            capacity_field,
                            responsible_person_field,
                        ], spacing=DesignSystem.SPACING_2),
                        commission_date_row,
                        ft.Divider(height=1, color=DesignSystem.BORDER_COLOR),
                        ft.Text(
                            translator.get_text("production_line.notes_label") if translator.get_text("production_line.notes_label") != "production_line.notes_label" else "Jegyzetek",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=DesignSystem.PRIMARY,
                        ),
                        notes_field,
                    ], spacing=DesignSystem.SPACING_3, tight=True, scroll=ft.ScrollMode.AUTO),
                    width=700,
                    height=700,
                ),
                actions=[],  # Will be set after submit_create is defined
            )
            print(f"[PRODUCTION_LINE] Dialog created: {dialog}, type: {type(dialog)}")
            
            # Flag to prevent double submission
            _submitting = {"value": False}
            
            def submit_create(e):
                # Prevent double submission
                if _submitting["value"]:
                    print("[PRODUCTION_LINE] submit_create() already in progress, ignoring duplicate call")
                    return
                
                print("[PRODUCTION_LINE] submit_create() called")
                print(f"[PRODUCTION_LINE] Event: {e}, type: {type(e)}")
                _submitting["value"] = True
                try:
                    print(f"[PRODUCTION_LINE] name_field.value: {name_field.value}")
                    if not name_field.value:
                        error_msg = translator.get_text("common.messages.required_field") + ": " + translator.get_text("production_line.name")
                        print(f"[PRODUCTION_LINE] Validation error: {error_msg}")
                        raise ValueError(error_msg)
                    
                    print("[PRODUCTION_LINE] Calling asset_service.create_production_line()...")
                    # Parse commission_date if provided
                    commission_date = None
                    if commission_date_field.value:
                        try:
                            commission_date = datetime.strptime(commission_date_field.value, "%Y-%m-%d")
                        except (ValueError, TypeError):
                            print(f"[PRODUCTION_LINE] Warning: Invalid commission_date format: {commission_date_field.value}")
                    
                    asset_service.create_production_line(
                        name=name_field.value,
                        code=code_field.value if code_field.value else None,
                        description=description_field.value if description_field.value else None,
                        location=location_field.value if location_field.value else None,
                        status=status_field.value if status_field.value else "Active",
                        capacity=capacity_field.value if capacity_field.value else None,
                        responsible_person=responsible_person_field.value if responsible_person_field.value else None,
                        commission_date=commission_date,
                        notes=notes_field.value if notes_field.value else None,
                    )
                    print("[PRODUCTION_LINE] Production line created successfully")
                    
                    # Close dialog with fallback
                    print("[PRODUCTION_LINE] Attempting to close dialog...")
                    try:
                        dialog_page.close(dialog)
                        print("[PRODUCTION_LINE] Dialog closed using dialog_page.close()")
                    except AttributeError as ae:
                        print(f"[PRODUCTION_LINE] AttributeError closing dialog: {ae}")
                        dialog.open = False
                        dialog_page.update()
                        print("[PRODUCTION_LINE] Dialog closed using dialog.open = False")
                    except Exception as close_exc:
                        print(f"[PRODUCTION_LINE] Exception closing dialog: {close_exc}")
                        import traceback
                        traceback.print_exc()
                        dialog.open = False
                        dialog_page.update()
                        print("[PRODUCTION_LINE] Dialog closed using dialog.open = False (fallback)")
                    
                    print("[PRODUCTION_LINE] Refreshing production lines list...")
                    refresh_production_lines_list()
                    
                    print("[PRODUCTION_LINE] Showing success message...")
                    dialog_page.snack_bar = ft.SnackBar(
                        content=ft.Text(translator.get_text("production_line.created_success") if translator.get_text("production_line.created_success") != "production_line.created_success" else "Termelési sor létrehozva"),
                        bgcolor=DesignSystem.SUCCESS,
                    )
                    dialog_page.snack_bar.open = True
                    dialog_page.update()
                    print("[PRODUCTION_LINE] Success message shown")
                except Exception as exc:
                    print(f"[PRODUCTION_LINE] ERROR in submit_create: {exc}")
                    import traceback
                    traceback.print_exc()
                    dialog_page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"{translator.get_text('common.error')}: {exc}"),
                        bgcolor=DesignSystem.ERROR,
                    )
                    dialog_page.snack_bar.open = True
                    dialog_page.update()
                    print("[PRODUCTION_LINE] Error message shown")
                finally:
                    _submitting["value"] = False
            
            # Set dialog actions now that submit_create is defined
            print("[PRODUCTION_LINE] Setting dialog actions...")
            dialog.actions = [
                ft.TextButton(
                    translator.get_text("common.buttons.cancel"),
                    on_click=lambda _: setattr(dialog, 'open', False) or dialog_page.update()
                ),
                ft.ElevatedButton(
                    translator.get_text("common.buttons.save"),
                    icon=ft.Icons.SAVE,
                    on_click=submit_create,
                    bgcolor=DesignSystem.PRIMARY,
                    color="#FFFFFF",
                ),
            ]
            print(f"[PRODUCTION_LINE] Dialog actions set: {len(dialog.actions)} actions")
            
            print("[PRODUCTION_LINE] ====== Attempting to open dialog ======")
            print(f"[PRODUCTION_LINE] dialog_page: {dialog_page}")
            print(f"[PRODUCTION_LINE] dialog_page type: {type(dialog_page)}")
            print(f"[PRODUCTION_LINE] hasattr(dialog_page, 'open'): {hasattr(dialog_page, 'open')}")
            print(f"[PRODUCTION_LINE] hasattr(dialog_page, 'dialog'): {hasattr(dialog_page, 'dialog')}")
            print(f"[PRODUCTION_LINE] dialog: {dialog}")
            print(f"[PRODUCTION_LINE] dialog type: {type(dialog)}")
            print(f"[PRODUCTION_LINE] dialog.open (before): {getattr(dialog, 'open', 'NO_OPEN_ATTR')}")
            
            try:
                print("[PRODUCTION_LINE] Calling dialog_page.open(dialog)...")
                dialog_page.open(dialog)
                print(f"[PRODUCTION_LINE] dialog_page.open() succeeded")
                print(f"[PRODUCTION_LINE] dialog.open (after): {getattr(dialog, 'open', 'NO_OPEN_ATTR')}")
            except AttributeError as ae:
                print(f"[PRODUCTION_LINE] AttributeError: {ae}")
                import traceback
                traceback.print_exc()
                print("[PRODUCTION_LINE] Using fallback: dialog_page.dialog = dialog, dialog.open = True")
                try:
                    dialog_page.dialog = dialog
                    dialog.open = True
                    dialog_page.update()
                    print(f"[PRODUCTION_LINE] Fallback succeeded, dialog.open={dialog.open}")
                except Exception as fallback_exc:
                    print(f"[PRODUCTION_LINE] Fallback also failed: {fallback_exc}")
                    import traceback
                    traceback.print_exc()
            except Exception as open_exc:
                print(f"[PRODUCTION_LINE] Exception opening dialog: {open_exc}")
                import traceback
                traceback.print_exc()
                print("[PRODUCTION_LINE] Using fallback: dialog_page.dialog = dialog, dialog.open = True")
                try:
                    dialog_page.dialog = dialog
                    dialog.open = True
                    dialog_page.update()
                    print(f"[PRODUCTION_LINE] Fallback succeeded, dialog.open={dialog.open}")
                except Exception as fallback_exc:
                    print(f"[PRODUCTION_LINE] Fallback also failed: {fallback_exc}")
                    import traceback
                    traceback.print_exc()
            print("[PRODUCTION_LINE] ====== Finished opening dialog ======")
            logger.debug("Dialog opening process completed")
            print("[PRODUCTION_LINE] ========================================")
        
        def open_edit_dialog(production_line_id: int):
            """Open dialog to edit a production line"""
            dialog_page = self.page if hasattr(self, 'page') and self.page else page
            
            session = SessionLocal()
            try:
                production_lines = asset_service.list_production_lines(session)
                production_line = next((pl for pl in production_lines if pl.id == production_line_id), None)
                
                if not production_line:
                    return
                
                name_field = create_modern_text_field(
                    label=translator.get_text("production_line.name") if translator.get_text("production_line.name") != "production_line.name" else "Név",
                    value=production_line.name,
                )
                code_field = create_modern_text_field(
                    label=translator.get_text("production_line.code") if translator.get_text("production_line.code") != "production_line.code" else "Kód",
                    value=production_line.code or "",
                )
                description_field = create_modern_text_field(
                    label=translator.get_text("production_line.description") if translator.get_text("production_line.description") != "production_line.description" else "Leírás",
                    value=production_line.description or "",
                    multiline=True,
                    max_lines=5,
                )
                location_field = create_modern_text_field(
                    label=translator.get_text("production_line.location") if translator.get_text("production_line.location") != "production_line.location" else "Helyszín",
                    value=production_line.location or "",
                )
                status_options = [
                    ft.dropdown.Option(
                        "Active",
                        translator.get_text("production_line.status_active") if translator.get_text("production_line.status_active") != "production_line.status_active" else "Aktív"
                    ),
                    ft.dropdown.Option(
                        "Inactive",
                        translator.get_text("production_line.status_inactive") if translator.get_text("production_line.status_inactive") != "production_line.status_inactive" else "Inaktív"
                    ),
                    ft.dropdown.Option(
                        "Maintenance",
                        translator.get_text("production_line.status_maintenance") if translator.get_text("production_line.status_maintenance") != "production_line.status_maintenance" else "Karbantartás"
                    ),
                ]
                status_field = create_modern_dropdown(
                    label=translator.get_text("production_line.status") if translator.get_text("production_line.status") != "production_line.status" else "Státusz",
                    options=status_options,
                    value=production_line.status or "Active",
                )
                capacity_field = create_modern_text_field(
                    label=translator.get_text("production_line.capacity") if translator.get_text("production_line.capacity") != "production_line.capacity" else "Kapacitás",
                    value=production_line.capacity or "",
                )
                responsible_person_field = create_modern_text_field(
                    label=translator.get_text("production_line.responsible_person") if translator.get_text("production_line.responsible_person") != "production_line.responsible_person" else "Felelős személy",
                    value=production_line.responsible_person or "",
                )
                commission_date_value = None
                if production_line.commission_date:
                    commission_date_value = production_line.commission_date.strftime("%Y-%m-%d")
                commission_date_row, commission_date_field = create_modern_date_field(
                    label=translator.get_text("production_line.commission_date") if translator.get_text("production_line.commission_date") != "production_line.commission_date" else "Üzembe helyezési dátum",
                    value=commission_date_value,
                    page=dialog_page,
                )
                notes_field = create_modern_text_field(
                    label=translator.get_text("production_line.notes") if translator.get_text("production_line.notes") != "production_line.notes" else "Jegyzetek",
                    value=production_line.notes or "",
                    multiline=True,
                    max_lines=4,
                )
                
                def submit_edit(e):
                    try:
                        if not name_field.value:
                            raise ValueError(translator.get_text("common.messages.required_field") + ": " + translator.get_text("production_line.name"))
                        
                        # Parse commission_date if provided
                        commission_date = None
                        if commission_date_field.value:
                            try:
                                commission_date = datetime.strptime(commission_date_field.value, "%Y-%m-%d")
                            except (ValueError, TypeError):
                                pass
                        
                        asset_service.update_production_line(
                            production_line_id=production_line_id,
                            name=name_field.value,
                            code=code_field.value if code_field.value else None,
                            description=description_field.value if description_field.value else None,
                            location=location_field.value if location_field.value else None,
                            status=status_field.value if status_field.value else "Active",
                            capacity=capacity_field.value if capacity_field.value else None,
                            responsible_person=responsible_person_field.value if responsible_person_field.value else None,
                            commission_date=commission_date,
                            notes=notes_field.value if notes_field.value else None,
                        )
                        
                        # Close dialog with fallback
                        try:
                            dialog_page.close(dialog)
                        except (AttributeError, Exception):
                            dialog.open = False
                            dialog_page.update()
                        
                        refresh_production_lines_list()
                        select_production_line(production_line_id)
                        
                        dialog_page.snack_bar = ft.SnackBar(
                            content=ft.Text(translator.get_text("production_line.updated_success") if translator.get_text("production_line.updated_success") != "production_line.updated_success" else "Termelési sor frissítve"),
                            bgcolor=DesignSystem.SUCCESS,
                        )
                        dialog_page.snack_bar.open = True
                        dialog_page.update()
                    except Exception as exc:
                        dialog_page.snack_bar = ft.SnackBar(
                            content=ft.Text(f"{translator.get_text('common.error')}: {exc}"),
                            bgcolor=DesignSystem.ERROR,
                        )
                        dialog_page.snack_bar.open = True
                        dialog_page.update()
                
                dialog = ft.AlertDialog(
                    modal=True,
                    title=ft.Row([
                        ft.Icon(ft.Icons.EDIT, color=DesignSystem.PRIMARY, size=24),
                        ft.Text(translator.get_text("production_line.edit") if translator.get_text("production_line.edit") != "production_line.edit" else "Termelési sor szerkesztése", size=20, weight=ft.FontWeight.BOLD)
                    ]),
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text(
                                translator.get_text("production_line.basic_information") if translator.get_text("production_line.basic_information") != "production_line.basic_information" else "Alapinformációk",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=DesignSystem.PRIMARY,
                            ),
                            name_field,
                            ft.Row([
                                code_field,
                                status_field,
                            ], spacing=DesignSystem.SPACING_2),
                            location_field,
                            ft.Divider(height=1, color=DesignSystem.BORDER_COLOR),
                            ft.Text(
                                translator.get_text("production_line.description_label") if translator.get_text("production_line.description_label") != "production_line.description_label" else "Leírás",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=DesignSystem.PRIMARY,
                            ),
                            description_field,
                            ft.Divider(height=1, color=DesignSystem.BORDER_COLOR),
                            ft.Text(
                                translator.get_text("production_line.details") if translator.get_text("production_line.details") != "production_line.details" else "Részletek",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=DesignSystem.PRIMARY,
                            ),
                            ft.Row([
                                capacity_field,
                                responsible_person_field,
                            ], spacing=DesignSystem.SPACING_2),
                            commission_date_row,
                            ft.Divider(height=1, color=DesignSystem.BORDER_COLOR),
                            ft.Text(
                                translator.get_text("production_line.notes_label") if translator.get_text("production_line.notes_label") != "production_line.notes_label" else "Jegyzetek",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=DesignSystem.PRIMARY,
                            ),
                            notes_field,
                        ], spacing=DesignSystem.SPACING_3, tight=True, scroll=ft.ScrollMode.AUTO),
                        width=700,
                        height=700,
                    ),
                    actions=[
                        ft.TextButton(
                            translator.get_text("common.buttons.cancel"),
                            on_click=lambda _: setattr(dialog, 'open', False) or dialog_page.update()
                        ),
                        ft.ElevatedButton(
                            translator.get_text("common.buttons.save"),
                            icon=ft.Icons.SAVE,
                            on_click=submit_edit,
                            bgcolor=DesignSystem.PRIMARY,
                            color="#FFFFFF",
                        ),
                    ],
                )
                
                dialog_page.open(dialog)
            finally:
                session.close()
        
        def open_delete_dialog(production_line_id: int):
            """Open dialog to delete a production line"""
            dialog_page = self.page if hasattr(self, 'page') and self.page else page
            
            session = SessionLocal()
            try:
                production_lines = asset_service.list_production_lines(session)
                production_line = next((pl for pl in production_lines if pl.id == production_line_id), None)
                
                if not production_line:
                    return
                
                machine_count = session.query(Machine).filter_by(production_line_id=production_line_id).count()
                
                def confirm_delete(e):
                    try:
                        asset_service.delete_production_line(production_line_id)
                        # Close dialog with fallback
                        try:
                            dialog_page.close(dialog)
                        except (AttributeError, Exception):
                            dialog.open = False
                            dialog_page.update()
                        selected_production_line_id_ref["value"] = None
                        details_container.content = ft.Column(
                            controls=[
                                ft.Text(
                                    translator.get_text("production_line.select_line") if translator.get_text("production_line.select_line") != "production_line.select_line" else "Válassz termelési sort",
                                    size=14,
                                    color=DesignSystem.TEXT_SECONDARY,
                                    italic=True,
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=20,
                        )
                        details_container.padding = 20
                        refresh_production_lines_list()
                        
                        dialog_page.snack_bar = ft.SnackBar(
                            content=ft.Text(translator.get_text("production_line.deleted_success") if translator.get_text("production_line.deleted_success") != "production_line.deleted_success" else "Termelési sor törölve"),
                            bgcolor=DesignSystem.SUCCESS,
                        )
                        dialog_page.snack_bar.open = True
                        dialog_page.update()
                    except Exception as exc:
                        dialog_page.snack_bar = ft.SnackBar(
                            content=ft.Text(f"{translator.get_text('common.error')}: {exc}"),
                            bgcolor=DesignSystem.ERROR,
                        )
                        dialog_page.snack_bar.open = True
                        dialog_page.update()
                
                warning_text = ""
                if machine_count > 0:
                    warning_text = translator.get_text("production_line.cannot_delete_has_machines") if translator.get_text("production_line.cannot_delete_has_machines") != "production_line.cannot_delete_has_machines" else f"Ez a termelési sor nem törölhető, mert {machine_count} gép tartozik hozzá."
                else:
                    warning_text = translator.get_text("production_line.delete_confirm") if translator.get_text("production_line.delete_confirm") != "production_line.delete_confirm" else f"Biztosan törölni szeretnéd a '{production_line.name}' termelési sort?"
                
                dialog = ft.AlertDialog(
                    modal=True,
                    title=ft.Row([
                        ft.Icon(ft.Icons.DELETE, color=DesignSystem.ERROR, size=24),
                        ft.Text(translator.get_text("production_line.delete") if translator.get_text("production_line.delete") != "production_line.delete" else "Termelési sor törlése", size=20, weight=ft.FontWeight.BOLD)
                    ]),
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text(warning_text, size=14, color=DesignSystem.TEXT_PRIMARY),
                        ], spacing=DesignSystem.SPACING_3, tight=True),
                        width=400,
                    ),
                    actions=[
                        ft.TextButton(
                            translator.get_text("common.buttons.cancel"),
                            on_click=lambda _: setattr(dialog, 'open', False) or dialog_page.update()
                        ),
                        ft.ElevatedButton(
                            translator.get_text("common.buttons.delete"),
                            icon=ft.Icons.DELETE,
                            on_click=confirm_delete if machine_count == 0 else None,
                            bgcolor=DesignSystem.ERROR if machine_count == 0 else DesignSystem.GRAY_400,
                            color="#FFFFFF",
                            disabled=machine_count > 0,
                        ),
                    ],
                )
                
                # Open dialog with fallback
                try:
                    dialog_page.open(dialog)
                except (AttributeError, Exception):
                    dialog_page.dialog = dialog
                    dialog.open = True
                    dialog_page.update()
            finally:
                session.close()
        
        # Initial load
        refresh_production_lines_list()
        
        # Build layout
        return ft.Row([
            # Left side: Production lines list
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text(
                            translator.get_text("production_line.title") if translator.get_text("production_line.title") != "production_line.title" else "Termelési Sorok",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color=DesignSystem.TEXT_PRIMARY,
                        ),
                        create_modern_button(
                            text=translator.get_text("production_line.create") if translator.get_text("production_line.create") != "production_line.create" else "Új termelési sor",
                            icon=ft.Icons.ADD,
                            on_click=lambda e: (print(f"[PRODUCTION_LINE] ====== BUTTON CLICKED! ======"), print(f"[PRODUCTION_LINE] Event: {e}, type: {type(e)}"), print(f"[PRODUCTION_LINE] Event control: {getattr(e, 'control', None)}"), open_create_dialog())[-1],
                            variant="blue",
                        ),
                    ], spacing=DesignSystem.SPACING_3, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    production_lines_list,
                ], spacing=DesignSystem.SPACING_4, expand=True),
                width=400,
                padding=DesignSystem.SPACING_4,
                border=ft.border.only(right=ft.BorderSide(1, DesignSystem.BORDER_COLOR)),
            ),
            # Right side: Details
            ft.Container(
                content=details_container,
                expand=True,
                padding=DesignSystem.SPACING_4,
            ),
        ], spacing=0, expand=True)

