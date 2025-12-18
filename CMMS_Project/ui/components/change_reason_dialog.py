"""
Dialog component for requesting change reason when modifying entities
"""
import flet as ft
from utils.localization_helper import translator
from ui.components.modern_components import DesignSystem, create_modern_text_field, create_modern_button


def show_change_reason_dialog(
    page: ft.Page,
    entity_name: str,
    entity_type: str,
    on_confirm: callable,
    on_cancel: callable = None,
) -> None:
    """
    Show a dialog to request the reason for a change.
    
    Args:
        page: Flet page instance
        entity_name: Name of the entity being modified
        entity_type: Type of entity (e.g., "Machine", "Part", "Worksheet")
        on_confirm: Callback function that receives the change reason as parameter
        on_cancel: Optional callback function for cancellation
    """
    change_reason_field = create_modern_text_field(
        label=translator.get_text("common.change_reason") if hasattr(translator, 'get_text') else "Változtatás oka / Change Reason",
        multiline=True,
        max_lines=5,
        hint_text=translator.get_text("common.change_reason_hint") if hasattr(translator, 'get_text') else "Adja meg a változtatás okát...",
        width=500,
    )
    
    error_text = ft.Text(
        color=DesignSystem.ERROR,
        size=12,
        visible=False,
    )
    
    def handle_confirm(e):
        change_reason = change_reason_field.value or ""
        
        # Validate: change reason is required
        if not change_reason.strip():
            error_text.value = translator.get_text("common.change_reason_required") if hasattr(translator, 'get_text') else "A változtatás oka kötelező! / Change reason is required!"
            error_text.visible = True
            dialog.update()
            return
        
        # Close dialog
        dialog.open = False
        page.update()
        
        # Call the confirm callback with the change reason
        on_confirm(change_reason.strip())
    
    def handle_cancel(e):
        dialog.open = False
        page.update()
        if on_cancel:
            on_cancel()
    
    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Row([
            ft.Icon(
                ft.Icons.EDIT_NOTE if hasattr(ft.Icons, 'EDIT_NOTE') else ft.Icons.EDIT,
                color=DesignSystem.INFO,
                size=24,
            ),
            ft.Text(
                translator.get_text("common.change_reason_title") if hasattr(translator, 'get_text') else "Változtatás oka / Change Reason",
                size=18,
                weight=ft.FontWeight.W_600,
                color=DesignSystem.TEXT_PRIMARY,
            ),
        ], spacing=DesignSystem.SPACING_2),
        content=ft.Container(
            content=ft.Column([
                ft.Text(
                    translator.get_text("common.change_reason_description", entity_name=entity_name, entity_type=entity_type) if hasattr(translator, 'get_text') else f"Adja meg a változtatás okát a(z) {entity_name} {entity_type} módosításához.",
                    size=12,
                    color=DesignSystem.TEXT_SECONDARY,
                ),
                ft.Container(height=DesignSystem.SPACING_2),
                change_reason_field,
                error_text,
            ], spacing=DesignSystem.SPACING_2, tight=True),
            width=550,
            padding=ft.padding.all(DesignSystem.SPACING_4),
        ),
        actions=[
            ft.TextButton(
                translator.get_text("common.buttons.cancel") if hasattr(translator, 'get_text') else "Mégse / Cancel",
                on_click=handle_cancel,
            ),
            create_modern_button(
                text=translator.get_text("common.buttons.confirm") if hasattr(translator, 'get_text') else "Megerősítés / Confirm",
                icon=ft.Icons.CHECK if hasattr(ft.Icons, 'CHECK') else ft.Icons.DONE,
                on_click=handle_confirm,
                bgcolor=DesignSystem.SUCCESS,
                color=DesignSystem.WHITE,
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        shape=ft.RoundedRectangleBorder(radius=DesignSystem.RADIUS_LG),
        bgcolor=DesignSystem.BG_SECONDARY,
    )
    
    page.dialog = dialog
    dialog.open = True
    page.update()

