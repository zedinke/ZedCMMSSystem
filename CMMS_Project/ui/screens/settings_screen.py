"""
Settings Screen (Beállítások képernyő)
Language selection, theme preferences, user info
"""

import flet as ft
# Compatibility for flet 0.23.2 - Icons are strings, not ft.Icons
if not hasattr(ft, 'Icons'):
    from utils.flet_icons import Icons
    ft.Icons = Icons
from pathlib import Path
import os
import threading
from datetime import datetime
from services.context_service import get_app_context
from services import auth_service
from services.settings_service import (
    get_maintenance_notification_settings, 
    set_maintenance_notification_settings,
    get_operating_hours_notification_settings,
    set_operating_hours_notification_settings,
    get_setting, 
    set_setting,
    get_github_owner,
    set_github_owner,
    get_github_repo,
    set_github_repo,
    get_pm_task_files_dir,
    set_pm_task_files_dir,
)
from services.update_service import get_update_service, UpdateInfo
from ui.components.update_dialog import create_update_dialog
from services.backup_service import (
    backup_database, backup_all_files, list_backups, restore_from_backup, cleanup_old_backups,
    schedule_backup, stop_backup_scheduler, is_backup_scheduler_running, get_backup_schedule_interval
)
from localization.translator import translator
from ui.components.modern_components import (
    DesignSystem,
    create_modern_text_field,
    create_modern_button,
    create_modern_card,
    create_vibrant_badge,
)
from ui.components.modern_card import (
    create_tailwind_card,
    create_info_card,
)
from ui.components.modern_components import create_empty_state_card
from ui.screens.super_mario_game import SuperMarioGame


