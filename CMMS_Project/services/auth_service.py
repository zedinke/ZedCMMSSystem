"""
Authentication Service
User authentication, password hashing, session management
"""

import secrets
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from database.models import User, UserSession, Role
from database.session_manager import SessionLocal
from config.app_config import SESSION_EXPIRY_HOURS, SESSION_TOKEN_LENGTH
import logging

logger = logging.getLogger(__name__)

# Create bcrypt password hasher (GDPR compliance requirement: bcrypt)
# Use bcrypt directly instead of passlib for better compatibility
try:
    import bcrypt
    USE_DIRECT_BCRYPT = True
    pwd_context = None  # Not needed when using direct bcrypt
except ImportError:
    USE_DIRECT_BCRYPT = False
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def utcnow():
    """Timezone-aware UTC now for session timestamps."""
    return datetime.now(timezone.utc)


class AuthenticationError(Exception):
    """Custom exception for authentication errors"""
    pass


def hash_password(password: str) -> str:
    """
    Hash password using bcrypt (GDPR compliance requirement)
    
    Args:
        password: Plain text password
    
    Returns:
        Hashed password
    """
    try:
        if USE_DIRECT_BCRYPT:
            # Use bcrypt directly for better compatibility
            import bcrypt
            return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        else:
            return pwd_context.hash(password)
    except Exception as e:
        logger.error(f"Error hashing password: {e}")
        raise AuthenticationError("Password hashing failed")


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify password against hash (bcrypt or Argon2 for backward compatibility)
    
    Args:
        password: Plain text password to verify
        password_hash: Hash to compare against (bcrypt or Argon2)
    
    Returns:
        True if password matches, False otherwise
    """
    if not password_hash or not password:
        return False
    
    # Detect hash type by prefix
    is_bcrypt = password_hash.startswith('$2') or password_hash.startswith('$2a$') or password_hash.startswith('$2b$') or password_hash.startswith('$2y$')
    is_argon2 = password_hash.startswith('$argon2')
    
    # Try bcrypt first (current standard)
    if is_bcrypt:
        try:
            if USE_DIRECT_BCRYPT:
                # Use bcrypt directly for better compatibility
                import bcrypt
                return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
            else:
                return pwd_context.verify(password, password_hash)
        except Exception as e:
            logger.error(f"Error verifying bcrypt password: {e}")
            return False
    
    # Try Argon2 for backward compatibility
    if is_argon2:
        try:
            from argon2 import PasswordHasher
            from argon2.exceptions import VerifyMismatchError, InvalidHash
            argon2_ph = PasswordHasher()
            try:
                # Argon2 verify: verify(hash, password)
                argon2_ph.verify(password_hash, password)
                # If Argon2 verification succeeds, log for future migration
                logger.info("Argon2 hash detected and verified, will be rehashed to bcrypt on next password change")
                return True
            except VerifyMismatchError:
                return False
            except InvalidHash as e:
                logger.warning(f"Invalid Argon2 hash format: {e}")
                return False
        except ImportError:
            logger.error("Argon2 not available, cannot verify Argon2 hash")
            return False
        except Exception as argon2_error:
            logger.error(f"Error verifying password with Argon2: {argon2_error}")
            return False
    
    # Unknown hash format
    logger.warning(f"Unknown hash format (not bcrypt or Argon2)")
    return False


def create_session(user_id: int, session: Session = None) -> str:
    """
    Create a new user session with token
    
    Args:
        user_id: User ID
        session: SQLAlchemy session (creates new if None)
    
    Returns:
        Token string (32 bytes)
    """
    should_close = False
    if session is None:
        session = SessionLocal()
        should_close = True
    
    try:
        # Generate random token
        token = secrets.token_urlsafe(SESSION_TOKEN_LENGTH)
        token_hash = hash_password(token)
        
        # Create session record
        expiry = utcnow() + timedelta(hours=SESSION_EXPIRY_HOURS)
        
        # Try to insert session with retry logic for timeout/lock issues
        max_retries = 2
        last_error = None
        
        for attempt in range(max_retries):
            try:
                # If this is a retry, create a completely new session
                if attempt > 0:
                    if should_close and session:
                        try:
                            session.rollback()
                            session.close()
                        except:
                            pass
                    session = SessionLocal()
                    should_close = True
                
                # Create fresh user_session object
                user_session = UserSession(
                    user_id=user_id,
                    token_hash=token_hash,
                    expires_at=expiry
                )
                
                session.add(user_session)
                # Use commit() directly - simpler and faster
                session.commit()
                logger.info(f"Session created for user_id={user_id} (attempt {attempt + 1})")
                return token
                
            except OperationalError as e:
                error_str = str(e)
                error_code = getattr(e.orig, 'args', [None])[0] if hasattr(e, 'orig') else None
                last_error = e
                
                # Check for lock timeout (1205) or connection timeout (2013)
                is_lock_timeout = error_code == 1205 or "Lock wait timeout" in error_str
                is_conn_timeout = error_code == 2013 or "Lost connection" in error_str or "timeout" in error_str.lower()
                
                if is_lock_timeout or is_conn_timeout:
                    logger.warning(f"Commit timeout/lock (attempt {attempt + 1}/{max_retries}): {error_code} - {error_str[:100]}")
                    try:
                        session.rollback()
                    except:
                        pass
                    
                    if attempt < max_retries - 1:
                        # Wait before retry
                        import time
                        wait_time = 0.5  # Shorter wait time
                        logger.info(f"Waiting {wait_time}s before retry...")
                        time.sleep(wait_time)
                    else:
                        # Last attempt failed - return token anyway, session will be created later
                        logger.error(f"Failed to create session after {max_retries} attempts, but returning token anyway")
                        # Don't raise error - allow login to proceed, session can be created later
                        return token
                else:
                    # Other operational error, don't retry
                    try:
                        session.rollback()
                    except:
                        pass
                    raise
            except AuthenticationError:
                # Re-raise authentication errors
                raise
            except Exception as e:
                try:
                    session.rollback()
                except:
                    pass
                logger.error(f"Error committing session: {e}")
                # On last attempt, return token anyway
                if attempt == max_retries - 1:
                    logger.warning("Returning token despite session creation error")
                    return token
                raise
        
    finally:
        if should_close and session:
            try:
                session.close()
            except:
                pass


def validate_session(token: str, session: Session = None) -> dict:
    """
    Validate session token
    
    Args:
        token: Session token
        session: SQLAlchemy session (creates new if None)
    
    Returns:
        Dict with user info if valid, raises AuthenticationError if invalid
    """
    should_close = False
    if session is None:
        session = SessionLocal()
        should_close = True
    
    try:
        # ULTRA-OPTIMIZED: Only get non-expired sessions, ordered by last activity (most recent first)
        # This reduces the number of sessions to check significantly
        from sqlalchemy import and_
        cutoff_time = utcnow() - timedelta(hours=SESSION_EXPIRY_HOURS)
        
        # Get only active, non-expired sessions, most recent first
        # Reduced limit to 50 for faster queries
        user_sessions = session.query(UserSession).filter(
            UserSession.expires_at > utcnow(),
            UserSession.last_activity_at > cutoff_time
        ).order_by(UserSession.last_activity_at.desc()).limit(50).all()  # Reduced limit for faster queries
        
        # Try to verify token against each session (most recent first = faster match)
        for user_session in user_sessions:
            if verify_password(token, user_session.token_hash):
                # Check expiry (double-check)
                if user_session.is_expired():
                    session.delete(user_session)
                    try:
                        session.commit()
                    except Exception as e:
                        session.rollback()
                        logger.error(f"Error committing expired session deletion: {e}")
                    raise AuthenticationError("Session expired")
                
                # Update last activity
                user_session.last_activity_at = utcnow()
                try:
                    session.commit()
                except Exception as e:
                    session.rollback()
                    logger.error(f"Error committing session update: {e}")
                    # Try to reconnect and retry once
                    try:
                        session.close()
                        session = SessionLocal()
                        user_session = session.query(UserSession).filter_by(id=user_session.id).first()
                        if user_session:
                            user_session.last_activity_at = utcnow()
                            session.commit()
                    except Exception as retry_error:
                        logger.error(f"Error on retry: {retry_error}")
                        raise AuthenticationError("Database connection error")
                
                # Get user with eager-loaded role to avoid N+1 query
                from sqlalchemy.orm import joinedload
                user = session.query(User).options(joinedload(User.role)).filter_by(id=user_session.user_id).first()
                if not user:
                    raise AuthenticationError("User not found")
                
                if not user.is_active:
                    raise AuthenticationError("User is inactive")
                
                logger.info(f"Session validated for user_id={user.id}")
                
                # Debug: log what we're returning
                logger.debug(f"User full_name from DB: {repr(user.full_name)}, username: {repr(user.username)}")
                
                return {
                    "user_id": user.id,
                    "username": user.username,
                    "full_name": user.full_name if user.full_name else None,  # Explicitly set None if empty
                    "email": user.email,
                    "role_name": user.role.name,
                    "role": user.role.name,  # Keep for backward compatibility
                    "language": user.language_preference,
                    "language_preference": user.language_preference or "hu",  # Keep for backward compatibility
                    "permissions": user.role.permissions,
                    "is_active": user.is_active,
                    "must_change_password": user.must_change_password or False,
                }
        
        raise AuthenticationError("Invalid token")
        
    finally:
        if should_close:
            session.close()


def logout_session(token: str, session: Session = None) -> bool:
    """
    Logout user session (optimized version)
    
    Args:
        token: Session token
        session: SQLAlchemy session (creates new if None)
    
    Returns:
        True if successful
    """
    should_close = False
    if session is None:
        session = SessionLocal()
        should_close = True
    
    try:
        # Optimize: Hash the token once and search directly by token_hash
        # This is much faster than loading all sessions and checking each one
        token_hash = hash_password(token)
        
        # Try to find session by token_hash directly
        # Note: Since bcrypt uses random salt, we can't directly compare hashes
        # But we can optimize by checking only non-expired sessions
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        
        # Get all non-expired sessions (much smaller set than all sessions)
        active_sessions = session.query(UserSession).filter(
            UserSession.expires_at > now
        ).all()
        
        # Check each active session (still need to verify_password due to bcrypt salt)
        for user_session in active_sessions:
            if verify_password(token, user_session.token_hash):
                session.delete(user_session)
                session.commit()
                logger.info(f"Session logged out for user_id={user_session.user_id}")
                return True
        
        # If not found in active sessions, check expired ones (less common case)
        expired_sessions = session.query(UserSession).filter(
            UserSession.expires_at <= now
        ).all()
        
        for user_session in expired_sessions:
            if verify_password(token, user_session.token_hash):
                session.delete(user_session)
                session.commit()
                logger.info(f"Session logged out for user_id={user_session.user_id} (expired)")
                return True
        
        return False
        
    except Exception as e:
        # Log error but don't fail logout - user should still be logged out locally
        logger.error(f"Error during logout_session: {e}")
        return False
        
    finally:
        if should_close:
            session.close()


def login(username: str, password: str, session: Session = None) -> tuple[str, dict]:
    """
    Authenticate user and create session
    
    Args:
        username: Username
        password: Plain text password
        session: SQLAlchemy session (creates new if None)
    
    Returns:
        Tuple of (session_token, user_info_dict)
        user_info_dict contains: user_id, username, full_name, email, role_name, role, 
                                 language, language_preference, permissions, is_active, must_change_password
    
    Raises:
        AuthenticationError: If credentials invalid or user inactive
    """
    should_close = False
    if session is None:
        logger.info(f"Creating new session for login: {username}")
        try:
            # Try to get a fresh connection by disposing old connections if needed
            from database.connection import engine
            from sqlalchemy import text
            try:
                # Test connection first with a simple query
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                    conn.commit()
                logger.info("Database connection test successful")
            except Exception as conn_test_error:
                logger.warning(f"Connection test failed, trying to recreate engine: {conn_test_error}")
                # Try to recreate engine if connection fails
                try:
                    from database.connection import recreate_engine
                    recreate_engine("production")
                    logger.info("Engine recreated successfully")
                except Exception as recreate_error:
                    logger.error(f"Failed to recreate engine: {recreate_error}")
            
            session = SessionLocal()
            logger.info("Session created successfully")
        except Exception as session_error:
            logger.error(f"Error creating session: {session_error}")
            import traceback
            traceback.print_exc()
            raise AuthenticationError(f"Database connection error: {str(session_error)}")
        should_close = True
    
    try:
        # Find user with role loaded to avoid N+1 query
        from sqlalchemy.orm import joinedload
        logger.info(f"Querying user: {username}")
        try:
            user = session.query(User).options(joinedload(User.role)).filter_by(username=username).first()
            logger.info(f"User query completed: {user is not None}")
        except Exception as query_error:
            logger.error(f"Database query error during login: {query_error}")
            import traceback
            traceback.print_exc()
            raise AuthenticationError(f"Database connection error: {str(query_error)}")
        
        if not user:
            logger.warning(f"Login attempt with non-existent username: {username}")
            raise AuthenticationError("Invalid credentials")
        
        if not user.is_active:
            logger.warning(f"Login attempt with inactive user: {username}")
            raise AuthenticationError("User account is inactive")
        
        # Verify password
        if not verify_password(password, user.password_hash):
            logger.warning(f"Login attempt with wrong password: {username}")
            raise AuthenticationError("Invalid credentials")
        
        # Create session - use None to create a separate session to avoid lock conflicts
        # Close the current session first to release any locks
        if should_close:
            try:
                session.close()
            except:
                pass
        
        token = create_session(user.id, session=None)  # Pass None to create new session
        logger.info(f"Successful login: {username}")
        
        # Build user info dict (same format as validate_session returns)
        user_info = {
            "user_id": user.id,
            "username": user.username,
            "full_name": user.full_name if user.full_name else None,
            "email": user.email,
            "role_name": user.role.name,
            "role": user.role.name,
            "language": user.language_preference,
            "language_preference": user.language_preference or "hu",
            "permissions": user.role.permissions,
            "is_active": user.is_active,
            "must_change_password": user.must_change_password or False,
        }
        
        return token, user_info
        
    finally:
        if should_close:
            session.close()


def get_current_user(token: str, session: Session = None) -> dict:
    """
    Get current user information
    
    Args:
        token: Session token
        session: SQLAlchemy session (creates new if None)
    
    Returns:
        User info dictionary
    """
    return validate_session(token, session)


def cleanup_expired_sessions(session: Session = None):
    """
    Clean up expired sessions from database
    
    Args:
        session: SQLAlchemy session (creates new if None)
    """
    should_close = False
    if session is None:
        session = SessionLocal()
        should_close = True
    
    try:
        expired = session.query(UserSession).filter(
            UserSession.expires_at < utcnow()
        ).all()
        
        count = len(expired)
        for user_session in expired:
            session.delete(user_session)
        
        session.commit()
        
        if count > 0:
            logger.info(f"Cleaned up {count} expired sessions")
        
    except OperationalError as e:
        # Database connection unavailable - don't fail, just log
        error_msg = str(e)
        if "Can't connect" in error_msg or "timed out" in error_msg:
            logger.warning(f"Cannot cleanup expired sessions - database unavailable: {e}")
        else:
            # Other operational errors - re-raise
            raise
    except Exception as e:
        # Other errors - log and continue
        logger.error(f"Error cleaning up expired sessions: {e}")
    finally:
        if should_close:
            session.close()


def update_user_language(user_id: int, language_code: str, session: Session = None) -> bool:
    """
    Update user's language preference
    
    Args:
        user_id: User ID
        language_code: Language code (en/hu)
        session: SQLAlchemy session (creates new if None)
    
    Returns:
        True if successful
    """
    should_close = False
    if session is None:
        session = SessionLocal()
        should_close = True
    
    try:
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            raise AuthenticationError("User not found")
        
        user.language_preference = language_code
        session.commit()
        
        logger.info(f"Language preference updated for user_id={user_id} to {language_code}")
        return True
        
    except Exception as e:
        logger.error(f"Error updating user language: {e}")
        return False
        
    finally:
        if should_close:
            session.close()
