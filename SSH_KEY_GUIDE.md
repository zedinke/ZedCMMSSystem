# 🔑 SSH KULCS KEZELÉSI ÚTMUTATÓ

## 📌 SSH Kulcs Helye

```
Privát kulcs: C:\Users\gelea\.ssh\cmms_key
Publikus kulcs: C:\Users\gelea\.ssh\cmms_key.pub
```

## 🔓 SSH Kulcs Használata

### 1. Szerver Elérés SSH Kulccsal

```bash
ssh -i "C:\Users\gelea\.ssh\cmms_key" -o StrictHostKeyChecking=no root@116.203.226.140
```

### 2. Fájl Feltöltés (SCP)

```bash
# Egyedi fájl
scp -i "C:\Users\gelea\.ssh\cmms_key" -o StrictHostKeyChecking=no \
  "E:\Artence_CMMS\CMMS_Project\api\server.py" \
  root@116.203.226.140:/opt/cmms-backend/api/

# Egész könyvtár
scp -r -i "C:\Users\gelea\.ssh\cmms_key" -o StrictHostKeyChecking=no \
  "E:\Artence_CMMS\CMMS_Project\api" \
  root@116.203.226.140:/opt/cmms-backend/
```

### 3. Szerver Parancs Futtatása SSH-n Keresztül

```bash
ssh -i "C:\Users\gelea\.ssh\cmms_key" root@116.203.226.140 "ps aux | grep uvicorn"
```

### 4. SSH Config File (Opcionális - Gyorsabb Access)

Hozz létre vagy szerkeszd meg a `C:\Users\gelea\.ssh\config` fájlt:

```
Host cmms_server
    HostName 116.203.226.140
    User root
    IdentityFile C:\Users\gelea\.ssh\cmms_key
    StrictHostKeyChecking no
    ConnectTimeout 10
```

Utána egyszerűen:
```bash
ssh cmms_server
```

---

## 🚀 BACKEND INDÍTÁS SSH KULCCSAL (LÉPÉSRŐL LÉPÉSRE)

### LÉPÉS 1: SSH Csatlakozás

```bash
ssh -i "C:\Users\gelea\.ssh\cmms_key" root@116.203.226.140
```

### LÉPÉS 2: Backend Könyvtárba Navigálás

```bash
cd /opt/cmms-backend
```

### LÉPÉS 3: Cache Törlés

```bash
find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null
find . -name '*.pyc' -delete 2>/dev/null
pkill -9 uvicorn 2>/dev/null
```

### LÉPÉS 4: Aktuális Backend Indítása

**Opció A: Nohup (Háttérben, reconnect után is fut)**
```bash
nohup bash -c 'export PYTHONPATH=/opt/cmms-backend && \
/opt/cmms-backend/venv/bin/python -m uvicorn api.server:app \
--host 0.0.0.0 --port 8000' > /tmp/backend.log 2>&1 &

echo "Backend started in background"
```

**Opció B: Screen Session (Interaktív, később vissza lehet csatlakozni)**
```bash
screen -S cmms_backend -d -m bash -c '\
export PYTHONPATH=/opt/cmms-backend && \
cd /opt/cmms-backend && \
/opt/cmms-backend/venv/bin/python -m uvicorn api.server:app \
--host 0.0.0.0 --port 8000'

echo "Backend started in screen session 'cmms_backend'"
```

### LÉPÉS 5: Backend Ellenőrzése

```bash
# Szerveren belül (localhost)
curl http://localhost:8000/api/health/

# Külső gépről
curl http://116.203.226.140:8000/api/health/
```

### LÉPÉS 6: Log Megtekintése

**Ha nohup-ot használtál:**
```bash
tail -f /tmp/backend.log
```

**Ha screen session-t használtál:**
```bash
screen -r cmms_backend
# Kilépés: CTRL+A majd D
```

---

## ✅ GYORS CSATORNÁK

### Teljes Backend Indítás Egy Parancsban (SSH-ból)

```bash
ssh -i "C:\Users\gelea\.ssh\cmms_key" root@116.203.226.140 \
"cd /opt/cmms-backend && \
pkill -9 uvicorn 2>/dev/null; \
find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null; \
find . -name '*.pyc' -delete 2>/dev/null; \
nohup bash -c 'export PYTHONPATH=/opt/cmms-backend && \
/opt/cmms-backend/venv/bin/python -m uvicorn api.server:app \
--host 0.0.0.0 --port 8000' > /tmp/backend.log 2>&1 &"

echo "Backend indítva! 10 másodperc múlva teszt..."
sleep 10
curl http://116.203.226.140:8000/api/health/
```

### Backend Status Check

```bash
ssh -i "C:\Users\gelea\.ssh\cmms_key" root@116.203.226.140 \
"ps aux | grep uvicorn | grep -v grep && echo 'Backend FUT' || echo 'Backend NEM FUT'"
```

### Backend Log Megtekintése (Valós Idő)

```bash
ssh -i "C:\Users\gelea\.ssh\cmms_key" root@116.203.226.140 "tail -f /tmp/backend.log"
```

---

## 🔒 SSH KULCS BIZTONSÁGI MEGJEGYZÉSEK

1. **Soha ne oszd meg** a privát kulcsot (`cmms_key`)
2. **Csak te** olvasd a privát kulcsot: `chmod 600 ~/.ssh/cmms_key`
3. **Regular backup**: A privát kulcs mentése biztonságos helyre
4. **Key Rotation**: Időnként új kulcs generálása:
   ```bash
   ssh-keygen -t ed25519 -f "C:\Users\gelea\.ssh\cmms_key_new" -N ""
   ```

---

## 🆘 HIBAKERESÉS

### SSH: "Permission denied (publickey)"
- Ellenőrizd: `C:\Users\gelea\.ssh\cmms_key` létezik-e
- SSH Ügynök: `eval $(ssh-agent -s)` és `ssh-add "C:\Users\gelea\.ssh\cmms_key"`

### SSH: "Connection timed out"
- Szerver lehet offline
- Firewall blokkolhatja az 22-es portot
- IP cím megváltozott

### Backend: "Address already in use"
- `pkill -9 uvicorn` - összes uvicorn leállítása
- Vagy más port: `--port 8001`

### Backend: "ModuleNotFoundError"
- PYTHONPATH beállítás: `export PYTHONPATH=/opt/cmms-backend`
- `/opt/cmms-backend`-ből kell indítani

---

**Dátum**: 2025.12.15  
**Szerző**: AI Assistant  
**Verzió**: 1.0

🔑 **SSH Kulcs Kész Használatra!**

