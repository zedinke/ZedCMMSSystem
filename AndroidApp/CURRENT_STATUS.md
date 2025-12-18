# CMMS Android App - Aktuális állapot

**Dátum:** 2025.12.15  
**Build verzió:** Debug APK telepítve az AVD-re  
**Backend szerver:** http://116.203.226.140:8000

## ✅ Elvégzett feladatok

### 1. Build hibák javítása
- **AppModule.kt**: TokenManager.getToken() Flow<String?> típusát javítottam `.first()` hívással
- **CreateInventoryViewModel.kt & Screen.kt**: Hozzáadtam a kötelező `name` paramétert az Inventory létrehozáshoz
- **AuthApi.kt**: Login végpont útvonala javítva: `POST v1/auth/login`

### 2. Backend integráció
- **BASE_URL**: `http://116.203.226.140:8000/api/` (Constants.kt)
- **Login endpoint**: `/api/v1/auth/login`
- **Cleartext HTTP**: Engedélyezve az AndroidManifest.xml-ben (`usesCleartextTraffic="true"`)
- **Timeout**: 30s minden hálózati hívásra

### 3. Diagnosztikai eszközök
- **DiagnosticsUtil.kt**: Szerver elérhetőség tesztelő utility osztály
  - DNS resolution teszt
  - Health check endpoint teszt (`/api/health/`)
  - Login endpoint teszt (401 válasz = endpoint létezik)
- **LoginScreen.kt**: "Test Server" gomb hozzáadva
  - A gomb megnyomásakor dialógus jelenik meg a szerver állapotával
  - Még a login előtt ellenőrizhető a backend elérhetősége

### 4. Hibakeresés támogatás
- **LoginViewModel.kt**: Részletes Log.d() és Log.e() hívások
- **AuthRepository.kt**: Hálózati válaszok logolása
- Minden login kísérlet előtt automatikusan lefut a diagnosztika

### 5. API dokumentáció
- **API_ENDPOINTS_REQUIRED.md**: Teljes API specifikáció
  - Minden szükséges endpoint felsorolva
  - DTO struktúrák leírva
  - Példa kérések

## ⚠️ Jelenlegi probléma

**Tünet**: A login gomb megnyomása után végtelen homokóra (loading spinner) jelenik meg, nem történik semmi.

**Lehetséges okok**:
1. **Hálózati timeout**: A szerver nem válaszol 30 másodperc alatt
2. **DNS/kapcsolódási hiba**: Az app nem éri el a szervert
3. **Endpoint nem létezik**: A `/api/v1/auth/login` 404-et ad vissza
4. **Váratlan kivétel**: Az app elkapja, de nem kezeli megfelelően

## 🔍 Következő lépések (diagnosztika)

### AZONNAL tesztelendő az AVD-n:

1. **Nyisd meg az appot az emulátoron**
2. **NE adj meg logint, hanem nyomd meg a "Test Server" gombot**
3. **A dialógusban látható lesz**:
   - DNS működik-e (116.203.226.140 feloldható-e)
   - Health endpoint elérhető-e
   - Login endpoint létezik-e (várható: 401 Unauthorized mock adatokkal)

Ez a 3 teszt megmutatja, hol van a probléma:
- Ha mindhárom sikeres → a backend elérhető, csak a login logikában van hiba
- Ha DNS hiba → hálózati probléma az emulátoron
- Ha Health/Login endpoint 404 → a backend routing hibás

### Ha a szerver elérhető, de a login nem működik:

Ellenőrizni kell a backend oldalon:
- A `/api/v1/auth/login` endpoint pontosan milyen formátumot vár
- JSON vagy form-encoded?
- Milyen mezőneveket vár? (username/password vagy email/password?)
- Mi a jelszó hashing algoritmus?

## 📋 Backend API követelmények összefoglalója

Az app a következőket várja a backendtől:

### Login (kötelező)
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "a.geleta",
  "password": "Gele007ta"
}
```

**Válasz (200 OK)**:
```json
{
  "access_token": "eyJ...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "user_id": 1,
  "username": "a.geleta",
  "role_name": "admin"
}
```

### További endpointok
- `/api/users` - Felhasználók (GET, POST, PUT, DELETE)
- `/api/machines` - Gépek
- `/api/worksheets` - Munkalapok
- `/api/inventory` - Készlet/Eszközök
- `/api/v1/pm/tasks` - Preventív karbantartás
- `/api/reports/summary` - Riportok

Részletek: `API_ENDPOINTS_REQUIRED.md`

## 🛠️ Amit még megtehetünk (ha szükséges)

### Ha a login form-encoded-et vár (OAuth2PasswordRequestForm)
Módosítani kell az `AuthApi.kt`-t és a `LoginRequest.kt`-t:
```kotlin
@FormUrlEncoded
@POST("v1/auth/login")
suspend fun login(
    @Field("username") username: String,
    @Field("password") password: String
): Response<TokenResponse>
```

### Ha más endpoint struktúrát használ a backend
- Egyszerűen átírhatók a routing útvonalak az API interface-ekben
- BASE_URL is módosítható a Constants.kt-ben

### Ha timeout probléma van
- Növelhető a TIMEOUT_SECONDS érték a Constants.kt-ben (jelenleg 30s)

## 📝 Tesztelési forgatókönyv

1. ✅ Build sikeres
2. ✅ APK telepítve az AVD-re
3. ⏳ **MOST KÖVETKEZIK**: AVD-n futtatni és "Test Server" gomb tesztelése
4. ⏳ Login teszt a valódi felhasználói adatokkal
5. ⏳ Ha sikeres login, akkor a többi funkció tesztelése

## 💡 Hogyan nézd meg a logokat

Mivel az adb nem elérhető közvetlenül a terminálból, két lehetőség van:

**Opció 1 - Android Studio Logcat**:
- Nyisd meg az Android Studiót
- Menj a View → Tool Windows → Logcat
- Szűrj a "LoginViewModel", "AuthRepository" vagy "DiagnosticsUtil" TAG-ekre

**Opció 2 - Diagnosztikai dialógus az app-ban**:
- Az app login képernyőjén a "Test Server" gomb részletes info-t ad
- Ezt képernyőképpel vagy manuálisan át tudod másolni

## ⚡ Gyors probléma-megoldási táblázat

| Hibaüzenet | Ok | Megoldás |
|------------|-----|----------|
| Végtelen homokóra | Timeout vagy nincs válasz | "Test Server" gomb → nézd meg a kapcsolódást |
| "Login failed: 404" | Rossz endpoint URL | Ellenőrizd a backend routing-ot |
| "Login failed: 401" | Hibás felhasználónév/jelszó | Ellenőrizd az adatbázisban a hash-t |
| "Login failed: 422" | Rossz request formátum | Form-encoded vs JSON különbség |
| "Connection refused" | Szerver nem fut | Indítsd el a backend szervert |
| "Network error" | DNS/hálózati hiba | Ellenőrizd az emulátor internet kapcsolatát |

## 🎯 Következő lépés NEKED

**Nyisd meg az emulátort, indítsd el a CMMS appot, és nyomd meg a "Test Server" gombot.**

A dialógusban látható eredmény alapján azonnal tudni fogjuk, mi a probléma, és folytathatom a javítást.

Ha bármilyen hibaüzenetet látsz (a dialógusban vagy a login után), **másold be ide**, és azonnal megjavítom!

