# Backend szerver állapot ellenőrzése SSH-n keresztül
# Futtatás: PowerShell-ben: .\check_backend_server.ps1

param(
    [string]$User = "root",  # Változtasd meg a felhasználónévre
    [string]$Server = "116.203.226.140",
    [string]$KeyPath = "$env:USERPROFILE\.ssh\zedhosting_server_ai2"
)

Write-Host "Backend szerver állapot ellenőrzése..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Gray
Write-Host ""

# SSH parancs futtatása a szerveren
$sshCommand = @"
# Systemd service állapot
echo "=== CMMS API Service Status ==="
systemctl status cmms-api --no-pager -l || echo "Service nem található"

echo ""
echo "=== API Health Check ==="
curl -s http://localhost:8000/api/health/ || echo "API nem elérhető"

echo ""
echo "=== Utolsó 20 log sor ==="
journalctl -u cmms-api -n 20 --no-pager || echo "Log nem elérhető"

echo ""
echo "=== Port 8000 ellenőrzés ==="
netstat -tulpn | grep 8000 || ss -tulpn | grep 8000 || echo "Port információ nem elérhető"

echo ""
echo "=== Python folyamatok ==="
ps aux | grep -E "(python|uvicorn|cmms)" | grep -v grep || echo "Nincs Python folyamat"

echo ""
echo "=== Working directory ==="
if [ -d "/opt/cmms-backend" ]; then
    ls -la /opt/cmms-backend/ | head -10
else
    echo "/opt/cmms-backend nem található"
fi
"@

Write-Host "SSH parancs futtatása..." -ForegroundColor Cyan
ssh -i $KeyPath $User@$Server $sshCommand

Write-Host ""
Write-Host "========================================" -ForegroundColor Gray
Write-Host "Ellenőrzés befejezve." -ForegroundColor Green

