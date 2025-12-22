"""
Worksheet Screen (Munkalap képernyő) - Modern 2025 design
Manage worksheets: create, view, edit, add parts, track downtime
"""

import flet as ft
# Compatibility for flet 0.23.2 - Icons are strings, not ft.Icons
if not hasattr(ft, 'Icons'):
    from utils.flet_icons import Icons
    ft.Icons = Icons
from datetime import datetime
from collections import defaultdict
from pathlib import Path
from services import worksheet_service, asset_service, inventory_service, pdf_service
from services.context_service import get_app_context, get_current_user_id
from services.settings_service import get_worksheet_name_format
from services.user_service import get_user
from services.autosave_service import get_autosave_service
import logging
import threading

logger = logging.getLogger(__name__)
from localization.translator import translator
from ui.components.pagination import PaginationController, create_pagination_controls, create_items_per_page_selector
from ui.components.batch_actions_bar import create_batch_actions_bar
from ui.components.modern_components import (
    create_modern_button,
    create_modern_card,
    create_modern_text_field,
    create_modern_dropdown,
    create_modern_dialog,
    create_modern_badge,
    create_vibrant_badge,
    create_modern_icon_button,
    create_modern_table,
    create_modern_divider,
    create_empty_state_card,
    DesignSystem,
)
from ui.components.modern_card import (
    create_tailwind_card,
    create_info_card,
)
from typing import Optional


