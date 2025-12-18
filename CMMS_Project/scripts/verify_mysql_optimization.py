"""
MySQL Optimalizálás Ellenőrzése SSH-n Keresztül
"""

import subprocess
import os
import sys

SERVER_HOST = "116.203.226.140"
SSH_USER = "root"
DOCKER_CONTAINER = "zed-mysql"
SSH_KEY = os.path.expanduser("~/.ssh/zedhosting_server")

def run_ssh_command(command):
    """SSH parancs futtatása"""
    ssh_cmd = ["ssh", "-i", SSH_KEY, "-o", "StrictHostKeyChecking=no",
               f"{SSH_USER}@{SERVER_HOST}", command]
    
    try:
        result = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stdout.strip()
    except Exception as e:
        return False, str(e)


def check_mysql_variables():
    """MySQL változók ellenőrzése"""
    print("=" * 70)
    print("MySQL Optimalizálás Ellenőrzése")
    print("=" * 70)
    print()
    
    # Fontos változók
    variables = [
        "innodb_buffer_pool_size",
        "max_connections",
        "tmp_table_size",
        "max_heap_table_size",
        "wait_timeout",
        "slow_query_log",
        "long_query_time",
    ]
    
    print("MySQL Változók:")
    print("-" * 70)
    
    for var in variables:
        success, output = run_ssh_command(
            f"docker exec {DOCKER_CONTAINER} mysql -u zedin_cmms -p'Gele007ta...' zedin_cmms -e \"SHOW VARIABLES LIKE '{var}';\" 2>&1"
        )
        
        if success:
            lines = output.split('\n')
            for line in lines:
                if var in line:
                    print(f"  {line}")
        else:
            print(f"  {var}: [HIBA] Nem sikerült lekérdezni")
    
    print()
    
    # Container állapot
    print("Container Állapot:")
    print("-" * 70)
    success, output = run_ssh_command(
        f"docker ps --filter name={DOCKER_CONTAINER} --format '{{{{.Status}}}}'"
    )
    if success:
        print(f"  {output}")
    
    print()
    print("=" * 70)


if __name__ == "__main__":
    check_mysql_variables()




