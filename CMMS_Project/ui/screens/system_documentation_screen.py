"""
System Documentation Screen
Teljes rendszer dokumentáció tree struktúrával, részletes leírásokkal és letölthető/nyomtatható formátummal
"""

import flet as ft
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import logging

from localization.translator import translator
from ui.components.modern_components import (
    create_modern_button,
    create_modern_card,
    DesignSystem,
)
from services.system_documentation_service import generate_system_documentation_docx

logger = logging.getLogger(__name__)


class SystemDocumentationScreen:
    """Teljes rendszer dokumentáció screen"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.current_section = None
        self.content_container = None
        self.sidebar_container = None
    
    def view(self, page: ft.Page):
        """Build the system documentation view"""
        if not hasattr(self, 'page') or self.page is None:
            self.page = page
        
        self.content_container = ft.Container(
            content=self._build_content(),
            expand=True,
            padding=ft.padding.all(DesignSystem.SPACING_LG),
            bgcolor=DesignSystem.BG_PRIMARY,
        )
        
        self.sidebar_container = ft.Container(
            content=self._build_sidebar(),
            width=300,
            bgcolor=DesignSystem.BG_SECONDARY,
            border=ft.border.only(right=ft.BorderSide(1, DesignSystem.BORDER_COLOR)),
            padding=ft.padding.all(DesignSystem.SPACING_MD),
        )
        
        return ft.Row([
            self.sidebar_container,
            self.content_container,
        ], expand=True)
    
    def _build_sidebar(self):
        """Build sidebar with documentation sections"""
        sections = [
            ("rendszer_attekintes", translator.get_text("system_doc.sections.overview")),
            ("logikai_analizis", translator.get_text("system_doc.sections.logical_analysis")),
            ("logikai_fa", translator.get_text("system_doc.sections.logical_tree")),
            ("munkafolyamatok", translator.get_text("system_doc.sections.workflows")),
            ("entitasok_muveletei", translator.get_text("system_doc.sections.entity_operations")),
            ("javaslatok", translator.get_text("system_doc.sections.improvements")),
            ("osszefoglalo", translator.get_text("system_doc.sections.summary")),
        ]
        
        section_items = []
        for section_key, section_title in sections:
            is_selected = self.current_section == section_key
            # Use simple text indicator instead of icons to avoid compatibility issues
            item = ft.Container(
                content=ft.Row([
                    ft.Text(
                        "▶" if is_selected else "•",
                        size=14,
                        color=DesignSystem.EMERALD_500 if is_selected else DesignSystem.TEXT_SECONDARY,
                        weight=ft.FontWeight.BOLD if is_selected else ft.FontWeight.NORMAL,
                        width=20,
                    ),
                    ft.Text(
                        section_title,
                        size=14,
                        weight=ft.FontWeight.W_600 if is_selected else ft.FontWeight.NORMAL,
                        color=DesignSystem.EMERALD_700 if is_selected else DesignSystem.TEXT_PRIMARY,
                        expand=True,
                    ),
                ], spacing=12),
                on_click=lambda e, key=section_key: self._select_section(key),
                padding=ft.padding.all(12),
                bgcolor=DesignSystem.EMERALD_50 if is_selected else "transparent",
                border=ft.border.all(2, DesignSystem.EMERALD_500) if is_selected else None,
                border_radius=8,
            )
            section_items.append(item)
        
        # Download button
        action_buttons = ft.Column([
            create_modern_button(
                text=translator.get_text("system_doc.actions.download_docx"),
                icon=ft.Icons.DOWNLOAD,
                on_click=self._download_docx,
                bgcolor=DesignSystem.EMERALD_500,
            ),
        ], spacing=12)
        
        return ft.Column([
            ft.Text(
                translator.get_text("system_doc.title"),
                size=20,
                weight=ft.FontWeight.BOLD,
                color=DesignSystem.TEXT_PRIMARY,
            ),
            ft.Divider(height=1, color=DesignSystem.BORDER_COLOR),
            ft.Container(height=DesignSystem.SPACING_MD),
            ft.Column(section_items, spacing=4),
            ft.Container(height=DesignSystem.SPACING_LG),
            ft.Divider(height=1, color=DesignSystem.BORDER_COLOR),
            ft.Container(height=DesignSystem.SPACING_MD),
            action_buttons,
        ], spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)
    
    def _build_content(self):
        """Build main content area"""
        if not self.current_section:
            return ft.Column([
                ft.Container(
                    content=ft.Column([
                        ft.Icon(
                            ft.Icons.DESCRIPTION if hasattr(ft.Icons, 'DESCRIPTION') else ft.Icons.ASSIGNMENT,
                            size=64,
                            color=DesignSystem.TEXT_SECONDARY,
                        ),
                        ft.Text(
                            translator.get_text("system_doc.select_section"),
                            size=18,
                            color=DesignSystem.TEXT_SECONDARY,
                        ),
                        ft.Text(
                            translator.get_text("system_doc.select_section_hint"),
                            size=14,
                            color=DesignSystem.TEXT_SECONDARY,
                        ),
                    ], spacing=16, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.padding.all(48),
                    alignment=ft.alignment.center,
                ),
            ], spacing=0, expand=True, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        
        # Get section content
        content = self._get_section_content(self.current_section)
        
        return ft.Column([
            # Header
            create_modern_card(
                content=ft.Column([
                    ft.Text(
                        content["title"],
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=DesignSystem.TEXT_PRIMARY,
                    ),
                    ft.Text(
                        content.get("subtitle", ""),
                        size=14,
                        color=DesignSystem.TEXT_SECONDARY,
                    ),
                ], spacing=8),
                padding=DesignSystem.SPACING_MD,
            ),
            
            ft.Container(height=DesignSystem.SPACING_LG),
            
            # Content
            create_modern_card(
                content=ft.Column([
                    self._build_section_body(content),
                ], spacing=16),
                padding=DesignSystem.SPACING_LG,
            ),
        ], spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)
    
    def _get_section_content(self, section_key: str) -> Dict:
        """Get content for a specific section"""
        # Read documentation files and build content
        # Use path relative to project root
        project_root = Path(__file__).parent.parent.parent
        docs_dir = project_root / "docs"
        
        sections = {
            "rendszer_attekintes": {
                "title": translator.get_text("system_doc.sections.overview"),
                "subtitle": translator.get_text("system_doc.sections.overview_subtitle"),
                "file": docs_dir / "SYSTEM_ARCHITECTURE_ANALYSIS.md",
            },
            "logikai_analizis": {
                "title": translator.get_text("system_doc.sections.logical_analysis"),
                "subtitle": translator.get_text("system_doc.sections.logical_analysis_subtitle"),
                "file": docs_dir / "DEEP_LOGICAL_ANALYSIS.md",
            },
            "logikai_fa": {
                "title": translator.get_text("system_doc.sections.logical_tree"),
                "subtitle": translator.get_text("system_doc.sections.logical_tree_subtitle"),
                "file": docs_dir / "LOGICAL_TREE_DIAGRAM.md",
            },
            "munkafolyamatok": {
                "title": translator.get_text("system_doc.sections.workflows"),
                "subtitle": translator.get_text("system_doc.sections.workflows_subtitle"),
                "file": docs_dir / "SYSTEM_WORKFLOW_DIAGRAM.md",
            },
            "entitasok_muveletei": {
                "title": translator.get_text("system_doc.sections.entity_operations"),
                "subtitle": translator.get_text("system_doc.sections.entity_operations_subtitle"),
                "file": None,  # Will be built from code
            },
            "javaslatok": {
                "title": translator.get_text("system_doc.sections.improvements"),
                "subtitle": translator.get_text("system_doc.sections.improvements_subtitle"),
                "file": docs_dir / "SYSTEM_IMPROVEMENTS_RECOMMENDATIONS.md",
            },
            "osszefoglalo": {
                "title": translator.get_text("system_doc.sections.summary"),
                "subtitle": translator.get_text("system_doc.sections.summary_subtitle"),
                "file": docs_dir / "COMPLETE_ANALYSIS_SUMMARY.md",
            },
        }
        
        section_info = sections.get(section_key, {})
        
        # Read file content if available
        content_text = ""
        if section_info.get("file") and section_info["file"].exists():
            try:
                content_text = section_info["file"].read_text(encoding='utf-8')
            except Exception as e:
                logger.error(f"Error reading documentation file: {e}")
                content_text = translator.get_text("system_doc.error.reading_file")
        
        # For entity operations, build from code
        if section_key == "entitasok_muveletei":
            content_text = self._build_entity_operations_content()
        
        return {
            "title": section_info.get("title", ""),
            "subtitle": section_info.get("subtitle", ""),
            "content": content_text,
        }
    
    def _build_entity_operations_content(self) -> str:
        """Build entity operations step-by-step descriptions"""
        # This will be built from the workflow diagrams and service code
        content = """# Entitás Műveletek - Lépésről Lépésre Leírások

