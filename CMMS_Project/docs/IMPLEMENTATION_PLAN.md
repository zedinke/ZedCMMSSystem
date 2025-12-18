# CMMS Rendszer - Teljes Implementációs Terv

**Dátum**: 2025.12.18  
**Cél**: Minden hiányosság pótlása, hibás logikák javítása, minden javaslat megvalósítása

---

## 📋 ÖSSZEFOGLALÓ

Ez a dokumentum tartalmazza a részletes implementációs tervet a `DEEP_LOGICAL_ANALYSIS.md` alapján azonosított minden javításhoz és fejlesztéshez.

---

## 🔍 JELENLEGI ÁLLAPOT ELEMZÉSE

### Logging Jelenlegi Helyzete

#### ✅ Már Implementálva (van log_action):

**PM Service:**
- ✅ `create_pm_task()` - VAN log_action (308-327 sorok)
- ✅ `update_pm_task()` - VAN log_action (399-414 sorok)
- ✅ `complete_pm_task()` - VAN log_action (666-684 sorok)

**Worksheet Service:**
- ⚠️ `create_worksheet()` - **NINCS log_action** (csak logger.info)
- ✅ `update_status()` - VAN log_action (172. sor körül)
- ❓ `add_part_to_worksheet()` - ELLENŐRIZENDŐ

**Inventory Service:**
- ✅ `create_part()` - VAN log_action (162. sor)
- ❓ `update_part()` - ELLENŐRIZENDŐ
- ❓ `delete_part()` - ELLENŐRIZENDŐ
- ❓ `adjust_stock()` - ELLENŐRIZENDŐ (van, de ellenőrizni kell)

**Storage Service:**
- ❓ `assign_part_to_location()` - ELLENŐRIZENDŐ
- ❓ `create_storage_location()` - ELLENŐRIZENDŐ

**Asset Service:**
- ❓ `create_machine()` - ELLENŐRIZENDŐ
- ❓ `update_machine()` - ELLENŐRIZENDŐ
- ❓ `delete_machine()` - ELLENŐRIZENDŐ

---

## 🎯 IMPLEMENTÁCIÓS FELADATOK

### PRIORITÁS 1: KRITIKUS (Azonnal javítandó)

#### P1.1: Hiányzó Logging Hozzáadása

**1.1.1 Worksheet Service - create_worksheet()**
- **Fájl:** `services/worksheet_service.py`
- **Sor:** ~57-128
- **Művelet:** Hozzáadni log_action() hívást a create_worksheet() függvényben
- **Kategória:** "worksheet"
- **Action Type:** "create"
- **Entity Type:** "Worksheet"
- **Példa metadata:** worksheet_title, machine_id, assigned_to_user_id

**1.1.2 Worksheet Service - add_part_to_worksheet()**
- **Fájl:** `services/worksheet_service.py`
- **Sor:** ~319-682
- **Művelet:** Ellenőrizni, van-e log_action, ha nincs, hozzáadni
- **Kategória:** "worksheet"
- **Action Type:** "update" (parts added)
- **Entity Type:** "WorksheetPart"

**1.1.3 Inventory Service - update_part()**
- **Fájl:** `services/inventory_service.py`
- **Sor:** ~853-968
- **Művelet:** Ellenőrizni, van-e log_action, ha nincs, hozzáadni
- **Kategória:** "inventory"
- **Action Type:** "update"
- **Entity Type:** "Part"
- **Metadata:** changes dictionary

**1.1.4 Inventory Service - delete_part()**
- **Fájl:** `services/inventory_service.py`
- **Sor:** ~970-1010
- **Művelet:** Ellenőrizni, van-e log_action, ha nincs, hozzáadni
- **Kategória:** "inventory"
- **Action Type:** "delete"
- **Entity Type:** "Part"

**1.1.5 Inventory Service - adjust_stock()**
- **Fájl:** `services/inventory_service.py`
- **Sor:** ~213-409
- **Művelet:** Ellenőrizni, van-e log_action, ha nincs, hozzáadni
- **Kategória:** "inventory"
- **Action Type:** "update"
- **Entity Type:** "InventoryLevel"
- **Megjegyzés:** Ez már lehet, hogy van a transaction_service-ben

**1.1.6 Storage Service - assign_part_to_location()**
- **Fájl:** `services/storage_service.py`
- **Sor:** ~371-535
- **Művelet:** Ellenőrizni, van-e log_action, ha nincs, hozzáadni
- **Kategória:** "inventory" vagy "storage"
- **Action Type:** "assign"
- **Entity Type:** "PartLocation"

**1.1.7 Storage Service - create_storage_location()**
- **Fájl:** `services/storage_service.py`
- **Művelet:** Ellenőrizni, van-e log_action, ha nincs, hozzáadni
- **Kategória:** "storage"
- **Action Type:** "create"
- **Entity Type:** "StorageLocation"

