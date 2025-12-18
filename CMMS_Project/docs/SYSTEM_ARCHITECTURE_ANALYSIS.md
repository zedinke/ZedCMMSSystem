# CMMS Rendszer Architektúra Elemzés és Javaslatok

**Dátum**: 2025.12.18  
**Cél**: Logikai munkafolyamatok és felhasználói élmény optimalizálása

---

## 📊 JELENLEGI RENDSZER ÁTTEKINTÉS

### Főmodulok és Kapcsolataik

```
┌─────────────────────────────────────────────────────────────────┐
│                    ÁTTEKINTÉS / OVERVIEW                        │
│  └── Dashboard (statisztikák, összesítések)                    │
└─────────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼────────┐  ┌──────▼──────┐  ┌────────▼───────┐
│ ESZKÖZKEZELÉS │  │ KÉSZLETKEZELÉS │  │  MŰVELETEK    │
│                │  │                │  │                │
│ Production Line│  │ Inventory      │  │ PM Tasks       │
│ Assets         │  │ Storage        │  │ Worksheets     │
│                │  │ Inventory Audit│  │ Service Records│
└────────────────┘  └────────────────┘  └────────────────┘
```

---

## 🔗 ENTITÁS KAPCSOLATOK ÁBRÁJA

```
ProductionLine (Termelési sor)
    │
    ├─── 1:N ─── Machine (Gép)
    │               │
    │               ├─── M:N ─── Part (Alkatrész) [kompatibilis]
    │               │
    │               ├─── 1:N ─── PMTask (Karbantartási feladat)
    │               │               │
    │               │               └─── 1:N ─── PMHistory (Karbantartási történet)
    │               │                                   │
    │               │                                   ├─── Generál → WorkRequestPDF
    │               │                                   ├─── Generál → PMWorksheetPDF
    │               │                                   ├─── Generál → ScrappingDocument[]
    │               │                                   └─── 1:N ─── PMTaskAttachment (Fájlok)
    │               │
    │               └─── 1:N ─── Worksheet (Munkalap)
    │                               │
    │                               ├─── 1:N ─── WorksheetPart (Felhasznált alkatrészek)
    │                               │               │
    │                               │               └─── N:1 ─── Part
    │                               │
    │                               └─── 1:1 ─── WorksheetPDF
    │
    └─── N:1 ─── User (Felhasználó) [responsible_person]

Part (Alkatrész)
    │
    ├─── 1:1 ─── InventoryLevel (Készlet szint)
    ├─── 1:N ─── StockTransaction (Készletmozgások)
    ├─── 1:N ─── PartLocation (Raktárhelyek)
    ├─── 1:N ─── StockReservation (Foglalások)
    └─── N:1 ─── Supplier (Beszállító)
```

---

## 🔄 MUNKAFOLYAMATOK

### 1. PM (Preventive Maintenance) Folyamat

```
[PM Task Létrehozás]
    │
    ├─── Manuális: PM menü → Új feladat
    └─── Automatikus: Production Line → Gép → "Karbantartás igénylése"
         │
         ├─── Hozzárendelés (felhasználóhoz vagy globális)
         ├─── Prioritás beállítása
         └─── Határidő megadása
              │
              ▼
[PM Task Aktív]
    │
    ├─── Feladat megjelenik PM listában
    └─── Dashboard-on látható (due_today, overdue)
         │
         ▼
[PM Task Elvégzése]
    │
    ├─── Feladat kiválasztása → "Elvégzés" gomb
    ├─── Kitöltendő mezők:
    │   ├─── Dátum, idő
    │   ├─── Munka leírása
    │   ├─── Megfigyelések
    │   ├─── Státusz (kész/részleges/problémás)
    │   ├─── Felhasznált alkatrészek (választható)
    │   │   └─── Storage location választás
    │   │   └─── Mennyiség megadása
    │   └─── Fájlok feltöltése (képek, dokumentumok)
    │
    ├─── Automatikus generálás:
    │   ├─── Work Request PDF
    │   ├─── PM Worksheet PDF
    │   └─── Scrapping Document[] (ha alkatrész használva)
    │
    └─── PMHistory létrehozása
         │
         ▼
[PMHistory Dokumentumok]
    │
    ├─── Fájlok mentése: {parent_dir}/pm_task_{id}/history_{history_id}/
    ├─── Dokumentumok másolása a könyvtárba
    └─── PMTaskAttachment rekordok létrehozása
         │
         ▼
[Elvégzett PM Task]
    │
    ├─── "Details" gomb → Részletes információ
    ├─── "Work Request" gomb → PDF megnyitása
    ├─── "Worksheet" gomb → PDF megnyitása
    ├─── "Scrapping Document" gomb → PDF[] megnyitása
    └─── "Files" gomb → Feltöltött fájlok megtekintése
```

