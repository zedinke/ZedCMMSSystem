"""
User Service
CRUD operations and preference handling for users
"""

from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from database.models import User, Role
from database.session_manager import SessionLocal
from services.auth_service import hash_password, verify_password
from config.roles import DEFAULT_PASSWORD, ROLE_DEVELOPER
from config.app_config import CACHE_DEFAULT_TTL
from utils.localization_helper import get_localized_error
from utils.cache import get_role_cache, get_user_cache
import logging

logger = logging.getLogger(__name__)


class UserServiceError(Exception):
    """Custom exception for user service errors"""
    pass


def create_user(username: str, email: str, password: str, role_name: str, 
                full_name: str = None, phone: str = None, profile_picture: str = None,
                language: str = "hu", vacation_days_per_year: int = None,
                shift_type: str = None, shift_start_time: str = None, shift_end_time: str = None,
                work_days_per_week: int = None, session: Session = None) -> User:
    should_close = False
    if session is None:
        session = SessionLocal()
        should_close = True
    try:
        # Check username/email uniqueness
        if session.query(User).filter_by(username=username).first():
            raise UserServiceError(get_localized_error("validation.username_exists"))
        if email and session.query(User).filter_by(email=email).first():
            raise UserServiceError(get_localized_error("duplicate_email"))

        role = session.query(Role).filter_by(name=role_name).first()
        if not role:
            raise UserServiceError(get_localized_error("role_not_found", role_name=role_name))

        # Use default password if not provided
        use_default_password = password is None or password == ""
        if use_default_password:
            password = DEFAULT_PASSWORD

        user = User(
            username=username,
            full_name=full_name,
            email=email,
            phone=phone,
            profile_picture=profile_picture,
            password_hash=hash_password(password),
            role_id=role.id,
            language_preference=language,
            must_change_password=use_default_password,  # Force password change if default used
            vacation_days_per_year=vacation_days_per_year if vacation_days_per_year is not None else 20,
            vacation_days_used=0,
            shift_type=shift_type,
            shift_start_time=shift_start_time,
            shift_end_time=shift_end_time,
            work_days_per_week=work_days_per_week if work_days_per_week is not None else 5,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        # Invalidate user cache
        cache = get_user_cache()
        cache.invalidate(f"user:{user.id}")
        logger.info(f"Created user {username} with role {role_name}")
        return user
    finally:
        if should_close:
            session.close()


def get_user(user_id: int, session: Session = None) -> User:
    """Get user with caching for ultra-fast access"""
    from utils.cache import get_user_cache
    
    # Try cache first
    cache = get_user_cache()
    cache_key = f"user:{user_id}"
    cached_user = cache.get(cache_key)
    if cached_user is not None:
        return cached_user
    
    should_close = False
    if session is None:
        session = SessionLocal(); should_close = True
    try:
        # Eager-load role to avoid lazy-load issues after session close
        user = session.query(User).options(joinedload(User.role)).filter_by(id=user_id).first()
        if user:
            # Cache for 5 minutes
            cache.set(cache_key, user, ttl=300)
        return user
    finally:
        if should_close:
            session.close()


def list_users(role_filter: str = None, session: Session = None):
    """List users with caching and optimized queries"""
    from utils.cache import get_user_cache
    
    should_close = False
    if session is None:
        session = SessionLocal(); should_close = True
    try:
        # Eager-load role to avoid lazy-load issues after session close
        query = session.query(User).options(joinedload(User.role))
        if role_filter:
            # Use join instead of separate query for better performance
            query = query.join(Role).filter(Role.name == role_filter)
        return query.all()
    finally:
        if should_close:
            session.close()


def list_all_users(session: Session = None) -> List[User]:
    """List all users (for user management screen)"""
    return list_users(role_filter=None, session=session)


def verify_user_password(user_id: int, password: str, session: Session = None) -> bool:
    """Verify if provided password matches user's password"""
    should_close = False
    if session is None:
        session = SessionLocal(); should_close = True
    try:
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            return False
        return verify_password(password, user.password_hash)
    finally:
        if should_close:
            session.close()


def update_user_language(user_id: int, language: str, session: Session = None) -> bool:
    should_close = False
    if session is None:
        session = SessionLocal(); should_close = True
    try:
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            raise UserServiceError(get_localized_error("user_not_found"))
        user.language_preference = language
        session.commit()
        # Invalidate user cache
        cache = get_user_cache()
        cache.invalidate(f"user:{user_id}")
        logger.info(f"Updated language for user {user.username} -> {language}")
        return True
    finally:
        if should_close:
            session.close()


def deactivate_user(user_id: int, session: Session = None) -> bool:
    should_close = False
    if session is None:
        session = SessionLocal(); should_close = True
    try:
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            raise UserServiceError(get_localized_error("user_not_found"))
        user.is_active = False
        session.commit()
        logger.info(f"Deactivated user {user.username}")
        return True
    finally:
        if should_close:
            session.close()


def change_password(user_id: int, new_password: str, session: Session = None) -> bool:
    should_close = False
    if session is None:
        session = SessionLocal(); should_close = True
    try:
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            raise UserServiceError(get_localized_error("user_not_found"))
        user.password_hash = hash_password(new_password)
        user.must_change_password = False  # Clear forced password change flag
        session.commit()
        logger.info(f"Password changed for user {user.username}")
        return True
    finally:
        if should_close:
            session.close()


def reset_user_password(user_id: int, session: Session = None) -> User:
    """Reset user password to default and force password change"""
    should_close = False
    if session is None:
        session = SessionLocal(); should_close = True
    try:
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            raise UserServiceError(get_localized_error("user_not_found"))
        
        user.password_hash = hash_password(DEFAULT_PASSWORD)
        user.must_change_password = True
        session.commit()
        
        logger.info(f"Password reset for user: {user.username}")
        return user
    finally:
        if should_close:
            session.close()


def update_user_role(user_id: int, new_role_name: str, session: Session = None) -> User:
    """Update user's role"""
    should_close = False
    if session is None:
        session = SessionLocal(); should_close = True
    try:
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            raise UserServiceError(get_localized_error("user_not_found"))
        
        role = session.query(Role).filter_by(name=new_role_name).first()
        if not role:
            raise UserServiceError(f"Role '{new_role_name}' not found")
        
        user.role_id = role.id
        session.commit()
        # Invalidate user cache
        cache = get_user_cache()
        cache.invalidate(f"user:{user_id}")
        logger.info(f"User role updated: {user.username} -> {new_role_name}")
        return user
    finally:
        if should_close:
            session.close()


def anonymize_user(user_id: int, anonymized_by_user_id: int, session: Session = None) -> None:
    """
    Anonymize user data (GDPR Right to be Forgotten)
    - Sets is_active = False
    - Removes PII: username, email, phone, full_name, profile_picture
    - Keeps: id, role_id, created_at (for statistics)
    - Sets anonymized_at timestamp
    """
    should_close = False
    if session is None:
        session = SessionLocal(); should_close = True
    try:
        from database.models import utcnow
        
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            raise UserServiceError(get_localized_error("user_not_found"))
        
        # Prevent anonymizing Developer users
        if user.role.name == ROLE_DEVELOPER:
            raise UserServiceError(get_localized_error("cannot_anonymize_developer"))
        
        # Check if already anonymized
        if user.anonymized_at is not None:
            raise UserServiceError(get_localized_error("user_already_anonymized"))
        
        # Remove PII (Personal Identifiable Information)
        original_username = user.username
        user.username = f"anonymized_{user.id}_{user.created_at.strftime('%Y%m%d')}"
        user.email = None
        user.phone = None
        user.full_name = None
        user.profile_picture = None
        
        # Deactivate user
        user.is_active = False
        
        # Set anonymization timestamp
        user.anonymized_at = utcnow()
        user.anonymized_by_user_id = anonymized_by_user_id
        
        session.commit()
        
        logger.info(f"User anonymized: {original_username} (id={user_id}) by user {anonymized_by_user_id}")
    finally:
        if should_close:
            session.close()


def delete_user(user_id: int, session: Session = None) -> None:
    """
    Delete a user (GDPR compliant - uses anonymization instead of hard delete)
    This function now calls anonymize_user() to comply with GDPR Right to be Forgotten
    """
    # For backward compatibility, we need anonymized_by_user_id
    # In practice, this should be called from UI/API with the current user's ID
    # For now, we'll use a system user ID (0) or require it as parameter
    # TODO: Update callers to pass anonymized_by_user_id
    raise UserServiceError(get_localized_error("delete_user_deprecated"))


def list_roles(session: Session = None) -> List[Role]:
    """List all roles with ultra-fast caching"""
    cache = get_role_cache()
    cache_key = "roles:all"
    
    # Try cache first
    cached_roles = cache.get(cache_key)
    if cached_roles is not None:
        return cached_roles

    should_close = False
    if session is None:
        session = SessionLocal(); should_close = True
    try:
        roles = session.query(Role).order_by(Role.name).all()
        # Cache for 10 minutes (roles don't change often)
        cache.set(cache_key, roles, ttl=600)
        return roles
    finally:
        if should_close:
            session.close()


def update_user_details(
    user_id: int,
    username: Optional[str] = None,
    full_name: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    role_name: Optional[str] = None,
    session: Session = None,
) -> User:
    """Update core user fields and optionally role.

    Performs basic uniqueness checks for username and email.
    """
    should_close = False
    if session is None:
        session = SessionLocal(); should_close = True
    try:
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            raise UserServiceError(get_localized_error("user_not_found"))

        # Username uniqueness
        if username and username != user.username:
            if session.query(User).filter_by(username=username).first():
                raise UserServiceError("Username already exists")
            user.username = username

        # Email uniqueness
        if email is not None and email != user.email:
            if email and session.query(User).filter_by(email=email).first():
                raise UserServiceError("Email already exists")
            user.email = email or None

        if full_name is not None:
            user.full_name = full_name or None

        if phone is not None:
            user.phone = phone or None

        if role_name:
            role = session.query(Role).filter_by(name=role_name).first()
            if not role:
                raise UserServiceError(get_localized_error("role_not_found", role_name=role_name))
            user.role_id = role.id

        # Update vacation and shift fields
        if vacation_days_per_year is not None:
            user.vacation_days_per_year = vacation_days_per_year
        if shift_type is not None:
            user.shift_type = shift_type
        if shift_start_time is not None:
            user.shift_start_time = shift_start_time
        if shift_end_time is not None:
            user.shift_end_time = shift_end_time
        if work_days_per_week is not None:
            user.work_days_per_week = work_days_per_week

        session.commit()
        # Invalidate user cache
        cache = get_user_cache()
        cache.invalidate(f"user:{user_id}")
        logger.info(f"User details updated: {user.username}")
        return user
    finally:
        if should_close:
            session.close()


def update_role_permissions(role_name: str, permissions: dict, session: Session = None) -> Role:
    """Update role permissions (Manager only, cannot edit Developer permissions)"""
    should_close = False
    if session is None:
        session = SessionLocal(); should_close = True
    try:
        if role_name == ROLE_DEVELOPER:
            raise UserServiceError(get_localized_error("cannot_modify_developer_role"))
        
        role = session.query(Role).filter_by(name=role_name).first()
        if not role:
            raise UserServiceError(get_localized_error("role_not_found", role_name=role_name))
        
        role.permissions = permissions
        session.commit()
        # Invalidate role cache
        cache = get_role_cache()
        cache.invalidate("roles:all")
        
        logger.info(f"Role permissions updated: {role_name}")
        return role
    finally:
        if should_close:
            session.close()
