# CMMS App - Gyors Tesztelési Útmutató

## 1️⃣ App indítása az AVD-n

Az app már telepítve van. Keresd meg az emulátoron a **CMMS** ikont és nyisd meg.

## 2️⃣ Test Server gomb tesztelése

Amikor megnyílik a login képernyő, **NE töltsd ki a mezőket még**!

1. Görgess le a képernyőn
2. Nyomd meg a **"Test Server"** gombot
3. Várj pár másodpercet amíg a diagnosztika lefut
4. Egy dialógus ablak fog megjelenni az eredményekkel

### Mit nézzünk a diagnosztikai eredményekben?

✅ **Sikeres teszt példa:**
```
=== SERVER DIAGNOSTICS ===

DNS Resolution:
DNS OK: 116.203.226.140

Server Connectivity:
Server OK: {"status":"ok"}

Login Endpoint:
Endpoint exists but credentials invalid (401) - this is expected
```

❌ **Sikertelen teszt példák:**

**DNS hiba:**
```
DNS Resolution:
DNS resolution failed: Unable to resolve host
```
→ **Megoldás**: Ellenőrizd az emulátor internet kapcsolatát (Settings → Wi-Fi)

**Szerver nem elérhető:**
```
Server Connectivity:
Connectivity test failed: Connection refused
```
→ **Megoldás**: Ellenőrizd, hogy a backend szerver fut-e (116.203.226.140:8000)

**Endpoint nem létezik:**
```
Login Endpoint:
Endpoint not found (404) - check the URL!
```
→ **Megoldás**: A backend login endpoint útvonala nem `/api/v1/auth/login`

## 3️⃣ Login teszt (ha a szerver elérhető)

Ha a "Test Server" minden eredménye zöld (401 is elfogadható a login endpoint-nál):

1. **Username**: `a.geleta`
2. **Password**: `Gele007ta`
3. Nyomd meg a **"Login"** gombot

### Lehetséges eredmények:

✅ **Sikeres login**: Az app átnavigál a főképernyőre

❌ **Login failed: 401 Unauthorized**: 
- A backend nem fogadja el a jelszót
- Ellenőrizd az adatbázisban a jelszó hash-t

❌ **Login failed: 422 Unprocessable Entity**:
- A backend más formátumot vár (pl. form-encoded)
- Jelezd, és átírom a kérés formátumát

❌ **Homokóra örökké pörög**:
- Timeout vagy nincs válasz
- Nézd meg a logokat az Android Studio Logcat-ben (TAG: "AuthRepository")

## 4️⃣ Logok megtekintése (opcionális)

Ha Android Studiód van nyitva:

1. View → Tool Windows → Logcat
2. Szűrő: `package:com.artence.cmms`
3. Vagy konkrét TAG-ekre: `LoginViewModel`, `AuthRepository`, `DiagnosticsUtil`

## 5️⃣ Mit jelentenek a hibaüzenetek?

| Üzenet | Mit jelent | Mit tegyek |
|--------|-----------|-----------|
| "Login failed: Not found" | Rossz endpoint URL | Másold be a pontos hibát |
| "Login failed: Unauthorized" | Hibás jelszó vagy felhasználónév | Ellenőrizd a backend adatbázist |
| "Invalid credentials" | A backend szerint nem jó a jelszó | Hash ellenőrzés kell |
| "Connection refused" | Szerver nem fut vagy firewall | Ellenőrizd a backend szervert |
| "Timeout" | Túl lassu válasz vagy nincs válasz | Növeld a timeoutot vagy javítsd a szervert |

## 📸 Screenshot készítése

Ha van hibaüzenet vagy furcsa eredmény:
1. Készíts képernyőképet az emulátorról (Windows: Win+Shift+S)
2. Vagy másold ki a szöveget a dialógusból
3. Küldd be nekem, és javítom a problémát

## ✨ Következő lépések sikeres login után

Ha a login működik, ezek a funkciók lesznek elérhetők:
- Machines (Gépek) megtekintése és kezelése
- Worksheets (Munkalapok) létrehozása
- Inventory (Készlet) nyilvántartása
- PM Tasks (Preventív karbantartás) ütemezése
- Reports (Riportok) megtekintése
- Settings (Beállítások) - nyelv váltás, kijelentkezés

---

**Fontos**: Ha bárhol elakadsz vagy hibaüzenetet látsz, **másold be a pontos szöveget**, és folytatom a javításokat!