## PM Task (Preventive Maintenance Task)

### Létrehozás
1. PM menü → "Új feladat" gomb
2. Gép kiválasztása
3. Feladat neve és leírás megadása
4. Prioritás beállítása
5. Határidő beállítása
6. Hozzárendelés (globális vagy felhasználóhoz)
7. Mentés

**Automatikus folyamatok:**
- Workflow validáció (workflow_service)
- Notification küldés (notification_service)
- Work Request PDF generálás (pdf_service)
- SystemLog bejegyzés (log_service)

### Elvégzés
1. PM menü → "Elvégzés" gomb a feladathoz
2. Completion dialog megnyitása
3. Dátum és idő megadása
4. Munka leírása
5. Megfigyelések rögzítése
6. Státusz választás (kész/részleges/problémás)
7. Alkatrészek hozzáadása (opcionális):
   - Part kiválasztás
   - Mennyiség megadása
   - Storage location kiválasztás
8. Fájlok feltöltése (opcionális)
9. Mentés

**Automatikus folyamatok:**
- PMHistory létrehozása
- Worksheet automatikus létrehozása (ha alkatrész használva)
- WorkRequestPDF generálás
- PMWorksheetPDF generálás
- Scrapping Documents generálás (ha alkatrész)
- Fájlok mentése (PMTaskAttachment)
- Notification küldés
- SystemLog bejegyzés

