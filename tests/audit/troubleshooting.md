# CMMS Audit System - Troubleshooting Guide

## 🔧 Gyakori Problémák és Megoldások

### 1. ImportError: No module named 'xxx'

**Probléma**: Hiányzó Python package-ek.

**Megoldás**:
```bash
# Győződj meg róla, hogy a virtuális környezet aktív
.\venv_audit\Scripts\activate

# Telepítsd újra a requirements-et
pip install -r tests\audit\requirements_audit.txt

# Ellenőrizd, hogy települt-e
pip list | findstr pytest
```

---

### 2. ModuleNotFoundError: No module named 'database'

**Probléma**: A CMMS_Project modul nem található a Python path-ban.

**Megoldás**:
```python
# Ellenőrizd, hogy a test fájlban van-e:
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "CMMS_Project"))
```

**Vagy futtasd a teszt mappából**:
```bash
cd E:\Artence_CMMS\tests\audit
python run_audit.py
```

---

### 3. Connection Error: Backend szerver nem elérhető

**Probléma**: Az API backend (http://116.203.226.140:8000) nem válaszol.

**Megoldás**:

1. **Ellenőrizd a szervert**:
```bash
curl http://116.203.226.140:8000/api/health/
```

2. **Módosítsd az audit_config.py-t** ha más URL kell:
```python
api_base_url: str = "http://localhost:8000/api"  # Helyi fejlesztéshez
```

3. **Indítsd el a helyi backend-et**:
```bash
cd E:\Artence_CMMS\CMMS_Project
python -m uvicorn api.server:app --host 0.0.0.0 --port 8000
```

---

### 4. Database Error: Unable to open database file

**Probléma**: A cmms.db adatbázis fájl nem található.

**Megoldás**:

1. **Ellenőrizd az adatbázis elérési utat** az `audit_config.py`-ban:
```python
database_path: str = str(CMMS_PROJECT / "data" / "cmms.db")
```

2. **Inicializáld az adatbázist** ha nem létezik:
```bash
cd E:\Artence_CMMS\CMMS_Project
python main.py
# Vagy
python -c "from database.connection import init_database; init_database()"
```

---

### 5. Test Failed: 401 Unauthorized

**Probléma**: Az audit teszt felhasználó (a.geleta) bejelentkezése sikertelen.

**Megoldás**:

1. **Ellenőrizd a felhasználói adatokat** az `audit_config.py`-ban:
```python
test_admin_username: str = "a.geleta"
test_admin_password: str = "Gele007ta"
```

2. **Ellenőrizd az adatbázisban**, hogy létezik-e a user:
```sql
SELECT * FROM users WHERE username = 'a.geleta';
```

3. **Hozz létre tesztfelhasználót** ha szükséges:
```python
from CMMS_Project.services.user_service import create_user
create_user(
    username="a.geleta",
    password="Gele007ta",
    role="Manager"
)
```

---

### 6. Permission Error: Access denied to logs/reports folder

**Probléma**: Nincs írási jog a logs vagy reports mappához.

**Megoldás**:

1. **Futtasd adminisztrátorként** a CMD-t vagy PowerShell-t.

2. **Ellenőrizd a mappák jogosultságait**:
```bash
# Windows
icacls E:\Artence_CMMS\tests\audit\logs
icacls E:\Artence_CMMS\tests\audit\reports
```

3. **Adj írási jogot** ha szükséges:
```bash
icacls E:\Artence_CMMS\tests\audit\logs /grant Users:F
```

---

### 7. Test Timeout: Tests hanging indefinitely

**Probléma**: A tesztek timeout miatt leállnak.

**Megoldás**:

1. **Növeld a timeout értékét** az `audit_config.py`-ban:
```python
api_timeout: int = 60  # 30-ról 60-ra
```

2. **Használj pytest timeout-ot**:
```bash
pytest tests/audit/02_functional --timeout=120
```

---

### 8. SSL/TLS Error: Certificate verification failed

**Probléma**: HTTPS tanúsítvány hiba.

**Megoldás**:

1. **Fejlesztési környezetben** kapcsold ki az SSL verifikációt:
```python
# base_test.py APITestMixin osztályban
requests.get(..., verify=False)
```

2. **Produkció környezetben** használj érvényes tanúsítványt.

---

### 9. HTML Report nem generálódik

**Probléma**: A `generate_html_report()` nem hoz létre fájlt.

**Megoldás**:

1. **Ellenőrizd a config beállítást**:
```python
# audit_config.py
generate_html_report: bool = True
```

2. **Ellenőrizd a reports mappát**:
```bash
dir E:\Artence_CMMS\tests\audit\reports
```

3. **Futtasd újra verbose móddal**:
```bash
python run_audit.py -v
```

---

### 10. "No tests collected" Warning

**Probléma**: A test discovery nem talál teszteket.

**Megoldás**:

1. **Ellenőrizd a test fájlok nevét**: Kezdődjenek `test_` prefix-el.

2. **Ellenőrizd a test class nevét**: Kezdődjön `Test` vagy örököljön `AuditBaseTest`-ből.

3. **Ellenőrizd a test metódusok nevét**: Kezdődjenek `test_` prefix-el.

4. **Futtasd verbose discovery-vel**:
```bash
pytest --collect-only tests/audit/02_functional
```

---

## 📋 Diagnosztikai Checklist

Használd ezt a checklistet a problémák diagnosztizálásához:

### Környezet Ellenőrzés
- [ ] Python verzió >= 3.9: `python --version`
- [ ] Virtuális környezet aktív: `where python` (kell hogy venv_audit legyen benne)
- [ ] Összes requirements telepítve: `pip list`
- [ ] CMMS_Project elérhető: `cd CMMS_Project && python -c "import database.models"`

### Backend Ellenőrzés
- [ ] Backend fut: `curl http://116.203.226.140:8000/api/health/`
- [ ] Login endpoint elérhető: `curl -X POST http://116.203.226.140:8000/api/v1/auth/login`
- [ ] Test user létezik az adatbázisban

### Adatbázis Ellenőrzés
- [ ] cmms.db fájl létezik: `dir CMMS_Project\data\cmms.db`
- [ ] Adatbázis elérhető: SQLite browser-rel megnyitható
- [ ] Táblák léteznek: users, assets, worksheets, stb.

### Fájlrendszer Ellenőrzés
- [ ] tests/audit/ mappa létezik
- [ ] logs/ és reports/ mappák léteznek és írhatóak
- [ ] audit_config.py hibátlan

### Teszt Ellenőrzés
- [ ] Test fájlok syntax hibátlanok: `python -m py_compile tests/audit/02_functional/test_functional_crud.py`
- [ ] Base test betölthető: `python -c "from tests.audit.base_test import AuditBaseTest"`

---

## 🆘 További Segítség

Ha a fenti megoldások nem működnek:

1. **Nézd meg a log fájlokat**:
   - `tests/audit/logs/audit_run.log`
   - `tests/audit/logs/functional_audit.log`
   - stb.

2. **Futtasd debug móddal**:
```bash
python -m pdb run_audit.py
```

3. **Ellenőrizd a Python import-okat**:
```bash
python -c "import sys; print('\n'.join(sys.path))"
```

4. **Próbáld egyenként a teszteket**:
```bash
python -m pytest tests/audit/02_functional/test_functional_crud.py::UserManagementAudit::test_01_user_create -v
```

---

**Utolsó frissítés**: 2025.12.15
**Verzió**: 1.0.0

