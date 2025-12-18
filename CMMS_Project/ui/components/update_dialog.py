"""
Update dialog component for displaying update information and options
"""

import flet as ft
from typing import Optional, Callable
from services.update_service import UpdateInfo
from ui.components.modern_components import DesignSystem, create_modern_button
from localization.translator import translator


def create_update_dialog(
    update_info: UpdateInfo,
    on_update_now: Callable,
    on_later: Callable,
    on_skip: Optional[Callable] = None,
) -> ft.AlertDialog:
    """
    Create update dialog with update information
    
    Args:
        update_info: UpdateInfo object with update details
        on_update_now: Callback when user clicks "Update Now"
        on_later: Callback when user clicks "Later"
        on_skip: Optional callback when user clicks "Skip" (if not critical)
    
    Returns:
        AlertDialog component
    """
    # Format release date if available
    release_date_text = ""
    if update_info.release_date:
        try:
            from datetime import datetime
            date_obj = datetime.fromisoformat(update_info.release_date.replace('Z', '+00:00'))
            release_date_text = date_obj.strftime("%Y.%m.%d")
        except:
            release_date_text = update_info.release_date[:10] if len(update_info.release_date) >= 10 else ""
    
    # Build changelog display
    changelog_content = []
    if update_info.changelog:
        # Parse markdown-style changelog
        changelog_lines = update_info.changelog.split('\n')
        for line in changelog_lines:
            line = line.strip()
            if line.startswith('##'):
                changelog_content.append(
                    ft.Text(
                        line.lstrip('#').strip(),
                        size=14,
                        weight=ft.FontWeight.BOLD,
                        color=DesignSystem.TEXT_PRIMARY,
                    )
                )
            elif line.startswith('-') or line.startswith('*'):
                changelog_content.append(
                    ft.Text(
                        f"  • {line.lstrip('-*').strip()}",
                        size=12,
                        color=DesignSystem.TEXT_SECONDARY,
                    )
                )
            elif line:
                changelog_content.append(
                    ft.Text(
                        line,
                        size=12,
                        color=DesignSystem.TEXT_SECONDARY,
                    )
                )
    
    if not changelog_content:
        changelog_content.append(
            ft.Text(
                translator.get_text("updates.no_changelog", "No changelog available"),
                size=12,
                color=DesignSystem.TEXT_SECONDARY,
                italic=True,
            )
        )
    
    # Critical update indicator
    critical_badge = None
    if update_info.critical:
        critical_badge = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.WARNING, color=DesignSystem.RED_500, size=16),
                ft.Text(
                    translator.get_text("updates.critical_update", "Critical Update"),
                    size=12,
                    weight=ft.FontWeight.BOLD,
                    color=DesignSystem.RED_500,
                ),
            ], spacing=4, tight=True),
            bgcolor=DesignSystem.RED_50,
            padding=ft.padding.symmetric(horizontal=8, vertical=4),
            border_radius=DesignSystem.RADIUS_MD,
        )
    
    # Build dialog content
    content_column = ft.Column(
        controls=[
            # Version info
            ft.Row([
                ft.Icon(ft.Icons.UPDATE, color=DesignSystem.BLUE_500, size=24),
                ft.Column([
                    ft.Text(
                        translator.get_text("updates.new_version_available", "New Version Available"),
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=DesignSystem.TEXT_PRIMARY,
                    ),
                    ft.Text(
                        f"v{update_info.version}" + (f" ({release_date_text})" if release_date_text else ""),
                        size=14,
                        color=DesignSystem.TEXT_SECONDARY,
                    ),
                ], spacing=2, tight=True, expand=True),
            ], spacing=12),
            
            # Critical badge
            critical_badge if critical_badge else ft.Container(height=0),
            
            ft.Divider(height=1, color=DesignSystem.BORDER_COLOR),
            
            # Changelog
            ft.Container(
                content=ft.Column([
                    ft.Text(
                        translator.get_text("updates.changelog", "Changes"),
                        size=14,
                        weight=ft.FontWeight.BOLD,
                        color=DesignSystem.TEXT_PRIMARY,
                    ),
                    ft.Container(
                        content=ft.Column(
                            changelog_content,
                            spacing=4,
                            tight=True,
                        ),
                        bgcolor=DesignSystem.BG_SECONDARY,
                        padding=12,
                        border_radius=DesignSystem.RADIUS_MD,
                        height=200,
                        width=500,
                    ),
                ], spacing=8, tight=True),
                padding=ft.padding.only(top=8),
            ),
        ],
        spacing=12,
        tight=False,
        width=550,
        scroll=ft.ScrollMode.AUTO,
    )
    
    # Build actions
    actions = []
    
    # Skip button (only if not critical)
    if not update_info.critical and on_skip:
        actions.append(
            ft.TextButton(
                translator.get_text("updates.skip_version", "Skip This Version"),
                on_click=lambda e: on_skip(),
                style=ft.ButtonStyle(color=DesignSystem.TEXT_SECONDARY),
            )
        )
    
    # Later button
    actions.append(
        ft.TextButton(
            translator.get_text("updates.later", "Later"),
            on_click=lambda e: on_later(),
            style=ft.ButtonStyle(color=DesignSystem.TEXT_SECONDARY),
        )
    )
    
    # Update Now button
    actions.append(
        create_modern_button(
            text=translator.get_text("updates.update_now", "Update Now"),
            icon=ft.Icons.DOWNLOAD,
            on_click=lambda e: on_update_now(),
            color=DesignSystem.BLUE_500 if not update_info.critical else DesignSystem.RED_500,
            use_gradient=False,
        )
    )
    
    # Create dialog
    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text(
            translator.get_text("updates.update_available", "Update Available"),
            size=20,
            weight=ft.FontWeight.BOLD,
            color=DesignSystem.TEXT_PRIMARY,
        ),
        content=content_column,
        actions=actions,
        actions_alignment=ft.MainAxisAlignment.END,
        shape=ft.RoundedRectangleBorder(radius=DesignSystem.RADIUS_LG),
        bgcolor=DesignSystem.BG_PRIMARY,
    )
    
    return dialog




