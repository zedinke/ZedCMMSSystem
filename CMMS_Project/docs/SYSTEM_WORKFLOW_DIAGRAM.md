# CMMS Rendszer Munkafolyamat Ábrák

## 1. Teljes Rendszer Áttekintés

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CMMS RENDSZER STRUKTÚRA                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────┐
│   DASHBOARD         │  ← Összesítések, statisztikák
└──────────┬──────────┘
           │
    ┌──────┴──────────────────────────────────────────────────┐
    │                                                          │
┌───▼──────────────────────────────────────────────────────┐  │
│           ESZKÖZKEZELÉS / ASSET MANAGEMENT               │  │
│                                                           │  │
│  ProductionLine → Machine → Part (M:N kompatibilitás)    │  │
│       │              │                                      │  │
│       │              ├──→ PMTask → PMHistory               │  │
│       │              │       │        │                     │  │
│       │              │       │        ├──→ WorkRequestPDF   │  │
│       │              │       │        ├──→ PMWorksheetPDF   │  │
│       │              │       │        ├──→ ScrappingDoc[]   │  │
│       │              │       │        └──→ PMTaskAttachment │  │
│       │              │       │                              │  │
│       │              └──→ Worksheet                         │  │
│       │                     │                               │  │
│       │                     ├──→ WorksheetPart → Part       │  │
│       │                     │       │                        │  │
│       │                     │       └──→ StockTransaction    │  │
│       │                     │                                │  │
│       │                     └──→ WorksheetPDF               │  │
└───────────────────────────────────────────────────────────┘  │
                                                                 │
┌──────────────────────────────────────────────────────────────┐│
│         KÉSZLETKEZELÉS / INVENTORY MANAGEMENT                ││
│                                                               ││
│  Part → InventoryLevel (összesített)                        ││
│    │                                                          ││
│    ├──→ PartLocation[] → StorageLocation (részletes)        ││
│    │                                                          ││
│    ├──→ StockTransaction[] (minden mozgás)                   ││
│    │                                                          ││
│    ├──→ StockReservation[] (foglalások)                     ││
│    │                                                          ││
│    └──→ Supplier                                             ││
└──────────────────────────────────────────────────────────────┘│
                                                                 │
┌──────────────────────────────────────────────────────────────┐│
│              MŰVELETEK / OPERATIONS                          ││
│                                                               ││
│  PM Task (előírt)          Worksheet (reaktív)              ││
│       │                          │                           ││
│       └──→ PMHistory            └──→ Closed                 ││
│            │                                                  ││
│            └───────→ Service Records (összesítő) ←──────────┘│
└──────────────────────────────────────────────────────────────┘
```

---

## 2. PM (Preventive Maintenance) Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                    PM TASK LÉTREHOZÁS                           │
└─────────────────────────────────────────────────────────────────┘
                            │
            ┌───────────────┴───────────────┐
            │                               │
   [Manuális]                        [Automatikus]
   PM menü                            Production Line
   → Új feladat                       → Gép
                                       → "Karbantartás igénylése"
            │                               │
            └───────────────┬───────────────┘
                            │
        ┌───────────────────┴───────────────────┐
        │                                       │
   Hozzárendelés:                    Beállítások:
   • Globális (mindenki)              • Prioritás
   • Felhasználóhoz                   • Határidő
        │                                       │
        └───────────────┬───────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │   PM TASK (pending/due/overdue)│
        └───────────────┬───────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │   FELHASZNÁLÓ: "Elvégzés"     │
        └───────────────┬───────────────┘
                        │
                        ▼
        ┌───────────────────────────────────────────┐
        │   COMPLETION DIALOG                       │
        │   • Dátum, idő                            │
        │   • Munka leírása                         │
        │   • Megfigyelések                         │
        │   • Státusz (kész/részleges/problémás)   │
        │   • Alkatrészek használata (opcionális)  │
        │     └─ Part kiválasztás                   │
        │     └─ Mennyiség                          │
        │     └─ Storage location                   │
        │   • Fájlok feltöltése                     │
        └───────────────┬───────────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────────────────┐
        │   AUTOMATIKUS FOLYAMATOK                  │
        │                                           │
        │   1. PMHistory létrehozása                │
        │   2. Worksheet létrehozása (HA alkatrész) │
        │   3. WorkRequestPDF generálás             │
        │   4. PMWorksheetPDF generálás             │
        │   5. ScrappingDoc[] generálás (HA alkatrész)│
        │   6. Fájlok mentése                       │
        │   7. PMTaskAttachment[] létrehozása       │
        └───────────────┬───────────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────────────────┐
        │   ELVÉGZETT PM TASK                       │
        │                                           │
        │   UI gombok:                              │
        │   • Details (összes információ)          │
        │   • Work Request (PDF)                    │
        │   • Worksheet (PDF)                       │
        │   • Scrapping Document (PDF[])            │
        │   • Files (feltöltött fájlok)            │
        └───────────────────────────────────────────┘
```

