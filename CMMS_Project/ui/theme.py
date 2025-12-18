"""
UI Theme Configuration
Tailwind CSS-inspired theme for the CMMS application
Vibrant colors, modern design with card-based layout
"""

import flet as ft
from ui.components.modern_components import DesignSystem

def get_app_theme():
    """
    Returns a Tailwind CSS-inspired theme with vibrant colors
    Primary: Emerald (Tailwind emerald-500) - Modern, vibrant green
    Secondary: Blue (Tailwind blue-500) - Modern blue accent
    Background: Clean grays optimized for card-based layout
    """
    
    return ft.Theme(
        color_scheme=ft.ColorScheme(
            # Primary colors - Tailwind Emerald
            primary=DesignSystem.EMERALD_500,            # Emerald-500 - Vibrant green
            on_primary="#FFFFFF",                         # White text on primary
            primary_container=DesignSystem.EMERALD_100,   # Emerald-100 - Light green background
            on_primary_container=DesignSystem.EMERALD_800, # Emerald-800 - Dark green text
            
            # Secondary colors - Tailwind Blue
            secondary=DesignSystem.BLUE_500,              # Blue-500 - Vibrant blue
            on_secondary="#FFFFFF",                       # White text on secondary
            secondary_container=DesignSystem.BLUE_100,    # Blue-100 - Light blue background
            on_secondary_container=DesignSystem.BLUE_800, # Blue-800 - Dark blue text
            
            # Tertiary colors - Tailwind Amber
            tertiary=DesignSystem.AMBER_500,              # Amber-500 - Warm amber
            on_tertiary="#FFFFFF",                        # White text on tertiary
            
            # Background colors - Tailwind Gray
            background=DesignSystem.GRAY_50,              # Gray-50 - Clean background for cards
            on_background=DesignSystem.GRAY_900,         # Gray-900 - Deep dark for text
            
            # Surface colors - Pure white for cards
            surface=DesignSystem.BG_SECONDARY,           # White - Pure white for cards
            on_surface=DesignSystem.GRAY_900,            # Gray-900 - Dark text on surface
            
            # Surface variant - Subtle borders
            surface_variant=DesignSystem.GRAY_100,       # Gray-100 - Light gray for borders
            on_surface_variant=DesignSystem.GRAY_500,    # Gray-500 - Medium gray for secondary text
            
            # Error colors - Tailwind Red
            error=DesignSystem.RED_500,                   # Red-500 - Vibrant red
            on_error="#FFFFFF",                          # White text on error
            
            # Outline and shadow
            outline=DesignSystem.GRAY_200,               # Gray-200 - Subtle borders
            shadow="#000000",                            # Black shadow
        ),
        
        # Text theme - Tailwind CSS typography
        text_theme=ft.TextTheme(
            display_large=ft.TextStyle(size=57, weight=ft.FontWeight.W_400, color=DesignSystem.GRAY_900),
            display_medium=ft.TextStyle(size=45, weight=ft.FontWeight.W_400, color=DesignSystem.GRAY_900),
            display_small=ft.TextStyle(size=36, weight=ft.FontWeight.W_400, color=DesignSystem.GRAY_900),
            headline_large=ft.TextStyle(size=32, weight=ft.FontWeight.W_600, color=DesignSystem.GRAY_900),
            headline_medium=ft.TextStyle(size=28, weight=ft.FontWeight.W_600, color=DesignSystem.GRAY_900),
            headline_small=ft.TextStyle(size=24, weight=ft.FontWeight.W_600, color=DesignSystem.GRAY_900),
            title_large=ft.TextStyle(size=22, weight=ft.FontWeight.W_600, color=DesignSystem.GRAY_900),
            title_medium=ft.TextStyle(size=16, weight=ft.FontWeight.W_500, color=DesignSystem.GRAY_900),
            title_small=ft.TextStyle(size=14, weight=ft.FontWeight.W_500, color=DesignSystem.GRAY_900),
            body_large=ft.TextStyle(size=16, weight=ft.FontWeight.W_400, color=DesignSystem.GRAY_900),
            body_medium=ft.TextStyle(size=14, weight=ft.FontWeight.W_400, color=DesignSystem.GRAY_900),
            body_small=ft.TextStyle(size=12, weight=ft.FontWeight.W_400, color=DesignSystem.GRAY_500),
            label_large=ft.TextStyle(size=14, weight=ft.FontWeight.W_500, color=DesignSystem.GRAY_900),
            label_medium=ft.TextStyle(size=12, weight=ft.FontWeight.W_500, color=DesignSystem.GRAY_900),
            label_small=ft.TextStyle(size=11, weight=ft.FontWeight.W_500, color=DesignSystem.GRAY_500),
        ),
    )

