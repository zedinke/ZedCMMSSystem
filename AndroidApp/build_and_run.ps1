#!/usr/bin/env pwsh
# =========================================================
# ANDROID CMMS MVP - BUILD & EMULATOR AUTOMATION (PowerShell)
# =========================================================
# Futtatas: .\build_and_run.ps1
# =========================================================

Write-Host ""
Write-Host "=== ANDROID CMMS MVP - BUILD & EMULATOR AUTOMATION ===" -ForegroundColor Green
Write-Host ""

function Use-AndroidStudioJdk {
    param(
        [string[]]$CandidateRoots = @(
            "C:\\Program Files\\Android\\Android Studio",
            "C:\\Users\\$env:USERNAME\\AppData\\Local\\Programs\\Android Studio"
        )
    )
    foreach ($root in $CandidateRoots) {
        $jbr = Join-Path $root "jbr"
        $jdkBin = Join-Path $jbr "bin"
        if (Test-Path $jdkBin) {
            Write-Host "Android Studio JDK talalva: $jbr" -ForegroundColor Green
            $env:JAVA_HOME = $jbr
            if ($env:Path -notlike "*${jdkBin}*") {
                $env:Path = "$jdkBin;" + $env:Path
            }
            return $true
        }
    }
    return $false
}

# =========================================================
# STEP 1: Check Prerequisites
# =========================================================
Write-Host "[1/6] Elofeltetelek ellenorzese..." -ForegroundColor Cyan

# Try Java
$javaOK = $false
try {
    $javaVersion = java -version 2>&1
    $javaOK = $true
    Write-Host "OK: Java telepitve (PATH)" -ForegroundColor Green
} catch {
    Write-Host "FIGYELEM: Java nem elerheto a PATH-ban, probalom az Android Studio JDK-t beallitani..." -ForegroundColor Yellow
}

if (-not $javaOK) {
    $studioSet = Use-AndroidStudioJdk
    if (-not $studioSet) {
        Write-Host "HIBA: Nem talalhato az Android Studio JDK (jbr). Telepitsd az Android Studio-t vagy allitsd be a JAVA_HOME-t." -ForegroundColor Red
        Write-Host "Tipikus eleresi ut: C\\Program Files\\Android\\Android Studio\\jbr" -ForegroundColor Gray
        # Nem lepunk ki, mert Gradle a wrapperrel probalhat futni org.gradle.java.home beallitassal
    } else {
        try {
            $javaVersion = java -version 2>&1
            Write-Host "OK: Android Studio JDK beallitva" -ForegroundColor Green
            $javaOK = $true
        } catch {
            Write-Host "FIGYELEM: A JDK beallitva, de a 'java -version' nem fut. Folytatom a buildet a Gradle wrapperrel." -ForegroundColor Yellow
        }
    }
}

# Check Gradle
if (-not (Test-Path "gradlew.bat")) {
    Write-Host "HIBA: gradlew.bat nem talalhato!" -ForegroundColor Red
    Write-Host "Biztos, hogy az AndroidApp mappaban vagy?" -ForegroundColor Yellow
    exit 1
}
Write-Host "OK: Gradle wrapper elerheto" -ForegroundColor Green

# =========================================================
# STEP 2: Clean Build
# =========================================================
Write-Host ""
Write-Host "[2/6] Clean build..." -ForegroundColor Cyan
& .\gradlew.bat --no-daemon clean

if ($LASTEXITCODE -ne 0) {
    Write-Host "HIBA: Clean sikertelen!" -ForegroundColor Red
    exit 1
}
Write-Host "OK: Clean OK" -ForegroundColor Green

# =========================================================
# STEP 3: Build Debug APK
# =========================================================
Write-Host ""
Write-Host "[3/6] Debug APK buildelese..." -ForegroundColor Cyan
Write-Host "Varakozas... (2-3 perc)" -ForegroundColor Yellow

& .\gradlew.bat --no-daemon assembleDebug

if ($LASTEXITCODE -ne 0) {
    Write-Host "HIBA: Build sikertelen!" -ForegroundColor Red
    exit 1
}

# Check APK
$apkPath = "app\build\outputs\apk\debug\app-debug.apk"
if (Test-Path $apkPath) {
    $apkSize = (Get-Item $apkPath).Length / 1MB
    Write-Host ("OK: Build OK - APK merete: {0} MB" -f [Math]::Round($apkSize, 2)) -ForegroundColor Green
} else {
    Write-Host "HIBA: APK nem talalhato!" -ForegroundColor Red
    exit 1
}

# =========================================================
# STEP 4: Check Emulator/Devices
# =========================================================
Write-Host ""
Write-Host "[4/6] Eszkozok ellenorzese..." -ForegroundColor Cyan

$devices = & adb devices 2>$null | Select-Object -Skip 1 | Where-Object { $_ -match "emulator|device" }

if ($devices.Count -eq 0) {
    Write-Host "FIGYELEM: Nincs csatlakoztatott eszkoz!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Emulator inditasa a Device Manager-bol:" -ForegroundColor Yellow
    Write-Host "  1. Android Studio megnyitasa" -ForegroundColor Gray
    Write-Host "  2. Tools > Device Manager" -ForegroundColor Gray
    Write-Host "  3. Launch in Emulator" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Vagy parancssorbol:" -ForegroundColor Yellow
    Write-Host '  emulator -avd "Pixel 7 Pro API 34"' -ForegroundColor Gray
    Write-Host ""
    Read-Host "Nyomj Enter-t amikor az emulator elindul"
} else {
    Write-Host "OK: Eszkozok talalva:" -ForegroundColor Green
    foreach ($device in $devices) {
        Write-Host "   $device" -ForegroundColor Gray
    }
}

# =========================================================
# STEP 5: Install APK
# =========================================================
Write-Host ""
Write-Host "[5/6] APK telepitese..." -ForegroundColor Cyan

& adb install -r $apkPath

if ($LASTEXITCODE -ne 0) {
    Write-Host "HIBA: Telepites sikertelen!" -ForegroundColor Red
    exit 1
}
Write-Host "OK: Telepites OK" -ForegroundColor Green

# =========================================================
# STEP 6: Launch App
# =========================================================
Write-Host ""
Write-Host "[6/6] Alkalmazas inditasa..." -ForegroundColor Cyan
& adb shell am start -n com.artence.cmms/.ui.screens.login.LoginActivity

Start-Sleep -Seconds 2

# =========================================================
# SUCCESS
# =========================================================
Write-Host ""
Write-Host "=== BUILD & INSTALL SIKERES ===" -ForegroundColor Green
Write-Host "Alkalmazas az emulator-on fut."
Write-Host "LOGIN ADATOK:"
Write-Host "  - Email: admin@example.com"
Write-Host "  - Password: Admin123456"
Write-Host "LOGCAT: View > Tool Windows > Logcat"
Write-Host "Utmutatok: QUICK_START.md es README.md"
Write-Host ""
