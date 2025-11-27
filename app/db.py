from typing import Dict, List, Optional
import json
from pathlib import Path
import bcrypt
import logging
from .domain.User import User
from .domain.Portfolio import Portfolio
from .exceptions import (
    DataAccessException,
    FileIOException,
    JsonParseException,
    DataCorruptionException,
    DataPersistenceException,
    ValidationException,
    UserNotFoundException,
    DuplicateUserException,
    UniqueConstraintError,
    PortfolioNotFoundException,
    AdminProtectionException,
    AuthenticationException,
    InvalidCredentialsException
)

DATA_FILE = Path(__file__).parent / "users.json"
PORTFOLIO_FILE = Path(__file__).parent / "portfolios.json"

# Toggle persistence - False for testing
PERSIST = False

# In-memory stores
_users: Dict[str, User] = {}
_current_user: Optional[User] = None
_portfolios: Dict[int, Portfolio] = {}


def _load() -> None:
    """
    Load users and portfolios from disk or initialize defaults.
    
    Raises:
        DataAccessException: When data loading fails critically
        FileIOException: When file operations fail
        JsonParseException: When JSON parsing fails
        DataCorruptionException: When data is corrupted
    """
    global _users
    
    if not PERSIST:
        # persistence disabled: initialize default in-memory admin
        try:
            _users = {"admin": User("admin", "admin", "admin", "admin", 9000.0, role="admin")}
            # ensure admin password is hashed in-memory
            for u in _users.values():
                if not (getattr(u, "password", "") or "").startswith("$2"):
                    u.password = _hash_password(u.password)
        except Exception as e:
            raise DataAccessException(f"Failed to initialize default admin user: {str(e)}", "INIT_ADMIN_FAILED")
        return

    if not DATA_FILE.exists():
        # initialize with admin
        try:
            _users = {"admin": User("admin", "admin", "admin", "admin", 10000.0, role="admin")}
            # ensure admin password is hashed on first save
            for u in _users.values():
                if not (getattr(u, "password", "") or "").startswith("$2"):
                    u.password = _hash_password(u.password)
            if PERSIST:
                _save()
        except Exception as e:
            raise DataAccessException(f"Failed to initialize and save default admin user: {str(e)}", "INIT_SAVE_FAILED")
        return
    
    try:
        if PERSIST:
            try:
                with DATA_FILE.open("r", encoding="utf-8") as f:
                    data = json.load(f)
            except (IOError, OSError) as e:
                raise FileIOException(f"Failed to read users data file: {str(e)}", "USER_FILE_READ_FAILED")
            except json.JSONDecodeError as e:
                raise JsonParseException(f"Invalid JSON in users data file: {str(e)}", "USER_JSON_INVALID")
            
            try:
                _users = {u["username"]: User.from_dict(u) for u in data}
            except (KeyError, TypeError, ValueError) as e:
                raise DataCorruptionException(f"Corrupted user data structure: {str(e)}", "USER_DATA_CORRUPTED")
            
            # Proactively migrate any plaintext passwords to bcrypt hashed passwords
            try:
                migrated = False
                for u in _users.values():
                    stored = getattr(u, "password", "") or ""
                    if stored and not stored.startswith("$2"):
                        u.password = _hash_password(stored)
                        migrated = True
                if migrated and PERSIST:
                    _save()
            except Exception as e:
                logging.warning(f"Password migration failed: {str(e)}")
        else:
            # when persistence is disabled, start with default admin
            _users = {"admin": User("admin", "admin", "admin", "admin", 8000.0, role="admin")}
    except (FileIOException, JsonParseException, DataCorruptionException):
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        # if load fails with unexpected error, fall back to admin-only but log the issue
        logging.error(f"Unexpected error during user data load: {str(e)}")
        _users = {"admin": User("admin", "admin", "admin", "admin", 5000.0, role="admin")}

    # load portfolios if present and persistence enabled
    if PERSIST:
        try:
            if PORTFOLIO_FILE.exists():
                try:
                    with PORTFOLIO_FILE.open("r", encoding="utf-8") as f:
                        pdata = json.load(f)
                except (IOError, OSError) as e:
                    raise FileIOException(f"Failed to read portfolios data file: {str(e)}", "PORTFOLIO_FILE_READ_FAILED")
                except json.JSONDecodeError as e:
                    raise JsonParseException(f"Invalid JSON in portfolios data file: {str(e)}", "PORTFOLIO_JSON_INVALID")
                
                try:
                    for p in pdata:
                        port = Portfolio.from_dict(p)
                        _portfolios[port.id] = port
                except (KeyError, TypeError, ValueError) as e:
                    raise DataCorruptionException(f"Corrupted portfolio data structure: {str(e)}", "PORTFOLIO_DATA_CORRUPTED")
        except (FileIOException, JsonParseException, DataCorruptionException):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # ignore portfolio load errors for non-critical failures
            logging.warning(f"Portfolio load failed with unexpected error: {str(e)}")
            _portfolios.clear()


