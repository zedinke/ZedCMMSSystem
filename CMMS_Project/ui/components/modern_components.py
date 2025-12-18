"""
Modern UI Components Library
FastAPI-inspired modern design system components
"""

import flet as ft
from datetime import date


# Design System Constants - Tailwind CSS Inspired
class DesignSystem:
    """Centralized design system constants with Tailwind CSS color palette"""
    
    # Tailwind CSS Emerald (Primary) - 50 to 900
    EMERALD_50 = "#ECFDF5"
    EMERALD_100 = "#D1FAE5"
    EMERALD_200 = "#A7F3D0"
    EMERALD_300 = "#6EE7B7"
    EMERALD_400 = "#34D399"
    EMERALD_500 = "#10B981"  # Primary
    EMERALD_600 = "#059669"
    EMERALD_700 = "#047857"
    EMERALD_800 = "#065F46"
    EMERALD_900 = "#064E3B"
    
    # Tailwind CSS Blue (Secondary) - 50 to 900
    BLUE_50 = "#EFF6FF"
    BLUE_100 = "#DBEAFE"
    BLUE_200 = "#BFDBFE"
    BLUE_300 = "#93C5FD"
    BLUE_400 = "#60A5FA"
    BLUE_500 = "#3B82F6"  # Secondary
    BLUE_600 = "#2563EB"
    BLUE_700 = "#1D4ED8"
    BLUE_800 = "#1E3A8A"
    BLUE_900 = "#1E40AF"
    
    # Tailwind CSS Purple (Accent)
    PURPLE_50 = "#FAF5FF"
    PURPLE_100 = "#F3E8FF"
    PURPLE_200 = "#E9D5FF"
    PURPLE_300 = "#D8B4FE"
    PURPLE_400 = "#C084FC"
    PURPLE_500 = "#A855F7"
    PURPLE_600 = "#9333EA"
    PURPLE_700 = "#7E22CE"
    PURPLE_800 = "#6B21A8"
    PURPLE_900 = "#581C87"
    
    # Tailwind CSS Orange (Accent)
    ORANGE_50 = "#FFF7ED"
    ORANGE_100 = "#FFEDD5"
    ORANGE_200 = "#FED7AA"
    ORANGE_300 = "#FDBA74"
    ORANGE_400 = "#FB923C"
    ORANGE_500 = "#F97316"
    ORANGE_600 = "#EA580C"
    ORANGE_700 = "#C2410C"
    ORANGE_800 = "#9A3412"
    ORANGE_900 = "#7C2D12"
    
    # Tailwind CSS Pink (Accent)
    PINK_50 = "#FDF2F8"
    PINK_100 = "#FCE7F3"
    PINK_200 = "#FBCFE8"
    PINK_300 = "#F9A8D4"
    PINK_400 = "#F472B6"
    PINK_500 = "#EC4899"
    PINK_600 = "#DB2777"
    PINK_700 = "#BE185D"
    PINK_800 = "#9F1239"
    PINK_900 = "#831843"
    
    # Tailwind CSS Cyan (Accent)
    CYAN_50 = "#ECFEFF"
    CYAN_100 = "#CFFAFE"
    CYAN_200 = "#A5F3FC"
    CYAN_300 = "#67E8F9"
    CYAN_400 = "#22D3EE"
    CYAN_500 = "#06B6D4"
    CYAN_600 = "#0891B2"
    CYAN_700 = "#0E7490"
    CYAN_800 = "#155E75"
    CYAN_900 = "#164E63"
    
    # Tailwind CSS Amber (Warning)
    AMBER_50 = "#FFFBEB"
    AMBER_100 = "#FEF3C7"
    AMBER_200 = "#FDE68A"
    AMBER_300 = "#FCD34D"
    AMBER_400 = "#FBBF24"
    AMBER_500 = "#F59E0B"
    AMBER_600 = "#D97706"
    AMBER_700 = "#B45309"
    AMBER_800 = "#92400E"
    AMBER_900 = "#78350F"
    
    # Tailwind CSS Red (Error)
    RED_50 = "#FEF2F2"
    RED_100 = "#FEE2E2"
    RED_200 = "#FECACA"
    RED_300 = "#FCA5A5"
    RED_400 = "#F87171"
    RED_500 = "#EF4444"
    RED_600 = "#DC2626"
    RED_700 = "#B91C1C"
    RED_800 = "#991B1B"
    RED_900 = "#7F1D1D"
    
    # Tailwind CSS Gray (Neutral)
    GRAY_50 = "#F9FAFB"
    GRAY_100 = "#F3F4F6"
    GRAY_200 = "#E5E7EB"
    GRAY_300 = "#D1D5DB"
    GRAY_400 = "#9CA3AF"
    GRAY_500 = "#6B7280"
    GRAY_600 = "#4B5563"
    GRAY_700 = "#374151"
    GRAY_800 = "#1F2937"
    GRAY_900 = "#111827"
    
    # Legacy color aliases (for backward compatibility)
    PRIMARY = EMERALD_500
    PRIMARY_LIGHT = EMERALD_100
    PRIMARY_DARK = EMERALD_800
    
    SECONDARY = BLUE_500
    SECONDARY_LIGHT = BLUE_100
    SECONDARY_DARK = BLUE_800
    
    SUCCESS = EMERALD_500
    WARNING = AMBER_500
    ERROR = RED_500
    INFO = BLUE_500
    
    # Common colors
    WHITE = "#FFFFFF"
    BLACK = GRAY_900
    
    # Backgrounds
    BG_PRIMARY = GRAY_50
    BG_SECONDARY = "#FFFFFF"
    BG_TERTIARY = GRAY_50
    
    # Text Colors
    TEXT_PRIMARY = GRAY_900
    TEXT_SECONDARY = GRAY_500
    TEXT_TERTIARY = GRAY_400
    
    # Borders
    BORDER_COLOR = GRAY_200
    BORDER_COLOR_LIGHT = GRAY_100
    
    # Spacing - Tailwind CSS spacing scale (4px base)
    SPACING_1 = 4   # 0.25rem
    SPACING_2 = 8   # 0.5rem
    SPACING_3 = 12  # 0.75rem
    SPACING_4 = 16  # 1rem
    SPACING_5 = 20  # 1.25rem
    SPACING_6 = 24  # 1.5rem
    SPACING_8 = 32  # 2rem
    SPACING_10 = 40 # 2.5rem
    SPACING_12 = 48 # 3rem
    SPACING_16 = 64 # 4rem
    SPACING_20 = 80 # 5rem
    
    # Legacy spacing aliases
    SPACING_XS = SPACING_1
    SPACING_SM = SPACING_2
    SPACING_MD = SPACING_4
    SPACING_LG = SPACING_6
    SPACING_XL = SPACING_8
    SPACING_XXL = SPACING_12
    
    # Border Radius - Tailwind CSS radius values
    RADIUS_NONE = 0
    RADIUS_SM = 2   # rounded-sm
    RADIUS_MD = 6   # rounded-md
    RADIUS_LG = 8   # rounded-lg
    RADIUS_XL = 12  # rounded-xl
    RADIUS_2XL = 16 # rounded-2xl
    RADIUS_3XL = 24 # rounded-3xl
    RADIUS_FULL = 9999 # rounded-full
    
    # Shadows - Tailwind CSS shadow values
    SHADOW_SM = ft.BoxShadow(
        spread_radius=0,
        blur_radius=1,
        color="#00000005",
        offset=ft.Offset(0, 1),
    )
    SHADOW_MD = ft.BoxShadow(
        spread_radius=0,
        blur_radius=4,
        color="#00000008",
        offset=ft.Offset(0, 2),
    )
    SHADOW_LG = ft.BoxShadow(
        spread_radius=0,
        blur_radius=8,
        color="#00000010",
        offset=ft.Offset(0, 4),
    )
    SHADOW_XL = ft.BoxShadow(
        spread_radius=0,
        blur_radius=12,
        color="#00000012",
        offset=ft.Offset(0, 8),
    )
    SHADOW_2XL = ft.BoxShadow(
        spread_radius=0,
        blur_radius=16,
        color="#00000015",
        offset=ft.Offset(0, 12),
    )


