"""
Dokumentáció képernyő
Vállalat szintű leírások és sablon dokumentáció
"""

import flet as ft
# Compatibility for flet 0.23.2 - Icons are strings, not ft.Icons
if not hasattr(ft, 'Icons'):
    from utils.flet_icons import Icons
    ft.Icons = Icons
from localization.translator import translator
from ui.components.modern_components import (
    create_modern_button,
    create_modern_card,
    create_modern_text_field,
    create_modern_dropdown,
    create_modern_dialog,
    create_modern_badge,
    create_vibrant_badge,
    create_modern_icon_button,
    create_modern_table,
    create_modern_divider,
    create_empty_state_card,
    DesignSystem,
)
from ui.components.modern_card import (
    create_tailwind_card,
    create_info_card,
)
from pathlib import Path


class DocumentationScreen:
    def __init__(self, page: ft.Page):
        self.page = page
        self.current_section = "templates"  # Start with templates section expanded
        self.current_template = "worksheet_template"  # Start with worksheet template selected
        self.content_container = None  # Store reference to content container for updates
        self.sidebar_container = None  # Store reference to sidebar container for updates
    
    def view(self, page: ft.Page):
        if not hasattr(self, 'page') or self.page is None:
            self.page = page
        
        # Get current language
        current_lang = translator.get_current_language()
        
        # Main container with sidebar and content
        # Store reference to content container for updates
        self.content_container = ft.Container(
            content=self._build_content(current_lang),
            expand=True,
            padding=ft.padding.all(DesignSystem.SPACING_LG),
            bgcolor=DesignSystem.BG_PRIMARY,
        )
        
        # Store sidebar container reference
        self.sidebar_container = ft.Container(
            content=self._build_sidebar(),
            width=250,
            bgcolor=DesignSystem.BG_SECONDARY,
            border=ft.border.only(right=ft.BorderSide(1, DesignSystem.BORDER_COLOR)),
            padding=ft.padding.all(DesignSystem.SPACING_MD),
        )
        
        content = ft.Row([
            # Left sidebar - Menu
            self.sidebar_container,
            # Right content area
            self.content_container,
        ], expand=True)
        
        return content
    
    def _build_sidebar(self):
        """Build the sidebar menu with submenus"""
        return ft.Column([
            ft.Text(
                translator.get_text("documentation.title"),
                size=20,
                weight=ft.FontWeight.BOLD,
            ),
            create_modern_divider(),
            ft.Container(height=DesignSystem.SPACING_MD),
            
            # Templates submenu
            self._build_submenu(
                translator.get_text("documentation.templates"),
                "templates",
                [
                    (translator.get_text("documentation.templates.worksheet"), "worksheet_template"),
                    (translator.get_text("documentation.templates.work_request"), "work_request_template"),
                    (translator.get_text("documentation.templates.qr_label"), "qr_label_template"),
                    (translator.get_text("documentation.templates.vacation"), "vacation_template"),
                    (translator.get_text("documentation.templates.scrapping"), "scrapping_template"),
                ]
            ),
        ], spacing=8, scroll=ft.ScrollMode.AUTO)
    
    def _build_submenu(self, title: str, section: str, items: list):
        """Build a collapsible submenu"""
        expanded = self.current_section == section
        
        def toggle_submenu(e):
            if self.current_section == section:
                self.current_section = None
            else:
                self.current_section = section
            # Rebuild the view to update the sidebar
            if hasattr(self.page, 'controls') and len(self.page.controls) > 0:
                # Find the documentation view in the page and update it
                for control in self.page.controls:
                    if hasattr(control, 'content') and hasattr(control.content, 'controls'):
                        for row in control.content.controls:
                            if hasattr(row, 'controls') and len(row.controls) > 1:
                                # Update the sidebar
                                row.controls[0].content = self._build_sidebar()
                                # Update the content
                                current_lang = translator.get_current_language()
                                row.controls[1].content = self._build_content(current_lang)
            self.page.update()
        
        header = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.FOLDER if not expanded else ft.Icons.FOLDER_OPEN, size=18),
                ft.Text(title, size=14, weight=ft.FontWeight.BOLD, expand=True),
                ft.Icon(ft.Icons.EXPAND_MORE if not expanded else ft.Icons.EXPAND_LESS, size=18),
            ], spacing=8),
            on_click=toggle_submenu,
            padding=ft.padding.symmetric(vertical=8, horizontal=12),
            bgcolor="#E8E8E8" if expanded else "transparent",
            border_radius=4,
        )
        
        submenu_items = []
        if expanded:
            for item_title, item_key in items:
                is_selected = self.current_template == item_key
                item = ft.Container(
                    content=ft.Row([
                        ft.Container(width=DesignSystem.SPACING_MD),
                        ft.Text(
                            item_title, 
                            size=12, 
                            expand=True, 
                            color=DesignSystem.TEXT_PRIMARY,
                            weight=ft.FontWeight.W_600 if is_selected else ft.FontWeight.NORMAL,
                        ),
                    ]),
                    on_click=lambda e, key=item_key: self._select_template(key),
                    padding=ft.padding.symmetric(vertical=6, horizontal=DesignSystem.SPACING_MD),
                    bgcolor=DesignSystem.EMERALD_100 if is_selected else "transparent",
                    border=ft.border.all(2, DesignSystem.EMERALD_500) if is_selected else None,
                    border_radius=DesignSystem.RADIUS_SM,
                )
                submenu_items.append(item)
        
        return ft.Column([
            header,
            ft.Column(submenu_items, spacing=2) if expanded else ft.Container(),
        ], spacing=0)
    
    def _select_template(self, template_key: str):
        """Select a template to show documentation"""
        self.current_template = template_key
        
        # Update the content container directly if it exists
        if self.content_container is not None:
            current_lang = translator.get_current_language()
            self.content_container.content = self._build_content(current_lang)
            
            # Update the sidebar to reflect the new selection
            if self.sidebar_container is not None:
                self.sidebar_container.content = self._build_sidebar()
            
            self.page.update()
        else:
            # Fallback: rebuild entire view
            self.page.update()
    
    def _build_content(self, lang: str):
        """Build the main content area"""
        if not self.current_template:
            return ft.Column([
                ft.Text(
                    translator.get_text("documentation.select_template"),
                    size=18,
                    color="#808080",
                ),
            ], spacing=16, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        
        # Get template documentation
        doc = self._get_template_documentation(self.current_template, lang)
        
        return ft.Column([
            # Header
            ft.Container(
                content=ft.Column([
                    ft.Text(doc["title"], size=24, weight=ft.FontWeight.BOLD),
                    ft.Text(doc["subtitle"], size=14, color="#666666"),
                    ft.Divider(height=1),
                ], spacing=8),
                padding=ft.padding.only(bottom=24),
            ),
            
            # Overview
            create_modern_card(
                content=ft.Column([
                    ft.Text(
                        translator.get_text("documentation.overview") if lang == "hu" else "Overview",
                        size=18,
                        weight=ft.FontWeight.W_600,
                        color=DesignSystem.TEXT_PRIMARY,
                    ),
                    ft.Text(doc["overview"], size=14, color=DesignSystem.TEXT_PRIMARY),
                ], spacing=DesignSystem.SPACING_MD),
                padding=DesignSystem.SPACING_MD,
                elevation=0,
            ),
            
            ft.Container(height=DesignSystem.SPACING_LG),
            
            # Variables section
            ft.Container(
                content=ft.Column([
                    ft.Text(
                        translator.get_text("documentation.variables") if lang == "hu" else "Available Variables",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Text(
                        translator.get_text("documentation.variables_description") if lang == "hu" else "The following variables can be used in the template. Use the format ${variable.name} to insert values.",
                        size=12,
                        color="#666666",
                    ),
                    ft.Container(height=16),
                    self._build_variables_table(doc["variables"], lang),
                ], spacing=12),
                padding=ft.padding.all(16),
                bgcolor="#FFFFFF",
                border=ft.border.all(1, "#E0E0E0"),
                border_radius=8,
            ),
            
            ft.Container(height=24),
            
            # Usage section
            create_modern_card(
                content=ft.Column([
                    ft.Text(
                        translator.get_text("documentation.usage") if lang == "hu" else "Usage Instructions",
                        size=18,
                        weight=ft.FontWeight.W_600,
                        color=DesignSystem.TEXT_PRIMARY,
                    ),
                    ft.Text(doc["usage"], size=14, color=DesignSystem.TEXT_PRIMARY),
                ], spacing=DesignSystem.SPACING_MD),
                padding=DesignSystem.SPACING_MD,
                elevation=0,
            ),
            
            ft.Container(height=DesignSystem.SPACING_LG),
            
            # Format section
            create_modern_card(
                content=ft.Column([
                    ft.Text(
                        translator.get_text("documentation.format") if lang == "hu" else "Template Format",
                        size=18,
                        weight=ft.FontWeight.W_600,
                        color=DesignSystem.TEXT_PRIMARY,
                    ),
                    ft.Text(doc["format"], size=14, color=DesignSystem.TEXT_PRIMARY),
                ], spacing=DesignSystem.SPACING_MD),
                padding=DesignSystem.SPACING_MD,
                elevation=0,
            ),
            
        ], spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)
    
    def _build_variables_table(self, variables: list, lang: str):
        """Build a table showing all available variables"""
        rows = []
        
        # Header row
        header_row = ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(
                    translator.get_text("documentation.variable_name") if lang == "hu" else "Variable Name",
                    weight=ft.FontWeight.BOLD,
                )),
                ft.DataCell(ft.Text(
                    translator.get_text("documentation.variable_type") if lang == "hu" else "Type",
                    weight=ft.FontWeight.BOLD,
                )),
                ft.DataCell(ft.Text(
                    translator.get_text("documentation.variable_description") if lang == "hu" else "Description",
                    weight=ft.FontWeight.BOLD,
                )),
            ],
        )
        rows.append(header_row)
        
        # Data rows
        for var in variables:
            row = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(f"${{{var['name']}}}", font_family="monospace", size=12, color=DesignSystem.TEXT_PRIMARY)),
                    ft.DataCell(ft.Text(var["type"], size=12, color=DesignSystem.TEXT_SECONDARY)),
                    ft.DataCell(ft.Text(var["description"], size=12, color=DesignSystem.TEXT_PRIMARY)),
                ],
            )
            rows.append(row)
        
        return create_modern_table(
            columns=[
                ft.DataColumn(ft.Text("")),
                ft.DataColumn(ft.Text("")),
                ft.DataColumn(ft.Text("")),
            ],
            rows=rows,
            border=True,
        )
    
    def _get_template_documentation(self, template_key: str, lang: str) -> dict:
        """Get documentation for a specific template"""
        docs = {
            "worksheet_template": {
                "hu": {
                    "title": "Munkalap Sablon Dokumentáció",
                    "subtitle": "Részletes leírás a munkalap sablon változóiról és használatáról",
                    "overview": """A munkalap sablon egy Microsoft Word (.docx) formátumú dokumentum, amelyet a rendszer használ a munkalapok (work orders) generálásához. A sablon lehetővé teszi a vállalat specifikus formázás és branding alkalmazását, miközben automatikusan kitölti a munkalap adatait.

A sablon használata során a rendszer a sablonban található placeholder változókat cseréli le a tényleges munkalap adatokra. Ez lehetővé teszi a teljes testreszabást, miközben biztosítja az adatok konzisztens megjelenítését.""",
                    "usage": """1. Helyezd el a sablon fájlt a 'templates' mappába
2. A Beállítások menüben válaszd ki a sablont a 'Munkalap sablon' dropdown-ból
3. A munkalap generálásakor a rendszer automatikusan használja a kiválasztott sablont
4. A sablonban használhatod a ${variable.name} formátumú változókat
5. A változók automatikusan le lesznek cserélve a tényleges adatokra""",
                    "format": """A sablon egy standard Microsoft Word (.docx) fájl, amely tartalmazhat:
- Szöveges tartalmat
- Táblázatokat
- Képeket
- Fejléc/lábléc információkat
- Vállalat logót és branding elemet

A változók a ${variable.name} formátumban kell, hogy szerepeljenek a sablonban.""",
                    "variables": [
                        {
                            "name": "worksheet.id",
                            "type": "Integer",
                            "description": "A munkalap egyedi azonosítója (ID). Ez a szám automatikusan generálódik a munkalap létrehozásakor."
                        },
                        {
                            "name": "worksheet.title",
                            "type": "String",
                            "description": "A munkalap címe vagy rövid leírása. Ez a mező a munkalap létrehozásakor megadott cím."
                        },
                        {
                            "name": "worksheet.description",
                            "type": "String",
                            "description": "A munkalap részletes leírása. Tartalmazhatja a hiba leírását, a szükséges javításokat és egyéb releváns információkat."
                        },
                        {
                            "name": "worksheet.status",
                            "type": "String",
                            "description": "A munkalap aktuális állapota. Lehetséges értékek: 'Open' (Nyitott), 'Waiting for Parts' (Részre vár), 'Closed' (Lezárva)."
                        },
                        {
                            "name": "worksheet.breakdown_time",
                            "type": "DateTime",
                            "description": "A gép leállásának időpontja. Formátum: YYYY-MM-DD HH:MM. Ha nincs megadva, akkor '-' jelenik meg."
                        },
                        {
                            "name": "worksheet.repair_finished_time",
                            "type": "DateTime",
                            "description": "A javítás befejezésének időpontja. Formátum: YYYY-MM-DD HH:MM. Csak lezárt munkalapoknál van értéke."
                        },
                        {
                            "name": "worksheet.total_downtime_hours",
                            "type": "Float",
                            "description": "A teljes leállási idő órákban. Automatikusan számítódik a breakdown_time és repair_finished_time alapján."
                        },
                        {
                            "name": "worksheet.fault_cause",
                            "type": "String",
                            "description": "A hiba okának leírása. Ez a mező kötelező a munkalap lezárásakor (MSZ EN 13460 követelmény)."
                        },
                        {
                            "name": "worksheet.created_at",
                            "type": "DateTime",
                            "description": "A munkalap létrehozásának időpontja. Formátum: YYYY-MM-DD HH:MM."
                        },
                        {
                            "name": "worksheet.closed_at",
                            "type": "DateTime",
                            "description": "A munkalap lezárásának időpontja. Formátum: YYYY-MM-DD HH:MM. Csak lezárt munkalapoknál van értéke."
                        },
                        {
                            "name": "machine.id",
                            "type": "Integer",
                            "description": "A gép egyedi azonosítója (ID)."
                        },
                        {
                            "name": "machine.name",
                            "type": "String",
                            "description": "A gép neve vagy megnevezése."
                        },
                        {
                            "name": "machine.serial_number",
                            "type": "String",
                            "description": "A gép sorozatszáma. Ez egyedi azonosító a gyártó által kiadott."
                        },
                        {
                            "name": "machine.model",
                            "type": "String",
                            "description": "A gép modellje vagy típusa."
                        },
                        {
                            "name": "machine.manufacturer",
                            "type": "String",
                            "description": "A gép gyártója vagy beszállítója."
                        },
                        {
                            "name": "machine.asset_tag",
                            "type": "String",
                            "description": "A gép eszköz címkéje vagy belső azonosítója. Ez a vállalat által kiadott egyedi azonosító."
                        },
                        {
                            "name": "production_line.name",
                            "type": "String",
                            "description": "A termelési sor neve, amelyhez a gép tartozik."
                        },
                        {
                            "name": "assigned_user.full_name",
                            "type": "String",
                            "description": "A munkalaphoz hozzárendelt karbantartó teljes neve. Ha nincs hozzárendelve, akkor '-' jelenik meg."
                        },
                        {
                            "name": "assigned_user.username",
                            "type": "String",
                            "description": "A munkalaphoz hozzárendelt karbantartó felhasználóneve."
                        },
                        {
                            "name": "assigned_user.email",
                            "type": "String",
                            "description": "A munkalaphoz hozzárendelt karbantartó e-mail címe."
                        },
                        {
                            "name": "generated_at",
                            "type": "DateTime",
                            "description": "A dokumentum generálásának időpontja. Formátum: YYYY-MM-DD HH:MM."
                        },
                        {
                            "name": "generated_by",
                            "type": "String",
                            "description": "A dokumentumot generáló felhasználó neve vagy a rendszer azonosítója."
                        },
                    ]
                },
                "en": {
                    "title": "Worksheet Template Documentation",
                    "subtitle": "Detailed description of worksheet template variables and usage",
                    "overview": """The worksheet template is a Microsoft Word (.docx) format document used by the system to generate work orders. The template allows for company-specific formatting and branding while automatically populating worksheet data.

When using the template, the system replaces placeholder variables found in the template with actual worksheet data. This enables full customization while ensuring consistent data presentation.""",
                    "usage": """1. Place the template file in the 'templates' folder
2. In the Settings menu, select the template from the 'Worksheet template' dropdown
3. When generating a worksheet, the system automatically uses the selected template
4. You can use ${variable.name} format variables in the template
5. Variables will be automatically replaced with actual data""",
                    "format": """The template is a standard Microsoft Word (.docx) file that can contain:
- Text content
- Tables
- Images
- Header/footer information
- Company logo and branding elements

Variables must appear in the template in ${variable.name} format.""",
                    "variables": [
                        {
                            "name": "worksheet.id",
                            "type": "Integer",
                            "description": "The unique identifier (ID) of the worksheet. This number is automatically generated when the worksheet is created."
                        },
                        {
                            "name": "worksheet.title",
                            "type": "String",
                            "description": "The title or brief description of the worksheet. This is the title provided when creating the worksheet."
                        },
                        {
                            "name": "worksheet.description",
                            "type": "String",
                            "description": "The detailed description of the worksheet. May include fault description, required repairs, and other relevant information."
                        },
                        {
                            "name": "worksheet.notes",
                            "type": "String",
                            "description": "Notes or additional comments related to the worksheet. If not specified, '-' is displayed."
                        },
                        {
                            "name": "worksheet.assigned_username",
                            "type": "String",
                            "description": "The full name of the technician assigned to the worksheet. If not assigned, '-' is displayed."
                        },
                        {
                            "name": "worksheet.downtime",
                            "type": "String",
                            "description": "The total downtime in formatted form. Example: '2.50h' (2 hours 30 minutes). If not specified, '-' is displayed."
                        },
                        {
                            "name": "worksheet.parts",
                            "type": "String",
                            "description": "List of parts used in the worksheet. Each part appears on a new line, format: 'SKU - Name (quantityx)'. If no parts, '-' is displayed."
                        },
                        {
                            "name": "machine.manufacturer_model",
                            "type": "String",
                            "description": "The manufacturer and model of the machine combined. Format: 'Manufacturer / Model'. If not specified, '-' is displayed."
                        },
                        {
                            "name": "worksheet.status",
                            "type": "String",
                            "description": "The current status of the worksheet. Possible values: 'Open', 'Waiting for Parts', 'Closed'."
                        },
                        {
                            "name": "worksheet.breakdown_time",
                            "type": "DateTime",
                            "description": "The time when the machine broke down. Format: YYYY-MM-DD HH:MM. If not specified, '-' is displayed."
                        },
                        {
                            "name": "worksheet.repair_finished_time",
                            "type": "DateTime",
                            "description": "The time when the repair was completed. Format: YYYY-MM-DD HH:MM. Only has a value for closed worksheets."
                        },
                        {
                            "name": "worksheet.total_downtime_hours",
                            "type": "Float",
                            "description": "The total downtime in hours. Automatically calculated based on breakdown_time and repair_finished_time."
                        },
                        {
                            "name": "worksheet.fault_cause",
                            "type": "String",
                            "description": "Description of the fault cause. This field is mandatory when closing a worksheet (MSZ EN 13460 requirement)."
                        },
                        {
                            "name": "worksheet.created_at",
                            "type": "DateTime",
                            "description": "The time when the worksheet was created. Format: YYYY-MM-DD HH:MM."
                        },
                        {
                            "name": "worksheet.closed_at",
                            "type": "DateTime",
                            "description": "The time when the worksheet was closed. Format: YYYY-MM-DD HH:MM. Only has a value for closed worksheets."
                        },
                        {
                            "name": "machine.id",
                            "type": "Integer",
                            "description": "The unique identifier (ID) of the machine."
                        },
                        {
                            "name": "machine.name",
                            "type": "String",
                            "description": "The name or designation of the machine."
                        },
                        {
                            "name": "machine.serial_number",
                            "type": "String",
                            "description": "The serial number of the machine. This is a unique identifier issued by the manufacturer."
                        },
                        {
                            "name": "machine.model",
                            "type": "String",
                            "description": "The model or type of the machine."
                        },
                        {
                            "name": "machine.manufacturer",
                            "type": "String",
                            "description": "The manufacturer or supplier of the machine."
                        },
                        {
                            "name": "machine.asset_tag",
                            "type": "String",
                            "description": "The asset tag or internal identifier of the machine. This is a unique identifier issued by the company."
                        },
                        {
                            "name": "production_line.name",
                            "type": "String",
                            "description": "The name of the production line to which the machine belongs."
                        },
                        {
                            "name": "assigned_user.full_name",
                            "type": "String",
                            "description": "The full name of the technician assigned to the worksheet. If not assigned, '-' is displayed."
                        },
                        {
                            "name": "assigned_user.username",
                            "type": "String",
                            "description": "The username of the technician assigned to the worksheet."
                        },
                        {
                            "name": "assigned_user.email",
                            "type": "String",
                            "description": "The email address of the technician assigned to the worksheet."
                        },
                        {
                            "name": "generated_at",
                            "type": "DateTime",
                            "description": "The time when the document was generated. Format: YYYY-MM-DD HH:MM."
                        },
                        {
                            "name": "generated_by",
                            "type": "String",
                            "description": "The name of the user who generated the document or the system identifier."
                        },
                    ]
                }
            },
            "work_request_template": {
                "hu": {
                    "title": "Munkaigénylő Lap Sablon Dokumentáció",
                    "subtitle": "Részletes leírás a munkaigénylő lap sablon változóiról és használatáról",
                    "overview": """A munkaigénylő lap sablon egy Microsoft Word (.docx) formátumú dokumentum, amelyet a rendszer használ a megelőző karbantartási (PM) feladatokhoz tartozó munkaigénylő lapok generálásához. A sablon lehetővé teszi a vállalat specifikus formázás és branding alkalmazását, miközben automatikusan kitölti a PM feladat adatait.

A sablon használata során a rendszer a sablonban található placeholder változókat cseréli le a tényleges PM feladat adatokra. Ez lehetővé teszi a teljes testreszabást, miközben biztosítja az adatok konzisztens megjelenítését.""",
                    "usage": """1. Helyezd el a sablon fájlt a 'templates' mappába
2. A Beállítások menüben válaszd ki a sablont a 'Munkaigénylő lap sablon' dropdown-ból
3. A munkaigénylő lap generálásakor a rendszer automatikusan használja a kiválasztott sablont
4. A sablonban használhatod a ${variable.name} formátumú változókat
5. A változók automatikusan le lesznek cserélve a tényleges adatokra""",
                    "format": """A sablon egy standard Microsoft Word (.docx) fájl, amely tartalmazhat:
- Szöveges tartalmat
- Táblázatokat
- Képeket
- Fejléc/lábléc információkat
- Vállalat logót és branding elemet

A változók a ${variable.name} formátumban kell, hogy szerepeljenek a sablonban.""",
                    "variables": [
                        {
                            "name": "pm_task.id",
                            "type": "Integer",
                            "description": "A PM feladat egyedi azonosítója (ID). Ez a szám automatikusan generálódik a feladat létrehozásakor."
                        },
                        {
                            "name": "pm_task.task_name",
                            "type": "String",
                            "description": "A PM feladat neve vagy címe. Ez a mező a feladat létrehozásakor megadott név."
                        },
                        {
                            "name": "pm_task.task_description",
                            "type": "String",
                            "description": "A PM feladat részletes leírása. Tartalmazhatja a végrehajtandó karbantartási lépéseket, ellenőrzési pontokat és egyéb releváns információkat."
                        },
                        {
                            "name": "pm_task.task_type",
                            "type": "String",
                            "description": "A PM feladat típusa. Lehetséges értékek: 'recurring' (Ismétlődő), 'one_time' (Egyszeri)."
                        },
                        {
                            "name": "pm_task.priority",
                            "type": "String",
                            "description": "A PM feladat prioritása. Lehetséges értékek: 'low' (Alacsony), 'normal' (Normál), 'high' (Magas), 'urgent' (Sürgős)."
                        },
                        {
                            "name": "pm_task.status",
                            "type": "String",
                            "description": "A PM feladat aktuális állapota. Lehetséges értékek: 'pending' (Függőben), 'in_progress' (Folyamatban), 'completed' (Befejezve), 'overdue' (Lejárt)."
                        },
                        {
                            "name": "pm_task.due_date",
                            "type": "DateTime",
                            "description": "A PM feladat esedékességi dátuma. Formátum: YYYY-MM-DD HH:MM. Ha nincs megadva, akkor a next_due_date értéke jelenik meg."
                        },
                        {
                            "name": "pm_task.next_due_date",
                            "type": "DateTime",
                            "description": "A PM feladat következő esedékességi dátuma. Formátum: YYYY-MM-DD HH:MM. Ismétlődő feladatoknál ez a következő végrehajtás időpontja."
                        },
                        {
                            "name": "pm_task.estimated_duration_minutes",
                            "type": "Integer",
                            "description": "A PM feladat becsült végrehajtási ideje percekben. Ha nincs megadva, akkor '-' jelenik meg."
                        },
                        {
                            "name": "pm_task.location",
                            "type": "String",
                            "description": "A PM feladat helyszíne. Ha a feladat egy géphez van rendelve, akkor a gép helyszíne, egyébként egy szabad szöveges helyszín."
                        },
                        {
                            "name": "pm_task.created_at",
                            "type": "DateTime",
                            "description": "A PM feladat létrehozásának időpontja. Formátum: YYYY-MM-DD HH:MM."
                        },
                        {
                            "name": "machine.name",
                            "type": "String",
                            "description": "A gép neve, amelyhez a PM feladat tartozik. Ha a feladat nem gép-specifikus, akkor '-' jelenik meg."
                        },
                        {
                            "name": "machine.serial_number",
                            "type": "String",
                            "description": "A gép sorozatszáma. Ha nincs megadva, akkor '-' jelenik meg."
                        },
                        {
                            "name": "machine.manufacturer_model",
                            "type": "String",
                            "description": "A gép gyártója és modellje kombinálva. Formátum: 'Gyártó / Modell'. Ha nincs megadva, akkor '-' jelenik meg."
                        },
                        {
                            "name": "production_line.name",
                            "type": "String",
                            "description": "A termelési sor neve, amelyhez a gép tartozik. Ha nincs megadva, akkor '-' jelenik meg."
                        },
                        {
                            "name": "assigned_user.full_name",
                            "type": "String",
                            "description": "A PM feladathoz hozzárendelt karbantartó teljes neve. Ha nincs hozzárendelve (globális feladat), akkor 'Globális / Global' jelenik meg."
                        },
                        {
                            "name": "assignment_type",
                            "type": "String",
                            "description": "A hozzárendelés típusa. Lehetséges értékek: 'Személyre szabott / Assigned' (ha van hozzárendelt felhasználó), 'Globális / Global' (ha nincs hozzárendelt felhasználó)."
                        },
                        {
                            "name": "created_by_user.full_name",
                            "type": "String",
                            "description": "A PM feladatot létrehozó felhasználó teljes neve."
                        },
                        {
                            "name": "generated_at",
                            "type": "DateTime",
                            "description": "A dokumentum generálásának időpontja. Formátum: YYYY-MM-DD HH:MM."
                        },
                        {
                            "name": "generated_by",
                            "type": "String",
                            "description": "A dokumentumot generáló felhasználó neve vagy a rendszer azonosítója."
                        },
                    ]
                },
                "en": {
                    "title": "Work Request Template Documentation",
                    "subtitle": "Detailed description of work request template variables and usage",
                    "overview": """The work request template is a Microsoft Word (.docx) format document used by the system to generate work request documents for preventive maintenance (PM) tasks. The template allows for company-specific formatting and branding while automatically populating PM task data.

When using the template, the system replaces placeholder variables found in the template with actual PM task data. This enables full customization while ensuring consistent data presentation.""",
                    "usage": """1. Place the template file in the 'templates' folder
2. In the Settings menu, select the template from the 'Work request template' dropdown
3. When generating a work request, the system automatically uses the selected template
4. You can use ${variable.name} format variables in the template
5. Variables will be automatically replaced with actual data""",
                    "format": """The template is a standard Microsoft Word (.docx) file that can contain:
- Text content
- Tables
- Images
- Header/footer information
- Company logo and branding elements

Variables must appear in the template in ${variable.name} format.""",
                    "variables": [
                        {
                            "name": "pm_task.id",
                            "type": "Integer",
                            "description": "The unique identifier (ID) of the PM task. This number is automatically generated when the task is created."
                        },
                        {
                            "name": "pm_task.task_name",
                            "type": "String",
                            "description": "The name or title of the PM task. This is the name provided when creating the task."
                        },
                        {
                            "name": "pm_task.task_description",
                            "type": "String",
                            "description": "The detailed description of the PM task. May include maintenance steps to be performed, checkpoints, and other relevant information."
                        },
                        {
                            "name": "pm_task.task_type",
                            "type": "String",
                            "description": "The type of the PM task. Possible values: 'recurring', 'one_time'."
                        },
                        {
                            "name": "pm_task.priority",
                            "type": "String",
                            "description": "The priority of the PM task. Possible values: 'low', 'normal', 'high', 'urgent'."
                        },
                        {
                            "name": "pm_task.status",
                            "type": "String",
                            "description": "The current status of the PM task. Possible values: 'pending', 'in_progress', 'completed', 'overdue'."
                        },
                        {
                            "name": "pm_task.due_date",
                            "type": "DateTime",
                            "description": "The due date of the PM task. Format: YYYY-MM-DD HH:MM. If not specified, the next_due_date value is displayed."
                        },
                        {
                            "name": "pm_task.next_due_date",
                            "type": "DateTime",
                            "description": "The next due date of the PM task. Format: YYYY-MM-DD HH:MM. For recurring tasks, this is the next execution date."
                        },
                        {
                            "name": "pm_task.estimated_duration_minutes",
                            "type": "Integer",
                            "description": "The estimated execution time of the PM task in minutes. If not specified, '-' is displayed."
                        },
                        {
                            "name": "pm_task.location",
                            "type": "String",
                            "description": "The location of the PM task. If the task is assigned to a machine, the machine location, otherwise a free-text location."
                        },
                        {
                            "name": "pm_task.created_at",
                            "type": "DateTime",
                            "description": "The time when the PM task was created. Format: YYYY-MM-DD HH:MM."
                        },
                        {
                            "name": "machine.name",
                            "type": "String",
                            "description": "The name of the machine to which the PM task belongs. If the task is not machine-specific, '-' is displayed."
                        },
                        {
                            "name": "machine.serial_number",
                            "type": "String",
                            "description": "The serial number of the machine. If not specified, '-' is displayed."
                        },
                        {
                            "name": "machine.manufacturer_model",
                            "type": "String",
                            "description": "The manufacturer and model of the machine combined. Format: 'Manufacturer / Model'. If not specified, '-' is displayed."
                        },
                        {
                            "name": "production_line.name",
                            "type": "String",
                            "description": "The name of the production line to which the machine belongs. If not specified, '-' is displayed."
                        },
                        {
                            "name": "assigned_user.full_name",
                            "type": "String",
                            "description": "The full name of the technician assigned to the PM task. If not assigned (global task), 'Globális / Global' is displayed."
                        },
                        {
                            "name": "assignment_type",
                            "type": "String",
                            "description": "The type of assignment. Possible values: 'Személyre szabott / Assigned' (if there is an assigned user), 'Globális / Global' (if there is no assigned user)."
                        },
                        {
                            "name": "created_by_user.full_name",
                            "type": "String",
                            "description": "The full name of the user who created the PM task."
                        },
                        {
                            "name": "generated_at",
                            "type": "DateTime",
                            "description": "The time when the document was generated. Format: YYYY-MM-DD HH:MM."
                        },
                        {
                            "name": "generated_by",
                            "type": "String",
                            "description": "The name of the user who generated the document or the system identifier."
                        },
                    ]
                }
            },
            "qr_label_template": {
                "hu": {
                    "title": "QR Címke Sablon Dokumentáció",
                    "subtitle": "Részletes leírás a QR címke sablon használatáról",
                    "overview": """A QR címke sablon egy Microsoft Word (.docx) formátumú dokumentum, amelyet a rendszer használ az alkatrészek QR kódos címkéinek generálásához. A sablon lehetővé teszi a vállalat specifikus formázás és branding alkalmazását, miközben automatikusan kitölti az alkatrész adatait.

A QR címke sablon használata során a rendszer a sablon alapján hozza létre a címkéket, de a címkék tartalma (szöveg, QR kód) programozottan generálódik. A sablon főként a dokumentum margóit, stílusait és formázását határozza meg.""",
                    "usage": """1. Helyezd el a sablon fájlt a 'templates' mappába
2. A Beállítások menüben válaszd ki a sablont a 'QR címke sablon' dropdown-ból
3. A QR címke generálásakor a rendszer automatikusan használja a kiválasztott sablont
4. Ha nincs sablon kiválasztva, az alapértelmezett beállításokat használja
5. A sablon határozza meg a dokumentum margóit és alapvető formázását""",
                    "format": """A sablon egy standard Microsoft Word (.docx) fájl, amely tartalmazhat:
- Oldal margókat és formázást
- Alapértelmezett stílusokat
- Fejléc/lábléc információkat
- Vállalat logót és branding elemet

A címkék tartalma (alkatrész adatok, QR kód) automatikusan generálódik a sablon alapján.""",
                    "variables": [
                        {
                            "name": "N/A",
                            "type": "N/A",
                            "description": "A QR címke sablon nem használ változókat, mivel a címkék tartalma programozottan generálódik. A sablon csak a dokumentum formázását határozza meg."
                        },
                    ]
                },
                "en": {
                    "title": "QR Label Template Documentation",
                    "subtitle": "Detailed description of QR label template usage",
                    "overview": """The QR label template is a Microsoft Word (.docx) format document used by the system to generate QR code labels for parts. The template allows for company-specific formatting and branding while automatically populating part data.

When using the QR label template, the system creates labels based on the template, but the label content (text, QR code) is programmatically generated. The template primarily determines document margins, styles, and formatting.""",
                    "usage": """1. Place the template file in the 'templates' folder
2. In the Settings menu, select the template from the 'QR label template' dropdown
3. When generating QR labels, the system automatically uses the selected template
4. If no template is selected, it uses default settings
5. The template determines document margins and basic formatting""",
                    "format": """The template is a standard Microsoft Word (.docx) file that can contain:
- Page margins and formatting
- Default styles
- Header/footer information
- Company logo and branding elements

Label content (part data, QR code) is automatically generated based on the template.""",
                    "variables": [
                        {
                            "name": "N/A",
                            "type": "N/A",
                            "description": "The QR label template does not use variables, as label content is programmatically generated. The template only determines document formatting."
                        },
                    ]
                }
            },
            "vacation_template": {
                "hu": {
                    "title": "Szabadság Igénylő Lap Sablon Dokumentáció",
                    "subtitle": "Részletes leírás a szabadság igénylő lap sablon használatáról",
                    "overview": """A szabadság igénylő lap sablon egy Microsoft Word (.docx) formátumú dokumentum, amelyet a rendszer használ a jóváhagyott szabadság igénylések dokumentumainak generálásához. A sablon lehetővé teszi a vállalat specifikus formázás és branding alkalmazását, miközben automatikusan kitölti a szabadság igénylés adatait.

A sablon használata során a rendszer a sablon alapján hozza létre a dokumentumot, és automatikusan helyettesíti a sablonban található változókat a tényleges adatokkal.""",
                    "usage": """1. Helyezd el a sablon fájlt a 'templates' mappába
2. A Beállítások menüben válaszd ki a sablont a 'Szabadság sablon' dropdown-ból
3. Amikor egy szabadság igénylés jóváhagyásra kerül, a rendszer automatikusan generálja a dokumentumot a kiválasztott sablon alapján
4. A generált dokumentum letölthető a szabadság igénylés részletei oldalról
5. Ha nincs sablon kiválasztva, az alapértelmezett formátumot használja""",
                    "format": """A sablon egy standard Microsoft Word (.docx) fájl, amely tartalmazhat:
- Vállalat logót és fejlécet
- Alapértelmezett stílusokat és formázást
- Változókat ${variable.name} formátumban
- Fejléc/lábléc információkat
- Aláírási mezőket""",
                    "variables": [
                        {
                            "name": "${vacation_request.start_date}",
                            "type": "Date",
                            "description": "A szabadság kezdő dátuma (YYYY-MM-DD formátumban)."
                        },
                        {
                            "name": "${vacation_request.end_date}",
                            "type": "Date",
                            "description": "A szabadság befejező dátuma (YYYY-MM-DD formátumban)."
                        },
                        {
                            "name": "${vacation_request.reason}",
                            "type": "String",
                            "description": "A szabadság igénylés indoklása, amelyet a felhasználó adott meg."
                        },
                        {
                            "name": "${user.name}",
                            "type": "String",
                            "description": "A szabadságot igénylő felhasználó teljes neve."
                        },
                        {
                            "name": "${vacation_request.days_count}",
                            "type": "Integer",
                            "description": "A szabadság napok száma (csak munkanapok, hétvégek nélkül)."
                        },
                        {
                            "name": "${vacation_request.status}",
                            "type": "String",
                            "description": "A szabadság igénylés státusza (pending, approved, rejected)."
                        },
                        {
                            "name": "${vacation_request.requested_at}",
                            "type": "DateTime",
                            "description": "Az igénylés létrehozásának dátuma és ideje."
                        },
                        {
                            "name": "${vacation_request.approved_by}",
                            "type": "String",
                            "description": "A jóváhagyó felhasználó neve (ha jóváhagyva)."
                        },
                        {
                            "name": "${vacation_request.approved_at}",
                            "type": "DateTime",
                            "description": "A jóváhagyás dátuma és ideje (ha jóváhagyva)."
                        }
                    ]
                },
                "en": {
                    "title": "Vacation Request Form Template Documentation",
                    "subtitle": "Detailed description of vacation request form template usage",
                    "overview": """The vacation request form template is a Microsoft Word (.docx) format document used by the system to generate vacation request forms for approved vacation requests. The template allows for company-specific formatting and branding while automatically populating vacation request data.

When using the template, the system creates the document based on the template and automatically replaces variables in the template with actual data.""",
                    "usage": """1. Place the template file in the 'templates' folder
2. In the Settings menu, select the template from the 'Vacation template' dropdown
3. When a vacation request is approved, the system automatically generates the document based on the selected template
4. The generated document can be downloaded from the vacation request details page
5. If no template is selected, it uses the default format""",
                    "format": """The template is a standard Microsoft Word (.docx) file that can contain:
- Company logo and header
- Default styles and formatting
- Variables in ${variable.name} format
- Header/footer information
- Signature fields""",
                    "variables": [
                        {
                            "name": "${vacation_request.start_date}",
                            "type": "Date",
                            "description": "The start date of the vacation (in YYYY-MM-DD format)."
                        },
                        {
                            "name": "${vacation_request.end_date}",
                            "type": "Date",
                            "description": "The end date of the vacation (in YYYY-MM-DD format)."
                        },
                        {
                            "name": "${vacation_request.reason}",
                            "type": "String",
                            "description": "The reason for the vacation request provided by the user."
                        },
                        {
                            "name": "${user.name}",
                            "type": "String",
                            "description": "The full name of the user requesting vacation."
                        },
                        {
                            "name": "${vacation_request.days_count}",
                            "type": "Integer",
                            "description": "The number of vacation days (workdays only, excluding weekends)."
                        },
                        {
                            "name": "${vacation_request.status}",
                            "type": "String",
                            "description": "The status of the vacation request (pending, approved, rejected)."
                        },
                        {
                            "name": "${vacation_request.requested_at}",
                            "type": "DateTime",
                            "description": "The date and time when the request was created."
                        },
                        {
                            "name": "${vacation_request.approved_by}",
                            "type": "String",
                            "description": "The name of the approving user (if approved)."
                        },
                        {
                            "name": "${vacation_request.approved_at}",
                            "type": "DateTime",
                            "description": "The date and time of approval (if approved)."
                        }
                    ]
                }
            },
            "scrapping_template": {
                "hu": {
                    "title": "Selejtezési Lap Sablon Dokumentáció",
                    "subtitle": "Részletes leírás a selejtezési lap sablon használatáról",
                    "overview": """A selejtezési lap sablon egy Microsoft Word (.docx) formátumú dokumentum, amelyet a rendszer használ az alkatrészek vagy eszközök selejtezési dokumentumainak generálásához. A sablon lehetővé teszi a vállalat specifikus formázás és branding alkalmazását, miközben automatikusan kitölti a selejtezési adatokat.

A sablon használata során a rendszer a sablon alapján hozza létre a dokumentumot, és automatikusan helyettesíti a sablonban található változókat a tényleges adatokkal. Selejtezési lap generálódik minden alkatrész vagy eszköz törlésnél, valamint karbantartásnál elhasznált anyagokról.""",
                    "usage": """1. Helyezd el a sablon fájlt a 'templates' mappába
2. A Beállítások menüben válaszd ki a sablont a 'Selejtezési sablon' dropdown-ból
3. Amikor egy alkatrész vagy eszköz törlésre kerül, vagy karbantartásnál anyagot használnak fel, a rendszer automatikusan generálja a selejtezési lapot a kiválasztott sablon alapján
4. A generált dokumentum letölthető a megfelelő oldalról (munkalap, alkatrész/eszköz részletek)
5. Ha nincs sablon kiválasztva, az alapértelmezett formátumot használja""",
                    "format": """A sablon egy standard Microsoft Word (.docx) fájl, amely tartalmazhat:
- Vállalat logót és fejlécet
- Alapértelmezett stílusokat és formázást
- Változókat ${variable.name} formátumban
- Fejléc/lábléc információkat
- Aláírási mezőket
- Selejtezési okok mezőket""",
                    "variables": [
                        {
                            "name": "${scrapping.item_name}",
                            "type": "String",
                            "description": "A selejtezett tétel neve (alkatrész vagy eszköz neve)."
                        },
                        {
                            "name": "${scrapping.item_type}",
                            "type": "String",
                            "description": "A tétel típusa ('Part' alkatrész vagy 'Machine' eszköz)."
                        },
                        {
                            "name": "${scrapping.reason}",
                            "type": "String",
                            "description": "A selejtezés indoka vagy oka."
                        },
                        {
                            "name": "${scrapping.date}",
                            "type": "Date",
                            "description": "A selejtezés dátuma (YYYY-MM-DD formátumban)."
                        },
                        {
                            "name": "${user.name}",
                            "type": "String",
                            "description": "A selejtezést végrehajtó felhasználó teljes neve."
                        },
                        {
                            "name": "${scrapping.quantity}",
                            "type": "Integer",
                            "description": "A selejtezett mennyiség (alkatrész esetén)."
                        },
                        {
                            "name": "${scrapping.serial_number}",
                            "type": "String",
                            "description": "A sorozatszám (eszköz esetén, ha elérhető)."
                        },
                        {
                            "name": "${scrapping.sku}",
                            "type": "String",
                            "description": "Az SKU kód (alkatrész esetén, ha elérhető)."
                        },
                        {
                            "name": "${scrapping.worksheet_id}",
                            "type": "Integer",
                            "description": "A kapcsolódó munkalap azonosítója (ha karbantartásból ered)."
                        }
                    ]
                },
                "en": {
                    "title": "Scrapping Document Template Documentation",
                    "subtitle": "Detailed description of scrapping document template usage",
                    "overview": """The scrapping document template is a Microsoft Word (.docx) format document used by the system to generate scrapping documents for parts or assets. The template allows for company-specific formatting and branding while automatically populating scrapping data.

When using the template, the system creates the document based on the template and automatically replaces variables in the template with actual data. Scrapping documents are generated for every part or asset deletion, as well as for materials used in maintenance.""",
                    "usage": """1. Place the template file in the 'templates' folder
2. In the Settings menu, select the template from the 'Scrapping template' dropdown
3. When a part or asset is deleted, or materials are used in maintenance, the system automatically generates the scrapping document based on the selected template
4. The generated document can be downloaded from the appropriate page (worksheet, part/asset details)
5. If no template is selected, it uses the default format""",
                    "format": """The template is a standard Microsoft Word (.docx) file that can contain:
- Company logo and header
- Default styles and formatting
- Variables in ${variable.name} format
- Header/footer information
- Signature fields
- Scrapping reason fields""",
                    "variables": [
                        {
                            "name": "${scrapping.item_name}",
                            "type": "String",
                            "description": "The name of the scrapped item (part or asset name)."
                        },
                        {
                            "name": "${scrapping.item_type}",
                            "type": "String",
                            "description": "The type of item ('Part' for parts or 'Machine' for assets)."
                        },
                        {
                            "name": "${scrapping.reason}",
                            "type": "String",
                            "description": "The reason or cause for scrapping."
                        },
                        {
                            "name": "${scrapping.date}",
                            "type": "Date",
                            "description": "The date of scrapping (in YYYY-MM-DD format)."
                        },
                        {
                            "name": "${user.name}",
                            "type": "String",
                            "description": "The full name of the user performing the scrapping."
                        },
                        {
                            "name": "${scrapping.quantity}",
                            "type": "Integer",
                            "description": "The scrapped quantity (for parts)."
                        },
                        {
                            "name": "${scrapping.serial_number}",
                            "type": "String",
                            "description": "The serial number (for assets, if available)."
                        },
                        {
                            "name": "${scrapping.sku}",
                            "type": "String",
                            "description": "The SKU code (for parts, if available)."
                        },
                        {
                            "name": "${scrapping.worksheet_id}",
                            "type": "Integer",
                            "description": "The related worksheet ID (if resulting from maintenance)."
                        }
                    ]
                }
            }
        }
        
        return docs.get(template_key, {}).get(lang, docs.get(template_key, {}).get("hu", {}))