**1.1.8 Asset Service - create_machine()**
- **Fájl:** `services/asset_service.py`
- **Sor:** ~196-430
- **Művelet:** Ellenőrizni, van-e log_action, ha nincs, hozzáadni
- **Kategória:** "asset"
- **Action Type:** "create"
- **Entity Type:** "Machine"

**1.1.9 Asset Service - update_machine()**
- **Fájl:** `services/asset_service.py`
- **Sor:** ~469-690
- **Művelet:** Ellenőrizni, van-e log_action, ha nincs, hozzáadni
- **Kategória:** "asset"
- **Action Type:** "update"
- **Entity Type:** "Machine"
- **Metadata:** changes dictionary

**1.1.10 Asset Service - delete_machine()**
- **Fájl:** `services/asset_service.py`
- **Művelet:** Ellenőrizni, van-e log_action, ha nincs, hozzáadni
- **Kategória:** "asset"
- **Action Type:** "delete"
- **Entity Type:** "Machine"

#### P1.2: InventoryLevel ↔ PartLocation Automatikus Validáció

**1.2.1 Storage Service - assign_part_to_location() validáció hozzáadása**
- **Fájl:** `services/storage_service.py`
- **Függvény:** `assign_part_to_location()`
- **Művelet:** 
  1. Hozzáadni `validate_inventory_levels()` hívást a commit után
  2. Ha discrepancy van, logger.warning()
  3. Opcionálisan: return warning message vagy flag

**1.2.2 Storage Service - remove_part_from_location() validáció**
- **Fájl:** `services/storage_service.py`
- **Függvény:** `remove_part_from_location()` (ha létezik)
- **Művelet:** Ugyanaz, mint 1.2.1

**1.2.3 Inventory Service - adjust_stock() validáció**
- **Fájl:** `services/inventory_service.py`
- **Függvény:** `adjust_stock()`
- **Művelet:** 
  1. Hozzáadni `validate_inventory_levels()` hívást, ha storage_location_id megadva
  2. Warning ha discrepancy

**1.2.4 UI Warning Hozzáadása**
- **Fájl:** `ui/screens/storage_screen.py`
- **Művelet:** Warning megjelenítése, ha validáció discrepancy-t talál
- **Opcionális:** Auto-fix gomb

---

### PRIORITÁS 2: FONTOS (Rövid távon javítandó)

#### P2.1: Egységes Error Handling Pattern

**2.1.1 Error Handling Helper Függvény Létrehozása**
- **Fájl:** `utils/error_handler.py` (vagy új fájl: `utils/service_error_handler.py`)
- **Művelet:** 
  - Helper függvény létrehozása: `handle_service_error(func, *args, **kwargs)`
  - Decorator létrehozása: `@service_error_handler`
  - Egységes error logging pattern

**2.2.2 Error Handling Pattern Alkalmazása**
- **Módosítandó fájlok:** Összes service fájl (42 fájl)
- **Művelet:**
  - Minden service függvényben egységes try-except-finally struktúra
  - `exc_info=True` minden logger.error()-nál
  - Session rollback logging
  - Konzisztens error handling

#### P2.2: Workflow Service Bővítése

**2.2.1 Part State Enum és Rules Hozzáadása**
- **Fájl:** `services/workflow_service.py`
- **Művelet:**
  - `PartState` Enum létrehozása (ACTIVE, INACTIVE, OBSOLETE)
  - WORKFLOW_RULES dictionary bővítése "part" típussal
  - State transition validáció hozzáadása

**2.2.2 Machine State Enum és Rules Hozzáadása**
- **Fájl:** `services/workflow_service.py`
- **Művelet:**
  - `MachineState` Enum létrehozása (ACTIVE, STOPPED, MAINTENANCE, SCRAPPED)
  - WORKFLOW_RULES dictionary bővítése "machine" típussal
  - State transition validáció hozzáadása

**2.2.3 Part Service Workflow Integráció**
- **Fájl:** `services/inventory_service.py`
- **Függvény:** `update_part()` (ha van status mező)
- **Művelet:** Workflow validáció hozzáadása, ha status változik

**2.2.4 Machine Service Workflow Integráció**
- **Fájl:** `services/asset_service.py`
- **Függvény:** `update_machine()` (status mezőnél)
- **Művelet:** Workflow validáció hozzáadása status változáskor

---

### PRIORITÁS 3: JAVASOLT (Hosszú távon)

#### P3.1: Service Dokumentáció Fejlesztése

**3.1.1 Docstring Template Létrehozása**
- **Fájl:** `docs/SERVICE_DOCSTRING_TEMPLATE.md`
- **Művelet:** Standard docstring template létrehozása

**3.1.2 Főbb Service Függvények Dokumentálása**
- **Fájlok:** 
  - `services/pm_service.py` - minden fő függvény
  - `services/worksheet_service.py` - minden fő függvény
  - `services/inventory_service.py` - minden fő függvény
  - `services/storage_service.py` - minden fő függvény
  - `services/asset_service.py` - minden fő függvény
- **Művelet:** Részletes docstring hozzáadása minden függvényhez

#### P3.2: Unit Tesztek Írása