def create_modern_button(
    text: str,
    on_click=None,
    icon: str = None,
    bgcolor: str = DesignSystem.PRIMARY,
    color: str = "#FFFFFF",
    width: int = None,
    height: int = 40,
    disabled: bool = False,
    variant: str = "filled",  # filled, outlined, text
    use_gradient: bool = False,
    gradient_colors: list = None,
    tooltip: str = None,
) -> ft.Control:
    """Create a modern button with Tailwind CSS-inspired styling"""
    style = ft.ButtonStyle(
        shape=ft.RoundedRectangleBorder(radius=DesignSystem.RADIUS_LG),
        elevation=0,
        padding=ft.padding.symmetric(horizontal=DesignSystem.SPACING_5, vertical=DesignSystem.SPACING_3),
    )
    
    # Gradient support - wrap button in Container if gradient is needed
    # ElevatedButton doesn't support gradient directly in older Flet versions
    if use_gradient and gradient_colors and variant == "filled":
        gradient = ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=gradient_colors,
        )
        
        # Create button without bgcolor (transparent)
        button = ft.ElevatedButton(
            text=text,
            icon=icon,
            on_click=on_click,
            bgcolor="transparent",
            color=color,
            width=width,
            height=height,
            disabled=disabled,
            style=style,
        )
        
        # Wrap button in Tooltip if tooltip text is provided
        button_content = button
        if tooltip:
            button_content = ft.Tooltip(
                message=tooltip,
                content=button,
            )
        
        # Wrap in Container with gradient background
        return ft.Container(
            content=button_content,
            gradient=gradient,
            border_radius=DesignSystem.RADIUS_LG,
            width=width,
            height=height,
        )
    
    # Normal button without gradient
    if variant == "outlined":
        style.bgcolor = "transparent"
        style.color = bgcolor
        style.side = ft.BorderSide(2, bgcolor)
    elif variant == "text":
        style.bgcolor = "transparent"
        style.color = bgcolor
    
    button = ft.ElevatedButton(
        text=text,
        icon=icon,
        on_click=on_click,
        bgcolor=bgcolor if variant == "filled" else None,
        color=color if variant == "filled" else bgcolor,
        width=width,
        height=height,
        disabled=disabled,
        style=style,
    )
    
    # Wrap in Tooltip if tooltip text is provided
    if tooltip:
        return ft.Tooltip(
            message=tooltip,
            content=button,
        )
    
    return button


