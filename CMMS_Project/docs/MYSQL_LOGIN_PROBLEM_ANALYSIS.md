# MySQL Login Probléma - Részletes Elemzés és Megoldás

## 🔴 KRITIKUS PROBLÉMA AZONOSÍTVA

A login folyamat lefagyásának oka: **A MySQL szerver `/tmp` könyvtára tele van**

### Probléma Leírása

1. **Hibaüzenet**: `(1114, "The table '/tmp/#sql1_12ba_0' is full")`
2. **Következmény**: A MySQL nem tud ideiglenes táblákat létrehozni a lekérdezésekhez
3. **Hatás**: 
   - Login folyamat lefagy
   - Session létrehozás sikertelen (lock timeout)
   - Adatbázis műveletek nem futnak le

### További Problémák

A diagnosztika során azonosított további problémák:

1. **10 régi tranzakció** - Több mint 7 órája futnak "waiting for handler commit" állapotban
   - Process ID-k: 2923, 2933, 2937, 2938, 2943, 2944, 2945, 2960, 2961, 2962
   - Ezek valószínűleg blokkolják a `user_sessions` táblát
   - Lock timeout (1205) hibát okoznak

2. **Tmp változók alacsonyak**:
   - `tmp_table_size`: 16 MB
   - `max_heap_table_size`: 16 MB
   - Ezek túl alacsonyak lehetnek nagy lekérdezésekhez

## 🔧 MEGOLDÁSOK

### 1. AZONNALI MEGOLDÁS - /tmp Könyvtár Felszabadítása

**A szerveren SSH kapcsolaton keresztül:**

```bash
# 1. Ellenőrizd a lemezterületet
df -h /tmp

# 2. Nézd meg mi foglalja a helyet
ls -lah /tmp | head -20
du -sh /tmp/* | sort -h | tail -10

# 3. MySQL állapot ellenőrzése
sudo systemctl status mysql

# 4. Régi tranzakciók kill-elése (ha lehetséges)
mysql -u root -p
SHOW PROCESSLIST;
KILL <process_id>;  # Minden régi tranzakcióhoz

# 5. MySQL újraindítása (ha szükséges)
sudo systemctl restart mysql

# 6. /tmp könyvtár felszabadítása (ÓVATOSAN!)
# Először állítsd le a MySQL-t
sudo systemctl stop mysql
sudo rm -rf /tmp/*
sudo systemctl start mysql
```

### 2. HOSSZÚ TÁVÚ MEGOLDÁS - Tmpdir Változtatása

**Ha a /tmp könyvtár rendszeresen tele van, állítsd be egy másik könyvtárat:**

```sql
-- Ideiglenes megoldás (újraindítás után visszaáll)
SET GLOBAL tmpdir = '/var/tmp';
```

**Állandó megoldás - my.cnf fájlban:**

```ini
[mysqld]
tmpdir = /var/tmp
```

### 3. TMP VÁLTOZÓK NÖVELÉSE

```sql
-- Növeld a tmp változókat
SET GLOBAL tmp_table_size = 128*1024*1024;  -- 128MB
SET GLOBAL max_heap_table_size = 128*1024*1024;  -- 128MB
```

**Állandó megoldás - my.cnf fájlban:**

```ini
[mysqld]
tmp_table_size = 128M
max_heap_table_size = 128M
```

### 4. RÉGI TRANZAKCIÓK KILL-ELÉSE

```sql
-- Keresd meg a régi tranzakciókat
SELECT ID, USER, TIME, STATE, INFO
FROM information_schema.PROCESSLIST
WHERE DB = 'zedin_cmms'
AND TIME > 300
AND STATE LIKE '%commit%'
ORDER BY TIME DESC;

-- Kill-eld őket
KILL <process_id>;
```

### 5. LEJÁRT SESSION-ÖK TÖRLÉSE

```sql
-- Töröld a lejárt session-öket
DELETE FROM user_sessions
WHERE expires_at <= NOW();
```

## 📊 DIAGNOSZTIKAI SCRIPTEK

A projekt tartalmaz két diagnosztikai scriptet:

1. **`scripts/diagnose_mysql_issues.py`** - Részletes szerver állapot ellenőrzés
2. **`scripts/fix_mysql_issues.py`** - Automatikus javítási kísérlet (korlátozott)

Futtatás:
```bash
cd CMMS_Project
python scripts/diagnose_mysql_issues.py
```

## ⚠️ FIGYELMEZTETÉSEK

1. **NE töröld a /tmp könyvtárat MySQL futása közben** - Ez adatvesztéshez vezethet
2. **Kill-elés előtt ellenőrizd** - Nézd meg mit csinál a tranzakció
3. **Backup készítése** - Mindig készíts backup-ot fontos változtatások előtt

## 🔍 MONITORING

Rendszeres ellenőrzés:

```bash
# Lemezterület
df -h /tmp

# MySQL folyamatok
mysql -u root -p -e "SHOW PROCESSLIST;"

# Aktív tranzakciók
mysql -u root -p -e "SELECT * FROM information_schema.innodb_trx;"
```

## 📝 KÖVETKEZŐ LÉPÉSEK

1. ✅ **AZONNAL**: Szabadítsd fel a /tmp könyvtárat a szerveren
2. ✅ **AZONNAL**: Kill-eld a régi tranzakciókat
3. ✅ **RÖVID TÁVON**: Növeld a tmp változókat
4. ✅ **HOSSZÚ TÁVON**: Állítsd be egy másik tmpdir-t
5. ✅ **MONITORING**: Állíts be automatikus monitoring-ot a /tmp könyvtárra

## 📞 KAPCSOLAT

Ha a probléma továbbra is fennáll, ellenőrizd:
- MySQL error log: `/var/log/mysql/error.log`
- System log: `journalctl -u mysql`
- Disk usage: `df -h`

---

**Dátum**: 2025-12-15  
**Szerver**: 116.203.226.140  
**Adatbázis**: zedin_cmms  
**MySQL Verzió**: 8.0.44