**3.2.1 Test Infrastructure Setup**
- **Fájlok:**
  - `tests/conftest.py` - pytest fixtures
  - `tests/services/__init__.py`
- **Művelet:** Test infrastructure létrehozása

**3.2.2 Főbb Service Függvények Tesztelése**
- **Fájlok:**
  - `tests/services/test_pm_service.py`
  - `tests/services/test_worksheet_service.py`
  - `tests/services/test_inventory_service.py`
  - `tests/services/test_storage_service.py`
  - `tests/services/test_asset_service.py`
  - `tests/services/test_workflow_service.py`
- **Művelet:** Unit tesztek írása

---

## 📝 IMPLEMENTÁCIÓS ÚTMUTATÓK

### Logging Hozzáadás Pattern

```python
def service_function(...):
    session, should_close = _get_session(session)
    try:
        # ... validáció, művelet ...
        
        session.commit()
        
        # ✅ Logging hozzáadása
        from services.log_service import log_action
        from services.context_service import get_current_user_id
        
        user_id = get_current_user_id() or user_id_param  # user_id_param ha van
        try:
            log_action(
                category="category_name",  # task, worksheet, inventory, asset, storage
                action_type="create",  # create, update, delete, assign, complete
                entity_type="EntityName",  # PMTask, Worksheet, Part, Machine, etc.
                entity_id=entity.id,
                user_id=user_id,
                description=f"Leírás magyarul: {entity.name}",
                metadata={
                    "key1": value1,
                    "key2": value2,
                    # ... releváns információk
                },
                session=session
            )
        except Exception as e:
            logger.warning(f"Error logging action: {e}")
        
        logger.info(f"Success: {operation_description}")
        return result
        
    except ValidationError as e:
        session.rollback()
        logger.warning(f"Validation error in {__name__}.{service_function.__name__}: {e}", exc_info=True)
        raise
    except BusinessLogicError as e:
        session.rollback()
        logger.warning(f"Business logic error in {__name__}.{service_function.__name__}: {e}", exc_info=True)
        raise
    except NotFoundError as e:
        session.rollback()
        logger.warning(f"Not found error in {__name__}.{service_function.__name__}: {e}", exc_info=True)
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Unexpected error in {__name__}.{service_function.__name__}: {e}", exc_info=True)
        raise
    finally:
        if should_close:
            session.close()
```

### Validáció Hozzáadás Pattern

```python
def assign_part_to_location(...):
    session, should_close = _get_session(session)
    try:
        # ... meglévő logika ...
        
        session.commit()
        
        # ✅ Validáció hozzáadása
        from services.inventory_service import validate_inventory_levels
        
        discrepancies = validate_inventory_levels(part_id=part_id, session=session)
        if discrepancies:
            logger.warning(
                f"Inventory level discrepancy detected for part {part_id}: "
                f"inventory_level={discrepancies[0]['inventory_level_qty']}, "
                f"total_in_locations={discrepancies[0]['total_in_locations_qty']}, "
                f"difference={discrepancies[0]['difference']}"
            )
            # Opcionálisan: return warning flag vagy raise Warning
            
        # ... további logika (pl. logging) ...
        
    finally:
        if should_close:
            session.close()
```

---

## ✅ ELLENŐRZÉSI LISTA

- [ ] P1.1.1: worksheet_service.create_worksheet() logging
- [ ] P1.1.2: worksheet_service.add_part_to_worksheet() logging
- [ ] P1.1.3: inventory_service.update_part() logging
- [ ] P1.1.4: inventory_service.delete_part() logging
- [ ] P1.1.5: inventory_service.adjust_stock() logging (ellenőrzés)
- [ ] P1.1.6: storage_service.assign_part_to_location() logging
- [ ] P1.1.7: storage_service.create_storage_location() logging
- [ ] P1.1.8: asset_service.create_machine() logging
- [ ] P1.1.9: asset_service.update_machine() logging
- [ ] P1.1.10: asset_service.delete_machine() logging
- [ ] P1.2.1: storage_service.assign_part_to_location() validáció
- [ ] P1.2.2: storage_service.remove_part_from_location() validáció (ha létezik)
- [ ] P1.2.3: inventory_service.adjust_stock() validáció
- [ ] P1.2.4: UI warning hozzáadása
- [ ] P2.1.1: Error handling helper létrehozása
- [ ] P2.1.2: Error handling pattern alkalmazása
- [ ] P2.2.1: Part State workflow hozzáadása
- [ ] P2.2.2: Machine State workflow hozzáadása
- [ ] P2.2.3: Part service workflow integráció
- [ ] P2.2.4: Machine service workflow integráció
- [ ] P3.1.1: Docstring template létrehozása
- [ ] P3.1.2: Főbb függvények dokumentálása
- [ ] P3.2.1: Test infrastructure setup
- [ ] P3.2.2: Unit tesztek írása

---

**Készítve:** AI Assistant  
**Dátum:** 2025.12.18  
**Verzió:** 1.0

