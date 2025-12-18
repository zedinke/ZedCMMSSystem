# CMMS - Computerized Maintenance Management System

**Professional bilingual (English/Hungarian) desktop maintenance management application built with Python and Flet.**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)

---

## 📋 Tartalomjegyzék / Table of Contents

- [Rendszer Áttekintés / System Overview](#rendszer-áttekintés--system-overview)
- [Főbb Funkciók Részletes Leírása / Detailed Feature Description](#főbb-funkciók-részletes-leírása--detailed-feature-description)
- [Telepítés / Installation](#telepítés--installation)
- [Használati Útmutató / User Guide](#használati-útmutató--user-guide)
- [Rendszer Architektúra / System Architecture](#rendszer-architektúra--system-architecture)
- [Adatbázis Struktúra / Database Structure](#adatbázis-struktúra--database-structure)
- [Munkafolyamatok Részletes Leírása / Detailed Workflows](#munkafolyamatok-részletes-leírása--detailed-workflows)
- [API Dokumentáció / API Documentation](#api-dokumentáció--api-documentation)
- [Fejlesztés és Karbantartás / Development & Maintenance](#fejlesztés-és-karbantartás--development--maintenance)
- [Dokumentáció / Documentation](#dokumentáció--documentation)
- [Biztonság / Security](#biztonság--security)
- [Hibaelhárítás / Troubleshooting](#hibaelhárítás--troubleshooting)

---

## 🎯 Rendszer Áttekintés / System Overview

A CMMS (Computerized Maintenance Management System) egy átfogó, professzionális karbantartáskezelő rendszer, amely segít a gépek, berendezések, készletek és munkafolyamatok hatékony kezelésében. A rendszer két fő komponensből áll: egy desktop alkalmazásból (Python + Flet) és egy Android mobil alkalmazásból (Kotlin + Jetpack Compose).

The CMMS (Computerized Maintenance Management System) is a comprehensive, professional maintenance management system that helps efficiently manage machines, equipment, inventory, and workflows. The system consists of two main components: a desktop application (Python + Flet) and an Android mobile application (Kotlin + Jetpack Compose).

### Rendszer Komponensek / System Components

1. **Desktop Alkalmazás / Desktop Application** (`CMMS_Project/`)
   - Python 3.9+ alapú asztali alkalmazás
   - Flet UI framework
   - SQLite adatbázis
   - Teljes funkcionalitás és adminisztráció

2. **Android Alkalmazás / Android Application** (`AndroidApp/`)
   - Kotlin alapú mobil alkalmazás
   - Jetpack Compose modern UI
   - Offline-first architektúra
   - Teljes szinkronizáció a desktop app-lal

3. **Backend API** (`CMMS_Project/api/`)
   - FastAPI REST API
   - JWT token autentikáció
   - CORS támogatás
   - Swagger/OpenAPI dokumentáció

### Főbb Jellemzők / Main Characteristics

- ✅ **Kétnyelvű támogatás / Bilingual Support**: Magyar és Angol felhasználói felület minden modulban
- ✅ **Szerepkör alapú hozzáférés / Role-based Access Control**: Adminisztrátor, Műszakvezető, Karbantartó, Termelő szerepkörök
- ✅ **Valós idejű értesítések / Real-time Notifications**: PM feladatok, munkalapok állapotváltozásai, értesítési csengő
- ✅ **SQLite adatbázis / SQLite Database**: Egyszerű telepítés, nincs szükség külön adatbázis szerverre
- ✅ **Offline működés / Offline Operation**: Lokális adatbázis, nincs szükség folyamatos internetkapcsolatra
- ✅ **Teljes dokumentáció / Complete Documentation**: Részletes rendszer dokumentáció letölthető DOCX formátumban
- ✅ **ISO 9001 kompatibilis / ISO 9001 Compatible**: Dokumentum generálás ISO 9001 szabványoknak megfelelően
- ✅ **Audit Trail / Audit Trail**: Minden felhasználói művelet naplózva és visszakövethető

---

## 🚀 Főbb Funkciók Részletes Leírása / Detailed Feature Description

### 1. Áttekintés / Overview

#### Dashboard
A Dashboard a rendszer központi irányítópultja, amely valós idejű információkat jelenít meg:

- **Statisztikák / Statistics**:
  - Aktív PM feladatok száma
  - Esedékes és lejárt feladatok
  - Munkalapok státusza
  - Készletszint figyelmeztetések
  - Költségvetés összesítések

- **Grafikonok / Charts**:
  - Karbantartási költségek időbeli alakulása
  - PM feladatok teljesítése
  - Alkatrész használati kimutatások
  - Gép állapotok áttekintése

- **Értesítések / Notifications**:
  - Új PM feladatok hozzárendelése
  - Munkalap státusz változások
  - Készlet kritikus szintek
  - Rendszer üzenetek

- **Gyors műveletek / Quick Actions**:
  - Új PM feladat létrehozása
  - Új munkalap létrehozása
  - Készletbevétel
  - Jelentés generálása

### 2. Eszközkezelés / Asset Management

#### Production Line (Termelési Sor)
A termelési vonalak a gyártási folyamatok logikai csoportosítását teszik lehetővé.

**Főbb funkciók / Main Features:**
- Termelési vonalak létrehozása, szerkesztése, törlése
- Részletes információk:
  - **Kód**: Egyedi azonosító
  - **Státusz**: Aktív, Inaktív, Karbantartás
  - **Kapacitás**: Termelési kapacitás megadása
  - **Felelős személy**: Hozzárendelt felhasználó
  - **Üzembe helyezési dátum**: Üzembe helyezés dátuma
  - **Helyszín / Location**: Fizikai elhelyezkedés
  - **Leírás / Description**: Részletes leírás
  - **Megjegyzések / Notes**: További információk

**Kapcsolódó adatok megjelenítése:**
- Kapcsolódó gépek listája teljes részletekkel
- Kompatibilis alkatrészek minden gépre
- PM feladatok a termelési vonal gépeire
- Karbantartási előzmények

**Navigáció:**
- Production Line kiválasztása → Részletes géplista
- Gép kiválasztása → Részletes gépinformációk + kompatibilis alkatrészek
- "Karbantartás igénylése" gomb → PM feladat létrehozása

#### Assets (Gépek / Berendezések)
A gépek és berendezések teljes körű kezelése minden szükséges információval.

**Főbb funkciók / Main Features:**
- **CRUD műveletek**: Létrehozás, olvasás, frissítés, törlés
- **Részletes gépinformációk**:

  **Alapadatok / Basic Information:**
  - Sorozatszám / Serial Number
  - Modell / Model
  - Gyártó / Manufacturer
  - Asset Tag (belső azonosító)
  - Kategória / Category
  - Státusz / Status (Aktív, Leállítva, Karbantartás, Selejtezve)

  **Életciklus adatok / Lifecycle Data:**
  - Telepítés dátuma / Installation Date
  - Vásárlás dátuma / Purchase Date
  - Garancia lejárat dátuma / Warranty Expiry Date
  - Várható élettartam / Expected Lifespan

  **Működési adatok / Operational Data:**
  - Üzemórák / Operating Hours
  - Karbantartási intervallum / Maintenance Interval
  - Utolsó szerviz dátuma / Last Service Date
  - Következő szerviz dátuma / Next Service Date
  - Energiafogyasztás / Energy Consumption
  - Teljesítmény igény / Power Requirements
  - Üzemi hőmérséklet tartomány / Operating Temperature Range

  **Fizikai jellemzők / Physical Characteristics:**
  - Súly / Weight
  - Méretek / Dimensions (hossz, szélesség, magasság)
  - Kritikus szint / Criticality Level (Alacsony, Közepes, Magas, Kritikus)

  **Pénzügyi információk / Financial Information:**
  - Vételár / Purchase Price
  - Beszállító / Supplier
  - Értékcsökkenés információ

  **Egyéb:**
  - Megjegyzések / Notes
  - Dokumentumok / Documents
  - Képek / Photos

- **Kompatibilis alkatrészek kezelése**:
  - Alkatrészek hozzárendelése gépekhez
  - Kompatibilitási mátrix
  - Alkatrész használati előzmények

- **Karbantartási történet**:
  - Összes PM feladat a gépre
  - Munkalapok előzményei
  - Szerviz feljegyzések
  - Költség követés

#### PM (Preventive Maintenance - Megelőző Karbantartás)
A megelőző karbantartási feladatok teljes életciklusának kezelése.

**Feladat Létrehozása / Task Creation:**
- **Manuális létrehozás**: PM menü → "Új feladat" gomb
- **Automatikus létrehozás**: Production Line → Gép kiválasztása → "Karbantartás igénylése" gomb

**Feladat Paraméterek / Task Parameters:**
- Feladat neve / Task Name
- Leírás / Description
- Kapcsolódó gép / Related Machine
- Hozzárendelés / Assignment:
  - Globális (minden aktív felhasználó)
  - Specifikus felhasználó
- Prioritás / Priority:
  - Alacsony / Low
  - Normál / Normal
  - Magas / High
  - Sürgős / Urgent
- Határidő / Due Date
- Ismétlődés / Recurrence (ha szükséges)

**Feladat Állapotok / Task States:**
- **Pending** (Függőben): Új létrehozott feladat
- **Due Today** (Ma esedékes): Ma kell elvégezni
- **Overdue** (Lejárt): A határidőn túl van
- **Completed** (Befejezve): Sikeresen elvégezve

**Feladat Elvégzése / Task Completion:**
Amikor egy PM feladatot elvégeznek, a következő információkat kell megadni:

- **Végrehajtási adatok / Execution Data:**
  - Végrehajtás dátuma és időpontja
  - Munka leírása
  - Megfigyelések
  - Eltöltött idő (percben)
  - Befejezési státusz (Kész, Részleges, Problémás)

- **Felhasznált alkatrészek / Parts Used:**
  - Alkatrész kiválasztása (csak kompatibilis alkatrészek)
  - Mennyiség megadása
  - Tárhely kiválasztása (csak üres vagy azonos SKU tartalmazó tárhelyek)
  - Készlet automatikus levonás

- **Fájlok feltöltése / File Upload:**
  - Képek (karbantartás előtt/után)
  - Dokumentumok (technikai leírások, hibajegyek, stb.)
  - Fájlok szervezése: `{parent_dir}/pm_task_{task_id}/history_{history_id}/`

**Automatikus Dokumentum Generálás / Automatic Document Generation:**
A rendszer automatikusan generálja a következő dokumentumokat:

1. **Work Request PDF/DOCX** (Munkaigénylő):
   - Feladat részletei
   - Gép információk
   - Hozzárendelt felhasználó
   - Határidő

2. **PM Worksheet PDF/DOCX** (PM Munkalap):
   - Elvégzett munkák leírása
   - Felhasznált alkatrészek listája
   - Megfigyelések
   - ISO 9001 kompatibilis formátum

3. **Scrapping Documents** (Selejtezési dokumentumok):
   - Automatikusan generálva minden felhasznált alkatrészre
   - Selejtezési dátum és ok
   - Alkatrész információk

**Befejezett Feladatok Megjelenítése / Completed Tasks Display:**
- Utolsó 10 befejezett feladat közvetlenül látható
- Régebbi feladatok csoportosítva (év/hónap/nap szerint)
- Minden befejezett feladatnál elérhető:
  - **Részletek gomb**: Teljes feladat információ
  - **Munkaigénylő gomb**: Work Request dokumentum letöltése
  - **Munkalap gomb**: PM Worksheet dokumentum letöltése
  - **Selejtezési dokumentum gomb**: Scrapping documents letöltése
  - **Fájlok gomb**: Feltöltött fájlok és generált dokumentumok megtekintése

#### Worksheets (Munkalapok)
A munkalapok a tényleges karbantartási munkák dokumentálására szolgálnak.

**Munkalap Létrehozása / Worksheet Creation:**
- **Manuális létrehozás**: Worksheets menü → "Új munkalap" gomb
- **Automatikus létrehozás**: PM Task elvégzésekor automatikusan

**Munkalap Státusz Munkafolyamat / Worksheet Status Workflow:**
```
New (Új) → In Progress (Folyamatban) → Completed (Befejezve) → Closed (Lezárva)
```

**Munkalap Funkciók / Worksheet Features:**
- **Alapadatok / Basic Data:**
  - Cím / Title
  - Leírás / Description
  - Kapcsolódó gép / Related Machine
  - Létrehozó felhasználó / Created By User
  - Létrehozás dátuma / Creation Date

- **Alkatrész felhasználás / Part Usage:**
  - Alkatrészek hozzáadása a munkalaphoz
  - Mennyiség megadása
  - Készlet automatikus levonás a kiválasztott tárhelyről
  - Alkatrész költség számítás

- **Státusz kezelés / Status Management:**
  - Státusz váltások workflow szabályok szerint
  - Megjegyzések státusz váltásokhoz
  - Végrehajtási idő követés

- **Dokumentáció / Documentation:**
  - DOCX export (ISO 9001 kompatibilis)
  - PDF export
  - Template alapú dokumentum generálás

#### Service Records (Szerviz Feljegyzések)
Összes karbantartási esemény áttekintése egy helyen.

**Funkciók / Features:**
- Összes PM History és Worksheet rekord időrendi csoportosítása
- Tab alapú nézet:
  - **Összes**: Minden karbantartási esemény
  - **PM Tasks**: Csak PM feladatok
  - **Worksheets**: Csak munkalapok
- Részletes végrehajtási információk
- Kapcsolódó dokumentumok elérése

### 3. Készletkezelés / Inventory Management

#### Parts (Alkatrészek)
Az alkatrészek teljes körű kezelése részletes információkkal.

**Főbb funkciók / Main Features:**
- **CRUD műveletek**: Létrehozás, olvasás, frissítés, törlés
- **Részletes részinformációk**:

  **Alapadatok / Basic Information:**
  - Név / Name
  - SKU (Stock Keeping Unit) - egyedi azonosító
  - Kategória / Category
  - Leírás / Description
  - Mértékegység / Unit (db, kg, m, stb.)

  **Készlet adatok / Stock Data:**
  - Készleten lévő mennyiség / Quantity on Hand
  - Foglalt mennyiség / Quantity Reserved
  - Elérhető mennyiség / Quantity Available
  - Minimális készlet / Safety Stock
  - Újrarendelési mennyiség / Reorder Quantity
  - Készlet státusz / Stock Status (Alacsony, Normál, Elégtelen)

  **Pénzügyi információk / Financial Information:**
  - Vételár / Buy Price
  - Eladási ár / Sell Price
  - Költség számítás

  **Beszállító információk / Supplier Information:**
  - Beszállító / Supplier
  - Beszállítói kód / Supplier Code
  - Szállítási idő / Lead Time

- **Kategorizálás / Categorization:**
  - **Összes**: Minden alkatrész listája (lapozható)
  - **Termelési sor szerint**: Termelési sor → Gép → Alkatrészek hierarchikus nézet
  - **Gép szerint**: Gép → Alkatrészek közvetlen csoportosítás

- **Készletmozgások / Stock Movements:**
  - Készletbevétel / Receive Stock
  - Készlet kiadás / Issue Stock
  - Készlet módosítás / Adjust Stock
  - Készlet átvitel / Transfer Stock
  - Minden mozgás naplózva audit trail-lel

- **Excel import/export:**
  - Tömeges alkatrész import Excel fájlból
  - Készlet export Excel formátumban
  - Template fájlok használata

- **QR kód támogatás:**
  - QR kód generálás alkatrészekhez
  - QR kód nyomtatás
  - QR kód beolvasás készletmozgásokhoz

#### Storage (Raktározás)
Hierarchikus raktárhelyek kezelése fa struktúrával.

**Főbb funkciók / Main Features:**
- **Hierarchikus struktúra / Hierarchical Structure:**
  ```
  Raktár (Warehouse)
    └── Zóna (Zone)
        └── Polc (Shelf)
            └── Rekesz (Bin)
                └── Pozíció (Position)
  ```

- **Tárhely kezelés / Location Management:**
  - Tárhelyek létrehozása, szerkesztése, törlése
  - Kód és név megadása
  - Szülő tárhely hozzárendelése
  - Kapacitás megadása (opcionális)

- **Alkatrész hozzárendelés / Part Assignment:**
  - Alkatrészek hozzárendelése tárhelyekhez
  - Mennyiség megadása tárhelyenként
  - Több tárhelyen lehet ugyanaz az alkatrész
  - Mennyiség követés tárhelyenként

- **"Alkatrészek raktárhely nélkül" lista / Parts Without Location:**
  - Összes olyan alkatrész listája, amelynek van készlete, de nincs hozzárendelt tárhelye
  - Figyelmeztetés megjelenítése
  - Gyors hozzárendelési lehetőség
  - Tárhely szűrés: csak üres vagy azonos SKU tartalmazó tárhelyek jelennek meg

- **Tárhely fa nézet / Location Tree View:**
  - Teljes hierarchia megjelenítése
  - Bővíthető/csukható szekciók
  - Alkatrészek listázása tárhelyenként
  - Mennyiségek megjelenítése

- **Készletvalidáció / Inventory Validation:**
  - Automatikus validáció: InventoryLevel.quantity_on_hand vs. PartLocation.quantity összeg
  - Eltérések azonosítása
  - Validációs jelentés generálása

#### Inventory Audit (Készletellenőrzés)
Rendszeres készletleltárak végrehajtása és dokumentálása.

**Funkciók / Features:**
- Leltár folyamat indítása
- Tényleges mennyiségek megadása
- Eltérések automatikus számítása
- Excel export leltári eredményekhez
- Audit trail minden leltári műveletre

### 4. Jelentések / Reports

A rendszer számos jelentéstípus lehetővé tesz:

- **Költség statisztikák / Cost Statistics:**
  - Karbantartási költségek időbeli alakulása
  - Alkatrész költségek
  - Gép költségek
  - Kategóriánkénti összesítések

- **Karbantartási előzmények / Maintenance History:**
  - PM feladatok teljesítése
  - Munkalapok statisztikái
  - Gép karbantartási előzmények
  - Teljesítmény mutatók

- **Alkatrész használati kimutatások / Part Usage Reports:**
  - Legtöbbet használt alkatrészek
  - Készletforgalom
  - Újrarendelési javaslatok

- **Export formátumok / Export Formats:**
  - PDF export
  - CSV export
  - Excel export

### 5. Emberi Erőforrások / Human Resources

#### Vacation (Szabadságkezelés)
Szabadságkérelmek kezelése és jóváhagyási workflow.

**Funkciók / Features:**
- Szabadságkérelmek létrehozása
- Kezdő és befejező dátum megadása
- Jóváhagyási workflow
- DOCX dokumentum generálás
- Naptár nézet szabadságokkal

#### Shift Schedule (Műszak Beosztás)
Műszak ütemezés és felhasználó-hozzárendelés.

**Funkciók / Features:**
- Műszak ütemezés létrehozása
- Felhasználók hozzárendelése műszakokhoz
- Műszak forgatás kezelése
- Naptár nézet műszakokkal

### 6. Rendszerkezelés / System Administration

#### Users (Felhasználók)
Felhasználói fiókok teljes körű kezelése.

**Funkciók / Features:**
- Felhasználók létrehozása, szerkesztése, törlése
- Profil információk kezelése:
  - Név, email, telefonszám
  - Szerepkör hozzárendelés
  - Aktív/inaktív státusz
- Jelszó változtatás
- Jelszó alaphelyzetbe állítás

#### Permissions (Jogosultságok)
Szerepkör alapú hozzáférés-vezérlés és entitás szintű jogosultságok.

**Szerepkörök / Roles:**
- **Adminisztrátor**: Teljes hozzáférés minden funkcióhoz
- **Műszakvezető - Karbantartó**: PM feladatok, munkalapok kezelése
- **Műszakvezető - Termelés**: Termelési adatok, gépek kezelése
- **Karbantartó**: PM feladatok végrehajtása, munkalapok kezelése
- **Termelő**: Alapvető információk megtekintése

**Jogosultságok / Permissions:**
- Entitás szintű jogosultságok (olvasás, írás, törlés)
- Finomhangolt hozzáférés-vezérlés

#### Logs (Naplók)
Teljes audit trail minden műveletre.

**Napló típusok / Log Types:**
- **Rendszernapló / System Log**: Rendszer szintű események
- **Audit log / Audit Log**: Felhasználói műveletek részletes naplózása
- **Hibanapló / Error Log**: Hibák és kivételek naplózása

**Funkciók / Features:**
- Naplók szűrése dátum, felhasználó, művelet típus szerint
- Export lehetőség
- Keresés naplókban

#### Settings (Beállítások)
Rendszer beállítások kezelése.

**Beállítások / Settings:**
- **Nyelvváltás / Language**: Magyar ↔ Angol
- **Adatbázis mód váltás / Database Mode**: Production ↔ Learning
- **PM feladat fájlok könyvtára / PM Task Files Directory**: Feltöltött fájlok és generált dokumentumok helye
- **Téma / Theme**: Világos/sötét téma (ha elérhető)
- **Biztonsági beállítások / Security Settings**

### 7. Fejlesztői Eszközök / Developer Tools

#### System Documentation (Rendszer Dokumentáció)
Teljes rendszer dokumentáció letölthető formátumban.

**Tartalom / Content:**
- Rendszer áttekintés
- Logikai fák és diagramok
- Entitás műveletek részletes leírása
- Munkafolyamatok dokumentációja
- Architektúra leírás
- API dokumentáció

**Export / Export:**
- DOCX formátum letöltése
- Tartalomjegyzék
- Formázott dokumentum
- Nyomtatható verzió

---

## 💻 Telepítés / Installation

### Rendszerkövetelmények / System Requirements

**Desktop Alkalmazás:**
- **Operációs rendszer / OS**: Windows 10 vagy újabb (64-bit)
- **Szabad lemezterület / Free Disk Space**: Minimum 500 MB
- **Jogosultság / Permissions**: Adminisztrátori jogosultság szükséges a telepítéshez
- **Adatbázis / Database**: SQLite (beágyazott, nincs külön telepítés szükséges)

**Android Alkalmazás:**
- Android 8.0 (API 26) vagy újabb
- Internet kapcsolat (szinkronizációhoz)

### Telepítési Módszerek / Installation Methods

#### 1. Windows Installer (Ajánlott / Recommended)

**Előnyök / Advantages:**
- ✅ Minden függőség tartalmazva van
- ✅ Nincs szükség Python telepítésre
- ✅ Egyszerű telepítési folyamat
- ✅ Automatikus Start Menu shortcut

**Telepítési lépések / Installation Steps:**

1. Töltse le a `ArtenceCMMS_Setup_v{version}.exe` fájlt
2. Kattintson duplán a telepítő fájlra
3. Ha megjelenik a "Windows protected your PC" figyelmeztetés:
   - Kattintson a "More info" gombra
   - Kattintson a "Run anyway" gombra
4. Kövesse a telepítési varázslót:
   - Telepítési útvonal kiválasztása (alapértelmezetten: `C:\Program Files\ArtenceCMMS`)
   - Desktop shortcut létrehozása (opcionális)
   - Start Menu shortcut (automatikus)
5. A telepítés után az alkalmazás azonnal használható

**Telepítés után / After Installation:**
- Start Menu: `Artence CMMS` → `Artence CMMS`
- Desktop: `Artence CMMS.lnk` (ha létrehozta)
- Közvetlenül: `C:\Program Files\ArtenceCMMS\CMMS.exe`

#### 2. Fejlesztői telepítés / Developer Installation

**Előfeltételek / Prerequisites:**
- Python 3.9 vagy újabb
- pip (Python package manager)
- Git (opcionális, repository klónozáshoz)

**Telepítési lépések / Installation Steps:**

1. **Repository klónozása vagy letöltése:**
```bash
git clone https://github.com/zedinke/ZedCMMSSystem.git
cd ZedCMMSSystem/CMMS_Project
```

2. **Virtuális környezet létrehozása:**
```bash
python -m venv venv

# Windows
.\venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Függőségek telepítése:**
```bash
pip install -r requirements.txt
```

4. **Alkalmazás futtatása:**
```bash
python main.py
```

### Android Alkalmazás Telepítése / Android App Installation

1. **APK fájl létrehozása:**
```bash
cd AndroidApp
./gradlew assembleDebug
```

2. **Telepítés emulátorra vagy eszközre:**
```bash
./gradlew installDebug
```

Vagy manuálisan telepítse az APK fájlt: `app/build/outputs/apk/debug/app-debug.apk`

### Első Indítás / First Launch

1. **Bejelentkezés / Login**:
   - Felhasználónév: `admin` (vagy a rendszergazda által megadott)
   - Jelszó: Lásd a rendszergazdát vagy a dokumentációt
   - **Fontos**: Változtassa meg a jelszót az első bejelentkezéskor!

2. **Adatbázis beállítás / Database Configuration**:
   - Az alkalmazás SQLite adatbázist használ
   - Az adatbázis fájl a `data/` könyvtárban található
   - A **Settings** menüben módosíthatja a beállításokat:
     - Production adatbázis elérési útja
     - Learning adatbázis elérési útja

3. **Nyelv kiválasztása / Language Selection**:
   - A Settings menüben válthat a magyar és angol nyelv között

---

## 📖 Használati Útmutató / User Guide

### Bejelentkezés / Login

1. Indítsa el az alkalmazást (Desktop vagy Android)
2. Adja meg a felhasználónevét és jelszavát
3. Válassza ki az adatbázis módot (Production / Learning)
4. Kattintson a "Bejelentkezés" gombra

### Főmenü Navigáció / Main Menu Navigation

A bal oldali menüben a következő kategóriák találhatók:

1. **Áttekintés / Overview**
   - Dashboard

2. **Eszközkezelés / Asset Management**
   - Production Line
   - Assets
   - Parts (Alkatrészek)

3. **Műveletek / Operations**
   - PM (Preventive Maintenance)
   - Worksheets
   - Service Records

4. **Készletkezelés / Inventory Management**
   - Storage
   - Inventory Audit

5. **Jelentések / Reports**

6. **Emberi Erőforrások / Human Resources**
   - Vacation
   - Shift Schedule

7. **Rendszerkezelés / System Administration**
   - Users
   - Permissions
   - Logs
   - Settings

8. **Fejlesztői Eszközök / Developer Tools**
   - System Documentation

### Gyors Műveletek / Quick Actions

**PM feladat létrehozása:**
1. Production Line menü → Termelési sor kiválasztása
2. Gép kiválasztása a listából
3. "Karbantartás igénylése" gomb
4. Feladat adatainak kitöltése
5. Mentés

**Alkatrész hozzárendelése tárhelyhez:**
1. Storage menü → "Alkatrészek tárhely nélkül" szekció
2. Alkatrész kiválasztása
3. "Tárhelyhez rendelés" gomb
4. Tárhely kiválasztása (csak kompatibilis tárhelyek jelennek meg)
5. Mennyiség megadása
6. Mentés

**Munkalap létrehozása:**
1. Worksheets menü → "Új munkalap" gomb
2. Alapadatok kitöltése
3. Gép kiválasztása
4. Mentés

**Jelentés generálása:**
1. Reports menü → Jelentéstípus kiválasztása
2. Szűrési paraméterek beállítása
3. Export gomb → PDF vagy CSV formátum

---

## 🏗️ Rendszer Architektúra / System Architecture

### Rétegek / Layers

```
┌─────────────────────────────────────────────────────────┐
│                  UI Layer (Flet)                        │
│  └── 22 Screen komponens                                │
│  └── 15 Reusable Component                              │
│  └── Navigation & Routing                               │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│              Service Layer (43 modul)                   │
│  ├── Core Services (Auth, User, Permission)            │
│  ├── Asset Services (Assets, Production Lines)         │
│  ├── Inventory Services (Parts, Storage)               │
│  ├── Maintenance Services (PM, Worksheets)             │
│  ├── Reporting Services (Reports, Charts, Excel)       │
│  └── System Services (Settings, Logging, Backup)       │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│         Database Layer (SQLAlchemy ORM)                 │
│  ├── 86 Database Table                                  │
│  ├── Relationships & Foreign Keys                       │
│  ├── Migrations (Alembic)                               │
│  └── Session Management                                 │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│              SQLite Database                            │
│  └── Local file-based database                          │
└─────────────────────────────────────────────────────────┘
```

### Komponens Struktúra / Component Structure

**Desktop Application:**
```
CMMS_Project/
├── config/              # Konfiguráció
│   ├── app_config.py    # Alkalmazás beállítások
│   ├── constants.py     # Konstansok és enumok
│   ├── roles.py         # Szerepkör definíciók
│   └── logging_config.py # Naplózás
├── database/            # Adatbázis réteg
│   ├── connection.py    # DB kapcsolat
│   ├── models.py        # 86 SQLAlchemy modell
│   ├── session_manager.py
│   └── db_init.py       # Inicializálás
├── services/            # 43 szolgáltatás modul
│   ├── auth_service.py
│   ├── asset_service.py
│   ├── inventory_service.py
│   ├── pm_service.py
│   ├── worksheet_service.py
│   ├── notification_service.py
│   └── ... (37 további)
├── ui/                  # Felhasználói felület
│   ├── screens/         # 22 képernyő
│   ├── components/      # 15 komponens
│   ├── theme.py
│   └── app.py
├── api/                 # REST API
│   ├── routers/
│   ├── schemas.py
│   └── server.py
├── utils/               # 18 segédfüggvény
├── localization/        # Lokalizáció (HU/EN)
├── templates/           # Dokumentum sablonok
├── tests/               # Unit tesztek
└── docs/                # 47+ dokumentáció
```

**Android Application:**
```
AndroidApp/
├── app/src/main/java/com/artence/cmms/
│   ├── data/
│   │   ├── local/       # Room database
│   │   ├── remote/      # API integration
│   │   └── repository/  # Repository pattern
│   ├── domain/          # Business logic
│   ├── ui/
│   │   ├── screens/     # 8 fő képernyő
│   │   └── components/
│   └── di/              # Dependency Injection
└── build.gradle.kts
```

### Szolgáltatások Listája / Services List

**Core Services (6):**
- `auth_service.py` - Autentikáció, session kezelés
- `user_service.py` - Felhasználókezelés
- `permission_service.py` - Jogosultságkezelés
- `context_service.py` - Alkalmazás kontextus
- `log_service.py` - Rendszer naplózás
- `audit_service.py` - Audit logok

**Asset Management Services (3):**
- `asset_service.py` - Gépek, Production Lines CRUD
- `asset_lifecycle_service.py` - Életciklus statisztikák
- `depreciation_service.py` - Értékcsökkenés

**Inventory Services (8):**
- `inventory_service.py` - Alkatrészek, beszállítók, készletmozgások
- `storage_service.py` - Tárhelyek hierarchikus kezelése
- `storage_history_service.py` - Tárhely előzmények
- `storage_document_service.py` - Tárhely dokumentumok
- `reservation_service.py` - Készlet foglalások
- `transaction_service.py` - Készlet tranzakciók
- `inventory_audit_service.py` - Készletellenőrzés
- `inventory_audit_excel_service.py` - Excel export

**Maintenance Services (5):**
- `pm_service.py` - Preventív karbantartás
- `worksheet_service.py` - Munkalapok
- `service_record_service.py` - Szerviz feljegyzések
- `scrapping_service.py` - Selejtezési dokumentumok
- `safety_service.py` - Biztonsági események

**Reporting Services (7):**
- `reports_service.py` - Jelentések, statisztikák
- `reports_service_extended.py` - Bővített jelentések
- `chart_service.py` - Grafikonok
- `excel_export_service.py` - Excel export
- `pdf_service.py` - PDF generálás
- `report_templates_service.py` - Jelentés sablonok
- `scheduled_reports_service.py` - Ütemezett jelentések

**Notification & Communication (3):**
- `notification_service.py` - Értesítések
- `shift_service.py` - Műszak beosztás
- `vacation_service.py` - Szabadságkezelés

**System Services (5):**
- `settings_service.py` - Alkalmazás beállítások
- `backup_service.py` - Adatbázis backup
- `update_service.py` - Frissítéskezelés
- `scheduler_service.py` - Ütemezett feladatok
- `search_service.py` - Globális keresés

**Utility Services (6):**
- `workflow_service.py` - **KÖZPONTI** állapot átmenetek
- `system_documentation_service.py` - Dokumentáció generálás
- `site_service.py` - Multi-site támogatás
- `excel_export_service.py` - Excel kezelés
- `pdf_service.py` - PDF kezelés
- További utility szolgáltatások

---

## 🗄️ Adatbázis Struktúra / Database Structure

### SQLite Adatbázis

A rendszer **SQLite adatbázist** használ, amely:
- ✅ Nincs szükség külön adatbázis szerver telepítésre
- ✅ Egyszerű telepítés és karbantartás
- ✅ Lokális működés (offline)
- ✅ Maximum 10 felhasználó és ~100GB adatforgalom 3-4 év alatt (a készletkezeléshez elegendő)
- ✅ WAL (Write-Ahead Logging) mód a jobb teljesítményért
- ✅ Foreign key constraints engedélyezve

### Főbb Entitások és Kapcsolatok / Main Entities and Relationships

A rendszer **86 adatbázis táblát** tartalmaz:

#### Auth & Users (5 tábla)
- `users` - Felhasználók
- `roles` - Szerepkörök
- `user_sessions` - Munkamenetek
- `audit_logs` - Audit naplók
- `system_logs` - Rendszernaplók

**Kapcsolatok:**
- User → Role (N:1)
- User → UserSession (1:N)
- User → AuditLog (1:N)
- User → SystemLog (1:N)

#### Assets (8 tábla)
- `production_lines` - Termelési sorok
- `machines` - Gépek
- `modules` - Modulok
- `machine_versions` - Gép verziók
- `asset_history` - Eszköz előzmények
- `machine_compatible_parts` - Gép-alkatrész kompatibilitás (junction table)
- `production_line_users` - Termelési sor-felhasználó kapcsolat

**Kapcsolatok:**
- ProductionLine → Machine (1:N)
- Machine → Module (1:N)
- Machine ↔ Part (M:N via machine_compatible_parts)
- ProductionLine → User (N:1, responsible_person)
- Machine → AssetHistory (1:N)

#### Inventory (12 tábla)
- `suppliers` - Beszállítók
- `parts` - Alkatrészek
- `inventory_levels` - Készletszintek
- `stock_transactions` - Készletmozgások
- `stock_batches` - Készlet tételek
- `storage_locations` - Raktárhelyek (hierarchikus)
- `part_locations` - Alkatrész-tárhely kapcsolat
- `stock_reservations` - Készlet foglalások
- `qrcode_data` - QR kód adatok
- `inventory_audits` - Készletellenőrzések
- `inventory_audit_items` - Leltári tételek

**Kapcsolatok:**
- Part → Supplier (N:1)
- Part → InventoryLevel (1:1)
- Part → StockTransaction (1:N)
- Part → PartLocation (1:N)
- Part → StockReservation (1:N)
- StorageLocation → StorageLocation (N:1, parent-child)
- StorageLocation → PartLocation (1:N)
- Part → QRCodeData (1:1)

#### Maintenance (15 tábla)
- `pm_tasks` - PM feladatok
- `pm_histories` - PM előzmények
- `pm_task_attachments` - PM fájlok
- `worksheets` - Munkalapok
- `worksheet_parts` - Munkalap-alkatrész kapcsolat
- `worksheet_photos` - Munkalap képek
- `worksheet_pdfs` - Munkalap PDF-ek
- `work_request_pdfs` - Munkaigénylő PDF-ek
- `pm_worksheet_pdfs` - PM munkalap PDF-ek
- `scrapping_documents` - Selejtezési dokumentumok
- `service_records` - Szerviz feljegyzések

**Kapcsolatok:**
- Machine → PMTask (1:N)
- PMTask → PMHistory (1:N)
- PMHistory → PMTaskAttachment (1:N)
- PMHistory → WorkRequestPDF (1:1)
- PMHistory → PMWorksheetPDF (1:1)
- PMHistory → Worksheet (1:1)
- PMHistory → ScrappingDocument (1:N)
- Machine → Worksheet (1:N)
- Worksheet → WorksheetPart (1:N)
- WorksheetPart → Part (N:1)
- Worksheet → WorksheetPhoto (1:N)
- Worksheet → WorksheetPDF (1:1)

#### Notifications (1 tábla)
- `notifications` - Értesítések

**Kapcsolatok:**
- User → Notification (1:N)

#### Human Resources (3 tábla)
- `vacations` - Szabadságok
- `shift_schedules` - Műszak ütemezések
- `shift_rotations` - Műszak forgatások

**Kapcsolatok:**
- User → Vacation (1:N)
- User → ShiftSchedule (1:N)

### Adatbázis Módok / Database Modes

- **Production**: Éles adatbázis (éles adatok)
- **Learning**: Tanuló/teszt adatbázis (teszteléshez)

A módok közötti váltás a **Settings** menüben lehetséges. Minden módnak saját SQLite fájlja van.

---

## 🔄 Munkafolyamatok Részletes Leírása / Detailed Workflows

### 1. PM (Preventive Maintenance) Teljes Folyamat

#### Fázis 1: PM Task Létrehozás

**Manuális létrehozás:**
1. PM menü → "Új feladat" gomb
2. Alapadatok kitöltése:
   - Feladat neve
   - Leírás
   - Kapcsolódó gép kiválasztása
3. Hozzárendelés:
   - Globális (minden aktív felhasználó)
   - Vagy specifikus felhasználó kiválasztása
4. Prioritás beállítása (Low, Normal, High, Urgent)
5. Határidő megadása
6. Mentés

**Automatikus létrehozás:**
1. Production Line menü → Termelési sor kiválasztása
2. Gép kiválasztása a részletes nézetből
3. "Karbantartás igénylése" gomb
4. Dialog megnyitása előre kitöltött géppel
5. További információk megadása (hozzárendelés, prioritás, határidő)
6. Mentés

**Automatikus értesítések:**
- Értesítés küldése a hozzárendelt felhasználó(k)nak
- Dashboard frissítése új feladattal

#### Fázis 2: PM Task Aktív Állapot

- Feladat megjelenik a PM listában
- Dashboard-on látható (due_today, overdue kategóriákban)
- Értesítési csengő jelzi az új feladatot
- Felhasználó láthatja a feladat részleteit

#### Fázis 3: PM Task Elvégzése

1. **Feladat kiválasztása** a PM listából
2. **"Elvégzés" gomb** kattintása
3. **Elvégzési adatok kitöltése**:
   - Dátum és időpont
   - Munka leírása (kötelező)
   - Megfigyelések (opcionális)
   - Eltöltött idő (percben)
   - Befejezési státusz (Kész, Részleges, Problémás)
   - Megjegyzések

4. **Felhasznált alkatrészek hozzáadása** (opcionális):
   - Alkatrész kiválasztása (csak a géphez kompatibilis alkatrészek jelennek meg)
   - Mennyiség megadása (nem lehet nagyobb, mint a készleten lévő mennyiség)
   - Tárhely kiválasztása (csak üres vagy azonos SKU tartalmazó tárhelyek)
   - Minden alkatrész automatikusan hozzáadódik a munkalaphoz

5. **Fájlok feltöltése** (opcionális):
   - Képek (karbantartás előtt/után)
   - Dokumentumok (technikai leírások, hibajegyek)
   - Fájlok mentése: `{pm_task_files_dir}/pm_task_{task_id}/history_{history_id}/`

6. **Mentés és automatikus feldolgozás**:
   - PM History létrehozása
   - Worksheet automatikus létrehozása (ha alkatrészeket használt)
   - Dokumentumok generálása

#### Fázis 4: Automatikus Dokumentum Generálás

A rendszer automatikusan generálja a következő dokumentumokat:

1. **Work Request PDF/DOCX**:
   - Feladat részletei
   - Gép információk
   - Hozzárendelt felhasználó
   - Határidő
   - Mentve: `{task_dir}/work_request_{task_id}.pdf`

2. **PM Worksheet PDF/DOCX**:
   - Elvégzett munkák leírása
   - Felhasznált alkatrészek listája (mennyiséggel)
   - Megfigyelések
   - Végrehajtási dátum és idő
   - ISO 9001 kompatibilis formátum
   - Mentve: `{task_dir}/pm_worksheet_{worksheet_id}.pdf`

3. **Scrapping Documents** (ha alkatrészeket használt):
   - Automatikusan generálva minden felhasznált alkatrészre
   - Selejtezési dátum
   - Selejtezési ok
   - Alkatrész információk
   - Mentve: `{task_dir}/scrapping_part_{part_id}_{timestamp}.docx`

4. **Fájlok másolása**:
   - Minden generált dokumentum másolódik a feladat könyvtárába
   - Struktúra: `{pm_task_files_dir}/pm_task_{task_id}/history_{history_id}/`

#### Fázis 5: Befejezett Feladat Megjelenítés

**Utolsó 10 befejezett feladat:**
- Közvetlenül látható a PM listában
- Részletes információkkal
- Műveleti gombok

**Régebbi feladatok:**
- Csoportosítva év/hónap/nap szerint
- Bővíthető/csukható kategóriákban
- Ugyanazok a műveleti lehetőségek

**Műveleti gombok minden befejezett feladathoz:**
- **Részletek**: Teljes feladat információ, végrehajtási adatok, kapcsolódó munkalap
- **Munkaigénylő**: Work Request PDF/DOCX letöltése/megnyitása
- **Munkalap**: PM Worksheet PDF/DOCX letöltése/megnyitása
- **Selejtezési dokumentum**: Scrapping documents letöltése/megnyitása
- **Fájlok**: Feltöltött fájlok és generált dokumentumok megtekintése

### 2. Worksheet Teljes Folyamat

#### Fázis 1: Worksheet Létrehozás

**Manuális létrehozás:**
1. Worksheets menü → "Új munkalap" gomb
2. Alapadatok kitöltése:
   - Cím
   - Leírás
   - Kapcsolódó gép kiválasztása
3. Mentés → Státusz: **New**

**Automatikus létrehozás:**
- PM Task elvégzésekor automatikusan létrejön, ha alkatrészeket használtak
- Előre kitöltve a PM Task adataival
- Státusz: **New**

#### Fázis 2: Worksheet: New → In Progress

1. Munkalap kiválasztása
2. "Módosítás" gomb
3. Státusz váltás: New → In Progress
4. Megjegyzés hozzáadása (opcionális)
5. Mentés

#### Fázis 3: Alkatrészek Hozzáadása

1. Munkalap részleteknél → "Alkatrész hozzáadása" gomb
2. Alkatrész kiválasztása (csak kompatibilis alkatrészek)
3. Mennyiség megadása
4. Tárhely kiválasztása (csak üres vagy azonos SKU tartalmazó)
5. Mentés → Automatikus készletlevonás

#### Fázis 4: Worksheet: In Progress → Completed

1. Munka befejezése után
2. Státusz váltás: In Progress → Completed
3. Megjegyzés (opcionális)
4. Mentés

#### Fázis 5: Worksheet: Completed → Closed

1. Végleges lezárás
2. Státusz váltás: Completed → Closed
3. Végleges dokumentumok generálása
4. Mentés

### 3. Inventory Teljes Folyamat

#### Fázis 1: Alkatrész Létrehozás

1. Parts menü → "Új alkatrész" gomb
2. Alapadatok kitöltése:
   - Név, SKU, kategória, leírás
   - Mértékegység
   - Beszállító (opcionális)
3. Pénzügyi információk:
   - Vételár, eladási ár
4. Készlet paraméterek:
   - Minimális készlet
   - Újrarendelési mennyiség
5. Kezdeti mennyiség megadása (opcionális)
6. Tárhely kiválasztása (ha kezdeti mennyiség > 0)
7. Mentés → Automatikus InventoryLevel létrehozás

#### Fázis 2: Alkatrész Tárhelyhez Rendelés

**Ha nincs tárhelyhez rendelve:**
1. Storage menü → "Alkatrészek tárhely nélkül" szekció
2. Alkatrész kiválasztása
3. "Tárhelyhez rendelés" gomb
4. Dialog megnyitása:
   - Alkatrész előre kiválasztva
   - Tárhely lista (csak üres vagy azonos SKU tartalmazó)
   - Mennyiség megadása
5. Mentés → PartLocation létrehozás

**Ha már van tárhelyhez rendelve:**
1. Storage menü → Tárhely fa nézet
2. Tárhely kiválasztása
3. "Alkatrész hozzáadása" gomb
4. Alkatrész és mennyiség megadása
5. Mentés

#### Fázis 3: Készletmozgások

**Készletbevétel (Receive Stock):**
1. Parts menü → Alkatrész kiválasztása
2. "Készletbevétel" gomb
3. Mennyiség megadása
4. Tárhely kiválasztása (csak kompatibilis tárhelyek)
5. Mentés → InventoryLevel.quantity_on_hand növelése, PartLocation létrehozása/frissítése

**Készlet kiadás (Issue Stock):**
1. Parts menü → Alkatrész kiválasztása
2. "Készlet kiadás" gomb
3. Mennyiség megadása (nem lehet több, mint készleten)
4. Tárhely kiválasztása (ahonnan kivonunk)
5. Mentés → InventoryLevel.quantity_on_hand csökkentése, PartLocation frissítése

**Készlet módosítás (Adjust Stock):**
1. Parts menü → Alkatrész kiválasztása
2. "Készlet módosítás" gomb
3. Új mennyiség megadása
4. Ok megadása (leltár, hibajavítás, stb.)
5. Mentés → InventoryLevel.quantity_on_hand frissítése

**Készlet átvitel (Transfer Stock):**
1. Storage menü → Tárhely kiválasztása
2. Alkatrész kiválasztása
3. "Átvitel" gomb
4. Cél tárhely kiválasztása
5. Mennyiség megadása
6. Mentés → Forrás tárhely csökkentése, cél tárhely növelése

#### Fázis 4: Készletvalidáció

**Automatikus validáció:**
- Minden készletmozgás után automatikus validáció
- InventoryLevel.quantity_on_hand vs. PartLocation.quantity összeg
- Eltérések naplózása

**Manuális validáció:**
1. Storage menü → "Validáció" gomb
2. Validációs futtatás
3. Eltérések listázása
4. Javítási javaslatok

---

## 🔌 API Dokumentáció / API Documentation

A rendszer FastAPI alapú REST API-t biztosít.

### Főbb Endpointok / Main Endpoints

**Authentication:**
- `POST /api/v1/auth/login` - Bejelentkezés
- `POST /api/v1/auth/logout` - Kijelentkezés
- `GET /api/v1/auth/me` - Aktuális felhasználó

**Assets:**
- `GET /api/v1/assets` - Gépek listája
- `POST /api/v1/assets` - Új gép létrehozása
- `GET /api/v1/assets/{id}` - Gép részletei
- `PUT /api/v1/assets/{id}` - Gép frissítése
- `DELETE /api/v1/assets/{id}` - Gép törlése

**Inventory:**
- `GET /api/v1/inventory/parts` - Alkatrészek listája
- `POST /api/v1/inventory/parts` - Új alkatrész
- `GET /api/v1/inventory/parts/{id}` - Alkatrész részletei

**PM Tasks:**
- `GET /api/v1/pm/tasks` - PM feladatok listája
- `POST /api/v1/pm/tasks` - Új PM feladat
- `PUT /api/v1/pm/tasks/{id}` - PM feladat frissítése

**Worksheets:**
- `GET /api/v1/worksheets` - Munkalapok listája
- `POST /api/v1/worksheets` - Új munkalap
- `PUT /api/v1/worksheets/{id}` - Munkalap frissítése

**API Dokumentáció elérése:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

Részletes API dokumentáció: Lásd `CMMS_Project/API_DOCUMENTATION.md`

---

## 🛠️ Fejlesztés és Karbantartás / Development & Maintenance

### Technológiai Stack / Technology Stack

**Desktop Application:**
- **Python 3.9+**
- **Flet 0.23.2+** - Cross-platform UI framework
- **SQLAlchemy 2.0+** - ORM
- **FastAPI 0.104+** - REST API
- **python-docx 1.1+** - DOCX generálás
- **ReportLab 4.0+** - PDF generálás
- **openpyxl 3.1+** - Excel kezelés
- **pandas 2.1+** - Adatkezelés

**Android Application:**
- **Kotlin**
- **Jetpack Compose** - Modern UI
- **Room** - Lokális adatbázis
- **Retrofit** - API integráció
- **Hilt** - Dependency Injection
- **Material Design 3**

### Függőségek Telepítése / Installing Dependencies

```bash
cd CMMS_Project
pip install -r requirements.txt
```

Főbb csomagok / Main packages:
- `flet>=0.23.2` - UI framework
- `sqlalchemy>=2.0.0` - ORM
- `fastapi>=0.104.0` - API framework
- `python-docx>=1.1.0` - DOCX generálás
- `reportlab>=4.0.0` - PDF generálás
- `openpyxl>=3.1.0` - Excel kezelés
- `pandas>=2.1.0` - Adatkezelés
- `argon2-cffi` - Jelszó hashelés
- `python-jose` - JWT token kezelés

### Tesztek Futtatása / Running Tests

```bash
# Összes teszt
python run_all_tests.py

# Pytest használata
pytest tests/

# Egyedi teszt fájl
pytest tests/test_pm_service.py -v

# Coverage report
pytest tests/ --cov=services --cov=utils
```

### Adatbázis Migrációk / Database Migrations

```bash
# Migrációk futtatása
python run_migrations.py

# Alembic használata
alembic upgrade head

# Új migráció létrehozása
alembic revision --autogenerate -m "Description"
```

### Kód Stílus / Code Style

- **PEP 8** követése
- Type hints használata
- Docstrings minden függvényhez
- Error handling konzisztens módon

### Logging

A rendszer három szintű naplózást használ:

1. **Python logging** (`logging` modul):
   - Alkalmazás szintű naplók
   - Fájlba írás: `data/logs/cmms.log`
   - Rotating logs (max 10 MB, 5 backup)

2. **SystemLog** (adatbázis):
   - Rendszer műveletek
   - Felhasználói műveletek
   - Visszakövethetőség

3. **AuditLog** (adatbázis):
   - Audit trail
   - Változások követése
   - Compliance követelmények

---

## 📚 Dokumentáció / Documentation

### Részletes Dokumentációk / Detailed Documentation

A `CMMS_Project/docs/` könyvtárban található dokumentációk:

1. **SYSTEM_ARCHITECTURE_ANALYSIS.md**
   - Rendszer architektúra áttekintés
   - Entitás kapcsolatok
   - Logikai problémák és javaslatok

2. **DEEP_LOGICAL_ANALYSIS.md**
   - Mély logikai elemzés
   - Függvények logikai struktúrája
   - Javaslatok és megoldások

3. **LOGICAL_TREE_DIAGRAM.md**
   - Rendszer logikai fa diagram
   - Szolgáltatás függőségek
   - Adatfolyam diagramok

4. **SYSTEM_WORKFLOW_DIAGRAM.md**
   - Munkafolyamat diagramok
   - PM, Worksheet, Inventory folyamatok

5. **IMPLEMENTATION_PLAN.md**
   - Implementációs terv
   - Prioritások (P1, P2, P3)
   - Fejlesztési fázisok

6. **USER_MANUAL.md**
   - Felhasználói kézikönyv
   - Részletes használati útmutató

7. **INSTALLATION_WINDOWS.md**
   - Telepítési útmutató Windows rendszerhez

### Rendszer Dokumentáció Letöltése / System Documentation Download

A **System Documentation** menüben az alkalmazáson belül:

- Teljes rendszer leírás
- Logikai fák és diagramok
- Entitás műveletek részletes leírása
- Munkafolyamatok dokumentációja
- Letölthető **DOCX formátumban** (tartalomjegyzékkel)

---

## 🔐 Biztonság / Security

### Jelszó Kezelés / Password Management

- **Argon2** hashelés használata (modern, biztonságos algoritmus)
- Salt automatikus generálása
- Jelszó változtatás kényszerítése (ha be van állítva)
- Jelszó komplexitás követelmények (konfigurálható)

### Autentikáció / Authentication

- **JWT (JSON Web Token)** token alapú autentikáció
- Token lejárat kezelés
- Refresh token támogatás
- Session kezelés

### Hozzáférés-vezérlés / Access Control

- **Szerepkör alapú hozzáférés** (RBAC)
- **Entitás szintű jogosultságok**
- Finomhangolt jogosultságok (olvasás, írás, törlés)
- IP cím alapú hozzáférés-vezérlés (opcionális)

### Audit Trail

- Minden felhasználói művelet naplózva
- Változások követése (mit, ki, mikor)
- Visszakövethetőség
- Compliance követelmények támogatása (ISO 9001, ISO 55001, GDPR)

### Adatbázis Biztonság

- SQLite fájl jogosultságok kezelése
- Backup és restore funkciók
- Adattitkosítás támogatása (SQLCipher)

---

## 🐛 Hibaelhárítás / Troubleshooting

### Gyakori Problémák és Megoldások / Common Issues and Solutions

#### 1. Adatbázis kapcsolati hiba / Database Connection Error

**Tünetek / Symptoms:**
- "Database connection failed" hibaüzenet
- Adatok nem töltődnek be

**Megoldás / Solution:**
1. Ellenőrizze az adatbázis fájl elérési útját a Settings menüben
2. Győződjön meg arról, hogy az adatbázis fájl létezik és írható
3. Ellenőrizze a fájl jogosultságokat
4. Próbálja meg újraindítani az alkalmazást

#### 2. Import hiba / Import Error

**Tünetek / Symptoms:**
- `ModuleNotFoundError` hibaüzenet
- Funkciók nem működnek

**Megoldás / Solution:**
1. Ellenőrizze, hogy minden függőség telepítve van: `pip install -r requirements.txt`
2. Győződjön meg arról, hogy a virtuális környezet aktív
3. Próbálja meg újratelepíteni a függőségeket

#### 3. Lokalizáció hiba / Localization Error

**Tünetek / Symptoms:**
- Hiányzó fordítások
- Hibaüzenetek kulcsokkal

**Megoldás / Solution:**
1. Ellenőrizze a `localization/translations/` könyvtárat
2. Futtassa: `python scripts/check_translations.py`
3. Ellenőrizze a JSON fájlok szintaxisát

#### 4. Dokumentum generálási hiba / Document Generation Error

**Tünetek / Symptoms:**
- PDF/DOCX nem jön létre
- Template hibaüzenetek

**Megoldás / Solution:**
1. Ellenőrizze a template fájlok meglétét a `templates/` könyvtárban
2. Győződjön meg arról, hogy a `python-docx` telepítve van
3. Ellenőrizze a fájl jogosultságokat a `generated_pdfs/` könyvtárban

#### 5. Értesítések nem jelennek meg / Notifications Not Showing

**Tünetek / Symptoms:**
- Értesítési csengő nem mutat új értesítéseket
- Értesítések lista üres

**Megoldás / Solution:**
1. Ellenőrizze az adatbázis kapcsolatot
2. Frissítse az értesítéseket (F5 vagy refresh gomb)
3. Ellenőrizze a `notifications` táblát az adatbázisban

#### 6. Készletvalidációs hiba / Inventory Validation Error

**Tünetek / Symptoms:**
- Készletszámok nem egyeznek
- Validációs hibaüzenetek

**Megoldás / Solution:**
1. Futtassa a validációt a Storage menüben
2. Ellenőrizze az eltéréseket
3. Javítsa ki a készletszámokat manuálisan vagy automatikus javítási funkcióval

### Log Fájlok / Log Files

**Hely / Location:**
- `data/logs/cmms.log` - Alkalmazás napló
- `data/logs/debug.log` - Debug napló (ha engedélyezve)

**Naplózási szintek / Log Levels:**
- DEBUG: Részletes debug információ
- INFO: Általános információk
- WARNING: Figyelmeztetések
- ERROR: Hibák
- CRITICAL: Kritikus hibák

---

## 📊 Rendszer Statisztikák / System Statistics

### Kód Metrikák / Code Metrics

- **Python kód sorok száma**: ~50,000+ sor
- **Service modulok**: 43 modul
- **UI képernyők**: 22 képernyő
- **UI komponensek**: 15 újrafelhasználható komponens
- **Adatbázis táblák**: 86 tábla
- **API végpontok**: 50+ endpoint
- **Lokalizáció nyelvek**: 2 (Magyar, Angol)
- **Dokumentáció fájlok**: 47+ Markdown dokumentum
- **Unit tesztek**: 20+ teszt fájl

### Teljesítmény / Performance

- **Adatbázis lekérdezések**: Optimalizálva indexekkel
- **UI válaszidő**: < 100ms átlagos
- **Dokumentum generálás**: < 2 másodperc (átlagos dokumentum)
- **Szinkronizáció**: Valós idejű (Android app)

---

## 📝 Verzió Információ / Version Information

- **Aktuális verzió / Current Version**: Lásd `CMMS_Project/version.txt`
- **Legutóbbi frissítés / Last Update**: 2025.12.18
- **Státusz / Status**: ✅ Stabil / Stable
- **Fejlesztési fázis / Development Phase**: Production Ready

---

## 📄 Licenc / License

Proprietary - All rights reserved

---

## 🙏 Köszönetnyilvánítás / Acknowledgments

Ez a rendszer modern szoftverfejlesztési elvekkel és best practice-ekkel készült:

- Clean Code elvek
- SOLID elvek
- Design Patterns használata
- Test-driven development
- Continuous Integration

This system was built with modern software development principles and best practices.

---

## 📞 Támogatás és Kapcsolat / Support and Contact

### Dokumentáció

- **Részletes README**: `CMMS_Project/README.md`
- **Android App README**: `AndroidApp/README.md`
- **Dokumentáció könyvtár**: `CMMS_Project/docs/`

### Hasznos Linkek / Useful Links

- **GitHub Repository**: [https://github.com/zedinke/ZedCMMSSystem](https://github.com/zedinke/ZedCMMSSystem)
- **Issue Tracking**: GitHub Issues használata
- **Changelog**: `CMMS_Project/CHANGELOG.md`

---

**Készítette / Created by**: Artence Development Team  
**Dátum / Date**: 2025.12.18  
**Verzió / Version**: 1.0.0

---

*Az alkalmazás folyamatosan fejlesztés alatt áll. Minden javaslat és visszajelzés szívesen várható.*

*The application is under continuous development. All suggestions and feedback are welcome.*
