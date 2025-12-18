# Hiányzó Funkciók - Missing Features

Ez a dokumentum összefoglalja azokat a funkciókat, amelyek a `IMPLEMENTATION_PLAN.md` és `Artience_ToyoInkGroup.md` dokumentumokban szerepelnek, de még nincsenek teljes mértékben implementálva.

---

## ✅ Elkészült Funkciók (Completed Features)

### 1. QR Code Generation & Printing ✅
**Státusz:** Teljesen implementálva / Fully implemented
- ❌ `utils/qr_generator.py` - QR kód generálás
- ❌ `ui/screens/qr_labels_dialog.py` - QR címkék generálása és nyomtatása
- ✅ `qrcode` library telepítve van a `requirements.txt`-ben

**Szükséges:**
- `generate_qr_code(part_id, sku)` - QR kép generálása
- `generate_qr_labels(part_ids, output_format='pdf')` - Nyomtatható címkék PDF-ben
- UI dialog a kiválasztott alkatrészekhez QR kódok generálásához

---

### 2. Backup & Recovery Service ✅
**Státusz:** Teljesen implementálva / Fully implemented
- ❌ `services/backup_service.py`
- ❌ Settings screen-ben "Backup Now" gomb
- ❌ Automatikus napi backup ütemezés

**Szükséges:**
- `backup_database()` - Adatbázis tömörített mentése `data/system_backups/`-be
- `backup_all_files()` - Fájlok mentése
- `restore_from_backup(backup_file)` - Visszaállítás validációval
- Settings UI-ban backup/restore funkciók

---

### 3. File Handler Utility ✅
**Státusz:** Teljesen implementálva / Fully implemented
- ❌ `utils/file_handler.py`
- ⚠️ Fájlkezelés szétszórtan van implementálva

**Szükséges:**
- `upload_file(file_obj, directory, allowed_extensions, max_size_mb)` - Fájl feltöltés validációval
- `download_file(file_path)` - Fájl letöltés
- `delete_file(file_path)` - Fájl törlés
- UUID-alapú fájlnevek biztonságért

---

### 4. Logging Configuration ✅
**Státusz:** Teljesen implementálva / Fully implemented
- ❌ `config/logging_config.py`
- ⚠️ Logging működik, de nincs strukturált konfiguráció

**Szükséges:**
- Log fájl: `logs/cmms.log`
- Log rotation: Utolsó 10 fájl, max 10 MB/fájl
- Szintek: DEBUG, INFO, WARNING, ERROR
- Formátum: timestamp, level, module, message

---

## 🟡 Fontos Hiányzó Funkciók (Important Features)

### 5. Module Management UI ✅
**Státusz:** Teljesen implementálva / Fully implemented
- ✅ `Module` modell létezik
- ✅ `asset_service.add_module()` létezik
- ❌ UI a modulok kezeléséhez (CRUD)
- ❌ Modulok megjelenítése a gép részletekben

**Szükséges:**
- Modul hozzáadása/szerkesztése/törlése UI-ban
- Modulok listája a gép részletekben
- Modul specifikációk megjelenítése

---

### 6. Asset History UI ✅
**Státusz:** Teljesen implementálva / Fully implemented
- ✅ `AssetHistory` modell létezik
- ❌ Asset history megjelenítése
- ❌ Activity timeline a gépekhez

**Szükséges:**
- `ui/screens/machine_history_screen.py` - Teljes géptörténet nézet
- Tabs: Worksheets, PM Tasks, Activity Timeline
- Változások nyomon követése

---

### 7. Machine History Screen ✅
**Státusz:** Teljesen implementálva / Fully implemented (dialog formában / as dialog)
- ❌ `ui/screens/machine_history_screen.py`
- ⚠️ Van némi history funkció, de nincs dedikált screen

**Szükséges:**
- Hierarchikus nézet: Production Line → Machine → History
- Worksheets listája a géphez
- PM Tasks listája
- Activity timeline

---

### 8. Audit Logging Service ✅
**Státusz:** Teljesen implementálva / Fully implemented
- ✅ `AuditLog` modell létezik
- ⚠️ Van némi audit logging, de nincs központi service
- ❌ Audit log megjelenítése UI-ban

**Szükséges:**
- `services/audit_service.py` - Központi audit logging
- Audit log megjelenítése (Settings vagy külön screen)
- Szűrés dátum, felhasználó, akció típus szerint

---

### 9. Translation Validator ✅
**Státusz:** Teljesen implementálva / Fully implemented
- ❌ `utils/translation_validator.py`
- ⚠️ Fordítások működnek, de nincs validáció

