# Szerver Backend Szinkronizálás Terv

## Cél
A szerveren lévő backend-et teljesen szinkronba hozni a lokális verzióval, majd az Android app-ot is igazítani.

## Jelenlegi állapot

### Lokális backend (CMMS_Project/api)
- **Prefix:** `/api/`
- **Router-ek:** auth, users, machines, worksheets, assets, permissions, health
- **Hiányzik:** inventory, pm, reports

### Szerver backend (/opt/cmms-backend/api)
- **Prefix:** `/api/v1/`
- **Router-ek:** auth, users, machines, worksheets, inventory, pm, reports
- **Hiányzik:** assets, permissions, health

## Teendők

### 1. Szerver router prefixek módosítása
- `/api/v1/` → `/api/` minden router-ben

### 2. Hiányzó router-ek hozzáadása szerverhez
- `assets.py` - lokális verzióból
- `health.py` - lokális verzióból
- `permissions.py` - lokális verzióból

### 3. Meglévő router-ek frissítése
- `auth.py` - lokális verzióval
- `users.py` - lokális verzióval
- `machines.py` - lokális verzióval
- `worksheets.py` - lokális verzióval

### 4. Inventory, PM, Reports router-ek átalakítása
- Prefix: `/api/v1/` → `/api/`
- Importok: lokális struktúrával kompatibilisra

### 5. Szerver fájlok frissítése
- `server.py` → `app.py` + `server.py` (lokális verzió)
- `schemas.py` - lokális verzióval
- `security.py` - lokális verzióval
- `dependencies.py` - lokális verzióval

### 6. Android app frissítése
- `Constants.kt`: BASE_URL `/api/v1/` → `/api/`
- Minden API interface: prefixek javítása

## Figyelem
- A lokális fájlokat NEM módosítjuk
- Csak a szerveren lévő fájlokat frissítjük
- Backup készült: `/opt/cmms-backend/api_backup_before_sync`

