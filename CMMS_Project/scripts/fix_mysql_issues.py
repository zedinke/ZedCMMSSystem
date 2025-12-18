"""
MySQL szerver problémák javítása
- Kill-eli a régi tranzakciókat
- Törli a lejárt session-öket
- Ajánlásokat ad a /tmp probléma megoldásához
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from database.connection import engine, get_database_config
from config.app_config import get_database_config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_mysql_issues():
    """Javítja a MySQL szerver problémáit"""
    print("=" * 80)
    print("MYSQL SZERVER JAVÍTÁS")
    print("=" * 80)
    
    try:
        config = get_database_config("production")
        
        # 1. Régi tranzakciók kill-elése
        print(f"\n1. RÉGI TRANZAKCIÓK KILL-ELÉSE:")
        with engine.connect() as conn:
            # Keresd meg a régi, blokkoló tranzakciókat
            result = conn.execute(text("""
                SELECT ID, USER, TIME, STATE, INFO
                FROM information_schema.PROCESSLIST
                WHERE DB = :db_name
                AND TIME > 300
                AND STATE LIKE '%commit%'
                ORDER BY TIME DESC
            """), {"db_name": config['database']})
            
            old_processes = result.fetchall()
            if old_processes:
                print(f"   {len(old_processes)} régi tranzakció található (>5 perc):")
                killed_count = 0
                for proc in old_processes:
                    proc_id = proc[0]
                    proc_time = proc[2]
                    proc_state = proc[3]
                    print(f"   - Process ID: {proc_id}, Time: {proc_time}s, State: {proc_state}")
                    
                    try:
                        # Kill-eljük a folyamatot
                        conn.execute(text(f"KILL {proc_id}"))
                        conn.commit()
                        print(f"     ✓ Kill-elve")
                        killed_count += 1
                    except Exception as e:
                        print(f"     ✗ Nem sikerült kill-elni: {e}")
                
                print(f"\n   Összesen {killed_count} tranzakció kill-elve")
            else:
                print("   ✓ Nincs régi tranzakció")
        
        # 2. Lejárt session-ök törlése
        print(f"\n2. LEJÁRT SESSION-ÖK TÖRLÉSE:")
        with engine.connect() as conn:
            # Számold meg a lejárt session-öket
            result = conn.execute(text("""
                SELECT COUNT(*) as count
                FROM user_sessions
                WHERE expires_at <= NOW()
            """))
            expired_count = result.fetchone()[0]
            
            if expired_count > 0:
                print(f"   {expired_count} lejárt session található")
                try:
                    result = conn.execute(text("""
                        DELETE FROM user_sessions
                        WHERE expires_at <= NOW()
                    """))
                    conn.commit()
                    deleted_count = result.rowcount
                    print(f"   ✓ {deleted_count} lejárt session törölve")
                except Exception as e:
                    print(f"   ✗ Nem sikerült törölni: {e}")
            else:
                print("   ✓ Nincs lejárt session")
        
        # 3. Tmp változók növelése (ha lehetséges)
        print(f"\n3. TMP VÁLTOZÓK NÖVELÉSE:")
        try:
            with engine.connect() as conn:
                # Ellenőrizd a jelenlegi értékeket
                result = conn.execute(text("SHOW VARIABLES LIKE 'tmp_table_size'"))
                current_tmp_size = int(result.fetchone()[1])
                
                result = conn.execute(text("SHOW VARIABLES LIKE 'max_heap_table_size'"))
                current_heap_size = int(result.fetchone()[1])
                
                print(f"   Jelenlegi tmp_table_size: {current_tmp_size / 1024 / 1024:.2f} MB")
                print(f"   Jelenlegi max_heap_table_size: {current_heap_size / 1024 / 1024:.2f} MB")
                
                # Próbáld meg növelni (ha SUPER jogosultság van)
                if current_tmp_size < 64 * 1024 * 1024:  # 64MB alatt
                    try:
                        new_size = 128 * 1024 * 1024  # 128MB
                        conn.execute(text(f"SET GLOBAL tmp_table_size = {new_size}"))
                        conn.execute(text(f"SET GLOBAL max_heap_table_size = {new_size}"))
                        conn.commit()
                        print(f"   ✓ Tmp változók növelve {new_size / 1024 / 1024:.2f} MB-ra")
                    except Exception as e:
                        print(f"   ⚠ Nem sikerült növelni (nincs SUPER jogosultság): {e}")
                        print(f"   Kérjük a DBA-t, hogy futtassa:")
                        print(f"   SET GLOBAL tmp_table_size = 128*1024*1024;")
                        print(f"   SET GLOBAL max_heap_table_size = 128*1024*1024;")
                else:
                    print("   ✓ Tmp változók már megfelelőek")
        except Exception as e:
            print(f"   ⚠ Nem sikerült módosítani: {e}")
        
        # 4. Ajánlások
        print(f"\n4. KRITIKUS AJÁNLÁSOK:")
        print(f"   ⚠⚠⚠ A /tmp könyvtár tele van a szerveren!")
        print(f"   Ez okozza a login lefagyását.")
        print(f"\n   AZONNALI LÉPÉSEK A SZERVEREN:")
        print(f"   1. SSH kapcsolat a szerverhez")
        print(f"   2. Ellenőrizd a lemezterületet:")
        print(f"      df -h /tmp")
        print(f"   3. Nézd meg mi foglalja a helyet:")
        print(f"      ls -lah /tmp | head -20")
        print(f"      du -sh /tmp/* | sort -h | tail -10")
        print(f"   4. Töröld az ideiglenes fájlokat (ÓVATOSAN!):")
        print(f"      # Először állítsd le a MySQL-t, ha lehetséges")
        print(f"      # sudo systemctl stop mysql")
        print(f"      # sudo rm -rf /tmp/*")
        print(f"      # sudo systemctl start mysql")
        print(f"\n   VAGY állítsd be egy másik tmpdir-t:")
        print(f"      SET GLOBAL tmpdir = '/var/tmp';")
        print(f"      # (Ez újraindítás után visszaáll, állítsd be a my.cnf-ben is)")
        
        print("\n" + "=" * 80)
        print("JAVÍTÁS BEFEJEZVE")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n✗ HIBA: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_mysql_issues()