## Worksheet (Munkalap)

### Létrehozás
1. Worksheets menü → "Új munkalap" gomb
2. Gép kiválasztása
3. Cím és leírás megadása
4. Hozzárendelt felhasználó kiválasztása
5. Mentés

**Automatikus folyamatok:**
- Notification küldés
- SystemLog bejegyzés

### Alkatrész hozzáadása
1. Worksheet részletek → "Alkatrész hozzáadása" gomb
2. Part kiválasztása
3. Mennyiség megadása
4. Storage location kiválasztása
5. Mentés

**Automatikus folyamatok:**
- Készlet ellenőrzés (InventoryLevel)
- PartLocation frissítés (storage_service)
- StockTransaction létrehozás (transaction_service)
- Scrapping Document generálás (ha auto-generate enabled)
- SystemLog bejegyzés

### Lezárás
1. Worksheet részletek → "Lezárás" gomb
2. Javítás befejezés időpontjának megadása
3. Mentés

**Automatikus folyamatok:**
- Workflow validáció
- Downtime kalkuláció
- WorksheetPDF generálás
- Scrapping Documents generálás (ha van alkatrész)
- Notification küldés
- SystemLog bejegyzés

## Part (Alkatrész)

### Létrehozás
1. Inventory/Alkatrészek menü → "Új alkatrész" gomb
2. SKU megadása (validáció: egyedi, formátum ellenőrzés)
3. Név megadása
4. Kategória, beszállító (opcionális)
5. Ár információk (vételár, eladási ár)
6. Készlet szint információk (safety stock, reorder quantity)
7. Kezdeti mennyiség (opcionális)
8. Storage location hozzárendelés (opcionális)
9. Mentés

**Automatikus folyamatok:**
- SKU validáció (validators.validate_sku)
- InventoryLevel automatikus létrehozás (quantity_on_hand=0)
- StockTransaction létrehozás (ha initial_quantity > 0)
- PartLocation létrehozás (ha storage_location megadva)
- SystemLog bejegyzés

### Készletbevétel
1. Inventory/Alkatrészek menü → Part kiválasztás → "Készletbevétel" gomb
2. Mennyiség megadása
3. Storage location kiválasztása (csak releváns helyek: üres vagy azonos SKU)
4. Mentés

**Automatikus folyamatok:**
- PartLocation létrehozás/frissítés
- InventoryLevel frissítés
- StockTransaction létrehozás
- Validáció (InventoryLevel ↔ PartLocation)
- SystemLog bejegyzés

## Machine (Gép)

### Létrehozás
1. Assets menü → Production Line kiválasztás → "Új gép" gomb
2. Alap információk: név, sorozatszám, modell, gyártó
3. Dátum információk: install date, purchase date, warranty expiry
4. Operációs információk: operating hours, maintenance interval
5. Fizikai információk: tömeg, méretek
6. Finanszírozási információk: purchase price, supplier
7. Kompatibilis alkatrészek hozzárendelése
8. Mentés

**Automatikus folyamatok:**
- SystemLog bejegyzés
- AssetHistory bejegyzés

### Karbantartás igénylése
1. Production Line menü → Gép kiválasztás → "Karbantartás igénylése" gomb
2. Feladat neve és leírás megadása
3. Hozzárendelés (globális vagy felhasználóhoz)
4. Prioritás beállítása
5. Határidő beállítása
6. Mentés

