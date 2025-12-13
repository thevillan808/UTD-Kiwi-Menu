import logging
from typing import List, Dict, Optional, Tuple
from .. import data_access as db
from ..domain.Portfolio import Portfolio
from ..exceptions import (
    ValidationException,
    PortfolioNotFoundException,
    UserNotFoundException,
    AuthorizationException,
    InsufficientFundsException,
    InsufficientSharesException,
    SecurityNotAvailableException,
    DataAccessException
)

# Test price override support
_TEST_PRICE_MAP = None

def set_test_price_map(price_map: dict):
    global _TEST_PRICE_MAP
    _TEST_PRICE_MAP = price_map

def clear_test_price_map():
    global _TEST_PRICE_MAP
    _TEST_PRICE_MAP = None

def get_price_map() -> Dict[str, float]:
    if _TEST_PRICE_MAP is not None:
        return _TEST_PRICE_MAP
    
    # Default stock prices
    return {
        "AAPL": 175.0,
        "GOOGL": 140.0,
        "MSFT": 410.0,
        "TSLA": 250.0,
        "AMZN": 145.0,
        "NVDA": 450.0,
        "META": 325.0,
        "NFLX": 400.0,
        "SPOT": 180.0,
        "UBER": 65.0
    }


def sell_from_portfolio(username: str, symbol: str, qty: int, portfolio_id: int, sale_price: float = None) -> Tuple[bool, str]:
    try:
        # Validate inputs
        if not isinstance(username, str) or not username.strip():
            raise ValidationException("Username must be a non-empty string", "INVALID_USERNAME")
        
        if not isinstance(symbol, str) or not symbol.strip():
            raise ValidationException("Symbol must be a non-empty string", "INVALID_SYMBOL")
        
        if not isinstance(qty, int) or qty <= 0:
            raise ValidationException("Quantity must be a positive integer", "INVALID_QUANTITY")
        
        if not isinstance(portfolio_id, int):
            raise ValidationException("Portfolio ID must be an integer", "INVALID_PORTFOLIO_ID")
        
        if sale_price is not None and (not isinstance(sale_price, (int, float)) or sale_price < 0):
            raise ValidationException("Sale price must be a non-negative number", "INVALID_SALE_PRICE")
        
        # Check user exists
        user = db.query_user(username.strip())
        if not user:
            raise UserNotFoundException(f"User '{username}' not found", "USER_NOT_FOUND")
        
        # Check portfolio exists
        portfolio = db.query_portfolio(portfolio_id)
        if not portfolio:
            raise PortfolioNotFoundException(f"Portfolio with ID {portfolio_id} not found", "PORTFOLIO_NOT_FOUND")
        
        # Check ownership
        if portfolio.owner_username != username.strip():
            raise AuthorizationException(f"User '{username}' does not own portfolio {portfolio_id}", "NOT_PORTFOLIO_OWNER")
        
        # Check symbol validity
        price_map = get_price_map()
        symbol = symbol.strip().upper()
        if symbol not in price_map:
            raise SecurityNotAvailableException(f"Symbol '{symbol}' is not available for trading", "SYMBOL_NOT_AVAILABLE")
        
        # Ensure security exists in database
        security_name = _get_security_name(symbol)
        db.get_or_create_security(symbol, security_name, price_map[symbol])
        
        # Check holdings
        investment = db.get_investment(portfolio_id, symbol)
        current_holdings = investment.quantity if investment else 0
        
        if current_holdings < qty:
            raise InsufficientSharesException(f"Insufficient shares: have {current_holdings}, need {qty}", "INSUFFICIENT_SHARES")
        
        # Calculate sale proceeds
        if sale_price is None:
            sale_price = price_map[symbol]
        
        proceeds = sale_price * qty
        
        # Update user balance
        new_balance = user.balance + proceeds
        db.update_user_balance(username.strip(), new_balance)
        
        # Update investment holdings
        new_holdings = current_holdings - qty
        db.update_investment(portfolio_id, symbol, new_holdings)
        
        # Record transaction
        db.record_transaction(
            username.strip(),
            portfolio_id,
            symbol,
            "SELL",
            qty,
            sale_price
        )
        
        return True, "ok"
        
    except (ValidationException, UserNotFoundException, PortfolioNotFoundException, 
            AuthorizationException, SecurityNotAvailableException, InsufficientSharesException):
        raise
    except Exception as e:
        logging.error(f"Failed to sell {qty} shares of {symbol} for user {username}: {str(e)}")
        raise DataAccessException(f"Failed to complete sale transaction: {str(e)}", "SALE_TRANSACTION_FAILED")


