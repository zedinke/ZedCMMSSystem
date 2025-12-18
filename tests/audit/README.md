# CMMS Rendszer - ISO & Működési AUDIT Teszt Sorozat

## 📋 Áttekintés

Ez az átfogó audit teszt sorozat az Artence CMMS rendszer teljes validálását végzi el az alábbi szempontok szerint:

- ✅ **ISO 9001**: Minőségirányítási rendszer megfelelőség
- ✅ **ISO 55001**: Eszközgazdálkodási rendszer megfelelőség
- ✅ **GDPR**: Adatvédelmi megfelelőség
- ✅ **Cyber Security**: Biztonsági szabványok
- ✅ **Működési követelmények**: Teljes funkcionális tesztelés

## 🎯 Teszt Struktúra

```
tests/audit/
├── 01_architecture/          # Architektúra audit
├── 02_functional/            # Funkcionális CRUD tesztek
├── 03_iso9001/               # ISO 9001 megfelelőség
├── 04_iso55001/              # ISO 55001 megfelelőség
├── 05_gdpr/                  # GDPR megfelelőség
├── 06_security/              # Biztonsági audit
├── 07_database/              # Adatbázis integritás
├── 08_performance/           # Teljesítmény tesztek
├── 09_localization/          # Lokalizáció audit
├── 10_ui_ux/                 # UI/UX audit
├── 11_integration/           # Integrációs tesztek
├── 12_regression/            # Regressziós tesztek
└── reports/                  # Audit jelentések
```

## 🚀 Gyors Indítás

### 1. Környezet előkészítése
```bash
cd E:\Artence_CMMS
python -m venv venv_audit
.\venv_audit\Scripts\activate
pip install -r tests\audit\requirements_audit.txt
```

### 2. Teljes audit futtatása
```bash
python tests\audit\run_full_audit.py
```

### 3. Kategória specifikus audit
```bash
# Csak funkcionális tesztek
python tests\audit\run_audit.py --category functional

# Csak biztonsági audit
python tests\audit\run_audit.py --category security

# ISO 9001 + ISO 55001
python tests\audit\run_audit.py --category iso9001,iso55001
```

## 📊 Audit Jelentések

Az audit futtatás után a jelentések a `tests/audit/reports/` mappában találhatók:

- `audit_report_YYYYMMDD_HHMMSS.html` - HTML formátumú összefoglaló
- `audit_report_YYYYMMDD_HHMMSS.pdf` - PDF export
- `audit_details_YYYYMMDD_HHMMSS.json` - Részletes JSON adatok
- `compliance_matrix.xlsx` - ISO/GDPR compliance mátrix

## 📈 Sikerkritériumok

| Kategória | Minimum Elfogadási Szint |
|-----------|--------------------------|
| Funkcionális tesztek | 95% PASS |
| ISO 9001 megfelelőség | 100% PASS |
| ISO 55001 megfelelőség | 100% PASS |
| GDPR megfelelőség | 100% PASS |
| Biztonsági audit | 98% PASS |
| Adatbázis integritás | 100% PASS |
| Teljesítmény | 90% PASS |
| UI/UX | 85% PASS |

## 🔧 Konfigurációs Fájlok

- `audit_config.yaml` - Főkonfiguráció (adatbázis, API URL-ek, timeout-ok)
- `compliance_checklist.yaml` - ISO/GDPR checklist
- `test_data.yaml` - Teszt adatok (felhasználók, eszközök, stb.)

## 📝 Audit Kategóriák Részletesen

### 01 - Architektúra Audit
- Windows Desktop app struktúra
- FastAPI backend routing
- Android app komponensek
- Adatbázis kapcsolatok
- API integrációk

### 02 - Funkcionális Audit
- **User Management**: CRUD, role management, GDPR compliance
- **Asset Management**: Lifecycle, hierarchy, depreciation
- **Inventory**: Stock tracking, transactions, low stock alerts
- **Worksheets**: Status workflow, assignment
- **PM Tasks**: Scheduling, completion tracking
- **Reports**: Dashboard metrics, PDF/Excel export

### 03 - ISO 9001 Audit
- Dokumentumkezelés
- Nyomon követhetőség
- Audit trail
- Verziókezelés
- Kockázatkezelés

### 04 - ISO 55001 Audit
- Eszköz életciklus
- Karbantartási stratégia
- MTBF/MTTR metrikák
- Asset register completeness

### 05 - GDPR Audit
- Személyes adatok kezelése
- Hozzáférési jogok
- Right to be forgotten
- Data encryption
- Consent management

### 06 - Biztonsági Audit
- Autentikáció (JWT, session)
- Authorizáció (RBAC)
- Password hashing (Argon2)
- SQL injection védelem
- XSS védelem
- CSRF védelem
- Rate limiting

### 07 - Adatbázis Audit
- Schema integritás
- Foreign key constraints
- Indexes hatékonysága
- Migration history
- Backup/restore

### 08 - Teljesítmény Audit
- API response time < 2s
- UI load time < 1s
- Database query optimization
- Concurrent user handling
- Memory leak detection

### 09 - Lokalizáció Audit
- en.json, hu.json teljesség
- UI strings hardcoded check
- Date/time formatting

### 10 - UI/UX Audit
- Material Design 3 compliance (Android)
- Flet UI consistency (Desktop)
- Accessibility
- Error handling UX

### 11 - Integrációs Audit
- Desktop ↔ Backend ↔ DB
- Android ↔ Backend ↔ DB
- Multi-platform consistency
- Offline sync

### 12 - Regressziós Audit
- Existing unit tests
- API endpoint regression
- Critical path scenarios

## 🛠️ Használt Eszközök

- **pytest** - Python test framework
- **requests** - API testing
- **selenium** - UI automation (opcionális)
- **locust** - Load testing
- **coverage** - Code coverage
- **bandit** - Security scanning
- **sqlalchemy** - DB testing
- **pandas** - Report generation

## 📞 Támogatás

Ha kérdés van az audit futtatásával kapcsolatban, ellenőrizd:
1. `tests/audit/troubleshooting.md` - Gyakori problémák
2. `tests/audit/logs/` - Audit logok
3. GitHub Issues - Nyílt hibák listája

---

**Utolsó frissítés**: 2025.12.15
**Verzió**: 1.0.0
**Felelős**: Artence CMMS Fejlesztői Csapat

