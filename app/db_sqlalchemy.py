from typing import List, Optional, Dict
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session
import bcrypt
import logging

from .database import get_session, close_session, init_db
from .models import (
    UserModel, PortfolioModel, SecurityModel, 
    InvestmentModel, TransactionModel, TransactionType
)
from .domain.User import User
from .domain.Portfolio import Portfolio
from .domain.Security import Security
from .exceptions import (
    ValidationException,
    UserNotFoundException,
    UniqueConstraintError,
    PortfolioNotFoundException,
    AdminProtectionException,
    InvalidCredentialsException,
    DataPersistenceException,
    SecurityNotFoundException
)

# Session state
_current_user: Optional[User] = None


def _hash_password(plain: str) -> str:
    """Hash plaintext password using bcrypt"""
    if plain is None:
        return ""
    if isinstance(plain, str):
        plain = plain.encode("utf-8")
    return bcrypt.hashpw(plain, bcrypt.gensalt()).decode("utf-8")


def _check_password(plain: str, hashed: str) -> bool:
    """Verify plaintext password against bcrypt hash"""
    if not plain or not hashed:
        return False
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


def _user_model_to_domain(user_model: UserModel) -> User:
    """Convert UserModel to User domain object"""
    user = User(
        user_model.username,
        user_model.password,
        user_model.first_name,
        user_model.last_name,
        user_model.balance,
        user_model.role
    )
    # Load portfolio holdings
    session = get_session()
    try:
        holdings = {}
        portfolios = session.query(PortfolioModel).filter_by(user_id=user_model.id).all()
        for portfolio in portfolios:
            for investment in portfolio.investments:
                ticker = investment.security.ticker
                if ticker in holdings:
                    holdings[ticker] += investment.quantity
                else:
                    holdings[ticker] = investment.quantity
        user.portfolio = holdings
    finally:
        close_session(session)
    return user


def _portfolio_model_to_domain(portfolio_model: PortfolioModel) -> Portfolio:
    """Convert PortfolioModel to Portfolio domain object"""
    holdings = {}
    for investment in portfolio_model.investments:
        ticker = investment.security.ticker
        holdings[ticker] = investment.quantity
    
    return Portfolio(
        portfolio_model.id,
        portfolio_model.name,
        portfolio_model.description,
        portfolio_model.investment_strategy,
        portfolio_model.owner.username,
        holdings
    )


def get_current_user() -> Optional[User]:
    """Return currently logged-in user"""
    return _current_user


def set_current_user(user: Optional[User]):
    """Set current session user"""
    global _current_user
    _current_user = user


def authenticate(username: str, password: str) -> Optional[User]:
    """
    Authenticate user by verifying password
    
    Raises:
        ValidationException: When credentials format is invalid
        InvalidCredentialsException: When credentials are invalid
    """
    if not username or not isinstance(username, str):
        raise ValidationException("Username must be a non-empty string", "INVALID_USERNAME")
    
    if not password or not isinstance(password, str):
        raise ValidationException("Password must be a non-empty string", "INVALID_PASSWORD")
    
    session = get_session()
    try:
        user_model = session.query(UserModel).filter_by(username=username.strip()).first()
        
        if not user_model:
            raise InvalidCredentialsException(f"User '{username}' not found", "USER_NOT_FOUND")
        
        if not _check_password(password, user_model.password):
            raise InvalidCredentialsException("Invalid password", "INVALID_PASSWORD")
        
        return _user_model_to_domain(user_model)
        
    finally:
        close_session(session)


def query_user(username: str) -> Optional[User]:
    """
    Return User if exists, otherwise None
    
    Raises:
        ValidationException: When username is invalid
    """
    if not username or not isinstance(username, str):
        raise ValidationException("Username must be a non-empty string", "INVALID_USERNAME")
    
    session = get_session()
    try:
        user_model = session.query(UserModel).filter_by(username=username.strip()).first()
        if not user_model:
            return None
        return _user_model_to_domain(user_model)
    finally:
        close_session(session)


