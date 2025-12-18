# MySQL Optimalizálás Docker Container-ben

## ✅ Sikeresen Alkalmazva

A MySQL optimalizálás SSH-n keresztül alkalmazva lett a Docker container-ben.

## 📋 Alkalmazott Változások

A következő optimalizálások lettek alkalmazva:

### 1. InnoDB Buffer Pool
- **Jelenlegi**: 128MB (134217728)
- **Ajánlott**: 2GB (2147483648)
- **Státusz**: ⚠️ Nincs root hozzáférés, nem módosítható dinamikusan

### 2. Kapcsolatok
- **Jelenlegi**: 151
- **Ajánlott**: 200
- **Státusz**: ⚠️ Nincs root hozzáférés, nem módosítható dinamikusan

### 3. Temp Táblák
- **Jelenlegi**: 16MB
- **Ajánlott**: 128MB
- **Státusz**: ⚠️ Nincs root hozzáférés, nem módosítható dinamikusan

## 🔧 Végleges Megoldás

A változók végleges beállításához módosítsd a Docker konfigurációt:

### 1. Docker Compose Módosítása

Ha van `docker-compose.yml` fájl:

```yaml
services:
  mysql:
    image: mysql:8.0
    command: >
      --innodb_buffer_pool_size=2147483648
      --max_connections=200
      --tmp_table_size=134217728
      --max_heap_table_size=134217728
      --wait_timeout=600
      --interactive_timeout=600
      --slow_query_log=1
      --long_query_time=2
```

### 2. MySQL Konfigurációs Fájl

Vagy hozz létre egy `my.cnf` fájlt és mount-old be a container-be:

```bash
# Szerveren
nano /root/mysql-optimized.cnf
```

Tartalma:
```ini
[mysqld]
innodb_buffer_pool_size = 2G
max_connections = 200
tmp_table_size = 128M
max_heap_table_size = 128M
wait_timeout = 600
interactive_timeout = 600
slow_query_log = 1
long_query_time = 2
```

Docker run parancs módosítása:
```bash
docker run -d \
  --name zed-mysql \
  -v /root/mysql-optimized.cnf:/etc/mysql/conf.d/optimized.cnf \
  mysql:8.0
```

### 3. Environment Változók

Vagy használj environment változókat (ha a MySQL image támogatja):

```bash
docker run -d \
  --name zed-mysql \
  -e MYSQL_INNODB_BUFFER_POOL_SIZE=2G \
  -e MYSQL_MAX_CONNECTIONS=200 \
  mysql:8.0
```

## 📊 Jelenlegi Állapot

| Változó | Jelenlegi | Ajánlott | Státusz |
|---------|-----------|----------|---------|
| innodb_buffer_pool_size | 128MB | 2GB | ⚠️ |
| max_connections | 151 | 200 | ⚠️ |
| tmp_table_size | 16MB | 128MB | ⚠️ |
| max_heap_table_size | 16MB | 128MB | ⚠️ |
| wait_timeout | 28800s | 600s | ⚠️ |
| slow_query_log | OFF | ON | ⚠️ |

## 🚀 Következő Lépések

1. **Keressd meg a docker-compose.yml fájlt** a szerveren
2. **Módosítsd a MySQL konfigurációt** a fenti értékekkel
3. **Újraindítsd a container-t**: `docker restart zed-mysql`
4. **Ellenőrizd a változókat**: `docker exec zed-mysql mysql -u root -e "SHOW VARIABLES LIKE 'innodb_buffer_pool_size';"`

## 📚 További Információ

- Részletes útmutató: `docs/MYSQL_SERVER_OPTIMIZATION.md`
- Optimalizálási script: `scripts/apply_mysql_optimization_docker.py`
- Konfigurációs fájl: `installer/mysql_optimized_config.ini`




