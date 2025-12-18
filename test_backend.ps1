#!/usr/bin/env powershell
# CMMS Backend Diagnosztika - PowerShell verzió
# Ez a script ellenőrzi, hogy a backend szerver és az API végpontok működnek-e

$baseUrl = "http://116.203.226.140:8000/api"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CMMS Backend Diagnosztika" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. HEALTH CHECK
Write-Host "1. Health Check..." -ForegroundColor Yellow
try {
    $health = Invoke-WebRequest -Uri "$baseUrl/health/" -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✅ Szerver ELÉRHETŐ" -ForegroundColor Green
} catch {
    Write-Host "❌ Szerver NEM ELÉRHETŐ!" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Lehetséges okok:" -ForegroundColor Yellow
    Write-Host "  1. Backend szerver nem fut" -ForegroundColor Yellow
    Write-Host "  2. IP-cím rossz (116.203.226.140)" -ForegroundColor Yellow
    Write-Host "  3. Hálózati probléma" -ForegroundColor Yellow
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
        -TimeoutSec 5 `
        -ErrorAction Stop

    $tokenData = $login.Content | ConvertFrom-Json
    $token = $tokenData.access_token
    Write-Host "✅ Login SIKERES" -ForegroundColor Green
    Write-Host "   User: $($tokenData.username)" -ForegroundColor Gray
    Write-Host "   Role: $($tokenData.role_name)" -ForegroundColor Gray
    Write-Host "   Token: $($token.Substring(0, 30))..." -ForegroundColor Gray
} catch {
    Write-Host "❌ Login SIKERTELEN!" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Lehetséges okok:" -ForegroundColor Yellow
    Write-Host "  1. Hibás felhasználónév/jelszó" -ForegroundColor Yellow
    Write-Host "  2. User nem létezik az adatbázisban" -ForegroundColor Yellow
    Write-Host "  3. Backend DB hiba" -ForegroundColor Yellow
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
        -TimeoutSec 5 `
        -ErrorAction Stop

    $assetsData = $assets.Content | ConvertFrom-Json
    Write-Host "✅ Assets API működik" -ForegroundColor Green
    Write-Host "   Eszközök száma: $($assetsData.items.Count)" -ForegroundColor Gray
    if ($assetsData.items.Count -gt 0) {
        Write-Host "   Minta eszközök:" -ForegroundColor Gray
        $assetsData.items | Select-Object -First 3 | ForEach-Object {
            Write-Host "      - $($_.name) [$($_.status)]" -ForegroundColor Gray
        }
    }
} catch {
    Write-Host "❌ Assets API HIBA!" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
}

# 4. WORKSHEETS
Write-Host ""
Write-Host "4. Worksheets adatok lekérése..." -ForegroundColor Yellow
try {
    $worksheets = Invoke-WebRequest -Uri "$baseUrl/v1/worksheets" `
        -Method GET `
        -Headers $headers `
        -UseBasicParsing `
        -TimeoutSec 5 `
        -ErrorAction Stop

    $worksheetData = $worksheets.Content | ConvertFrom-Json
    Write-Host "✅ Worksheets API működik" -ForegroundColor Green
    Write-Host "   Munkalapok száma: $($worksheetData.items.Count)" -ForegroundColor Gray
    if ($worksheetData.items.Count -gt 0) {
        Write-Host "   Minta munkalapok:" -ForegroundColor Gray
        $worksheetData.items | Select-Object -First 3 | ForEach-Object {
            Write-Host "      - $($_.title) [$($_.status)]" -ForegroundColor Gray
        }
    }
} catch {
    Write-Host "❌ Worksheets API HIBA!" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
}

# 5. MACHINES
Write-Host ""
Write-Host "5. Machines adatok lekérése..." -ForegroundColor Yellow
try {
    $machines = Invoke-WebRequest -Uri "$baseUrl/v1/machines" `
        -Method GET `
        -Headers $headers `
        -UseBasicParsing `
        -TimeoutSec 5 `
        -ErrorAction Stop

    $machineData = $machines.Content | ConvertFrom-Json
    Write-Host "✅ Machines API működik" -ForegroundColor Green
    Write-Host "   Gépek száma: $($machineData.items.Count)" -ForegroundColor Gray
    if ($machineData.items.Count -gt 0) {
        Write-Host "   Minta gépek:" -ForegroundColor Gray
        $machineData.items | Select-Object -First 3 | ForEach-Object {
            Write-Host "      - $($_.name) [$($_.status)]" -ForegroundColor Gray
        }
    }
} catch {
    Write-Host "❌ Machines API HIBA!" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
}

# 6. INVENTORY
Write-Host ""
Write-Host "6. Inventory adatok lekérése..." -ForegroundColor Yellow
try {
    $inventory = Invoke-WebRequest -Uri "$baseUrl/v1/inventory" `
        -Method GET `
        -Headers $headers `
        -UseBasicParsing `
        -TimeoutSec 5 `
        -ErrorAction Stop

    $inventoryData = $inventory.Content | ConvertFrom-Json
    Write-Host "✅ Inventory API működik" -ForegroundColor Green
    Write-Host "   Termékek száma: $($inventoryData.items.Count)" -ForegroundColor Gray
    if ($inventoryData.items.Count -gt 0) {
        Write-Host "   Minta termékek:" -ForegroundColor Gray
        $inventoryData.items | Select-Object -First 3 | ForEach-Object {
            Write-Host "      - $($_.name) [Qty: $($_.quantity)]" -ForegroundColor Gray
        }
    }
} catch {
    Write-Host "❌ Inventory API HIBA!" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
}

# 7. PM TASKS
Write-Host ""
Write-Host "7. PM Tasks adatok lekérése..." -ForegroundColor Yellow
try {
    $pmTasks = Invoke-WebRequest -Uri "$baseUrl/v1/pm/tasks" `
        -Method GET `
        -Headers $headers `
        -UseBasicParsing `
        -TimeoutSec 5 `
        -ErrorAction Stop

    $pmData = $pmTasks.Content | ConvertFrom-Json
    Write-Host "✅ PM Tasks API működik" -ForegroundColor Green
    Write-Host "   PM Tasks száma: $($pmData.items.Count)" -ForegroundColor Gray
    if ($pmData.items.Count -gt 0) {
        Write-Host "   Minta PM tasks:" -ForegroundColor Gray
        $pmData.items | Select-Object -First 3 | ForEach-Object {
            Write-Host "      - $($_.title) [Frequency: $($_.frequency)]" -ForegroundColor Gray
        }
    }
} catch {
    Write-Host "❌ PM Tasks API HIBA!" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
}

# ÖSSZEFOGLALÁS
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ DIAGNOSZTIKA BEFEJEZVE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Következő lépés:" -ForegroundColor Yellow
Write-Host "  1. Ha az összes API működik (✅), akkor az Android app-ot kell debugolni" -ForegroundColor Gray
Write-Host "  2. Az Android Studio Logcat-ben nézd meg a hibaüzeneteket" -ForegroundColor Gray
Write-Host "  3. Ellenőrizd a Constants.kt BASE_URL-t" -ForegroundColor Gray
Write-Host ""

Write-Host "Nyomj ENTER-t a kilépéshez..."
Read-Host

