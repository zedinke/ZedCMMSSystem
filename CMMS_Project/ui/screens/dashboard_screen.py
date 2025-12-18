"""
Dashboard képernyő - Modern 2025 design
"""

import flet as ft
# Compatibility for flet 0.23.2 - Icons are strings, not ft.Icons
if not hasattr(ft, 'Icons'):
    from utils.flet_icons import Icons
    ft.Icons = Icons
from services.context_service import get_app_context
from services.reports_service import get_all_statistics
from services.reports_service_extended import get_trend_statistics, get_average_statistics
from services import worksheet_service, pm_service, asset_service
from localization.translator import translator
from utils.currency import format_price
from ui.components.compliance_badges import create_compliance_badges_corner
from ui.components.modern_components import (
    create_modern_button,
    create_modern_card,
    create_modern_badge,
    create_vibrant_badge,
    DesignSystem,
)
from ui.components.modern_card import (
    create_metric_card,
    create_tailwind_card,
    create_info_card,
)
from database.connection import recreate_engine
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DashboardScreen:
    def __init__(self, on_logout):
        self.on_logout = on_logout
        self.page = None

    def _build_mode_selector(self):
        """Build database mode selector component"""
        # Lazy import to avoid circular dependency
        from ui.app import state
        
        # Create RadioGroup first
        mode_radio_group = ft.RadioGroup(
            value=state.database_mode,
            content=ft.Row(
                controls=[
                    ft.Radio(
                        value="production",
                        label=translator.get_text("dashboard.mode.production"),
                    ),
                    ft.Radio(
                        value="learning",
                        label=translator.get_text("dashboard.mode.learning"),
                    ),
                ],
                spacing=20,
            ),
        )
        
        # Create text display for current mode
        current_mode_text = ft.Text(
            translator.get_text("dashboard.mode.current", mode=translator.get_text("dashboard.mode.production") if state.database_mode == "production" else translator.get_text("dashboard.mode.learning")),
            size=12,
            weight=ft.FontWeight.W_500,
        )
        
        # Create warning text
        warning_text = ft.Text(
            translator.get_text("dashboard.mode.warning"),
            size=11,
            color="#F59E0B" if state.database_mode == "learning" else "#10B981",
            italic=True,
        )
        
        def on_mode_change(e):
            """Handle mode change"""
            # Lazy import to avoid circular dependency
            from ui.app import state
            new_mode = e.control.value
            old_mode = state.database_mode
            
            if new_mode != old_mode:
                try:
                    # Update state
                    state.database_mode = new_mode
                    
                    # Recreate engine with new mode
                    recreate_engine(new_mode)
                    
                    # Update UI elements
                    mode_text = translator.get_text("dashboard.mode.production") if new_mode == "production" else translator.get_text("dashboard.mode.learning")
                    current_mode_text.value = translator.get_text("dashboard.mode.current", mode=mode_text)
                    warning_text.color = "#F59E0B" if new_mode == "learning" else "#10B981"
                    
                    # Update RadioGroup value
                    mode_radio_group.value = new_mode
                    
                    # Show success message
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(translator.get_text("dashboard.mode.switched", mode=mode_text)),
                        bgcolor="green",
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
                    
                    # Refresh dashboard data
                    # Note: Full page refresh might be needed
                except Exception as ex:
                    logger.error(f"Error switching database mode: {ex}")
                    # Revert RadioGroup value on error
                    mode_radio_group.value = old_mode
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"Hiba a módváltáskor / Error switching mode: {str(ex)}"),
                        bgcolor="red",
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
        
        mode_radio_group.on_change = on_mode_change
        
        current_mode = state.database_mode
        mode_text = translator.get_text("dashboard.mode.production") if current_mode == "production" else translator.get_text("dashboard.mode.learning")
        warning_color = "#F59E0B" if current_mode == "learning" else "#10B981"  # Orange for learning, green for production
        
        return create_modern_card(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(
                                ft.Icons.STORAGE if hasattr(ft.Icons, 'STORAGE') else ft.Icons.DATABASE,
                                size=24,
                                color=warning_color,
                            ),
                            ft.Text(
                                translator.get_text("dashboard.mode.title"),
                                size=18,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ],
                        spacing=10,
                    ),
                    ft.Divider(height=1),
                    mode_radio_group,
                    ft.Container(
                        content=current_mode_text,
                        padding=ft.padding.only(top=5),
                    ),
                    ft.Container(
                        content=warning_text,
                        padding=ft.padding.only(top=5),
                    ),
                ],
                spacing=8,
            ),
            padding=15,
        )

    def view(self, page: ft.Page):
        self.page = page
        ctx = get_app_context()
        # Use full_name if available, otherwise use username
        display_name = (ctx.full_name if ctx.full_name and ctx.full_name.strip() else ctx.username) or translator.get_text("common.labels.user")
        greeting = translator.get_text("dashboard.greeting", name=display_name)

        logout_btn = create_modern_button(
            text=translator.get_text("common.buttons.logout"),
            icon=ft.Icons.EXIT_TO_APP if hasattr(ft.Icons, 'EXIT_TO_APP') else ft.Icons.LOGOUT,
            on_click=lambda e: self.on_logout(),
            bgcolor=DesignSystem.ERROR,
            height=40,
        )
        
        def close_app(_):
            """Close the application"""
            page.window.close()
        
        close_app_btn = create_modern_button(
            text=translator.get_text("common.buttons.close_app"),
            icon=ft.Icons.CLOSE,
            on_click=close_app,
            bgcolor=DesignSystem.TEXT_SECONDARY,
            height=40,
        )

        # Get quick statistics (optimized with caching)
        try:
            ctx = get_app_context()
            user_id = ctx.user_id if ctx else None
            
            # Get current month statistics (cached for 5 minutes)
            stats = get_all_statistics("month", user_id)
            
            # Use count queries instead of loading all records (much faster)
            from database.session_manager import SessionLocal
            from database.models import Worksheet, PMTask, Machine
            from sqlalchemy import func
            
            session = SessionLocal()
            try:
                # Count worksheets (optimized - no need to load all)
                worksheet_count = session.query(func.count(Worksheet.id)).scalar() or 0
                active_worksheets = session.query(func.count(Worksheet.id)).filter(
                    Worksheet.status == "Open"
                ).scalar() or 0
                
                # Count PM tasks (optimized)
                pm_count = session.query(func.count(PMTask.id)).filter(
                    PMTask.next_due_date <= datetime.utcnow()
                ).scalar() or 0
                
                # Count machines (optimized)
                machine_count = session.query(func.count(Machine.id)).scalar() or 0
            finally:
                session.close()
            
            # Get cost and time stats from cached statistics
            total_cost = stats.get('cost', {}).get('total_cost', 0)
            total_time = stats.get('time', {}).get('total_time_hours', 0)
            total_tasks = stats.get('tasks', {}).get('total_tasks', 0)
            
            # Get trend analysis (cached)
            try:
                trend_stats = get_trend_statistics(["month", "week"], user_id)
                trend_comparison = trend_stats.get('_comparison', {})
            except Exception as e:
                logger.error(f"Error getting trend stats: {e}")
                trend_comparison = {}
            
        except Exception as e:
            logger.error(f"Error loading dashboard statistics: {e}")
            worksheet_count = 0
            active_worksheets = 0
            pm_count = 0
            machine_count = 0
            total_cost = 0
            total_time = 0
            total_tasks = 0
            trend_comparison = {}
        
        # Modern metric cards with Tailwind CSS vibrant colors
        cards = ft.Row(
            controls=[
                create_metric_card(
                    value=str(machine_count),
                    label=translator.get_text("menu.assets"),
                    icon=ft.Icons.PRECISION_MANUFACTURING if hasattr(ft.Icons, 'PRECISION_MANUFACTURING') else ft.Icons.FACTORY,
                    color=DesignSystem.PURPLE_500,
                    use_gradient=True,
                    gradient_colors=[DesignSystem.PURPLE_400, DesignSystem.PURPLE_600],
                ),
                create_metric_card(
                    value=f"{active_worksheets}/{worksheet_count}",
                    label=translator.get_text("menu.worksheets"),
                    icon=ft.Icons.ASSIGNMENT if hasattr(ft.Icons, 'ASSIGNMENT') else ft.Icons.DESCRIPTION,
                    color=DesignSystem.EMERALD_500,
                    use_gradient=True,
                    gradient_colors=[DesignSystem.EMERALD_400, DesignSystem.EMERALD_600],
                ),
                create_metric_card(
                    value=str(pm_count),
                    label=translator.get_text("preventive_maintenance.title"),
                    icon=ft.Icons.CONSTRUCTION if hasattr(ft.Icons, 'CONSTRUCTION') else ft.Icons.BUILD,
                    color=DesignSystem.ORANGE_500,
                    use_gradient=True,
                    gradient_colors=[DesignSystem.ORANGE_400, DesignSystem.ORANGE_600],
                ),
                create_metric_card(
                    value=format_price(total_cost),
                    label=translator.get_text("dashboard.total_cost"),
                    icon=ft.Icons.ATTACH_MONEY if hasattr(ft.Icons, 'ATTACH_MONEY') else ft.Icons.PAYMENTS,
                    color=DesignSystem.CYAN_500,
                    use_gradient=True,
                    gradient_colors=[DesignSystem.CYAN_400, DesignSystem.CYAN_600],
                ),
            ],
            wrap=True,
            spacing=DesignSystem.SPACING_4,
        )
        
        # Quick statistics section
        quick_stats_section = _build_quick_stats_section(
            total_tasks, total_time, trend_comparison
        )
        
        # Alerts/Notifications section
        alerts_section = _build_alerts_section(
            active_worksheets, pm_count, total_cost, trend_comparison
        )

        # Welcome header with icon - Tailwind CSS design
        welcome_header = create_tailwind_card(
            content=ft.Row([
                ft.Container(
                    content=ft.Icon(ft.Icons.DASHBOARD, size=32, color=DesignSystem.EMERALD_500),
                    padding=ft.padding.all(DesignSystem.SPACING_3),
                    bgcolor=DesignSystem.EMERALD_100,
                    border_radius=DesignSystem.RADIUS_XL,
                ),
                ft.Column([
                    ft.Text(greeting, size=28, weight=ft.FontWeight.W_700, color=DesignSystem.TEXT_PRIMARY),
                    ft.Text(
                        translator.get_text("dashboard.quick_stats"),
                        size=14,
                        color=DesignSystem.TEXT_SECONDARY,
                    ),
                ], spacing=DesignSystem.SPACING_1, tight=True),
                ft.Container(expand=True),
                create_compliance_badges_corner(),
                ft.Container(width=DesignSystem.SPACING_2),
                close_app_btn,
                ft.Container(width=DesignSystem.SPACING_2),
                logout_btn,
            ], alignment=ft.MainAxisAlignment.START),
            padding=DesignSystem.SPACING_6,
            elevation=2,
            accent_color=DesignSystem.EMERALD_500,
            border_accent=True,
        )

        # Build mode selector
        mode_selector = self._build_mode_selector()
        
        return ft.Column(
            controls=[
                welcome_header,
                ft.Container(height=16),
                mode_selector,
                ft.Container(height=16),
                cards,
                ft.Container(height=24),
                quick_stats_section,
                ft.Container(height=24),
                alerts_section,
            ],
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )




