# 📱 Android CMMS App - Valós Telefon Tesztelési Útmutató

## ✅ Gyors Indítás - Telefonra Telepítés

### 1. ELŐFELTÉTELEK
- ✅ Android telefon (API 26+, Android 8.0+)
- ✅ USB kábel (MTP/ADB támogatással)
- ✅ Windows PC (Android SDK Tools)
- ✅ USB debugging engedélyezve a telefonon

### 2. USB DEBUGGING ENGEDÉLYEZÉSE

**Android telefonon:**
1. Menj: `Beállítások > Rólunk`
2. Keresd meg: `Build szám`
3. Kattints 7x-et a Build számon
4. Engedélyezve van a Developer Mode
5. Menj: `Beállítások > Fejlesztői beállítások`
6. Kapcsold be: `USB Debugging`
7. Kattints `OK` az engedélyezési dialóguson

---

### 3. TELEFON CSATLAKOZTATÁSA

```batch
# 1. Csatlakoztasd az USB kábellel a PC-hez
# 2. Ellenőrizd a csatlakozást:

cd E:\Artence_CMMS\AndroidApp
adb devices
```

**Elvárt kimenet:**
```
List of attached devices
emulator-5554          device
R58N7071234            device
```

Ha a telefon **`device`** státuszban van → OK! ✅

---

### 4. APK TELEPÍTÉSE TELEFONRA

```batch
# Option 1: Android Studio Build
cd E:\Artence_CMMS\AndroidApp
gradlew.bat installDebug

# Option 2: Közvetlen APK telepítése
adb install app\build\outputs\apk\debug\app-debug.apk

# Option 3: APK másolása és manuális telepítés
# Másold az APK-t: app\build\outputs\apk\debug\app-debug.apk
# Helyezd a telefon Downloads mappájába
# Nyisd meg és telepítsd
```

**Telepítés közben:**
```
Installing APK 'app-debug.apk' on 'R58N7071234' for :app:debug
Installed on 1 device.
```

---

### 5. APP INDÍTÁSA

**A telefonon:**
1. Görgess a Downloaded/Installed appshoz
2. Keresd: **CMMS**
3. Kattints az ikonra → **App elindul**

---

## 🧪 TELJES TESZT FORGATÓKÖNYV - VALÓS TELEFON

### LOGIN TESZT

**Tesztesetek:**

#### TC-001: Sikeres Login
```
1. Megnyitod az appot
   ✅ Login screen jelenik meg
   
2. Megadod az adatokat:
   - Username: a.geleta
   - Password: Gele007ta
   
3. Megnyomod: LOGIN gomb
   ✅ Loading spinner 3 mp-ig
   ✅ Sikeres bejelentkezés → Dashboard
   
Результат: ✅ PASS
```

#### TC-002: Hibás Jelszó
```
1. Username: a.geleta
2. Password: hibas1234
3. LOGIN megnyomása
   ✅ Error toast/snackbar: "Invalid credentials"
   
Результат: ✅ PASS
```

#### TC-003: Test Server Gomb
```
1. Login screen
2. Görgess le → "Test Server" gomb
3. Megnyomása
   ✅ Dialógus megjelenik:
      - DNS Resolution
      - Server Connectivity
      - Login Endpoint Test
   
Результат: ✅ PASS vagy ❌ FAIL (backend elérhetőség)
```

---

### DASHBOARD TESZTEK

#### TC-004: Dashboard Betöltés
```
1. Sikeres login után
   ✅ Dashboard automatikus betöltődik
   ✅ Top AppBar: "Felhasználó neve" jelenik meg
   
2. Metrika Cards:
   ✅ Total Assets szám
   ✅ Total Worksheets szám
   ✅ Pending PM Tasks
   ✅ Low Stock Items
   
Результат: ✅ PASS
```

#### TC-005: SwipeRefresh
```
1. Dashboard nyitva
2. Lehúzod felülről (SwipeRefresh)
   ✅ Circular progress indicator
   ✅ Adatok frissülnek
   
Результат: ✅ PASS
```

#### TC-006: Bottom Navigation
```
1. Dashboard
2. Kattintasz az ikonokra:
   ✅ Dashboard ikont
   ✅ Assets ikont
   ✅ Worksheets ikont
   ✅ Machines ikont
   ✅ Inventory ikont
   ✅ PM ikont
   ✅ Reports ikont
   ✅ Settings ikont
   
3. Minden screen betöltődik?
   
Результат: ✅ PASS
```

---

### ASSETS MANAGEMENT TESZTEK