def _save() -> None:
    """
    Persist users and portfolios to disk if persistence is enabled.
    
    Raises:
        DataPersistenceException: When save operations fail
        FileIOException: When file operations fail
    """
    if not PERSIST:
        return
    
    # Save users
    try:
        user_data = [u.to_dict() for u in _users.values()]
        with DATA_FILE.open("w", encoding="utf-8") as f:
            json.dump(user_data, f, indent=2)
    except (IOError, OSError) as e:
        raise FileIOException(f"Failed to write users data file: {str(e)}", "USER_FILE_WRITE_FAILED")
    except (TypeError, ValueError) as e:
        raise DataPersistenceException(f"Failed to serialize user data: {str(e)}", "USER_SERIALIZATION_FAILED")
    except Exception as e:
        raise DataPersistenceException(f"Unexpected error saving users: {str(e)}", "USER_SAVE_UNEXPECTED")

    # Save portfolios
    try:
        portfolio_data = [p.to_dict() for p in _portfolios.values()]
        with PORTFOLIO_FILE.open("w", encoding="utf-8") as f:
            json.dump(portfolio_data, f, indent=2)
    except (IOError, OSError) as e:
        raise FileIOException(f"Failed to write portfolios data file: {str(e)}", "PORTFOLIO_FILE_WRITE_FAILED")
    except (TypeError, ValueError) as e:
        raise DataPersistenceException(f"Failed to serialize portfolio data: {str(e)}", "PORTFOLIO_SERIALIZATION_FAILED")
    except Exception as e:
        raise DataPersistenceException(f"Unexpected error saving portfolios: {str(e)}", "PORTFOLIO_SAVE_UNEXPECTED")


def _hash_password(plain: str) -> str:
    """Hash a plaintext password using bcrypt."""
    if plain is None:
        return ""
    if isinstance(plain, str):
        plain = plain.encode("utf-8")
    return bcrypt.hashpw(plain, bcrypt.gensalt()).decode("utf-8")


