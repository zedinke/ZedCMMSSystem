"""
MySQL Optimalizálás Alkalmazása SSH-n Keresztül
Automatikusan alkalmazza az optimalizált MySQL beállításokat a szerveren
"""

import subprocess
import sys
import os
from pathlib import Path

# Projekt root
PROJECT_ROOT = Path(__file__).parent.parent

# SSH beállítások
SERVER_HOST = "116.203.226.140"
SSH_USER = "root"
SSH_KEY_PATHS = [
    os.path.expanduser("~/.ssh/zedhosting_server"),
    os.path.expanduser("~/.ssh/id_rsa_zedin"),
    os.path.expanduser("~/.ssh/id_ed25519"),
    os.path.expanduser("~/.ssh/id_rsa"),
]

# MySQL konfigurációs fájl helyek (Docker és közvetlen telepítés)
MYSQL_CONFIG_PATHS = [
    "/etc/mysql/my.cnf",
    "/etc/my.cnf",
    "/etc/mysql/mysql.conf.d/mysqld.cnf",
]

# Docker container neve (ha Docker-ben fut)
DOCKER_CONTAINER = "zed-mysql"


def find_ssh_key():
    """Megkeresi az elérhető SSH kulcsot"""
    for key_path in SSH_KEY_PATHS:
        if os.path.exists(key_path):
            return key_path
    return None


