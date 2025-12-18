# Automatikus Frissítési Rendszer Dokumentáció

## Áttekintés

Az Artence CMMS rendszer automatikus frissítési mechanizmust tartalmaz, amely lehetővé teszi a felhasználók számára, hogy egyszerűen és biztonságosan frissítsék az alkalmazást a legújabb verzióra. A rendszer GitHub Releases API-t használ a frissítések ellenőrzéséhez és letöltéséhez.

## Architektúra

### Komponensek

A frissítési rendszer három fő komponensből áll:

1. **CMMS.exe** - Fő alkalmazás
   - Verzió ellenőrzés kezdeményezése
   - Frissítési értesítések megjelenítése
   - Updater.exe indítása

2. **Updater.exe** - Frissítő alkalmazás (standalone)
   - CMMS.exe bezárása
   - Új telepítő letöltése GitHub-ról
   - Telepítés futtatása
   - CMMS.exe újraindítása

3. **GitHub Releases** - Frissítési forrás
   - Verzió információ tárolása
   - Telepítő fájlok elérhetősége
   - Changelog és release notes

### Folyamat Diagram

```
[Felhasználó] → [Settings → Frissítés ellenőrzése]
                      ↓
              [Update Service]
                      ↓
         [GitHub Releases API]
                      ↓
              [Új verzió?]
                 ↙      ↘
              Igen      Nem
               ↓         ↓
    [Update Dialog]  [Naprakész]
               ↓
    [Frissítés most?]
         ↙      ↘
       Igen     Nem
        ↓        ↓
[Updater.exe] [Később]
    indítása
        ↓
[CMMS.exe bezárása]
        ↓
[Telepítő letöltése]
        ↓
[Telepítés futtatása]
        ↓
[CMMS.exe újraindítása]
```

## Használat

### Felhasználói Szemszögből

#### 1. Frissítés Ellenőrzése

1. Nyissa meg az alkalmazást
2. Menjen a **Beállítások** menüpontba
3. Görgessen le a **Frissítések / Updates** szekcióhoz
4. Kattintson a **"Frissítés ellenőrzése / Check for updates"** gombra

#### 2. Frissítési Dialógus

Ha új verzió elérhető, megjelenik egy dialógus, amely tartalmazza:

- **Verziószám**: Az új verzió száma (pl. v1.0.1)
- **Kiadás dátuma**: A release dátum
- **Changelog**: A változások listája
- **Kritikus frissítés jelző**: Ha a frissítés kritikus

**Lehetőségek**:
- **Frissítés most**: Azonnal elindítja a frissítési folyamatot
- **Később**: Bezárja a dialógust, később lehet újra ellenőrizni
- **Verzió kihagyása**: Kihagyja ezt a verziót (csak nem kritikus frissítéseknél)

#### 3. Frissítési Folyamat

A "Frissítés most" gombra kattintva:

1. Az alkalmazás bezárul
2. Az **Updater.exe** elindul
3. A telepítő letöltése GitHub-ról
4. A telepítő automatikus futtatása (silent mode)
5. Az alkalmazás újraindítása az új verzióval

