# CMMS System – Detailed Step-by-Step Implementation Plan

## Bilingual (English/Hungarian) Maintenance Management System
### Complete Technical Roadmap for Python/Flet Desktop Application

---

## Table of Contents
1. [Phase 1: Foundation & Project Setup](#phase-1-foundation--project-setup-week-1)
2. [Phase 2: Database Models & Core Schema](#phase-2-database-models--core-schema-week-1-days-3-5)
3. [Phase 3: Authentication & Core Services](#phase-3-authentication--core-services-layer-week-2-days-1-2)
4. [Phase 4: Main UI Framework & Navigation](#phase-4-main-ui-framework--navigation-week-2-days-3-5)
5. [Phase 5: Asset Management Module](#phase-5-asset-management-module-week-3-days-1-2)
6. [Phase 6: Inventory Management Module](#phase-6-inventory-management-module-week-3-days-3-5)
7. [Phase 7: Worksheet Management (Core)](#phase-7-worksheet-management-core-week-4)
8. [Phase 8: Preventive Maintenance Module](#phase-8-preventive-maintenance-module-week-4-days-3-5)
9. [Phase 9: Dashboard & Reporting](#phase-9-dashboard--reporting-week-5-days-1-2)
10. [Phase 10: Localization Completion & Refinement](#phase-10-localization-completion--refinement-week-5-days-3-4)
11. [Phase 11: Testing & Quality Assurance](#phase-11-testing--quality-assurance-week-5-day-5--week-6-days-1-2)
12. [Phase 12: Polish, Packaging & Deployment](#phase-12-polish-packaging--deployment-week-6-days-3-5)

---

## Phase 1: Foundation & Project Setup (Week 1)

### 1.1 Create Project Folder Structure

- Initialize `CMMS_Project/` with subfolders: `config/`, `database/`, `localization/`, `services/`, `ui/`, `utils/`, `data/`, `tests/`
- Create placeholder files: `__init__.py` in each folder, `main.py`, `requirements.txt`, `README.md`
- Set up `.gitignore`: Exclude `*.db`, `data/`, `logs/`, `.env`, `__pycache__/`
- Create `data/` subfolders: `database/`, `files/equipment_manuals/`, `files/maintenance_photos/`, `reports/generated/`, `system_backups/`, `logs/`

### 1.2 Define & Create requirements.txt

Dependencies:
- **UI**: `flet==0.X.X` (latest stable)
- **Database**: `sqlalchemy==2.0.X`, `alembic==1.X.X`
- **Utilities**: `pandas==2.X.X`, `qrcode==7.X.X`, `Pillow==10.X.X`
- **PDF Generation**: `weasyprint==60.X.X`, `jinja2==3.X.X`
- **Excel**: `openpyxl==3.X.X` (for pandas Excel support)
- **Security**: `argon2-cffi==23.X.X`, `cryptography==41.X.X`
- **Localization**: `babel==2.X.X`
- **Database Drivers**: (SQLite built-in with Python)
- **Testing**: `pytest==7.X.X`, `pytest-cov==4.X.X`
- **Utilities**: `python-dotenv==1.X.X`, `python-dateutil==2.X.X`

### 1.3 Initialize SQLite Database Structure

- Create `database/connection.py`: Engine initialization with `StaticPool` for SQLite
- Create `database/session_manager.py`: Session factory using `sessionmaker()`
- Create `config/settings.py`: Database path, debug mode, file upload limits, app constants
- Write initialization logic: Check if DB exists; if not, create schema on first run

### 1.4 Set Up Localization Framework

- Create `localization/translator.py`: Singleton `Translator` class with methods:
  - `load_language(lang_code)` – Load JSON file into memory
  - `get_text(key, **kwargs)` – Lookup nested key with parameter interpolation
  - `get_available_languages()` – Return list of loaded languages
  - `set_current_language(code)` – Update current language and trigger callbacks
- Create `localization/language_manager.py`: Persist language selection to database
- Create translation JSON files: `localization/translations/en.json`, `hu.json`
  - Populate with core UI strings: common buttons (save, cancel, ok, delete), menu items, form labels, validation messages
  - Use hierarchical structure: `auth.login.username_label`, `common.buttons.save`, `messages.error.required_field`

### 1.5 Initial Configuration & Constants

- `config/constants.py`: Define file upload limits (10MB), supported formats (PDF, JPG, PNG), database paths, default values
- `config/app_config.py`: App title, version, window size, default language (English)

### 1.6 Version Control & Documentation

- Initialize Git repo; first commit with project skeleton
- Create `README.md`: Project overview, setup instructions, folder structure explanation
- Create `ARCHITECTURE.md`: High-level system design and module descriptions

**Deliverables:**
- Working project folder structure
- `requirements.txt` ready for `pip install`
- SQLite connection infrastructure in place
- Bilingual translation framework loaded
- First commit with skeleton code

---

## Phase 2: Database Models & Core Schema (Week 1, Days 3-5)

### 2.1 User & Authentication Models

Create in `database/models.py`:
- **`User`**: `id`, `username` (unique), `email`, `password_hash`, `role_id` (FK), `is_active`, `language_preference` (EN/HU), `created_at`, `updated_at`
- **`Role`**: `id`, `name` (Manager/Technician), `permissions` (JSON blob with feature flags)
- **`UserSession`**: `id`, `user_id` (FK), `token_hash`, `created_at`, `expires_at`, `last_activity_at`
- **`AuditLog`**: `id`, `user_id` (FK), `action_type` (login, create, edit, delete), `entity_type` (equipment, work_order), `entity_id`, `timestamp`, `changes` (JSON)

**Relationships:**
- User ← (1:M) → Role
- User ← (1:M) → UserSession
- User ← (1:M) → AuditLog

### 2.2 Asset Management Models

- **`ProductionLine`**: `id`, `name`, `description`, `location`, `created_at`
- **`Machine`**: `id`, `production_line_id` (FK), `name`, `serial_number`, `model`, `manufacturer`, `manual_pdf_path`, `created_at`, `updated_at`
- **`Module`**: `id`, `machine_id` (FK), `name`, `description`, `specifications` (JSON), `created_at`
- **`AssetHistory`**: `id`, `asset_id` (Machine or Module), `action_type` (created, modified, manual_updated), `timestamp`, `user_id` (FK), `description`

**Relationships:**
- ProductionLine ← (1:M) → Machine
- Machine ← (1:M) → Module
- Asset ← (1:M) → AssetHistory (via polymorphic or separate tables)

### 2.3 Inventory & Warehouse Models

- **`Part`**: `id`, `sku` (unique), `name`, `description`, `category`, `buy_price`, `sell_price`, `safety_stock`, `reorder_quantity`, `supplier_id` (FK), `last_count_date`, `created_at`
- **`Supplier`**: `id`, `name`, `contact_person`, `email`, `phone`, `address`, `city`, `postal_code`, `country`
- **`InventoryLevel`**: `id`, `part_id` (FK, unique), `quantity_on_hand`, `quantity_reserved`, `bin_location`, `last_updated`
- **`StockTransaction`**: `id`, `part_id` (FK), `transaction_type` (received, issued, adjustment), `quantity`, `reference_id` (worksheet_id, purchase_order_id), `reference_type`, `user_id` (FK), `notes`, `timestamp`
- **`QRCodeData`**: `id`, `part_id` (FK), `qr_data`, `generated_at`, `is_printed` (boolean)

**Relationships:**
- Part ← (1:M) → InventoryLevel (unique pairing)
- Part ← (1:M) → StockTransaction
- Supplier ← (1:M) → Part
- Part ← (1:M) → QRCodeData

### 2.4 Worksheet Models (Core)

- **`Worksheet`**: `id`, `machine_id` (FK), `assigned_to_user_id` (FK), `title`, `description`, `status` (Open/Waiting for Parts/Closed), `breakdown_time` (datetime), `repair_finished_time` (datetime), `total_downtime_hours` (calculated), `created_at`, `closed_at`, `notes`
- **`WorksheetPart`**: `id`, `worksheet_id` (FK), `part_id` (FK), `quantity_used`, `unit_cost_at_time`, `notes`, `added_at`
- **`WorksheetPhoto`**: `id`, `worksheet_id` (FK), `photo_path` (stored as UUID filename), `original_filename`, `description`, `uploaded_at`
- **`WorksheetPDF`**: `id`, `worksheet_id` (FK, unique), `pdf_path`, `generated_at`, `page_count`

**Relationships:**
- Machine ← (1:M) → Worksheet
- User ← (1:M) → Worksheet
- Worksheet ← (1:M) → WorksheetPart
- Part ← (1:M) → WorksheetPart
- Worksheet ← (1:M) → WorksheetPhoto
- Worksheet ← (1:1) → WorksheetPDF

### 2.5 Preventive Maintenance Models

- **`PMTask`**: `id`, `machine_id` (FK), `task_name`, `task_description`, `frequency_days`, `last_executed_date`, `next_due_date`, `is_active` (boolean), `created_at`
- **`PMSchedule`**: `id`, `pm_task_id` (FK), `scheduled_date` (for one-off schedules)
- **`PMHistory`**: `id`, `pm_task_id` (FK), `executed_date`, `assigned_to_user_id` (FK), `completed_by_user_id` (FK), `completion_status` (completed/skipped), `notes`, `duration_minutes`

**Relationships:**
- Machine ← (1:M) → PMTask
- PMTask ← (1:M) → PMHistory
- User ← (1:M) → PMHistory (assigned_to and completed_by)

### 2.6 Configuration & Settings Models

- **`AppSetting`**: `id`, `key` (unique), `value` (JSON-friendly), `description`, `updated_at`
  - Store: company name, default currency, timezone, email settings for alerts, backup schedule

### 2.7 Define Indexes & Constraints

- Index on `User.username`, `Part.sku` (unique)
- Index on `Worksheet.machine_id`, `Worksheet.status`, `Worksheet.created_at`
- Index on `StockTransaction.part_id`, `StockTransaction.timestamp`
- Index on `PMTask.next_due_date` (for dashboard filtering)
- Foreign key constraints with `ondelete='CASCADE'` where appropriate (asset deletes remove worksheets)

### 2.8 Add Relationships & Lazy Loading Strategy

- User ← (1:M) → Worksheet: `lazy='select'` (load technician worksheets on-demand)
- Machine ← (1:M) → Worksheet: `lazy='joined'` (always load active worksheets with machine)
- Worksheet ← (1:M) → WorksheetPart: `lazy='selectin'` (batch-load parts for a worksheet)
- Part ← (1:M) → StockTransaction: `lazy='select'` (on-demand history)

**Deliverables:**
- Complete `models.py` with all SQLAlchemy classes
- Database schema ready for creation via `Base.metadata.create_all()`
- Clear relationship definitions with cascade rules
- Well-documented model comments

---

## Phase 3: Authentication & Core Services Layer (Week 2, Days 1-2)

### 3.1 Authentication Service

Create `services/auth_service.py`:
- **`hash_password(password: str)`**: Use Argon2 (argon2-cffi) to hash passwords
- **`verify_password(password: str, hash: str)`**: Verify plaintext against hash
- **`create_session(user_id: int)`**: Generate random 32-byte token, hash it, store in DB with expiry (24h or configurable)
- **`validate_session(token: str)`**: Check token exists, hasn't expired, update last_activity; return user context if valid
- **`logout_session(token: str)`**: Mark session as inactive
- **`login(username: str, password: str)`**: Lookup user, verify password, create session, return token
- **`get_current_user(token: str)`**: Return User object with role and permissions
- **Error Handling**: Raise `AuthenticationError` for invalid credentials

### 3.2 User Management Service

Create `services/user_service.py`:
- **`create_user(username, email, password, role_id)`**: Validate username uniqueness, hash password
- **`get_user(user_id)`**: Fetch User with role
- **`list_users(role_filter=None)`**: List all users (Manager only)
- **`update_user_language(user_id, language_code)`**: Update user's language preference
- **`deactivate_user(user_id)`**: Set is_active=False
- **Validation**: Check username format, email format, password strength

### 3.3 Permission Check Utility

Create `services/permission_service.py`:
- **`has_permission(user: User, action: str, resource_id=None)`**: Check if user's role allows action
  - Manager: all permissions
  - Technician: can create/view worksheets, view inventory (no edit), view assets

### 3.4 Multilingual Support Service

Create `services/localization_service.py`:
- **`initialize_localization()`**: Load en.json and hu.json at startup
- **`get_text(key: str, lang_code: str = None, **params)`**: Lookup string with parameter interpolation
- **`format_date(date: datetime, lang_code: str)`**: Locale-aware date formatting using Babel
- **`format_currency(amount: float, lang_code: str)`**: Format with proper currency symbol
- **Observer Pattern**: Register callbacks for language change, trigger UI refresh

### 3.5 Base Service Layer Structure

Create `services/base_service.py`:
- **`BaseService` class**: Abstract base with common methods
  - `get_session()`: Returns new session
  - `log_audit(user_id, action, entity_type, entity_id, changes)`: Log to AuditLog
  - `handle_db_error(e)`: Convert SQLAlchemy exceptions to user-friendly messages

### 3.6 Validation Utilities

Create `utils/validators.py`:
- **`validate_username(username)`**: Pattern check
- **`validate_email(email)`**: Basic RFC pattern
- **`validate_password_strength(password)`**: Min length, uppercase, lowercase, numbers
- **`validate_sku(sku)`**: Pattern for part identifiers
- **`validate_file_upload(filename, max_size_mb, allowed_extensions)`**: Security validation

### 3.7 Database Initialization

Create `database/database.py`:
- **`init_database()`**: 
  - Create engine with `StaticPool`
  - Call `Base.metadata.create_all(engine)` to create all tables
  - Insert default roles if not exist
  - Create default admin user if no users exist

### 3.8 Session & Context Management

Create `services/context_service.py`:
- **`AppContext` class**: Holds current user, role, language, session token
- **`get_app_context()`**: Return current context
- **`set_app_context(user_id, token, language)`**: Initialize context on login
- **`clear_app_context()`**: Clear on logout

**Deliverables:**
- Working authentication system
- Session token generation and validation
- Role-based permission checks
- Core service layer framework
- Localization service
- Database initialization logic

---

## Phase 4: Main UI Framework & Navigation (Week 2, Days 3-5)

### 4.1 Flet App Structure

Create `ui/app.py`:
- **`MainApp` class**: Main app instance
- **Route management**: Dictionary mapping route names to screen constructors
- **Navigation stack**: Track current screen, support back button

### 4.2 Theme & Styling

Create `ui/theme.py`:
- **Color palette**: Define primary, secondary, success, warning, error colors
- **Material Design 3**: Use Flet's built-in Material theme
- **Typography**: Define font sizes for headers, body, labels
- **Spacing constants**: Padding, margins, gaps

### 4.3 Core Layout Components

Create `ui/components/layout.py`:
- **`MainLayout` component**: Container with header, sidebar, content area
  - Header: App title, user name, language selector, logout button
  - Sidebar: Navigation menu
  - Content: Dynamic screen rendering

### 4.4 Language Selector Component

Create `ui/components/language_selector.py`:
- **`LanguageSelector` class**: Dropdown showing EN / HU
- On selection change: Update database, emit callback for screen refresh
- Display flag emojis or language codes

### 4.5 Reusable UI Components

Create `ui/components/common.py`:
- **`CustomButton`**: Wrapper around flet.ElevatedButton with theme styling
- **`CustomTextField`**: Input with validation feedback
- **`CustomDataTable`**: Reusable table with sorting/pagination
- **`Dialog`**: Confirmation dialogs
- **`SnackBar`**: Toast notifications
- **`ProgressBar`**: For imports and bulk operations

### 4.6 Login Screen

Create `ui/screens/login_screen.py`:
- **`LoginScreen` class**: 
  - Username and password fields
  - Login button
  - Language selector (allow language choice before login)
  - Error messages display

### 4.7 Navigation Menu & Router

Create `ui/navigation.py`:
- **`AppRouter` class**: 
  - Route dictionary mapping to screen constructors
  - `navigate_to(route, params=None)`: Change current screen
  - `go_back()`: Return to previous screen
  - `on_logout()`: Clear AppContext, navigate to login

### 4.8 Dashboard Skeleton

Create `ui/screens/dashboard_screen.py`:
- **`DashboardScreen` class**:
  - Welcome message
  - Quick stats: Active worksheets, overdue PM tasks, low stock items
  - Placeholder sections for charts

### 4.9 Settings Screen Skeleton

Create `ui/screens/settings_screen.py`:
- **`SettingsScreen` class**:
  - User profile (name, email, role read-only)
  - Language selector
  - Change password form
  - Backup/restore options placeholder

### 4.10 App Entry Point

Update `main.py`:
```python
import flet as ft
from ui.app import MainApp
from database.database import init_database
from services.localization_service import localization_service

if __name__ == "__main__":
    init_database()
    localization_service.initialize_localization()
    app = MainApp()
    ft.app(target=app.main, view=ft.AppView.WEB_BROWSER)
```

### 4.11 Translation Files - Expand

Update `localization/translations/en.json` and `hu.json`:
- `auth.*`: login labels, error messages
- `common.*`: buttons, dialogs, confirmations
- `menu.*`: navigation items
- `dashboard.*`: welcome message, quick stats labels
- `settings.*`: profile, language, password change

**Deliverables:**
- Working Flet application with multi-screen navigation
- Login screen with authentication
- Main layout with sidebar and header
- Language selector fully integrated
- Dashboard and settings screens
- Reusable UI component library
- Complete translation keys

---

## Phase 5: Asset Management Module (Week 3, Days 1-2)

### 5.1 Asset Service Layer

Create `services/asset_service.py`:
- Production line CRUD operations
- Machine CRUD operations
- **`upload_machine_manual(machine_id, pdf_file)`**: Validate, store, link to machine
- Module CRUD operations
- **`get_machine_history(machine_id)`**: Fetch linked worksheets, PM tasks

### 5.2 Asset Management Screens

Create `ui/screens/asset_screen.py`:
- **`AssetScreen` class**: Hierarchical view
  1. Production Lines tab: List with expand/collapse
  2. Machines tab: List with detail view
  3. Machine Detail modal: Display specs, manual link, modules, history

### 5.3 Create/Edit Production Line Dialog

Create `ui/screens/production_line_dialog.py`:
- Fields: Name, Description, Location
- Validation: Name required, min 3 chars

### 5.4 Create/Edit Machine Dialog

Create `ui/screens/machine_dialog.py`:
- Fields: Name, Serial, Model, Manufacturer, Production Line
- File upload for PDF manual with validation

### 5.5 Machine History View

Create `ui/screens/machine_history_screen.py`:
- Tabs: Worksheets, PM Tasks, Activity Timeline

### 5.6 PDF Manual Management

Create `utils/file_handler.py`:
- **`upload_file(file_obj, directory, allowed_extensions, max_size_mb)`**
- **`download_file(file_path)`**
- **`delete_file(file_path)`**

### 5.7 Permission Checks in Assets

- Manager: Full CRUD
- Technician: Read-only, can create worksheets

**Deliverables:**
- Asset management service layer
- Hierarchical asset screens
- Machine detail with manual upload
- Machine history view
- File upload/download utilities
- Permission checks
- Audit logging

---

## Phase 6: Inventory Management Module (Week 3, Days 3-5)

### 6.1 Inventory Service Layer

Create `services/inventory_service.py`:
- Part CRUD operations with uniqueness validation
- **`adjust_stock(part_id, quantity_change, ...)`**: Update inventory, create transaction
- **`import_parts_from_excel(file_path, user_id)`**: Bulk import with validation and rollback
- Supplier CRUD operations

### 6.2 QR Code Service

Create `utils/qr_generator.py`:
- **`generate_qr_code(part_id, sku)`**: Create QR image
- **`generate_qr_labels(part_ids, output_format='pdf')`**: Create printable labels

### 6.3 Inventory Management Screen

Create `ui/screens/inventory_screen.py`:
- **Parts Tab**: DataTable with SKU, Name, On-Hand, Safety Stock, Status
- **Stock Movements Tab**: Transaction history with filters
- **Suppliers Tab**: Supplier management

### 6.4 Add/Edit Part Dialog

Create `ui/screens/part_dialog.py`:
- Fields: SKU, Name, Description, Category, Buy/Sell Price, Safety Stock, Supplier
- Calculate profit margin display

### 6.5 Stock Adjustment Dialog

Create `ui/screens/stock_adjustment_dialog.py`:
- Part search, quantity input, reason dropdown
- Auto-calculate new quantity

### 6.6 Excel Import Dialog

Create `ui/screens/import_dialog.py`:
- File picker, column mapping, preview, progress bar
- Summary after import with counts

### 6.7 QR Code Generation & Printing

Create `ui/screens/qr_labels_dialog.py`:
- Filter parts, select for label generation
- PDF preview and download

**Deliverables:**
- Inventory service with CRUD and bulk operations
- Parts management screen
- Excel/CSV bulk import with transaction safety
- Stock adjustment tracking
- QR code generation and printing
- Low stock alerts

---

## Phase 7: Worksheet Management (Core) (Week 4)

### 7.1 Worksheet Service Layer

Create `services/worksheet_service.py`:
- **`create_worksheet(machine_id, user_id, ...)`**: Create with status='Open'
- **`update_worksheet(worksheet_id, data)`**: Update with status transitions
- **`add_part_to_worksheet(worksheet_id, part_id, qty, ...)`**: Reserve parts
- **`remove_part_from_worksheet(worksheet_id, part_id)`**: Unreserve parts
- **`upload_worksheet_photo(worksheet_id, image_file)`**: Store photos
- Status transition logic: Open → Waiting → Closed (deduct parts, calculate downtime)

### 7.2 Worksheet PDF Export Service

Create `services/pdf_service.py`:
- **`export_worksheet_to_pdf(worksheet_id)`**:
  1. Fetch worksheet data
  2. Render Jinja2 template
  3. Generate PDF with WeasyPrint
  4. Save to `data/reports/generated/`

Jinja2 Template (`templates/worksheet_template.html`):
- Professional layout
- Machine info, timing, parts table, photos
- Bilingual support

### 7.3 Worksheet Management Screen

Create `ui/screens/worksheet_screen.py`:
- **Active Worksheets Tab**: DataTable filtered by status
- **Archive Tab**: Closed worksheets, paginated
- Filters and sorting

### 7.4 Create Worksheet Dialog

Create `ui/screens/worksheet_create_dialog.py`:
- Machine selection, title, description

### 7.5 Worksheet Detail / Edit Screen

Create `ui/screens/worksheet_detail_screen.py`:
- Title & Description (editable)
- Status dropdown with transitions
- Timing: Breakdown time, repair finished time, calculated downtime
- Parts: Add/remove with quantity tracking
- Photos: Add/view/delete thumbnails
- Notes: Text area
- Buttons: Save, Export PDF, Delete, Close

### 7.6 Add Part to Worksheet Dialog

Create `ui/screens/add_part_dialog.py`:
- Part search with autocomplete
- Show current on-hand quantity
- Input quantity used
- Auto-populate unit cost
- Calculate total live

### 7.7 Status Workflow Logic

- Open → Waiting for Parts: Manual change
- Waiting → Closed: Deduct parts, generate PDF, mark closed_at
- Closed → Read-only

### 7.8 Permission Checks

- Manager: Full access, can delete
- Technician: Own worksheets only

**Deliverables:**
- Worksheet service with full CRUD and status workflow
- Worksheet detail screen with timing, parts, photos
- Status transition logic with validation
- PDF export with bilingual template
- Permission checks
- Search, filter, archive functionality

---

## Phase 8: Preventive Maintenance Module (Week 4, Days 3-5)

### 8.1 PM Service Layer

Create `services/pm_service.py`:
- **`create_pm_task(machine_id, task_name, ...)`**: Create task with schedule
- **`get_pm_tasks_due_today()`**: Filter tasks
- **`get_pm_tasks_overdue()`**: Filter overdue
- **`get_pm_tasks_for_machine(machine_id)`**: Fetch all
- **`execute_pm_task(pm_task_id, user_id)`**: Create history record
- **`complete_pm_task(task_history_id, ...)`**: Mark complete, reschedule
- **`skip_pm_task(task_history_id, reason)`**: Skip with reschedule
- **`update_pm_task(task_id, data)`**: Update schedule
- **`delete_pm_task(task_id)`**: Soft-delete

### 8.2 PM Management Screen

Create `ui/screens/pm_screen.py`:
- **Due Today Tab**: Task list, color-coded
- **Schedule Tab**: Gantt view or calendar for next 3 months
- **All Tasks Tab**: DataTable with filters

### 8.3 Create/Edit PM Task Dialog

Create `ui/screens/pm_task_dialog.py`:
- Machine selection, task name, description, frequency days

### 8.4 Execute PM Task Screen

Create `ui/screens/pm_execution_screen.py`:
- Task details, assignee, in-progress status
- Option to create linked worksheet

### 8.5 Complete PM Task Dialog

Create `ui/screens/pm_complete_dialog.py`:
- Duration input, notes field

### 8.6 PM Dashboard Widget

- "Due Today" count
- "Overdue" count
- Upcoming tasks list

**Deliverables:**
- PM service with task CRUD and scheduling
- PM management screens
- Task execution and completion workflow
- Overdue detection
- Dashboard integration

---

## Phase 9: Dashboard & Reporting (Week 5, Days 1-2)

### 9.1 Dashboard Service Layer

Create `services/dashboard_service.py`:
- **`get_dashboard_metrics()`**: Worksheet counts, top machines, PM due, low stock, recent worksheets
- **`get_worksheet_trend(days=30)`**: Daily count for chart
- **`get_downtime_by_machine(days=90)`**: For bar chart
- **`get_stock_status()`**: Count by status
- **`get_technician_performance(days=30)`**: Worksheets, efficiency

### 9.2 Enhanced Dashboard Screen

Update `ui/screens/dashboard_screen.py`:
- **Metrics Cards**: Active worksheets, overdue PM, low stock, MTD downtime
- **Charts**:
  1. Worksheets by status (Pie)
  2. Top 5 machines by downtime (Bar)
  3. Worksheet trend (Line)
  4. Stock status (Pie)
- **Quick Action Panels**: Due PM tasks, recent worksheets, low stock alerts

### 9.3 Reports Screen

Create `ui/screens/reports_screen.py`:
- **Report Types**:
  1. Maintenance Summary
  2. Equipment Performance
  3. Technician Performance
  4. Inventory Status
  5. Financial Summary
- **Actions**: Filter, export PDF/CSV, print

### 9.4 Report Generator Service

Create `services/report_service.py`:
- **`generate_maintenance_report(date_range, filters)`**: Aggregate and create PDF
- **`export_report_csv(report_data)`**: Export to CSV
- Bilingual output support

### 9.5 Report Templates

Create Jinja2 templates in `templates/`:
- `report_maintenance.html`
- `report_equipment.html`
- `report_technician.html`
- `report_inventory.html`
- `report_financial.html`

Each with:
- Bilingual headers
- Tables and charts
- Professional formatting
- Generation timestamp footer

**Deliverables:**
- Dashboard with 4+ charts and metrics
- Multi-type report generation
- Report filtering and export
- Bilingual templates
- Chart rendering

---

## Phase 10: Localization Completion & Refinement (Week 5, Days 3-4)

### 10.1 Complete Translation Files

Expand `localization/translations/en.json` and `hu.json` with:
- All screen titles and labels from Phases 1-9
- Form placeholders and validation messages
- Error messages (database, file upload, import)
- Success messages
- Confirmation dialogs
- Help text and tooltips
- Report titles and labels
- Dashboard metrics labels
- Permission error messages

Structure:
```json
{
  "common": { "buttons": {...}, "messages": {...} },
  "screens": { "asset": {...}, "worksheet": {...}, ... },
  "errors": { "validation": {...}, "database": {...} }
}
```

### 10.2 Translation Validation Utility

Create `utils/translation_validator.py`:
- **`validate_translation_completeness()`**: Compare EN/HU keys
- **`validate_placeholders()`**: Check format consistency
- Run validation on app startup
- Report missing keys, halt on critical errors

### 10.3 Date/Time Formatting by Language

Implement in `services/localization_service.py`:
- **`format_date(datetime_obj, lang_code)`**:
  - EN: "12/12/2025"
  - HU: "2025.12.12"
- **`format_datetime(datetime_obj, lang_code)`**:
  - EN: "12/12/2025 3:45 PM"
  - HU: "2025.12.12 15:45"
- **`format_currency(amount, lang_code, currency)`**:
  - EN: "$1,234.56"
  - HU: "1 234,56 USD"
- **`format_time_duration(hours, minutes, lang_code)`**:
  - EN: "2 hrs 30 mins"
  - HU: "2 óra 30 perc"

### 10.4 Bilingual Testing Checklist

Create `TESTING.md`:
- [ ] All screens display in EN and HU
- [ ] Language switcher works on every screen
- [ ] Dates, times, currencies format correctly
- [ ] No hardcoded English text
- [ ] Error messages in correct language
- [ ] Help text translated
- [ ] Reports bilingual
- [ ] PDFs bilingual
- [ ] Language persisted after login

### 10.5 Localization Edge Cases

- Form validation messages
- Database error messages
- File upload errors
- Permission denied messages
- Confirmation dialogs

### 10.6 Language Persistence Enhancement

- Load user's language from database after login
- Auto-switch app language
- Store preference per user

**Deliverables:**
- Complete 100+ key translation files
- Translation validation utility
- Locale-aware formatting
- Bilingual testing checklist
- No hardcoded English text
- Language preference persistence

---

## Phase 11: Testing & Quality Assurance (Week 5, Day 5 + Week 6, Days 1-2)

### 11.1 Unit Tests

Create `tests/` with:
- **`test_models.py`**: Model creation, relationships
- **`test_services.py`**: Business logic (auth, CRUD, workflows)
- **`test_utils.py`**: Validators, file handlers, formatters

### 11.2 Integration Tests

- Database operations with in-memory SQLite
- Workflow testing (worksheet creation → completion)
- File operations
- Bulk import scenarios

### 11.3 Manual UI Testing

Create `MANUAL_TESTING.md`:
- Authentication flow
- Asset management (CRUD, manual upload)
- Inventory (add parts, import, adjust stock)
- Worksheet workflow (create, add parts, close, PDF)
- PM management
- Reports and dashboard
- Bilingual testing

### 11.4 Performance Testing

- Large datasets (1000+ parts, 500+ worksheets)
- Query optimization
- PDF generation performance

### 11.5 Security Testing

- SQL injection prevention
- File upload validation
- Authorization checks
- Session token expiry
- Password hashing strength
- Audit logging

### 11.6 Error Handling & Edge Cases

- Database connection failures
- File system issues
- Missing translations
- Invalid file uploads
- Import failures with rollback
- Duplicate entries

### 11.7 Bug Tracking & Fixes

- Log all bugs found
- Prioritize: critical, high, medium
- Fix and retest

**Deliverables:**
- Unit test suite (70-80% coverage)
- Integration tests
- Manual testing checklist
- Performance benchmarks
- Security audit checklist
- Bug log and fixes

---

## Phase 12: Polish, Packaging & Deployment (Week 6, Days 3-5)

### 12.1 UI/UX Refinement

- Consistency review (button placement, layouts, colors)
- Form label alignment
- Error message styling
- Hover states and feedback
- Responsive layout
- Accessibility (tab order, keyboard shortcuts)
- Screen transitions
- Loading indicators

### 12.2 Help & Documentation

Create docs:
- **`USER_MANUAL.md`**: Getting started, features guide, FAQ, troubleshooting
- **`INSTALLATION.md`**: System requirements, step-by-step setup, configuration
- **`TECHNICAL.md`**: Architecture, modules, extending features, schema

### 12.3 Data Backup & Recovery

Create `services/backup_service.py`:
- **`backup_database()`**: Compress DB to `data/system_backups/`
- **`backup_all_files()`**: Backup `data/files/`
- **`restore_from_backup(backup_file)`**: Restore with validation
- Add "Backup Now" button in Settings
- Schedule nightly backups

### 12.4 Application Logging

Create `config/logging_config.py`:
- Log to file: `logs/cmms.log`
- Levels: DEBUG, INFO, WARNING, ERROR
- Log rotation: Last 10 files, max 10 MB each
- Include timestamp, level, module, message

### 12.5 Executable Packaging

Use **PyInstaller**:
```bash
pyinstaller --onefile --windowed --icon=icon.ico --name=CMMS main.py
```
- Output: `dist/CMMS.exe` (~100-200 MB)

Or use **NSIS** for installer:
- `CMMS_Setup.exe`
- Uninstaller support
- Start menu shortcuts

### 12.6 Version Management

- Create `version.txt`: `1.0.0`
- Display in About screen
- Future: Update checks

### 12.7 Configuration & Setup Wizard (Optional)

First launch wizard:
- [ ] Set language
- [ ] Create admin user
- [ ] Configure database (optional)
- [ ] Create initial facilities
- [ ] Set company name

### 12.8 Performance Optimization

- Pre-compile Jinja2 templates
- Cache frequently-used queries
- Index optimization review
- Memory profiling on large datasets

### 12.9 Final Security Audit

- [ ] Passwords hashed with Argon2
- [ ] No secrets in source code
- [ ] File uploads validated
- [ ] Authorization checks complete
- [ ] Audit logging enabled
- [ ] Sessions timeout
- [ ] SQL injection prevention
- [ ] Tests passing

### 12.10 Release Checklist

- [ ] All tests passing
- [ ] No debug code
- [ ] Documentation complete
- [ ] Version bumped
- [ ] Changelog updated
- [ ] README updated
- [ ] Executable tested on clean Windows
- [ ] Installation tested
- [ ] Backup/restore tested
- [ ] Performance acceptable

**Deliverables:**
- Polished, professional UI
- Complete user and installation manuals
- Automated backup/restore
- Windows executable or installer
- Comprehensive logging
- Version management
- Optimized performance
- Security audit completed

---

## Implementation Timeline Summary

| Phase | Duration | Focus |
|-------|----------|-------|
| **1** | Week 1, Days 1-2 | Foundation, structure, localization |
| **2** | Week 1, Days 3-5 | Database models, schema |
| **3** | Week 2, Days 1-2 | Authentication, services, permissions |
| **4** | Week 2, Days 3-5 | Main UI, navigation, login, dashboard |
| **5** | Week 3, Days 1-2 | Asset management (CRUD, manuals, history) |
| **6** | Week 3, Days 3-5 | Inventory (parts, import, QR codes) |
| **7** | Week 4 | **Core**: Worksheet system, status workflow, PDF |
| **8** | Week 4, Days 3-5 | Preventive maintenance |
| **9** | Week 5, Days 1-2 | Dashboard, charts, reports |
| **10** | Week 5, Days 3-4 | Complete translations, localization |
| **11** | Week 5-6 | Testing, QA, security |
| **12** | Week 6, Days 3-5 | Polish, packaging, deployment |

**Total: ~6 weeks for MVP with all core features and bilingual support**

---

## Architecture Decision Summary

| Decision | Recommendation | Rationale |
|----------|-----------------|-----------|
| **Translation Files** | JSON in `localization/translations/` | Version-controllable, lightweight, hierarchical |
| **Language Switching** | Observer pattern with dynamic UI refresh | Better UX than restart |
| **Authentication** | Argon2 + local session tokens | Modern, secure, offline-suitable |
| **Database Sessions** | Session factory with explicit management | Thread-safe, avoids global state |
| **PDF Generation** | WeasyPrint for complex layouts | HTML/CSS input, excellent styling |
| **Bulk Import** | Pandas with transaction rollback | Efficient, error-safe |
| **File Storage** | UUID filenames, organized by type | Security, prevent collisions |
| **Permissions** | Role-based in service layer | Scalable, security-first |
| **Testing** | Unit tests on services, manual UI tests | Flet lacks robust UI test framework |
| **Packaging** | PyInstaller for `.exe` | Single file, no installation hassle |

---

## Key Technical Decisions

### Localization Strategy
- **JSON files with dot-notation keys** for translations
- **Babel library** for locale-aware date/time/currency formatting
- **Observer pattern** for dynamic language switching without app restart
- **Per-user language preferences** stored in database

### Authentication & Security
- **Argon2-cffi** for password hashing (modern, GPU-resistant)
- **32-byte random tokens** for session management
- **24-hour session expiry** with activity tracking
- **Role-based access control** (Manager/Technician) enforced in service layer

### Database Design
- **SQLAlchemy ORM** for type-safe database operations
- **SQLite with StaticPool** for single-user/small team usage
- **Lazy loading strategies** optimized per relationship
- **Alembic migrations** for schema versioning

### File Management
- **UUID-based filenames** for security and uniqueness
- **Organized directory structure** by content type
- **MIME type validation** with python-magic library
- **Size and extension whitelisting** for uploads

### PDF & Reporting
- **WeasyPrint** for template-based PDF generation (Jinja2 HTML templates)
- **Bilingual templates** supporting EN and HU content
- **Embedded images** as base64 for portability
- **Professional styling** with CSS for layouts

### User Interface
- **Flet framework** for modern Material Design 3 UI
- **Component-based architecture** for reusability
- **State management** via AppContext for user/role/language
- **Route-based navigation** with screen stacking

---

## Project Completion Criteria

✅ **Fully Functional CMMS System** with:
- ✅ User authentication and role-based access
- ✅ Asset management (Production Line → Machine → Module)
- ✅ Inventory management with bulk import and QR codes
- ✅ Worksheet system with status workflow
- ✅ Preventive maintenance scheduling
- ✅ Dashboard with charts and metrics
- ✅ Multi-page reports (PDF/CSV export)
- ✅ Bilingual UI (English/Hungarian)
- ✅ Comprehensive testing and documentation
- ✅ Windows desktop executable deployment

---

**Document Version: 1.0**
**Last Updated: December 12, 2025**
**Status: Implementation Plan - Ready for Development**