def _check_password(plain: str, hashed: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    if not plain or not hashed:
        return False
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


_load()


def get_current_user() -> Optional[User]:
    """Return the currently logged-in user."""
    return _current_user


def set_current_user(user: Optional[User]):
    """Set the current in-memory session user."""
    global _current_user
    _current_user = user


def query_all_users() -> List[User]:
    """Return all users in memory."""
    return list(_users.values())


def _next_portfolio_id() -> int:
    # start IDs at 0 for the first portfolio
    if not _portfolios:
        return 0
    return max(_portfolios.keys()) + 1


def create_portfolio(name: str, description: str, investment_strategy: str, username: str) -> Portfolio:
    """Create and store a new Portfolio object."""
    pid = _next_portfolio_id()
    p = Portfolio(pid, name, description, investment_strategy, username, holdings={})
    _portfolios[pid] = p
    _save()
    return p


def query_portfolio(pid: int) -> Optional[Portfolio]:
    """Query a portfolio by id."""
    return _portfolios.get(pid)


def query_all_portfolios() -> List[Portfolio]:
    """
    Return all portfolios.

    @return: list of Portfolio objects
    """
    return list(_portfolios.values())


def update_portfolio(pid: int, **kwargs) -> bool:
    """
    Update portfolio fields without permission checks (low-level data op).

    @param pid: portfolio id
    @param kwargs: fields to set
    @return: True if updated, False if not found
    """
    p = _portfolios.get(pid)
    if not p:
        return False
    for k, v in kwargs.items():
        if hasattr(p, k):
            setattr(p, k, v)
    _save()
    return True


def delete_portfolio(pid: int) -> bool:
    """
    Delete a portfolio by id.

    @param pid: portfolio id
    @return: True if deleted, False if not found
    """
    if pid in _portfolios:
        del _portfolios[pid]
        _save()
        return True
    return False


def query_user(username: str) -> Optional[User]:
    """
    Return the User if it exists, otherwise None.

    @param username: username
    @return: User or None
    
    Raises:
        ValidationException: When username is invalid
    """
    if not username or not isinstance(username, str):
        raise ValidationException("Username must be a non-empty string", "INVALID_USERNAME")
    
    return _users.get(username.strip())


def create_new_user(user: User) -> None:
    """
    Create a new user object in the in-memory store and persist if enabled.

    @param user: User instance (password may be plaintext; will be hashed)
    @return: None
    
    Raises:
        UniqueConstraintError: When user already exists
        ValidationException: When user data is invalid
        DataPersistenceException: When saving fails
    """
    if not user or not isinstance(user, User):
        raise ValidationException("User must be a valid User instance", "INVALID_USER_OBJECT")
    
    if not user.username or not user.username.strip():
        raise ValidationException("Username cannot be empty", "EMPTY_USERNAME")
    
    username = user.username.strip()
    if username in _users:
        raise UniqueConstraintError(f"User '{username}' already exists", "USER_ALREADY_EXISTS")
    
    try:
        # ensure password is hashed before saving
        if not (getattr(user, "password", "") or "").startswith("$2"):
            user.password = _hash_password(user.password)
        _users[username] = user
        _save()
    except (DataPersistenceException, FileIOException):
        # Remove user from memory if save failed
        if username in _users:
            del _users[username]
        raise
    except Exception as e:
        # Remove user from memory if save failed
        if username in _users:
            del _users[username]
        raise DataPersistenceException(f"Failed to create user: {str(e)}", "USER_CREATION_FAILED")


def delete_user(username: str) -> bool:
    """
    Delete the user if present. Prevent deletion if it would leave no admins.

    @param username: username to delete
    @return: True if deleted, False otherwise
    
    Raises:
        ValidationException: When username is invalid
        UserNotFoundException: When user does not exist
        AdminProtectionException: When trying to delete the last admin
        DataPersistenceException: When saving fails
    """
    if not username or not isinstance(username, str):
        raise ValidationException("Username must be a non-empty string", "INVALID_USERNAME")
    
    username = username.strip()
    user_to_delete = _users.get(username)
    
    if not user_to_delete:
        raise UserNotFoundException(f"User '{username}' not found", "USER_NOT_FOUND")
    
    # Count current admins 
    admin_count = sum(1 for user in _users.values() if user.role == "admin")
    
    # If this is an admin and deleting would leave < 1 admin, prevent deletion
    if user_to_delete.role == "admin" and admin_count <= 1:
        raise AdminProtectionException("Cannot delete the last admin user", "LAST_ADMIN_PROTECTION")
    
    try:
        del _users[username]
        _save()
        return True
    except (DataPersistenceException, FileIOException):
        # Restore user if save failed
        _users[username] = user_to_delete
        raise
    except Exception as e:
        # Restore user if save failed
        _users[username] = user_to_delete
        raise DataPersistenceException(f"Failed to delete user: {str(e)}", "USER_DELETION_FAILED")


def update_user_role(username: str, new_role: str) -> bool:
    """
    Update a user's role.

    @param username: username
    @param new_role: role string
    @return: True if updated, False otherwise
    """
    user = _users.get(username)
    if not user:
        return False
    user.role = new_role
    _save()
    return True


def authenticate(username: str, password: str) -> Optional[User]:
    """
    Authenticate a user by verifying the provided password.
    
    @param username: Username to authenticate
    @param password: Password to verify
    @return: User object if authentication successful, None otherwise
    
    Raises:
        ValidationException: When credentials format is invalid
        InvalidCredentialsException: When credentials are invalid
    """
    if not username or not isinstance(username, str):
        raise ValidationException("Username must be a non-empty string", "INVALID_USERNAME")
    
    if not password or not isinstance(password, str):
        raise ValidationException("Password must be a non-empty string", "INVALID_PASSWORD")
    
    try:
        user = query_user(username)
        if not user:
            raise InvalidCredentialsException(f"User '{username}' not found", "USER_NOT_FOUND")
        
        # Support migrated plaintext entries
        stored = getattr(user, "password", "") or ""
        if stored.startswith("$2"):
            ok = _check_password(password, stored)
            if not ok:
                raise InvalidCredentialsException("Invalid password", "INVALID_PASSWORD")
            return user
        else:
            # stored appears to be plaintext — verify directly and upgrade to hashed
            if stored == password:
                try:
                    # re-hash stored plaintext and persist
                    user.password = _hash_password(stored)
                    _save()
                except Exception as e:
                    logging.warning(f"Failed to upgrade password hash for user {username}: {str(e)}")
                return user
            else:
                raise InvalidCredentialsException("Invalid password", "INVALID_PASSWORD")
    except (ValidationException, InvalidCredentialsException):
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        raise AuthenticationException(f"Authentication failed due to system error: {str(e)}", "AUTH_SYSTEM_ERROR")
