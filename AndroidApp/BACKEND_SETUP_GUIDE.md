# Backend Setup útmutató - CMMS Android App

## Probléma
Az Android app nem tud közvetlenül MySQL adatbázishoz csatlakozni biztonsági okok miatt.

## Megoldás: Egyszerű REST API Backend

---

## Opció 1: Node.js Backend (Ajánlott - Legegyszerűbb)

### Telepítés (5 perc)

1. **Node.js telepítése**: https://nodejs.org/

2. **Backend mappa létrehozása**:
```bash
mkdir cmms-backend
cd cmms-backend
npm init -y
npm install express mysql2 cors body-parser jsonwebtoken bcrypt
```

3. **server.js fájl létrehozása**:
```javascript
const express = require('express');
const mysql = require('mysql2/promise');
const cors = require('cors');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');

const app = express();
app.use(cors());
app.use(express.json());

// MySQL kapcsolat
const pool = mysql.createPool({
  host: 'your-mysql-host.com',     // Cseréld le!
  user: 'your-username',             // Cseréld le!
  password: 'your-password',         // Cseréld le!
  database: 'cmms_db',               // Cseréld le!
  waitForConnections: true,
  connectionLimit: 10
});

const SECRET_KEY = 'your-secret-key-change-this';

// ==================== AUTH ====================

// Login
app.post('/api/v1/auth/login', async (req, res) => {
  try {
    const { username, password } = req.body;
    const [users] = await pool.query(
      'SELECT * FROM users WHERE email = ?', 
      [username]
    );
    
    if (users.length === 0) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }
    
    const user = users[0];
    // Egyszerű jelszó ellenőrzés (később bcrypt-et használj!)
    if (user.password !== password && !await bcrypt.compare(password, user.password_hash || '')) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }
    
    const token = jwt.sign({ userId: user.id }, SECRET_KEY, { expiresIn: '24h' });
    
    res.json({
      accessToken: token,
      userId: user.id,
      username: user.email,
      roleName: user.role || 'USER'
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// ==================== MACHINES ====================

app.get('/api/v1/machines', async (req, res) => {
  try {
    const [machines] = await pool.query('SELECT * FROM machines ORDER BY created_at DESC');
    res.json(machines);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/api/v1/machines/:id', async (req, res) => {
  try {
    const [machines] = await pool.query('SELECT * FROM machines WHERE id = ?', [req.params.id]);
    res.json(machines[0] || null);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.post('/api/v1/machines', async (req, res) => {
  try {
    const [result] = await pool.query('INSERT INTO machines SET ?', req.body);
    res.json({ id: result.insertId, ...req.body });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// ==================== WORKSHEETS ====================

app.get('/api/v1/worksheets', async (req, res) => {
  try {
    const [worksheets] = await pool.query('SELECT * FROM worksheets ORDER BY created_at DESC');
    res.json(worksheets);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// ==================== INVENTORY ====================

app.get('/api/v1/inventory', async (req, res) => {
  try {
    const [items] = await pool.query('SELECT * FROM inventory ORDER BY name');
    res.json(items);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Szerver indítása
const PORT = process.env.PORT || 8080;
app.listen(PORT, () => {
  console.log(`CMMS Backend running on http://localhost:${PORT}`);
});
```

4. **Indítás**:
```bash
node server.js
```

5. **Android app beállítása**:
- Ha lokálisan fut: `BASE_URL = "http://10.0.2.2:8080/api/v1/"`
- Ha távoli szerver: `BASE_URL = "https://your-server.com/api/v1/"`

---

## Opció 2: PHP Backend (Ha van webhosting)

### 1. Fájlstruktúra:
```
public_html/
├── api/
│   ├── auth/
│   │   └── login.php
│   ├── machines/
│   │   ├── index.php (GET all)
│   │   ├── get.php (GET by id)
│   │   └── create.php (POST)
│   ├── worksheets/
│   └── inventory/
└── config.php
```

### 2. config.php:
```php
<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE');
header('Access-Control-Allow-Headers: Content-Type, Authorization');

$host = 'your-mysql-host.com';
$db = 'cmms_db';
$user = 'your-username';
$pass = 'your-password';

