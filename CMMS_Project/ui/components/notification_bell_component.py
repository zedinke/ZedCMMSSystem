"""
Notification Bell Component
Displays a bell icon with notification badge and dropdown panel for notifications
"""
import flet as ft
from typing import Optional, List
from datetime import datetime
import threading
from services.context_service import get_current_user_id
from services.notification_service import (
    get_user_notifications,
    get_unread_count,
    mark_notification_read,
    mark_all_read
)
from localization.translator import translator
from ui.components.modern_components import DesignSystem
import logging

logger = logging.getLogger(__name__)


# Compatibility for flet 0.23.2 - Icons are strings, not ft.Icons
if not hasattr(ft, 'Icons'):
    from utils.flet_icons import Icons
    ft.Icons = Icons


def create_notification_bell(page: ft.Page) -> ft.Container:
    """
    Create notification bell component with icon, badge, and dropdown panel
    
    Args:
        page: Flet page instance
    
    Returns:
        Container with notification bell component
    """
    # Badge for unread count
    badge = ft.Container(
        content=ft.Text(
            "0",
            size=10,
            weight=ft.FontWeight.BOLD,
            color="white",
        ),
        bgcolor="#EF4444",  # Red
        padding=ft.padding.symmetric(horizontal=5, vertical=2),
        border_radius=10,
        visible=False,
    )
    
    # Bell icon button - use fallback pattern like other components
    bell_icon = getattr(ft.Icons, 'NOTIFICATIONS_OUTLINED', None) or \
                getattr(ft.Icons, 'NOTIFICATIONS_ACTIVE', None) or \
                getattr(ft.Icons, 'NOTIFICATIONS_NONE', None) or \
                getattr(ft.Icons, 'NOTIFICATIONS', None) or \
                getattr(ft.Icons, 'CIRCLE_NOTIFICATIONS', None) or \
                ft.Icons.INFO
    
    bell_btn = ft.IconButton(
        icon=bell_icon,
        tooltip=translator.get_text("notifications.bell_title"),
        on_click=lambda e: _toggle_notification_panel(page),
    )
    
    # Stack to overlay badge on icon button
    bell_stack = ft.Stack(
        controls=[
            bell_btn,
            ft.Container(
                content=badge,
                top=5,
                right=5,
                width=18,
                height=18,
            ),
        ],
        width=40,
        height=40,
    )
    
    # Dropdown panel (initially hidden)
    panel = ft.Container(
        content=ft.Column(
            controls=[],
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
            height=500,  # Fixed height for scrolling
        ),
        bgcolor=DesignSystem.BG_SECONDARY,
        border=ft.border.all(1, DesignSystem.BORDER_COLOR),
        border_radius=8,
        padding=8,
        width=400,
        visible=False,
    )
    
    # Main container
    container = ft.Container(
        content=ft.Column(
            controls=[
                bell_stack,
                panel,
            ],
            spacing=4,
            tight=True,
        ),
        padding=0,
    )
    
    # Store references in page
    if not hasattr(page, '_notification_bell'):
        page._notification_bell = {
            'badge': badge,
            'bell_btn': bell_btn,
            'panel': panel,
            'container': container,
            'is_open': False,
            'refresh_timer': None,
        }
    else:
        # Update references
        page._notification_bell['badge'] = badge
        page._notification_bell['bell_btn'] = bell_btn
        page._notification_bell['panel'] = panel
        page._notification_bell['container'] = container
    
    # Initial load
    _refresh_notifications(page)
    
    # Start auto-refresh timer (30 seconds)
    _start_auto_refresh(page)
    
    return container


def _toggle_notification_panel(page: ft.Page):
    """Toggle notification panel visibility"""
    if not hasattr(page, '_notification_bell'):
        return
    
    bell_data = page._notification_bell
    bell_data['is_open'] = not bell_data['is_open']
    bell_data['panel'].visible = bell_data['is_open']
    
    if bell_data['is_open']:
        _refresh_notifications(page)
    
    page.update()