def create_modern_text_field(
    label: str = None,
    value: str = None,
    hint_text: str = None,
    password: bool = False,
    can_reveal_password: bool = False,
    read_only: bool = False,
    width: int = None,
    height: int = None,
    multiline: bool = False,
    on_change=None,
    keyboard_type=None,
    max_lines: int = None,
) -> ft.TextField:
    """Create a modern text field with consistent styling"""
    text_field = ft.TextField(
        label=label,
        value=value,
        hint_text=hint_text,
        password=password,
        can_reveal_password=can_reveal_password,
        read_only=read_only,
        width=width,
        height=height,
        multiline=multiline,
        on_change=on_change,
        border_color=DesignSystem.BORDER_COLOR,
        focused_border_color=DesignSystem.PRIMARY,
        border_radius=DesignSystem.RADIUS_MD,
        content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
        text_size=14,
        label_style=ft.TextStyle(color=DesignSystem.TEXT_SECONDARY, size=14),
    )
    # Set keyboard_type if provided
    if keyboard_type is not None:
        text_field.keyboard_type = keyboard_type
    # Set max_lines if provided
    if max_lines is not None:
        text_field.max_lines = max_lines
    return text_field


def create_modern_dropdown(
    label: str = None,
    options: list = None,
    value: str = None,
    width: int = None,
    on_change=None,
) -> ft.Dropdown:
    """Create a modern dropdown with consistent styling"""
    return ft.Dropdown(
        label=label,
        options=options or [],
        value=value,
        width=width,
        on_change=on_change,
        border_color=DesignSystem.BORDER_COLOR,
        focused_border_color=DesignSystem.PRIMARY,
        border_radius=DesignSystem.RADIUS_MD,
        content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
        text_size=14,
        label_style=ft.TextStyle(color=DesignSystem.TEXT_SECONDARY, size=14),
    )


