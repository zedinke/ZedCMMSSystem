"""
Updater.exe - Standalone update application
Handles downloading and installing updates for CMMS.exe
"""

import sys
import os
import subprocess
import time
import tempfile
import shutil
import argparse
import logging
from pathlib import Path
from typing import Optional
import urllib.request
import urllib.error

# Setup logging
log_dir = Path(os.getenv('LOCALAPPDATA', os.path.expanduser('~/.local/share'))) / "ArtenceCMMS" / "data" / "logs"
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / "updater.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class Updater:
    """Main updater class"""
    
    def __init__(self):
        self.cmms_exe_name = "CMMS.exe"
        self.cmms_exe_path = None
        self.temp_dir = Path(tempfile.gettempdir()) / "ArtenceCMMS_Update"
        self.temp_dir.mkdir(exist_ok=True)
    
    def find_cmms_exe(self) -> Optional[Path]:
        """Find CMMS.exe installation path"""
        # Try common installation paths
        possible_paths = [
            Path(os.getenv("ProgramFiles", "C:\\Program Files")) / "ArtenceCMMS" / "CMMS.exe",
            Path(os.getenv("ProgramFiles(x86)", "C:\\Program Files (x86)")) / "ArtenceCMMS" / "CMMS.exe",
            Path(__file__).parent / "CMMS.exe",  # Same directory as updater
        ]
        
        for path in possible_paths:
            if path.exists():
                logger.info(f"Found CMMS.exe at: {path}")
                return path
        
        logger.error("CMMS.exe not found in standard locations")
        return None
    
    def close_cmms_exe(self, timeout: int = 10) -> bool:
        """
        Close CMMS.exe gracefully
        
        Args:
            timeout: Maximum time to wait for graceful shutdown
        
        Returns:
            True if closed successfully
        """
        logger.info("Attempting to close CMMS.exe...")
        
        # Find CMMS.exe process
        try:
            import psutil
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    if proc.info['name'] and proc.info['name'].lower() == 'cmms.exe':
                        processes.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            if not processes:
                logger.info("CMMS.exe is not running")
                return True
            
            # Try graceful shutdown first
            for proc in processes:
                try:
                    logger.info(f"Closing process {proc.info['pid']} gracefully...")
                    proc.terminate()
                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    logger.warning(f"Could not terminate process: {e}")
            
            # Wait for processes to exit
            start_time = time.time()
            while time.time() - start_time < timeout:
                still_running = [p for p in processes if p.is_running()]
                if not still_running:
                    logger.info("CMMS.exe closed successfully")
                    return True
                time.sleep(0.5)
            
            # Force kill if still running
            logger.warning("Force killing CMMS.exe processes...")
            for proc in processes:
                if proc.is_running():
                    try:
                        proc.kill()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
            
            # Wait a bit more
            time.sleep(1)
            still_running = [p for p in processes if p.is_running()]
            if still_running:
                logger.error("Failed to close all CMMS.exe processes")
                return False
            
            logger.info("CMMS.exe closed successfully (force kill)")
            return True
            
        except ImportError:
            logger.warning("psutil not available, using alternative method")
            # Fallback: use taskkill command
            try:
                result = subprocess.run(
                    ["taskkill", "/F", "/IM", self.cmms_exe_name],
                    capture_output=True,
                    timeout=timeout
                )
                if result.returncode == 0:
                    logger.info("CMMS.exe closed successfully (taskkill)")
                    return True
                elif "not found" in result.stdout.decode().lower():
                    logger.info("CMMS.exe is not running")
                    return True
                else:
                    logger.error(f"Failed to close CMMS.exe: {result.stderr.decode()}")
                    return False
            except Exception as e:
                logger.error(f"Error closing CMMS.exe: {e}")
                return False
    
    def download_installer(self, url: str, version: str) -> Optional[Path]:
        """
        Download installer from URL
        
        Args:
            url: Download URL
            version: Version string
        
        Returns:
            Path to downloaded installer or None
        """
        installer_filename = f"ArtenceCMMS_Setup_v{version}.exe"
        installer_path = self.temp_dir / installer_filename
        
        logger.info(f"Downloading installer from: {url}")
        logger.info(f"Save location: {installer_path}")
        
        try:
            # Download with progress
            def show_progress(block_num, block_size, total_size):
                if total_size > 0:
                    percent = min(100, (block_num * block_size * 100) // total_size)
                    if block_num % 10 == 0:  # Update every 10 blocks
                        logger.info(f"Download progress: {percent}%")
            
            urllib.request.urlretrieve(url, installer_path, show_progress)
            
            if installer_path.exists() and installer_path.stat().st_size > 0:
                logger.info(f"Download completed: {installer_path.stat().st_size / 1024 / 1024:.2f} MB")
                return installer_path
            else:
                logger.error("Downloaded file is empty or does not exist")
                return None
                
        except urllib.error.URLError as e:
            logger.error(f"Network error downloading installer: {e}")
            return None
        except Exception as e:
            logger.error(f"Error downloading installer: {e}", exc_info=True)
            return None
    
    def run_installer(self, installer_path: Path) -> bool:
        """
        Run installer in silent mode
        
        Args:
            installer_path: Path to installer executable
        
        Returns:
            True if installation succeeded
        """
        logger.info(f"Running installer: {installer_path}")
        
        try:
            # Run installer silently
            # /SILENT = silent mode with progress window
            # /VERYSILENT = very silent mode without progress window
            # /RESTARTAPPLICATIONS=0 = don't restart applications automatically
            result = subprocess.run(
                [str(installer_path), "/SILENT", "/RESTARTAPPLICATIONS=0"],
                timeout=300,  # 5 minute timeout
                capture_output=True
            )
            
            if result.returncode == 0:
                logger.info("Installation completed successfully")
                return True
            else:
                logger.error(f"Installation failed with return code: {result.returncode}")
                if result.stderr:
                    logger.error(f"Error output: {result.stderr.decode()}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Installation timed out")
            return False
        except Exception as e:
            logger.error(f"Error running installer: {e}", exc_info=True)
            return False
    
    def restart_cmms(self) -> bool:
        """
        Restart CMMS.exe
        
        Returns:
            True if started successfully
        """
        if not self.cmms_exe_path:
            self.cmms_exe_path = self.find_cmms_exe()
        
        if not self.cmms_exe_path or not self.cmms_exe_path.exists():
            logger.error("Cannot restart CMMS.exe: executable not found")
            return False
        
        logger.info(f"Restarting CMMS.exe: {self.cmms_exe_path}")
        
        try:
            # Start CMMS.exe in new process
            subprocess.Popen([str(self.cmms_exe_path)], cwd=self.cmms_exe_path.parent)
            logger.info("CMMS.exe started successfully")
            return True
        except Exception as e:
            logger.error(f"Error starting CMMS.exe: {e}", exc_info=True)
            return False
    
    def cleanup(self):
        """Clean up temporary files"""
        try:
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
                logger.info("Temporary files cleaned up")
        except Exception as e:
            logger.warning(f"Error cleaning up temporary files: {e}")
    
    def update(self, version: str, url: str, restart: bool = True) -> bool:
        """
        Main update process
        
        Args:
            version: Target version
            url: Download URL
            restart: Whether to restart CMMS.exe after update
        
        Returns:
            True if update succeeded
        """
        logger.info(f"Starting update process to version {version}")
        
        try:
            # Step 1: Close CMMS.exe
            if not self.close_cmms_exe():
                logger.error("Failed to close CMMS.exe. Update aborted.")
                return False
            
            # Step 2: Download installer
            installer_path = self.download_installer(url, version)
            if not installer_path:
                logger.error("Failed to download installer. Update aborted.")
                return False
            
            # Step 3: Run installer
            if not self.run_installer(installer_path):
                logger.error("Installation failed. Update aborted.")
                return False
            
            # Step 4: Cleanup
            self.cleanup()
            
            # Step 5: Restart CMMS.exe
            if restart:
                time.sleep(2)  # Wait a bit before restarting
                if not self.restart_cmms():
                    logger.warning("Update completed but failed to restart CMMS.exe")
                    return True  # Still consider update successful
            
            logger.info("Update completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Update process failed: {e}", exc_info=True)
            return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Artence CMMS Updater")
    parser.add_argument("--update", action="store_true", help="Run update process")
    parser.add_argument("--version", type=str, help="Target version")
    parser.add_argument("--url", type=str, help="Download URL")
    parser.add_argument("--restart", action="store_true", default=True, help="Restart CMMS.exe after update")
    parser.add_argument("--no-restart", dest="restart", action="store_false", help="Don't restart CMMS.exe")
    
    args = parser.parse_args()
    
    if not args.update:
        logger.error("--update flag is required")
        parser.print_help()
        sys.exit(1)
    
    if not args.version or not args.url:
        logger.error("--version and --url are required for update")
        parser.print_help()
        sys.exit(1)
    
    updater = Updater()
    success = updater.update(args.version, args.url, args.restart)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()