**Automatikus folyamatok:**
- PMTask létrehozása (pm_service.create_pm_task)
- Notification küldés
- Work Request PDF generálás

## Storage Location (Raktárhely)

### Létrehozás
1. Storage menü → "Új raktárhely" gomb
2. Név megadása
3. Szülő hely kiválasztása (opcionális - hierarchikus struktúra)
4. Típus, kód, leírás (opcionális)
5. Mentés

**Automatikus folyamatok:**
- Hierarchia validáció (cirkuláris referencia ellenőrzés)
- SystemLog bejegyzés

### Alkatrész hozzárendelés
1. Storage menü → Part kiválasztás → "Tárhelyhez rendelés" gomb
2. Storage location kiválasztása (csak releváns: üres vagy azonos SKU)
3. Mennyiség megadása
4. Mentés

**Automatikus folyamatok:**
- PartLocation létrehozás/frissítés
- InventoryLevel frissítés
- Validáció (InventoryLevel ↔ PartLocation)
- SystemLog bejegyzés
"""
        return content
    
    def _build_section_body(self, content: Dict) -> ft.Control:
        """Build the body of a documentation section"""
        # Convert markdown-like content to Flet controls
        content_text = content.get("content", "")
        
        # Simple markdown parsing for display
        lines = content_text.split('\n')
        controls = []
        
        for line in lines:
            line = line.strip()
            if not line:
                controls.append(ft.Container(height=12))
                continue
            
            # Headers
            if line.startswith('# '):
                controls.append(ft.Text(
                    line[2:],
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=DesignSystem.TEXT_PRIMARY,
                ))
            elif line.startswith('## '):
                controls.append(ft.Text(
                    line[3:],
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=DesignSystem.TEXT_PRIMARY,
                ))
            elif line.startswith('### '):
                controls.append(ft.Text(
                    line[4:],
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=DesignSystem.TEXT_PRIMARY,
                ))
            # Lists
            elif line.startswith('- ') or line.startswith('* '):
                controls.append(ft.Row([
                    ft.Text('•', size=16, color=DesignSystem.TEXT_PRIMARY, width=20),
                    ft.Text(
                        line[2:],
                        size=14,
                        color=DesignSystem.TEXT_PRIMARY,
                        expand=True,
                    ),
                ], spacing=8))
            # Code blocks
            elif line.startswith('```'):
                continue  # Skip code block markers for now
            # Regular text
            else:
                controls.append(ft.Text(
                    line,
                    size=14,
                    color=DesignSystem.TEXT_PRIMARY,
                    selectable=True,
                ))
        
        return ft.Column(controls, spacing=8)
    
    def _select_section(self, section_key: str):
        """Select a documentation section"""
        self.current_section = section_key
        
        if self.content_container is not None:
            self.content_container.content = self._build_content()
        
        if self.sidebar_container is not None:
            self.sidebar_container.content = self._build_sidebar()
        
        self.page.update()
    
    def _download_docx(self, e):
        """Download documentation as DOCX"""
        try:
            def on_save_result(e: ft.FilePickerResultEvent):
                if e.path:
                    output_path = Path(e.path)
                    if not output_path.suffix or output_path.suffix.lower() != '.docx':
                        output_path = output_path.with_suffix('.docx')
                    
                    try:
                        docx_path = generate_system_documentation_docx(output_path)
                        
                        self.page.snack_bar = ft.SnackBar(
                            content=ft.Text(translator.get_text("system_doc.success.downloaded")),
                            bgcolor=DesignSystem.SUCCESS,
                        )
                        self.page.snack_bar.open = True
                        self.page.update()
                    except ImportError as import_error:
                        self.page.snack_bar = ft.SnackBar(
                            content=ft.Text(f"python-docx nincs telepítve: {import_error}"),
                            bgcolor=DesignSystem.ERROR,
                        )
                        self.page.snack_bar.open = True
                        self.page.update()
                else:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(translator.get_text("system_doc.error.cancelled")),
                        bgcolor=DesignSystem.INFO,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
            
            file_picker = ft.FilePicker(on_result=on_save_result)
            self.page.overlay.append(file_picker)
            self.page.update()
            
            file_picker.save_file(
                dialog_title=translator.get_text("system_doc.save_dialog_title"),
                file_name=f"system_documentation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx",
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["docx"],
            )
        except Exception as ex:
            logger.error(f"Error downloading documentation: {ex}", exc_info=True)
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(translator.get_text("system_doc.error.download_failed")),
                bgcolor=DesignSystem.ERROR,
            )
            self.page.snack_bar.open = True
            self.page.update()