### 2. Worksheet (Munkalap) Folyamat

```
[Worksheet Létrehozás]
    │
    ├─── Manuális: Worksheets menü → Új munkalap
    └─── Automatikus: PM Task elvégzésekor (PMService)
         │
         ├─── Gép kiválasztása
         ├─── Felhasználó hozzárendelése
         ├─── Cím, leírás
         └─── Leállás ideje (opcionális)
              │
              ▼
[Worksheet Státusz: Open]
    │
    ├─── Alkatrész hozzáadása (választható)
    │   ├─── Part kiválasztása
    │   ├─── Mennyiség
    │   ├─── Storage location
    │   └─── Automatikus készletcsökkentés
    │
    └─── Státusz változtatás
         │
         ├─── "Waiting for Parts" → Várás alkatrészekre
         └─── "Closed" → Lezárás
              │
              ├─── Javítás befejezési ideje megadása
              ├─── Downtime kalkuláció
              └─── Automatikus generálás:
                  └─── Scrapping Document[] (ha alkatrész használva)
```

### 3. Inventory (Készletkezelés) Folyamat

```
[Part Létrehozás]
    │
    ├─── Inventory menü → Új alkatrész
    ├─── Alapadatok (SKU, név, leírás)
    ├─── Beszállító, árak
    ├─── Biztonsági készlet
    └─── Kezdeti mennyiség (opcionális)
         │
         ▼
[InventoryLevel Létrehozás]
    │
    └─── Ha nincs storage location → "Parts without storage location" listában jelenik meg
         │
         ▼
[Storage Location Hozzárendelés]
    │
    ├─── Storage menü → "Parts without storage location"
    └─── Part kiválasztása → "Tárhelyhez rendelés"
         │
         ├─── Kompatibilis tárhelyek szűrése:
         │   ├─── Üres tárhelyek
         │   └─── Azonos SKU-val rendelkező tárhelyek
         │
         └─── Mennyiség megadása
              │
              ▼
[PartLocation Létrehozás]
```

---

## ⚠️ LOGIKAI PROBLÉMÁK ÉS JAVASLATOK

### 1. ⚠️ PROBLÉMA: PMHistory ↔ Worksheet Kapcsolat Nem Használatos a UI-ban

**Jelenlegi helyzet:**
- PMHistory modellben MÁR VAN `worksheet_id` mező ✅
- PM Task elvégzésekor automatikusan be van állítva ✅
- **DE** a UI-ban nincs mutatva ez a kapcsolat ❌
- Worksheet részleteknél nincs visszalink a PMHistory-re ❌

**Javaslat:**
- PM Task elvégzett részleteknél mutassuk a kapcsolódó Worksheet-et (ha van)
- Worksheet részleteknél mutassuk, hogy melyik PM Task-ból jött (ha van)
- Service Records-ban egyesített nézet PMHistory + Worksheet

---

### 2. ❌ PROBLÉMA: Inventory és Storage Logika Szétválasztva

**Jelenlegi helyzet:**
- Inventory menü: alkatrészek kezelése
- Storage menü: tárhelyek kezelése
- Nincs egyértelmű munkafolyamat

