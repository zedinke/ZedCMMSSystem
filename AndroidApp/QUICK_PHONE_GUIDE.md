# 📱 CMMS Android App - TELEFONRA TELEPÍTÉS ÉS TESZTELÉS

## ⚡ GYORS ÚTMUTATÓ - 5 PERC ALATT

### Lépés 1: Telefon Előkészítése (1 perc)
```
1. Telefon: Beállítások → Fejlesztői beállítások → USB Debugging ON
   (ha nem látod a Fejlesztői beállítások:
    Rólunk → Build szám 7x-et kattints)

2. USB kábellel csatlakoztasd a PC-hez

3. Telefon: Jóváhagyás gomb a "Debgging" jóváhagyási dialógusban
```

### Lépés 2: Android App Telepítése (2 perc)
```batch
# Nyisd meg a Command Prompt-ot
cd E:\Artence_CMMS\AndroidApp

# Futtasd a telepítő scriptet:
install_to_phone.bat

# Vagy manuálisan:
gradlew.bat installDebug
```

**Elvárt kimenet:**
```
Installing APK 'app-debug.apk' on 'Your Phone' for :app:debug
Installed on 1 device.
BUILD SUCCESSFUL
```

### Lépés 3: App Indítása Telefonon (1 perc)
```
1. Telefon: Alkalmazások
2. Keresd: CMMS (vagy keress le)
3. Megnyitás
```

### Lépés 4: Bejelentkezés (1 perc)
```
Username: a.geleta
Password: Gele007ta
Bejelentkezés gomb ➜ Mehetünk!
```

---

## 🎯 TESZTELENDŐ FUNKCIÓK (GYAKORLATI ÚTMUTATÓ)

### ✅ 1. LOGIN TESZT
Nyisd meg az appot után:
- [ ] Username: a.geleta
- [ ] Password: Gele007ta
- [ ] Login gomb megnyomása
- [ ] ✅ Dashboard megjelenjen

### ✅ 2. DASHBOARD
- [ ] Látod-e a metric cardokat? (Assets, Worksheets, stb.)
- [ ] Húzd le a képernyőt (Refresh)
- [ ] Adatok frissülnek-e?

### ✅ 3. ASSETS MANAGEMENT
- [ ] Bottom Nav: Assets megnyomása
- [ ] Asset lista megjelenik-e?
- [ ] + gomb: Create Asset
  - [ ] Name: "Test Machine"
  - [ ] Status: OPERATIONAL
  - [ ] Save
- [ ] Új asset megjelenik-e?
- [ ] Asset szerkesztése (Edit gomb)
- [ ] Asset törlése (Delete gomb)

### ✅ 4. WORKSHEETS
- [ ] Bottom Nav: Worksheets
- [ ] + gomb: Create Worksheet
  - [ ] Title: "Test Work"
  - [ ] Status: OPEN
  - [ ] Save
- [ ] Státusz megváltoztatása (chipre kattint)

### ✅ 5. MACHINES
- [ ] Bottom Nav: Machines
- [ ] Gépek listája megjelenik-e?

### ✅ 6. INVENTORY
- [ ] Bottom Nav: Inventory
- [ ] Készlet items listája
- [ ] Low stock items piros színnel?

### ✅ 7. PM (PREVENTIVE MAINTENANCE)
- [ ] Bottom Nav: PM
- [ ] PM tasks listája
- [ ] Due date szerint rendezve?

### ✅ 8. REPORTS
- [ ] Bottom Nav: Reports
- [ ] Report típusok kiválasztása
- [ ] Generate Report
- [ ] Report megjelenik-e?

### ✅ 9. SETTINGS
- [ ] Bottom Nav: Settings
- [ ] Profile Edit: Név módosítása, Save
- [ ] Language: English/Magyar váltás
- [ ] Logout: Bejelentkezés kijelentkezés

### ✅ 10. OFFLINE MODE
- [ ] Airplane Mode bekapcsolása
- [ ] Assets lista még betöltődik-e?
- [ ] + gomb: Create Asset offline
- [ ] Success toast?
- [ ] Airplane Mode kikapcsolása
- [ ] Refresh: Asset szinkronizálódik-e?

---

## 📋 TESZTKITÖLTŐ LAP

**Telefon típusa**: _________________  
**Android verzió**: _________________  
**Teszt dátuma**: _________________  
**Tesztelő neve**: _________________

### Funkciók Státusza

