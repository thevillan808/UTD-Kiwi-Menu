from typing import List, Optional
import logging
from .. import db
from ..domain.User import User
from ..exceptions import (
    ValidationException,
    InvalidUsernameException,
    InvalidPasswordException,
    InvalidRoleException,
    DuplicateUserException,
    UniqueConstraintError,
    UserNotFoundException,
    DataAccessException,
    BusinessLogicException
)

def list_users() -> List[User]:
    """Return all users."""
    try:
        return db.query_all_users()
    except Exception as e:
        logging.error(f"Failed to retrieve users: {str(e)}")
        raise DataAccessException(f"Failed to retrieve users: {str(e)}", "USER_RETRIEVAL_FAILED")


def add_user(username: str, password: str, first_name: str, last_name: str, role: str = "user") -> bool:
    """Add a new user. Returns True if created, False if username exists or invalid input."""
    # Validate input parameters
    if not username or not isinstance(username, str) or not username.strip():
        raise InvalidUsernameException("Username must be a non-empty string", "INVALID_USERNAME")
    
    if not password or not isinstance(password, str) or not password.strip():
        raise InvalidPasswordException("Password must be a non-empty string", "INVALID_PASSWORD")
    
    if role not in ["user", "admin"]:
        raise InvalidRoleException(f"Role must be 'user' or 'admin', got '{role}'", "INVALID_ROLE")
    
    # Normalize inputs
    username = username.strip()
    password = password.strip()
    first_name = first_name.strip() if first_name else ""
    last_name = last_name.strip() if last_name else ""
    
    try:
        # Check if user already exists
        existing_user = db.query_user(username)
        if existing_user:
            raise UniqueConstraintError(f"User '{username}' already exists", "USER_ALREADY_EXISTS")
        
        # Validate balance is non-negative (default to 0.0)
        balance = 0.0
        
        user = User(username, password, first_name, last_name, balance, role=role)
        db.create_new_user(user)
        return True
        
    except (UniqueConstraintError, ValidationException):
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        logging.error(f"Failed to create user {username}: {str(e)}")
        raise DataAccessException(f"Failed to create user: {str(e)}", "USER_CREATION_FAILED")


def delete_user(username: str) -> bool:
    """Delete a user by username."""
    if not username or not isinstance(username, str) or not username.strip():
        raise InvalidUsernameException("Username must be a non-empty string", "INVALID_USERNAME")
    
    try:
        return db.delete_user(username.strip())
    except (UserNotFoundException, BusinessLogicException, ValidationException):
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        logging.error(f"Failed to delete user {username}: {str(e)}")
        raise DataAccessException(f"Failed to delete user: {str(e)}", "USER_DELETION_FAILED")


def change_role(username: str, new_role: str) -> bool:
    """Change a user's role."""
    if not username or not isinstance(username, str) or not username.strip():
        raise InvalidUsernameException("Username must be a non-empty string", "INVALID_USERNAME")
    
    if new_role not in ["user", "admin"]:
        raise InvalidRoleException(f"Role must be 'user' or 'admin', got '{new_role}'", "INVALID_ROLE")
    
    try:
        # Check if user exists
        user = db.query_user(username.strip())
        if not user:
            raise UserNotFoundException(f"User '{username}' not found", "USER_NOT_FOUND")
        
        return db.update_user_role(username.strip(), new_role)
    except (UserNotFoundException, InvalidRoleException, ValidationException):
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        logging.error(f"Failed to change role for user {username}: {str(e)}")
        raise DataAccessException(f"Failed to change user role: {str(e)}", "ROLE_CHANGE_FAILED")


def get_user(username: str) -> Optional[User]:
    """Return a user by username."""
    if not username or not isinstance(username, str) or not username.strip():
        raise InvalidUsernameException("Username must be a non-empty string", "INVALID_USERNAME")
    
    try:
        return db.query_user(username.strip())
    except ValidationException:
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        logging.error(f"Failed to retrieve user {username}: {str(e)}")
        raise DataAccessException(f"Failed to retrieve user: {str(e)}", "USER_RETRIEVAL_FAILED")