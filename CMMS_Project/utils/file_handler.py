"""
File Handler Utility
Centralized file upload, download, and management
"""

import os
import shutil
import uuid
from pathlib import Path
from typing import Optional, List, Tuple
from datetime import datetime

import logging

logger = logging.getLogger(__name__)


def upload_file(file_obj, directory: Path, allowed_extensions: List[str], 
                max_size_mb: int = 10, use_uuid: bool = True) -> Optional[Path]:
    """
    Upload and save a file with validation
    
    Args:
        file_obj: File object (from Flet FilePicker or similar)
        directory: Target directory path
        allowed_extensions: List of allowed extensions (e.g., ['.pdf', '.jpg'])
        max_size_mb: Maximum file size in MB
        use_uuid: If True, use UUID for filename; otherwise keep original name
    
    Returns:
        Path to saved file, or None on error
    """
    try:
        # Ensure directory exists
        directory.mkdir(parents=True, exist_ok=True)
        
        # Get original filename
        if hasattr(file_obj, 'name'):
            original_filename = file_obj.name
        elif isinstance(file_obj, str):
            original_filename = Path(file_obj).name
        else:
            original_filename = "uploaded_file"
        
        # Validate extension
        file_ext = Path(original_filename).suffix.lower()
        if file_ext not in allowed_extensions:
            raise ValueError(f"File extension {file_ext} not allowed. Allowed: {allowed_extensions}")
        
        # Generate filename
        if use_uuid:
            filename = f"{uuid.uuid4()}{file_ext}"
        else:
            # Sanitize filename
            safe_name = "".join(c for c in original_filename if c.isalnum() or c in "._- ")
            filename = safe_name
        
        output_path = directory / filename
        
        # Check file size if file_obj has size attribute
        if hasattr(file_obj, 'size'):
            size_mb = file_obj.size / (1024 * 1024)
            if size_mb > max_size_mb:
                raise ValueError(f"File size {size_mb:.2f} MB exceeds maximum {max_size_mb} MB")
        
        # Save file
        if hasattr(file_obj, 'read'):
            # File-like object
            with open(output_path, 'wb') as f:
                shutil.copyfileobj(file_obj, f)
        elif isinstance(file_obj, (str, Path)):
            # Path string
            shutil.copy2(file_obj, output_path)
        else:
            raise ValueError("Unsupported file object type")
        
        logger.info(f"File uploaded: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        return None


def download_file(file_path: Path, target_path: Optional[Path] = None) -> Optional[Path]:
    """
    Download/copy a file to target location
    
    Args:
        file_path: Source file path
        target_path: Target path (if None, returns source path)
    
    Returns:
        Path to downloaded file, or None on error
    """
    try:
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if target_path is None:
            return file_path
        
        # Ensure target directory exists
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy file
        shutil.copy2(file_path, target_path)
        
        logger.info(f"File downloaded: {target_path}")
        return target_path
        
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        return None


def delete_file(file_path: Path) -> bool:
    """
    Delete a file
    
    Args:
        file_path: Path to file to delete
    
    Returns:
        True if successful, False otherwise
    """
    try:
        if file_path.exists():
            file_path.unlink()
            logger.info(f"File deleted: {file_path}")
            return True
        else:
            logger.warning(f"File not found for deletion: {file_path}")
            return False
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        return False


def validate_file_upload(filename: str, max_size_mb: int, allowed_extensions: List[str]) -> Tuple[bool, Optional[str]]:
    """
    Validate file before upload
    
    Args:
        filename: File name
        max_size_mb: Maximum size in MB
        allowed_extensions: List of allowed extensions
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Check extension
        file_ext = Path(filename).suffix.lower()
        if file_ext not in allowed_extensions:
            return False, f"File extension {file_ext} not allowed. Allowed: {allowed_extensions}"
        
        return True, None
        
    except Exception as e:
        return False, f"Validation error: {e}"


def get_file_size(file_path: Path) -> Optional[int]:
    """
    Get file size in bytes
    
    Args:
        file_path: Path to file
    
    Returns:
        File size in bytes, or None on error
    """
    try:
        if file_path.exists():
            return file_path.stat().st_size
        return None
    except Exception as e:
        logger.error(f"Error getting file size: {e}")
        return None


def ensure_directory(directory: Path) -> bool:
    """
    Ensure directory exists, create if not
    
    Args:
        directory: Directory path
    
    Returns:
        True if successful, False otherwise
    """
    try:
        directory.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Error ensuring directory: {e}")
        return False

