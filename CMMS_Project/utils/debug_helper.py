"""
Centralized Debug System
Provides detailed step-by-step debugging for the entire application.
Only active when DEBUG=True in app_config.py
"""

import os
import sys
import traceback
import inspect
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Dict, Callable
from functools import wraps
from contextlib import contextmanager

# Import LOGS_DIR (but not DEBUG - we'll read it dynamically)
try:
    from config.app_config import LOGS_DIR, PROJECT_ROOT
except ImportError:
    LOGS_DIR = Path("data/logs")
    PROJECT_ROOT = Path(__file__).parent.parent

# Try to load dotenv if available
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

# Debug log file
DEBUG_LOG_FILE = LOGS_DIR / "debug.log"

# Ensure log directory exists
try:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
except (PermissionError, OSError):
    # Fallback to temp directory
    import tempfile
    LOGS_DIR = Path(tempfile.gettempdir()) / "cmms_debug"
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    DEBUG_LOG_FILE = LOGS_DIR / "debug.log"


class DebugLevel:
    """Debug message levels"""
    ENTRY = "ENTRY"
    EXIT = "EXIT"
    STEP = "STEP"
    VARIABLE = "VARIABLE"
    CALL = "CALL"
    RETURN = "RETURN"
    ERROR = "ERROR"
    EXCEPTION = "EXCEPTION"
    UI = "UI"
    DB = "DB"
    SERVICE = "SERVICE"