**Javaslat - Logikus munkafolyamat:**

```
[Új alkatrész hozzáadása]
    │
    ├─── 1. Inventory menü → Új alkatrész
    │   └─── Alapadatok megadása
    │   └─── Kezdeti mennyiség (opcionális)
    │       │
    │       └─── HA van kezdeti mennyiség:
    │           └─── Automatikusan megjelenik "Storage assignment" lépés
    │               └─── Tárhely kiválasztása (Inline a létrehozásban)
    │
    └─── 2. HA nincs tárhely hozzárendelve:
        └─── Dashboard notification: "X alkatrész vár tárhelyre"
            └─── Kattintás → Storage menü → "Parts without location"
```

**Vagy jobb megoldás:**
- Inventory menüben legyen egy "Storage" tab/fül
- Új alkatrész létrehozásakor egy lépésben lehessen tárhelyet is hozzárendelni
- Ha nincs hozzárendelve, akkor megjelenik a "Parts without location" lista

---

### 3. ❌ PROBLÉMA: Service Records Hiányos

**Jelenlegi helyzet:**
- Van Service Records menüpont
- De nem egyértelmű, hogy mi a kapcsolat PM Task-okkal és Worksheet-okkal

**Javaslat:**
- Service Records legyen egy **összesítő nézet**:
  - PMHistory rekordok
  - Worksheet rekordok (closed)
  - Egyesített timeline
  - Szűrhető gép, dátum, felhasználó szerint

---

### 4. ❌ PROBLÉMA: Production Line → Machine → Part Hierarchia Nem Intuitív

**Jelenlegi helyzet:**
- Production Line menü: sorok listája
- Production Line kiválasztásakor: gépek és alkatrészek listája
- De az Inventory menüben is lehet gépek szerint csoportosítani

**Javaslat - Logikus navigáció:**

```
Production Line menü
    │
    └─── Production Line kiválasztás
        │
        ├─── [Gépek] tab
        │   └─── Gép kiválasztás
        │       ├─── Részletes információk
        │       ├─── "Karbantartás igénylése" gomb
        │       └─── [Kompatibilis alkatrészek] fül
        │
        └─── [Alkatrészek] tab (opcionális)
            └─── Összes kompatibilis alkatrész listája
                └─── Kattintás → Alkatrész részletek
```

---

### 5. ❌ PROBLÉMA: Worksheet és PM Task Alkatrész Használat Duplikáció

**Jelenlegi helyzet:**
- PM Task elvégzésekor lehet alkatrészt használni
- Worksheet-ben is lehet alkatrészt használni
- Ha PM Task-ból jön Worksheet, akkor duplikáció lehet

**Javaslat:**
- Ha PM Task elvégzésekor alkatrészt használunk, NE hozzon létre Worksheet-et
- Vagy ha létrehoz Worksheet-et, akkor a PM Task alkatrészei ne kerüljenek át
- Vagy egyértelműen jelölje, hogy melyik alkatrész hol van használva

---

### 6. ❌ PROBLÉMA: Storage Location és InventoryLevel Konfúzió

**Jelenlegi helyzet:**
- `InventoryLevel`: összesített készlet (part_id → quantity_on_hand)
- `PartLocation`: részletes tárhelyek (part_id + storage_location_id → quantity)
- Nincs egyértelmű összegzés

**Javaslat:**
- `InventoryLevel.quantity_on_hand` mindig legyen a `PartLocation.quantity` összege
- Validáció: InventoryLevel = SUM(PartLocation.quantity)
- Ha nem egyezik, warning és javítási lehetőség

---

## ✅ JAVASOLT LOGIKUS MENÜ STRUKTÚRA