def create_modern_card(
    content: ft.Control,
    title: str = None,
    subtitle: str = None,
    icon: str = None,
    icon_color: str = DesignSystem.PRIMARY,
    padding: int = DesignSystem.SPACING_LG,
    elevation: int = 1,  # 0-3
    on_click=None,
) -> ft.Container:
    """Create a modern card component"""
    card_content = []
    
    # Header
    if title or icon:
        header_items = []
        if icon:
            header_items.append(
                ft.Container(
                    content=ft.Icon(icon, size=20, color=icon_color),
                    padding=ft.padding.all(10),
                    bgcolor=f"{icon_color}15",
                    border_radius=DesignSystem.RADIUS_MD,
                )
            )
        if title:
            header_items.append(
                ft.Text(
                    title,
                    size=18,
                    weight=ft.FontWeight.W_600,
                    color=DesignSystem.TEXT_PRIMARY,
                )
            )
        if subtitle:
            header_items.append(
                ft.Text(
                    subtitle,
                    size=14,
                    color=DesignSystem.TEXT_SECONDARY,
                )
            )
        
        card_content.append(
            ft.Container(
                content=ft.Row(header_items, spacing=12) if icon else ft.Column(header_items, spacing=4),
                padding=ft.padding.only(bottom=DesignSystem.SPACING_MD),
            )
        )
    
    # Main content
    if isinstance(content, list):
        card_content.extend(content)
    elif isinstance(content, ft.Column):
        # If content is a Column, extract its controls and filter None values
        if hasattr(content, 'controls') and content.controls:
            # Filter None values from the Column's controls
            filtered_controls = [c for c in content.controls if c is not None]
            card_content.extend(filtered_controls)
        else:
            card_content.append(content)
    else:
        card_content.append(content)
    
    # Filter out None values to prevent _build_add_commands errors
    card_content = [c for c in card_content if c is not None]
    
    # Ensure card_content is not empty
    if not card_content:
        card_content = [ft.Text("Empty content")]
    
    shadows = [DesignSystem.SHADOW_SM, DesignSystem.SHADOW_MD, DesignSystem.SHADOW_LG, DesignSystem.SHADOW_XL]
    
    # Create Column with filtered controls
    card_column = ft.Column(card_content, spacing=0)
    
    # Double-check: filter out None values from card_column.controls if any
    if hasattr(card_column, 'controls') and card_column.controls:
        card_column.controls = [c for c in card_column.controls if c is not None]
    
    return ft.Container(
        content=card_column,
        padding=ft.padding.all(padding),
        bgcolor=DesignSystem.BG_SECONDARY,
        border_radius=DesignSystem.RADIUS_LG,
        border=ft.border.all(1, DesignSystem.BORDER_COLOR),
        shadow=shadows[min(elevation, 3)] if elevation > 0 else None,
        on_click=on_click,
    )


def create_modern_table(
    columns: list,
    rows: list,
    border: bool = True,
) -> ft.DataTable:
    """Create a modern data table"""
    return ft.DataTable(
        columns=columns,
        rows=rows,
        border=ft.border.all(1, DesignSystem.BORDER_COLOR) if border else None,
        border_radius=DesignSystem.RADIUS_MD,
        heading_row_color=DesignSystem.BG_TERTIARY,
        heading_row_height=48,
        data_row_min_height=48,
        data_row_max_height=72,
        heading_text_style=ft.TextStyle(
            size=14,
            weight=ft.FontWeight.W_600,
            color=DesignSystem.TEXT_PRIMARY,
        ),
        data_text_style=ft.TextStyle(
            size=14,
            color=DesignSystem.TEXT_PRIMARY,
        ),
    )


