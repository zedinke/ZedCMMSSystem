# Backend API specifikáció – CMMS Android app igényei

Base URL: http://116.203.226.140:8000/api/
Megjegyzés: Egyes modulok a `v1/` prefixet használják (pl. PM, Auth), így a teljes útvonal pl. `http://116.203.226.140:8000/api/v1/auth/login`.

## Autentikáció
- POST v1/auth/login
  - Body: { "username": string, "password": string }
  - 200: { "access_token": string, "token_type": string, "expires_in": number, "user_id": number, "username": string, "role_name": string }
  - 401/422: hibák

Header minden további kéréshez: `Authorization: Bearer <token>`

## Felhasználók
- GET users
  - Query: skip, limit, role_name?, status?
  - 200: { items: UserDto[], total: number }
- GET users/{id}
- POST users
- PUT users/{id}
- DELETE users/{id}
- POST users/{id}/reset-password

UserDto mezők: lásd `app/src/main/java/.../data/remote/dto/UserDto.kt`

## Gépek (Machines)
- GET machines (skip, limit, status?) -> ListResponse<MachineDto>
- GET machines/{id}
- POST machines (CreateMachineDto)
- PUT machines/{id} (UpdateMachineDto)
- DELETE machines/{id}

Dto-k: `MachineDto.kt`

## Munkalapok (Worksheets)
- GET worksheets (skip, limit, status?, machine_id?) -> ListResponse<WorksheetDto>
- GET worksheets/{id}
- POST worksheets (CreateWorksheetDto)
- PUT worksheets/{id} (UpdateWorksheetDto)
- DELETE worksheets/{id}

Dto-k: `WorksheetDto.kt`

## Készlet/Eszköz (Inventory / Assets)
Megjegyzés: Az Android app Inventory néven hivatkozik rá, de a backend valójában Asset modellként szolgálja ki.

- GET inventory -> ListResponse<InventoryDto>
- GET inventory/{id}
- POST inventory (CreateInventoryDto)
- PUT inventory/{id} (UpdateInventoryDto)
- DELETE inventory/{id}

Dto-k és mezők: `InventoryDto.kt`
- InventoryDto: id, name, asset_type, asset_tag?, machine_id?, status, created_at, updated_at, ... (legacy: quantity?, min_quantity?, max_quantity?, location?)
- CreateInventoryDto: name (kötelező), asset_type?="Spare", asset_tag?, machine_id?, status?="active", category?, description?, (legacy: quantity?, min_quantity?, max_quantity?, location?)
- UpdateInventoryDto: name?, asset_type?, asset_tag?, machine_id?, status?, category?, description?, quantity?, min_quantity?, max_quantity?, location?

## PM (Preventív karbantartás)
Base: v1/pm/
- GET v1/pm/tasks (skip, limit) -> List<PMTaskDto>
- GET v1/pm/tasks/{id}
- GET v1/pm/tasks/machine/{machineId}
- GET v1/pm/tasks/upcoming?limit=10
- POST v1/pm/tasks (CreatePMTaskDto)
- PUT v1/pm/tasks/{id} (UpdatePMTaskDto)
- POST v1/pm/tasks/{id}/execute (ExecutePMTaskDto)
- DELETE v1/pm/tasks/{id}

Dto-k: `data/remote/dto/pm/*`

## Riportok
- GET reports/summary -> ReportsSummaryDto

## Globális követelmények
- Minden, tokenköteles végpont: `Authorization: Bearer <access_token>`
- Tartalom: `Content-Type: application/json`
- Időkorlátok: 30s (lásd `Constants.TIMEOUT_SECONDS`)

## Példa kérések
- Login
  POST http://116.203.226.140:8000/api/v1/auth/login
  Body: {"username":"demo","password":"demo"}

- Inventory létrehozás
  POST http://116.203.226.140:8000/api/inventory
  Body: {"name":"Bearing 6204","quantity":50,"min_quantity":10,"max_quantity":200,"location":"A1"}

## Megjegyzések
- Az app az Android manifestben engedélyezi a cleartext HTTP-t: usesCleartextTraffic=true.
- A PM és Auth modulok `v1/` prefixet használnak; a többi modul közvetlenül a BASE_URL után érhető el (users, machines, worksheets, inventory, reports).
- A login csak `username` + `password` párost fogad; e-mailt nem.