```
┌─────────────────────────────────────────────────────────────┐
│ 1. ÁTTEKINTÉS / OVERVIEW                                    │
│    └─── Dashboard (statisztikák, összesítések)             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 2. ESZKÖZKEZELÉS / ASSET MANAGEMENT                         │
│    ├─── Production Lines (termelési sorok)                 │
│    │   └─── [Gépek listája, Alkatrészek listája]          │
│    ├─── Assets / Machines (gépek)                          │
│    │   └─── [Lista, Karbantartás igénylése]               │
│    └─── Preventive Maintenance (PM Tasks)                  │
│        ├─── [Aktív feladatok]                              │
│        ├─── [Elvégzett feladatok]                          │
│        └─── [Feladat létrehozás]                           │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 3. MŰVELETEK / OPERATIONS                                   │
│    ├─── Worksheets (Munkalapok)                            │
│    │   ├─── [Aktív munkalapok]                             │
│    │   ├─── [Lezárt munkalapok]                            │
│    │   └─── [Új munkalap létrehozása]                      │
│    └─── Service Records (Szerviz feljegyzések)             │
│        └─── [Összesítő nézet: PM + Worksheet]              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 4. KÉSZLETKEZELÉS / INVENTORY MANAGEMENT                    │
│    ├─── Parts (Alkatrészek)                                │
│    │   ├─── [Alkatrész lista]                              │
│    │   ├─── [Csoportosítás: All/Production Line/Machine]   │
│    │   └─── [Új alkatrész + Storage hozzárendelés]         │
│    ├─── Storage (Raktárkezelés)                            │
│    │   ├─── [Tárhelyek fa struktúra]                       │
│    │   └─── [Alkatrészek tárhely nélkül]                   │
│    └─── Inventory Audit (Készletellenőrzés)                │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 5. JELENTÉSEK / REPORTS                                     │
│    └─── Reports (statisztikák, export)                     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 6. EMBERI ERŐFORRÁSOK / HUMAN RESOURCES                     │
│    ├─── Vacation (Szabadságok)                             │
│    └─── Shift Schedule (Műszak beosztás)                   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 7. RENDSZERKEZELÉS / SYSTEM ADMIN                           │
│    ├─── Users (Felhasználók)                               │
│    ├─── Permissions (Jogosultságok)                        │
│    ├─── Logs (Rendszer naplók)                             │
│    └─── Settings (Beállítások)                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 PRIORITÁSOS JAVÍTÁSOK

### Sürgős (Logikai zavarok)

1. **PMHistory ↔ Worksheet kapcsolat UI-ban mutatása**
   - ✅ PMHistory modellben már van `worksheet_id` mező
   - ❌ UI-ban NEM látható ez a kapcsolat
   - Javaslat: PM Task részleteknél mutassuk a kapcsolódó Worksheet-et
   - Javaslat: Worksheet részleteknél mutassuk a kapcsolódó PMHistory-t

2. **Inventory + Storage integráció**
   - Új alkatrész létrehozásakor tárhely hozzárendelés lehetősége
   - Egyértelmű workflow

3. **Service Records átstruktúrálás**
   - Összesítő nézet PM + Worksheet rekordokból
   - Timeline megjelenítés

### Fontos (Felhasználói élmény)

4. **Production Line → Machine → Part navigáció javítása**
   - Tab-ok használata
   - Inline részletek megjelenítése

5. **Worksheet és PM Task alkatrész használat egyeztetése**
   - Duplikáció elkerülése
   - Egyértelmű jelölés

6. **InventoryLevel ↔ PartLocation validáció**
   - Automatikus szinkronizáció
   - Warning ha nincs egyezés

---

## 📝 ÖSSZEFOGLALÁS

A rendszer **jól felépített**, de vannak logikai hiányosságok a modulok közötti kapcsolatokban. A fő problémák:

1. **Duplikáció**: PM Task és Worksheet alkatrész használat
2. **Szétválasztottság**: Inventory és Storage nincs integrálva
3. **Nem mutatott kapcsolatok**: PMHistory ↔ Worksheet kapcsolat létezik, de UI-ban nem látható
4. **Nem intuitív navigáció**: Production Line → Machine → Part hierarchia

A javítások után a rendszer **logikusabb** és **könnyebben használható** lesz.

