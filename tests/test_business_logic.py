"""
Tests for business logic in services.

Tests buy/sell operations, transaction recording, and validation.
"""

import pytest
from app.service import portfolio_service
from app.service import user_service
from app import db
from app.domain.User import User
from app.exceptions import (
    InsufficientFundsException,
    InsufficientSharesException,
    SecurityNotAvailableException,
    AuthorizationException,
    UserNotFoundException,
    PortfolioNotFoundException
)


class TestBuyOperations:
    """Test buy operations in portfolio service"""
    
    def test_buy_success(self, test_db, sample_user, sample_portfolio):
        """Test successful buy operation"""
        # Initialize security
        db.get_or_create_security("AAPL", "Apple Inc.", 175.0)
        
        # Set balance
        db.update_user_balance("testuser", 2000.0)
        
        ok, reason = portfolio_service.buy_to_portfolio("testuser", "AAPL", 5, sample_portfolio.id)
        
        assert ok is True
        assert reason == "ok"
        
        # Check balance decreased
        user = db.query_user("testuser")
        assert user.balance < 2000.0
        
        # Check investment created
        investment = db.get_investment(sample_portfolio.id, "AAPL")
        assert investment is not None
        assert investment.quantity >= 5
        
        # Check transaction recorded
        transactions = db.query_transactions_by_user("testuser")
        assert len(transactions) >= 1
    
    def test_buy_insufficient_funds(self, test_db, sample_user, sample_portfolio):
        """Test buy with insufficient funds"""
        # Initialize security
        db.get_or_create_security("AAPL", "Apple Inc.", 175.0)
        
        # Set low balance
        db.update_user_balance("testuser", 100.0)
        
        with pytest.raises(InsufficientFundsException):
            portfolio_service.buy_to_portfolio("testuser", "AAPL", 10, sample_portfolio.id)
    
    def test_buy_invalid_security(self, test_db, sample_user, sample_portfolio):
        """Test buy with invalid security"""
        with pytest.raises(SecurityNotAvailableException):
            portfolio_service.buy_to_portfolio("testuser", "INVALID", 5, sample_portfolio.id)
    
    def test_buy_nonexistent_portfolio(self, test_db, sample_user):
        """Test buy for nonexistent portfolio"""
        with pytest.raises(PortfolioNotFoundException):
            portfolio_service.buy_to_portfolio("testuser", "AAPL", 5, 99999)
    
    def test_buy_wrong_owner(self, test_db, sample_user, sample_admin, sample_portfolio):
        """Test buy for portfolio owned by different user"""
        with pytest.raises(AuthorizationException):
            portfolio_service.buy_to_portfolio("admin", "AAPL", 5, sample_portfolio.id)


class TestSellOperations:
    """Test sell operations in portfolio service"""
    
    def test_sell_success(self, test_db, sample_user, sample_portfolio, sample_security, sample_investment):
        """Test successful sell operation"""
        initial_balance = sample_user.balance
        
        ok, reason = portfolio_service.sell_from_portfolio("testuser", "AAPL", 5, sample_portfolio.id)
        
        assert ok is True
        assert reason == "ok"
        
        # Check balance increased
        user = db.query_user("testuser")
        assert user.balance > initial_balance
        
        # Check investment decreased
        investment = db.get_investment(sample_portfolio.id, "AAPL")
        assert investment.quantity < 10
        
        # Check transaction recorded
        transactions = db.query_transactions_by_user("testuser")
        assert len(transactions) >= 1
    
    def test_sell_insufficient_shares(self, test_db, sample_user, sample_portfolio, sample_security, sample_investment):
        """Test sell with insufficient shares"""
        with pytest.raises(InsufficientSharesException):
            portfolio_service.sell_from_portfolio("testuser", "AAPL", 100, sample_portfolio.id)
    
    def test_sell_no_holdings(self, test_db, sample_user, sample_portfolio):
        """Test sell when no holdings exist"""
        # Initialize security without investment
        db.get_or_create_security("GOOGL", "Alphabet Inc.", 140.0)
        
        with pytest.raises(InsufficientSharesException):
            portfolio_service.sell_from_portfolio("testuser", "GOOGL", 5, sample_portfolio.id)
    
    def test_sell_with_custom_price(self, test_db, sample_user, sample_portfolio, sample_security, sample_investment):
        """Test sell with custom price"""
        initial_balance = sample_user.balance
        custom_price = 200.0
        
        ok, reason = portfolio_service.sell_from_portfolio("testuser", "AAPL", 5, sample_portfolio.id, custom_price)
        
        assert ok is True
        
        # Check balance increased by correct amount
        user = db.query_user("testuser")
        expected_proceeds = custom_price * 5
        assert user.balance == pytest.approx(initial_balance + expected_proceeds)
    
    def test_sell_wrong_owner(self, test_db, sample_user, sample_admin, sample_portfolio, sample_security, sample_investment):
        """Test sell for portfolio owned by different user"""
        with pytest.raises(AuthorizationException):
            portfolio_service.sell_from_portfolio("admin", "AAPL", 5, sample_portfolio.id)


