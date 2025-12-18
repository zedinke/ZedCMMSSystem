"""
MySQL szerver javítás közvetlen MySQL kapcsolaton keresztül
Használja a meglévő MySQL hitelesítést
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

def fix_mysql_direct():
    """Javítja a MySQL problémákat közvetlen MySQL kapcsolaton keresztül"""
    print("=" * 80)
    print("MYSQL SZERVER JAVÍTÁS - KÖZVETLEN MYSQL KAPCSOLAT")
    print("=" * 80)
    
    try:
        config = get_database_config("production")
        print(f"\nKapcsolódás: {config['host']}:{config['port']}/{config['database']}")
        
        # 1. Kapcsolat tesztelése
        print(f"\n1. KAPCSOLAT TESZTELÉSE...")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test"))
            if result.fetchone()[0] == 1:
                print("   ✓ Kapcsolat sikeres")
            else:
                print("   ✗ Kapcsolat probléma")
                return
        
        # 2. Régi tranzakciók kill-elése (egyszerűbb módszerrel)
        print(f"\n2. RÉGI TRANZAKCIÓK KILL-ELÉSE...")
        try:
            with engine.connect() as conn:
                # Egyszerűbb lekérdezés, ami nem használ ideiglenes táblát
                result = conn.execute(text("SHOW PROCESSLIST"))
                processes = result.fetchall()
                
                killed_count = 0
                for proc in processes:
                    # proc struktúra: (Id, User, Host, db, Command, Time, State, Info)
                    proc_id = proc[0]
                    proc_db = proc[3]
                    proc_time = proc[5] if len(proc) > 5 else 0
                    proc_state = proc[6] if len(proc) > 6 else ""
                    
                    # Kill-eljük a régi, blokkoló tranzakciókat
                    if (proc_db == config['database'] and 
                        proc_time > 300 and  # Több mint 5 perc
                        ('commit' in str(proc_state).lower() or 'lock' in str(proc_state).lower())):
                        try:
                            print(f"   Kill-eljük a Process ID {proc_id} (Time: {proc_time}s, State: {proc_state})")
                            conn.execute(text(f"KILL {proc_id}"))
                            conn.commit()
                            killed_count += 1
                        except Exception as e:
                            print(f"   ⚠ Nem sikerült kill-elni {proc_id}: {e}")
                
                if killed_count > 0:
                    print(f"   ✓ {killed_count} régi tranzakció kill-elve")
                else:
                    print("   ✓ Nincs régi tranzakció")
        except Exception as e:
            print(f"   ⚠ Nem sikerült kill-elni a tranzakciókat: {e}")
            if "full" in str(e).lower() or "tmp" in str(e).lower():
                print("   ⚠⚠⚠ KRITIKUS: A /tmp könyvtár még mindig tele van!")
                print("   Kérlek, futtasd ezt a szerveren SSH-n keresztül:")
                print("   systemctl stop mysql")
                print("   rm -rf /tmp/*")
                print("   systemctl start mysql")
        
        # 3. Lejárt session-ök törlése
        print(f"\n3. LEJÁRT SESSION-ÖK TÖRLÉSE...")
        try:
            with engine.connect() as conn:
                # Számold meg először
                result = conn.execute(text("SELECT COUNT(*) as count FROM user_sessions WHERE expires_at <= NOW()"))
                expired_count = result.fetchone()[0]
                
                if expired_count > 0:
                    print(f"   {expired_count} lejárt session található")
                    result = conn.execute(text("DELETE FROM user_sessions WHERE expires_at <= NOW()"))
                    conn.commit()
                    deleted_count = result.rowcount
                    print(f"   ✓ {deleted_count} lejárt session törölve")
                else:
                    print("   ✓ Nincs lejárt session")
        except Exception as e:
            print(f"   ⚠ Nem sikerült törölni: {e}")
        
        # 4. MySQL változók ellenőrzése és növelése (ha lehetséges)
        print(f"\n4. MYSQL VÁLTOZÓK ELLENŐRZÉSE...")
        try:
            with engine.connect() as conn:
                # Ellenőrizd a jelenlegi értékeket
                result = conn.execute(text("SHOW VARIABLES LIKE 'tmp_table_size'"))
                current_tmp = int(result.fetchone()[1])
                
                result = conn.execute(text("SHOW VARIABLES LIKE 'max_heap_table_size'"))
                current_heap = int(result.fetchone()[1])
                
                print(f"   tmp_table_size: {current_tmp / 1024 / 1024:.2f} MB")
                print(f"   max_heap_table_size: {current_heap / 1024 / 1024:.2f} MB")
                
                # Próbáld meg növelni (ha SUPER jogosultság van)
                if current_tmp < 64 * 1024 * 1024:
                    try:
                        new_size = 128 * 1024 * 1024
                        conn.execute(text(f"SET GLOBAL tmp_table_size = {new_size}"))
                        conn.execute(text(f"SET GLOBAL max_heap_table_size = {new_size}"))
                        conn.commit()
                        print(f"   ✓ Tmp változók növelve {new_size / 1024 / 1024:.2f} MB-ra")
                    except Exception as e:
                        print(f"   ⚠ Nem sikerült növelni (nincs SUPER jogosultság): {e}")
                        print(f"   Kérjük a DBA-t, hogy futtassa:")
                        print(f"   SET GLOBAL tmp_table_size = 128*1024*1024;")
                        print(f"   SET GLOBAL max_heap_table_size = 128*1024*1024;")
        except Exception as e:
            print(f"   ⚠ Nem sikerült módosítani: {e}")
        
        # 5. Végleges ellenőrzés
        print(f"\n5. VÉGLEGES ELLENŐRZÉS...")
        try:
            with engine.connect() as conn:
                # Próbáljunk meg egy egyszerű lekérdezést
                result = conn.execute(text("SELECT COUNT(*) as count FROM user_sessions"))
                count = result.fetchone()[0]
                print(f"   ✓ user_sessions tábla elérhető: {count} sor")
                
                # Próbáljunk meg egy INSERT-et (nem commitolva)
                result = conn.execute(text("SELECT 1"))
                print(f"   ✓ Egyszerű lekérdezések működnek")
        except Exception as e:
            print(f"   ⚠ Probléma: {e}")
            if "full" in str(e).lower() or "tmp" in str(e).lower():
                print("   ⚠⚠⚠ KRITIKUS: A /tmp könyvtár még mindig tele van!")
                print("   SSH-n keresztül futtasd:")
                print("   systemctl stop mysql && rm -rf /tmp/* && systemctl start mysql")
        
        print("\n" + "=" * 80)
        print("JAVÍTÁS BEFEJEZVE")
        print("=" * 80)
        print("\n⚠ FONTOS:")
        print("Ha a /tmp könyvtár még mindig tele van, az SSH-n keresztül kell felszabadítani.")
        print("A MySQL változók növelése segíthet, de a /tmp felszabadítása kritikus!")
        print("\nTeszteld most a login-t!")
        
    except Exception as e:
        print(f"\n✗ HIBA: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_mysql_direct()

