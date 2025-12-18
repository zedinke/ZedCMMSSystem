# CMMS Rendszer Javítási Javaslatok - Prioritások

**Dátum**: 2025.12.18  
**Status**: Elemzés kész, javítási javaslatok prioritásokkal

---

## 📋 ÖSSZEFOGLALÓ

A rendszer áttekintése során **6 fő problémát** azonosítottam:

1. ✅ **PMHistory ↔ Worksheet kapcsolat** - Már létezik DB-ben, de UI-ban nincs mutatva
2. ❌ **Inventory + Storage szétválasztás** - Nem intuitív workflow
3. ❌ **Service Records hiányos** - Nem egyértelmű, mit tartalmaz
4. ⚠️ **PM Task alkatrész használat duplikáció** - Logikai kérdés
5. ⚠️ **InventoryLevel ↔ PartLocation validáció** - Adatintegritás
6. ⚠️ **Production Line navigáció** - Felhasználói élmény

---

## 🚨 PRIORITÁS 1: KRITIKUS (Azonnal javítandó)

### 1.1 PMHistory ↔ Worksheet Kapcsolat UI-ban

**Probléma:**
- PM Task elvégzésekor létrejön Worksheet, de nem látszik a kapcsolat
- Felhasználó nem tudja, melyik Worksheet melyik PM Task-ból jött

**Megoldás:**

#### A) PM Screen - Elvégzett Task részleteknél
```python
# pm_screen.py - open_completed_task_details() függvényben

# Hozzáadás a részletekhez:
if last_history.worksheet_id:
    worksheet_link = ft.Row([
        ft.Text(translator.get_text("preventive_maintenance.worksheet") + ": "),
        ft.TextButton(
            f"Worksheet #{last_history.worksheet_id}",
            on_click=lambda _: page.go(f"/worksheets/detail/{last_history.worksheet_id}")
        )
    ])
    # Hozzáadás a dialog content-hoz
```

#### B) Worksheet Screen - Részleteknél
```python
# worksheet_screen.py - részletek megjelenítésénél

# Keressük meg, hogy van-e PMHistory ezzel a worksheet_id-vel
pm_history = session.query(PMHistory).filter_by(worksheet_id=worksheet.id).first()
if pm_history:
    pm_link = ft.Row([
        ft.Text("PM Task: "),
        ft.TextButton(
            pm_history.pm_task.task_name,
            on_click=lambda _: page.go(f"/pm?task_id={pm_history.pm_task_id}")
        )
    ])
```

**Fájlok módosítandók:**
- `ui/screens/pm_screen.py`
- `ui/screens/worksheet_screen.py`

---

### 1.2 Inventory + Storage Integráció

**Probléma:**
- Új alkatrész létrehozásakor nincs lehetőség tárhely hozzárendelésére
- Külön menüpont kell a hozzárendeléshez

**Megoldás:**

#### A) Inventory Screen - Új alkatrész dialog bővítése

```python
# inventory_screen.py - open_add_part_dialog() függvényben

# Hozzáadás az initial_quantity_field után:
storage_section = ft.Container(
    content=ft.Column([
        ft.Text(
            translator.get_text("storage.assign_to_location"),
            weight=ft.FontWeight.BOLD,
            size=16
        ),
        StorageLocationPicker(page=page, part_id=None),  # None, mert új part
        ft.Text(
            translator.get_text("storage.assign_location_hint"),
            size=12,
            color=ft.colors.GREY_600,
            italic=True
        )
    ]),
    padding=10,
    visible=True  # Mindig látható
)

# A dialog content-hoz hozzáadás
dialog.content = ft.Container(
    content=ft.Column([
        # ... meglévő mezők ...
        initial_quantity_field,
        ft.Divider(),
        storage_section,  # ÚJ
        # ... többi mezők ...
    ])
)
```

#### B) Storage assignment a create_part során

```python
# inventory_screen.py - submit_add_part() függvényben

# Part létrehozása után:
if storage_picker and storage_picker.get_value():
    location_id, other_location = storage_picker.get_value()
    if location_id:
        from services.storage_service import assign_part_to_location
        assign_part_to_location(
            part_id=new_part.id,
            storage_location_id=location_id,
            quantity=initial_quantity or 0
        )
```

**Fájlok módosítandók:**
- `ui/screens/inventory_screen.py`

---

## 🔴 PRIORITÁS 2: FONTOS (1-2 hét alatt)

### 2.1 Service Records Átstruktúrálás

**Probléma:**
- Nem egyértelmű, mit tartalmaz
- Nincs összekapcsolva PMHistory és Worksheet rekordokkal

**Megoldás:**

```python
# service_records_screen.py - Új struktúra

def view(self, page: ft.Page):
    # Tab-ok:
    tabs = ft.Tabs([
        ft.Tab(text="Összes", icon=ft.Icons.LIST),
        ft.Tab(text="PM Tasks", icon=ft.Icons.BUILD),
        ft.Tab(text="Worksheets", icon=ft.Icons.DESCRIPTION),
    ])
    
    # Összes tab: PMHistory + Worksheet egyesített lista
    # Timeline nézet dátum szerint csoportosítva
    # Szűrők: gép, dátum, felhasználó
```

**Fájlok módosítandók:**
- `ui/screens/service_records_screen.py`
- `services/service_records_service.py` (ha létezik)

---

### 2.2 InventoryLevel ↔ PartLocation Validáció

**Probléma:**
- InventoryLevel.quantity_on_hand nem mindig egyezik PartLocation[] összegével
- Nincs validáció

