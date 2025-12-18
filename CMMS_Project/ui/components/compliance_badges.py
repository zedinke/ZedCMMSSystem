"""
Compliance Badges Component
Displays ISO and regulatory compliance badges with tooltips
"""

import flet as ft
# Compatibility for flet 0.23.2 - Icons are strings, not ft.Icons
if not hasattr(ft, 'Icons'):
    from utils.flet_icons import Icons
    ft.Icons = Icons
from localization.translator import translator


def create_compliance_badge(
    compliance_key: str,
    icon: str,
    color: str,
    tooltip_text: str = None
) -> ft.Tooltip:
    """
    Creates a single compliance badge with icon and tooltip
    
    Args:
        compliance_key: Translation key for the compliance (e.g., "compliance.gdpr")
        icon: Flet icon name (e.g., "SECURITY")
        color: Badge background color (hex)
        tooltip_text: Optional custom tooltip text
    
    Returns:
        ft.Container with badge
    """
    title = translator.get_text(f"{compliance_key}.title")
    description = tooltip_text or translator.get_text(f"{compliance_key}.description")
    
    badge_container = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(
                    getattr(ft.Icons, icon, "info"),
                    size=16,
                    color="#FFFFFF",
                ),
                ft.Text(
                    title,
                    size=10,
                    weight=ft.FontWeight.BOLD,
                    color="#FFFFFF",
                ),
            ],
            spacing=4,
            tight=True,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        bgcolor=color,
        padding=ft.padding.symmetric(horizontal=8, vertical=4),
        border_radius=12,
    )
    
    badge = ft.Tooltip(
        message=description,
        content=badge_container,
    )
    
    return badge


def create_compliance_badges_row(compact: bool = False) -> ft.Row:
    """
    Creates a row of all compliance badges
    
    Args:
        compact: If True, shows only icons without text
    
    Returns:
        ft.Row with all compliance badges
    """
    badges = [
        create_compliance_badge(
            "compliance.gdpr",
            "SECURITY",
            "#10B981",  # Green
        ),
        create_compliance_badge(
            "compliance.iso55001",
            "VERIFIED",
            "#6366F1",  # Blue
        ),
        create_compliance_badge(
            "compliance.szt_law",
            "ACCOUNT_BALANCE",
            "#8B5CF6",  # Purple
        ),
        create_compliance_badge(
            "compliance.msz_en13460",
            "DESCRIPTION",
            "#F59E0B",  # Orange
        ),
        create_compliance_badge(
            "compliance.nav",
            "BUSINESS",
            "#6B7280",  # Gray
        ),
    ]
    # Filter out None values to prevent _build_add_commands errors
    badges = [b for b in badges if b is not None]
    
    if compact:
        # Compact version: smaller badges, only icons
        compact_badges = []
        for badge in badges:
            # badge is a Tooltip, so we need to access its content
            badge_container = badge.content
            # Create new container with only icon
            icon_only_container = ft.Container(
                content=badge_container.content.controls[0],  # Keep only icon
                bgcolor=badge_container.bgcolor,
                padding=ft.padding.all(6),
                border_radius=badge_container.border_radius,
            )
            compact_badge = ft.Tooltip(
                message=badge.message,
                content=icon_only_container,
            )
            compact_badges.append(compact_badge)
        badges = compact_badges
    
    return ft.Row(
        controls=badges,
        spacing=8,
        alignment=ft.MainAxisAlignment.CENTER,
        wrap=False,
    )


def create_compliance_footer() -> ft.Container:
    """
    Creates a footer container with compliance badges, copyright, and system information
    Suitable for login screen
    
    Returns:
        ft.Container with footer
    """
    from ui.components.modern_components import DesignSystem
    from config.app_config import APP_NAME, APP_VERSION
    
    # System information
    system_info = [
        f"{APP_NAME} v{APP_VERSION}",
        "Computerized Maintenance Management System",
        "CMMS - Karbantartás Menedzsment Rendszer",
    ]
    
    # Copyright and ownership information
    copyright_info = [
        "© 2025 Geleta Ákos - Minden jog fenntartva / All rights reserved",
        "Tulajdonos / Owner: Geleta Ákos",
        "Email: geleako@gmail.com",
    ]
    
    # Technical information
    technical_info = [
        "Python + Flet Framework",
        "MySQL Database",
        "SQLAlchemy ORM",
        "Modern Tailwind CSS Design",
    ]
    
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Divider(height=1, color="#E5E7EB"),
                ft.Container(
                    content=create_compliance_badges_row(compact=False),
                    padding=ft.padding.symmetric(vertical=12, horizontal=20),
                    alignment=ft.alignment.center,
                ),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            # System name and version
                            ft.Text(
                                system_info[0],
                                size=11,
                                weight=ft.FontWeight.W_600,
                                color=DesignSystem.TEXT_PRIMARY,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Text(
                                system_info[1],
                                size=9,
                                color=DesignSystem.TEXT_SECONDARY,
                                text_align=ft.TextAlign.CENTER,
                                italic=True,
                            ),
                            ft.Container(height=8),
                            # Copyright and ownership
                            ft.Text(
                                copyright_info[0],
                                size=9,
                                weight=ft.FontWeight.W_500,
                                color=DesignSystem.TEXT_PRIMARY,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Text(
                                copyright_info[1],
                                size=9,
                                color=DesignSystem.TEXT_SECONDARY,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Text(
                                copyright_info[2],
                                size=9,
                                color=DesignSystem.BLUE_600,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Container(height=8),
                            # Technical stack
                            ft.Row(
                                controls=[
                                    ft.Text(
                                        " | ".join(technical_info),
                                        size=8,
                                        color=DesignSystem.TEXT_TERTIARY,
                                        text_align=ft.TextAlign.CENTER,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                wrap=True,
                            ),
                            ft.Container(height=4),
                            ft.Text(
                                translator.get_text("compliance.footer_note") if hasattr(translator, 'get_text') and translator.get_text("compliance.footer_note") else "Szabványoknak megfelelő rendszer / Standards compliant system",
                                size=8,
                                color=DesignSystem.TEXT_TERTIARY,
                                text_align=ft.TextAlign.CENTER,
                                italic=True,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=2,
                        tight=True,
                    ),
                    padding=ft.padding.symmetric(vertical=16, horizontal=20),
                    alignment=ft.alignment.center,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
            tight=True,
        ),
        bgcolor="#F9FAFB",
        padding=0,
    )


def create_compliance_badges_corner() -> ft.Container:
    """
    Creates a compact corner badge group
    Suitable for dashboard screen
    
    Returns:
        ft.Container with corner badges
    """
    return ft.Container(
        content=create_compliance_badges_row(compact=True),
        padding=ft.padding.all(8),
        bgcolor="#FFFFFF",
        border_radius=8,
        border=ft.border.all(1, "#E5E7EB"),
        tooltip=translator.get_text("compliance.tooltip") if hasattr(translator, 'get_text') and translator.get_text("compliance.tooltip") else "Szabályozási megfelelőség / Regulatory Compliance",
    )

