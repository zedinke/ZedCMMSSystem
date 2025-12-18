"""
Reusable confirmation dialog components
"""

import flet as ft
from typing import Dict, Optional, Callable
from localization.translator import translator
from ui.components.modern_components import (
    create_modern_button,
    create_modern_card,
    DesignSystem,
)


def create_add_confirmation_dialog(
    page: ft.Page,
    title: str,
    summary_data: Dict[str, any],
    on_confirm: Callable,
    on_cancel: Optional[Callable] = None,
) -> ft.AlertDialog:
    """
    Create confirmation dialog for add operations
    
    Args:
        page: Flet page object
        title: Dialog title
        summary_data: Dictionary with summary information to display
        on_confirm: Callback function when user confirms
        on_cancel: Optional callback function when user cancels
    
    Returns:
        ft.AlertDialog: The confirmation dialog
    """
    def handle_confirm(e):
        dialog.open = False
        page.update()
        on_confirm(e)
    
    def handle_cancel(e):
        dialog.open = False
        page.update()
        if on_cancel:
            on_cancel(e)
    
    # Build summary content
    summary_items = []
    for key, value in summary_data.items():
        if value is not None and value != "":
            # Try to get localized label, fallback to key
            label = key
            try:
                label = translator.get_text(f"inventory.summary.{key}")
            except:
                try:
                    label = translator.get_text(f"assets.summary.{key}")
                except:
                    try:
                        label = translator.get_text(f"users.{key}")
                    except:
                        label = key.replace("_", " ").title()
            summary_items.append(
                ft.Row([
                    ft.Text(
                        f"{label}:",
                        size=12,
                        weight=ft.FontWeight.W_600,
                        color=DesignSystem.TEXT_PRIMARY,
                        width=150,
                    ),
                    ft.Text(
                        str(value),
                        size=12,
                        color=DesignSystem.TEXT_SECONDARY,
                        expand=True,
                    ),
                ], spacing=8)
            )
    
    summary_content = ft.Column(
        summary_items,
        spacing=8,
        scroll=ft.ScrollMode.AUTO,
    )
    
    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text(
            title,
            size=18,
            weight=ft.FontWeight.W_600,
            color=DesignSystem.TEXT_PRIMARY,
        ),
        content=ft.Container(
            content=ft.Column([
                ft.Text(
                    translator.get_text("confirmations.add.summary") if hasattr(translator, 'get_text') else "Összesítő / Summary",
                    size=14,
                    weight=ft.FontWeight.W_600,
                    color=DesignSystem.TEXT_PRIMARY,
                ),
                ft.Container(height=8),
                summary_content,
                ft.Container(height=16),
                ft.Text(
                    translator.get_text("confirmations.add.question") if hasattr(translator, 'get_text') else "Biztosan hozzá szeretné adni? / Are you sure you want to add?",
                    size=12,
                    color=DesignSystem.TEXT_SECONDARY,
                    italic=True,
                ),
            ], spacing=0),
            width=500,
            height=400,
        ),
        actions=[
            ft.TextButton(
                translator.get_text("confirmations.cancel_button") if hasattr(translator, 'get_text') else "Mégse / Cancel",
                on_click=handle_cancel,
            ),
            create_modern_button(
                text=translator.get_text("confirmations.add.confirm_button") if hasattr(translator, 'get_text') else "Igen, hozzáadás / Yes, Add",
                on_click=handle_confirm,
                bgcolor=DesignSystem.SUCCESS,
                color="#FFFFFF",
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        shape=ft.RoundedRectangleBorder(radius=DesignSystem.RADIUS_LG),
        bgcolor=DesignSystem.BG_SECONDARY,
    )
    
    return dialog


def create_delete_confirmation_dialog(
    page: ft.Page,
    title: str,
    summary_data: Dict[str, any],
    on_confirm: Callable,
    on_cancel: Optional[Callable] = None,
    warning_message: Optional[str] = None,
) -> ft.AlertDialog:
    """
    Create confirmation dialog for delete operations
    
    Args:
        page: Flet page object
        title: Dialog title
        summary_data: Dictionary with summary information to display
        on_confirm: Callback function when user confirms
        on_cancel: Optional callback function when user cancels
        warning_message: Optional additional warning message
    
    Returns:
        ft.AlertDialog: The confirmation dialog
    """
    def handle_confirm(e):
        dialog.open = False
        page.update()
        on_confirm(e)
    
    def handle_cancel(e):
        dialog.open = False
        page.update()
        if on_cancel:
            on_cancel(e)
    
    # Build summary content
    summary_items = []
    for key, value in summary_data.items():
        if value is not None and value != "":
            # Try to get localized label, fallback to key
            label = key
            try:
                label = translator.get_text(f"inventory.summary.{key}")
            except:
                try:
                    label = translator.get_text(f"assets.summary.{key}")
                except:
                    try:
                        label = translator.get_text(f"users.{key}")
                    except:
                        label = key.replace("_", " ").title()
            summary_items.append(
                ft.Row([
                    ft.Text(
                        f"{label}:",
                        size=12,
                        weight=ft.FontWeight.W_600,
                        color=DesignSystem.TEXT_PRIMARY,
                        width=150,
                    ),
                    ft.Text(
                        str(value),
                        size=12,
                        color=DesignSystem.TEXT_SECONDARY,
                        expand=True,
                    ),
                ], spacing=8)
            )
    
    summary_content = ft.Column(
        summary_items,
        spacing=8,
        scroll=ft.ScrollMode.AUTO,
    )
    
    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text(
            title,
            size=18,
            weight=ft.FontWeight.W_600,
            color=DesignSystem.ERROR,
        ),
        content=ft.Container(
            content=ft.Column([
                ft.Text(
                    translator.get_text("confirmations.delete.summary") if hasattr(translator, 'get_text') else "Összesítő / Summary",
                    size=14,
                    weight=ft.FontWeight.W_600,
                    color=DesignSystem.TEXT_PRIMARY,
                ),
                ft.Container(height=8),
                summary_content,
                ft.Container(height=16),
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.WARNING, color=DesignSystem.ERROR, size=20),
                        ft.Text(
                            translator.get_text("confirmations.delete.warning") if hasattr(translator, 'get_text') else "Ez a művelet nem visszavonható! / This action cannot be undone!",
                            size=12,
                            color=DesignSystem.ERROR,
                            weight=ft.FontWeight.W_600,
                            expand=True,
                        ),
                    ], spacing=8),
                    padding=ft.padding.all(12),
                    bgcolor=f"{DesignSystem.ERROR}15",
                    border_radius=DesignSystem.RADIUS_MD,
                ),
                ft.Text(
                    warning_message or "",
                    size=11,
                    color=DesignSystem.TEXT_SECONDARY,
                    visible=bool(warning_message),
                ) if warning_message else ft.Container(),
                ft.Container(height=8),
                ft.Text(
                    translator.get_text("confirmations.delete.question") if hasattr(translator, 'get_text') else "Biztosan törölni szeretné? / Are you sure you want to delete?",
                    size=12,
                    color=DesignSystem.TEXT_SECONDARY,
                    italic=True,
                ),
            ], spacing=0),
            width=500,
            height=450,
        ),
        actions=[
            ft.TextButton(
                translator.get_text("confirmations.cancel_button") if hasattr(translator, 'get_text') else "Mégse / Cancel",
                on_click=handle_cancel,
            ),
            create_modern_button(
                text=translator.get_text("confirmations.delete.confirm_button") if hasattr(translator, 'get_text') else "Igen, törlés / Yes, Delete",
                on_click=handle_confirm,
                bgcolor=DesignSystem.ERROR,
                color="#FFFFFF",
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        shape=ft.RoundedRectangleBorder(radius=DesignSystem.RADIUS_LG),
        bgcolor=DesignSystem.BG_SECONDARY,
    )
    
    return dialog


def create_modify_confirmation_dialog(
    page: ft.Page,
    title: str,
    entity_name: str,
    changes: Dict[str, Dict[str, any]],
    on_confirm: Callable,
    on_cancel: Optional[Callable] = None,
) -> ft.AlertDialog:
    """
    Create confirmation dialog for modify operations
    
    Args:
        page: Flet page object
        title: Dialog title
        entity_name: Name of the entity being modified
        changes: Dictionary of changes in format {"field": {"old": old_value, "new": new_value}}
        on_confirm: Callback function when user confirms
        on_cancel: Optional callback function when user cancels
    
    Returns:
        ft.AlertDialog: The confirmation dialog
    """
    def handle_confirm(e):
        dialog.open = False
        page.update()
        on_confirm(e)
    
    def handle_cancel(e):
        dialog.open = False
        page.update()
        if on_cancel:
            on_cancel(e)
    
    # Build changes content
    change_items = []
    for field, change_data in changes.items():
        old_value = change_data.get("old", "-")
        new_value = change_data.get("new", "-")
        
        # Get localized field name
        field_label = translator.get_text(f"inventory.summary.{field}") if hasattr(translator, 'get_text') else field
        
        change_items.append(
            ft.Container(
                content=ft.Row([
                    ft.Text(
                        f"{field_label}:",
                        size=12,
                        weight=ft.FontWeight.W_600,
                        color=DesignSystem.TEXT_PRIMARY,
                        width=150,
                    ),
                    ft.Text(
                        f'"{old_value}"',
                        size=12,
                        color=DesignSystem.TEXT_SECONDARY,
                    ),
                    ft.Icon(ft.Icons.ARROW_FORWARD, size=16, color=DesignSystem.TEXT_SECONDARY),
                    ft.Text(
                        f'"{new_value}"',
                        size=12,
                        color=DesignSystem.PRIMARY,
                        weight=ft.FontWeight.W_600,
                        expand=True,
                    ),
                ], spacing=8),
                padding=ft.padding.symmetric(vertical=4),
            )
        )
    
    changes_content = ft.Column(
        change_items,
        spacing=4,
        scroll=ft.ScrollMode.AUTO,
    )
    
    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text(
            title,
            size=18,
            weight=ft.FontWeight.W_600,
            color=DesignSystem.TEXT_PRIMARY,
        ),
        content=ft.Container(
            content=ft.Column([
                ft.Text(
                    entity_name,
                    size=14,
                    weight=ft.FontWeight.W_600,
                    color=DesignSystem.TEXT_PRIMARY,
                ),
                ft.Container(height=8),
                ft.Text(
                    translator.get_text("confirmations.modify.changes") if hasattr(translator, 'get_text') else "Változások / Changes",
                    size=14,
                    weight=ft.FontWeight.W_600,
                    color=DesignSystem.TEXT_PRIMARY,
                ),
                ft.Container(height=8),
                changes_content,
                ft.Container(height=16),
                ft.Text(
                    translator.get_text("confirmations.modify.question") if hasattr(translator, 'get_text') else "Biztosan módosítani szeretné? / Are you sure you want to modify?",
                    size=12,
                    color=DesignSystem.TEXT_SECONDARY,
                    italic=True,
                ),
            ], spacing=0),
            width=600,
            height=500,
        ),
        actions=[
            ft.TextButton(
                translator.get_text("confirmations.cancel_button") if hasattr(translator, 'get_text') else "Mégse / Cancel",
                on_click=handle_cancel,
            ),
            create_modern_button(
                text=translator.get_text("confirmations.modify.confirm_button") if hasattr(translator, 'get_text') else "Igen, módosítás / Yes, Modify",
                on_click=handle_confirm,
                bgcolor=DesignSystem.INFO,
                color="#FFFFFF",
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        shape=ft.RoundedRectangleBorder(radius=DesignSystem.RADIUS_LG),
        bgcolor=DesignSystem.BG_SECONDARY,
    )
    
    return dialog

