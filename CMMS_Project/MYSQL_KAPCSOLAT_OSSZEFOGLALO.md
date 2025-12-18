# MySQL Kapcsolat Állapot Összefoglaló

## Aktuális Helyzet

### Konfiguráció
- **Szerver**: 116.203.226.140
- **Port**: 3306
- **Adatbázis**: zedin_cmms
- **Felhasználó**: zedin_cmms
- **Jelszó**: Gele007ta...

### Kapcsolati Beállítások
A MySQL kapcsolat a következő fájlokban van konfigurálva:

1. **`config/app_config.py`** - Adatbázis konfiguráció
   - `DB_PROD_HOST`, `DB_PROD_PORT`, `DB_PROD_USER`, `DB_PROD_PASSWORD`, `DB_PROD_NAME`
   - Environment változókkal felülírható (`.env` fájl)

2. **`database/connection.py`** - SQLAlchemy kapcsolat
   - Connection pooling (pool_size=20, max_overflow=40)
   - Auto-reconnect (pool_pre_ping=True)
   - Timeout beállítások (connect_timeout=10s, read/write_timeout=60s)

## Probléma

### Közvetlen Kapcsolat
A Windows gépről közvetlenül **NEM elérhető** a MySQL szerver:
```
ConnectionRefusedError: [WinError 10061] Nem hozható létre kapcsolat, 
mert a célszámítógép már visszautasította a kapcsolatot
```

**Lehetséges okok:**
1. A MySQL szerver csak localhost-on hallgat (bind-address = 127.0.0.1)
2. A tűzfal blokkolja a 3306 portot
3. A MySQL szolgáltatás nem fut
4. A szerver csak bizonyos IP címekről engedélyezi a kapcsolatot

### SSH Kapcsolat
Az SSH kapcsolat is timeout-ot ad, ami azt jelenti:
- Az SSH kulcs nem működik megfelelően, VAGY
- A szerver nem elérhető SSH-n keresztül sem, VAGY
- A tűzfal blokkolja az SSH kapcsolatot is

## Megoldási Lehetőségek

### 1. SSH Tunnel Használata (Ajánlott)

Ha a MySQL csak localhost-on hallgat, SSH tunnel-t kell használni:

```powershell
# SSH tunnel létrehozása (PowerShell-ben)
ssh -i $env:USERPROFILE\.ssh\id_rsa_zedin -L 3307:localhost:3306 root@116.203.226.140 -N
```

Ezután a konfigurációban változtasd meg:
- `DB_PROD_HOST = "127.0.0.1"` vagy `"localhost"`
- `DB_PROD_PORT = 3307`

### 2. MySQL Szerver Állapot Ellenőrzése SSH-n Keresztül

Futtasd SSH-n keresztül a szerveren:

```bash
# SSH kapcsolat
ssh -i ~/.ssh/id_rsa_zedin root@116.203.226.140

# MySQL szolgáltatás állapot
systemctl status mysql

# MySQL újraindítás (ha nem fut)
systemctl restart mysql

# MySQL port ellenőrzés
netstat -tulpn | grep 3306

# MySQL konfiguráció ellenőrzése (bind-address)
grep bind-address /etc/mysql/my.cnf
# vagy
grep bind-address /etc/mysql/mysql.conf.d/mysqld.cnf
```

### 3. MySQL Bind-Address Módosítása

Ha a MySQL csak localhost-on hallgat, módosítsd a konfigurációt:

```bash
# Szerveren
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf

# Változtasd meg:
# bind-address = 127.0.0.1
# erre:
bind-address = 0.0.0.0

# MySQL újraindítás
sudo systemctl restart mysql

# Tűzfal port megnyitása (ha szükséges)
sudo ufw allow 3306/tcp
```

### 4. Tűzfal Beállítások

Ellenőrizd a tűzfal beállításokat:

```bash
# UFW állapot
sudo ufw status

# Port megnyitása
sudo ufw allow 3306/tcp

# MySQL user jogosultságok ellenőrzése
mysql -u root -p
SELECT user, host FROM mysql.user WHERE user='zedin_cmms';
```

## Tesztelési Scriptek

### 1. Lokális Teszt (SSH Tunnel után)
```python
# CMMS_Project/scripts/diagnose_mysql_issues.py
python scripts/diagnose_mysql_issues.py
```

### 2. SSH-n Keresztüli Teszt
```python
# CMMS_Project/scripts/check_mysql_via_ssh.py
python scripts/check_mysql_via_ssh.py
```

### 3. Egyszerű Kapcsolat Teszt
```python
from database.connection import engine
from sqlalchemy import text

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("✓ Kapcsolat működik!")
except Exception as e:
    print(f"✗ Kapcsolat hiba: {e}")
```

## Következő Lépések

1. **SSH kapcsolat javítása**
   - Ellenőrizd az SSH kulcsot
   - Teszteld az SSH kapcsolatot manuálisan
   - Ha működik, használj SSH tunnel-t

2. **MySQL szerver állapot ellenőrzése**
   - SSH-z be a szerverre
   - Ellenőrizd, hogy fut-e a MySQL
   - Nézd meg a MySQL konfigurációt

3. **Kapcsolat tesztelése**
   - SSH tunnel után teszteld a lokális kapcsolatot
   - Vagy módosítsd a MySQL bind-address beállítását

## Hasznos Parancsok

### Windows PowerShell
```powershell
# SSH kapcsolat teszt
ssh -i $env:USERPROFILE\.ssh\id_rsa_zedin root@116.203.226.140

# SSH tunnel (egy terminálban)
ssh -i $env:USERPROFILE\.ssh\id_rsa_zedin -L 3307:localhost:3306 root@116.203.226.140 -N

# Port tesztelés
Test-NetConnection -ComputerName 116.203.226.140 -Port 3306
```

### Linux/Mac
```bash
# SSH kapcsolat
ssh -i ~/.ssh/id_rsa_zedin root@116.203.226.140

# SSH tunnel
ssh -i ~/.ssh/id_rsa_zedin -L 3307:localhost:3306 root@116.203.226.140 -N

# Port tesztelés
nc -zv 116.203.226.140 3306
```

## Dokumentáció

- `docs/SSH_MYSQL_FIX_GUIDE.md` - SSH-n keresztüli MySQL javítás
- `scripts/diagnose_mysql_issues.py` - MySQL diagnosztikai script
- `scripts/check_mysql_via_ssh.py` - SSH-n keresztüli MySQL ellenőrzés
- `scripts/fix_mysql_server.py` - MySQL szerver javítás SSH-n keresztül