def _refresh_notifications(page: ft.Page):
    """Refresh notification count and list"""
    try:
        user_id = get_current_user_id()
        if not user_id:
            return
        
        # Get unread count
        unread_count = get_unread_count(user_id)
        
        # Update badge
        if hasattr(page, '_notification_bell'):
            bell_data = page._notification_bell
            badge = bell_data['badge']
            if unread_count > 0:
                badge.content.value = str(unread_count) if unread_count <= 99 else "99+"
                badge.visible = True
            else:
                badge.visible = False
        
        # Refresh panel if open
        if hasattr(page, '_notification_bell') and page._notification_bell.get('is_open', False):
            _update_notification_panel(page, user_id)
        
        page.update()
    except Exception as e:
        logger.error(f"Error refreshing notifications: {e}")


def _update_notification_panel(page: ft.Page, user_id: int):
    """Update notification panel content"""
    try:
        # Get notifications
        notifications = get_user_notifications(user_id, limit=20)
        
        if not hasattr(page, '_notification_bell'):
            return
        
        bell_data = page._notification_bell
        panel = bell_data['panel']
        
        # Build panel content
        controls = []
        
        # Header
        header = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text(
                        translator.get_text("notifications.bell_title"),
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=DesignSystem.TEXT_PRIMARY,
                    ),
                    ft.Container(expand=True),
                    ft.TextButton(
                        text=translator.get_text("notifications.mark_all_read"),
                        on_click=lambda e: _mark_all_read(page),
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.padding.only(bottom=8),
            border=ft.border.only(bottom=ft.BorderSide(1, DesignSystem.BORDER_COLOR)),
        )
        controls.append(header)
        
        # Notifications list
        if notifications:
            # Separate unread and read
            unread = [n for n in notifications if not n.is_read]
            read = [n for n in notifications if n.is_read]
            
            # Show unread first
            for notification in unread:
                controls.append(_create_notification_item(page, notification, is_unread=True))
            
            # Separator if both exist
            if unread and read:
                controls.append(
                    ft.Container(
                        content=ft.Divider(),
                        padding=ft.padding.symmetric(vertical=4),
                    )
                )
            
            # Show read
            for notification in read:
                controls.append(_create_notification_item(page, notification, is_unread=False))
        else:
            # Empty state
            controls.append(
                ft.Container(
                    content=ft.Text(
                        translator.get_text("notifications.no_notifications"),
                        color=DesignSystem.TEXT_SECONDARY,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    padding=20,
                    alignment=ft.alignment.center,
                )
            )
        
        # Footer - View all button
        footer = ft.Container(
            content=ft.TextButton(
                text=translator.get_text("notifications.view_all"),
                on_click=lambda e: _navigate_to_all_notifications(page),
            ),
            padding=ft.padding.only(top=8),
            border=ft.border.only(top=ft.BorderSide(1, DesignSystem.BORDER_COLOR)),
        )
        controls.append(footer)
        
        # Update panel content
        panel.content.controls = controls
        panel.content.update()
        
    except Exception as e:
        logger.error(f"Error updating notification panel: {e}")


def _create_notification_item(page: ft.Page, notification, is_unread: bool) -> ft.Container:
    """Create a single notification item in the panel"""
    # Icon based on notification type
    icon_map = {
        "info": getattr(ft.Icons, 'INFO_OUTLINED', None) or ft.Icons.INFO,
        "warning": getattr(ft.Icons, 'WARNING_AMBER_OUTLINED', None) or getattr(ft.Icons, 'WARNING', None) or ft.Icons.INFO,
        "error": getattr(ft.Icons, 'ERROR_OUTLINED', None) or getattr(ft.Icons, 'ERROR', None) or ft.Icons.INFO,
        "success": getattr(ft.Icons, 'CHECK_CIRCLE_OUTLINED', None) or getattr(ft.Icons, 'CHECK_CIRCLE', None) or ft.Icons.INFO,
    }
    icon = icon_map.get(notification.notification_type, getattr(ft.Icons, 'NOTIFICATIONS_OUTLINED', None) or ft.Icons.INFO)
    icon_color_map = {
        "info": "#3B82F6",  # Blue
        "warning": "#F59E0B",  # Amber
        "error": "#EF4444",  # Red
        "success": "#10B981",  # Green
    }
    icon_color = icon_color_map.get(notification.notification_type, DesignSystem.TEXT_SECONDARY)
    
    # Format date
    created_at = notification.created_at
    if isinstance(created_at, datetime):
        date_str = created_at.strftime("%Y-%m-%d %H:%M")
    else:
        date_str = str(created_at)
    
    # Item container
    item = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(icon, color=icon_color, size=20),
                ft.Column(
                    controls=[
                        ft.Text(
                            notification.title,
                            size=14,
                            weight=ft.FontWeight.BOLD if is_unread else ft.FontWeight.NORMAL,
                            color=DesignSystem.TEXT_PRIMARY,
                        ),
                        ft.Text(
                            notification.message,
                            size=12,
                            color=DesignSystem.TEXT_SECONDARY,
                            max_lines=2,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                        ft.Text(
                            date_str,
                            size=10,
                            color=DesignSystem.TEXT_SECONDARY,
                        ),
                    ],
                    spacing=2,
                    expand=True,
                    tight=True,
                ),
            ],
            spacing=8,
            alignment=ft.MainAxisAlignment.START,
        ),
        padding=ft.padding.all(8),
        bgcolor=DesignSystem.BG_PRIMARY if is_unread else DesignSystem.BG_SECONDARY,
        border_radius=4,
        on_click=lambda e, n=notification: _on_notification_click(page, n),
        tooltip=translator.get_text("common.click_to_view"),
    )
    
    return item


