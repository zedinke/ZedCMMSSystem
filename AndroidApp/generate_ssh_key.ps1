# SSH kulcs generálása a szerverhez
# Futtatás: PowerShell-ben: .\generate_ssh_key.ps1

Write-Host "SSH kulcs generálása a zedhosting szerverhez..." -ForegroundColor Green

# Ellenőrizzük, hogy létezik-e a .ssh könyvtár
$sshDir = "$env:USERPROFILE\.ssh"
if (-not (Test-Path $sshDir)) {
    New-Item -ItemType Directory -Path $sshDir -Force | Out-Null
    Write-Host "✓ .ssh könyvtár létrehozva" -ForegroundColor Green
}

# SSH kulcs generálása
$keyPath = "$sshDir\zedhosting_server_ai2"
Write-Host "Kulcs generálása: $keyPath" -ForegroundColor Yellow

ssh-keygen -t ed25519 -f $keyPath -N '""' -C "cmms-backend-server"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ SSH kulcs sikeresen generálva!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Publikus kulcs tartalma:" -ForegroundColor Cyan
    Write-Host "----------------------------------------" -ForegroundColor Gray
    Get-Content "$keyPath.pub"
    Write-Host "----------------------------------------" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Következő lépések:" -ForegroundColor Yellow
    Write-Host "1. Másold ki a fenti publikus kulcsot" -ForegroundColor White
    Write-Host "2. Add hozzá a szerver authorized_keys fájlhoz:" -ForegroundColor White
    Write-Host "   ssh-copy-id -i $keyPath.pub user@116.203.226.140" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Vagy manuálisan:" -ForegroundColor White
    Write-Host "   cat $keyPath.pub | ssh user@116.203.226.140 'cat >> ~/.ssh/authorized_keys'" -ForegroundColor Cyan
} else {
    Write-Host "✗ Hiba történt a kulcs generálása során!" -ForegroundColor Red
}