def _build_quick_stats_section(total_tasks: int, total_time: float, trend_comparison: dict) -> ft.Container:
    """Build quick statistics section with Tailwind CSS cards"""
    from ui.components.modern_components import DesignSystem
    
    return create_tailwind_card(
        content=ft.Column([
            ft.Text(
                translator.get_text("dashboard.quick_statistics") if hasattr(translator, 'get_text') else "Gyors Statisztikák / Quick Statistics",
                size=20,
                weight=ft.FontWeight.W_600,
                color=DesignSystem.TEXT_PRIMARY,
            ),
            ft.Container(height=DesignSystem.SPACING_4),
            ft.Row([
                create_info_card(
                    icon=ft.Icons.ASSIGNMENT if hasattr(ft.Icons, 'ASSIGNMENT') else ft.Icons.DESCRIPTION,
                    title=str(total_tasks),
                    description=translator.get_text("dashboard.this_month_tasks") if hasattr(translator, 'get_text') else "Havi Feladatok / Monthly Tasks",
                    variant="blue",
                ),
                create_info_card(
                    icon=ft.Icons.ACCESS_TIME if hasattr(ft.Icons, 'ACCESS_TIME') else ft.Icons.SCHEDULE,
                    title=f"{total_time:.1f} óra",
                    description=translator.get_text("dashboard.this_month_time") if hasattr(translator, 'get_text') else "Havi Idő / Monthly Time",
                    variant="purple",
                ),
            ], spacing=DesignSystem.SPACING_4, wrap=True),
        ], spacing=0),
        padding=DesignSystem.SPACING_6,
        elevation=1,
    )


