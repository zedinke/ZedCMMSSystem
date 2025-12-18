"""
Modern Card Component
Tailwind CSS-inspired modern card design with vibrant colors
"""

import flet as ft
from ui.components.modern_components import DesignSystem


def create_modern_card(
    content: ft.Control,
    title: str = None,
    subtitle: str = None,
    icon: str = None,
    color: str = None,
    elevation: int = 0,
    padding: int = 24,
    on_click=None,
) -> ft.Container:
    """
    Create a modern card component with FastAPI-inspired design
    
    Args:
        content: Main content of the card
        title: Optional title text
        subtitle: Optional subtitle text
        icon: Optional icon name
        color: Optional accent color
        elevation: Shadow elevation (0-8)
        padding: Internal padding
        on_click: Optional click handler
    """
    card_content = []
    
    # Header with icon and title
    if title or icon:
        header_items = []
        if icon:
            header_items.append(
                ft.Icon(
                    icon,
                    size=24,
                    color=color or "#10B981",
                )
            )
        if title:
            header_items.append(
                ft.Text(
                    title,
                    size=18,
                    weight=ft.FontWeight.W_600,
                    color="#111827",
                )
            )
        if subtitle:
            header_items.append(
                ft.Text(
                    subtitle,
                    size=14,
                    color="#6B7280",
                )
            )
        
        card_content.append(
            ft.Container(
                content=ft.Column(
                    header_items,
                    spacing=8,
                ) if len(header_items) > 1 else ft.Row(
                    header_items,
                    spacing=12,
                ),
                padding=ft.padding.only(bottom=16),
            )
        )
    
    # Main content
    if isinstance(content, list):
        card_content.extend(content)
    else:
        card_content.append(content)
    
    return ft.Container(
        content=ft.Column(
            card_content,
            spacing=0,
        ),
        padding=ft.padding.all(padding),
        bgcolor="#FFFFFF",
        border_radius=12,
        border=ft.border.all(1, "#E5E7EB"),
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=8 if elevation > 0 else 0,
            color="#00000010" if elevation > 0 else "transparent",
            offset=ft.Offset(0, 2),
        ),
        on_click=on_click,
    )


def create_metric_card(
    value: str,
    label: str,
    icon: str = None,
    color: str = DesignSystem.EMERALD_500,
    trend: str = None,
    trend_color: str = None,
    use_gradient: bool = False,
    gradient_colors: list = None,
) -> ft.Container:
    """
    Create a modern metric card for dashboard with Tailwind CSS styling
    
    Args:
        value: Main metric value
        label: Metric label
        icon: Optional icon name
        color: Accent color
        trend: Optional trend indicator (e.g., "+12%")
        trend_color: Color for trend indicator
        use_gradient: Whether to use gradient background
        gradient_colors: List of colors for gradient [start, end]
    """
    content_items = []
    
    if icon:
        content_items.append(
            ft.Container(
                content=ft.Icon(icon, size=24, color=color),
                padding=ft.padding.all(DesignSystem.SPACING_3),
                bgcolor=f"{color}15",
                border_radius=DesignSystem.RADIUS_LG,
            )
        )
    
    metric_column = [
        ft.Text(
            value,
            size=32,
            weight=ft.FontWeight.W_700,
            color=DesignSystem.TEXT_PRIMARY,
        ),
        ft.Text(
            label,
            size=14,
            color=DesignSystem.TEXT_SECONDARY,
        ),
    ]
    
    if trend:
        metric_column.append(
            ft.Container(
                content=ft.Text(
                    trend,
                    size=12,
                    weight=ft.FontWeight.W_600,
                    color=trend_color or color,
                ),
                padding=ft.padding.symmetric(horizontal=DesignSystem.SPACING_2, vertical=DesignSystem.SPACING_1),
                bgcolor=f"{trend_color or color}15",
                border_radius=DesignSystem.RADIUS_MD,
            )
        )
    
    content_items.append(
        ft.Column(
            metric_column,
            spacing=DesignSystem.SPACING_1,
            expand=True,
        )
    )
    
    # Gradient support
    gradient = None
    if use_gradient and gradient_colors:
        gradient = ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=gradient_colors,
        )
    
    return ft.Container(
        content=ft.Row(
            content_items,
            spacing=DesignSystem.SPACING_4,
        ),
        padding=ft.padding.all(DesignSystem.SPACING_6),
        bgcolor=DesignSystem.BG_SECONDARY if not gradient else None,
        gradient=gradient,
        border_radius=DesignSystem.RADIUS_XL,
        border=ft.border.all(1, DesignSystem.BORDER_COLOR),
        shadow=DesignSystem.SHADOW_LG,
    )