def buy_to_portfolio(username: str, symbol: str, qty: int, portfolio_id: int) -> Tuple[bool, str]:
    try:
        # Validate inputs
        if not isinstance(username, str) or not username.strip():
            raise ValidationException("Username must be a non-empty string", "INVALID_USERNAME")
        
        if not isinstance(symbol, str) or not symbol.strip():
            raise ValidationException("Symbol must be a non-empty string", "INVALID_SYMBOL")
        
        if not isinstance(qty, int) or qty <= 0:
            raise ValidationException("Quantity must be a positive integer", "INVALID_QUANTITY")
        
        if not isinstance(portfolio_id, int):
            raise ValidationException("Portfolio ID must be an integer", "INVALID_PORTFOLIO_ID")
        
        # Check user exists
        user = db.query_user(username.strip())
        if not user:
            raise UserNotFoundException(f"User '{username}' not found", "USER_NOT_FOUND")
        
        # Check portfolio exists
        portfolio = db.query_portfolio(portfolio_id)
        if not portfolio:
            raise PortfolioNotFoundException(f"Portfolio with ID {portfolio_id} not found", "PORTFOLIO_NOT_FOUND")
        
        # Check ownership
        if portfolio.owner_username != username.strip():
            raise AuthorizationException(f"User '{username}' does not own portfolio {portfolio_id}", "NOT_PORTFOLIO_OWNER")
        
        # Check symbol validity
        price_map = get_price_map()
        symbol = symbol.strip().upper()
        if symbol not in price_map:
            raise SecurityNotAvailableException(f"Symbol '{symbol}' is not available for trading", "SYMBOL_NOT_AVAILABLE")
        
        # Ensure security exists in database
        security_name = _get_security_name(symbol)
        db.get_or_create_security(symbol, security_name, price_map[symbol])
        
        # Calculate cost
        price = price_map[symbol]
        cost = price * qty
        
        # Check funds
        if user.balance < cost:
            raise InsufficientFundsException(f"Insufficient funds: need ${cost:.2f}, have ${user.balance:.2f}", "INSUFFICIENT_FUNDS")
        
        # Update user balance
        new_balance = user.balance - cost
        db.update_user_balance(username.strip(), new_balance)
        
        # Update investment holdings
        investment = db.get_investment(portfolio_id, symbol)
        current_holdings = investment.quantity if investment else 0
        new_holdings = current_holdings + qty
        db.update_investment(portfolio_id, symbol, new_holdings)
        
        # Record transaction
        db.record_transaction(
            username.strip(),
            portfolio_id,
            symbol,
            "BUY",
            qty,
            price
        )
        
        return True, "ok"
        
    except (ValidationException, UserNotFoundException, PortfolioNotFoundException, 
            AuthorizationException, SecurityNotAvailableException, InsufficientFundsException):
        raise
    except Exception as e:
        logging.error(f"Failed to buy {qty} shares of {symbol} for user {username}: {str(e)}")
        raise DataAccessException(f"Failed to complete purchase transaction: {str(e)}", "PURCHASE_TRANSACTION_FAILED")


