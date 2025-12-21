"""
Update service for checking and downloading application updates from GitHub
"""

import os
import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path
import urllib.request
import urllib.error

from utils.version_utils import is_newer_version, normalize_version
from config.app_config import APP_VERSION

logger = logging.getLogger(__name__)


class UpdateInfo:
    """Information about an available update"""
    
    def __init__(self, version: str, download_url: str, release_date: str = None, 
                 changelog: str = None, critical: bool = False, min_supported_version: str = None):
        self.version = version
        self.download_url = download_url
        self.release_date = release_date
        self.changelog = changelog or ""
        self.critical = critical
        self.min_supported_version = min_supported_version
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "version": self.version,
            "download_url": self.download_url,
            "release_date": self.release_date,
            "changelog": self.changelog,
            "critical": self.critical,
            "min_supported_version": self.min_supported_version,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UpdateInfo':
        """Create from dictionary"""
        return cls(
            version=data.get("version", ""),
            download_url=data.get("download_url", ""),
            release_date=data.get("release_date"),
            changelog=data.get("changelog"),
            critical=data.get("critical", False),
            min_supported_version=data.get("min_supported_version"),
        )


class UpdateService:
    """Service for checking and managing updates"""
    
    def __init__(self, github_owner: str = None, github_repo: str = None):
        """
        Initialize update service
        
        Args:
            github_owner: GitHub repository owner (or from env/config)
            github_repo: GitHub repository name (or from env/config)
        """
        # Try to get from database settings first, then env vars, then parameter
        try:
            from services.settings_service import get_github_owner, get_github_repo
            db_owner = get_github_owner()
            db_repo = get_github_repo()
            
            self.github_owner = github_owner or db_owner or os.getenv("GITHUB_OWNER", "zedinke")
            self.github_repo = github_repo or db_repo or os.getenv("GITHUB_REPO", "ZedCMMSSystem")
        except Exception as e:
            logger.warning(f"Could not load GitHub settings from database: {e}")
            self.github_owner = github_owner or os.getenv("GITHUB_OWNER", "zedinke")
            self.github_repo = github_repo or os.getenv("GITHUB_REPO", "ZedCMMSSystem")
        
        # Normalize values: strip whitespace and check for empty strings
        if self.github_owner:
            self.github_owner = self.github_owner.strip()
        if self.github_repo:
            self.github_repo = self.github_repo.strip()
        
        # Validate configuration
        if not self.github_owner or not self.github_repo:
            logger.warning("GitHub owner/repo not configured. Update checking disabled.")
            logger.info(f"  Current config - owner: '{self.github_owner}', repo: '{self.github_repo}'")
            logger.info("  Configure GitHub settings in Settings → Updates section or set GITHUB_OWNER/GITHUB_REPO environment variables")
        else:
            logger.info(f"Update service initialized with GitHub: {self.github_owner}/{self.github_repo}")
        
        # Build URLs (even if config is invalid, for error messages)
        self.api_base_url = f"https://api.github.com/repos/{self.github_owner}/{self.github_repo}"
        self.releases_url = f"{self.api_base_url}/releases"
        self.latest_release_url = f"{self.releases_url}/latest"
    
    def reload_config(self):
        """Reload GitHub configuration from database"""
        try:
            from services.settings_service import get_github_owner, get_github_repo
            db_owner = get_github_owner()
            db_repo = get_github_repo()
            
            old_owner = self.github_owner
            old_repo = self.github_repo
            
            if db_owner:
                self.github_owner = db_owner.strip()
            if db_repo:
                self.github_repo = db_repo.strip()
            
            # Validate after reload
            if not self.github_owner or not self.github_repo:
                logger.warning("GitHub owner/repo not configured after reload. Update checking disabled.")
            elif old_owner != self.github_owner or old_repo != self.github_repo:
                logger.info(f"GitHub configuration reloaded: {self.github_owner}/{self.github_repo}")
            
            # Rebuild URLs
            self.api_base_url = f"https://api.github.com/repos/{self.github_owner}/{self.github_repo}"
            self.releases_url = f"{self.api_base_url}/releases"
            self.latest_release_url = f"{self.releases_url}/latest"
        except Exception as e:
            logger.warning(f"Could not reload GitHub settings: {e}", exc_info=True)
    
    def check_for_updates(self, current_version: str = None) -> Optional[UpdateInfo]:
        """
        Check for available updates from GitHub
        
        Args:
            current_version: Current application version (defaults to APP_VERSION)
        
        Returns:
            UpdateInfo if update is available, None otherwise
        """
        if not self.github_owner or not self.github_repo:
            logger.warning("Cannot check for updates: GitHub repository not configured")
            logger.info(f"  Please configure GitHub owner/repo in Settings → Updates section")
            logger.info(f"  Current values - owner: '{self.github_owner}', repo: '{self.github_repo}'")
            return None
        
        current_version = current_version or APP_VERSION
        logger.info(f"Checking for updates (current version: {current_version}, repo: {self.github_owner}/{self.github_repo})")
        
        try:
            # Fetch latest release from GitHub API
            latest_release = self._fetch_latest_release()
            if not latest_release:
                logger.warning("No release information available from GitHub")
                return None
            
            # Extract version from release tag
            tag_name = latest_release.get("tag_name", "")
            if not tag_name:
                logger.warning("Release tag_name is empty")
                return None
            
            latest_version = tag_name.lstrip("vV")
            latest_version = normalize_version(latest_version)
            
            logger.info(f"Latest version on GitHub: {latest_version} (from tag: {tag_name})")
            
            # Compare versions
            if not is_newer_version(latest_version, current_version):
                logger.info(f"Application is up to date (current: {current_version}, latest: {latest_version})")
                return None
            
            # Extract download URL from release assets
            print(f"[UPDATE] Extracting download URL from release assets...")
            download_url = self._extract_download_url(latest_release)
            if not download_url:
                print(f"[UPDATE] ERROR: No download URL found in release assets")
                print(f"[UPDATE]   Release has {len(latest_release.get('assets', []))} asset(s)")
                print(f"[UPDATE]   Release data keys: {list(latest_release.keys())}")
                if latest_release.get('assets'):
                    print(f"[UPDATE]   First asset keys: {list(latest_release['assets'][0].keys()) if latest_release['assets'] else 'No assets'}")
                logger.warning("No download URL found in release assets")
                logger.info(f"  Release has {len(latest_release.get('assets', []))} asset(s)")
                logger.info(f"  Release data keys: {list(latest_release.keys())}")
                if latest_release.get('assets'):
                    logger.info(f"  First asset keys: {list(latest_release['assets'][0].keys()) if latest_release['assets'] else 'No assets'}")
                return None
            print(f"[UPDATE] Download URL found: {download_url[:80]}...")
            
            # Extract additional information
            release_date = latest_release.get("published_at", "")
            changelog = latest_release.get("body", "")
            critical = latest_release.get("prerelease", False) == False and "critical" in changelog.lower()
            
            update_info = UpdateInfo(
                version=latest_version,
                download_url=download_url,
                release_date=release_date,
                changelog=changelog,
                critical=critical,
            )
            
            print(f"[UPDATE] SUCCESS: Update available: {latest_version}")
            print(f"[UPDATE] Download URL: {download_url[:80]}...")
            logger.info(f"Update available: {latest_version} (download URL: {download_url[:50]}...)")
            return update_info
            
        except urllib.error.URLError as e:
            print(f"[UPDATE] ERROR: Network error while checking for updates: {e}")
            logger.error(f"Network error while checking for updates: {e}")
            logger.debug(f"  URL attempted: {self.latest_release_url}", exc_info=True)
            return None
        except Exception as e:
            print(f"[UPDATE] ERROR: Exception while checking for updates: {e}")
            import traceback
            print(f"[UPDATE] Traceback: {traceback.format_exc()}")
            logger.error(f"Error checking for updates: {e}", exc_info=True)
            return None
    
    def _fetch_latest_release(self) -> Optional[Dict[str, Any]]:
        """
        Fetch latest release information from GitHub API
        Falls back to tags if no releases are found
        
        Returns:
            Release data dictionary or None
        """
        try:
            logger.debug(f"Fetching latest release from: {self.latest_release_url}")
            
            # Create request with User-Agent header (GitHub requires this)
            request = urllib.request.Request(
                self.latest_release_url,
                headers={
                    "User-Agent": "ArtenceCMMS-Updater/1.0",
                    "Accept": "application/vnd.github.v3+json",
                }
            )
            
            with urllib.request.urlopen(request, timeout=10) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    logger.debug(f"Successfully fetched release data (tag: {data.get('tag_name', 'N/A')})")
                    return data
                else:
                    logger.error(f"GitHub API returned status {response.status} (expected 200)")
                    return None
                    
        except urllib.error.HTTPError as e:
            if e.code == 404:
                logger.info(f"No releases found on GitHub (404 Not Found), trying tags instead")
                logger.info(f"  URL: {self.latest_release_url}")
                # Fallback to tags API
                return self._fetch_latest_tag()
            elif e.code == 403:
                logger.error(f"GitHub API access forbidden (403) - rate limit exceeded or repository is private")
                logger.info(f"  URL: {self.latest_release_url}")
            else:
                logger.error(f"HTTP error fetching release: {e.code} - {e.reason}")
                logger.info(f"  URL: {self.latest_release_url}")
            return None
        except urllib.error.URLError as e:
            logger.error(f"URL error fetching release: {e.reason}")
            logger.info(f"  URL: {self.latest_release_url}")
            logger.info(f"  Check internet connection and GitHub accessibility")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching release: {e}", exc_info=True)
            logger.info(f"  URL: {self.latest_release_url}")
            return None
    
    def _fetch_latest_tag(self) -> Optional[Dict[str, Any]]:
        """
        Fetch latest tag information from GitHub API
        Used as fallback when no releases are available
        
        Returns:
            Tag data dictionary formatted as release data or None
        """
        try:
            tags_url = f"{self.api_base_url}/tags"
            print(f"[UPDATE] Fetching latest tag from: {tags_url}")
            logger.debug(f"Fetching latest tag from: {tags_url}")
            
            request = urllib.request.Request(
                tags_url,
                headers={
                    "User-Agent": "ArtenceCMMS-Updater/1.0",
                    "Accept": "application/vnd.github.v3+json",
                }
            )
            
            with urllib.request.urlopen(request, timeout=10) as response:
                if response.status == 200:
                    tags = json.loads(response.read().decode())
                    if not tags:
                        logger.warning("No tags found in repository")
                        return None
                    
                    # Get the first (latest) tag
                    # Tags are usually sorted by creation date, but we'll sort by version
                    from utils.version_utils import parse_version, compare_versions
                    
                    # Sort tags by version (descending)
                    def tag_version_key(tag):
                        tag_name = tag.get("name", "").lstrip("vV")
                        major, minor, patch, _ = parse_version(tag_name)
                        return (major, minor, patch)
                    
                    sorted_tags = sorted(tags, key=tag_version_key, reverse=True)
                    latest_tag = sorted_tags[0]
                    tag_name = latest_tag.get("name", "")
                    
                    logger.info(f"Found latest tag: {tag_name}")
                    
                    # Format as release data
                    # Build download URL for installer from Git LFS
                    # For Git LFS files, we need to use the GitHub API to get the download URL
                    version = tag_name.lstrip("vV")
                    # Try to get the file content URL from GitHub API
                    file_path = f"CMMS_Project/installer/ZedCMMS_Setup_v{version}.exe"
                    content_url = f"{self.api_base_url}/contents/{file_path}?ref={tag_name}"
                    
                    # First try to get the download URL from GitHub API
                    download_url = None
                    try:
                        content_request = urllib.request.Request(
                            content_url,
                            headers={
                                "User-Agent": "ArtenceCMMS-Updater/1.0",
                                "Accept": "application/vnd.github.v3+json",
                            }
                        )
                        with urllib.request.urlopen(content_request, timeout=10) as content_response:
                            if content_response.status == 200:
                                content_data = json.loads(content_response.read().decode())
                                # For LFS files, GitHub provides download_url in the response
                                download_url = content_data.get("download_url")
                                # If download_url is None, try to get it from git_lfs or other fields
                                if not download_url:
                                    # For Git LFS files, the download might be through a different mechanism
                                    # Try using the raw.githubusercontent.com URL
                                    download_url = f"https://raw.githubusercontent.com/{self.github_owner}/{self.github_repo}/{tag_name}/{file_path}"
                                    logger.info(f"Using raw GitHub URL for LFS file: {download_url[:50]}...")
                                else:
                                    logger.info(f"Found download URL from GitHub API: {download_url[:50]}...")
                            elif content_response.status == 404:
                                # File not found at that path, try alternative path
                                logger.warning(f"File not found at {file_path}, trying alternative path")
                                # Try without CMMS_Project prefix
                                alt_file_path = f"installer/ZedCMMS_Setup_v{version}.exe"
                                alt_content_url = f"{self.api_base_url}/contents/{alt_file_path}?ref={tag_name}"
                                try:
                                    alt_content_request = urllib.request.Request(
                                        alt_content_url,
                                        headers={
                                            "User-Agent": "ArtenceCMMS-Updater/1.0",
                                            "Accept": "application/vnd.github.v3+json",
                                        }
                                    )
                                    with urllib.request.urlopen(alt_content_request, timeout=10) as alt_content_response:
                                        if alt_content_response.status == 200:
                                            alt_content_data = json.loads(alt_content_response.read().decode())
                                            download_url = alt_content_data.get("download_url")
                                            if not download_url:
                                                download_url = f"https://raw.githubusercontent.com/{self.github_owner}/{self.github_repo}/{tag_name}/{alt_file_path}"
                                except Exception:
                                    pass
                    except Exception as e:
                        logger.warning(f"Could not get download URL from GitHub API: {e}")
                    
                    # Fallback to raw URL if API didn't work
                    if not download_url:
                        # Try both paths
                        download_url = f"https://raw.githubusercontent.com/{self.github_owner}/{self.github_repo}/{tag_name}/{file_path}"
                        logger.info(f"Using raw GitHub URL as fallback: {download_url[:50]}...")
                    
                    # Ensure we have a download URL
                    if not download_url:
                        logger.error(f"Could not construct download URL for tag {tag_name}")
                        return None
                    
                    # Create release-like structure
                    release_data = {
                        "tag_name": tag_name,
                        "name": tag_name,
                        "published_at": latest_tag.get("commit", {}).get("sha", ""),  # Use commit SHA as fallback
                        "body": f"Release {tag_name}",
                        "assets": [
                            {
                                "name": f"ZedCMMS_Setup_v{version}.exe",
                                "browser_download_url": download_url
                            }
                        ]
                    }
                    
                    logger.info(f"Formatted tag as release data (download URL: {download_url[:50]}...)")
                    logger.debug(f"Release data structure: tag_name={release_data['tag_name']}, assets count={len(release_data['assets'])}")
                    return release_data
                else:
                    logger.error(f"GitHub API returned status {response.status} (expected 200)")
                    return None
                    
        except urllib.error.HTTPError as e:
            if e.code == 404:
                logger.warning(f"No tags found on GitHub (404 Not Found)")
                logger.info(f"  URL: {tags_url}")
            elif e.code == 403:
                logger.error(f"GitHub API access forbidden (403) - rate limit exceeded or repository is private")
                logger.info(f"  URL: {tags_url}")
            else:
                logger.error(f"HTTP error fetching tags: {e.code} - {e.reason}")
                logger.info(f"  URL: {tags_url}")
            return None
        except urllib.error.URLError as e:
            logger.error(f"URL error fetching tags: {e.reason}")
            logger.info(f"  URL: {tags_url}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching tags: {e}", exc_info=True)
            logger.info(f"  URL: {tags_url}")
            return None
    
    def _extract_download_url(self, release_data: Dict[str, Any]) -> Optional[str]:
        """
        Extract download URL from release assets
        
        Args:
            release_data: Release data from GitHub API
        
        Returns:
            Download URL or None
        """
        assets = release_data.get("assets", [])
        logger.debug(f"Extracting download URL from {len(assets)} asset(s)")
        
        # Look for installer .exe file
        for asset in assets:
            name = asset.get("name", "")
            browser_download_url = asset.get("browser_download_url")
            logger.debug(f"  Asset: {name}, URL: {browser_download_url[:50] if browser_download_url else 'None'}...")
            if name.endswith(".exe") and "Setup" in name:
                if browser_download_url:
                    logger.info(f"Found installer download URL: {browser_download_url[:50]}...")
                    return browser_download_url
                else:
                    logger.warning(f"Asset {name} has no browser_download_url")
        
        # If no .exe found, return first asset URL
        if assets:
            first_asset = assets[0]
            first_url = first_asset.get("browser_download_url")
            logger.info(f"Using first asset URL: {first_url[:50] if first_url else 'None'}...")
            return first_url
        
        logger.warning("No assets found in release data")
        return None
    
    def get_release_notes(self, version: str = None) -> Optional[str]:
        """
        Get release notes for a specific version
        
        Args:
            version: Version to get notes for (defaults to latest)
        
        Returns:
            Release notes or None
        """
        try:
            if version:
                # Fetch specific release
                release_url = f"{self.releases_url}/tags/v{version.lstrip('vV')}"
            else:
                # Fetch latest release
                release_url = self.latest_release_url
            
            request = urllib.request.Request(
                release_url,
                headers={
                    "User-Agent": "ArtenceCMMS-Updater/1.0",
                    "Accept": "application/vnd.github.v3+json",
                }
            )
            
            with urllib.request.urlopen(request, timeout=10) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    return data.get("body", "")
                else:
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching release notes: {e}")
            return None


# Global instance
_update_service = None


def get_update_service() -> UpdateService:
    """Get global update service instance"""
    global _update_service
    if _update_service is None:
        _update_service = UpdateService()
    return _update_service