def create_tailwind_card(
    content: ft.Control,
    title: str = None,
    subtitle: str = None,
    icon: str = None,
    icon_color: str = DesignSystem.EMERALD_500,
    accent_color: str = None,
    padding: int = DesignSystem.SPACING_6,
    elevation: int = 1,
    use_gradient: bool = False,
    gradient_colors: list = None,
    border_accent: bool = False,
    on_click=None,
) -> ft.Container:
    """
    Create a Tailwind CSS-inspired card with vibrant colors and modern styling
    
    Args:
        content: Main content of the card
        title: Optional title text
        subtitle: Optional subtitle text
        icon: Optional icon name
        icon_color: Color for icon
        accent_color: Accent color for border/background
        padding: Internal padding
        elevation: Shadow elevation (0-4)
        use_gradient: Whether to use gradient background
        gradient_colors: List of colors for gradient [start, end]
        border_accent: Whether to use accent color for border
        on_click: Optional click handler
    """
    card_content = []
    
    # Header
    if title or icon:
        header_items = []
        if icon:
            header_items.append(
                ft.Container(
                    content=ft.Icon(icon, size=24, color=icon_color),
                    padding=ft.padding.all(DesignSystem.SPACING_2 + 2),
                    bgcolor=f"{icon_color}15",
                    border_radius=DesignSystem.RADIUS_LG,
                )
            )
        if title:
            title_column_items = [
                ft.Text(
                    title,
                    size=18,
                    weight=ft.FontWeight.W_600,
                    color=DesignSystem.TEXT_PRIMARY,
                ),
            ]
            if subtitle:
                title_column_items.append(
                    ft.Text(
                        subtitle,
                        size=14,
                        color=DesignSystem.TEXT_SECONDARY,
                    )
                )
            header_items.append(
                ft.Column(title_column_items, spacing=2, tight=True)
            )
        
        # Filter None values from header_items
        header_items = [item for item in header_items if item is not None]
        if header_items:
            card_content.append(
                ft.Container(
                    content=ft.Row(header_items, spacing=DesignSystem.SPACING_3),
                    padding=ft.padding.only(bottom=DesignSystem.SPACING_4),
                )
            )
    
    # Main content
    if isinstance(content, list):
        card_content.extend(content)
    elif isinstance(content, ft.Column):
        if hasattr(content, 'controls') and content.controls:
            filtered_controls = [c for c in content.controls if c is not None]
            card_content.extend(filtered_controls)
        else:
            card_content.append(content)
    else:
        card_content.append(content)
    
    # Filter None values
    card_content = [c for c in card_content if c is not None]
    
    if not card_content:
        card_content = [ft.Text("Empty content")]
    
    # Gradient support
    gradient = None
    if use_gradient and gradient_colors:
        gradient = ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=gradient_colors,
        )
    
    # Border color
    border_color = accent_color if border_accent and accent_color else DesignSystem.BORDER_COLOR
    
    shadows = [
        None,
        DesignSystem.SHADOW_SM,
        DesignSystem.SHADOW_MD,
        DesignSystem.SHADOW_LG,
        DesignSystem.SHADOW_XL,
    ]
    
    return ft.Container(
        content=ft.Column(card_content, spacing=0),
        padding=ft.padding.all(padding),
        bgcolor=DesignSystem.BG_SECONDARY if not gradient else None,
        gradient=gradient,
        border_radius=DesignSystem.RADIUS_XL,
        border=ft.border.all(2 if border_accent else 1, border_color),
        shadow=shadows[min(elevation, 4)] if elevation > 0 else None,
        on_click=on_click,
    )


def create_info_card(
    icon: str,
    title: str,
    description: str,
    action_button: ft.Control = None,
    icon_color: str = DesignSystem.BLUE_500,
    variant: str = "blue",  # blue, purple, pink, cyan, orange, emerald
) -> ft.Container:
    """
    Create an informational card with vibrant colors
    
    Args:
        icon: Icon name
        title: Card title
        description: Card description
        action_button: Optional action button
        icon_color: Color for icon
        variant: Color variant (blue, purple, pink, cyan, orange, emerald)
    """
    color_map = {
        "blue": (DesignSystem.BLUE_500, DesignSystem.BLUE_100),
        "purple": (DesignSystem.PURPLE_500, DesignSystem.PURPLE_100),
        "pink": (DesignSystem.PINK_500, DesignSystem.PINK_100),
        "cyan": (DesignSystem.CYAN_500, DesignSystem.CYAN_100),
        "orange": (DesignSystem.ORANGE_500, DesignSystem.ORANGE_100),
        "emerald": (DesignSystem.EMERALD_500, DesignSystem.EMERALD_100),
        "red": (DesignSystem.RED_500, DesignSystem.RED_100),
    }
    
    primary_color, bg_color = color_map.get(variant, (DesignSystem.BLUE_500, DesignSystem.BLUE_100))
    
    content_items = [
        ft.Container(
            content=ft.Icon(icon, size=32, color=primary_color),
            padding=ft.padding.all(DesignSystem.SPACING_3),
            bgcolor=bg_color,
            border_radius=DesignSystem.RADIUS_XL,
        ),
        ft.Text(
            title,
            size=18,
            weight=ft.FontWeight.W_600,
            color=DesignSystem.TEXT_PRIMARY,
        ),
        ft.Text(
            description,
            size=14,
            color=DesignSystem.TEXT_SECONDARY,
        ),
    ]
    
    if action_button:
        content_items.append(
            ft.Container(
                content=action_button,
                padding=ft.padding.only(top=DesignSystem.SPACING_4),
            )
        )
    
    return create_tailwind_card(
        content=ft.Column(
            content_items,
            spacing=DesignSystem.SPACING_3,
        ),
        padding=DesignSystem.SPACING_6,
        icon_color=primary_color,
        accent_color=primary_color,
        border_accent=True,
        elevation=1,
    )