def create_modern_dialog(
    title: str,
    content: ft.Control,
    actions: list = None,
) -> ft.AlertDialog:
    """Create a modern dialog"""
    return ft.AlertDialog(
        title=ft.Text(
            title,
            size=20,
            weight=ft.FontWeight.W_600,
            color=DesignSystem.TEXT_PRIMARY,
        ),
        content=content,
        actions=actions or [],
        actions_alignment=ft.MainAxisAlignment.END,
        shape=ft.RoundedRectangleBorder(radius=DesignSystem.RADIUS_LG),
        bgcolor=DesignSystem.BG_SECONDARY,
    )


def create_modern_divider() -> ft.Divider:
    """Create a modern divider"""
    return ft.Divider(
        height=1,
        color=DesignSystem.BORDER_COLOR,
    )


def create_modern_badge(
    text: str,
    color: str = DesignSystem.PRIMARY,
    size: int = 12,
) -> ft.Container:
    """Create a modern badge/chip"""
    return ft.Container(
        content=ft.Text(
            text,
            size=size,
            weight=ft.FontWeight.W_500,
            color=color,
        ),
        padding=ft.padding.symmetric(horizontal=DesignSystem.SPACING_2 + 2, vertical=DesignSystem.SPACING_1),
        bgcolor=f"{color}15",
        border_radius=DesignSystem.RADIUS_MD,
    )


def create_vibrant_badge(
    text: str,
    variant: str = "purple",  # purple, pink, cyan, orange, emerald, blue
    size: int = 12,
    icon: str = None,
) -> ft.Container:
    """Create a vibrant badge with Tailwind CSS colors"""
    color_map = {
        "purple": DesignSystem.PURPLE_600,
        "pink": DesignSystem.PINK_600,
        "cyan": DesignSystem.CYAN_600,
        "orange": DesignSystem.ORANGE_600,
        "emerald": DesignSystem.EMERALD_600,
        "blue": DesignSystem.BLUE_600,
    }
    bg_color_map = {
        "purple": DesignSystem.PURPLE_100,
        "pink": DesignSystem.PINK_100,
        "cyan": DesignSystem.CYAN_100,
        "orange": DesignSystem.ORANGE_100,
        "emerald": DesignSystem.EMERALD_100,
        "blue": DesignSystem.BLUE_100,
    }
    
    text_color = color_map.get(variant, DesignSystem.PURPLE_600)
    bg_color = bg_color_map.get(variant, DesignSystem.PURPLE_100)
    
    badge_content = []
    if icon:
        badge_content.append(ft.Icon(icon, size=size, color=text_color))
    badge_content.append(
        ft.Text(
            text,
            size=size,
            weight=ft.FontWeight.W_600,
            color=text_color,
        )
    )
    
    return ft.Container(
        content=ft.Row(
            badge_content,
            spacing=DesignSystem.SPACING_1,
            tight=True,
        ),
        padding=ft.padding.symmetric(horizontal=DesignSystem.SPACING_2 + 2, vertical=DesignSystem.SPACING_1),
        bgcolor=bg_color,
        border_radius=DesignSystem.RADIUS_MD,
    )