**Szükséges:**
- `validate_translation_completeness()` - EN/HU kulcsok összehasonlítása
- `validate_placeholders()` - Formátum konzisztencia ellenőrzés
- App indításkor futtatás, kritikus hibáknál leállás

---

## 🟢 Dokumentáció & Testing

### 10. User Documentation ✅
**Státusz:** Teljesen implementálva / Fully implemented
- ❌ `docs/USER_MANUAL.md`
- ❌ `docs/INSTALLATION.md`
- ❌ `docs/TECHNICAL.md`

**Szükséges:**
- **USER_MANUAL.md**: Kezdő lépések, funkciók útmutató, FAQ, hibaelhárítás
- **INSTALLATION.md**: Rendszerkövetelmények, lépésről lépésre telepítés, konfiguráció
- **TECHNICAL.md**: Architektúra, modulok, funkciók bővítése, séma

---

### 11. Testing Suite
**Státusz:** Van néhány teszt, de nincs teljes coverage
- ⚠️ Van néhány teszt fájl (`tests/` mappában)
- ❌ Nincs teljes unit test coverage (70-80% cél)
- ❌ Nincs teljes integration test suite
- ❌ Nincs manual testing checklist

**Szükséges:**
- Unit tesztek minden service-hez
- Integration tesztek workflow-okhoz
- Manual testing checklist (`MANUAL_TESTING.md`)
- Performance tesztek nagy adatkészletekkel

---

## 🔵 Deployment & Packaging

### 12. Executable Packaging ✅
**Státusz:** Teljesen implementálva / Fully implemented (build.spec és build.py)
- ❌ PyInstaller setup
- ❌ Windows .exe generálás
- ❌ NSIS installer (opcionális)

**Szükséges:**
- `build.py` vagy `setup.py` PyInstaller konfigurációval
- `.exe` fájl generálása (~100-200 MB)
- Installer opció (NSIS)
- Start menu shortcuts

---

### 13. Setup Wizard
**Státusz:** Hiányzik (opcionális, de ajánlott)
- ❌ First launch wizard
- ⚠️ Jelenleg manuális beállítás szükséges

**Szükséges:**
- Első indításkor wizard:
  - [ ] Nyelv beállítása
  - [ ] Admin felhasználó létrehozása
  - [ ] Adatbázis konfiguráció (opcionális)
  - [ ] Kezdeti létesítmények létrehozása
  - [ ] Cégnév beállítása

---

### 14. Version Management ✅
**Státusz:** Teljesen implementálva / Fully implemented
- ❌ `version.txt` fájl
- ❌ About screen verzióval
- ❌ Update check (jövőbeli funkció)

**Szükséges:**
- `version.txt`: `1.0.0`
- About screen verzió megjelenítéssel
- Jövőben: automatikus update check

---

## 📊 Prioritási Rendezés

### Magas Prioritás (Következő Sprint)
1. **QR Code Generation** - Inventory modulhoz kritikus
2. **Backup Service** - Adatvédelemhez kritikus
3. **File Handler Utility** - Kód tisztításához fontos
4. **Logging Configuration** - Debugging és monitoring

### Közepes Prioritás (Következő 2 Sprint)
5. **Module Management UI** - Asset management kiegészítése
6. **Asset History UI** - Teljes history tracking
7. **Machine History Screen** - Felhasználói kérés
8. **Audit Logging Service** - Biztonság és compliance

### Alacsony Prioritás (Polish & Documentation)
9. **Translation Validator** - Quality assurance
10. **User Documentation** - Felhasználói támogatás
11. **Testing Suite** - Code quality
12. **Executable Packaging** - Deployment
13. **Setup Wizard** - UX improvement
14. **Version Management** - Professional polish

---

## ✅ Már Implementált Funkciók (Reference)

- ✅ User Authentication & Roles
- ✅ Asset Management (Production Line → Machine)
- ✅ Inventory Management (CRUD, Excel import)
- ✅ Worksheet System (teljes workflow, DOCX export)
- ✅ Preventive Maintenance (teljes modul)
- ✅ Dashboard (valós statisztikák, grafikonok)
- ✅ Reports & Charts (részletes jelentések, Excel export)
- ✅ Localization (HU/EN, teljes fordítás)
- ✅ Settings Screen
- ✅ Service Records (modell és service)

---

**Dokumentum verzió:** 1.0  
**Utolsó frissítés:** 2025-12-13  
**Státusz:** Aktuális hiányzó funkciók listája

