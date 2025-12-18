# Hogyan Hozz Létre Frissítést?

## Fontos Megértendő:

**Nem elég csak feltölteni egy nagyobb verziószámú installer exe-t!**

A rendszer a **GitHub Releases API-t** használja, és a következőket keresi:

1. ✅ **GitHub Release** létrehozása **tag-gel** (pl. `v1.0.7`)
2. ✅ Az installer **exe fájl feltöltése** a release assets-ként
3. ✅ A verzió összehasonlítás a **release tag** és a **version.txt** alapján történik

## Lépésről Lépésre Útmutató

### 1. Verzió Frissítése a Kódban

Frissítsd a `version.txt` fájlt:

```txt
1.0.7
```

**Fontos:** Ez a verzió kell legyen **kisebb**, mint amit a release tag-ben fogsz használni (vagy egyenlő, ha csak rebuild).

### 2. Telepítő Build-elése

```bash
cd CMMS_Project
python build_installer.py
```

Ez létrehozza:
- `dist/CMMS.exe`
- `dist/Updater.exe`
- `installer/ArtenceCMMS_Setup_v1.0.7.exe`

**Fontos:** A telepítő neve tartalmazza a verziót (`v1.0.7`), ami **meg kell egyezzen** a release tag-gel!

### 3. GitHub Release Létrehozása

#### Opció A: GitHub Web UI (Egyszerű)

1. Menj a GitHub repository **Releases** oldalára
2. Kattints **"Draft a new release"** gombra
3. Töltsd ki:
   - **Choose a tag:** Hozz létre új tag-et: `v1.0.7` (vagy `1.0.7`)
   - **Release title:** `v1.0.7` vagy `Version 1.0.7`
   - **Description:** Changelog (markdown formátumban)
   
   Példa changelog:
   ```markdown
   ## Changes in v1.0.7
   
   ### Bug Fixes
   - Fix update system configuration
   - Fix version comparison
   
   ### Improvements
   - Better error handling
   - Improved logging
   ```

4. **Attach binaries:** Feltöltsd az `installer/ArtenceCMMS_Setup_v1.0.7.exe` fájlt
5. Kattints **"Publish release"** gombra

#### Opció B: Git Tag + GitHub Release

```bash
# 1. Commit a változásokat
git add version.txt
git commit -m "Bump version to 1.0.7"
git push

# 2. Tag létrehozása
git tag v1.0.7
git push origin v1.0.7

# 3. GitHub Release létrehozása web UI-ban (lásd Opció A)
# Vagy használd a GitHub CLI-t:
gh release create v1.0.7 installer/ArtenceCMMS_Setup_v1.0.7.exe --title "v1.0.7" --notes "Changelog here"
```

### 4. Hogyan Működik az Update Detektálás?

A rendszer ezt a folyamatot követi:

```python
# 1. Lekéri a legújabb release-t GitHub API-ból
latest_release = GET https://api.github.com/repos/{owner}/{repo}/releases/latest

# 2. Kiolvassa a tag_name-t (pl. "v1.0.7")
tag_name = latest_release.get("tag_name")  # "v1.0.7"

# 3. Normalizálja (eltávolítja a "v" előtagot)
latest_version = "1.0.7"

# 4. Összehasonlítja az aktuális APP_VERSION-nal
current_version = "1.0.6"  # version.txt-ből

# 5. Ha latest_version > current_version:
if is_newer_version("1.0.7", "1.0.6"):  # True
    # Update elérhető!
    
# 6. Keresi az installer exe-t a release assets-ben
for asset in latest_release.get("assets"):
    if asset.get("name").endswith(".exe") and "Setup" in asset.get("name"):
        download_url = asset.get("browser_download_url")
```

### 5. Fontos Szabályok

#### ✅ DO (Tedd ezt):

- Release tag formátum: `v1.0.7` vagy `1.0.7` (a "v" opcionális)
- Telepítő név: tartalmazza a verziót (`ArtenceCMMS_Setup_v1.0.7.exe`)
- Release title és tag **egyezzen meg**
- Feltöltés: installer exe **release assets-ként**

#### ❌ DON'T (Ne tedd ezt):

- ❌ Ne tölts fel csak egy exe-t GitHub-ra release nélkül
- ❌ Ne használj más formátumot a verzióhoz (pl. `1.0.7-beta`)
- ❌ Ne felejtsd el a release tag-et
- ❌ Ne nevezd másképp az installer exe-t (kell legyen benne "Setup")

