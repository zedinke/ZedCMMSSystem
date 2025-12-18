"""
MySQL szerver diagnosztikai script
Ellenőrzi a szerver állapotát, lock-okat, tranzakciókat és a user_sessions tábla állapotát
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

def check_mysql_status():
    """Ellenőrzi a MySQL szerver állapotát"""
    print("=" * 80)
    print("MySQL SZERVER DIAGNOSZTIKA")
    print("=" * 80)
    
    try:
        config = get_database_config("production")
        print(f"\n1. KAPCSOLATI INFORMAcióK:")
        print(f"   Host: {config['host']}")
        print(f"   Port: {config['port']}")
        print(f"   Database: {config['database']}")
        print(f"   User: {config['user']}")
        
        # Kapcsolat tesztelése
        print(f"\n2. KAPCSOLAT TESZTELÉSE...")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test"))
            test_value = result.fetchone()[0]
            if test_value == 1:
                print("   ✓ Kapcsolat sikeres")
            else:
                print("   ✗ Kapcsolat probléma")
                return
        
        # MySQL verzió
        print(f"\n3. MYSQL VERZIÓ:")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT VERSION() as version"))
            version = result.fetchone()[0]
            print(f"   MySQL Version: {version}")
        
        # Aktív kapcsolatok (egyszerűsített lekérdezés)
        print(f"\n4. AKTÍV KAPCSOLATOK:")
        try:
            with engine.connect() as conn:
                # Egyszerűbb lekérdezés, ami nem használ ideiglenes táblát
                result = conn.execute(text("SHOW PROCESSLIST"))
                processes = result.fetchall()
                if processes:
                    print(f"   Összesen {len(processes)} aktív kapcsolat:")
                    cmms_processes = [p for p in processes if p[3] == config['database']]
                    print(f"   Ebből {len(cmms_processes)} a {config['database']} adatbázishoz:")
                    for proc in cmms_processes[:10]:  # Első 10
                        print(f"   - ID: {proc[0]}, User: {proc[1]}, Time: {proc[5]}s, State: {proc[6]}")
                        if proc[7]:  # INFO
                            print(f"     Query: {proc[7][:100]}")
                else:
                    print("   Nincs aktív kapcsolat")
        except Exception as e:
            print(f"   ⚠ Nem sikerült lekérdezni a kapcsolatokat: {e}")
            if "full" in str(e).lower() or "tmp" in str(e).lower():
                print("   ⚠⚠⚠ KRITIKUS: A /tmp könyvtár tele van! Ez okozza a login problémát!")
                print("   MEGOLDÁS: Szabadítsd fel a /tmp könyvtárat a szerveren!")
        
        # Lock-olt tranzakciók
        print(f"\n5. LOCK-OLT TRANZAKCIÓK:")
        try:
            with engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT 
                        r.trx_id waiting_trx_id,
                        r.trx_mysql_thread_id waiting_thread,
                        r.trx_query waiting_query,
                        b.trx_id blocking_trx_id,
                        b.trx_mysql_thread_id blocking_thread,
                        b.trx_query blocking_query
                    FROM information_schema.innodb_lock_waits w
                    INNER JOIN information_schema.innodb_trx b ON b.trx_id = w.blocking_trx_id
                    INNER JOIN information_schema.innodb_trx r ON r.trx_id = w.requesting_trx_id
                """))
                
                locks = result.fetchall()
                if locks:
                    print(f"   ⚠ {len(locks)} lock-olt tranzakció található:")
                    for lock in locks:
                        print(f"   - Waiting Thread: {lock[1]}, Blocking Thread: {lock[4]}")
                        print(f"     Waiting Query: {lock[2][:100] if lock[2] else 'N/A'}")
                        print(f"     Blocking Query: {lock[5][:100] if lock[5] else 'N/A'}")
                else:
                    print("   ✓ Nincs lock-olt tranzakció")
        except Exception as e:
            print(f"   ⚠ Nem sikerült lekérdezni a lock-okat: {e}")
            print("   (Ez normális, ha nem InnoDB táblákat használsz)")
        
        # Aktív tranzakciók
        print(f"\n6. AKTÍV TRANZAKCIÓK:")
        try:
            with engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT 
                        trx_id,
                        trx_state,
                        trx_started,
                        trx_requested_lock_id,
                        trx_wait_started,
                        trx_weight,
                        trx_mysql_thread_id,
                        trx_query
                    FROM information_schema.innodb_trx
                    ORDER BY trx_started DESC
                """))
                
                transactions = result.fetchall()
                if transactions:
                    print(f"   ⚠ {len(transactions)} aktív tranzakció:")
                    for trx in transactions[:5]:  # Első 5
                        print(f"   - Thread ID: {trx[6]}, State: {trx[1]}, Started: {trx[2]}")
                        if trx[7]:  # Query
                            print(f"     Query: {trx[7][:100]}")
                else:
                    print("   ✓ Nincs aktív tranzakció")
        except Exception as e:
            print(f"   ⚠ Nem sikerült lekérdezni a tranzakciókat: {e}")
        
        # user_sessions tábla állapota
        print(f"\n7. USER_SESSIONS TÁBLA ÁLLAPOTA:")
        with engine.connect() as conn:
            # Tábla létezés
            result = conn.execute(text("""
                SELECT COUNT(*) as count
                FROM information_schema.tables
                WHERE table_schema = :db_name
                AND table_name = 'user_sessions'
            """), {"db_name": config['database']})
            
            table_exists = result.fetchone()[0] > 0
            if table_exists:
                print("   ✓ Tábla létezik")
                
                # Sorok száma
                result = conn.execute(text("SELECT COUNT(*) as count FROM user_sessions"))
                count = result.fetchone()[0]
                print(f"   Összes session: {count}")
                
                # Aktív session-ök
                result = conn.execute(text("""
                    SELECT COUNT(*) as count
                    FROM user_sessions
                    WHERE expires_at > NOW()
                """))
                active_count = result.fetchone()[0]
                print(f"   Aktív session-ök: {active_count}")
                
                # Lejárt session-ök
                result = conn.execute(text("""
                    SELECT COUNT(*) as count
                    FROM user_sessions
                    WHERE expires_at <= NOW()
                """))
                expired_count = result.fetchone()[0]
                print(f"   Lejárt session-ök: {expired_count}")
                
                # Tábla lock státusz
                result = conn.execute(text("""
                    SELECT 
                        TABLE_NAME,
                        ENGINE,
                        TABLE_ROWS,
                        DATA_LENGTH,
                        INDEX_LENGTH,
                        AUTO_INCREMENT
                    FROM information_schema.TABLES
                    WHERE TABLE_SCHEMA = :db_name
                    AND TABLE_NAME = 'user_sessions'
                """), {"db_name": config['database']})
                
                table_info = result.fetchone()
                if table_info:
                    print(f"   Engine: {table_info[1]}")
                    print(f"   Sorok (becsült): {table_info[2]}")
                    print(f"   Adatméret: {table_info[3] / 1024 / 1024:.2f} MB" if table_info[3] else "   Adatméret: 0 MB")
                    print(f"   Indexméret: {table_info[4] / 1024 / 1024:.2f} MB" if table_info[4] else "   Indexméret: 0 MB")
            else:
                print("   ✗ Tábla nem létezik!")
        
        # Indexek ellenőrzése
        print(f"\n8. USER_SESSIONS INDEXEK:")
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    INDEX_NAME,
                    COLUMN_NAME,
                    SEQ_IN_INDEX,
                    NON_UNIQUE
                FROM information_schema.STATISTICS
                WHERE TABLE_SCHEMA = :db_name
                AND TABLE_NAME = 'user_sessions'
                ORDER BY INDEX_NAME, SEQ_IN_INDEX
            """), {"db_name": config['database']})
            
            indexes = result.fetchall()
            if indexes:
                current_index = None
                for idx in indexes:
                    if idx[0] != current_index:
                        current_index = idx[0]
                        unique = "UNIQUE" if idx[3] == 0 else "INDEX"
                        print(f"   {unique} {idx[0]}: {idx[1]}")
                    else:
                        print(f"              {idx[1]}")
            else:
                print("   ⚠ Nincs index a táblán")
        
        # MySQL változók ellenőrzése
        print(f"\n9. MYSQL VÁLTOZÓK:")
        with engine.connect() as conn:
            important_vars = [
                'innodb_lock_wait_timeout',
                'wait_timeout',
                'interactive_timeout',
                'max_connections',
                'innodb_buffer_pool_size',
                'transaction_isolation',
                'tmpdir',
                'tmp_table_size',
                'max_heap_table_size'
            ]
            
            for var_name in important_vars:
                try:
                    result = conn.execute(text(f"SHOW VARIABLES LIKE '{var_name}'"))
                    row = result.fetchone()
                    if row:
                        value = row[1]
                        # Formázás nagy számokhoz
                        if 'size' in var_name and value.isdigit():
                            value_int = int(value)
                            if value_int > 1024 * 1024:
                                value = f"{value_int / 1024 / 1024:.2f} MB"
                            elif value_int > 1024:
                                value = f"{value_int / 1024:.2f} KB"
                        print(f"   {var_name}: {value}")
                except Exception as e:
                    print(f"   {var_name}: Nem elérhető ({e})")
        
        # Kapcsolati pool állapot
        print(f"\n10. KAPCSOLATI POOL ÁLLAPOT:")
        print(f"   Pool size: {engine.pool.size()}")
        print(f"   Checked out: {engine.pool.checkedout()}")
        print(f"   Overflow: {engine.pool.overflow()}")
        print(f"   Checked in: {engine.pool.checkedin()}")
        
        # /tmp könyvtár ellenőrzése
        print(f"\n11. /TMP KÖNYVTÁR ÁLLAPOTA:")
        try:
            with engine.connect() as conn:
                # Próbáljuk meg lekérdezni a tmpdir változót
                result = conn.execute(text("SHOW VARIABLES LIKE 'tmpdir'"))
                tmpdir_row = result.fetchone()
                if tmpdir_row:
                    tmpdir = tmpdir_row[1]
                    print(f"   Tmpdir: {tmpdir}")
                    print(f"   ⚠⚠⚠ FIGYELEM: Ha a /tmp könyvtár tele van, a MySQL nem tud működni!")
                    print(f"   Ellenőrizd a szerveren: df -h {tmpdir}")
        except Exception as e:
            print(f"   ⚠ Nem sikerült lekérdezni: {e}")
        
        # Ajánlások
        print(f"\n12. AJÁNLÁSOK ÉS MEGOLDÁSOK:")
        with engine.connect() as conn:
            # Lejárt session-ök törlése
            result = conn.execute(text("""
                SELECT COUNT(*) as count
                FROM user_sessions
                WHERE expires_at <= NOW()
            """))
            expired_count = result.fetchone()[0]
            
            if expired_count > 100:
                print(f"   ⚠ {expired_count} lejárt session van. Érdemes lehet törölni őket.")
                print(f"   SQL: DELETE FROM user_sessions WHERE expires_at <= NOW();")
            
            # Lock timeout ellenőrzés
            result = conn.execute(text("SHOW VARIABLES LIKE 'innodb_lock_wait_timeout'"))
            lock_timeout = result.fetchone()[1]
            if int(lock_timeout) < 50:
                print(f"   ⚠ Az innodb_lock_wait_timeout ({lock_timeout}s) alacsony lehet.")
                print(f"   Érdemes lehet növelni: SET GLOBAL innodb_lock_wait_timeout = 50;")
        
        print(f"\n   ⚠⚠⚠ KRITIKUS PROBLÉMA AZONOSÍTVA:")
        print(f"   A '/tmp/#sql1_12ba_0' tábla tele van hiba azt jelzi, hogy:")
        print(f"   1. A MySQL szerver /tmp könyvtára tele van")
        print(f"   2. Ez megakadályozza az ideiglenes táblák létrehozását")
        print(f"   3. Ez okozza a login lefagyását")
        print(f"\n   MEGOLDÁSOK:")
        print(f"   1. Szabadítsd fel a /tmp könyvtárat a szerveren:")
        print(f"      ssh szerver")
        print(f"      df -h /tmp  # Ellenőrizd a lemezterületet")
        print(f"      ls -lah /tmp | head -20  # Nézd meg mi foglalja")
        print(f"      rm -rf /tmp/*  # Töröld az ideiglenes fájlokat (ÓVATOSAN!)")
        print(f"\n   2. Vagy állítsd be egy másik tmpdir-t:")
        print(f"      SET GLOBAL tmpdir = '/var/tmp';")
        print(f"\n   3. Növeld a tmp_table_size-t:")
        print(f"      SET GLOBAL tmp_table_size = 256*1024*1024;  # 256MB")
        print(f"      SET GLOBAL max_heap_table_size = 256*1024*1024;  # 256MB")
        
        print("\n" + "=" * 80)
        print("DIAGNOSZTIKA BEFEJEZVE")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n✗ HIBA: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_mysql_status()

