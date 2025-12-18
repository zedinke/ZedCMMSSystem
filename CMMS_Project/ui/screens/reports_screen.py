"""
Reports Screen - Grafikonok és Kimutatások
"""

import flet as ft
# Compatibility for flet 0.23.2 - Icons are strings, not ft.Icons
if not hasattr(ft, 'Icons'):
    from utils.flet_icons import Icons
    ft.Icons = Icons
from datetime import datetime
from pathlib import Path
from typing import Optional
import os
import threading

from services.reports_service import get_all_statistics, get_period_comparison, get_technician_statistics
from services.reports_service_extended import get_trend_statistics, get_average_statistics, get_machine_statistics
from services.excel_export_service import export_reports_to_excel
from services.chart_service import generate_cost_chart, generate_time_chart, generate_tasks_chart, generate_tasks_pie_chart
from services.context_service import get_app_context
from services import asset_service
from localization.translator import translator
from utils.currency import format_price
from ui.components.modern_components import (
    create_modern_button,
    create_modern_card,
    create_vibrant_badge,
    create_empty_state_card,
    DesignSystem,
)
from ui.components.modern_card import (
    create_tailwind_card,
    create_info_card,
    create_metric_card,
)
import logging

logger = logging.getLogger(__name__)


class ReportsScreen:
    def __init__(self):
        self.current_period = "month"
        self.show_personal = False
        self.periods = ["day", "week", "month", "year"]
        self.filter_machine_id = None
        self.filter_status = None
        self.filter_priority = None
        self.expanded_filters = False
        self.technician_sort_column = 'tasks'
        self.technician_sort_ascending = False
        self.technician_search_text = ""
    
    def view(self, page: ft.Page):
        ctx = get_app_context()
        user_id = ctx.user_id if ctx and self.show_personal else None
        
        # Period selector
        period_dropdown = ft.Dropdown(
            label=translator.get_text("reports.period") if hasattr(translator, 'get_text') else "Időszak / Period",
            options=[
                ft.dropdown.Option("day", "Nap / Day"),
                ft.dropdown.Option("week", "Hét / Week"),
                ft.dropdown.Option("month", "Hó / Month"),
                ft.dropdown.Option("year", "Év / Year"),
            ],
            value=self.current_period,
            width=200,
            on_change=lambda e: self._on_period_change(e, page),
        )
        
        # Personal/All toggle
        personal_switch = ft.Switch(
            label=translator.get_text("reports.personal_only") if hasattr(translator, 'get_text') else "Csak személyes / Personal only",
            value=self.show_personal,
            on_change=lambda e: self._on_personal_toggle(e, page),
        )
        
        # Export button
        export_btn = ft.ElevatedButton(
            translator.get_text("reports.export_excel") if hasattr(translator, 'get_text') else "Excel letöltés / Export Excel",
            icon=ft.Icons.DOWNLOAD if hasattr(ft.Icons, 'DOWNLOAD') else ft.Icons.FILE_DOWNLOAD,
            on_click=lambda e: self._on_export_excel(e, page),
            bgcolor=DesignSystem.SUCCESS,
            color="#FFFFFF",
            height=44,
        )
        
        # Print button
        print_btn = ft.ElevatedButton(
            translator.get_text("reports.print") if hasattr(translator, 'get_text') else "Nyomtatás / Print",
            icon=ft.Icons.PRINT if hasattr(ft.Icons, 'PRINT') else ft.Icons.PRINT_OUTLINED,
            on_click=lambda e: self._on_print(e, page),
            bgcolor=DesignSystem.SECONDARY,
            color="#FFFFFF",
            height=44,
        )
        
        # Filters section
        filters_section = self._build_filters_section(page)
        
        # Get statistics with filters
        # Log filter values to verify they are being used
        logger.info(f"Getting statistics - period: {self.current_period}, user_id: {user_id}, machine_id: {self.filter_machine_id}, status: {self.filter_status}, priority: {self.filter_priority}")
        stats = get_all_statistics(
            self.current_period, 
            user_id,
            self.filter_machine_id,
            self.filter_status,
            self.filter_priority
        )
        
        # Get extended statistics
        try:
            from services.reports_service_extended import get_trend_statistics as get_ext_trends
            trend_stats = get_ext_trends(self.periods, user_id)
            avg_stats = get_average_statistics(self.current_period, user_id)
            machine_stats = get_machine_statistics(self.current_period, self.filter_machine_id)
        except Exception as e:
            logger.error(f"Error getting extended statistics: {e}")
            trend_stats = {}
            avg_stats = {}
            machine_stats = []
        
        # Build content
        content = ft.Column([
            # Header
            ft.Row([
                ft.Text(
                    translator.get_text("reports.title") if hasattr(translator, 'get_text') else "Grafikonok és Kimutatások / Reports and Charts",
                    size=24,
                    weight=ft.FontWeight.W_700,
                ),
                ft.Column(expand=True),
                period_dropdown,
                personal_switch,
                print_btn,
                export_btn,
            ], spacing=20),
            
            # Filters section
            filters_section,
            
            ft.Divider(height=1),
            
            # Extended statistics (trends, averages)
            self._build_extended_statistics_section(trend_stats, avg_stats),
            
            # Statistics cards
            self._build_statistics_cards(stats),
            
            ft.Divider(height=1),
            
            # Machine statistics section
            *([self._build_machine_statistics_section(machine_stats)] if machine_stats else []),
            
            # Charts section
            self._build_charts_section(stats, page),
            
        ], spacing=16, scroll=ft.ScrollMode.AUTO, expand=True)
        
        return content
    
    def _on_period_change(self, e, page: ft.Page):
        self.current_period = e.control.value
        # Trigger route change to rebuild view properly
        page.go("/reports")
    
    def _on_personal_toggle(self, e, page: ft.Page):
        self.show_personal = e.control.value
        # Trigger route change to rebuild view properly
        page.go("/reports")
    
    def _on_export_excel(self, e, page: ft.Page):
        """Export reports to Excel with file picker"""
        def on_save_result(e: ft.FilePickerResultEvent):
            if e.path is None:
                # User cancelled
                page.snack_bar = ft.SnackBar(
                    ft.Text(translator.get_text("worksheets.download_cancelled")),
                    bgcolor=DesignSystem.TEXT_SECONDARY
                )
                page.snack_bar.open = True
                page.update()
                return
            
            def export_thread():
                try:
                    ctx = get_app_context()
                    user_id = ctx.user_id if ctx and self.show_personal else None
                    
                    # Ensure .xlsx extension
                    save_path = Path(e.path)
                    if not save_path.suffix.lower() == '.xlsx':
                        save_path = save_path.with_suffix('.xlsx')
                    
                    logger.info(f"Generating Excel file to: {save_path}")
                    
                    # Generate Excel file directly to selected location
                    output_path = export_reports_to_excel(
                        periods=self.periods,
                        user_id=user_id,
                        output_path=save_path
                    )
                    
                    logger.info(f"Excel file generated: {output_path}, exists: {output_path.exists()}")
                    
                    # Verify file was created
                    if output_path.exists() and output_path.stat().st_size > 0:
                        # Open file
                        try:
                            os.startfile(str(output_path))
                        except Exception as open_err:
                            logger.warning(f"Could not open file: {open_err}")
                        
                        page.snack_bar = ft.SnackBar(
                            ft.Text(f"Excel fájl létrehozva: {output_path.name}"),
                            bgcolor=DesignSystem.SUCCESS
                        )
                    else:
                        error_msg = f"Fájl nem jött létre vagy üres. Path: {output_path}"
                        logger.error(error_msg)
                        page.snack_bar = ft.SnackBar(
                            ft.Text(f"{translator.get_text('common.messages.error_occurred')}: {error_msg}"),
                            bgcolor=DesignSystem.ERROR
                        )
                    page.snack_bar.open = True
                    page.update()
                except Exception as ex:
                    import traceback
                    error_trace = traceback.format_exc()
                    logger.error(f"Excel export error: {ex}\n{error_trace}")
                    page.snack_bar = ft.SnackBar(
                        ft.Text(f"{translator.get_text('common.messages.error_occurred')}: {str(ex)}"),
                        bgcolor=DesignSystem.ERROR
                    )
                    page.snack_bar.open = True
                    page.update()
            
            # Show loading
            page.snack_bar = ft.SnackBar(
                ft.Text(translator.get_text("reports.excel_generating")),
                bgcolor=DesignSystem.SECONDARY
            )
            page.snack_bar.open = True
            page.update()
            
            # Run in background thread
            thread = threading.Thread(target=export_thread, daemon=True)
            thread.start()
        
        # Create file picker
        file_picker = ft.FilePicker(on_result=on_save_result)
        page.overlay.append(file_picker)
        page.update()
        
        # Generate default filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"reports_{timestamp}.xlsx"
        
        # Open save dialog
        file_picker.save_file(
            dialog_title=translator.get_text("reports.save_excel") if hasattr(translator, 'get_text') else "Excel fájl mentése / Save Excel file",
            file_name=default_filename,
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["xlsx"],
        )
    
    def _build_statistics_cards(self, stats: dict) -> ft.Row:
        """Build statistics cards"""
        cost_stats = stats.get('cost', {})
        time_stats = stats.get('time', {})
        task_stats = stats.get('tasks', {})
        
        def _format_currency(value: float) -> str:
            return f"{value:,.2f} €"
        
        def _format_hours(value: float) -> str:
            return f"{value:.2f} óra"
        
        cards = ft.Row([
            # Cost card
            ft.Container(
                content=ft.Column([
                    ft.Text(
                        translator.get_text("reports.total_cost") if hasattr(translator, 'get_text') else "Össz Költség / Total Cost",
                        size=14,
                        color=DesignSystem.TEXT_SECONDARY,
                    ),
                    ft.Text(
                        _format_currency(cost_stats.get('total_cost', 0)),
                        size=28,
                        weight=ft.FontWeight.W_700,
                        color=DesignSystem.SUCCESS,
                    ),
                    ft.Text(
                        f"Munkalap: {_format_currency(cost_stats.get('worksheet_cost', 0))}",
                        size=12,
                        color=DesignSystem.TEXT_SECONDARY,
                    ),
                    ft.Text(
                        f"Szerviz: {_format_currency(cost_stats.get('service_cost', 0))}",
                        size=12,
                        color=DesignSystem.TEXT_SECONDARY,
                    ),
                ], spacing=4),
                padding=20,
                bgcolor=DesignSystem.PRIMARY_LIGHT,
                border_radius=12,
                expand=True,
            ),
            
            # Time card
            ft.Container(
                content=ft.Column([
                    ft.Text(
                        translator.get_text("reports.total_time") if hasattr(translator, 'get_text') else "Össz Idő / Total Time",
                        size=14,
                        color=DesignSystem.TEXT_SECONDARY,
                    ),
                    ft.Text(
                        _format_hours(time_stats.get('total_time_hours', 0)),
                        size=28,
                        weight=ft.FontWeight.W_700,
                        color=DesignSystem.SECONDARY,
                    ),
                    ft.Text(
                        f"Leállás: {_format_hours(time_stats.get('worksheet_downtime_hours', 0))}",
                        size=12,
                        color=DesignSystem.TEXT_SECONDARY,
                    ),
                    ft.Text(
                        f"PM: {_format_hours(time_stats.get('pm_duration_hours', 0))}",
                        size=12,
                        color=DesignSystem.TEXT_SECONDARY,
                    ),
                ], spacing=4),
                padding=20,
                bgcolor=DesignSystem.SECONDARY_LIGHT,
                border_radius=12,
                expand=True,
            ),
            
            # Tasks card
            ft.Container(
                content=ft.Column([
                    ft.Text(
                        translator.get_text("reports.total_tasks") if hasattr(translator, 'get_text') else "Össz Feladat / Total Tasks",
                        size=14,
                        color=DesignSystem.TEXT_SECONDARY,
                    ),
                    ft.Text(
                        str(task_stats.get('total_tasks', 0)),
                        size=28,
                        weight=ft.FontWeight.W_700,
                        color=DesignSystem.WARNING,
                    ),
                    ft.Text(
                        f"Munkalapok: {task_stats.get('worksheet_count', 0)}",
                        size=12,
                        color=DesignSystem.TEXT_SECONDARY,
                    ),
                    ft.Text(
                        f"PM: {task_stats.get('pm_count', 0)}",
                        size=12,
                        color=DesignSystem.TEXT_SECONDARY,
                    ),
                ], spacing=4),
                padding=20,
                bgcolor="#FFFBEB",  # Amber-50, keep for warning background
                border_radius=12,
                expand=True,
            ),
        ], spacing=16)
        
        return cards
    
    def _build_charts_section(self, stats: dict, page: ft.Page) -> ft.Column:
        """Build charts section with visual charts"""
        cost_stats = stats.get('cost', {})
        time_stats = stats.get('time', {})
        task_stats = stats.get('tasks', {})
        
        # Get comparison data for all periods
        ctx = get_app_context()
        user_id = ctx.user_id if ctx and self.show_personal else None
        all_periods_stats = get_period_comparison(
            self.periods, 
            user_id,
            self.filter_machine_id,
            self.filter_status,
            self.filter_priority
        )
        
        # Generate charts (with error handling)
        try:
            cost_chart_path = generate_cost_chart(all_periods_stats)
        except Exception as ex:
            logger.error(f"Error generating cost chart: {ex}")
            cost_chart_path = None
        
        try:
            time_chart_path = generate_time_chart(all_periods_stats)
        except Exception as ex:
            logger.error(f"Error generating time chart: {ex}")
            time_chart_path = None
        
        try:
            tasks_chart_path = generate_tasks_chart(all_periods_stats)
        except Exception as ex:
            logger.error(f"Error generating tasks chart: {ex}")
            tasks_chart_path = None
        
        try:
            tasks_pie_chart_path = generate_tasks_pie_chart(all_periods_stats, "year")
        except Exception as ex:
            logger.error(f"Error generating tasks pie chart: {ex}")
            tasks_pie_chart_path = None
        
        charts_column = ft.Column([
            ft.Text(
                translator.get_text("reports.charts") if hasattr(translator, 'get_text') else "Grafikonok és Kimutatások / Charts and Reports",
                size=20,
                weight=ft.FontWeight.BOLD,
            ),
            
            # Period comparison table (summary at the top)
            self._build_period_comparison_table(all_periods_stats),
            
            # Cost section: Chart first, then table below
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text(
                            translator.get_text("reports.cost_breakdown") if hasattr(translator, 'get_text') else "Költség Bontás / Cost Breakdown",
                            size=18,
                            weight=ft.FontWeight.W_700,
                        ),
                        self._build_chart_image(cost_chart_path, 900, 500, page),
                    ], spacing=16),
                    padding=20,
                ),
            ),
            ft.Card(
                content=ft.Container(
                    content=self._build_cost_breakdown_table_content(all_periods_stats),
                    padding=20,
                ),
            ),
            
            # Time section: Chart first, then table below
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text(
                            translator.get_text("reports.time_breakdown") if hasattr(translator, 'get_text') else "Idő Bontás / Time Breakdown",
                            size=18,
                            weight=ft.FontWeight.W_700,
                        ),
                        self._build_chart_image(time_chart_path, 900, 500, page),
                    ], spacing=16),
                    padding=20,
                ),
            ),
            ft.Card(
                content=ft.Container(
                    content=self._build_time_breakdown_table_content(all_periods_stats),
                    padding=20,
                ),
            ),
            
            # Tasks section: Charts first, then table below
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text(
                            translator.get_text("reports.tasks_breakdown") if hasattr(translator, 'get_text') else "Feladat Bontás / Tasks Breakdown",
                            size=18,
                            weight=ft.FontWeight.W_700,
                        ),
                        ft.Row([
                            ft.Container(
                                content=ft.Column([
                                    ft.Text(
                                        translator.get_text("reports.tasks_breakdown") if hasattr(translator, 'get_text') else "Feladat Bontás / Tasks Breakdown",
                                        size=14,
                                        weight=ft.FontWeight.W_700,
                                    ),
                                    self._build_chart_image(tasks_chart_path, 450, 400, page),
                                ], spacing=12),
                                expand=1,
                            ),
                            ft.Container(
                                content=ft.Column([
                                    ft.Text(
                                        translator.get_text("reports.tasks_distribution") if hasattr(translator, 'get_text') else "Feladat Eloszlás / Tasks Distribution",
                                        size=14,
                                        weight=ft.FontWeight.W_700,
                                    ),
                                    self._build_chart_image(tasks_pie_chart_path, 450, 400, page),
                                ], spacing=12),
                                expand=1,
                            ),
                        ], spacing=16),
                    ], spacing=16),
                    padding=20,
                ),
            ),
            ft.Card(
                content=ft.Container(
                    content=self._build_tasks_breakdown_table_content(all_periods_stats),
                    padding=20,
                ),
            ),
            
            ft.Text(
                translator.get_text("reports.excel_note") if hasattr(translator, 'get_text') else "Megjegyzés: Részletes grafikonok az Excel exportban találhatók. / Note: Detailed charts are available in Excel export.",
                size=12,
                color=DesignSystem.TEXT_SECONDARY,
                italic=True,
            ),
            
            # Technician/Personal statistics section
            ft.Divider(height=1),
            self._build_technician_statistics_section(page),
        ], spacing=20)
        
        return charts_column
    
    def _build_chart_image(self, chart_path: Optional[Path], width: int, height: int, page: ft.Page = None) -> ft.Control:
        """Build chart image component"""
        if chart_path is None:
            return ft.Container(
                content=ft.Text("Grafikon nem elérhető / Chart not available", color=DesignSystem.TEXT_SECONDARY),
                width=width,
                height=height,
                alignment=ft.alignment.center,
            )
        
        if not chart_path.exists():
            logger.warning(f"Chart file does not exist: {chart_path}")
            return ft.Container(
                content=ft.Text("Grafikon fájl nem található / Chart file not found", color=DesignSystem.TEXT_SECONDARY),
                width=width,
                height=height,
                alignment=ft.alignment.center,
            )
        
        try:
            # Use file path directly - Flet should handle local file paths
            abs_path = str(chart_path.absolute())
            
            # Verify file exists and is readable
            if not chart_path.exists():
                raise FileNotFoundError(f"Chart file not found: {chart_path}")
            
            # Check file size (avoid loading huge files)
            file_size = chart_path.stat().st_size
            if file_size > 5 * 1024 * 1024:  # 5MB limit
                logger.warning(f"Chart file too large ({file_size} bytes), skipping: {chart_path}")
                return ft.Container(
                    content=ft.Text("Grafikon fájl túl nagy / Chart file too large", color=DesignSystem.TEXT_SECONDARY),
                    width=width,
                    height=height,
                    alignment=ft.alignment.center,
                )
            
            # Use file path directly - Flet supports local file paths
            # Make chart clickable with tooltip
            chart_image = ft.Image(
                src=abs_path,
                width=width,
                height=height,
                fit=ft.ImageFit.CONTAIN,
            )
            
            # Wrap in GestureDetector for click handling and add tooltip
            if page:
                return ft.GestureDetector(
                    content=ft.Tooltip(
                        message=translator.get_text("reports.chart_tooltip") if hasattr(translator, 'get_text') else "Kattints a részletekért / Click for details",
                        content=chart_image,
                    ),
                    on_tap=lambda e: self._on_chart_click(chart_path, page),
                )
            else:
                # If page is not available, just return the image with tooltip
                return ft.Tooltip(
                    message=translator.get_text("reports.chart_tooltip") if hasattr(translator, 'get_text') else "Kattints a részletekért / Click for details",
                    content=chart_image,
                )
        except FileNotFoundError as e:
            logger.warning(f"Chart file not found: {e}")
            return ft.Container(
                content=ft.Text("Grafikon fájl nem található / Chart file not found", color=DesignSystem.TEXT_SECONDARY),
                width=width,
                height=height,
                alignment=ft.alignment.center,
            )
        except Exception as e:
            logger.error(f"Error loading chart image: {e}", exc_info=True)
            return ft.Container(
                content=ft.Text(f"Grafikon betöltési hiba / Chart load error: {str(e)[:50]}", color=DesignSystem.TEXT_SECONDARY),
                width=width,
                height=height,
                alignment=ft.alignment.center,
            )
    
    def _build_cost_breakdown_table_content(self, all_periods_stats: dict) -> ft.Column:
        """Build cost breakdown table content (without Card wrapper)"""
        period_labels = {
            "day": "Nap / Day",
            "week": "Hét / Week",
            "month": "Hó / Month",
            "year": "Év / Year"
        }
        
        rows = [
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(period_labels.get(period, period))),
                    ft.DataCell(ft.Text(format_price(all_periods_stats.get(period, {}).get('cost', {}).get('worksheet_cost', 0)))),
                    ft.DataCell(ft.Text(format_price(all_periods_stats.get(period, {}).get('cost', {}).get('service_cost', 0)))),
                    ft.DataCell(ft.Text(format_price(all_periods_stats.get(period, {}).get('cost', {}).get('total_cost', 0)), weight=ft.FontWeight.BOLD)),
                ]
            )
            for period in self.periods
        ]
        
        return ft.Column([
            ft.Text(
                translator.get_text("reports.cost_breakdown") if hasattr(translator, 'get_text') else "Költség Kimutatás / Cost Report",
                size=16,
                weight=ft.FontWeight.BOLD,
            ),
            ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text(translator.get_text("reports.period") if hasattr(translator, 'get_text') else "Időszak / Period")),
                    ft.DataColumn(ft.Text(translator.get_text("reports.worksheet_cost") if hasattr(translator, 'get_text') else "Munkalap Költség / Worksheet Cost")),
                    ft.DataColumn(ft.Text(translator.get_text("reports.service_cost") if hasattr(translator, 'get_text') else "Szerviz Költség / Service Cost")),
                    ft.DataColumn(ft.Text(translator.get_text("reports.total_cost") if hasattr(translator, 'get_text') else "Összesen / Total")),
                ],
                rows=rows,
                border=ft.border.all(1, DesignSystem.BORDER_COLOR),
            ),
        ], spacing=12)
    
    def _build_time_breakdown_table_content(self, all_periods_stats: dict) -> ft.Column:
        """Build time breakdown table content (without Card wrapper)"""
        period_labels = {
            "day": "Nap / Day",
            "week": "Hét / Week",
            "month": "Hó / Month",
            "year": "Év / Year"
        }
        
        def _format_hours(value: float) -> str:
            return f"{value:.2f} óra"
        
        rows = [
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(period_labels.get(period, period))),
                    ft.DataCell(ft.Text(_format_hours(all_periods_stats.get(period, {}).get('time', {}).get('worksheet_downtime_hours', 0)))),
                    ft.DataCell(ft.Text(_format_hours(all_periods_stats.get(period, {}).get('time', {}).get('pm_duration_hours', 0)))),
                    ft.DataCell(ft.Text(_format_hours(all_periods_stats.get(period, {}).get('time', {}).get('service_duration_hours', 0)))),
                    ft.DataCell(ft.Text(_format_hours(all_periods_stats.get(period, {}).get('time', {}).get('total_time_hours', 0)), weight=ft.FontWeight.BOLD)),
                ]
            )
            for period in self.periods
        ]
        
        return ft.Column([
            ft.Text(
                translator.get_text("reports.time_breakdown") if hasattr(translator, 'get_text') else "Idő Kimutatás / Time Report",
                size=16,
                weight=ft.FontWeight.BOLD,
            ),
            ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text(translator.get_text("reports.period") if hasattr(translator, 'get_text') else "Időszak / Period")),
                    ft.DataColumn(ft.Text(translator.get_text("reports.downtime") if hasattr(translator, 'get_text') else "Leállás / Downtime")),
                    ft.DataColumn(ft.Text(translator.get_text("reports.pm_time") if hasattr(translator, 'get_text') else "PM Idő / PM Time")),
                    ft.DataColumn(ft.Text(translator.get_text("reports.service_time") if hasattr(translator, 'get_text') else "Szerviz Idő / Service Time")),
                    ft.DataColumn(ft.Text(translator.get_text("reports.total_time") if hasattr(translator, 'get_text') else "Összesen / Total")),
                ],
                rows=rows,
                border=ft.border.all(1, DesignSystem.BORDER_COLOR),
            ),
        ], spacing=12)
    
    def _build_tasks_breakdown_table_content(self, all_periods_stats: dict) -> ft.Column:
        """Build tasks breakdown table content (without Card wrapper)"""
        period_labels = {
            "day": "Nap / Day",
            "week": "Hét / Week",
            "month": "Hó / Month",
            "year": "Év / Year"
        }
        
        rows = [
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(period_labels.get(period, period))),
                    ft.DataCell(ft.Text(str(all_periods_stats.get(period, {}).get('tasks', {}).get('worksheet_count', 0)))),
                    ft.DataCell(ft.Text(str(all_periods_stats.get(period, {}).get('tasks', {}).get('pm_count', 0)))),
                    ft.DataCell(ft.Text(str(all_periods_stats.get(period, {}).get('tasks', {}).get('total_tasks', 0)), weight=ft.FontWeight.BOLD)),
                ]
            )
            for period in self.periods
        ]
        
        return ft.Column([
            ft.Text(
                translator.get_text("reports.tasks_breakdown") if hasattr(translator, 'get_text') else "Feladat Kimutatás / Tasks Report",
                size=16,
                weight=ft.FontWeight.BOLD,
            ),
            ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text(translator.get_text("reports.period") if hasattr(translator, 'get_text') else "Időszak / Period")),
                    ft.DataColumn(ft.Text(translator.get_text("reports.worksheets") if hasattr(translator, 'get_text') else "Munkalapok / Worksheets")),
                    ft.DataColumn(ft.Text(translator.get_text("reports.pm_tasks") if hasattr(translator, 'get_text') else "PM Feladatok / PM Tasks")),
                    ft.DataColumn(ft.Text(translator.get_text("reports.total_tasks") if hasattr(translator, 'get_text') else "Összesen / Total")),
                ],
                rows=rows,
                border=ft.border.all(1, DesignSystem.BORDER_COLOR),
            ),
        ], spacing=12)
    
    def _build_technician_statistics_section(self, page: ft.Page) -> ft.Card:
        """Build technician/personal statistics section"""
        ctx = get_app_context()
        user_id = ctx.user_id if ctx and self.show_personal else None
        
        # Get technician statistics
        try:
            technician_stats = get_technician_statistics(self.current_period)
        except Exception as e:
            logger.error(f"Error getting technician statistics: {e}")
            technician_stats = []
        
        if not technician_stats:
            return ft.Card(
                content=ft.Container(
                    content=ft.Text(
                        translator.get_text("reports.no_technician_data") if hasattr(translator, 'get_text') else "Nincs adat karbantartókra / No technician data available",
                        color=DesignSystem.TEXT_SECONDARY,
                    ),
                    padding=20,
                ),
            )
        
        def _format_hours(value: float) -> str:
            return f"{value:.2f} óra"
        
        # Filter by search text
        if self.technician_search_text:
            search_lower = self.technician_search_text.lower()
            technician_stats = [
                tech for tech in technician_stats
                if search_lower in (tech.get('full_name') or '').lower() or 
                   search_lower in (tech.get('username') or '').lower()
            ]
        
        # Sort technician stats
        if self.technician_sort_column == 'name':
            technician_stats.sort(key=lambda x: (x['full_name'] or x['username']).lower(), 
                                 reverse=not self.technician_sort_ascending)
        elif self.technician_sort_column == 'tasks':
            technician_stats.sort(key=lambda x: x['tasks_completed'], 
                                 reverse=not self.technician_sort_ascending)
        elif self.technician_sort_column == 'downtime':
            technician_stats.sort(key=lambda x: x.get('downtime_hours', 0), 
                                 reverse=not self.technician_sort_ascending)
        elif self.technician_sort_column == 'time':
            technician_stats.sort(key=lambda x: x.get('total_hours', 0), 
                                 reverse=not self.technician_sort_ascending)
        
        # Build table rows with clickable cells
        rows = []
        for tech in technician_stats:
            tech_name = tech['full_name'] or tech['username']
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(
                            ft.GestureDetector(
                                content=ft.Text(tech_name, color="#6366F1"),
                                on_tap=lambda e, t=tech: self._on_technician_row_click(t, page),
                            )
                        ),
                        ft.DataCell(ft.Text(str(tech['tasks_completed']))),
                        ft.DataCell(ft.Text(str(tech['worksheets_count']))),
                        ft.DataCell(ft.Text(str(tech['pm_count']))),
                        ft.DataCell(ft.Text(_format_hours(tech['downtime_hours']))),
                        ft.DataCell(ft.Text(_format_hours(tech['total_hours']))),
                    ]
                )
            )
        
        # Search field
        search_field = ft.TextField(
            label=translator.get_text("reports.search_technician") if hasattr(translator, 'get_text') else "Keresés / Search",
            hint_text=translator.get_text("reports.search_hint") if hasattr(translator, 'get_text') else "Karbantartó neve...",
            value=self.technician_search_text,
            width=300,
            on_change=lambda e: self._on_technician_search_change(e, page),
            prefix_icon=ft.Icons.SEARCH,
        )
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text(
                            translator.get_text("reports.technician_performance") if hasattr(translator, 'get_text') else "Karbantartók Teljesítménye / Technician Performance",
                            size=18,
                            weight=ft.FontWeight.W_700,
                            expand=True,
                        ),
                        search_field,
                    ], spacing=16),
                    ft.DataTable(
                        columns=[
                            ft.DataColumn(
                                ft.Text(translator.get_text("reports.technician") if hasattr(translator, 'get_text') else "Karbantartó / Technician"),
                                on_sort=lambda e: self._sort_technician_table(e, 'name', page),
                            ),
                            ft.DataColumn(
                                ft.Text(translator.get_text("reports.tasks_completed") if hasattr(translator, 'get_text') else "Elvégzett Feladatok / Tasks Completed"),
                                on_sort=lambda e: self._sort_technician_table(e, 'tasks', page),
                            ),
                            ft.DataColumn(ft.Text(translator.get_text("reports.worksheets") if hasattr(translator, 'get_text') else "Munkalapok / Worksheets")),
                            ft.DataColumn(ft.Text(translator.get_text("reports.pm_tasks") if hasattr(translator, 'get_text') else "PM Feladatok / PM Tasks")),
                            ft.DataColumn(
                                ft.Text(translator.get_text("reports.downtime") if hasattr(translator, 'get_text') else "Állásidő / Downtime"),
                                on_sort=lambda e: self._sort_technician_table(e, 'downtime', page),
                            ),
                            ft.DataColumn(
                                ft.Text(translator.get_text("reports.total_time") if hasattr(translator, 'get_text') else "Össz Idő / Total Time"),
                                on_sort=lambda e: self._sort_technician_table(e, 'time', page),
                            ),
                        ],
                        rows=rows,
                        border=ft.border.all(1, DesignSystem.BORDER_COLOR),
                        sort_column_index={
                            'name': 0,
                            'tasks': 1,
                            'downtime': 4,
                            'time': 5
                        }.get(self.technician_sort_column, 1),
                        sort_ascending=self.technician_sort_ascending,
                    ),
                ], spacing=16),
                padding=20,
            ),
        )
    
    def _build_filters_section(self, page: ft.Page) -> ft.Container:
        """Build filters section"""
        # Load machines for filter
        try:
            machines = asset_service.list_machines()
            machine_options = [ft.dropdown.Option(None, "Összes / All")]
            for machine in machines:
                # Store as string to match dropdown behavior
                machine_options.append(ft.dropdown.Option(str(machine.id), machine.name))
        except Exception as e:
            logger.error(f"Error loading machines: {e}")
            machine_options = [ft.dropdown.Option(None, "Összes / All")]
        
        machine_filter = ft.Dropdown(
            label=translator.get_text("reports.filter_machine") if hasattr(translator, 'get_text') else "Gép / Machine",
            options=machine_options,
            value=str(self.filter_machine_id) if self.filter_machine_id is not None else None,
            width=200,
            on_change=lambda e: self._on_filter_change(e, page, 'machine'),
        )
        
        status_filter = ft.Dropdown(
            label=translator.get_text("reports.filter_status") if hasattr(translator, 'get_text') else "Státusz / Status",
            options=[
                ft.dropdown.Option(None, "Összes / All"),
                ft.dropdown.Option("Open", "Nyitott / Open"),
                ft.dropdown.Option("Closed", "Lezárt / Closed"),
                ft.dropdown.Option("Waiting for Parts", "Alkatrészre vár / Waiting for Parts"),
            ],
            value=self.filter_status,
            width=200,
            on_change=lambda e: self._on_filter_change(e, page, 'status'),
        )
        
        priority_filter = ft.Dropdown(
            label=translator.get_text("reports.filter_priority") if hasattr(translator, 'get_text') else "Prioritás / Priority",
            options=[
                ft.dropdown.Option(None, "Összes / All"),
                ft.dropdown.Option("low", "Alacsony / Low"),
                ft.dropdown.Option("normal", "Normál / Normal"),
                ft.dropdown.Option("high", "Magas / High"),
                ft.dropdown.Option("urgent", "Sürgős / Urgent"),
            ],
            value=self.filter_priority,
            width=200,
            on_change=lambda e: self._on_filter_change(e, page, 'priority'),
        )
        
        # Collapsible filters
        filters_content = ft.Row([
            machine_filter,
            status_filter,
            priority_filter,
        ], spacing=16) if self.expanded_filters else ft.Container(height=0, visible=False)
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.EXPAND_MORE if not self.expanded_filters else ft.Icons.EXPAND_LESS,
                        on_click=lambda e: self._toggle_filters(e, page),
                        tooltip="Szűrők megjelenítése / Show filters",
                    ),
                    ft.Text(
                        translator.get_text("reports.filters") if hasattr(translator, 'get_text') else "Szűrők / Filters",
                        size=16,
                        weight=ft.FontWeight.W_700,
                    ),
                ], spacing=8),
                filters_content,
            ], spacing=8),
            padding=10,
            visible=True,
        )
    
    def _toggle_filters(self, e, page: ft.Page):
        """Toggle filters visibility"""
        self.expanded_filters = not self.expanded_filters
        page.go("/reports")
    
    def _on_filter_change(self, e, page: ft.Page, filter_type: str):
        """Handle filter change"""
        try:
            if filter_type == 'machine':
                # Convert to int if not None, as machine_id must be int
                value = e.control.value
                if value is None or value == "" or value == "None":
                    self.filter_machine_id = None
                else:
                    try:
                        self.filter_machine_id = int(value)
                    except (ValueError, TypeError):
                        self.filter_machine_id = None
                logger.info(f"Filter changed - machine_id: {self.filter_machine_id}")
            elif filter_type == 'status':
                self.filter_status = e.control.value if e.control.value and e.control.value != "None" else None
                logger.info(f"Filter changed - status: {self.filter_status}")
            elif filter_type == 'priority':
                self.filter_priority = e.control.value if e.control.value and e.control.value != "None" else None
                logger.info(f"Filter changed - priority: {self.filter_priority}")
            
            # Log current filter values before route change
            logger.info(f"Filters before route change - machine_id: {self.filter_machine_id}, status: {self.filter_status}, priority: {self.filter_priority}")
            
            # Force route change to rebuild view with new filters
            # The ReportsScreen object is reused, so filter values persist
            # Use page.route to set route and then trigger render
            if hasattr(page, 'route'):
                page.route = "/reports"
            page.go("/reports")
        except Exception as ex:
            logger.error(f"Error in filter change: {ex}", exc_info=True)
            page.snack_bar = ft.SnackBar(
                ft.Text(f"Szűrő hiba: {str(ex)}"),
                bgcolor=DesignSystem.ERROR
            )
            page.snack_bar.open = True
            page.update()
    
    def _on_print(self, e, page: ft.Page):
        """Print reports view - Generate and open Excel file for printing"""
        def on_save_result(e: ft.FilePickerResultEvent):
            if e.path is None:
                # User cancelled
                page.snack_bar = ft.SnackBar(
                    ft.Text(translator.get_text("worksheets.download_cancelled")),
                    bgcolor=DesignSystem.TEXT_SECONDARY
                )
                page.snack_bar.open = True
                page.update()
                return
            
            def export_and_open_thread():
                try:
                    ctx = get_app_context()
                    user_id = ctx.user_id if ctx and self.show_personal else None
                    
                    # Ensure .xlsx extension
                    save_path = Path(e.path)
                    if not save_path.suffix.lower() == '.xlsx':
                        save_path = save_path.with_suffix('.xlsx')
                    
                    logger.info(f"Generating Excel file for printing to: {save_path}")
                    
                    # Generate Excel file with all reports and charts in one workbook
                    output_path = export_reports_to_excel(
                        periods=self.periods,
                        user_id=user_id,
                        output_path=save_path
                    )
                    
                    logger.info(f"Excel file generated: {output_path}, exists: {output_path.exists()}")
                    
                    # Verify file was created
                    if output_path.exists() and output_path.stat().st_size > 0:
                        # Open file (user can print it)
                        try:
                            import os
                            os.startfile(str(output_path))
                            page.snack_bar = ft.SnackBar(
                                ft.Text(translator.get_text("reports.excel_opened_for_printing") if hasattr(translator, 'get_text') else f"Excel fájl megnyitva nyomtatáshoz: {output_path.name}"),
                                bgcolor=DesignSystem.SUCCESS
                            )
                        except Exception as open_err:
                            logger.warning(f"Could not open file: {open_err}")
                            page.snack_bar = ft.SnackBar(
                                ft.Text(translator.get_text("reports.excel_generated_but_not_opened") if hasattr(translator, 'get_text') else f"Excel fájl létrehozva: {output_path.name}"),
                                bgcolor=DesignSystem.SUCCESS
                            )
                    else:
                        error_msg = f"Fájl nem jött létre vagy üres. Path: {output_path}"
                        logger.error(error_msg)
                        page.snack_bar = ft.SnackBar(
                            ft.Text(f"{translator.get_text('common.messages.error_occurred')}: {error_msg}"),
                            bgcolor=DesignSystem.ERROR
                        )
                    page.snack_bar.open = True
                    page.update()
                except Exception as ex:
                    import traceback
                    error_trace = traceback.format_exc()
                    logger.error(f"Excel export error: {ex}\n{error_trace}")
                    page.snack_bar = ft.SnackBar(
                        ft.Text(f"{translator.get_text('common.messages.error_occurred')}: {str(ex)}"),
                        bgcolor=DesignSystem.ERROR
                    )
                    page.snack_bar.open = True
                    page.update()
            
            # Show loading
            page.snack_bar = ft.SnackBar(
                ft.Text(translator.get_text("reports.excel_generating")),
                bgcolor=DesignSystem.SECONDARY
            )
            page.snack_bar.open = True
            page.update()
            
            # Run in background thread
            thread = threading.Thread(target=export_and_open_thread, daemon=True)
            thread.start()
        
        # Create file picker
        file_picker = ft.FilePicker(on_result=on_save_result)
        page.overlay.append(file_picker)
        page.update()
        
        # Generate default filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"reports_for_printing_{timestamp}.xlsx"
        
        # Open save dialog
        file_picker.save_file(
            dialog_title=translator.get_text("reports.save_excel_for_printing") if hasattr(translator, 'get_text') else "Excel fájl mentése nyomtatáshoz / Save Excel file for printing",
            file_name=default_filename,
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["xlsx"],
        )
    
    def _build_extended_statistics_section(self, trend_stats: dict, avg_stats: dict) -> ft.Column:
        """Build extended statistics section with trends and averages"""
        sections = []
        
        # Trend comparison
        if trend_stats.get('_comparison'):
            comparison = trend_stats['_comparison']
            sections.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text(
                                translator.get_text("reports.trend_analysis") if hasattr(translator, 'get_text') else "Trend Elemzés / Trend Analysis",
                                size=16,
                                weight=ft.FontWeight.W_700,
                            ),
                            ft.Row([
                                ft.Container(
                                    content=ft.Column([
                                        ft.Text("Költség változás / Cost Change", size=12),
                                        ft.Text(
                                            f"{comparison.get('cost_change', 0):+.1f}%",
                                            size=18,
                                            weight=ft.FontWeight.W_700,
                                            color="#10B981" if comparison.get('cost_change', 0) < 0 else "#EF4444",
                                        ),
                                    ]),
                                    expand=1,
                                ),
                                ft.Container(
                                    content=ft.Column([
                                        ft.Text("Idő változás / Time Change", size=12),
                                        ft.Text(
                                            f"{comparison.get('time_change', 0):+.1f}%",
                                            size=18,
                                            weight=ft.FontWeight.W_700,
                                            color=DesignSystem.SUCCESS if comparison.get('time_change', 0) < 0 else DesignSystem.ERROR,
                                        ),
                                    ]),
                                    expand=1,
                                ),
                                ft.Container(
                                    content=ft.Column([
                                        ft.Text("Feladat változás / Tasks Change", size=12),
                                        ft.Text(
                                            f"{comparison.get('tasks_change', 0):+.1f}%",
                                            size=18,
                                            weight=ft.FontWeight.W_700,
                                            color=DesignSystem.SUCCESS if comparison.get('tasks_change', 0) > 0 else DesignSystem.ERROR,
                                        ),
                                    ]),
                                    expand=1,
                                ),
                            ], spacing=16),
                        ], spacing=12),
                        padding=20,
                    ),
                )
            )
        
        # Averages
        if avg_stats:
            sections.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text(
                                translator.get_text("reports.averages") if hasattr(translator, 'get_text') else "Átlagok / Averages",
                                size=16,
                                weight=ft.FontWeight.W_700,
                            ),
                            ft.DataTable(
                                columns=[
                                    ft.DataColumn(ft.Text(translator.get_text("reports.metric") if hasattr(translator, 'get_text') else "Mutató / Metric")),
                                    ft.DataColumn(ft.Text(translator.get_text("reports.value") if hasattr(translator, 'get_text') else "Érték / Value")),
                                ],
                                rows=[
                                    ft.DataRow(cells=[
                                        ft.DataCell(ft.Text(translator.get_text("reports.avg_cost_per_task"))),
                                        ft.DataCell(ft.Text(format_price(avg_stats.get('avg_cost_per_task', 0)))),
                                    ]),
                                    ft.DataRow(cells=[
                                        ft.DataCell(ft.Text(translator.get_text("reports.avg_time_per_task"))),
                                        ft.DataCell(ft.Text(f"{avg_stats.get('avg_time_per_task', 0):.2f} óra")),
                                    ]),
                                    ft.DataRow(cells=[
                                        ft.DataCell(ft.Text(translator.get_text("reports.avg_cost_per_hour"))),
                                        ft.DataCell(ft.Text(format_price(avg_stats.get('avg_cost_per_hour', 0)))),
                                    ]),
                                    ft.DataRow(cells=[
                                        ft.DataCell(ft.Text(translator.get_text("reports.tasks_per_day"))),
                                        ft.DataCell(ft.Text(f"{avg_stats.get('tasks_per_day', 0):.2f}")),
                                    ]),
                                ],
                                border=ft.border.all(1, DesignSystem.BORDER_COLOR),
                            ),
                        ], spacing=12),
                        padding=20,
                    ),
                )
            )
        
        return ft.Column(sections, spacing=16) if sections else ft.Container()
    
    def _build_machine_statistics_section(self, machine_stats: list) -> ft.Card:
        """Build machine statistics section"""
        if not machine_stats:
            return ft.Container()
        
        rows = []
        for machine in machine_stats:
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(machine['machine_name'])),
                        ft.DataCell(ft.Text(str(machine['worksheet_count']))),
                        ft.DataCell(ft.Text(f"{machine['total_downtime_hours']:.2f} óra")),
                        ft.DataCell(ft.Text(format_price(machine['total_cost']))),
                    ]
                )
            )
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text(
                        translator.get_text("reports.machine_statistics") if hasattr(translator, 'get_text') else "Gépek Statisztikái / Machine Statistics",
                        size=18,
                        weight=ft.FontWeight.W_700,
                    ),
                    ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text(translator.get_text("reports.machine") if hasattr(translator, 'get_text') else "Gép / Machine")),
                            ft.DataColumn(ft.Text(translator.get_text("reports.worksheets") if hasattr(translator, 'get_text') else "Munkalapok / Worksheets")),
                            ft.DataColumn(ft.Text(translator.get_text("reports.downtime") if hasattr(translator, 'get_text') else "Leállás / Downtime")),
                            ft.DataColumn(ft.Text(translator.get_text("reports.total_cost") if hasattr(translator, 'get_text') else "Össz Költség / Total Cost")),
                        ],
                        rows=rows,
                        border=ft.border.all(1, DesignSystem.BORDER_COLOR),
                    ),
                ], spacing=16),
                padding=20,
            ),
        )
    
    def _sort_technician_table(self, e, column: str, page: ft.Page):
        """Handle technician table sorting"""
        if self.technician_sort_column == column:
            self.technician_sort_ascending = not self.technician_sort_ascending
        else:
            self.technician_sort_column = column
            self.technician_sort_ascending = True
        page.go("/reports")
    
    def _on_technician_search_change(self, e, page: ft.Page):
        """Handle technician search text change"""
        self.technician_search_text = e.control.value or ""
        page.go("/reports")
    
    def _close_dialog(self, page: ft.Page):
        """Close dialog"""
        if page.dialog:
            page.dialog.open = False
            page.update()
    
    def _on_technician_row_click(self, tech: dict, page: ft.Page):
        """Handle technician row click - show detailed information"""
        try:
            # Create detail dialog
            detail_content = ft.Column([
                ft.Text(
                    tech.get('full_name') or tech.get('username') or "Ismeretlen / Unknown",
                    size=20,
                    weight=ft.FontWeight.W_700,
                ),
                ft.Divider(),
                ft.Text(f"{translator.get_text('reports.tasks_completed') if hasattr(translator, 'get_text') else 'Elvégzett Feladatok'}: {tech.get('tasks_completed', 0)}"),
                ft.Text(f"{translator.get_text('reports.worksheets') if hasattr(translator, 'get_text') else 'Munkalapok'}: {tech.get('worksheets_count', 0)}"),
                ft.Text(f"{translator.get_text('reports.pm_tasks') if hasattr(translator, 'get_text') else 'PM Feladatok'}: {tech.get('pm_count', 0)}"),
                ft.Text(f"{translator.get_text('reports.downtime') if hasattr(translator, 'get_text') else 'Állásidő'}: {tech.get('downtime_hours', 0):.2f} óra"),
                ft.Text(f"{translator.get_text('reports.total_time') if hasattr(translator, 'get_text') else 'Össz Idő'}: {tech.get('total_hours', 0):.2f} óra"),
            ], spacing=12, scroll=ft.ScrollMode.AUTO)
            
            dialog = ft.AlertDialog(
                title=ft.Text(translator.get_text("reports.technician_details")),
                content=detail_content,
                actions=[
                    ft.TextButton("Bezárás / Close", on_click=lambda e: self._close_dialog(page)),
                ],
            )
            
            page.dialog = dialog
            dialog.open = True
            page.update()
        except Exception as ex:
            logger.error(f"Error showing technician details: {ex}")
            page.snack_bar = ft.SnackBar(
                ft.Text(f"Hiba / Error: {str(ex)}"),
                bgcolor=DesignSystem.ERROR
            )
            page.snack_bar.open = True
            page.update()
    
    def _on_chart_click(self, chart_path: Path, page: ft.Page):
        """Handle chart click - show detailed view"""
        try:
            # Get chart statistics for detailed view
            ctx = get_app_context()
            user_id = ctx.user_id if ctx and self.show_personal else None
            
            stats = get_all_statistics(
                self.current_period,
                user_id,
                self.filter_machine_id,
                self.filter_status,
                self.filter_priority
            )
            
            # Create detail dialog
            detail_content = ft.Column([
                ft.Text(
                    translator.get_text("reports.chart_details") if hasattr(translator, 'get_text') else "Grafikon Részletek / Chart Details",
                    size=18,
                    weight=ft.FontWeight.W_700,
                ),
                ft.Divider(),
                ft.Text(f"Időszak / Period: {self.current_period}"),
                ft.Text(f"Össz Költség / Total Cost: {format_price(stats.get('cost', {}).get('total_cost', 0))}"),
                ft.Text(f"Össz Idő / Total Time: {stats.get('time', {}).get('total_time_hours', 0):.2f} óra"),
                ft.Text(f"Össz Feladat / Total Tasks: {stats.get('tasks', {}).get('total_tasks', 0)}"),
                ft.Container(height=10),
                ft.Text(
                    translator.get_text("reports.chart_file") if hasattr(translator, 'get_text') else f"Fájl / File: {chart_path.name}",
                    size=12,
                    color=DesignSystem.TEXT_SECONDARY,
                ),
            ], spacing=12, scroll=ft.ScrollMode.AUTO)
            
            dialog = ft.AlertDialog(
                title=ft.Text(translator.get_text("reports.chart_details")),
                content=detail_content,
                actions=[
                    ft.TextButton("Bezárás / Close", on_click=lambda e: self._close_dialog(page)),
                ],
            )
            
            page.dialog = dialog
            dialog.open = True
            page.update()
        except Exception as ex:
            logger.error(f"Error showing chart details: {ex}")
            page.snack_bar = ft.SnackBar(
                ft.Text(f"Hiba / Error: {str(ex)}"),
                bgcolor=DesignSystem.ERROR
            )
            page.snack_bar.open = True
            page.update()
    
    def _close_dialog(self, page: ft.Page):
        """Close dialog"""
        if page.dialog:
            page.dialog.open = False
            page.update()
    
    def _build_period_comparison_table(self, all_periods_stats: dict) -> ft.Card:
        """Build period comparison table"""
        period_labels = {
            "day": "Nap / Day",
            "week": "Hét / Week",
            "month": "Hó / Month",
            "year": "Év / Year"
        }
        
        def _format_hours(value: float) -> str:
            return f"{value:.2f} óra"
        
        rows = [
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(period_labels.get(period, period), weight=ft.FontWeight.BOLD)),
                    ft.DataCell(ft.Text(format_price(all_periods_stats.get(period, {}).get('cost', {}).get('total_cost', 0)))),
                    ft.DataCell(ft.Text(_format_hours(all_periods_stats.get(period, {}).get('time', {}).get('total_time_hours', 0)))),
                    ft.DataCell(ft.Text(str(all_periods_stats.get(period, {}).get('tasks', {}).get('total_tasks', 0)))),
                ]
            )
            for period in self.periods
        ]
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text(
                        translator.get_text("reports.period_comparison") if hasattr(translator, 'get_text') else "Időszak Összehasonlítás / Period Comparison",
                        size=16,
                        weight=ft.FontWeight.W_700,
                    ),
                    ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text(translator.get_text("reports.period") if hasattr(translator, 'get_text') else "Időszak / Period")),
                            ft.DataColumn(ft.Text(translator.get_text("reports.total_cost") if hasattr(translator, 'get_text') else "Össz Költség / Total Cost")),
                            ft.DataColumn(ft.Text(translator.get_text("reports.total_time") if hasattr(translator, 'get_text') else "Össz Idő / Total Time")),
                            ft.DataColumn(ft.Text(translator.get_text("reports.total_tasks") if hasattr(translator, 'get_text') else "Össz Feladat / Total Tasks")),
                        ],
                        rows=rows,
                        border=ft.border.all(1, DesignSystem.BORDER_COLOR),
                    ),
                ], spacing=12),
                padding=20,
            ),
        )
    
    def _build_cost_breakdown_table(self, all_periods_stats: dict) -> ft.Card:
        """Build cost breakdown table"""
        period_labels = {
            "day": "Nap / Day",
            "week": "Hét / Week",
            "month": "Hó / Month",
            "year": "Év / Year"
        }
        
        rows = [
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(period_labels.get(period, period))),
                    ft.DataCell(ft.Text(format_price(all_periods_stats.get(period, {}).get('cost', {}).get('worksheet_cost', 0)))),
                    ft.DataCell(ft.Text(format_price(all_periods_stats.get(period, {}).get('cost', {}).get('service_cost', 0)))),
                    ft.DataCell(ft.Text(format_price(all_periods_stats.get(period, {}).get('cost', {}).get('total_cost', 0)), weight=ft.FontWeight.BOLD)),
                ]
            )
            for period in self.periods
        ]
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text(
                        translator.get_text("reports.cost_breakdown") if hasattr(translator, 'get_text') else "Költség Bontás / Cost Breakdown",
                        size=16,
                        weight=ft.FontWeight.W_700,
                    ),
                    ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text(translator.get_text("reports.period") if hasattr(translator, 'get_text') else "Időszak / Period")),
                            ft.DataColumn(ft.Text(translator.get_text("reports.worksheet_cost") if hasattr(translator, 'get_text') else "Munkalap Költség / Worksheet Cost")),
                            ft.DataColumn(ft.Text(translator.get_text("reports.service_cost") if hasattr(translator, 'get_text') else "Szerviz Költség / Service Cost")),
                            ft.DataColumn(ft.Text(translator.get_text("reports.total_cost") if hasattr(translator, 'get_text') else "Összesen / Total")),
                        ],
                        rows=rows,
                        border=ft.border.all(1, DesignSystem.BORDER_COLOR),
                    ),
                ], spacing=12),
                padding=20,
            ),
        )
    
    def _build_time_breakdown_table(self, all_periods_stats: dict) -> ft.Card:
        """Build time breakdown table"""
        period_labels = {
            "day": "Nap / Day",
            "week": "Hét / Week",
            "month": "Hó / Month",
            "year": "Év / Year"
        }
        
        def _format_hours(value: float) -> str:
            return f"{value:.2f} óra"
        
        rows = [
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(period_labels.get(period, period))),
                    ft.DataCell(ft.Text(_format_hours(all_periods_stats.get(period, {}).get('time', {}).get('worksheet_downtime_hours', 0)))),
                    ft.DataCell(ft.Text(_format_hours(all_periods_stats.get(period, {}).get('time', {}).get('pm_duration_hours', 0)))),
                    ft.DataCell(ft.Text(_format_hours(all_periods_stats.get(period, {}).get('time', {}).get('service_duration_hours', 0)))),
                    ft.DataCell(ft.Text(_format_hours(all_periods_stats.get(period, {}).get('time', {}).get('total_time_hours', 0)), weight=ft.FontWeight.BOLD)),
                ]
            )
            for period in self.periods
        ]
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text(
                        translator.get_text("reports.time_breakdown") if hasattr(translator, 'get_text') else "Idő Bontás / Time Breakdown",
                        size=16,
                        weight=ft.FontWeight.W_700,
                    ),
                    ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text(translator.get_text("reports.period") if hasattr(translator, 'get_text') else "Időszak / Period")),
                            ft.DataColumn(ft.Text(translator.get_text("reports.downtime") if hasattr(translator, 'get_text') else "Leállás / Downtime")),
                            ft.DataColumn(ft.Text(translator.get_text("reports.pm_time") if hasattr(translator, 'get_text') else "PM Idő / PM Time")),
                            ft.DataColumn(ft.Text(translator.get_text("reports.service_time") if hasattr(translator, 'get_text') else "Szerviz Idő / Service Time")),
                            ft.DataColumn(ft.Text(translator.get_text("reports.total_time") if hasattr(translator, 'get_text') else "Összesen / Total")),
                        ],
                        rows=rows,
                        border=ft.border.all(1, DesignSystem.BORDER_COLOR),
                    ),
                ], spacing=12),
                padding=20,
            ),
        )
    
    def _build_tasks_breakdown_table(self, all_periods_stats: dict) -> ft.Card:
        """Build tasks breakdown table"""
        period_labels = {
            "day": "Nap / Day",
            "week": "Hét / Week",
            "month": "Hó / Month",
            "year": "Év / Year"
        }
        
        rows = [
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(period_labels.get(period, period))),
                    ft.DataCell(ft.Text(str(all_periods_stats.get(period, {}).get('tasks', {}).get('worksheet_count', 0)))),
                    ft.DataCell(ft.Text(str(all_periods_stats.get(period, {}).get('tasks', {}).get('pm_count', 0)))),
                    ft.DataCell(ft.Text(str(all_periods_stats.get(period, {}).get('tasks', {}).get('total_tasks', 0)), weight=ft.FontWeight.BOLD)),
                ]
            )
            for period in self.periods
        ]
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text(
                        translator.get_text("reports.tasks_breakdown") if hasattr(translator, 'get_text') else "Feladat Bontás / Tasks Breakdown",
                        size=16,
                        weight=ft.FontWeight.W_700,
                    ),
                    ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text(translator.get_text("reports.period") if hasattr(translator, 'get_text') else "Időszak / Period")),
                            ft.DataColumn(ft.Text(translator.get_text("reports.worksheets") if hasattr(translator, 'get_text') else "Munkalapok / Worksheets")),
                            ft.DataColumn(ft.Text(translator.get_text("reports.pm_tasks") if hasattr(translator, 'get_text') else "PM Feladatok / PM Tasks")),
                            ft.DataColumn(ft.Text(translator.get_text("reports.total_tasks") if hasattr(translator, 'get_text') else "Összesen / Total")),
                        ],
                        rows=rows,
                        border=ft.border.all(1, DesignSystem.BORDER_COLOR),
                    ),
                ], spacing=12),
                padding=20,
            ),
        )

