# Lemezterület Használat Elemzése

## Aktuális Állapot (Felszabadítás után)

**Összes lemezterület**: 75G  
**Használatban**: 9.1G (13%)  
**Szabad**: 63G (87%)

## Legnagyobb Könyvtárak

### 1. `/var/lib` - 7.2G (legnagyobb)

#### Docker (`/var/lib/docker`) - ~3.2G
- **`rootfs`**: 2.8G - Docker container fájlrendszerek
- **`volumes`**: 213M - Docker volumes (MySQL adatbázis: 222MB)
- **`buildkit`**: 145M - Build cache
- **`containers`**: 2.5M - Container metaadatok

#### Docker Image-ek (összesen ~4GB)
- **zedhosting-api**: 2GB (legnagyobb)
- **mysql:8.0**: 1.08GB
- **zedhosting-web**: 480MB
- **traefik:v3.2**: 245MB
- **adminer**: 170MB
- **redis:7-alpine**: 61MB

### 2. `/var/log` - 676M
- Log fájlok (folyamatosan növekszik)

### 3. `/opt` - 1.7G
- Alkalmazások és szoftverek

### 4. `/usr` - 1.8G
- Rendszer programok és könyvtárak

### 5. `/boot` - 116M
- Boot fájlok

## Mi Foglalta Korábban a Helyet?

### Törölt Tartalom (Docker Cleanup után)

**Előtte**: 75G / 75G (100% tele)  
**Utána**: 9.1G / 75G (13%)

**Törölt tartalom**:
- **Docker build cache**: ~69.59GB (ez volt a fő probléma!)
- **Nem használt Docker image-ek**: 
  - postgres:15-alpine
  - zedhosting-daemon:latest
  - node:20-slim
  - traefik:v2.10, traefik:v3.1
- **Nem használt container-ek**

## Jelenlegi Használat Részletezve

### Docker Container-ek (futó)
- **zed-web**: 4.1kB
- **zed-mysql**: 32.8kB (+ 222MB volume)
- **zed-traefik**: 16.4kB
- **zed-api**: 4.1kB
- **zed-adminer**: 73.7kB
- **zed-redis**: 4.1kB (+ 2.2kB volume)

### Docker Volumes
- **zedhosting_mysql_data**: 222.2MB (MySQL adatbázis)
- **zedhosting_traefik_acme**: 13.35kB (SSL tanúsítványok)
- **zedhosting_redis_data**: 2.212kB

## Ajánlások

### 1. Rendszeres Karbantartás

```bash
# Docker tisztítás (havonta)
docker system prune -a --volumes -f

# Build cache tisztítás
docker builder prune -a -f

# Log rotáció beállítása
# /etc/logrotate.d/docker-containers
```

### 2. Log Fájlok Kezelése

```bash
# Log fájlok mérete ellenőrzése
du -sh /var/log/*

# Régi log fájlok törlése
find /var/log -type f -name "*.log" -mtime +30 -delete
```

### 3. Docker Image Optimalizálás

- Használj multi-stage build-eket
- Töröld a nem használt image-eket
- Használj kisebb base image-eket (alpine)

### 4. Monitoring

```bash
# Lemezterület figyelése
df -h

# Docker lemezterület
docker system df

# Nagy fájlok keresése
find / -type f -size +100M 2>/dev/null | xargs du -h | sort -h
```

## Összefoglalás

**Fő probléma volt**: Docker build cache (~70GB)  
**Megoldás**: `docker system prune -a --volumes -f`  
**Eredmény**: 75G → 9.1G használat

**Jelenlegi használat**:
- Docker image-ek: ~4GB
- Docker volumes: ~222MB (MySQL adatbázis)
- Log fájlok: ~676MB
- Rendszer fájlok: ~4GB

**Szabad hely**: 63GB (87%)

## Hasznos Parancsok

```bash
# Teljes lemezterület
df -h

# Legnagyobb könyvtárak
du -sh /* | sort -h

# Docker lemezterület
docker system df -v

# Nagy fájlok keresése
find / -type f -size +100M -exec ls -lh {} \; 2>/dev/null | awk '{print $5, $9}' | sort -h

# Log fájlok mérete
du -sh /var/log/* | sort -h
```




