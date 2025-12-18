# Telepítő és Indító Build Útmutató

Ez az útmutató részletesen leírja, hogyan készíthető el a Windows telepítő és indító .exe fájl az Artence CMMS alkalmazáshoz.

## Előfeltételek

### 1. Python Környezet

- **Python 3.10+** telepítve
- **Virtual environment** aktiválva (`.venv`)
- **Függőségek** telepítve:
  ```bash
  pip install -r requirements.txt
  pip install pyinstaller
  ```

### 2. Inno Setup

- **Telepítés**: Töltse le és telepítse az Inno Setup 6-ot
  - Letöltés: https://jrsoftware.org/isinfo.php
  - Telepítési útvonal: `C:\Program Files (x86)\Inno Setup 6\` (alapértelmezett)
- **Ellenőrzés**: A `ISCC.exe` fájlnak elérhetőnek kell lennie

### 3. Szükséges Fájlok

A következő fájloknak létezniük kell a `CMMS_Project` mappában:
- `build.spec` - PyInstaller konfiguráció CMMS.exe-hez
- `updater.spec` - PyInstaller konfiguráció Updater.exe-hez
- `main.py` - Alkalmazás belépési pont
- `updater.py` - Updater.exe belépési pont
- `version.txt` - Verziószám
- `installer.iss` - Inno Setup script
- `icon.ico` - Alkalmazás ikon (opcionális, de ajánlott)

## Build Lépések

### 1. Környezet Előkészítése

```bash
# Navigáljon a projekt mappába
cd CMMS_Project

# Aktiválja a virtual environment-et (Windows)
.venv\Scripts\activate

# Aktiválja a virtual environment-et (Linux/Mac)
source .venv/bin/activate
```

### 2. Ikon Létrehozása (ha nincs)

Ha nincs `icon.ico` fájl:

```bash
python create_icon.py
```

Ez létrehozza az `icon.ico` fájlt. Ha a PIL/Pillow nincs telepítve, egy placeholder fájl jön létre.

**Megjegyzés**: Az ikon fájl opcionális, de ajánlott a professzionális megjelenéshez.

### 3. Verzió Beállítása

Ellenőrizze vagy frissítse a `version.txt` fájlt:

```
1.0.0
```

A verziószám semantic versioning formátumban kell lennie: `MAJOR.MINOR.PATCH`

### 4. Build Futtatása

Futtassa a build scriptet:

```bash
python build_installer.py
```

Ez a script automatikusan:

1. **Ellenőrzi az előfeltételeket**:
   - PyInstaller telepítve?
   - Inno Setup telepítve?
   - Szükséges fájlok léteznek?

2. **Build-eli a CMMS.exe fájlt**:
   - PyInstaller futtatása `build.spec` fájllal
   - Output: `dist\CMMS.exe`

3. **Build-eli az Updater.exe fájlt**:
   - PyInstaller futtatása `updater.spec` fájllal
   - Output: `dist\Updater.exe`

4. **Build-eli a telepítőt**:
   - Inno Setup futtatása `installer.iss` fájllal
   - Output: `installer\ArtenceCMMS_Setup_v{version}.exe`

5. **Ellenőrzi a build eredményeket**:
   - Minden fájl létezik?
   - Fájlméretek ellenőrzése

### 5. Build Eredmények

Sikeres build után a következő fájlok jönnek létre:

```
CMMS_Project/
├── dist/
│   ├── CMMS.exe          # Fő alkalmazás
│   └── Updater.exe       # Frissítő alkalmazás
└── installer/
    └── ArtenceCMMS_Setup_v1.0.0.exe  # Telepítő
