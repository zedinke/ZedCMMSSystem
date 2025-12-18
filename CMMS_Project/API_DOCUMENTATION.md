# CMMS REST API Documentation

## Overview

The CMMS REST API provides programmatic access to all Computerized Maintenance Management System functionality. It uses JWT token-based authentication and follows RESTful principles.

**Base URL:** `http://localhost:8000/api`

**API Version:** 1.0.0

**Documentation:**
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

---

## Table of Contents

1. [Authentication](#authentication)
2. [API Endpoints](#api-endpoints)
   - [Authentication](#authentication-endpoints)
   - [Users](#users-endpoints)
   - [Machines](#machines-endpoints)
   - [Worksheets](#worksheets-endpoints)
   - [Assets](#assets-endpoints)
   - [Health](#health-endpoints)
3. [Error Handling](#error-handling)
4. [Common Patterns](#common-patterns)
5. [Integration Examples](#integration-examples)

---

## Authentication

### Login (Obtain Token)

The API uses JWT (JSON Web Tokens) for authentication. All protected endpoints require a valid JWT token in the `Authorization` header.

**Endpoint:** `POST /api/auth/login`

**Request:**
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "password123"
  }'
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjEsInJvbGVfbmFtZSI6ImFkbWluIiwiZXhwIjoxNzAyNDM5MjAwfQ.sig",
  "token_type": "bearer",
  "expires_in": 86400,
  "user_id": 1,
  "username": "admin",
  "role_name": "admin"
}
```

**Error Response (401 Unauthorized):**
```json
{
  "detail": "Invalid username or password"
}
```

### Using Token in Requests

Include the token in the `Authorization` header:

```bash
curl -X GET "http://localhost:8000/api/users/" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Token Validity:** Tokens expire after 24 hours

---

## API Endpoints

### Authentication Endpoints

#### Login
- **POST** `/api/auth/login`
- **Authentication:** Not required
- **Request:** `LoginRequest` (username, password)
- **Response:** `TokenResponse` (access_token, token_type, expires_in, user_id, username, role_name)
- **Status Codes:** 200 (success), 401 (invalid credentials), 422 (validation error)

---

### Users Endpoints

#### List Users
- **GET** `/api/users/`
- **Authentication:** Required
- **Query Parameters:**
  - `skip` (int, default: 0) - Number of records to skip
  - `limit` (int, default: 10, max: 100) - Number of records to return
  - `role_name` (string, optional) - Filter by role name
  - `status` (string, optional) - Filter by status
- **Response:** `UserListResponse` (total, items)

**Example:**
```bash
curl -X GET "http://localhost:8000/api/users/?skip=0&limit=10&role_name=manager" \
  -H "Authorization: Bearer <token>"
```

#### Get User by ID
- **GET** `/api/users/{user_id}`
- **Authentication:** Required
- **Path Parameters:** `user_id` (int)
- **Response:** `UserResponse`

**Example:**
```bash
curl -X GET "http://localhost:8000/api/users/1" \
  -H "Authorization: Bearer <token>"
```

#### Create User
- **POST** `/api/users/`
- **Authentication:** Required (admin, manager)
- **Request:** `UserCreate` (username, email, full_name?, phone?, role_id)
- **Response:** `UserResponse` (201 Created)

**Example:**
```bash
curl -X POST "http://localhost:8000/api/users/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "jsmith",
    "email": "john@company.com",
    "full_name": "John Smith",
    "phone": "+36301234567",
    "role_id": 2
  }'
```

#### Update User
- **PUT** `/api/users/{user_id}`
- **Authentication:** Required (admin, manager)
- **Path Parameters:** `user_id` (int)
- **Request:** `UserUpdate` (username?, email?, full_name?, phone?, role_id?)
- **Response:** `UserResponse`

**Example:**
```bash
curl -X PUT "http://localhost:8000/api/users/1" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"email": "john.new@company.com"}'
```

#### Delete User
- **DELETE** `/api/users/{user_id}`
- **Authentication:** Required (admin only)
- **Path Parameters:** `user_id` (int)
- **Response:** 204 No Content

**Example:**
```bash
curl -X DELETE "http://localhost:8000/api/users/5" \
  -H "Authorization: Bearer <token>"
```

#### Reset Password
- **POST** `/api/users/{user_id}/reset-password`
- **Authentication:** Required (admin, manager)
- **Path Parameters:** `user_id` (int)
- **Response:** `UserResponse`

**Example:**
```bash
curl -X POST "http://localhost:8000/api/users/5/reset-password" \
  -H "Authorization: Bearer <token>"
```

---

### Machines Endpoints

#### List Machines
- **GET** `/api/machines/`
- **Authentication:** Required
- **Query Parameters:**
  - `skip` (int, default: 0)
  - `limit` (int, default: 10, max: 100)
  - `status` (string, optional) - operational, maintenance, offline

#### Get Machine by ID
- **GET** `/api/machines/{machine_id}`
- **Authentication:** Required

#### Create Machine
- **POST** `/api/machines/`
- **Authentication:** Required
- **Request:** `MachineCreate` (name, model?, serial_number?, production_line_id?, status?)

**Example:**
```bash
curl -X POST "http://localhost:8000/api/machines/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "CNC Machine A1",
    "model": "HAAS VF-4",
    "serial_number": "ABC123456",
    "status": "operational"
  }'
```

#### Update Machine
- **PUT** `/api/machines/{machine_id}`
- **Authentication:** Required
- **Request:** `MachineUpdate` (name?, model?, serial_number?, production_line_id?, status?)

#### Delete Machine
- **DELETE** `/api/machines/{machine_id}`
- **Authentication:** Required

---

### Worksheets Endpoints

#### List Worksheets
- **GET** `/api/worksheets/`
- **Authentication:** Required
- **Query Parameters:**
  - `skip` (int)
  - `limit` (int)
  - `status` (string, optional) - pending, in_progress, completed
  - `machine_id` (int, optional)

#### Get Worksheet by ID
- **GET** `/api/worksheets/{worksheet_id}`
- **Authentication:** Required

#### Create Worksheet
- **POST** `/api/worksheets/`
- **Authentication:** Required
- **Request:** `WorksheetCreate` (machine_id, maintenance_type, description?, assigned_to_user_id?, status?)

**Example:**
```bash
curl -X POST "http://localhost:8000/api/worksheets/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "machine_id": 1,
    "maintenance_type": "preventive",
    "description": "Monthly maintenance check",
    "assigned_to_user_id": 2,
    "status": "pending"
  }'
```

#### Update Worksheet
- **PUT** `/api/worksheets/{worksheet_id}`
- **Authentication:** Required
- **Request:** `WorksheetUpdate` (description?, assigned_to_user_id?, status?)

#### Delete Worksheet
- **DELETE** `/api/worksheets/{worksheet_id}`
- **Authentication:** Required

---

### Assets Endpoints

#### List Assets
- **GET** `/api/assets/`
- **Authentication:** Required
- **Query Parameters:**
  - `skip` (int)
  - `limit` (int)
  - `status` (string, optional) - active, inactive, maintenance
  - `asset_type` (string, optional)
  - `machine_id` (int, optional)

#### Get Asset by ID
- **GET** `/api/assets/{asset_id}`
- **Authentication:** Required

#### Create Asset
- **POST** `/api/assets/`
- **Authentication:** Required
- **Request:** `AssetCreate` (name, asset_type, asset_tag?, machine_id?, status?)

#### Update Asset
- **PUT** `/api/assets/{asset_id}`
- **Authentication:** Required
- **Request:** `AssetUpdate` (name?, asset_type?, asset_tag?, machine_id?, status?)

#### Delete Asset
- **DELETE** `/api/assets/{asset_id}`
- **Authentication:** Required

---

### Health Endpoints

#### Health Check
- **GET** `/api/health/`
- **Authentication:** Not required
- **Response:** `HealthResponse` (status, timestamp, version)

**Example:**
```bash
curl -X GET "http://localhost:8000/api/health/"
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-13T10:30:45.123456",
  "version": "1.0.0"
}
```

#### Readiness Check
- **GET** `/api/health/ready`
- **Authentication:** Not required
- **Response:** 200 OK

---

## Error Handling

All errors follow a consistent format:

```json
{
  "detail": "Error message"
}
```

### Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | GET request successful |
| 201 | Created | POST request successful |
| 204 | No Content | DELETE successful |
| 400 | Bad Request | Invalid request format |
| 401 | Unauthorized | Missing or invalid token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Duplicate username/email |
| 422 | Validation Error | Invalid field values |
| 500 | Server Error | Internal server error |
| 503 | Unavailable | Service unhealthy |

---

## Common Patterns

### Pagination

All list endpoints support pagination:

```bash
curl -X GET "http://localhost:8000/api/users/?skip=20&limit=10" \
  -H "Authorization: Bearer <token>"
```

Response includes total count:
```json
{
  "total": 50,
  "items": [...]
}
```

### Filtering

Apply filters via query parameters:

```bash
curl -X GET "http://localhost:8000/api/worksheets/?status=pending&machine_id=1" \
  -H "Authorization: Bearer <token>"
```

### Role-Based Access Control

Endpoints may require specific roles:

| Endpoint | Required Role |
|----------|---------------|
| POST /users | admin, manager |
| PUT /users | admin, manager |
| DELETE /users | admin |
| POST /machines | any authenticated |
| POST /worksheets | any authenticated |

---

## Integration Examples

### Python Client

```python
import requests
from datetime import datetime, timedelta

class CMSSClient:
    def __init__(self, base_url="http://localhost:8000/api"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.username = None
        self.role_name = None
    
    def login(self, username, password):
        """Login and obtain JWT token"""
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={"username": username, "password": password}
        )
        response.raise_for_status()
        data = response.json()
        
        self.token = data["access_token"]
        self.user_id = data["user_id"]
        self.username = data["username"]
        self.role_name = data["role_name"]
        
        return data
    
    def get_headers(self):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.token}"}
    
    def list_users(self, skip=0, limit=10):
        """List users"""
        response = requests.get(
            f"{self.base_url}/users/",
            headers=self.get_headers(),
            params={"skip": skip, "limit": limit}
        )
        response.raise_for_status()
        return response.json()
    
    def get_user(self, user_id):
        """Get user by ID"""
        response = requests.get(
            f"{self.base_url}/users/{user_id}",
            headers=self.get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def create_user(self, username, email, full_name, phone, role_id):
        """Create new user"""
        response = requests.post(
            f"{self.base_url}/users/",
            headers=self.get_headers(),
            json={
                "username": username,
                "email": email,
                "full_name": full_name,
                "phone": phone,
                "role_id": role_id
            }
        )
        response.raise_for_status()
        return response.json()
    
    def update_user(self, user_id, **kwargs):
        """Update user"""
        response = requests.put(
            f"{self.base_url}/users/{user_id}",
            headers=self.get_headers(),
            json=kwargs
        )
        response.raise_for_status()
        return response.json()
    
    def delete_user(self, user_id):
        """Delete user"""
        response = requests.delete(
            f"{self.base_url}/users/{user_id}",
            headers=self.get_headers()
        )
        response.raise_for_status()
        return response.status_code == 204
    
    def list_machines(self, skip=0, limit=10, status=None):
        """List machines"""
        params = {"skip": skip, "limit": limit}
        if status:
            params["status"] = status
        
        response = requests.get(
            f"{self.base_url}/machines/",
            headers=self.get_headers(),
            params=params
        )
        response.raise_for_status()
        return response.json()

# Usage Example
if __name__ == "__main__":
    client = CMSSClient()
    
    # Login
    print("Logging in...")
    client.login("admin", "password123")
    print(f"✅ Logged in as {client.username} ({client.role_name})")
    
    # List users
    print("\nListing users...")
    users = client.list_users(limit=5)
    print(f"Found {users['total']} users:")
    for user in users['items']:
        print(f"  - {user['username']} ({user['role']['name']})")
    
    # Create new user
    print("\nCreating new user...")
    new_user = client.create_user(
        username="jsmith",
        email="john@company.com",
        full_name="John Smith",
        phone="+36301234567",
        role_id=2
    )
    print(f"✅ Created user: {new_user['username']}")
    
    # Update user
    print("\nUpdating user...")
    updated = client.update_user(new_user['id'], phone="+36309876543")
    print(f"✅ Updated phone: {updated['phone']}")
    
    # List machines
    print("\nListing machines...")
    machines = client.list_machines(status="operational")
    print(f"Found {machines['total']} operational machines:")
    for machine in machines['items']:
        print(f"  - {machine['name']} ({machine['status']})")
```

### JavaScript/Node.js Client

```javascript
const axios = require('axios');

class CMSSClient {
    constructor(baseURL = 'http://localhost:8000/api') {
        this.baseURL = baseURL;
        this.token = null;
        this.userId = null;
        this.username = null;
        this.roleName = null;
    }

    async login(username, password) {
        try {
            const response = await axios.post(
                `${this.baseURL}/auth/login`,
                { username, password }
            );
            
            this.token = response.data.access_token;
            this.userId = response.data.user_id;
            this.username = response.data.username;
            this.roleName = response.data.role_name;
            
            return response.data;
        } catch (error) {
            throw new Error(`Login failed: ${error.response.data.detail}`);
        }
    }

    getHeaders() {
        return {
            'Authorization': `Bearer ${this.token}`,
            'Content-Type': 'application/json'
        };
    }

    async listUsers(skip = 0, limit = 10) {
        const response = await axios.get(
            `${this.baseURL}/users/`,
            {
                headers: this.getHeaders(),
                params: { skip, limit }
            }
        );
        return response.data;
    }

    async createUser(username, email, fullName, phone, roleId) {
        const response = await axios.post(
            `${this.baseURL}/users/`,
            {
                username,
                email,
                full_name: fullName,
                phone,
                role_id: roleId
            },
            { headers: this.getHeaders() }
        );
        return response.data;
    }

    async listMachines(skip = 0, limit = 10, status = null) {
        const params = { skip, limit };
        if (status) params.status = status;
        
        const response = await axios.get(
            `${this.baseURL}/machines/`,
            {
                headers: this.getHeaders(),
                params
            }
        );
        return response.data;
    }
}

// Usage Example
(async () => {
    const client = new CMSSClient();
    
    try {
        // Login
        console.log('Logging in...');
        await client.login('admin', 'password123');
        console.log(`✅ Logged in as ${client.username}`);
        
        // List users
        console.log('\nListing users...');
        const users = await client.listUsers(0, 5);
        console.log(`Found ${users.total} users:`);
        users.items.forEach(user => {
            console.log(`  - ${user.username} (${user.role.name})`);
        });
        
        // Create user
        console.log('\nCreating new user...');
        const newUser = await client.createUser(
            'jsmith',
            'john@company.com',
            'John Smith',
            '+36301234567',
            2
        );
        console.log(`✅ Created user: ${newUser.username}`);
        
    } catch (error) {
        console.error('❌ Error:', error.message);
    }
})();
```

### cURL Examples

```bash
# Login
TOKEN=$(curl -s -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password123"}' \
  | jq -r '.access_token')

echo "Token: $TOKEN"

# List users
curl -X GET "http://localhost:8000/api/users/" \
  -H "Authorization: Bearer $TOKEN"

# Create machine
curl -X POST "http://localhost:8000/api/machines/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "CNC Machine A1",
    "model": "HAAS VF-4",
    "serial_number": "ABC123456",
    "status": "operational"
  }'

# Get health status
curl -X GET "http://localhost:8000/api/health/"
```

---

## Running the API Server

```bash
# Start the API server
python api/server.py

# Or use uvicorn directly
uvicorn api.app:create_app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000` with automatic documentation at `http://localhost:8000/api/docs`.

---

## Support & Troubleshooting

### Common Issues

**401 Unauthorized**
- Solution: Ensure token is valid and not expired. Re-login to get a new token.

**403 Forbidden**
- Solution: Your user role doesn't have permission for this operation. Contact your administrator.

**409 Conflict**
- Solution: Username or email already exists. Use a unique value.

**422 Validation Error**
- Solution: Check request parameters match the schema (required fields, data types).

### Performance Tips

1. **Use pagination** - Always specify `skip` and `limit` parameters
2. **Filter early** - Use status, role_name filters to reduce data size
3. **Batch operations** - Reuse the same token for multiple requests
4. **Monitor health** - Check `/api/health/` to ensure API is responsive

---

## Version History

- **v1.0.0** (2025-12-13) - Initial release
  - User management (CRUD, password reset)
  - Machine management
  - Worksheet tracking
  - Asset inventory
  - JWT authentication
  - Role-based access control