| # | Funkció | ✅ Működik | ⚠️ Figyelmeztetés | ❌ Hiba | Megjegyzés |
|----|---------|-----------|------------------|--------|-----------|
| 1 | Login | ☐ | ☐ | ☐ | |
| 2 | Dashboard | ☐ | ☐ | ☐ | |
| 3 | Assets CRUD | ☐ | ☐ | ☐ | |
| 4 | Worksheets | ☐ | ☐ | ☐ | |
| 5 | Machines | ☐ | ☐ | ☐ | |
| 6 | Inventory | ☐ | ☐ | ☐ | |
| 7 | PM Tasks | ☐ | ☐ | ☐ | |
| 8 | Reports | ☐ | ☐ | ☐ | |
| 9 | Settings | ☐ | ☐ | ☐ | |
| 10 | Offline Mode | ☐ | ☐ | ☐ | |

### Teljesítés: ____/10 (__%)

---

## 🔍 KÖZÖS PROBLÉMÁK ÉS MEGOLDÁSOK

### Problem 1: Telefon nem jelenik meg az `adb devices`-ben
```
Megoldás:
1. USB debugging kikapcs/bekapcs a telefonon
2. USB kábel cseréje
3. PC USB port cseréje
4. Telefon újraindítása
```

### Problem 2: "Installed on 0 device" hiba
```
Megoldás:
1. Ellenőrizd: adb devices
2. Kattints OK-ra a telefon jóváhagyási dialógusán
3. Próbáld meg: gradlew.bat installDebug
```

### Problem 3: App összeomlott (Force Close)
```
Megoldás:
1. Android app cache törlés:
   adb shell pm clear com.artence.cmms
   
2. App újraindítása
3. Ha továbbra sem működik: újra telepítés
   adb uninstall com.artence.cmms
   gradlew.bat installDebug
```

### Problem 4: Backend szerver nem elérhető (❌ Test Server gomb)
```
Megoldás:
1. Győződj meg, hogy a backend szerver fut PC-n:
   cd E:\Artence_CMMS\CMMS_Project
   python -m uvicorn api.server:app --host 0.0.0.0 --port 8000
   
2. Nézd meg a szerver URL-t Constants.kt fájlban
   
3. PC és telefon ugyanaz az hálózaton van-e?
   
4. Windows tűzfal blokkolhat (nyisd meg a portot)
```

### Problem 5: Login hibás (401 Unauthorized)
```
Megoldás:
1. Ellenőrizd az adatbázist:
   SELECT * FROM users WHERE username = 'a.geleta';
   
2. Próbáld másik felhasználóval
   
3. Végezz pasword reset-et az admin felhasználón
```

---

## 📊 VÉGSŐ ÖSSZEFOGLALÁS

### Ha a tesztek > 80% sikeres:
✅ **Az app READY a produkciós használatra!**

### Ha a tesztek < 80% sikeres:
⚠️ **Még szükséges javítások:**
- Backend szerver stabilitása
- Hálózati kapcsolat megbízhatósága
- Néhány UI/UX finomítás

---

## 🚀 KÖVETKEZŐ LÉPÉSEK

1. **Telefonra telepítés** (`install_to_phone.bat`)
2. **Tesztelési napló kitöltése** (fenti táblázat)
3. **Hibák dokumentálása** (ha vannak)
4. **Feedback küldése** az fejlesztői teamnek

---

## 📚 TELJES ÚTMUTATÓK

Részletes tesztelési útmutatók:
- 📖 `PHONE_TESTING_GUIDE.md` - 23 tesztecase részletesen
- 📖 `FUNCTIONAL_TEST_REPORT.md` - Windows vs Android összehasonlítás
- 📖 `README.md` - Alapvető dokumentáció
- 📖 `CURRENT_STATUS.md` - Projekt állapota

---

## ✅ CHECKLIST - MIELŐTT TELEPÍTESZ

- [ ] USB debugging bekapcsolva a telefonon?
- [ ] USB kábellel csatlakoztattad a telefont?
- [ ] `adb devices` mutat-e az eszközt?
- [ ] Android Studio / ADB telepítve van?
- [ ] Backend szerver fut?
- [ ] Telefonon van internet (WiFi/4G)?

---

**Készítette**: AI Assistant  
**Dátum**: 2025.12.15  
**Verzió**: 1.0  
**Projekt**: CMMS Android App - Phone Testing Guide

🚀 **MOST TELEPÍTSD ÉS TESZTELD!**

