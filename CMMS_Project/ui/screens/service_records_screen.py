"""
Szervizelések áttekintése képernyő - Összesítő nézet PMHistory + Worksheet + ServiceRecord
"""

import flet as ft
# Compatibility for flet 0.23.2 - Icons are strings, not ft.Icons
if not hasattr(ft, 'Icons'):
    from utils.flet_icons import Icons
    ft.Icons = Icons
from collections import defaultdict
from datetime import datetime
from services import service_record_service
from services.context_service import get_app_context
from localization.translator import translator
from utils.currency import format_price
from ui.components.modern_components import DesignSystem


class ServiceRecordsScreen:
    def __init__(self, page: ft.Page):
        self.page = page
        self.current_tab = 0  # 0=all, 1=pm, 2=worksheets
        self.filter_machine_id = None
        self.filter_user_id = None
    
    def view(self, page: ft.Page):
        if not hasattr(self, 'page') or self.page is None:
            self.page = page
        
        records_list = ft.Column([], spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)
        
        def refresh_records(update_page=True):
            page_ref = self.page if hasattr(self, 'page') and self.page else page
            records_list.controls.clear()
            
            # Get combined records
            combined_records = service_record_service.get_all_service_records_combined(
                machine_id=self.filter_machine_id,
                user_id=self.filter_user_id
            )
            
            # Filter by tab type
            if self.current_tab == 1:  # PM Tasks only
                combined_records = [r for r in combined_records if r['type'] == 'pm_history']
            elif self.current_tab == 2:  # Worksheets only
                combined_records = [r for r in combined_records if r['type'] == 'worksheet']
            # else: all (tab 0)
            
            if not combined_records:
                records_list.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(name=ft.Icons.BUILD_CIRCLE, size=48, color="#9CA3AF"),
                            ft.Text("Nincs szervizelési rekord", size=16, color="#6B7280"),
                        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=40,
                        expand=True,
                    )
                )
            else:
                # Group by date (year/month/day)
                grouped_records = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
                
                # Hungarian month names
                month_names = {
                    1: "január", 2: "február", 3: "március", 4: "április",
                    5: "május", 6: "június", 7: "július", 8: "augusztus",
                    9: "szeptember", 10: "október", 11: "november", 12: "december"
                }
                
                for record in combined_records:
                    date = record['date']
                    if date:
                        year = date.year
                        month = date.month
                        day = date.day
                        grouped_records[year][month][day].append(record)
                
                # Build UI with grouped structure
                for year in sorted(grouped_records.keys(), reverse=True):
                    year_expansion = ft.ExpansionTile(
                        title=ft.Text(f"{year}. év", size=14, weight=ft.FontWeight.BOLD, color="#1F2937"),
                        leading=ft.Icon(ft.Icons.CALENDAR_MONTH, color="#6366F1"),
                        initially_expanded=False,
                    )
                    year_content = ft.Column([], spacing=4)
                    
                    for month in sorted(grouped_records[year].keys(), reverse=True):
                        month_expansion = ft.ExpansionTile(
                            title=ft.Text(month_names[month], size=13, weight=ft.FontWeight.BOLD, color="#374151"),
                            leading=ft.Icon(ft.Icons.CALENDAR_VIEW_MONTH, color="#8B5CF6"),
                            initially_expanded=False,
                        )
                        month_content = ft.Column([], spacing=4)
                        
                        for day in sorted(grouped_records[year][month].keys(), reverse=True):
                            day_records = grouped_records[year][month][day]
                            day_expansion = ft.ExpansionTile(
                                title=ft.Text(f"{day}. nap ({len(day_records)} rekord)", size=12, weight=ft.FontWeight.BOLD, color="#6B7280"),
                                leading=ft.Icon(ft.Icons.CALENDAR_TODAY, color="#10B981"),
                                initially_expanded=False,
                            )
                            day_content = ft.Column([], spacing=6)
                            
                            for record in day_records:
                                # Create card for each record
                                record_type = record['type']
                                date_str = record['date'].strftime('%Y-%m-%d %H:%M') if record['date'] else '-'
                                
                                # Type badge
                                type_colors = {
                                    'service_record': '#6366F1',
                                    'pm_history': '#F59E0B',
                                    'worksheet': '#10B981'
                                }
                                type_labels = {
                                    'service_record': 'Szerviz',
                                    'pm_history': 'PM Task',
                                    'worksheet': 'Munkalap'
                                }
                                
                                type_badge = ft.Container(
                                    content=ft.Text(
                                        type_labels.get(record_type, record_type),
                                        size=10,
                                        weight=ft.FontWeight.BOLD,
                                        color="#FFFFFF"
                                    ),
                                    bgcolor=type_colors.get(record_type, '#6B7280'),
                                    padding=ft.padding.symmetric(horizontal=8, vertical=2),
                                    border_radius=4,
                                )
                                
                                record_card = ft.Card(
                                    elevation=1,
                                    content=ft.Container(
                                        content=ft.Column([
                                            ft.Row([
                                                type_badge,
                                                ft.Text(date_str, size=13, weight=ft.FontWeight.BOLD, color="#1F2937", expand=True),
                                                ft.Text(format_price(record['cost']), size=14, weight=ft.FontWeight.BOLD, color="#10B981"),
                                            ], spacing=8),
                                            ft.Text(f"Gép: {record['machine_name']}", size=12, color="#6B7280"),
                                            ft.Text(f"Végrehajtó: {record['user_name']}", size=11, color="#6B7280"),
                                            ft.Text(record['description'], size=12, color="#374151"),
                                            ft.Text(f"Időtartam: {record['duration_hours']:.2f} óra" if record['duration_hours'] > 0 else "", size=11, color="#9CA3AF") if record['duration_hours'] > 0 else ft.Container(),
                                        ], spacing=4, tight=True),
                                        padding=12,
                                    ),
                                )
                                day_content.controls.append(record_card)
                            
                            day_expansion.controls = [day_content]
                            month_content.controls.append(day_expansion)
                        
                        month_expansion.controls = [month_content]
                        year_content.controls.append(month_expansion)
                    
                    year_expansion.controls = [year_content]
                    records_list.controls.append(year_expansion)
            
            if update_page:
                page.update()
        
        def on_tab_change(e):
            self.current_tab = e.control.selected_index
            refresh_records()
        
        tabs = ft.Tabs(
            selected_index=self.current_tab,
            on_change=on_tab_change,
            tabs=[
                ft.Tab(
                    text="Összes",
                    icon=ft.Icons.LIST if hasattr(ft.Icons, 'LIST') else ft.Icons.VIEW_LIST,
                ),
                ft.Tab(
                    text="PM Tasks",
                    icon=ft.Icons.CONSTRUCTION if hasattr(ft.Icons, 'CONSTRUCTION') else ft.Icons.BUILD,
                ),
                ft.Tab(
                    text="Worksheets",
                    icon=ft.Icons.ASSIGNMENT if hasattr(ft.Icons, 'ASSIGNMENT') else ft.Icons.DESCRIPTION,
                ),
            ]
        )
        
        refresh_records(update_page=False)
        
        return ft.Column([
            ft.Row([
                ft.Text("Szervizelések áttekintése", size=18, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            tabs,
            records_list,
        ], spacing=12, expand=True)
