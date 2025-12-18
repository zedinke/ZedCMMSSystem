"""
Storage History Screen
Displays storage operation history with documents
"""

import flet as ft
# Compatibility for flet 0.23.2 - Icons are strings, not ft.Icons
if not hasattr(ft, 'Icons'):
    from utils.flet_icons import Icons
    ft.Icons = Icons
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import os

from services.storage_history_service import get_storage_history, get_storage_history_summary
from localization.translator import translator
from ui.components.modern_components import (
    create_modern_button,
    create_modern_text_field,
    create_modern_dropdown,
    create_vibrant_badge,
    create_modern_card,
    DesignSystem,
)
from ui.components.modern_card import create_tailwind_card
import logging

logger = logging.getLogger(__name__)


class StorageHistoryScreen:
    def __init__(self, page: ft.Page):
        self.page = page
    
    def view(self, page: ft.Page):
        if not hasattr(self, 'page') or self.page is None:
            self.page = page
        
        # History list container
        history_list = ft.Column([], spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)
        
        # Filters
        start_date_field = ft.TextField(
            label=translator.get_text("common.date_from") or "Dátumtól",
            hint_text="YYYY-MM-DD",
            width=200,
        )
        end_date_field = ft.TextField(
            label=translator.get_text("common.date_to") or "Dátumig",
            hint_text="YYYY-MM-DD",
            width=200,
        )
        
        action_type_dropdown = create_modern_dropdown(
            label=translator.get_text("storage.action_type") or "Művelet típusa",
            options=[
                ft.dropdown.Option("", translator.get_text("common.all") or "Összes"),
                ft.dropdown.Option("assign", translator.get_text("storage.assign") or "Hozzárendelés"),
                ft.dropdown.Option("update", translator.get_text("common.buttons.edit") or "Módosítás"),
                ft.dropdown.Option("remove", translator.get_text("storage.remove_part") or "Eltávolítás"),
                ft.dropdown.Option("transfer", translator.get_text("storage.transfer") or "Áttárazás"),
                ft.dropdown.Option("create", translator.get_text("common.buttons.create") or "Létrehozás"),
                ft.dropdown.Option("delete", translator.get_text("common.buttons.delete") or "Törlés"),
            ],
            width=200,
        )
        
        def refresh_history():
            """Refresh history list"""
            try:
                history_list.controls.clear()
                
                # Parse dates
                start_date = None
                end_date = None
                if start_date_field.value:
                    try:
                        start_date = datetime.strptime(start_date_field.value, "%Y-%m-%d")
                    except:
                        pass
                if end_date_field.value:
                    try:
                        end_date = datetime.strptime(end_date_field.value, "%Y-%m-%d")
                        # Add one day to include the entire end date
                        end_date = end_date + timedelta(days=1)
                    except:
                        pass
                
                # Get action type
                action_type = action_type_dropdown.value if action_type_dropdown.value else None
                
                # Get history
                history = get_storage_history(
                    start_date=start_date,
                    end_date=end_date,
                    action_type=action_type,
                    limit=500,
                )
                
                if not history:
                    history_list.controls.append(
                        ft.Container(
                            content=ft.Text(
                                translator.get_text("common.messages.no_data") or "Nincs adat",
                                size=14,
                                color=DesignSystem.TEXT_SECONDARY,
                            ),
                            padding=20,
                            alignment=ft.alignment.center,
                        )
                    )
                else:
                    for entry in history:
                        # Build action description
                        action_text = ""
                        if entry['action_type'] == "assign":
                            action_text = translator.get_text("storage.assign") or "Hozzárendelés"
                        elif entry['action_type'] == "update":
                            action_text = translator.get_text("common.buttons.edit") or "Módosítás"
                        elif entry['action_type'] == "remove":
                            action_text = translator.get_text("storage.remove_part") or "Eltávolítás"
                        elif entry['action_type'] == "transfer":
                            action_text = translator.get_text("storage.transfer") or "Áttárazás"
                        elif entry['action_type'] == "create":
                            action_text = translator.get_text("common.buttons.create") or "Létrehozás"
                        elif entry['action_type'] == "delete":
                            action_text = translator.get_text("common.buttons.delete") or "Törlés"
                        else:
                            action_text = entry['action_type']
                        
                        # Build part info
                        part_info = ""
                        if entry['part']:
                            part_info = f"{entry['part']['sku']} - {entry['part']['name']}"
                            if entry['quantity']:
                                part_info += f" ({entry['quantity']} db)"
                        
                        # Build location info
                        location_info = ""
                        if entry['action_type'] == "transfer":
                            if entry['source_location']:
                                location_info = f"{entry['source_location']['path']} → "
                            if entry['target_location']:
                                location_info += entry['target_location']['path']
                        elif entry['location']:
                            location_info = entry['location']['path']
                        
                        # Build user info
                        user_info = entry['user_name'] or translator.get_text("common.unknown") or "Ismeretlen"
                        
                        # Build timestamp
                        timestamp_str = entry['timestamp'].strftime("%Y-%m-%d %H:%M") if entry['timestamp'] else "-"
                        
                        # Build ID
                        entry_id = entry.get('id', '-')
                        
                        # Create card
                        card_content = ft.Column([
                            ft.Row([
                                create_vibrant_badge(
                                    text=action_text,
                                    variant="blue" if entry['action_type'] == "assign" else ("purple" if entry['action_type'] == "transfer" else "orange"),
                                    size=12,
                                ),
                                ft.Container(expand=True),
                                ft.Text(
                                    f"ID: {entry_id}",
                                    size=11,
                                    color=DesignSystem.TEXT_SECONDARY,
                                    weight=ft.FontWeight.W_500,
                                ),
                                ft.Container(width=8),
                                ft.Text(
                                    timestamp_str,
                                    size=12,
                                    color=DesignSystem.TEXT_SECONDARY,
                                ),
                            ]),
                            ft.Container(height=8),
                            ft.Text(
                                entry['description'] or "",
                                size=14,
                                weight=ft.FontWeight.W_500,
                            ),
                            ft.Container(height=4),
                            ft.Row([
                                ft.Text(
                                    translator.get_text("inventory.part") or "Alkatrész",
                                    size=12,
                                    color=DesignSystem.TEXT_SECONDARY,
                                ),
                                ft.Text(
                                    part_info or "-",
                                    size=12,
                                    weight=ft.FontWeight.W_500,
                                ),
                            ]) if part_info else ft.Container(),
                            ft.Row([
                                ft.Text(
                                    translator.get_text("storage.location") or "Tárhely",
                                    size=12,
                                    color=DesignSystem.TEXT_SECONDARY,
                                ),
                                ft.Text(
                                    location_info or "-",
                                    size=12,
                                    weight=ft.FontWeight.W_500,
                                ),
                            ]) if location_info else ft.Container(),
                            ft.Row([
                                ft.Text(
                                    translator.get_text("common.labels.user") or "Felhasználó",
                                    size=12,
                                    color=DesignSystem.TEXT_SECONDARY,
                                ),
                                ft.Text(
                                    user_info,
                                    size=12,
                                    weight=ft.FontWeight.W_500,
                                ),
                            ]),
                            # Documents with download option
                            ft.Row([
                                *[
                                    ft.ElevatedButton(
                                        text=doc['name'],
                                        icon=ft.Icons.DOWNLOAD if hasattr(ft.Icons, 'DOWNLOAD') else "download",
                                        on_click=lambda e, doc_path=doc['path'], doc_name=doc['name']: download_document(doc_path, doc_name),
                                        height=32,
                                        style=ft.ButtonStyle(
                                            color=DesignSystem.BLUE_600,
                                            bgcolor=DesignSystem.BLUE_50,
                                        ),
                                    )
                                    for doc in entry['documents']
                                ],
                            ], wrap=True) if entry['documents'] else ft.Container(),
                        ], spacing=4)
                        
                        card = create_tailwind_card(
                            content=card_content,
                            padding=16,
                        )
                        
                        history_list.controls.append(card)
                
                if page:
                    page.update()
            except Exception as e:
                logger.error(f"Error refreshing history: {e}", exc_info=True)
                history_list.controls.append(
                    ft.Container(
                        content=ft.Text(f"Error: {e}", color="red", size=14),
                        padding=10,
                    )
                )
                if page:
                    page.update()
        
        def download_document(source_path: str, doc_name: str):
            """Download document with file picker (user chooses save location)"""
            import shutil
            try:
                if not os.path.exists(source_path):
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(translator.get_text("common.messages.error_occurred") or "Hiba történt: A dokumentum nem található"),
                        bgcolor=DesignSystem.ERROR,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
                    return
                
                # Get file extension
                file_ext = Path(source_path).suffix
                default_filename = Path(source_path).name
                
                def on_save_result(e: ft.FilePickerResultEvent):
                    try:
                        if e.path:
                            dest_path = e.path
                            # Ensure correct extension
                            if not dest_path.endswith(file_ext):
                                dest_path = dest_path + file_ext
                            
                            # Copy file to user-selected location
                            shutil.copy2(source_path, dest_path)
                            
                            self.page.snack_bar = ft.SnackBar(
                                content=ft.Text(
                                    (translator.get_text("storage.document_downloaded") or "Dokumentum letöltve") + f": {dest_path}"
                                ),
                                bgcolor=DesignSystem.SUCCESS,
                            )
                            self.page.snack_bar.open = True
                            self.page.update()
                            
                            # Remove file picker from overlay after use
                            try:
                                if file_picker in self.page.overlay:
                                    self.page.overlay.remove(file_picker)
                                    self.page.update()
                            except:
                                pass
                        else:
                            # User cancelled
                            self.page.snack_bar = ft.SnackBar(
                                content=ft.Text(translator.get_text("common.messages.operation_cancelled") or "Letöltés megszakítva"),
                                bgcolor=DesignSystem.INFO,
                            )
                            self.page.snack_bar.open = True
                            self.page.update()
                            
                            # Remove file picker from overlay after cancellation
                            try:
                                if file_picker in self.page.overlay:
                                    self.page.overlay.remove(file_picker)
                                    self.page.update()
                            except:
                                pass
                    except Exception as ex:
                        logger.error(f"Error saving document: {ex}", exc_info=True)
                        self.page.snack_bar = ft.SnackBar(
                            content=ft.Text(f"{translator.get_text('common.messages.error_occurred') or 'Hiba történt'}: {str(ex)}"),
                            bgcolor=DesignSystem.ERROR,
                        )
                        self.page.snack_bar.open = True
                        self.page.update()
                        
                        # Remove file picker from overlay on error
                        try:
                            if file_picker in self.page.overlay:
                                self.page.overlay.remove(file_picker)
                                self.page.update()
                        except:
                            pass
                
                # Create file picker for save dialog
                file_picker = ft.FilePicker(on_result=on_save_result)
                self.page.overlay.append(file_picker)
                self.page.update()
                
                # Open save dialog
                file_picker.save_file(
                    dialog_title=translator.get_text("storage.download_document") or "Dokumentum letöltése",
                    file_name=default_filename,
                    file_type=ft.FilePickerFileType.CUSTOM,
                    allowed_extensions=[file_ext.lstrip('.')] if file_ext else ["docx", "pdf"],
                )
            except Exception as e:
                logger.error(f"Error downloading document: {e}", exc_info=True)
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"{translator.get_text('common.messages.error_occurred') or 'Hiba történt'}: {str(e)}"),
                    bgcolor=DesignSystem.ERROR,
                )
                self.page.snack_bar.open = True
                self.page.update()
        
        def apply_filters(e):
            """Apply filters and refresh"""
            refresh_history()
        
        # Set default dates (last 30 days)
        default_end = datetime.now()
        default_start = default_end - timedelta(days=30)
        start_date_field.value = default_start.strftime("%Y-%m-%d")
        end_date_field.value = default_end.strftime("%Y-%m-%d")
        
        # Filter button
        filter_btn = create_modern_button(
            text=translator.get_text("common.buttons.filter") or "Szűrés",
            icon=ft.Icons.FILTER_LIST if hasattr(ft.Icons, 'FILTER_LIST') else "filter_list",
            on_click=apply_filters,
            bgcolor=DesignSystem.BLUE_500,
            color=DesignSystem.WHITE,
        )
        
        # Refresh button
        refresh_btn = create_modern_button(
            text=translator.get_text("common.buttons.refresh") or "Frissítés",
            icon=ft.Icons.REFRESH,
            on_click=lambda e: refresh_history(),
            bgcolor=DesignSystem.GRAY_500,
            color=DesignSystem.WHITE,
        )
        
        # Initial load
        refresh_history()
        
        return ft.Column([
            ft.Row([
                ft.Text(
                    translator.get_text("storage.history") or "Raktártörténet",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Container(expand=True),
                refresh_btn,
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Container(height=12),
            create_tailwind_card(
                content=ft.Column([
                    ft.Text(
                        translator.get_text("common.filters") or "Szűrők",
                        size=14,
                        weight=ft.FontWeight.W_600,
                    ),
                    ft.Row([
                        start_date_field,
                        end_date_field,
                        action_type_dropdown,
                        filter_btn,
                    ], spacing=12),
                ], spacing=8),
                padding=16,
            ),
            ft.Container(height=12),
            history_list,
        ], spacing=12, expand=True)