class TestPortfolioService:
    """Test portfolio service operations"""
    
    def test_create_portfolio(self, test_db, sample_user):
        """Test creating portfolio through service"""
        portfolio = portfolio_service.create_portfolio(
            "Service Portfolio",
            "Test Description",
            "Growth",
            "testuser"
        )
        
        assert portfolio is not None
        assert portfolio.name == "Service Portfolio"
    
    def test_list_portfolios(self, test_db, sample_portfolio):
        """Test listing all portfolios"""
        portfolios = portfolio_service.list_portfolios()
        assert len(portfolios) >= 1
    
    def test_get_portfolio(self, test_db, sample_portfolio):
        """Test getting portfolio by id"""
        portfolio = portfolio_service.get_portfolio(sample_portfolio.id)
        assert portfolio is not None
        assert portfolio.id == sample_portfolio.id
    
    def test_update_portfolio_as_owner(self, test_db, sample_user, sample_portfolio):
        """Test updating portfolio as owner"""
        success = portfolio_service.update_portfolio(
            sample_portfolio.id,
            "testuser",
            name="Updated Name"
        )
        assert success is True
    
    def test_update_portfolio_as_admin(self, test_db, sample_admin, sample_portfolio):
        """Test updating portfolio as admin"""
        success = portfolio_service.update_portfolio(
            sample_portfolio.id,
            "admin",
            name="Admin Updated"
        )
        assert success is True
    
    def test_delete_portfolio_as_owner(self, test_db, sample_user, sample_portfolio):
        """Test deleting portfolio as owner"""
        portfolio_id = sample_portfolio.id
        success = portfolio_service.delete_portfolio(portfolio_id, "testuser")
        assert success is True


class TestUserService:
    """Test user service operations"""
    
    def test_add_user(self, test_db):
        """Test adding user through service"""
        success = user_service.add_user("newuser", "password", "New", "User", "user")
        assert success is True
        
        user = db.query_user("newuser")
        assert user is not None
    
    def test_list_users(self, test_db, sample_user):
        """Test listing all users"""
        users = user_service.list_users()
        assert len(users) >= 1
    
    def test_get_user(self, test_db, sample_user):
        """Test getting user by username"""
        user = user_service.get_user("testuser")
        assert user is not None
        assert user.username == "testuser"
    
    def test_change_role(self, test_db, sample_user):
        """Test changing user role"""
        success = user_service.change_role("testuser", "admin")
        assert success is True
        
        user = db.query_user("testuser")
        assert user.role == "admin"
    
    def test_delete_user(self, test_db, sample_user, sample_admin):
        """Test deleting user through service"""
        success = user_service.delete_user("testuser")
        assert success is True
        
        user = db.query_user("testuser")
        assert user is None


class TestTransactionRecording:
    """Test that transactions are properly recorded"""
    
    def test_buy_records_transaction(self, test_db, sample_user, sample_portfolio):
        """Test that buy operation records transaction"""
        db.get_or_create_security("AAPL", "Apple Inc.", 175.0)
        db.update_user_balance("testuser", 2000.0)
        
        initial_count = len(db.query_transactions_by_user("testuser"))
        
        portfolio_service.buy_to_portfolio("testuser", "AAPL", 5, sample_portfolio.id)
        
        transactions = db.query_transactions_by_user("testuser")
        assert len(transactions) == initial_count + 1
        
        last_transaction = transactions[-1]
        assert last_transaction.transaction_type.value == "BUY"
        assert last_transaction.quantity == 5
    
    def test_sell_records_transaction(self, test_db, sample_user, sample_portfolio, sample_security, sample_investment):
        """Test that sell operation records transaction"""
        initial_count = len(db.query_transactions_by_user("testuser"))
        
        portfolio_service.sell_from_portfolio("testuser", "AAPL", 3, sample_portfolio.id)
        
        transactions = db.query_transactions_by_user("testuser")
        assert len(transactions) == initial_count + 1
        
        last_transaction = transactions[-1]
        assert last_transaction.transaction_type.value == "SELL"
        assert last_transaction.quantity == 3
    
    def test_transaction_links_to_entities(self, test_db, sample_user, sample_portfolio, sample_security, sample_investment):
        """Test that transaction properly links to user, portfolio, and security"""
        portfolio_service.sell_from_portfolio("testuser", "AAPL", 2, sample_portfolio.id)
        
        transactions = db.query_transactions_by_user("testuser")
        transaction = transactions[-1]
        
        assert transaction.user_id == sample_user.id
        assert transaction.portfolio_id == sample_portfolio.id
        assert transaction.security_id == sample_security.id