def _get_security_name(ticker: str) -> str:
    names = {
        "AAPL": "Apple Inc.",
        "GOOGL": "Alphabet Inc.",
        "MSFT": "Microsoft Corporation",
        "TSLA": "Tesla Inc.",
        "AMZN": "Amazon.com Inc.",
        "NVDA": "NVIDIA Corporation",
        "META": "Meta Platforms Inc.",
        "NFLX": "Netflix Inc.",
        "SPOT": "Spotify Technology S.A.",
        "UBER": "Uber Technologies Inc."
    }
    return names.get(ticker.upper(), ticker.upper())


def create_portfolio(name: str, description: str, investment_strategy: str, username: str) -> Portfolio:
    try:
        if not isinstance(name, str) or not name.strip():
            raise ValidationException("Portfolio name must be a non-empty string", "INVALID_PORTFOLIO_NAME")
        
        if not isinstance(description, str):
            description = ""
        
        if not isinstance(investment_strategy, str):
            investment_strategy = ""
        
        if not isinstance(username, str) or not username.strip():
            raise ValidationException("Username must be a non-empty string", "INVALID_USERNAME")
        
        user = db.query_user(username.strip())
        if not user:
            raise UserNotFoundException(f"User '{username}' not found", "USER_NOT_FOUND")
        
        return db.create_portfolio(name.strip(), description.strip(), investment_strategy.strip(), username.strip())
        
    except (ValidationException, UserNotFoundException):
        raise
    except Exception as e:
        logging.error(f"Failed to create portfolio for user {username}: {str(e)}")
        raise DataAccessException(f"Failed to create portfolio: {str(e)}", "PORTFOLIO_CREATION_FAILED")


def list_portfolios() -> List[Portfolio]:
    try:
        return db.query_all_portfolios()
    except Exception as e:
        logging.error(f"Failed to retrieve portfolios: {str(e)}")
        raise DataAccessException(f"Failed to retrieve portfolios: {str(e)}", "PORTFOLIO_RETRIEVAL_FAILED")


def get_portfolio(pid: int) -> Optional[Portfolio]:
    try:
        if not isinstance(pid, int):
            raise ValidationException("Portfolio ID must be an integer", "INVALID_PORTFOLIO_ID")
        
        return db.query_portfolio(pid)
    except ValidationException:
        raise
    except Exception as e:
        logging.error(f"Failed to retrieve portfolio {pid}: {str(e)}")
        raise DataAccessException(f"Failed to retrieve portfolio: {str(e)}", "PORTFOLIO_RETRIEVAL_FAILED")


def update_portfolio(pid: int, actor_username: str = None, **kwargs) -> bool:
    p = db.query_portfolio(pid)
    if not p:
        return False
    if actor_username:
        actor = db.query_user(actor_username)
        if not actor:
            return False
        if actor.username != p.owner_username and actor.role != "admin":
            return False
    return db.update_portfolio(pid, **kwargs)


def delete_portfolio(pid: int, actor_username: str = None) -> bool:
    p = db.query_portfolio(pid)
    if not p:
        return False
    if actor_username:
        actor = db.query_user(actor_username)
        if not actor:
            return False
        if actor.username != p.owner_username and actor.role != "admin":
            return False
    return db.delete_portfolio(pid)


def liquidate_investments(username: str) -> dict:
    try:
        user = db.query_user(username)
        if not user:
            return {"error": "user_not_found"}
        
        portfolios = [p for p in db.query_all_portfolios() if p.owner_username == username]
        
        if not portfolios:
            return {"status": "no_holdings"}
        
        result = {}
        for portfolio in portfolios:
            for symbol, qty in portfolio.holdings.items():
                if qty > 0:
                    try:
                        ok, reason = sell_from_portfolio(username, symbol, qty, portfolio.id)
                        result[symbol] = {"ok": ok, "sold": qty}
                    except Exception as e:
                        result[symbol] = {"ok": False, "reason": str(e)}
        
        return result
    except Exception as e:
        logging.error(f"Failed to liquidate investments for {username}: {str(e)}")
        return {"error": str(e)}