def get_dark_theme():
    """Returns the dark mode version with Tailwind CSS dark theme colors"""
    return ft.Theme(
        color_scheme=ft.ColorScheme(
            # Primary colors - Lighter emerald for dark mode
            primary=DesignSystem.EMERALD_400,            # Emerald-400 - Lighter green for dark
            on_primary=DesignSystem.EMERALD_900,        # Emerald-900 - Dark text on light primary
            primary_container=DesignSystem.EMERALD_800, # Emerald-800 - Dark green container
            on_primary_container=DesignSystem.EMERALD_100, # Emerald-100 - Light text on dark container
            
            # Secondary colors - Lighter blue for dark mode
            secondary=DesignSystem.BLUE_400,             # Blue-400 - Lighter blue
            on_secondary=DesignSystem.BLUE_800,          # Blue-800 - Dark text on light secondary
            secondary_container=DesignSystem.BLUE_800,   # Blue-800 - Dark blue container
            on_secondary_container=DesignSystem.BLUE_100, # Blue-100 - Light text
            
            # Tertiary colors - Tailwind Amber
            tertiary=DesignSystem.AMBER_400,             # Amber-400 - Lighter amber
            on_tertiary=DesignSystem.AMBER_900,         # Amber-900 - Dark text
            
            # Background colors - Deep dark grays
            background=DesignSystem.GRAY_900,           # Gray-900 - Deep dark
            on_background=DesignSystem.GRAY_50,         # Gray-50 - Light gray text
            
            # Surface colors - Slightly lighter than background
            surface=DesignSystem.GRAY_800,               # Gray-800 - Dark gray surface
            on_surface=DesignSystem.GRAY_50,            # Gray-50 - Light text
            
            # Surface variant
            surface_variant=DesignSystem.GRAY_700,     # Gray-700 - Medium dark gray
            on_surface_variant=DesignSystem.GRAY_300,   # Gray-300 - Light gray text
            
            # Error colors - Softer red for dark mode
            error=DesignSystem.RED_400,                  # Red-400 - Softer red for dark mode
            on_error=DesignSystem.RED_900,              # Red-900 - Dark text on light error
            
            # Outline and shadow
            outline=DesignSystem.GRAY_600,               # Gray-600 - Medium gray borders
        ),
        # Text theme - Tailwind CSS typography for dark mode
        text_theme=ft.TextTheme(
            display_large=ft.TextStyle(size=57, weight=ft.FontWeight.W_400, color=DesignSystem.GRAY_50),
            display_medium=ft.TextStyle(size=45, weight=ft.FontWeight.W_400, color=DesignSystem.GRAY_50),
            display_small=ft.TextStyle(size=36, weight=ft.FontWeight.W_400, color=DesignSystem.GRAY_50),
            headline_large=ft.TextStyle(size=32, weight=ft.FontWeight.W_600, color=DesignSystem.GRAY_50),
            headline_medium=ft.TextStyle(size=28, weight=ft.FontWeight.W_600, color=DesignSystem.GRAY_50),
            headline_small=ft.TextStyle(size=24, weight=ft.FontWeight.W_600, color=DesignSystem.GRAY_50),
            title_large=ft.TextStyle(size=22, weight=ft.FontWeight.W_600, color=DesignSystem.GRAY_50),
            title_medium=ft.TextStyle(size=16, weight=ft.FontWeight.W_500, color=DesignSystem.GRAY_50),
            title_small=ft.TextStyle(size=14, weight=ft.FontWeight.W_500, color=DesignSystem.GRAY_50),
            body_large=ft.TextStyle(size=16, weight=ft.FontWeight.W_400, color=DesignSystem.GRAY_50),
            body_medium=ft.TextStyle(size=14, weight=ft.FontWeight.W_400, color=DesignSystem.GRAY_50),
            body_small=ft.TextStyle(size=12, weight=ft.FontWeight.W_400, color=DesignSystem.GRAY_300),
            label_large=ft.TextStyle(size=14, weight=ft.FontWeight.W_500, color=DesignSystem.GRAY_50),
            label_medium=ft.TextStyle(size=12, weight=ft.FontWeight.W_500, color=DesignSystem.GRAY_50),
            label_small=ft.TextStyle(size=11, weight=ft.FontWeight.W_500, color=DesignSystem.GRAY_300),
        ),
    )
