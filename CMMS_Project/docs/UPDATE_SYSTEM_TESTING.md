# Update System Testing Guide

## Automatikus Tesztelés

Futtasd a teszt scriptet:

```bash
cd CMMS_Project
python test_update_system.py
```

A teszt ellenőrzi:
1. GitHub konfiguráció betöltését
2. Verzió összehasonlítás működését
3. Update ellenőrzés működését (ha GitHub be van állítva)
4. Update beállítások betöltését
5. Updater.exe elérési útvonalak keresését

### Teszt Eredmények (2025-12-18)

```
PASS: Version Utilities - ✓ Minden verzió összehasonlítás helyesen működik
PASS: Update Settings - ✓ Beállítások betöltése működik
PASS: Updater.exe Paths - ✓ Updater.exe megtalálható: dist/Updater.exe

FAIL: GitHub Configuration - ✗ GitHub owner nincs beállítva (ez normális, első futtatáskor)
SKIP: Update Check - GitHub konfiguráció nélkül nem futtatható
```

## Manuális Tesztelés

### 1. GitHub Konfiguráció Beállítása

#### Az alkalmazáson belül:
1. Indítsd el a CMMS alkalmazást
2. Menj a **Settings / Beállítások** menüpontba
3. Görgess le a **Frissítések / Updates** szekcióhoz
4. Add meg a **GitHub Owner** mezőben a GitHub felhasználóneved vagy szervezet nevet
5. Add meg a **GitHub Repository** mezőben a repository nevét (pl. `Artence_CMMS`)
6. Kattints a **Mentés / Save** gombra

#### Environment változókkal (fejlesztéshez):
```bash
# Windows PowerShell
$env:GITHUB_OWNER = "your-username"
$env:GITHUB_REPO = "Artence_CMMS"

# Windows CMD
set GITHUB_OWNER=your-username
set GITHUB_REPO=Artence_CMMS
```

### 2. Manuális Frissítés Ellenőrzés Tesztelése

1. Nyisd meg a **Settings / Beállítások** oldalt
2. Görgess le a **Frissítések / Updates** szekcióhoz
3. Kattints a **"Frissítés ellenőrzése / Check for updates"** gombra
4. Várt eredmények:
   - Ha GitHub nincs beállítva: "GitHub repository nincs beállítva / GitHub repository not configured"
   - Ha GitHub be van állítva, de nincs új verzió: "Az alkalmazás naprakész / Application is up to date"
   - Ha új verzió elérhető: Update dialog megjelenik

### 3. Automatikus Frissítés Ellenőrzés Tesztelése

#### Indításkori ellenőrzés:
1. Beállításokban engedélyezd az **"Automatikus frissítés ellenőrzés / Auto check for updates"** opciót
2. Állítsd be a gyakoriságot **"Indításkor / On startup"** értékre
3. Zárj be és indítsd újra az alkalmazást
4. Bejelentkezés után automatikusan ellenőrzi a frissítéseket
5. Ha új verzió elérhető, megjelenik az update dialog

#### Napi/Heti ellenőrzés:
1. Beállításokban engedélyezd az automatikus ellenőrzést
2. Állítsd be a gyakoriságot **"Naponta / Daily"** vagy **"Hetente / Weekly"** értékre
3. Az első ellenőrzés azonnal megtörténik
4. A következő ellenőrzés csak a beállított időszak után

### 4. Verzió Kihagyás Tesztelése

1. Ha új verzió elérhető, az update dialogban kattints a **"Skip This Version"** gombra
2. A verzió kihagyásra kerül
3. Újraindítás után ugyanez a verzió nem jelenik meg újra
4. Egy újabb verzió esetén újra megjelenik az értesítés

### 5. Updater.exe Tesztelése

#### Elérési útvonal ellenőrzés:
A teszt script ellenőrzi a következő helyeket:
- `dist/Updater.exe` (development)
- `C:\Program Files\ArtenceCMMS\Updater.exe` (installed)
- `%LOCALAPPDATA%\ArtenceCMMS\Updater.exe` (portable)

#### Frissítés folyamat tesztelése (Óvatosan!):
1. Először teszteld egy test repository-ban
2. Hozz létre egy új release-t GitHub-on
3. Az update dialogban kattints **"Update Now"** gombra
4. Várt eredmény:
   - CMMS.exe bezáródik
   - Updater.exe elindul
   - Telepítő letöltődik
   - Telepítés lefut
   - CMMS.exe újraindul

## Tipikus Problémák és Megoldások

### Probléma: "GitHub repository nincs beállítva"

**Megoldás:**
1. Beállítások → Frissítések → Add meg a GitHub owner-t és repo-t
2. Vagy állítsd be environment változókkal

### Probléma: "Updater.exe nem található"

**Megoldás:**
1. Ellenőrizd, hogy a `dist/Updater.exe` létezik-e
2. Ha nincs, futtasd: `python build_installer.py` (buildeli az Updater.exe-t is)
3. Telepítés után ellenőrizd: `C:\Program Files\ArtenceCMMS\Updater.exe`

### Probléma: "No releases found on GitHub"

**Megoldás:**
1. Ellenőrizd, hogy a GitHub repository-ban van-e release
2. Ellenőrizd, hogy a repository neve helyes-e
3. Ellenőrizd, hogy a repository public-e (vagy van-e hozzáférésed)

### Probléma: Update dialog nem jelenik meg automatikusan

**Megoldás:**
1. Ellenőrizd, hogy be van-e kapcsolva az automatikus ellenőrzés
2. Ellenőrizd a log fájlt: `%LOCALAPPDATA%\ArtenceCMMS\data\logs\cmms.log`
3. Keress rá: "Starting automatic update check" vagy "GitHub repository not configured"

## Log Fájlok Ellenőrzése

A frissítés rendszer részletes logolást végez:

**Log fájl helye:**
- Development: `CMMS_Project/data/logs/cmms.log`
- Installed: `%LOCALAPPDATA%\ArtenceCMMS\data\logs\cmms.log`
- Updater log: `%LOCALAPPDATA%\ArtenceCMMS\data\logs\updater.log`

**Keresendő log üzenetek:**
```
INFO - Update service initialized with GitHub: owner/repo
INFO - Checking for updates (current version: X.X.X, repo: owner/repo)
INFO - Latest version on GitHub: X.X.X
INFO - Update available: X.X.X
INFO - Starting automatic update check...
```

## Teszt Checklist

- [ ] GitHub konfiguráció beállítva (owner + repo)
- [ ] Manuális frissítés ellenőrzés működik
- [ ] Verzió összehasonlítás helyes
- [ ] Automatikus ellenőrzés indításkor működik
- [ ] Automatikus ellenőrzés napi/heti beállítás működik
- [ ] Verzió kihagyás működik
- [ ] Update dialog megjelenik új verzió esetén
- [ ] Updater.exe megtalálható
- [ ] Frissítési folyamat működik (ha teszt release elérhető)
- [ ] Log fájlok tartalmazzák a szükséges információkat

## Jövőbeli Fejlesztések

- [ ] Unit tesztek az update_service.py-hoz
- [ ] Integration tesztek a GitHub API-val
- [ ] Mock tesztek a GitHub API nélküli teszteléshez
- [ ] End-to-end tesztek a teljes frissítési folyamathoz

