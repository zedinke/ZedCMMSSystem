# Telepítési Gyakori Kérdések (FAQ)

## Indító Fájlok és Shortcut-ok

### Létrejön-e automatikusan az indító fájl?

**Igen!** A telepítő automatikusan létrehozza:

1. **CMMS.exe** - Ez maga az "indító fájl"
   - Helye: `C:\Program Files\ArtenceCMMS\CMMS.exe`
   - Közvetlenül futtatható (dupla kattintás)
   - Önállóan működik, nincs szükség külső fájlokra

2. **Start Menu shortcut** - Automatikusan létrejön
   - Helye: `C:\ProgramData\Microsoft\Windows\Start Menu\Programs\ArtenceCMMS\Artence CMMS.lnk`
   - Közvetlenül a `CMMS.exe`-re mutat
   - Mindig létrejön, nem opcionális

3. **Desktop shortcut** - Opcionális
   - Helye: `C:\Users\{felhasználó}\Desktop\Artence CMMS.lnk`
   - A telepítés során checkbox-szal választható
   - Közvetlenül a `CMMS.exe`-re mutat

### Hogyan indíthatom el az alkalmazást?

**3 módon**:

1. **Desktop shortcut** (ha létrejött):
   - Dupla kattintás az "Artence CMMS" ikonra az asztalon

2. **Start Menu**:
   - Start gomb → "Artence CMMS" mappa → "Artence CMMS"

3. **Közvetlenül a .exe fájl**:
   - Navigáljon: `C:\Program Files\ArtenceCMMS\`
   - Dupla kattintás a `CMMS.exe` fájlra

### Van-e külön launcher.exe fájl?

**Nem**. A `CMMS.exe` maga az indító fájl. Nincs szükség külön launcher.exe-re, mert:

- A `CMMS.exe` tartalmazza a Python interpreter-t
- Önállóan működik
- Közvetlenül futtatható

### Mi a különbség a CMMS.exe és az Updater.exe között?

- **CMMS.exe**: Fő alkalmazás - ez az, amit minden nap használsz
- **Updater.exe**: Frissítő alkalmazás - csak frissítéskor fut le automatikusan

**Nem kell manuálisan futtatni az Updater.exe-t** - a frissítési rendszer automatikusan kezeli.

## Függőségek és Előfeltételek

### Szükséges-e Python telepítés?

**Nem!** A telepítő tartalmazza az összes szükséges függőséget:

- ✅ Python interpreter (beágyazva a CMMS.exe-be)
- ✅ Összes Python modul (Flet, SQLAlchemy, Pandas, stb.)
- ✅ Rendszerkönyvtárak és DLL-ek

**Nincs szükség**:
- ❌ Python telepítésre
- ❌ pip install-ra
- ❌ requirements.txt telepítésre

### Mi történik, ha nincs internet a célgépen?

- ✅ **Telepítés**: Működik internet nélkül is
- ✅ **Alkalmazás indítás**: Működik internet nélkül is
- ⚠️ **Adatbázis kapcsolat**: Internet szükséges (MySQL szerver távoli)

**Megjegyzés**: Ha a MySQL szerver helyi (localhost), akkor internet nélkül is működik.

## Telepítés és Eltávolítás

### Hol kerülnek a fájlok?

**Telepített fájlok** (nem módosítható):
```
C:\Program Files\ArtenceCMMS\
├── CMMS.exe
├── Updater.exe
├── templates\
├── localization\
└── migrations\
```

**Felhasználói adatok** (módosítható):
```
%LOCALAPPDATA%\ArtenceCMMS\
├── data\
│   ├── logs\
│   ├── files\
│   ├── reports\
│   └── system_backups\
└── generated_pdfs\
```

### Mi történik az adatokkal frissítéskor?

**Minden felhasználói adat megmarad**:
- Log fájlok
- Feltöltött fájlok
- Generált jelentések
- Mentések
- Beállítások

Csak az alkalmazás fájlok frissülnek (`C:\Program Files\ArtenceCMMS\`).

### Mi történik az adatokkal eltávolításkor?

**Alapértelmezetten**:
- Az alkalmazás fájlok törlődnek
- A felhasználói adatok megmaradnak (`%LOCALAPPDATA%\ArtenceCMMS\`)

**Ha teljes eltávolítást szeretne**:
- Manuálisan törölje a `%LOCALAPPDATA%\ArtenceCMMS\` mappát

## Hibaelhárítás

### Az alkalmazás nem indul el

**Lehetséges okok**:
1. **Windows Defender blokkolja**: 
   - Vezérlőpult → Windows Defender → Kivételek hozzáadása
   - Vagy: "Run anyway" a figyelmeztetésnél

2. **Jogosultság hiány**:
   - Futtassa adminisztrátorként (jobb klikk → "Futtatás rendszergazdaként")

3. **Fájl sérülés**:
   - Telepítse újra az alkalmazást

### Shortcut-ok nem jelennek meg

**Megoldás**:
1. Ellenőrizze a Desktop mappát
2. Ellenőrizze a Start Menu mappát: `C:\ProgramData\Microsoft\Windows\Start Menu\Programs\ArtenceCMMS\`
3. Hozzon létre manuálisan shortcut-ot:
   - Jobb klikk a `CMMS.exe`-re → "Küldés ide" → "Asztal (shortcut létrehozása)"

### "Updater.exe nem található" hiba

**Ok**: Az Updater.exe nem lett telepítve vagy törölve lett

**Megoldás**:
1. Telepítse újra az alkalmazást
2. Vagy másolja manuálisan: `dist\Updater.exe` → `C:\Program Files\ArtenceCMMS\`

## További Kérdések

### Módosíthatom a telepítési útvonalat?

**Igen**, a telepítés során választható másik útvonal. Azonban:
- Ajánlott: `C:\Program Files\ArtenceCMMS\` (alapértelmezett)
- Alternatíva: `C:\Program Files (x86)\ArtenceCMMS\` vagy egyedi útvonal

### Telepíthetem több gépre is?

**Igen**, ugyanazt a telepítő fájlt használhatja több gépen is. Minden gép önállóan működik.

### Működik offline módban?

**Igen**, ha:
- A MySQL szerver helyi (localhost)
- Vagy nincs szükség adatbázis kapcsolatra

**Nem**, ha:
- Távoli MySQL szerverhez kell csatlakozni (internet szükséges)

---

**Utolsó frissítés**: 2025-12-15




