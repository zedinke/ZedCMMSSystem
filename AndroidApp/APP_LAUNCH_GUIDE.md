# 📱 ANDROID APP INDÍTÁSI ÚTMUTATÓ

## 🚀 GYORS INDÍTÁS - LÉPÉSRŐL LÉPÉSRE

### 1️⃣ ANDROID STUDIO MEGNYITÁSA

1. **Nyisd meg az Android Studio-t**
2. **Open Project** → Válaszd ki: `E:\Artence_CMMS\AndroidApp`
3. Várj, amíg a Gradle sync befejeződik (alul a progress bar)

---

### 2️⃣ EMULÁTOR INDÍTÁSA

**Opció A: Meglévő Emulátor**
1. Klikk a felső toolbar-on: **Device Manager** (telefon ikon)
2. Válassz egy eszközt (pl. "Pixel 5 API 33")
3. Klikk a **Play (▶)** gombra
4. Várj ~30-60 másodpercet, amíg az emulátor elindul

**Opció B: Új Emulátor Létrehozása**
1. Device Manager → **Create Device**
2. Válassz egy eszközt: **Pixel 5** vagy **Pixel 6**
3. System Image: **API 33 (Android 13)** vagy **API 34 (Android 14)**
4. Finish → Play ▶

---

### 3️⃣ APP BUILD ÉS FUTTATÁS

#### Android Studio-ban:

1. **Válaszd ki az eszközt** a felső toolbar-on (pl. "Pixel 5 API 33")
2. Klikk a zöld **Run (▶)** gombra
3. Várj, amíg az app build-elődik és települ
4. Az app automatikusan elindul az emulátoron!

#### Vagy terminálban:

```batch
cd E:\Artence_CMMS\AndroidApp

REM Build és telepítés
gradlew.bat installDebug

REM App indítása
adb shell am start -n com.artence.cmms/.MainActivity
```

---

### 4️⃣ APP HASZNÁLATA

1. **Login Screen megjelenik**
   - Username: `a.geleta`
   - Password: `Gele007ta`

2. **Offline Mode**
   - Ha a backend (116.203.226.140:8000) nem elérhető
   - Az app offline módban működik
   - Room SQLite cache-ből tölt

3. **Online Mode** (ha backend fut)
   - Dashboard betöltődik az ÉLES ADATOKKAL
   - Szinkronizáció automatikus
   - CRUD műveletek a szerverre mentődnek

---

## 🔧 HIBAKERESÉS

### Probléma: "No connected devices"

**Megoldás:**
1. Indítsd el az emulátort a Device Manager-ből
2. Vagy futtasd terminálban:
   ```batch
   %LOCALAPPDATA%\Android\Sdk\emulator\emulator -avd Pixel_5_API_33
   ```

### Probléma: "Gradle sync failed"

**Megoldás:**
1. Android Studio → File → Invalidate Caches → Invalidate and Restart
2. Vagy terminálban:
   ```batch
   cd E:\Artence_CMMS\AndroidApp
   gradlew.bat clean
   gradlew.bat build
   ```

### Probléma: "ADB not found"

**Megoldás:**
1. Állítsd be a PATH-ot:
   ```batch
   set ANDROID_HOME=%LOCALAPPDATA%\Android\Sdk
   set PATH=%PATH%;%ANDROID_HOME%\platform-tools
   ```

### Probléma: Login sikertelen (Network Error)

**OK**: Backend szerver nem fut

**Megoldás:**
1. **Offline használat**: Az app offline módban működik!
2. **Backend indítás**: Lásd `BACKEND_ACTIVATION_COMPLETE.md`
3. **Helyi backend**: 
   ```batch
   cd E:\Artence_CMMS\CMMS_Project
   python -m uvicorn api.server:app --host 0.0.0.0 --port 8000
   ```

---

## 📋 TESZTELÉSI CHECKLIST

