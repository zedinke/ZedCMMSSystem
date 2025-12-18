# MySQL Optimalizálás - Gyors Útmutató

## 🚀 Gyors Lépések

### 1. Ellenőrzés (Jelenlegi Állapot)

```bash
cd CMMS_Project
python -m utils.mysql_optimizer production
```

Ez megmutatja:
- Jelenlegi beállításokat
- Optimalizálási javaslatokat
- Teljesítmény metrikákat

### 2. Optimalizált Konfiguráció Alkalmazása

#### Windows:

1. **Backup készítése:**
   ```cmd
   copy "C:\ProgramData\MySQL\MySQL Server 8.0\my.ini" "C:\ProgramData\MySQL\MySQL Server 8.0\my.ini.backup"
   ```

2. **Konfiguráció másolása:**
   - Nyisd meg: `CMMS_Project\installer\mysql_optimized_config.ini`
   - Másold a tartalmát a `C:\ProgramData\MySQL\MySQL Server 8.0\my.ini` fájlba
   - **FONTOS:** Módosítsd az `innodb_buffer_pool_size` értékét a szerver RAM méretéhez!

3. **MySQL újraindítása:**
   ```cmd
   net stop MySQL80
   net start MySQL80
   ```

#### Linux:

1. **Backup készítése:**
   ```bash
   sudo cp /etc/mysql/my.cnf /etc/mysql/my.cnf.backup
   ```

2. **Konfiguráció másolása:**
   ```bash
   sudo cp CMMS_Project/installer/mysql_optimized_config.ini /etc/mysql/my.cnf
   ```
   - **FONTOS:** Módosítsd az `innodb_buffer_pool_size` értékét a szerver RAM méretéhez!

3. **MySQL újraindítása:**
   ```bash
   sudo systemctl restart mysql
   ```

### 3. Ellenőrzés (Utána)

```bash
python -m utils.mysql_optimizer production
```

## 📊 Ajánlott Buffer Pool Méret

| Szerver RAM | Buffer Pool Méret |
|-------------|-------------------|
| 2GB         | 512MB - 1GB       |
| 4GB         | 1GB - 2GB         |
| 8GB         | 2GB - 4GB         |
| 16GB        | 4GB - 8GB         |

**Szabály:** RAM 70-80%-a, de legalább 1GB

## ⚠️ Fontos Megjegyzések

1. **Backup:** Mindig készíts backup-ot a konfigról!
2. **Buffer Pool:** A legfontosabb beállítás - ne hagyd ki!
3. **Tesztelés:** Teszteld a változtatásokat staging környezetben először
4. **Monitoring:** Figyeld a MySQL log fájlokat az újraindítás után

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

- Részletes útmutató: `docs/MYSQL_SERVER_OPTIMIZATION.md`
- Optimalizálási script: `utils/mysql_optimizer.py`
- Konfigurációs fájl: `installer/mysql_optimized_config.ini`




