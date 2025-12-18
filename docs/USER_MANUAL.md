# CMMS Rendszer - Felhasználói Kézikönyv
# CMMS System - User Manual

## Tartalomjegyzék / Table of Contents

1. [Bevezetés / Introduction](#bevezetés--introduction)
2. [Bejelentkezés / Login](#bejelentkezés--login)
3. [Főmenü / Main Menu](#főmenü--main-menu)
4. [Eszközkezelés / Asset Management](#eszközkezelés--asset-management)
5. [Készletkezelés / Inventory Management](#készletkezelés--inventory-management)
6. [Munkalapok / Worksheets](#munkalapok--worksheets)
7. [Megelőző Karbantartás / Preventive Maintenance](#megelőző-karbantartás--preventive-maintenance)
8. [Szabadságkezelés / Vacation Management](#szabadságkezelés--vacation-management)
9. [Műszak Beosztás / Shift Schedule](#műszak-beosztás--shift-schedule)
10. [Jelentések / Reports](#jelentések--reports)
11. [Rendszer Naplók / System Logs](#rendszer-naplók--system-logs)
12. [Beállítások / Settings](#beállítások--settings)

---

## Bevezetés / Introduction

A CMMS (Computerized Maintenance Management System) egy átfogó karbantartáskezelő rendszer, amely segít a gépek, berendezések és készletek hatékony kezelésében.

The CMMS (Computerized Maintenance Management System) is a comprehensive maintenance management system that helps efficiently manage machines, equipment, and inventory.

### Főbb funkciók / Key Features

- **Eszközkezelés / Asset Management**: Gépek és berendezések nyilvántartása
- **Készletkezelés / Inventory Management**: Alkatrészek és készletek kezelése
- **Munkalapok / Worksheets**: Karbantartási munkalapok létrehozása és kezelése
- **Megelőző Karbantartás / Preventive Maintenance**: Ütemezett karbantartási feladatok
- **Jelentések / Reports**: Részletes statisztikák és kimutatások
- **Kétnyelvű támogatás / Bilingual Support**: Magyar és Angol nyelv

---

## Bejelentkezés / Login

1. Indítsd el az alkalmazást / Start the application
2. Add meg a felhasználóneved és jelszavad / Enter your username and password
3. Kattints a "Bejelentkezés" / "Login" gombra

### Szerepkörök / Roles

- **Manager / Menedzser**: Teljes hozzáférés minden funkcióhoz / Full access to all features
- **Technician / Karbantartó**: Korlátozott hozzáférés / Limited access

---

## Főmenü / Main Menu

A bal oldali menüben a következő opciók érhetők el:

The left sidebar menu provides access to:

- **Dashboard / Vezérlőpult**: Áttekintés és gyors statisztikák / Overview and quick statistics
- **Eszközök / Assets**: Gépek és berendezések kezelése / Manage machines and equipment
- **Készlet / Inventory**: Alkatrészek kezelése / Manage parts
- **Munkalapok / Worksheets**: Karbantartási munkalapok / Maintenance worksheets
- **PM Feladatok / PM Tasks**: Megelőző karbantartás / Preventive maintenance
- **Szabadság / Vacation**: Szabadság igénylések és naptár / Vacation requests and calendar
- **Műszak Beosztás / Shift Schedule**: Műszak beállítások / Shift settings
- **Jelentések / Reports**: Statisztikák és kimutatások / Statistics and reports
- **Naplók / Logs**: Rendszer naplók megtekintése / View system logs
- **Dokumentáció / Documentation**: Sablon dokumentáció / Template documentation
- **Beállítások / Settings**: Rendszerbeállítások / System settings

---

## Eszközkezelés / Asset Management

### Gépek hozzáadása / Adding Machines

1. Kattints az "Eszközök" menüpontra / Click on "Assets" menu item
2. Kattints a "+ Hozzáadás" gombra / Click the "+ Add" button
3. Töltsd ki a kötelező mezőket / Fill in required fields:
   - Név / Name
   - Termelési vonal ID / Production Line ID
   - Sorozatszám / Serial Number
   - Gyártó / Manufacturer
   - Modell / Model
4. Kattints a "Mentés" gombra / Click "Save"

### Gép történet megtekintése / Viewing Machine History

1. Az eszközök listájában kattints a gép melletti "Történet" ikonra / In the assets list, click the "History" icon next to a machine
2. A megnyíló ablakban négy fül érhető el / The dialog shows four tabs:
   - **Munkalapok / Worksheets**: A géphez kapcsolódó munkalapok / Worksheets for this machine
   - **PM Feladatok / PM Tasks**: Megelőző karbantartási feladatok / Preventive maintenance tasks
   - **Modulok / Modules**: A gép moduljai / Machine modules
   - **Aktivitás / Activity**: Változások idővonala / Timeline of changes

### Modulok kezelése / Managing Modules

1. Nyisd meg a gép történetét / Open machine history
2. Kattints a "Modulok" fülre / Click the "Modules" tab
3. Kattints a "+ Modul hozzáadása" gombra / Click "+ Add Module"
4. Add meg a modul nevét és leírását / Enter module name and description
5. Mentés / Save

---

## Készletkezelés / Inventory Management

### Alkatrész hozzáadása / Adding Parts

1. Kattints a "Készlet" menüpontra / Click "Inventory" menu item
2. Kattints a "+ Hozzáadás" gombra / Click "+ Add" button
3. Töltsd ki az adatokat / Fill in the data:
   - Név / Name
   - SKU (kötelező / required)
   - Kategória / Category
   - Vételár / Buy Price
   - Biztonsági készlet / Safety Stock
4. Kattints a "Mentés" gombra / Click "Save"

### QR Kód generálás / QR Code Generation

1. Az alkatrész kártyán kattints a QR kód ikonra / On the part card, click the QR code icon
2. A megnyíló ablakban láthatod a QR kódot / The dialog shows the QR code
3. Kattints a "Címkék generálása" gombra a nyomtatható címkékhez / Click "Generate Labels" for printable labels

### Tömeges QR Címkék / Bulk QR Labels

1. A készlet képernyőn kattints a "QR Címkék" gombra / On inventory screen, click "QR Labels" button
2. Jelöld ki a kívánt alkatrészeket / Select desired parts
3. Kattints a "Generálás" gombra / Click "Generate"
4. A PDF automatikusan megnyílik / PDF opens automatically

---

## Munkalapok / Worksheets

### Munkalap létrehozása / Creating a Worksheet

1. Kattints a "Munkalapok" menüpontra / Click "Worksheets" menu item
2. Kattints a "+ Új munkalap" gombra / Click "+ New Worksheet"
3. Válassz gépet / Select machine
4. Add meg a címet és leírást / Enter title and description
5. Kattints a "Létrehozás" gombra / Click "Create"

### Munkalap státuszok / Worksheet Statuses

- **Nyitott / Open**: Munkálatok folyamatban / Work in progress
- **Alkatrészre vár / Waiting for Parts**: Szüneteltetve, alkatrész hiány miatt / Paused due to missing parts
- **Lezárt / Closed**: Befejezve, készlet levonva / Completed, stock deducted

### Alkatrész hozzáadása / Adding Parts

1. Nyisd meg a munkalap részleteit / Open worksheet details
2. Kattints az "Alkatrész hozzáadása" gombra / Click "Add Part" button
3. Válassz alkatrészt és mennyiséget / Select part and quantity
4. A készlet csak akkor vonódik le, amikor a munkalap lezárásra kerül / Stock is only deducted when worksheet is closed

### DOCX Export / DOCX Export

1. A munkalap részleteinél kattints a "DOCX letöltése" gombra / In worksheet details, click "Download DOCX"
2. Válassz mentési helyet / Choose save location
3. A dokumentum ISO 9001 kompatibilis formátumban készül / Document is generated in ISO 9001 compatible format

---

## Megelőző Karbantartás / Preventive Maintenance

### PM Feladat létrehozása / Creating PM Task

1. Kattints a "PM Feladatok" menüpontra / Click "PM Tasks" menu item
2. Kattints a "+ Új feladat" gombra / Click "+ New Task"
3. Válassz gépet / Select machine
4. Add meg a feladat nevét és gyakoriságát / Enter task name and frequency
5. Kattints a "Létrehozás" gombra / Click "Create"

### PM Feladat végrehajtása / Executing PM Task

1. A "Esedékes ma" listában kattints egy feladatra / In "Due Today" list, click a task
2. Kattints a "Végrehajtás" gombra / Click "Execute" button
3. Add meg a részleteket / Enter details:
   - Időtartam / Duration
   - Megjegyzések / Notes
4. Kattints a "Befejezés" gombra / Click "Complete"

---

## Jelentések / Reports

### Jelentések megtekintése / Viewing Reports

1. Kattints a "Jelentések" menüpontra / Click "Reports" menu item
2. Válassz időszakot (Nap/Hét/Hó/Év) / Select period (Day/Week/Month/Year)
3. Használd a "Személyes csak" kapcsolót a saját adataidhoz / Use "Personal only" toggle for your own data

### Szűrők / Filters

- **Gép / Machine**: Szűrés gép szerint / Filter by machine
- **Státusz / Status**: Szűrés státusz szerint / Filter by status
- **Prioritás / Priority**: Szűrés prioritás szerint / Filter by priority

### Grafikonok / Charts

- **Költség bontás / Cost Breakdown**: Költségek kategóriánként / Costs by category
- **Idő bontás / Time Breakdown**: Idő felhasználás / Time usage
- **Feladat bontás / Task Breakdown**: Feladatok típusonként / Tasks by type

**Megjegyzés / Note**: Kattints egy grafikonra a részletekért / Click a chart for details

### Excel Export / Excel Export

1. Kattints az "Excel letöltése" gombra / Click "Download Excel" button
2. Válassz mentési helyet / Choose save location
3. Az Excel fájl tartalmazza az összes grafikonokat és táblázatokat / Excel file contains all charts and tables

---

## Rendszer Naplók / System Logs

### Naplók megtekintése / Viewing Logs

1. Kattints a "Naplók" / "Logs" menüpontra
2. Szűrj év, hónap, kategória szerint / Filter by year, month, category
3. Keresés a leírásban / Search in description
4. A naplók mutatják:
   - **Művelet típusa / Action Type**: create, update, delete, approve, stb.
   - **Entitás típusa / Entity Type**: part, machine, worksheet, vacation, stb.
   - **Felhasználó / User**: Ki végezte a műveletet / Who performed the action
   - **Időbélyeg / Timestamp**: Mikor történt / When it happened
   - **Leírás / Description**: Részletes információ / Detailed information

### Napló kategóriák / Log Categories

- **Asset Management**: Eszköz változások / Asset changes
- **Inventory**: Készletmozgások / Stock movements
- **Worksheet**: Munkalap műveletek / Worksheet operations
- **PM**: Megelőző karbantartás / Preventive maintenance
- **Vacation**: Szabadság műveletek / Vacation operations
- **User**: Felhasználó műveletek / User operations
- **System**: Rendszer műveletek / System operations

### Napló archiválás és törlés / Log Archiving and Deletion

A beállításokban konfigurálható:
- **Log archiválási időszak / Log Archive Period**: Hány év után archiválódjanak / After how many years to archive
- **Log törlési időszak / Log Delete Period**: Hány év után törlődjenek / After how many years to delete

Configurable in settings:
- **Log Archive Period**: Years before archiving
- **Log Delete Period**: Years before deletion

---

## Selejtezési Dokumentumok / Scrapping Documents

### Automatikus generálás / Automatic Generation

A rendszer automatikusan generál selejtezési dokumentumokat (DOCX) a következő esetekben:

The system automatically generates scrapping documents (DOCX) in the following cases:

1. **Alkatrész törlésnél / When deleting a part**: Generálódik egy selejtezési lap / Scrapping sheet is generated
2. **Eszköz törlésnél / When deleting an asset**: Generálódik egy selejtezési lap / Scrapping sheet is generated
3. **Karbantartásnál elhasznált anyagoknál / Materials used in maintenance**: Generálódik egy selejtezési dokumentum / Scrapping document is generated

### Selejtezési dokumentum letöltése / Downloading Scrapping Document

1. A megfelelő képernyőn (alkatrész/eszköz részletek, munkalap) / On the appropriate screen (part/asset details, worksheet)
2. Kattints a "Selejtezési dokumentum letöltése" / "Download Scrapping Document" gombra
3. A dokumentum a kiválasztott sablon alapján generálódik / Document is generated based on selected template

### Selejtezési sablon beállítása / Setting Scrapping Template

1. Menj a "Beállítások" / "Settings" képernyőre
2. A "Sablonok" / "Templates" szekcióban válaszd ki a selejtezési sablont / In "Templates" section, select scrapping template
3. A sablon változóit lásd a "Dokumentáció" menüben / See template variables in "Documentation" menu

---

## Beállítások / Settings

### Nyelv váltás / Language Change

1. Kattints a "Beállítások" menüpontra / Click "Settings" menu item
2. Válassz nyelvet a "Nyelv" legördülő menüből / Select language from "Language" dropdown
3. A változás azonnal érvénybe lép / Change takes effect immediately

### Sablonok / Templates

- **Munkalap sablon / Worksheet Template**: Válassz DOCX sablont a munkalapokhoz / Select DOCX template for worksheets
- **Munkaigénylő sablon / Work Request Template**: Válassz DOCX sablont a munkaigénylőkhöz / Select DOCX template for work requests

### Adatmentés / Backup

1. A "Beállítások" képernyőn görgess le az "Adatmentés" részhez / On "Settings" screen, scroll to "Backup" section
2. **Adatbázis mentése / Backup Database**: Csak az adatbázist menti / Backs up only database
3. **Teljes mentés / Full Backup**: Adatbázis + fájlok ZIP-ben / Database + files in ZIP

**Megjegyzés / Note**: A mentések a `data/system_backups/` mappában találhatók / Backups are stored in `data/system_backups/` folder

### Ütemezett mentés / Scheduled Backup

1. Az "Adatmentés" szekcióban található az "Ütemezett mentés" / "Scheduled Backup" rész
2. Add meg az időközt (órákban) / Enter interval (in hours):
   - **Backup interval (hours)**: Hány óránként történjen a mentés / How often to backup
   - **Retention (days)**: Hány napig tartsa meg a mentéseket / How many days to keep backups
3. Kattints az "Indítás" / "Start" gombra az ütemezett mentés elindításához / Click "Start" to start scheduled backups
4. Kattints a "Leállítás" / "Stop" gombra az ütemezett mentés leállításához / Click "Stop" to stop scheduled backups

**Megjegyzés / Note**: Az ütemezett mentés háttérben fut, és automatikusan törli a régi mentéseket / Scheduled backup runs in background and automatically deletes old backups

---

## Gyakori kérdések / FAQ

### Hogyan állíthatom vissza az adatokat? / How do I restore data?

A jelenlegi verzióban a visszaállítás manuálisan történik a backup fájlokból. / In current version, restoration is manual from backup files.

### Hol találom a generált dokumentumokat? / Where are generated documents?

- Munkalapok: `generated_pdfs/` mappa / Worksheets: `generated_pdfs/` folder
- Jelentések: Letöltéskor választott hely / Reports: User-selected location

### Hogyan változtathatom meg a jelszavam? / How do I change my password?

Jelenleg csak a Manager szerepkör változtathatja meg a jelszavakat. / Currently only Manager role can change passwords.

---

**Dokumentum verzió / Document Version**: 1.0.0  
**Utolsó frissítés / Last Updated**: 2025-12-14