def create_modern_icon_button(
    icon: str,
    on_click=None,
    tooltip: str = None,
    color: str = DesignSystem.TEXT_SECONDARY,
    bgcolor: str = None,
    size: int = 20,
    vibrant: bool = False,
    variant: str = "emerald",  # emerald, blue, purple, pink, cyan, orange
) -> ft.IconButton:
    """Create a modern icon button with Tailwind CSS-inspired hover effects"""
    if vibrant:
        color_map = {
            "emerald": DesignSystem.EMERALD_600,
            "blue": DesignSystem.BLUE_600,
            "purple": DesignSystem.PURPLE_600,
            "pink": DesignSystem.PINK_600,
            "cyan": DesignSystem.CYAN_600,
            "orange": DesignSystem.ORANGE_600,
        }
        overlay_map = {
            "emerald": DesignSystem.EMERALD_100,
            "blue": DesignSystem.BLUE_100,
            "purple": DesignSystem.PURPLE_100,
            "pink": DesignSystem.PINK_100,
            "cyan": DesignSystem.CYAN_100,
            "orange": DesignSystem.ORANGE_100,
        }
        color = color_map.get(variant, DesignSystem.EMERALD_600)
        overlay_color = overlay_map.get(variant, DesignSystem.EMERALD_100)
    else:
        overlay_color = DesignSystem.GRAY_100
    
    return ft.IconButton(
        icon=icon,
        on_click=on_click,
        tooltip=tooltip,
        icon_color=color,
        bgcolor=bgcolor,
        icon_size=size,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=DesignSystem.RADIUS_LG),
            overlay_color=overlay_color,  # Hover effect
        ),
    )


def create_loading_indicator(
    message: str = None,
    size: int = 40,
) -> ft.Container:
    """Create a loading indicator (ProgressRing)"""
    from localization.translator import translator
    
    controls = [
        ft.ProgressRing(
            width=size,
            height=size,
            stroke_width=4,
            color=DesignSystem.PRIMARY,
        )
    ]
    
    if message:
        controls.append(
            ft.Text(
                message,
                size=14,
                color=DesignSystem.TEXT_SECONDARY,
            )
        )
    
    return ft.Container(
        content=ft.Column(
            controls,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
            tight=True,
        ),
        padding=DesignSystem.SPACING_LG,
        alignment=ft.alignment.center,
    )


