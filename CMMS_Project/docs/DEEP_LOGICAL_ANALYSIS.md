# CMMS Rendszer - Mélyreható Logikai Analízis

**Dátum**: 2025.12.18  
**Verzió**: v1.0.6  
**Cél**: Teljes rendszer logikai struktúrájának és munkafolyamatainak részletes értékelése

---

## 📊 TARTALOMJEGYZÉK

1. [Rendszer Struktúra Áttekintése](#1-rendszer-struktúra-áttekintése)
2. [Logikai Fa (Logical Tree)](#2-logikai-fa-logical-tree)
3. [Naplózás (Logging) Analízis](#3-naplózás-logging-analízis)
4. [Munkafolyamatok (Workflows)](#4-munkafolyamatok-workflows)
5. [Probléma Azonosítás](#5-probléma-azonosítás)
6. [Javaslatok és Prioritások](#6-javaslatok-és-prioritások)

---

## 1. RENDSZER STRUKTÚRA ÁTTEKINTÉSE

### 1.1 Fő Komponensek

```
CMMS Rendszer
│
├─── API Layer (FastAPI)
│    ├─── Authentication (JWT tokens)
│    ├─── REST API endpoints
│    └─── API Documentation
│
├─── UI Layer (Flet Framework)
│    ├─── 19 Screen komponens
│    ├─── Komponensek (Components)
│    └─── Navigáció (Routing)
│
├─── Service Layer (42 Service modul)
│    ├─── Core Services (Auth, User, Permission)
│    ├─── Asset Services (Assets, Production Lines, Lifecycle)
│    ├─── Inventory Services (Parts, Storage, Transactions)
│    ├─── Maintenance Services (PM, Worksheets, Service Records)
│    ├─── Reporting Services (Reports, Charts, Excel Export)
│    ├─── System Services (Settings, Logging, Backup, Audit)
│    └─── Utility Services (Notifications, Search, Workflow)
│
├─── Database Layer (SQLAlchemy ORM)
│    ├─── Models (30+ entitás)
│    ├─── Relationships (Foreign Keys, Relationships)
│    ├─── Migrations (Alembic)
│    └─── Session Management
│
└─── Infrastructure
     ├─── Logging System (Rotating logs)
     ├─── Localization (HU/EN)
     ├─── Error Handling
     └─── Configuration Management
```

### 1.2 Service Modulok Listája (42 modul)

#### Core Services
- `auth_service.py` - Autentikáció, session kezelés
- `user_service.py` - Felhasználókezelés
- `permission_service.py` - Jogosultságkezelés
- `context_service.py` - Alkalmazás kontextus (current user, IP, etc.)
- `log_service.py` - Rendszer naplózás (SystemLog)
- `audit_service.py` - Audit logok (AuditLog)

#### Asset Management Services
- `asset_service.py` - Gépek, Production Lines CRUD
- `asset_lifecycle_service.py` - Életciklus statisztikák
- `depreciation_service.py` - Értékcsökkenés számítások

#### Inventory Services
- `inventory_service.py` - Alkatrészek, beszállítók, készletmozgások
- `storage_service.py` - Tárhelyek hierarchikus kezelése
- `storage_history_service.py` - Tárhely előzmények
- `storage_document_service.py` - Tárhely dokumentumok
- `reservation_service.py` - Készlet foglalások
- `transaction_service.py` - Készlet tranzakciók (dekorátor)
- `inventory_audit_service.py` - Készletellenőrzés
- `inventory_audit_excel_service.py` - Excel export

#### Maintenance Services
- `pm_service.py` - Preventív karbantartás (PM Tasks, PMHistory)
- `worksheet_service.py` - Munkalapok (Worksheets, WorksheetParts)
- `service_record_service.py` - Szerviz feljegyzések
- `scrapping_service.py` - Selejtezési dokumentumok
- `safety_service.py` - Biztonsági események (SafetyIncidents, LOTO, etc.)

#### Reporting Services
- `reports_service.py` - Jelentések, statisztikák
- `reports_service_extended.py` - Bővített jelentések
- `chart_service.py` - Grafikonok generálása
- `excel_export_service.py` - Excel exportálás
- `pdf_service.py` - PDF generálás
- `report_templates_service.py` - Jelentés sablonok
- `scheduled_reports_service.py` - Ütemezett jelentések

#### Notification & Communication
- `notification_service.py` - Értesítések (bell icon)
- `shift_service.py` - Műszak beosztás
- `vacation_service.py` - Szabadságkezelés

#### System Services
- `settings_service.py` - Alkalmazás beállítások
- `backup_service.py` - Adatbázis backup
- `update_service.py` - Frissítéskezelés
- `scheduler_service.py` - Ütemezett feladatok
- `search_service.py` - Globális keresés

#### Utility Services
- `workflow_service.py` - **KÖZPONTI** állapot átmenetek (PM Task, Worksheet)
- `site_service.py` - Multi-site/multi-tenant támogatás (kevésbé használt)

---

## 2. LOGIKAI FA (LOGICAL TREE)

### 2.1 Entitás Hierarchia és Kapcsolatok

```
┌──────────────────────────────────────────────────────────────────────┐
│                        USER & AUTHENTICATION                         │
│  User ──┐                                                           │
│         ├─── Role (permissions)                                     │
│         ├─── UserSession (JWT tokens)                               │
│         ├─── SystemLog (műveletek naplózása)                        │
│         └─── AuditLog (audit trail)                                 │
└──────────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────────────┐
│                      PRODUCTION STRUCTURE                            │
│                                                                      │
│  ProductionLine (Termelési sor)                                     │
│      │                                                               │
│      ├─── 1:N ─── Machine (Gép)                                    │
│      │      │                                                       │
│      │      ├─── M:N ─── Part (Alkatrész) [kompatibilis]           │
│      │      │      │                                                │
│      │      │      └─── CompatibleMachine (junction table)          │
│      │      │                                                       │
│      │      ├─── 1:N ─── PMTask (Karbantartási feladat)            │
│      │      │      │                                                │
│      │      │      └─── 1:N ─── PMHistory (Karbantartási történet) │
│      │      │              │                                        │
│      │      │              ├─── 1:1 ─── WorkRequestPDF              │
│      │      │              ├─── 1:1 ─── PMWorksheetPDF              │
│      │      │              ├─── 1:N ─── ScrappingDocument[]         │
│      │      │              ├─── 1:N ─── PMTaskAttachment (Fájlok)   │
│      │      │              └─── 1:1 ─── Worksheet (opcionális)      │
│      │      │                                                       │
│      │      └─── 1:N ─── Worksheet (Munkalap)                      │
│      │              │                                                │
│      │              ├─── 1:N ─── WorksheetPart (Felhasznált alk.)   │
│      │              │      │                                        │
│      │              │      └─── N:1 ─── Part                        │
│      │              │                                                │
│      │              ├─── 1:1 ─── WorksheetPDF                       │
│      │              └─── 1:1 ─── PMHistory (opcionális)             │
│      │                                                               │
│      └─── N:1 ─── User (responsible_person)                         │
└──────────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────────────┐
│                       INVENTORY STRUCTURE                            │
│                                                                      │
│  Part (Alkatrész)                                                   │
│      │                                                               │
│      ├─── N:1 ─── Supplier (Beszállító)                            │
│      │                                                               │
│      ├─── 1:1 ─── InventoryLevel (Készlet szint)                   │
│      │      │                                                        │
│      │      └─── quantity_on_hand (összesített készlet)             │
│      │                                                               │
│      ├─── 1:N ─── PartLocation (Tárhelyek hozzárendelése)          │
│      │      │                                                        │
│      │      ├─── N:1 ─── StorageLocation (Hierarchikus tárhely)     │
│      │      │      │                                                │
│      │      │      └─── parent_location_id (fa struktúra)           │
│      │      │                                                        │
│      │      └─── quantity (mennyiség adott tárhelyen)               │
│      │                                                               │
│      ├─── 1:N ─── StockTransaction (Készletmozgások)                │
│      │      │                                                        │
│      │      └─── transaction_type (received, issued, adjustment)     │
│      │                                                               │
│      ├─── 1:N ─── StockBatch (Készlet tételek - FIFO/LIFO)          │
│      │                                                               │
│      └─── 1:N ─── StockReservation (Foglalások)                     │
└──────────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────────────┐
│                     SERVICE RECORDS & HISTORY                         │
│                                                                      │
│  ServiceRecord (Szerviz feljegyzés)                                 │
│      │                                                               │
│      ├─── N:1 ─── Machine                                            │
│      ├─── N:1 ─── User (created_by)                                  │
│      └─── service_date, service_cost, notes                          │
│                                                                      │
│  AssetHistory (Gép előzmények)                                      │
│      │                                                               │
│      ├─── N:1 ─── Machine                                            │
│      └─── action_type, description, user_id                          │
└──────────────────────────────────────────────────────────────────────┘
```

### 2.2 Fő Munkafolyamatok Logikai Fája

```
WORKFLOW: PM Task Lifecycle
│
├─── [CREATE] PMTask létrehozás
│    │
│    ├─── Manuális: PM Screen → "Új feladat"
│    └─── Automatikus: Production Line → Machine → "Karbantartás igénylése"
│         │
│         └─── pm_service.create_pm_task()
│              ├─── Validáció (machine_id, task_name, etc.)
│              ├─── Workflow validáció (workflow_service)
│              ├─── Notification küldés (notification_service)
│              └─── Work Request PDF generálás (pdf_service)
│
├─── [UPDATE] PMTask státusz változtatás
│    │
│    └─── pm_service.update_pm_task()
│         ├─── Workflow validáció (workflow_service.transition_state)
│         ├─── Notification küldés (ha assigned_to_user_id változott)
│         └─── Logging (log_service.log_action)
│
└─── [COMPLETE] PMTask elvégzése
     │
     └─── pm_service.complete_pm_task()
          ├─── Workflow validáció (pending/due_today/overdue → completed)
          ├─── PMHistory létrehozása
          ├─── Worksheet automatikus létrehozása (ha create_worksheet=True)
          ├─── Alkatrészek hozzáadása Worksheet-hez (ha van)
          ├─── Dokumentumok generálása:
          │   ├─── Work Request PDF (pdf_service)
          │   ├─── PM Worksheet PDF (pdf_service)
          │   └─── Scrapping Documents[] (scrapping_service, ha alkatrész használva)
          ├─── Fájlok mentése (save_pm_task_attachments)
          ├─── Notification küldés (notification_service)
          └─── Logging (log_service.log_action)
```

```
WORKFLOW: Worksheet Lifecycle
│
├─── [CREATE] Worksheet létrehozás
│    │
│    ├─── Manuális: Worksheet Screen → "Új munkalap"
│    └─── Automatikus: PM Service (complete_pm_task → create_worksheet)
│         │
│         └─── worksheet_service.create_worksheet()
│              ├─── Validáció (machine_id, assigned_to_user_id)
│              ├─── Notification küldés (notification_service)
│              └─── Logging (log_service.log_action)
│
├─── [UPDATE] Alkatrész hozzáadása
│    │
│    └─── worksheet_service.add_part_to_worksheet()
│         ├─── Part és StorageLocation validáció
│         ├─── Készlet ellenőrzés (InventoryLevel)
│         ├─── PartLocation frissítés (storage_service)
│         ├─── StockTransaction létrehozás (transaction_service)
│         ├─── Scrapping Document generálás (ha auto-generate enabled)
│         └─── Logging (log_service.log_action)
│
└─── [CLOSE] Worksheet lezárása
     │
     └─── worksheet_service.update_status(status="Closed")
          ├─── Workflow validáció (open/waiting → closed)
          ├─── Downtime kalkuláció (breakdown_time → repair_finished_time)
          ├─── Worksheet PDF generálás (pdf_service)
          ├─── Scrapping Documents generálás (ha van alkatrész)
          ├─── Notification küldés (notification_service)
          └─── Logging (log_service.log_action)
```

```
WORKFLOW: Inventory Management
│
├─── [CREATE] Part létrehozás
│    │
│    └─── inventory_service.create_part()
│         ├─── SKU validáció (validators.validate_sku)
│         ├─── InventoryLevel automatikus létrehozás (quantity_on_hand=0)
│         ├─── StockTransaction létrehozás (ha initial_quantity > 0)
│         └─── Logging (log_service.log_action)
│
├─── [ASSIGN] Part → StorageLocation hozzárendelés
│    │
│    └─── storage_service.assign_part_to_location()
│         ├─── PartLocation létrehozás/frissítés
│         ├─── InventoryLevel.quantity_on_hand frissítés
│         └─── Logging (log_service.log_action)
│
└─── [ADJUST] Készletmozgás
     │
     └─── inventory_service.adjust_stock()
          ├─── StockTransaction létrehozás
          ├─── InventoryLevel frissítés
          ├─── PartLocation frissítés (ha storage_location_id megadva)
          └─── Logging (log_service.log_action)
```

### 2.3 Service Függőségek Fa

```
workflow_service (CENTRAL)
│
├─── pm_service
│    ├─── notification_service
│    ├─── worksheet_service
│    ├─── pdf_service
│    ├─── scrapping_service
│    └─── log_service
│
├─── worksheet_service
│    ├─── inventory_service
│    ├─── storage_service
│    ├─── transaction_service
│    ├─── notification_service
│    ├─── pdf_service
│    ├─── scrapping_service
│    └─── log_service
│
├─── inventory_service
│    ├─── storage_service
│    ├─── transaction_service
│    └─── log_service
│
└─── storage_service
     ├─── log_service
     └─── context_service (user_id)
```

---

## 3. NAPLÓZÁS (LOGGING) ANALÍZIS

### 3.1 Naplózás Struktúra

#### A) Python Logging (logger.info/warning/error)

**Jelenlegi helyzet:**
- ✅ Minden service modulban van `logger = logging.getLogger(__name__)`
- ✅ Főbb műveleteknél van naplózás (create, update, delete)
- ⚠️ Nem minden művelet van naplózva
- ⚠️ Nem egységes a naplózás szintje (info/warning/error)

**Statisztika:**
- 409 `logger.` hívás 38 fájlban
- Főleg `logger.info()`, `logger.warning()`, `logger.error()` használat
- `logger.debug()` ritkán használt

#### B) SystemLog (log_service.log_action)

**Jelenlegi helyzet:**
- ✅ `log_service.log_action()` függvény létezik
- ✅ Kategóriák: document, worksheet, work_request, scrapping, task, assignment, inventory, asset, user
- ❌ **HIÁNYZÓ**: Nem minden kritikus művelet hívja meg a `log_action()`-t
- ❌ **HIÁNYZÓ**: A log_action() hívások nem konzisztensek

**Statisztika:**
- 8 `log_action(` hívás a log_service.py-ban (definíció)
- ~20-30 `log_action(` hívás az egész codebase-ben
- **PROBLÉMA**: Sok service NEM használja a log_action()-t

#### C) AuditLog (audit_service.log_audit)

**Jelenlegi helyzet:**
- ✅ `audit_service.log_audit()` függvény létezik
- ❌ **RITKÁN HASZNÁLT**: Csak néhány helyen hívódik meg
- ⚠️ Nem egyértelmű, mi a különbség SystemLog és AuditLog között

### 3.2 Naplózás Hiányosságok

#### 3.2.1 Kritikus műveletek, ahol NINCS log_action()

1. **PM Service:**
   - ✅ `complete_pm_task()` - NINCS log_action
   - ✅ `create_pm_task()` - NINCS log_action
   - ✅ `update_pm_task()` - NINCS log_action

2. **Worksheet Service:**
   - ✅ `create_worksheet()` - NINCS log_action (csak logger.info)
   - ✅ `update_status()` - NINCS log_action
   - ✅ `add_part_to_worksheet()` - NINCS log_action

3. **Inventory Service:**
   - ✅ `create_part()` - NINCS log_action
   - ✅ `update_part()` - NINCS log_action
   - ✅ `delete_part()` - NINCS log_action
   - ✅ `adjust_stock()` - NINCS log_action

4. **Storage Service:**
   - ✅ `assign_part_to_location()` - NINCS log_action (csak logger.info)
   - ✅ `create_storage_location()` - NINCS log_action

5. **Asset Service:**
   - ✅ `create_machine()` - NINCS log_action
   - ✅ `update_machine()` - NINCS log_action
   - ✅ `delete_machine()` - NINCS log_action

#### 3.2.2 Error Handling Hiányosságok

1. **Nem minden try-except blokkban van logging:**
   - ⚠️ Sok helyen van `except Exception as e:`, de nincs `logger.error()`
   - ⚠️ Nincs `exc_info=True` a hibák részletesebb naplózásához

2. **Transaction rollback logging:**
   - ⚠️ Sok helyen van `session.rollback()`, de nincs log

### 3.3 Naplózás Javaslatok

#### P1 (KRITIKUS): Minden CRUD művelet naplózása

**Implementáció:**
```python
# Példa: pm_service.create_pm_task()

def create_pm_task(...):
    session, should_close = _get_session(session)
    try:
        # ... validáció, létrehozás ...
        
        session.commit()
        
        # ✅ Hozzáadás: log_action hívás
        from services.log_service import log_action
        log_action(
            category="task",
            action_type="create",
            entity_type="PMTask",
            entity_id=task.id,
            user_id=created_by_user_id,
            description=f"PM Task created: {task.task_name}",
            metadata={
                "machine_id": machine_id,
                "task_type": task_type,
                "frequency_days": frequency_days,
                "priority": priority,
            },
            session=session
        )
        
        logger.info(f"PM Task created: {task.id} - {task.task_name}")
        return task
    except Exception as e:
        session.rollback()
        logger.error(f"Error creating PM task: {e}", exc_info=True)  # ✅ exc_info=True
        raise
```

#### P2 (FONTOS): Egységes error logging pattern

**Implementáció:**
```python
# Minden service-ben használjuk ezt a pattern-t:

try:
    # ... művelet ...
    session.commit()
    logger.info(f"Success: {operation_description}")
except ValidationError as e:
    session.rollback()
    logger.warning(f"Validation error: {e}", exc_info=True)
    raise
except BusinessLogicError as e:
    session.rollback()
    logger.warning(f"Business logic error: {e}", exc_info=True)
    raise
except Exception as e:
    session.rollback()
    logger.error(f"Unexpected error in {function_name}: {e}", exc_info=True)
    raise
```

---

## 4. MUNKAFOLYAMATOK (WORKFLOWS)

### 4.1 Workflow Service Analízis

**Jelenlegi helyzet:**
- ✅ Központi workflow service létezik (`workflow_service.py`)
- ✅ PM Task és Worksheet állapot átmenetek definiálva
- ✅ `transition_state()` függvény validálja az átmeneteket
- ✅ Workflow rules dictionary-ban definiálva

**Problémák:**
1. ⚠️ **HIÁNYZÓ**: Inventory állapotok (nincs workflow service-ben)
2. ⚠️ **HIÁNYZÓ**: Part állapotok (active/inactive/obsolete)
3. ⚠️ **HIÁNYZÓ**: Machine állapotok (Active/Stopped/Maintenance/Scrapped)

### 4.2 Fő Munkafolyamatok Elemzése

#### 4.2.1 PM Task → Worksheet Kapcsolat

**Jelenlegi logika:**
```
PM Task Complete
    │
    ├─── PMHistory létrehozása
    │
    ├─── Worksheet automatikus létrehozás (ha create_worksheet=True)
    │    │
    │    └─── PMHistory.worksheet_id = worksheet.id
    │
    └─── Alkatrészek hozzáadása Worksheet-hez
```

**Probléma:**
- ⚠️ **DUPLIKÁCIÓ LEHETSÉGES**: Ha PM Task elvégzésekor alkatrészt használunk, ÉS később Worksheet-ben is alkatrészt adunk hozzá, akkor duplikáció lehet
- ✅ **JÓ MEGOLDÁS**: PM Task completion dialog-ban az alkatrészek automatikusan Worksheet-hez kerülnek, így nincs duplikáció

**Javaslat:**
- ✅ Jelenlegi megoldás MŰKÖDIK
- ⚠️ Dokumentálni kellene ezt a munkafolyamatot

#### 4.2.2 InventoryLevel ↔ PartLocation Szinkronizáció

**Jelenlegi logika:**
```
PartLocation.quantity változás
    │
    └─── InventoryLevel.quantity_on_hand frissítés
```

**Probléma:**
- ⚠️ **HIÁNYZÓ VALIDÁCIÓ**: Nincs automatikus validáció, hogy `InventoryLevel.quantity_on_hand == SUM(PartLocation.quantity)`
- ✅ `validate_inventory_levels()` függvény LÉTEZIK, de csak manuálisan hívható

**Javaslat:**
- ✅ Validáció függvény létezik
- ❌ **HIÁNYZÓ**: Automatikus validáció minden módosítás után
- ❌ **HIÁNYZÓ**: Warning UI-ban, ha nincs egyezés

---

## 5. PROBLÉMA AZONOSÍTÁS

### 5.1 Kritikus Problémák (P1)

#### ❌ P1.1: Hiányzó Logging

**Leírás:**
- Sok kritikus művelet NEM hívja meg a `log_action()`-t
- Nem lehet auditálni, ki mit csinált

**Érintett fájlok:**
- `services/pm_service.py` - create_pm_task, update_pm_task, complete_pm_task
- `services/worksheet_service.py` - create_worksheet, update_status, add_part_to_worksheet
- `services/inventory_service.py` - create_part, update_part, delete_part, adjust_stock
- `services/storage_service.py` - assign_part_to_location, create_storage_location
- `services/asset_service.py` - create_machine, update_machine, delete_machine

**Megoldás:**
- Minden CRUD műveletnél hozzáadni `log_action()` hívást
- Egységes error logging pattern

#### ❌ P1.2: InventoryLevel ↔ PartLocation Szinkronizáció

**Leírás:**
- `InventoryLevel.quantity_on_hand` NEM mindig egyezik `SUM(PartLocation.quantity)`-vel
- Validáció csak manuálisan hívható

**Megoldás:**
- Automatikus validáció minden PartLocation módosítás után
- Warning UI-ban, ha nincs egyezés
- Auto-fix gomb (opcionális)

### 5.2 Fontos Problémák (P2)

#### ⚠️ P2.1: Workflow Service Hiányos

**Leírás:**
- Csak PM Task és Worksheet workflow van definiálva
- Inventory, Part, Machine állapotok NINCSENEK workflow service-ben

**Megoldás:**
- Part állapotok hozzáadása (active/inactive/obsolete)
- Machine állapotok hozzáadása (Active/Stopped/Maintenance/Scrapped)
- Inventory állapotok (ha szükséges)

#### ⚠️ P2.2: Error Handling Inkonzisztens

**Leírás:**
- Nem minden try-except blokkban van logging
- Nincs `exc_info=True` mindenhol
- Nincs konzisztens error handling pattern

**Megoldás:**
- Egységes error handling pattern minden service-ben
- `exc_info=True` minden logger.error()-nál
- Transaction rollback logging

### 5.3 Javasolt Javítások (P3)

#### 💡 P3.1: Service Dokumentáció

**Leírás:**
- Sok service függvénynek nincs részletes docstring
- Nincs munkafolyamat dokumentáció

**Megoldás:**
- Részletes docstring minden service függvényhez
- Munkafolyamat diagramok dokumentációban

#### 💡 P3.2: Unit Tesztek

**Leírás:**
- Kevés unit teszt létezik
- Nincs coverage report

**Megoldás:**
- Unit teszt írása főbb service függvényekhez
- Coverage report generálása

---

## 6. JAVASLATOK ÉS PRIORITÁSOK

### 6.1 Prioritás 1: KRITIKUS (Azonnal javítandó)

#### 1.1 Logging Hozzáadása Minden Kritikus Művelethez

**Becsült idő:** 4-6 óra

**Módosítandó fájlok:**
- `services/pm_service.py`
  - `create_pm_task()` - hozzáadni log_action
  - `update_pm_task()` - hozzáadni log_action
  - `complete_pm_task()` - hozzáadni log_action
- `services/worksheet_service.py`
  - `create_worksheet()` - hozzáadni log_action
  - `update_status()` - hozzáadni log_action
  - `add_part_to_worksheet()` - hozzáadni log_action
- `services/inventory_service.py`
  - `create_part()` - hozzáadni log_action
  - `update_part()` - hozzáadni log_action
  - `delete_part()` - hozzáadni log_action
  - `adjust_stock()` - hozzáadni log_action
- `services/storage_service.py`
  - `assign_part_to_location()` - hozzáadni log_action
  - `create_storage_location()` - hozzáadni log_action
- `services/asset_service.py`
  - `create_machine()` - hozzáadni log_action
  - `update_machine()` - hozzáadni log_action
  - `delete_machine()` - hozzáadni log_action

**Példa implementáció:**
```python
def create_pm_task(...):
    session, should_close = _get_session(session)
    try:
        # ... validáció, létrehozás ...
        session.commit()
        
        # ✅ Logging hozzáadása
        from services.log_service import log_action
        log_action(
            category="task",
            action_type="create",
            entity_type="PMTask",
            entity_id=task.id,
            user_id=created_by_user_id,
            description=f"PM Task created: {task.task_name} for machine {machine.name}",
            metadata={
                "machine_id": machine_id,
                "task_type": task_type,
                "frequency_days": frequency_days,
                "priority": priority,
                "assigned_to_user_id": assigned_to_user_id,
            },
            session=session
        )
        
        logger.info(f"PM Task created: {task.id} - {task.task_name}")
        return task
    except Exception as e:
        session.rollback()
        logger.error(f"Error creating PM task: {e}", exc_info=True)
        raise
    finally:
        if should_close:
            session.close()
```

#### 1.2 InventoryLevel ↔ PartLocation Automatikus Validáció

**Becsült idő:** 2-3 óra

**Módosítandó fájlok:**
- `services/storage_service.py`
  - `assign_part_to_location()` - hozzáadni validációt
  - `remove_part_from_location()` - hozzáadni validációt
- `services/inventory_service.py`
  - `adjust_stock()` - hozzáadni validációt

**Implementáció:**
```python
def assign_part_to_location(...):
    # ... meglévő logika ...
    
    # ✅ Validáció hozzáadása
    from services.inventory_service import validate_inventory_levels
    discrepancies = validate_inventory_levels(part_id=part_id, session=session)
    if discrepancies:
        logger.warning(f"Inventory level discrepancy for part {part_id}: {discrepancies}")
        # Opcionálisan: auto-fix vagy warning küldése
    
    # ... további logika ...
```

### 6.2 Prioritás 2: FONTOS (Rövid távon javítandó)

#### 2.1 Egységes Error Handling Pattern

**Becsült idő:** 3-4 óra

**Módosítandó fájlok:**
- Összes service fájl (42 fájl)

**Implementáció:**
```python
# Egységes pattern minden service függvényben:

def service_function(...):
    session, should_close = _get_session(session)
    try:
        # ... művelet ...
        session.commit()
        
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

#### 2.2 Workflow Service Bővítése

**Becsült idő:** 2-3 óra

**Módosítandó fájlok:**
- `services/workflow_service.py`

**Implementáció:**
```python
class PartState(Enum):
    """Part states"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    OBSOLETE = "obsolete"

class MachineState(Enum):
    """Machine states"""
    ACTIVE = "Active"
    STOPPED = "Stopped"
    MAINTENANCE = "Maintenance"
    SCRAPPED = "Scrapped"

WORKFLOW_RULES: Dict[str, Dict[Enum, Set[Enum]]] = {
    # ... meglévő rules ...
    "part": {
        PartState.ACTIVE: {PartState.INACTIVE, PartState.OBSOLETE},
        PartState.INACTIVE: {PartState.ACTIVE, PartState.OBSOLETE},
        PartState.OBSOLETE: set(),  # Terminal state
    },
    "machine": {
        MachineState.ACTIVE: {MachineState.STOPPED, MachineState.MAINTENANCE, MachineState.SCRAPPED},
        MachineState.STOPPED: {MachineState.ACTIVE, MachineState.MAINTENANCE},
        MachineState.MAINTENANCE: {MachineState.ACTIVE, MachineState.STOPPED},
        MachineState.SCRAPPED: set(),  # Terminal state
    }
}
```

### 6.3 Prioritás 3: JAVASOLT (Hosszú távon)

#### 3.1 Service Dokumentáció Fejlesztése

**Becsült idő:** 8-10 óra

**Módosítandó fájlok:**
- Összes service fájl (42 fájl)

**Példa:**
```python
def create_pm_task(
    machine_id: int,
    task_name: str,
    frequency_days: Optional[int] = None,
    task_description: Optional[str] = None,
    assigned_to_user_id: Optional[int] = None,
    priority: str = "normal",
    status: str = "pending",
    due_date: Optional[datetime] = None,
    estimated_duration_minutes: Optional[int] = None,
    created_by_user_id: Optional[int] = None,
    location: Optional[str] = None,
    task_type: str = "recurring",
    session: Session = None
) -> PMTask:
    """
    Create a new PM (Preventive Maintenance) task.
    
    This function creates a PM task for a specific machine. The task can be either
    recurring (with frequency_days) or one-time (task_type="one_time").
    
    Workflow:
    1. Validates machine exists
    2. Validates workflow state transition
    3. Creates PMTask record
    4. Sends notification (if assigned_to_user_id provided)
    5. Generates Work Request PDF
    6. Logs action to SystemLog
    
    Args:
        machine_id: ID of the machine this PM task is for
        task_name: Name/description of the PM task
        frequency_days: How often this task should be performed (for recurring tasks)
        task_description: Detailed description of the task
        assigned_to_user_id: User ID to assign the task to (None = global assignment)
        priority: Task priority ("low", "normal", "high", "urgent")
        status: Initial status (default: "pending")
        due_date: Due date for the task
        estimated_duration_minutes: Estimated time to complete in minutes
        created_by_user_id: User ID who created this task
        location: Location where task should be performed
        task_type: "recurring" or "one_time"
        session: Database session (creates new if None)
    
    Returns:
        PMTask: Created PM task object
    
    Raises:
        NotFoundError: If machine not found
        ValidationError: If validation fails
        StateTransitionError: If invalid state transition
        BusinessLogicError: If business rules violated
    
    Example:
        >>> task = create_pm_task(
        ...     machine_id=1,
        ...     task_name="Monthly oil change",
        ...     frequency_days=30,
        ...     priority="normal",
        ...     created_by_user_id=1
        ... )
        >>> print(task.id)
        42
    """
    # ... implementáció ...
```

#### 3.2 Unit Tesztek Írása

**Becsült idő:** 20-30 óra

**Létrehozandó fájlok:**
- `tests/services/test_pm_service.py`
- `tests/services/test_worksheet_service.py`
- `tests/services/test_inventory_service.py`
- `tests/services/test_storage_service.py`
- `tests/services/test_asset_service.py`
- `tests/services/test_workflow_service.py`

---

## 7. ÖSSZEFOGLALÁS

### 7.1 Jelenlegi Állapot Értékelése

**Erősségek:**
- ✅ Jól strukturált moduláris architektúra
- ✅ Központi workflow service
- ✅ Logging infrastruktúra létezik
- ✅ Error handling framework létezik
- ✅ Naplózás alapvetően működik (Python logging)

**Gyengeségek:**
- ❌ Hiányzó `log_action()` hívások kritikus műveleteknél
- ❌ Inkonzisztens error handling
- ❌ Hiányzó automatikus validáció (InventoryLevel ↔ PartLocation)
- ❌ Hiányos workflow service (csak PM Task és Worksheet)
- ⚠️ Kevés dokumentáció

### 7.2 Logikai Értékelés

**Összesített pontszám: 7.5/10**

- **Struktúra:** 9/10 (jól felépített, moduláris)
- **Logika:** 8/10 (logikus munkafolyamatok, néhány hiányosság)
- **Naplózás:** 6/10 (infrastruktúra jó, de nem használt konzisztensen)
- **Error Handling:** 7/10 (framework jó, de inkonzisztens)
- **Dokumentáció:** 6/10 (alapvető, de részletesebb kellene)

### 7.3 Főbb Javaslatok Összefoglalása

1. **P1: Logging hozzáadása** - Minden CRUD műveletnél log_action() hívás
2. **P1: Automatikus validáció** - InventoryLevel ↔ PartLocation szinkronizáció
3. **P2: Egységes error handling** - Konzisztens pattern minden service-ben
4. **P2: Workflow service bővítése** - Part és Machine állapotok
5. **P3: Dokumentáció** - Részletes docstring-ek és munkafolyamat dokumentáció
6. **P3: Unit tesztek** - Főbb service függvényekhez

---

**Készítve:** AI Assistant  
**Dátum:** 2025.12.18  
**Verzió:** 1.0