def run_ssh_command(command, description=""):
    """SSH parancs futtatása a szerveren"""
    ssh_key = find_ssh_key()
    
    if not ssh_key:
        print(f"[ERROR] SSH kulcs nem található!")
        print(f"Keresett helyek:")
        for path in SSH_KEY_PATHS:
            print(f"  - {path}")
        return False, ""
    
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
        print(f"[INFO] {description}")
        result = subprocess.run(
            ssh_cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            return True, result.stdout
        else:
            print(f"[ERROR] Parancs sikertelen: {description}")
            print(f"  STDERR: {result.stderr}")
            return False, result.stderr
            
    except subprocess.TimeoutExpired:
        print(f"[ERROR] Timeout: {description}")
        return False, "Timeout"
    except Exception as e:
        print(f"[ERROR] Hiba: {e}")
        return False, str(e)


def check_docker_mysql():
    """Ellenőrzi, hogy Docker container-ben fut-e a MySQL"""
    success, output = run_ssh_command(
        f"docker ps --filter name={DOCKER_CONTAINER} --format '{{{{.Names}}}}'",
        "Docker container ellenőrzése"
    )
    
    if success and DOCKER_CONTAINER in output:
        return True
    return False


def get_mysql_config_path():
    """Megkeresi a MySQL konfigurációs fájl helyét"""
    # Docker esetén
    if check_docker_mysql():
        print("[INFO] MySQL Docker container-ben fut")
        # Docker container-ben a konfiguráció lehet:
        # 1. Bind mount-on keresztül
        # 2. Vagy a container-ben /etc/mysql/my.cnf
        return "docker"
    
    # Közvetlen telepítés esetén
    for config_path in MYSQL_CONFIG_PATHS:
        success, output = run_ssh_command(
            f"test -f {config_path} && echo 'exists' || echo 'not found'",
            f"Konfiguráció ellenőrzése: {config_path}"
        )
        if success and "exists" in output:
            return config_path
    
    return None


def backup_mysql_config(config_path):
    """Backup készítése a MySQL konfigról"""
    if config_path == "docker":
        # Docker esetén a konfiguráció lehet bind mount-on
        success, output = run_ssh_command(
            f"docker inspect {DOCKER_CONTAINER} --format '{{{{json .Mounts}}}}'",
            "Docker mount pontok ellenőrzése"
        )
        if success:
            print("[INFO] Docker container mount pontok:")
            print(output)
        return True
    
    # Közvetlen telepítés backup
    backup_path = f"{config_path}.backup.$(date +%Y%m%d_%H%M%S)"
    success, output = run_ssh_command(
        f"cp {config_path} {backup_path} && echo 'backup_ok'",
        f"Backup készítése: {config_path}"
    )
    
    if success and "backup_ok" in output:
        print(f"[OK] Backup készült: {backup_path}")
        return True
    else:
        print(f"[WARNING] Backup nem sikerült, de folytatjuk...")
        return False


def read_optimized_config():
    """Beolvassa az optimalizált konfigurációt"""
    config_file = PROJECT_ROOT / "installer" / "mysql_optimized_config.ini"
    
    if not config_file.exists():
        print(f"[ERROR] Optimalizált konfiguráció nem található: {config_file}")
        return None
    
    with open(config_file, 'r', encoding='utf-8') as f:
        return f.read()


def apply_config_docker():
    """Alkalmazza a konfigurációt Docker container-ben"""
    print("\n[INFO] Docker container optimalizálása...")
    
    # Docker container-ben a MySQL konfiguráció módosítása
    # Először nézzük meg a mount pontokat és a container konfigurációt
    success, mounts_output = run_ssh_command(
        f"docker inspect {DOCKER_CONTAINER} --format '{{{{json .Mounts}}}}'",
        "Docker mount pontok ellenőrzése"
    )
    
    if success and mounts_output:
        print("[INFO] Docker mount pontok:")
        print(mounts_output)
    
    # Olvasd be az optimalizált konfigurációt
    config_content = read_optimized_config()
    if not config_content:
        return False
    
    # Docker container-ben a MySQL konfiguráció helye
    # Általában: /etc/mysql/my.cnf vagy /etc/my.cnf
    # De lehet, hogy a volume-ban van: /var/lib/mysql
    
    # 1. Ellenőrizzük, hogy van-e my.cnf a container-ben
    success, config_check = run_ssh_command(
        f"docker exec {DOCKER_CONTAINER} ls -la /etc/mysql/my.cnf /etc/my.cnf 2>&1 | head -5",
        "MySQL konfigurációs fájl ellenőrzése"
    )
    
    # 2. Konfigurációs fájl létrehozása/módosítása a szerveren
    temp_config = "/tmp/mysql_optimized_config.cnf"
    
    # Fájl létrehozása a szerveren (sorokkal)
    print("[INFO] Optimalizált konfiguráció létrehozása a szerveren...")
    
    # Először töröljük a temp fájlt, ha létezik
    run_ssh_command(f"rm -f {temp_config}", "Temp fájl törlése")
    
    # Konfiguráció írása a szerverre (base64 encoding használata a biztonságos átvitelhez)
    import base64
    config_bytes = config_content.encode('utf-8')
    config_b64 = base64.b64encode(config_bytes).decode('ascii')
    
    # Base64 dekódolás és fájlba írás a szerveren
    success, output = run_ssh_command(
        f"echo '{config_b64}' | base64 -d > {temp_config}",
        "Konfiguráció létrehozása base64 dekódolással"
    )
    
    if not success:
        # Alternatíva: scp használata
        print("[INFO] Base64 módszer sikertelen, scp használata...")
        # Lokális temp fájl
        local_temp = PROJECT_ROOT / "temp_mysql_config.cnf"
        with open(local_temp, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        # Scp másolás
        ssh_key = find_ssh_key()
        scp_cmd = ["scp", "-i", ssh_key, "-o", "StrictHostKeyChecking=no",
                   str(local_temp), f"{SSH_USER}@{SERVER_HOST}:{temp_config}"]
        try:
            result = subprocess.run(scp_cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                success = True
            else:
                print(f"[ERROR] SCP sikertelen: {result.stderr}")
                success = False
        finally:
            if local_temp.exists():
                local_temp.unlink()
    
    # 3. Konfiguráció másolása Docker container-be
    print("[INFO] Konfiguráció másolása Docker container-be...")
    
    # Először backup a container-ben lévő konfigról
    run_ssh_command(
        f"docker exec {DOCKER_CONTAINER} sh -c 'cp /etc/mysql/my.cnf /etc/mysql/my.cnf.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null || cp /etc/my.cnf /etc/my.cnf.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null || echo backup_skipped'",
        "Container konfiguráció backup"
    )
    
    # Konfiguráció másolása
    success, output = run_ssh_command(
        f"docker cp {temp_config} {DOCKER_CONTAINER}:/etc/mysql/conf.d/optimized.cnf",
        "Konfiguráció másolása container-be"
    )
    
    if not success:
        # Alternatíva: közvetlenül a my.cnf-be
        print("[INFO] Alternatív módszer: my.cnf közvetlen módosítása...")
        success, output = run_ssh_command(
            f"docker cp {temp_config} {DOCKER_CONTAINER}:/etc/mysql/my.cnf",
            "Konfiguráció másolása my.cnf-be"
        )
    
    # 4. Container újraindítása
    print("\n[INFO] Container újraindítása...")
    success, output = run_ssh_command(
        f"docker restart {DOCKER_CONTAINER}",
        "Docker container újraindítása"
    )
    
    if success:
        print("[OK] Docker container újraindítva")
        # Várjunk, hogy a MySQL elinduljon
        import time
        print("[INFO] Várakozás a MySQL elindulására (10 másodperc)...")
        time.sleep(10)
        
        # Ellenőrzés
        success, status = run_ssh_command(
            f"docker ps --filter name={DOCKER_CONTAINER} --format '{{{{.Status}}}}'",
            "Container állapot ellenőrzése"
        )
        if success:
            print(f"[INFO] Container állapot: {status.strip()}")
        
        return True
    else:
        print("[ERROR] Docker container újraindítás sikertelen")
        return False


def apply_config_direct(config_path):
    """Alkalmazza a konfigurációt közvetlen telepítésnél"""
    print(f"\n[INFO] MySQL konfiguráció alkalmazása: {config_path}")
    
    # 1. Backup
    backup_mysql_config(config_path)
    
    # 2. Olvasd be az optimalizált konfigurációt
    config_content = read_optimized_config()
    if not config_content:
        return False
    
    # 3. Konfiguráció írása a szerverre
    # Ideiglenes fájl létrehozása lokálisan
    temp_local = PROJECT_ROOT / "temp_mysql_config.ini"
    with open(temp_local, 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    # Fájl másolása SSH-n keresztül
    ssh_key = find_ssh_key()
    scp_cmd = ["scp", "-i", ssh_key, "-o", "StrictHostKeyChecking=no", 
                str(temp_local), f"{SSH_USER}@{SERVER_HOST}:{config_path}"]
    
    try:
        result = subprocess.run(scp_cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            print(f"[ERROR] Konfiguráció másolása sikertelen")
            print(f"  STDERR: {result.stderr}")
            # Alternatíva: cat használata
            print("[INFO] Alternatív módszerrel próbálkozás...")
            config_lines = config_content.split('\n')
            for line in config_lines:
                if line.strip() and not line.strip().startswith(';'):
                    escaped_line = line.replace('"', '\\"').replace('$', '\\$')
                    run_ssh_command(
                        f'echo "{escaped_line}" >> {config_path}',
                        "Konfiguráció hozzáfűzése"
                    )
        else:
            print(f"[OK] Konfiguráció másolva: {config_path}")
    finally:
        # Temp fájl törlése
        if temp_local.exists():
            temp_local.unlink()
    
    # 4. MySQL újraindítása
    success, output = run_ssh_command(
        "systemctl restart mysql || service mysql restart",
        "MySQL újraindítása"
    )
    
    if success:
        print("[OK] MySQL újraindítva")
        return True
    else:
        print("[ERROR] MySQL újraindítás sikertelen")
        print(f"  Output: {output}")
        return False


def check_mysql_status():
    """Ellenőrzi a MySQL állapotot"""
    if check_docker_mysql():
        success, output = run_ssh_command(
            f"docker ps --filter name={DOCKER_CONTAINER} --format '{{{{.Status}}}}'",
            "Docker container állapot"
        )
        if success:
            print(f"[INFO] Container állapot: {output.strip()}")
    else:
        success, output = run_ssh_command(
            "systemctl status mysql --no-pager -l | head -10 || service mysql status",
            "MySQL szolgáltatás állapot"
        )
        if success:
            print(f"[INFO] MySQL állapot:\n{output}")


def main():
    """Fő függvény"""
    print("=" * 70)
    print("MySQL Optimalizálás Alkalmazása SSH-n Keresztül")
    print("=" * 70)
    print()
    
    # 1. SSH kulcs ellenőrzése
    ssh_key = find_ssh_key()
    if not ssh_key:
        print("[ERROR] SSH kulcs nem található!")
        print("Kérlek, helyezd el az SSH kulcsot az alábbi helyek egyikén:")
        for path in SSH_KEY_PATHS:
            print(f"  - {path}")
        return False
    
    print(f"[OK] SSH kulcs található: {ssh_key}")
    
    # 2. SSH kapcsolat tesztelése
    print("\n[INFO] SSH kapcsolat tesztelése...")
    success, output = run_ssh_command("echo 'SSH connection OK'", "SSH kapcsolat teszt")
    if not success:
        print("[ERROR] SSH kapcsolat nem működik!")
        print("Kérlek, teszteld manuálisan:")
        print(f"  ssh -i {ssh_key} {SSH_USER}@{SERVER_HOST}")
        return False
    
    print("[OK] SSH kapcsolat működik")
    
    # 3. MySQL konfiguráció helyének meghatározása
    print("\n[INFO] MySQL konfiguráció helyének meghatározása...")
    config_path = get_mysql_config_path()
    
    if config_path == "docker":
        print("[INFO] MySQL Docker container-ben fut")
        # Docker optimalizálás
        if apply_config_docker():
            print("\n[OK] Docker container optimalizálva!")
        else:
            print("\n[ERROR] Docker container optimalizálás sikertelen")
            return False
    elif config_path:
        print(f"[OK] MySQL konfiguráció található: {config_path}")
        # Közvetlen telepítés optimalizálás
        if apply_config_direct(config_path):
            print("\n[OK] MySQL konfiguráció alkalmazva!")
        else:
            print("\n[ERROR] Konfiguráció alkalmazás sikertelen")
            return False
    else:
        print("[ERROR] MySQL konfiguráció nem található!")
        print("Kérlek, ellenőrizd manuálisan a MySQL telepítést.")
        return False
    
    # 4. MySQL állapot ellenőrzése
    print("\n[INFO] MySQL állapot ellenőrzése...")
    check_mysql_status()
    
    # 5. Ellenőrzés az optimalizálási scripttel
    print("\n[INFO] Optimalizálás ellenőrzése...")
    print("Futtasd a következő parancsot az ellenőrzéshez:")
    print("  python utils/mysql_optimizer.py production")
    
    print("\n" + "=" * 70)
    print("[OK] MySQL optimalizálás alkalmazva!")
    print("=" * 70)
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