```

## Manuális Build (Lépésről Lépésre)

Ha a build script nem működik, manuálisan is build-elheti:

### 1. CMMS.exe Build

```bash
python -m PyInstaller --clean --noconfirm build.spec
```

**Ellenőrzés**: `dist\CMMS.exe` létezik-e

### 2. Updater.exe Build

```bash
python -m PyInstaller --clean --noconfirm updater.spec
```

**Ellenőrzés**: `dist\Updater.exe` létezik-e

### 3. Telepítő Build

```bash
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
```

**Megjegyzés**: Ha az Inno Setup másik útvonalon van telepítve, módosítsa az útvonalat.

**Ellenőrzés**: `installer\ArtenceCMMS_Setup_v{version}.exe` létezik-e

## Build Konfiguráció

### build.spec (CMMS.exe)

A PyInstaller konfiguráció tartalmazza:
- **Entry point**: `main.py`
- **Data files**: templates, localization, migrations
- **Hidden imports**: összes szükséges Python modul
- **Output**: `dist\CMMS.exe`
- **Icon**: `icon.ico` (ha létezik)
- **Console**: `False` (nincs konzol ablak)

### updater.spec (Updater.exe)

A PyInstaller konfiguráció tartalmazza:
- **Entry point**: `updater.py`
- **Hidden imports**: urllib, subprocess, psutil (opcionális)
- **Output**: `dist\Updater.exe`
- **Console**: `True` (konzol mód debugging-hoz)
- **Icon**: `icon.ico` (ha létezik)

### installer.iss (Telepítő)

Az Inno Setup script tartalmazza:
- **Alkalmazás információk**: név, verzió, publisher
- **Telepítési útvonal**: `{pf}\ArtenceCMMS` (Program Files)
- **Fájlok másolása**: 
  - CMMS.exe
  - Updater.exe
  - templates, localization, migrations
- **Shortcut-ok**: Desktop és Start Menu
- **Uninstaller**: automatikus támogatás

## Verziókezelés

### Verzió Frissítése

1. Szerkessze a `version.txt` fájlt:
   ```
   1.0.1
   ```

2. Futtassa újra a build scriptet:
   ```bash
   python build_installer.py
   ```

3. Az új telepítő tartalmazza a frissített verziót:
   - Fájlnév: `ArtenceCMMS_Setup_v1.0.1.exe`
   - Windows verzióinformációk: 1.0.1

### Verzió Olvasása

A verzió automatikusan olvasódik a `version.txt` fájlból:
- PyInstaller build: verzió a .exe fájlban
- Inno Setup build: verzió a telepítő fájlnévben és a Windows regisztrációban

## Telepítő Tesztelés

### 1. Telepítés Tesztelése

1. Futtassa a telepítőt egy tiszta Windows gépen (vagy VM-ben)
2. Kövesse a telepítési lépéseket
3. Ellenőrizze:
   - Az alkalmazás telepítve van-e: `C:\Program Files\ArtenceCMMS\`
   - Shortcut-ok létrejöttek-e:
     - Desktop: `Artence CMMS.lnk`
     - Start Menu: `Artence CMMS` mappa
   - Az alkalmazás elindul-e

### 2. Funkcionalitás Tesztelése

Tesztelje az alkalmazás fő funkcióit:
- Bejelentkezés
- Adatbázis kapcsolat
- Fájlok feltöltése
- Jelentések generálása
- Beállítások módosítása
- **Frissítés ellenőrzés** (ha GitHub repository be van állítva)

### 3. Uninstaller Tesztelése

1. Telepítse az alkalmazást
2. Futtassa az uninstaller-t:
   - Vezérlőpult → Programok és szolgáltatások
   - Vagy Start Menu → Artence CMMS → Uninstall
3. Ellenőrizze:
   - Az alkalmazás eltávolítva van-e
   - A felhasználói adatok megmaradtak-e (`%LOCALAPPDATA%\ArtenceCMMS\`)

## Hibaelhárítás

### PyInstaller Build Hiba

**"Module not found" hiba**:
- Ellenőrizze a `hiddenimports` listát a `build.spec` vagy `updater.spec`-ben
- Adja hozzá a hiányzó modult

**"Data file not found" hiba**:
- Ellenőrizze a `datas` listát a `build.spec`-ben
- Ellenőrizze, hogy a fájlok léteznek-e

**"Icon file not found" hiba**:
- Ez nem kritikus hiba, a build folytatódik
- Hozzon létre egy `icon.ico` fájlt vagy futtassa a `create_icon.py` scriptet

### Inno Setup Build Hiba

**"ISCC.exe not found"**:
- Ellenőrizze az Inno Setup telepítési útvonalát
- Frissítse a `build_installer.py`-ban az útvonalat, ha szükséges

**"Source file not found"**:
- Ellenőrizze, hogy a `dist\CMMS.exe` létezik-e
- Ellenőrizze, hogy a `dist\Updater.exe` létezik-e
- Futtassa először a PyInstaller build-et

**"Version file not found"**:
- Ellenőrizze, hogy a `version.txt` létezik-e
- Ellenőrizze, hogy a fájl tartalmaz verziószámot

### Telepítő Hiba

**"Access denied" telepítéskor**:
- Futtassa a telepítőt adminisztrátorként
- Jobb klikk → "Futtatás rendszergazdaként"

**"File in use" telepítéskor**:
- Zárja be az alkalmazást, ha fut
- Ellenőrizze a Task Manager-ben
- Indítsa újra a számítógépet, ha szükséges

## Build Optimalizálás

### Executable Méret Csökkentése

- Használjon `--onefile` módot (már be van állítva)
- Exclude-oljon nem használt modulokat
- Használjon UPX tömörítést (már be van állítva)

### Telepítő Méret Csökkentése

- Használjon LZMA2 tömörítést (már be van állítva)
- Ne tartalmazza a fejlesztői fájlokat
- Ne tartalmazza a teszt fájlokat

## Distribution

### Telepítő Terjesztése

A telepítő fájl (`ArtenceCMMS_Setup_v{version}.exe`) tartalmazza:
- Az összes szükséges fájlt
- Az alkalmazás .exe fájlját (CMMS.exe)
- A frissítő alkalmazást (Updater.exe)
- A sablonokat és fordításokat
- Az uninstaller-t

### Függőségek és Előfeltételek

**FONTOS**: A telepítő **minden szükséges függőséget tartalmaz**, beleértve:

- ✅ **Python interpreter** - Beágyazva a CMMS.exe-be (PyInstaller onefile mód)
- ✅ **Összes Python modul** - Flet, SQLAlchemy, Pandas, Openpyxl, stb. (minden beágyazva)
- ✅ **Rendszerkönyvtárak** - Szükséges DLL-ek és egyéb fájlok
- ✅ **Alkalmazás fájlok** - Templates, lokalizációk, migrációk

**Nincs szükség a célgépen**:
- ❌ Python telepítésre
- ❌ pip install-ra
- ❌ requirements.txt telepítésre
- ❌ Virtual environment-re
- ❌ További konfigurációra

**Rendszerkövetelmények a célgépen**:
- Windows 10 vagy újabb (64-bit)
- Adminisztrátori jogosultság (telepítéshez)
- Internet kapcsolat (csak adatbázis kapcsolathoz, nem a telepítéshez)

### Telepítés Másik Gépen

1. **Másolja át a telepítő fájlt**:
   - `ArtenceCMMS_Setup_v{version}.exe`
   - USB-ről, hálózatról, vagy bármilyen módon

2. **Futtassa a telepítőt**:
   - Dupla kattintás a telepítő fájlra
   - Adminisztrátori jogosultság szükséges
   - Kövesse a telepítési varázslót

3. **Kész!**:
   - Az alkalmazás azonnal használható
   - Nincs szükség további telepítésre vagy konfigurációra
   - Az alkalmazás tartalmazza az összes függőséget

### PyInstaller Onefile Mód

A `build.spec` fájlban a `onefile=True` mód be van állítva, ami azt jelenti:

- **Egyetlen .exe fájl**: A CMMS.exe tartalmazza az összes szükséges fájlt
- **Önálló működés**: Nincs szükség külső fájlokra vagy könyvtárakra
- **Portable**: Bárhova másolható és futtatható

**Működés**:
1. A CMMS.exe indításakor PyInstaller kicsomagolja a fájlokat egy temp mappába
2. Futtatja az alkalmazást
3. Bezáráskor törli a temp fájlokat

**Előnyök**:
- Egyszerű terjesztés (egy fájl)
- Nincs szükség külön Python telepítésre
- Önálló működés

**Hátrányok**:
- Nagyobb fájlméret (minden beágyazva)
- Lassabb indítás (kicsomagolás ideje)

### Verziófrissítés Terjesztése

1. Készítse el az új telepítőt (verzió frissítéssel)
2. Terjesztse az új telepítőt
3. A felhasználók futtathatják az új telepítőt (felülírja a régit)
4. A felhasználói adatok megmaradnak

**Vagy** használja az automatikus frissítési rendszert:
- GitHub Release létrehozása
- A felhasználók automatikusan értesítést kapnak
- Egy kattintással frissíthetnek

## Gyors Referencia

### Teljes Build (Ajánlott)

```bash
cd CMMS_Project
.venv\Scripts\activate
python build_installer.py
```

### Csak CMMS.exe

```bash
python -m PyInstaller --clean --noconfirm build.spec
```

### Csak Updater.exe

```bash
python -m PyInstaller --clean --noconfirm updater.spec
```

### Csak Telepítő

```bash
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
```

## További Információk

- **PyInstaller dokumentáció**: https://pyinstaller.org/
- **Inno Setup dokumentáció**: https://jrsoftware.org/ishelp/
- **Build folyamat**: Lásd `docs/BUILD_PROCESS.md`
- **Telepítési útmutató**: Lásd `docs/INSTALLATION_WINDOWS.md`
- **Frissítési rendszer**: Lásd `docs/UPDATE_SYSTEM.md`

---

**Utolsó frissítés**: 2025-12-15  
**Build Tool**: PyInstaller 6.3.0 + Inno Setup 6

