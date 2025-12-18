# 🔍 Android CMMS App - Backend Szinkronizációs Diagnosztika

## Probléma: Az Android App Nem Mutatja az Adatokat

### Lehetséges Okok:

1. ❌ **Backend szerver nem válaszol** (116.203.226.140:8000)
2. ❌ **API endpoint különbségek** (URL path rossz)
3. ❌ **Login sikertelen** (token nem jó)
4. ❌ **Network connectivity** (emulátor/telefon hálózat)
5. ❌ **Room adatbázis üres** (adatok nem szinkronizálódtak)

---

## 📋 Diagnosztikai Lépések

### 1. SZERVER ELÉRHETŐSÉG TESZT

**PowerShell-ben futtasd:**

```powershell
# Health check
$response = Invoke-WebRequest -Uri "http://116.203.226.140:8000/api/health/" -UseBasicParsing
if ($response.StatusCode -eq 200) {
    Write-Host "✅ Backend szerver ELÉRHETŐ" -ForegroundColor Green
    $response.Content
} else {
    Write-Host "❌ Backend szerver NEM VÁLASZOL" -ForegroundColor Red
}
```

**Elvárt kimenet:**
```json
{"status": "ok"}
```

### 2. LOGIN TESZT

```powershell
$loginBody = @{
    username = "a.geleta"
    password = "Gele007ta"
} | ConvertTo-Json

$loginResponse = Invoke-WebRequest -Uri "http://116.203.226.140:8000/api/v1/auth/login" `
    -Method POST `
    -Headers @{"Content-Type" = "application/json"} `
    -Body $loginBody `
    -UseBasicParsing

if ($loginResponse.StatusCode -eq 200) {
    Write-Host "✅ Login SIKERES" -ForegroundColor Green
    $tokenData = $loginResponse.Content | ConvertFrom-Json
    $accessToken = $tokenData.access_token
    Write-Host "Token: $($accessToken.Substring(0, 20))..."
} else {
    Write-Host "❌ Login SIKERTELEN" -ForegroundColor Red
}
```

### 3. ASSETS API TESZT

```powershell
# Előfeltétel: szükséges a token a loginból

$headers = @{
    "Authorization" = "Bearer $accessToken"
    "Content-Type" = "application/json"
}

$assetsResponse = Invoke-WebRequest -Uri "http://116.203.226.140:8000/api/v1/assets" `
    -Method GET `
    -Headers $headers `
    -UseBasicParsing

if ($assetsResponse.StatusCode -eq 200) {
    Write-Host "✅ Assets API MŰKÖDIK" -ForegroundColor Green
    $assetsData = $assetsResponse.Content | ConvertFrom-Json
    Write-Host "Eszközök száma: $($assetsData.items.Count)"
    $assetsData.items | ForEach-Object { Write-Host "  - $($_.name)" }
} else {
    Write-Host "❌ Assets API HIBA" -ForegroundColor Red
}
```

---

## 🧪 TELJES DIAGNOSZTIKAI SCRIPT

Mentsd el ezt `test_backend.ps1` fájlként és futtasd PowerShell-ben:

```powershell
$baseUrl = "http://116.203.226.140:8000/api"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CMMS Backend Diagnosztika" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. HEALTH CHECK
Write-Host "1. Health Check..." -ForegroundColor Yellow
try {
    $health = Invoke-WebRequest -Uri "$baseUrl/health/" -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ Szerver ELÉRHETŐ" -ForegroundColor Green
} catch {
    Write-Host "❌ Szerver NEM ELÉRHETŐ" -ForegroundColor Red
    Write-Host "   Error: $_" -ForegroundColor Red
    exit
}

