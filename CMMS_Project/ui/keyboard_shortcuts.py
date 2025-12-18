"""
Keyboard shortcuts handler
"""
import flet as ft
from typing import Dict, Callable, Optional
import logging

logger = logging.getLogger(__name__)

# Shortcut definitions
SHORTCUTS: Dict[str, Dict[str, Callable]] = {
    "global": {
        "Ctrl+S": lambda page: _handle_save(page),
        "Ctrl+N": lambda page: _handle_new(page),
        "Ctrl+F": lambda page: _handle_search(page),
        "Ctrl+W": lambda page: _handle_close(page),
        "Escape": lambda page: _handle_cancel(page),
    }
}


def register_shortcuts(page: ft.Page, context: str = "global"):
    """
    Register keyboard shortcuts for page
    
    Args:
        page: Flet page
        context: Shortcut context (global, worksheet, etc.)
    """
    def on_keyboard(e: ft.KeyboardEvent):
        shortcut = _format_shortcut(e.key, e.ctrl, e.shift, e.alt)
        shortcuts = SHORTCUTS.get(context, {})
        
        if shortcut in shortcuts:
            try:
                shortcuts[shortcut](page)
            except Exception as ex:
                logger.error(f"Error handling shortcut {shortcut}: {ex}")
    
    page.on_keyboard_event = on_keyboard


def _format_shortcut(key: str, ctrl: bool, shift: bool, alt: bool) -> str:
    """Format keyboard event to shortcut string"""
    parts = []
    if ctrl:
        parts.append("Ctrl")
    if shift:
        parts.append("Shift")
    if alt:
        parts.append("Alt")
    parts.append(key)
    return "+".join(parts)


def _handle_save(page: ft.Page):
    """Handle Ctrl+S"""
    # Trigger save action if available
    if hasattr(page, '_current_save_handler'):
        page._current_save_handler()


def _handle_new(page: ft.Page):
    """Handle Ctrl+N"""
    # Trigger new action if available
    if hasattr(page, '_current_new_handler'):
        page._current_new_handler()


def _handle_search(page: ft.Page):
    """Handle Ctrl+F"""
    # Focus search field if available
    if hasattr(page, '_global_search'):
        page._global_search['field'].focus()


def _handle_close(page: ft.Page):
    """Handle Ctrl+W"""
    # Close current dialog or view
    if page.overlay and len(page.overlay) > 0:
        page.overlay.pop()
        page.update()


def _handle_cancel(page: ft.Page):
    """Handle Escape"""
    # Cancel current operation
    _handle_close(page)

