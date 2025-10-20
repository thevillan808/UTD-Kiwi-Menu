"""
Custom exception classes for the UTD-kiwi-cli application.

These exceptions provide specific error handling for different scenarios
throughout the application layers.
"""


class KiwiAppException(Exception):
    """Base exception class for all UTD-kiwi-cli application exceptions."""
    
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


# Authentication and Authorization Exceptions
class AuthenticationException(KiwiAppException):
    """Raised when authentication fails."""
    pass


class AuthorizationException(KiwiAppException):
    """Raised when user lacks permission for an operation."""
    pass


class InvalidCredentialsException(AuthenticationException):
    """Raised when username/password combination is invalid."""
    pass


class UserNotFoundException(AuthenticationException):
    """Raised when a user is not found."""
    pass


# Data Validation Exceptions
class ValidationException(KiwiAppException):
    """Base class for data validation errors."""
    pass


class InvalidUsernameException(ValidationException):
    """Raised when username format is invalid."""
    pass


class InvalidPasswordException(ValidationException):
    """Raised when password format is invalid."""
    pass


class InvalidBalanceException(ValidationException):
    """Raised when balance value is invalid (e.g., negative)."""
    pass


class InvalidRoleException(ValidationException):
    """Raised when user role is invalid."""
    pass


class InvalidPortfolioDataException(ValidationException):
    """Raised when portfolio data is invalid."""
    pass


class InvalidSecurityDataException(ValidationException):
    """Raised when security/stock data is invalid."""
    pass


class InvalidTransactionDataException(ValidationException):
    """Raised when transaction data is invalid."""
    pass


# Business Logic Exceptions
class BusinessLogicException(KiwiAppException):
    """Base class for business logic violations."""
    pass


class InsufficientFundsException(BusinessLogicException):
    """Raised when user has insufficient funds for an operation."""
    pass


class InsufficientSharesException(BusinessLogicException):
    """Raised when user tries to sell more shares than they own."""
    pass


class DuplicateUserException(BusinessLogicException):
    """Raised when trying to create a user that already exists."""
    pass


class UniqueConstraintError(BusinessLogicException):
    """Raised when a unique constraint violation occurs (e.g., duplicate username, portfolio name)."""
    pass


class DuplicatePortfolioException(BusinessLogicException):
    """Raised when trying to create a portfolio with a duplicate name for the same user."""
    pass


class SecurityNotAvailableException(BusinessLogicException):
    """Raised when a requested security/stock is not available for trading."""
    pass


class PortfolioNotFoundException(BusinessLogicException):
    """Raised when a portfolio is not found."""
    pass


class SecurityNotFoundException(BusinessLogicException):
    """Raised when a security/stock is not found."""
    pass


class AdminProtectionException(BusinessLogicException):
    """Raised when trying to perform operations that would compromise admin access."""
    pass


# Data Access Exceptions
class DataAccessException(KiwiAppException):
    """Base class for data access errors."""
    pass


class FileIOException(DataAccessException):
    """Raised when file I/O operations fail."""
    pass


class DataCorruptionException(DataAccessException):
    """Raised when data files are corrupted or contain invalid data."""
    pass


class JsonParseException(DataAccessException):
    """Raised when JSON parsing fails."""
    pass


class DataPersistenceException(DataAccessException):
    """Raised when data persistence operations fail."""
    pass


# CLI and User Interface Exceptions
class UserInterfaceException(KiwiAppException):
    """Base class for user interface errors."""
    pass


class InvalidMenuSelectionException(UserInterfaceException):
    """Raised when user makes an invalid menu selection."""
    pass


class UserCancelledException(UserInterfaceException):
    """Raised when user cancels an operation."""
    pass


class InputValidationException(UserInterfaceException):
    """Raised when user input fails validation."""
    pass


# System Exceptions
class SystemException(KiwiAppException):
    """Base class for system-level errors."""
    pass


class ConfigurationException(SystemException):
    """Raised when configuration is invalid or missing."""
    pass


class ServiceUnavailableException(SystemException):
    """Raised when a required service is unavailable."""
    pass