# CMMS Rendszer - Telepítési Útmutató
# CMMS System - Installation Guide

## Rendszerkövetelmények / System Requirements

### Minimális követelmények / Minimum Requirements

- **Operációs rendszer / OS**: Windows 10 vagy újabb / Windows 10 or later
- **RAM**: 4 GB (8 GB ajánlott / recommended)
- **Szabad hely / Free Space**: 500 MB
- **Python**: 3.10 vagy újabb / Python 3.10 or later (fejlesztéshez / for development)

### Ajánlott követelmények / Recommended Requirements

- **RAM**: 8 GB vagy több / 8 GB or more
- **Szabad hely / Free Space**: 1 GB
- **Processzor / CPU**: Modern multi-core processzor / Modern multi-core processor

---

## Telepítési módszerek / Installation Methods

### 1. Előre összeállított .exe fájl / Pre-built .exe File

1. Töltsd le a `CMMS.exe` fájlt / Download the `CMMS.exe` file
2. Futtasd a telepítőt / Run the installer
3. Kövesd a telepítési varázslót / Follow the installation wizard
4. Indítsd el az alkalmazást / Start the application

### 2. Python forráskódból / From Python Source Code

#### Előfeltételek / Prerequisites

- Python 3.10+ telepítve / Python 3.10+ installed
- pip (Python package manager)

#### Telepítési lépések / Installation Steps

1. **Klónozd vagy töltsd le a projektet / Clone or download the project**
   ```bash
   git clone <repository-url>
   cd Artence_CMMS
   ```

2. **Hozz létre virtuális környezetet / Create virtual environment**
   ```bash
   python -m venv .venv
   ```

3. **Aktiváld a virtuális környezetet / Activate virtual environment**
   
   Windows:
   ```bash
   .venv\Scripts\activate
   ```
   
   Linux/Mac:
   ```bash
   source .venv/bin/activate
   ```

4. **Telepítsd a függőségeket / Install dependencies**
   ```bash
   cd CMMS_Project
   pip install -r requirements.txt
   ```

5. **Indítsd el az alkalmazást / Start the application**
   ```bash
   python main.py
   ```

---

## Első indítás / First Launch

### Adatbázis inicializálás / Database Initialization

Az alkalmazás első indításakor automatikusan létrehozza az adatbázist és a szükséges mappákat.

On first launch, the application automatically creates the database and required folders.

### Alapértelmezett admin felhasználó / Default Admin User

Ha nincs felhasználó az adatbázisban, az alkalmazás létrehoz egy alapértelmezett admin felhasználót:

If no users exist in the database, the application creates a default admin user:

- **Felhasználónév / Username**: `admin`
- **Jelszó / Password**: `admin123` (változtasd meg azonnal! / change immediately!)
- **Szerepkör / Role**: Manager

**FONTOS / IMPORTANT**: Változtasd meg az admin jelszavát az első bejelentkezés után! / Change the admin password after first login!

---

## Új funkciók / New Features (v1.0.0)

### Szabadságkezelés / Vacation Management
- Szabadság igénylések / Vacation requests
- Jóváhagyási workflow / Approval workflow
- Naptár nézet / Calendar view
- Automatikus dokumentum generálás / Automatic document generation

### Műszak Beosztás / Shift Schedule
- Felhasználói műszak beosztások / User shift schedules
- 1, 3, és 4 műszakos rendszerek támogatása / Support for 1, 3, and 4 shift systems

### Rendszer Naplózás / System Logging
- Részletes művelet naplózás / Detailed operation logging
- Kategorizált naplók / Categorized logs
- Archiválás és törlés beállítások / Archiving and deletion settings

### Selejtezési Dokumentumok / Scrapping Documents
- Automatikus generálás alkatrész/eszköz törlésnél / Automatic generation on part/asset deletion
- Karbantartás során elhasznált anyagok dokumentálása / Documentation of materials used in maintenance

### Ütemezett Mentések / Scheduled Backups
- Automatikus mentések konfigurálható időközzel / Automatic backups with configurable interval
- Automatikus régi mentések törlése / Automatic deletion of old backups

---