---

## 3. Worksheet Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                    WORKSHEET LÉTREHOZÁS                         │
└─────────────────────────────────────────────────────────────────┘
                            │
            ┌───────────────┴───────────────┐
            │                               │
   [Manuális]                        [Automatikus]
   Worksheets menü                   PM Task elvégzés
   → Új munkalap                     (alkatrész használat esetén)
            │                               │
            └───────────────┬───────────────┘
                            │
        ┌───────────────────┴───────────────────┐
        │                                       │
   Gép kiválasztás                  Hozzárendelés:
   • Production Line                • Felhasználó
   • Machine                        • Leállás ideje (opc.)
        │                                       │
        └───────────────┬───────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │   WORKSHEET (Open)            │
        └───────────────┬───────────────┘
                        │
                        ▼
        ┌───────────────────────────────────────────┐
        │   ALKATRÉSZ HASZNÁLAT (opcionális)        │
        │   • Part kiválasztás                      │
        │   • Mennyiség                             │
        │   • Storage location                      │
        │                                           │
        │   → Automatikus készletcsökkentés         │
        │   → StockTransaction létrehozás           │
        │   → WorksheetPart létrehozás              │
        └───────────────┬───────────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────────────────┐
        │   STÁTUSZ VÁLTOZTATÁS                     │
        │                                           │
        │   Open → Waiting for Parts                │
        │   Waiting → Closed                        │
        └───────────────┬───────────────────────────┘
                        │
                        ▼ (ha Closed)
        ┌───────────────────────────────────────────┐
        │   LEZÁRÁS                                 │
        │   • Javítás befejezési ideje (kötelező)  │
        │   • Downtime kalkuláció                   │
        │   • MSZ EN 13460 validáció                │
        │                                           │
        │   Automatikus:                            │
        │   • ScrappingDoc[] generálás              │
        │     (ha alkatrész használva)              │
        └───────────────────────────────────────────┘
```

---

## 4. Inventory & Storage Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                    ÚJ ALKATRÉSZ LÉTREHOZÁS                      │
└─────────────────────────────────────────────────────────────────┘
                            │
                        [Inventory menü]
                        → Új alkatrész
                            │
        ┌───────────────────┴───────────────────┐
        │                                       │
   Alapadatok:                          Kezdeti mennyiség:
   • SKU (egyedi)                       • Mennyiség (opc.)
   • Név                                • Storage location (OPC.)
   • Leírás                             │
   • Kategória                          │
   • Beszállító                        │
   • Árak                              │
   • Biztonsági készlet                │
        │                                       │
        └───────────────┬───────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │   InventoryLevel létrehozás   │
        │   (quantity_on_hand = 0)      │
        └───────────────┬───────────────┘
                        │
        ┌───────────────┴───────────────┐
        │                               │
    VAN storage location?          NINCS storage location?
        │                               │
        ▼                               ▼
┌───────────────┐              ┌───────────────────────────┐
│ PartLocation  │              │ "Parts without location"  │
│ létrehozás    │              │ listában jelenik meg      │
│               │              │ (Storage menü)            │
│ InventoryLevel│              │                           │
│ frissítés     │              │ → "Tárhelyhez rendelés"   │
└───────────────┘              └───────────────┬───────────┘
                                               │
                                               ▼
                                    ┌──────────────────────┐
                                    │ STORAGE LOCATION     │
                                    │ Hozzárendelés        │
                                    │                      │
                                    │ Szűrés:              │
                                    │ • Üres tárhelyek     │
                                    │ • Azonos SKU tárhelyek│
                                    │                      │
                                    │ Mennyiség megadása   │
                                    └──────────┬───────────┘
                                               │
                                               ▼
                                    ┌──────────────────────┐
                                    │ PartLocation         │
                                    │ létrehozás           │
                                    │                      │
                                    │ InventoryLevel       │
                                    │ frissítés            │
                                    └──────────────────────┘
```

