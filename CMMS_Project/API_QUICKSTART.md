# 🚀 CMMS REST API - Quick Start Guide

## Start the API Server

```bash
cd E:\Artence_CMMS\CMMS_Project
python api/server.py
```

**Server starts at:** http://localhost:8000

---

## Access API Documentation

Open in your browser:
- **Swagger UI (Interactive):** http://localhost:8000/api/docs
- **ReDoc (Beautiful):** http://localhost:8000/api/redoc

---

## Login (Get JWT Token)

**Command:**
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user_id": 1,
  "username": "admin",
  "role_name": "admin"
}
```

Save the `access_token` for subsequent requests.

---

## Use the Token

Add to Authorization header:

```bash
curl -X GET "http://localhost:8000/api/users/" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## API Endpoints

### Users
- `GET /api/users/` - List all users
- `GET /api/users/{user_id}` - Get user details
- `POST /api/users/` - Create user (admin/manager)
- `PUT /api/users/{user_id}` - Update user (admin/manager)
- `DELETE /api/users/{user_id}` - Delete user (admin)
- `POST /api/users/{user_id}/reset-password` - Reset password

### Machines
- `GET /api/machines/` - List machines
- `GET /api/machines/{machine_id}` - Get machine
- `POST /api/machines/` - Create machine
- `PUT /api/machines/{machine_id}` - Update machine
- `DELETE /api/machines/{machine_id}` - Delete machine

### Worksheets
- `GET /api/worksheets/` - List worksheets
- `GET /api/worksheets/{worksheet_id}` - Get worksheet
- `POST /api/worksheets/` - Create worksheet
- `PUT /api/worksheets/{worksheet_id}` - Update worksheet
- `DELETE /api/worksheets/{worksheet_id}` - Delete worksheet

### Assets/Parts
- `GET /api/assets/` - List assets
- `GET /api/assets/{asset_id}` - Get asset
- `POST /api/assets/` - Create asset
- `PUT /api/assets/{asset_id}` - Update asset
- `DELETE /api/assets/{asset_id}` - Delete asset

### Health
- `GET /api/health/` - Health check
- `GET /api/health/ready` - Readiness probe

---

## Example: List Users

```bash
# 1. Login
TOKEN=$(curl -s -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}' | jq -r '.access_token')

# 2. List users
curl -X GET "http://localhost:8000/api/users/?skip=0&limit=10" \
  -H "Authorization: Bearer $TOKEN" | jq

# 3. Get single user
curl -X GET "http://localhost:8000/api/users/1" \
  -H "Authorization: Bearer $TOKEN" | jq
```

---

## Example: Create Machine

```bash
TOKEN=$(curl -s -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}' | jq -r '.access_token')

curl -X POST "http://localhost:8000/api/machines/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "CNC Machine A1",
    "model": "HAAS VF-4",
    "serial_number": "ABC123456",
    "status": "operational"
  }' | jq
```

---

## Python Client Example

```python
import requests

BASE_URL = "http://localhost:8000/api"

# Login
response = requests.post(
    f"{BASE_URL}/auth/login",
    json={"username": "admin", "password": "admin"}
)
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# List users
users = requests.get(f"{BASE_URL}/users/", headers=headers).json()
print(f"Found {users['total']} users")
for user in users['items']:
    print(f"  - {user['username']} ({user['role']['name']})")

# Create machine
machine = requests.post(
    f"{BASE_URL}/machines/",
    headers=headers,
    json={
        "name": "New CNC",
        "model": "HAAS VF-4",
        "status": "operational"
    }
).json()
print(f"Created machine: {machine['name']}")

# Update machine
updated = requests.put(
    f"{BASE_URL}/machines/{machine['id']}",
    headers=headers,
    json={"status": "maintenance"}
).json()
print(f"Machine status: {updated['status']}")
```

---

## Pagination

All list endpoints support pagination:

```bash
# Get page 2 (skip 10 items, take 10)
curl -X GET "http://localhost:8000/api/users/?skip=10&limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Filtering

Filter by status:

```bash
# Get only operational machines
curl -X GET "http://localhost:8000/api/machines/?status=operational" \
  -H "Authorization: Bearer $TOKEN"

# Get only pending worksheets
curl -X GET "http://localhost:8000/api/worksheets/?status=pending" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Error Handling

Invalid token:
```bash
curl -X GET "http://localhost:8000/api/users/" \
  -H "Authorization: Bearer invalid_token"

# Response: 401 Unauthorized
# {"detail":"Invalid or expired token"}
```

Resource not found:
```bash
curl -X GET "http://localhost:8000/api/users/99999" \
  -H "Authorization: Bearer $TOKEN"

# Response: 404 Not Found
# {"detail":"User not found"}
```

Insufficient permissions:
```bash
curl -X DELETE "http://localhost:8000/api/users/1" \
  -H "Authorization: Bearer $TECHNICIAN_TOKEN"

# Response: 403 Forbidden
# {"detail":"This operation requires one of these roles: admin"}
```

---

## Role-Based Access

| Operation | Required Role | Endpoint |
|-----------|---------------|----------|
| Login | Any | POST /auth/login |
| List Users | Any authenticated | GET /users/ |
| Create User | admin, manager | POST /users/ |
| Update User | admin, manager | PUT /users/{id} |
| Delete User | admin | DELETE /users/{id} |
| Reset Password | admin, manager | POST /users/{id}/reset-password |
| Create Machine | Any authenticated | POST /machines/ |
| Create Worksheet | Any authenticated | POST /worksheets/ |

---

## Stop the Server

Press `Ctrl+C` in the terminal running the server.

---

## Full Documentation

See **API_DOCUMENTATION.md** for:
- Complete endpoint reference
- All request/response schemas
- Detailed authentication workflow
- Advanced usage patterns
- Integration examples
- Troubleshooting guide

---

## File Structure

```
api/
├── app.py               # FastAPI factory
├── server.py            # Entry point (python api/server.py)
├── security.py          # JWT, tokens, password hashing
├── schemas.py           # Pydantic models
├── dependencies.py      # Auth, DB, role injection
└── routers/
    ├── auth.py          # Login endpoint
    ├── users.py         # User CRUD
    ├── machines.py      # Machine CRUD
    ├── worksheets.py    # Worksheet CRUD
    ├── assets.py        # Asset/Part CRUD
    └── health.py        # Health checks
```

---

## Next Steps

1. ✅ Start the API server
2. ✅ Open http://localhost:8000/api/docs
3. ✅ Login with admin/admin
4. ✅ Test endpoints in Swagger UI
5. ✅ Read API_DOCUMENTATION.md for advanced usage

---

**Status:** ✨ API Server Ready to Use!