class WorksheetScreen:
    def __init__(self):
        self.current_worksheet = None
        self.selected_part_id = None
        self.mode = "list"  # list | create | detail
        self.show_closed = False
        self.expanded_worksheets = {}  # Track which worksheets are expanded

    def set_mode_from_route(self, route: str):
        """Parse sub-route to decide which subview to show"""
        try:
            parts = route.split("/")
            self.mode = "list"
            if len(parts) >= 2 and parts[1] == "create":
                self.mode = "create"
            elif len(parts) >= 2 and parts[1] == "detail" and len(parts) >= 3:
                self.mode = "detail"
                # Try to load worksheet from ID in route
                try:
                    worksheet_id = int(parts[2])
                    self.current_worksheet = worksheet_service.get_worksheet(worksheet_id)
                    print(f"[UI] Loaded worksheet {worksheet_id} from route")
                except (ValueError, Exception) as ex:
                    print(f"[UI] Error loading worksheet from route: {ex}")
                    self.current_worksheet = None
                    self.mode = "list"
        except Exception as ex:
            print(f"[UI] Error parsing route: {ex}")
            self.mode = "list"

    def _get_status_color(self, status: str) -> str:
        """Get color for worksheet status"""
        status_colors = {
            "Open": DesignSystem.SUCCESS,  # Green
            "Waiting for Parts": DesignSystem.WARNING,  # Amber
            "Closed": DesignSystem.TEXT_SECONDARY,  # Gray
        }
        return status_colors.get(status, DesignSystem.TEXT_SECONDARY)

    def _get_status_bg_color(self, status: str) -> str:
        """Get background color for worksheet status"""
        status_bg_colors = {
            "Open": DesignSystem.PRIMARY_LIGHT,  # Green light
            "Waiting for Parts": "#FEF3C7",  # Amber light
            "Closed": "#F1F5F9",  # Gray light
        }
        return status_bg_colors.get(status, "#F1F5F9")

    def _get_status_icon(self, status: str):
        """Get icon for worksheet status"""
        status_icons = {
            "Open": ft.Icons.PLAY_CIRCLE_OUTLINED if hasattr(ft.Icons, 'PLAY_CIRCLE_OUTLINED') else ft.Icons.PLAY_ARROW,
            "Waiting for Parts": ft.Icons.PAUSE_CIRCLE_OUTLINED if hasattr(ft.Icons, 'PAUSE_CIRCLE_OUTLINED') else ft.Icons.PAUSE,
            "Closed": ft.Icons.CHECK_CIRCLE_OUTLINED if hasattr(ft.Icons, 'CHECK_CIRCLE_OUTLINED') else ft.Icons.CHECK_CIRCLE,
        }
        return status_icons.get(status, ft.Icons.INFO)

    def _build_preview_panel(self, ws, page):
        """Build preview panel for worksheet"""
        # Reload worksheet with parts to ensure they are loaded
        if ws:
            try:
                ws = worksheet_service.get_worksheet(ws.id)
            except Exception as ex:
                logger.warning(f"Error reloading worksheet with parts in preview: {ex}")
        
        # Format dates
        breakdown_str = ws.breakdown_time.strftime("%Y-%m-%d %H:%M") if ws.breakdown_time else "-"
        repair_str = ws.repair_finished_time.strftime("%Y-%m-%d %H:%M") if ws.repair_finished_time else "-"
        downtime_str = f"{ws.total_downtime_hours:.2f}h" if ws.total_downtime_hours is not None else "-"
        created_str = ws.created_at.strftime("%Y-%m-%d %H:%M") if ws.created_at else "-"
        
        # Get PM task information if this worksheet is related to a PM task
        pm_task_info = worksheet_service.get_pm_task_for_worksheet(ws.id)
        is_pm_worksheet = pm_task_info is not None
        
        # Check if work request is available
        work_request_path = worksheet_service.get_work_request_for_worksheet(ws.id)
        has_work_request = work_request_path is not None
        
        # Check for scrapping documents for parts used in this worksheet
        from services.scrapping_service import list_scrapping_documents
        scrapping_docs = list_scrapping_documents(entity_type="Part")
        worksheet_scrapping_docs = [doc for doc in scrapping_docs if doc.worksheet_id == ws.id]
        has_scrapping_docs = len(worksheet_scrapping_docs) > 0
        
        # Create wrapper functions to avoid lambda closure issues in PyInstaller
        def create_worksheet_handlers(worksheet, work_req_path, scrapping_docs):
            def handle_edit(e):
                self._on_worksheet_edit(worksheet, page)
            
            def handle_pdf_download(e):
                self._on_pdf_download(worksheet, page)
            
            def handle_work_request_download(e):
                self._on_work_request_download(worksheet, page, work_req_path)
            
            def handle_scrapping_download(e):
                self._on_scrapping_download(worksheet, page, scrapping_docs)
            
            return handle_edit, handle_pdf_download, handle_work_request_download, handle_scrapping_download
        
        handle_edit, handle_pdf_download, handle_work_request_download, handle_scrapping_download = create_worksheet_handlers(ws, work_request_path, worksheet_scrapping_docs)
        
        # Parts info - detailed list with quantities
        # Ensure parts are loaded
        parts_list = []
        if ws:
            try:
                # Access parts to trigger lazy loading if needed
                parts_list = list(ws.parts) if ws.parts else []
            except Exception as ex:
                logger.warning(f"Error accessing worksheet parts: {ex}")
                parts_list = []
        
        parts_count = len(parts_list)
        total_parts_used = sum(part_link.quantity_used for part_link in parts_list) if parts_list else 0
        parts_text = f"{total_parts_used} db ({parts_count} típus)" if parts_count > 0 else "Nincs alkatrész"
        
        # Build parts list preview with detailed quantities
        parts_preview = []
        if parts_list and len(parts_list) > 0:
            for part_link in parts_list[:5]:  # Show max 5 parts
                part_name = part_link.part.name if part_link.part else '-'
                part_sku = part_link.part.sku if part_link.part and part_link.part.sku else ''
                quantity = part_link.quantity_used
                unit = part_link.part.unit if part_link.part and part_link.part.unit else 'db'
                parts_preview.append(
                    ft.Text(
                        f"• {part_name} ({part_sku}): {quantity} {unit}",
                        size=12,
                        color=DesignSystem.TEXT_SECONDARY,
                    )
                )
            if len(parts_list) > 5:
                parts_preview.append(
                    ft.Text(
                        f"... és még {len(parts_list) - 5} alkatrész",
                        size=12,
                        color=DesignSystem.TEXT_TERTIARY,
                        italic=True,
                    )
                )
        else:
            parts_preview.append(
                ft.Text(
                    "Nincs alkatrész",
                    size=12,
                    color=DesignSystem.TEXT_TERTIARY,
                    italic=True,
                )
            )
        
        # Assigned user (safe access to avoid lazy loading errors)
        try:
            assigned_user = ws.assigned_user.username if ws.assigned_user else "-"
        except Exception:
            # Fallback if assigned_user is not loaded or session is closed
            assigned_user = "-"
        
        # PM task info section
        pm_info_section = None
        if is_pm_worksheet:
            executed_str = pm_task_info['executed_date'].strftime("%Y-%m-%d %H:%M") if pm_task_info.get('executed_date') else "-"
            pm_info_section = ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.CONSTRUCTION if hasattr(ft.Icons, 'CONSTRUCTION') else ft.Icons.BUILD, size=20, color="#F59E0B"),
                    ft.Text(
                        translator.get_text("preventive_maintenance.title"),
                        size=12,
                        weight=ft.FontWeight.W_600,
                        color=DesignSystem.TEXT_SECONDARY,
                    ),
                ], spacing=8),
                ft.Container(height=8),
                ft.TextButton(
                    pm_task_info['pm_task_name'],
                    on_click=lambda _: page.go(f"/pm?task_id={pm_task_info['pm_task_id']}"),
                    style=ft.ButtonStyle(color=DesignSystem.PRIMARY),
                ),
                ft.Container(height=4),
                ft.Text(
                    pm_task_info.get('pm_task_description', '-') or '-',
                    size=12,
                    color=DesignSystem.TEXT_SECONDARY,
                ),
                ft.Container(height=8),
                ft.Text(
                    f"Végrehajtva: {executed_str}",
                    size=11,
                    color=DesignSystem.TEXT_TERTIARY,
                ),
            ], spacing=0)
        
        return ft.Container(
            content=ft.Column([
                create_modern_divider(),
                ft.Container(height=16),
                pm_info_section if pm_info_section else ft.Container(height=0),
                ft.Container(height=16) if pm_info_section else ft.Container(height=0),
                ft.Divider(height=1, color="#E2E8F0") if pm_info_section else ft.Container(height=0),
                ft.Container(height=16) if pm_info_section else ft.Container(height=0),
                ft.Row([
                    ft.Column([
                        ft.Text(
                            translator.get_text("worksheets.machine"),
                            size=11,
                            color=DesignSystem.TEXT_TERTIARY,
                        ),
                        ft.Text(
                            ws.machine.name if ws.machine else "-",
                            size=14,
                            weight=ft.FontWeight.W_600,
                            color=DesignSystem.TEXT_PRIMARY,
                        ),
                    ], spacing=4, tight=True),
                    ft.Column([
                        ft.Text(
                            translator.get_text("worksheets.technician"),
                            size=11,
                            color=DesignSystem.TEXT_TERTIARY,
                        ),
                        ft.Text(
                            assigned_user,
                            size=14,
                            weight=ft.FontWeight.W_600,
                            color=DesignSystem.TEXT_PRIMARY,
                        ),
                    ], spacing=4, tight=True),
                    ft.Column([
                        ft.Text(
                            translator.get_text("worksheets.parts_used"),
                            size=11,
                            color=DesignSystem.TEXT_TERTIARY,
                        ),
                        ft.Text(
                            parts_text,
                            size=14,
                            weight=ft.FontWeight.W_600,
                            color=DesignSystem.TEXT_PRIMARY,
                        ),
                    ], spacing=4, tight=True),
                ], spacing=24),
                ft.Container(height=16),
                ft.Row([
                    ft.Column([
                        ft.Text(
                            translator.get_text("worksheets.breakdown_time"),
                            size=11,
                            color=DesignSystem.TEXT_TERTIARY,
                        ),
                        ft.Text(breakdown_str, size=13, color="#0F172A"),
                    ], spacing=4, tight=True),
                    ft.Column([
                        ft.Text(
                            translator.get_text("worksheets.repair_finished_time"),
                            size=11,
                            color=DesignSystem.TEXT_TERTIARY,
                        ),
                        ft.Text(repair_str, size=13, color="#0F172A"),
                    ], spacing=4, tight=True),
                    ft.Column([
                        ft.Text(
                            translator.get_text("worksheets.downtime"),
                            size=11,
                            color=DesignSystem.TEXT_TERTIARY,
                        ),
                        ft.Text(downtime_str, size=13, weight=ft.FontWeight.W_600, color="#6366F1"),
                    ], spacing=4, tight=True),
                ], spacing=24),
                ft.Container(height=16),
                create_modern_divider(),
                ft.Container(height=16),
                ft.Column([
                    ft.Text(
                        translator.get_text("worksheets.parts_used"),
                        size=12,
                        weight=ft.FontWeight.W_600,
                        color=DesignSystem.TEXT_SECONDARY,
                    ),
                    ft.Container(height=8),
                    ft.Column(parts_preview, spacing=4, tight=True),
                ], spacing=0) if parts_preview else ft.Container(),
                ft.Container(height=16) if parts_preview else ft.Container(height=0),
                ft.Divider(height=1, color="#E2E8F0") if ws.notes else ft.Container(height=0),
                ft.Container(height=16) if ws.notes else ft.Container(height=0),
                ft.Column([
                    ft.Text(
                        translator.get_text("worksheets.notes"),
                        size=12,
                        weight=ft.FontWeight.W_600,
                        color=DesignSystem.TEXT_SECONDARY,
                    ),
                    ft.Container(height=8),
                    ft.Text(
                        ws.notes or "-",
                        size=12,
                        color=DesignSystem.TEXT_PRIMARY,
                        selectable=True,
                    ),
                ], spacing=0) if ws.notes else ft.Container(),
                ft.Container(height=16) if ws.notes else ft.Container(height=0),
                create_modern_divider(),
                ft.Container(height=16),
                ft.Row([
                    ft.ElevatedButton(
                        translator.get_text("common.buttons.edit"),
                        icon=ft.Icons.EDIT if hasattr(ft.Icons, 'EDIT') else ft.Icons.EDIT_OUTLINED,
                        on_click=handle_edit,
                        bgcolor="#6366F1",
                        color="#FFFFFF",
                        height=40,
                    ),
                    ft.ElevatedButton(
                        "DOCX",
                        icon=ft.Icons.DOWNLOAD if hasattr(ft.Icons, 'DOWNLOAD') else ft.Icons.FILE_DOWNLOAD,
                        on_click=handle_pdf_download,
                        bgcolor=DesignSystem.SUCCESS,
                        color="#FFFFFF",
                        height=40,
                    ),
                    # Work request button (only if available)
                    ft.ElevatedButton(
                        translator.get_text("preventive_maintenance.work_request"),
                        icon=ft.Icons.DESCRIPTION if hasattr(ft.Icons, 'DESCRIPTION') else ft.Icons.ASSIGNMENT,
                        on_click=handle_work_request_download,
                        bgcolor="#F59E0B",
                        color="#FFFFFF",
                        height=40,
                    ) if has_work_request else ft.Container(width=0, height=0),
                    # Scrapping document button (only if available)
                    ft.ElevatedButton(
                        translator.get_text("scrapping.download"),
                        icon=ft.Icons.DESCRIPTION if hasattr(ft.Icons, 'DESCRIPTION') else ft.Icons.ASSIGNMENT,
                        on_click=handle_scrapping_download,
                        bgcolor="#EF4444",
                        color="#FFFFFF",
                        height=40,
                    ) if has_scrapping_docs else ft.Container(width=0, height=0),
                ], spacing=12),
            ], spacing=0),
            padding=20,
            bgcolor="#F8FAFC",
            border=ft.border.all(1, "#E2E8F0"),
            border_radius=12,
        )

    def _on_worksheet_edit(self, ws, page):
        """Handle worksheet edit click"""
        self.current_worksheet = ws
        self.mode = "detail"
        page.go(f"/worksheets/detail/{ws.id}")

    def _on_pdf_download(self, ws, page):
        """Handle PDF download click - ask user where to save"""
        try:
            import os
            import shutil
            from pathlib import Path
            
            ctx = get_app_context()
            generated_by = ctx.username or "system"
            worksheet_id = ws.id
            
            # Generate default filename
            filename = f"worksheet_{worksheet_id}"
            if ws.closed_at:
                closed_date = ws.closed_at.strftime("%Y-%m-%d")
                filename = f"worksheet_{worksheet_id}_{closed_date}"
            default_filename = f"{filename}.docx"
            
            # Create a temporary file first (will be moved to user-selected location)
            temp_dir = Path("temp_pdfs")
            temp_dir.mkdir(exist_ok=True)
            temp_path = temp_dir / default_filename
            
            # Show loading message
            page.snack_bar = ft.SnackBar(ft.Text(translator.get_text("worksheets.document_generating")))
            page.snack_bar.open = True
            page.update()
            
            # Generate document (DOCX) to temp location first
            try:
                print(f"[UI] Generating document for worksheet {worksheet_id} to temp location")
                docx_path = pdf_service.generate_worksheet_pdf(
                    worksheet_id, 
                    generated_by=generated_by, 
                    output_path=str(temp_path)
                )
                print(f"[UI] Document generated successfully: {docx_path}")
                
                # File extension is always DOCX now
                file_ext = "docx"
                file_type_name = "DOCX"
                
                # Now ask user where to save
                def on_save_result(e: ft.FilePickerResultEvent):
                    try:
                        dest_path = getattr(e, "path", None)
                        if dest_path and os.path.exists(docx_path):
                            # Ensure correct extension
                            if not dest_path.endswith(f'.{file_ext}'):
                                dest_path = dest_path + f'.{file_ext}'
                            
                            # Copy file to user-selected location
                            shutil.copy2(docx_path, dest_path)
                            
                            # Clean up temp file
                            try:
                                os.remove(docx_path)
                            except Exception:
                                pass
                            
                            page.snack_bar = ft.SnackBar(
                                ft.Text(f"{file_type_name} letöltve ide: {dest_path}")
                            )
                            page.snack_bar.open = True
                            page.update()
                        elif dest_path is None:
                            # User cancelled - clean up temp file
                            try:
                                os.remove(docx_path)
                            except Exception:
                                pass
                            page.snack_bar = ft.SnackBar(
                                ft.Text(translator.get_text("worksheets.download_cancelled"))
                            )
                            page.snack_bar.open = True
                            page.update()
                    except Exception as ex:
                        print(f"[UI] Error saving file: {ex}")
                        import traceback
                        traceback.print_exc()
                        page.snack_bar = ft.SnackBar(ft.Text(f"Hiba a mentéskor: {str(ex)}"))
                        page.snack_bar.open = True
                        page.update()
                
                # Create file picker for save dialog
                file_picker = ft.FilePicker(
                    on_result=on_save_result
                )
                page.overlay.append(file_picker)
                page.update()
                
                # Open save dialog
                file_picker.save_file(
                    dialog_title=f"{file_type_name} mentése / Save {file_type_name}",
                    file_name=default_filename,
                    file_type=ft.FilePickerFileType.CUSTOM,
                    allowed_extensions=[file_ext]
                )
                
            except Exception as ex:
                print(f"[UI] PDF generation error: {ex}")
                import traceback
                traceback.print_exc()
                page.snack_bar = ft.SnackBar(ft.Text(f"{translator.get_text('common.messages.error_occurred')}: {str(ex)}"))
                page.snack_bar.open = True
                page.update()
        except Exception as ex:
            print(f"[UI] _on_pdf_download error: {ex}")
            import traceback
            traceback.print_exc()
            page.snack_bar = ft.SnackBar(ft.Text(f"{translator.get_text('common.messages.error_occurred')}: {str(ex)}"))
            page.snack_bar.open = True
            page.update()

    def _on_scrapping_download(self, ws, page, scrapping_docs):
        """Handle scrapping document download - allow user to choose save location"""
        try:
            if not scrapping_docs:
                page.snack_bar = ft.SnackBar(
                    ft.Text(translator.get_text("scrapping.document_not_found") if hasattr(translator, 'get_text') else "Nincs selejtezési lap / No scrapping document"),
                    bgcolor=DesignSystem.ERROR
                )
                page.snack_bar.open = True
                page.update()
                return
            
            from pathlib import Path
            import os
            import shutil
            
            # If single document, save it directly
            if len(scrapping_docs) == 1:
                doc_path = Path(scrapping_docs[0].docx_path)
                if not doc_path.exists():
                    page.snack_bar = ft.SnackBar(
                        ft.Text(translator.get_text("scrapping.document_not_found") if hasattr(translator, 'get_text') else "Selejtezési lap nem található / Scrapping document not found"),
                        bgcolor=DesignSystem.ERROR
                    )
                    page.snack_bar.open = True
                    page.update()
                    return
                
                # Use file picker to let user choose save location
                file_picker = ft.FilePicker()
                page.overlay.append(file_picker)
                page.update()
                
                # Generate default filename
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                default_filename = f"selejtezesi_lap_{timestamp}.docx"
                
                def on_save_result(e: ft.FilePickerResultEvent):
                    try:
                        dest_path = getattr(e, "path", None)
                        if dest_path:
                            # Ensure .docx extension
                            if not dest_path.endswith('.docx'):
                                dest_path = dest_path + '.docx'
                            
                            # Copy file to chosen location
                            shutil.copy2(str(doc_path), dest_path)
                            
                            page.snack_bar = ft.SnackBar(
                                ft.Text(translator.get_text("scrapping.document_saved") if hasattr(translator, 'get_text') else f"Selejtezési lap mentve: {dest_path}"),
                                bgcolor=DesignSystem.SUCCESS
                            )
                        else:
                            # User cancelled
                            page.snack_bar = ft.SnackBar(
                                ft.Text(translator.get_text("common.buttons.cancel") if hasattr(translator, 'get_text') else "Mentés megszakítva"),
                                bgcolor=DesignSystem.INFO
                            )
                    except Exception as save_ex:
                        logger.error(f"Error saving scrapping document: {save_ex}", exc_info=True)
                        page.snack_bar = ft.SnackBar(
                            ft.Text(f"{translator.get_text('common.messages.error_occurred')}: {save_ex}"),
                            bgcolor=DesignSystem.ERROR
                        )
                    finally:
                        page.overlay.remove(file_picker)
                        page.snack_bar.open = True
                        page.update()
                
                file_picker.on_result = on_save_result
                file_picker.save_file(
                    dialog_title=translator.get_text("scrapping.save_document") if hasattr(translator, 'get_text') else "Selejtezési lap mentése",
                    file_name=default_filename,
                    file_type=ft.FilePickerFileType.CUSTOM,
                    allowed_extensions=["docx"]
                )
            else:
                # Multiple documents - let user choose which one to save, or save all
                # For now, save the first one (can be enhanced later to show a list)
                doc_path = Path(scrapping_docs[0].docx_path)
                if not doc_path.exists():
                    page.snack_bar = ft.SnackBar(
                        ft.Text(translator.get_text("scrapping.document_not_found") if hasattr(translator, 'get_text') else "Selejtezési lap nem található / Scrapping document not found"),
                        bgcolor=DesignSystem.ERROR
                    )
                    page.snack_bar.open = True
                    page.update()
                    return
                
                # Use file picker to let user choose save location
                file_picker = ft.FilePicker()
                page.overlay.append(file_picker)
                page.update()
                
                # Generate default filename
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                default_filename = f"selejtezesi_lap_{timestamp}.docx"
                
                def on_save_result(e: ft.FilePickerResultEvent):
                    try:
                        dest_path = getattr(e, "path", None)
                        if dest_path:
                            # Ensure .docx extension
                            if not dest_path.endswith('.docx'):
                                dest_path = dest_path + '.docx'
                            
                            # Copy file to chosen location
                            shutil.copy2(str(doc_path), dest_path)
                            
                            page.snack_bar = ft.SnackBar(
                                ft.Text(f"{len(scrapping_docs)} selejtezési lap található. Az első mentve: {dest_path}"),
                                bgcolor=DesignSystem.SUCCESS
                            )
                        else:
                            # User cancelled
                            page.snack_bar = ft.SnackBar(
                                ft.Text(translator.get_text("common.buttons.cancel") if hasattr(translator, 'get_text') else "Mentés megszakítva"),
                                bgcolor=DesignSystem.INFO
                            )
                    except Exception as save_ex:
                        logger.error(f"Error saving scrapping document: {save_ex}", exc_info=True)
                        page.snack_bar = ft.SnackBar(
                            ft.Text(f"{translator.get_text('common.messages.error_occurred')}: {save_ex}"),
                            bgcolor=DesignSystem.ERROR
                        )
                    finally:
                        page.overlay.remove(file_picker)
                        page.snack_bar.open = True
                        page.update()
                
                file_picker.on_result = on_save_result
                file_picker.save_file(
                    dialog_title=translator.get_text("scrapping.save_document") if hasattr(translator, 'get_text') else "Selejtezési lap mentése",
                    file_name=default_filename,
                    file_type=ft.FilePickerFileType.CUSTOM,
                    allowed_extensions=["docx"]
                )
        except Exception as e:
            logger.error(f"Error downloading scrapping document: {e}", exc_info=True)
            page.snack_bar = ft.SnackBar(
                ft.Text(f"{translator.get_text('common.messages.error_occurred')}: {e}"),
                bgcolor=DesignSystem.ERROR
            )
            page.snack_bar.open = True
            page.update()
    
    def _on_work_request_download(self, ws, page, work_request_path: str = None):
        """Handle work request download click"""
        try:
            import os
            import shutil
            from pathlib import Path
            
            # Get work request path if not provided
            if not work_request_path:
                work_request_path = worksheet_service.get_work_request_for_worksheet(ws.id)
            
            if not work_request_path or not os.path.exists(work_request_path):
                page.snack_bar = ft.SnackBar(ft.Text(translator.get_text("worksheets.work_request_not_found")))
                page.snack_bar.open = True
                page.update()
                return
            
            # Generate default filename
            filename = f"work_request_{ws.id}"
            if ws.closed_at:
                closed_date = ws.closed_at.strftime("%Y-%m-%d")
                filename = f"work_request_{ws.id}_{closed_date}"
            default_filename = f"{filename}.docx"
            
            # Create a temporary file first (will be moved to user-selected location)
            temp_dir = Path("temp_pdfs")
            temp_dir.mkdir(exist_ok=True)
            temp_path = temp_dir / default_filename
            
            # Copy work request to temp location
            shutil.copy2(work_request_path, temp_path)
            
            # Show loading message
            page.snack_bar = ft.SnackBar(ft.Text(translator.get_text("worksheets.work_request_preparing")))
            page.snack_bar.open = True
            page.update()
            
            # Now ask user where to save
            def on_save_result(e: ft.FilePickerResultEvent):
                try:
                    dest_path = getattr(e, "path", None)
                    if dest_path and os.path.exists(temp_path):
                        # Ensure correct extension
                        if not dest_path.endswith('.docx'):
                            dest_path = dest_path + '.docx'
                        
                        # Copy file to user-selected location
                        shutil.copy2(temp_path, dest_path)
                        
                        # Clean up temp file
                        try:
                            os.remove(temp_path)
                        except Exception:
                            pass
                        
                        page.snack_bar = ft.SnackBar(
                            ft.Text(f"Munkaigénylő lap letöltve ide: {dest_path}")
                        )
                        page.snack_bar.open = True
                        page.update()
                    elif dest_path is None:
                        # User cancelled - clean up temp file
                        try:
                            os.remove(temp_path)
                        except Exception:
                            pass
                        page.snack_bar = ft.SnackBar(
                            ft.Text("Letöltés megszakítva / Download cancelled")
                        )
                        page.snack_bar.open = True
                        page.update()
                except Exception as ex:
                    print(f"[UI] Error saving work request file: {ex}")
                    import traceback
                    traceback.print_exc()
                    page.snack_bar = ft.SnackBar(ft.Text(f"Hiba a mentéskor: {str(ex)}"))
                    page.snack_bar.open = True
                    page.update()
            
            # Create file picker for save dialog
            file_picker = ft.FilePicker(
                on_result=on_save_result
            )
            page.overlay.append(file_picker)
            page.update()
            
            # Open save dialog
            file_picker.save_file(
                dialog_title="Munkaigénylő lap mentése / Save Work Request",
                file_name=default_filename,
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["docx"]
            )
            
        except Exception as ex:
            print(f"[UI] _on_work_request_download error: {ex}")
            import traceback
            traceback.print_exc()
            page.snack_bar = ft.SnackBar(ft.Text(f"{translator.get_text('common.messages.error_occurred')}: {str(ex)}"))
            page.snack_bar.open = True
            page.update()

    def _build_worksheet_card(self, ws, on_worksheet_selected, page, selected_worksheet_ids=None, on_selection_change=None):
        """Build modern worksheet card with expandable preview"""
        status_color = self._get_status_color(ws.status)
        status_bg_color = self._get_status_bg_color(ws.status)
        status_icon = self._get_status_icon(ws.status)
        
        # Format dates
        breakdown_str = ws.breakdown_time.strftime("%Y-%m-%d %H:%M") if ws.breakdown_time else "-"
        created_str = ws.created_at.strftime("%Y-%m-%d") if ws.created_at else "-"
        
        # Get PM task information if this worksheet is related to a PM task
        pm_task_info = worksheet_service.get_pm_task_for_worksheet(ws.id)
        is_pm_worksheet = pm_task_info is not None
        
        # Check if work request is available
        work_request_path = worksheet_service.get_work_request_for_worksheet(ws.id)
        has_work_request = work_request_path is not None
        
        # Check if this worksheet is expanded
        is_expanded = self.expanded_worksheets.get(ws.id, False)
        
        # Create checkbox for multi-select (if selection is enabled)
        worksheet_checkbox = None
        if selected_worksheet_ids is not None and on_selection_change is not None:
            worksheet_checkbox = ft.Checkbox(
                value=ws.id in selected_worksheet_ids,
                on_change=lambda e, ws_id=ws.id: on_selection_change(ws_id, e),
                tooltip=translator.get_text("common.select") if hasattr(translator, 'get_text') else "Select",
            )
        
        # Preview panel
        preview_panel = self._build_preview_panel(ws, page)
        preview_panel.visible = is_expanded
        
        # Toggle function
        def toggle_preview(e):
            self.expanded_worksheets[ws.id] = not self.expanded_worksheets.get(ws.id, False)
            preview_panel.visible = self.expanded_worksheets[ws.id]
            # Update chevron icon
            chevron_icon.icon = ft.Icons.EXPAND_LESS if preview_panel.visible else ft.Icons.EXPAND_MORE
            page.update()
        
        # Chevron icon
        chevron_icon = ft.IconButton(
            icon=ft.Icons.EXPAND_LESS if is_expanded else ft.Icons.EXPAND_MORE,
            on_click=toggle_preview,
            icon_size=20,
            tooltip="Előnézet megjelenítése",
        )
        
        # PM task badge if this is a PM worksheet
        pm_badge = None
        if is_pm_worksheet:
            pm_badge = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.CONSTRUCTION if hasattr(ft.Icons, 'CONSTRUCTION') else ft.Icons.BUILD, size=16, color="#F59E0B"),
                    ft.Text(
                        pm_task_info['pm_task_name'],
                        size=11,
                        weight=ft.FontWeight.W_600,
                        color=DesignSystem.WARNING,
                    ),
                ], spacing=4, tight=True),
                padding=6,
                bgcolor="#FEF3C7",
                border_radius=6,
            )
        
        # Check if work request is available
        work_request_path = worksheet_service.get_work_request_for_worksheet(ws.id)
        has_work_request = work_request_path is not None
        
        # Main card content
        card_content = ft.Container(
            content=ft.Column([
                ft.Row([
                    worksheet_checkbox if worksheet_checkbox else ft.Container(width=0),
                    ft.Container(width=8) if worksheet_checkbox else ft.Container(width=0),  # Spacing
                ft.Container(
                    content=ft.Icon(status_icon, size=24, color=status_color),
                    padding=8,
                    bgcolor=status_bg_color,
                    border_radius=8,
                ),
                ft.Column([
                    ft.Row([
                        ft.Text(
                            ws.title if ws.title else f"{translator.get_text('worksheets.worksheet')} #{ws.id}",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=DesignSystem.TEXT_PRIMARY,
                        ),
                        pm_badge if pm_badge else ft.Container(),
                    ], spacing=8, tight=True),
                    ft.Text(
                        ws.machine.name if ws.machine else "-",
                        size=14,
                        color=DesignSystem.TEXT_SECONDARY,
                    ),
                ], spacing=4, tight=True, expand=True),
                ft.Container(
                    content=ft.Text(
                        ws.status,
                        size=12,
                        weight=ft.FontWeight.W_600,
                        color=status_color,
                    ),
                    padding=8,
                    bgcolor=status_bg_color,
                    border_radius=6,
                ),
                chevron_icon,
            ], alignment=ft.MainAxisAlignment.START),
            ft.Container(height=12),
            ft.Row([
                ft.Column([
                    ft.Text(
                        translator.get_text("worksheets.breakdown_time"),
                        size=11,
                        color=DesignSystem.TEXT_TERTIARY,
                    ),
                    ft.Text(breakdown_str, size=13, color="#0F172A"),
                ], spacing=2, tight=True),
                ft.Column([
                    ft.Text(
                        translator.get_text("common.time.day"),
                        size=11,
                        color=DesignSystem.TEXT_TERTIARY,
                    ),
                    ft.Text(created_str, size=13, color="#0F172A"),
                ], spacing=2, tight=True),
                ft.Column(expand=True),
                ft.ElevatedButton(
                    translator.get_text("common.buttons.edit"),
                    icon=ft.Icons.EDIT if hasattr(ft.Icons, 'EDIT') else ft.Icons.EDIT_OUTLINED,
                    on_click=lambda e, w=ws: on_worksheet_selected(w),
                    bgcolor="#6366F1",
                    color="#FFFFFF",
                    height=36,
                ),
            ], alignment=ft.MainAxisAlignment.START),
            ], spacing=0),
            padding=20,
        )
        
        # Combine card and preview
        full_content = ft.Column([
            card_content,
            preview_panel,
        ], spacing=0)
        
        return ft.Card(
            elevation=0,
            content=ft.Container(
                padding=0,
                border=ft.border.all(1, "#E2E8F0"),
                border_radius=12,
                bgcolor="#FFFFFF",
                content=full_content,
            ),
        )

    def _build_grouped_worksheet_list(self, worksheets, on_worksheet_selected, page, selected_worksheet_ids=None, on_selection_change=None):
        """Build a modern grouped list of worksheets"""
        list_items = []
        
        if not worksheets:
            list_items.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(name=ft.Icons.ASSIGNMENT if hasattr(ft.Icons, 'ASSIGNMENT') else ft.Icons.DESCRIPTION, size=64, color="#94A3B8"),
                        ft.Text(
                            translator.get_text("empty_states.no_worksheets"),
                            size=16,
                            color=DesignSystem.TEXT_SECONDARY,
                        ),
                    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
                    padding=40,
                    expand=True,
                )
            )
            return list_items
        
        # Group worksheets by date
        grouped = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        for ws in worksheets:
            ref_date = ws.breakdown_time or ws.created_at or datetime.now()
            year = ref_date.strftime("%Y")
            month = ref_date.strftime("%m")
            day = ref_date.strftime("%d")
            grouped[year][month][day].append(ws)
        
        # Render grouped structure
        for year in sorted(grouped.keys(), reverse=True):
            month_items = []
            
            for month in sorted(grouped[year].keys(), reverse=True):
                month_name = datetime.strptime(month, "%m").strftime("%B")
                day_items = []
                
                for day in sorted(grouped[year][month].keys(), reverse=True):
                    day_worksheets = grouped[year][month][day]
                    worksheet_cards = [
                        self._build_worksheet_card(ws, on_worksheet_selected, page, selected_worksheet_ids, on_selection_change)
                        for ws in day_worksheets
                    ]
                    
                    day_items.append(
                        ft.ExpansionTile(
                            title=ft.Text(
                                f"{day}. ({len(day_worksheets)} munkalap)",
                                size=13,
                                weight=ft.FontWeight.W_600,
                                color="#475569",
                            ),
                            bgcolor="#F8FAFC",
                            controls=worksheet_cards,
                            initially_expanded=False,
                        )
                    )
                
                month_items.append(
                    ft.ExpansionTile(
                        title=ft.Text(
                            month_name,
                            size=15,
                            weight=ft.FontWeight.W_600,
                            color="#334155",
                        ),
                        bgcolor="#F1F5F9",
                        controls=day_items,
                        initially_expanded=False,
                    )
                )
            
            list_items.append(
                ft.ExpansionTile(
                    title=ft.Text(
                        year,
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=DesignSystem.TEXT_PRIMARY,
                    ),
                    bgcolor="#E2E8F0",
                    controls=month_items,
                    initially_expanded=len(grouped) == 1,
                )
            )
        
        return list_items

    def view(self, page: ft.Page):
        ctx = get_app_context()

        # Decide which sub-view to render based on mode
        if self.mode == "create":
            return self._create_worksheet_view(page)
        if self.mode == "detail":
            if self.current_worksheet:
                return self._worksheet_detail_view(page)
            else:
                # If detail mode but no worksheet loaded, go back to list
                print("[UI] Detail mode but no worksheet loaded, switching to list")
                self.mode = "list"
                # Continue to render list view below

        # Otherwise render list
        def get_worksheets():
            """Helper function to get worksheets based on current filter"""
            return worksheet_service.list_all_worksheets() if self.show_closed else worksheet_service.list_active_worksheets()
        
        # Pagination settings
        ITEMS_PER_PAGE = 25
        
        # Get all worksheets
        all_worksheets = get_worksheets()
        total_worksheets_count = len(all_worksheets)
        
        # Initialize PaginationController
        pagination_controller = PaginationController(
            total_items=total_worksheets_count,
            items_per_page=ITEMS_PER_PAGE,
            on_page_change=None,  # Will be set after refresh function is defined
        )
        
        # Selected items for batch operations
        selected_worksheet_ids = set()
        
        # Get paginated worksheets
        offset = pagination_controller.start_index
        limit = pagination_controller.items_per_page
        worksheets = all_worksheets[offset:offset + limit]

        def on_worksheet_selected(ws):
            try:
                print("[UI] worksheet selected", ws.id)
                self.current_worksheet = ws
                self.mode = "detail"
                page.go(f"/worksheets/detail/{ws.id}")
            except Exception as ex:
                print(f"[UI] Error selecting worksheet: {ex}")
                import traceback
                traceback.print_exc()
                page.snack_bar = ft.SnackBar(ft.Text(f"{translator.get_text('common.messages.error_occurred')}: {str(ex)}"))
                page.snack_bar.open = True
                page.update()

        def create_new_worksheet():
            try:
                print("[UI] create_new_worksheet clicked")
                self.mode = "create"
                page.go("/worksheets/create")
            except Exception as ex:
                print(f"[UI] Error creating worksheet: {ex}")
                import traceback
                traceback.print_exc()
                page.snack_bar = ft.SnackBar(ft.Text(f"{translator.get_text('common.messages.error_occurred')}: {str(ex)}"))
                page.snack_bar.open = True
                page.update()
        
        # Selection change handler
        batch_actions_bar_ref = {"value": None}  # Reference to batch actions bar
        
        def _on_worksheet_selection_change(worksheet_id, e):
            """Handle worksheet selection checkbox change"""
            if e.control.value:
                selected_worksheet_ids.add(worksheet_id)
            else:
                selected_worksheet_ids.discard(worksheet_id)
            
            # Update batch actions bar visibility
            _update_batch_actions_bar()
            page.update()
        
        def _clear_selection():
            """Clear all selections"""
            selected_worksheet_ids.clear()
            # Rebuild list
            ws_list_items = self._build_grouped_worksheet_list(worksheets, on_worksheet_selected, page, selected_worksheet_ids, _on_worksheet_selection_change)
            ws_list.controls.clear()
            ws_list.controls.extend(ws_list_items)
            _update_batch_actions_bar()
            page.update()
        
        def _select_all():
            """Select all worksheets on current page"""
            for ws in worksheets:
                selected_worksheet_ids.add(ws.id)
            # Rebuild list
            ws_list_items = self._build_grouped_worksheet_list(worksheets, on_worksheet_selected, page, selected_worksheet_ids, _on_worksheet_selection_change)
            ws_list.controls.clear()
            ws_list.controls.extend(ws_list_items)
            _update_batch_actions_bar()
            page.update()
        
        def _update_batch_actions_bar():
            """Update batch actions bar visibility and content"""
            selected_count = len(selected_worksheet_ids)
            
            if batch_actions_bar_ref["value"]:
                batch_actions_bar_ref["value"].visible = selected_count > 0
                if selected_count > 0:
                    # Update the bar content
                    batch_actions_bar_ref["value"].content = _create_batch_actions_bar_content()
                page.update()
        
        def _create_batch_actions_bar_content():
            """Create batch actions bar content"""
            selected_count = len(selected_worksheet_ids)
            
            def on_batch_delete():
                """Delete selected worksheets"""
                if not selected_worksheet_ids:
                    return
                
                from ui.components.confirmation_dialogs import create_delete_confirmation_dialog
                
                def confirm_delete():
                    try:
                        deleted_count = 0
                        for worksheet_id in list(selected_worksheet_ids):
                            try:
                                worksheet_service.delete_worksheet(worksheet_id)
                                deleted_count += 1
                            except Exception as e:
                                print(f"Error deleting worksheet {worksheet_id}: {e}")
                        
                        selected_worksheet_ids.clear()
                        # Reload worksheets
                        all_worksheets = get_worksheets()
                        pagination_controller.update_total_items(len(all_worksheets))
                        offset = pagination_controller.start_index
                        limit = pagination_controller.items_per_page
                        worksheets = all_worksheets[offset:offset + limit]
                        ws_list_items = self._build_grouped_worksheet_list(worksheets, on_worksheet_selected, page, selected_worksheet_ids, _on_worksheet_selection_change)
                        ws_list.controls.clear()
                        ws_list.controls.extend(ws_list_items)
                        _update_batch_actions_bar()
                        header_text.value = f"{len(worksheets)} munkalap"
                        page.snack_bar = ft.SnackBar(
                            content=ft.Text(f"{deleted_count} {translator.get_text('worksheets.worksheet')} törölve"),
                            bgcolor=DesignSystem.SUCCESS,
                        )
                        page.snack_bar.open = True
                        page.update()
                    except Exception as e:
                        page.snack_bar = ft.SnackBar(
                            content=ft.Text(f"Hiba: {e}"),
                            bgcolor=DesignSystem.ERROR,
                        )
                        page.snack_bar.open = True
                        page.update()
                
                dialog = create_delete_confirmation_dialog(
                    page=page,
                    entity_name=f"{selected_count} {translator.get_text('worksheets.worksheet')}",
                    on_confirm=confirm_delete,
                )
                page.dialog = dialog
                dialog.open = True
                page.update()
            
            def on_batch_export():
                """Export selected worksheets"""
                if not selected_worksheet_ids:
                    return
                
                try:
                    from services.export_service import ExportService
                    worksheets_list = [worksheet_service.get_worksheet(ws_id) for ws_id in selected_worksheet_ids]
                    
                    # Convert worksheets to dict format
                    worksheets_data = []
                    for ws in worksheets_list:
                        if ws:
                            worksheets_data.append({
                                "ID": ws.id,
                                "Cím": ws.title or "",
                                "Gép": ws.machine.name if ws.machine else "",
                                "Státusz": ws.status or "",
                                "Hibabejelentés ideje": ws.breakdown_time.strftime("%Y-%m-%d %H:%M") if ws.breakdown_time else "",
                                "Létrehozva": ws.created_at.strftime("%Y-%m-%d") if ws.created_at else "",
                            })
                    
                    # Export to CSV
                    csv_data = ExportService.export_to_csv(
                        data=worksheets_data,
                        headers=["ID", "Cím", "Gép", "Státusz", "Hibabejelentés ideje", "Létrehozva"],
                    )
                    
                    # Save file
                    filename = f"worksheets_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                    file_path = Path.home() / "Downloads" / filename
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    file_path.write_bytes(csv_data)
                    
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"{len(worksheets_list)} {translator.get_text('worksheets.worksheet')} exportálva: {file_path}"),
                        bgcolor=DesignSystem.SUCCESS,
                    )
                    page.snack_bar.open = True
                    page.update()
                except Exception as e:
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"Export hiba: {e}"),
                        bgcolor=DesignSystem.ERROR,
                    )
                    page.snack_bar.open = True
                    page.update()
            
            # Create wrapper functions to avoid lambda closure issues in PyInstaller
            def handle_batch_delete(e):
                on_batch_delete()
            
            def handle_batch_export(e):
                on_batch_export()
            
            actions = [
                {
                    "label": translator.get_text("common.buttons.delete"),
                    "icon": ft.Icons.DELETE,
                    "on_click": handle_batch_delete,
                    "color": DesignSystem.ERROR,
                },
                {
                    "label": translator.get_text("common.buttons.export"),
                    "icon": ft.Icons.DOWNLOAD,
                    "on_click": handle_batch_export,
                    "color": DesignSystem.BLUE_500,
                },
            ]
            
            return create_batch_actions_bar(
                selected_count=selected_count,
                actions=actions,
                on_clear_selection=_clear_selection,
                page=page,
            )
        
        # Create batch actions bar container
        batch_actions_bar_container = ft.Container(
            content=_create_batch_actions_bar_content(),
            visible=False,
        )
        batch_actions_bar_ref["value"] = batch_actions_bar_container
        
        # Set up pagination controller callback
        def on_page_change(page_num):
            # page_num is 1-based from PaginationController
            # Convert to 0-based
            offset = (page_num - 1) * pagination_controller.items_per_page
            limit = pagination_controller.items_per_page
            worksheets = all_worksheets[offset:offset + limit]
            
            # Rebuild list
            ws_list_items = self._build_grouped_worksheet_list(worksheets, on_worksheet_selected, page, selected_worksheet_ids, _on_worksheet_selection_change)
            ws_list.controls.clear()
            ws_list.controls.extend(ws_list_items)
            header_text.value = f"{len(worksheets)} munkalap"
            page.update()
        
        pagination_controller.on_page_change = on_page_change

        # Build grouped list
        ws_list_items = self._build_grouped_worksheet_list(worksheets, on_worksheet_selected, page, selected_worksheet_ids, _on_worksheet_selection_change)
        ws_list = ft.ListView(ws_list_items, expand=True, spacing=12)
        
        # Header text (must be defined before callback)
        header_text = ft.Text(
            f"{len(worksheets)} munkalap",
            size=13,
            color="#64748B",
        )

        def on_toggle_closed(e):
            try:
                self.show_closed = e.control.value
                print(f"[UI] Toggle closed: {self.show_closed}")
                # Reload worksheets based on filter
                all_worksheets = get_worksheets()
                pagination_controller.update_total_items(len(all_worksheets))
                offset = pagination_controller.start_index
                limit = pagination_controller.items_per_page
                worksheets = all_worksheets[offset:offset + limit]
                print(f"[UI] Loaded {len(worksheets)} worksheets (show_closed={self.show_closed})")
                # Rebuild list items
                new_list_items = self._build_grouped_worksheet_list(worksheets, on_worksheet_selected, page, selected_worksheet_ids, _on_worksheet_selection_change)
                # Update ListView controls
                ws_list.controls.clear()
                ws_list.controls.extend(new_list_items)
                # Update header count
                header_text.value = f"{len(worksheets)} munkalap"
                print(f"[UI] Updated list with {len(new_list_items)} items")
                page.update()
            except Exception as ex:
                print(f"[UI] Error toggling closed filter: {ex}")
                import traceback
                traceback.print_exc()
                page.snack_bar = ft.SnackBar(ft.Text(f"{translator.get_text('common.messages.error_occurred')}: {str(ex)}"))
                page.snack_bar.open = True
                page.update()
        
        # Create pagination controls
        pagination_controls = create_pagination_controls(
            controller=pagination_controller,
            show_page_numbers=True,
            max_page_buttons=7,
        )
        
        # Create items per page selector
        items_per_page_selector = create_items_per_page_selector(
            controller=pagination_controller,
            options=[10, 25, 50, 100],
        )
        
        # Wrap pagination controls in a container
        pagination_row = ft.Row([
            pagination_controls,
            ft.Container(width=DesignSystem.SPACING_4),
            items_per_page_selector,
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=DesignSystem.SPACING_2) if pagination_controller.total_pages > 1 else ft.Container()
        
        # Select all checkbox
        select_all_checkbox = ft.Checkbox(
            value=False,
            on_change=lambda e: (_select_all() if e.control.value else _clear_selection()),
            tooltip=translator.get_text("common.select_all") if hasattr(translator, 'get_text') else "Select All",
        )
        
        # Modern header
        header = ft.Container(
            content=ft.Row([
                select_all_checkbox,
                ft.Container(width=8),
                ft.Container(
                    content=ft.Icon(
                        ft.Icons.ASSIGNMENT if hasattr(ft.Icons, 'ASSIGNMENT') else ft.Icons.DESCRIPTION,
                        size=28,
                        color="#6366F1",
                    ),
                    padding=10,
                    bgcolor="#E0E7FF",
                    border_radius=10,
                ),
                ft.Column([
                    ft.Text(
                        translator.get_text("worksheets.title"),
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=DesignSystem.TEXT_PRIMARY,
                    ),
                    header_text,
                ], spacing=2, tight=True),
                ft.Column(expand=True),
                ft.Switch(
                    label="Lezárt munkalapok",
                    value=self.show_closed,
                    on_change=on_toggle_closed,
                ),
                ft.Container(width=16),
                ft.ElevatedButton(
                    translator.get_text("worksheets.create_new"),
                    icon=ft.Icons.ADD,
                    on_click=lambda e: create_new_worksheet(),  # This is fine, no closure issue
                    bgcolor="#6366F1",
                    color="#FFFFFF",
                    height=44,
                ),
            ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=20,
            bgcolor="#FFFFFF",
            border_radius=12,
        )

        return ft.Column([
            header,
            batch_actions_bar_container,
            ft.Container(height=16),
            pagination_row,
            ws_list,
            pagination_row,
        ], spacing=0, expand=True, scroll=ft.ScrollMode.AUTO)

    def _worksheet_detail_view(self, page: ft.Page):
        """Modern detail view of a single worksheet"""
        ws = self.current_worksheet
        
        # Reload worksheet with parts to ensure they are loaded
        if ws:
            try:
                ws = worksheet_service.get_worksheet(ws.id)
                self.current_worksheet = ws
            except Exception as ex:
                logger.warning(f"Error reloading worksheet with parts: {ex}")
        
        # Initialize autosave service
        autosave_service = get_autosave_service()
        user_id = get_current_user_id()
        autosave_timer_ref = {"value": None}
        autosave_enabled = True
        
        save_picker_result = {"path": None}
        pending_save_callback = {"fn": None}

        def _on_save_result(e: ft.FilePickerResultEvent):
            dest_path = getattr(e, "path", None)
            save_picker_result["path"] = dest_path
            cb = pending_save_callback.get("fn")
            if cb and dest_path:
                cb(dest_path)
            pending_save_callback["fn"] = None

        file_picker = ft.FilePicker(on_result=_on_save_result)
        page.overlay.append(file_picker)
        
        def open_add_part_dialog():
            """Open dialog to add part to worksheet with storage location selection"""
            from database.session_manager import SessionLocal
            from database.models import Part
            from services.storage_service import get_part_locations, get_storage_location_path
            from services.inventory_service import get_inventory_level
            from database.models import InventoryLevel
            
            session = SessionLocal()
            try:
                # Get compatible parts for the machine
                machine_id = ws.machine_id if ws else None
                if machine_id:
                    # Get parts compatible with this machine
                    compatible_parts = session.query(Part).join(
                        Part.compatible_machines
                    ).filter_by(id=machine_id).all()
                else:
                    # If no machine, show all parts
                    compatible_parts = session.query(Part).all()
                
                # Also get all parts as fallback
                all_parts = session.query(Part).all()
                if not compatible_parts:
                    compatible_parts = all_parts
            finally:
                session.close()
            
            # Part dropdown
            part_dropdown = create_modern_dropdown(
                label=translator.get_text("inventory.part"),
                options=[ft.dropdown.Option(str(p.id), f"{p.sku} - {p.name}") for p in compatible_parts],
            )
            
            # Quantity field
            quantity_field = create_modern_text_field(
                label=translator.get_text("inventory.quantity"),
                keyboard_type=ft.KeyboardType.NUMBER,
                value="1",
            )
            
            # Storage location dropdown (will be populated when part is selected)
            storage_location_dropdown = create_modern_dropdown(
                label=translator.get_text("storage.location") or "Raktárhely",
                options=[],
            )
            
            # Stock info
            stock_info_text = ft.Text("", size=12, color=DesignSystem.TEXT_SECONDARY)
            
            def update_part_info(part_id_str):
                """Update storage locations and stock info when part is selected"""
                if not part_id_str:
                    storage_location_dropdown.options = []
                    storage_location_dropdown.value = None
                    stock_info_text.value = ""
                    page.update()
                    return
                
                try:
                    part_id = int(part_id_str)
                    session = SessionLocal()
                    try:
                        # Get storage locations for this part
                        part_locations = get_part_locations(part_id, session)
                        
                        # Build dropdown options
                        location_options = []
                        for pl in part_locations:
                            location_path = get_storage_location_path(pl['location_id'], session)
                            location_options.append(
                                ft.dropdown.Option(
                                    str(pl['location_id']),
                                    f"{location_path} ({pl['quantity']} db)"
                                )
                            )
                        
                        storage_location_dropdown.options = location_options
                        if location_options:
                            storage_location_dropdown.value = str(location_options[0].key)
                        
                        # Get stock info
                        inv_level = session.query(InventoryLevel).filter_by(part_id=part_id).first()
                        stock_qty = inv_level.quantity_on_hand if inv_level else 0
                        stock_info_text.value = f"{translator.get_text('inventory.on_hand') or 'Készleten'}: {stock_qty} db"
                    finally:
                        session.close()
                    
                    page.update()
                except Exception as e:
                    logger.error(f"Error updating part info: {e}")
            
            part_dropdown.on_change = lambda e: update_part_info(e.control.value)
            
            def submit(e):
                try:
                    if not part_dropdown.value:
                        raise ValueError(translator.get_text("common.messages.required_field"))
                    if not quantity_field.value:
                        raise ValueError(translator.get_text("common.messages.required_field"))
                    
                    part_id = int(part_dropdown.value)
                    quantity = int(quantity_field.value)
                    
                    if quantity <= 0:
                        raise ValueError(translator.get_text("storage.quantity_must_be_positive") or "A mennyiségnek pozitívnak kell lennie")
                    
                    storage_location_id = None
                    if storage_location_dropdown.value:
                        storage_location_id = int(storage_location_dropdown.value)
                    
                    # Get part to get current price
                    session = SessionLocal()
                    try:
                        part = session.query(Part).filter_by(id=part_id).first()
                        if not part:
                            raise ValueError("Alkatrész nem található")
                        
                        worksheet_service.add_part_to_worksheet(
                            worksheet_id=ws.id,
                            part_id=part_id,
                            quantity_used=quantity,
                            unit_cost_at_time=part.buy_price or 0.0,
                            user_id=get_current_user_id(),
                            storage_location_id=storage_location_id,
                        )
                    finally:
                        session.close()
                    
                    # Close dialog
                    try:
                        page.close(dialog)
                    except:
                        dialog.open = False
                        page.dialog = None
                        page.update()
                    
                    # Refresh worksheet detail view by reloading
                    self.current_worksheet = worksheet_service.get_worksheet(ws.id)
                    # Reload the view
                    page.views[-1].controls[0] = self._worksheet_detail_view(page)
                    page.update()
                    
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text(translator.get_text("worksheets.part_added") or "Alkatrész hozzáadva"),
                        bgcolor=DesignSystem.SUCCESS,
                    )
                    page.snack_bar.open = True
                    page.update()
                except Exception as exc:
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"{translator.get_text('common.error')}: {exc}"),
                        bgcolor=DesignSystem.ERROR,
                    )
                    page.snack_bar.open = True
                    page.update()
            
            dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text(translator.get_text("worksheets.add_part") or "Alkatrész hozzáadása"),
                content=ft.Container(
                    content=ft.Column(
                        controls=[
                            part_dropdown,
                            stock_info_text,
                            quantity_field,
                            storage_location_dropdown,
                        ],
                        spacing=12,
                    ),
                    width=500,
                ),
                actions=[
                    ft.TextButton(
                        translator.get_text("common.buttons.cancel"),
                        on_click=lambda e: setattr(dialog, 'open', False) or page.update(),
                    ),
                    ft.ElevatedButton(
                        translator.get_text("common.buttons.add"),
                        on_click=submit,
                        bgcolor=DesignSystem.EMERALD_500,
                        color=DesignSystem.WHITE,
                    ),
                ],
            )
            
            try:
                page.open(dialog)
            except:
                page.dialog = dialog
                dialog.open = True
                page.update()
        
        # Parts list - ensure parts are loaded
        parts_list_items = []
        parts_list = []
        if ws:
            try:
                # Reload worksheet to ensure parts are loaded
                ws_reloaded = worksheet_service.get_worksheet(ws.id)
                parts_list = list(ws_reloaded.parts) if ws_reloaded.parts else []
            except Exception as ex:
                logger.warning(f"Error loading worksheet parts in detail view: {ex}")
                parts_list = []
        
        if parts_list:
            for part_link in parts_list:
                parts_list_items.append(
                    ft.Card(
                        elevation=0,
                        content=ft.Container(
                            padding=16,
                            border=ft.border.all(1, "#E2E8F0"),
                            border_radius=8,
                            content=ft.Row([
                                ft.Icon(ft.Icons.INVENTORY_2, size=20, color="#6366F1"),
                                ft.Column([
                                    ft.Text(
                                        part_link.part.name if part_link.part else "-",
                                        size=14,
                                        weight=ft.FontWeight.W_600,
                                        color=DesignSystem.TEXT_PRIMARY,
                                    ),
                                    ft.Text(
                                        f"{translator.get_text('worksheets.quantity_used')}: {part_link.quantity_used}",
                                        size=12,
                                        color=DesignSystem.TEXT_SECONDARY,
                                    ),
                                ], spacing=2, tight=True, expand=True),
                            ], alignment=ft.MainAxisAlignment.START),
                        ),
                    )
                )
        else:
            parts_list_items.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.INVENTORY_2, size=48, color="#94A3B8"),
                        ft.Text(
                            translator.get_text("common.messages.no_data"),
                            size=14,
                            color=DesignSystem.TEXT_SECONDARY,
                        ),
                    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                    padding=40,
                )
            )

        # Status dropdown
        status_options = [
            ft.dropdown.Option(key="Open", text=translator.get_text("worksheets.status_open")),
            ft.dropdown.Option(key="Waiting for Parts", text=translator.get_text("worksheets.status_waiting")),
            ft.dropdown.Option(key="Closed", text=translator.get_text("worksheets.status_closed")),
        ]

        status_label_to_key = {
            translator.get_text("worksheets.status_open"): "Open",
            translator.get_text("worksheets.status_waiting"): "Waiting for Parts",
            translator.get_text("worksheets.status_closed"): "Closed",
        }

        repair_value = ""
        if ws.repair_finished_time:
            repair_value = ws.repair_finished_time.strftime("%Y-%m-%d %H:%M")
        elif ws.status == "Closed":
            repair_value = datetime.now().strftime("%Y-%m-%d %H:%M")

        repair_finished_field = ft.TextField(
            label=translator.get_text("worksheets.repair_finished_time"),
            hint_text="YYYY-MM-DD HH:MM",
            value=repair_value,
            visible=True,
            disabled=ws.status != "Closed",
            border_radius=8,
        )

        def _compute_downtime_value():
            try:
                if not ws.breakdown_time:
                    return "—"
                if not repair_finished_field.value:
                    return "—"
                breakdown_dt = ws.breakdown_time
                repair_dt = datetime.strptime(repair_finished_field.value, "%Y-%m-%d %H:%M")
                if (breakdown_dt.tzinfo is None) != (repair_dt.tzinfo is None):
                    if breakdown_dt.tzinfo is not None:
                        breakdown_dt = breakdown_dt.replace(tzinfo=None)
                    else:
                        repair_dt = repair_dt.replace(tzinfo=None)
                delta_hours = (repair_dt - breakdown_dt).total_seconds() / 3600
                return f"{delta_hours:.2f}h"
            except Exception:
                return "—"

        def on_status_change(e):
            new_status = e.control.value
            repair_finished_field.disabled = (new_status != "Closed")
            if new_status == "Closed" and not repair_finished_field.value:
                repair_finished_field.value = datetime.now().strftime("%Y-%m-%d %H:%M")
            downtime_field.value = _compute_downtime_value()
            page.update()

        status_field = ft.Dropdown(
            label=translator.get_text("worksheets.status"),
            options=status_options,
            value=ws.status,
            on_change=on_status_change,
            border_radius=8,
        )

        def close_worksheet():
            try:
                print("[UI] close_worksheet click", ws.id)
                repair_finished_time = None
                if repair_finished_field.value:
                    repair_finished_time = datetime.strptime(repair_finished_field.value, "%Y-%m-%d %H:%M")
                
                target_status = status_field.value or "Closed"
                if target_status not in {"Open", "Waiting for Parts", "Closed"}:
                    target_status = status_label_to_key.get(target_status, target_status)
                
                # Validate fault_cause if closing worksheet (MSZ EN 13460 requirement)
                if target_status == "Closed":
                    if not fault_cause_field.value or not fault_cause_field.value.strip():
                        page.snack_bar = ft.SnackBar(
                            ft.Text(translator.get_text("common.messages.fault_cause_required")),
                            bgcolor=DesignSystem.ERROR
                        )
                        page.snack_bar.open = True
                        page.update()
                        return
                
                # Update notes first if provided
                if notes_field.value:
                    worksheet_service.update_notes(ws.id, notes_field.value)
                
                # Update fault_cause (required for Closed status, save it before status update)
                if fault_cause_field.value:
                    from database.session_manager import SessionLocal
                    from database.models import Worksheet
                    session = SessionLocal()
                    try:
                        ws_db = session.query(Worksheet).filter_by(id=ws.id).first()
                        if ws_db:
                            ws_db.fault_cause = fault_cause_field.value.strip()
                            session.commit()
                    finally:
                        session.close()
                
                # Update status (this will also validate and calculate downtime)
                ws_updated = worksheet_service.update_worksheet_status(ws.id, target_status, repair_finished_time=repair_finished_time)

                if ws_updated and ws_updated.total_downtime_hours is not None:
                    downtime_field.value = f"{ws_updated.total_downtime_hours:.2f}h"

                downtime_txt = ""
                if ws_updated and ws_updated.total_downtime_hours is not None:
                    downtime_txt = f" (downtime: {ws_updated.total_downtime_hours:.2f}h)"
                page.snack_bar = ft.SnackBar(
                    ft.Text(translator.get_text("success_messages.updated") + downtime_txt)
                )
                page.snack_bar.open = True
                self.mode = "list"
                page.go("/worksheets")
            except Exception as ex:
                print("[UI] close_worksheet error", ex)
                import traceback
                traceback.print_exc()
                page.snack_bar = ft.SnackBar(ft.Text(f"{translator.get_text('common.messages.error_occurred')}: {str(ex)}"))
                page.snack_bar.open = True
            page.update()

        def download_pdf():
            try:
                import os
                from pathlib import Path
                
                worksheet_id = ws.id
                print(f"[UI] download_docx click, worksheet_id={worksheet_id}")
                ctx = get_app_context()
                generated_by = ctx.username or "system"
                
                # Generate filename
                filename = f"worksheet_{worksheet_id}"
                try:
                    if ws.closed_at and ws.assigned_user:
                        closed_date = ws.closed_at.strftime("%Y-%m-%d")
                        username = ws.assigned_user.username
                        filename = f"worksheet_{worksheet_id}_{closed_date}_{username}"
                    elif ws.closed_at:
                        closed_date = ws.closed_at.strftime("%Y-%m-%d")
                        filename = f"worksheet_{worksheet_id}_{closed_date}"
                except Exception as e:
                    print(f"[UI] Error building filename: {e}")
                
                # Use Downloads folder or generated_pdfs folder
                downloads_path = Path.home() / "Downloads"
                if not downloads_path.exists():
                    downloads_path = Path("generated_pdfs")
                    downloads_path.mkdir(exist_ok=True)
                
                output_path = downloads_path / f"{filename}.docx"
                
                # Show loading message
                page.snack_bar = ft.SnackBar(ft.Text(translator.get_text("worksheets.document_generating")))
                page.snack_bar.open = True
                page.update()
                
                try:
                    print(f"[UI] Generating DOCX for worksheet {worksheet_id} to {output_path}")
                    docx_path = pdf_service.generate_worksheet_pdf(
                        worksheet_id, 
                        generated_by=generated_by, 
                        output_path=str(output_path)
                    )
                    print(f"[UI] DOCX generated successfully: {docx_path}")
                    
                    # Open DOCX file
                    if os.path.exists(docx_path):
                        os.startfile(docx_path)
                        page.snack_bar = ft.SnackBar(ft.Text(f"{translator.get_text('worksheets.export_pdf')} {translator.get_text('common.messages.operation_successful')}: {docx_path}"))
                    else:
                        page.snack_bar = ft.SnackBar(ft.Text(f"{translator.get_text('worksheets.export_pdf')} {translator.get_text('common.messages.operation_successful')}: {docx_path}"))
                    page.snack_bar.open = True
                except Exception as gen_ex:
                    print(f"[UI] DOCX generation error: {gen_ex}")
                    import traceback
                    traceback.print_exc()
                    page.snack_bar = ft.SnackBar(ft.Text(f"Hiba: {str(gen_ex)}"))
                    page.snack_bar.open = True
                finally:
                    page.update()
            except Exception as ex:
                print(f"[UI] download_docx error: {ex}")
                import traceback
                traceback.print_exc()
                page.snack_bar = ft.SnackBar(ft.Text(f"{translator.get_text('common.messages.error_occurred')}: {str(ex)}"))
                page.snack_bar.open = True
                page.update()
        
        def download_work_request():
            """Download work request for this worksheet if available"""
            work_request_path = worksheet_service.get_work_request_for_worksheet(ws.id)
            if not work_request_path:
                page.snack_bar = ft.SnackBar(ft.Text(translator.get_text("worksheets.work_request_not_found")))
                page.snack_bar.open = True
                page.update()
                return
            
            try:
                import os
                import shutil
                from pathlib import Path
                
                # Generate filename
                filename = f"work_request_{ws.id}"
                if ws.closed_at:
                    closed_date = ws.closed_at.strftime("%Y-%m-%d")
                    filename = f"work_request_{ws.id}_{closed_date}"
                
                # Use Downloads folder or generated_pdfs folder
                downloads_path = Path.home() / "Downloads"
                if not downloads_path.exists():
                    downloads_path = Path("generated_pdfs")
                    downloads_path.mkdir(exist_ok=True)
                
                output_path = downloads_path / f"{filename}.docx"
                
                # Copy work request to downloads
                shutil.copy2(work_request_path, output_path)
                
                # Open DOCX file
                if os.path.exists(output_path):
                    os.startfile(output_path)
                    page.snack_bar = ft.SnackBar(ft.Text(f"{translator.get_text('preventive_maintenance.work_request')} {translator.get_text('common.buttons.download')}: {output_path}"))
                else:
                    page.snack_bar = ft.SnackBar(ft.Text(f"{translator.get_text('preventive_maintenance.work_request')} {translator.get_text('common.buttons.download')}: {output_path}"))
                page.snack_bar.open = True
                page.update()
            except Exception as ex:
                print(f"[UI] download_work_request error: {ex}")
                import traceback
                traceback.print_exc()
                page.snack_bar = ft.SnackBar(ft.Text(f"{translator.get_text('common.messages.error_occurred')}: {str(ex)}"))
                page.snack_bar.open = True
                page.update()
        
        # Check if work request is available
        work_request_available = worksheet_service.get_work_request_for_worksheet(ws.id) is not None

        def back_to_list():
            self.mode = "list"
            page.go("/worksheets")

        # Modern header
        header = ft.Container(
            content=ft.Row([
                ft.IconButton(
                    ft.Icons.ARROW_BACK,
                    on_click=lambda e: back_to_list(),
                    icon_size=24,
                ),
                ft.Container(
                    content=ft.Icon(
                        ft.Icons.ASSIGNMENT if hasattr(ft.Icons, 'ASSIGNMENT') else ft.Icons.DESCRIPTION,
                        size=28,
                        color="#6366F1",
                    ),
                    padding=10,
                    bgcolor="#E0E7FF",
                    border_radius=10,
                ),
                ft.Column([
                    ft.Text(
                        ws.title if ws.title else f"{translator.get_text('worksheets.worksheet')} #{ws.id}",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=DesignSystem.TEXT_PRIMARY,
                    ),
                    ft.Text(
                        ws.machine.name if ws.machine else "-",
                        size=14,
                        color=DesignSystem.TEXT_SECONDARY,
                    ),
                ], spacing=2, tight=True),
            ], alignment=ft.MainAxisAlignment.START),
            padding=20,
            bgcolor="#FFFFFF",
            border_radius=12,
        )

        # Form section
        form_section = ft.Card(
            elevation=0,
            content=ft.Container(
                padding=24,
                border=ft.border.all(1, "#E2E8F0"),
                border_radius=12,
                bgcolor="#FFFFFF",
                content=ft.Column([
                    ft.Row([
                        ft.Text(
                            translator.get_text("worksheets.machine"),
                            size=16,
                            weight=ft.FontWeight.W_600,
                            color=DesignSystem.TEXT_PRIMARY,
                        ),
                    ]),
                    ft.TextField(
                        label=translator.get_text("worksheets.machine"),
                        value=ws.machine.name if ws.machine else "-",
                        read_only=True,
                        border_radius=8,
                    ),
                    ft.TextField(
                        label=translator.get_text("worksheets.breakdown_time"),
                        value=ws.breakdown_time.strftime("%Y-%m-%d %H:%M") if ws.breakdown_time else "",
                        read_only=True,
                        border_radius=8,
                    ),
                    repair_finished_field,
                    downtime_field := ft.TextField(
                        label=translator.get_text("worksheets.downtime"),
                        value=f"{ws.total_downtime_hours:.2f}h" if ws.total_downtime_hours is not None else "—",
                        read_only=True,
                        border_radius=8,
                    ),
                    status_field,
                    fault_cause_field := ft.TextField(
                        label=translator.get_text("worksheets.fault_cause_label"),
                        hint_text=translator.get_text("worksheets.fault_cause_hint"),
                        value=ws.fault_cause or "" if hasattr(ws, 'fault_cause') else "",
                        multiline=True,
                        min_lines=2,
                        border_radius=8,
                    ),
                    notes_field := ft.TextField(
                        label=translator.get_text("worksheets.notes"),
                        value=ws.notes or "",
                        multiline=True,
                        min_lines=3,
                        border_radius=8,
                    ),
                ], spacing=16),
            ),
        )
        
        # Load draft if exists
        if ws and user_id:
            draft = autosave_service.load_draft("worksheet", user_id, entity_id=ws.id)
            if draft and draft.get("form_data"):
                form_data = draft.get("form_data", {})
                if "status" in form_data and form_data["status"]:
                    status_field.value = form_data["status"]
                if "fault_cause" in form_data and form_data["fault_cause"]:
                    fault_cause_field.value = form_data["fault_cause"]
                if "notes" in form_data and form_data["notes"]:
                    notes_field.value = form_data["notes"]
                if "repair_finished" in form_data and form_data["repair_finished"]:
                    repair_finished_field.value = form_data["repair_finished"]
        
        # Auto-save function
        def save_draft():
            """Save current form state as draft"""
            if not autosave_enabled or not ws or not user_id:
                return
            
            try:
                form_data = {
                    "status": status_field.value or "",
                    "fault_cause": fault_cause_field.value or "",
                    "notes": notes_field.value or "",
                    "repair_finished": repair_finished_field.value or "",
                }
                
                autosave_service.save_draft(
                    entity_type="worksheet",
                    form_data=form_data,
                    user_id=user_id,
                    entity_id=ws.id,
                )
                logger.debug(f"Auto-saved draft for worksheet {ws.id}")
            except Exception as e:
                logger.error(f"Error auto-saving draft: {e}")
        
        # Auto-save on field changes
        def on_field_change(e):
            """Handle field change and trigger auto-save"""
            if autosave_timer_ref["value"]:
                autosave_timer_ref["value"].cancel()
            
            # Schedule auto-save after 2 seconds of inactivity
            def delayed_save():
                save_draft()
            
            timer = threading.Timer(2.0, delayed_save)
            timer.daemon = True
            autosave_timer_ref["value"] = timer
            timer.start()
        
        # Attach change handlers
        status_field.on_change = lambda e: (on_status_change(e), on_field_change(e))
        fault_cause_field.on_change = on_field_change
        notes_field.on_change = on_field_change
        repair_finished_field.on_change = on_field_change
        
        # Periodic auto-save (every 30 seconds)
        def periodic_autosave():
            """Periodic auto-save timer"""
            if autosave_enabled and ws and user_id:
                save_draft()
                # Schedule next save
                timer = threading.Timer(30.0, periodic_autosave)
                timer.daemon = True
                timer.start()
        
        # Start periodic auto-save
        if ws and user_id:
            timer = threading.Timer(30.0, periodic_autosave)
            timer.daemon = True
            timer.start()
        
        # Clean up draft on successful save
        original_close_worksheet = close_worksheet
        def close_worksheet_with_cleanup():
            """Close worksheet and clean up draft"""
            try:
                original_close_worksheet()
                # Delete draft after successful save
                if ws and user_id:
                    autosave_service.delete_draft("worksheet", user_id, entity_id=ws.id)
            except Exception as e:
                logger.error(f"Error in close_worksheet_with_cleanup: {e}")
                original_close_worksheet()
        
        # Replace close_worksheet function
        close_worksheet = close_worksheet_with_cleanup

        # Parts section
        parts_section = ft.Card(
            elevation=0,
            content=ft.Container(
                padding=24,
                border=ft.border.all(1, "#E2E8F0"),
                border_radius=12,
                bgcolor="#FFFFFF",
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.INVENTORY_2, size=20, color="#6366F1"),
                        ft.Text(
                            translator.get_text("worksheets.parts_used"),
                            size=16,
                            weight=ft.FontWeight.W_600,
                            color=DesignSystem.TEXT_PRIMARY,
                        ),
                        ft.Container(expand=True),
                        create_modern_button(
                            text="+ " + (translator.get_text("worksheets.add_part") or "Alkatrész hozzáadása"),
                            icon=ft.Icons.ADD,
                            on_click=lambda e: open_add_part_dialog(),  # This is fine, no closure issue
                            bgcolor=DesignSystem.EMERALD_500,
                            color=DesignSystem.WHITE,
                            height=36,
                        ),
                    ], spacing=8),
                    ft.Container(height=12),
                    ft.ListView(parts_list_items, height=200, spacing=8),
                ], spacing=0),
            ),
        )

        # Create wrapper function to avoid lambda closure issues in PyInstaller
        def handle_close_worksheet(e):
            close_worksheet()
        
        # Create wrapper functions for other buttons
        def handle_download_pdf(e):
            download_pdf()
        
        def handle_download_work_request(e):
            download_work_request()
        
        def handle_back_to_list(e):
            back_to_list()

        return ft.Column([
            header,
            ft.Container(height=16),
            form_section,
            ft.Container(height=16),
            parts_section,
            ft.Container(height=16),
            ft.Row([
                ft.ElevatedButton(
                    translator.get_text("worksheets.close_worksheet"),
                    icon=ft.Icons.CHECK_CIRCLE if hasattr(ft.Icons, 'CHECK_CIRCLE') else ft.Icons.CHECK,
                    on_click=handle_close_worksheet,
                    bgcolor=DesignSystem.SUCCESS,
                    color="#FFFFFF",
                    height=44,
                ),
                ft.ElevatedButton(
                    translator.get_text("worksheets.export_pdf"),
                    icon=ft.Icons.DOWNLOAD if hasattr(ft.Icons, 'DOWNLOAD') else ft.Icons.FILE_DOWNLOAD,
                    on_click=lambda e: download_pdf(),
                    bgcolor="#6366F1",
                    color="#FFFFFF",
                    height=44,
                ),
                ft.ElevatedButton(
                    translator.get_text("preventive_maintenance.work_request"),
                    icon=ft.Icons.DESCRIPTION if hasattr(ft.Icons, 'DESCRIPTION') else ft.Icons.ASSIGNMENT,
                    on_click=lambda e: download_work_request(),
                    bgcolor="#F59E0B",
                    color="#FFFFFF",
                    height=44,
                    visible=work_request_available,
                ) if work_request_available else ft.Container(width=0, height=0),
                ft.Column(expand=True),
                ft.TextButton(
                    translator.get_text("common.buttons.cancel"),
                    on_click=lambda e: back_to_list(),
                ),
            ]),
        ], spacing=0, expand=True, scroll=ft.ScrollMode.AUTO)

    def _create_worksheet_view(self, page: ft.Page):
        """Modern create new worksheet view"""
        try:
            print("[UI] enter _create_worksheet_view")
            machines = asset_service.list_machines()
            print("[UI] machines count", len(machines))
            machine_options = [
                ft.dropdown.Option(text=m.name, key=str(m.id)) for m in machines
            ]

            if not machine_options:
                def back_to_list():
                    self.mode = "list"
                    page.go("/worksheets")

                return ft.Column([
                    ft.Container(
                        content=ft.Row([
                            ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: back_to_list()),
                            ft.Text(
                                translator.get_text("worksheets.create_new"),
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color=DesignSystem.TEXT_PRIMARY,
                            ),
                        ]),
                        padding=20,
                    ),
                    ft.Card(
                        elevation=0,
                        content=ft.Container(
                            padding=40,
                            border=ft.border.all(1, "#E2E8F0"),
                            border_radius=12,
                            bgcolor="#FFFFFF",
                            content=ft.Column([
                                ft.Icon(ft.Icons.FACTORY, size=64, color="#94A3B8"),
                                ft.Text(
                                    translator.get_text("empty_states.no_machines"),
                                    size=16,
                                    color=DesignSystem.TEXT_SECONDARY,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                                ft.Container(height=20),
                                ft.TextButton(
                                    translator.get_text("common.buttons.cancel"),
                                    on_click=lambda e: back_to_list(),
                                ),
                            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
                        ),
                    ),
                ], spacing=16, expand=True, scroll=ft.ScrollMode.AUTO)

            machine_dropdown = ft.Dropdown(
                label=translator.get_text("worksheets.machine"),
                options=machine_options,
                value=str(machines[0].id) if machines else None,
                border_radius=8,
            )

            breakdown_time_field = ft.TextField(
                label=translator.get_text("worksheets.breakdown_time"),
                hint_text="YYYY-MM-DD HH:MM",
                value=datetime.now().strftime("%Y-%m-%d %H:%M"),
                border_radius=8,
            )

            def create_ws():
                try:
                    print("[UI] create_ws submit")
                    if not machine_dropdown.value:
                        page.snack_bar = ft.SnackBar(
                            ft.Text(translator.get_text("errors.validation.required_field"))
                        )
                        page.snack_bar.open = True
                        page.update()
                        return

                    machine_id = int(machine_dropdown.value)
                    breakdown_dt = None
                    if breakdown_time_field.value:
                        breakdown_dt = datetime.strptime(breakdown_time_field.value, "%Y-%m-%d %H:%M")

                    # Create worksheet - the title will be formatted automatically in create_worksheet
                    # using the format from settings
                    ctx = get_app_context()
                    
                    ws = worksheet_service.create_worksheet(
                        machine_id=machine_id,
                        assigned_to_user_id=ctx.user_id,
                        title="",  # Title will be generated from settings format
                        breakdown_time=breakdown_dt,
                    )
                    print(f"[UI] worksheet created id={ws.id if ws else 'None'}")
                    page.snack_bar = ft.SnackBar(ft.Text(translator.get_text("success_messages.created")))
                    page.snack_bar.open = True
                    self.current_worksheet = ws
                    self.mode = "detail"
                    page.go(f"/worksheets/detail/{ws.id}")

                except Exception as ex:
                    print("[UI] create_ws error", ex)
                    page.snack_bar = ft.SnackBar(ft.Text(str(ex)))
                    page.snack_bar.open = True
                    page.update()

            def back_to_list():
                self.mode = "list"
                page.go("/worksheets")

            # Modern header
            header = ft.Container(
                content=ft.Row([
                    ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: back_to_list()),
                    ft.Container(
                        content=ft.Icon(
                            ft.Icons.ADD_CIRCLE if hasattr(ft.Icons, 'ADD_CIRCLE') else ft.Icons.ADD,
                            size=28,
                            color="#6366F1",
                        ),
                        padding=10,
                        bgcolor="#E0E7FF",
                        border_radius=10,
                    ),
                    ft.Text(
                        translator.get_text("worksheets.create_new"),
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=DesignSystem.TEXT_PRIMARY,
                    ),
                ], alignment=ft.MainAxisAlignment.START),
                padding=20,
                bgcolor="#FFFFFF",
                border_radius=12,
            )

            # Form card
            form_card = ft.Card(
                elevation=0,
                content=ft.Container(
                    padding=24,
                    border=ft.border.all(1, "#E2E8F0"),
                    border_radius=12,
                    bgcolor="#FFFFFF",
                    content=ft.Column([
                        machine_dropdown,
                        breakdown_time_field,
                        ft.Container(height=20),
                        ft.Row([
                            ft.ElevatedButton(
                                translator.get_text("common.buttons.create"),
                                icon=ft.Icons.CHECK if hasattr(ft.Icons, 'CHECK') else ft.Icons.CHECK_CIRCLE,
                                on_click=lambda e: create_ws(),
                                bgcolor="#6366F1",
                                color="#FFFFFF",
                                height=44,
                            ),
                            ft.Column(expand=True),
                            ft.TextButton(
                                translator.get_text("common.buttons.cancel"),
                                on_click=lambda e: back_to_list(),
                            ),
                        ]),
                    ], spacing=16),
                ),
            )

            return ft.Column([
                header,
                ft.Container(height=16),
                form_card,
            ], spacing=0, expand=True, scroll=ft.ScrollMode.AUTO)
        except Exception as ex:
            print("[UI] create view error", ex)
            return ft.Container(content=ft.Text(f"Create view error: {ex}", color="red"), padding=20)
