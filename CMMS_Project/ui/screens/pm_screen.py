"""
PM képernyő - Megelőző karbantartás
"""

import flet as ft
# Compatibility for flet 0.23.2 - Icons are strings, not ft.Icons
if not hasattr(ft, 'Icons'):
    from utils.flet_icons import Icons
    ft.Icons = Icons
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from pathlib import Path
from services import pm_service, asset_service, service_record_service, user_service
from services.settings_service import get_maintenance_notification_settings
from services.context_service import get_app_context
from database.models import utcnow
from localization.translator import translator
from utils.currency import format_price
from utils.permissions import can_edit_pm
from ui.components.modern_components import (
    create_modern_button,
    create_modern_card,
    create_modern_text_field,
    create_modern_dropdown,
    create_modern_dialog,
    create_modern_badge,
    create_vibrant_badge,
    create_modern_icon_button,
    create_modern_divider,
    create_empty_state_card,
    DesignSystem,
)
from ui.components.modern_card import (
    create_tailwind_card,
    create_info_card,
)


class PMScreen:
    def __init__(self):
        self.page = None
    
    def view(self, page: ft.Page):
        self.page = page
        
        # Get current user for filtering
        ctx = get_app_context()
        current_user_id = ctx.user_id if ctx.is_authenticated() else None
        
        # Get PM tasks filtered by user (show global tasks or tasks assigned to current user)
        due_tasks = pm_service.list_due_tasks(user_id=current_user_id)
        
        # Get maintenance notification settings
        notif_settings = get_maintenance_notification_settings()
        days_ahead = (
            notif_settings['months_ahead'] * 30 +
            notif_settings['weeks_ahead'] * 7 +
            notif_settings['days_ahead'] +
            notif_settings['hours_ahead'] / 24
        )
        
        # Get machines with upcoming service
        machines_with_service = asset_service.get_machines_with_upcoming_service(int(days_ahead))
        
        # Get machines with due operating hours update
        machines_with_due_operating_hours = asset_service.get_machines_with_due_operating_hours_update()
        
        def open_maintenance_overview():
            """Open dialog with all maintenance records"""
            dialog_page = self.page if self.page else page
            
            # Get all service records
            all_records = service_record_service.get_service_records(limit=None)
            
            # Calculate total cost
            total_cost = sum(record.service_cost or 0 for record in all_records)
            
            # Build records list
            records_list = ft.Column([], spacing=8, scroll=ft.ScrollMode.AUTO, height=500)
            
            if not all_records:
                records_list.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(name=ft.Icons.HISTORY, size=48, color=DesignSystem.TEXT_TERTIARY),
                            ft.Text("Nincs rögzített karbantartás", size=16, color=DesignSystem.TEXT_SECONDARY),
                        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=40,
                    )
                )
            else:
                for record in all_records:
                    machine_name = record.machine.name if record.machine else f"Gép ID: {record.machine_id}"
                    card = create_modern_card(
                        content=ft.Column([
                            ft.Row([
                                ft.Column([
                                    ft.Text(
                                        f"{record.service_type or 'N/A'} - {machine_name}",
                                        size=14,
                                        weight=ft.FontWeight.W_600,
                                        color=DesignSystem.TEXT_PRIMARY,
                                    ),
                                    ft.Text(
                                        f"{record.service_date.strftime('%Y-%m-%d %H:%M') if record.service_date else '-'}",
                                        size=12,
                                        color=DesignSystem.TEXT_SECONDARY,
                                    ),
                                ], expand=True),
                                ft.Text(
                                    format_price(record.service_cost or 0),
                                    size=16,
                                    weight=ft.FontWeight.W_600,
                                    color=DesignSystem.SECONDARY,
                                ),
                            ], spacing=DesignSystem.SPACING_SM),
                            create_modern_divider(),
                            ft.Row([
                                ft.Text(f"Végrehajtó: {record.performed_by or '-'}", size=11, color=DesignSystem.TEXT_SECONDARY),
                                ft.Container(width=DesignSystem.SPACING_MD),
                                ft.Text(f"Technikus: {record.technician_name or '-'}", size=11, color=DesignSystem.TEXT_SECONDARY),
                            ]),
                            ft.Row([
                                ft.Container(expand=True),
                                ft.Text(f"Időtartam: {int((record.service_duration_hours or 0) * 60)} perc" if record.service_duration_hours else "Időtartam: -", size=11, color=DesignSystem.TEXT_SECONDARY),
                            ]),
                            ft.Text(f"Cserélt alkatrészek: {record.parts_replaced or 'Nincs'}", size=11, color=DesignSystem.TEXT_SECONDARY) if record.parts_replaced else ft.Container(),
                            ft.Text(f"Megjegyzés: {record.notes or '-'}", size=11, color=DesignSystem.TEXT_TERTIARY, italic=True) if record.notes else ft.Container(),
                        ], spacing=DesignSystem.SPACING_XS, tight=True),
                        padding=DesignSystem.SPACING_MD,
                    )
                    records_list.controls.append(card)
            
            # Total cost summary
            total_summary = ft.Container(
                content=ft.Row([
                    ft.Text("Összes költség:", size=16, weight=ft.FontWeight.W_600, color=DesignSystem.TEXT_PRIMARY),
                    ft.Container(expand=True),
                    ft.Text(
                        format_price(total_cost),
                        size=20,
                        weight=ft.FontWeight.W_700,
                        color=DesignSystem.SUCCESS,
                    ),
                ], spacing=8),
                padding=DesignSystem.SPACING_MD,
                bgcolor=DesignSystem.PRIMARY_LIGHT,
                border_radius=8,
            )
            
            dialog = ft.AlertDialog(
                modal=True,
                title=ft.Row([
                    ft.Icon(ft.Icons.HISTORY, color="#6366F1", size=24),
                    ft.Text("Karbantartások áttekintése", size=20, weight=ft.FontWeight.BOLD, color="#1F2937"),
                ], spacing=10),
                content=ft.Container(
                    content=ft.Column([
                        total_summary,
                        ft.Container(height=10),
                        ft.Text(f"Összesen {len(all_records)} karbantartás", size=12, color="#6B7280"),
                        ft.Divider(height=1, color="#E5E7EB"),
                        records_list,
                    ], spacing=8, tight=False, scroll=ft.ScrollMode.AUTO),
                    width=800,
                    height=650,
                    padding=15,
                ),
                actions=[
                    ft.TextButton(
                        "Bezárás",
                        on_click=lambda _: setattr(dialog, 'open', False) or dialog_page.update(),
                        style=ft.ButtonStyle(color="#6B7280")
                    ),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            
            try:
                dialog_page.open(dialog)
            except:
                dialog_page.dialog = dialog
                dialog.open = True
                dialog_page.update()
        
        # PM Tasks section
        pm_tasks_list = ft.Column([], spacing=8, scroll=ft.ScrollMode.AUTO)
        completed_tasks_list = ft.Column([], spacing=8, scroll=ft.ScrollMode.AUTO)
        
        def refresh_pm_tasks():
            pm_tasks_list.controls.clear()
            completed_tasks_list.controls.clear()
            # Get all active tasks (not just due ones) for the current user
            tasks = pm_service.list_pm_tasks(user_id=current_user_id, status=None)
            
            # Separate pending/in_progress tasks from completed tasks
            pending_tasks = [t for t in tasks if t.status != "completed"]
            completed_tasks = [t for t in tasks if t.status == "completed"]
            
            if not pending_tasks and not completed_tasks:
                pm_tasks_list.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(name=ft.Icons.BUILD, size=48, color="#9CA3AF"),
                            ft.Text(translator.get_text("empty_states.no_pm_tasks"), size=16, color="#6B7280"),
                        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=40,
                    )
                )
            else:
                # Display pending/in_progress tasks
                for task in pending_tasks:
                    if task.machine_id:
                        machine_name = task.machine.name if hasattr(task, 'machine') and task.machine else f"Gép ID: {task.machine_id}"
                    else:
                        machine_name = f"{translator.get_text('preventive_maintenance.other')}: {task.location or '-'}"
                    
                    # Priority color
                    priority_colors = {
                        "urgent": "#EF4444",
                        "high": "#F59E0B",
                        "normal": "#6366F1",
                        "low": "#6B7280"
                    }
                    priority_color = priority_colors.get(task.priority or "normal", "#6B7280")
                    
                    # Status color
                    status_colors = {
                        "pending": "#F59E0B",
                        "in_progress": "#6366F1",
                        "completed": "#10B981",
                        "cancelled": "#6B7280"
                    }
                    status_color = status_colors.get(task.status or "pending", "#6B7280")
                    
                    def open_complete_dialog(t=task):
                        """Open modern dialog to fill in comprehensive completion details"""
                        dialog_page = self.page if self.page else page
                        from datetime import datetime
                        
                        # Get current datetime for completion
                        now = datetime.now()
                        completion_date_str = now.strftime("%Y-%m-%d")
                        completion_time_str = now.strftime("%H:%M")
                        
                        # Section 1: Basic Information
                        completion_date_field = create_modern_text_field(
                            label=translator.get_text("preventive_maintenance.completion_date") if hasattr(translator, 'get_text') else "Befejezés dátuma",
                            value=completion_date_str,
                            width=250,
                        )
                        completion_time_field = create_modern_text_field(
                            label=translator.get_text("preventive_maintenance.completion_time") if hasattr(translator, 'get_text') else "Befejezés időpontja",
                            value=completion_time_str,
                            width=200,
                        )
                        duration_field = create_modern_text_field(
                            label=translator.get_text("preventive_maintenance.duration_minutes"),
                            value=str(t.estimated_duration_minutes) if t.estimated_duration_minutes else "",
                            width=200,
                            keyboard_type=ft.KeyboardType.NUMBER,
                        )
                        
                        # Section 2: Work Details
                        work_description_field = create_modern_text_field(
                            label=translator.get_text("preventive_maintenance.work_description") if hasattr(translator, 'get_text') else "Elvégzett munkák részletes leírása",
                            hint_text=translator.get_text("preventive_maintenance.work_description_hint") if hasattr(translator, 'get_text') else "Írd le részletesen, mit végeztél el...",
                            multiline=True,
                            max_lines=6,
                            width=600,
                        )
                        observations_field = create_modern_text_field(
                            label=translator.get_text("preventive_maintenance.observations") if hasattr(translator, 'get_text') else "Megfigyelések / Problémák",
                            hint_text=translator.get_text("preventive_maintenance.observations_hint") if hasattr(translator, 'get_text') else "Vannak-e észrevételek, problémák, javaslatok?",
                            multiline=True,
                            max_lines=4,
                            width=600,
                        )
                        
                        # Section 3: Status
                        completion_status_field = create_modern_dropdown(
                            label=translator.get_text("preventive_maintenance.completion_status") if hasattr(translator, 'get_text') else "Befejezés státusza",
                            options=[
                                ft.dropdown.Option("completed", translator.get_text("preventive_maintenance.status_completed") if hasattr(translator, 'get_text') else "Sikeresen elvégezve"),
                                ft.dropdown.Option("partial", translator.get_text("preventive_maintenance.status_partial") if hasattr(translator, 'get_text') else "Részben elvégezve"),
                                ft.dropdown.Option("issues", translator.get_text("preventive_maintenance.status_issues") if hasattr(translator, 'get_text') else "Problémák voltak"),
                            ],
                            value="completed",
                            width=300,
                        )
                        
                        # Section 4: Notes (general)
                        notes_field = create_modern_text_field(
                            label=translator.get_text("preventive_maintenance.notes"),
                            hint_text=translator.get_text("preventive_maintenance.notes_hint") if hasattr(translator, 'get_text') else "Egyéb megjegyzések...",
                            multiline=True,
                            max_lines=4,
                            width=600,
                        )
                        
                        # Section 5: File Uploads (images and documents)
                        selected_files = []  # Store selected file paths
                        selected_files_display = ft.Column([], spacing=4)  # Display list of selected files
                        
                        def on_files_picked(e: ft.FilePickerResultEvent):
                            """Handle file picker result"""
                            if e.files:
                                selected_files.clear()
                                selected_files.extend([f.path for f in e.files])
                                
                                # Update display list
                                selected_files_display.controls.clear()
                                for file_path in selected_files:
                                    file_name = Path(file_path).name
                                    selected_files_display.controls.append(
                                        ft.Row([
                                            ft.Icon(
                                                ft.Icons.INSERT_PHOTO if file_name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')) else ft.Icons.INSERT_DRIVE_FILE,
                                                size=16,
                                                color=DesignSystem.TEXT_SECONDARY,
                                            ),
                                            ft.Text(file_name, size=12, color=DesignSystem.TEXT_SECONDARY, expand=True),
                                            ft.IconButton(
                                                icon=ft.Icons.DELETE_OUTLINE,
                                                icon_size=16,
                                                tooltip="Eltávolítás / Remove",
                                                on_click=lambda _, path=file_path: remove_file(path),
                                            ),
                                        ], spacing=8)
                                    )
                                page.update()
                        
                        file_picker = ft.FilePicker(on_result=on_files_picked)
                        dialog_page.overlay.append(file_picker)
                        
                        def pick_files(e):
                            """Open file picker"""
                            file_picker.pick_files(
                                dialog_title=translator.get_text("preventive_maintenance.select_files") if hasattr(translator, 'get_text') else "Fájlok kiválasztása / Select Files",
                                allow_multiple=True,
                                allowed_extensions=["jpg", "jpeg", "png", "gif", "bmp", "pdf", "doc", "docx", "xls", "xlsx", "txt"],
                            )
                        
                        def remove_file(file_path):
                            """Remove a file from the selected files list"""
                            if file_path in selected_files:
                                selected_files.remove(file_path)
                                # Rebuild display list
                                selected_files_display.controls.clear()
                                for fp in selected_files:
                                    file_name = Path(fp).name
                                    selected_files_display.controls.append(
                                        ft.Row([
                                            ft.Icon(
                                                ft.Icons.INSERT_PHOTO if file_name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')) else ft.Icons.INSERT_DRIVE_FILE,
                                                size=16,
                                                color=DesignSystem.TEXT_SECONDARY,
                                            ),
                                            ft.Text(file_name, size=12, color=DesignSystem.TEXT_SECONDARY, expand=True),
                                            ft.IconButton(
                                                icon=ft.Icons.DELETE_OUTLINE,
                                                icon_size=16,
                                                tooltip="Eltávolítás / Remove",
                                                on_click=lambda _, path=fp: remove_file(path),
                                            ),
                                        ], spacing=8)
                                    )
                                page.update()
                        
                        files_section = ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Text(
                                        translator.get_text("preventive_maintenance.attach_files") if hasattr(translator, 'get_text') else "Fájlok csatolása / Attach Files",
                                        size=14,
                                        weight=ft.FontWeight.BOLD,
                                        color=DesignSystem.TEXT_PRIMARY,
                                        expand=True,
                                    ),
                                    create_modern_button(
                                        text=translator.get_text("preventive_maintenance.select_files") if hasattr(translator, 'get_text') else "Fájlok kiválasztása",
                                        icon=ft.Icons.ATTACH_FILE,
                                        on_click=pick_files,
                                        variant="outlined",
                                    ),
                                ], spacing=8),
                                ft.Divider(height=1, color=DesignSystem.BORDER_COLOR),
                                ft.Container(height=8),
                                selected_files_display,
                                ft.Text(
                                    translator.get_text("preventive_maintenance.files_hint") if hasattr(translator, 'get_text') else "Támogatott formátumok: Képek (JPG, PNG, GIF, BMP), Dokumentumok (PDF, DOC, DOCX, XLS, XLSX, TXT)",
                                    size=11,
                                    color=DesignSystem.TEXT_SECONDARY,
                                    italic=True,
                                ),
                            ], spacing=8),
                            padding=ft.padding.all(16),
                            bgcolor=DesignSystem.BG_TERTIARY,
                            border_radius=DesignSystem.RADIUS_MD,
                        )
                        
                        # Load compatible parts if machine is assigned
                        parts_section = ft.Container()
                        part_quantity_fields = {}  # Store quantity fields for each part
                        part_storage_pickers = {}  # Store storage location pickers for each part
                        
                        if t.machine_id and hasattr(t, 'machine') and t.machine:
                            from services import inventory_service
                            from database.session_manager import SessionLocal
                            from database.models import Machine, InventoryLevel
                            from sqlalchemy.orm import joinedload
                            session = SessionLocal()
                            try:
                                # Get machine with compatible parts
                                machine = session.query(Machine).options(
                                    joinedload(Machine.id_compatible_parts)
                                ).filter_by(id=t.machine_id).first()
                                
                                if machine and machine.id_compatible_parts:
                                    parts_list = []
                                    for part in machine.id_compatible_parts:
                                        # Get current stock level
                                        inv_level = session.query(InventoryLevel).filter_by(part_id=part.id).first()
                                        stock_qty = inv_level.quantity_on_hand if inv_level else 0
                                        
                                        # Create modern quantity field for this part
                                        qty_field = create_modern_text_field(
                                            label=f"{part.name} ({part.sku})",
                                            hint_text=f"{translator.get_text('preventive_maintenance.quantity_on_hand') if hasattr(translator, 'get_text') else 'Raktáron'}: {stock_qty} {part.unit}",
                                            value="0",
                                            width=300,
                                            keyboard_type=ft.KeyboardType.NUMBER,
                                        )
                                        part_quantity_fields[part.id] = qty_field
                                        
                                        # Create storage location picker for this part (filtered to locations with this part)
                                        from ui.components.storage_location_picker import StorageLocationPicker
                                        storage_picker = StorageLocationPicker(page=dialog_page)
                                        storage_location_picker = storage_picker.build(
                                            label=translator.get_text("storage.location") if hasattr(translator, 'get_text') else "Raktárhely",
                                            width=300,
                                            part_id=part.id,  # Filter to only show locations that have this part
                                        )
                                        part_storage_pickers[part.id] = storage_picker
                                        
                                        parts_list.append(
                                            ft.Row([
                                                qty_field,
                                                ft.Container(
                                                    content=ft.Text(f"({part.unit})", size=12, color=DesignSystem.TEXT_SECONDARY),
                                                    padding=ft.padding.only(top=32),
                                                ),
                                                storage_location_picker,
                                            ], spacing=8)
                                        )
                                    
                                    if parts_list:
                                        parts_section = ft.Container(
                                            content=ft.Column([
                                                ft.Text(
                                                    translator.get_text("inventory.parts_used") if hasattr(translator, 'get_text') else "Felhasznált alkatrészek",
                                                    size=14,
                                                    weight=ft.FontWeight.BOLD,
                                                    color=DesignSystem.TEXT_PRIMARY,
                                                ),
                                                ft.Divider(height=1, color=DesignSystem.BORDER_COLOR),
                                                ft.Container(height=8),
                                                ft.Column(parts_list, spacing=8, scroll=ft.ScrollMode.AUTO),
                                            ], spacing=4),
                                            padding=ft.padding.all(16),
                                            bgcolor=DesignSystem.BG_TERTIARY,
                                            border_radius=DesignSystem.RADIUS_MD,
                                        )
                                    else:
                                        parts_section = ft.Container(
                                            content=ft.Column([
                                                ft.Text(
                                                    translator.get_text("inventory.parts_used") if hasattr(translator, 'get_text') else "Felhasznált alkatrészek",
                                                    size=14,
                                                    weight=ft.FontWeight.BOLD,
                                                    color=DesignSystem.TEXT_PRIMARY,
                                                ),
                                                ft.Divider(height=1, color=DesignSystem.BORDER_COLOR),
                                                ft.Container(height=8),
                                                ft.Text(
                                                    translator.get_text("preventive_maintenance.no_compatible_parts") if hasattr(translator, 'get_text') else "Nincs kompatibilis alkatrész",
                                                    size=12,
                                                    color=DesignSystem.TEXT_SECONDARY,
                                                    italic=True,
                                                ),
                                            ], spacing=4),
                                            padding=ft.padding.all(16),
                                            bgcolor=DesignSystem.BG_TERTIARY,
                                            border_radius=DesignSystem.RADIUS_MD,
                                        )
                            finally:
                                session.close()
                        
                        def submit_completion(e):
                            print(f"[PM] ====== submit_completion CALLED ======")
                            print(f"[PM] Event: {e}, type: {type(e)}")
                            print(f"[PM] Task ID: {t.id}")
                            print(f"[PM] Current user ID: {current_user_id}")
                            try:
                                print(f"[PM] Parsing completion date and time...")
                                # Parse completion date and time
                                completion_date_str = completion_date_field.value.strip() if completion_date_field.value else completion_date_str
                                completion_time_str = completion_time_field.value.strip() if completion_time_field.value else completion_time_str
                                print(f"[PM] Date: {completion_date_str}, Time: {completion_time_str}")
                                
                                # Combine date and time
                                try:
                                    completion_datetime = datetime.strptime(f"{completion_date_str} {completion_time_str}", "%Y-%m-%d %H:%M")
                                    print(f"[PM] Parsed datetime: {completion_datetime}")
                                except Exception as dt_ex:
                                    print(f"[PM] Error parsing datetime: {dt_ex}, using now()")
                                    completion_datetime = datetime.now()
                                
                                # Get duration
                                duration_str = duration_field.value.strip() if duration_field.value else None
                                duration_minutes = int(duration_str) if duration_str and duration_str.isdigit() else (t.estimated_duration_minutes or 0)
                                print(f"[PM] Duration: {duration_minutes} minutes")
                                
                                # Get work description and observations
                                work_description = work_description_field.value.strip() if work_description_field.value else None
                                observations = observations_field.value.strip() if observations_field.value else None
                                completion_status = completion_status_field.value if completion_status_field.value else "completed"
                                print(f"[PM] Work description length: {len(work_description) if work_description else 0}")
                                print(f"[PM] Observations length: {len(observations) if observations else 0}")
                                print(f"[PM] Completion status: {completion_status}")
                                
                                # Combine all notes
                                notes_parts = []
                                if work_description:
                                    notes_parts.append(f"Elvégzett munkák:\n{work_description}")
                                if observations:
                                    notes_parts.append(f"Megfigyelések:\n{observations}")
                                if notes_field.value and notes_field.value.strip():
                                    notes_parts.append(f"Megjegyzések:\n{notes_field.value.strip()}")
                                
                                notes = "\n\n".join(notes_parts) if notes_parts else None
                                
                                print(f"[PM] Completing task {t.id} with status={completion_status}, duration={duration_minutes}, notes length={len(notes) if notes else 0}")
                                print(f"[PM] Calling pm_service.complete_pm_task...")
                                
                                # Complete the PM task and create worksheet
                                # Returns (pm_history, worksheet_id) to avoid detached instance issues
                                print(f"[PM] Calling pm_service.complete_pm_task(task_id={t.id}, completed_by_user_id={current_user_id}, duration_minutes={duration_minutes})...")
                                pm_history, worksheet_id = pm_service.complete_pm_task(
                                    task_id=t.id,
                                    completed_by_user_id=current_user_id,
                                    notes=notes,
                                    duration_minutes=duration_minutes,
                                    create_worksheet=True
                                )
                                print(f"[PM] pm_service.complete_pm_task returned: pm_history={pm_history}, worksheet_id={worksheet_id}")
                                
                                # Add parts to worksheet if any were used
                                if worksheet_id and part_quantity_fields:
                                    from services import worksheet_service
                                    for part_id, qty_field in part_quantity_fields.items():
                                        try:
                                            qty_value = qty_field.value.strip() if qty_field.value else "0"
                                            quantity = int(qty_value) if qty_value.isdigit() else 0
                                            if quantity > 0:
                                                # Get storage location if picker exists
                                                storage_location_id = None
                                                if part_id in part_storage_pickers:
                                                    location_id, other_location = part_storage_pickers[part_id].get_value()
                                                    storage_location_id = location_id if location_id else None
                                                
                                                # Get part to get current price
                                                from database.session_manager import SessionLocal
                                                from database.models import Part
                                                session = SessionLocal()
                                                try:
                                                    part = session.query(Part).filter_by(id=part_id).first()
                                                    if part:
                                                        worksheet_part = worksheet_service.add_part_to_worksheet(
                                                            worksheet_id=worksheet_id,
                                                            part_id=part_id,
                                                            quantity_used=quantity,
                                                            unit_cost_at_time=part.buy_price or 0.0,
                                                            user_id=current_user_id,
                                                            storage_location_id=storage_location_id
                                                        )
                                                        print(f"[PM] Added {quantity} x {part.name} to worksheet {worksheet_id} from location {storage_location_id}")
                                                        print(f"[PM] Generated {quantity} scrapping documents for part {part.name}")
                                                finally:
                                                    session.close()
                                        except Exception as part_ex:
                                            print(f"[PM] Error adding part {part_id} to worksheet: {part_ex}")
                                
                                # Save uploaded files if any
                                if selected_files and pm_history:
                                    try:
                                        print(f"[PM] Saving {len(selected_files)} uploaded files...")
                                        pm_service.save_pm_task_attachments(
                                            pm_history_id=pm_history.id,
                                            file_paths=selected_files,
                                            uploaded_by_user_id=current_user_id
                                        )
                                        print(f"[PM] Files saved successfully")
                                    except Exception as file_ex:
                                        print(f"[PM] Error saving files: {file_ex}")
                                        import traceback
                                        traceback.print_exc()
                                        # Don't fail the whole completion if file save fails
                                
                                # Copy generated documents to PM task directory
                                if pm_history:
                                    try:
                                        print(f"[PM] Copying generated documents to PM task directory...")
                                        pm_service.copy_pm_task_documents_to_directory(
                                            pm_task_id=t.id,
                                            pm_history_id=pm_history.id
                                        )
                                        print(f"[PM] Documents copied successfully")
                                    except Exception as doc_ex:
                                        print(f"[PM] Error copying documents: {doc_ex}")
                                        import traceback
                                        traceback.print_exc()
                                        # Don't fail the whole completion if document copy fails
                                
                                print(f"[PM] Task {t.id} completed successfully")
                                
                                # Close dialog
                                print(f"[PM] Closing dialog...")
                                try:
                                    dialog.open = False
                                    dialog_page.update()
                                    print(f"[PM] Dialog closed successfully")
                                except Exception as close_ex:
                                    print(f"[PM] Error closing dialog: {close_ex}")
                                    # Try alternative method
                                    try:
                                        dialog_page.close(dialog)
                                        dialog_page.update()
                                        print(f"[PM] Dialog closed using alternative method")
                                    except:
                                        pass
                                
                                # Refresh PM tasks list
                                print(f"[PM] Refreshing PM tasks list...")
                                refresh_pm_tasks()
                                print(f"[PM] PM tasks list refreshed")
                                
                                print(f"[PM] Showing success snackbar...")
                                snackbar_page = self.page if hasattr(self, 'page') and self.page else page
                                snackbar_page.snack_bar = ft.SnackBar(
                                    content=ft.Text(translator.get_text("preventive_maintenance.task_completed")),
                                    bgcolor=DesignSystem.SUCCESS
                                )
                                snackbar_page.snack_bar.open = True
                                snackbar_page.update()
                                print(f"[PM] Success snackbar shown")
                            except Exception as ex:
                                print(f"[PM] ====== ERROR in submit_completion ======")
                                print(f"[PM] Error type: {type(ex).__name__}")
                                print(f"[PM] Error message: {str(ex)}")
                                import traceback
                                traceback.print_exc()
                                print(f"[PM] ====== END ERROR ======")
                                
                                # Show error to user
                                error_page = self.page if hasattr(self, 'page') and self.page else page
                                error_page.snack_bar = ft.SnackBar(
                                    content=ft.Text(f"{translator.get_text('common.error')}: {str(ex)}"),
                                    bgcolor=DesignSystem.ERROR
                                )
                                error_page.snack_bar.open = True
                                error_page.update()
                                page.snack_bar = ft.SnackBar(
                                    content=ft.Text(f"{translator.get_text('common.messages.error_occurred')}: {ex}"),
                                    bgcolor=DesignSystem.ERROR
                                )
                                page.snack_bar.open = True
                                page.update()
                        
                        # Build modern dialog content with sections
                        dialog_content = ft.Container(
                            content=ft.Column([
                                # Task info header
                                ft.Container(
                                    content=ft.Column([
                                        ft.Row([
                                            ft.Icon(ft.Icons.BUILD, color=DesignSystem.PRIMARY, size=20),
                                            ft.Text(t.task_name, size=16, weight=ft.FontWeight.BOLD, color=DesignSystem.TEXT_PRIMARY),
                                        ], spacing=8),
                                        ft.Text(
                                            f"{translator.get_text('preventive_maintenance.machine')}: {t.machine.name if t.machine else '-'}",
                                            size=12,
                                            color=DesignSystem.TEXT_SECONDARY
                                        ),
                                    ], spacing=4),
                                    padding=ft.padding.all(12),
                                    bgcolor=DesignSystem.BG_TERTIARY,
                                    border_radius=DesignSystem.RADIUS_MD,
                                ),
                                
                                # Section 1: Basic Information
                                ft.Container(
                                    content=ft.Column([
                                        ft.Text(
                                            translator.get_text("common.basic_info") if hasattr(translator, 'get_text') else "Alapadatok",
                                            size=14,
                                            weight=ft.FontWeight.BOLD,
                                            color=DesignSystem.TEXT_PRIMARY,
                                        ),
                                        ft.Divider(height=1, color=DesignSystem.BORDER_COLOR),
                                        ft.Container(height=8),
                                        ft.Row([
                                            completion_date_field,
                                            completion_time_field,
                                            duration_field,
                                        ], spacing=12, wrap=False),
                                    ], spacing=8),
                                    padding=ft.padding.all(16),
                                ),
                                
                                # Section 2: Work Details
                                ft.Container(
                                    content=ft.Column([
                                        ft.Text(
                                            translator.get_text("preventive_maintenance.work_details") if hasattr(translator, 'get_text') else "Munkaleírás",
                                            size=14,
                                            weight=ft.FontWeight.BOLD,
                                            color=DesignSystem.TEXT_PRIMARY,
                                        ),
                                        ft.Divider(height=1, color=DesignSystem.BORDER_COLOR),
                                        ft.Container(height=8),
                                        work_description_field,
                                        ft.Container(height=12),
                                        observations_field,
                                    ], spacing=8),
                                    padding=ft.padding.all(16),
                                    bgcolor=DesignSystem.BG_TERTIARY,
                                    border_radius=DesignSystem.RADIUS_MD,
                                ),
                                
                                # Section 3: Status
                                ft.Container(
                                    content=ft.Column([
                                        ft.Text(
                                            translator.get_text("preventive_maintenance.status") if hasattr(translator, 'get_text') else "Státusz",
                                            size=14,
                                            weight=ft.FontWeight.BOLD,
                                            color=DesignSystem.TEXT_PRIMARY,
                                        ),
                                        ft.Divider(height=1, color=DesignSystem.BORDER_COLOR),
                                        ft.Container(height=8),
                                        completion_status_field,
                                    ], spacing=8),
                                    padding=ft.padding.all(16),
                                ),
                                
                                # Section 4: Parts Used
                                parts_section,
                                
                                # Section 5: Additional Notes
                                ft.Container(
                                    content=ft.Column([
                                        ft.Text(
                                            translator.get_text("preventive_maintenance.additional_notes") if hasattr(translator, 'get_text') else "További megjegyzések",
                                            size=14,
                                            weight=ft.FontWeight.BOLD,
                                            color=DesignSystem.TEXT_PRIMARY,
                                        ),
                                        ft.Divider(height=1, color=DesignSystem.BORDER_COLOR),
                                        ft.Container(height=8),
                                        notes_field,
                                    ], spacing=8),
                                    padding=ft.padding.all(16),
                                    bgcolor=DesignSystem.BG_TERTIARY,
                                    border_radius=DesignSystem.RADIUS_MD,
                                ),
                                
                                # Section 6: File Uploads
                                files_section,
                            ], spacing=12, tight=False, scroll=ft.ScrollMode.AUTO),
                            width=700,
                            height=700,
                            padding=20,
                        )
                        
                        dialog = ft.AlertDialog(
                            modal=True,
                            title=ft.Row([
                                ft.Icon(ft.Icons.CHECK_CIRCLE, color=DesignSystem.SUCCESS, size=28),
                                ft.Text(
                                    translator.get_text("preventive_maintenance.complete_task") if hasattr(translator, 'get_text') else "Feladat befejezése",
                                    size=22,
                                    weight=ft.FontWeight.BOLD,
                                    color=DesignSystem.TEXT_PRIMARY,
                                ),
                            ], spacing=12),
                            content=dialog_content,
                            actions=[
                                ft.TextButton(
                                    translator.get_text("common.buttons.cancel"),
                                    on_click=lambda _: setattr(dialog, 'open', False) or dialog_page.update(),
                                    style=ft.ButtonStyle(color="#6B7280")
                                ),
                                ft.ElevatedButton(
                                    translator.get_text("preventive_maintenance.task_completed"),
                                    icon=ft.Icons.CHECK,
                                    on_click=lambda e: (print(f"[PM] ====== BUTTON CLICKED ======"), print(f"[PM] Event: {e}"), submit_completion(e)),
                                    bgcolor=DesignSystem.SUCCESS,
                                    color="#FFFFFF",
                                ),
                            ],
                            actions_alignment=ft.MainAxisAlignment.END,
                        )
                        
                        try:
                            dialog_page.open(dialog)
                        except Exception as dialog_ex:
                            try:
                                dialog_page.dialog = dialog
                                dialog.open = True
                                dialog_page.update()
                            except Exception as dialog_ex2:
                                print(f"[PM] Error opening dialog: {dialog_ex}, {dialog_ex2}")
                                import traceback
                                traceback.print_exc()
                                # Show error to user
                                page.snack_bar = ft.SnackBar(
                                    content=ft.Text(f"{translator.get_text('common.messages.error_occurred')}: {str(dialog_ex)}"),
                                    bgcolor=DesignSystem.ERROR
                                )
                                page.snack_bar.open = True
                                page.update()
                    
                    def complete_task(t=task):
                        def handle_click(_):
                            print(f"[PM] Complete button clicked for task {t.id}")
                            try:
                                open_complete_dialog(t)
                            except Exception as ex:
                                print(f"[PM] Error opening complete dialog: {ex}")
                                import traceback
                                traceback.print_exc()
                                # Show error to user
                                error_page = self.page if self.page else page
                                error_page.snack_bar = ft.SnackBar(
                                    content=ft.Text(f"{translator.get_text('common.messages.error_occurred')}: {str(ex)}"),
                                    bgcolor=DesignSystem.ERROR
                                )
                                error_page.snack_bar.open = True
                                error_page.update()
                        return handle_click
                    
                    # Edit button function (only for users with edit permission)
                    edit_button = None
                    if can_edit_pm():
                        def open_edit_dialog(t=task):
                            """Open dialog to edit PM task"""
                            dialog_page = self.page if self.page else page
                            
                            # Form fields
                            task_name_field = create_modern_text_field(
                                label=translator.get_text("preventive_maintenance.task_name"),
                                value=t.task_name,
                                width=500,
                            )
                            task_description_field = create_modern_text_field(
                                label=translator.get_text("preventive_maintenance.task_description"),
                                value=t.task_description or "",
                                multiline=True,
                                max_lines=5,
                                width=500,
                            )
                            # Set min_lines directly on the TextField if needed
                            if hasattr(task_description_field, 'min_lines'):
                                task_description_field.min_lines = 3
                            priority_field = create_modern_dropdown(
                                label=translator.get_text("preventive_maintenance.priority"),
                                options=[
                                    ft.dropdown.Option("low", translator.get_text("preventive_maintenance.priority_low")),
                                    ft.dropdown.Option("normal", translator.get_text("preventive_maintenance.priority_normal")),
                                    ft.dropdown.Option("high", translator.get_text("preventive_maintenance.priority_high")),
                                    ft.dropdown.Option("urgent", translator.get_text("preventive_maintenance.priority_urgent")),
                                ],
                                value=t.priority or "normal",
                                width=200,
                            )
                            status_field = create_modern_dropdown(
                                label=translator.get_text("preventive_maintenance.status"),
                                options=[
                                    ft.dropdown.Option("pending", translator.get_text("preventive_maintenance.status_pending")),
                                    ft.dropdown.Option("in_progress", translator.get_text("preventive_maintenance.status_in_progress")),
                                    ft.dropdown.Option("completed", translator.get_text("preventive_maintenance.status_completed")),
                                    ft.dropdown.Option("cancelled", translator.get_text("preventive_maintenance.status_cancelled")),
                                ],
                                value=t.status or "pending",
                                width=200,
                            )
                            estimated_duration_field = create_modern_text_field(
                                label=translator.get_text("preventive_maintenance.estimated_duration_minutes"),
                                value=str(t.estimated_duration_minutes) if t.estimated_duration_minutes else "",
                                width=200,
                                keyboard_type=ft.KeyboardType.NUMBER,
                            )
                            
                            def submit_edit(_):
                                try:
                                    task_name = task_name_field.value.strip() if task_name_field.value else None
                                    if not task_name:
                                        page.snack_bar = ft.SnackBar(
                                            content=ft.Text(translator.get_text("preventive_maintenance.task_name_required")),
                                            bgcolor=DesignSystem.ERROR
                                        )
                                        page.snack_bar.open = True
                                        page.update()
                                        return
                                    
                                    # Update PM task
                                    pm_service.update_pm_task(
                                        task_id=t.id,
                                        task_name=task_name,
                                        task_description=task_description_field.value.strip() if task_description_field.value else None,
                                        priority=priority_field.value,
                                        status=status_field.value,
                                        estimated_duration_minutes=int(estimated_duration_field.value) if estimated_duration_field.value and estimated_duration_field.value.isdigit() else None,
                                    )
                                    
                                    # Close dialog
                                    edit_dialog.open = False
                                    dialog_page.update()
                                    
                                    # Refresh PM tasks list
                                    refresh_pm_tasks()
                                    
                                    page.snack_bar = ft.SnackBar(
                                        content=ft.Text(translator.get_text("preventive_maintenance.task_updated")),
                                        bgcolor=DesignSystem.SUCCESS
                                    )
                                    page.snack_bar.open = True
                                    page.update()
                                except Exception as ex:
                                    page.snack_bar = ft.SnackBar(
                                        content=ft.Text(f"{translator.get_text('common.messages.error_occurred')}: {ex}"),
                                        bgcolor=DesignSystem.ERROR
                                    )
                                    page.snack_bar.open = True
                                    page.update()
                            
                            edit_dialog = ft.AlertDialog(
                                modal=True,
                                title=ft.Row([
                                    ft.Icon(ft.Icons.EDIT, color=DesignSystem.PRIMARY, size=24),
                                    ft.Text(translator.get_text("preventive_maintenance.edit_task"), size=20, weight=ft.FontWeight.BOLD, color="#1F2937"),
                                ], spacing=10),
                                content=ft.Container(
                                    content=ft.Column([
                                        task_name_field,
                                        task_description_field,
                                        ft.Row([
                                            priority_field,
                                            status_field,
                                            estimated_duration_field,
                                        ], spacing=10),
                                    ], spacing=12, tight=False, scroll=ft.ScrollMode.AUTO),
                                    width=550,
                                    height=400,
                                    padding=15,
                                ),
                                actions=[
                                    ft.TextButton(
                                        translator.get_text("common.buttons.cancel"),
                                        on_click=lambda _: setattr(edit_dialog, 'open', False) or dialog_page.update(),
                                    ),
                                    ft.ElevatedButton(
                                        translator.get_text("common.buttons.save"),
                                        icon=ft.Icons.SAVE,
                                        on_click=submit_edit,
                                        bgcolor=DesignSystem.PRIMARY,
                                        color="#FFFFFF",
                                    ),
                                ],
                                actions_alignment=ft.MainAxisAlignment.END,
                            )
                            
                            try:
                                dialog_page.open(edit_dialog)
                            except:
                                dialog_page.dialog = edit_dialog
                                edit_dialog.open = True
                                dialog_page.update()
                        
                        def edit_task(t=task):
                            return lambda _: open_edit_dialog(t)
                        
                        edit_button = ft.IconButton(
                            icon=ft.Icons.EDIT,
                            icon_color=DesignSystem.PRIMARY,
                            tooltip=translator.get_text("preventive_maintenance.edit_task"),
                            on_click=edit_task(),
                        )
                    
                    card = ft.Card(
                        elevation=2,
                        content=ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Column([
                                        ft.Row([
                                            ft.Icon(ft.Icons.BUILD, color=priority_color, size=20),
                                            ft.Text(task.task_name, size=16, weight=ft.FontWeight.BOLD, color="#1F2937"),
                                            ft.Container(
                                                content=ft.Text(
                                                    task.priority.upper() if task.priority else "NORMAL",
                                                    size=10,
                                                    weight=ft.FontWeight.BOLD,
                                                    color="#FFFFFF"
                                                ),
                                                bgcolor=priority_color,
                                                padding=ft.padding.symmetric(horizontal=8, vertical=2),
                                                border_radius=4,
                                            ) if task.priority else ft.Container(),
                                        ], spacing=8),
                                        ft.Text(f"Gép: {machine_name}", size=12, color="#6B7280"),
                                        ft.Row([
                                            ft.Text(f"Esedékes: {task.next_due_date.strftime('%Y-%m-%d') if task.next_due_date else '-'}", size=12, color="#EF4444", weight=ft.FontWeight.BOLD),
                                            ft.Container(width=10),
                                            ft.Container(
                                                content=ft.Text(
                                                    task.status.upper() if task.status else "PENDING",
                                                    size=10,
                                                    weight=ft.FontWeight.BOLD,
                                                    color="#FFFFFF"
                                                ),
                                                bgcolor=status_color,
                                                padding=ft.padding.symmetric(horizontal=8, vertical=2),
                                                border_radius=4,
                                            ) if task.status else ft.Container(),
                                        ]),
                                        ft.Text(f"{translator.get_text('preventive_maintenance.assigned_to')} {task.assigned_user.full_name if task.assigned_user else translator.get_text('preventive_maintenance.global')}", size=11, color="#6B7280"),
                                        ft.Text(task.task_description or "Nincs leírás", size=11, color="#9CA3AF", italic=True) if task.task_description else ft.Container(),
                                    ], expand=True),
                                    ft.Row([
                                        edit_button if edit_button else ft.Container(),
                                        ft.ElevatedButton(
                                            translator.get_text("preventive_maintenance.complete"),
                                            icon=ft.Icons.CHECK_CIRCLE,
                                            on_click=complete_task(),
                                            bgcolor=DesignSystem.SUCCESS,
                                            color="#FFFFFF",
                                            visible=task.status != "completed",
                                        ) if current_user_id and (not task.assigned_to_user_id or task.assigned_to_user_id == current_user_id) else ft.Container(),
                                    ], spacing=8) if edit_button or (current_user_id and (not task.assigned_to_user_id or task.assigned_to_user_id == current_user_id)) else ft.Container(),
                                ], spacing=8),
                            ], spacing=4),
                            padding=16,
                        ),
                    )
                    pm_tasks_list.controls.append(card)
                
                # Display completed tasks: last 10 directly, rest grouped by date
                # Helper function to create completed task card (extracted for reuse)
                def create_completed_task_card(task, last_history=None, last_executed="-", 
                                              has_work_request=False, has_worksheet=False, 
                                              has_scrapping=False, scrapping_docs=[]):
                    """Create a card for a completed PM task"""
                    if task.machine_id:
                        machine_name = task.machine.name if hasattr(task, 'machine') and task.machine else f"Gép ID: {task.machine_id}"
                    else:
                        machine_name = f"{translator.get_text('preventive_maintenance.other')}: {task.location or '-'}"
                    
                    status_color = "#10B981"  # Green for completed
                    
                    def open_completed_task_details(t=task, h=last_history):
                        """Open detailed dialog for completed PM task"""
                        dialog_page = self.page if self.page else page
                        
                        # Fetch all related data
                        from database.session_manager import SessionLocal
                        from database.models import PMHistory, WorkRequestPDF, PMWorksheetPDF, ScrappingDocument, Worksheet, WorksheetPart, PMTask
                        from sqlalchemy.orm import joinedload
                        detail_session = SessionLocal()
                        try:
                            task_detail = detail_session.query(PMTask).options(
                                joinedload(PMTask.machine),
                                joinedload(PMTask.assigned_user)
                            ).filter_by(id=t.id).first()
                            
                            history_detail = detail_session.query(PMHistory).options(
                                joinedload(PMHistory.completed_user),
                                joinedload(PMHistory.worksheet).joinedload(Worksheet.parts).joinedload(WorksheetPart.part)
                            ).filter_by(pm_task_id=t.id).order_by(PMHistory.executed_date.desc()).first()
                            
                            worksheet_detail = history_detail.worksheet if history_detail and history_detail.worksheet else None
                            
                        except Exception as ex:
                            print(f"[PM] Error loading task details: {ex}")
                            task_detail = t
                            history_detail = h
                            worksheet_detail = None
                        finally:
                            detail_session.close()
                        
                        # Build detailed content (same as before - reuse existing logic)
                        detail_items = []
                        
                        # Basic task info
                        detail_items.append(ft.Container(
                            content=ft.Column([
                                ft.Text(
                                    translator.get_text("preventive_maintenance.task_details") if hasattr(translator, 'get_text') else "Feladat részletei",
                                    size=18,
                                    weight=ft.FontWeight.BOLD,
                                    color="#1F2937",
                                ),
                                ft.Divider(height=1, color="#E5E7EB"),
                                ft.Container(height=12),
                                ft.Row([
                                    ft.Text(
                                        translator.get_text("preventive_maintenance.task_name") if hasattr(translator, 'get_text') else "Feladat neve:",
                                        size=14,
                                        weight=ft.FontWeight.BOLD,
                                        width=200,
                                    ),
                                    ft.Text(task_detail.task_name if task_detail else "-", size=14, color="#374151", expand=True),
                                ], spacing=12),
                                ft.Container(height=8),
                                ft.Row([
                                    ft.Text(
                                        translator.get_text("preventive_maintenance.task_description") if hasattr(translator, 'get_text') else "Leírás:",
                                        size=14,
                                        weight=ft.FontWeight.BOLD,
                                        width=200,
                                    ),
                                    ft.Text(task_detail.task_description if task_detail and task_detail.task_description else "-", size=14, color="#374151", expand=True, selectable=True),
                                ], spacing=12),
                                ft.Container(height=8),
                                ft.Row([
                                    ft.Text(
                                        "Gép:",
                                        size=14,
                                        weight=ft.FontWeight.BOLD,
                                        width=200,
                                    ),
                                    ft.Text(machine_name, size=14, color="#374151", expand=True),
                                ], spacing=12),
                            ], spacing=8),
                            padding=16,
                            bgcolor="#F9FAFB",
                            border_radius=8,
                        ))
                        
                        # Execution details
                        if history_detail:
                            detail_items.append(ft.Container(
                                content=ft.Column([
                                    ft.Text(
                                        translator.get_text("preventive_maintenance.execution_details") if hasattr(translator, 'get_text') else "Végrehajtás részletei",
                                        size=18,
                                        weight=ft.FontWeight.BOLD,
                                        color="#1F2937",
                                    ),
                                    ft.Divider(height=1, color="#E5E7EB"),
                                    ft.Container(height=12),
                                    ft.Row([
                                        ft.Text(
                                            "Elvégzés dátuma:",
                                            size=14,
                                            weight=ft.FontWeight.BOLD,
                                            width=200,
                                        ),
                                        ft.Text(
                                            history_detail.executed_date.strftime('%Y-%m-%d %H:%M') if history_detail.executed_date else "-",
                                            size=14,
                                            color="#374151",
                                            expand=True,
                                        ),
                                    ], spacing=12),
                                    ft.Container(height=8),
                                    ft.Row([
                                        ft.Text(
                                            "Elvégző:",
                                            size=14,
                                            weight=ft.FontWeight.BOLD,
                                            width=200,
                                        ),
                                        ft.Text(
                                            history_detail.completed_user.full_name if history_detail.completed_user else "-",
                                            size=14,
                                            color="#374151",
                                            expand=True,
                                        ),
                                    ], spacing=12),
                                    ft.Container(height=8),
                                    ft.Row([
                                        ft.Text(
                                            "Időtartam:",
                                            size=14,
                                            weight=ft.FontWeight.BOLD,
                                            width=200,
                                        ),
                                        ft.Text(
                                            f"{history_detail.duration_minutes or 0} perc" if history_detail.duration_minutes else "-",
                                            size=14,
                                            color="#374151",
                                            expand=True,
                                        ),
                                    ], spacing=12),
                                    ft.Container(height=8),
                                    ft.Row([
                                        ft.Text(
                                            "Megjegyzések:",
                                            size=14,
                                            weight=ft.FontWeight.BOLD,
                                            width=200,
                                        ),
                                        ft.Text(
                                            history_detail.notes if history_detail.notes else "-",
                                            size=14,
                                            color="#374151",
                                            expand=True,
                                            selectable=True,
                                        ),
                                    ], spacing=12),
                                ], spacing=8),
                                padding=16,
                                bgcolor="#F9FAFB",
                                border_radius=8,
                            ))
                        
                        # Worksheet details
                        if worksheet_detail and history_detail:
                            worksheet_parts = []
                            if hasattr(worksheet_detail, 'parts') and worksheet_detail.parts:
                                for wp in worksheet_detail.parts:
                                    part_name = wp.part.name if wp.part else f"Alkatrész ID: {wp.part_id}"
                                    worksheet_parts.append(
                                        ft.Row([
                                            ft.Text(f"• {part_name}", size=14, color="#374151", expand=True),
                                            ft.Text(f"{wp.quantity_used} db", size=14, color="#374151", weight=ft.FontWeight.BOLD),
                                        ], spacing=12)
                                    )
                            
                            detail_items.append(ft.Container(
                                content=ft.Column([
                                    ft.Text(
                                        translator.get_text("preventive_maintenance.worksheet") if hasattr(translator, 'get_text') else "Munkalap",
                                        size=18,
                                        weight=ft.FontWeight.BOLD,
                                        color="#1F2937",
                                    ),
                                    ft.Divider(height=1, color="#E5E7EB"),
                                    ft.Container(height=12),
                                    ft.Row([
                                        ft.Text(
                                            "Munkalap ID:",
                                            size=14,
                                            weight=ft.FontWeight.BOLD,
                                            width=200,
                                        ),
                                        ft.TextButton(
                                            f"Worksheet #{worksheet_detail.id}",
                                            on_click=lambda _: (setattr(dialog, 'open', False), dialog_page.update(), page.go(f"/worksheets/detail/{worksheet_detail.id}")),
                                            style=ft.ButtonStyle(color="#6366F1"),
                                        ),
                                    ], spacing=12),
                                    ft.Container(height=8),
                                    ft.Row([
                                        ft.Text(
                                            "Cím:",
                                            size=14,
                                            weight=ft.FontWeight.BOLD,
                                            width=200,
                                        ),
                                        ft.Text(worksheet_detail.title if worksheet_detail.title else "-", size=14, color="#374151", expand=True),
                                    ], spacing=12),
                                    ft.Container(height=8),
                                    ft.Row([
                                        ft.Text(
                                            "Státusz:",
                                            size=14,
                                            weight=ft.FontWeight.BOLD,
                                            width=200,
                                        ),
                                        ft.Text(worksheet_detail.status if worksheet_detail.status else "-", size=14, color="#374151", expand=True),
                                    ], spacing=12),
                                    *((
                                        [ft.Container(height=16),
                                         ft.Text("Használt alkatrészek:", size=14, weight=ft.FontWeight.BOLD),
                                         ft.Container(height=8)] + worksheet_parts
                                    ) if worksheet_parts else [
                                        ft.Text("Nincs használt alkatrész", size=14, color="#9CA3AF", italic=True)
                                    ]),
                                ], spacing=8),
                                padding=16,
                                bgcolor="#F9FAFB",
                                border_radius=8,
                            ))
                        
                        dialog_content = ft.Container(
                            content=ft.Column(detail_items, spacing=16, scroll=ft.ScrollMode.AUTO),
                            width=700,
                            height=600,
                            padding=20,
                        )
                        
                        dialog = ft.AlertDialog(
                            modal=True,
                            title=ft.Row([
                                ft.Icon(ft.Icons.INFO_OUTLINE, color="#6366F1", size=28),
                                ft.Text(
                                    translator.get_text("common.buttons.view_details") if hasattr(translator, 'get_text') else "Részletek",
                                    size=22,
                                    weight=ft.FontWeight.BOLD,
                                    color="#1F2937",
                                ),
                            ], spacing=12),
                            content=dialog_content,
                            actions=[
                                ft.TextButton(
                                    translator.get_text("common.buttons.close"),
                                    on_click=lambda _: (setattr(dialog, 'open', False), dialog_page.update()),
                                    style=ft.ButtonStyle(color="#6B7280")
                                ),
                            ],
                            actions_alignment=ft.MainAxisAlignment.END,
                        )
                        
                        try:
                            dialog_page.open(dialog)
                        except:
                            dialog_page.dialog = dialog
                            dialog.open = True
                            dialog_page.update()
                    
                    def view_work_request_pdf_completed(t=task):
                        """Open work request PDF for completed task"""
                        try:
                            from database.session_manager import SessionLocal
                            from database.models import WorkRequestPDF
                            from pathlib import Path
                            import os
                            
                            session = SessionLocal()
                            pdf_record = session.query(WorkRequestPDF).filter_by(pm_task_id=t.id).first()
                            session.close()
                            
                            if pdf_record and Path(pdf_record.pdf_path).exists():
                                os.startfile(pdf_record.pdf_path)
                            else:
                                page.snack_bar = ft.SnackBar(
                                    content=ft.Text(translator.get_text("preventive_maintenance.document_not_found")),
                                    bgcolor=DesignSystem.ERROR
                                )
                                page.snack_bar.open = True
                                page.update()
                        except Exception as ex:
                            page.snack_bar = ft.SnackBar(
                                content=ft.Text(f"{translator.get_text('common.messages.error_occurred')}: {ex}"),
                                bgcolor=DesignSystem.ERROR
                            )
                            page.snack_bar.open = True
                            page.update()
                    
                    def view_worksheet_pdf_completed(t=task, h=last_history):
                        """Open worksheet PDF for completed task"""
                        if not h:
                            page.snack_bar = ft.SnackBar(
                                content=ft.Text(translator.get_text("preventive_maintenance.document_not_found")),
                                bgcolor=DesignSystem.ERROR
                            )
                            page.snack_bar.open = True
                            page.update()
                            return
                        
                        try:
                            from database.session_manager import SessionLocal
                            from database.models import PMWorksheetPDF
                            from pathlib import Path
                            import os
                            
                            session = SessionLocal()
                            pdf_record = session.query(PMWorksheetPDF).filter_by(pm_history_id=h.id).first()
                            session.close()
                            
                            if pdf_record and Path(pdf_record.pdf_path).exists():
                                os.startfile(pdf_record.pdf_path)
                            else:
                                page.snack_bar = ft.SnackBar(
                                    content=ft.Text(translator.get_text("preventive_maintenance.document_not_found")),
                                    bgcolor=DesignSystem.ERROR
                                )
                                page.snack_bar.open = True
                                page.update()
                        except Exception as ex:
                            page.snack_bar = ft.SnackBar(
                                content=ft.Text(f"{translator.get_text('common.messages.error_occurred')}: {ex}"),
                                bgcolor=DesignSystem.ERROR
                            )
                            page.snack_bar.open = True
                            page.update()
                    
                    def view_scrapping_docs_completed(t=task, h=last_history, docs=scrapping_docs):
                        """Open scrapping documents folder for completed task"""
                        if not h or not docs:
                            page.snack_bar = ft.SnackBar(
                                content=ft.Text(translator.get_text("preventive_maintenance.document_not_found")),
                                bgcolor=DesignSystem.ERROR
                            )
                            page.snack_bar.open = True
                            page.update()
                            return
                        
                        try:
                            from pathlib import Path
                            import os
                            import shutil
                            
                            # Create folder for scrapping documents
                            output_dir = Path("generated_pdfs") / f"scrapping_pm_{h.id}"
                            output_dir.mkdir(parents=True, exist_ok=True)
                            
                            # Copy documents to folder
                            for doc in docs:
                                if doc.docx_path and Path(doc.docx_path).exists():
                                    shutil.copy2(doc.docx_path, output_dir / Path(doc.docx_path).name)
                            
                            # Open folder
                            os.startfile(output_dir)
                            
                            page.snack_bar = ft.SnackBar(
                                content=ft.Text(f"{len(docs)} selejt igénylő lap másolva"),
                                bgcolor=DesignSystem.SUCCESS
                            )
                            page.snack_bar.open = True
                            page.update()
                        except Exception as ex:
                            page.snack_bar = ft.SnackBar(
                                content=ft.Text(f"{translator.get_text('common.messages.error_occurred')}: {ex}"),
                                bgcolor=DesignSystem.ERROR
                            )
                            page.snack_bar.open = True
                            page.update()
                    
                    # Build action buttons
                    action_buttons = []
                    
                    # Details button (always visible)
                    action_buttons.append(
                        ft.ElevatedButton(
                            translator.get_text("common.buttons.view_details") if hasattr(translator, 'get_text') else "Részletek",
                            icon=ft.Icons.INFO_OUTLINE,
                            on_click=lambda _, t=task, h=last_history: open_completed_task_details(t, h),
                            bgcolor="#6366F1",
                            color="#FFFFFF",
                            height=36,
                            tooltip="Feladat részleteinek megtekintése",
                        )
                    )
                    
                    # Work request button
                    if has_work_request:
                        action_buttons.append(
                            ft.ElevatedButton(
                                translator.get_text("preventive_maintenance.work_request") if hasattr(translator, 'get_text') else "Munkaigénylő",
                                icon=ft.Icons.PICTURE_AS_PDF if hasattr(ft.Icons, 'PICTURE_AS_PDF') else ft.Icons.DESCRIPTION,
                                on_click=lambda _, t=task: view_work_request_pdf_completed(t),
                                bgcolor=DesignSystem.ERROR,
                                color="#FFFFFF",
                                height=36,
                                tooltip="Munkaigénylő lap megnyitása",
                            )
                        )
                    
                    # Worksheet button
                    if has_worksheet:
                        action_buttons.append(
                            ft.ElevatedButton(
                                translator.get_text("preventive_maintenance.worksheet") if hasattr(translator, 'get_text') else "Munkalap",
                                icon=ft.Icons.DESCRIPTION,
                                on_click=lambda _, t=task, h=last_history: view_worksheet_pdf_completed(t, h),
                                bgcolor=DesignSystem.SUCCESS,
                                color="#FFFFFF",
                                height=36,
                                tooltip="Munkalap megnyitása",
                            )
                        )
                    
                    # Scrapping documents button
                    if has_scrapping:
                        action_buttons.append(
                            ft.ElevatedButton(
                                translator.get_text("preventive_maintenance.scrapping_document") if hasattr(translator, 'get_text') else "Selejt igénylő",
                                icon=ft.Icons.FILE_DOWNLOAD,
                                on_click=lambda _, t=task, h=last_history, docs=scrapping_docs: view_scrapping_docs_completed(t, h, docs),
                                bgcolor="#F59E0B",
                                color="#FFFFFF",
                                height=36,
                                tooltip=f"{len(scrapping_docs)} selejt igénylő lap",
                            )
                        )
                    
                    # Files button (attachments and documents)
                    def view_files_completed(t=task, h=last_history):
                        """Open dialog to view all files (attachments and documents) for completed task"""
                        dialog_page = self.page if self.page else page
                        
                        from database.session_manager import SessionLocal
                        from database.models import PMTaskAttachment, PMHistory, WorkRequestPDF, PMWorksheetPDF, ScrappingDocument
                        from services.pm_service import get_pm_task_directory, copy_pm_task_documents_to_directory
                        import os
                        
                        session = SessionLocal()
                        try:
                            # Ensure documents are copied to directory (if not already done)
                            if h and h.pm_task_id:
                                try:
                                    copy_pm_task_documents_to_directory(h.pm_task_id, h.id, session=session)
                                except Exception as copy_ex:
                                    # Don't fail if copy fails, just log
                                    print(f"[PM] Error copying documents: {copy_ex}")
                            
                            # Get attachments
                            attachments = session.query(PMTaskAttachment).filter_by(pm_history_id=h.id).all() if h else []
                            
                            # Get directory
                            if h and h.pm_task_id:
                                task_dir = get_pm_task_directory(h.pm_task_id, h.id)
                            else:
                                task_dir = None
                            
                            # Build file list
                            file_items = []
                            
                            # Add attachments
                            for att in attachments:
                                file_path = Path(att.file_path)
                                if file_path.exists():
                                    file_type_icon = ft.Icons.INSERT_PHOTO if att.file_type == "image" else ft.Icons.INSERT_DRIVE_FILE
                                    file_items.append(
                                        ft.ListTile(
                                            leading=ft.Icon(file_type_icon, color=DesignSystem.TEXT_SECONDARY),
                                            title=ft.Text(att.original_filename, size=14),
                                            subtitle=ft.Text(
                                                f"{att.file_type} • {att.uploaded_at.strftime('%Y-%m-%d %H:%M') if att.uploaded_at else '-'}",
                                                size=11,
                                                color=DesignSystem.TEXT_SECONDARY
                                            ),
                                            trailing=ft.IconButton(
                                                icon=ft.Icons.OPEN_IN_NEW,
                                                tooltip="Megnyitás / Open",
                                                on_click=lambda _, path=str(file_path): os.startfile(path),
                                            ),
                                        )
                                    )
                            
                            # Add documents from directory
                            if task_dir and task_dir.exists():
                                for doc_file in task_dir.iterdir():
                                    if doc_file.is_file() and doc_file.name not in [att.file_path.split(os.sep)[-1] for att in attachments if att.file_path]:
                                        # This is a document that wasn't already listed as attachment
                                        file_items.append(
                                            ft.ListTile(
                                                leading=ft.Icon(ft.Icons.DESCRIPTION, color=DesignSystem.TEXT_SECONDARY),
                                                title=ft.Text(doc_file.name, size=14),
                                                subtitle=ft.Text(
                                                    f"{doc_file.stat().st_size / 1024:.1f} KB",
                                                    size=11,
                                                    color=DesignSystem.TEXT_SECONDARY
                                                ),
                                                trailing=ft.IconButton(
                                                    icon=ft.Icons.OPEN_IN_NEW,
                                                    tooltip="Megnyitás / Open",
                                                    on_click=lambda _, path=str(doc_file): os.startfile(path),
                                                ),
                                            )
                                        )
                            
                            if not file_items:
                                file_items.append(
                                    ft.Text(
                                        translator.get_text("preventive_maintenance.no_files") if hasattr(translator, 'get_text') else "Nincsenek fájlok / No files",
                                        size=12,
                                        color=DesignSystem.TEXT_SECONDARY,
                                        italic=True,
                                    )
                                )
                            
                            # Create dialog
                            files_dialog = ft.AlertDialog(
                                modal=True,
                                title=ft.Row([
                                    ft.Icon(ft.Icons.FOLDER_OPEN, color=DesignSystem.BLUE_500, size=28),
                                    ft.Text(
                                        translator.get_text("preventive_maintenance.files_and_documents") if hasattr(translator, 'get_text') else "Fájlok és dokumentumok / Files and Documents",
                                        size=22,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                ], spacing=12),
                                content=ft.Container(
                                    content=ft.Column(
                                        file_items,
                                        spacing=4,
                                        scroll=ft.ScrollMode.AUTO,
                                        height=400,
                                    ),
                                    width=600,
                                    padding=20,
                                ),
                                actions=[
                                    ft.TextButton(
                                        translator.get_text("common.buttons.close"),
                                        on_click=lambda _: (setattr(files_dialog, 'open', False), dialog_page.update()),
                                    ),
                                ],
                            )
                            
                            try:
                                dialog_page.open(files_dialog)
                            except:
                                dialog_page.dialog = files_dialog
                                files_dialog.open = True
                                dialog_page.update()
                                
                        finally:
                            session.close()
                    
                    # Add Files button if there are any attachments or documents
                    has_files = False
                    if last_history:
                        from database.session_manager import SessionLocal
                        from database.models import PMTaskAttachment
                        check_session = SessionLocal()
                        try:
                            attachments_count = check_session.query(PMTaskAttachment).filter_by(pm_history_id=last_history.id).count()
                            if attachments_count > 0:
                                has_files = True
                            elif last_history.pm_task_id:
                                task_dir = pm_service.get_pm_task_directory(last_history.pm_task_id, last_history.id)
                                if task_dir.exists() and any(task_dir.iterdir()):
                                    has_files = True
                        finally:
                            check_session.close()
                    
                    if has_files or last_history:
                        action_buttons.append(
                            ft.ElevatedButton(
                                translator.get_text("preventive_maintenance.files") if hasattr(translator, 'get_text') else "Fájlok",
                                icon=ft.Icons.FOLDER_OPEN,
                                on_click=lambda _, t=task, h=last_history: view_files_completed(t, h),
                                bgcolor=DesignSystem.INFO,
                                color="#FFFFFF",
                                height=36,
                                tooltip="Fájlok és dokumentumok megtekintése",
                            )
                        )
                    
                    card = ft.Card(
                        elevation=1,
                        content=ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Column([
                                        ft.Row([
                                            ft.Icon(ft.Icons.CHECK_CIRCLE, color=status_color, size=20),
                                            ft.Text(task.task_name, size=16, weight=ft.FontWeight.BOLD, color="#1F2937"),
                                            ft.Container(
                                                content=ft.Text(
                                                    "ELVÉGEZVE",
                                                    size=10,
                                                    weight=ft.FontWeight.BOLD,
                                                    color="#FFFFFF"
                                                ),
                                                bgcolor=status_color,
                                                padding=ft.padding.symmetric(horizontal=8, vertical=2),
                                                border_radius=4,
                                            ),
                                        ], spacing=8),
                                        ft.Text(f"Gép: {machine_name}", size=12, color="#6B7280"),
                                        ft.Row([
                                            ft.Text(f"Elvégzve: {last_executed}", size=12, color="#10B981", weight=ft.FontWeight.BOLD),
                                            ft.Container(width=10),
                                            ft.Text(f"Következő esedékesség: {task.next_due_date.strftime('%Y-%m-%d') if task.next_due_date else '-'}", size=12, color="#6B7280"),
                                        ]),
                                        ft.Text(f"{translator.get_text('preventive_maintenance.assigned_to')} {task.assigned_user.full_name if task.assigned_user else translator.get_text('preventive_maintenance.global')}", size=11, color="#6B7280"),
                                        ft.Text(task.task_description or "Nincs leírás", size=11, color="#9CA3AF", italic=True) if task.task_description else ft.Container(),
                                    ], expand=True),
                                ], spacing=8),
                                ft.Container(height=12) if action_buttons else ft.Container(),
                                ft.Row(
                                    action_buttons,
                                    spacing=8,
                                    wrap=False,
                                ) if action_buttons else ft.Container(),
                            ], spacing=4),
                            padding=16,
                        ),
                    )
                    return card
                
                # Separate tasks into recent (last 10) and older ones
                recent_tasks = completed_tasks[:10]
                older_tasks = completed_tasks[10:] if len(completed_tasks) > 10 else []
                
                # Display recent tasks directly
                for task in recent_tasks:
                    # Get last execution date and related data from PMHistory
                    from database.session_manager import SessionLocal
                    from database.models import PMHistory, WorkRequestPDF, PMWorksheetPDF, ScrappingDocument
                    from sqlalchemy.orm import joinedload
                    session = SessionLocal()
                    try:
                        last_history = session.query(PMHistory).options(
                            joinedload(PMHistory.worksheet)
                        ).filter_by(pm_task_id=task.id).order_by(PMHistory.executed_date.desc()).first()
                        last_executed = last_history.executed_date.strftime('%Y-%m-%d %H:%M') if last_history and last_history.executed_date else "-"
                        
                        # Check for available documents
                        work_request_pdf = session.query(WorkRequestPDF).filter_by(pm_task_id=task.id).first()
                        worksheet_pdf = session.query(PMWorksheetPDF).filter_by(pm_history_id=last_history.id).first() if last_history else None
                        scrapping_docs = session.query(ScrappingDocument).filter_by(pm_history_id=last_history.id).all() if last_history else []
                        has_work_request = work_request_pdf is not None
                        has_worksheet = worksheet_pdf is not None
                        has_scrapping = len(scrapping_docs) > 0
                    except Exception as ex:
                        print(f"[PM] Error fetching completed task data: {ex}")
                        last_executed = "-"
                        last_history = None
                        has_work_request = False
                        has_worksheet = False
                        has_scrapping = False
                        scrapping_docs = []
                    finally:
                        session.close()
                    
                    # Use helper function to create card
                    card = create_completed_task_card(
                        task, last_history, last_executed,
                        has_work_request, has_worksheet, has_scrapping, scrapping_docs
                    )
                    completed_tasks_list.controls.append(card)
                
                # Group older tasks by date (year/month/day) and display in ExpansionTiles
                if older_tasks:
                    # Group tasks by execution date
                    from datetime import timezone as tz
                    grouped_tasks = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
                    
                    # Hungarian month names
                    month_names = {
                        1: "január", 2: "február", 3: "március", 4: "április",
                        5: "május", 6: "június", 7: "július", 8: "augusztus",
                        9: "szeptember", 10: "október", 11: "november", 12: "december"
                    }
                    
                    for task in older_tasks:
                        # Get last execution date
                        session = SessionLocal()
                        try:
                            last_history = session.query(PMHistory).options(
                                joinedload(PMHistory.worksheet)
                            ).filter_by(pm_task_id=task.id).order_by(PMHistory.executed_date.desc()).first()
                            
                            if last_history and last_history.executed_date:
                                exec_date = last_history.executed_date
                                if exec_date.tzinfo is None:
                                    exec_date = exec_date.replace(tzinfo=tz.utc)
                                
                                year = exec_date.year
                                month = exec_date.month
                                day = exec_date.day
                                
                                grouped_tasks[year][month][day].append((task, last_history))
                        except Exception as ex:
                            print(f"[PM] Error grouping completed task: {ex}")
                        finally:
                            session.close()
                    
                    # Build grouped UI with ExpansionTiles
                    for year in sorted(grouped_tasks.keys(), reverse=True):
                        year_expansion = ft.ExpansionTile(
                            title=ft.Text(f"{year}. év", size=14, weight=ft.FontWeight.BOLD, color="#1F2937"),
                            leading=ft.Icon(ft.Icons.CALENDAR_MONTH, color="#6366F1"),
                            initially_expanded=False,
                        )
                        year_content = ft.Column([], spacing=4)
                        
                        for month in sorted(grouped_tasks[year].keys(), reverse=True):
                            month_expansion = ft.ExpansionTile(
                                title=ft.Text(month_names[month], size=13, weight=ft.FontWeight.BOLD, color="#374151"),
                                leading=ft.Icon(ft.Icons.CALENDAR_VIEW_MONTH, color="#8B5CF6"),
                                initially_expanded=False,
                            )
                            month_content = ft.Column([], spacing=4)
                            
                            for day in sorted(grouped_tasks[year][month].keys(), reverse=True):
                                day_expansion = ft.ExpansionTile(
                                    title=ft.Text(f"{day}. nap ({len(grouped_tasks[year][month][day])} feladat)", size=12, weight=ft.FontWeight.BOLD, color="#6B7280"),
                                    leading=ft.Icon(ft.Icons.CALENDAR_TODAY, color="#10B981"),
                                    initially_expanded=False,
                                )
                                day_content = ft.Column([], spacing=6)
                                
                                for task, last_history in grouped_tasks[year][month][day]:
                                    # Get task data for card creation
                                    session = SessionLocal()
                                    try:
                                        last_executed = last_history.executed_date.strftime('%Y-%m-%d %H:%M') if last_history and last_history.executed_date else "-"
                                        
                                        # Check for available documents
                                        work_request_pdf = session.query(WorkRequestPDF).filter_by(pm_task_id=task.id).first()
                                        worksheet_pdf = session.query(PMWorksheetPDF).filter_by(pm_history_id=last_history.id).first() if last_history else None
                                        scrapping_docs = session.query(ScrappingDocument).filter_by(pm_history_id=last_history.id).all() if last_history else []
                                        has_work_request = work_request_pdf is not None
                                        has_worksheet = worksheet_pdf is not None
                                        has_scrapping = len(scrapping_docs) > 0
                                    except Exception as ex:
                                        print(f"[PM] Error fetching completed task data: {ex}")
                                        last_executed = "-"
                                        has_work_request = False
                                        has_worksheet = False
                                        has_scrapping = False
                                        scrapping_docs = []
                                    finally:
                                        session.close()
                                    
                                    # Use helper function to create card
                                    card = create_completed_task_card(
                                        task, last_history, last_executed,
                                        has_work_request, has_worksheet, has_scrapping, scrapping_docs
                                    )
                                    day_content.controls.append(card)
                                
                                day_expansion.controls = [day_content]
                                month_content.controls.append(day_expansion)
                            
                            month_expansion.controls = [month_content]
                            year_content.controls.append(month_expansion)
                        
                        year_expansion.controls = [year_content]
                        completed_tasks_list.controls.append(year_expansion)
        
        refresh_pm_tasks()
        
        # Machines with upcoming service section
        machines_list = ft.Column([], spacing=8, scroll=ft.ScrollMode.AUTO)
        
        # Operating hours notifications section
        operating_hours_list = ft.Column([], spacing=8, scroll=ft.ScrollMode.AUTO)
        
        def open_delegate_operating_hours_task(machine_data):
            """Open dialog to create PM task for operating hours update"""
            dialog_page = self.page if self.page else page
            
            # Get current user ID for this dialog
            ctx = get_app_context()
            dialog_user_id = ctx.user_id if ctx.is_authenticated() else None
            
            # Get users for assignment
            users = user_service.list_all_users()
            
            machine = machine_data['machine']
            next_update_date = machine_data['next_update_date']
            is_overdue = machine_data['is_overdue']
            
            # Pre-fill task name
            task_name_field = ft.TextField(
                label=translator.get_text("preventive_maintenance.task_name"),
                prefix_icon=ft.Icons.BUILD,
                value=f"Üzemóra ellenőrzés - {machine.name}",
                width=400,
            )
            
            # Task description
            task_description_field = ft.TextField(
                label=translator.get_text("preventive_maintenance.task_description"),
                prefix_icon=ft.Icons.DESCRIPTION,
                multiline=True,
                max_lines=3,
                value=f"Üzemóra ellenőrzés és korrekció a következő gépen:\n\nGép: {machine.name}\nSorozatszám: {machine.serial_number or '-'}\nModell: {machine.model or '-'}\nGyártó: {machine.manufacturer or '-'}\n\nKövetkező ellenőrzési dátum: {next_update_date.strftime('%Y-%m-%d') if next_update_date else '-'}",
                width=400,
            )
            
            # Assignment options
            assignment_radio = ft.RadioGroup(
                content=ft.Column([
                    ft.Radio(value="global", label=translator.get_text("preventive_maintenance.global_assignment")),
                    ft.Radio(value="assigned", label=translator.get_text("preventive_maintenance.assigned_to_user")),
                ], spacing=4),
                value="global",
            )
            
            # User dropdown (initially disabled)
            user_options = [ft.dropdown.Option(str(u.id), f"{u.full_name or u.username} ({u.username})") for u in users] if users else []
            assigned_user_dropdown = ft.Dropdown(
                label=translator.get_text("preventive_maintenance.assigned_user"),
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
            priority_dropdown = ft.Dropdown(
                label=translator.get_text("preventive_maintenance.priority"),
                prefix_icon=ft.Icons.PRIORITY_HIGH,
                options=[
                    ft.dropdown.Option("low", translator.get_text("preventive_maintenance.priority_low")),
                    ft.dropdown.Option("normal", translator.get_text("preventive_maintenance.priority_normal")),
                    ft.dropdown.Option("high", translator.get_text("preventive_maintenance.priority_high")),
                    ft.dropdown.Option("urgent", translator.get_text("preventive_maintenance.priority_urgent")),
                ],
                value="high" if is_overdue else "normal",
                width=200,
            )
            
            # Due date field
            due_date_field = ft.TextField(
                label=translator.get_text("preventive_maintenance.due_date"),
                prefix_icon=ft.Icons.CALENDAR_TODAY,
                value=next_update_date.strftime('%Y-%m-%d') if next_update_date else '',
                hint_text="YYYY-MM-DD",
                width=200,
            )
            
            def submit_task(_):
                try:
                    if not task_name_field.value:
                        raise ValueError(f"{translator.get_text('preventive_maintenance.task_name')} {translator.get_text('common.messages.required_field')}")
                    
                    machine_id = machine.id
                    
                    # Parse due date
                    due_date_value = None
                    if due_date_field.value:
                        try:
                            due_date_value = datetime.strptime(due_date_field.value, '%Y-%m-%d')
                        except ValueError:
                            raise ValueError(translator.get_text("common.messages.invalid_date_format"))
                    
                    assigned_to_user_id = None
                    if assignment_radio.value == "assigned":
                        if not assigned_user_dropdown.value:
                            raise ValueError(f"{translator.get_text('preventive_maintenance.assignment')} {translator.get_text('common.messages.required_field')}")
                        assigned_to_user_id = int(assigned_user_dropdown.value)
                    
                    # Create one-time PM task for operating hours update
                    pm_service.create_pm_task(
                        machine_id=machine_id,
                        task_name=task_name_field.value,
                        frequency_days=None,
                        task_description=task_description_field.value or None,
                        assigned_to_user_id=assigned_to_user_id,
                        priority=priority_dropdown.value or "normal",
                        status="pending",
                        due_date=due_date_value,
                        estimated_duration_minutes=15,  # Default 15 minutes for operating hours update
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
                        content=ft.Text(translator.get_text("preventive_maintenance.task_created")),
                        bgcolor=DesignSystem.SUCCESS
                    )
                    dialog_page.snack_bar.open = True
                    
                    # Refresh PM tasks list
                    refresh_pm_tasks()
                    dialog_page.update()
                except Exception as exc:
                    dialog_page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"{translator.get_text('common.messages.error_occurred')}: {str(exc)}"),
                        bgcolor=DesignSystem.ERROR
                    )
                    dialog_page.snack_bar.open = True
                    dialog_page.update()
            
            dialog = ft.AlertDialog(
                modal=True,
                title=ft.Row([
                    ft.Icon(ft.Icons.ACCESS_TIME, color="#F59E0B", size=24),
                    ft.Text("Üzemóra ellenőrzés delegálása", size=20, weight=ft.FontWeight.BOLD, color="#1F2937"),
                ], spacing=10),
                content=ft.Container(
                    content=ft.Column([
                        # Machine info card
                        create_info_card(
                            icon=ft.Icons.PRECISION_MANUFACTURING,
                            title=f"{machine.name}",
                            description=f"Sorozatszám: {machine.serial_number or '-'}\nModell: {machine.model or '-'}\nGyártó: {machine.manufacturer or '-'}",
                            icon_color=DesignSystem.ORANGE_500,
                            variant="orange",
                        ),
                        ft.Container(height=10),
                        ft.Divider(height=1),
                        ft.Container(height=10),
                        task_name_field,
                        task_description_field,
                        ft.Row([
                            priority_dropdown,
                            due_date_field,
                        ], spacing=10),
                        ft.Container(height=10),
                        ft.Text("Feladat delegálása", size=12, weight=ft.FontWeight.BOLD, color="#6B7280"),
                        assignment_radio,
                        assigned_user_dropdown,
                    ], spacing=8, tight=False, scroll=ft.ScrollMode.AUTO),
                    width=500,
                    height=600,
                    padding=15,
                ),
                actions=[
                    ft.TextButton(
                        translator.get_text("common.buttons.cancel"),
                        on_click=lambda _: setattr(dialog, 'open', False) or dialog_page.update(),
                        style=ft.ButtonStyle(color="#6B7280"),
                    ),
                    ft.ElevatedButton(
                        translator.get_text("preventive_maintenance.create_task"),
                        icon=ft.Icons.CHECK,
                        on_click=submit_task,
                        bgcolor=DesignSystem.ORANGE_500,
                        color="#FFFFFF",
                    ),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            
            try:
                dialog_page.open(dialog)
            except:
                dialog_page.dialog = dialog
                dialog.open = True
                dialog_page.update()
        
        if not machines_with_due_operating_hours:
            operating_hours_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(name=ft.Icons.ACCESS_TIME, size=48, color="#9CA3AF"),
                        ft.Text("Nincs esedékes üzemóra ellenőrzés", size=16, color="#6B7280"),
                    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=40,
                )
            )
        else:
            for machine_data in machines_with_due_operating_hours:
                machine = machine_data['machine']
                next_update_date = machine_data['next_update_date']
                is_overdue = machine_data['is_overdue']
                
                # Calculate days until update
                now = utcnow()
                if isinstance(now, datetime):
                    current_time = now
                else:
                    current_time = datetime.now()
                
                if next_update_date:
                    if next_update_date.tzinfo is None:
                        next_update_date = next_update_date.replace(tzinfo=timezone.utc)
                    if current_time.tzinfo is None:
                        current_time = current_time.replace(tzinfo=timezone.utc)
                    
                    days_until = (next_update_date - current_time).days
                else:
                    days_until = None
                
                days_text = f"{days_until} nap múlva" if days_until is not None and days_until > 0 else "Esedékes" if days_until is not None and days_until <= 0 else "Soha nem volt ellenőrizve"
                
                # Frequency info
                freq_type = machine.operating_hours_update_frequency_type
                freq_value = machine.operating_hours_update_frequency_value
                frequency_text = ""
                if freq_type == 'day':
                    frequency_text = f"Minden {freq_value} nap"
                elif freq_type == 'week':
                    frequency_text = f"Minden {freq_value} hét"
                elif freq_type == 'month':
                    frequency_text = f"Minden {freq_value} hónap"
                
                card = ft.Card(
                    elevation=2,
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.ACCESS_TIME, color="#F59E0B", size=20),
                                ft.Text(machine.name, size=16, weight=ft.FontWeight.BOLD, color="#1F2937"),
                                ft.Container(expand=True),
                                create_vibrant_badge(
                                    text="Esedékes" if is_overdue else "Közelgő",
                                    variant="pink" if is_overdue else "orange",
                                ) if is_overdue or (days_until is not None and days_until <= 7) else ft.Container(),
                            ], spacing=8),
                            ft.Text(f"Sorozatszám: {machine.serial_number or '-'}", size=12, color="#6B7280"),
                            ft.Text(f"Modell: {machine.model or '-'}", size=12, color="#6B7280"),
                            ft.Text(f"Gyártó: {machine.manufacturer or '-'}", size=12, color="#6B7280"),
                            ft.Text(
                                f"Következő ellenőrzés: {next_update_date.strftime('%Y-%m-%d') if next_update_date else '-'} ({days_text})",
                                size=12,
                                color="#EF4444" if is_overdue else "#F59E0B" if days_until is not None and days_until <= 7 else "#6B7280",
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(f"Ellenőrzési gyakoriság: {frequency_text}", size=11, color="#9CA3AF"),
                            ft.Text(f"Utolsó ellenőrzés: {machine.last_operating_hours_update.strftime('%Y-%m-%d') if machine.last_operating_hours_update else 'Soha nem volt ellenőrizve'}", size=11, color="#9CA3AF"),
                            ft.Text(f"Jelenlegi üzemóra: {machine.operating_hours or 0}", size=11, color="#9CA3AF"),
                            ft.Container(height=8),
                            ft.Row([
                                ft.Container(expand=True),
                                create_modern_button(
                                    text="Feladat delegálása",
                                    icon=ft.Icons.ASSIGNMENT if hasattr(ft.Icons, 'ASSIGNMENT') else ft.Icons.ADD_TASK,
                                    on_click=lambda e, md=machine_data: open_delegate_operating_hours_task(md),
                                    bgcolor=DesignSystem.ORANGE_500,
                                    color="#FFFFFF",
                                ),
                            ]),
                        ], spacing=4),
                        padding=16,
                    ),
                )
                operating_hours_list.controls.append(card)
        
        if not machines_with_service:
            machines_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(name=ft.Icons.PRECISION_MANUFACTURING, size=48, color="#9CA3AF"),
                        ft.Text("Nincs esedékes szervizelés", size=16, color="#6B7280"),
                    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=40,
                )
            )
        else:
            for machine in machines_with_service:
                if machine.next_service_date:
                    # Handle timezone-aware vs timezone-naive datetime comparison
                    next_service = machine.next_service_date
                    now = utcnow()
                    
                    # If next_service_date is timezone-naive, make it timezone-aware (assume UTC)
                    if next_service.tzinfo is None:
                        from datetime import timezone
                        next_service = next_service.replace(tzinfo=timezone.utc)
                    
                    # If utcnow() returns timezone-naive, make it timezone-aware
                    if now.tzinfo is None:
                        from datetime import timezone
                        now = now.replace(tzinfo=timezone.utc)
                    
                    days_until = (next_service - now).days
                else:
                    days_until = None
                
                days_text = f"{days_until} nap múlva" if days_until is not None and days_until > 0 else "Esedékes" if days_until is not None and days_until <= 0 else "-"
                
                def open_delegate_service_task(m=machine):
                    """Open dialog to create PM task for service"""
                    dialog_page = self.page if self.page else page
                    
                    # Get current user ID for this dialog
                    ctx = get_app_context()
                    dialog_user_id = ctx.user_id if ctx.is_authenticated() else None
                    
                    # Get users for assignment
                    users = user_service.list_all_users()
                    
                    # Pre-fill task name
                    task_name_field = ft.TextField(
                        label=translator.get_text("preventive_maintenance.task_name"),
                        prefix_icon=ft.Icons.BUILD,
                        value=f"Szervizelés - {m.name}",
                        width=400,
                    )
                    
                    # Task description
                    task_description_field = ft.TextField(
                        label=translator.get_text("preventive_maintenance.task_description"),
                        prefix_icon=ft.Icons.DESCRIPTION,
                        multiline=True,
                        max_lines=3,
                        value=f"Szervizelés a következő gépen:\n\nGép: {m.name}\nSorozatszám: {m.serial_number or '-'}\nModell: {m.model or '-'}\nGyártó: {m.manufacturer or '-'}\n\nKövetkező szervizelési dátum: {m.next_service_date.strftime('%Y-%m-%d') if m.next_service_date else '-'}",
                        width=400,
                    )
                    
                    # Assignment options
                    assignment_radio = ft.RadioGroup(
                        content=ft.Column([
                            ft.Radio(value="global", label=translator.get_text("preventive_maintenance.global_assignment")),
                            ft.Radio(value="assigned", label=translator.get_text("preventive_maintenance.assigned_to_user")),
                        ], spacing=4),
                        value="global",
                    )
                    
                    # User dropdown (initially disabled)
                    user_options = [ft.dropdown.Option(str(u.id), f"{u.full_name or u.username} ({u.username})") for u in users] if users else []
                    assigned_user_dropdown = ft.Dropdown(
                        label=translator.get_text("preventive_maintenance.assigned_user"),
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
                    priority_dropdown = ft.Dropdown(
                        label=translator.get_text("preventive_maintenance.priority"),
                        prefix_icon=ft.Icons.PRIORITY_HIGH,
                        options=[
                            ft.dropdown.Option("low", translator.get_text("preventive_maintenance.priority_low")),
                            ft.dropdown.Option("normal", translator.get_text("preventive_maintenance.priority_normal")),
                            ft.dropdown.Option("high", translator.get_text("preventive_maintenance.priority_high")),
                            ft.dropdown.Option("urgent", translator.get_text("preventive_maintenance.priority_urgent")),
                        ],
                        value="high" if days_until is not None and days_until <= 7 else "normal",
                        width=200,
                    )
                    
                    # Due date field
                    due_date_field = ft.TextField(
                        label=translator.get_text("preventive_maintenance.due_date"),
                        prefix_icon=ft.Icons.CALENDAR_TODAY,
                        value=m.next_service_date.strftime('%Y-%m-%d') if m.next_service_date else '',
                        hint_text="YYYY-MM-DD",
                        width=200,
                    )
                    
                    def submit_task(_):
                        try:
                            if not task_name_field.value:
                                raise ValueError(f"{translator.get_text('preventive_maintenance.task_name')} {translator.get_text('common.messages.required_field')}")
                            
                            machine_id = m.id
                            
                            # Parse due date
                            due_date_value = None
                            if due_date_field.value:
                                try:
                                    due_date_value = datetime.strptime(due_date_field.value, '%Y-%m-%d')
                                except ValueError:
                                    raise ValueError(translator.get_text("common.messages.invalid_date_format"))
                            
                            assigned_to_user_id = None
                            if assignment_radio.value == "assigned":
                                if not assigned_user_dropdown.value:
                                    raise ValueError(f"{translator.get_text('preventive_maintenance.assignment')} {translator.get_text('common.messages.required_field')}")
                                assigned_to_user_id = int(assigned_user_dropdown.value)
                            
                            # Create one-time PM task for service
                            pm_service.create_pm_task(
                                machine_id=machine_id,
                                task_name=task_name_field.value,
                                frequency_days=None,
                                task_description=task_description_field.value or None,
                                assigned_to_user_id=assigned_to_user_id,
                                priority=priority_dropdown.value or "normal",
                                status="pending",
                                due_date=due_date_value,
                                estimated_duration_minutes=60,  # Default 60 minutes for service
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
                                content=ft.Text(translator.get_text("preventive_maintenance.task_created")),
                                bgcolor=DesignSystem.SUCCESS
                            )
                            dialog_page.snack_bar.open = True
                            
                            # Refresh PM tasks list
                            refresh_pm_tasks()
                            dialog_page.update()
                        except Exception as exc:
                            dialog_page.snack_bar = ft.SnackBar(
                                content=ft.Text(f"{translator.get_text('common.messages.error_occurred')}: {str(exc)}"),
                                bgcolor=DesignSystem.ERROR
                            )
                            dialog_page.snack_bar.open = True
                            dialog_page.update()
                    
                    dialog = ft.AlertDialog(
                        modal=True,
                        title=ft.Row([
                            ft.Icon(ft.Icons.BUILD, color="#10B981", size=24),
                            ft.Text("Szervizelés delegálása", size=20, weight=ft.FontWeight.BOLD, color="#1F2937"),
                        ], spacing=10),
                        content=ft.Container(
                            content=ft.Column([
                                # Machine info card
                                create_info_card(
                                    icon=ft.Icons.PRECISION_MANUFACTURING,
                                    title=f"{m.name}",
                                    description=f"Sorozatszám: {m.serial_number or '-'}\nModell: {m.model or '-'}\nGyártó: {m.manufacturer or '-'}",
                                    icon_color=DesignSystem.EMERALD_500,
                                    variant="emerald",
                                ),
                                ft.Container(height=10),
                                ft.Divider(height=1),
                                ft.Container(height=10),
                                task_name_field,
                                task_description_field,
                                ft.Row([
                                    priority_dropdown,
                                    due_date_field,
                                ], spacing=10),
                                ft.Container(height=10),
                                ft.Text("Feladat delegálása", size=12, weight=ft.FontWeight.BOLD, color="#6B7280"),
                                assignment_radio,
                                assigned_user_dropdown,
                            ], spacing=8, tight=False, scroll=ft.ScrollMode.AUTO),
                            width=500,
                            height=600,
                            padding=15,
                        ),
                        actions=[
                            ft.TextButton(
                                translator.get_text("common.buttons.cancel"),
                                on_click=lambda _: setattr(dialog, 'open', False) or dialog_page.update(),
                                style=ft.ButtonStyle(color="#6B7280"),
                            ),
                            ft.ElevatedButton(
                                translator.get_text("preventive_maintenance.create_task"),
                                icon=ft.Icons.CHECK,
                                on_click=submit_task,
                                bgcolor=DesignSystem.EMERALD_500,
                                color="#FFFFFF",
                            ),
                        ],
                        actions_alignment=ft.MainAxisAlignment.END,
                    )
                    
                    try:
                        dialog_page.open(dialog)
                    except:
                        dialog_page.dialog = dialog
                        dialog.open = True
                        dialog_page.update()
                
                card = ft.Card(
                    elevation=2,
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.PRECISION_MANUFACTURING, color="#10B981", size=20),
                                ft.Text(machine.name, size=16, weight=ft.FontWeight.BOLD, color="#1F2937"),
                            ], spacing=8),
                            ft.Text(f"Sorozatszám: {machine.serial_number or '-'}", size=12, color="#6B7280"),
                            ft.Text(
                                f"Következő szervizelés: {machine.next_service_date.strftime('%Y-%m-%d') if machine.next_service_date else '-'} ({days_text})",
                                size=12,
                                color="#EF4444" if days_until is not None and days_until <= 7 else "#F59E0B" if days_until is not None and days_until <= 30 else "#6B7280",
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(f"Utolsó szervizelés: {machine.last_service_date.strftime('%Y-%m-%d') if machine.last_service_date else 'Nincs'}", size=11, color="#9CA3AF"),
                            ft.Container(height=8),
                            ft.Row([
                                ft.Container(expand=True),
                                create_modern_button(
                                    text="Feladat delegálása",
                                    icon=ft.Icons.ASSIGNMENT if hasattr(ft.Icons, 'ASSIGNMENT') else ft.Icons.ADD_TASK,
                                    on_click=lambda e, m=machine: open_delegate_service_task(m),
                                    bgcolor=DesignSystem.EMERALD_500,
                                    color="#FFFFFF",
                                ),
                            ]),
                        ], spacing=4),
                        padding=16,
                    ),
                )
                machines_list.controls.append(card)

        # Overview button (service records)
        overview_btn = ft.ElevatedButton(
            text="Karbantartások áttekintése",
            icon=ft.Icons.HISTORY,
            tooltip="Összes elvégzett karbantartás megtekintése",
            on_click=lambda _: open_maintenance_overview(),
            bgcolor="#6366F1",
            color="#FFFFFF",
            height=40,
        )
        
        # PM History button (PM task execution history)
        def open_pm_history_overview():
            """Open dialog with PM task execution history grouped by date"""
            # Import timezone locally to ensure it's available in closure
            from datetime import timezone as tz
            dialog_page = self.page if self.page else page
            
            # Get all PM history records
            all_history = pm_service.list_pm_history(user_id=current_user_id, completion_status="completed")
            
            if not all_history:
                empty_dialog = ft.AlertDialog(
                    modal=True,
                    title=ft.Row([
                        ft.Icon(ft.Icons.HISTORY, color="#6366F1", size=24),
                        ft.Text(translator.get_text("preventive_maintenance.completed_tasks"), size=20, weight=ft.FontWeight.BOLD, color="#1F2937"),
                    ], spacing=10),
                    content=ft.Container(
                        content=ft.Column([
                            ft.Icon(name=ft.Icons.BUILD, size=48, color="#9CA3AF"),
                            ft.Text(translator.get_text("preventive_maintenance.no_completed_tasks"), size=16, color="#6B7280"),
                        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16),
                        padding=40,
                    ),
                    actions=[
                        ft.TextButton(translator.get_text("common.buttons.close"), on_click=lambda _: setattr(empty_dialog, 'open', False) or dialog_page.update(), style=ft.ButtonStyle(color="#6B7280")),
                    ],
                )
                try:
                    dialog_page.open(empty_dialog)
                except:
                    dialog_page.dialog = empty_dialog
                    empty_dialog.open = True
                    dialog_page.update()
                return
            
            # Group history by year/month/day
            grouped_history = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
            
            # Hungarian month names
            month_names = {
                1: "január", 2: "február", 3: "március", 4: "április",
                5: "május", 6: "június", 7: "július", 8: "augusztus",
                9: "szeptember", 10: "október", 11: "november", 12: "december"
            }
            
            for history in all_history:
                if history.executed_date:
                    exec_date = history.executed_date
                    if exec_date.tzinfo is None:
                        exec_date = exec_date.replace(tzinfo=tz.utc)
                    
                    year = exec_date.year
                    month = exec_date.month
                    day = exec_date.day
                    
                    # Get task and machine info
                    task = history.pm_task if hasattr(history, 'pm_task') and history.pm_task else None
                    if task:
                        if task.machine_id:
                            machine_name = task.machine.name if hasattr(task, 'machine') and task.machine else f"Gép ID: {task.machine_id}"
                        else:
                            machine_name = f"{translator.get_text('preventive_maintenance.other')}: {task.location or '-'}"
                    else:
                        machine_name = "Ismeretlen"
                    
                    grouped_history[year][month][day].append((history, task, machine_name))
            
            # Build UI with expandable sections
            history_list = ft.Column([], spacing=8, scroll=ft.ScrollMode.AUTO)
            
            # Sort years descending
            sorted_years = sorted(grouped_history.keys(), reverse=True)
            
            for year in sorted_years:
                year_expansion = ft.ExpansionTile(
                    title=ft.Text(f"{year}. {translator.get_text('common.time.year')}", size=14, weight=ft.FontWeight.BOLD, color="#1F2937"),
                    leading=ft.Icon(ft.Icons.CALENDAR_MONTH, color="#6366F1"),
                    initially_expanded=False,
                )
                year_content = ft.Column([], spacing=4)
                
                # Sort months descending
                sorted_months = sorted(grouped_history[year].keys(), reverse=True)
                
                for month in sorted_months:
                    month_expansion = ft.ExpansionTile(
                        title=ft.Text(f"{month_names[month]}", size=13, weight=ft.FontWeight.BOLD, color="#374151"),
                        leading=ft.Icon(ft.Icons.CALENDAR_VIEW_MONTH, color="#8B5CF6"),
                        initially_expanded=False,
                    )
                    month_content = ft.Column([], spacing=4)
                    
                    # Sort days descending
                    sorted_days = sorted(grouped_history[year][month].keys(), reverse=True)
                    
                    for day in sorted_days:
                        day_expansion = ft.ExpansionTile(
                            title=ft.Text(f"{day}. {translator.get_text('common.time.day')}", size=12, weight=ft.FontWeight.BOLD, color="#6B7280"),
                            leading=ft.Icon(ft.Icons.CALENDAR_TODAY, color="#10B981"),
                            initially_expanded=True,
                        )
                        day_content = ft.Column([], spacing=6)
                        
                        for history, task, machine_name in grouped_history[year][month][day]:
                            exec_date = history.executed_date
                            if exec_date.tzinfo is None:
                                exec_date = exec_date.replace(tzinfo=tz.utc)
                            
                            card = ft.Card(
                                elevation=1,
                                content=ft.Container(
                                    content=ft.Column([
                                        ft.Row([
                                            ft.Column([
                                                ft.Text(
                                                    task.task_name if task else "Ismeretlen feladat",
                                                    size=13,
                                                    weight=ft.FontWeight.BOLD,
                                                    color="#1F2937",
                                                ),
                                                ft.Text(f"Gép/Helyszín: {machine_name}", size=11, color="#6B7280"),
                                            ], expand=True),
                                            ft.Text(
                                                exec_date.strftime("%H:%M"),
                                                size=12,
                                                color="#9CA3AF",
                                            ),
                                        ], spacing=8),
                                        ft.Divider(height=1, color="#E5E7EB"),
                                        ft.Row([
                                            ft.Text(f"{translator.get_text('preventive_maintenance.executed_by')}: {history.completed_user.full_name if history.completed_user else '-'}", size=11, color="#6B7280"),
                                            ft.Container(width=20),
                                            ft.Text(f"{translator.get_text('preventive_maintenance.duration_minutes')}: {history.duration_minutes or 0} {translator.get_text('common.time.minutes')}", size=11, color="#6B7280"),
                                        ]),
                                        ft.Text(f"Megjegyzés: {history.notes or '-'}", size=11, color="#9CA3AF", italic=True) if history.notes else ft.Container(),
                                        ft.Divider(height=1, color="#E5E7EB"),
                                        # Document buttons
                                        ft.Row([
                                            ft.ElevatedButton(
                                                translator.get_text("preventive_maintenance.work_request"),
                                                icon=ft.Icons.PICTURE_AS_PDF,
                                                on_click=lambda _, h=history: view_work_request_pdf(h),
                                                bgcolor=DesignSystem.ERROR,
                                                color="#FFFFFF",
                                                height=32,
                                                tooltip="Munkaigénylő lap megtekintése / View work request",
                                            ),
                                            ft.ElevatedButton(
                                                translator.get_text("preventive_maintenance.worksheet"),
                                                icon=ft.Icons.DESCRIPTION,
                                                on_click=lambda _, h=history: view_pm_worksheet_pdf(h),
                                                bgcolor=DesignSystem.SUCCESS,
                                                color="#FFFFFF",
                                                height=32,
                                                tooltip="Munkalap megtekintése / View worksheet",
                                            ),
                                            ft.ElevatedButton(
                                                translator.get_text("common.buttons.download"),
                                                icon=ft.Icons.DOWNLOAD,
                                                on_click=lambda _, h=history: download_combined_pdf(h),
                                                bgcolor="#6366F1",
                                                color="#FFFFFF",
                                                height=32,
                                                tooltip="Dokumentumok letöltése / Download documents",
                                            ),
                                        ], spacing=8),
                                    ], spacing=4, tight=True),
                                    padding=12,
                                ),
                            )
                            
                            def view_work_request_pdf(h):
                                """Open work request DOCX"""
                                try:
                                    from services import pdf_service
                                    from database.models import WorkRequestPDF
                                    from database.session_manager import SessionLocal
                                    from pathlib import Path
                                    import os
                                    
                                    session = SessionLocal()
                                    pdf_record = session.query(WorkRequestPDF).filter_by(pm_task_id=h.pm_task_id).first()
                                    session.close()
                                    
                                    if pdf_record and Path(pdf_record.pdf_path).exists():
                                        os.startfile(pdf_record.pdf_path)
                                    else:
                                        page.snack_bar = ft.SnackBar(content=ft.Text(translator.get_text("preventive_maintenance.document_not_found")), bgcolor=DesignSystem.ERROR)
                                        page.snack_bar.open = True
                                        page.update()
                                except Exception as ex:
                                    page.snack_bar = ft.SnackBar(content=ft.Text(f"{translator.get_text('common.messages.error_occurred')}: {ex}"), bgcolor=DesignSystem.ERROR)
                                    page.snack_bar.open = True
                                    page.update()
                            
                            def view_pm_worksheet_pdf(h):
                                """Open PM worksheet DOCX"""
                                try:
                                    from services import pdf_service
                                    from database.models import PMWorksheetPDF
                                    from database.session_manager import SessionLocal
                                    from pathlib import Path
                                    import os
                                    
                                    session = SessionLocal()
                                    pdf_record = session.query(PMWorksheetPDF).filter_by(pm_history_id=h.id).first()
                                    session.close()
                                    
                                    if pdf_record and Path(pdf_record.pdf_path).exists():
                                        os.startfile(pdf_record.pdf_path)
                                    else:
                                        page.snack_bar = ft.SnackBar(content=ft.Text(translator.get_text("preventive_maintenance.document_not_found")), bgcolor=DesignSystem.ERROR)
                                        page.snack_bar.open = True
                                        page.update()
                                except Exception as ex:
                                    page.snack_bar = ft.SnackBar(content=ft.Text(f"{translator.get_text('common.messages.error_occurred')}: {ex}"), bgcolor=DesignSystem.ERROR)
                                    page.snack_bar.open = True
                                    page.update()
                            
                            def download_combined_pdf(h):
                                """Download combined documents (work request + worksheet)"""
                                try:
                                    from database.models import WorkRequestPDF, PMWorksheetPDF
                                    from database.session_manager import SessionLocal
                                    from pathlib import Path
                                    import os
                                    import shutil
                                    
                                    session = SessionLocal()
                                    work_request_doc = session.query(WorkRequestPDF).filter_by(pm_task_id=h.pm_task_id).first()
                                    pm_worksheet_doc = session.query(PMWorksheetPDF).filter_by(pm_history_id=h.id).first()
                                    session.close()
                                    
                                    doc_paths = []
                                    if work_request_doc and Path(work_request_doc.pdf_path).exists():
                                        doc_paths.append(work_request_doc.pdf_path)
                                    if pm_worksheet_doc and Path(pm_worksheet_doc.pdf_path).exists():
                                        doc_paths.append(pm_worksheet_doc.pdf_path)
                                    
                                    if not doc_paths:
                                        page.snack_bar = ft.SnackBar(content=ft.Text(translator.get_text("preventive_maintenance.no_documents_available")), bgcolor=DesignSystem.ERROR)
                                        page.snack_bar.open = True
                                        page.update()
                                        return
                                    
                                    # Create a folder with both documents
                                    output_dir = Path("generated_pdfs") / f"pm_combined_{h.id}"
                                    output_dir.mkdir(parents=True, exist_ok=True)
                                    
                                    # Copy documents to folder
                                    for doc_path in doc_paths:
                                        shutil.copy2(doc_path, output_dir / Path(doc_path).name)
                                    
                                    # Open folder
                                    os.startfile(output_dir)
                                    
                                    page.snack_bar = ft.SnackBar(content=ft.Text(translator.get_text("preventive_maintenance.documents_copied")), bgcolor=DesignSystem.SUCCESS)
                                    page.snack_bar.open = True
                                    page.update()
                                except Exception as ex:
                                    page.snack_bar = ft.SnackBar(content=ft.Text(f"{translator.get_text('common.messages.error_occurred')}: {ex}"), bgcolor=DesignSystem.ERROR)
                                    page.snack_bar.open = True
                                    page.update()
                            
                            day_content.controls.append(card)
                        
                        day_expansion.controls = [day_content]
                        month_content.controls.append(day_expansion)
                    
                    month_expansion.controls = [month_content]
                    year_content.controls.append(month_expansion)
                
                year_expansion.controls = [year_content]
                history_list.controls.append(year_expansion)
            
            # Total count
            total_count = len(all_history)
            
            dialog = ft.AlertDialog(
                modal=True,
                title=ft.Row([
                    ft.Icon(ft.Icons.HISTORY, color="#6366F1", size=24),
                    ft.Text(translator.get_text("preventive_maintenance.completed_tasks"), size=20, weight=ft.FontWeight.BOLD, color="#1F2937"),
                ], spacing=10),
                content=ft.Container(
                    content=ft.Column([
                        ft.Container(
                            content=ft.Row([
                                ft.Text(translator.get_text("preventive_maintenance.total_completed").replace("{count}", str(total_count)), size=12, weight=ft.FontWeight.BOLD, color="#6B7280"),
                            ]),
                            padding=ft.padding.only(bottom=8),
                        ),
                        ft.Divider(height=1, color="#E5E7EB"),
                        history_list,
                    ], spacing=8, tight=False, scroll=ft.ScrollMode.AUTO),
                    width=900,
                    height=700,
                    padding=15,
                ),
                actions=[
                    ft.TextButton(
                        translator.get_text("common.buttons.close"),
                        on_click=lambda _: setattr(dialog, 'open', False) or dialog_page.update(),
                        style=ft.ButtonStyle(color="#6B7280")
                    ),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            
            try:
                dialog_page.open(dialog)
            except:
                dialog_page.dialog = dialog
                dialog.open = True
                dialog_page.update()
        
        pm_history_btn = ft.ElevatedButton(
            text=translator.get_text("preventive_maintenance.completed_tasks"),
            icon=ft.Icons.CHECK_CIRCLE,
            tooltip=translator.get_text("preventive_maintenance.completed_tasks"),
            on_click=lambda _: open_pm_history_overview(),
            bgcolor=DesignSystem.SUCCESS,
            color="#FFFFFF",
            height=40,
        )
        
        # Create PM Task button (only for Manager and Maintenance Supervisor)
        create_task_btn = None
        if can_edit_pm():
            def open_create_pm_task_dialog(_):
                dialog_page = self.page if self.page else page
                
                # Get current user ID for this dialog
                ctx = get_app_context()
                dialog_user_id = ctx.user_id if ctx.is_authenticated() else None
                
                # Get machines and users
                machines = asset_service.list_machines()
                users = user_service.list_all_users()
                
                # Form fields
                machine_options = [ft.dropdown.Option(str(m.id), f"{m.name} ({m.serial_number or '-'})") for m in machines] if machines else []
                machine_options.append(ft.dropdown.Option("other", translator.get_text("preventive_maintenance.other")))
                
                machine_dropdown = ft.Dropdown(
                    label=translator.get_text("preventive_maintenance.machine"),
                    prefix_icon=ft.Icons.PRECISION_MANUFACTURING,
                    options=machine_options,
                    width=300,
                )
                
                # Location field for "other" option
                location_field = ft.TextField(
                    label=translator.get_text("preventive_maintenance.location"),
                    prefix_icon=ft.Icons.LOCATION_ON,
                    width=300,
                    visible=False,
                )
                
                def on_machine_change(_):
                    location_field.visible = (machine_dropdown.value == "other")
                    dialog_page.update()
                
                machine_dropdown.on_change = on_machine_change
                
                task_name_field = ft.TextField(
                    label=translator.get_text("preventive_maintenance.task_name"),
                    prefix_icon=ft.Icons.BUILD,
                    width=300,
                )
                
                task_description_field = ft.TextField(
                    label=translator.get_text("preventive_maintenance.description"),
                    multiline=True,
                    min_lines=3,
                    prefix_icon=ft.Icons.DESCRIPTION,
                )
                
                # Task type selection (recurring or one-time)
                task_type_options = [
                    ft.Radio(value="recurring", label=translator.get_text("preventive_maintenance.task_type_recurring")),
                    ft.Radio(value="one_time", label=translator.get_text("preventive_maintenance.task_type_one_time")),
                ]
                task_type_radio = ft.RadioGroup(
                    content=ft.Column(task_type_options, spacing=4),
                    value="recurring",
                )
                
                frequency_field = ft.TextField(
                    label=translator.get_text("preventive_maintenance.frequency_days"),
                    keyboard_type=ft.KeyboardType.NUMBER,
                    prefix_icon=ft.Icons.REPEAT,
                    value="30",
                    width=150,
                )
                
                def on_task_type_change(_):
                    frequency_field.visible = (task_type_radio.value == "recurring")
                    if task_type_radio.value == "one_time":
                        frequency_field.value = ""
                    elif not frequency_field.value:
                        frequency_field.value = "30"
                    dialog_page.update()
                
                task_type_radio.on_change = on_task_type_change
                
                priority_dropdown = ft.Dropdown(
                    label=translator.get_text("preventive_maintenance.priority"),
                    prefix_icon=ft.Icons.FLAG,
                    options=[
                        ft.dropdown.Option("low", translator.get_text("preventive_maintenance.priority_low")),
                        ft.dropdown.Option("normal", translator.get_text("preventive_maintenance.priority_normal")),
                        ft.dropdown.Option("high", translator.get_text("preventive_maintenance.priority_high")),
                        ft.dropdown.Option("urgent", translator.get_text("preventive_maintenance.priority_urgent")),
                    ],
                    value="normal",
                    width=150,
                )
                
                assignment_type = [ft.Radio(value="global", label=translator.get_text("preventive_maintenance.assignment_global"))]
                assignment_type.append(ft.Radio(value="assigned", label=translator.get_text("preventive_maintenance.assignment_assigned")))
                assignment_radio = ft.RadioGroup(
                    content=ft.Column(assignment_type, spacing=4),
                    value="global",
                )
                
                assigned_user_dropdown = ft.Dropdown(
                    label=translator.get_text("preventive_maintenance.assignment"),
                    prefix_icon=ft.Icons.PERSON,
                    options=[ft.dropdown.Option(str(u.id), u.full_name or u.username) for u in users] if users else [],
                    width=300,
                    visible=False,
                )
                
                def on_assignment_change(_):
                    assigned_user_dropdown.visible = (assignment_radio.value == "assigned")
                    dialog_page.update()
                
                assignment_radio.on_change = on_assignment_change
                
                estimated_duration_field = ft.TextField(
                    label=translator.get_text("preventive_maintenance.estimated_duration"),
                    keyboard_type=ft.KeyboardType.NUMBER,
                    prefix_icon=ft.Icons.ACCESS_TIME,
                    width=150,
                )
                
                # Due date picker (similar to service record)
                due_date_value = [None]
                due_date_display_field = ft.TextField(
                    label=f"{translator.get_text('preventive_maintenance.due_date')} ({translator.get_text('common.optional')})",
                    hint_text=translator.get_text("common.click_calendar_icon"),
                    read_only=True,
                    prefix_icon=ft.Icons.SCHEDULE,
                )
                
                year_field = ft.TextField(label="Év", value=str(datetime.now().year), width=100, keyboard_type=ft.KeyboardType.NUMBER, dense=True, visible=False)
                month_field = ft.TextField(label="Hónap", value=str(datetime.now().month), width=100, keyboard_type=ft.KeyboardType.NUMBER, dense=True, visible=False)
                day_field = ft.TextField(label="Nap", value=str(datetime.now().day), width=100, keyboard_type=ft.KeyboardType.NUMBER, dense=True, visible=False)
                
                date_picker_row = ft.Row([year_field, month_field, day_field], spacing=8)
                date_picker_row.visible = False
                
                def toggle_date_picker(_):
                    date_picker_row.visible = not date_picker_row.visible
                    year_field.visible = date_picker_row.visible
                    month_field.visible = date_picker_row.visible
                    day_field.visible = date_picker_row.visible
                    if date_picker_row.visible and not due_date_display_field.value:
                        year_field.value = str(datetime.now().year)
                        month_field.value = str(datetime.now().month)
                        day_field.value = str(datetime.now().day)
                    elif not date_picker_row.visible:
                        try:
                            year = int(year_field.value)
                            month = int(month_field.value)
                            day = int(day_field.value)
                            selected_date = datetime(year, month, day)
                            due_date_value[0] = selected_date
                            due_date_display_field.value = selected_date.strftime("%Y-%m-%d")
                        except:
                            pass
                    dialog_page.update()
                
                def on_date_field_change(_):
                    try:
                        year = int(year_field.value or datetime.now().year)
                        month = int(month_field.value or datetime.now().month)
                        day = int(day_field.value or datetime.now().day)
                        selected_date = datetime(year, month, day)
                        due_date_value[0] = selected_date
                        due_date_display_field.value = selected_date.strftime("%Y-%m-%d")
                        dialog_page.update()
                    except:
                        pass
                
                year_field.on_change = on_date_field_change
                month_field.on_change = on_date_field_change
                day_field.on_change = on_date_field_change
                
                due_date_field = ft.Column([
                    ft.Row([
                        ft.Container(content=due_date_display_field, expand=True),
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
                
                def submit_task(_):
                    try:
                        print(f"[PM] submit_task called")
                        if not machine_dropdown.value:
                            raise ValueError(f"{translator.get_text('preventive_maintenance.machine')} {translator.get_text('common.messages.required_field')}")
                        
                        # Check if "other" is selected and location is provided
                        if machine_dropdown.value == "other":
                            if not location_field.value:
                                raise ValueError(f"{translator.get_text('preventive_maintenance.location')} {translator.get_text('common.messages.required_field')}")
                            machine_id = None
                            location = location_field.value
                        else:
                            machine_id = int(machine_dropdown.value)
                            location = None
                        
                        if not task_name_field.value:
                            raise ValueError(f"{translator.get_text('preventive_maintenance.task_name')} {translator.get_text('common.messages.required_field')}")
                        
                        task_type = task_type_radio.value or "recurring"
                        frequency_days = None
                        
                        if task_type == "recurring":
                            if not frequency_field.value:
                                raise ValueError(f"{translator.get_text('preventive_maintenance.frequency_days')} {translator.get_text('common.messages.required_field')}")
                            frequency_days = int(frequency_field.value)
                        
                        assigned_to_user_id = None
                        
                        if assignment_radio.value == "assigned":
                            if not assigned_user_dropdown.value:
                                raise ValueError(f"{translator.get_text('preventive_maintenance.assignment')} {translator.get_text('common.messages.required_field')}")
                            assigned_to_user_id = int(assigned_user_dropdown.value)
                        
                        estimated_duration = int(estimated_duration_field.value) if estimated_duration_field.value else None
                        
                        print(f"[PM] Creating task: name={task_name_field.value}, machine_id={machine_id}, location={location}, task_type={task_type}")
                        
                        pm_service.create_pm_task(
                            machine_id=machine_id,
                            task_name=task_name_field.value,
                            frequency_days=frequency_days,
                            task_description=task_description_field.value or None,
                            assigned_to_user_id=assigned_to_user_id,
                            priority=priority_dropdown.value or "normal",
                            status="pending",
                            due_date=due_date_value[0],
                            estimated_duration_minutes=estimated_duration,
                            created_by_user_id=dialog_user_id,
                            location=location,
                            task_type=task_type,
                        )
                        
                        print(f"[PM] Task created successfully")
                        
                        # Close dialog
                        try:
                            dialog_page.close(dialog)
                        except Exception as close_err:
                            print(f"[PM] Error closing dialog: {close_err}")
                            dialog.open = False
                            dialog_page.update()
                        
                        # Show success message
                        dialog_page.snack_bar = ft.SnackBar(content=ft.Text(translator.get_text("preventive_maintenance.task_created")), bgcolor=DesignSystem.SUCCESS)
                        dialog_page.snack_bar.open = True
                        
                        # Refresh PM tasks list
                        print(f"[PM] Refreshing PM tasks list")
                        refresh_pm_tasks()
                        dialog_page.update()
                        print(f"[PM] Page updated")
                    except Exception as exc:
                        import traceback
                        error_trace = traceback.format_exc()
                        print(f"[PM] Error in submit_task: {exc}")
                        print(f"[PM] Traceback: {error_trace}")
                        dialog_page.snack_bar = ft.SnackBar(content=ft.Text(f"{translator.get_text('common.messages.error_occurred')}: {str(exc)}"), bgcolor=DesignSystem.ERROR)
                        dialog_page.snack_bar.open = True
                        dialog_page.update()
                
                dialog = ft.AlertDialog(
                    modal=True,
                    title=ft.Row([
                        ft.Icon(ft.Icons.ADD_TASK, color="#6366F1", size=24),
                        ft.Text(translator.get_text("preventive_maintenance.create_new"), size=20, weight=ft.FontWeight.BOLD, color="#1F2937"),
                    ], spacing=10),
                    content=ft.Container(
                        content=ft.Column([
                            ft.Container(
                                content=ft.Column([
                                    ft.Text(translator.get_text("common.basic_info"), size=12, weight=ft.FontWeight.BOLD, color="#6B7280"),
                                    ft.Row([
                                        ft.Container(content=machine_dropdown, expand=1),
                                        ft.Container(content=task_name_field, expand=1, margin=ft.margin.only(left=10)),
                                    ]),
                                    ft.Container(content=location_field, padding=ft.padding.only(top=8)),
                                    task_description_field,
                                ], spacing=8),
                                padding=ft.padding.only(bottom=10),
                            ),
                            ft.Divider(height=1, color="#E5E7EB"),
                            ft.Container(
                                content=ft.Column([
                                    ft.Text(translator.get_text("common.settings"), size=12, weight=ft.FontWeight.BOLD, color="#6B7280"),
                                    ft.Container(
                                        content=ft.Column([
                                            ft.Text(translator.get_text("preventive_maintenance.task_type"), size=11, weight=ft.FontWeight.BOLD, color="#6B7280"),
                                            task_type_radio,
                                        ], spacing=4),
                                        padding=ft.padding.only(bottom=8),
                                    ),
                                    ft.Row([
                                        ft.Container(content=frequency_field, expand=1),
                                        ft.Container(content=priority_dropdown, expand=1, margin=ft.margin.only(left=10)),
                                        ft.Container(content=estimated_duration_field, expand=1, margin=ft.margin.only(left=10)),
                                    ]),
                                ], spacing=8),
                                padding=ft.padding.only(top=10, bottom=10),
                            ),
                            ft.Divider(height=1, color="#E5E7EB"),
                            ft.Container(
                                content=ft.Column([
                                    ft.Text(translator.get_text("preventive_maintenance.assignment"), size=12, weight=ft.FontWeight.BOLD, color="#6B7280"),
                                    assignment_radio,
                                    ft.Container(content=assigned_user_dropdown, padding=ft.padding.only(left=20, top=8)),
                                ], spacing=8),
                                padding=ft.padding.only(top=10, bottom=10),
                            ),
                            ft.Divider(height=1, color="#E5E7EB"),
                            ft.Container(
                                content=ft.Column([
                                    ft.Text(translator.get_text("preventive_maintenance.due_date"), size=12, weight=ft.FontWeight.BOLD, color="#6B7280"),
                                    due_date_field,
                                ], spacing=8),
                                padding=ft.padding.only(top=10, bottom=10),
                            ),
                        ], tight=False, spacing=12, scroll=ft.ScrollMode.AUTO),
                        width=700, height=650, padding=15,
                    ),
                    actions=[
                        ft.TextButton(translator.get_text("common.buttons.cancel"), on_click=lambda _: setattr(dialog, 'open', False) or dialog_page.update(), style=ft.ButtonStyle(color="#6B7280")),
                        ft.ElevatedButton(translator.get_text("common.buttons.create"), icon=ft.Icons.ADD, on_click=submit_task, style=ft.ButtonStyle(bgcolor="#6366F1", color="#FFFFFF")),
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                )
                
                try:
                    dialog_page.open(dialog)
                except:
                    dialog_page.dialog = dialog
                    dialog.open = True
                    dialog_page.update()
            
            create_task_btn = ft.ElevatedButton(
                text=f"+ {translator.get_text('preventive_maintenance.create_new')}",
                icon=ft.Icons.ADD_TASK,
                tooltip=translator.get_text("preventive_maintenance.create_new"),
                on_click=open_create_pm_task_dialog,
                bgcolor=DesignSystem.SUCCESS,
                color="#FFFFFF",
                height=40,
            )

        return ft.Column([
            ft.Row([
                ft.Text("Megelőző karbantartás", size=18, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                pm_history_btn,
                ft.Container(width=10),
                overview_btn,
                ft.Container(width=10) if create_task_btn else ft.Container(),
                create_task_btn if create_task_btn else ft.Container(),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Container(height=10),
            ft.Text("Esedékes PM feladatok", size=14, weight=ft.FontWeight.BOLD, color="#6B7280"),
            pm_tasks_list,
            ft.Container(height=20),
            ft.Divider(height=1),
            ft.Container(height=10),
            ft.Text("Elvégzett PM feladatok", size=14, weight=ft.FontWeight.BOLD, color="#10B981"),
            completed_tasks_list,
            ft.Container(height=20),
            ft.Divider(height=1),
            ft.Container(height=10),
            ft.Text("Eszközök esedékes szervizeléssel", size=14, weight=ft.FontWeight.BOLD, color="#6B7280"),
            machines_list,
            ft.Container(height=20),
            ft.Divider(height=1),
            ft.Container(height=10),
            ft.Text("Eszközök esedékes üzemóra ellenőrzéssel", size=14, weight=ft.FontWeight.BOLD, color="#F59E0B"),
            operating_hours_list,
        ], spacing=12, expand=True, scroll=ft.ScrollMode.AUTO)

