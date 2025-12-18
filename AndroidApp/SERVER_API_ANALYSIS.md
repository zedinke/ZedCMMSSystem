# Backend Szerver API Elemzés

## Szerver információk
- **IP:** 116.203.226.140
- **Port:** 8000
- **Status:** ✅ Aktív és fut
- **Service:** cmms-api.service (systemd)
- **Python:** 3.12.3
- **Backend könyvtár:** /opt/cmms-backend

## API Struktúra

### Router Prefixek
**MINDEN router `/api/v1/` prefixet használ:**
- `/api/v1/auth` - Authentication
- `/api/v1/machines` - Machines
- `/api/v1/inventory` - Inventory (NEM `/api/assets`)
- `/api/v1/worksheets` - Worksheets
- `/api/v1/pm` - Preventive Maintenance
- `/api/v1/users` - Users
- `/api/v1/reports` - Reports

### Health Check
- ✅ `/api/health/` - Működik (detailed health check)
- ✅ `/health` - Működik (simple health check)
- ❌ `/api/v1/health/` - Nincs ilyen endpoint

## Problémák az Android App-ban

### 1. API URL Prefix eltérés
- **Szerver:** `/api/v1/`
- **Android App (jelenleg):** `/api/`
- **Megoldás:** Android app BASE_URL visszaállítása `/api/v1/`-re

### 2. Inventory vs Assets
- **Szerver:** `/api/v1/inventory` router létezik
- **Android App:** `/api/assets`-ot hív (rossz!)
- **Megoldás:** 
  - Vagy: Android app-ban `/api/v1/inventory` használata
  - Vagy: Szerveren `/api/v1/assets` router hozzáadása

### 3. PM API
- **Szerver:** ✅ Van `/api/v1/pm` router
- **Android App:** `/api/pm-tasks`-ot hív (rossz!)
- **Megoldás:** Android app PMApi frissítése `/api/v1/pm`-re

## Javasolt javítások

### Android App módosítások:

1. **Constants.kt:**
```kotlin
const val BASE_URL = "http://116.203.226.140:8000/api/v1/"
```

2. **InventoryApi.kt:**
```kotlin
@GET("inventory")  // NEM "assets"
suspend fun getInventory(...)
```

3. **PMApi.kt:**
```kotlin
@GET("pm/tasks")  // NEM "pm-tasks"
suspend fun getPMTasks(...)
```

## Szerver API Végpontok

### Authentication
- `POST /api/v1/auth/login` - Login

### Machines
- `GET /api/v1/machines` - List machines
- `GET /api/v1/machines/{id}` - Get machine
- `POST /api/v1/machines` - Create machine
- `PUT /api/v1/machines/{id}` - Update machine
- `DELETE /api/v1/machines/{id}` - Delete machine

### Inventory
- `GET /api/v1/inventory` - List inventory
- `GET /api/v1/inventory/{id}` - Get inventory item
- `POST /api/v1/inventory` - Create inventory item
- `PUT /api/v1/inventory/{id}` - Update inventory item
- `DELETE /api/v1/inventory/{id}` - Delete inventory item

### Worksheets
- `GET /api/v1/worksheets` - List worksheets
- `GET /api/v1/worksheets/{id}` - Get worksheet
- `POST /api/v1/worksheets` - Create worksheet
- `PUT /api/v1/worksheets/{id}` - Update worksheet
- `DELETE /api/v1/worksheets/{id}` - Delete worksheet

### PM (Preventive Maintenance)
- `GET /api/v1/pm/tasks` - List PM tasks
- `GET /api/v1/pm/tasks/{id}` - Get PM task
- `POST /api/v1/pm/tasks` - Create PM task
- `PUT /api/v1/pm/tasks/{id}` - Update PM task
- `DELETE /api/v1/pm/tasks/{id}` - Delete PM task

### Users
- `GET /api/v1/users` - List users
- `GET /api/v1/users/{id}` - Get user
- `POST /api/v1/users` - Create user
- `PUT /api/v1/users/{id}` - Update user
- `DELETE /api/v1/users/{id}` - Delete user

### Reports
- `GET /api/v1/reports/summary` - Get summary
- `GET /api/v1/reports/trends` - Get trends

## Logokból látható hibák

```
GET /api/v1/assets HTTP/1.1" 404 Not Found
GET /api/assets?skip=0&limit=100 HTTP/1.1" 404 Not Found
GET /api/inventory?skip=0&limit=100 HTTP/1.1" 404 Not Found
GET /api/v1/inventory?limit=5 HTTP/1.1" 401 Unauthorized
```

**Megjegyzés:** A 401 Unauthorized normális, ha nincs token. A 404 Not Found azért van, mert rossz URL-t hív az app.

