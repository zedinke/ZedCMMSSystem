# 🔧 BACKEND SZERVER JAVÍTÁS - VÉGSŐ MEGOLDÁS

## 📊 JEL ENLEGI HELYZET

✅ **Sikerült elérni**: SSH kapcsolat működik  
✅ **Feltöltve**: api, services, database, config, utils, localization modulok  
❌ **Probléma**: Backend szerver NEM INDUL - hiányzik `get_user_language` függvény

## 🎯 AZONNALI MEGOLDÁS (SSH-ban)

### LÉPÉS 1: Csatlakozz SSH-val

```bash
ssh root@116.203.226.140
# Jelszó: Gele007ta...
```

### LÉPÉS 2: Töltsd fel az összes fájlt újra

```bash
cd /opt/cmms-backend

# Backup a régiről
mv api api_backup_$(date +%Y%m%d_%H%M%S)
mv services services_backup_$(date +%Y%m%d_%H%M%S)

# Tölts fel TELJES projektet a PC-dről
# Windows-ról SCP-vel (új CMD ablakból):
```

**Windows CMD-ben**:
```batch
cd E:\Artence_CMMS
scp -r CMMS_Project\api root@116.203.226.140:/opt/cmms-backend/
scp -r CMMS_Project\services root@116.203.226.140:/opt/cmms-backend/
scp -r CMMS_Project\database root@116.203.226.140:/opt/cmms-backend/
scp -r CMMS_Project\config root@116.203.226.140:/opt/cmms-backend/
scp -r CMMS_Project\utils root@116.203.226.140:/opt/cmms-backend/
scp -r CMMS_Project\localization root@116.203.226.140:/opt/cmms-backend/
```

### LÉPÉS 3: Indítsd el a backend szervert (SSH-ban)

```bash
cd /opt/cmms-backend

# Állíts le minden régi uvicorn folyamatot
pkill -9 -f uvicorn

# Indítsd el a szervert PYTHONPATH-tal
PYTHONPATH=/opt/cmms-backend \
  /opt/cmms-backend/venv/bin/python -m uvicorn \
  api.server:app \
  --host 0.0.0.0 \
  --port 8000 \
  > /tmp/backend.log 2>&1 &

# Ellenőrizd, fut-e
ps aux | grep uvicorn

# Nézd meg a log-ot
tail -f /tmp/backend.log
```

### LÉPÉS 4: Teszteld a backend-et

```bash
# SSH-ból
curl http://localhost:8000/api/health/

# Windows-ról
curl http://116.203.226.140:8000/api/health/
```

**Elvárt válasz**:
```json
{"status":"ok"}
```

---

## 🔄 ALTERNATÍV MEGOLDÁS: Systemd Service

Ha gyakran újra kell indítani, használj systemd service-t:

### Service fájl létrehozása (SSH-ban)

```bash
cat > /etc/systemd/system/cmms-backend.service << 'EOF'
[Unit]
Description=CMMS Backend API
After=network.target mysql.service

[Service]
Type=simple
User=cmms
WorkingDirectory=/opt/cmms-backend
Environment="PYTHONPATH=/opt/cmms-backend"
ExecStart=/opt/cmms-backend/venv/bin/python -m uvicorn api.server:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Engedélyezd és indítsd el
systemctl daemon-reload
systemctl enable cmms-backend
systemctl start cmms-backend

# Ellenőrizd a státuszt
systemctl status cmms-backend

# Nézd meg a logokat
journalctl -u cmms-backend -f
```

---

## 📱 ANDROID APP FRISSÍTÉSE

Miután a backend fut, az Android app automatikusan csatlakozni fog!

### Ellenőrzőlista:

1. ✅ Backend szerver fut: `ps aux | grep uvicorn`
2. ✅ Health endpoint válaszol: `curl http://116.203.226.140:8000/api/health/`
3. ✅ Login teszt: 
```bash
curl -X POST http://116.203.226.140:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"a.geleta","password":"Gele007ta"}'
```

4. ✅ Android app újraindítása
5. ✅ Login az appban: a.geleta / Gele007ta
6. ✅ Adatok megjelennek!

---

## 🆘 HA MÉG MINDIG NEM MŰKÖDIK

### Probléma: "get_user_language not defined"

**Megoldás**: Az `api/dependencies.py` hiányos. Másold fel TELJES fájlt:

```bash
# Windows CMD-ben
scp E:\Artence_CMMS\CMMS_Project\api\dependencies.py root@116.203.226.140:/opt/cmms-backend/api/

# Ellenőrizd
ssh root@116.203.226.140 "grep -n 'def get_user_language' /opt/cmms-backend/api/dependencies.py"
```

Kell látszódjon valami ilyesmi:
```
89:def get_user_language(
```

### Probléma: "No module named 'services'"

**Megoldás**: PYTHONPATH beállítás:

```bash
export PYTHONPATH=/opt/cmms-backend
python -c "from services.user_service import get_all_users; print('OK')"
```

### Probléma: Port 8000 already in use

**Megoldás**:
```bash
# Találd meg a folyamatot
lsof -i :8000

# Állítsd le
kill -9 <PID>

# Vagy összes uvicorn leállítása
pkill -9 -f uvicorn
```

---

## ✅ GYORS ELLENŐRZÉS (1 perc)

```bash
# 1. SSH csatlakozás
ssh root@116.203.226.140

# 2. Szerver státusz
ps aux | grep uvicorn | grep -v grep

# 3. Ha NEM fut, indítsd el:
cd /opt/cmms-backend && PYTHONPATH=/opt/cmms-backend /opt/cmms-backend/venv/bin/python -m uvicorn api.server:app --host 0.0.0.0 --port 8000 &

# 4. Health check
curl http://localhost:8000/api/health/

# 5. Kilépés
exit
```

---

## 📝 EREDMÉNY DOKUMENTÁLÁSA

Ha sikerült elindítani:

1. ✅ Backend fut: `systemctl status cmms-backend` vagy `ps aux | grep uvicorn`
2. ✅ Log helye: `/tmp/backend.log` vagy `journalctl -u cmms-backend`
3. ✅ Android app kapcsolódik: URL = `http://116.203.226.140:8000/api/`

---

**Következő lépés**: Ha még SSH-ban vagy, futtasd le a LÉPÉS 3-at és nézd meg a log-ot!

**Dátum**: 2025.12.15  
**Státusz**: Backend fájlok feltöltve, szerver indítás szükséges  
**Utolsó hiba**: `get_user_language not defined` (dependencies.py hiányos)