#### TC-007: Assets Lista
```
1. Bottom Nav → Assets
   ✅ LazyColumn lista jelenik meg
   ✅ Asset cards: név, típus, státusz látható
   
2. Scroll down
   ✅ Több asset betöltődik
   
3. Pull to refresh
   ✅ Lista frissül
   
Результат: ✅ PASS
```

#### TC-008: Asset Létrehozás
```
1. Assets screen
2. FAB (+ gomb) → Create Asset
   ✅ Form megjelenik
   
3. Kitöltés:
   - Name: "Test Machine"
   - Type: Machine
   - Status: OPERATIONAL
   - Criticality: HIGH
   
4. Save gomb
   ✅ Success toast: "Asset created"
   ✅ Lista frissül, új asset megjelenik
   
Результат: ✅ PASS
```

#### TC-009: Asset Módosítás
```
1. Asset listán
2. Kattints egy assetre
   ✅ Detail screen megnyílódik
   
3. Edit gomb
   ✅ Form megjelenik az aktuális adatokkal
   
4. Módosítsd az adatokat:
   - Status: MAINTENANCE
   
5. Save
   ✅ Success toast
   ✅ Lista frissül
   
Результат: ✅ PASS
```

#### TC-010: Asset Törlés
```
1. Asset detail
2. Delete gomb
   ✅ Confirmation AlertDialog
   
3. Confirm
   ✅ Success toast
   ✅ Vissza a listára
   ✅ Asset eltűnt
   
Результат: ✅ PASS
```

#### TC-011: Asset Szűrés
```
1. Assets lista
2. Filter icon
   ✅ FilterChip-ek vagy Dialog megjelenik
   
3. Válassz: Status = MAINTENANCE
   ✅ Lista csak MAINTENANCE asset-eket mutat
   
4. Clear filters
   ✅ Összes asset megjelenik
   
Результат: ✅ PASS
```

---

### WORKSHEETS TESZTEK

#### TC-012: Worksheet Lista
```
1. Bottom Nav → Worksheets
   ✅ Card layout lista megjelenik
   ✅ Minden card mutatja:
      - Title
      - Status (chip-ként)
      - Priority (icon+color)
      - Assigned user
      
Результат: ✅ PASS
```

#### TC-013: Worksheet Státusz Workflow
```
1. Worksheet detail megnyitása
2. Status chip-re kattintás
   ✅ Status picker dialog
   
3. Státusz váltogatása:
   OPEN → IN_PROGRESS → COMPLETED → CLOSED
   
4. Mentés után
   ✅ Status megváltozik
   ✅ Lista frissül
   
Результат: ✅ PASS
```

#### TC-014: Worksheet Létrehozás
```
1. Worksheets screen
2. FAB → Create Worksheet
   ✅ Form megjelenik
   
3. Kitöltés:
   - Title: "Test Maintenance"
   - Status: OPEN
   - Priority: HIGH
   - Assign To: (user kiválasztása)
   
4. Save
   ✅ Success toast
   ✅ Új worksheet megjelenik a listán
   
Результат: ✅ PASS
```

---

### INVENTORY TESZTEK

#### TC-015: Low Stock Alert
```
1. Bottom Nav → Inventory
   ✅ Lista megjelenik
   
2. Keress low stock items
   ✅ Piros ikonnal vagy háttérrel kiemelve
   ✅ Például: qty < min_stock_level
   
Результат: ✅ PASS
```

#### TC-016: Inventory CRUD
```
1. Create Inventory item
   ✅ Form: Name, Part Number, Quantity, Min Stock Level
   
2. Save
   ✅ Lista frissül
   
3. Edit item
   ✅ Mennyiség módosítása
   
4. Delete item
   ✅ Confirmation → Success
   
Результат: ✅ PASS
```

---

### PM (PREVENTIVE MAINTENANCE) TESZTEK

#### TC-017: PM Tasks Lista
```
1. Bottom Nav → PM
   ✅ Due date szerint rendezett lista
   
2. Overdue tasks
   ✅ Piros szín
   
3. Today tasks
   ✅ Sárga szín
   
4. Future tasks
   ✅ Normál szín
   
Результат: ✅ PASS
```

#### TC-018: PM Task Teljesítése
```
1. PM task részletes nézet
2. "Complete" gomb
   ✅ Dialog: notes mező + OK
   
3. Notes megadása
4. OK
   ✅ Success toast
   ✅ Task státusza: COMPLETED
   ✅ Lista frissül
   
Результат: ✅ PASS
```

---

### REPORTS TESZTEK

#### TC-019: Report Generálás
```
1. Bottom Nav → Reports
   ✅ Report típusok listája
   
2. Report kiválasztása: "Asset Summary"
   ✅ Date range picker megjelenik
   
3. Date range beállítása
4. Generate
   ✅ Report betöltődik
   ✅ PDF/HTML preview
   
5. Share/Export
   ✅ Share intent vagy Download
   
Результат: ✅ PASS
```

