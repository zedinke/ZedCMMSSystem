# Telepítő Build Útmutató

Ez a dokumentum leírja, hogyan készíthető el a Windows telepítő az Artence CMMS alkalmazáshoz.

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

A következő fájloknak létezniük kell:
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
cd CMMS_Project
.venv\Scripts\activate  # Windows
```

### 2. Ikon Létrehozása (ha nincs)

Ha nincs `icon.ico` fájl:

```bash
python create_icon.py
```

Ez létrehozza az `icon.ico` fájlt. Ha a PIL/Pillow nincs telepítve, egy placeholder fájl jön létre.

### 3. Build Futtatása

Futtassa a build scriptet:

```bash
python build_installer.py
```

Ez a script:
1. Ellenőrzi az előfeltételeket
2. Build-eli a `CMMS.exe` fájlt PyInstaller-rel
3. Build-eli az `Updater.exe` fájlt PyInstaller-rel
4. Build-eli a telepítőt Inno Setup-tal
5. Ellenőrzi a build eredményeket

### 4. Build Eredmények

Sikeres build után:

- **CMMS.exe**: `dist\CMMS.exe` (fő alkalmazás)
- **Updater.exe**: `dist\Updater.exe` (frissítő alkalmazás)
- **Installer**: `installer\ArtenceCMMS_Setup_v{version}.exe` (telepítő)

## Manuális Build (Lépésről Lépésre)

Ha a build script nem működik, manuálisan is build-elheti:

### 1. CMMS.exe Build

```bash
python -m PyInstaller --clean --noconfirm build.spec
```

Ellenőrizze: `dist\CMMS.exe` létezik-e

### 2. Updater.exe Build

```bash
python -m PyInstaller --clean --noconfirm updater.spec
```

Ellenőrizze: `dist\Updater.exe` létezik-e

### 3. Inno Setup Build

```bash
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
```

Ellenőrizze: `installer\ArtenceCMMS_Setup_v{version}.exe` létezik-e

## Build Konfiguráció

### build.spec

A PyInstaller konfiguráció tartalmazza:
- **Entry point**: `main.py`
- **Data files**: templates, localization, migrations
- **Hidden imports**: összes szükséges Python modul
- **Output**: `dist\CMMS.exe`
- **Icon**: `icon.ico` (ha létezik)

### installer.iss

Az Inno Setup script tartalmazza:
- **Alkalmazás információk**: név, verzió, publisher
- **Telepítési útvonal**: `{pf}\ArtenceCMMS`
- **Fájlok másolása**: CMMS.exe + szükséges adatok
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

3. Az új telepítő tartalmazza a frissített verziót

### Verzió Olvasása

A verzió automatikusan olvasódik a `version.txt` fájlból:
- PyInstaller build: verzió a .exe fájlban
- Inno Setup build: verzió a telepítő fájlnévben és a Windows regisztrációban

## Telepítő Testelés

### 1. Telepítés Tesztelése

1. Futtassa a telepítőt egy tiszta Windows gépen (vagy VM-ben)
2. Kövesse a telepítési lépéseket
3. Ellenőrizze:
   - Az alkalmazás telepítve van-e
   - Shortcut-ok létrejöttek-e
   - Az alkalmazás elindul-e

### 2. Funkcionalitás Tesztelése

Tesztelje az alkalmazás fő funkcióit:
- Bejelentkezés
- Adatbázis kapcsolat
- Fájlok feltöltése
- Jelentések generálása
- Beállítások módosítása

### 3. Uninstaller Tesztelése

1. Telepítse az alkalmazást
2. Futtassa az uninstaller-t
3. Ellenőrizze:
   - Az alkalmazás eltávolítva van-e
   - A felhasználói adatok megmaradtak-e (`%LOCALAPPDATA%`)

## Hibaelhárítás

### PyInstaller Build Hiba

**"Module not found" hiba**:
- Ellenőrizze a `hiddenimports` listát a `build.spec`-ben
- Adja hozzá a hiányzó modult

**"Data file not found" hiba**:
- Ellenőrizze a `datas` listát a `build.spec`-ben
- Ellenőrizze, hogy a fájlok léteznek-e

### Inno Setup Build Hiba

**"ISCC.exe not found"**:
- Ellenőrizze az Inno Setup telepítési útvonalát
- Frissítse a `build_installer.py`-ban az útvonalat

**"Source file not found"**:
- Ellenőrizze, hogy a `dist\CMMS.exe` létezik-e
- Ellenőrizze, hogy a `dist\Updater.exe` létezik-e
- Futtassa először a PyInstaller build-eket

### Telepítő Hiba

**"Access denied" telepítéskor**:
- Futtassa a telepítőt adminisztrátorként

**"File in use" telepítéskor**:
- Zárja be az alkalmazást, ha fut
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

**Nincs szükség**:
- Python telepítésre
- Függőségek telepítésére
- További konfigurációra

### Verziófrissítés Terjesztése

1. Készítse el az új telepítőt
2. Terjesztse az új telepítőt
3. A felhasználók futtathatják az új telepítőt (felülírja a régit)
4. A felhasználói adatok megmaradnak

## További Információk

- **PyInstaller dokumentáció**: https://pyinstaller.org/
- **Inno Setup dokumentáció**: https://jrsoftware.org/ishelp/
- **Build folyamat**: Lásd `docs/BUILD_PROCESS.md`

---

**Utolsó frissítés**: 2025-12-15  
**Build Tool**: PyInstaller 6.3.0 + Inno Setup 6