**Megoldás:**

```python
# services/inventory_service.py - Új függvény

def validate_inventory_levels(part_id: Optional[int] = None, session: Session = None):
    """Validálja, hogy InventoryLevel = SUM(PartLocation.quantity)"""
    session, should_close = _get_session(session)
    try:
        query = session.query(Part, InventoryLevel, func.sum(PartLocation.quantity).label('total_in_locations'))
        query = query.join(InventoryLevel).outerjoin(PartLocation)
        
        if part_id:
            query = query.filter(Part.id == part_id)
        
        query = query.group_by(Part.id, InventoryLevel.id)
        
        discrepancies = []
        for part, inv_level, total_locations in query.all():
            total = total_locations or 0
            if inv_level.quantity_on_hand != total:
                discrepancies.append({
                    'part_id': part.id,
                    'part_name': part.name,
                    'inventory_level': inv_level.quantity_on_hand,
                    'total_in_locations': total,
                    'difference': inv_level.quantity_on_hand - total
                })
        
        return discrepancies
    finally:
        if should_close:
            session.close()
```

**UI-ban:**
- Storage menüben "Validáció" gomb
- Ha van eltérés, warning és javítási lehetőség

**Fájlok módosítandók:**
- `services/inventory_service.py` vagy új `services/validation_service.py`
- `ui/screens/storage_screen.py`

---

## 🟡 PRIORITÁS 3: JAVASOLT (1-2 hónap alatt)

### 3.1 PM Task Alkatrész Használat Egyeztetés

**Probléma:**
- PM Task elvégzésekor lehet alkatrészt használni
- Aztán automatikusan létrejön Worksheet
- Lehet duplikáció

**Megoldás - Lehetőségek:**

#### Opció A: PM Task-ból NE hozzon létre Worksheet-et
- Csak akkor hozzon létre, ha explicit módon kéri
- Alkatrész használat → csak PMHistory-ben rögzítés

#### Opció B: PM Task alkatrészei átkerülnek Worksheet-be
- Ha PM Task-ból jön Worksheet, akkor az alkatrészek automatikusan átkerülnek
- UI-ban jelölés: "PM Task-ból származik"

#### Opció C: Két külön workflow
- PM Task elvégzés → csak dokumentumok (nincs Worksheet)
- Ha Worksheet kell → külön létrehozás, manuális alkatrész hozzáadás

**Ajánlás: Opció B** - Egyszerűbb és logikusabb

---

### 3.2 Production Line Navigáció Javítás

**Probléma:**
- Jelenleg minden gép és alkatrész egy oldalon van
- Nehéz navigálni

**Megoldás:**

```python
# production_line_screen.py - select_production_line() módosítás

# Tab-ok használata:
tabs = ft.Tabs([
    ft.Tab(text="Gépek", icon=ft.Icons.FACTORY),
    ft.Tab(text="Alkatrészek", icon=ft.Icons.INVENTORY_2),
    ft.Tab(text="PM Tasks", icon=ft.Icons.BUILD),
])

# Gépek tab:
# - Jelenlegi gép lista ExpansionTile-okkal
# - Gép kiválasztás → részletes információk
# - "Karbantartás igénylése" gomb

# Alkatrészek tab:
# - Összes kompatibilis alkatrész listája (gépek szerint csoportosítva)
# - Kattintás → részletes alkatrész információk

# PM Tasks tab:
# - A termelési sorhoz tartozó gépek PM Task-jai
# - Szűrhető státusz, prioritás szerint
```

**Fájlok módosítandók:**
- `ui/screens/production_line_screen.py`

---

## 📊 ÖSSZEFOGLALÓ TABELLA

| Priorítás | Probléma | Javasolt Megoldás | Becsült Idő | Fájlok |
|-----------|----------|-------------------|-------------|--------|
| 🚨 P1 | PMHistory ↔ Worksheet UI link | Linkek hozzáadása mindkét oldalon | 2-3 óra | pm_screen.py, worksheet_screen.py |
| 🚨 P1 | Inventory + Storage integráció | Új alkatrész dialog bővítése | 3-4 óra | inventory_screen.py |
| 🔴 P2 | Service Records átstruktúrálás | Összesítő nézet + Timeline | 4-6 óra | service_records_screen.py |
| 🔴 P2 | InventoryLevel validáció | Validáció függvény + UI gomb | 3-4 óra | inventory_service.py, storage_screen.py |
| 🟡 P3 | PM alkatrész duplikáció | Workflow egyeztetés | 4-5 óra | pm_service.py, pm_screen.py |
| 🟡 P3 | Production Line navigáció | Tab-ok használata | 3-4 óra | production_line_screen.py |

**Összes becsült idő: 19-26 óra**

---

## 🎯 KÖVETKEZŐ LÉPÉSEK

1. **Első**: PMHistory ↔ Worksheet linkek hozzáadása (legkönnyebb, legfontosabb)
2. **Második**: Inventory + Storage integráció (felhasználói élmény javítás)
3. **Harmadik**: Service Records átstruktúrálás (logika egyértelműsítés)
4. **Negyedik**: Validáció és egyéb javítások

---

## 📝 MEGJEGYZÉSEK

- Az ábrák és elemzések a `docs/SYSTEM_ARCHITECTURE_ANALYSIS.md` fájlban találhatók
- A workflow ábrák a `docs/SYSTEM_WORKFLOW_DIAGRAM.md` fájlban vannak
- Minden javítás után érdemes tesztelni a teljes workflow-t végig