def create_loading_overlay(
    message: str = None,
) -> ft.Container:
    """Create a loading overlay for long operations"""
    from localization.translator import translator
    
    return ft.Container(
        content=ft.Column(
            [
                ft.ProgressRing(
                    width=60,
                    height=60,
                    stroke_width=6,
                    color=DesignSystem.PRIMARY,
                ),
                ft.Text(
                    message or translator.get_text("common.loading"),
                    size=16,
                    color=DesignSystem.TEXT_PRIMARY,
                    weight=ft.FontWeight.W_500,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=16,
            tight=True,
        ),
        bgcolor="#FFFFFFE0",  # Semi-transparent white
        padding=DesignSystem.SPACING_XL,
        border_radius=DesignSystem.RADIUS_LG,
        alignment=ft.alignment.center,
    )


def show_error_snackbar(
    page: ft.Page,
    message: str,
    duration: int = 4000,
):
    """Show error message in SnackBar with consistent styling"""
    page.snack_bar = ft.SnackBar(
        content=ft.Text(message, color="#FFFFFF"),
        bgcolor=DesignSystem.ERROR,
        duration=duration,
        action="OK",
        action_color="#FFFFFF",
    )
    page.snack_bar.open = True
    page.update()


def show_success_snackbar(
    page: ft.Page,
    message: str,
    duration: int = 3000,
):
    """Show success message in SnackBar with consistent styling"""
    page.snack_bar = ft.SnackBar(
        content=ft.Text(message, color="#FFFFFF"),
        bgcolor=DesignSystem.SUCCESS,
        duration=duration,
        action="OK",
        action_color="#FFFFFF",
    )
    page.snack_bar.open = True
    page.update()


def show_info_snackbar(
    page: ft.Page,
    message: str,
    duration: int = 3000,
):
    """Show info message in SnackBar with consistent styling"""
    page.snack_bar = ft.SnackBar(
        content=ft.Text(message, color="#FFFFFF"),
        bgcolor=DesignSystem.INFO,
        duration=duration,
        action="OK",
        action_color="#FFFFFF",
    )
    page.snack_bar.open = True
    page.update()


def create_modern_divider(
    height: float = 1,
    color: str = DesignSystem.BORDER_COLOR,
    thickness: float = 1,
) -> ft.Divider:
    """Creates a modern divider with consistent styling."""
    return ft.Divider(height=height, color=color, thickness=thickness)


def create_modern_date_field(
    label: str,
    value: str = None,
    hint_text: str = None,
    on_change=None,
    required: bool = False,
    min_date: date = None,
    max_date: date = None,
    page: ft.Page = None,
) -> tuple:
    """
    Create a modern date input field with calendar picker dialog.
    Returns a tuple (Row container, TextField reference) for easy access to the field value.
    
    Args:
        label: Field label
        value: Initial date value (YYYY-MM-DD format)
        hint_text: Placeholder text
        on_change: Callback when date changes
        required: Whether field is required
        min_date: Minimum selectable date
        max_date: Maximum selectable date
        page: Flet Page reference (needed for date picker dialog)
    """
    from datetime import date, datetime, timedelta
    # Import translator for tooltip text
    try:
        from localization.translator import translator
    except ImportError:
        # Fallback translator
        class Translator:
            def get_text(self, key, default=None):
                return default or key
        translator = Translator()
    
    # Add asterisk to label if required
    display_label = label
    if required:
        display_label = f"{label} *"
    
    # Parse initial date value
    initial_date = None
    if value:
        try:
            initial_date = datetime.strptime(value, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            pass
    
    if not initial_date:
        initial_date = date.today()
    
    date_field = create_modern_text_field(
        label=display_label,
        value=value or "",
        hint_text=hint_text or "YYYY-MM-DD",
        on_change=on_change,
    )
    
    def open_date_picker(e):
        """Open simple date picker dialog"""
        if not page:
            # Fallback: set today's date
            today = date.today()
            date_field.value = today.strftime("%Y-%m-%d")
            date_field.update()
            if on_change:
                on_change(None)
            return
        
        # Parse current date or use today
        current_date = initial_date
        if date_field.value:
            try:
                current_date = datetime.strptime(date_field.value, "%Y-%m-%d").date()
            except (ValueError, TypeError):
                current_date = date.today()
        else:
            current_date = date.today()
        
        # Create year, month, day fields
        year_field = create_modern_text_field(
            label="Év / Year",
            value=str(current_date.year),
            width=100,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        
        month_field = create_modern_text_field(
            label="Hónap / Month",
            value=str(current_date.month),
            width=100,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        
        day_field = create_modern_text_field(
            label="Nap / Day",
            value=str(current_date.day),
            width=100,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        
        # Create date picker dialog first (before callbacks that reference it)
        # Use modal=False if there's already a dialog open
        is_modal = not (hasattr(page, 'dialog') and page.dialog and page.dialog.open)
        
        date_dialog = ft.AlertDialog(
            modal=is_modal,
            title=ft.Text(display_label),
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[year_field, month_field, day_field],
                        spacing=10,
                    ),
                    ft.Text(
                        "Adja meg az évet, hónapot és napot, majd kattintson az OK gombra.",
                        size=12,
                        color=DesignSystem.TEXT_SECONDARY,
                    ),
                ],
                spacing=15,
                width=400,
                height=120,
            ),
            actions=[],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        def confirm_date(e):
            """Confirm selected date"""
            try:
                year = int(year_field.value)
                month = int(month_field.value)
                day = int(day_field.value)
                selected_date = date(year, month, day)
                
                # Validate date range
                if min_date and selected_date < min_date:
                    selected_date = min_date
                if max_date and selected_date > max_date:
                    selected_date = max_date
                
                date_field.value = selected_date.strftime("%Y-%m-%d")
                date_field.update()
                
                # Close dialog
                date_dialog.open = False
                page.update()
                
                if on_change:
                    on_change(None)
            except (ValueError, TypeError):
                # Invalid date, keep current
                date_dialog.open = False
                page.update()
        
        def cancel_date(e):
            """Cancel date selection"""
            date_dialog.open = False
            page.update()
        
        # Set actions after dialog creation
        date_dialog.actions = [
            ft.TextButton(
                text="Mégse / Cancel",
                on_click=cancel_date,
            ),
            ft.ElevatedButton(
                text="OK",
                on_click=confirm_date,
                bgcolor=DesignSystem.PRIMARY,
                color="#FFFFFF",
            ),
        ]
        
        # Show dialog - store current dialog if exists to restore later
        old_dialog = getattr(page, 'dialog', None)
        page.dialog = date_dialog
        date_dialog.open = True
        page.update()
    
    # Get tooltip text
    try:
        tooltip_text = translator.get_text("common.select_date")
    except:
        tooltip_text = "Dátum kiválasztása / Select date"
    
    calendar_btn = create_modern_icon_button(
        icon=ft.icons.CALENDAR_TODAY,
        on_click=open_date_picker,
        tooltip=tooltip_text,
        color=DesignSystem.PRIMARY,
    )
    
    
    date_row = ft.Row(
        controls=[
            ft.Container(content=date_field, expand=True),
            calendar_btn,
        ],
        spacing=8,
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )
    
    return (date_row, date_field)


def create_modern_section_header(
    title: str,
    subtitle: str = None,
    action: ft.Control = None,
) -> ft.Container:
    """Create a modern section header"""
    items = [
        ft.Column([
            ft.Text(
                title,
                size=20,
                weight=ft.FontWeight.W_600,
                color=DesignSystem.TEXT_PRIMARY,
            ),
            ft.Text(
                subtitle,
                size=14,
                color=DesignSystem.TEXT_SECONDARY,
            ) if subtitle else None,
        ], spacing=4, tight=True),
    ]
    
    if action:
        items.append(ft.Container(expand=True))
        items.append(action)
    
    return ft.Container(
        content=ft.Row(items, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        padding=ft.padding.only(bottom=DesignSystem.SPACING_MD),
    )


def create_card_grid(
    cards: list,
    columns: int = 3,
    spacing: int = DesignSystem.SPACING_4,
    run_spacing: int = DesignSystem.SPACING_4,
) -> ft.GridView:
    """Create a responsive card grid layout"""
    return ft.GridView(
        controls=cards,
        runs_count=columns,
        max_extent=300,
        child_aspect_ratio=1.0,
        spacing=spacing,
        run_spacing=run_spacing,
        padding=DesignSystem.SPACING_4,
    )


def create_empty_state_card(
    icon: str,
    title: str,
    description: str = None,
    action_button: ft.Control = None,
    icon_color: str = DesignSystem.GRAY_400,
) -> ft.Container:
    """Create an empty state card with vibrant styling"""
    content_items = [
        ft.Icon(
            icon,
            size=64,
            color=icon_color,
        ),
        ft.Text(
            title,
            size=20,
            weight=ft.FontWeight.W_600,
            color=DesignSystem.TEXT_PRIMARY,
        ),
    ]
    
    if description:
        content_items.append(
            ft.Text(
                description,
                size=14,
                color=DesignSystem.TEXT_SECONDARY,
                text_align=ft.TextAlign.CENTER,
            )
        )
    
    if action_button:
        content_items.append(
            ft.Container(
                content=action_button,
                padding=ft.padding.only(top=DesignSystem.SPACING_4),
            )
        )
    
    return create_modern_card(
        content=ft.Column(
            content_items,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=DesignSystem.SPACING_2,
        ),
        padding=DesignSystem.SPACING_8,
        elevation=0,
    )


def create_loading_card(
    message: str = None,
    size: int = 40,
) -> ft.Container:
    """Create a loading state card"""
    from localization.translator import translator
    
    controls = [
        ft.ProgressRing(
            width=size,
            height=size,
            stroke_width=4,
            color=DesignSystem.PRIMARY,
        )
    ]
    
    if message:
        controls.append(
            ft.Text(
                message,
                size=14,
                color=DesignSystem.TEXT_SECONDARY,
            )
        )
    
    return create_modern_card(
        content=ft.Column(
            controls,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=DesignSystem.SPACING_3,
            tight=True,
        ),
        padding=DesignSystem.SPACING_8,
        elevation=0,
    )

