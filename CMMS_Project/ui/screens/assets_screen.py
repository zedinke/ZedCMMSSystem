"""
Eszközök képernyő (váz)
"""

import flet as ft
from services import asset_service
from services import service_record_service
from services.context_service import get_app_context
from localization.translator import translator
from utils.currency import format_price
from datetime import datetime, timedelta
from utils.debug_helper import (
    debug_entry, debug_exit, debug_step, debug_variable, debug_call, 
    debug_return, debug_error, debug_exception, debug_ui, debug_service,
    debug_context, is_debug_enabled
)
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


class AssetsScreen:
    def __init__(self, page: ft.Page):
        self.page = page
    
    def view(self, page: ft.Page):
        # Use stored page reference for dialogs
        if not hasattr(self, 'page') or self.page is None:
            self.page = page
        
        machines_list = ft.Column([], spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)

        def open_correct_operating_hours_dialog(machine):
            """Open operating hours correction dialog with history and confirmation"""
            module_name = "assets_screen"
            function_name = "open_correct_operating_hours_dialog"
            
            debug_entry(module_name, function_name, {
                "machine_id": machine.id if hasattr(machine, 'id') else None,
                "machine_name": machine.name if hasattr(machine, 'name') else None,
                "machine_type": type(machine).__name__
            })
            
            try:
                debug_step(module_name, function_name, "Getting dialog_page reference")
                dialog_page = self.page if hasattr(self, 'page') and self.page else page
                debug_variable(module_name, function_name, "dialog_page", {
                    "type": type(dialog_page).__name__,
                    "has_open": hasattr(dialog_page, 'open'),
                    "has_dialog": hasattr(dialog_page, 'dialog')
                })
                
                debug_step(module_name, function_name, "Getting fresh machine data")
                debug_call(module_name, function_name, "asset_service.get_machine_with_history", {
                    "machine_id": machine.id
                })
                machine_full = asset_service.get_machine_with_history(machine.id)
                debug_return(module_name, function_name, "asset_service.get_machine_with_history", {
                    "machine_id": machine_full.id if hasattr(machine_full, 'id') else None,
                    "machine_name": machine_full.name if hasattr(machine_full, 'name') else None
                })
                
                current_hours = machine_full.operating_hours or 0.0
                debug_variable(module_name, function_name, "current_hours", current_hours)
                
                debug_step(module_name, function_name, "Getting operating hours history")
                debug_call(module_name, function_name, "asset_service.get_operating_hours_history", {
                    "machine_id": machine_full.id,
                    "limit": 10
                })
                history = asset_service.get_operating_hours_history(machine_full.id, limit=10)
                debug_return(module_name, function_name, "asset_service.get_operating_hours_history", {
                    "history_count": len(history) if history else 0
                })
                
                debug_step(module_name, function_name, "Calculating next reading date")
                debug_call(module_name, function_name, "asset_service.calculate_next_operating_hours_update_date", {
                    "machine_id": machine_full.id
                })
                next_reading_date = asset_service.calculate_next_operating_hours_update_date(machine_full)
                debug_return(module_name, function_name, "asset_service.calculate_next_operating_hours_update_date", {
                    "next_reading_date": str(next_reading_date) if next_reading_date else None
                })
            
                debug_step(module_name, function_name, "Creating UI fields")
                new_hours_field = create_modern_text_field(
                    label=translator.get_text("assets.operating_hours"),
                    value=str(current_hours),
                    keyboard_type=ft.KeyboardType.NUMBER,
                )
                debug_variable(module_name, function_name, "new_hours_field", {
                    "type": type(new_hours_field).__name__,
                    "value": new_hours_field.value if hasattr(new_hours_field, 'value') else None
                })
                
                notes_field = create_modern_text_field(
                    label=translator.get_text("common.notes"),
                    multiline=True,
                    max_lines=3,
                )
                debug_variable(module_name, function_name, "notes_field", {
                    "type": type(notes_field).__name__
                })
            
                debug_step(module_name, function_name, "Creating history list")
                history_list = ft.Column([], spacing=4, scroll=ft.ScrollMode.AUTO)
                
                def refresh_history():
                    debug_step(module_name, "refresh_history", "Refreshing history list")
                    history_list.controls.clear()
                    if history:
                        for entry in history:
                            history_list.controls.append(
                                ft.Container(
                                    content=ft.Column([
                                        ft.Row([
                                            ft.Text(
                                                f"{entry['user_name'] or translator.get_text('common.unknown')} - {entry['timestamp'].strftime('%Y-%m-%d %H:%M') if entry['timestamp'] else 'N/A'}",
                                                size=12,
                                                weight=ft.FontWeight.W_600,
                                            ),
                                        ]),
                                        ft.Row([
                                            ft.Text(
                                                f"{translator.get_text('assets.operating_hours_old_value')}: {entry['old_hours']:.2f} {translator.get_text('common.time.hours')}",
                                                size=11,
                                                color="#6B7280",
                                            ),
                                            ft.Text(" → ", size=11, color="#6B7280"),
                                            ft.Text(
                                                f"{translator.get_text('assets.operating_hours_new_value')}: {entry['new_hours']:.2f} {translator.get_text('common.time.hours')}",
                                                size=11,
                                                color="#6B7280",
                                            ),
                                            ft.Text(
                                                f" ({entry['difference']:+.2f})",
                                                size=11,
                                                color="#10B981" if entry['difference'] >= 0 else "#EF4444",
                                            ),
                                        ]),
                                        ft.Text(
                                            entry['notes'] or "",
                                            size=10,
                                            color="#9CA3AF",
                                        ) if entry['notes'] else ft.Container(height=0),
                                    ], spacing=2, tight=True),
                                    padding=ft.padding.all(8),
                                    bgcolor="#F9FAFB",
                                    border_radius=4,
                                )
                            )
                    else:
                        history_list.controls.append(
                            ft.Text(
                                translator.get_text("common.messages.no_data"),
                                size=12,
                                color="#6B7280",
                                italic=True,
                            )
                        )
                    # Don't call update() here - the control is not yet added to the page
                    # It will be updated when the dialog is opened
                    debug_step(module_name, "refresh_history", f"History list prepared with {len(history_list.controls)} items")
                
                # Prepare history list (but don't update yet - control not on page)
                refresh_history()
                
                debug_step(module_name, function_name, "Creating machine info section")
                machine_info_section = ft.Container(
                    content=ft.Column([
                        ft.Text(
                        translator.get_text("assets.machine_info"),
                        size=12,
                        weight=ft.FontWeight.BOLD,
                        color="#6B7280",
                    ),
                    ft.Row([
                        ft.Text(
                            f"{translator.get_text('assets.machine_name')}: ",
                            size=11,
                            color="#6B7280",
                        ),
                        ft.Text(
                            machine_full.name,
                            size=11,
                            weight=ft.FontWeight.W_600,
                        ),
                    ]),
                    ft.Row([
                        ft.Text(
                            f"{translator.get_text('assets.machine_serial')}: ",
                            size=11,
                            color="#6B7280",
                        ),
                        ft.Text(
                            machine_full.serial_number or translator.get_text("common.unknown"),
                            size=11,
                        ),
                    ]) if machine_full.serial_number else ft.Container(height=0),
                    ft.Row([
                        ft.Text(
                            f"{translator.get_text('assets.machine_model')}: ",
                            size=11,
                            color="#6B7280",
                        ),
                        ft.Text(
                            machine_full.model or translator.get_text("common.unknown"),
                            size=11,
                        ),
                    ]) if machine_full.model else ft.Container(height=0),
                    ft.Row([
                        ft.Text(
                            f"{translator.get_text('assets.machine_manufacturer')}: ",
                            size=11,
                            color="#6B7280",
                        ),
                        ft.Text(
                            machine_full.manufacturer or translator.get_text("common.unknown"),
                            size=11,
                        ),
                    ]) if machine_full.manufacturer else ft.Container(height=0),
                ], spacing=4, tight=True),
                padding=ft.padding.all(12),
                bgcolor="#F3F4F6",
                    border_radius=4,
                )
                
                debug_step(module_name, function_name, "Creating next reading date section")
                next_reading_section = ft.Container(
                    content=ft.Column([
                    ft.Text(
                        translator.get_text("assets.next_reading_date"),
                        size=12,
                        weight=ft.FontWeight.BOLD,
                        color="#6B7280",
                    ),
                    ft.Text(
                        next_reading_date.strftime("%Y-%m-%d %H:%M") if next_reading_date else translator.get_text("assets.no_next_reading_date"),
                        size=11,
                        color="#10B981" if next_reading_date and next_reading_date <= datetime.now() + timedelta(days=7) else "#6B7280",
                    ),
                ], spacing=4, tight=True),
                padding=ft.padding.all(12),
                bgcolor="#F3F4F6",
                    border_radius=4,
                )
                
                def submit_correction(_):
                    debug_entry(module_name, "submit_correction", {})
                    try:
                        debug_step(module_name, "submit_correction", "Parsing new_hours value")
                        new_hours = float(new_hours_field.value) if new_hours_field.value else 0.0
                        debug_variable(module_name, "submit_correction", "new_hours", new_hours)
                        
                        if new_hours < 0:
                            raise ValueError(translator.get_text("assets.operating_hours_positive"))
                        
                        debug_step(module_name, "submit_correction", "Showing confirmation dialog")
                        
                        # Show confirmation dialog
                        def confirm_update(_):
                            debug_entry(module_name, "confirm_update", {})
                            try:
                                debug_step(module_name, "confirm_update", "Getting current user ID")
                                from services.context_service import get_current_user_id
                                user_id = get_current_user_id()
                                debug_variable(module_name, "confirm_update", "user_id", user_id)
                                
                                debug_step(module_name, "confirm_update", "Calling asset_service.update_operating_hours")
                                debug_service(module_name, "confirm_update", "asset_service.update_operating_hours", {
                                    "machine_id": machine_full.id,
                                    "new_operating_hours": new_hours,
                                    "notes": notes_field.value if notes_field.value else None,
                                    "user_id": user_id
                                })
                                asset_service.update_operating_hours(
                                    machine_id=machine_full.id,
                                    new_operating_hours=new_hours,
                                    notes=notes_field.value if notes_field.value else None,
                                    user_id=user_id
                                )
                                debug_step(module_name, "confirm_update", "update_operating_hours completed successfully")
                            
                                debug_step(module_name, "confirm_update", "Closing confirmation dialog")
                                try:
                                    confirm_dialog_page.close(confirm_dialog)
                                    debug_step(module_name, "confirm_update", "Confirmation dialog closed successfully")
                                except Exception as close_exc:
                                    debug_exception(module_name, "confirm_update", close_exc, {"action": "close_confirm_dialog"})
                                    confirm_dialog.open = False
                                    confirm_dialog_page.dialog = None
                                    confirm_dialog_page.update()
                                
                                debug_step(module_name, "confirm_update", "Closing main dialog")
                                try:
                                    dialog_page.close(dialog)
                                    debug_step(module_name, "confirm_update", "Main dialog closed successfully")
                                except Exception as close_exc:
                                    debug_exception(module_name, "confirm_update", close_exc, {"action": "close_main_dialog"})
                                    dialog.open = False
                                    dialog_page.dialog = None
                                    dialog_page.update()
                                
                                debug_step(module_name, "confirm_update", "Refreshing machine list and reopening dialog")
                                refresh_list(update_page=False)
                                updated_machine = asset_service.get_machine_with_history(machine_full.id)
                                debug_step(module_name, "confirm_update", "Reopening operating hours dialog with updated machine")
                                open_correct_operating_hours_dialog(updated_machine)
                                
                                debug_ui(module_name, "confirm_update", "Showing success snackbar")
                                dialog_page.snack_bar = ft.SnackBar(
                                    content=ft.Text(translator.get_text("assets.operating_hours_updated")),
                                    bgcolor="#10B981"
                                )
                                dialog_page.snack_bar.open = True
                                dialog_page.update()
                                debug_exit(module_name, "confirm_update", {"success": True})
                            except Exception as exc:
                                debug_exception(module_name, "confirm_update", exc, {
                                    "machine_id": machine_full.id,
                                    "new_hours": new_hours
                                })
                                confirm_dialog_page.snack_bar = ft.SnackBar(
                                    content=ft.Text(f"{translator.get_text('common.error')}: {exc}"),
                                    bgcolor="#EF4444"
                                )
                                confirm_dialog_page.snack_bar.open = True
                                confirm_dialog_page.update()
                                debug_exit(module_name, "confirm_update", {"success": False, "error": str(exc)})
                        
                        def cancel_update(_):
                            debug_entry(module_name, "cancel_update", {})
                            try:
                                confirm_dialog_page.close(confirm_dialog)
                                debug_step(module_name, "cancel_update", "Confirmation dialog closed")
                            except Exception as close_exc:
                                debug_exception(module_name, "cancel_update", close_exc, {"action": "close_dialog"})
                                confirm_dialog.open = False
                                confirm_dialog_page.dialog = None
                                confirm_dialog_page.update()
                            debug_exit(module_name, "cancel_update", {})
                        
                        confirm_dialog_page = dialog_page
                        confirm_dialog = ft.AlertDialog(
                            title=ft.Text(
                                translator.get_text("common.messages.confirm"),
                                size=18,
                                weight=ft.FontWeight.W_600,
                            ),
                            content=ft.Container(
                                content=ft.Column([
                                ft.Text(
                                    translator.get_text("assets.confirm_operating_hours_update"),
                                    size=14,
                                ),
                                ft.Container(height=8),
                                ft.Text(
                                    f"{translator.get_text('assets.current_operating_hours')}: {current_hours:.2f} {translator.get_text('common.time.hours')} → {new_hours:.2f} {translator.get_text('common.time.hours')}",
                                    size=12,
                                    weight=ft.FontWeight.W_600,
                                    color="#6366F1",
                                ),
                                ], spacing=0, tight=True),
                                width=400,
                                padding=15,
                            ),
                            actions=[
                            ft.TextButton(
                                translator.get_text("common.buttons.cancel"),
                                on_click=cancel_update,
                                style=ft.ButtonStyle(color="#6B7280"),
                            ),
                            ft.ElevatedButton(
                                translator.get_text("common.buttons.save"),
                                icon=ft.Icons.CHECK,
                                on_click=confirm_update,
                                style=ft.ButtonStyle(
                                    bgcolor=DesignSystem.BLUE_500,
                                    color="#FFFFFF",
                                ),
                            ),
                            ],
                            actions_alignment=ft.MainAxisAlignment.END,
                        )
                        
                        debug_step(module_name, "submit_correction", "Opening confirmation dialog")
                        try:
                            confirm_dialog_page.open(confirm_dialog)
                            debug_step(module_name, "submit_correction", "Confirmation dialog opened successfully")
                        except Exception as open_exc:
                            debug_exception(module_name, "submit_correction", open_exc, {"action": "open_confirm_dialog"})
                            confirm_dialog_page.dialog = confirm_dialog
                            confirm_dialog.open = True
                            confirm_dialog_page.update()
                            debug_step(module_name, "submit_correction", "Confirmation dialog opened using fallback method")
                        
                        debug_exit(module_name, "submit_correction", {})
                    except Exception as exc:
                        debug_exception(module_name, "submit_correction", exc, {
                            "new_hours_field_value": new_hours_field.value if hasattr(new_hours_field, 'value') else None
                        })
                        dialog_page.snack_bar = ft.SnackBar(
                            content=ft.Text(f"{translator.get_text('common.error')}: {exc}"),
                            bgcolor="#EF4444"
                        )
                        dialog_page.snack_bar.open = True
                        dialog_page.update()
                        debug_exit(module_name, "submit_correction", {"success": False, "error": str(exc)})
                
                debug_step(module_name, function_name, "Creating main dialog")
                dialog = ft.AlertDialog(
                    title=ft.Text(
                        translator.get_text("assets.correct_operating_hours"),
                        size=20,
                        weight=ft.FontWeight.W_600,
                    ),
                    content=ft.Container(
                        content=ft.Column([
                            machine_info_section,
                        ft.Container(height=12),
                        ft.Container(
                            content=ft.Column([
                                ft.Text(
                                    f"{translator.get_text('assets.current_operating_hours')}: {current_hours:.2f} {translator.get_text('common.time.hours')}",
                                    size=14,
                                    weight=ft.FontWeight.W_600,
                                ),
                                ft.Container(height=8),
                                new_hours_field,
                                ft.Container(height=8),
                                notes_field,
                            ], spacing=0, tight=True),
                            padding=ft.padding.all(12),
                            bgcolor="#FFFFFF",
                            border_radius=4,
                        ),
                        ft.Container(height=12),
                        next_reading_section,
                        ft.Container(height=12),
                        ft.Container(
                            content=ft.Column([
                                ft.Text(
                                    translator.get_text("assets.operating_hours_history"),
                                    size=12,
                                    weight=ft.FontWeight.BOLD,
                                    color="#6B7280",
                                ),
                                ft.Container(height=8),
                                ft.Container(
                                    content=history_list,
                                    height=150,
                                ),
                            ], spacing=0, tight=True),
                            padding=ft.padding.all(12),
                            bgcolor="#FFFFFF",
                            border_radius=4,
                        ),
                        ], spacing=0, tight=True, scroll=ft.ScrollMode.AUTO),
                        width=600,
                        padding=15,
                    ),
                    actions=[
                    ft.TextButton(
                        translator.get_text("common.cancel"),
                        on_click=lambda _: setattr(dialog, 'open', False) or setattr(dialog_page, 'dialog', None) or dialog_page.update(),
                        style=ft.ButtonStyle(color="#6B7280"),
                    ),
                    ft.ElevatedButton(
                        translator.get_text("common.buttons.save"),
                        icon=ft.Icons.SAVE,
                        on_click=submit_correction,
                        style=ft.ButtonStyle(
                            bgcolor=DesignSystem.BLUE_500,
                            color="#FFFFFF",
                        ),
                    ),
                ],
                    actions_alignment=ft.MainAxisAlignment.END,
                )
                
                debug_step(module_name, function_name, "Attempting to open main dialog")
                try:
                    dialog_page.open(dialog)
                    debug_step(module_name, function_name, "Main dialog opened successfully using page.open()")
                    debug_variable(module_name, function_name, "dialog.open", dialog.open if hasattr(dialog, 'open') else None)
                    # Now that dialog is open, update the history list if needed
                    try:
                        history_list.update()
                        debug_step(module_name, function_name, "History list updated after dialog opened")
                    except Exception as update_exc:
                        # If update fails, it's okay - the dialog will handle it on next update
                        debug_step(module_name, function_name, f"History list update skipped (not yet on page): {update_exc}")
                except Exception as open_exc:
                    debug_exception(module_name, function_name, open_exc, {"action": "open_dialog", "method": "page.open()"})
                    debug_step(module_name, function_name, "Using fallback method to open dialog")
                    dialog_page.dialog = dialog
                    dialog.open = True
                    dialog_page.update()
                    debug_step(module_name, function_name, "Main dialog opened using fallback method")
                    debug_variable(module_name, function_name, "dialog.open", dialog.open if hasattr(dialog, 'open') else None)
                    debug_variable(module_name, function_name, "page.dialog", dialog_page.dialog is not None if hasattr(dialog_page, 'dialog') else None)
                    # Now that dialog is open, update the history list if needed
                    try:
                        history_list.update()
                        debug_step(module_name, function_name, "History list updated after dialog opened (fallback)")
                    except Exception as update_exc:
                        # If update fails, it's okay - the dialog will handle it on next update
                        debug_step(module_name, function_name, f"History list update skipped (not yet on page): {update_exc}")
                
                debug_exit(module_name, function_name, {"dialog_created": True, "dialog_opened": True})
            except Exception as e:
                debug_exception(module_name, function_name, e, {
                    "machine_id": machine.id if hasattr(machine, 'id') else None
                })
                debug_exit(module_name, function_name, {"success": False, "error": str(e)})
                raise

        def refresh_list(update_page=True):
            # Don't update if dialog is open
            page_ref = self.page if hasattr(self, 'page') and self.page else page
            if hasattr(page_ref, 'dialog') and page_ref.dialog is not None:
                dialog_open = getattr(page_ref.dialog, 'open', False)
                if dialog_open:
                    print("[ASSETS] Skipping refresh_list update because dialog is open")
                    return
            
            # Check if we need to open a machine dialog from search
            if hasattr(page_ref, '_open_machine_dialog_id') and page_ref._open_machine_dialog_id:
                machine_id = page_ref._open_machine_dialog_id
                page_ref._open_machine_dialog_id = None  # Clear flag
                try:
                    machine = asset_service.get_machine(machine_id)
                    if machine:
                        # Open edit dialog after a small delay to ensure list is rendered
                        import threading
                        def open_dialog():
                            import time
                            time.sleep(0.2)
                            try:
                                open_edit_machine_dialog(machine)
                            except Exception as e:
                                print(f"[ASSETS] Error opening machine dialog from search: {e}")
                        threading.Thread(target=open_dialog, daemon=True).start()
                except Exception as e:
                    print(f"[ASSETS] Error loading machine for search: {e}")
            
            machines = asset_service.list_machines()
            machines_list.controls.clear()
            
            # Load machines with history for version display
            machines_with_history = []
            for machine in machines:
                machine_full = asset_service.get_machine_with_history(machine.id)
                machines_with_history.append(machine_full if machine_full else machine)
            
            if not machines_with_history:
                machines_list.controls.append(
                    create_empty_state_card(
                        icon=ft.Icons.FACTORY,
                        title=translator.get_text("empty_states.no_machines"),
                        icon_color=DesignSystem.GRAY_400,
                    )
                )
            else:
                for machine in machines_with_history:
                    # Get compatible parts
                    compatible_parts = machine.id_compatible_parts if hasattr(machine, 'id_compatible_parts') else []
                    parts_text = ", ".join([p.name for p in compatible_parts[:3]])
                    if len(compatible_parts) > 3:
                        parts_text += f" +{len(compatible_parts) - 3} további"
                    
                    # Production line name
                    prod_line_name = machine.production_line.name if hasattr(machine, 'production_line') and machine.production_line else f"ID: {machine.production_line_id}"
                    
                    # Create Tailwind CSS card for each machine
                    status_color_map = {
                        "Active": (DesignSystem.EMERALD_500, "emerald"),
                        "Stopped": (DesignSystem.ORANGE_500, "orange"),
                        "Scrapped": (DesignSystem.RED_500, "red"),
                    }
                    status_color, status_variant = status_color_map.get(machine.status, (DesignSystem.GRAY_500, None))
                    
                    card_content_items = [
                                ft.Row([
                            ft.Container(
                                content=ft.Icon(ft.Icons.PRECISION_MANUFACTURING, color=DesignSystem.PURPLE_500, size=24),
                                padding=ft.padding.all(DesignSystem.SPACING_2),
                                bgcolor=DesignSystem.PURPLE_100,
                                border_radius=DesignSystem.RADIUS_LG,
                            ),
                                    ft.Column([
                                            ft.Text(
                                                machine.name,
                                    size=18,
                                    weight=ft.FontWeight.W_600,
                                    color=DesignSystem.TEXT_PRIMARY,
                                            ),
                                ft.Container(height=DesignSystem.SPACING_1),
                                        ft.Row([
                                    ft.Text(
                                        f"{translator.get_text('assets.production_line')}: {prod_line_name}",
                                        size=13,
                                        color=DesignSystem.TEXT_SECONDARY,
                                    ),
                                    ft.Container(width=DesignSystem.SPACING_4),
                                    ft.Text(
                                        f"{translator.get_text('assets.serial_number')}: {machine.serial_number or '-'}",
                                        size=13,
                                        color=DesignSystem.TEXT_SECONDARY,
                                    ),
                                ], spacing=DesignSystem.SPACING_2),
                                ft.Container(height=DesignSystem.SPACING_1),
                                        ft.Row([
                                    ft.Text(
                                        f"{translator.get_text('assets.model')}: {machine.model or '-'}",
                                        size=13,
                                        color=DesignSystem.TEXT_SECONDARY,
                                    ),
                                    ft.Container(width=DesignSystem.SPACING_4),
                                    create_vibrant_badge(
                                        text=machine.status,
                                        variant=status_variant or "blue",
                                        size=11,
                                    ) if status_variant else ft.Text(
                                        f"{translator.get_text('assets.status')}: {machine.status}",
                                        size=13,
                                        color=DesignSystem.TEXT_SECONDARY,
                                    ),
                                ], spacing=DesignSystem.SPACING_2),
                            ], expand=True, spacing=0),
                        ], spacing=DesignSystem.SPACING_3),
                    ]
                    
                    if compatible_parts:
                        card_content_items.append(
                                        ft.Container(
                                            content=ft.Column([
                                                ft.Text(
                                                    translator.get_text("assets.compatible_parts"),
                                        size=12,
                                        weight=ft.FontWeight.W_600,
                                        color=DesignSystem.TEXT_SECONDARY,
                                                ),
                                                ft.Text(
                                                    parts_text or translator.get_text("empty_states.no_parts"),
                                        size=12,
                                        color=DesignSystem.TEXT_TERTIARY,
                                                    italic=True,
                                                ),
                                ], spacing=DesignSystem.SPACING_1, tight=True),
                                bgcolor=DesignSystem.GRAY_50,
                                padding=DesignSystem.SPACING_2,
                                border_radius=DesignSystem.RADIUS_MD,
                            )
                        )
                    
                                        # Version and audit info
                    if hasattr(machine, 'updated_by_user') or hasattr(machine, 'version'):
                        card_content_items.append(
                                        ft.Container(
                                            content=ft.Row([
                                    ft.Icon(ft.Icons.HISTORY, size=12, color=DesignSystem.TEXT_TERTIARY),
                                                ft.Text(
                                                    f"Verzió: {machine.version if hasattr(machine, 'version') else 1}",
                                        size=11,
                                        color=DesignSystem.TEXT_TERTIARY,
                                                ),
                                    ft.Container(width=DesignSystem.SPACING_2),
                                    ft.Icon(ft.Icons.PERSON, size=12, color=DesignSystem.TEXT_TERTIARY),
                                                ft.Text(
                                                    f"Utolsó módosítás: {machine.updated_by_user.full_name if hasattr(machine, 'updated_by_user') and machine.updated_by_user else 'Ismeretlen'} ({machine.updated_at.strftime('%Y-%m-%d %H:%M') if hasattr(machine, 'updated_at') and machine.updated_at else '-'})",
                                        size=11,
                                        color=DesignSystem.TEXT_TERTIARY,
                                                ),
                                ], spacing=DesignSystem.SPACING_1, tight=True),
                                padding=ft.padding.only(top=DesignSystem.SPACING_2),
                            )
                        )
                    
                    card_content_items.append(
                                    ft.Row([
                            create_modern_icon_button(
                                            icon=ft.Icons.BUILD_CIRCLE,
                                            tooltip="Szervizelés hozzáadása",
                                            on_click=lambda e, m=machine: open_add_service_dialog(m),
                                color=DesignSystem.EMERALD_500,
                                vibrant=True,
                                variant="emerald",
                                        ),
                            create_modern_icon_button(
                                            icon=ft.Icons.EDIT,
                                            tooltip=translator.get_text("common.buttons.edit"),
                                            on_click=lambda e, m=machine: open_edit_machine_dialog(m),
                                color=DesignSystem.BLUE_500,
                                vibrant=True,
                                variant="blue",
                                        ),
                            create_modern_icon_button(
                                            icon=ft.Icons.ACCESS_TIME,
                                            tooltip=translator.get_text("assets.correct_operating_hours"),
                                            on_click=lambda e, m=machine: open_correct_operating_hours_dialog(m),
                                color=DesignSystem.ORANGE_500,
                                vibrant=True,
                                variant="orange",
                            ),
                            create_modern_icon_button(
                                            icon=ft.Icons.DELETE,
                                            tooltip=translator.get_text("common.buttons.delete"),
                                            on_click=lambda e, m=machine: open_delete_machine_dialog(m),
                                color=DesignSystem.RED_500,
                                vibrant=True,
                                variant="red",
                            ),
                        ], spacing=DesignSystem.SPACING_2),
                    )
                    
                    card_content = ft.Column(card_content_items, spacing=DesignSystem.SPACING_2)
                    card_content.controls = [c for c in card_content.controls if c is not None]
                    
                    card = create_tailwind_card(
                        content=card_content,
                        padding=DesignSystem.SPACING_4,
                        elevation=1,
                        accent_color=DesignSystem.PURPLE_500,
                    )
                    machines_list.controls.append(card)
            
            if update_page:
                page.update()

        def open_add_dialog(e):
            print(f"[ASSETS] open_add_dialog called, event: {e}")
            # Use stored page reference instead of parameter
            dialog_page = self.page if hasattr(self, 'page') and self.page else page
            print(f"[ASSETS] page object: {dialog_page}, page type: {type(dialog_page)}")
            try:
                name_field = ft.TextField(
                    label=translator.get_text("assets.name"),
                    autofocus=True,
                    prefix_icon=ft.Icons.LABEL,
                )
                line_field = ft.TextField(
                    label=translator.get_text("assets.parent_line_id"),
                    keyboard_type=ft.KeyboardType.NUMBER,
                    prefix_icon=ft.Icons.NUMBERS,
                )
                serial_field = ft.TextField(
                    label=translator.get_text("assets.serial_number"),
                    prefix_icon=ft.Icons.CONFIRMATION_NUMBER,
                )
                manufacturer_field = ft.TextField(
                    label=translator.get_text("assets.manufacturer"),
                    prefix_icon=ft.Icons.BUSINESS,
                )
                model_field = ft.TextField(
                    label=translator.get_text("assets.model"),
                    prefix_icon=ft.Icons.DESIGN_SERVICES,
                )
                install_date_field = ft.TextField(
                    label=translator.get_text("assets.install_date"),
                    hint_text="YYYY-MM-DD",
                    prefix_icon=ft.Icons.CALENDAR_TODAY,
                )
                status_field = ft.Dropdown(
                    label=translator.get_text("assets.status"),
                    prefix_icon=ft.Icons.INFO,
                    options=[
                        ft.dropdown.Option("Active"),
                        ft.dropdown.Option("Stopped"),
                        ft.dropdown.Option("Scrapped"),
                    ],
                    value="Active"
                )
                maintenance_field = ft.TextField(
                    label=translator.get_text("assets.maintenance_interval"),
                    hint_text="pl. Havonta vagy 500 üzemóra",
                    prefix_icon=ft.Icons.BUILD,
                )
                manual_field = ft.TextField(
                    label=translator.get_text("assets.manual_path"),
                    hint_text="pl. c:/docs/manual.pdf vagy URL",
                    prefix_icon=ft.Icons.DESCRIPTION,
                )
                # Extended fields
                asset_tag_field = ft.TextField(
                    label="Eszköz azonosító",
                    hint_text="Egyedi eszköz azonosító",
                    prefix_icon=ft.Icons.TAG,
                )
                purchase_date_field = ft.TextField(
                    label="Vásárlás dátuma",
                    hint_text="YYYY-MM-DD",
                    prefix_icon=ft.Icons.SHOPPING_CART,
                )
                purchase_price_field = ft.TextField(
                    label="Vásárlási ár",
                    keyboard_type=ft.KeyboardType.NUMBER,
                    hint_text="EUR",
                    prefix_icon=ft.Icons.ATTACH_MONEY,
                )
                warranty_expiry_field = ft.TextField(
                    label="Garancia lejárat",
                    hint_text="YYYY-MM-DD",
                    prefix_icon=ft.Icons.SECURITY,
                )
                supplier_field = ft.TextField(
                    label="Beszállító",
                    prefix_icon=ft.Icons.STOREFRONT,
                )
                operating_hours_field = ft.TextField(
                    label="Üzemóra",
                    keyboard_type=ft.KeyboardType.NUMBER,
                    hint_text="óra",
                    prefix_icon=ft.Icons.ACCESS_TIME,
                )
                last_service_field = ft.TextField(
                    label="Utolsó szerviz",
                    hint_text="YYYY-MM-DD",
                    prefix_icon=ft.Icons.BUILD_CIRCLE,
                )
                next_service_field = ft.TextField(
                    label="Következő szerviz",
                    hint_text="YYYY-MM-DD",
                    prefix_icon=ft.Icons.SCHEDULE,
                )
                criticality_field = ft.Dropdown(
                    label="Kritikussági szint",
                    prefix_icon=ft.Icons.PRIORITY_HIGH,
                    options=[
                        ft.dropdown.Option("Critical"),
                        ft.dropdown.Option("High"),
                        ft.dropdown.Option("Medium"),
                        ft.dropdown.Option("Low"),
                    ],
                )
                energy_field = ft.TextField(
                    label="Energiafogyasztás",
                    hint_text="pl. 15 kW",
                    prefix_icon=ft.Icons.BOLT,
                )
                power_req_field = ft.TextField(
                    label="Energiaigény",
                    hint_text="pl. 220V/3-phase",
                    prefix_icon=ft.Icons.POWER,
                )
                temp_range_field = ft.TextField(
                    label="Működési hőmérséklet",
                    hint_text="pl. 0-40°C",
                    prefix_icon=ft.Icons.THERMOSTAT,
                )
                weight_field = ft.TextField(
                    label="Súly",
                    keyboard_type=ft.KeyboardType.NUMBER,
                    hint_text="kg",
                    prefix_icon=ft.Icons.SCALE,
                )
                dimensions_field = ft.TextField(
                    label="Méretek",
                    hint_text="pl. 2000x1500x1800 mm",
                    prefix_icon=ft.Icons.STRAIGHTEN,
                )
                notes_field = ft.TextField(
                    label="Megjegyzések",
                    multiline=True,
                    max_lines=3,
                    prefix_icon=ft.Icons.NOTE,
                )
                
                # Operating hours update frequency settings
                operating_hours_frequency_type_field = ft.Dropdown(
                    label=translator.get_text("assets.operating_hours_update_frequency_type"),
                    prefix_icon=ft.Icons.REFRESH if hasattr(ft.Icons, 'REFRESH') else ft.Icons.REPEAT if hasattr(ft.Icons, 'REPEAT') else None,
                    options=[
                        ft.dropdown.Option("day", translator.get_text("common.day")),
                        ft.dropdown.Option("week", translator.get_text("common.week")),
                        ft.dropdown.Option("month", translator.get_text("common.month")),
                    ],
                    value=None,
                )
                operating_hours_frequency_value_field = ft.TextField(
                    label=translator.get_text("assets.operating_hours_update_frequency_value"),
                    keyboard_type=ft.KeyboardType.NUMBER,
                    hint_text=translator.get_text("assets.frequency_value_hint"),
                    prefix_icon=ft.Icons.NUMBERS,
                    disabled=True,
                )
                
                def on_frequency_type_change(_):
                    operating_hours_frequency_value_field.disabled = operating_hours_frequency_type_field.value is None
                    dialog_page.update()
                
                operating_hours_frequency_type_field.on_change = on_frequency_type_change

                def submit(_):
                    try:
                        if not name_field.value or not line_field.value:
                            raise ValueError(translator.get_text("common.messages.required_field"))
                        line_id = int(line_field.value)
                        
                        # Parse dates if provided
                        from datetime import datetime
                        def parse_date(date_str):
                            if not date_str:
                                return None
                            try:
                                return datetime.strptime(date_str, "%Y-%m-%d")
                            except ValueError:
                                raise ValueError("Dátum formátum hiba (YYYY-MM-DD)")
                        
                        val_install_date = parse_date(install_date_field.value)
                        val_purchase_date = parse_date(purchase_date_field.value)
                        val_warranty_expiry = parse_date(warranty_expiry_field.value)
                        val_last_service = parse_date(last_service_field.value)
                        val_next_service = parse_date(next_service_field.value)
                        
                        # Parse numbers
                        def parse_float(value_str):
                            if not value_str:
                                return None
                            try:
                                return float(value_str)
                            except ValueError:
                                return None
                        
                        val_purchase_price = parse_float(purchase_price_field.value)
                        val_operating_hours = parse_float(operating_hours_field.value)
                        val_weight = parse_float(weight_field.value)
                        
                        # Parse operating hours update frequency
                        operating_hours_freq_type = operating_hours_frequency_type_field.value if operating_hours_frequency_type_field.value else None
                        operating_hours_freq_value = None
                        if operating_hours_freq_type and operating_hours_frequency_value_field.value:
                            try:
                                operating_hours_freq_value = int(operating_hours_frequency_value_field.value)
                            except ValueError:
                                operating_hours_freq_value = None
                        
                        # Get current user
                        ctx = get_app_context()
                        user_id = ctx.user_id if ctx.is_authenticated() else None

                        asset_service.create_machine(
                            production_line_id=line_id,
                            name=name_field.value,
                            serial_number=serial_field.value or None,
                            model=model_field.value or None,
                            manufacturer=manufacturer_field.value or None,
                            manual_pdf_path=manual_field.value or None,
                            install_date=val_install_date,
                            status=status_field.value,
                            maintenance_interval=maintenance_field.value or None,
                            asset_tag=asset_tag_field.value or None,
                            purchase_date=val_purchase_date,
                            purchase_price=val_purchase_price,
                            warranty_expiry_date=val_warranty_expiry,
                            supplier=supplier_field.value or None,
                            operating_hours=val_operating_hours,
                            last_service_date=val_last_service,
                            next_service_date=val_next_service,
                            criticality_level=criticality_field.value or None,
                            energy_consumption=energy_field.value or None,
                            power_requirements=power_req_field.value or None,
                            operating_temperature_range=temp_range_field.value or None,
                            weight=val_weight,
                            dimensions=dimensions_field.value or None,
                            notes=notes_field.value or None,
                            created_by_user_id=user_id,
                            operating_hours_update_frequency_type=operating_hours_freq_type,
                            operating_hours_update_frequency_value=operating_hours_freq_value,
                        )
                        try:
                            dialog_page.close(dialog)
                        except:
                            dialog.open = False
                            dialog_page.update()
                        dialog_page.snack_bar = ft.SnackBar(
                            content=ft.Text(translator.get_text("assets.machine_added")),
                            bgcolor="#10B981",
                        )
                        dialog_page.snack_bar.open = True
                        refresh_list(update_page=True)
                    except Exception as exc:
                        dialog_page.snack_bar = ft.SnackBar(
                            ft.Text(f"{translator.get_text('assets.machine_add_error')}: {exc}")
                        )
                        dialog_page.snack_bar.open = True
                    dialog_page.update()

                # Modern, szép design a formhoz
                dialog = ft.AlertDialog(
                    modal=True,
                    title=ft.Row([
                        ft.Icon(ft.Icons.PRECISION_MANUFACTURING, color="#6366F1", size=24),
                        ft.Text(
                            translator.get_text("assets.add_machine_dialog_title"),
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
                                        translator.get_text("common.messages.required_fields"),
                                        size=12,
                                        weight=ft.FontWeight.BOLD,
                                        color="#6B7280",
                                    ),
                                    name_field,
                                    line_field,
                                ], spacing=8),
                                padding=ft.padding.only(bottom=10),
                            ),
                            ft.Divider(height=1, color="#E5E7EB"),
                            
                            # Alap információk
                            ft.Container(
                                content=ft.Column([
                                    ft.Text(
                                        "Alap információk",
                                        size=12,
                                        weight=ft.FontWeight.BOLD,
                                        color="#6B7280",
                                    ),
                                    ft.Row([
                                        ft.Container(content=manufacturer_field, expand=1),
                                        ft.Container(content=model_field, expand=1, margin=ft.margin.only(left=10)),
                                    ]),
                                    serial_field,
                                ], spacing=8),
                                padding=ft.padding.only(top=10, bottom=10),
                            ),
                            ft.Divider(height=1, color="#E5E7EB"),
                            
                            # Státusz és dátum
                            ft.Container(
                                content=ft.Column([
                                    ft.Text(
                                        "Státusz és dátum",
                                        size=12,
                                        weight=ft.FontWeight.BOLD,
                                        color="#6B7280",
                                    ),
                                    ft.Row([
                                        ft.Container(content=status_field, expand=1),
                                        ft.Container(content=install_date_field, expand=1, margin=ft.margin.only(left=10)),
                                    ]),
                                ], spacing=8),
                                padding=ft.padding.only(top=10, bottom=10),
                            ),
                            ft.Divider(height=1, color="#E5E7EB"),
                            
                            # Karbantartás és dokumentáció
                            ft.Container(
                                content=ft.Column([
                                    ft.Text(
                                        "Karbantartás és dokumentáció",
                                        size=12,
                                        weight=ft.FontWeight.BOLD,
                                        color="#6B7280",
                                    ),
                                    maintenance_field,
                                    ft.Row([
                                        ft.Container(content=last_service_field, expand=1),
                                        ft.Container(content=next_service_field, expand=1, margin=ft.margin.only(left=10)),
                                    ]),
                                    operating_hours_field,
                                    ft.Row([
                                        ft.Container(content=operating_hours_frequency_type_field, expand=1),
                                        ft.Container(content=operating_hours_frequency_value_field, expand=1, margin=ft.margin.only(left=10)),
                                    ]),
                                    manual_field,
                                ], spacing=8),
                                padding=ft.padding.only(top=10, bottom=10),
                            ),
                            ft.Divider(height=1, color="#E5E7EB"),
                            
                            # Vásárlás és garancia
                            ft.Container(
                                content=ft.Column([
                                    ft.Text(
                                        "Vásárlás és garancia",
                                        size=12,
                                        weight=ft.FontWeight.BOLD,
                                        color="#6B7280",
                                    ),
                                    ft.Row([
                                        ft.Container(content=purchase_date_field, expand=1),
                                        ft.Container(content=purchase_price_field, expand=1, margin=ft.margin.only(left=10)),
                                    ]),
                                    ft.Row([
                                        ft.Container(content=warranty_expiry_field, expand=1),
                                        ft.Container(content=supplier_field, expand=1, margin=ft.margin.only(left=10)),
                                    ]),
                                ], spacing=8),
                                padding=ft.padding.only(top=10, bottom=10),
                            ),
                            ft.Divider(height=1, color="#E5E7EB"),
                            
                            # Műszaki információk
                            ft.Container(
                                content=ft.Column([
                                    ft.Text(
                                        "Műszaki információk",
                                        size=12,
                                        weight=ft.FontWeight.BOLD,
                                        color="#6B7280",
                                    ),
                                    ft.Row([
                                        ft.Container(content=energy_field, expand=1),
                                        ft.Container(content=power_req_field, expand=1, margin=ft.margin.only(left=10)),
                                    ]),
                                    ft.Row([
                                        ft.Container(content=temp_range_field, expand=1),
                                        ft.Container(content=weight_field, expand=1, margin=ft.margin.only(left=10)),
                                    ]),
                                    dimensions_field,
                                ], spacing=8),
                                padding=ft.padding.only(top=10, bottom=10),
                            ),
                            ft.Divider(height=1, color="#E5E7EB"),
                            
                            # További információk
                            ft.Container(
                                content=ft.Column([
                                    ft.Text(
                                        "További információk",
                                        size=12,
                                        weight=ft.FontWeight.BOLD,
                                        color="#6B7280",
                                    ),
                                    asset_tag_field,
                                    criticality_field,
                                    notes_field,
                                ], spacing=8),
                                padding=ft.padding.only(top=10, bottom=10),
                            ),
                        ], 
                        tight=False,
                        spacing=12,
                        scroll=ft.ScrollMode.AUTO,
                        ),
                        width=700,
                        height=700,
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
                    try:
                        dialog_page.close(dialog)
                    except:
                        dialog.open = False
                        dialog_page.update()

                # Set dialog and show it using modern page.open() method
                print(f"[ASSETS] Setting dialog on page: {dialog_page}")
                try:
                    # Modern Flet way: use page.open() instead of page.dialog + page.update()
                    dialog_page.open(dialog)
                    print(f"[ASSETS] Dialog opened using page.open() - dialog.open={dialog.open}")
                except AttributeError:
                    # Fallback to old method if page.open() doesn't exist
                    print("[ASSETS] page.open() not available, using fallback method")
                    dialog_page.dialog = dialog
                    dialog.open = True
                    dialog_page.update()
                    print(f"[ASSETS] Dialog opened using fallback - dialog.open={dialog.open}, page.dialog exists={dialog_page.dialog is not None}")
                except Exception as open_error:
                    print(f"[ASSETS] Error opening dialog: {open_error}")
                    import traceback
                    traceback.print_exc()
                    # Try fallback
                    try:
                        dialog_page.dialog = dialog
                        dialog.open = True
                        dialog_page.update()
                        print(f"[ASSETS] Fallback successful - dialog.open={dialog.open}")
                    except Exception as fallback_error:
                        print(f"[ASSETS] Fallback also failed: {fallback_error}")
                print(f"[ASSETS] Final state - dialog.open={dialog.open}, page.dialog: {dialog_page.dialog}")
            except Exception as ex:
                 print(f"Error opening dialog: {ex}")
                 dialog_page.snack_bar = ft.SnackBar(ft.Text(f"Error opening dialog: {ex}"))
                 dialog_page.snack_bar.open = True
                 dialog_page.update()

        def open_edit_machine_dialog(machine):
            """Open edit dialog for machine"""
            module_name = "assets_screen"
            function_name = "open_edit_machine_dialog"
            
            debug_entry(module_name, function_name, {
                "machine_id": machine.id if hasattr(machine, 'id') else None,
                "machine_name": machine.name if hasattr(machine, 'name') else None,
                "machine_type": type(machine).__name__
            })
            
            try:
                debug_step(module_name, function_name, "Getting dialog_page reference")
                dialog_page = self.page if hasattr(self, 'page') and self.page else page
                debug_variable(module_name, function_name, "dialog_page", {
                    "type": type(dialog_page).__name__,
                    "has_open": hasattr(dialog_page, 'open'),
                    "has_dialog": hasattr(dialog_page, 'dialog')
                })
                
                debug_step(module_name, function_name, "Creating form fields")
                name_field = ft.TextField(
                    label=translator.get_text("assets.name"),
                    value=machine.name,
                    prefix_icon=ft.Icons.LABEL,
                )
                line_field = ft.TextField(
                    label=translator.get_text("assets.parent_line_id"),
                    keyboard_type=ft.KeyboardType.NUMBER,
                    value=str(machine.production_line_id),
                    prefix_icon=ft.Icons.NUMBERS,
                )
                serial_field = ft.TextField(
                    label=translator.get_text("assets.serial_number"),
                    value=machine.serial_number or "",
                    prefix_icon=ft.Icons.CONFIRMATION_NUMBER,
                )
                model_field = ft.TextField(
                    label=translator.get_text("assets.model"),
                    value=machine.model or "",
                    prefix_icon=ft.Icons.DESIGN_SERVICES,
                )
                manufacturer_field = ft.TextField(
                    label=translator.get_text("assets.manufacturer"),
                    value=machine.manufacturer or "",
                    prefix_icon=ft.Icons.BUSINESS,
                )
                manual_field = ft.TextField(
                    label=translator.get_text("assets.manual_path"),
                    value=machine.manual_pdf_path or "",
                    prefix_icon=ft.Icons.DESCRIPTION,
                )
                install_date_field = ft.TextField(
                    label=translator.get_text("assets.install_date"),
                    value=machine.install_date.strftime("%Y-%m-%d") if machine.install_date else "",
                    prefix_icon=ft.Icons.CALENDAR_TODAY,
                )
                status_field = ft.Dropdown(
                    label=translator.get_text("assets.status"),
                    prefix_icon=ft.Icons.INFO,
                    options=[
                        ft.dropdown.Option("Active"),
                        ft.dropdown.Option("Stopped"),
                        ft.dropdown.Option("Scrapped"),
                    ],
                    value=machine.status,
                )
                maintenance_field = ft.TextField(
                    label=translator.get_text("assets.maintenance_interval"),
                    value=machine.maintenance_interval or "",
                    prefix_icon=ft.Icons.BUILD,
                )
                debug_step(module_name, function_name, "Form fields created")
                
                # Extended fields for edit
                debug_step(module_name, function_name, "Creating extended fields")
                purchase_date_field = ft.TextField(
                    label="Vásárlás dátuma",
                    value=machine.purchase_date.strftime("%Y-%m-%d") if hasattr(machine, 'purchase_date') and machine.purchase_date else "",
                    hint_text="YYYY-MM-DD",
                    prefix_icon=ft.Icons.SHOPPING_CART,
                )
                purchase_price_field = ft.TextField(
                    label="Vásárlási ár",
                    value=str(machine.purchase_price) if hasattr(machine, 'purchase_price') and machine.purchase_price else "",
                    keyboard_type=ft.KeyboardType.NUMBER,
                    hint_text="Ft",
                    prefix_icon=ft.Icons.ATTACH_MONEY,
                )
                warranty_expiry_field = ft.TextField(
                    label="Garancia lejárat",
                    value=machine.warranty_expiry_date.strftime("%Y-%m-%d") if hasattr(machine, 'warranty_expiry_date') and machine.warranty_expiry_date else "",
                    hint_text="YYYY-MM-DD",
                    prefix_icon=ft.Icons.SECURITY,
                )
                supplier_field = ft.TextField(
                    label="Beszállító",
                    value=machine.supplier or "" if hasattr(machine, 'supplier') else "",
                    prefix_icon=ft.Icons.STOREFRONT,
                )
                operating_hours_field = ft.TextField(
                    label="Üzemóra",
                    value=str(machine.operating_hours) if hasattr(machine, 'operating_hours') and machine.operating_hours else "",
                    keyboard_type=ft.KeyboardType.NUMBER,
                    hint_text="óra",
                    prefix_icon=ft.Icons.ACCESS_TIME,
                )
                last_service_field = ft.TextField(
                    label="Utolsó szerviz",
                    value=machine.last_service_date.strftime("%Y-%m-%d") if hasattr(machine, 'last_service_date') and machine.last_service_date else "",
                    hint_text="YYYY-MM-DD",
                    prefix_icon=ft.Icons.BUILD_CIRCLE,
                )
                next_service_field = ft.TextField(
                    label="Következő szerviz",
                    value=machine.next_service_date.strftime("%Y-%m-%d") if hasattr(machine, 'next_service_date') and machine.next_service_date else "",
                    hint_text="YYYY-MM-DD",
                    prefix_icon=ft.Icons.SCHEDULE,
                )
                criticality_field = ft.Dropdown(
                    label="Kritikussági szint",
                    prefix_icon=ft.Icons.PRIORITY_HIGH,
                    options=[
                        ft.dropdown.Option("Critical"),
                        ft.dropdown.Option("High"),
                        ft.dropdown.Option("Medium"),
                        ft.dropdown.Option("Low"),
                    ],
                    value=machine.criticality_level if hasattr(machine, 'criticality_level') and machine.criticality_level else None,
                )
                energy_field = ft.TextField(
                    label="Energiafogyasztás",
                    value=machine.energy_consumption or "" if hasattr(machine, 'energy_consumption') else "",
                    hint_text="pl. 15 kW",
                    prefix_icon=ft.Icons.BOLT,
                )
                power_req_field = ft.TextField(
                    label="Energiaigény",
                    value=machine.power_requirements or "" if hasattr(machine, 'power_requirements') else "",
                    hint_text="pl. 220V/3-phase",
                    prefix_icon=ft.Icons.POWER,
                )
                temp_range_field = ft.TextField(
                    label="Működési hőmérséklet",
                    value=machine.operating_temperature_range or "" if hasattr(machine, 'operating_temperature_range') else "",
                    hint_text="pl. 0-40°C",
                    prefix_icon=ft.Icons.THERMOSTAT,
                )
                weight_field = ft.TextField(
                    label="Súly",
                    value=str(machine.weight) if hasattr(machine, 'weight') and machine.weight else "",
                    keyboard_type=ft.KeyboardType.NUMBER,
                    hint_text="kg",
                    prefix_icon=ft.Icons.SCALE,
                )
                dimensions_field = ft.TextField(
                    label="Méretek",
                    value=machine.dimensions or "" if hasattr(machine, 'dimensions') else "",
                    hint_text="pl. 2000x1500x1800 mm",
                    prefix_icon=ft.Icons.STRAIGHTEN,
                )
                notes_field = ft.TextField(
                    label="Megjegyzések",
                    value=machine.notes or "" if hasattr(machine, 'notes') else "",
                    multiline=True,
                    max_lines=3,
                    prefix_icon=ft.Icons.NOTE,
                )
                # Change description field removed - now shown in separate dialog before submit
                
                # Asset tag field
                asset_tag_field = ft.TextField(
                    label="Eszköz azonosító",
                    hint_text="Egyedi eszköz azonosító",
                    prefix_icon=ft.Icons.TAG,
                    value=getattr(machine, 'asset_tag', '') if hasattr(machine, 'asset_tag') else '',
                )
                
                debug_step(module_name, function_name, "All form fields created")
                
                # Operating hours update frequency settings
                operating_hours_frequency_type_field_edit = ft.Dropdown(
                    label=translator.get_text("assets.operating_hours_update_frequency_type"),
                    prefix_icon=ft.Icons.REFRESH if hasattr(ft.Icons, 'REFRESH') else ft.Icons.REPEAT if hasattr(ft.Icons, 'REPEAT') else None,
                    options=[
                        ft.dropdown.Option("day", translator.get_text("common.day")),
                        ft.dropdown.Option("week", translator.get_text("common.week")),
                        ft.dropdown.Option("month", translator.get_text("common.month")),
                    ],
                    value=getattr(machine, 'operating_hours_update_frequency_type', None),
                )
                operating_hours_frequency_value_field_edit = ft.TextField(
                    label=translator.get_text("assets.operating_hours_update_frequency_value"),
                    keyboard_type=ft.KeyboardType.NUMBER,
                    hint_text=translator.get_text("assets.frequency_value_hint"),
                    prefix_icon=ft.Icons.NUMBERS,
                    value=str(getattr(machine, 'operating_hours_update_frequency_value', '')) if hasattr(machine, 'operating_hours_update_frequency_value') and getattr(machine, 'operating_hours_update_frequency_value') else '',
                    disabled=not (hasattr(machine, 'operating_hours_update_frequency_type') and getattr(machine, 'operating_hours_update_frequency_type')),
                )
                
                def on_frequency_type_change_edit(_):
                    operating_hours_frequency_value_field_edit.disabled = operating_hours_frequency_type_field_edit.value is None
                    dialog_page.update()
                
                operating_hours_frequency_type_field_edit.on_change = on_frequency_type_change_edit
                
                debug_step(module_name, function_name, "Creating submit_edit handler")
                def submit_edit(_):
                    debug_entry(module_name, "submit_edit", {})
                    try:
                        debug_step(module_name, "submit_edit", "Validating form fields")
                        if not name_field.value or not line_field.value:
                            raise ValueError(translator.get_text("common.messages.required_field"))
                        line_id = int(line_field.value)
                        debug_variable(module_name, "submit_edit", "line_id", line_id)
                        
                        from datetime import datetime
                        def parse_date(date_str):
                            if not date_str:
                                return None
                            try:
                                return datetime.strptime(date_str, "%Y-%m-%d")
                            except ValueError:
                                raise ValueError("Dátum formátum hiba (YYYY-MM-DD)")
                        
                        def parse_float(value_str):
                            if not value_str:
                                return None
                            try:
                                return float(value_str)
                            except ValueError:
                                return None
                        
                        debug_step(module_name, "submit_edit", "Parsing form values")
                        val_install_date = parse_date(install_date_field.value)
                        val_purchase_date = parse_date(purchase_date_field.value)
                        val_warranty_expiry = parse_date(warranty_expiry_field.value)
                        val_last_service = parse_date(last_service_field.value)
                        val_next_service = parse_date(next_service_field.value)
                        
                        val_purchase_price = parse_float(purchase_price_field.value)
                        val_operating_hours = parse_float(operating_hours_field.value)
                        val_weight = parse_float(weight_field.value)
                        
                        # Parse operating hours update frequency
                        operating_hours_freq_type = operating_hours_frequency_type_field_edit.value if operating_hours_frequency_type_field_edit.value else None
                        operating_hours_freq_value = None
                        if operating_hours_freq_type and operating_hours_frequency_value_field_edit.value:
                            try:
                                operating_hours_freq_value = int(operating_hours_frequency_value_field_edit.value)
                            except ValueError:
                                operating_hours_freq_value = None
                        
                        # Get current user
                        debug_step(module_name, "submit_edit", "Getting current user")
                        ctx = get_app_context()
                        user_id = ctx.user_id if ctx.is_authenticated() else None
                        debug_variable(module_name, "submit_edit", "user_id", user_id)
                        
                        # Show change reason dialog before updating
                        from ui.components.change_reason_dialog import show_change_reason_dialog
                        
                        def perform_update(change_reason: str):
                            debug_step(module_name, "submit_edit", "Calling asset_service.update_machine")
                            debug_service(module_name, "submit_edit", "asset_service.update_machine", {
                                "machine_id": machine.id,
                                "name": name_field.value,
                                "production_line_id": line_id,
                                "change_reason": change_reason
                            })
                            asset_service.update_machine(
                                machine_id=machine.id,
                                name=name_field.value,
                                production_line_id=line_id,
                                serial_number=serial_field.value or None,
                                model=model_field.value or None,
                                manufacturer=manufacturer_field.value or None,
                                manual_pdf_path=manual_field.value or None,
                                install_date=val_install_date,
                                status=status_field.value,
                                maintenance_interval=maintenance_field.value or None,
                                purchase_date=val_purchase_date,
                                purchase_price=val_purchase_price,
                                warranty_expiry_date=val_warranty_expiry,
                                supplier=supplier_field.value or None,
                                operating_hours=val_operating_hours,
                                last_service_date=val_last_service,
                                next_service_date=val_next_service,
                                criticality_level=criticality_field.value or None,
                                energy_consumption=energy_field.value or None,
                                power_requirements=power_req_field.value or None,
                                operating_temperature_range=temp_range_field.value or None,
                                weight=val_weight,
                                dimensions=dimensions_field.value or None,
                                notes=notes_field.value or None,
                                updated_by_user_id=user_id,
                                change_description=change_reason,
                                operating_hours_update_frequency_type=operating_hours_freq_type,
                                operating_hours_update_frequency_value=operating_hours_freq_value,
                            )
                            debug_step(module_name, "submit_edit", "update_machine completed successfully")
                            
                            debug_step(module_name, "submit_edit", "Closing dialog")
                            try:
                                dialog_page.close(dialog)
                                debug_step(module_name, "submit_edit", "Dialog closed successfully")
                            except Exception as close_exc:
                                debug_exception(module_name, "submit_edit", close_exc, {"action": "close_dialog"})
                                dialog.open = False
                                dialog_page.dialog = None
                                dialog_page.update()
                            
                            debug_ui(module_name, "submit_edit", "Showing success snackbar")
                            dialog_page.snack_bar = ft.SnackBar(content=ft.Text("Gép frissítve"), bgcolor="#10B981")
                            dialog_page.snack_bar.open = True
                            debug_step(module_name, "submit_edit", "Refreshing machine list")
                            refresh_list(update_page=True)
                            debug_exit(module_name, "submit_edit", {"success": True})
                        
                        # Show change reason dialog before updating
                        from ui.components.change_reason_dialog import show_change_reason_dialog
                        show_change_reason_dialog(
                            page=dialog_page,
                            entity_name=machine.name,
                            entity_type=translator.get_text("assets.machine") if hasattr(translator, 'get_text') else "Gép",
                            on_confirm=perform_update,
                        )
                    except Exception as exc:
                        debug_exception(module_name, "submit_edit", exc, {
                            "machine_id": machine.id,
                            "name_field_value": name_field.value if hasattr(name_field, 'value') else None,
                            "line_field_value": line_field.value if hasattr(line_field, 'value') else None
                        })
                        dialog_page.snack_bar = ft.SnackBar(content=ft.Text(f"Hiba: {exc}"), bgcolor="#EF4444")
                        dialog_page.snack_bar.open = True
                        dialog_page.update()
                        debug_exit(module_name, "submit_edit", {"success": False, "error": str(exc)})
                
                debug_step(module_name, function_name, "Creating dialog")
                # Modern, szép design a formhoz
                dialog = ft.AlertDialog(
                modal=True,
                title=ft.Row([
                    ft.Icon(ft.Icons.EDIT, color="#6366F1", size=24),
                    ft.Text(
                        "Gép szerkesztése",
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
                                    translator.get_text("common.messages.required_fields"),
                                    size=12,
                                    weight=ft.FontWeight.BOLD,
                                    color="#6B7280",
                                ),
                                name_field,
                                line_field,
                            ], spacing=8),
                            padding=ft.padding.only(bottom=10),
                        ),
                        ft.Divider(height=1, color="#E5E7EB"),
                        
                        # Alap információk
                        ft.Container(
                            content=ft.Column([
                                ft.Text(
                                    "Alap információk",
                                    size=12,
                                    weight=ft.FontWeight.BOLD,
                                    color="#6B7280",
                                ),
                                ft.Row([
                                    ft.Container(content=manufacturer_field, expand=1),
                                    ft.Container(content=model_field, expand=1, margin=ft.margin.only(left=10)),
                                ]),
                                serial_field,
                            ], spacing=8),
                            padding=ft.padding.only(top=10, bottom=10),
                        ),
                        ft.Divider(height=1, color="#E5E7EB"),
                        
                        # Státusz és dátum
                        ft.Container(
                            content=ft.Column([
                                ft.Text(
                                    "Státusz és dátum",
                                    size=12,
                                    weight=ft.FontWeight.BOLD,
                                    color="#6B7280",
                                ),
                                ft.Row([
                                    ft.Container(content=status_field, expand=1),
                                    ft.Container(content=install_date_field, expand=1, margin=ft.margin.only(left=10)),
                                ]),
                            ], spacing=8),
                            padding=ft.padding.only(top=10, bottom=10),
                        ),
                        ft.Divider(height=1, color="#E5E7EB"),
                        
                        # Karbantartás és dokumentáció
                        ft.Container(
                            content=ft.Column([
                                ft.Text(
                                    "Karbantartás és dokumentáció",
                                    size=12,
                                    weight=ft.FontWeight.BOLD,
                                    color="#6B7280",
                                ),
                                maintenance_field,
                                ft.Row([
                                    ft.Container(content=last_service_field, expand=1),
                                    ft.Container(content=next_service_field, expand=1, margin=ft.margin.only(left=10)),
                                ]),
                                    operating_hours_field,
                                    ft.Row([
                                        ft.Container(content=operating_hours_frequency_type_field_edit, expand=1),
                                        ft.Container(content=operating_hours_frequency_value_field_edit, expand=1, margin=ft.margin.only(left=10)),
                                    ]),
                                    manual_field,
                                ], spacing=8),
                                padding=ft.padding.only(top=10, bottom=10),
                            ),
                        ft.Divider(height=1, color="#E5E7EB"),
                        
                        # Vásárlás és garancia
                        ft.Container(
                            content=ft.Column([
                                ft.Text(
                                    "Vásárlás és garancia",
                                    size=12,
                                    weight=ft.FontWeight.BOLD,
                                    color="#6B7280",
                                ),
                                ft.Row([
                                    ft.Container(content=purchase_date_field, expand=1),
                                    ft.Container(content=purchase_price_field, expand=1, margin=ft.margin.only(left=10)),
                                ]),
                                ft.Row([
                                    ft.Container(content=warranty_expiry_field, expand=1),
                                    ft.Container(content=supplier_field, expand=1, margin=ft.margin.only(left=10)),
                                ]),
                            ], spacing=8),
                            padding=ft.padding.only(top=10, bottom=10),
                        ),
                        ft.Divider(height=1, color="#E5E7EB"),
                        
                        # Műszaki információk
                        ft.Container(
                            content=ft.Column([
                                ft.Text(
                                    "Műszaki információk",
                                    size=12,
                                    weight=ft.FontWeight.BOLD,
                                    color="#6B7280",
                                ),
                                ft.Row([
                                    ft.Container(content=energy_field, expand=1),
                                    ft.Container(content=power_req_field, expand=1, margin=ft.margin.only(left=10)),
                                ]),
                                ft.Row([
                                    ft.Container(content=temp_range_field, expand=1),
                                    ft.Container(content=weight_field, expand=1, margin=ft.margin.only(left=10)),
                                ]),
                                dimensions_field,
                            ], spacing=8),
                            padding=ft.padding.only(top=10, bottom=10),
                        ),
                        ft.Divider(height=1, color="#E5E7EB"),
                        
                        # További információk
                        ft.Container(
                            content=ft.Column([
                                ft.Text(
                                    "További információk",
                                    size=12,
                                    weight=ft.FontWeight.BOLD,
                                    color="#6B7280",
                                ),
                                asset_tag_field,
                                criticality_field,
                                notes_field,
                            ], spacing=8),
                            padding=ft.padding.only(top=10, bottom=10),
                        ),
                    ], 
                    tight=False,
                    spacing=12,
                    scroll=ft.ScrollMode.AUTO,
                    ),
                    width=700,
                    height=700,
                    padding=15,
                ),
                actions=[
                    ft.TextButton(
                        translator.get_text("common.buttons.cancel"),
                        on_click=lambda _: setattr(dialog, 'open', False) or dialog_page.update(),
                        style=ft.ButtonStyle(color="#6B7280"),
                    ),
                    ft.ElevatedButton(
                        translator.get_text("common.buttons.save"),
                        icon=ft.Icons.SAVE,
                        on_click=submit_edit,
                        style=ft.ButtonStyle(
                            bgcolor="#6366F1",
                            color="#FFFFFF",
                        ),
                    ),
                ],
                    actions_alignment=ft.MainAxisAlignment.END,
                )
                
                debug_step(module_name, function_name, "Attempting to open edit dialog")
                try:
                    dialog_page.open(dialog)
                    debug_step(module_name, function_name, "Edit dialog opened successfully using page.open()")
                    debug_variable(module_name, function_name, "dialog.open", dialog.open if hasattr(dialog, 'open') else None)
                except Exception as open_exc:
                    debug_exception(module_name, function_name, open_exc, {"action": "open_dialog", "method": "page.open()"})
                    debug_step(module_name, function_name, "Using fallback method to open dialog")
                    dialog_page.dialog = dialog
                    dialog.open = True
                    dialog_page.update()
                    debug_step(module_name, function_name, "Edit dialog opened using fallback method")
                    debug_variable(module_name, function_name, "dialog.open", dialog.open if hasattr(dialog, 'open') else None)
                    debug_variable(module_name, function_name, "page.dialog", dialog_page.dialog is not None if hasattr(dialog_page, 'dialog') else None)
                
                debug_exit(module_name, function_name, {"dialog_created": True, "dialog_opened": True})
            except Exception as e:
                debug_exception(module_name, function_name, e, {
                    "machine_id": machine.id if hasattr(machine, 'id') else None
                })
                debug_exit(module_name, function_name, {"success": False, "error": str(e)})
                raise
        
        def open_delete_machine_dialog(machine):
            """Open delete confirmation dialog"""
            dialog_page = self.page if hasattr(self, 'page') and self.page else page
            
            def confirm_delete(e):
                try:
                    ctx = get_app_context()
                    user_id = ctx.user_id if ctx.is_authenticated() else None
                    asset_service.delete_machine(machine.id, deleted_by_user_id=user_id)
                    try:
                        dialog_page.close(dialog)
                    except:
                        dialog.open = False
                        dialog_page.update()
                    dialog_page.snack_bar = ft.SnackBar(content=ft.Text("Gép törölve"), bgcolor="#10B981")
                    dialog_page.snack_bar.open = True
                    refresh_list(update_page=True)
                except Exception as exc:
                    dialog_page.snack_bar = ft.SnackBar(content=ft.Text(f"Hiba: {exc}"), bgcolor="#EF4444")
                    dialog_page.snack_bar.open = True
                dialog_page.update()
            
            dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Gép törlése"),
                content=ft.Text(f"Biztosan törölni szeretnéd a '{machine.name}' ({machine.serial_number or '-'}) gépet?"),
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

        refresh_list()

        # Create add button
        def open_add_service_dialog(machine):
            """Open add service record dialog"""
            dialog_page = self.page if hasattr(self, 'page') and self.page else page
            
            # Get machine with compatible parts
            machine_full = asset_service.get_machine_with_history(machine.id)
            compatible_parts = machine_full.id_compatible_parts if hasattr(machine_full, 'id_compatible_parts') else []
            
            service_date_field = ft.TextField(
                label="Szervizelés dátuma",
                value=datetime.now().strftime("%Y-%m-%d"),
                hint_text="YYYY-MM-DD",
                prefix_icon=ft.Icons.CALENDAR_TODAY,
            )
            service_type_field = ft.Dropdown(
                label="Szervizelés típusa",
                prefix_icon=ft.Icons.BUILD,
                options=[
                    ft.dropdown.Option("Preventive"),
                    ft.dropdown.Option("Corrective"),
                    ft.dropdown.Option("Emergency"),
                    ft.dropdown.Option("Inspection"),
                    ft.dropdown.Option("Other"),
                ],
            )
            performed_by_field = ft.TextField(
                label="Végrehajtó",
                prefix_icon=ft.Icons.BUSINESS,
            )
            technician_field = ft.TextField(
                label="Technikus neve",
                prefix_icon=ft.Icons.PERSON,
            )
            service_cost_field = ft.TextField(
                label="Szervizelés költsége",
                keyboard_type=ft.KeyboardType.NUMBER,
                hint_text="EUR",
                prefix_icon=ft.Icons.ATTACH_MONEY,
            )
            duration_field = ft.TextField(
                label="Időtartam (óra)",
                keyboard_type=ft.KeyboardType.NUMBER,
                prefix_icon=ft.Icons.ACCESS_TIME,
            )
            description_field = ft.TextField(
                label="Leírás",
                multiline=True,
                min_lines=3,
                prefix_icon=ft.Icons.DESCRIPTION,
            )
            notes_field = ft.TextField(
                label="Megjegyzések",
                multiline=True,
                min_lines=2,
                prefix_icon=ft.Icons.NOTE,
            )
            # Date picker for next service date - integrated into form
            next_service_date_value = [None]  # Use list to allow modification in nested functions
            date_picker_visible = [False]  # Track visibility of date picker fields
            
            next_service_display_field = ft.TextField(
                label="Következő szervizelés dátuma",
                hint_text="Kattints a naptár ikonra",
                read_only=True,
                prefix_icon=ft.Icons.SCHEDULE,
            )
            
            # Date picker fields (hidden by default)
            year_field = ft.TextField(
                label="Év",
                value=str(datetime.now().year),
                width=100,
                keyboard_type=ft.KeyboardType.NUMBER,
                dense=True,
                visible=False,
            )
            month_field = ft.TextField(
                label="Hónap",
                value=str(datetime.now().month),
                width=100,
                keyboard_type=ft.KeyboardType.NUMBER,
                dense=True,
                visible=False,
            )
            day_field = ft.TextField(
                label="Nap",
                value=str(datetime.now().day),
                width=100,
                keyboard_type=ft.KeyboardType.NUMBER,
                dense=True,
                visible=False,
            )
            
            def toggle_date_picker(e):
                """Toggle date picker fields visibility"""
                date_picker_visible[0] = not date_picker_visible[0]
                year_field.visible = date_picker_visible[0]
                month_field.visible = date_picker_visible[0]
                day_field.visible = date_picker_visible[0]
                date_picker_row.visible = date_picker_visible[0]
                
                if date_picker_visible[0]:
                    # Set default values if field is empty
                    if not next_service_display_field.value:
                        year_field.value = str(datetime.now().year)
                        month_field.value = str(datetime.now().month)
                        day_field.value = str(datetime.now().day)
                else:
                    # Try to parse and set the date when hiding
                    try:
                        year = int(year_field.value)
                        month = int(month_field.value)
                        day = int(day_field.value)
                        selected_date = datetime(year, month, day)
                        next_service_date_value[0] = selected_date
                        next_service_display_field.value = selected_date.strftime("%Y-%m-%d")
                    except:
                        pass
                
                dialog_page.update()
            
            def on_date_field_change(_):
                """Update display field when date fields change"""
                try:
                    year = int(year_field.value or datetime.now().year)
                    month = int(month_field.value or datetime.now().month)
                    day = int(day_field.value or datetime.now().day)
                    selected_date = datetime(year, month, day)
                    next_service_date_value[0] = selected_date
                    next_service_display_field.value = selected_date.strftime("%Y-%m-%d")
                    dialog_page.update()
                except:
                    pass
            
            year_field.on_change = on_date_field_change
            month_field.on_change = on_date_field_change
            day_field.on_change = on_date_field_change
            
            date_picker_row = ft.Row([
                year_field,
                month_field,
                day_field,
            ], spacing=8)
            date_picker_row.visible = False
            
            next_service_field = ft.Column([
                ft.Row([
                    ft.Container(content=next_service_display_field, expand=True),
                    ft.IconButton(
                        icon=ft.Icons.CALENDAR_MONTH,
                        tooltip="Dátum kiválasztása",
                        on_click=toggle_date_picker,
                        bgcolor="#6366F1",
                        icon_color="#FFFFFF",
                    ),
                ], spacing=8),
                date_picker_row,
            ], spacing=4, tight=True)
            
            # Compatible parts checkboxes with quantity
            selected_parts = {}  # {part_id: {'name': part_name, 'quantity': quantity}}
            part_rows = []
            for part in compatible_parts:
                quantity_field = ft.TextField(
                    label="db",
                    keyboard_type=ft.KeyboardType.NUMBER,
                    width=80,
                    dense=True,
                    value="1",
                    disabled=True,
                )
                
                checkbox = ft.Checkbox(
                    label=f"{part.name} ({part.sku})",
                    value=False,
                    data=part.id,
                )
                
                def on_part_change(e, part_id=part.id, part_name=part.name, qty_field=quantity_field):
                    if e.control.value:
                        qty_field.disabled = False
                        qty_value = qty_field.value or "1"
                        try:
                            qty = int(qty_value)
                        except:
                            qty = 1
                        selected_parts[part_id] = {'name': part_name, 'quantity': qty}
                    else:
                        qty_field.disabled = True
                        qty_field.value = "1"
                        selected_parts.pop(part_id, None)
                    dialog_page.update()
                
                def on_quantity_change(e, part_id=part.id, part_name=part.name):
                    if part_id in selected_parts:
                        qty_value = e.control.value or "1"
                        try:
                            qty = int(qty_value)
                            if qty > 0:
                                selected_parts[part_id]['quantity'] = qty
                        except:
                            pass
                
                checkbox.on_change = on_part_change
                quantity_field.on_change = on_quantity_change
                
                row = ft.Row([
                    checkbox,
                    quantity_field,
                ], spacing=8)
                part_rows.append(row)
            
            compatible_parts_list = ft.Column(
                controls=part_rows if part_rows else [ft.Text("Nincs kompatibilis alkatrész", size=12, color="#9CA3AF", italic=True)],
                scroll=ft.ScrollMode.AUTO,
                height=150,
            )
            
            # Other parts list (custom parts with name and price)
            other_parts_list = ft.Column([], spacing=4, scroll=ft.ScrollMode.AUTO, height=150)
            other_parts_data = []  # List of {name: str, price: float}
            
            def add_other_part():
                """Add a new other part row"""
                part_name_field = ft.TextField(
                    label="Alkatrész neve",
                    width=200,
                    dense=True,
                )
                part_price_field = ft.TextField(
                    label="Ár (EUR)",
                    keyboard_type=ft.KeyboardType.NUMBER,
                    width=150,
                    dense=True,
                )
                
                def remove_part(row_container):
                    other_parts_list.controls.remove(row_container)
                    dialog_page.update()
                
                row = ft.Container(
                    content=ft.Row([
                        part_name_field,
                        part_price_field,
                        ft.IconButton(
                            icon=ft.Icons.DELETE,
                            icon_color="#EF4444",
                            tooltip="Eltávolítás",
                            on_click=lambda _: remove_part(row),
                        ),
                    ], spacing=8),
                    padding=4,
                )
                other_parts_list.controls.append(row)
                dialog_page.update()
            
            add_other_part_btn = ft.ElevatedButton(
                "+ Egyéb alkatrész hozzáadása",
                icon=ft.Icons.ADD,
                on_click=lambda _: add_other_part(),
                bgcolor="#10B981",
                color="#FFFFFF",
                height=35,
            )
            
            def submit_service(_):
                try:
                    def parse_date(date_str):
                        if not date_str:
                            return None
                        return datetime.strptime(date_str, "%Y-%m-%d")
                    
                    def parse_float(value_str):
                        if not value_str:
                            return None
                        try:
                            return float(value_str)
                        except ValueError:
                            return None
                    
                    val_service_date = parse_date(service_date_field.value)
                    if not val_service_date:
                        raise ValueError("Szervizelés dátuma kötelező")
                    
                    val_next_service = next_service_date_value[0]
                    val_cost = parse_float(service_cost_field.value)
                    val_duration = parse_float(duration_field.value)
                    
                    # Build parts replaced string
                    parts_list = []
                    # Add selected compatible parts with quantity
                    for part_id, part_data in selected_parts.items():
                        part_name = part_data['name']
                        quantity = part_data.get('quantity', 1)
                        if quantity > 1:
                            parts_list.append(f"{part_name} ({quantity} db)")
                        else:
                            parts_list.append(part_name)
                    # Add other parts with prices
                    for row in other_parts_list.controls:
                        if isinstance(row.content, ft.Row):
                            name_field = None
                            price_field = None
                            for control in row.content.controls:
                                if isinstance(control, ft.TextField):
                                    if control.label == "Alkatrész neve":
                                        name_field = control
                                    elif control.label == "Ár (EUR)":
                                        price_field = control
                            if name_field and name_field.value:
                                part_info = name_field.value
                                if price_field and price_field.value:
                                    try:
                                        price = float(price_field.value)
                                        part_info += f" ({format_price(price)})"
                                    except:
                                        pass
                                parts_list.append(part_info)
                    
                    parts_replaced_text = ", ".join(parts_list) if parts_list else None
                    
                    ctx = get_app_context()
                    user_id = ctx.user_id if ctx.is_authenticated() else None
                    
                    service_record_service.create_service_record(
                        machine_id=machine.id,
                        service_date=val_service_date,
                        service_type=service_type_field.value or None,
                        performed_by=performed_by_field.value or None,
                        technician_name=technician_field.value or None,
                        service_cost=val_cost,
                        service_duration_hours=val_duration,
                        description=description_field.value or None,
                        notes=notes_field.value or None,
                        next_service_date=val_next_service,
                        parts_replaced=parts_replaced_text,
                        created_by_user_id=user_id,
                    )
                    
                    try:
                        dialog_page.close(dialog)
                    except:
                        dialog.open = False
                        dialog_page.update()
                    
                    dialog_page.snack_bar = ft.SnackBar(content=ft.Text("Szervizelés hozzáadva"), bgcolor="#10B981")
                    dialog_page.snack_bar.open = True
                    refresh_list(update_page=True)
                except Exception as exc:
                    dialog_page.snack_bar = ft.SnackBar(content=ft.Text(f"Hiba: {exc}"), bgcolor="#EF4444")
                    dialog_page.snack_bar.open = True
                dialog_page.update()
            
            dialog = ft.AlertDialog(
                modal=True,
                title=ft.Row([
                    ft.Icon(ft.Icons.BUILD_CIRCLE, color="#6366F1", size=24),
                    ft.Text("Szervizelés hozzáadása", size=20, weight=ft.FontWeight.BOLD, color="#1F2937"),
                ], spacing=10),
                content=ft.Container(
                    content=ft.Column([
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Alap információk", size=12, weight=ft.FontWeight.BOLD, color="#6B7280"),
                                ft.Row([
                                    ft.Container(content=service_date_field, expand=1),
                                    ft.Container(content=service_type_field, expand=1, margin=ft.margin.only(left=10)),
                                ]),
                                ft.Row([
                                    ft.Container(content=performed_by_field, expand=1),
                                    ft.Container(content=technician_field, expand=1, margin=ft.margin.only(left=10)),
                                ]),
                            ], spacing=8),
                            padding=ft.padding.only(bottom=10),
                        ),
                        ft.Divider(height=1, color="#E5E7EB"),
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Költség és időtartam", size=12, weight=ft.FontWeight.BOLD, color="#6B7280"),
                                ft.Row([
                                    ft.Container(content=service_cost_field, expand=1),
                                    ft.Container(content=duration_field, expand=1, margin=ft.margin.only(left=10)),
                                ]),
                            ], spacing=8),
                            padding=ft.padding.only(top=10, bottom=10),
                        ),
                        ft.Divider(height=1, color="#E5E7EB"),
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Részletek", size=12, weight=ft.FontWeight.BOLD, color="#6B7280"),
                                description_field,
                                notes_field,
                                next_service_field,
                            ], spacing=8),
                            padding=ft.padding.only(top=10, bottom=10),
                        ),
                        ft.Divider(height=1, color="#E5E7EB"),
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Cserélt alkatrészek", size=12, weight=ft.FontWeight.BOLD, color="#6B7280"),
                                ft.Text("Kompatibilis alkatrészek:", size=11, color="#6B7280"),
                                ft.Container(
                                    content=compatible_parts_list,
                                    border=ft.border.all(1, "#E5E7EB"),
                                    border_radius=5,
                                    padding=8,
                                    bgcolor="#F9FAFB",
                                ),
                                ft.Container(height=10),
                                ft.Text("Egyéb alkatrészek:", size=11, color="#6B7280"),
                                add_other_part_btn,
                                ft.Container(
                                    content=other_parts_list,
                                    border=ft.border.all(1, "#E5E7EB"),
                                    border_radius=5,
                                    padding=8,
                                    bgcolor="#F9FAFB",
                                ),
                            ], spacing=8),
                            padding=ft.padding.only(top=10, bottom=10),
                        ),
                    ], tight=False, spacing=12, scroll=ft.ScrollMode.AUTO),
                    width=750, height=750, padding=15,
                ),
                actions=[
                    ft.TextButton("Mégse", on_click=lambda _: setattr(dialog, 'open', False) or dialog_page.update(), style=ft.ButtonStyle(color="#6B7280")),
                    ft.ElevatedButton("Hozzáadás", icon=ft.Icons.ADD, on_click=submit_service, style=ft.ButtonStyle(bgcolor="#6366F1", color="#FFFFFF")),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            
            try:
                dialog_page.open(dialog)
            except:
                dialog_page.dialog = dialog
                dialog.open = True
                dialog_page.update()
        
        def open_service_records_view(e):
            """Open service records overview screen"""
            print(f"[ASSETS] open_service_records_view called, event: {e}")
            dialog_page = self.page if hasattr(self, 'page') and self.page else page
            print(f"[ASSETS] Using page: {dialog_page}, current route: {getattr(dialog_page, 'route', 'unknown')}")
            try:
                print("[ASSETS] Calling page.go('/service_records')")
                dialog_page.go("/service_records")
                print(f"[ASSETS] Navigation called, new route: {getattr(dialog_page, 'route', 'unknown')}")
            except Exception as ex:
                print(f"[ASSETS] Error navigating to service_records: {ex}")
                import traceback
                traceback.print_exc()
                dialog_page.snack_bar = ft.SnackBar(content=ft.Text(f"Hiba a navigációban: {ex}"), bgcolor="#EF4444")
                dialog_page.snack_bar.open = True
                dialog_page.update()
        
        add_btn = ft.ElevatedButton(
            text="+ Hozzáadás",
            icon=ft.Icons.ADD,
            tooltip=translator.get_text("assets.create_machine"),
            on_click=open_add_dialog,
            bgcolor="#6366F1",
            color="#FFFFFF",
            height=40,
        )
        
        service_records_btn = ft.ElevatedButton(
            text="Szervizelések áttekintése",
            icon=ft.Icons.HISTORY,
            tooltip="Összes szervizelés megtekintése",
            on_click=open_service_records_view,
            bgcolor="#10B981",
            color="#FFFFFF",
            height=40,
        )

        return ft.Column([
            ft.Row([
                ft.Text(translator.get_text("assets.title"), size=18, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                service_records_btn,
                ft.Container(width=10),
                add_btn,
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            machines_list,
        ], spacing=12, expand=True)