### ✅ Offline Teszt
- [ ] App települ az emulátorra
- [ ] Login screen megjelenik
- [ ] Offline adatok betöltődnek
- [ ] Asset létrehozás működik
- [ ] Worksheet szerkesztés működik
- [ ] Navigation működik

### ✅ Online Teszt (ha backend fut)
- [ ] Login sikeres: a.geleta / Gele007ta
- [ ] Dashboard betölt ÉLES adatokkal
- [ ] Assets lista megjelenik
- [ ] Asset részletek megnyithatók
- [ ] Új asset létrehozható
- [ ] Szinkronizáció működik

---

## 🎯 GYORS PARANCSOK

### App Build
```batch
cd E:\Artence_CMMS\AndroidApp
gradlew.bat assembleDebug
```

### App Telepítés
```batch
gradlew.bat installDebug
```

### App Indítás (ha már telepítve)
```batch
adb shell am start -n com.artence.cmms/.MainActivity
```

### App Törlés
```batch
adb uninstall com.artence.cmms
```

### Logcat (Debug)
```batch
adb logcat | findstr "CMMS\|AssetsViewModel\|LoginViewModel"
```

---

## 📱 ANDROID STUDIO SHORTCUTS

| Akció | Shortcut |
|-------|----------|
| Run App | **Shift + F10** |
| Debug App | **Shift + F9** |
| Build Project | **Ctrl + F9** |
| Open Device Manager | **Ctrl + Shift + A** → "Device Manager" |
| Logcat | **Alt + 6** |

---

## 🔥 LEGGYORSABB MÓDSZER

### 1. Android Studio-ban:

1. Open Project: `E:\Artence_CMMS\AndroidApp`
2. Klikk: **Device Manager** (telefon ikon)
3. Válassz eszközt → **Play ▶**
4. Várj 30 másodpercet
5. Klikk: **Run ▶** (zöld play gomb)
6. **KÉSZ!** Az app elindul!

---

## 📊 APP FUNKCIÓK TESZTELÉSE

### Dashboard
- ✅ 4 metric card (Assets, Worksheets, PM Tasks, Inventory)
- ✅ Quick actions
- ✅ Recent items

### Assets
- ✅ Lista view
- ✅ Keresés
- ✅ Filter (status)
- ✅ Részletek megtekintése
- ✅ Új asset létrehozása
- ✅ Szerkesztés
- ✅ Törlés

### Worksheets
- ✅ Lista view
- ✅ Status filter (Open, In Progress, Closed)
- ✅ Részletek
- ✅ Create worksheet
- ✅ Status változtatás

### Settings
- ✅ Profile megtekintése
- ✅ Language váltás (EN/HU)
- ✅ Theme váltás (Light/Dark)
- ✅ Logout

---

## 🎓 TIPPEK

1. **Első indításnál**: Az app offline cache-t inicializál (~3-5 másodperc)
2. **Login**: Ha backend offline, a login sikertelen lesz, de offline mód működik
3. **Adatok**: Az offline adatok a Room SQLite DB-ben vannak (`/data/data/com.artence.cmms/databases/`)
4. **Szinkronizáció**: Automatikus, amikor backend online lesz
5. **Performance**: Az app gyors, mert offline-first architektúra

---

## ✅ SIKERES INDÍTÁS JELEI

1. **Build Output**: "BUILD SUCCESSFUL in XXs"
2. **Install Output**: "Installed on 1 device"
3. **Emulátor**: App ikon megjelenik
4. **App elindul**: Login screen látható
5. **Offline Banner**: "Offline mode - data will sync when online"

---

**🎉 MOST MÁR KÉSZEN ÁLLSZ AZ APP TESZTELÉSÉRE!**

**Következő lépés**: Android Studio → Device Manager → Play ▶ → Run ▶

---

**Dátum**: 2025.12.15  
**Készítette**: AI Assistant  
**Verzió**: 1.0