### 6. Tesztelés

#### A) Ellenőrizd a Release-t:

```bash
# Teszt script futtatása
python test_update_system.py

# Vagy manuálisan:
curl https://api.github.com/repos/{owner}/{repo}/releases/latest
```

Várható válasz:
```json
{
  "tag_name": "v1.0.7",
  "name": "v1.0.7",
  "assets": [
    {
      "name": "ArtenceCMMS_Setup_v1.0.7.exe",
      "browser_download_url": "https://github.com/.../releases/download/v1.0.7/ArtenceCMMS_Setup_v1.0.7.exe"
    }
  ]
}
```

#### B) Teszteld az Alkalmazásban:

1. Indítsd el a CMMS alkalmazást (verzió: 1.0.6)
2. Menj Settings → Updates
3. Kattints "Frissítés ellenőrzése"
4. **Várható:** "Új verzió elérhető: v1.0.7" üzenet és update dialog

### 7. Példa Teljes Workflow

```bash
# 1. Verzió frissítése
echo "1.0.7" > version.txt

# 2. Commit
git add version.txt
git commit -m "Bump version to 1.0.7"
git push

# 3. Build
python build_installer.py

# 4. Tag
git tag v1.0.7
git push origin v1.0.7

# 5. GitHub Release létrehozása (web UI vagy CLI)
# - Tag: v1.0.7
# - Title: v1.0.7
# - Upload: installer/ArtenceCMMS_Setup_v1.0.7.exe
# - Notes: Changelog

# 6. Tesztelés
# - Alkalmazásban: Settings → Check for updates
# - Ellenőrizd, hogy megjelenik-e az update dialog
```

## Gyakori Hibák és Megoldások

### ❌ "No releases found on GitHub"

**Ok:** Nincs release a repository-ban vagy rossz tag formátum

**Megoldás:**
- Ellenőrizd, hogy van-e release a GitHub Releases oldalon
- Ellenőrizd, hogy a tag helyes-e (`v1.0.7` vagy `1.0.7`)

### ❌ "No download URL found in release assets"

**Ok:** Nincs `.exe` fájl a release assets-ben, vagy nem tartalmazza a "Setup" szót

**Megoldás:**
- Feltöltsd az installer exe-t a release assets-ként
- Ellenőrizd, hogy a fájlnév tartalmazza-e a "Setup" szót (pl. `ArtenceCMMS_Setup_v1.0.7.exe`)

### ❌ "Application is up to date" (de tudod, hogy van új verzió)

**Ok:** 
1. A release tag verziója nem nagyobb, mint a jelenlegi `version.txt` verzió
2. Vagy a verzió összehasonlítás hibás

**Megoldás:**
- Ellenőrizd a release tag-et: `v1.0.7` → `1.0.7`
- Ellenőrizd a `version.txt`-t: `1.0.6`
- Ha `1.0.7 > 1.0.6`, akkor működnie kell

### ❌ Verzió összehasonlítás nem működik

**Tesztelés:**
```python
from utils.version_utils import is_newer_version

print(is_newer_version("1.0.7", "1.0.6"))  # True kell legyen
print(is_newer_version("1.0.6", "1.0.7"))  # False kell legyen
print(is_newer_version("1.0.6", "1.0.6"))  # False kell legyen
```

## Automatikus Release Létrehozás (GitHub Actions)

Ha GitHub Actions-t használsz, beállíthatod, hogy automatikusan:
1. Tag push esetén build-elje a telepítőt
2. Létrehozza a release-t
3. Feltöltse az installer exe-t

Lásd: `.github/workflows/release.yml` (ha van)

## Összefoglalás

**Egyszerűen:**

1. ✅ Frissítsd a `version.txt`-t
2. ✅ Build-eld a telepítőt
3. ✅ Hozz létre **GitHub Release-t tag-gel** (`v1.0.7`)
4. ✅ Feltöltsd az installer exe-t a release assets-ként
5. ✅ Teszteld az alkalmazásban

**Az update automatikusan észlelődik, ha:**
- A release tag verziója **nagyobb**, mint a jelenlegi `version.txt` verzió
- Az installer exe **feltöltve** van a release assets-ként
- A GitHub konfiguráció **helyesen** be van állítva az alkalmazásban

