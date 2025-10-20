from typing import Dict, Any
from ..exceptions import (
    ValidationException,
    InvalidUsernameException,
    InvalidPasswordException,
    InvalidBalanceException,
    InvalidRoleException,
    DataCorruptionException
)


class User:
    def __init__(self, username: str, password: str, first_name: str, last_name: str, balance: float, role: str = "user"):
        """User domain model."""
        # Validate username
        if not username or not isinstance(username, str) or not username.strip():
            raise InvalidUsernameException("Username must be a non-empty string", "INVALID_USERNAME")
        
        # Validate password
        if not password or not isinstance(password, str):
            raise InvalidPasswordException("Password must be a non-empty string", "INVALID_PASSWORD")
        
        # Validate role
        if role not in ["user", "admin"]:
            raise InvalidRoleException(f"Role must be 'user' or 'admin', got '{role}'", "INVALID_ROLE")
        
        # Validate balance
        try:
            balance_float = float(balance) if balance is not None else 0.0
            if balance_float < 0:
                raise InvalidBalanceException("Balance cannot be negative", "NEGATIVE_BALANCE")
        except (ValueError, TypeError):
            raise InvalidBalanceException("Balance must be a valid number", "INVALID_BALANCE_TYPE")
        
        self.username = username.strip()
        self.password = password
        self.first_name = first_name.strip() if first_name else ""
        self.last_name = last_name.strip() if last_name else ""
        self.balance = balance_float
        self.role = role
        self.portfolio = {}

    def __str__(self):
        """String representation for debugging."""
        return (
            f"<user: username={self.username}; name={self.last_name}, {self.first_name}; "
            f"balance={self.balance}; role={self.role}>"
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize user to dictionary."""
        return {
            "username": self.username,
            "password": self.password,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "balance": self.balance,
            "role": self.role,
            "portfolio": getattr(self, "portfolio", {}),
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "User":
        """Deserialize a user from a dictionary."""
        try:
            if not isinstance(d, dict):
                raise DataCorruptionException("User data must be a dictionary", "INVALID_USER_DATA_TYPE")
            
            # Validate required fields
            if "username" not in d:
                raise DataCorruptionException("Missing required field: username", "MISSING_USERNAME")
            
            if "password" not in d:
                raise DataCorruptionException("Missing required field: password", "MISSING_PASSWORD")
            
            # Handle both old (firstname/lastname) and new (first_name/last_name) format
            first_name = d.get("first_name") or d.get("firstname", "")
            last_name = d.get("last_name") or d.get("lastname", "")
            
            # Create user with validation
            u = User(
                d.get("username"),
                d.get("password"),
                first_name,
                last_name,
                d.get("balance", 0.0),
                d.get("role", "user"),
            )
            u.portfolio = d.get("portfolio", {}) or {}
            return u
            
        except (InvalidUsernameException, InvalidPasswordException, InvalidBalanceException, 
                InvalidRoleException, DataCorruptionException):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            raise DataCorruptionException(f"Failed to deserialize user data: {str(e)}", "USER_DESERIALIZATION_FAILED")