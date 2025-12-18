"""
Storage Location Picker Component
Dropdown with hierarchical locations + "Other" option for manual entry
"""

import flet as ft
from services.storage_service import get_all_storage_locations_flat
from database.session_manager import SessionLocal
from localization.translator import translator
from ui.components.modern_components import create_modern_dropdown, create_modern_text_field, DesignSystem


class StorageLocationPicker:
    """Component for selecting storage location with 'Other' option"""
    
    def __init__(self, page: ft.Page = None):
        self.page = page
        self.dropdown = None
        self.other_field = None
        self.container = None
        self._selected_location_id = None
        self._other_text = None
    
    def build(
        self,
        label: str = None,
        value: int = None,
        other_value: str = None,
        on_change=None,
        width: int = None,
        part_id: int = None  # Optional: filter locations for this specific part
    ) -> ft.Control:
        """Build the storage location picker component
        
        Args:
            part_id: If provided, only show empty locations OR locations containing this part (same SKU)
        """
        session = SessionLocal()
        try:
            from database.models import StorageLocation, PartLocation
            # Get all active locations
            all_locations = get_all_storage_locations_flat(session)
            
            # Get all locations that have children (these are parent locations)
            # These are locations that are referenced as parent_id by other active locations
            parent_ids = {
                row[0] for row in session.query(StorageLocation.parent_id)
                .filter(StorageLocation.parent_id.isnot(None))
                .filter(StorageLocation.is_active == True)
                .distinct()
                .all()
            }
            
            # Filter to only leaf nodes (locations without children)
            leaf_locations = [loc for loc in all_locations if loc.id not in parent_ids]
            
            # If part_id is provided, filter locations to only show locations with this part
            part_location_quantities = {}  # {location_id: quantity}
            part_unit = "db"  # Default unit
            if part_id is not None:
                # Get the part to get its unit
                from database.models import Part
                part = session.query(Part).filter_by(id=part_id).first()
                if part and part.unit:
                    part_unit = part.unit
                
                # Get locations that have THIS specific part assigned, with quantities
                part_locations = session.query(PartLocation).filter_by(part_id=part_id).all()
                
                # Build dict of location_id -> quantity
                for pl in part_locations:
                    part_location_quantities[pl.storage_location_id] = pl.quantity
                
                # Filter: only show locations that have this specific part (NO empty locations)
                filtered_locations = []
                location_ids_with_part = set(part_location_quantities.keys())
                for loc in leaf_locations:
                    if loc.id in location_ids_with_part:
                        filtered_locations.append(loc)
                
                leaf_locations = filtered_locations
            
            # Build dropdown options
            options = [ft.dropdown.Option("", translator.get_text("common.none"))]
            # Only add "__OTHER__" option if part_id is not provided (for general use)
            if part_id is None:
                options.append(ft.dropdown.Option("__OTHER__", translator.get_text("storage.other_location")))
            
            for loc in leaf_locations:
                # Show location name with quantity if part_id is provided
                if part_id is not None and loc.id in part_location_quantities:
                    quantity = part_location_quantities[loc.id]
                    display_text = f"{loc.name} ({quantity} {part_unit})"
                else:
                    display_text = loc.name
                options.append(ft.dropdown.Option(str(loc.id), display_text))
            
            # Determine initial value
            initial_value = ""
            if value:
                initial_value = str(value)
            elif other_value:
                initial_value = "__OTHER__"
            
            # Create dropdown
            self.dropdown = create_modern_dropdown(
                label=label or translator.get_text("storage.location"),
                value=initial_value,
                options=options,
                on_change=lambda e: self._on_dropdown_change(e, on_change),
                width=width
            )
            
            # Create other text field (initially hidden)
            self.other_field = create_modern_text_field(
                label=translator.get_text("storage.other_location_text"),
                value=other_value or "",
                hint_text=translator.get_text("storage.enter_location_manually"),
                width=width,
                on_change=lambda e: self._on_other_change(e, on_change)
            )
            
            # Set visibility - hide initially, show if "__OTHER__" is selected
            self.other_field.visible = (initial_value == "__OTHER__")
            
            # Container with both controls
            self.container = ft.Column(
                controls=[self.dropdown, self.other_field],
                spacing=8,
                tight=True
            )
            
            return self.container
        finally:
            session.close()
    
    def _on_dropdown_change(self, e, on_change_callback):
        """Handle dropdown value change"""
        value = e.control.value
        
        if value == "__OTHER__":
            # Show other field
            self.other_field.visible = True
            self._selected_location_id = None
            self._other_text = self.other_field.value or ""
        elif value == "":
            # None selected
            self.other_field.visible = False
            self._selected_location_id = None
            self._other_text = None
        else:
            # Location selected
            self.other_field.visible = False
            self._selected_location_id = int(value)
            self._other_text = None
        
        if self.page:
            self.page.update()
        
        if on_change_callback:
            on_change_callback(e)
    
    def _on_other_change(self, e, on_change_callback):
        """Handle other text field change"""
        self._other_text = e.control.value
        if on_change_callback:
            on_change_callback(e)
    
    def get_value(self) -> tuple:
        """
        Get selected value
        Returns: (location_id: Optional[int], other_text: Optional[str])
        """
        return (self._selected_location_id, self._other_text)
    
    def set_value(self, location_id: int = None, other_text: str = None):
        """Set the picker value"""
        if other_text:
            self.dropdown.value = "__OTHER__"
            self.other_field.value = other_text
            self.other_field.visible = True
            self._selected_location_id = None
            self._other_text = other_text
        elif location_id:
            self.dropdown.value = str(location_id)
            self.other_field.visible = False
            self._selected_location_id = location_id
            self._other_text = None
        else:
            self.dropdown.value = ""
            self.other_field.visible = False
            self._selected_location_id = None
            self._other_text = None
        
        if self.page:
            self.page.update()


