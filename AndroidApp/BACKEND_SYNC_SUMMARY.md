# Android App - Backend Szerver Szinkronizálás Összefoglaló

## Felderített eltérések és javítások

### ✅ 1. API URL Prefix javítva
- **Szerver:** `/api/v1/` prefix minden router-nél
- **Android App (előtte):** `/api/` prefix
- **Android App (javítva):** `/api/v1/` prefix
- **Fájl:** `Constants.kt`

### ✅ 2. Inventory API javítva
- **Szerver:** `/api/v1/inventory` router létezik
- **Android App (előtte):** `/api/assets`-ot hívott
- **Android App (javítva):** `/api/v1/inventory` használata
- **Fájl:** `InventoryApi.kt`

### ✅ 3. PM API javítva
- **Szerver:** `/api/v1/pm/tasks` router létezik
- **Android App (előtte):** `/api/pm-tasks`-ot hívott
- **Android App (javítva):** `/api/v1/pm/tasks` használata
- **Paraméter:** `task_id` (nem `id`)
- **Fájl:** `PMApi.kt`

### ✅ 4. Path paraméterek javítva
A szerver specifikus paraméterneveket használ:
- **Machines:** `machine_id` (nem `id`)
- **Inventory:** `inventory_id` (nem `id`)
- **Worksheets:** `worksheet_id` (nem `id`)
- **PM Tasks:** `task_id` (nem `id`)
- **Users:** `id` (ez jó)

### ⚠️ 5. Assets API - Nincs szerveren
- **Szerver:** Nincs `/api/v1/assets` router
- **Android App:** Van `AssetApi` interface
- **Megoldás:** 
  - Vagy: AssetApi törlése/kommentálása
  - Vagy: Assets endpoint hozzáadása a szerverhez
  - Vagy: Assets kezelése inventory-n keresztül

### ✅ 6. Pagináció támogatás
- **Szerver:** ListResponse formátum (total, items)
- **Android App:** ListResponse wrapper hozzáadva
- **Fájlok:** Minden API interface frissítve

## Szerver API Végpontok (minden `/api/v1/` prefix)

### Authentication
- `POST /api/v1/auth/login` ✅
- `POST /api/v1/auth/logout` (opcionális)
- `POST /api/v1/auth/register` (opcionális)

### Machines
- `GET /api/v1/machines` ✅
- `GET /api/v1/machines/{machine_id}` ✅
- `POST /api/v1/machines` ✅
- `PUT /api/v1/machines/{machine_id}` ✅
- `DELETE /api/v1/machines/{machine_id}` ✅

### Inventory
- `GET /api/v1/inventory` ✅
- `GET /api/v1/inventory/{inventory_id}` ✅
- `POST /api/v1/inventory` ✅
- `PUT /api/v1/inventory/{inventory_id}` ✅
- `DELETE /api/v1/inventory/{inventory_id}` ✅

### Worksheets
- `GET /api/v1/worksheets` ✅
- `GET /api/v1/worksheets/{worksheet_id}` ✅
- `POST /api/v1/worksheets` ✅
- `PUT /api/v1/worksheets/{worksheet_id}` ✅
- `DELETE /api/v1/worksheets/{worksheet_id}` ✅

### PM (Preventive Maintenance)
- `GET /api/v1/pm/tasks` ✅
- `GET /api/v1/pm/tasks/{task_id}` ✅
- `POST /api/v1/pm/tasks` ✅
- `PUT /api/v1/pm/tasks/{task_id}` ✅
- `DELETE /api/v1/pm/tasks/{task_id}` ✅

### Users
- `GET /api/v1/users/me` ✅
- `GET /api/v1/users` ✅
- `POST /api/v1/users` ✅
- `PUT /api/v1/users/{id}` ✅
- `DELETE /api/v1/users/{id}` ✅

### Reports
- `GET /api/v1/reports/summary` ✅
- `GET /api/v1/reports/trends` ✅

## Módosított fájlok

1. `Constants.kt` - BASE_URL: `/api/` → `/api/v1/`
2. `InventoryApi.kt` - `/api/assets` → `/api/v1/inventory`, paraméterek: `id` → `inventory_id`
3. `PMApi.kt` - `/api/pm-tasks` → `/api/v1/pm/tasks`, paraméterek: `id` → `task_id`
4. `MachineApi.kt` - Paraméterek: `id` → `machine_id`
5. `WorksheetApi.kt` - Paraméterek: `id` → `worksheet_id`
6. `ListResponse.kt` - Új wrapper osztály paginációhoz
7. Minden repository frissítve ListResponse kezelésére

## További teendők

1. **AssetApi kezelése:**
   - Döntés: törlés vagy szerveren hozzáadás
   - Ha törlés: AssetRepository és kapcsolódó kód eltávolítása

2. **Tesztelés:**
   - Login tesztelése
   - Minden CRUD művelet tesztelése
   - Pagináció tesztelése

3. **DTO-k ellenőrzése:**
   - Szerver sémák vs Android DTO-k összevetése
   - Hiányzó mezők pótlása

## Szerver információk

- **IP:** 116.203.226.140
- **Port:** 8000
- **Status:** ✅ Aktív
- **Service:** cmms-api.service
- **Backend könyvtár:** /opt/cmms-backend
- **Python:** 3.12.3

