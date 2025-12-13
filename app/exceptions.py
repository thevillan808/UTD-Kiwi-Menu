class KiwiAppException(Exception):
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class AuthenticationException(KiwiAppException):
    pass


class AuthorizationException(KiwiAppException):
    pass


class InvalidCredentialsException(AuthenticationException):
    pass


class UserNotFoundException(AuthenticationException):
    pass


class ValidationException(KiwiAppException):
    pass


class InvalidUsernameException(ValidationException):
    pass


class InvalidPasswordException(ValidationException):
    pass


class InvalidBalanceException(ValidationException):
    pass


class InvalidRoleException(ValidationException):
    pass


class InvalidPortfolioDataException(ValidationException):
    pass


class InvalidSecurityDataException(ValidationException):
    pass


class InvalidTransactionDataException(ValidationException):
    pass


class BusinessLogicException(KiwiAppException):
    pass


class InsufficientFundsException(BusinessLogicException):
    pass


class InsufficientSharesException(BusinessLogicException):
    pass


class DuplicateUserException(BusinessLogicException):
    pass


class UniqueConstraintError(BusinessLogicException):
    pass


class DuplicatePortfolioException(BusinessLogicException):
    pass


class SecurityNotAvailableException(BusinessLogicException):
    pass


class PortfolioNotFoundException(BusinessLogicException):
    pass


class SecurityNotFoundException(BusinessLogicException):
    pass


class AdminProtectionException(BusinessLogicException):
    pass


class DataAccessException(KiwiAppException):
    pass


class FileIOException(DataAccessException):
    pass


class DataCorruptionException(DataAccessException):
    pass


class JsonParseException(DataAccessException):
    pass


class DataPersistenceException(DataAccessException):
    pass


class UserInterfaceException(KiwiAppException):
    pass


class InvalidMenuSelectionException(UserInterfaceException):
    pass


class UserCancelledException(UserInterfaceException):
    pass


class InputValidationException(UserInterfaceException):
    pass


class SystemException(KiwiAppException):
    pass


class ConfigurationException(SystemException):
    pass


class ServiceUnavailableException(SystemException):
    pass
