# MySQL Szerver Javítás - SSH Útmutató

## 🔴 KRITIKUS PROBLÉMA

A MySQL szerver nem elérhető. Valószínűleg leállt a régi tranzakciók kill-elése után, vagy a /tmp könyvtár tele van.

## 📋 LÉPÉSEK A JAVÍTÁSHOZ

### 1. SSH Kapcsolat a Szerverhez

```bash
ssh -i ~/.ssh/id_rsa_zedin root@116.203.226.140
```

VAGY ha jelszó szükséges:
```bash
ssh root@116.203.226.140
```

### 2. MySQL Állapot Ellenőrzése

```bash
# Ellenőrizd, hogy fut-e a MySQL
systemctl status mysql

# VAGY
service mysql status
```

### 3. /tmp Könyvtár Ellenőrzése

```bash
# Lemezterület ellenőrzés
df -h /tmp

# Tmp könyvtár tartalma
ls -lah /tmp | head -20

# Legnagyobb fájlok
du -sh /tmp/* 2>/dev/null | sort -h | tail -10
```

### 4. MySQL Újraindítása

```bash
# MySQL újraindítása
systemctl restart mysql

# VAGY ha systemctl nem elérhető
service mysql restart

# Ellenőrizd az állapotot
systemctl status mysql
```

### 5. Ha a /tmp Tele Van - Felszabadítás

```bash
# ⚠⚠⚠ ÓVATOSAN! Ez törölni fogja a /tmp könyvtár tartalmát!

# 1. Állítsd le a MySQL-t
systemctl stop mysql

# 2. Töröld a /tmp tartalmát
rm -rf /tmp/*

# 3. Indítsd újra a MySQL-t
systemctl start mysql

# 4. Ellenőrizd az állapotot
systemctl status mysql
```

### 6. MySQL Változók Beállítása

```bash
# MySQL-be belépés root-ként
mysql -u root -p

# Futtasd ezeket a parancsokat:
SET GLOBAL tmp_table_size = 128*1024*1024;
SET GLOBAL max_heap_table_size = 128*1024*1024;
SET GLOBAL innodb_lock_wait_timeout = 50;

# Ellenőrizd:
SHOW VARIABLES LIKE 'tmp_table_size';
SHOW VARIABLES LIKE 'max_heap_table_size';
SHOW VARIABLES LIKE 'innodb_lock_wait_timeout';

# Kilépés
exit;
```

### 7. Lejárt Session-ök Törlése

```bash
mysql -u zedin_cmms -p'Gele007ta...' zedin_cmms << 'EOF'
DELETE FROM user_sessions WHERE expires_at <= NOW();
SELECT ROW_COUNT() AS deleted_sessions;
EOF
```

### 8. Végleges Ellenőrzés

```bash
# MySQL kapcsolat tesztelése
mysql -u zedin_cmms -p'Gele007ta...' zedin_cmms -e "SELECT 1"

# Folyamatok ellenőrzése
mysql -u root -p -e "SHOW PROCESSLIST;"

# Lemezterület
df -h /tmp
```

## 🔧 ALTERNATÍV MEGOLDÁS - Tmpdir Változtatása

Ha a /tmp könyvtár rendszeresen tele van, állítsd be egy másik könyvtárat:

```bash
# 1. Hozz létre egy új tmp könyvtárat
mkdir -p /var/tmp/mysql
chmod 1777 /var/tmp/mysql

# 2. MySQL konfiguráció módosítása
nano /etc/mysql/my.cnf
# VAGY
nano /etc/my.cnf

# 3. Add hozzá ezt a sort:
[mysqld]
tmpdir = /var/tmp/mysql

# 4. MySQL újraindítása
systemctl restart mysql
```

## 📊 DIAGNOSZTIKAI PARANCSOK

```bash
# MySQL error log ellenőrzése
tail -50 /var/log/mysql/error.log

# VAGY
tail -50 /var/log/mysqld.log

# System log ellenőrzése
journalctl -u mysql -n 50

# Aktív kapcsolatok
mysql -u root -p -e "SHOW PROCESSLIST;"

# Aktív tranzakciók
mysql -u root -p -e "SELECT * FROM information_schema.innodb_trx;"

# Lock-olt táblák
mysql -u root -p -e "SHOW OPEN TABLES WHERE In_use > 0;"
```

## ✅ SIKERES JAVÍTÁS UTÁN

Miután a MySQL újra elérhető:

1. Teszteld a kapcsolatot:
```bash
python -c "from database.connection import engine; from sqlalchemy import text; conn = engine.connect(); print('✓ Kapcsolat működik'); conn.close()"
```

2. Teszteld a login-t:
```bash
python test_login_after_fix.py
```

3. Indítsd el az alkalmazást és próbáld meg bejelentkezni!

---

**Szerver**: 116.203.226.140  
**MySQL Port**: 3306  
**Database**: zedin_cmms  
**User**: zedin_cmms

