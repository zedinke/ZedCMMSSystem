"""
Breadcrumb navigation component
"""
import flet as ft
from typing import List, Tuple, Optional, Callable


def create_breadcrumb(
    items: List[Tuple[str, Optional[str]]],
    on_navigate: Optional[Callable[[str], None]] = None
) -> ft.Row:
    """
    Create breadcrumb navigation
    
    Args:
        items: List of (label, route) tuples
        on_navigate: Callback for navigation
    
    Returns:
        Row component with breadcrumb
    """
    breadcrumb_items = []
    
    for i, (label, route) in enumerate(items):
        if i > 0:
            breadcrumb_items.append(
                ft.Icon(ft.Icons.CHEVRON_RIGHT, size=16, color="#9CA3AF")
            )
        
        if route and on_navigate:
            breadcrumb_items.append(
                ft.TextButton(
                    label,
                    on_click=lambda e, r=route: on_navigate(r),
                    style=ft.ButtonStyle(color="#6366F1")
                )
            )
        else:
            breadcrumb_items.append(
                ft.Text(label, size=14, color="#6B7280")
            )
    
    return ft.Row(
        breadcrumb_items,
        spacing=8,
        wrap=False
    )

