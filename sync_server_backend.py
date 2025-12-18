#!/usr/bin/env python3
"""
Script to sync local backend files to server via SSH
"""
import subprocess
import sys
from pathlib import Path

# Server connection details
SSH_KEY = Path.home() / ".ssh" / "zedhosting_server"
SERVER = "root@116.203.226.140"
SERVER_PATH = "/opt/cmms-backend"

# Files to sync
FILES_TO_SYNC = [
    "CMMS_Project/api/routers/auth.py",
    "CMMS_Project/api/routers/machines.py",
    "CMMS_Project/api/routers/worksheets.py",
    "CMMS_Project/api/routers/users.py",
    "CMMS_Project/api/routers/assets.py",
    "CMMS_Project/api/routers/health.py",
    "CMMS_Project/api/routers/permissions.py",
    "CMMS_Project/api/app.py",
    "CMMS_Project/api/server.py",
    "CMMS_Project/api/schemas.py",
    "CMMS_Project/api/security.py",
    "CMMS_Project/api/dependencies.py",
    "CMMS_Project/api/routers/__init__.py",
]

def sync_file(local_path, server_path):
    """Sync a single file to server"""
    print(f"Syncing {local_path} -> {server_path}...")
    try:
        # Read local file
        with open(local_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Write to server via SSH
        cmd = [
            "ssh",
            "-i", str(SSH_KEY),
            SERVER,
            f"cat > {server_path}"
        ]
        
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate(input=content)
        
        if process.returncode != 0:
            print(f"Error syncing {local_path}: {stderr}")
            return False
        
        print(f"✓ Synced {local_path}")
        return True
    except Exception as e:
        print(f"Error syncing {local_path}: {e}")
        return False

def main():
    """Main sync function"""
    print("Starting server backend sync...")
    print(f"SSH Key: {SSH_KEY}")
    print(f"Server: {SERVER}")
    print(f"Server Path: {SERVER_PATH}")
    print()
    
    success_count = 0
    fail_count = 0
    
    for local_file in FILES_TO_SYNC:
        local_path = Path(local_file)
        if not local_path.exists():
            print(f"⚠ Local file not found: {local_path}")
            fail_count += 1
            continue
        
        # Determine server path
        if "routers" in local_file:
            server_file = f"{SERVER_PATH}/api/routers/{local_path.name}"
        else:
            server_file = f"{SERVER_PATH}/api/{local_path.name}"
        
        if sync_file(local_path, server_file):
            success_count += 1
        else:
            fail_count += 1
    
    print()
    print(f"Sync complete: {success_count} succeeded, {fail_count} failed")

if __name__ == "__main__":
    main()

