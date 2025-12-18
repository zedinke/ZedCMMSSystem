# CMMS Rendszer - Technikai Dokumentáció
# CMMS System - Technical Documentation

## Architektúra / Architecture

### Technológiai stack / Technology Stack

- **UI Framework**: Flet (Flutter for Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Language**: Python 3.10+
- **Document Generation**: python-docx (DOCX), matplotlib (Charts), openpyxl (Excel)

### Projekt struktúra / Project Structure

```
CMMS_Project/
├── config/              # Konfiguráció / Configuration
│   ├── app_config.py
│   ├── constants.py
│   └── logging_config.py
├── database/            # Adatbázis / Database
│   ├── models.py        # SQLAlchemy modellek / Models
│   ├── session_manager.py
│   └── database.py
├── services/            # Üzleti logika / Business Logic
│   ├── auth_service.py
│   ├── asset_service.py
│   ├── inventory_service.py
│   ├── worksheet_service.py
│   ├── pm_service.py
│   ├── reports_service.py
│   ├── backup_service.py
│   └── ...
├── ui/                  # Felhasználói felület / User Interface
│   ├── app.py          # Fő alkalmazás / Main app
│   ├── screens/        # Képernyők / Screens
│   └── theme.py        # Téma / Theme
├── utils/               # Segédeszközök / Utilities
│   ├── qr_generator.py
│   ├── file_handler.py
│   ├── currency.py
│   └── ...
├── localization/        # Fordítások / Translations
│   ├── translator.py
│   └── translations/
│       ├── hu.json
│       └── en.json
└── main.py             # Belépési pont / Entry point
```

---

## Adatbázis séma / Database Schema

### Főbb táblák / Main Tables

#### Users & Authentication
- `users`: Felhasználók / Users
- `roles`: Szerepkörök / Roles
- `user_sessions`: Aktív munkamenetek / Active sessions
- `audit_logs`: Audit napló / Audit log

#### Asset Management
- `production_lines`: Termelési vonalak / Production lines
- `machines`: Gépek / Machines
- `modules`: Modulok / Modules
- `asset_history`: Eszköz történet / Asset history

#### Inventory
- `parts`: Alkatrészek / Parts
- `suppliers`: Beszállítók / Suppliers
- `inventory_levels`: Készletszintek / Inventory levels
- `stock_transactions`: Készletmozgások / Stock transactions
- `qr_codes`: QR kód metaadatok / QR code metadata

#### Worksheets
- `worksheets`: Munkalapok / Worksheets
- `worksheet_parts`: Munkalap alkatrészek / Worksheet parts
- `worksheet_photos`: Munkalap fotók / Worksheet photos
- `worksheet_pdfs`: Generált dokumentumok / Generated documents

#### Preventive Maintenance
- `pm_tasks`: PM feladatok / PM tasks
- `pm_histories`: PM végrehajtások / PM executions
- `work_request_pdfs`: Munkaigénylő dokumentumok / Work request documents
- `pm_worksheet_pdfs`: PM munkalap dokumentumok / PM worksheet documents

#### Vacation Management
- `vacation_requests`: Szabadság igénylések / Vacation requests
- `shift_schedules`: Műszak beosztások / Shift schedules
- `vacation_documents`: Szabadság dokumentumok / Vacation documents

#### System Logging
- `system_logs`: Rendszer naplók / System logs

#### Scrapping
- `scrapping_documents`: Selejtezési dokumentumok / Scrapping documents

#### Service Records
- `service_records`: Szervizelési nyilvántartások / Service records

---

## Szolgáltatások / Services

### Auth Service (`services/auth_service.py`)

- `login(username, password)`: Bejelentkezés / Login
- `logout(token)`: Kijelentkezés / Logout
- `create_session(user_id)`: Munkamenet létrehozása / Create session
- `validate_session(token)`: Munkamenet validálása / Validate session

### Asset Service (`services/asset_service.py`)

- `create_machine(...)`: Gép létrehozása / Create machine
- `update_machine(...)`: Gép frissítése / Update machine
- `list_machines(...)`: Gépek listázása / List machines
- `add_module(...)`: Modul hozzáadása / Add module
- `list_modules_for_machine(...)`: Modulok listázása / List modules
- `get_machine_history(...)`: Gép történet / Machine history

### Inventory Service (`services/inventory_service.py`)

- `create_part(...)`: Alkatrész létrehozása / Create part
- `update_part(...)`: Alkatrész frissítése / Update part
- `adjust_stock(...)`: Készlet módosítása / Adjust stock
- `import_parts_from_excel(...)`: Excel import / Excel import

### Worksheet Service (`services/worksheet_service.py`)

- `create_worksheet(...)`: Munkalap létrehozása / Create worksheet
- `update_worksheet(...)`: Munkalap frissítése / Update worksheet
- `add_part_to_worksheet(...)`: Alkatrész hozzáadása / Add part
- `close_worksheet(...)`: Munkalap lezárása / Close worksheet
- `list_worksheets_for_machine(...)`: Gépenkénti munkalapok / Worksheets by machine

### PM Service (`services/pm_service.py`)

- `create_pm_task(...)`: PM feladat létrehozása / Create PM task
- `list_pm_tasks(...)`: PM feladatok listázása / List PM tasks
- `record_execution(...)`: Végrehajtás rögzítése / Record execution
- `list_pm_tasks(...)`: Gépenkénti PM feladatok / PM tasks by machine

### Reports Service (`services/reports_service.py`)

- `get_cost_statistics(...)`: Költség statisztikák / Cost statistics
- `get_time_statistics(...)`: Idő statisztikák / Time statistics
- `get_task_statistics(...)`: Feladat statisztikák / Task statistics
- `get_technician_statistics(...)`: Karbantartó statisztikák / Technician statistics
- `get_trend_statistics(...)`: Trend elemzés / Trend analysis

### Backup Service (`services/backup_service.py`)

- `backup_database(...)`: Adatbázis mentés / Database backup
- `backup_all_files(...)`: Teljes mentés / Full backup
- `restore_from_backup(...)`: Visszaállítás / Restore
- `list_backups(...)`: Mentések listázása / List backups

---

## Lokalizáció / Localization

### Fordítási rendszer / Translation System

A fordítások JSON fájlokban tárolódnak hierarchikus struktúrában:

Translations are stored in JSON files with hierarchical structure:

```json
{
  "common": {
    "buttons": {
      "save": "Mentés / Save",
      "cancel": "Mégse / Cancel"
    }
  },
  "worksheets": {
    "title": "Munkalapok / Worksheets"
  }
}
```

### Használat / Usage

```python
from localization.translator import translator

# Aktuális nyelv / Current language
text = translator.get_text("common.buttons.save")

# Specifikus nyelv / Specific language
text = translator.get_text("common.buttons.save", "en")
```

### Fordítás validáció / Translation Validation

```python
from utils.translation_validator import validate_all

result = validate_all(Path("localization/translations"))
if not result['valid']:
    print("Translation validation failed")
```

---

## Dokumentum generálás / Document Generation

### DOCX Generálás / DOCX Generation

A rendszer `python-docx` könyvtárat használ template-alapú dokumentum generáláshoz.

The system uses `python-docx` library for template-based document generation.

**Sablonok helye / Template location**: `templates/`

**Generált fájlok helye / Generated files location**: `generated_pdfs/`

### Template struktúra / Template Structure

A sablonok DOCX fájlok, amelyek placeholder-eket tartalmaznak:

Templates are DOCX files containing placeholders:

- `{worksheet_id}`: Munkalap ID / Worksheet ID
- `{machine_name}`: Gép neve / Machine name
- `{created_at}`: Létrehozás dátuma / Creation date
- stb. / etc.

---

## Biztonság / Security

### Jelszó hash-elés / Password Hashing

- **Algoritmus / Algorithm**: Argon2 (argon2-cffi)
- **Salt**: Automatikusan generálva / Automatically generated

### Munkamenet kezelés / Session Management

- **Token hossz / Token length**: 32 byte
- **Lejárat / Expiry**: 24 óra (konfigurálható / configurable)
- **Aktivitás követés / Activity tracking**: Utolsó aktivitás időpontja / Last activity timestamp

### Audit Logging

Minden fontos művelet naplózva van:

All important actions are logged:

- Bejelentkezés / Login
- Adat létrehozás / Data creation
- Adat módosítás / Data modification
- Adat törlés / Data deletion

---

## Bővíthetőség / Extensibility

### Új szolgáltatás hozzáadása / Adding New Service

1. Hozz létre egy új fájlt a `services/` mappában / Create new file in `services/` folder
2. Definiáld a szolgáltatás függvényeket / Define service functions
3. Használd a `_get_session()` helper-t session kezeléshez / Use `_get_session()` helper for session management

### Új képernyő hozzáadása / Adding New Screen

1. Hozz létre egy új fájlt a `ui/screens/` mappában / Create new file in `ui/screens/` folder
2. Definiáld a `Screen` osztályt `view(page)` metódussal / Define `Screen` class with `view(page)` method
3. Regisztráld az `ui/app.py`-ban / Register in `ui/app.py`

### Új fordítás kulcs hozzáadása / Adding New Translation Key

1. Add hozzá a kulcsot minden nyelvi fájlhoz / Add key to all language files
2. Használd hierarchikus struktúrát / Use hierarchical structure
3. Futtasd a translation validátort / Run translation validator

---

## Teljesítmény optimalizálás / Performance Optimization

### Adatbázis indexek / Database Indexes

A következő mezők indexelve vannak:

The following fields are indexed:

- `users.username`
- `worksheets.machine_id`, `worksheets.status`, `worksheets.created_at`
- `pm_tasks.next_due_date`
- `stock_transactions.part_id`, `stock_transactions.timestamp`

### Lazy Loading

- **joinedload**: Gépek és termelési vonalak / Machines and production lines
- **selectinload**: Munkalap alkatrészek / Worksheet parts
- **select**: Felhasználó munkalapok / User worksheets

---

## Tesztelés / Testing

### Unit tesztek / Unit Tests

A tesztek a `tests/` mappában találhatók:

Tests are located in `tests/` folder:

```bash
pytest tests/
```

### Teszt lefedettség / Test Coverage

```bash
pytest --cov=services --cov=utils tests/
```

---

## Deployment

### PyInstaller Build

```bash
pyinstaller --onefile --windowed --icon=icon.ico --name=CMMS main.py
```

### Build konfiguráció / Build Configuration

A `build.spec` fájl tartalmazza a build beállításokat:

The `build.spec` file contains build settings:

- Hidden imports
- Data files
- Icon
- Version info

---

## Hibakeresés / Debugging

### Logging szintek / Logging Levels

- **DEBUG**: Részletes információk / Detailed information
- **INFO**: Általános információk / General information
- **WARNING**: Figyelmeztetések / Warnings
- **ERROR**: Hibák / Errors

### Log fájl helye / Log File Location

`data/logs/cmms.log`

### Log rotation

- Maximum fájlméret / Max file size: 10 MB
- Megtartott fájlok száma / Number of files kept: 10

---

## API Dokumentáció (Jövőbeli) / API Documentation (Future)

A rendszer jelenleg desktop alkalmazás, de REST API támogatás tervezve.

The system is currently a desktop application, but REST API support is planned.

---

**Dokumentum verzió / Document Version**: 1.0  
**Utolsó frissítés / Last Updated**: 2025-12-13

