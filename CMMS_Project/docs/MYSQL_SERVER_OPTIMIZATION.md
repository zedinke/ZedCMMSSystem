# MySQL Szerver Optimalizálási Útmutató

Ez a dokumentum a MySQL szerver optimalizálását mutatja be a Zed CMMS System számára.

## 🚀 Gyors Optimalizálások

### 1. MySQL Konfigurációs Fájl (my.cnf / my.ini)

A MySQL konfigurációs fájl helye:
- **Windows**: `C:\ProgramData\MySQL\MySQL Server 8.0\my.ini`
- **Linux**: `/etc/mysql/my.cnf` vagy `/etc/my.cnf`

### 2. Ajánlott Beállítások

```ini
[mysqld]
# ============================================
# Alapvető Beállítások
# ============================================

# InnoDB Buffer Pool (a legfontosabb!)
# Állítsd be a RAM 70-80%-ára (de legalább 1GB)
innodb_buffer_pool_size = 2G
innodb_buffer_pool_instances = 4

# InnoDB Log File mérete (növeli az írási teljesítményt)
innodb_log_file_size = 256M
innodb_log_buffer_size = 64M

# InnoDB Flush Módszer (gyorsabb írás)
innodb_flush_log_at_trx_commit = 2  # 0=legyorsabb, 1=legbiztonságosabb, 2=kompromisszum

# ============================================
# Kapcsolat Beállítások
# ============================================

# Maximális kapcsolatok száma
max_connections = 200

# Kapcsolat timeout
wait_timeout = 600
interactive_timeout = 600

# ============================================
# Query Cache (MySQL 5.7-ben elérhető)
# ============================================

# MySQL 8.0-ban nincs query cache, de MySQL 5.7-ben:
# query_cache_type = 1
# query_cache_size = 128M
# query_cache_limit = 4M

# ============================================
# Temp Tables és Sort
# ============================================

# Temp táblák memóriában (gyorsabb)
tmp_table_size = 128M
max_heap_table_size = 128M

# Sort buffer (gyorsabb rendezés)
sort_buffer_size = 4M
read_buffer_size = 2M
read_rnd_buffer_size = 4M

# ============================================
# Binlog és Replication (ha nincs szükség rá)
# ============================================

# Binlog kikapcsolása ha nincs replication
# skip-log-bin

# ============================================
# Slow Query Log (teljesítmény elemzéshez)
# ============================================

slow_query_log = 1
slow_query_log_file = /var/log/mysql/slow-query.log
long_query_time = 2  # 2 másodperc feletti query-k naplózása

# ============================================
# Egyéb Optimalizálások
# ============================================

# Table cache
table_open_cache = 2000
table_definition_cache = 1400

# Thread cache
thread_cache_size = 50

# Join buffer
join_buffer_size = 4M

# Key buffer (MyISAM táblákhoz, ha vannak)
key_buffer_size = 32M
```

### 3. Windows-specifikus Beállítások

Windows-on a `my.ini` fájlban:

```ini
[mysqld]
# Windows-specific
shared-memory
shared-memory-base-name = MYSQL

# Performance Schema (hasznos, de fogyaszt erőforrást)
performance_schema = ON
performance_schema_max_table_instances = 12500
```

## 📊 Teljesítmény Ellenőrzés

### 1. MySQL Status Ellenőrzés

```sql
-- Buffer pool használat
SHOW STATUS LIKE 'Innodb_buffer_pool%';

-- Kapcsolatok
SHOW STATUS LIKE 'Threads_connected';
SHOW STATUS LIKE 'Max_used_connections';

-- Slow queries
SHOW STATUS LIKE 'Slow_queries';

-- Query cache (MySQL 5.7)
SHOW STATUS LIKE 'Qcache%';
```

### 2. Aktuális Konfiguráció Megtekintése

