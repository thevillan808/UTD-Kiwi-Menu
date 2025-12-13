import logging
import traceback
from .db import db
from .models import (
    UserModel, PortfolioModel, SecurityModel, 
    InvestmentModel, TransactionModel, TransactionType
)
from .domain.User import User as DomainUser
from .domain.Portfolio import Portfolio as DomainPortfolio
from .domain.Security import Security as DomainSecurity
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
import bcrypt
from sqlalchemy.exc import IntegrityError

def hash_password(password):
    if password:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    return ""

def check_password(password, hashed):
    if not password or not hashed:
        return False
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        return False

def convert_user_to_domain(user_model):
    user = DomainUser(
        user_model.username,
        user_model.password,
        user_model.first_name,
        user_model.last_name,
        user_model.balance,
        user_model.role
    )
    holdings = {}
    portfolios = db.session.query(PortfolioModel).filter_by(user_id=user_model.id).all()
    for portfolio in portfolios:
        investments = getattr(portfolio, 'investments', [])
        for investment in investments:
            ticker = investment.security.ticker
            if ticker in holdings:
                holdings[ticker] += investment.quantity
            else:
                holdings[ticker] = investment.quantity
    user.portfolio = holdings
    return user

def convert_portfolio_to_domain(portfolio_model):
    holdings = {}
    for investment in portfolio_model.investments:
        ticker = investment.security.ticker
        holdings[ticker] = investment.quantity
    return DomainPortfolio(
        portfolio_model.id,
        portfolio_model.name,
        portfolio_model.description,
        portfolio_model.investment_strategy,
        portfolio_model.owner.username,
        holdings
    )

def query_user(username):
    if not username:
        raise ValidationException("Username required", "INVALID_USERNAME")
    user_model = db.session.query(UserModel).filter_by(username=username.strip()).first()
    if not user_model:
        return None
    return convert_user_to_domain(user_model)

def query_all_users():
    user_models = db.session.query(UserModel).all()
    return [convert_user_to_domain(u) for u in user_models]

def create_new_user(user):
    if not user or not user.username:
        raise ValidationException("Invalid user data", "INVALID_USER")
    try:
        existing = db.session.query(UserModel).filter_by(username=user.username.strip()).first()
        if existing:
            raise UniqueConstraintError(f"User '{user.username}' already exists", "USER_EXISTS")
        password = user.password
        if not password.startswith("$2"):
            password = hash_password(password)
        user_model = UserModel(
            username=user.username.strip(),
            password=password,
            first_name=user.first_name,
            last_name=user.last_name,
            balance=user.balance,
            role=user.role
        )
        db.session.add(user_model)
        db.session.commit()
    except (UniqueConstraintError, ValidationException):
        db.session.rollback()
        raise
    except IntegrityError:
        db.session.rollback()
        raise UniqueConstraintError(f"User '{user.username}' already exists", "USER_EXISTS")
    except Exception as e:
        db.session.rollback()
        raise DataPersistenceException(f"Failed to create user: {str(e)}", "CREATE_FAILED")

def delete_user(username):
    if not username:
        raise ValidationException("Username required", "INVALID_USERNAME")
    try:
        user_model = db.session.query(UserModel).filter_by(username=username.strip()).first()
        if not user_model:
            raise UserNotFoundException(f"User '{username}' not found", "USER_NOT_FOUND")
        admin_count = db.session.query(UserModel).filter_by(role="admin").count()
        if user_model.role == "admin" and admin_count <= 1:
            raise AdminProtectionException("Cannot delete last admin", "LAST_ADMIN")
        db.session.delete(user_model)
        db.session.commit()
        return True
    except (ValidationException, UserNotFoundException, AdminProtectionException):
        db.session.rollback()
        raise
    except Exception as e:
        db.session.rollback()
        raise DataPersistenceException(f"Failed to delete user: {str(e)}", "DELETE_FAILED")

def update_user_role(username, new_role):
    try:
        user_model = db.session.query(UserModel).filter_by(username=username.strip()).first()
        if not user_model:
            return False
        user_model.role = new_role
        db.session.commit()
        return True
    except:
        db.session.rollback()
        return False

def update_user_balance(username, new_balance):
    try:
        user_model = db.session.query(UserModel).filter_by(username=username.strip()).first()
        if not user_model:
            return False
        user_model.balance = new_balance
        db.session.commit()
        return True
    except:
        db.session.rollback()
        return False

def create_portfolio(name, description, investment_strategy, username):
    try:
        user_model = db.session.query(UserModel).filter_by(username=username.strip()).first()
        if not user_model:
            raise UserNotFoundException(f"User '{username}' not found", "USER_NOT_FOUND")
        portfolio_model = PortfolioModel(
            name=name.strip(),
            description=description.strip(),
            investment_strategy=investment_strategy.strip(),
            user_id=user_model.id
        )
        db.session.add(portfolio_model)
        db.session.commit()
        db.session.refresh(portfolio_model)
        return convert_portfolio_to_domain(portfolio_model)
    except Exception as e:
        db.session.rollback()
        raise DataPersistenceException(f"Failed to create portfolio: {str(e)}", "CREATE_FAILED")

def query_portfolio(pid):
    portfolio_model = db.session.query(PortfolioModel).filter_by(id=pid).first()
    if not portfolio_model:
        return None
    return convert_portfolio_to_domain(portfolio_model)

def query_all_portfolios():
    portfolio_models = db.session.query(PortfolioModel).all()
    return [convert_portfolio_to_domain(p) for p in portfolio_models]

