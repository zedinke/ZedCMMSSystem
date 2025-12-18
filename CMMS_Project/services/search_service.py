"""
Global Search Service
Provides unified search functionality across all entities
"""
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from database.session_manager import SessionLocal
from database.models import Machine, Part, Worksheet, User, ProductionLine, StorageLocation
import logging

logger = logging.getLogger(__name__)


def _get_session(session: Optional[Session]) -> tuple:
    """Get or create database session"""
    if session is not None:
        return session, False
    return SessionLocal(), True


def global_search(query: str, limit: int = 20, session: Session = None) -> Dict[str, List[Dict]]:
    """
    Perform global search across all entities
    
    Args:
        query: Search query string
        limit: Maximum results per category
        session: Optional database session
    
    Returns:
        Dictionary with search results by category:
        {
            "machines": [...],
            "parts": [...],
            "worksheets": [...],
            "users": [...],
            "production_lines": [...],
            "storage_locations": [...]
        }
    """
    session, should_close = _get_session(session)
    
    try:
        if not query or len(query.strip()) < 2:
            return {
                "machines": [],
                "parts": [],
                "worksheets": [],
                "users": [],
                "production_lines": [],
                "storage_locations": []
            }
        
        search_term = f"%{query.strip().lower()}%"
        results = {
            "machines": [],
            "parts": [],
            "worksheets": [],
            "users": [],
            "production_lines": [],
            "storage_locations": []
        }
        
        # Search machines
        try:
            machines = (
                session.query(Machine)
                .filter(
                    or_(
                        func.lower(Machine.name).like(search_term),
                        func.lower(Machine.serial_number).like(search_term),
                        func.lower(Machine.asset_tag).like(search_term),
                        func.lower(Machine.model).like(search_term),
                        func.lower(Machine.manufacturer).like(search_term),
                    )
                )
                .limit(limit)
                .all()
            )
            results["machines"] = [
                {
                    "id": m.id,
                    "name": m.name,
                    "type": "machine",
                    "display": f"{m.name} ({m.serial_number or m.asset_tag or 'N/A'})",
                    "subtitle": f"{m.manufacturer or ''} {m.model or ''}".strip() or None,
                }
                for m in machines
            ]
        except Exception as e:
            logger.warning(f"Error searching machines: {e}")
        
        # Search parts
        try:
            parts = (
                session.query(Part)
                .filter(
                    or_(
                        func.lower(Part.name).like(search_term),
                        func.lower(Part.sku).like(search_term),
                        func.lower(Part.description).like(search_term),
                    )
                )
                .limit(limit)
                .all()
            )
            results["parts"] = [
                {
                    "id": p.id,
                    "name": p.name,
                    "type": "part",
                    "display": f"{p.name} ({p.sku})",
                    "subtitle": p.description or None,
                }
                for p in parts
            ]
        except Exception as e:
            logger.warning(f"Error searching parts: {e}")
        
        # Search worksheets
        try:
            worksheets = (
                session.query(Worksheet)
                .filter(
                    or_(
                        func.lower(Worksheet.title).like(search_term),
                        func.lower(Worksheet.description).like(search_term),
                    )
                )
                .limit(limit)
                .all()
            )
            results["worksheets"] = [
                {
                    "id": w.id,
                    "name": w.title,
                    "type": "worksheet",
                    "display": w.title,
                    "subtitle": f"Status: {w.status}" if w.status else None,
                }
                for w in worksheets
            ]
        except Exception as e:
            logger.warning(f"Error searching worksheets: {e}")
        
        # Search users
        try:
            users = (
                session.query(User)
                .filter(
                    or_(
                        func.lower(User.username).like(search_term),
                        func.lower(User.full_name).like(search_term),
                        func.lower(User.email).like(search_term),
                    )
                )
                .filter(User.is_active == True)
                .limit(limit)
                .all()
            )
            results["users"] = [
                {
                    "id": u.id,
                    "name": u.full_name or u.username,
                    "type": "user",
                    "display": u.full_name or u.username,
                    "subtitle": u.email or None,
                }
                for u in users
            ]
        except Exception as e:
            logger.warning(f"Error searching users: {e}")
        
        # Search production lines
        try:
            production_lines = (
                session.query(ProductionLine)
                .filter(
                    func.lower(ProductionLine.name).like(search_term)
                )
                .limit(limit)
                .all()
            )
            results["production_lines"] = [
                {
                    "id": pl.id,
                    "name": pl.name,
                    "type": "production_line",
                    "display": pl.name,
                    "subtitle": None,
                }
                for pl in production_lines
            ]
        except Exception as e:
            logger.warning(f"Error searching production lines: {e}")
        
        # Search storage locations
        try:
            storage_locations = (
                session.query(StorageLocation)
                .filter(
                    or_(
                        func.lower(StorageLocation.name).like(search_term),
                        func.lower(StorageLocation.description).like(search_term),
                    )
                )
                .filter(StorageLocation.is_active == True)
                .limit(limit)
                .all()
            )
            results["storage_locations"] = [
                {
                    "id": sl.id,
                    "name": sl.name,
                    "type": "storage_location",
                    "display": sl.name,
                    "subtitle": sl.description or None,
                }
                for sl in storage_locations
            ]
        except Exception as e:
            logger.warning(f"Error searching storage locations: {e}")
        
        return results
        
    finally:
        if should_close:
            session.close()