## Mappa struktúra / Folder Structure

Az alkalmazás a következő mappákat hozza létre:

The application creates the following folders:

```
Artence_CMMS/
├── CMMS_Project/
│   ├── data/
│   │   ├── database/          # Adatbázis fájlok / Database files
│   │   ├── files/              # Feltöltött fájlok / Uploaded files
│   │   │   ├── equipment_manuals/
│   │   │   └── maintenance_photos/
│   │   ├── reports/            # Generált jelentések / Generated reports
│   │   ├── system_backups/     # Adatmentések / Backups
│   │   └── logs/               # Naplófájlok / Log files
│   ├── generated_pdfs/         # Generált DOCX fájlok / Generated DOCX files
│   └── templates/              # DOCX sablonok / DOCX templates
```

---

## Konfiguráció / Configuration

### Adatbázis beállítások / Database Settings

Az adatbázis útvonala a `config/app_config.py` fájlban található:

Database path is configured in `config/app_config.py`:

```python
DATABASE_PATH = PROJECT_ROOT / "data" / "cmms.db"
```

### Nyelv beállítások / Language Settings

Az alapértelmezett nyelv a `config/app_config.py` fájlban:

Default language in `config/app_config.py`:

```python
DEFAULT_LANGUAGE = "hu"  # hu (Hungarian) or en (English)
```

---

## Hibaelhárítás / Troubleshooting

### Az alkalmazás nem indul el / Application won't start

1. Ellenőrizd, hogy a Python telepítve van-e / Check if Python is installed
2. Ellenőrizd a `requirements.txt` fájlban lévő csomagokat / Check packages in `requirements.txt`
3. Nézd meg a `data/logs/cmms.log` fájlt hibákért / Check `data/logs/cmms.log` for errors

### Adatbázis hiba / Database Error

1. Ellenőrizd, hogy van-e írási jogosultság a `data/` mappához / Check write permissions for `data/` folder
2. Töröld a `data/cmms.db` fájlt (vigyázat: adatvesztés!) / Delete `data/cmms.db` file (warning: data loss!)
3. Indítsd újra az alkalmazást / Restart the application

### Import hibák / Import Errors

1. Aktiváld a virtuális környezetet / Activate virtual environment
2. Telepítsd újra a függőségeket / Reinstall dependencies:
   ```bash
   pip install -r requirements.txt --force-reinstall
   ```

### Grafikonok nem jelennek meg / Charts not displaying

1. Telepítsd a `matplotlib` csomagot / Install `matplotlib` package:
   ```bash
   pip install matplotlib
   ```

### Excel export nem működik / Excel export not working

1. Telepítsd az `openpyxl` csomagot / Install `openpyxl` package:
   ```bash
   pip install openpyxl
   ```

---

## Frissítés / Update

### Adatbázis migráció / Database Migration

Az alkalmazás automatikusan kezeli az adatbázis sémaváltozásokat.

The application automatically handles database schema changes.

### Biztonsági mentés frissítés előtt / Backup Before Update

**FONTOS / IMPORTANT**: Mindig készíts biztonsági mentést frissítés előtt! / Always backup before updating!

1. Menj a "Beállítások" képernyőre / Go to "Settings" screen
2. Kattints a "Teljes mentés" gombra / Click "Full Backup" button
3. Mentsd el a backup fájlt biztonságos helyre / Save backup file to safe location

---

## Fejlesztői telepítés / Developer Installation

### További követelmények / Additional Requirements

- Git
- Code editor (VS Code, PyCharm, stb.)

### Fejlesztői függőségek / Developer Dependencies

```bash
pip install -r requirements.txt
pip install black flake8 isort  # Code formatting tools
```

### Teszt futtatása / Running Tests

```bash
pytest tests/
```

---

## Támogatás / Support

Problémák esetén ellenőrizd:

For issues, check:

1. `data/logs/cmms.log` - Alkalmazás naplók / Application logs
2. Konzol kimenet / Console output
3. Dokumentáció / Documentation

---

**Dokumentum verzió / Document Version**: 1.0.0  
**Utolsó frissítés / Last Updated**: 2025-12-14

