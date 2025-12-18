"""
MySQL Optimalizálás Docker Container-ben - Biztonságos Módszer
Docker container-ben a MySQL változókat dinamikusan állítja be (nem kell újraindítás)
"""

import subprocess
import os
import sys
import time

SERVER_HOST = "116.203.226.140"
SSH_USER = "root"
DOCKER_CONTAINER = "zed-mysql"
SSH_KEY = os.path.expanduser("~/.ssh/zedhosting_server")

def run_ssh_command(command, description=""):
    """SSH parancs futtatása"""
    ssh_cmd = ["ssh", "-i", SSH_KEY, "-o", "StrictHostKeyChecking=no",
               "-o", "ConnectTimeout=10", f"{SSH_USER}@{SERVER_HOST}", command]
    
    try:
        result = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            return False, result.stderr.strip()
    except Exception as e:
        return False, str(e)


def check_container_running():
    """Ellenőrzi, hogy a container fut-e"""
    success, output = run_ssh_command(
        f"docker ps --filter name={DOCKER_CONTAINER} --format '{{{{.Status}}}}'",
        "Container állapot ellenőrzése"
    )
    
    if success and "Up" in output:
        return True
    return False


def wait_for_mysql():
    """Vár, amíg a MySQL elindul"""
    print("[INFO] Várakozás a MySQL elindulására...")
    for i in range(30):  # Max 30 másodperc
        success, output = run_ssh_command(
            f"docker exec {DOCKER_CONTAINER} mysqladmin ping -u zedin_cmms -p'Gele007ta...' 2>&1",
            "MySQL ping"
        )
        if success and "mysqld is alive" in output:
            print("[OK] MySQL elindult")
            return True
        time.sleep(1)
    print("[WARNING] MySQL nem indult el 30 másodpercen belül")
    return False


def set_mysql_variable(var_name, value, description=""):
    """MySQL változó beállítása"""
    # Próbáljuk meg root-tal (ha nincs jelszó)
    commands = [
        f"docker exec {DOCKER_CONTAINER} mysql -u root -e \"SET GLOBAL {var_name} = {value};\" 2>&1",
        f"docker exec {DOCKER_CONTAINER} mysql -u zedin_cmms -p'Gele007ta...' zedin_cmms -e \"SET GLOBAL {var_name} = {value};\" 2>&1",
    ]
    
    for cmd in commands:
        success, output = run_ssh_command(cmd, f"{description or var_name} beállítása")
        if success and "ERROR" not in output.upper():
            return True
    
    return False


def verify_mysql_variable(var_name):
    """MySQL változó ellenőrzése"""
    success, output = run_ssh_command(
        f"docker exec {DOCKER_CONTAINER} mysql -u zedin_cmms -p'Gele007ta...' zedin_cmms -e \"SHOW VARIABLES LIKE '{var_name}';\" 2>&1",
        f"{var_name} ellenőrzése"
    )
    
    if success:
        lines = output.split('\n')
        for line in lines:
            if var_name in line:
                return line.strip()
    return None


def main():
    """Fő függvény"""
    print("=" * 70)
    print("MySQL Optimalizálás Docker Container-ben")
    print("=" * 70)
    print()
    
    # 1. Container ellenőrzése
    if not check_container_running():
        print("[ERROR] Container nem fut!")
        print("Indítsd el a container-t:")
        print(f"  ssh -i {SSH_KEY} {SSH_USER}@{SERVER_HOST} 'docker start {DOCKER_CONTAINER}'")
        return False
    
    print("[OK] Container fut")
    
    # 2. MySQL elindulásának várása
    if not wait_for_mysql():
        return False
    
    # 3. Optimalizált változók beállítása
    print("\n[INFO] MySQL változók beállítása...")
    print("-" * 70)
    
    # Fontos változók (értékek byte-ban)
    variables = {
        "innodb_buffer_pool_size": "2147483648",  # 2GB
        "max_connections": "200",
        "tmp_table_size": "134217728",  # 128MB
        "max_heap_table_size": "134217728",  # 128MB
        "wait_timeout": "600",
        "interactive_timeout": "600",
        "slow_query_log": "1",
        "long_query_time": "2",
    }
    
    results = {}
    
    for var_name, value in variables.items():
        success = set_mysql_variable(
            var_name, 
            value,
            f"{var_name} = {value}"
        )
        results[var_name] = success
        
        if success:
            print(f"[OK] {var_name} = {value}")
        else:
            print(f"[WARNING] {var_name} beállítása sikertelen")
    
    # 4. Ellenőrzés
    print("\n[INFO] Változók ellenőrzése...")
    print("-" * 70)
    
    for var_name in variables.keys():
        value = verify_mysql_variable(var_name)
        if value:
            print(f"  {value}")
        else:
            print(f"  {var_name}: [Nem sikerült lekérdezni]")
    
    # 5. Összefoglaló
    print("\n" + "=" * 70)
    successful = sum(1 for v in results.values() if v)
    total = len(results)
    
    if successful == total:
        print(f"[OK] Minden változó sikeresen beállítva ({successful}/{total})")
    else:
        print(f"[WARNING] {successful}/{total} változó lett beállítva")
        print("Néhány változó csak root jogosultsággal állítható be.")
    
    print("=" * 70)
    print()
    print("FONTOS: Ezek a változók csak addig érvényesek, amíg a container fut.")
    print("Végleges beállításhoz módosítsd a docker-compose.yml fájlt vagy")
    print("a MySQL konfigurációs fájlt a container-ben.")
    print()
    
    return successful > 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)