def update_portfolio(pid, **kwargs):
    try:
        portfolio_model = db.session.query(PortfolioModel).filter_by(id=pid).first()
        if not portfolio_model:
            return False
        for key, value in kwargs.items():
            if hasattr(portfolio_model, key):
                setattr(portfolio_model, key, value)
        db.session.commit()
        return True
    except:
        db.session.rollback()
        return False

def delete_portfolio(pid):
    try:
        portfolio_model = db.session.query(PortfolioModel).filter_by(id=pid).first()
        if not portfolio_model:
            return False
        db.session.delete(portfolio_model)
        db.session.commit()
        return True
    except:
        db.session.rollback()
        return False

def get_or_create_security(ticker, name, reference_price):
    security = db.session.query(SecurityModel).filter_by(ticker=ticker.upper()).first()
    if not security:
        security = SecurityModel(
            ticker=ticker.upper(),
            name=name,
            reference_price=reference_price
        )
        db.session.add(security)
        db.session.commit()
        db.session.refresh(security)
    return security

def query_security(ticker):
    return db.session.query(SecurityModel).filter_by(ticker=ticker.upper()).first()

def query_all_securities():
    securities = db.session.query(SecurityModel).all()
    return [DomainSecurity(s.ticker, s.name, s.reference_price) for s in securities]

def query_transactions_by_security(ticker):
    security_model = db.session.query(SecurityModel).filter_by(ticker=ticker.upper()).first()
    if not security_model:
        return []
    return db.session.query(TransactionModel).filter_by(security_id=security_model.id).all()

def get_investment(portfolio_id, ticker):
    security = db.session.query(SecurityModel).filter_by(ticker=ticker.upper()).first()
    if not security:
        return None
    return db.session.query(InvestmentModel).filter_by(
        portfolio_id=portfolio_id,
        security_id=security.id
    ).first()

def update_investment(portfolio_id, ticker, quantity):
    try:
        security = db.session.query(SecurityModel).filter_by(ticker=ticker.upper()).first()
        if not security:
            return False
        investment = db.session.query(InvestmentModel).filter_by(
            portfolio_id=portfolio_id,
            security_id=security.id
        ).first()
        if investment:
            if quantity <= 0:
                db.session.delete(investment)
            else:
                investment.quantity = quantity
        else:
            if quantity > 0:
                investment = InvestmentModel(
                    portfolio_id=portfolio_id,
                    security_id=security.id,
                    quantity=quantity
                )
                db.session.add(investment)
        db.session.commit()
        return True
    except Exception:
        db.session.rollback()
        return False

def initialize_securities(securities):
    logging.debug(f"Initializing securities: {securities}")
    try:
        for ticker, (name, price) in securities.items():
            existing = db.session.query(SecurityModel).filter_by(ticker=ticker.upper()).first()
            if not existing:
                security = SecurityModel(
                    ticker=ticker.upper(),
                    name=name,
                    reference_price=price
                )
                db.session.add(security)
        db.session.commit()
    except Exception:
        db.session.rollback()

def initialize_default_admin():
    logging.debug("Initializing default admin user")
    try:
        admin = db.session.query(UserModel).filter_by(username="admin").first()
        if not admin:
            admin = UserModel(
                username="admin",
                password=hash_password("admin"),
                first_name="Admin",
                last_name="User",
                balance=10000.0,
                role="admin"
            )
            db.session.add(admin)
            db.session.commit()
    except Exception:
        db.session.rollback()

def remove_investment(portfolio_id, ticker):
    try:
        # First find the security
        security = db.session.query(SecurityModel).filter_by(ticker=ticker).first()
        if not security:
            return False
        
        # Then find the investment
        investment = db.session.query(InvestmentModel).filter_by(
            portfolio_id=portfolio_id,
            security_id=security.id
        ).first()
        if investment:
            db.session.delete(investment)
            db.session.commit()
            return True
        return False
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error removing investment: {e}")
        return False

def create_security(ticker, name, asset_type):
    try:
        # Use reference_price parameter (default 100.0)
        security = SecurityModel(ticker=ticker, name=name, reference_price=100.0)
        db.session.add(security)
        db.session.commit()
        return DomainSecurity(security.ticker, security.name, security.reference_price)
    except IntegrityError:
        db.session.rollback()
        # Security already exists, return it
        existing = db.session.query(SecurityModel).filter_by(ticker=ticker).first()
        if existing:
            return DomainSecurity(existing.ticker, existing.name, existing.reference_price)
        raise
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating security: {e}")
        raise

def query_transactions_by_ticker(ticker):
    try:
        # Find security first
        security = db.session.query(SecurityModel).filter_by(ticker=ticker).first()
        if not security:
            return []
        
        transactions = db.session.query(TransactionModel).filter_by(security_id=security.id).all()
        result = []
        for t in transactions:
            trans_dict = {
                'id': t.id,
                'user_id': t.user_id,
                'portfolio_id': t.portfolio_id,
                'ticker': ticker,
                'transaction_type': t.transaction_type.value if hasattr(t.transaction_type, 'value') else str(t.transaction_type),
                'quantity': t.quantity,
                'price': t.price,
                'timestamp': t.timestamp.isoformat() if t.timestamp else None
            }
            result.append(type('Transaction', (), trans_dict))
        return result
    except Exception as e:
        logging.error(f"Error querying transactions: {e}")
        return []
