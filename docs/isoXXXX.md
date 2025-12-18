Act as a Senior Software Architect and Full Stack Developer. Build a production-ready CMMS desktop application in Python (Flet + SQLite).

**CRITICAL COMPLIANCE INSTRUCTIONS (Szabványok és Törvények)**
The system must be architected to strictly comply with the following Hungarian and International standards:
1.  **GDPR & Infotv. (Data Privacy):** Passwords must be hashed (bcrypt). Users cannot be hard-deleted; implement an "Anonymize User" feature (Right to be Forgotten) that keeps statistics but removes PII (Personal Identifiable Information).
2.  **ISO 55001 (Asset Management):** Full lifecycle tracking. Assets cannot be deleted from DB, only marked as `status='Selejtezve'`.
3.  **2000. évi C. törvény (Szt. - Accounting):** Inventory changes must have an audit trail. Never just update `stock_quantity`. Create a `StockLog` entry for every movement.
4.  **MSZ EN 13460 (Maintenance Docs):** Worksheets must contain all mandatory fields: ID, Dates, Machine, Cause, Action, Parts, Personnel.
5.  **NAV Compliance:** The system generates INTERNAL documents ("Munkalap") only. Do NOT use the word "Számla" (Invoice) anywhere.

**0. LANGUAGE REQUIREMENT**
- **Communication:** Explain everything in **HUNGARIAN**.
- **UI Language:** All Labels, Buttons, Menus, Alerts must be in **HUNGARIAN**.

**1. Tech Stack**
- **Python 3.10+**, **Flet** (UI), **SQLite** + **SQLAlchemy** (ORM).
- Libraries: `pandas`, `qrcode`, `bcrypt` (security), `fpdf`.

**2. Database Schema (Enhanced for Compliance)**
- **Users:** `id`, `username`, `password_hash`, `role`, `is_active` (bool), `hourly_rate`.
- **Assets:** `id`, `name`, `parent_id`, `serial_number`, `manufacturer`, `install_date`, `status` ('Aktív', 'Selejtezve'), `manual_path`.
- **Parts:** `id`, `name`, `sku`, `stock_quantity`, `safety_stock`, `location`, `unit`, `avg_price`, `supplier`.
- **StockLogs (CRITICAL for Szt.):** `id`, `part_id`, `change_amount` (+/-), `reason` ('Beszerzés', 'Felhasználás', 'Korrekció'), `timestamp`, `user_id`.
- **Worksheets:** `id`, `user_id`, `asset_id`, `created_date`, `status` ('Nyitott', 'Alkatrészre_vár', 'Lezárt'), `breakdown_time`, `repair_finished_time`, `description`, `fault_cause` (MSZ EN 13460), `photo_path`.
- **WorksheetItems:** `id`, `worksheet_id`, `part_id`, `quantity_used`.

**3. Functional Requirements**

**A. Authentication & GDPR**
- Login with Hashed Passwords.
- **User Management:** instead of "Delete", implement "Deactivate/Anonymize".

**B. Inventory (Szt. Compliant)**
- **Stock Movement:** When adding parts or using them in a worksheet, AUTOMATICALY create a record in `StockLogs`.
- **Excel Import:** For initial population.
- **Visuals:** Red row if `stock <= safety_stock`.

**C. Worksheets (MSZ EN 13460 Compliant)**
- **Workflow:** Open -> Waiting -> Closed.
- **Mandatory Fields:** Do not allow closing if 'Description' or 'Dates' are missing.
- **Downtime Calc:** `Repair End` - `Breakdown Start`.
- **PDF Export:** Generate a professional PDF titled "KARBANTARTÁSI MUNKALAP" (not Invoice).

**D. Asset Lifecycle (ISO 55001)**
- Hierarchy View (Tree).
- History tab: Show all previous worksheets for the selected machine.

**4. Implementation Plan**
Step 1: Setup structure, `requirements.txt`.
Step 2: Create `models.py` strictly following the Schema above (including `StockLogs`).
Step 3: Create `database.py` with `bcrypt` password hashing init.
Step 4: Create Main UI & Login.
Step 5: Implement Inventory with Audit Logs.

**Let's start with Step 1, 2 and 3. Ensure the StockLogs table is created.**