Act as a Senior Software Architect and Full Stack Developer. I need you to build a comprehensive Maintenance Management System (CMMS) desktop application.

**Project Context:**
- **Target Platform:** Windows Desktop (.exe) primarily, designed with responsiveness for a future Android port.
- **Tech Stack:**
  - Language: **Python**
  - UI Framework: **Flet** (Flutter for Python) for modern Material Design.
  - Database: **SQLite** (local file) using **SQLAlchemy** ORM.
  - Libraries: `pandas` (for Excel import), `qrcode`, `Pillow` (images).
- **Goal:** A robust, standalone system for managing maintenance, inventory, and automated reporting.

**Detailed Feature Requirements:**

1.  **User Authentication & Roles:**
    -   **Manager:** Full access (Inventory editing, Settings, Reports).
    -   **Technician:** Restricted access (Create Worksheets, View Assets, View Inventory without edit rights).

2.  **Asset Management:**
    -   Hierarchy: Production Line -> Machine -> Module.
    -   **Document Storage:** Allow uploading/linking a PDF manual to a Machine (store file path in DB).
    -   **History:** View all past worksheets associated with a specific machine.

3.  **Inventory & Warehouse:**
    -   Fields: Name, SKU, Buy Price, Sell Price, Stock, Safety Stock, Location, Supplier.
    -   **Bulk Import:** Add a button to import Parts from an **Excel/CSV file** (essential for initial setup).
    -   **QR Code:** Generate/Print QR codes for parts.
    -   **Restock Logic:** If Stock <= Safety Stock, flag as "To Order".

4.  **Worksheet System (The Core):**
    -   **Workflow Status:** Implement a status field: **'Open', 'Waiting for Parts', 'Closed'**.
        -   *Open:* Work in progress.
        -   *Waiting:* Paused due to lack of parts.
        -   *Closed:* Work finished, stock deducted.
    -   **Downtime Tracking:** Input 'Breakdown Time' and 'Repair Finished Time' to calculate total downtime hours.
    -   **Parts Usage:** Add parts (deducts from stock only when status becomes 'Closed' or explicitly saved).
    -   **Photo:** Attach an image of the repair (store path).
    -   **Output:** Save as PDF in `worksheets/YYYY-MM-DD/`.

5.  **Preventive Maintenance (PM):**
    -   Schedule tasks (e.g., "Weekly Greasing" every 7 days).
    -   Dashboard shows "Due Today" tasks.

6.  **Dashboard:**
    -   Charts: Worksheets per Status, Top Machines by Downtime.

**Coding Guidelines (Strict):**
-   **Modular Structure:** Split code into `main.py`, `database.py`, `models.py`, and a `views/` folder for UI screens.
-   **Full File Output:** When modifying or creating a file, **ALWAYS provide the full content of the file**. Do not use placeholders like `# ... rest of code` or diffs. I need to copy-paste entire files.

**Implementation Plan:**
1.  Define the project folder structure and `requirements.txt`.
2.  Create `models.py` with SQLAlchemy classes (including Status, Downtime, PDF paths).
3.  Create `database.py` to init the DB.
4.  Create the Main Navigation Layout.

Let's start with Step 1, 2 and 3: Structure, Requirements and Database Models.