def _build_alerts_section(active_worksheets: int, pm_count: int, total_cost: float, trend_comparison: dict) -> ft.Container:
    """Build alerts/notifications section with Tailwind CSS cards"""
    from ui.components.modern_components import DesignSystem
    
    alerts = []
    
    # High cost alert
    if total_cost > 10000:  # Threshold: 10,000 EUR
        alerts.append(
            create_info_card(
                icon=ft.Icons.WARNING,
                title=translator.get_text("dashboard.alert_high_cost") if hasattr(translator, 'get_text') else "Magas havi költség / High monthly cost",
                description=translator.get_text("dashboard.alert_high_cost_desc") if hasattr(translator, 'get_text') else f"Jelenlegi havi költség: {format_price(total_cost)}",
                icon_color=DesignSystem.RED_500,
                variant="red",
            )
        )
    
    # Many active worksheets alert
    if active_worksheets > 10:
        alerts.append(
            create_info_card(
                icon=ft.Icons.INFO,
                title=translator.get_text("dashboard.alert_many_worksheets") if hasattr(translator, 'get_text') else "Sok aktív munkalap / Many active worksheets",
                description=(translator.get_text("dashboard.alert_many_worksheets_desc") if hasattr(translator, 'get_text') else "{count} aktív munkalap van").format(count=active_worksheets),
                icon_color=DesignSystem.ORANGE_500,
                variant="orange",
            )
        )
    
    # Trend alerts
    if trend_comparison:
        cost_change = trend_comparison.get('cost_change', 0)
        if cost_change > 20:  # More than 20% increase
            alerts.append(
                create_info_card(
                    icon=ft.Icons.TRENDING_UP,
                    title=translator.get_text("dashboard.alert_cost_increase") if hasattr(translator, 'get_text') else "Költség növekedés / Cost increase",
                    description=(translator.get_text("dashboard.alert_cost_increase_desc") if hasattr(translator, 'get_text') else "Költség {percent}%-kal nőtt").format(percent=f"{cost_change:.1f}"),
                    icon_color=DesignSystem.RED_500,
                    variant="red",
                )
            )
    
    if not alerts:
        return ft.Container()  # No alerts
    
    return create_tailwind_card(
        content=ft.Column([
            ft.Text(
                translator.get_text("dashboard.alerts") if hasattr(translator, 'get_text') else "Értesítések / Alerts",
                size=20,
                weight=ft.FontWeight.W_600,
                color=DesignSystem.TEXT_PRIMARY,
            ),
            ft.Container(height=DesignSystem.SPACING_4),
            ft.Column(alerts, spacing=DesignSystem.SPACING_3),
        ], spacing=0),
        padding=DesignSystem.SPACING_6,
        elevation=1,
    )
