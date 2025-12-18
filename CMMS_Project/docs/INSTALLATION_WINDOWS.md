# Windows Telepítési Útmutató

## Rendszerkövetelmények

- **Operációs rendszer**: Windows 10 vagy újabb (64-bit)
- **Szabad lemezterület**: Minimum 500 MB
- **Jogosultság**: Adminisztrátori jogosultság szükséges a telepítéshez
- **Hálózat**: Internet kapcsolat szükséges az adatbázis kapcsolathoz (MySQL szerver)

### Fontos Megjegyzés - Függőségek

**A telepítő tartalmazza az összes szükséges függőséget!**

- ✅ **Nincs szükség Python telepítésre** - A Python interpreter beágyazva van
- ✅ **Nincs szükség pip install-ra** - Minden Python modul beágyazva van
- ✅ **Nincs szükség requirements.txt-re** - Minden függőség tartalmazva van
- ✅ **Önálló működés** - Az alkalmazás azonnal használható telepítés után

A telepítő egyetlen fájlként tartalmazza:
- Python interpreter és runtime
- Összes Python modul (Flet, SQLAlchemy, Pandas, Openpyxl, stb.)
- Szükséges rendszerkönyvtárak és DLL-ek
- Alkalmazás fájlok (templates, lokalizációk)

## Telepítési Lépések

### 1. Telepítő letöltése

Töltse le a `ArtenceCMMS_Setup_v{version}.exe` fájlt.

### 2. Telepítő futtatása

1. Kattintson duplán a telepítő fájlra
2. Ha megjelenik a "Windows protected your PC" figyelmeztetés:
   - Kattintson a "More info" gombra
   - Kattintson a "Run anyway" gombra
3. Kövesse a telepítési varázslót

### 3. Telepítési Opciók

A telepítés során a következő opciókat választhatja:

- **Telepítési útvonal**: Alapértelmezetten `C:\Program Files\ArtenceCMMS`
- **Desktop shortcut**: Hozzon létre ikont az asztalon (opcionális, checkbox)
- **Start Menu shortcut**: Hozzon létre ikont a Start menüben (automatikus, mindig létrejön)

### 4. Telepítés befejezése

A telepítés után **automatikusan létrejönnek**:

- ✅ **Start Menu shortcut**: `C:\ProgramData\Microsoft\Windows\Start Menu\Programs\ArtenceCMMS\Artence CMMS.lnk`
  - Ez mindig létrejön, automatikusan
  - Közvetlenül a `CMMS.exe`-re mutat
  
- ✅ **Desktop shortcut**: `C:\Users\{felhasználó}\Desktop\Artence CMMS.lnk` (ha be van jelölve)
  - Opcionális, checkbox-szal választható
  - Közvetlenül a `CMMS.exe`-re mutat

- ✅ **Telepített fájlok**: 
  - `C:\Program Files\ArtenceCMMS\CMMS.exe` - Fő alkalmazás (ez az "indító fájl")
  - `C:\Program Files\ArtenceCMMS\Updater.exe` - Frissítő alkalmazás

**Fontos**: 
- A `CMMS.exe` **közvetlenül futtatható** - ez maga az "indító fájl"
- A shortcut-ok (.lnk fájlok) csak gyors eléréshez szolgálnak
- Nincs szükség külön launcher.exe fájlra - a `CMMS.exe` önállóan működik

## Első Indítás

### 1. Alkalmazás indítása

- **Desktop shortcut**: Kattintson duplán az "Artence CMMS" ikonra az asztalon
- **Start Menu**: Keresse meg az "Artence CMMS" mappát a Start menüben és kattintson az alkalmazásra

### 2. Bejelentkezés

- **Felhasználónév**: `admin`
- **Alapértelmezett jelszó**: Lásd a rendszergazdát vagy a dokumentációt
- **Fontos**: Változtassa meg a jelszót az első bejelentkezéskor!

### 3. Adatbázis kapcsolat

Az alkalmazás MySQL adatbázist használ. Az adatbázis beállításokat a **Fejlesztői eszközök** menüpontban módosíthatja:
- Production Database (Éles adatbázis)
- Learning Database (Tanuló adatbázis)

## Telepítés Eltávolítása

### Uninstaller használata

1. Nyissa meg a **Vezérlőpult** → **Programok és szolgáltatások** (Programs and Features)
2. Keresse meg az "Artence CMMS" elemet
3. Kattintson az **Eltávolítás** (Uninstall) gombra
4. Vagy használja a Start Menu-ban lévő "Uninstall Artence CMMS" shortcut-ot

### Manuális eltávolítás

Ha az uninstaller nem működik:

1. Törölje a telepítési mappát: `C:\Program Files\ArtenceCMMS`
2. Törölje a felhasználói adatokat (opcionális): `%LOCALAPPDATA%\ArtenceCMMS`
3. Törölje a shortcut-okat az asztalról és Start menüből

**Figyelem**: A felhasználói adatok törlése végleges! Mentse el a fontos adatokat előtte.

## Adatok Helye

### Telepített fájlok

```
C:\Program Files\ArtenceCMMS\
├── CMMS.exe                    # Fő alkalmazás
├── templates\                  # DOCX sablonok
├── localization\               # Fordítások
└── migrations\                 # Adatbázis migrációk
```

### Felhasználói adatok

```
%LOCALAPPDATA%\ArtenceCMMS\
├── data\
│   ├── logs\                   # Naplófájlok
│   ├── files\                  # Feltöltött fájlok
│   ├── reports\                # Generált jelentések
│   └── system_backups\         # Mentések
└── generated_pdfs\             # Generált PDF/DOCX fájlok
```

**Megjegyzés**: A `%LOCALAPPDATA%` útvonal általában:
- Windows 10/11: `C:\Users\{felhasználónév}\AppData\Local\ArtenceCMMS`

## Hibaelhárítás

### Az alkalmazás nem indul el

1. **Ellenőrizze a jogosultságokat**: Futtassa adminisztrátorként
2. **Ellenőrizze a Windows Defender**: Lehet, hogy blokkolja az alkalmazást
3. **Nézd meg a naplófájlt**: `%LOCALAPPDATA%\ArtenceCMMS\data\logs\cmms.log`

### "Database connection error" hiba

1. Ellenőrizze az internet kapcsolatot
2. Ellenőrizze az adatbázis beállításokat a **Fejlesztői eszközök** menüpontban
3. Ellenőrizze, hogy a MySQL szerver elérhető-e

### Telepítés során hiba

1. **"Access denied" hiba**: Futtassa a telepítőt adminisztrátorként
2. **"File in use" hiba**: Zárja be az alkalmazást, ha fut
3. **"Disk space" hiba**: Szabadítson fel legalább 500 MB lemezterületet

### Shortcut-ok nem jelennek meg

1. Ellenőrizze a Desktop mappát
2. Ellenőrizze a Start Menu mappát: `C:\ProgramData\Microsoft\Windows\Start Menu\Programs\ArtenceCMMS`
3. Hozzon létre manuálisan shortcut-ot: Jobb klikk → Új → Parancsikon

### Verziófrissítés

1. Töltse le az új telepítőt
2. Futtassa a telepítőt (felülírja a régi verziót)
3. A felhasználói adatok megmaradnak

## További Segítség

- **Dokumentáció**: `C:\Program Files\ArtenceCMMS\docs\`
- **Naplófájlok**: `%LOCALAPPDATA%\ArtenceCMMS\data\logs\`
- **Támogatás**: Lépjen kapcsolatba a rendszergazdával

---

**Utolsó frissítés**: 2025-12-15  
**Verzió**: 1.0.0

