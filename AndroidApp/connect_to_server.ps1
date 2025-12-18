# SSH kapcsolat a backend szerverhez
# Futtatás: PowerShell-ben: .\connect_to_server.ps1

param(
    [string]$User = "root",  # Változtasd meg a felhasználónévre
    [string]$Server = "116.203.226.140",
    [string]$KeyPath = "$env:USERPROFILE\.ssh\zedhosting_server_ai2"
)

Write-Host "SSH kapcsolat létesítése a szerverhez..." -ForegroundColor Green
Write-Host "Szerver: $Server" -ForegroundColor Yellow
Write-Host "Felhasználó: $User" -ForegroundColor Yellow
Write-Host "Kulcs: $KeyPath" -ForegroundColor Yellow
Write-Host ""

# Ellenőrizzük, hogy létezik-e a kulcs
if (-not (Test-Path $KeyPath)) {
    Write-Host "✗ SSH kulcs nem található: $KeyPath" -ForegroundColor Red
    Write-Host "Futtasd először: .\generate_ssh_key.ps1" -ForegroundColor Yellow
    exit 1
}

# SSH kapcsolat létesítése
Write-Host "Kapcsolódás..." -ForegroundColor Cyan
ssh -i $KeyPath $User@$Server