class SettingsScreen:
    def __init__(self, on_language_change=None, on_logout=None):
        self.on_language_change = on_language_change
        self.on_logout = on_logout

    def view(self, page: ft.Page):
        ctx = get_app_context()
        current_lang = translator.get_current_language()

        # Language Selector
        lang_options = [
            ft.dropdown.Option("en", "English"),
            ft.dropdown.Option("hu", "Magyar"),
            ft.dropdown.Option("de", "Deutsch"),
            ft.dropdown.Option("ro", "Română"),
            ft.dropdown.Option("ja", "日本語"),
        ]
        
        def on_lang_change(e):
            new_lang = e.control.value
            if new_lang:
                translator.set_current_language(new_lang)
                # Save to database
                ctx = get_app_context()
                auth_service.update_user_language(ctx.user_id, new_lang)
                if self.on_language_change:
                    self.on_language_change(new_lang)
                page.update()

        language_dropdown = ft.Dropdown(
            label=translator.get_text("settings.language"),
            options=lang_options,
            value=current_lang,
            on_change=on_lang_change,
            width=200,
        )

        # User Profile Section
        user_info = ft.Column([
            ft.Text(translator.get_text("settings.user_profile"), size=16, weight=ft.FontWeight.BOLD),
            ft.TextField(
                label=translator.get_text("settings.username"),
                value=ctx.username or "-",
                read_only=True,
            ),
            ft.TextField(
                label=translator.get_text("settings.email"),
                value=ctx.email or "-",
                read_only=True,
            ),
            ft.TextField(
                label=translator.get_text("settings.role"),
                value=ctx.role or "-",
                read_only=True,
            ),
        ], spacing=12)

        # Language Section
        language_section = ft.Column([
            ft.Text(translator.get_text("settings.language"), size=16, weight=ft.FontWeight.BOLD),
            language_dropdown,
        ], spacing=12)

        # Worksheet Template Selector
        from services.settings_service import (
            list_docx_templates, 
            get_selected_worksheet_template, 
            set_selected_worksheet_template,
            get_selected_work_request_template,
            set_selected_work_request_template,
            get_selected_qr_label_template,
            set_selected_qr_label_template,
            get_selected_storage_receipt_template,
            set_selected_storage_receipt_template,
            get_selected_storage_transfer_template,
            set_selected_storage_transfer_template,
            get_selected_inventory_count_template,
            set_selected_inventory_count_template,
            get_selected_inventory_correction_template,
            set_selected_inventory_correction_template,
            get_worksheet_name_format,
            set_worksheet_name_format,
            get_selected_scrapping_template,
            set_selected_scrapping_template,
            get_selected_vacation_template,
            set_selected_vacation_template,
            get_log_archive_years,
            set_log_archive_years,
            get_log_delete_years,
            set_log_delete_years,
            get_auto_generate_scrapping_doc,
            set_auto_generate_scrapping_doc
        )
        template_files = list_docx_templates()
        selected_worksheet = get_selected_worksheet_template()
        selected_work_request = get_selected_work_request_template()
        selected_qr_label = get_selected_qr_label_template()
        selected_scrapping = get_selected_scrapping_template()
        selected_vacation = get_selected_vacation_template()
        selected_storage_receipt = get_selected_storage_receipt_template()
        selected_storage_transfer = get_selected_storage_transfer_template()
        selected_inventory_count = get_selected_inventory_count_template()
        selected_inventory_correction = get_selected_inventory_correction_template()
        
        worksheet_template_dropdown = ft.Dropdown(
            label=translator.get_text("settings.worksheet_template"),
            options=[ft.dropdown.Option(str(p), p.name) for p in template_files] or [ft.dropdown.Option("", "Nincs sablon")],
            value=str(selected_worksheet) if selected_worksheet else None,
            width=400,
        )

        def on_worksheet_template_change(e):
            val = e.control.value
            if val:
                set_selected_worksheet_template(Path(val))
                page.snack_bar = ft.SnackBar(ft.Text(translator.get_text("success_messages.updated")))
                page.snack_bar.open = True
                page.update()

        worksheet_template_dropdown.on_change = on_worksheet_template_change

        work_request_template_dropdown = ft.Dropdown(
            label=translator.get_text("settings.work_request_template"),
            options=[ft.dropdown.Option(str(p), p.name) for p in template_files] or [ft.dropdown.Option("", "Nincs sablon")],
            value=str(selected_work_request) if selected_work_request else None,
            width=400,
        )

        def on_work_request_template_change(e):
            val = e.control.value
            if val:
                set_selected_work_request_template(Path(val))
                page.snack_bar = ft.SnackBar(ft.Text(translator.get_text("success_messages.updated")))
                page.snack_bar.open = True
                page.update()

        work_request_template_dropdown.on_change = on_work_request_template_change

        qr_label_template_dropdown = ft.Dropdown(
            label=translator.get_text("settings.qr_label_template"),
            options=[ft.dropdown.Option(str(p), p.name) for p in template_files] or [ft.dropdown.Option("", "Nincs sablon")],
            value=str(selected_qr_label) if selected_qr_label else None,
            width=400,
        )

        def on_qr_label_template_change(e):
            val = e.control.value
            if val:
                set_selected_qr_label_template(Path(val))
                page.snack_bar = ft.SnackBar(ft.Text(translator.get_text("success_messages.updated")))
                page.snack_bar.open = True
                page.update()

        qr_label_template_dropdown.on_change = on_qr_label_template_change

        # Worksheet Name Format
        worksheet_name_format = get_worksheet_name_format()
        worksheet_name_format_field = create_modern_text_field(
            label=translator.get_text("settings.worksheet_name_format") if hasattr(translator, 'get_text') else "Munkalap névformátum / Worksheet Name Format",
            hint_text=translator.get_text("settings.worksheet_name_format_hint") if hasattr(translator, 'get_text') else "Pl.: Munkalap - {user_name} - #{worksheet_id}",
            value=worksheet_name_format,
            width=400,
        )
        
        def on_worksheet_name_format_change(e):
            val = e.control.value
            if val:
                set_worksheet_name_format(val)
                page.snack_bar = ft.SnackBar(ft.Text(translator.get_text("success_messages.updated")))
                page.snack_bar.open = True
                page.update()
        
        worksheet_name_format_field.on_change = on_worksheet_name_format_change
        
        # Scrapping Template
        scrapping_template_dropdown = ft.Dropdown(
            label=translator.get_text("settings.scrapping_template"),
            options=[ft.dropdown.Option(str(p), p.name) for p in template_files] or [ft.dropdown.Option("", "Nincs sablon")],
            value=str(selected_scrapping) if selected_scrapping else None,
            width=400,
        )
        
        def on_scrapping_template_change(e):
            val = e.control.value
            if val:
                set_selected_scrapping_template(Path(val))
                page.snack_bar = ft.SnackBar(ft.Text(translator.get_text("success_messages.updated")))
                page.snack_bar.open = True
                page.update()
        
        scrapping_template_dropdown.on_change = on_scrapping_template_change
        
        # Vacation template dropdown
        vacation_options = [ft.dropdown.Option(str(t), t.name) for t in template_files] or [ft.dropdown.Option("", "Nincs sablon")]
        vacation_template_dropdown = ft.Dropdown(
            label=translator.get_text("settings.vacation_template"),
            options=vacation_options,
            value=str(selected_vacation) if selected_vacation else None,
            width=400,
        )
        
        def on_vacation_template_change(e):
            val = e.control.value
            if val:
                set_selected_vacation_template(Path(val))
                page.snack_bar = ft.SnackBar(ft.Text(translator.get_text("success_messages.updated")))
                page.snack_bar.open = True
                page.update()
        
        vacation_template_dropdown.on_change = on_vacation_template_change
        
        # Storage Receipt Template
        storage_receipt_template_dropdown = ft.Dropdown(
            label=translator.get_text("settings.storage_receipt_template") or "Betárazás sablon",
            options=[ft.dropdown.Option(str(p), p.name) for p in template_files] or [ft.dropdown.Option("", "Nincs sablon")],
            value=str(selected_storage_receipt) if selected_storage_receipt else None,
            width=400,
        )
        
        def on_storage_receipt_template_change(e):
            val = e.control.value
            if val:
                set_selected_storage_receipt_template(Path(val))
                page.snack_bar = ft.SnackBar(ft.Text(translator.get_text("success_messages.updated")))
                page.snack_bar.open = True
                page.update()
        
        storage_receipt_template_dropdown.on_change = on_storage_receipt_template_change
        
        # Storage Transfer Template
        storage_transfer_template_dropdown = ft.Dropdown(
            label=translator.get_text("settings.storage_transfer_template") or "Áttárazás sablon",
            options=[ft.dropdown.Option(str(p), p.name) for p in template_files] or [ft.dropdown.Option("", "Nincs sablon")],
            value=str(selected_storage_transfer) if selected_storage_transfer else None,
            width=400,
        )
        
        def on_storage_transfer_template_change(e):
            val = e.control.value
            if val:
                set_selected_storage_transfer_template(Path(val))
                page.snack_bar = ft.SnackBar(ft.Text(translator.get_text("success_messages.updated")))
                page.snack_bar.open = True
                page.update()
        
        storage_transfer_template_dropdown.on_change = on_storage_transfer_template_change
        
        # Inventory Count Template
        inventory_count_template_dropdown = ft.Dropdown(
            label=translator.get_text("settings.inventory_count_template") if hasattr(translator, 'get_text') and translator.get_text("settings.inventory_count_template") else "Leltár sablon / Inventory Count Template",
            options=[ft.dropdown.Option(str(p), p.name) for p in template_files] or [ft.dropdown.Option("", "Nincs sablon")],
            value=str(selected_inventory_count) if selected_inventory_count else None,
            width=400,
        )
        
        def on_inventory_count_template_change(e):
            val = e.control.value
            if val:
                set_selected_inventory_count_template(Path(val))
                page.snack_bar = ft.SnackBar(ft.Text(translator.get_text("success_messages.updated")))
                page.snack_bar.open = True
                page.update()
        
        inventory_count_template_dropdown.on_change = on_inventory_count_template_change
        
        # Inventory Correction Template
        inventory_correction_template_dropdown = ft.Dropdown(
            label=translator.get_text("settings.inventory_correction_template") if hasattr(translator, 'get_text') and translator.get_text("settings.inventory_correction_template") else "Készletkorrekció sablon / Inventory Correction Template",
            options=[ft.dropdown.Option(str(p), p.name) for p in template_files] or [ft.dropdown.Option("", "Nincs sablon")],
            value=str(selected_inventory_correction) if selected_inventory_correction else None,
            width=400,
        )
        
        def on_inventory_correction_template_change(e):
            val = e.control.value
            if val:
                set_selected_inventory_correction_template(Path(val))
                page.snack_bar = ft.SnackBar(ft.Text(translator.get_text("success_messages.updated")))
                page.snack_bar.open = True
                page.update()
        
        inventory_correction_template_dropdown.on_change = on_inventory_correction_template_change
        
        # Log Settings
        log_archive_years = get_log_archive_years()
        log_archive_years_field = create_modern_text_field(
            label=translator.get_text("settings.log_archive_years"),
            value=str(log_archive_years),
            keyboard_type=ft.KeyboardType.NUMBER,
            width=200,
        )
        
        def on_log_archive_years_change(e):
            val = e.control.value
            if val:
                try:
                    years = int(val)
                    set_log_archive_years(years)
                    page.snack_bar = ft.SnackBar(ft.Text(translator.get_text("success_messages.updated")))
                    page.snack_bar.open = True
                    page.update()
                except ValueError:
                    pass
        
        log_archive_years_field.on_change = on_log_archive_years_change
        
        log_delete_years = get_log_delete_years()
        log_delete_years_field = create_modern_text_field(
            label=translator.get_text("settings.log_delete_years"),
            value=str(log_delete_years),
            keyboard_type=ft.KeyboardType.NUMBER,
            width=200,
        )
        
        def on_log_delete_years_change(e):
            val = e.control.value
            if val:
                try:
                    years = int(val)
                    set_log_delete_years(years)
                    page.snack_bar = ft.SnackBar(ft.Text(translator.get_text("success_messages.updated")))
                    page.snack_bar.open = True
                    page.update()
                except ValueError:
                    pass
        
        log_delete_years_field.on_change = on_log_delete_years_change
        
        # Auto-generate scrapping doc
        auto_generate_scrapping = get_auto_generate_scrapping_doc()
        auto_generate_scrapping_checkbox = ft.Checkbox(
            label=translator.get_text("settings.auto_generate_scrapping_doc"),
            value=auto_generate_scrapping,
            on_change=lambda e: set_auto_generate_scrapping_doc(e.control.value),
        )
        
        # Inventory Audit Excel Template Settings
        from services.settings_service import (
            get_inventory_audit_excel_template_dir,
            set_inventory_audit_excel_template_dir,
            list_excel_templates,
        )
        excel_template_dir = get_inventory_audit_excel_template_dir()
        excel_templates = list_excel_templates(excel_template_dir)
        
        excel_template_dir_field = create_modern_text_field(
            label=translator.get_text("settings.inventory_audit_excel_template_dir") if hasattr(translator, 'get_text') else "Készletellenőrzés Excel sablon könyvtár",
            value=str(excel_template_dir) if excel_template_dir else "",
            hint_text="pl. templates/excel_templates",
            width=400,
        )
        
        def on_excel_template_dir_change(e):
            val = e.control.value
            if val:
                try:
                    template_dir = Path(val)
                    if template_dir.exists() and template_dir.is_dir():
                        set_inventory_audit_excel_template_dir(template_dir)
                        page.snack_bar = ft.SnackBar(ft.Text(translator.get_text("success_messages.updated")))
                        page.snack_bar.open = True
                        page.update()
                    else:
                        page.snack_bar = ft.SnackBar(ft.Text("A könyvtár nem létezik vagy nem könyvtár / Directory does not exist or is not a directory"), bgcolor=DesignSystem.ERROR)
                        page.snack_bar.open = True
                        page.update()
                except Exception as exc:
                    page.snack_bar = ft.SnackBar(ft.Text(f"Hiba: {exc}"), bgcolor=DesignSystem.ERROR)
                    page.snack_bar.open = True
                    page.update()
        
        excel_template_dir_field.on_change = on_excel_template_dir_change
        
        # PM Task Files Directory Settings
        pm_task_files_dir = get_pm_task_files_dir()
        pm_task_files_dir_field = create_modern_text_field(
            label=translator.get_text("settings.pm_task_files_dir") if hasattr(translator, 'get_text') else "PM task fájlok könyvtára / PM Task Files Directory",
            value=str(pm_task_files_dir) if pm_task_files_dir else "",
            hint_text="pl. C:\\CMMS_Files\\PM_Tasks",
            width=400,
        )
        
        def on_pm_task_files_dir_pick(e: ft.FilePickerResultEvent):
            """Handle directory picker result for PM task files"""
            if e.path:
                try:
                    selected_dir = Path(e.path)
                    if selected_dir.exists() and selected_dir.is_dir():
                        set_pm_task_files_dir(selected_dir)
                        pm_task_files_dir_field.value = str(selected_dir)
                        page.snack_bar = ft.SnackBar(ft.Text(translator.get_text("success_messages.updated")), bgcolor=DesignSystem.SUCCESS)
                        page.snack_bar.open = True
                        page.update()
                    else:
                        page.snack_bar = ft.SnackBar(ft.Text("A könyvtár nem létezik / Directory does not exist"), bgcolor=DesignSystem.ERROR)
                        page.snack_bar.open = True
                        page.update()
                except Exception as exc:
                    page.snack_bar = ft.SnackBar(ft.Text(f"Hiba: {exc}"), bgcolor=DesignSystem.ERROR)
                    page.snack_bar.open = True
                    page.update()
        
        pm_task_files_dir_picker = ft.FilePicker(on_result=on_pm_task_files_dir_pick)
        page.overlay.append(pm_task_files_dir_picker)
        
        def on_pm_task_files_dir_browse(e):
            """Open directory picker for PM task files"""
            pm_task_files_dir_picker.get_directory_path(
                dialog_title="PM task fájlok könyvtár kiválasztása / Select PM Task Files Directory"
            )
        
        pm_task_files_dir_browse_btn = create_modern_button(
            text="Tallózás / Browse",
            icon=ft.Icons.FOLDER_OPEN if hasattr(ft.Icons, 'FOLDER_OPEN') else (ft.Icons.FOLDER if hasattr(ft.Icons, 'FOLDER') else ft.Icons.INSERT_DRIVE_FILE),
            on_click=on_pm_task_files_dir_browse,
            variant="outlined",
        )
        
        def on_pm_task_files_dir_change(e):
            """Handle manual path entry for PM task files"""
            val = e.control.value
            if val:
                try:
                    files_dir = Path(val)
                    if files_dir.exists() and files_dir.is_dir():
                        set_pm_task_files_dir(files_dir)
                        page.snack_bar = ft.SnackBar(ft.Text(translator.get_text("success_messages.updated")), bgcolor=DesignSystem.SUCCESS)
                        page.snack_bar.open = True
                        page.update()
                    else:
                        page.snack_bar = ft.SnackBar(ft.Text("A könyvtár nem létezik vagy nem könyvtár / Directory does not exist or is not a directory"), bgcolor=DesignSystem.ERROR)
                        page.snack_bar.open = True
                        page.update()
                except Exception as exc:
                    page.snack_bar = ft.SnackBar(ft.Text(f"Hiba: {exc}"), bgcolor=DesignSystem.ERROR)
                    page.snack_bar.open = True
                    page.update()
        
        pm_task_files_dir_field.on_change = on_pm_task_files_dir_change
        
        template_section = ft.Column([
            ft.Text(translator.get_text("settings.templates"), size=16, weight=ft.FontWeight.BOLD),
            ft.Text(translator.get_text("settings.templates_description"), size=12, color=DesignSystem.TEXT_SECONDARY),
            worksheet_template_dropdown,
            ft.Container(height=12),
            work_request_template_dropdown,
            ft.Container(height=12),
            qr_label_template_dropdown,
            ft.Container(height=12),
            scrapping_template_dropdown,
            ft.Container(height=12),
            vacation_template_dropdown,
            ft.Container(height=12),
            storage_receipt_template_dropdown,
            ft.Container(height=12),
            storage_transfer_template_dropdown,
            ft.Container(height=12),
            inventory_count_template_dropdown,
            ft.Container(height=12),
            inventory_correction_template_dropdown,
            ft.Container(height=24),
            ft.Divider(height=1),
            ft.Container(height=12),
            ft.Text("Excel sablonok / Excel Templates", size=16, weight=ft.FontWeight.BOLD),
            ft.Text("Készletellenőrzés Excel export sablonok könyvtára / Inventory audit Excel export template directory", size=12, color=DesignSystem.TEXT_SECONDARY),
            excel_template_dir_field,
            ft.Text(f"Elérhető Excel sablonok: {len(excel_templates)} / Available Excel templates: {len(excel_templates)}", size=11, color=DesignSystem.TEXT_SECONDARY),
            ft.Container(height=24),
            ft.Divider(height=1),
            ft.Container(height=12),
            ft.Text("PM task fájlok könyvtár / PM Task Files Directory", size=16, weight=ft.FontWeight.BOLD),
            ft.Text("A PM task karbantartásokhoz és szervizekhez feltöltött fájlok (képek, dokumentumok) szülő könyvtára. / Parent directory for files (images, documents) uploaded to PM task maintenance and service work.", size=12, color=DesignSystem.TEXT_SECONDARY),
            ft.Row([
                pm_task_files_dir_field,
                pm_task_files_dir_browse_btn,
            ], spacing=DesignSystem.SPACING_3),
            ft.Container(height=24),
            ft.Divider(height=1),
            ft.Container(height=12),
            ft.Text(translator.get_text("settings.worksheet_name_format") if hasattr(translator, 'get_text') else "Munkalap névformátum / Worksheet Name Format", size=16, weight=ft.FontWeight.BOLD),
            ft.Text(translator.get_text("settings.worksheet_name_format_description") if hasattr(translator, 'get_text') else "A munkalapok automatikus elnevezésének formátuma. Változók: {worksheet_name}, {user_name}, {worksheet_id}", size=12, color=DesignSystem.TEXT_SECONDARY),
            worksheet_name_format_field,
            ft.Container(height=24),
            ft.Divider(height=1),
            ft.Container(height=12),
            ft.Text("Log beállítások / Log Settings", size=16, weight=ft.FontWeight.BOLD),
            ft.Text("Log archiválási és törlési időszakok beállítása / Configure log archive and delete periods", size=12, color=DesignSystem.TEXT_SECONDARY),
            ft.Row([
                log_archive_years_field,
                log_delete_years_field,
            ], spacing=10),
            ft.Container(height=12),
            auto_generate_scrapping_checkbox,
        ], spacing=12)
        
        # Maintenance Notification Settings
        notif_settings = get_maintenance_notification_settings()
        months_field = ft.TextField(
            label="Hónapok",
            value=str(notif_settings['months_ahead']),
            keyboard_type=ft.KeyboardType.NUMBER,
            width=100,
        )
        weeks_field = ft.TextField(
            label="Hetek",
            value=str(notif_settings['weeks_ahead']),
            keyboard_type=ft.KeyboardType.NUMBER,
            width=100,
        )
        days_field = ft.TextField(
            label="Napok",
            value=str(notif_settings['days_ahead']),
            keyboard_type=ft.KeyboardType.NUMBER,
            width=100,
        )
        hours_field = ft.TextField(
            label="Órák",
            value=str(notif_settings['hours_ahead']),
            keyboard_type=ft.KeyboardType.NUMBER,
            width=100,
        )
        
        def save_maintenance_settings(_):
            try:
                months = int(months_field.value or '0')
                weeks = int(weeks_field.value or '0')
                days = int(days_field.value or '0')
                hours = int(hours_field.value or '0')
                
                set_maintenance_notification_settings(
                    months=months,
                    weeks=weeks,
                    days=days,
                    hours=hours,
                )
                page.snack_bar = ft.SnackBar(ft.Text(translator.get_text("settings.maintenance_settings_saved")), bgcolor=DesignSystem.SUCCESS)
                page.snack_bar.open = True
                page.update()
            except Exception as exc:
                page.snack_bar = ft.SnackBar(ft.Text(f"{translator.get_text('common.messages.error_occurred')}: {exc}"), bgcolor=DesignSystem.ERROR)
                page.snack_bar.open = True
                page.update()
        
        maintenance_section = ft.Column([
            ft.Text("Karbantartási beállítások", size=16, weight=ft.FontWeight.BOLD),
            ft.Text("Mennyivel előtte jelezzen a rendszer esedékes karbantartásról:", size=12, color=DesignSystem.TEXT_SECONDARY),
            ft.Row([
                months_field,
                weeks_field,
                days_field,
                hours_field,
            ], spacing=10),
            ft.ElevatedButton(
                "Mentés",
                icon=ft.Icons.SAVE if hasattr(ft.Icons, 'SAVE') else (ft.Icons.SAVE_ALT if hasattr(ft.Icons, 'SAVE_ALT') else ft.Icons.CHECK),
                on_click=save_maintenance_settings,
                bgcolor=DesignSystem.SECONDARY,
                color="#FFFFFF",
            ),
        ], spacing=12)
        
        # Operating Hours Notification Settings
        operating_hours_notif_settings = get_operating_hours_notification_settings()
        oh_months_field = ft.TextField(
            label="Hónapok",
            value=str(operating_hours_notif_settings['months_ahead']),
            keyboard_type=ft.KeyboardType.NUMBER,
            width=100,
        )
        oh_weeks_field = ft.TextField(
            label="Hetek",
            value=str(operating_hours_notif_settings['weeks_ahead']),
            keyboard_type=ft.KeyboardType.NUMBER,
            width=100,
        )
        oh_days_field = ft.TextField(
            label="Napok",
            value=str(operating_hours_notif_settings['days_ahead']),
            keyboard_type=ft.KeyboardType.NUMBER,
            width=100,
        )
        oh_hours_field = ft.TextField(
            label="Órák",
            value=str(operating_hours_notif_settings['hours_ahead']),
            keyboard_type=ft.KeyboardType.NUMBER,
            width=100,
        )
        
        def save_operating_hours_settings(_):
            try:
                months = int(oh_months_field.value or '0')
                weeks = int(oh_weeks_field.value or '0')
                days = int(oh_days_field.value or '0')
                hours = int(oh_hours_field.value or '0')
                
                set_operating_hours_notification_settings(
                    months=months,
                    weeks=weeks,
                    days=days,
                    hours=hours,
                )
                page.snack_bar = ft.SnackBar(ft.Text(translator.get_text("settings.operating_hours_settings_saved") if hasattr(translator, 'get_text') and translator.get_text("settings.operating_hours_settings_saved") else "Üzemóra értesítési beállítások mentve"), bgcolor=DesignSystem.SUCCESS)
                page.snack_bar.open = True
                page.update()
            except Exception as exc:
                page.snack_bar = ft.SnackBar(ft.Text(f"{translator.get_text('common.messages.error_occurred')}: {exc}"), bgcolor=DesignSystem.ERROR)
                page.snack_bar.open = True
                page.update()
        
        operating_hours_section = ft.Column([
            ft.Text("Üzemóra értesítési beállítások", size=16, weight=ft.FontWeight.BOLD),
            ft.Text("Mennyivel előtte jelezzen a rendszer esedékes üzemóra ellenőrzésről:", size=12, color=DesignSystem.TEXT_SECONDARY),
            ft.Row([
                oh_months_field,
                oh_weeks_field,
                oh_days_field,
                oh_hours_field,
            ], spacing=10),
            ft.ElevatedButton(
                "Mentés",
                icon=ft.Icons.SAVE if hasattr(ft.Icons, 'SAVE') else (ft.Icons.SAVE_ALT if hasattr(ft.Icons, 'SAVE_ALT') else ft.Icons.CHECK),
                on_click=save_operating_hours_settings,
                bgcolor=DesignSystem.SECONDARY,
                color="#FFFFFF",
            ),
        ], spacing=12)

        # Backup & Recovery Section
        backup_status_text = ft.Text("", size=12, color=DesignSystem.TEXT_SECONDARY)
        
        def create_backup(e):
            """Create database backup"""
            backup_status_text.value = "Mentés folyamatban... / Backup in progress..."
            backup_status_text.color = "#2196F3"
            page.update()
            
            def backup_thread():
                try:
                    backup_path = backup_database()
                    if backup_path:
                        backup_status_text.value = f"Mentés kész: {backup_path.name} / Backup created"
                        backup_status_text.color = "#4CAF50"
                        page.snack_bar = ft.SnackBar(
                            ft.Text(f"Adatbázis mentve: {backup_path.name} / Database backed up"),
                            bgcolor=DesignSystem.SUCCESS
                        )
                    else:
                        backup_status_text.value = "Hiba a mentés során / Backup error"
                        backup_status_text.color = "#F44336"
                        page.snack_bar = ft.SnackBar(
                            ft.Text(translator.get_text("settings.backup_error")),
                            bgcolor=DesignSystem.ERROR
                        )
                    page.snack_bar.open = True
                except Exception as ex:
                    backup_status_text.value = f"{translator.get_text('common.messages.error_occurred')}: {ex}"
                    backup_status_text.color = "#F44336"
                    page.snack_bar = ft.SnackBar(
                        ft.Text(f"{translator.get_text('common.messages.error_occurred')}: {ex}"),
                        bgcolor=DesignSystem.ERROR
                    )
                    page.snack_bar.open = True
                finally:
                    page.update()
            
            threading.Thread(target=backup_thread, daemon=True).start()
        
        def create_full_backup(e):
            """Create full backup (database + files)"""
            backup_status_text.value = "Teljes mentés folyamatban... / Full backup in progress..."
            backup_status_text.color = "#2196F3"
            page.update()
            
            def backup_thread():
                try:
                    backup_path = backup_all_files()
                    if backup_path:
                        backup_status_text.value = f"Teljes mentés kész: {backup_path.name} / Full backup created"
                        backup_status_text.color = "#4CAF50"
                        page.snack_bar = ft.SnackBar(
                            ft.Text(f"Teljes mentés kész: {backup_path.name} / Full backup created"),
                            bgcolor=DesignSystem.SUCCESS
                        )
                        # Open backup location
                        os.startfile(str(backup_path.parent))
                    else:
                        backup_status_text.value = "Hiba a mentés során / Backup error"
                        backup_status_text.color = "#F44336"
                        page.snack_bar = ft.SnackBar(
                            ft.Text(translator.get_text("settings.backup_error")),
                            bgcolor=DesignSystem.ERROR
                        )
                    page.snack_bar.open = True
                except Exception as ex:
                    backup_status_text.value = f"{translator.get_text('common.messages.error_occurred')}: {ex}"
                    backup_status_text.color = "#F44336"
                    page.snack_bar = ft.SnackBar(
                        ft.Text(f"{translator.get_text('common.messages.error_occurred')}: {ex}"),
                        bgcolor=DesignSystem.ERROR
                    )
                    page.snack_bar.open = True
                finally:
                    page.update()
        
        # List available backups with download and restore buttons
        backups = list_backups()
        
        def download_backup(backup_path):
            """Download backup file to user-selected location"""
            def on_save_result(e: ft.FilePickerResultEvent):
                if e.path is None:
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text(translator.get_text("worksheets.download_cancelled")),
                        bgcolor=DesignSystem.TEXT_SECONDARY,
                    )
                    page.snack_bar.open = True
                    page.update()
                    return
                
                def download_thread():
                    try:
                        import shutil
                        save_path = Path(e.path)
                        # Preserve original extension
                        if not save_path.suffix:
                            save_path = save_path.with_suffix(backup_path.suffix)
                        
                        shutil.copy2(backup_path, save_path)
                        
                        page.snack_bar = ft.SnackBar(
                            content=ft.Text(f"Mentés letöltve: {save_path.name} / Backup downloaded: {save_path.name}"),
                            bgcolor=DesignSystem.SUCCESS,
                        )
                        page.snack_bar.open = True
                        page.update()
                    except Exception as exc:
                        page.snack_bar = ft.SnackBar(
                            content=ft.Text(f"Hiba letöltéskor / Download error: {exc}"),
                            bgcolor=DesignSystem.ERROR,
                        )
                        page.snack_bar.open = True
                        page.update()
                
                threading.Thread(target=download_thread, daemon=True).start()
            
            file_picker = ft.FilePicker(on_result=on_save_result)
            page.overlay.append(file_picker)
            page.update()  # Update page first to add FilePicker to page
            file_picker.save_file(
                dialog_title="Mentés letöltése / Download Backup",
                file_name=backup_path.name,
            )
        
        def restore_backup(backup_path):
            """Restore database from backup file"""
            def confirm_restore(e):
                dialog.open = False
                page.update()
                
                def restore_thread():
                    try:
                        backup_status_text.value = "Visszaállítás folyamatban... / Restore in progress..."
                        backup_status_text.color = "#2196F3"
                        page.update()
                        
                        success = restore_from_backup(backup_path, restore_files=False)
                        
                        if success:
                            backup_status_text.value = f"Visszaállítás sikeres: {backup_path.name} / Restore successful"
                            backup_status_text.color = "#4CAF50"
                            page.snack_bar = ft.SnackBar(
                                content=ft.Text(
                                    f"Adatbázis visszaállítva: {backup_path.name}. Újraindítás szükséges! / "
                                    f"Database restored: {backup_path.name}. Restart required!"
                                ),
                                bgcolor=DesignSystem.SUCCESS,
                            )
                        else:
                            backup_status_text.value = "Hiba a visszaállítás során / Restore error"
                            backup_status_text.color = "#F44336"
                            page.snack_bar = ft.SnackBar(
                                content=ft.Text("Hiba a visszaállítás során / Restore error"),
                                bgcolor=DesignSystem.ERROR,
                            )
                        page.snack_bar.open = True
                    except Exception as exc:
                        backup_status_text.value = f"Hiba: {exc} / Error: {exc}"
                        backup_status_text.color = "#F44336"
                        page.snack_bar = ft.SnackBar(
                            content=ft.Text(f"Hiba / Error: {exc}"),
                            bgcolor=DesignSystem.ERROR,
                        )
                        page.snack_bar.open = True
                    finally:
                        page.update()
                
                threading.Thread(target=restore_thread, daemon=True).start()
            
            dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Visszaállítás megerősítése / Confirm Restore"),
                content=ft.Column([
                    ft.Text(f"Biztosan visszaállítod az adatbázist ebből a mentésből? / Are you sure you want to restore the database from this backup?", size=12),
                    ft.Text(f"Mentés: {backup_path.name}", size=11, weight=ft.FontWeight.W_600, color=DesignSystem.TEXT_SECONDARY),
                    ft.Text("Figyelem: Az aktuális adatbázis felül lesz írva! / Warning: Current database will be overwritten!", size=11, color=DesignSystem.ERROR),
                ], spacing=8, tight=True),
                actions=[
                    ft.TextButton(
                        translator.get_text("common.buttons.cancel"),
                        on_click=lambda e: (setattr(dialog, 'open', False), page.update()),
                    ),
                    ft.TextButton(
                        "Visszaállítás / Restore",
                        on_click=confirm_restore,
                        style=ft.ButtonStyle(color=DesignSystem.ERROR),
                    ),
                ],
            )
            page.dialog = dialog
            dialog.open = True
            page.update()
        
        def restore_from_file(e):
            """Restore database from user-selected file"""
            def on_pick_result(e: ft.FilePickerResultEvent):
                if e.files is None or len(e.files) == 0:
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text(translator.get_text("worksheets.download_cancelled")),
                        bgcolor=DesignSystem.TEXT_SECONDARY,
                    )
                    page.snack_bar.open = True
                    page.update()
                    return
                
                backup_file = Path(e.files[0].path)
                
                def restore_thread():
                    try:
                        backup_status_text.value = "Visszaállítás folyamatban... / Restore in progress..."
                        backup_status_text.color = "#2196F3"
                        page.update()
                        
                        success = restore_from_backup(backup_file, restore_files=False)
                        
                        if success:
                            backup_status_text.value = f"Visszaállítás sikeres: {backup_file.name} / Restore successful"
                            backup_status_text.color = "#4CAF50"
                            page.snack_bar = ft.SnackBar(
                                content=ft.Text(
                                    f"Adatbázis visszaállítva: {backup_file.name}. Újraindítás szükséges! / "
                                    f"Database restored: {backup_file.name}. Restart required!"
                                ),
                                bgcolor=DesignSystem.SUCCESS,
                            )
                        else:
                            backup_status_text.value = "Hiba a visszaállítás során / Restore error"
                            backup_status_text.color = "#F44336"
                            page.snack_bar = ft.SnackBar(
                                content=ft.Text("Hiba a visszaállítás során / Restore error"),
                                bgcolor=DesignSystem.ERROR,
                            )
                        page.snack_bar.open = True
                    except Exception as exc:
                        backup_status_text.value = f"Hiba: {exc} / Error: {exc}"
                        backup_status_text.color = "#F44336"
                        page.snack_bar = ft.SnackBar(
                            content=ft.Text(f"Hiba / Error: {exc}"),
                            bgcolor=DesignSystem.ERROR,
                        )
                        page.snack_bar.open = True
                    finally:
                        page.update()
                
                threading.Thread(target=restore_thread, daemon=True).start()
            
            file_picker = ft.FilePicker(on_result=on_pick_result)
            page.overlay.append(file_picker)
            page.update()  # Update page first to add FilePicker to page
            file_picker.pick_files(
                dialog_title="Mentés kiválasztása / Select Backup File",
                allowed_extensions=["db", "zip"],
                allow_multiple=False,
            )
        
        # Build backup list with action buttons
        backup_cards = []
        for backup in backups[:10]:  # Show up to 10 backups
            if backup.exists():
                backup_size_mb = backup.stat().st_size / 1024 / 1024
                backup_date = datetime.fromtimestamp(backup.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                
                backup_card = create_tailwind_card(
                    content=ft.Column([
                        ft.Row([
                            ft.Column([
                                ft.Text(backup.name, size=14, weight=ft.FontWeight.W_600),
                                ft.Text(f"{backup_size_mb:.2f} MB • {backup_date}", size=11, color=DesignSystem.TEXT_SECONDARY),
                            ], spacing=DesignSystem.SPACING_1, expand=True),
                        ], spacing=DesignSystem.SPACING_2),
                        ft.Row([
                            create_modern_button(
                                text="Letöltés / Download",
                                icon=ft.Icons.DOWNLOAD if hasattr(ft.Icons, 'DOWNLOAD') else (ft.Icons.FILE_DOWNLOAD if hasattr(ft.Icons, 'FILE_DOWNLOAD') else ft.Icons.GET_APP),
                                on_click=lambda e, bp=backup: download_backup(bp),
                                variant="outlined",
                            ),
                            create_modern_button(
                                text="Visszaállítás / Restore",
                                icon=ft.Icons.RESTORE if hasattr(ft.Icons, 'RESTORE') else (ft.Icons.RESTORE_PAGE if hasattr(ft.Icons, 'RESTORE_PAGE') else ft.Icons.UNDO),
                                on_click=lambda e, bp=backup: restore_backup(bp),
                                bgcolor=DesignSystem.AMBER_500,
                                color=DesignSystem.WHITE,
                            ),
                        ], spacing=DesignSystem.SPACING_2),
                    ], spacing=DesignSystem.SPACING_2),
                    padding=DesignSystem.SPACING_3,
                )
                backup_cards.append(backup_card)
        
        # Scheduled Backup Settings
        backup_interval_field = create_modern_text_field(
            label="Backup interval (hours) / Mentési időköz (óra)",
            value=str(get_backup_schedule_interval()),
            keyboard_type=ft.KeyboardType.NUMBER,
            width=200,
        )
        
        backup_retention_field = create_modern_text_field(
            label="Retention (days) / Megtartás (nap)",
            value="30",
            keyboard_type=ft.KeyboardType.NUMBER,
            width=200,
        )
        
        scheduler_status_text = ft.Text(
            f"Status: {'Running' if is_backup_scheduler_running() else 'Stopped'} / Állapot: {'Fut' if is_backup_scheduler_running() else 'Leállítva'}",
            size=12,
            color=DesignSystem.SUCCESS if is_backup_scheduler_running() else DesignSystem.TEXT_SECONDARY,
        )
        
        def start_scheduled_backup(e):
            try:
                interval = int(backup_interval_field.value or "24")
                retention = int(backup_retention_field.value or "30")
                
                if interval < 1:
                    page.snack_bar = ft.SnackBar(
                        ft.Text("Interval must be at least 1 hour / Az időköz legalább 1 óra kell legyen"),
                        bgcolor=DesignSystem.ERROR
                    )
                    page.snack_bar.open = True
                    page.update()
                    return
                
                schedule_backup(interval_hours=interval, retention_days=retention)
                scheduler_status_text.value = f"Status: Running (every {interval}h) / Állapot: Fut (minden {interval} óra)"
                scheduler_status_text.color = DesignSystem.SUCCESS
                page.snack_bar = ft.SnackBar(
                    ft.Text(f"Scheduled backup started / Ütemezett mentés elindítva"),
                    bgcolor=DesignSystem.SUCCESS
                )
                page.snack_bar.open = True
                page.update()
            except ValueError:
                page.snack_bar = ft.SnackBar(
                    ft.Text("Invalid values / Érvénytelen értékek"),
                    bgcolor=DesignSystem.ERROR
                )
                page.snack_bar.open = True
                page.update()
        
        def stop_scheduled_backup(e):
            stop_backup_scheduler()
            scheduler_status_text.value = "Status: Stopped / Állapot: Leállítva"
            scheduler_status_text.color = DesignSystem.TEXT_SECONDARY
            page.snack_bar = ft.SnackBar(
                ft.Text("Scheduled backup stopped / Ütemezett mentés leállítva"),
                bgcolor=DesignSystem.INFO
            )
            page.snack_bar.open = True
            page.update()
        
        # Manual Backup Section
        manual_backup_card = create_tailwind_card(
            content=ft.Column([
                ft.Row([
                    ft.Icon(
                        ft.Icons.BACKUP if hasattr(ft.Icons, 'BACKUP') else (ft.Icons.SAVE if hasattr(ft.Icons, 'SAVE') else ft.Icons.SAVE_ALT),
                        size=24,
                        color=DesignSystem.BLUE_500,
                    ),
                    ft.Text("Manuális mentés / Manual Backup", size=18, weight=ft.FontWeight.W_600),
                ], spacing=DesignSystem.SPACING_2),
                ft.Container(height=DesignSystem.SPACING_2),
                ft.Text("Rendszeres mentés ajánlott az adatok védelméért. / Regular backups recommended for data protection.", size=12, color=DesignSystem.TEXT_SECONDARY),
                ft.Container(height=DesignSystem.SPACING_4),
                ft.Row([
                    create_modern_button(
                        text="Adatbázis mentése / Backup Database",
                        icon=ft.Icons.BACKUP if hasattr(ft.Icons, 'BACKUP') else (ft.Icons.SAVE if hasattr(ft.Icons, 'SAVE') else ft.Icons.SAVE_ALT),
                        on_click=create_backup,
                        bgcolor=DesignSystem.BLUE_500,
                        color=DesignSystem.WHITE,
                    ),
                    create_modern_button(
                        text="Teljes mentés / Full Backup",
                        icon=ft.Icons.ARCHIVE if hasattr(ft.Icons, 'ARCHIVE') else (ft.Icons.FOLDER if hasattr(ft.Icons, 'FOLDER') else ft.Icons.FOLDER_OPEN),
                        on_click=create_full_backup,
                        bgcolor=DesignSystem.SUCCESS,
                        color=DesignSystem.WHITE,
                    ),
                ], spacing=DesignSystem.SPACING_3),
                ft.Container(height=DesignSystem.SPACING_2),
                backup_status_text,
            ], spacing=0),
            padding=DesignSystem.SPACING_4,
        )
        
        # Scheduled Backup Section
        scheduled_backup_card = create_tailwind_card(
            content=ft.Column([
                ft.Row([
                    ft.Icon(
                        ft.Icons.SCHEDULE if hasattr(ft.Icons, 'SCHEDULE') else (ft.Icons.ACCESS_TIME if hasattr(ft.Icons, 'ACCESS_TIME') else ft.Icons.CLOCK),
                        size=24,
                        color=DesignSystem.AMBER_500,
                    ),
                    ft.Text("Ütemezett mentés / Scheduled Backup", size=18, weight=ft.FontWeight.W_600),
                ], spacing=DesignSystem.SPACING_2),
                ft.Container(height=DesignSystem.SPACING_4),
                ft.Row([
                    backup_interval_field,
                    backup_retention_field,
                ], spacing=DesignSystem.SPACING_3),
                ft.Container(height=DesignSystem.SPACING_2),
                ft.Row([
                    scheduler_status_text,
                    ft.Container(expand=True),
                    create_modern_button(
                        text="Start / Indítás",
                        icon=ft.Icons.PLAY_ARROW if hasattr(ft.Icons, 'PLAY_ARROW') else (ft.Icons.PLAY_CIRCLE if hasattr(ft.Icons, 'PLAY_CIRCLE') else ft.Icons.PLAY_CIRCLE_FILLED),
                        on_click=start_scheduled_backup,
                        bgcolor=DesignSystem.SUCCESS,
                        color=DesignSystem.WHITE,
                    ),
                    create_modern_button(
                        text="Stop / Leállítás",
                        icon=ft.Icons.STOP if hasattr(ft.Icons, 'STOP') else (ft.Icons.STOP_CIRCLE if hasattr(ft.Icons, 'STOP_CIRCLE') else (ft.Icons.CLOSE if hasattr(ft.Icons, 'CLOSE') else ft.Icons.CLEAR)),
                        on_click=stop_scheduled_backup,
                        bgcolor=DesignSystem.ERROR,
                        color=DesignSystem.WHITE,
                    ),
                ], spacing=DesignSystem.SPACING_3),
            ], spacing=0),
            padding=DesignSystem.SPACING_4,
        )
        
        # Available Backups Section
        available_backups_card = create_tailwind_card(
            content=ft.Column([
                ft.Row([
                    ft.Icon(
                        ft.Icons.FOLDER_OPEN if hasattr(ft.Icons, 'FOLDER_OPEN') else (ft.Icons.FOLDER if hasattr(ft.Icons, 'FOLDER') else ft.Icons.INSERT_DRIVE_FILE),
                        size=24,
                        color=DesignSystem.EMERALD_500,
                    ),
                    ft.Text("Elérhető mentések / Available Backups", size=18, weight=ft.FontWeight.W_600),
                    ft.Container(expand=True),
                    ft.Text(f"({len(backups)})", size=14, color=DesignSystem.TEXT_SECONDARY, weight=ft.FontWeight.W_500),
                ], spacing=DesignSystem.SPACING_2),
                ft.Container(height=DesignSystem.SPACING_4),
                ft.Row([
                    create_modern_button(
                        text="Fájlból visszaállítás / Restore from File",
                        icon=ft.Icons.UPLOAD_FILE if hasattr(ft.Icons, 'UPLOAD_FILE') else (ft.Icons.FILE_UPLOAD if hasattr(ft.Icons, 'FILE_UPLOAD') else (ft.Icons.INSERT_DRIVE_FILE if hasattr(ft.Icons, 'INSERT_DRIVE_FILE') else ft.Icons.FOLDER_OPEN)),
                        on_click=restore_from_file,
                        variant="outlined",
                    ),
                ], spacing=DesignSystem.SPACING_2),
                ft.Container(height=DesignSystem.SPACING_3),
                ft.Column(
                    controls=backup_cards if backup_cards else [
                        create_empty_state_card(
                            icon=ft.Icons.INFO_OUTLINE if hasattr(ft.Icons, 'INFO_OUTLINE') else (ft.Icons.INFO if hasattr(ft.Icons, 'INFO') else ft.Icons.HELP_OUTLINE),
                            title="Nincsenek mentések / No backups",
                            description="Még nem készült mentés. Használd a 'Adatbázis mentése' gombot. / No backups yet. Use the 'Backup Database' button.",
                        ),
                    ],
                    spacing=DesignSystem.SPACING_2,
                ),
            ], spacing=0),
            padding=DesignSystem.SPACING_4,
        )
        
        backup_section = ft.Column([
            ft.Text("Adatmentés & Visszaállítás / Backup & Recovery", size=22, weight=ft.FontWeight.W_700),
            ft.Container(height=DesignSystem.SPACING_4),
            manual_backup_card,
            ft.Container(height=DesignSystem.SPACING_4),
            scheduled_backup_card,
            ft.Container(height=DesignSystem.SPACING_4),
            available_backups_card,
        ], spacing=0)
        
        # Updates Section
        from config.app_config import APP_NAME, APP_VERSION, UPDATE_CHECK_ENABLED
        from services.settings_service import get_github_owner, set_github_owner, get_github_repo, set_github_repo
        from utils.version_utils import normalize_version
        
        # Use APP_VERSION from config, which is already loaded from version.txt
        current_version = normalize_version(APP_VERSION)
        
        update_check_enabled = get_setting("auto_update_check", "true" if UPDATE_CHECK_ENABLED else "false") == "true"
        update_check_frequency = get_setting("update_check_frequency", "startup")
        last_update_check = get_setting("last_update_check")
        
        # GitHub Repository Settings
        github_owner = get_github_owner() or ""
        github_repo = get_github_repo() or "ZedCMMSSystem"
        
        github_owner_field = create_modern_text_field(
            label="GitHub Owner / Felhasználónév vagy szervezet",
            hint_text="pl.: username vagy organization",
            value=github_owner,
            width=300,
        )
        
        github_repo_field = create_modern_text_field(
            label="GitHub Repository / Repository neve",
            hint_text="pl.: ZedCMMSSystem",
            value=github_repo,
            width=300,
        )
        
        def on_github_settings_change(e):
            """Save GitHub settings"""
            new_owner = github_owner_field.value.strip() if github_owner_field.value else None
            new_repo = github_repo_field.value.strip() if github_repo_field.value else None
            
            if new_owner:
                set_github_owner(new_owner)
            if new_repo:
                set_github_repo(new_repo)
            
            # Reload update service config
            try:
                update_service = get_update_service()
                update_service.reload_config()
            except Exception:
                pass
            
            page.snack_bar = ft.SnackBar(ft.Text(translator.get_text("success_messages.updated")))
            page.snack_bar.open = True
            page.update()
        
        github_save_button = create_modern_button(
            text="Mentés / Save",
            icon=ft.Icons.SAVE if hasattr(ft.Icons, 'SAVE') else (ft.Icons.SAVE_ALT if hasattr(ft.Icons, 'SAVE_ALT') else ft.Icons.CHECK),
            on_click=on_github_settings_change,
            bgcolor=DesignSystem.BLUE_500,
            color=DesignSystem.WHITE,
        )
        
        update_status_text = ft.Text("", size=12, color=DesignSystem.TEXT_SECONDARY)
        update_info_ref = {"value": None}  # Store update info
        
        def check_for_updates(e):
            """Check for updates"""
            update_status_text.value = "Frissítés ellenőrzése... / Checking for updates..."
            update_status_text.color = DesignSystem.BLUE_500
            page.update()
            
            def check_thread():
                try:
                    update_service = get_update_service()
                    update_service.reload_config()  # Reload config before checking
                    
                    if not update_service.github_owner or not update_service.github_repo:
                        update_status_text.value = "GitHub repository nincs beállítva / GitHub repository not configured"
                        update_status_text.color = DesignSystem.ERROR
                        page.update()
                        return
                    
                    update_info = update_service.check_for_updates(current_version)
                    if update_info:
                        # Check if this version should be skipped
                        skip_version = get_setting("skip_version")
                        if skip_version and skip_version == update_info.version:
                            update_status_text.value = f"Verzió kihagyva: v{update_info.version} / Version skipped: v{update_info.version}"
                            update_status_text.color = DesignSystem.TEXT_SECONDARY
                            page.update()
                            return
                        
                        update_info_ref["value"] = update_info
                        update_status_text.value = f"Új verzió elérhető: v{update_info.version} / New version available: v{update_info.version}"
                        update_status_text.color = DesignSystem.SUCCESS
                        # Show update dialog
                        show_update_dialog(update_info)
                    else:
                        update_status_text.value = "Az alkalmazás naprakész / Application is up to date"
                        update_status_text.color = DesignSystem.SUCCESS
                        set_setting("last_update_check", datetime.now().isoformat())
                except Exception as ex:
                    update_status_text.value = f"Hiba: {ex} / Error: {ex}"
                    update_status_text.color = DesignSystem.ERROR
                finally:
                    page.update()
            
            threading.Thread(target=check_thread, daemon=True).start()
        
        def show_update_dialog(update_info: UpdateInfo):
            """Show update dialog"""
            def on_update_now():
                # Close dialog
                page.close(dialog)
                page.update()
                
                # Start updater
                start_updater(update_info)
            
            def on_later():
                page.close(dialog)
                page.update()
            
            def on_skip():
                # Skip this version
                set_setting("skip_version", update_info.version)
                page.close(dialog)
                page.update()
            
            dialog = create_update_dialog(
                update_info=update_info,
                on_update_now=on_update_now,
                on_later=on_later,
                on_skip=on_skip if not update_info.critical else None,
            )
            page.open(dialog)
        
        def start_updater(update_info: UpdateInfo):
            """Start updater.exe to perform update"""
            import logging
            logger = logging.getLogger(__name__)
            
            try:
                import subprocess
                import sys
                
                # Find updater.exe - search in multiple locations
                updater_paths = [
                    # Same directory as CMMS.exe (most common for installed version)
                    Path(sys.executable).parent / "Updater.exe",
                    # Current working directory (for development)
                    Path("Updater.exe"),
                    Path.cwd() / "Updater.exe",
                    # Program Files installation directory
                    Path(os.getenv("ProgramFiles", "C:\\Program Files")) / "ArtenceCMMS" / "Updater.exe",
                    Path(os.getenv("ProgramFiles(x86)", "C:\\Program Files (x86)")) / "ArtenceCMMS" / "Updater.exe",
                    # AppData Local (portable installations)
                    Path(os.getenv("LOCALAPPDATA", os.path.expanduser("~/.local/share"))) / "ArtenceCMMS" / "Updater.exe",
                    # Project root (for development)
                    Path(__file__).parent.parent.parent.parent / "dist" / "Updater.exe",
                ]
                
                logger.info("Searching for Updater.exe...")
                updater_exe = None
                searched_paths = []
                for path in updater_paths:
                    abs_path = path.resolve() if path.exists() else path
                    searched_paths.append(str(abs_path))
                    if path.exists():
                        updater_exe = path
                        logger.info(f"Found Updater.exe at: {updater_exe}")
                        break
                
                if not updater_exe:
                    error_msg = "Updater.exe nem található / Updater.exe not found"
                    logger.error(error_msg)
                    logger.info(f"Searched paths: {', '.join(searched_paths)}")
                    
                    page.snack_bar = ft.SnackBar(
                        ft.Text(f"{error_msg}\nKeresett helyek / Searched locations: {len(searched_paths)}"),
                        bgcolor=DesignSystem.ERROR,
                        duration=5000
                    )
                    page.snack_bar.open = True
                    page.update()
                    return
                
                # Validate updater executable
                if not updater_exe.is_file():
                    error_msg = f"Updater.exe nem érvényes fájl / Updater.exe is not a valid file: {updater_exe}"
                    logger.error(error_msg)
                    page.snack_bar = ft.SnackBar(
                        ft.Text(error_msg),
                        bgcolor=DesignSystem.ERROR
                    )
                    page.snack_bar.open = True
                    page.update()
                    return
                
                logger.info(f"Starting Updater.exe with parameters: version={update_info.version}, url={update_info.download_url[:50]}...")
                
                # Start updater with parameters
                process = subprocess.Popen([
                    str(updater_exe),
                    "--update",
                    "--version", update_info.version,
                    "--url", update_info.download_url,
                    "--restart",
                ])
                
                logger.info(f"Updater.exe started successfully (PID: {process.pid})")
                
                # Give updater a moment to initialize
                import time
                time.sleep(0.5)
                
                # Close application
                page.window_close()
                
            except FileNotFoundError as ex:
                error_msg = f"Updater.exe nem található: {ex} / Updater.exe not found: {ex}"
                logger.error(error_msg, exc_info=True)
                page.snack_bar = ft.SnackBar(
                    ft.Text(error_msg),
                    bgcolor=DesignSystem.ERROR,
                    duration=5000
                )
                page.snack_bar.open = True
                page.update()
            except Exception as ex:
                error_msg = f"Frissítés indítása sikertelen: {ex} / Failed to start update: {ex}"
                logger.error(error_msg, exc_info=True)
                page.snack_bar = ft.SnackBar(
                    ft.Text(error_msg),
                    bgcolor=DesignSystem.ERROR,
                    duration=5000
                )
                page.snack_bar.open = True
                page.update()
        
        def on_update_check_enabled_change(e):
            enabled = e.control.value
            set_setting("auto_update_check", "true" if enabled else "false")
            page.update()
        
        def on_update_frequency_change(e):
            frequency = e.control.value
            set_setting("update_check_frequency", frequency)
            page.update()
        
        update_check_enabled_checkbox = ft.Checkbox(
            label=translator.get_text("updates.auto_check", "Automatikus frissítés ellenőrzés / Auto check for updates"),
            value=update_check_enabled,
            on_change=on_update_check_enabled_change,
        )
        
        update_frequency_dropdown = ft.Dropdown(
            label=translator.get_text("updates.check_frequency", "Ellenőrzési gyakoriság / Check frequency"),
            options=[
                ft.dropdown.Option("startup", translator.get_text("updates.on_startup", "Indításkor / On startup")),
                ft.dropdown.Option("daily", translator.get_text("updates.daily", "Naponta / Daily")),
                ft.dropdown.Option("weekly", translator.get_text("updates.weekly", "Hetente / Weekly")),
            ],
            value=update_check_frequency,
            on_change=on_update_frequency_change,
            width=200,
        )
        
        updates_section = ft.Column([
            ft.Text("Frissítések / Updates", size=16, weight=ft.FontWeight.BOLD),
            ft.Text(f"Jelenlegi verzió / Current version: {current_version}", size=12, color=DesignSystem.TEXT_SECONDARY),
            ft.Container(height=DesignSystem.SPACING_4),
            ft.Text("GitHub Repository Beállítások / GitHub Repository Settings", size=14, weight=ft.FontWeight.W_600),
            ft.Row([
                github_owner_field,
                github_repo_field,
                github_save_button,
            ], spacing=DesignSystem.SPACING_3),
            ft.Text(
                f"Jelenlegi beállítás / Current: {github_owner}/{github_repo}" if github_owner else "GitHub repository nincs beállítva / GitHub repository not configured",
                size=10,
                color=DesignSystem.TEXT_TERTIARY,
                italic=True,
            ),
            ft.Container(height=DesignSystem.SPACING_4),
            ft.Divider(height=1),
            ft.Container(height=DesignSystem.SPACING_2),
            update_check_enabled_checkbox,
            update_frequency_dropdown,
            ft.Container(height=DesignSystem.SPACING_2),
            create_modern_button(
                text=translator.get_text("updates.check_now", "Frissítés ellenőrzése / Check for updates"),
                icon=ft.Icons.UPDATE if hasattr(ft.Icons, 'UPDATE') else (ft.Icons.SYNC if hasattr(ft.Icons, 'SYNC') else ft.Icons.REFRESH),
                on_click=check_for_updates,
                color=DesignSystem.BLUE_500,
            ),
            ft.Container(height=4),
            update_status_text,
        ], spacing=8)
        
        # About Section with Easter Egg
        # Easter egg trigger: 5 clicks on version within 2 seconds
        version_click_count = {"count": 0, "last_click": 0}
        
        def on_version_click(e):
            """Easter egg trigger - 5 clicks within 2 seconds"""
            import time
            current_time = time.time()
            
            # Reset if more than 2 seconds passed since last click
            if current_time - version_click_count["last_click"] > 2:
                version_click_count["count"] = 0
            
            version_click_count["count"] += 1
            version_click_count["last_click"] = current_time
            
            # Activate easter egg after 5 clicks
            if version_click_count["count"] >= 5:
                version_click_count["count"] = 0  # Reset counter
                # Launch Super Mario game!
                try:
                    game = SuperMarioGame()
                    game.view(page)
                except Exception as ex:
                    print(f"[SETTINGS] Error launching easter egg: {ex}")
                    import traceback
                    traceback.print_exc()
        
        # Version text with click handler
        version_text = ft.GestureDetector(
            content=ft.Text(
                f"Verzió / Version: {current_version}",
                size=12,
                color=DesignSystem.TEXT_SECONDARY
            ),
            on_tap=on_version_click,
        )
        
        about_section = ft.Column([
            ft.Text("Rendszer információk / System Information", size=16, weight=ft.FontWeight.BOLD),
            ft.Text(f"{APP_NAME}", size=14, weight=ft.FontWeight.BOLD),
            version_text,
            ft.Text("© 2025 Artence CMMS", size=11, color=DesignSystem.TEXT_TERTIARY, italic=True),
        ], spacing=8)
        
        # Logout Button
        logout_btn = ft.ElevatedButton(
            translator.get_text("common.buttons.logout"),
            icon=ft.Icons.LOGOUT,
            on_click=lambda e: self.on_logout() if self.on_logout else None,
        )

        return ft.Column([
            user_info,
            ft.Divider(height=1),
            language_section,
            ft.Divider(height=1),
            template_section,
            ft.Divider(height=1),
            maintenance_section,
            ft.Divider(height=1),
            operating_hours_section,
            ft.Divider(height=1),
            backup_section,
            ft.Divider(height=1),
            updates_section,
            ft.Divider(height=1),
            about_section,
            ft.Divider(height=1),
            ft.Container(
                content=logout_btn,
                padding=ft.padding.only(top=20),
            ),
        ], spacing=16, scroll=ft.ScrollMode.AUTO, expand=True)

