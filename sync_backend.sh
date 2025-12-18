#!/bin/bash
# Backend szinkronizáló script
# Feltölti az összes szükséges fájlt és elindítja a backend szervert

echo "===== CMMS Backend Szinkronizáció ====="
echo ""

# Állj le az összes régi uvicorn folyamatot
echo "1. Régi uvicorn folyamatok leállítása..."
pkill -9 -f uvicorn 2>/dev/null
sleep 1

# Töltsd fel az api/dependencies.py-t
echo "2. dependencies.py feltöltése..."
cd /opt/cmms-backend/api/
cat > dependencies.py << 'EOFPYTHON'
# Itt a teljes dependencies.py tartalom jön
EOFPYTHON

# Ellenőrizd a fájlokat
echo "3. Fájlok ellenőrzése..."
ls -la /opt/cmms-backend/api/dependencies.py
ls -la /opt/cmms-backend/services/
ls -la /opt/cmms-backend/utils/

# Indítsd el a backend szervert
echo "4. Backend szerver indítása..."
cd /opt/cmms-backend
PYTHONPATH=/opt/cmms-backend nohup /opt/cmms-backend/venv/bin/python -m uvicorn api.server:app --host 0.0.0.0 --port 8000 > /tmp/backend.log 2>&1 &

sleep 3

# Ellenőrizd, hogy fut-e
echo "5. Backend szerver státusz..."
ps aux | grep uvicorn | grep -v grep

echo ""
echo "===== Kész! ====="
echo "Log: tail -f /tmp/backend.log"