---

## 5. Problémás Területek (Logikai Hiányosságok)

```
┌─────────────────────────────────────────────────────────────────┐
│                    IDENTIFIKÁLT PROBLÉMÁK                       │
└─────────────────────────────────────────────────────────────────┘

1. ❌ PMHistory ↔ Worksheet kapcsolat hiányzik
   ┌──────────────┐          ┌──────────────┐
   │  PMHistory   │          │  Worksheet   │
   │              │    ?     │              │
   │              │ ──────── │              │
   └──────────────┘          └──────────────┘
   
   JAVASLAT: PMHistory.worksheet_id mező

2. ❌ Inventory + Storage szétválasztva
   ┌──────────────┐          ┌──────────────┐
   │  Inventory   │          │   Storage    │
   │   (Parts)    │    ≠     │  (Locations) │
   └──────────────┘          └──────────────┘
   
   JAVASLAT: Integrált workflow, inline storage assignment

3. ❌ Service Records nem kapcsolódik egyértelműen
   ┌──────────────┐
   │Service Records│  ← Mit tartalmaz?
   └──────────────┘    • PMHistory?
                       • Worksheet?
                       • Mindkettő?
   
   JAVASLAT: Összesítő nézet PMHistory + Worksheet

4. ❌ Alkatrész használat duplikáció
   PM Task elvégzés        Worksheet
   (alkatrész használat)   (alkatrész használat)
        │                       │
        └───────────┬───────────┘
                    │
            Két helyen van?
            Vagy átmásolódik?
   
   JAVASLAT: Egyértelműsítés, vagy ne legyen duplikáció

5. ❌ InventoryLevel ↔ PartLocation validáció hiányzik
   InventoryLevel.quantity_on_hand = ?
   PartLocation[].quantity összege = ?
   
   JAVASLAT: Automatikus validáció és szinkronizáció
```

---

## 6. Javasolt Logikus Menü Struktúra

```
┌─────────────────────────────────────────────────────────────┐
│ 1. ÁTTEKINTÉS                                               │
│    • Dashboard                                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 2. ESZKÖZKEZELÉS                                            │
│    ├── Production Lines                                     │
│    │   └── [Gépek] tab                                      │
│    │   └── [Alkatrészek] tab (opcionális)                  │
│    │                                                         │
│    ├── Assets / Machines                                    │
│    │   └── Lista                                            │
│    │   └── Karbantartás igénylése                           │
│    │                                                         │
│    └── Preventive Maintenance                               │
│        ├── Aktív feladatok                                  │
│        ├── Elvégzett feladatok                              │
│        └── Új feladat                                       │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 3. MŰVELETEK                                                │
│    ├── Worksheets                                           │
│    │   ├── Aktív                                            │
│    │   ├── Lezárt                                           │
│    │   └── Új                                               │
│    │                                                         │
│    └── Service Records (ÖSSZESÍTŐ)                          │
│        └── PMHistory + Worksheet egyesített nézet           │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 4. KÉSZLETKEZELÉS                                           │
│    ├── Parts                                                │
│    │   ├── Lista (csoportosítás: All/Line/Machine)          │
│    │   └── Új alkatrész + Storage inline                    │
│    │                                                         │
│    ├── Storage                                              │
│    │   ├── Tárhelyek fa                                     │
│    │   └── Alkatrészek tárhely nélkül                       │
│    │                                                         │
│    └── Inventory Audit                                      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 5. JELENTÉSEK                                               │
│    └── Reports                                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 6. EMBERI ERŐFORRÁSOK                                       │
│    ├── Vacation                                             │
│    └── Shift Schedule                                       │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 7. RENDSZERKEZELÉS                                          │
│    ├── Users                                                │
│    ├── Permissions                                          │
│    ├── Logs                                                 │
│    └── Settings                                             │
└─────────────────────────────────────────────────────────────┘
```

