"""
MySQL kapcsolat tesztelése SSH tunnel-lal
Ez a script létrehoz egy SSH tunnel-t és teszteli a MySQL kapcsolatot
"""

import subprocess
import sys
import os
import time
import signal

# Projekt root hozzáadása a path-hoz
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.app_config import get_database_config
from database.connection import recreate_engine
from sqlalchemy import text

SSH_KEY = os.path.expanduser("~/.ssh/zedhosting_server")
SERVER_HOST = "116.203.226.140"
SSH_USER = "root"
LOCAL_PORT = 3307
REMOTE_HOST = "116.203.226.140"  # Lehet localhost is, ha a MySQL ugyanazon a gépen van
REMOTE_PORT = 3306

def start_ssh_tunnel():
    """SSH tunnel indítása háttérben"""
    print(f"[INFO] SSH tunnel inditasa...")
    print(f"  Lokalis port: {LOCAL_PORT}")
    print(f"  Tavoli szerver: {REMOTE_HOST}:{REMOTE_PORT}")
    
    ssh_cmd = [
        "ssh",
        "-i", SSH_KEY,
        "-o", "StrictHostKeyChecking=no",
        "-o", "ConnectTimeout=10",
        "-L", f"{LOCAL_PORT}:{REMOTE_HOST}:{REMOTE_PORT}",
        "-N",  # Ne futtasson parancsot, csak tunnel
        "-f",  # Háttérben futtatás
        f"{SSH_USER}@{SERVER_HOST}"
    ]
    
    try:
        result = subprocess.run(
            ssh_cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print(f"[OK] SSH tunnel elinditva")
            print(f"  A tunnel a {LOCAL_PORT} porton hallgat")
            return True
        else:
            print(f"[ERROR] SSH tunnel inditas sikertelen")
            print(f"  STDOUT: {result.stdout}")
            print(f"  STDERR: {result.stderr}")
            return False
    except Exception as e:
        print(f"[ERROR] SSH tunnel hiba: {e}")
        return False

def stop_ssh_tunnel():
    """SSH tunnel leállítása"""
    print(f"\n[INFO] SSH tunnel leallitasa...")
    try:
        # Keresd meg az SSH tunnel folyamatot
        result = subprocess.run(
            ["powershell", "-Command", f"Get-Process | Where-Object {{$_.CommandLine -like '*ssh*{LOCAL_PORT}*'}} | Stop-Process -Force"],
            capture_output=True,
            text=True
        )
        print(f"[OK] SSH tunnel leallitva")
    except Exception as e:
        print(f"[WARN] SSH tunnel leallitas: {e}")
        print(f"  Manuálisan állítsd le: Get-Process | Where-Object {{$_.CommandLine -like '*ssh*'}} | Stop-Process")

def test_mysql_connection():
    """MySQL kapcsolat tesztelése localhost-on keresztül"""
    print(f"\n[INFO] MySQL kapcsolat tesztelese...")
    print(f"  Host: 127.0.0.1")
    print(f"  Port: {LOCAL_PORT}")
    
    # Ideiglenesen módosítsd a konfigurációt
    original_config = get_database_config("production")
    
    # Hozz létre egy új engine-t localhost-tal
    try:
        from sqlalchemy import create_engine
        from urllib.parse import quote_plus
        
        config = get_database_config("production")
        encoded_password = quote_plus(config["password"])
        local_url = f"mysql+pymysql://{config['user']}:{encoded_password}@127.0.0.1:{LOCAL_PORT}/{config['database']}"
        
        print(f"  Connection URL: mysql+pymysql://{config['user']}:***@127.0.0.1:{LOCAL_PORT}/{config['database']}")
        
        test_engine = create_engine(
            local_url,
            pool_pre_ping=True,
            connect_args={
                "connect_timeout": 5,
                "read_timeout": 10,
                "write_timeout": 10,
            }
        )
        
        # Várj egy kicsit, hogy a tunnel létrejöjjön
        time.sleep(2)
        
        with test_engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test, VERSION() as version"))
            row = result.fetchone()
            if row and row[0] == 1:
                print(f"[OK] MySQL kapcsolat mukodik!")
                print(f"  MySQL verzio: {row[1]}")
                
                # További teszt
                result = conn.execute(text("SELECT DATABASE() as current_db"))
                db = result.fetchone()[0]
                print(f"  Aktualis adatbazis: {db}")
                
                return True
            else:
                print(f"[ERROR] MySQL kapcsolat nem mukodik megfeleloen")
                return False
                
    except Exception as e:
        print(f"[ERROR] MySQL kapcsolat hiba: {e}")
        return False
    finally:
        test_engine.dispose()

def main():
    """Fő függvény"""
    print("="*80)
    print("MYSQL KAPCSOLAT TESZTELESE SSH TUNNEL-LAL")
    print("="*80)
    
    # SSH kulcs ellenőrzése
    if not os.path.exists(SSH_KEY):
        print(f"[ERROR] SSH kulcs nem talalhato: {SSH_KEY}")
        return False
    
    print(f"[OK] SSH kulcs talalhato: {SSH_KEY}")
    
    # SSH tunnel indítása
    if not start_ssh_tunnel():
        print("\n[INFO] Probald meg manualisan inditani az SSH tunnel-t:")
        print(f"  ssh -i {SSH_KEY} -L {LOCAL_PORT}:{REMOTE_HOST}:{REMOTE_PORT} -N {SSH_USER}@{SERVER_HOST}")
        return False
    
    try:
        # MySQL kapcsolat tesztelése
        if test_mysql_connection():
            print("\n" + "="*80)
            print("[SUCCESS] MySQL kapcsolat sikeresen mukodik SSH tunnel-lal!")
            print("="*80)
            print("\nHasznalati utmutato:")
            print("1. Inditsd el az SSH tunnel-t egy terminalban:")
            print(f"   ssh -i {SSH_KEY} -L {LOCAL_PORT}:{REMOTE_HOST}:{REMOTE_PORT} -N {SSH_USER}@{SERVER_HOST}")
            print("\n2. Modositsd a konfiguraciot (app_config.py vagy .env):")
            print(f"   DB_PROD_HOST=127.0.0.1")
            print(f"   DB_PROD_PORT={LOCAL_PORT}")
            print("\n3. Az alkalmazas most mar elerheti a MySQL-t!")
            return True
        else:
            print("\n[ERROR] MySQL kapcsolat nem mukodik")
            return False
    finally:
        # SSH tunnel leállítása (opcionális)
        # stop_ssh_tunnel()  # Kommenteld ki, ha szeretnéd megtartani a tunnel-t

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n[INFO] Megszakitva")
        stop_ssh_tunnel()
        sys.exit(1)