```sql
-- Buffer pool méret
SHOW VARIABLES LIKE 'innodb_buffer_pool_size';

-- Kapcsolatok
SHOW VARIABLES LIKE 'max_connections';

-- Minden változó
SHOW VARIABLES;
```

### 3. Teljesítmény Schema Használata

```sql
-- Engedélyezés
SET GLOBAL performance_schema = ON;

-- Lassú query-k keresése
SELECT * FROM performance_schema.events_statements_summary_by_digest 
ORDER BY avg_timer_wait DESC LIMIT 10;
```

## 🔧 Optimalizálási Scriptek

### 1. Index Optimalizálás

```sql
-- Táblák optimalizálása
OPTIMIZE TABLE users;
OPTIMIZE TABLE machines;
OPTIMIZE TABLE worksheets;
OPTIMIZE TABLE parts;
OPTIMIZE TABLE inventory_levels;
OPTIMIZE TABLE stock_transactions;
OPTIMIZE TABLE audit_logs;

-- Vagy minden tábla egyszerre
SELECT CONCAT('OPTIMIZE TABLE ', table_name, ';') 
FROM information_schema.tables 
WHERE table_schema = 'your_database_name';
```

### 2. Statisztikák Frissítése

```sql
-- Táblák statisztikáinak frissítése
ANALYZE TABLE users;
ANALYZE TABLE machines;
ANALYZE TABLE worksheets;
ANALYZE TABLE parts;
ANALYZE TABLE inventory_levels;
```

### 3. Index Használat Ellenőrzése

```sql
-- Nem használt indexek keresése
SELECT 
    s.table_schema,
    s.table_name,
    s.index_name,
    s.cardinality,
    s.non_unique,
    s.seq_in_index,
    s.column_name
FROM information_schema.statistics s
LEFT JOIN information_schema.index_usage i 
    ON s.table_schema = i.object_schema 
    AND s.table_name = i.object_name 
    AND s.index_name = i.index_name
WHERE s.table_schema = 'your_database_name'
    AND i.index_name IS NULL;
```

## 📈 Ajánlott Értékek CMMS Rendszerhez

### Kis Közepes Adatbázis (< 10GB, < 100 felhasználó)

```ini
innodb_buffer_pool_size = 1G
max_connections = 100
tmp_table_size = 64M
max_heap_table_size = 64M
```

### Közepes Nagy Adatbázis (10-50GB, 100-500 felhasználó)

```ini
innodb_buffer_pool_size = 4G
max_connections = 200
tmp_table_size = 128M
max_heap_table_size = 128M
```

### Nagy Adatbázis (> 50GB, > 500 felhasználó)

```ini
innodb_buffer_pool_size = 8G
max_connections = 300
tmp_table_size = 256M
max_heap_table_size = 256M
```

## ⚠️ Fontos Megjegyzések

1. **Buffer Pool Méret**: Soha ne állítsd be a teljes RAM-ra! Hagyj legalább 2-4GB-t az operációs rendszernek és más alkalmazásoknak.

2. **Változtatások Alkalmazása**: MySQL újraindítása szükséges a legtöbb változtatáshoz:
   ```bash
   # Windows (Service)
   net stop MySQL80
   net start MySQL80
   
   # Linux
   sudo systemctl restart mysql
   ```

3. **Backup**: Mindig készíts backup-ot a konfiguráció módosítása előtt!

4. **Fokozatos Optimalizálás**: Ne változtass mindent egyszerre! Teszteld egy-egy változtatást.

## 🛠️ Automatikus Optimalizálási Script

Lásd: `utils/mysql_optimizer.py` - Ez a script automatikusan ellenőrzi és javasol optimalizálásokat.

## 📚 További Források

- [MySQL Performance Tuning](https://dev.mysql.com/doc/refman/8.0/en/optimization.html)
- [InnoDB Buffer Pool](https://dev.mysql.com/doc/refman/8.0/en/innodb-buffer-pool.html)
- [MySQL Server Variables](https://dev.mysql.com/doc/refman/8.0/en/server-system-variables.html)




