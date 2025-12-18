# Android App - Backend API Kompatibilitási Javítások

## Összefoglaló

Az Android app és a backend API közötti kompatibilitási problémák javítása. Csak az AndroidApp-ot módosítottuk, a backend változatlan maradt.

## Változtatások

### 1. Inventory API Endpoint Módosítás

**Probléma**: Az Android app `/api/inventory`-t hívott, de a backend csak `/api/assets`-ot használ.

**Megoldás**: 
- `InventoryApi.kt` - Minden endpoint `/api/inventory` helyett `/api/assets`-ot használ
- A backend `Part` modellt használ az `assets` endpoint-on keresztül

**Fájl**: `app/src/main/java/com/artence/cmms/data/remote/api/InventoryApi.kt`

### 2. InventoryDto Struktúra Módosítás

**Probléma**: Az `InventoryDto` nem kompatibilis volt a backend `AssetResponse`-szal.

**Megoldás**:
- Az `InventoryDto` most kompatibilis az `AssetResponse` mezőivel:
  - `id`, `name`, `asset_type`, `asset_tag`, `machine_id`, `status`, `created_at`, `updated_at`
- A régi mezők (`asset_id`, `part_id`, `quantity`, stb.) opcionálisak maradtak backward compatibility miatt

**Fájl**: `app/src/main/java/com/artence/cmms/data/remote/dto/InventoryDto.kt`

### 3. InventoryMapper Frissítés

**Probléma**: Az `InventoryMapper` nem tudta kezelni az új `InventoryDto` struktúrát.

**Megoldás**:
- `fromDto()` és `dtoToEntity()` frissítve, hogy kezelje az új mezőket
- Mapping: `machine_id` → `assetId`, `name` → `assetName` és `partName`

**Fájl**: `app/src/main/java/com/artence/cmms/domain/mapper/InventoryMapper.kt`

### 4. PM API - Nincs Backend Támogatás

**Probléma**: Az Android app `/api/pm-tasks`-ot hív, de a backend-ben nincs PM router.

**Megoldás**: 
- A PMApi-t nem módosítottuk, mert a backend nem támogatja
- A PM funkciók jelenleg nem működnek az app-ban
- Javasolt: PM router hozzáadása a backend-hez, vagy PMApi kommentálása

**Fájl**: `app/src/main/java/com/artence/cmms/data/remote/api/PMApi.kt`

## Response Formátumok

A backend `AssetListResponse` formátumot használ:
```json
{
  "total": 10,
  "items": [...]
}
```

Ez kompatibilis az Android app `ListResponse<T>` formátumával.

## Tesztelés

1. **Inventory lista**: Az app most `/api/assets`-ot hív, és az `AssetResponse`-okat kap
2. **Inventory részletek**: Az `InventoryDto` most kompatibilis az `AssetResponse`-szal
3. **PM tasks**: Jelenleg nem működik, mert nincs backend támogatás

## Következő Lépések

1. PM router hozzáadása a backend-hez (ha szükséges)
2. Tesztelés az éles backend-del (`http://116.203.226.140:8000/api/`)
3. További DTO-k ellenőrzése és szinkronizálása

## Megjegyzések

- A backend `Part` modellt használ, nem `InventoryLevel`-t
- Az `InventoryDto` quantity mezői jelenleg `null`-ok lesznek, mert az `AssetResponse` nem tartalmazza őket
- A mapper default értékeket használ (0) a quantity mezőkhöz