---

### SETTINGS TESZTEK

#### TC-020: Profile Edit
```
1. Bottom Nav → Settings
   ✅ Profile info megjelenítve
   
2. Edit gomb
   ✅ Form: name, email, phone szerkeszthető
   
3. Save
   ✅ Success toast
   ✅ Profile frissül
   
Результат: ✅ PASS
```

#### TC-021: Language Switch
```
1. Settings screen
2. Language selector
   ✅ English / Magyar opciókat
   
3. Válassz Magyart
   ✅ App nyelvezete megváltozik
   ✅ Összes string magyarra fordítva
   
Результат: ✅ PASS
```

#### TC-022: Logout
```
1. Settings
2. Logout gomb
   ✅ Confirmation dialog
   
3. Confirm
   ✅ Login screen megjelenik
   ✅ Session lezárva
   
Результат: ✅ PASS
```

---

## 🔄 OFFLINE MODE TESZT

#### TC-023: Offline Funkcionalitás
```
1. App: Assets lista betöltve
2. Airplane Mode ON
   ✅ App továbbra működik (cache-ből)
   
3. Create Asset (offline)
   ✅ Local DB-be megy
   ✅ Success toast
   
4. Asset lista
   ✅ Új asset megjelenik (offline)
   
5. Airplane Mode OFF
6. Refresh vagy auto-sync
   ✅ Az új asset szinkronizálódik a serverrel
   
Результат: ✅ PASS
```

---

## 📊 TELJES TESZTKIMENET ÖSSZEFOGLALÁSA

### Tesztesetek Összesen: 23
- ✅ Sikeres: ___/23
- ❌ Sikertelen: ___/23
- ⚠️ Figyelmeztetés: ___/23
- ⏭️ Kihagyott: ___/23

### Teljesítés %: ____%

---

## 🐛 ISSUE TRACKER

Ha bármi nem működik, jegyezd fel:

| Test Case | Issue | Súlyosság | Megjegyzés |
|-----------|-------|-----------|-----------|
| TC-001 | ... | CRITICAL / HIGH / MEDIUM / LOW | |
| | | | |

---

## ✅ VÉGSŐ ÖSSZEFOGLALÁS

**Android app telefon tesztelésének végén:**

- [ ] Összes tesztecase lefuttatva
- [ ] Legalább 90% sikeres tesztek
- [ ] Nincsenek CRITICAL hibák
- [ ] Offline mode működik
- [ ] UI/UX megfelelő
- [ ] Performance megfelelő (< 2s loading)
- [ ] Nincs FC (Force Close)

---

## 🔧 HIBAELHÁRÍTÁS

### Ha "Test Server" gomb sikertelen (❌ Hálózati hiba)
```
Probléma: Backend szerver nem elérhető
Megoldás:
1. Győződj meg, hogy a backend szerver fut (PC-n)
2. Ellenőrizd a WiFi/4G kapcsolatot
3. Ellenőrizd, hogy PC és telefon ugyanaz az hálózaton van-e
4. Próbáld meg a backend URL-t böngészőben: 
   http://[PC_IP]:8000/api/health/
```

### Ha login sikertelen (401 Unauthorized)
```
Probléma: Hibás felhasználónév/jelszó vagy backend DB hiba
Megoldás:
1. Ellenőrizd: a.geleta / Gele007ta helyes-e
2. Ellenőrizd, hogy a backend DB-ben létezik-e ez a user
3. Próbáld meg curl-lel:
   curl -X POST http://[PC_IP]:8000/api/v1/auth/login 
        -H "Content-Type: application/json" 
        -d "{\"username\":\"a.geleta\",\"password\":\"Gele007ta\"}"
```

### Ha app freezeol vagy FC (Force Close)
```
Probléma: Alkalmzás összeomlott
Megoldás:
1. Ellenőrizz logokat: adb logcat
2. Indítsd újra az appot
3. Próbáld meg a cache törlést:
   adb shell pm clear com.artence.cmms
```

---

## 📞 TESZTELÉSI NAPLÓ

**Tesztelés kezdete**: ___________  
**Tesztelés vége**: ___________  
**Tesztelő**: ___________  
**Eszköz**: Android _____ (API _____)  
**App verzió**: 1.0.0 Debug

### Megjegyzések:

```
[Itt jegyezd fel a megállapításokat]
```

---

**Készítette**: AI Assistant  
**Dátum**: 2025.12.15  
**Verzió**: 1.0  
**Projekt**: CMMS Android App - Real Device Testing