def query_all_users() -> List[User]:
    """Return all users"""
    session = get_session()
    try:
        user_models = session.query(UserModel).all()
        return [_user_model_to_domain(u) for u in user_models]
    finally:
        close_session(session)


def create_new_user(user: User) -> None:
    """
    Create new user in database
    
    Raises:
        UniqueConstraintError: When user already exists
        ValidationException: When user data is invalid
        DataPersistenceException: When saving fails
    """
    if not user or not isinstance(user, User):
        raise ValidationException("User must be a valid User instance", "INVALID_USER_OBJECT")
    
    if not user.username or not user.username.strip():
        raise ValidationException("Username cannot be empty", "EMPTY_USERNAME")
    
    session = get_session()
    try:
        # Check if user exists
        existing = session.query(UserModel).filter_by(username=user.username.strip()).first()
        if existing:
            raise UniqueConstraintError(f"User '{user.username}' already exists", "USER_ALREADY_EXISTS")
        
        # Hash password if not already hashed
        password = user.password
        if not password.startswith("$2"):
            password = _hash_password(password)
        
        # Create user model
        user_model = UserModel(
            username=user.username.strip(),
            password=password,
            first_name=user.first_name,
            last_name=user.last_name,
            balance=user.balance,
            role=user.role
        )
        
        session.add(user_model)
        session.commit()
        
    except (UniqueConstraintError, ValidationException):
        session.rollback()
        raise
    except IntegrityError as e:
        session.rollback()
        raise UniqueConstraintError(f"User '{user.username}' already exists", "USER_ALREADY_EXISTS")
    except Exception as e:
        session.rollback()
        raise DataPersistenceException(f"Failed to create user: {str(e)}", "USER_CREATION_FAILED")
    finally:
        close_session(session)


def delete_user(username: str) -> bool:
    """
    Delete user if present
    
    Raises:
        ValidationException: When username is invalid
        UserNotFoundException: When user does not exist
        AdminProtectionException: When trying to delete last admin
        DataPersistenceException: When saving fails
    """
    if not username or not isinstance(username, str):
        raise ValidationException("Username must be a non-empty string", "INVALID_USERNAME")
    
    session = get_session()
    try:
        username = username.strip()
        user_model = session.query(UserModel).filter_by(username=username).first()
        
        if not user_model:
            raise UserNotFoundException(f"User '{username}' not found", "USER_NOT_FOUND")
        
        # Count admins
        admin_count = session.query(UserModel).filter_by(role="admin").count()
        
        if user_model.role == "admin" and admin_count <= 1:
            raise AdminProtectionException("Cannot delete the last admin user", "LAST_ADMIN_PROTECTION")
        
        session.delete(user_model)
        session.commit()
        return True
        
    except (ValidationException, UserNotFoundException, AdminProtectionException):
        session.rollback()
        raise
    except Exception as e:
        session.rollback()
        raise DataPersistenceException(f"Failed to delete user: {str(e)}", "USER_DELETION_FAILED")
    finally:
        close_session(session)


def update_user_role(username: str, new_role: str) -> bool:
    """Update user role"""
    session = get_session()
    try:
        user_model = session.query(UserModel).filter_by(username=username.strip()).first()
        if not user_model:
            return False
        
        user_model.role = new_role
        session.commit()
        return True
        
    except Exception:
        session.rollback()
        return False
    finally:
        close_session(session)


def update_user_balance(username: str, new_balance: float) -> bool:
    """Update user balance"""
    session = get_session()
    try:
        user_model = session.query(UserModel).filter_by(username=username.strip()).first()
        if not user_model:
            return False
        
        user_model.balance = new_balance
        session.commit()
        return True
        
    except Exception:
        session.rollback()
        return False
    finally:
        close_session(session)


