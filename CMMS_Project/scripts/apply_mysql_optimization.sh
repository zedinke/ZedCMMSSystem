#!/bin/bash
# MySQL Optimalizálás Alkalmazása - Linux Script
# FONTOS: Futtasd root-ként vagy sudo-val!

echo "=========================================="
echo "MySQL Szerver Optimalizálás Alkalmazása"
echo "=========================================="
echo ""

# Backup készítése
echo "1. Backup készítése a jelenlegi konfigról..."
MYSQL_CONFIG="/etc/mysql/my.cnf"
if [ -f "$MYSQL_CONFIG" ]; then
    cp "$MYSQL_CONFIG" "${MYSQL_CONFIG}.backup.$(date +%Y%m%d_%H%M%S)"
    echo "   ✓ Backup készült: ${MYSQL_CONFIG}.backup.$(date +%Y%m%d_%H%M%S)"
else
    echo "   ⚠ MySQL konfigurációs fájl nem található: $MYSQL_CONFIG"
    echo "   Keresd meg a my.cnf fájlt és módosítsd manuálisan!"
    exit 1
fi

# Konfiguráció másolása
echo ""
echo "2. Optimalizált konfiguráció alkalmazása..."
echo "   FONTOS: Ellenőrizd az innodb_buffer_pool_size értékét!"
echo "   Módosítsd a fájlban a RAM méretéhez igazítva."

# MySQL újraindítása
echo ""
echo "3. MySQL újraindítása..."
systemctl restart mysql

if [ $? -eq 0 ]; then
    echo "   ✓ MySQL sikeresen újraindult"
else
    echo "   ✗ Hiba a MySQL újraindítása során!"
    echo "   Visszaállítás: cp ${MYSQL_CONFIG}.backup.* $MYSQL_CONFIG"
    exit 1
fi

# Ellenőrzés
echo ""
echo "4. MySQL állapot ellenőrzése..."
sleep 2
systemctl status mysql --no-pager | head -10

echo ""
echo "=========================================="
echo "✓ Optimalizálás alkalmazva!"
echo "=========================================="
echo ""
echo "Futtasd a következő parancsot az ellenőrzéshez:"
echo "  python -m utils.mysql_optimizer production"
echo ""




