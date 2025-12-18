# 🚀 ANDROID STUDIO - VIRTUÁLIS ESZKÖZ SETUP & APP FUTTATÁS

**Dátum:** 2025-01-14  
**Cél:** App futtatása Android Studio-ból virtuális eszközön  
**Idő:** ~10-15 perc

---

## 📋 LÉPÉSRŐL LÉPÉSRE ÚTMUTATÓ

### STEP 1: ANDROID STUDIO MEGNYITÁSA

```
1. Android Studio indítása (ha még nem nyitva van)
2. File > Open Project
3. Mappa kiválasztása: E:\Artence_CMMS\AndroidApp
4. ENTER / OK
```

**Várás:** Gradle sync befejezése (1-2 perc)

```
Bottom panelen látni fogod:
├─ Gradle sync running...
└─ Gradle sync finished ✅
```

---

### STEP 2: VIRTUÁLIS ESZKÖZ (EMULATOR) ELLENŐRZÉSE

#### 2a. Device Manager megnyitása

```
Android Studio menüben:
Tools > Device Manager
```

**Vagy alul a jobb sarokban:**
```
Device Manager ikont keresd (telefon + tájékozódás)
```

---

#### 2b. Virtuális Eszköz Listája

```
Amit kell látni:
┌─────────────────────────────────────────────┐
│ Device Manager                              │
├─────────────────────────────────────────────┤
│ Virtual                                     │
│ ├─ Pixel 7 Pro API 34     (vagy hasonló)  │
│ └─ Status: Installed                       │
└─────────────────────────────────────────────┘
```

**Ha nincs eszköz:** Kell létrehozni egyet
→ Menj a STEP 3-hoz

---

### STEP 3: VIRTUÁLIS ESZKÖZ LÉTREHOZÁSA (ha szükséges)

#### 3a. Create Virtual Device

```
Device Manager ablakban:
1. Bal felül: "+ Create Device" gomb
2. Kattintás
```

#### 3b. Device Kiválasztása

```
Virtual Device Configuration
├─ Category: Phone
├─ Device: Pixel 7 Pro  ← Válaszd ezt
└─ Next
```

#### 3c. System Image

```
System Image kiválasztása
├─ Recommended tab
├─ API Level: 34 (Android 14)  ← Ez kell
├─ Download gomb (ha szükséges)
└─ Next
```

#### 3d. Verify Configuration

```
Android Virtual Device (AVD)
├─ Name: Pixel 7 Pro API 34
├─ Device: Pixel 7 Pro
├─ System Image: Android 14 (API 34)
├─ RAM: 8GB
└─ Finish
```

**Kimenetel:** Virtuális eszköz létrehozva ✅

---

### STEP 4: VIRTUÁLIS ESZKÖZ INDÍTÁSA

#### 4a. Device Manager-ben

```
Device Manager ablakban:
├─ Pixel 7 Pro API 34 eszköz található
├─ Jobb oldali gombsor:
│  ├─ Play gomb (zöld, indítás)
│  └─ Kattints a Play-ra
└─ Várakozás...
```

#### 4b. Emulator Boot

```
⏳ Emulator indul (20-40 másodperc)

Amit fogsz látni:
├─ Emulator ablak megnyílik
├─ Android splash screen
├─ Boot animation (zöld körök)
└─ Végül: Android home screen
```

**Kimenetel:**
```
✅ Emulator teljesen betöltött
✅ Lock screen vagy home screen látható
✅ Kész az app futtatásához
```

---

### STEP 5: PROJEKT MEGNYITÁSA ANDROID STUDIO-BAN

#### 5a. Project Explorer

```
Android Studio bal oldala:
├─ Project tab (ha nincs látható: Alt+1)
├─ android > app > src > main
└─ MainActivity.kt / LoginActivity.kt
```

#### 5b. Run Configuration Ellenőrzése

```
Felső menü:
Run > Edit Configurations

Értékek:
├─ Module: app
├─ Deploy: APK
├─ Target: (üres jó, vagy válassz)
└─ OK
```

---

### STEP 6: APP INDÍTÁSA (A FŐ LÉPÉS!)

#### 6a. Run Gomb

```
Felső toolbar:
├─ Zöld Play gomb (▶)  ← Ez az!
└─ Kattintás
```

**Vagy:**
```
Menü: Run > Run 'app'
Vagy: Shift + F10 (billentyűzet)
```

#### 6b. Select Deployment Target Dialog

```
Ablak megjelenik:

┌─────────────────────────────────────┐
│ Select Deployment Target            │
├─────────────────────────────────────┤
│ ☑ Pixel 7 Pro API 34 (emulator)    │ ← Jelölt
│   Status: Online                    │
│                                     │
│ [OK]  [Cancel]                      │
└─────────────────────────────────────┘
```

**Teendő:**
```
1. Pixel 7 Pro API 34 kiválasztva legyen
2. OK gomb kattintás
```

#### 6c. Build Process

```
Alul a Build ablakban fogsz látni:

Gradle build running...
├─ Compiling Kotlin...  [████░░░░]
├─ Packaging APK...     [████████]
└─ Installing APK...    [████████]

Build completed successfully ✅
```

#### 6d. App Indítása

```
Emulator-on fogsz látni:

T+0s:  Splash screen megjelenik
       "Android CMMS"
       
T+1s:  Logo fade-in animáció
       
T+2s:  Splash eltűnik
       
T+3s:  ✅ LOGIN SCREEN MEGJELENIK!
```

---

### STEP 7: LOGIN TESZTELÉSE

#### 7a. Login Screen