def create_portfolio(name: str, description: str, investment_strategy: str, username: str) -> Portfolio:
    """Create and store new Portfolio"""
    session = get_session()
    try:
        # Find user
        user_model = session.query(UserModel).filter_by(username=username.strip()).first()
        if not user_model:
            raise UserNotFoundException(f"User '{username}' not found", "USER_NOT_FOUND")
        
        # Create portfolio
        portfolio_model = PortfolioModel(
            name=name.strip(),
            description=description.strip(),
            investment_strategy=investment_strategy.strip(),
            user_id=user_model.id
        )
        
        session.add(portfolio_model)
        session.commit()
        session.refresh(portfolio_model)
        
        return _portfolio_model_to_domain(portfolio_model)
        
    except Exception as e:
        session.rollback()
        raise DataPersistenceException(f"Failed to create portfolio: {str(e)}", "PORTFOLIO_CREATION_FAILED")
    finally:
        close_session(session)


def query_portfolio(pid: int) -> Optional[Portfolio]:
    """Query portfolio by id"""
    session = get_session()
    try:
        portfolio_model = session.query(PortfolioModel).filter_by(id=pid).first()
        if not portfolio_model:
            return None
        return _portfolio_model_to_domain(portfolio_model)
    finally:
        close_session(session)


def query_all_portfolios() -> List[Portfolio]:
    """Return all portfolios"""
    session = get_session()
    try:
        portfolio_models = session.query(PortfolioModel).all()
        return [_portfolio_model_to_domain(p) for p in portfolio_models]
    finally:
        close_session(session)


def update_portfolio(pid: int, **kwargs) -> bool:
    """Update portfolio fields"""
    session = get_session()
    try:
        portfolio_model = session.query(PortfolioModel).filter_by(id=pid).first()
        if not portfolio_model:
            return False
        
        for key, value in kwargs.items():
            if hasattr(portfolio_model, key):
                setattr(portfolio_model, key, value)
        
        session.commit()
        return True
        
    except Exception:
        session.rollback()
        return False
    finally:
        close_session(session)


def delete_portfolio(pid: int) -> bool:
    """Delete portfolio by id"""
    session = get_session()
    try:
        portfolio_model = session.query(PortfolioModel).filter_by(id=pid).first()
        if not portfolio_model:
            return False
        
        session.delete(portfolio_model)
        session.commit()
        return True
        
    except Exception:
        session.rollback()
        return False
    finally:
        close_session(session)


def get_or_create_security(ticker: str, name: str, reference_price: float) -> SecurityModel:
    """Get existing security or create new one"""
    session = get_session()
    try:
        security = session.query(SecurityModel).filter_by(ticker=ticker.upper()).first()
        if not security:
            security = SecurityModel(
                ticker=ticker.upper(),
                name=name,
                reference_price=reference_price
            )
            session.add(security)
            session.commit()
            session.refresh(security)
        return security
    finally:
        close_session(session)


def query_security(ticker: str) -> Optional[SecurityModel]:
    """Query security by ticker"""
    session = get_session()
    try:
        return session.query(SecurityModel).filter_by(ticker=ticker.upper()).first()
    finally:
        close_session(session)


def query_all_securities() -> List[SecurityModel]:
    """Return all securities"""
    session = get_session()
    try:
        return session.query(SecurityModel).all()
    finally:
        close_session(session)


def record_transaction(
    username: str,
    portfolio_id: int,
    ticker: str,
    transaction_type: str,
    quantity: int,
    price: float
) -> TransactionModel:
    """
    Record a buy or sell transaction
    
    Returns:
        TransactionModel: The created transaction record
    """
    session = get_session()
    try:
        # Get user
        user_model = session.query(UserModel).filter_by(username=username.strip()).first()
        if not user_model:
            raise UserNotFoundException(f"User '{username}' not found", "USER_NOT_FOUND")
        
        # Get portfolio
        portfolio_model = session.query(PortfolioModel).filter_by(id=portfolio_id).first()
        if not portfolio_model:
            raise PortfolioNotFoundException(f"Portfolio {portfolio_id} not found", "PORTFOLIO_NOT_FOUND")
        
        # Get security
        security_model = session.query(SecurityModel).filter_by(ticker=ticker.upper()).first()
        if not security_model:
            raise SecurityNotFoundException(f"Security '{ticker}' not found", "SECURITY_NOT_FOUND")
        
        # Create transaction
        trans_type = TransactionType.BUY if transaction_type.upper() == "BUY" else TransactionType.SELL
        transaction = TransactionModel(
            user_id=user_model.id,
            portfolio_id=portfolio_id,
            security_id=security_model.id,
            transaction_type=trans_type,
            quantity=quantity,
            price=price
        )
        
        session.add(transaction)
        session.commit()
        session.refresh(transaction)
        
        return transaction
        
    except Exception as e:
        session.rollback()
        if isinstance(e, (UserNotFoundException, PortfolioNotFoundException, SecurityNotFoundException)):
            raise
        raise DataPersistenceException(f"Failed to record transaction: {str(e)}", "TRANSACTION_CREATION_FAILED")
    finally:
        close_session(session)