def _on_notification_click(page: ft.Page, notification):
    """Handle notification click - navigate and mark as read"""
    try:
        # Mark as read
        mark_notification_read(notification.id)
        
        # Navigate to related entity
        if notification.related_entity_type and notification.related_entity_id:
            _navigate_to_entity(page, notification.related_entity_type, notification.related_entity_id)
        
        # Refresh notifications
        _refresh_notifications(page)
        
        # Close panel
        if hasattr(page, '_notification_bell'):
            bell_data = page._notification_bell
            bell_data['is_open'] = False
            bell_data['panel'].visible = False
            page.update()
        
    except Exception as e:
        logger.error(f"Error handling notification click: {e}")


def _navigate_to_entity(page: ft.Page, entity_type: str, entity_id: int):
    """Navigate to the related entity"""
    try:
        if entity_type == "PMTask":
            # Navigate to PM screen
            page.go("/pm")
            page.update()
        elif entity_type == "Worksheet":
            # Navigate to worksheet detail
            page.go(f"/worksheets/detail/{entity_id}")
            page.update()
        else:
            logger.warning(f"Unknown entity type for navigation: {entity_type}")
    except Exception as e:
        logger.error(f"Error navigating to entity: {e}")


def _mark_all_read(page: ft.Page):
    """Mark all notifications as read"""
    try:
        user_id = get_current_user_id()
        if not user_id:
            return
        
        mark_all_read(user_id)
        _refresh_notifications(page)
    except Exception as e:
        logger.error(f"Error marking all notifications as read: {e}")


def _navigate_to_all_notifications(page: ft.Page):
    """Navigate to all notifications page (placeholder - could be implemented later)"""
    # For now, just close the panel
    if hasattr(page, '_notification_bell'):
        bell_data = page._notification_bell
        bell_data['is_open'] = False
        bell_data['panel'].visible = False
        page.update()
    
    # TODO: Navigate to dedicated notifications page when implemented
    logger.info("Navigate to all notifications page (not yet implemented)")


def _start_auto_refresh(page: ft.Page):
    """Start automatic refresh timer (30 seconds)"""
    def refresh_loop():
        while True:
            threading.Event().wait(30)  # Wait 30 seconds
            try:
                if hasattr(page, '_notification_bell'):
                    # Refresh notifications (will call page.update() inside)
                    _refresh_notifications(page)
            except Exception as e:
                logger.error(f"Error in auto-refresh: {e}")
    
    # Start refresh thread
    thread = threading.Thread(target=refresh_loop, daemon=True)
    thread.start()
    
    # Store thread reference
    if hasattr(page, '_notification_bell'):
        page._notification_bell['refresh_thread'] = thread