$conn = new mysqli($host, $user, $pass, $db);
if ($conn->connect_error) {
    http_response_code(500);
    echo json_encode(['error' => 'Database connection failed']);
    exit;
}
?>
```

### 3. api/auth/login.php:
```php
<?php
require_once '../../config.php';

$input = json_decode(file_get_contents('php://input'), true);
$username = $input['username'] ?? '';
$password = $input['password'] ?? '';

$stmt = $conn->prepare("SELECT * FROM users WHERE email = ?");
$stmt->bind_param("s", $username);
$stmt->execute();
$result = $stmt->get_result();

if ($row = $result->fetch_assoc()) {
    if (password_verify($password, $row['password_hash'])) {
        echo json_encode([
            'accessToken' => bin2hex(random_bytes(32)),
            'userId' => (int)$row['id'],
            'username' => $row['email'],
            'roleName' => $row['role'] ?? 'USER'
        ]);
    } else {
        http_response_code(401);
        echo json_encode(['error' => 'Invalid credentials']);
    }
} else {
    http_response_code(401);
    echo json_encode(['error' => 'User not found']);
}
?>
```

---

## Opció 3: Python Flask (Közepes)

```python
from flask import Flask, request, jsonify
import mysql.connector
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

db = mysql.connector.connect(
    host="your-mysql-host.com",
    user="your-username",
    password="your-password",
    database="cmms_db"
)

@app.route('/api/v1/auth/login', methods=['POST'])
def login():
    data = request.json
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email=%s", (data['username'],))
    user = cursor.fetchone()
    
    if user and user['password'] == data['password']:
        return jsonify({
            'accessToken': 'token123',
            'userId': user['id'],
            'username': user['email'],
            'roleName': user['role']
        })
    return jsonify({'error': 'Invalid credentials'}), 401

if __name__ == '__main__':
    app.run(port=8080)
```

---

## MySQL Adatbázis Séma (Példa)

```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,  -- Vagy password_hash
    role VARCHAR(50) DEFAULT 'USER',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE machines (
    id INT AUTO_INCREMENT PRIMARY KEY,
    production_line_id INT,
    name VARCHAR(255) NOT NULL,
    serial_number VARCHAR(100),
    model VARCHAR(100),
    manufacturer VARCHAR(100),
    status VARCHAR(50),
    asset_tag VARCHAR(50),
    description TEXT,
    install_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE worksheets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    worksheet_number VARCHAR(50) UNIQUE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    type VARCHAR(50),
    priority VARCHAR(20),
    status VARCHAR(50),
    assigned_to_user_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE inventory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    sku VARCHAR(100),
    quantity INT DEFAULT 0,
    min_stock_level INT DEFAULT 0,
    location VARCHAR(255),
    unit_price DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Teszt felhasználó
INSERT INTO users (email, password, role) 
VALUES ('admin@example.com', 'Admin123456', 'ADMIN');
```

---

## Android App Konfiguráció

### Constants.kt beállítása:

```kotlin
object Constants {
    // Lokális teszt (Node.js szerver a gépeden):
    const val BASE_URL = "http://10.0.2.2:8080/api/v1/"
    
    // Vagy távoli szerver:
    // const val BASE_URL = "https://your-domain.com/api/v1/"
    
    const val TIMEOUT_SECONDS = 30L
}
```

---

## Deployment (Éles környezet)

### 1. Cloud Hosting opciók:
- **Heroku** (ingyenes tier): Node.js/PHP
- **Railway.app** (ingyenes): Node.js
- **Vercel** (ingyenes): Node.js API routes
- **AWS EC2** (fizetős): Teljes kontroll
- **DigitalOcean** ($5/hó): VPS

### 2. HTTPS beállítás (kötelező élesben):
- Let's Encrypt (ingyenes SSL)
- Cloudflare (ingyenes SSL + CDN)

---

## Gyors Start (Legegyszerűbb)

1. Telepíts Node.js-t
2. Másold be a fenti `server.js` kódot
3. Állítsd be a MySQL adatokat
4. `npm install express mysql2 cors jsonwebtoken bcrypt`
5. `node server.js`
6. Android app: `BASE_URL = "http://10.0.2.2:8080/api/v1/"`

✅ Kész! Az app működni fog a MySQL szerverrel.

