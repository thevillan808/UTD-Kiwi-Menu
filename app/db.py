from typing import List, Optional, Dict
from sqlalchemy.exc import IntegrityError
import bcrypt

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

# Keep track of current logged in user
_current_user = None


def hash_password(password):
    # Hash a password using bcrypt
    if password:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    return ""


def check_password(password, hashed):
    # Check if password matches the hash
    if not password or not hashed:
        return False
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except:
        return False


def convert_user_to_domain(user_model):
    # Convert database user to User object
    user = User(
        user_model.username,
        user_model.password,
        user_model.first_name,
        user_model.last_name,
        user_model.balance,
        user_model.role
    )
    # Get all holdings for this user
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


def convert_portfolio_to_domain(portfolio_model):
    # Convert database portfolio to Portfolio object
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


def get_current_user():
    return _current_user


def set_current_user(user):
    global _current_user
    _current_user = user


def authenticate(username, password):
    # Check if username and password are valid
    if not username or not password:
        raise ValidationException("Username and password required", "INVALID_INPUT")
    
    session = get_session()
    try:
        user_model = session.query(UserModel).filter_by(username=username.strip()).first()
        
        if not user_model:
            raise InvalidCredentialsException(f"User '{username}' not found", "USER_NOT_FOUND")
        
        if not check_password(password, user_model.password):
            raise InvalidCredentialsException("Invalid password", "INVALID_PASSWORD")
        
        return convert_user_to_domain(user_model)
        
    finally:
        close_session(session)


def query_user(username):
    # Find a user by username
    if not username:
        raise ValidationException("Username required", "INVALID_USERNAME")
    
    session = get_session()
    try:
        user_model = session.query(UserModel).filter_by(username=username.strip()).first()
        if not user_model:
            return None
        return convert_user_to_domain(user_model)
    finally:
        close_session(session)


def query_all_users():
    # Get all users
    session = get_session()
    try:
        user_models = session.query(UserModel).all()
        return [convert_user_to_domain(u) for u in user_models]
    finally:
        close_session(session)


def create_new_user(user):
    # Add a new user to database
    if not user or not user.username:
        raise ValidationException("Invalid user data", "INVALID_USER")
    
    session = get_session()
    try:
        # Check if user already exists
        existing = session.query(UserModel).filter_by(username=user.username.strip()).first()
        if existing:
            raise UniqueConstraintError(f"User '{user.username}' already exists", "USER_EXISTS")
        
        # Hash password if needed
        password = user.password
        if not password.startswith("$2"):
            password = hash_password(password)
        
        # Create new user
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
    except IntegrityError:
        session.rollback()
        raise UniqueConstraintError(f"User '{user.username}' already exists", "USER_EXISTS")
    except Exception as e:
        session.rollback()
        raise DataPersistenceException(f"Failed to create user: {str(e)}", "CREATE_FAILED")
    finally:
        close_session(session)


def delete_user(username):
    # Delete a user
    if not username:
        raise ValidationException("Username required", "INVALID_USERNAME")
    
    session = get_session()
    try:
        user_model = session.query(UserModel).filter_by(username=username.strip()).first()
        
        if not user_model:
            raise UserNotFoundException(f"User '{username}' not found", "USER_NOT_FOUND")
        
        # Don't delete last admin
        admin_count = session.query(UserModel).filter_by(role="admin").count()
        
        if user_model.role == "admin" and admin_count <= 1:
            raise AdminProtectionException("Cannot delete last admin", "LAST_ADMIN")
        
        session.delete(user_model)
        session.commit()
        return True
        
    except (ValidationException, UserNotFoundException, AdminProtectionException):
        session.rollback()
        raise
    except Exception as e:
        session.rollback()
        raise DataPersistenceException(f"Failed to delete user: {str(e)}", "DELETE_FAILED")
    finally:
        close_session(session)


def update_user_role(username, new_role):
    # Change user role
    session = get_session()
    try:
        user_model = session.query(UserModel).filter_by(username=username.strip()).first()
        if not user_model:
            return False
        
        user_model.role = new_role
        session.commit()
        return True
        
    except:
        session.rollback()
        return False
    finally:
        close_session(session)


def update_user_balance(username, new_balance):
    # Update user balance
    session = get_session()
    try:
        user_model = session.query(UserModel).filter_by(username=username.strip()).first()
        if not user_model:
            return False
        
        user_model.balance = new_balance
        session.commit()
        return True
        
    except:
        session.rollback()
        return False
    finally:
        close_session(session)