class DebugHelper:
    """Centralized debug logging helper"""
    
    _enabled = None
    _log_file = None
    
    @classmethod
    def is_enabled(cls) -> bool:
        """Check if debug mode is enabled - dynamically checks each time from .env file"""
        # First try to read from environment variable (if set)
        debug_value = os.getenv("DEBUG")
        if debug_value:
            return debug_value.lower() == "true"
        
        # If not in environment, try to read from .env file directly
        # This allows DEBUG to be changed via .env file without restarting the app
        try:
            # Try to find .env file
            env_file = PROJECT_ROOT / ".env"
            if not env_file.exists():
                # Try in parent directory
                env_file = PROJECT_ROOT.parent / ".env"
            
            if env_file.exists():
                with open(env_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, value = line.split("=", 1)
                            if key.strip() == "DEBUG":
                                return value.strip().strip('"').strip("'").lower() == "true"
        except Exception:
            # If reading .env fails, fall back to default
            pass
        
        # Default to False if not found
        return False
    
    @classmethod
    def _get_log_file(cls):
        """Get or create log file handle"""
        if cls._log_file is None:
            try:
                cls._log_file = open(DEBUG_LOG_FILE, "a", encoding="utf-8")
            except (PermissionError, OSError):
                # Fallback to stderr if file can't be opened
                cls._log_file = sys.stderr
        return cls._log_file
    
    @classmethod
    def _format_message(
        cls,
        level: str,
        module: str,
        function: str,
        message: str,
        data: Optional[Dict[str, Any]] = None
    ) -> str:
        """Format debug message"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        
        parts = [
            f"[DEBUG]",
            f"[{timestamp}]",
            f"[{module}]",
            f"[{function}]",
            f"[{level}]",
            f"{message}"
        ]
        
        if data:
            import json
            try:
                # Convert data to JSON, handling non-serializable objects
                data_str = json.dumps(data, default=str, indent=2, ensure_ascii=False)
                parts.append(f"\n[DATA]\n{data_str}")
            except Exception:
                parts.append(f"\n[DATA]\n{str(data)}")
        
        return " ".join(parts)
    
    @classmethod
    def log(
        cls,
        level: str,
        module: str,
        function: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        exception: Optional[Exception] = None
    ):
        """Log a debug message"""
        is_enabled = cls.is_enabled()
        
        # Always print debug status for troubleshooting (only first time)
        if not is_enabled:
            # Print warning that debug is disabled (only once to avoid spam)
            if not hasattr(cls, '_warned_disabled'):
                print(f"[DEBUG WARNING] Debug logging is DISABLED. Set DEBUG=True in .env or app_config.py to enable.", flush=True)
                cls._warned_disabled = True
            return
        
        formatted = cls._format_message(level, module, function, message, data)
        
        # Add exception traceback if provided
        if exception:
            formatted += f"\n[EXCEPTION]\n{''.join(traceback.format_exception(type(exception), exception, exception.__traceback__))}"
        
        # Write to console (force flush to ensure output appears immediately)
        print(formatted, flush=True)
        sys.stdout.flush()  # Force flush stdout
        
        # Write to file
        try:
            log_file = cls._get_log_file()
            log_file.write(formatted + "\n")
            log_file.flush()
        except Exception as e:
            # If file write fails, print error to console
            print(f"[DEBUG ERROR] Failed to write to log file: {e}", flush=True)
            pass
    
    @classmethod
    def log_entry(cls, module: str, function: str, params: Optional[Dict[str, Any]] = None):
        """Log function entry"""
        cls.log(DebugLevel.ENTRY, module, function, f"Entering {function}", {"params": params})
    
    @classmethod
    def log_exit(cls, module: str, function: str, return_value: Any = None):
        """Log function exit"""
        cls.log(DebugLevel.EXIT, module, function, f"Exiting {function}", {"return": return_value})
    
    @classmethod
    def log_step(cls, module: str, function: str, step: str, data: Optional[Dict[str, Any]] = None):
        """Log a step within a function"""
        cls.log(DebugLevel.STEP, module, function, step, data)
    
    @classmethod
    def log_variable(cls, module: str, function: str, var_name: str, var_value: Any):
        """Log a variable value"""
        cls.log(DebugLevel.VARIABLE, module, function, f"Variable: {var_name}", {"value": var_value})
    
    @classmethod
    def log_call(cls, module: str, function: str, called_function: str, params: Optional[Dict[str, Any]] = None):
        """Log a function call"""
        cls.log(DebugLevel.CALL, module, function, f"Calling: {called_function}", {"params": params})
    
    @classmethod
    def log_return(cls, module: str, function: str, called_function: str, return_value: Any):
        """Log a function return"""
        cls.log(DebugLevel.RETURN, module, function, f"Return from: {called_function}", {"return": return_value})
    
    @classmethod
    def log_error(cls, module: str, function: str, error: str, data: Optional[Dict[str, Any]] = None):
        """Log an error"""
        cls.log(DebugLevel.ERROR, module, function, f"ERROR: {error}", data)
    
    @classmethod
    def log_exception(cls, module: str, function: str, exception: Exception, context: Optional[Dict[str, Any]] = None):
        """Log an exception with full traceback"""
        cls.log(DebugLevel.EXCEPTION, module, function, f"EXCEPTION: {type(exception).__name__}: {str(exception)}", context, exception=exception)
    
    @classmethod
    def log_ui(cls, module: str, function: str, action: str, data: Optional[Dict[str, Any]] = None):
        """Log UI-related actions"""
        cls.log(DebugLevel.UI, module, function, f"UI: {action}", data)
    
    @classmethod
    def log_db(cls, module: str, function: str, query: str, params: Optional[Dict[str, Any]] = None):
        """Log database operations"""
        cls.log(DebugLevel.DB, module, function, f"DB: {query}", params)
    
    @classmethod
    def log_service(cls, module: str, function: str, service_call: str, params: Optional[Dict[str, Any]] = None):
        """Log service calls"""
        cls.log(DebugLevel.SERVICE, module, function, f"SERVICE: {service_call}", params)


def debug_function(func: Callable) -> Callable:
    """Decorator for automatic function debugging"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not DebugHelper.is_enabled():
            return func(*args, **kwargs)
        
        # Get module and function name
        module = func.__module__ if hasattr(func, '__module__') else 'unknown'
        function_name = func.__name__
        
        # Prepare parameters
        params = {}
        if args:
            # Try to get parameter names
            try:
                sig = inspect.signature(func)
                param_names = list(sig.parameters.keys())
                for i, arg in enumerate(args):
                    if i < len(param_names):
                        param_name = param_names[i]
                        # Try to serialize, fallback to string representation
                        try:
                            import json
                            json.dumps(arg, default=str)
                            params[param_name] = arg
                        except:
                            params[param_name] = str(type(arg).__name__)
            except:
                params['args'] = [str(type(a).__name__) for a in args]
        
        if kwargs:
            params.update({k: v for k, v in kwargs.items()})
        
        DebugHelper.log_entry(module, function_name, params)
        
        try:
            result = func(*args, **kwargs)
            DebugHelper.log_exit(module, function_name, result)
            return result
        except Exception as e:
            DebugHelper.log_exception(module, function_name, e, {"args": str(args), "kwargs": str(kwargs)})
            raise
    
    return wrapper


@contextmanager
def debug_context(module: str, function: str, context_name: str, data: Optional[Dict[str, Any]] = None):
    """Context manager for debugging code blocks"""
    if not DebugHelper.is_enabled():
        yield
        return
    
    DebugHelper.log_step(module, function, f"Entering context: {context_name}", data)
    try:
        yield
        DebugHelper.log_step(module, function, f"Exiting context: {context_name}")
    except Exception as e:
        DebugHelper.log_exception(module, function, e, {"context": context_name})
        raise


# Convenience functions
def is_debug_enabled() -> bool:
    """Check if debug mode is enabled"""
    return DebugHelper.is_enabled()


def debug_log(level: str, module: str, function: str, message: str, data: Optional[Dict[str, Any]] = None):
    """Log a debug message"""
    DebugHelper.log(level, module, function, message, data)


def debug_entry(module: str, function: str, params: Optional[Dict[str, Any]] = None):
    """Log function entry"""
    DebugHelper.log_entry(module, function, params)


def debug_exit(module: str, function: str, return_value: Any = None):
    """Log function exit"""
    DebugHelper.log_exit(module, function, return_value)


def debug_step(module: str, function: str, step: str, data: Optional[Dict[str, Any]] = None):
    """Log a step"""
    DebugHelper.log_step(module, function, step, data)


def debug_variable(module: str, function: str, var_name: str, var_value: Any):
    """Log a variable"""
    DebugHelper.log_variable(module, function, var_name, var_value)


def debug_call(module: str, function: str, called_function: str, params: Optional[Dict[str, Any]] = None):
    """Log a function call"""
    DebugHelper.log_call(module, function, called_function, params)


def debug_return(module: str, function: str, called_function: str, return_value: Any):
    """Log a function return"""
    DebugHelper.log_return(module, function, called_function, return_value)


def debug_error(module: str, function: str, error: str, data: Optional[Dict[str, Any]] = None):
    """Log an error"""
    DebugHelper.log_error(module, function, error, data)


def debug_exception(module: str, function: str, exception: Exception, context: Optional[Dict[str, Any]] = None):
    """Log an exception"""
    DebugHelper.log_exception(module, function, exception, context)


def debug_ui(module: str, function: str, action: str, data: Optional[Dict[str, Any]] = None):
    """Log UI action"""
    DebugHelper.log_ui(module, function, action, data)


def debug_db(module: str, function: str, query: str, params: Optional[Dict[str, Any]] = None):
    """Log database operation"""
    DebugHelper.log_db(module, function, query, params)


def debug_service(module: str, function: str, service_call: str, params: Optional[Dict[str, Any]] = None):
    """Log service call"""
    DebugHelper.log_service(module, function, service_call, params)

