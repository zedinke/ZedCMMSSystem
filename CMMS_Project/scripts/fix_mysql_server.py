"""
MySQL szerver javítás SSH-n keresztül
Kapcsolódik a szerverhez és javítja a MySQL problémákat
"""

import subprocess
import sys
import os

SERVER_HOST = "116.203.226.140"
# Próbáld meg a zedin kulcsot először, ha nincs, akkor az ed25519-t
SSH_KEY_PATH = os.path.expanduser("~/.ssh/id_rsa_zedin")
if not os.path.exists(SSH_KEY_PATH):
    SSH_KEY_PATH = os.path.expanduser("~/.ssh/id_ed25519")

def run_ssh_command(command, description):
    """SSH parancs futtatása a szerveren"""
    print(f"\n{'='*80}")
    print(f"{description}")
    print(f"{'='*80}")
    
    ssh_cmd = [
        "ssh",
        "-i", SSH_KEY_PATH,
        "-o", "StrictHostKeyChecking=no",
        "-o", "ConnectTimeout=10",
        f"root@{SERVER_HOST}",
        command
    ]
    
    try:
        result = subprocess.run(
            ssh_cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"STDERR: {result.stderr}")
        
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"⚠ Timeout: A parancs túl sokáig tartott")
        return False
    except FileNotFoundError:
        print(f"✗ SSH nem található. Telepítsd az OpenSSH-t.")
        return False
    except Exception as e:
        print(f"✗ Hiba: {e}")
        return False

def fix_mysql_server():
    """Javítja a MySQL szerver problémáit"""
    print("="*80)
    print("MYSQL SZERVER JAVÍTÁS SSH-N KERESZTÜL")
    print("="*80)
    
    # 1. Ellenőrizd az SSH kulcsot
    if not os.path.exists(SSH_KEY_PATH):
        print(f"\n✗ SSH kulcs nem található: {SSH_KEY_PATH}")
        print("Kérlek, hozd létre az SSH kulcsot először:")
        print(f"  ssh-keygen -t ed25519 -f {SSH_KEY_PATH}")
        return False
    
    print(f"\n✓ SSH kulcs található: {SSH_KEY_PATH}")
    
    # 2. Kapcsolat tesztelése
    print("\n1. KAPCSOLAT TESZTELÉSE...")
    if not run_ssh_command("echo 'SSH connection successful'", "Kapcsolat teszt"):
        print("\n⚠ SSH kapcsolat nem működik jelszó nélkül.")
        print("Próbáljuk meg jelszóval vagy használjuk a MySQL-t közvetlenül.")
        print("\nFolytatás MySQL-lel...")
        # Ne álljunk meg, próbáljuk meg MySQL-lel
    
    # 3. MySQL újraindítása SSH-n keresztül (ha lehetséges)
    print("\n2. MYSQL ÚJRAINDÍTÁSA SSH-N KERESZTÜL...")
    print("   (Ha SSH nem működik, kérlek futtasd manuálisan a szerveren:)")
    print("   systemctl restart mysql")
    run_ssh_command("systemctl restart mysql && echo 'MySQL újraindítva' || echo 'MySQL újraindítás sikertelen vagy nincs jogosultság'", "MySQL újraindítás")
    
    # 4. /tmp könyvtár felszabadítása SSH-n keresztül
    print("\n3. /TMP KÖNYVTÁR FELSZABADÍTÁSA SSH-N KERESZTÜL...")
    print("   ⚠⚠⚠ KRITIKUS LÉPÉS - Ez törölni fogja a /tmp könyvtár tartalmát!")
    print("   Ha SSH nem működik, futtasd manuálisan:")
    print("   systemctl stop mysql")
    print("   rm -rf /tmp/*")
    print("   systemctl start mysql")
    
    response = input("\n⚠ Folytatod az automatikus /tmp felszabadítást? (i/n): ")
    if response.lower() == 'i':
        run_ssh_command("systemctl stop mysql && rm -rf /tmp/* && systemctl start mysql && echo '✓ Tmp könyvtár felszabadítva és MySQL újraindítva' || echo '✗ Hiba történt'", "Tmp felszabadítás")
    else:
        print("   Kihagyva - kérlek futtasd manuálisan!")
    
    # 5. Várakozás MySQL újraindulására
    print("\n4. VÁRAKOZÁS MYSQL ÚJRAINDULÁSÁRA...")
    import time
    for i in range(10):
        print(f"   Várakozás... ({i+1}/10)")
        time.sleep(2)
        try:
            from database.connection import recreate_engine
            recreate_engine("production")
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("   ✓ MySQL elérhető!")
            break
        except:
            continue
    else:
        print("   ⚠ MySQL még nem elérhető, próbáld meg később")
    
    print("\n" + "="*80)
    print("JAVÍTÁS BEFEJEZVE")
    print("="*80)
    print("\nKérlek, teszteld a login-t most!")

if __name__ == "__main__":
    fix_mysql_server()

