# MySQL Optimalizálás Alkalmazása - Lépésről Lépésre

## ✅ Elkészült Fájlok

1. **`installer/mysql_optimized_config.ini`** - Optimalizált MySQL konfiguráció
2. **`utils/mysql_optimizer.py`** - Ellenőrző script
3. **`docs/MYSQL_SERVER_OPTIMIZATION.md`** - Részletes útmutató
4. **`docs/MYSQL_OPTIMIZATION_QUICK_START.md`** - Gyors útmutató

## 🚀 Alkalmazás Lépései

### 1. Ellenőrzés (Jelenlegi Állapot)

```bash
cd CMMS_Project
python utils/mysql_optimizer.py production
```

### 2. Konfiguráció Alkalmazása

#### Windows Szerveren:

1. **Nyisd meg a MySQL konfigurációs fájlt:**
   ```
   C:\ProgramData\MySQL\MySQL Server 8.0\my.ini
   ```

2. **Készíts backup-ot:**
   ```cmd
   copy "C:\ProgramData\MySQL\MySQL Server 8.0\my.ini" "C:\ProgramData\MySQL\MySQL Server 8.0\my.ini.backup"
   ```

3. **Másold az optimalizált beállításokat:**
   - Nyisd meg: `CMMS_Project\installer\mysql_optimized_config.ini`
   - Másold a tartalmát a `my.ini` fájlba
   - **FONTOS:** Módosítsd az `innodb_buffer_pool_size` értékét!

4. **MySQL újraindítása:**
   ```cmd
   net stop MySQL80
   net start MySQL80
   ```

#### Linux Szerveren:

1. **Backup:**
   ```bash
   sudo cp /etc/mysql/my.cnf /etc/mysql/my.cnf.backup
   ```

2. **Konfiguráció másolása:**
   ```bash
   sudo nano /etc/mysql/my.cnf
   # Másold be az optimalizált beállításokat
   ```

3. **MySQL újraindítása:**
   ```bash
   sudo systemctl restart mysql
   ```

### 3. Buffer Pool Méret Beállítása

**FONTOS:** Módosítsd az `innodb_buffer_pool_size` értékét a szerver RAM méretéhez!

```ini
; Példa: 4GB RAM esetén
innodb_buffer_pool_size = 2G

; Példa: 8GB RAM esetén  
innodb_buffer_pool_size = 4G
```

**Szabály:** RAM 70-80%-a, de legalább 1GB

### 4. Ellenőrzés (Utána)

```bash
python utils/mysql_optimizer.py production
```

## 📊 Várható Javulás

| Optimalizálás | Javulás |
|---------------|---------|
| Buffer Pool (1GB → 2GB) | 50-100% |
| Temp táblák memóriában | 30-50% |
| Kapcsolatok optimalizálása | 20-40% |
| **ÖSSZESEN** | **70-150%** |

## ⚠️ Fontos

1. **Backup:** Mindig készíts backup-ot!
2. **Tesztelés:** Teszteld staging környezetben először
3. **Monitoring:** Figyeld a MySQL log fájlokat
4. **Visszaállítás:** Ha probléma van, használd a backup fájlt

## 🔧 További Optimalizálások

### Táblák Optimalizálása

```sql
OPTIMIZE TABLE users;
OPTIMIZE TABLE machines;
OPTIMIZE TABLE worksheets;
OPTIMIZE TABLE parts;
OPTIMIZE TABLE inventory_levels;
OPTIMIZE TABLE stock_transactions;
OPTIMIZE TABLE audit_logs;
```

### Statisztikák Frissítése

```sql
ANALYZE TABLE users;
ANALYZE TABLE machines;
ANALYZE TABLE worksheets;
ANALYZE TABLE parts;
```

## 📚 További Információ

- **Részletes útmutató:** `docs/MYSQL_SERVER_OPTIMIZATION.md`
- **Gyors útmutató:** `docs/MYSQL_OPTIMIZATION_QUICK_START.md`
- **Konfigurációs fájl:** `installer/mysql_optimized_config.ini`




