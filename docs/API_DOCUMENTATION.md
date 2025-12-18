# ANDROID CMMS - API DOCUMENTATION

**Version:** 1.0  
**Base URL:** `https://api.example.com/api/v1`  
**Authentication:** Bearer Token (JWT)

---

## 📋 Table of Contents
- [Authentication](#authentication)
- [Assets](#assets)
- [Worksheets](#worksheets)
- [Machines](#machines)
- [Inventory](#inventory)
- [PM Tasks](#pm-tasks)
- [Error Codes](#error-codes)

---

## Authentication

### POST /auth/login
Authenticate user and get JWT token.

**Request:**
```http
POST /api/v1/auth/login HTTP/1.1
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePassword123"
}
```

**Response (200 OK):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expiresIn": 1800,
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "user@example.com",
    "role": "technician"
  }
}
```

**Error (401 Unauthorized):**
```json
{
  "error": "Invalid credentials",
  "message": "Email or password is incorrect"
}
```

---

## Assets

### GET /assets
Get all assets.

**Request:**
```http
GET /api/v1/assets HTTP/1.1
Authorization: Bearer {token}
```

**Query Parameters:**
- `filter`: Status filter (operational, maintenance, broken, archived)
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20)

**Response (200 OK):**
```json
{
  "data": [
    {
      "id": 1,
      "name": "Industrial Compressor",
      "status": "operational",
      "serialNumber": "SN-2024-001",
      "model": "XL-3000",
      "manufacturer": "TechCorp",
      "location": "Building A, Floor 2",
      "category": "Equipment",
      "assetTag": "ASSET-001",
      "purchaseDate": 1704067200000,
      "purchasePrice": 15000.00,
      "warrantyExpiry": 1735689600000,
      "description": "Main production compressor",
      "createdAt": 1704067200000,
      "updatedAt": 1704067200000
    }
  ],
  "meta": {
    "total": 125,
    "page": 1,
    "pageSize": 20,
    "totalPages": 7
  }
}
```

### GET /assets/{id}
Get single asset by ID.

**Request:**
```http
GET /api/v1/assets/1 HTTP/1.1
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "Industrial Compressor",
  "status": "operational",
  ...
}
```

### POST /assets
Create new asset.

**Request:**
```http
POST /api/v1/assets HTTP/1.1
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "New Equipment",
  "serialNumber": "SN-2024-002",
  "model": "XL-2000",
  "manufacturer": "TechCorp",
  "location": "Building B",
  "category": "Equipment",
  "assetTag": "ASSET-002",
  "purchaseDate": 1704067200000,
  "purchasePrice": 12000.00,
  "warrantyExpiry": 1735689600000,
  "description": "Backup equipment"
}
```

**Response (201 Created):**
```json
{
  "id": 126,
  "name": "New Equipment",
  ...
}
```

### PUT /assets/{id}
Update asset.

**Request:**
```http
PUT /api/v1/assets/1 HTTP/1.1
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Updated Equipment Name",
  "status": "maintenance",
  "location": "Building C"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "Updated Equipment Name",
  ...
}
```

### DELETE /assets/{id}
Delete asset.

**Request:**
```http
DELETE /api/v1/assets/1 HTTP/1.1
Authorization: Bearer {token}
```

**Response (204 No Content):**
```
(empty)
```

---

## Worksheets

### GET /worksheets
Get all worksheets.

**Request:**
```http
GET /api/v1/worksheets?filter=pending HTTP/1.1
Authorization: Bearer {token}
```

**Query Parameters:**
- `filter`: Status filter (pending, in_progress, completed, cancelled)
- `priority`: Filter by priority (low, medium, high, critical)

**Response (200 OK):**
```json
{
  "data": [
    {
      "id": 1,
      "title": "Monthly Maintenance Check",
      "status": "pending",
      "priority": "high",
      "description": "Complete monthly maintenance routine",
      "machineId": 5,
      "assignedToUserId": 2,
      "createdAt": 1704067200000,
      "updatedAt": 1704067200000
    }
  ],
  "meta": { ... }
}
```

### POST /worksheets
Create new worksheet.

**Request:**
```http
POST /api/v1/worksheets HTTP/1.1
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "Equipment Inspection",
  "description": "Full equipment inspection",
  "priority": "medium",
  "machineId": 1,
  "assignedToUserId": 3
}
```

**Response (201 Created):**
```json
{
  "id": 250,
  "title": "Equipment Inspection",
  "status": "pending",
  ...
}
```

### PUT /worksheets/{id}
Update worksheet.

**Response (200 OK):**
Similar to POST response.

### POST /worksheets/{id}/status
Change worksheet status.

**Request:**
```http
POST /api/v1/worksheets/1/status HTTP/1.1
Authorization: Bearer {token}
Content-Type: application/json

{
  "status": "in_progress"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "status": "in_progress",
  ...
}
```

### DELETE /worksheets/{id}
Delete worksheet.

**Response (204 No Content):**

---

## Machines

### GET /machines
Get all machines.

**Request:**
```http
GET /api/v1/machines HTTP/1.1
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
{
  "data": [
    {
      "id": 1,
      "name": "Production Machine A",
      "status": "operational",
      "serialNumber": "PM-2024-001",
      "model": "PM-3000",
      "manufacturer": "MachFactory",
      "productionLineId": 1,
      "installDate": 1704067200000,
      "description": "Main production line machine"
    }
  ],
  "meta": { ... }
}
```

### GET /machines/{id}
Get machine details.

### POST /machines
Create new machine.

### PUT /machines/{id}
Update machine.

### DELETE /machines/{id}
Delete machine.

---

## Inventory

### GET /inventory
Get all inventory items.

**Request:**
```http
GET /api/v1/inventory HTTP/1.1
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
{
  "data": [
    {
      "id": 1,
      "itemName": "Oil Filter",
      "currentQuantity": 50,
      "minQuantity": 10,
      "maxQuantity": 100,
      "location": "Warehouse A",
      "status": "normal",
      "unit": "pieces"
    }
  ],
  "meta": { ... }
}
```

### POST /inventory
Create new inventory item.

**Request:**
```http
POST /api/v1/inventory HTTP/1.1
Authorization: Bearer {token}
Content-Type: application/json

{
  "itemName": "Replacement Belt",
  "currentQuantity": 25,
  "minQuantity": 5,
  "maxQuantity": 50,
  "location": "Storage Room",
  "unit": "pieces"
}
```

**Response (201 Created):**

### PUT /inventory/{id}
Update inventory.

### DELETE /inventory/{id}
Delete inventory item.

---

## PM Tasks

### GET /pm-tasks
Get all PM tasks.

**Request:**
```http
GET /api/v1/pm-tasks HTTP/1.1
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
{
  "data": [
    {
      "id": 1,
      "machineId": 1,
      "machineName": "Production Machine A",
      "taskName": "Bearing Lubrication",
      "description": "Lubricate all machine bearings",
      "frequency": "weekly",
      "nextScheduled": 1704240000000,
      "lastExecuted": 1704067200000,
      "status": "scheduled",
      "priority": "high",
      "assignedToUserId": 2,
      "estimatedDuration": 30
    }
  ],
  "meta": { ... }
}
```

### POST /pm-tasks/{id}/execute
Mark PM task as executed.

**Request:**
```http
POST /api/v1/pm-tasks/1/execute HTTP/1.1
Authorization: Bearer {token}
Content-Type: application/json

{
  "status": "completed",
  "lastExecuted": 1704240000000
}
```

**Response (200 OK):**

---

## Error Codes

| Code | Status | Description |
|------|--------|-------------|
| 200 | OK | Successful request |
| 201 | Created | Resource created successfully |
| 204 | No Content | Request succeeded, no content to return |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Missing or invalid authentication token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Resource already exists (duplicate) |
| 500 | Server Error | Internal server error |
| 503 | Service Unavailable | Service temporarily unavailable |

### Error Response Format

```json
{
  "error": "error_code",
  "message": "Human readable error message",
  "details": {
    "field": "Specific field error (if applicable)"
  }
}
```

---

## Authentication Headers

All requests (except `/auth/login`) require:
```
Authorization: Bearer {jwt_token}
```

Token expires after 30 minutes. Use the `expiresIn` value from login response.

---

## Rate Limiting

- **Limit:** 100 requests per minute
- **Header:** `X-RateLimit-Remaining`
- **Error:** 429 Too Many Requests

---

**Last Updated:** 2025-01-14  
**Documentation Version:** 1.0

