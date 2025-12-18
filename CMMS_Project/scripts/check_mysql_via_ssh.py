"""
MySQL kapcsolat ellenőrzése SSH-n keresztül
Ellenőrzi a MySQL szerver állapotát a távoli szerveren
"""

import subprocess
import sys
import os

# Projekt root hozzáadása a path-hoz
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.app_config import get_database_config

SERVER_HOST = "116.203.226.140"
SSH_USER = "root"

# SSH kulcs útvonalak próbálkozása
SSH_KEY_PATHS = [
    os.path.expanduser("~/.ssh/zedhosting_server"),
    os.path.expanduser("~/.ssh/id_rsa_zedin"),
    os.path.expanduser("~/.ssh/zedhosting_server_ai2"),
    os.path.expanduser("~/.ssh/id_ed25519"),
    os.path.expanduser("~/.ssh/id_rsa"),
]

def find_ssh_key():
    """Megkeresi az elérhető SSH kulcsot"""
    for key_path in SSH_KEY_PATHS:
        if os.path.exists(key_path):
            return key_path
    return None

def run_ssh_command(command, description):
    """SSH parancs futtatása a szerveren"""
    print(f"\n{'='*80}")
    print(f"{description}")
    print(f"{'='*80}")
    
    ssh_key = find_ssh_key()
    
    ssh_cmd = ["ssh"]
    if ssh_key:
        ssh_cmd.extend(["-i", ssh_key])
    
    ssh_cmd.extend([
        "-o", "StrictHostKeyChecking=no",
        "-o", "ConnectTimeout=10",
        f"{SSH_USER}@{SERVER_HOST}",
        command
    ])
    
    try:
        result = subprocess.run(
            ssh_cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.stdout:
            print(result.stdout)
        if result.stderr and result.returncode != 0:
            print(f"STDERR: {result.stderr}", file=sys.stderr)
        
        return result.returncode == 0, result.stdout
    except subprocess.TimeoutExpired:
        print(f"[WARN] Timeout: A parancs tul sokig tartott")
        return False, ""
    except FileNotFoundError:
        print(f"[ERROR] SSH nem talalhato. Telepitsd az OpenSSH-t.")
        return False, ""
    except Exception as e:
        print(f"[ERROR] Hiba: {e}")
        return False, ""

def check_mysql_via_ssh():
    """MySQL állapot ellenőrzése SSH-n keresztül"""
    print("="*80)
    print("MYSQL KAPCSOLAT ELLENŐRZÉSE SSH-N KERESZTÜL")
    print("="*80)
    
    config = get_database_config("production")
    print(f"\nKonfiguráció:")
    print(f"  Host: {config['host']}")
    print(f"  Port: {config['port']}")
    print(f"  Database: {config['database']}")
    print(f"  User: {config['user']}")
    
    ssh_key = find_ssh_key()
    if ssh_key:
        print(f"\n[OK] SSH kulcs talalhato: {ssh_key}")
    else:
        print(f"\n[WARN] SSH kulcs nem talalhato, jelszo szukseges lehet")
    
    # 1. SSH kapcsolat tesztelése
    print("\n1. SSH KAPCSOLAT TESZTELÉSE...")
    success, output = run_ssh_command("echo 'SSH connection successful'", "SSH kapcsolat teszt")
    if not success:
        print("[WARN] SSH kapcsolat nem mukodik. Probald meg manualisan:")
        print(f"   ssh {SSH_USER}@{SERVER_HOST}")
        return False
    
    # 2. MySQL szolgáltatás állapota
    print("\n2. MYSQL SZOLGÁLTATÁS ÁLLAPOTA...")
    run_ssh_command("systemctl status mysql --no-pager -l || service mysql status", "MySQL szolgáltatás állapot")
    
    # 3. MySQL folyamat ellenőrzése
    print("\n3. MYSQL FOLYAMAT ELLENŐRZÉSE...")
    run_ssh_command("ps aux | grep -E 'mysql|mysqld' | grep -v grep || echo 'Nincs MySQL folyamat'", "MySQL folyamatok")
    
    # 4. MySQL port ellenőrzése
    print("\n4. MYSQL PORT ELLENŐRZÉSE (3306)...")
    run_ssh_command("netstat -tulpn | grep 3306 || ss -tulpn | grep 3306 || echo 'Port 3306 nem hallható'", "MySQL port")
    
    # 5. MySQL kapcsolat tesztelése a szerveren
    print("\n5. MYSQL KAPCSOLAT TESZTELÉSE A SZERVEREN...")
    mysql_test_cmd = f"mysql -u {config['user']} -p'{config['password']}' {config['database']} -e 'SELECT 1 as test, VERSION() as version;' 2>&1"
    success, output = run_ssh_command(mysql_test_cmd, "MySQL kapcsolat teszt a szerveren")
    
    if success and "test" in output.lower():
        print("[OK] MySQL kapcsolat mukodik a szerveren!")
    else:
        print("[ERROR] MySQL kapcsolat nem mukodik a szerveren")
    
    # 6. /tmp könyvtár ellenőrzése
    print("\n6. /TMP KÖNYVTÁR ÁLLAPOTA...")
    run_ssh_command("df -h /tmp && echo '' && ls -lah /tmp | head -10", "/tmp könyvtár állapot")
    
    # 7. MySQL error log ellenőrzése
    print("\n7. MYSQL ERROR LOG (utolsó 20 sor)...")
    run_ssh_command("tail -20 /var/log/mysql/error.log 2>/dev/null || tail -20 /var/log/mysqld.log 2>/dev/null || echo 'Error log nem található'", "MySQL error log")
    
    # 8. Aktív MySQL kapcsolatok
    print("\n8. AKTÍV MYSQL KAPCSOLATOK...")
    mysql_connections_cmd = f"mysql -u {config['user']} -p'{config['password']}' -e 'SHOW PROCESSLIST;' 2>&1 | head -20"
    run_ssh_command(mysql_connections_cmd, "Aktív MySQL kapcsolatok")
    
    print("\n" + "="*80)
    print("ELLENŐRZÉS BEFEJEZVE")
    print("="*80)
    print("\nÖsszefoglalás:")
    print("  - Ha a MySQL szolgáltatás nem fut, indítsd el: systemctl start mysql")
    print("  - Ha a /tmp könyvtár tele van, szabadítsd fel")
    print("  - Ha a MySQL port nem hallható, ellenőrizd a tűzfal beállításokat")
    print("  - A MySQL csak localhost-on hallgathat, SSH tunnel szükséges lehet")

if __name__ == "__main__":
    check_mysql_via_ssh()

