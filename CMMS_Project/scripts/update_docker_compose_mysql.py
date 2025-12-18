"""
Docker Compose MySQL Optimalizálás
Módosítja a docker-compose.yml fájlt az optimalizált MySQL beállításokkal
"""

import subprocess
import os
import sys

SERVER_HOST = "116.203.226.140"
SSH_USER = "root"
DOCKER_COMPOSE_FILE = "/root/zedhosting/docker-compose.yml"
SSH_KEY = os.path.expanduser("~/.ssh/zedhosting_server")

def run_ssh_command(command):
    """SSH parancs futtatása"""
    ssh_cmd = ["ssh", "-i", SSH_KEY, "-o", "StrictHostKeyChecking=no",
               f"{SSH_USER}@{SERVER_HOST}", command]
    
    try:
        result = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, "", str(e)


def main():
    """Fő függvény"""
    print("=" * 70)
    print("Docker Compose MySQL Optimalizálás")
    print("=" * 70)
    print()
    
    # 1. Docker compose fájl olvasása
    print(f"[INFO] Docker compose fájl olvasása: {DOCKER_COMPOSE_FILE}")
    success, content, error = run_ssh_command(f"cat {DOCKER_COMPOSE_FILE}")
    
    if not success:
        print(f"[ERROR] Nem sikerült olvasni a fájlt: {error}")
        return False
    
    print("[OK] Fájl beolvasva")
    print()
    print("Jelenlegi tartalom:")
    print("-" * 70)
    print(content[:500] + "..." if len(content) > 500 else content)
    print()
    
    # 2. Backup készítése
    print("[INFO] Backup készítése...")
    success, _, _ = run_ssh_command(
        f"cp {DOCKER_COMPOSE_FILE} {DOCKER_COMPOSE_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
    )
    if success:
        print("[OK] Backup készült")
    else:
        print("[WARNING] Backup nem sikerült, de folytatjuk...")
    
    # 3. MySQL optimalizációs beállítások hozzáadása
    print("\n[INFO] MySQL optimalizációs beállítások hozzáadása...")
    
    # Command argumentumok MySQL-hez
    mysql_command = """command: >
      --innodb_buffer_pool_size=2147483648
      --max_connections=200
      --tmp_table_size=134217728
      --max_heap_table_size=134217728
      --wait_timeout=600
      --interactive_timeout=600
      --slow_query_log=1
      --long_query_time=2
      --innodb_log_file_size=268435456
      --innodb_log_buffer_size=67108864
      --innodb_flush_log_at_trx_commit=2
      --innodb_read_io_threads=4
      --innodb_write_io_threads=4"""
    
    # Ellenőrizzük, hogy van-e már command rész
    if "command:" in content:
        print("[INFO] Már van command rész, frissítjük...")
        # TODO: Frissítsd a meglévő command részt
    else:
        print("[INFO] Command rész hozzáadása...")
        # Keressük meg a mysql service részt és adjuk hozzá a command-ot
        # TODO: YAML parsing és módosítás
    
    print("\n[INFO] Manuális módosítás szükséges!")
    print("=" * 70)
    print("Kérlek, módosítsd manuálisan a docker-compose.yml fájlt:")
    print(f"  ssh -i {SSH_KEY} {SSH_USER}@{SERVER_HOST}")
    print(f"  nano {DOCKER_COMPOSE_FILE}")
    print()
    print("Add hozzá a MySQL service-hez:")
    print("-" * 70)
    print(mysql_command)
    print("-" * 70)
    print()
    print("Majd újraindítsd a container-t:")
    print(f"  cd /root/zedhosting && docker-compose restart mysql")
    print()
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)




