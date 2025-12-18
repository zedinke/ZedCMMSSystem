# CMMS - Computerized Maintenance Management System

**Professional bilingual (English/Hungarian) desktop maintenance management application built with Python and Flet.**

---

## 📋 Tartalomjegyzék / Table of Contents

- [Rendszer Áttekintés / System Overview](#rendszer-áttekintés--system-overview)
- [Főbb Funkciók / Key Features](#főbb-funkciók--key-features)
- [Telepítés / Installation](#telepítés--installation)
- [Használat / Usage](#használat--usage)
- [Rendszer Struktúra / System Structure](#rendszer-struktúra--system-structure)
- [Adatbázis / Database](#adatbázis--database)
- [Munkafolyamatok / Workflows](#munkafolyamatok--workflows)
- [Dokumentáció / Documentation](#dokumentáció--documentation)
- [Fejlesztés / Development](#fejlesztés--development)
- [Licenc / License](#licenc--license)

---

## 🎯 Rendszer Áttekintés / System Overview

A CMMS (Computerized Maintenance Management System) egy átfogó karbantartáskezelő rendszer, amely segít a gépek, berendezések, készletek és munkafolyamatok hatékony kezelésében.

The CMMS (Computerized Maintenance Management System) is a comprehensive maintenance management system that helps efficiently manage machines, equipment, inventory, and workflows.

### Főbb Jellemzők / Main Characteristics

- ✅ **Kétnyelvű támogatás / Bilingual Support**: Magyar és Angol felhasználói felület
- ✅ **Szerepkör alapú hozzáférés / Role-based Access**: Adminisztrátor, Műszakvezető, Karbantartó, Termelő
- ✅ **Valós idejű értesítések / Real-time Notifications**: PM feladatok, munkalapok állapotváltozásai
- ✅ **Teljes dokumentáció / Complete Documentation**: Részletes rendszer dokumentáció letölthető DOCX formátumban
- ✅ **SQLite adatbázis / SQLite Database**: Egyszerű telepítés és karbantartás
- ✅ **Offline működés / Offline Operation**: Lokális adatbázis, nincs szükség folyamatos internetkapcsolatra

---

## 🚀 Főbb Funkciók / Key Features

### 1. Áttekintés / Overview
- **Dashboard**: Valós idejű statisztikák, grafikonok, értesítések
- **Összesítések**: Költségvetés, karbantartási előrejelzések, állapotjelentések

### 2. Eszközkezelés / Asset Management

#### Production Line (Termelési Sor)
- Termelési vonalak létrehozása és kezelése
- Részletes információk: kód, státusz, kapacitás, felelős személy, üzembe helyezési dátum
- Kapcsolódó gépek és alkatrészek megjelenítése

#### Assets (Gépek / Berendezések)
- Gépek CRUD műveletei (létrehozás, szerkesztés, törlés)
- Részletes gépinformációk:
  - Alapadatok: sorozatszám, modell, gyártó, asset tag
  - Életciklus adatok: telepítés dátuma, vásárlás dátuma, garancia lejárat
  - Működési adatok: üzemórák, energiafogyasztás, hőmérséklet tartomány
  - Fizikai/finanszírozási: súly, méretek, vételár, beszállító
- Kompatibilis alkatrészek kezelése
- Karbantartási történet követése

#### PM (Preventive Maintenance - Megelőző Karbantartás)
- PM feladatok létrehozása és ütemezése
- Feladat hozzárendelés (felhasználóhoz vagy globális)
- Prioritás és határidő beállítása
- Feladat elvégzése:
  - Munka leírása, megfigyelések
  - Felhasznált alkatrészek
  - Dokumentumok generálása (Munkaigénylő, Munkalap, Selejtezési dokumentum)
  - Fájlok feltöltése (képek, dokumentumok)
- Befejezett feladatok csoportosítása (év/hónap/nap)

#### Worksheets (Munkalapok)
- Munkalapok létrehozása és kezelése
- Státusz munkafolyamat: New → In Progress → Completed → Closed
- Alkatrész felhasználás követése
- Készletlevonás automatikus kezelése
- DOCX és PDF export (ISO 9001 kompatibilis)

#### Service Records (Szerviz Feljegyzések)
- Összes karbantartási esemény áttekintése
- PM feladatok és munkalapok időrendi csoportosítása
- Részletes végrehajtási információk

### 3. Készletkezelés / Inventory Management

#### Parts (Alkatrészek)
- Alkatrészek CRUD műveletei
- Részletes részinformációk:
  - Alapadatok: név, SKU, kategória, leírás
  - Készlet adatok: mennyiség, minimális készlet, újrarendelési mennyiség
  - Pénzügyi: vételár, eladási ár
  - Beszállító információk
- Kategorizálás: Összes / Termelési sor / Gép
- Excel import/export

#### Storage (Raktározás)
- Hierarchikus raktárhelyek kezelése (fa struktúra)
- Alkatrészek hozzárendelése raktárhelyekhez
- Mennyiség követés raktárhelyenként
- "Alkatrészek raktárhely nélkül" lista
- Automatikus készletvalidáció

#### Inventory Audit (Készletellenőrzés)
- Készletleltár folyamat
- Eltérések dokumentálása
- Excel export

### 4. Jelentések / Reports
- Költség statisztikák
- Karbantartási előzmények
- Alkatrész használati kimutatások
- PDF és CSV export

### 5. Emberi Erőforrások / Human Resources

#### Vacation (Szabadságkezelés)
- Szabadságkérelmek létrehozása
- Jóváhagyási workflow
- DOCX dokumentum generálás

#### Shift Schedule (Műszak Beosztás)
- Műszak ütemezés
- Felhasználó-hozzárendelés

### 6. Rendszerkezelés / System Administration

#### Users (Felhasználók)
- Felhasználói fiókok kezelése
- Profil információk
- Jelszó változtatás

#### Permissions (Jogosultságok)
- Szerepkör alapú hozzáférés-vezérlés
- Entitás szintű jogosultságok

#### Logs (Naplók)
- Rendszernapló
- Audit log
- Felhasználói műveletek nyomon követése

#### Settings (Beállítások)
- Nyelvváltás (Magyar/Angol)
- Adatbázis mód váltás (Production/Learning)
- PM feladat fájlok könyvtára
- Egyéb rendszerbeállítások

### 7. Fejlesztői Eszközök / Developer Tools

#### System Documentation (Rendszer Dokumentáció)
- Teljes rendszer leírás
- Logikai fák és munkafolyamatok
- Entitás műveletek részletes leírása
- Letölthető DOCX formátumban (tartalomjegyzékkel)

---

## 💻 Telepítés / Installation

### Rendszerkövetelmények / System Requirements

- **Operációs rendszer / OS**: Windows 10 vagy újabb (64-bit)
- **Szabad lemezterület / Free Disk Space**: Minimum 500 MB
- **Jogosultság / Permissions**: Adminisztrátori jogosultság szükséges a telepítéshez
- **Adatbázis / Database**: SQLite (beágyazott, nincs külön telepítés szükséges)

### Telepítési Módszerek / Installation Methods

#### 1. Telepítő használata (Ajánlott / Recommended)

**Windows Installer (.exe)**

1. Töltse le a `ArtenceCMMS_Setup_v{version}.exe` fájlt
2. Kattintson duplán a telepítő fájlra
3. Ha megjelenik a "Windows protected your PC" figyelmeztetés:
   - Kattintson a "More info" gombra
   - Kattintson a "Run anyway" gombra
4. Kövesse a telepítési varázslót

**Fontos / Important**: A telepítő tartalmazza az összes szükséges függőséget - nincs szükség Python telepítésre vagy pip install-ra.

#### 2. Fejlesztői telepítés / Developer Installation

**Előfeltételek / Prerequisites:**
- Python 3.9+
- pip (Python package manager)

**Telepítési lépések / Installation Steps:**

1. Klónozza vagy töltse le a projektet:
```bash
cd CMMS_Project
```

2. Hozzon létre virtuális környezetet:
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

3. Telepítse a függőségeket:
```bash
pip install -r requirements.txt
```

4. Futtassa az alkalmazást:
```bash
python main.py
```

### Első Indítás / First Launch

1. **Bejelentkezés / Login**:
   - Felhasználónév: `admin` (vagy a rendszergazda által megadott)
   - Jelszó: Lásd a rendszergazdát vagy a dokumentációt
   - **Fontos**: Változtassa meg a jelszót az első bejelentkezéskor!

2. **Adatbázis beállítás / Database Configuration**:
   - Az alkalmazás SQLite adatbázist használ
   - Az adatbázis fájl a `data/` könyvtárban található
   - A **Settings** menüben módosíthatja a beállításokat

---

## 📖 Használat / Usage

### Bejelentkezés / Login

1. Indítsa el az alkalmazást
2. Adja meg a felhasználónevét és jelszavát
3. Válassza ki az adatbázis módot (Production / Learning)

### Főmenü Navigáció / Main Menu Navigation

A bal oldali menüben a következő kategóriák találhatók:

1. **Áttekintés / Overview**: Dashboard
2. **Eszközkezelés / Asset Management**:
   - Production Line
   - Assets
   - Parts (Alkatrészek)
3. **Műveletek / Operations**:
   - PM (Preventive Maintenance)
   - Worksheets
   - Service Records
4. **Készletkezelés / Inventory Management**:
   - Storage
   - Inventory Audit
5. **Jelentések / Reports**
6. **Emberi Erőforrások / Human Resources**:
   - Vacation
   - Shift Schedule
7. **Rendszerkezelés / System Administration**:
   - Users
   - Permissions
   - Logs
   - Settings
8. **Fejlesztői Eszközök / Developer Tools**:
   - System Documentation

### Gyors Műveletek / Quick Actions

- **PM feladat létrehozása**: Production Line → Gép kiválasztása → "Karbantartás igénylése"
- **Alkatrész hozzárendelése**: Parts → "Új alkatrész" → Tárhely kiválasztás
- **Munkalap létrehozása**: Worksheets → "Új munkalap"
- **Jelentés generálása**: Reports → Válasszon jelentéstípus → Export

---

## 🏗️ Rendszer Struktúra / System Structure

```
CMMS_Project/
├── config/              # Konfiguráció fájlok
│   ├── app_config.py    # Alkalmazás beállítások
│   ├── constants.py     # Konstansok és enumok
│   ├── roles.py         # Szerepkör definíciók
│   └── logging_config.py # Naplózás konfiguráció
├── database/            # Adatbázis réteg
│   ├── connection.py    # Adatbázis kapcsolat
│   ├── models.py        # SQLAlchemy modellek (86 tábla)
│   ├── session_manager.py # Munkamenet kezelés
│   └── db_init.py       # Adatbázis inicializálás
├── localization/        # Lokalizáció támogatás
│   ├── translator.py    # Fordítás kezelő
│   └── translations/
│       ├── en.json      # Angol szövegek
│       └── hu.json      # Magyar szövegek
├── services/            # Üzleti logika réteg (43 szolgáltatás)
│   ├── auth_service.py
│   ├── asset_service.py
│   ├── inventory_service.py
│   ├── pm_service.py
│   ├── worksheet_service.py
│   ├── notification_service.py
│   └── ... (további 37 szolgáltatás)
├── ui/                  # Felhasználói felület
│   ├── screens/         # Képernyő komponensek (22 képernyő)
│   ├── components/      # Újrafelhasználható komponensek (15 komponens)
│   ├── theme.py         # UI téma
│   └── app.py           # Fő alkalmazás
├── utils/               # Segédfüggvények (18 modul)
│   ├── error_handler.py
│   ├── pagination.py
│   ├── validators.py
│   └── ...
├── api/                 # REST API (FastAPI)
│   ├── routers/         # API végpontok
│   ├── schemas.py       # Pydantic modellek
│   └── server.py        # API szerver
├── data/                # Adat könyvtárak
│   ├── files/           # Feltöltött fájlok
│   ├── reports/         # Generált jelentések
│   ├── logs/            # Alkalmazás naplók
│   └── app_settings.json # Alkalmazás beállítások
├── templates/           # Dokumentum sablonok
│   ├── worksheet_template.docx
│   ├── work_request_template.docx
│   └── ...
├── tests/               # Unit tesztek
├── migrations/          # Adatbázis migrációk (Alembic)
├── docs/                # Dokumentáció (47 dokumentum)
└── main.py              # Alkalmazás belépési pont
```

---

## 🗄️ Adatbázis / Database

### SQLite Adatbázis

A rendszer **SQLite adatbázist** használ, amely:
- ✅ Nincs szükség külön adatbázis szerver telepítésre
- ✅ Egyszerű telepítés és karbantartás
- ✅ Lokális működés (offline)
- ✅ Maximum 10 felhasználó és ~100GB adatforgalom 3-4 év alatt (a készletkezeléshez elegendő)

### Főbb Entitások / Main Entities

A rendszer **86 adatbázis táblát** tartalmaz:

**Auth & Users**:
- `users`, `roles`, `user_sessions`, `audit_logs`

**Assets**:
- `production_lines`, `machines`, `modules`, `asset_history`, `machine_versions`

**Inventory**:
- `suppliers`, `parts`, `inventory_levels`, `stock_transactions`, `stock_batches`
- `storage_locations`, `part_locations`, `qrcode_data`

**Maintenance**:
- `pm_tasks`, `pm_histories`, `pm_task_attachments`
- `worksheets`, `worksheet_parts`, `worksheet_photos`, `worksheet_pdfs`
- `work_request_pdfs`, `pm_worksheet_pdfs`, `scrapping_documents`

**Notifications**:
- `notifications`

**Service Records**:
- `service_records`

**Human Resources**:
- `vacations`, `shift_schedules`, `shift_rotations`

### Adatbázis Módok / Database Modes

- **Production**: Éles adatbázis
- **Learning**: Tanuló/teszt adatbázis

A módok közötti váltás a **Settings** menüben lehetséges.

---

## 🔄 Munkafolyamatok / Workflows

### 1. PM (Preventive Maintenance) Folyamat

```
[PM Task Létrehozás]
    │
    ├── Manuális: PM menü → Új feladat
    └── Automatikus: Production Line → Gép → "Karbantartás igénylése"
         │
         ├── Hozzárendelés (felhasználóhoz vagy globális)
         ├── Prioritás beállítása
         └── Határidő megadása
              │
              ▼
[PM Task Aktív]
    │
    ├── Feladat megjelenik PM listában
    └── Dashboard-on látható (due_today, overdue)
         │
         ▼
[PM Task Elvégzése]
    │
    ├── Feladat kiválasztása → "Elvégzés" gomb
    ├── Kitöltendő mezők:
    │   ├── Dátum, idő
    │   ├── Munka leírása
    │   ├── Megfigyelések
    │   ├── Státusz (kész/részleges/problémás)
    │   ├── Felhasznált alkatrészek (választható)
    │   │   └── Storage location választás
    │   └── Fájlok feltöltése (képek, dokumentumok)
    │
    ▼
[Automatikus Dokumentum Generálás]
    │
    ├── Work Request PDF/DOCX
    ├── PM Worksheet PDF/DOCX
    └── Scrapping Documents (ha alkatrészeket használt)
         │
         ▼
[PM History Létrehozása]
    │
    ├── Feladat státusz: completed
    ├── Következő ütemezés
    └── Dokumentumok és fájlok mentve
```

### 2. Worksheet Folyamat

```
[Worksheet Létrehozás]
    │
    ├── Manuális: Worksheets → "Új munkalap"
    └── Automatikus: PM Task elvégzésekor
         │
         ▼
[Worksheet: New]
    │
    ├── Alapadatok kitöltése
    ├── Kapcsolódó gép kiválasztása
    └── Mentés
         │
         ▼
[Worksheet: In Progress]
    │
    ├── Alkatrészek hozzáadása
    │   └── Készlet automatikus levonás
    ├── Munkafolyamat dokumentálása
    └── Státusz váltás
         │
         ▼
[Worksheet: Completed]
    │
    ├── Munka befejezése
    └── Státusz váltás
         │
         ▼
[Worksheet: Closed]
    │
    └── Végleges dokumentumok generálása
```

### 3. Inventory Folyamat

```
[Alkatrész Létrehozás]
    │
    ├── Parts → "Új alkatrész"
    ├── Alapadatok kitöltése (név, SKU, ár, stb.)
    └── Kezdeti mennyiség megadása (opcionális)
         │
         ▼
[Tárhelyhez Rendelés]
    │
    ├── Storage → "Alkatrészek tárhely nélkül"
    ├── Alkatrész kiválasztása
    ├── Tárhely választás (csak üres vagy azonos SKU)
    └── Mennyiség megadása
         │
         ▼
[Készlet Mozgások]
    │
    ├── Receive Stock (Készletbevétel)
    ├── Adjust Stock (Készlet módosítás)
    └── Transfer (Átvitel tárhelyek között)
```

---

## 📚 Dokumentáció / Documentation

A rendszer részletes dokumentációját a következő helyeken találja:

### Főbb Dokumentumok / Main Documents

1. **System Architecture Analysis** (`docs/SYSTEM_ARCHITECTURE_ANALYSIS.md`)
   - Rendszer architektúra áttekintés
   - Entitás kapcsolatok
   - Logikai problémák és javaslatok

2. **Deep Logical Analysis** (`docs/DEEP_LOGICAL_ANALYSIS.md`)
   - Mély logikai elemzés
   - Függvények logikai struktúrája
   - Javaslatok és megoldások

3. **Logical Tree Diagram** (`docs/LOGICAL_TREE_DIAGRAM.md`)
   - Rendszer logikai fa diagram
   - Szolgáltatás függőségek
   - Adatfolyam diagramok

4. **System Workflow Diagram** (`docs/SYSTEM_WORKFLOW_DIAGRAM.md`)
   - Munkafolyamat diagramok
   - PM, Worksheet, Inventory folyamatok

5. **Implementation Plan** (`docs/IMPLEMENTATION_PLAN.md`)
   - Implementációs terv
   - Prioritások (P1, P2, P3)
   - Fejlesztési fázisok

6. **User Manual** (`docs/USER_MANUAL.md`)
   - Felhasználói kézikönyv
   - Részletes használati útmutató

7. **Installation Guide** (`docs/INSTALLATION_WINDOWS.md`)
   - Telepítési útmutató Windows rendszerhez

### Rendszer Dokumentáció Letöltése / System Documentation Download

A **System Documentation** menüben a következőket találja:

- Teljes rendszer leírás
- Logikai fák és diagramok
- Entitás műveletek részletes leírása
- Munkafolyamatok dokumentációja
- Letölthető **DOCX formátumban** (tartalomjegyzékkel)

---

## 🛠️ Fejlesztés / Development

### Technológiai Stack / Technology Stack

- **Programozási nyelv / Language**: Python 3.9+
- **UI Framework**: Flet (cross-platform)
- **Adatbázis**: SQLite (SQLAlchemy ORM)
- **API**: FastAPI (REST API)
- **Dokumentáció generálás**: python-docx
- **PDF generálás**: ReportLab, WeasyPrint
- **Excel kezelés**: openpyxl, pandas

### Függőségek / Dependencies

Lásd: `requirements.txt`

Főbb csomagok / Main packages:
- `flet>=0.23.2` - UI framework
- `sqlalchemy>=2.0.0` - ORM
- `fastapi>=0.104.0` - API framework
- `python-docx>=1.1.0` - DOCX generálás
- `reportlab>=4.0.0` - PDF generálás
- `openpyxl>=3.1.0` - Excel kezelés
- `pandas>=2.1.0` - Adatkezelés

### Tesztek Futtatása / Running Tests

```bash
# Összes teszt
python run_all_tests.py

# Pytest használata
pytest tests/

# Egyedi teszt fájl
pytest tests/test_pm_service.py
```

### Adatbázis Migrációk / Database Migrations

```bash
# Migrációk futtatása
python run_migrations.py

# Alembic használata
alembic upgrade head
```

### Projekt Struktúra Fejlesztői Nézetben / Project Structure Developer View

- **43 Service modul**: Üzleti logika
- **22 UI Screen**: Felhasználói képernyők
- **15 UI Component**: Újrafelhasználható komponensek
- **86 Database Table**: Adatbázis táblák
- **2 Language**: Magyar és Angol lokalizáció

---

## 📊 Rendszer Statisztikák / System Statistics

- **Kód sorok száma / Lines of Code**: ~50,000+ sor Python kód
- **Szolgáltatások száma / Services**: 43 modul
- **UI Képernyők száma / UI Screens**: 22 képernyő
- **Adatbázis táblák száma / Database Tables**: 86 tábla
- **Lokalizáció nyelvek / Localization Languages**: 2 (Magyar, Angol)
- **Dokumentáció fájlok / Documentation Files**: 47+ Markdown dokumentum

---

## 🔐 Biztonság / Security

- **Jelszó hashelés / Password Hashing**: Argon2
- **Munkamenet kezelés / Session Management**: Token alapú autentikáció
- **Szerepkör alapú hozzáférés / Role-based Access**: Finomhangolt jogosultságok
- **Audit log / Audit Log**: Összes felhasználói művelet naplózása
- **Adatbázis titkosítás / Database Encryption**: SQLite titkosítás támogatott

---

## 🐛 Hibaelhárítás / Troubleshooting

### Gyakori Problémák / Common Issues

**1. Adatbázis kapcsolati hiba / Database Connection Error**
- Ellenőrizze az adatbázis fájl elérési útját a Settings menüben
- Győződjön meg arról, hogy az adatbázis fájl létezik és írható

**2. Import hiba / Import Error**
- Ellenőrizze, hogy minden függőség telepítve van: `pip install -r requirements.txt`
- Győződjön meg arról, hogy a virtuális környezet aktív

**3. Lokalizáció hiba / Localization Error**
- Ellenőrizze a `localization/translations/` könyvtárat
- Futtassa: `python scripts/check_translations.py`

**4. Dokumentum generálási hiba / Document Generation Error**
- Ellenőrizze a template fájlok meglétét a `templates/` könyvtárban
- Győződjön meg arról, hogy a `python-docx` telepítve van

---

## 📞 Támogatás / Support

Ha problémába ütközik vagy kérdése van:

1. Tekintse meg a dokumentációt a `docs/` könyvtárban
2. Ellenőrizze a System Documentation menüt az alkalmazásban
3. Nézze meg a `CHANGELOG.md` fájlt a legfrissebb változásokért

---

## 📝 Verzió Információ / Version Information

- **Aktuális verzió / Current Version**: Lásd `version.txt`
- **Legutóbbi frissítés / Last Update**: 2025.12.18
- **Státusz / Status**: ✅ Stabil / Stable

---

## 📄 Licenc / License

Proprietary - All rights reserved

---

## 🙏 Köszönetnyilvánítás / Acknowledgments

Ez a rendszer modern szoftverfejlesztési elvekkel és best practice-ekkel készült.

This system was built with modern software development principles and best practices.

---

**Készítette / Created by**: Artence Development Team  
**Dátum / Date**: 2025.12.18  
**Verzió / Version**: 1.0.0

---

*Az alkalmazás folyamatosan fejlesztés alatt áll. Minden javaslat és visszajelzés szívesen várható.*

*The application is under continuous development. All suggestions and feedback are welcome.*