**Megjegyzés**: A frissítés során az összes felhasználói adat megmarad (`%LOCALAPPDATA%\ArtenceCMMS\`).

### Automatikus Frissítés Ellenőrzés

A rendszer támogatja az automatikus frissítés ellenőrzést:

1. **Beállítások**:
   - **Automatikus frissítés ellenőrzés**: Bekapcsolható/kikapcsolható
   - **Ellenőrzési gyakoriság**:
     - **Indításkor**: Minden alkalmazásindításkor
     - **Naponta**: Egyszer naponta
     - **Hetente**: Egyszer hetente

2. **Működés**:
   - Ha automatikus ellenőrzés be van kapcsolva, az alkalmazás a beállított gyakorisággal ellenőrzi a frissítéseket
   - Ha új verzió található, értesítést jelenít meg
   - A felhasználó dönthet a frissítésről

## Fejlesztői Szemszögből

### Konfiguráció

#### GitHub Repository Beállítása

A frissítési rendszer működéséhez be kell állítani a GitHub repository információkat:

**1. Environment változók** (ajánlott):
```bash
GITHUB_OWNER=your-username
GITHUB_REPO=Artence_CMMS
```

**2. Vagy közvetlenül az `app_config.py`-ban**:
```python
GITHUB_OWNER = "your-username"
GITHUB_REPO = "Artence_CMMS"
```

#### Verziókezelés

A verziószám a `version.txt` fájlból olvasódik:
```
1.0.0
```

**Semantic Versioning** formátumot használ:
- `MAJOR.MINOR.PATCH` (pl. 1.0.0)
- `MAJOR`: Nagy változások, nem kompatibilis API változások
- `MINOR`: Új funkciók, visszafelé kompatibilis
- `PATCH`: Bug javítások, visszafelé kompatibilis

### Release Létrehozása

#### 1. Verzió Frissítése

1. Frissítse a `version.txt` fájlt:
   ```
   1.0.1
   ```

2. Commit és push:
   ```bash
   git add version.txt
   git commit -m "Bump version to 1.0.1"
   git push
   ```

#### 2. Release Tag Létrehozása

1. Hozzon létre egy tag-et:
   ```bash
   git tag v1.0.1
   git push origin v1.0.1
   ```

2. A GitHub Actions automatikusan:
   - Build-eli a telepítőt
   - Létrehozza a Release-t
   - Feltölti a telepítő fájlt

#### 3. Manuális Release (ha GitHub Actions nincs beállítva)

1. Build futtatása:
   ```bash
   cd CMMS_Project
   python build_installer.py
   ```

2. GitHub Release létrehozása:
   - Menjen a GitHub repository **Releases** oldalára
   - Kattintson **"Draft a new release"**
   - Tag: `v1.0.1`
   - Title: `v1.0.1`
   - Description: Changelog (markdown formátumban)
   - Feltöltés: `installer/ArtenceCMMS_Setup_v1.0.1.exe`

### Release Notes / Changelog

A release notes markdown formátumban írható:

```markdown
## Changes in v1.0.1

### New Features
- Új funkció 1
- Új funkció 2

### Bug Fixes
- Bug javítás 1
- Bug javítás 2

### Improvements
- Teljesítmény javítás
- UI fejlesztés
```

**Kritikus frissítés jelzése**: Ha a changelog tartalmazza a "critical" szót, a frissítés kritikusnak lesz jelölve.

### Build Folyamat

#### Telepítő Build

A `build_installer.py` script:

1. **Előfeltételek ellenőrzése**:
   - PyInstaller telepítve?
   - Inno Setup telepítve?
   - Szükséges fájlok léteznek?

2. **CMMS.exe build**:
   - PyInstaller futtatása `build.spec` fájllal
   - Output: `dist/CMMS.exe`

3. **Updater.exe build**:
   - PyInstaller futtatása `updater.spec` fájllal
   - Output: `dist/Updater.exe`

4. **Telepítő build**:
   - Inno Setup futtatása `installer.iss` fájllal
   - Output: `installer/ArtenceCMMS_Setup_v{version}.exe`

#### GitHub Actions Workflow

A `.github/workflows/release.yml` workflow:

- **Trigger**: Version tag push (pl. `v1.0.1`)
- **Folyamat**:
  1. Code checkout
  2. Python környezet beállítása
  3. Függőségek telepítése
  4. Inno Setup telepítése
  5. Build futtatása
  6. Release létrehozása és fájl feltöltése

## Technikai Részletek

### Update Service (`services/update_service.py`)

**Fő funkciók**:

- `check_for_updates(current_version)`: GitHub API lekérdezése és verzió összehasonlítás
- `get_release_notes(version)`: Release notes lekérése

**API Endpoint**:
```
https://api.github.com/repos/{owner}/{repo}/releases/latest
```

**Válasz formátum**:
```json
{
  "tag_name": "v1.0.1",
  "published_at": "2025-12-15T10:00:00Z",
  "body": "## Changes\n- Bug fixes",
  "assets": [
    {
      "name": "ArtenceCMMS_Setup_v1.0.1.exe",
      "browser_download_url": "https://github.com/.../releases/download/v1.0.1/ArtenceCMMS_Setup_v1.0.1.exe"
    }
  ]
}
```

### Updater.exe (`updater.py`)

**Parancssori paraméterek**:
```
Updater.exe --update --version=1.0.1 --url=https://... --restart
```

**Folyamat**:

1. **CMMS.exe bezárása**:
   - Graceful shutdown (10 másodperc timeout)
   - Force kill ha szükséges

2. **Telepítő letöltése**:
   - Temp mappa: `%TEMP%\ArtenceCMMS_Update\`
   - Progress tracking
   - SHA256 checksum ellenőrzés (jövőbeli fejlesztés)

3. **Telepítés**:
   - Silent mode: `/SILENT`
   - Ne indítsa újra automatikusan: `/RESTARTAPPLICATIONS=0`

4. **Újraindítás**:
   - CMMS.exe indítása sikeres telepítés után

### Verzió Összehasonlítás (`utils/version_utils.py`)

**Funkciók**:
- `parse_version(version_string)`: Verzió string feldolgozása
- `compare_versions(v1, v2)`: Verziók összehasonlítása
- `is_newer_version(latest, current)`: Újabb verzió ellenőrzése

**Példa**:
```python
from utils.version_utils import is_newer_version

if is_newer_version("1.0.1", "1.0.0"):
    print("Új verzió elérhető!")
```

## Beállítások Tárolása

A frissítési beállítások az adatbázisban tárolódnak (`AppSetting` modell):

- `auto_update_check`: `"true"` vagy `"false"`
- `update_check_frequency`: `"startup"`, `"daily"`, vagy `"weekly"`
- `last_update_check`: ISO formátumú dátum string
- `skip_version`: Kihagyott verziószám

## Hibaelhárítás

### Frissítés nem működik

**Probléma**: "GitHub repository nincs beállítva"

**Megoldás**:
1. Ellenőrizze a `GITHUB_OWNER` és `GITHUB_REPO` environment változókat
2. Vagy állítsa be közvetlenül az `app_config.py`-ban

**Probléma**: "Updater.exe nem található"

**Megoldás**:
1. Ellenőrizze, hogy az `Updater.exe` telepítve van-e (`C:\Program Files\ArtenceCMMS\Updater.exe`)
2. Ha nincs, futtassa újra a telepítőt

**Probléma**: "Hálózati hiba letöltés során"

**Megoldás**:
1. Ellenőrizze az internet kapcsolatot
2. Ellenőrizze, hogy a GitHub elérhető-e
3. Próbálja újra később

### Telepítési hibák

**Probléma**: "CMMS.exe nem zárható be"

**Megoldás**:
1. Zárja be manuálisan az alkalmazást
2. Ellenőrizze a Task Manager-ben, hogy fut-e még
3. Indítsa újra a frissítést

**Probléma**: "Telepítés sikertelen"

**Megoldás**:
1. Ellenőrizze a log fájlt: `%LOCALAPPDATA%\ArtenceCMMS\data\logs\updater.log`
2. Futtassa manuálisan a telepítőt adminisztrátorként
3. Ha továbbra sem működik, lépjen kapcsolatba a támogatással

## Biztonsági Megfontolások

### Jelenlegi Implementáció

- **HTTPS**: Minden letöltés HTTPS-en keresztül történik
- **GitHub API**: Hivatalos GitHub API használata
- **Certificate Validation**: Automatikus SSL tanúsítvány ellenőrzés

### Jövőbeli Fejlesztések

- **Digitális aláírás**: Code signing certificate telepítő és Updater.exe aláírásához
- **SHA256 Checksum**: Telepítő fájl integritás ellenőrzése
- **Rollback mechanizmus**: Automatikus visszaállás sikertelen telepítés esetén

## Gyakori Kérdések (FAQ)

### Mi történik a felhasználói adatokkal frissítéskor?

**Válasz**: Minden felhasználói adat megmarad. A frissítés csak az alkalmazás fájlokat cseréli le (`C:\Program Files\ArtenceCMMS\`), de a felhasználói adatok (`%LOCALAPPDATA%\ArtenceCMMS\`) érintetlenek maradnak.

### Milyen gyakran ellenőrizzen frissítést?

**Válasz**: 
- **Indításkor**: Ha gyakran használja az alkalmazást
- **Naponta**: Ha ritkábban használja
- **Hetente**: Ha csak időnként használja

### Mi a különbség a kritikus és normál frissítés között?

**Válasz**: 
- **Kritikus frissítés**: Biztonsági javítások vagy kritikus bug javítások. Nem lehet kihagyni.
- **Normál frissítés**: Új funkciók vagy kisebb javítások. Kihagyható.

### Mi történik, ha kihagyok egy verziót?

**Válasz**: A kihagyott verzió nem jelenik meg újra az értesítésekben. Azonban a következő újabb verzió továbbra is megjelenik.

### Hogyan állíthatom vissza egy korábbi verzióra?

**Válasz**: 
1. Töltse le a korábbi verzió telepítőjét a GitHub Releases oldalról
2. Futtassa a telepítőt (felülírja az aktuális verziót)
3. A felhasználói adatok megmaradnak

## További Információk

- **GitHub Repository**: [GitHub Releases](https://github.com/{owner}/{repo}/releases)
- **Log fájlok**: `%LOCALAPPDATA%\ArtenceCMMS\data\logs\updater.log`
- **Támogatás**: Lépjen kapcsolatba a rendszergazdával

---

**Utolsó frissítés**: 2025-12-15  
**Verzió**: 1.0.0