# 2. LOGIN
Write-Host ""
Write-Host "2. Login tesztelése..." -ForegroundColor Yellow
try {
    $loginBody = @{
        username = "a.geleta"
        password = "Gele007ta"
    } | ConvertTo-Json

    $login = Invoke-WebRequest -Uri "$baseUrl/v1/auth/login" `
        -Method POST `
        -Headers @{"Content-Type" = "application/json"} `
        -Body $loginBody `
        -UseBasicParsing `
        -TimeoutSec 5

    $tokenData = $login.Content | ConvertFrom-Json
    $token = $tokenData.access_token
    Write-Host "✅ Login SIKERES" -ForegroundColor Green
    Write-Host "   Token: $($token.Substring(0, 30))..." -ForegroundColor Gray
} catch {
    Write-Host "❌ Login SIKERTELEN" -ForegroundColor Red
    Write-Host "   Error: $_" -ForegroundColor Red
    exit
}

# 3. ASSETS
Write-Host ""
Write-Host "3. Assets adatok lekérése..." -ForegroundColor Yellow
try {
    $headers = @{
        "Authorization" = "Bearer $token"
        "Content-Type" = "application/json"
    }

    $assets = Invoke-WebRequest -Uri "$baseUrl/v1/assets" `
        -Method GET `
        -Headers $headers `
        -UseBasicParsing `
        -TimeoutSec 5

    $assetsData = $assets.Content | ConvertFrom-Json
    Write-Host "✅ Assets API működik" -ForegroundColor Green
    Write-Host "   Eszközök száma: $($assetsData.items.Count)" -ForegroundColor Gray
    if ($assetsData.items.Count -gt 0) {
        $assetsData.items | Select-Object -First 5 | ForEach-Object {
            Write-Host "      - $($_.name) [$($_.status)]" -ForegroundColor Gray
        }
    }
} catch {
    Write-Host "❌ Assets API HIBA" -ForegroundColor Red
    Write-Host "   Error: $_" -ForegroundColor Red
}

# 4. WORKSHEETS
Write-Host ""
Write-Host "4. Worksheets adatok lekérése..." -ForegroundColor Yellow
try {
    $worksheets = Invoke-WebRequest -Uri "$baseUrl/v1/worksheets" `
        -Method GET `
        -Headers $headers `
        -UseBasicParsing `
        -TimeoutSec 5

    $worksheetData = $worksheets.Content | ConvertFrom-Json
    Write-Host "✅ Worksheets API működik" -ForegroundColor Green
    Write-Host "   Munkalapok száma: $($worksheetData.items.Count)" -ForegroundColor Gray
    if ($worksheetData.items.Count -gt 0) {
        $worksheetData.items | Select-Object -First 5 | ForEach-Object {
            Write-Host "      - $($_.title) [$($_.status)]" -ForegroundColor Gray
        }
    }
} catch {
    Write-Host "❌ Worksheets API HIBA" -ForegroundColor Red
    Write-Host "   Error: $_" -ForegroundColor Red
}

# 5. MACHINES
Write-Host ""
Write-Host "5. Machines adatok lekérése..." -ForegroundColor Yellow
try {
    $machines = Invoke-WebRequest -Uri "$baseUrl/v1/machines" `
        -Method GET `
        -Headers $headers `
        -UseBasicParsing `
        -TimeoutSec 5

    $machineData = $machines.Content | ConvertFrom-Json
    Write-Host "✅ Machines API működik" -ForegroundColor Green
    Write-Host "   Gépek száma: $($machineData.items.Count)" -ForegroundColor Gray
    if ($machineData.items.Count -gt 0) {
        $machineData.items | Select-Object -First 5 | ForEach-Object {
            Write-Host "      - $($_.name) [$($_.status)]" -ForegroundColor Gray
        }
    }
} catch {
    Write-Host "❌ Machines API HIBA" -ForegroundColor Red
    Write-Host "   Error: $_" -ForegroundColor Red
}

# 6. INVENTORY
Write-Host ""
Write-Host "6. Inventory adatok lekérése..." -ForegroundColor Yellow
try {
    $inventory = Invoke-WebRequest -Uri "$baseUrl/v1/inventory" `
        -Method GET `
        -Headers $headers `
        -UseBasicParsing `
        -TimeoutSec 5

    $inventoryData = $inventory.Content | ConvertFrom-Json
    Write-Host "✅ Inventory API működik" -ForegroundColor Green
    Write-Host "   Termékek száma: $($inventoryData.items.Count)" -ForegroundColor Gray
    if ($inventoryData.items.Count -gt 0) {
        $inventoryData.items | Select-Object -First 5 | ForEach-Object {
            Write-Host "      - $($_.name) [Qty: $($_.quantity)]" -ForegroundColor Gray
        }
    }
} catch {
    Write-Host "❌ Inventory API HIBA" -ForegroundColor Red
    Write-Host "   Error: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ DIAGNOSZTIKA BEFEJEZVE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
```

---

## 🎯 MIVEL KEZDJÜNK?

### 1. Futtasd a PowerShell diagnosztikát

```powershell
# PowerShell megnyitása és futtatása
cd E:\Artence_CMMS
.\test_backend.ps1
```

### 2. Nézd az eredményt

- ✅ Ha **mindent GREEN** → A backend OKÉ, az Android app-ot kell debugolni
- ❌ Ha valami RED → Szerver problémám van

### 3. Ha SZERVER OK, de az Android app üres

```
Akkor az App UI probléma:
1. ViewModel nem frissítődik
2. API token nem jó
3. Room adatbázis nem beszúrja az adatokat
```

---

## 📱 ANDROID APP DEBUGOLÁSA

Ha a szerver OK, de az app üres, nézd meg az Android Studio Logcat-ben:

```bash
# Nyisd meg Android Studiót
# View → Tool Windows → Logcat
# Szűrő: "AssetsViewModel" vagy "AssetRepository"

# Keress ERROR és Exception üzeneteket
```

**Tipikus hibák:**

```
E/AssetRepository: Failed to fetch assets: 401 Unauthorized
   → Login sikertelen, token lejárt

E/AssetRepository: Failed to fetch assets: 404 Not Found
   → API endpoint rossz (pl. /v1/assets helyett /assets)

E/AssetRepository: Connection refused
   → Backend szerver nem fut
```

---

## ✅ MEGOLDÁSOK

### Ha "401 Unauthorized"
```
1. Újra bejelentkezés
2. Token frissítés
3. Login endpoint tesztelése
```

### Ha "404 Not Found"
```
1. API routing ellenőrzése
2. Constants.kt BASE_URL ellenőrzése
3. Backend API végpontok validálása
```

### Ha "Connection refused"
```
1. Backend szerver indítása
2. Hálózati kapcsolat ellenőrzése
3. Firewall port 8000-re nyitva van-e?
```

---

**Futtasd a diagnosztikai scriptet és írd be az eredményt!**

