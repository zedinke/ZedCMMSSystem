"""
Site service for multi-site/multi-tenant support
"""

from typing import Optional, List, Dict
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from database.models import Site, SiteUser, User, Machine, Part, Worksheet, utcnow
from database.session_manager import SessionLocal
import logging

logger = logging.getLogger(__name__)


def create_site(
    name: str,
    code: str,
    address: Optional[str] = None,
    timezone: str = "UTC",
    settings: Optional[Dict] = None,
    session: Session = None
) -> Site:
    """Create a new site"""
    if session is None:
        session = SessionLocal()
        should_close = True
    else:
        should_close = False
    
    try:
        # Check if code already exists
        existing = session.query(Site).filter_by(code=code).first()
        if existing:
            raise ValueError(f"Site with code '{code}' already exists")
        
        site = Site(
            name=name,
            code=code,
            address=address,
            timezone=timezone,
            settings=settings or {},
            is_active=True
        )
        
        session.add(site)
        session.commit()
        logger.info(f"Created site: {name} ({code})")
        return site
    
    finally:
        if should_close:
            session.close()


def list_sites(active_only: bool = False, session: Session = None) -> List[Site]:
    """List all sites"""
    if session is None:
        session = SessionLocal()
        should_close = True
    else:
        should_close = False
    
    try:
        query = session.query(Site)
        if active_only:
            query = query.filter(Site.is_active == True)
        return query.order_by(Site.name).all()
    
    finally:
        if should_close:
            session.close()


def get_site(site_id: int, session: Session = None) -> Optional[Site]:
    """Get a site by ID"""
    if session is None:
        session = SessionLocal()
        should_close = True
    else:
        should_close = False
    
    try:
        return session.query(Site).filter_by(id=site_id).first()
    
    finally:
        if should_close:
            session.close()


def get_site_by_code(code: str, session: Session = None) -> Optional[Site]:
    """Get a site by code"""
    if session is None:
        session = SessionLocal()
        should_close = True
    else:
        should_close = False
    
    try:
        return session.query(Site).filter_by(code=code).first()
    
    finally:
        if should_close:
            session.close()


def update_site(
    site_id: int,
    name: Optional[str] = None,
    address: Optional[str] = None,
    timezone: Optional[str] = None,
    settings: Optional[Dict] = None,
    is_active: Optional[bool] = None,
    session: Session = None
) -> Site:
    """Update a site"""
    if session is None:
        session = SessionLocal()
        should_close = True
    else:
        should_close = False
    
    try:
        site = session.query(Site).filter_by(id=site_id).first()
        if not site:
            raise ValueError(f"Site {site_id} not found")
        
        if name is not None:
            site.name = name
        if address is not None:
            site.address = address
        if timezone is not None:
            site.timezone = timezone
        if settings is not None:
            site.settings = settings
        if is_active is not None:
            site.is_active = is_active
        
        session.commit()
        logger.info(f"Updated site: {site_id}")
        return site
    
    finally:
        if should_close:
            session.close()


def assign_user_to_site(
    user_id: int,
    site_id: int,
    role_at_site: Optional[str] = None,
    is_primary: bool = False,
    session: Session = None
) -> SiteUser:
    """Assign a user to a site"""
    if session is None:
        session = SessionLocal()
        should_close = True
    else:
        should_close = False
    
    try:
        # Check if assignment already exists
        existing = session.query(SiteUser).filter_by(
            user_id=user_id,
            site_id=site_id
        ).first()
        
        if existing:
            # Update existing
            if role_at_site is not None:
                existing.role_at_site = role_at_site
            if is_primary:
                # Unset other primary sites for this user
                session.query(SiteUser).filter(
                    SiteUser.user_id == user_id,
                    SiteUser.id != existing.id
                ).update({'is_primary_site': False})
                existing.is_primary_site = True
            session.commit()
            return existing
        
        # If setting as primary, unset other primary sites
        if is_primary:
            session.query(SiteUser).filter(
                SiteUser.user_id == user_id
            ).update({'is_primary_site': False})
        
        site_user = SiteUser(
            user_id=user_id,
            site_id=site_id,
            role_at_site=role_at_site,
            is_primary_site=is_primary
        )
        
        session.add(site_user)
        session.commit()
        logger.info(f"Assigned user {user_id} to site {site_id}")
        return site_user
    
    finally:
        if should_close:
            session.close()


def get_user_sites(user_id: int, session: Session = None) -> List[Site]:
    """Get all sites for a user"""
    if session is None:
        session = SessionLocal()
        should_close = True
    else:
        should_close = False
    
    try:
        site_users = session.query(SiteUser).filter_by(user_id=user_id).all()
        return [su.site for su in site_users if su.site]
    
    finally:
        if should_close:
            session.close()


def get_user_primary_site(user_id: int, session: Session = None) -> Optional[Site]:
    """Get user's primary site"""
    if session is None:
        session = SessionLocal()
        should_close = True
    else:
        should_close = False
    
    try:
        site_user = session.query(SiteUser).filter_by(
            user_id=user_id,
            is_primary_site=True
        ).first()
        
        return site_user.site if site_user else None
    
    finally:
        if should_close:
            session.close()


def remove_user_from_site(user_id: int, site_id: int, session: Session = None) -> bool:
    """Remove a user from a site"""
    if session is None:
        session = SessionLocal()
        should_close = True
    else:
        should_close = False
    
    try:
        site_user = session.query(SiteUser).filter_by(
            user_id=user_id,
            site_id=site_id
        ).first()
        
        if not site_user:
            return False
        
        session.delete(site_user)
        session.commit()
        logger.info(f"Removed user {user_id} from site {site_id}")
        return True
    
    finally:
        if should_close:
            session.close()


def get_site_statistics(site_id: int, session: Session = None) -> Dict:
    """Get statistics for a site"""
    if session is None:
        session = SessionLocal()
        should_close = True
    else:
        should_close = False
    
    try:
        # TODO: Multi-site support - site_id fields removed from models temporarily
        # When multi-site is implemented, add site_id columns to database and models
        machine_count = session.query(Machine).count()  # .filter_by(site_id=site_id).count()
        part_count = session.query(Part).count()  # .filter_by(site_id=site_id).count()
        worksheet_count = session.query(Worksheet).count()  # .filter_by(site_id=site_id).count()
        user_count = session.query(SiteUser).filter_by(site_id=site_id).count()
        
        return {
            'machine_count': machine_count,
            'part_count': part_count,
            'worksheet_count': worksheet_count,
            'user_count': user_count
        }
    
    finally:
        if should_close:
            session.close()

