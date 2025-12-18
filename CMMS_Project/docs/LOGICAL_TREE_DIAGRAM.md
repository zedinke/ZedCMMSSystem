# CMMS Rendszer - Logikai Fa Diagram

**Dátum**: 2025.12.18  
**Cél**: Vizuális reprezentáció a rendszer logikai struktúrájáról és munkafolyamatairól

---

## 📊 TARTALOMJEGYZÉK

1. [Teljes Rendszer Logikai Fa](#1-teljes-rendszer-logikai-fa)
2. [Service Függőségek Fa](#2-service-függőségek-fa)
3. [Adatfolyam Diagram](#3-adatfolyam-diagram)
4. [Munkafolyamat Fa](#4-munkafolyamat-fa)

---

## 1. TELJES RENDSZER LOGIKAI FA

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CMMS RENDSZER ARCHITEKTÚRA                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
            ┌───────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
            │  UI LAYER    │ │ SERVICE     │ │ DATABASE    │
            │  (Flet)      │ │ LAYER       │ │ LAYER       │
            │              │ │ (42 modul)  │ │ (SQLAlchemy)│
            └───────┬──────┘ └──────┬──────┘ └──────┬──────┘
                    │               │               │
                    └───────────────┼───────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
            ┌───────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
            │ INFRASTRUCTURE│ │ WORKFLOW    │ │ LOGGING     │
            │ (Config,      │ │ SERVICE     │ │ SYSTEM      │
            │  Localization)│ │ (Central)   │ │ (Rotating)  │
            └───────────────┘ └─────────────┘ └─────────────┘
```

---

## 2. SERVICE FÜGGŐSÉGEK FA

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SERVICE DEPENDENCY TREE                              │
└─────────────────────────────────────────────────────────────────────────────┘

workflow_service (CENTRAL WORKFLOW ENGINE)
│
├─► pm_service
│   │
│   ├─► notification_service
│   │   └─► user_service (get users by roles)
│   │
│   ├─► worksheet_service
│   │   ├─► inventory_service
│   │   │   └─► storage_service
│   │   │       └─► log_service
│   │   │
│   │   ├─► transaction_service (decorator)
│   │   ├─► notification_service
│   │   ├─► pdf_service
│   │   └─► scrapping_service
│   │
│   ├─► pdf_service
│   │   └─► settings_service (get template paths)
│   │
│   ├─► scrapping_service
│   │   ├─► pdf_service
│   │   └─► settings_service
│   │
│   └─► log_service
│
├─► worksheet_service
│   │
│   ├─► inventory_service
│   │   ├─► storage_service
│   │   └─► transaction_service
│   │
│   ├─► transaction_service (decorator)
│   │   └─► log_service
│   │
│   ├─► notification_service
│   │   └─► user_service
│   │
│   ├─► pdf_service
│   │   └─► settings_service
│   │
│   ├─► scrapping_service
│   │   ├─► pdf_service
│   │   └─► settings_service
│   │
│   └─► log_service
│
├─► inventory_service
│   │
│   ├─► storage_service
│   │   ├─► log_service
│   │   └─► context_service (get current user)
│   │
│   ├─► transaction_service
│   │   └─► log_service
│   │
│   └─► log_service
│
├─► storage_service
│   │
│   ├─► log_service
│   └─► context_service
│
└─► asset_service
    │
    ├─► log_service
    └─► inventory_service (for compatible parts)
```

---

## 3. ADATFOLYAM DIAGRAM

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PM TASK COMPLETION FLOW                             │
└─────────────────────────────────────────────────────────────────────────────┘

USER ACTION: "Complete PM Task"
    │
    ▼
┌─────────────────────────┐
│  pm_screen.py           │
│  (UI Layer)             │
│  - open_complete_dialog │
│  - submit_completion    │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  pm_service.py          │
│  complete_pm_task()     │
└────────────┬────────────┘
             │
    ┌────────┼────────┐
    │        │        │
    ▼        ▼        ▼
┌────────┐ ┌──────────────┐ ┌─────────────────┐
│ Workflow│ │ Create       │ │ Generate        │
│ Valid.  │ │ PMHistory    │ │ Documents       │
│         │ │              │ │                 │
│ workflow│ │ - Set        │ │ - Work Request  │
│ _service│ │   worksheet_ │ │   PDF           │
│         │ │   id         │ │                 │
│         │ │              │ │ - PM Worksheet  │
│         │ │ - Set        │ │   PDF           │
│         │ │   completion │ │                 │
│         │ │   _status    │ │ - Scrapping     │
│         │ │              │ │   Docs[]        │
└─────────┘ └──────┬───────┘ └────────┬────────┘
                   │                  │
                   │                  │
                   ▼                  ▼
        ┌──────────────────┐ ┌──────────────┐
        │ worksheet_service│ │ pdf_service  │
        │ create_worksheet │ │              │
        │                  │ │ - Templates  │
        │ - Create         │ │ - Fill data  │
        │   Worksheet      │ │ - Generate   │
        │                  │ │ - Save       │
        │ - Notification   │ └──────────────┘
        └────────┬─────────┘
                 │
                 ▼
        ┌──────────────────┐
        │ notification_    │
        │ service          │
        │                  │
        │ - Send to user   │
        │ - Send to        │
        │   managers       │
        └────────┬─────────┘
                 │
                 ▼
        ┌──────────────────┐
        │ log_service      │
        │ log_action()     │
        │                  │
        │ - SystemLog      │
        │   creation       │
        └──────────────────┘
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    WORKSHEET PART ADDITION FLOW                             │
└─────────────────────────────────────────────────────────────────────────────┘

USER ACTION: "Add Part to Worksheet"
    │
    ▼
┌─────────────────────────┐
│  worksheet_screen.py    │
│  (UI Layer)             │
│  - open_add_part_dialog │
│  - submit_add_part      │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  worksheet_service.py   │
│  add_part_to_worksheet()│
└────────────┬────────────┘
             │
    ┌────────┼────────┐
    │        │        │
    ▼        ▼        ▼
┌────────┐ ┌──────────────┐ ┌─────────────────┐
│ Validate│ │ Inventory    │ │ Storage         │
│ Part    │ │ Check        │ │ Update          │
│         │ │              │ │                 │
│ - Part  │ │ - Check      │ │ - Update        │
│   exists│ │   quantity_  │ │   PartLocation  │
│         │ │   on_hand    │ │                 │
│ - Stock │ │              │ │ - Deduct        │
│   avail.│ │ - Reserve    │ │   quantity      │
└─────────┘ └──────┬───────┘ └────────┬────────┘
                   │                  │
                   │                  │
                   ▼                  ▼
        ┌──────────────────┐ ┌──────────────┐
        │ transaction_     │ │ scrapping_   │
        │ service          │ │ service      │
        │                  │ │              │
        │ @transaction     │ │ - Generate   │
        │ decorator        │ │   Scrapping  │
        │                  │ │   Doc for    │
        │ - Create         │ │   each unit  │
        │   StockTrans.    │ │              │
        │                  │ │ - Create     │
        │ - Update         │ │   PDF        │
        │   InventoryLevel │ └──────────────┘
        └────────┬─────────┘
                 │
                 ▼
        ┌──────────────────┐
        │ log_service      │
        │ log_action()     │
        │                  │
        │ - SystemLog      │
        │   creation       │
        └──────────────────┘
```

---

## 4. MUNKAFOLYAMAT FA

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PM TASK LIFECYCLE TREE                               │
└─────────────────────────────────────────────────────────────────────────────┘

[PMTask State: pending]
    │
    │ [WORKFLOW: transition_state()]
    │
    ├───► [State: due_today] (automatikus, ha due_date == today)
    │     │
    │     └───► [State: overdue] (automatikus, ha due_date < today)
    │           │
    │           └───► [State: completed] (user action)
    │
    ├───► [State: in_progress] (user action)
    │     │
    │     └───► [State: completed] (user action)
    │
    └───► [State: completed] (user action - direct completion allowed)
          │
          ▼
    [PMHistory Created]
          │
          ├───► [Worksheet Created] (if create_worksheet=True)
          │     │
          │     └───► [Parts Added to Worksheet] (if parts used)
          │           │
          │           └───► [Scrapping Documents Generated] (auto)
          │
          ├───► [Work Request PDF Generated]
          │
          ├───► [PM Worksheet PDF Generated]
          │
          ├───► [Scrapping Documents Generated] (if parts used)
          │
          ├───► [Files Uploaded] (PMTaskAttachment)
          │
          └───► [Notifications Sent]
                │
                ├───► To completing user
                └───► To managers/shift leaders
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       WORKSHEET LIFECYCLE TREE                              │
└─────────────────────────────────────────────────────────────────────────────┘

[Worksheet State: Open]
    │
    │ [WORKFLOW: transition_state()]
    │
    ├───► [Parts Added] (optional)
    │     │
    │     ├───► [InventoryLevel Updated] (quantity_on_hand -= quantity)
    │     │
    │     ├───► [PartLocation Updated] (quantity -= quantity)
    │     │
    │     ├───► [StockTransaction Created] (transaction_type="issued")
    │     │
    │     └───► [Scrapping Document Generated] (auto, if enabled)
    │
    ├───► [State: Waiting for Parts]
    │     │
    │     └───► [State: Closed] (user action)
    │
    └───► [State: Closed] (user action)
          │
          ├───► [Downtime Calculated] (breakdown_time → repair_finished_time)
          │
          ├───► [Worksheet PDF Generated]
          │
          └───► [Notifications Sent]
                │
                ├───► To assigned user
                └───► To managers/shift leaders
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    INVENTORY PART LIFECYCLE TREE                            │
└─────────────────────────────────────────────────────────────────────────────┘

[Part Created]
    │
    ├───► [InventoryLevel Created] (quantity_on_hand = initial_quantity or 0)
    │
    ├───► [StockTransaction Created] (if initial_quantity > 0)
    │     │
    │     └───► transaction_type = "initial_stock" or "received"
    │
    └───► [Storage Assignment] (optional, immediate or later)
          │
          ├───► [If immediate]:
          │     │
          │     ├───► [PartLocation Created] (storage_location_id, quantity)
          │     │
          │     └───► [InventoryLevel.quantity_on_hand = initial_quantity]
          │
          └───► [If later]:
                │
                ├───► [Part appears in "Parts without storage location" list]
                │
                └───► [User assigns to location]
                      │
                      ├───► [PartLocation Created/Updated]
                      │
                      └───► [InventoryLevel.quantity_on_hand updated]
                            │
                            ▼
                    [VALIDATION CHECK]
                            │
                            ├───► [InventoryLevel.quantity_on_hand == SUM(PartLocation.quantity)]
                            │     │
                            │     └───► ✅ PASS
                            │
                            └───► [DISCREPANCY DETECTED]
                                  │
                                  └───► ⚠️ WARNING (should log and notify)
```

---

## 5. ENTITÁS KAPCSOLATOK RÉSZLETES FA

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PRODUCTION LINE → MACHINE → PARTS                        │
└─────────────────────────────────────────────────────────────────────────────┘

ProductionLine
    │
    ├─── 1:N ─── Machine
    │      │
    │      ├─── Basic Info
    │      │    ├─── name, serial_number, model, manufacturer
    │      │    ├─── asset_tag, status
    │      │    └─── criticality_level
    │      │
    │      ├─── Dates & Lifecycle
    │      │    ├─── install_date
    │      │    ├─── purchase_date, purchase_price
    │      │    ├─── warranty_expiry_date
    │      │    ├─── last_service_date
    │      │    └─── next_service_date
    │      │
    │      ├─── Operational Info
    │      │    ├─── operating_hours
    │      │    ├─── maintenance_interval
    │      │    ├─── energy_consumption
    │      │    ├─── power_requirements
    │      │    └─── operating_temperature_range
    │      │
    │      ├─── Physical & Financial
    │      │    ├─── weight, dimensions
    │      │    ├─── purchase_price
    │      │    └─── supplier
    │      │
    │      ├─── M:N ─── Part (via CompatibleMachine)
    │      │    │
    │      │    ├─── Part Info
    │      │    │    ├─── name, sku, description
    │      │    │    ├─── category, unit
    │      │    │    └─── supplier_id
    │      │    │
    │      │    ├─── Inventory Info
    │      │    │    ├─── InventoryLevel.quantity_on_hand
    │      │    │    ├─── InventoryLevel.quantity_reserved
    │      │    │    ├─── InventoryLevel.quantity_available
    │      │    │    └─── safety_stock, reorder_quantity
    │      │    │
    │      │    ├─── Financial Info
    │      │    │    ├─── buy_price
    │      │    │    └─── sell_price
    │      │    │
    │      │    └─── Storage Locations
    │      │         │
    │      │         └─── 1:N ─── PartLocation
    │      │                  │
    │      │                  ├─── StorageLocation (hierarchikus)
    │      │                  │    ├─── name, code
    │      │                  │    ├─── parent_location_id (tree structure)
    │      │                  │    └─── location_type, capacity
    │      │                  │
    │      │                  └─── quantity (mennyiség adott tárhelyen)
    │      │
    │      ├─── 1:N ─── PMTask
    │      │    │
    │      │    ├─── Task Info
    │      │    │    ├─── task_name, task_description
    │      │    │    ├─── task_type (recurring/one_time)
    │      │    │    ├─── frequency_days
    │      │    │    ├─── priority, status
    │      │    │    ├─── due_date, next_due_date
    │      │    │    └─── estimated_duration_minutes
    │      │    │
    │      │    ├─── Assignment
    │      │    │    ├─── assigned_to_user_id (None = global)
    │      │    │    └─── created_by_user_id
    │      │    │
    │      │    └─── 1:N ─── PMHistory
    │      │         │
    │      │         ├─── Execution Info
    │      │         │    ├─── executed_date
    │      │         │    ├─── completion_status
    │      │         │    ├─── duration_minutes
    │      │         │    ├─── work_description
    │      │         │    ├─── observations, notes
    │      │         │    ├─── assigned_to_user_id
    │      │         │    └─── completed_by_user_id
    │      │         │
    │      │         ├─── Documents (1:1)
    │      │         │    ├─── WorkRequestPDF
    │      │         │    ├─── PMWorksheetPDF
    │      │         │    └─── ScrappingDocument[] (1:N)
    │      │         │
    │      │         ├─── Files (1:N)
    │      │         │    └─── PMTaskAttachment
    │      │         │         ├─── file_path
    │      │         │         ├─── original_filename
    │      │         │         ├─── file_type (image/document/other)
    │      │         │         └─── uploaded_by_user_id
    │      │         │
    │      │         └─── Linked Worksheet (1:1, optional)
    │      │              └─── worksheet_id
    │      │
    │      └─── 1:N ─── Worksheet
    │           │
    │           ├─── Worksheet Info
    │           │    ├─── title, description
    │           │    ├─── status (Open/Waiting/Closed)
    │           │    ├─── breakdown_time
    │           │    ├─── repair_finished_time
    │           │    └─── total_downtime_hours
    │           │
    │           ├─── Assignment
    │           │    └─── assigned_to_user_id
    │           │
    │           ├─── Parts Used (1:N)
    │           │    └─── WorksheetPart
    │           │         ├─── part_id
    │           │         ├─── quantity_used
    │           │         ├─── unit_cost_at_time
    │           │         ├─── storage_location_id
    │           │         └─── notes
    │           │
    │           ├─── Documents (1:1)
    │           │    └─── WorksheetPDF
    │           │
    │           └─── Linked PM History (1:1, optional)
    │                └─── PMHistory.worksheet_id
    │
    └─── Assignment
         └─── responsible_person (User ID)
```

---

## 6. LOGIKUS MŰVELET FOLYAMATOK

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                  LOGICAL OPERATION: CREATE NEW PART                         │
└─────────────────────────────────────────────────────────────────────────────┘

1. USER ACTION
   │
   ├─── Navigate: Inventory → "Add New Part"
   │
   └─── Fill form:
        ├─── Basic info (name, SKU, description, category, unit)
        ├─── Financial info (buy_price, sell_price)
        ├─── Inventory info (safety_stock, reorder_quantity)
        ├─── Supplier selection
        └─── Initial quantity (optional)
             │
             └─── If > 0:
                  └─── Storage location selection (optional)
                       │
                       └─── StorageLocationPicker (filters: empty or same SKU)
                            │
                            └─── Shows quantity on hand per location

2. BACKEND PROCESSING
   │
   ├─── inventory_service.create_part()
   │    │
   │    ├─── Validate SKU (validators.validate_sku)
   │    │
   │    ├─── Check SKU uniqueness
   │    │
   │    ├─── Create Part record
   │    │
   │    ├─── Create InventoryLevel (quantity_on_hand = initial_quantity or 0)
   │    │
   │    └─── If initial_quantity > 0:
   │         │
   │         └─── inventory_service.adjust_stock()
   │              │
   │              ├─── Create StockTransaction (transaction_type="initial_stock")
   │              │
   │              └─── Update InventoryLevel.quantity_on_hand

3. STORAGE ASSIGNMENT (if location selected)
   │
   └─── storage_service.assign_part_to_location()
        │
        ├─── Create/Update PartLocation
        │    │
        │    └─── quantity = initial_quantity
        │
        └─── Update InventoryLevel.quantity_on_hand (should match SUM)

4. VALIDATION (should happen)
   │
   └─── inventory_service.validate_inventory_levels()
        │
        ├─── Check: InventoryLevel.quantity_on_hand == SUM(PartLocation.quantity)
        │
        └─── If discrepancy:
             │
             └─── ⚠️ WARNING (should log and notify)

5. LOGGING (should happen)
   │
   └─── log_service.log_action()
        │
        ├─── category="inventory"
        ├─── action_type="create"
        ├─── entity_type="Part"
        ├─── entity_id=part.id
        └─── metadata={...}
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│            LOGICAL OPERATION: COMPLETE PM TASK WITH PARTS                   │
└─────────────────────────────────────────────────────────────────────────────┘

1. USER ACTION
   │
   ├─── Navigate: PM Screen → Select task → "Complete"
   │
   └─── Fill completion form:
        ├─── Completion date & time
        ├─── Work description
        ├─── Observations
        ├─── Completion status (completed/partial/issues)
        ├─── Notes
        ├─── Parts used (optional)
        │    │
        │    └─── For each part:
        │         ├─── Select part (from compatible parts)
        │         ├─── Enter quantity
        │         └─── Select storage location (StorageLocationPicker with part_id filter)
        │
        └─── Files upload (optional)
             └─── Images, documents

2. BACKEND PROCESSING
   │
   ├─── pm_service.complete_pm_task()
   │    │
   │    ├─── Workflow validation (workflow_service.transition_state)
   │    │    │
   │    │    └─── Check: pending/due_today/overdue → completed (allowed)
   │    │
   │    ├─── Create PMHistory record
   │    │    │
   │    │    ├─── Set execution details
   │    │    ├─── Set completion_status
   │    │    └─── Set assigned_to_user_id, completed_by_user_id
   │    │
   │    ├─── Create Worksheet (if create_worksheet=True)
   │    │    │
   │    │    ├─── worksheet_service.create_worksheet()
   │    │    │
   │    │    ├─── Link: PMHistory.worksheet_id = worksheet.id
   │    │    │
   │    │    └─── Notification: notify_worksheet_assigned()
   │    │
   │    ├─── Generate Work Request PDF
   │    │    │
   │    │    └─── pdf_service.generate_work_request_pdf()
   │    │
   │    ├─── Generate PM Worksheet PDF
   │    │    │
   │    │    └─── pdf_service.generate_pm_worksheet_pdf()
   │    │
   │    ├─── Update PMTask status to "completed"
   │    │
   │    └─── Notification: notify_pm_task_completed()
   │         │
   │         └─── Send to: completing user + managers/shift leaders

3. PARTS PROCESSING (if parts used)
   │
   └─── For each part in completion form:
        │
        └─── worksheet_service.add_part_to_worksheet()
             │
             ├─── Validate part exists and is compatible with machine
             │
             ├─── Check inventory level (quantity_on_hand >= quantity)
             │
             ├─── Check storage location (has enough quantity)
             │
             ├─── Create WorksheetPart record
             │
             ├─── Update PartLocation.quantity (deduct)
             │
             ├─── Update InventoryLevel.quantity_on_hand (deduct)
             │
             ├─── Create StockTransaction (transaction_type="issued")
             │
             ├─── Generate Scrapping Document (if auto-generate enabled)
             │    │
             │    └─── scrapping_service.generate_scrapping_document()
             │         │
             │         └─── One document per unit used
             │
             └─── Logging: log_action() (should happen)

4. FILE PROCESSING (if files uploaded)
   │
   └─── pm_service.save_pm_task_attachments()
        │
        ├─── Create directory: {parent_dir}/pm_task_{id}/history_{history_id}/
        │
        ├─── Copy files to directory
        │
        ├─── Create PMTaskAttachment records
        │
        └─── Set file_type (image/document/other)

5. DOCUMENT COPYING
   │
   └─── pm_service.copy_pm_task_documents_to_directory()
        │
        ├─── Copy Work Request PDF
        ├─── Copy PM Worksheet PDF
        └─── Copy Scrapping Documents[]

6. LOGGING (should happen)
   │
   └─── log_service.log_action()
        │
        ├─── category="task"
        ├─── action_type="complete"
        ├─── entity_type="PMTask"
        ├─── entity_id=task.id
        └─── metadata={...}
```

---

## 7. HIERARCHIKUS STORAGE STRUCTURE

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STORAGE LOCATION TREE STRUCTURE                          │
└─────────────────────────────────────────────────────────────────────────────┘

StorageLocation (Root)
    │
    ├─── StorageLocation (Building A)
    │    │
    │    ├─── StorageLocation (Floor 1)
    │    │    │
    │    │    ├─── StorageLocation (Room 101)
    │    │    │    │
    │    │    │    ├─── StorageLocation (Shelf A1)
    │    │    │    │    │
    │    │    │    │    └─── PartLocation[] (parts assigned here)
    │    │    │    │
    │    │    │    └─── StorageLocation (Shelf A2)
    │    │    │         │
    │    │    │         └─── PartLocation[] (parts assigned here)
    │    │    │
    │    │    └─── StorageLocation (Room 102)
    │    │         │
    │    │         └─── StorageLocation (Shelf B1)
    │    │              │
    │    │              └─── PartLocation[] (parts assigned here)
    │    │
    │    └─── StorageLocation (Floor 2)
    │         │
    │         └─── StorageLocation (Room 201)
    │              │
    │              └─── StorageLocation (Shelf C1)
    │                   │
    │                   └─── PartLocation[] (parts assigned here)
    │
    └─── StorageLocation (Building B)
         │
         └─── StorageLocation (Warehouse)
              │
              └─── StorageLocation (Zone A)
                   │
                   └─── StorageLocation (Rack 1)
                        │
                        └─── PartLocation[] (parts assigned here)

PartLocation (Leaf nodes)
    │
    ├─── part_id (FK → Part)
    ├─── storage_location_id (FK → StorageLocation, must be leaf)
    ├─── quantity (quantity stored at this location)
    └─── notes (optional)

VALIDATION RULE:
    SUM(PartLocation.quantity WHERE part_id = X) == InventoryLevel.quantity_on_hand WHERE part_id = X
```

---

## 8. NAPLÓZÁS STRUKTÚRA

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        LOGGING ARCHITECTURE                                 │
└─────────────────────────────────────────────────────────────────────────────┘

LOGGING LAYERS:

1. Python Logging (logger.info/warning/error/debug)
   │
   ├─── Console Output (StreamHandler)
   └─── File Output (RotatingFileHandler)
        │
        ├─── File: data/logs/cmms.log
        ├─── Max size: 10 MB
        ├─── Backup count: 10 files
        └─── Rotation: automatic

2. SystemLog (Database - SystemLog table)
   │
   ├─── log_service.log_action()
   │    │
   │    ├─── Category: task, worksheet, work_request, scrapping, assignment, inventory, asset, user, document
   │    │
   │    ├─── Action Type: create, update, delete, generate, assign, complete, scrap
   │    │
   │    ├─── Entity Type: PMTask, Worksheet, Part, Machine, etc.
   │    │
   │    ├─── Entity ID: ID of the entity
   │    │
   │    ├─── User ID: User who performed the action
   │    │
   │    ├─── Description: Detailed description
   │    │
   │    ├─── Metadata: JSON with additional info
   │    │
   │    ├─── Timestamp: UTC timestamp
   │    │
   │    ├─── Date Categories: year, month, week, day (for filtering)
   │    │
   │    ├─── IP Address: Client IP
   │    │
   │    └─── User Agent: Client user agent string

3. AuditLog (Database - AuditLog table)
   │
   └─── audit_service.log_audit()
        │
        ├─── Similar to SystemLog but for audit trail
        └─── Less frequently used (mainly for compliance)

CURRENT STATUS:
    ✅ Python logging: GOOD (used throughout)
    ⚠️ SystemLog: PARTIAL (not used consistently)
    ❌ AuditLog: RARELY USED
```

---

**Készítve:** AI Assistant  
**Dátum:** 2025.12.18  
**Verzió:** 1.0

