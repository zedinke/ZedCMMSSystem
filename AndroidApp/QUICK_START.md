# ⚡ QUICK START - APK BUILD & EMULATOR FUTTATÁS

## 🚀 LEGGYORSABB MÓDSZER (3 LÉPÉS)

### 1️⃣ Nyisd meg a PowerShell-t az AndroidApp mappában

```powershell
cd E:\Artence_CMMS\AndroidApp
```

### 2️⃣ Futtasd a build script-et

**Windows (PowerShell):**
```powershell
.\build_and_run.ps1
```

**Vagy Windows (Command Prompt):**
```cmd
build_and_run.bat
```

### 3️⃣ Kész! Az app az emulator-on fog futni

---

## 📱 AZ EMULATOR INDÍTÁSA (Ha szükséges)

**Android Studio-ban:**
```
1. Tools > Device Manager
2. Jobb klikk Pixel 7 Pro API 34-en
3. Launch in Emulator
```

**Vagy PowerShell-ből:**
```powershell
emulator -avd "Pixel 7 Pro API 34"
```

---

## 🔑 LOGIN ADATOK

```
Email:    admin@example.com
Password: Admin123456
```

---

## 📊 MIT VÁR EL?

```
1. Build folyamat: ~2-3 perc
2. APK telepítés: ~5-10 másodperc
3. App indítás: ~1-2 másodperc

ÖSSZESEN: 3-5 perc
```

---

## 🛠️ HA GOND VAN

### "Nincs csatlakoztatott emulator"
→ Device Manager-ből indítsd az emulatort

### "APK telepítés sikertelen"
→ Emulator újraindítása / `adb kill-server`

### "Gradle sync hiba"
→ Android Studio: File > Invalidate Caches > Restart

---

## 📖 RÉSZLETES ÚTMUTATÓ

👉 Nézd meg: `APK_BUILD_EMULATOR_GUIDE.md`

---

## ✅ SIKERES FUTTATÁS JELE

```
Emulator-on megjelenik:
├─ Android CMMS splash screen
├─ Login screen (Email + Password)
├─ Kattintható gombok
└─ Dashboard 8 menü kartya

STATUS: ✅ App működik! 🎉
```

---

**Dátum:** 2025-01-14  
**Verzió:** 1.0  
**Status:** ✅ READY TO RUN