def query_transactions_by_user(username: str) -> List[TransactionModel]:
    """Query all transactions for a user"""
    session = get_session()
    try:
        user_model = session.query(UserModel).filter_by(username=username.strip()).first()
        if not user_model:
            return []
        return session.query(TransactionModel).filter_by(user_id=user_model.id).all()
    finally:
        close_session(session)


def query_transactions_by_portfolio(portfolio_id: int) -> List[TransactionModel]:
    """Query all transactions for a portfolio"""
    session = get_session()
    try:
        return session.query(TransactionModel).filter_by(portfolio_id=portfolio_id).all()
    finally:
        close_session(session)


def query_transactions_by_security(ticker: str) -> List[TransactionModel]:
    """Query all transactions for a security"""
    session = get_session()
    try:
        security_model = session.query(SecurityModel).filter_by(ticker=ticker.upper()).first()
        if not security_model:
            return []
        return session.query(TransactionModel).filter_by(security_id=security_model.id).all()
    finally:
        close_session(session)


def get_investment(portfolio_id: int, ticker: str) -> Optional[InvestmentModel]:
    """Get investment for a portfolio and security"""
    session = get_session()
    try:
        security = session.query(SecurityModel).filter_by(ticker=ticker.upper()).first()
        if not security:
            return None
        
        return session.query(InvestmentModel).filter_by(
            portfolio_id=portfolio_id,
            security_id=security.id
        ).first()
    finally:
        close_session(session)


def update_investment(portfolio_id: int, ticker: str, quantity: int) -> bool:
    """Update or create investment"""
    session = get_session()
    try:
        security = session.query(SecurityModel).filter_by(ticker=ticker.upper()).first()
        if not security:
            return False
        
        investment = session.query(InvestmentModel).filter_by(
            portfolio_id=portfolio_id,
            security_id=security.id
        ).first()
        
        if investment:
            if quantity <= 0:
                session.delete(investment)
            else:
                investment.quantity = quantity
        else:
            if quantity > 0:
                investment = InvestmentModel(
                    portfolio_id=portfolio_id,
                    security_id=security.id,
                    quantity=quantity
                )
                session.add(investment)
        
        session.commit()
        return True
        
    except Exception:
        session.rollback()
        return False
    finally:
        close_session(session)


def initialize_securities(securities: Dict[str, tuple]):
    """Initialize default securities in database"""
    session = get_session()
    try:
        for ticker, (name, price) in securities.items():
            existing = session.query(SecurityModel).filter_by(ticker=ticker.upper()).first()
            if not existing:
                security = SecurityModel(
                    ticker=ticker.upper(),
                    name=name,
                    reference_price=price
                )
                session.add(security)
        session.commit()
    except Exception as e:
        session.rollback()
        logging.warning(f"Failed to initialize securities: {str(e)}")
    finally:
        close_session(session)


def initialize_default_admin():
    """Initialize default admin user if not exists"""
    session = get_session()
    try:
        admin = session.query(UserModel).filter_by(username="admin").first()
        if not admin:
            admin = UserModel(
                username="admin",
                password=_hash_password("admin"),
                first_name="Admin",
                last_name="User",
                balance=10000.0,
                role="admin"
            )
            session.add(admin)
            session.commit()
    except Exception as e:
        session.rollback()
        logging.warning(f"Failed to initialize admin: {str(e)}")
    finally:
        close_session(session)