```
Emulatort nézve:
┌──────────────────────────┐
│ Android CMMS             │
├──────────────────────────┤
│                          │
│ Email                    │
│ [____________]           │
│                          │
│ Password                 │
│ [____________]           │
│                          │
│    [LOGIN]               │
│                          │
└──────────────────────────┘
```

#### 7b. Adatok Beírása

```
1. Email mező kattintása
2. Gépelés: admin@example.com
3. Password mező kattintása
4. Gépelés: Admin123456
5. Login gomb kattintása
```

#### 7c. Loading & Navigation

```
T+0s:  Login gomb megnyomva
       Loading spinner megjelenik
       
T+1s:  API call (szimulált)
       Token tárolás
       
T+2s:  Splash screen eltűnik
       
T+3s:  ✅ DASHBOARD MEGJELENIK!
```

#### 7d. Dashboard

```
Emulatort nézve:
┌──────────────────────────┐
│ Dashboard                │
├──────────────────────────┤
│ Welcome, admin!          │
│                          │
│ [Assets]  [Inventory]    │
│ [Worksheets] [Machines]  │
│ [PM]      [Reports]      │
│ [Users]   [Settings]     │
│                          │
└──────────────────────────┘
```

**Kimenetel:** ✅ **APP FUTÁSA SIKERES!**

---

### STEP 8: TOVÁBBI TESZTELÉS

#### 8a. Assets menü tesztelése

```
1. Emulator-on: Assets kártya kattintása
2. Assets lista megjelenik
3. Elemek betöltődnek
4. Scroll mozgatás → Smooth 60 FPS
```

#### 8b. Logcat Monitoring

```
Android Studio alul:
Logcat tab kattintása

Fogsz látni:
├─ App üzenetek
├─ Loading információk
├─ API calls
└─ Errors (ha vannak)

Szűrés az appra:
Logcat szűrő: com.artence.cmms
```

#### 8c. Performance Monitoring

```
Android Studio alul:
Profiler tab kattintása

Mérések:
├─ Memory: 68-110MB ✅
├─ CPU: <20% ✅
├─ FPS: 60 FPS ✅
└─ Network: (ha API calls)
```

---

## 🎯 ELLENŐRZŐLISTA

### Futtatás Előtt:
- [ ] Android Studio nyitva
- [ ] Projekt betöltve (Gradle sync kész)
- [ ] Virtuális eszköz létrehozva
- [ ] Emulator elindítva (vagy adat az indításra)

### Futtatás:
- [ ] Run gomb megnyomva (▶)
- [ ] Deployment Target kiválasztva
- [ ] Build sikeresen befejezve
- [ ] APK telepítve az emulatorra

### Utána:
- [ ] Splash screen megjelent
- [ ] Login screen megjelent
- [ ] Login sikeres (admin@example.com / Admin123456)
- [ ] Dashboard megjelent
- [ ] 8 menü kártya látható

---

## 🔧 HIBAELHÁRÍTÁS

### Probléma: "No devices detected"

```
Megoldás:
1. Emulator teljesen betöltött-e?
   Device Manager > Play gomb
   
2. Várd meg a boot végét (~30 sec)
   
3. Run > Run 'app' ismét
```

### Probléma: "Build failed"

```
Megoldás:
1. Build > Clean Project
2. File > Invalidate Caches > Restart
3. Run > Run 'app' ismét
```

### Probléma: "APK installation failed"

```
Megoldás:
1. Terminal: adb uninstall com.artence.cmms
2. Run > Run 'app' ismét
```

### Probléma: "Gradle sync failed"

```
Megoldás:
1. File > Invalidate Caches
2. Restart
3. Gradle sync megvárása
```

### Probléma: "Emulator very slow"

```
Megoldás:
1. Device Manager > Edit
2. RAM: 4GB vagy 8GB
3. Emulator újraindítása
```

---

## 📊 EXPECTED RESULT

```
╔═════════════════════════════════════════╗
║   ANDROID STUDIO APP FUTTATÁS - SIKERES ║
╠═════════════════════════════════════════╣
║                                         ║
║ ✅ Emulator betöltött                  ║
║ ✅ App telepítve                       ║
║ ✅ Splash screen megjelent             ║
║ ✅ Login screen betöltve               ║
║ ✅ Login funkció működik               ║
║ ✅ Dashboard megjelent                 ║
║ ✅ 60 FPS smooth rendering             ║
║ ✅ Logcat nincsenek hibák              ║
║                                         ║
║ STATUS: 🎉 APP TELJES MŰKÖDIK!        ║
║                                         ║
╚═════════════════════════════════════════╝
```

---

## 📱 BILLENTYŰZET PARANCSOK

```
Shift + F10    = Run app
Shift + F9     = Debug app
Ctrl + Shift + R = Rerun
Ctrl + F       = Find in files
Alt + 1        = Project view
Alt + 6        = Logcat view
```

---

## ✨ TIPPEK & TRICKS

### 1. Hot Reload (Java módosítás)
```
Run > Hot Swap
Kódot módosítod > Ctrl+S > Automatikus reload
```

### 2. Breakpoint Debugolás
```
Sor szám mellett klikk > Piros pont
Run > Debug 'app'
Debugger panel megjelenik
```

### 3. Screenshots készítése
```
Emulator menü (felül jobb):
Screenshot > Save
```

### 4. Screen Recording
```
Emulator menü > Record video
Demo videó készítéséhez
```

---

**Android Studio Guide:** v1.0  
**Dátum:** 2025-01-14  
**Status:** ✅ READY TO RUN

