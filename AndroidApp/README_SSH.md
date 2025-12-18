# SSH Kapcsolat a Backend Szerverhez

## 1. SSH kulcs generálása

Futtasd PowerShell-ben:

```powershell
.\generate_ssh_key.ps1
```

Ez létrehozza a `%USERPROFILE%\.ssh\zedhosting_server_ai2` kulcsot.

## 2. Publikus kulcs hozzáadása a szerverhez

### Opció A: ssh-copy-id használata (ha telepítve van)

```powershell
ssh-copy-id -i "$env:USERPROFILE\.ssh\zedhosting_server_ai2.pub" user@116.203.226.140
```

### Opció B: Manuális hozzáadás

1. Másold ki a publikus kulcs tartalmát:
```powershell
Get-Content "$env:USERPROFILE\.ssh\zedhosting_server_ai2.pub"
```

2. SSH-z be a szerverre (jelszóval):
```powershell
ssh user@116.203.226.140
```

3. A szerveren futtasd:
```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo "ITT_A_PUBLIKUS_KULCS_TARTALMA" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

## 3. Kapcsolódás a szerverhez

```powershell
.\connect_to_server.ps1
```

Vagy manuálisan:
```powershell
ssh -i "$env:USERPROFILE\.ssh\zedhosting_server_ai2" user@116.203.226.140
```

## 4. Backend szerver állapot ellenőrzése

```powershell
.\check_backend_server.ps1
```

Ez ellenőrzi:
- Systemd service állapot
- API health check
- Logok
- Port állapot
- Python folyamatok

## Konfiguráció módosítása

A scriptekben módosíthatod:
- `$User` - SSH felhasználónév (alapértelmezett: "root")
- `$Server` - Szerver IP (alapértelmezett: "116.203.226.140")
- `$KeyPath` - Kulcs útvonala

## Hibaelhárítás

### "Permission denied (publickey)"
- Ellenőrizd, hogy a publikus kulcs hozzá lett-e adva a szerver `authorized_keys` fájlhoz
- Ellenőrizd a kulcs jogosultságait: `icacls "$env:USERPROFILE\.ssh\zedhosting_server_ai2"`

### "Connection refused"
- Ellenőrizd, hogy a szerver elérhető-e: `Test-NetConnection -ComputerName 116.203.226.140 -Port 22`
- Ellenőrizd a tűzfal beállításokat

### "Host key verification failed"
- Töröld a régi kulcsot: `ssh-keygen -R 116.203.226.140`