def create_portfolio(name, description, investment_strategy, username):
    # Create a new portfolio
    session = get_session()
    try:
        # Find the user
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
        
        return convert_portfolio_to_domain(portfolio_model)
        
    except Exception as e:
        session.rollback()
        raise DataPersistenceException(f"Failed to create portfolio: {str(e)}", "CREATE_FAILED")
    finally:
        close_session(session)


def query_portfolio(pid):
    # Find portfolio by id
    session = get_session()
    try:
        portfolio_model = session.query(PortfolioModel).filter_by(id=pid).first()
        if not portfolio_model:
            return None
        return convert_portfolio_to_domain(portfolio_model)
    finally:
        close_session(session)


def query_all_portfolios():
    # Get all portfolios
    session = get_session()
    try:
        portfolio_models = session.query(PortfolioModel).all()
        return [convert_portfolio_to_domain(p) for p in portfolio_models]
    finally:
        close_session(session)


def update_portfolio(pid, **kwargs):
    # Update portfolio info
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
        
    except:
        session.rollback()
        return False
    finally:
        close_session(session)


def delete_portfolio(pid):
    # Delete a portfolio
    session = get_session()
    try:
        portfolio_model = session.query(PortfolioModel).filter_by(id=pid).first()
        if not portfolio_model:
            return False
        
        session.delete(portfolio_model)
        session.commit()
        return True
        
    except:
        session.rollback()
        return False
    finally:
        close_session(session)


def get_or_create_security(ticker, name, reference_price):
    # Get security or create if doesn't exist
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


def query_security(ticker):
    # Find security by ticker
    session = get_session()
    try:
        return session.query(SecurityModel).filter_by(ticker=ticker.upper()).first()
    finally:
        close_session(session)


def query_all_securities():
    # Get all securities
    session = get_session()
    try:
        return session.query(SecurityModel).all()
    finally:
        close_session(session)


def record_transaction(username, portfolio_id, ticker, transaction_type, quantity, price):
    # Save a buy or sell transaction
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
        
        # Create transaction record
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
        raise DataPersistenceException(f"Failed to record transaction: {str(e)}", "TRANSACTION_FAILED")
    finally:
        close_session(session)


def query_transactions_by_user(username):
    # Get all transactions for a user
    session = get_session()
    try:
        user_model = session.query(UserModel).filter_by(username=username.strip()).first()
        if not user_model:
            return []
        return session.query(TransactionModel).filter_by(user_id=user_model.id).all()
    finally:
        close_session(session)


def query_transactions_by_portfolio(portfolio_id):
    # Get all transactions for a portfolio
    session = get_session()
    try:
        return session.query(TransactionModel).filter_by(portfolio_id=portfolio_id).all()
    finally:
        close_session(session)


def query_transactions_by_security(ticker):
    # Get all transactions for a security
    session = get_session()
    try:
        security_model = session.query(SecurityModel).filter_by(ticker=ticker.upper()).first()
        if not security_model:
            return []
        return session.query(TransactionModel).filter_by(security_id=security_model.id).all()
    finally:
        close_session(session)


def get_investment(portfolio_id, ticker):
    # Get investment for portfolio and security
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


def update_investment(portfolio_id, ticker, quantity):
    # Update or create investment holding
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
                # Delete if quantity is 0
                session.delete(investment)
            else:
                investment.quantity = quantity
        else:
            if quantity > 0:
                # Create new investment
                investment = InvestmentModel(
                    portfolio_id=portfolio_id,
                    security_id=security.id,
                    quantity=quantity
                )
                session.add(investment)
        
        session.commit()
        return True
        
    except:
        session.rollback()
        return False
    finally:
        close_session(session)


def initialize_securities(securities):
    # Add default securities to database
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
    except:
        session.rollback()
    finally:
        close_session(session)


def initialize_default_admin():
    # Create default admin user
    session = get_session()
    try:
        admin = session.query(UserModel).filter_by(username="admin").first()
        if not admin:
            admin = UserModel(
                username="admin",
                password=hash_password("admin"),
                first_name="Admin",
                last_name="User",
                balance=10000.0,
                role="admin"
            )
            session.add(admin)
            session.commit()
    except:
        session.rollback()
    finally:
        close_session(session)
