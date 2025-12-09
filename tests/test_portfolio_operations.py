"""
Tests for portfolio operations.

Tests portfolio CRUD, investment tracking, and transactions.
"""

import pytest
from app import db
from app.exceptions import (
    UserNotFoundException,
    PortfolioNotFoundException,
    ValidationException
)


class TestPortfolioOperations:
    """Test portfolio database operations"""
    
    def test_create_portfolio(self, test_db, sample_user):
        """Test creating a new portfolio"""
        portfolio = db.create_portfolio(
            "New Portfolio",
            "Test Description",
            "Growth",
            "testuser"
        )
        
        assert portfolio is not None
        assert portfolio.name == "New Portfolio"
        assert portfolio.description == "Test Description"
        assert portfolio.investment_strategy == "Growth"
        assert portfolio.owner_username == "testuser"
    
    def test_create_portfolio_for_nonexistent_user(self, test_db):
        """Test creating portfolio for nonexistent user raises error"""
        with pytest.raises(Exception):
            db.create_portfolio(
                "Portfolio",
                "Description",
                "Strategy",
                "nonexistent"
            )
    
    def test_query_portfolio(self, test_db, sample_portfolio):
        """Test querying portfolio by id"""
        portfolio = db.query_portfolio(sample_portfolio.id)
        assert portfolio is not None
        assert portfolio.id == sample_portfolio.id
        assert portfolio.name == "Test Portfolio"
    
    def test_query_nonexistent_portfolio(self, test_db):
        """Test querying nonexistent portfolio returns None"""
        portfolio = db.query_portfolio(99999)
        assert portfolio is None
    
    def test_query_all_portfolios(self, test_db, sample_portfolio):
        """Test querying all portfolios"""
        portfolios = db.query_all_portfolios()
        assert len(portfolios) >= 1
        portfolio_ids = [p.id for p in portfolios]
        assert sample_portfolio.id in portfolio_ids
    
    def test_update_portfolio(self, test_db, sample_portfolio):
        """Test updating portfolio fields"""
        success = db.update_portfolio(
            sample_portfolio.id,
            name="Updated Portfolio",
            description="Updated Description"
        )
        assert success is True
        
        portfolio = db.query_portfolio(sample_portfolio.id)
        assert portfolio.name == "Updated Portfolio"
        assert portfolio.description == "Updated Description"
    
    def test_delete_portfolio(self, test_db, sample_portfolio):
        """Test deleting a portfolio"""
        portfolio_id = sample_portfolio.id
        success = db.delete_portfolio(portfolio_id)
        assert success is True
        
        portfolio = db.query_portfolio(portfolio_id)
        assert portfolio is None
    
    def test_delete_nonexistent_portfolio(self, test_db):
        """Test deleting nonexistent portfolio returns False"""
        success = db.delete_portfolio(99999)
        assert success is False


class TestSecurityOperations:
    """Test security database operations"""
    
    def test_get_or_create_security_new(self, test_db):
        """Test creating a new security"""
        security = db.get_or_create_security("GOOGL", "Alphabet Inc.", 140.0)
        assert security is not None
        assert security.ticker == "GOOGL"
        assert security.name == "Alphabet Inc."
        assert security.reference_price == 140.0
    
    def test_get_or_create_security_existing(self, test_db, sample_security):
        """Test getting an existing security"""
        security = db.get_or_create_security("AAPL", "Apple Inc.", 175.0)
        assert security is not None
        assert security.id == sample_security.id
        assert security.ticker == "AAPL"
    
    def test_query_security(self, test_db, sample_security):
        """Test querying security by ticker"""
        security = db.query_security("AAPL")
        assert security is not None
        assert security.ticker == "AAPL"
        assert security.name == "Apple Inc."
    
    def test_query_nonexistent_security(self, test_db):
        """Test querying nonexistent security returns None"""
        security = db.query_security("INVALID")
        assert security is None
    
    def test_query_all_securities(self, test_db, sample_security):
        """Test querying all securities"""
        securities = db.query_all_securities()
        assert len(securities) >= 1
        tickers = [s.ticker for s in securities]
        assert "AAPL" in tickers


class TestInvestmentOperations:
    """Test investment database operations"""
    
    def test_get_investment(self, test_db, sample_investment, sample_portfolio):
        """Test getting an investment"""
        investment = db.get_investment(sample_portfolio.id, "AAPL")
        assert investment is not None
        assert investment.quantity == 10
    
    def test_get_nonexistent_investment(self, test_db, sample_portfolio):
        """Test getting nonexistent investment returns None"""
        investment = db.get_investment(sample_portfolio.id, "GOOGL")
        assert investment is None
    
    def test_update_investment_increase(self, test_db, sample_portfolio, sample_security):
        """Test updating investment to increase quantity"""
        success = db.update_investment(sample_portfolio.id, "AAPL", 20)
        assert success is True
        
        investment = db.get_investment(sample_portfolio.id, "AAPL")
        assert investment.quantity == 20
    
    def test_update_investment_decrease(self, test_db, sample_investment, sample_portfolio):
        """Test updating investment to decrease quantity"""
        success = db.update_investment(sample_portfolio.id, "AAPL", 5)
        assert success is True
        
        investment = db.get_investment(sample_portfolio.id, "AAPL")
        assert investment.quantity == 5
    
    def test_update_investment_to_zero_deletes(self, test_db, sample_investment, sample_portfolio):
        """Test updating investment to zero deletes it"""
        success = db.update_investment(sample_portfolio.id, "AAPL", 0)
        assert success is True
        
        investment = db.get_investment(sample_portfolio.id, "AAPL")
        assert investment is None
    
    def test_update_investment_create_new(self, test_db, sample_portfolio):
        """Test updating investment creates new if doesn't exist"""
        # Create GOOGL security
        db.get_or_create_security("GOOGL", "Alphabet Inc.", 140.0)
        
        success = db.update_investment(sample_portfolio.id, "GOOGL", 15)
        assert success is True
        
        investment = db.get_investment(sample_portfolio.id, "GOOGL")
        assert investment is not None
        assert investment.quantity == 15


class TestTransactionOperations:
    """Test transaction recording operations"""
    
    def test_record_buy_transaction(self, test_db, sample_user, sample_portfolio, sample_security):
        """Test recording a buy transaction"""
        transaction = db.record_transaction(
            "testuser",
            sample_portfolio.id,
            "AAPL",
            "BUY",
            10,
            175.0
        )
        
        assert transaction is not None
        assert transaction.transaction_type.value == "BUY"
        assert transaction.quantity == 10
        assert transaction.price == 175.0
    
    def test_record_sell_transaction(self, test_db, sample_user, sample_portfolio, sample_security):
        """Test recording a sell transaction"""
        transaction = db.record_transaction(
            "testuser",
            sample_portfolio.id,
            "AAPL",
            "SELL",
            5,
            180.0
        )
        
        assert transaction is not None
        assert transaction.transaction_type.value == "SELL"
        assert transaction.quantity == 5
        assert transaction.price == 180.0
    
    def test_query_transactions_by_user(self, test_db, sample_user, sample_portfolio, sample_security):
        """Test querying transactions by user"""
        # Record some transactions
        db.record_transaction("testuser", sample_portfolio.id, "AAPL", "BUY", 10, 175.0)
        db.record_transaction("testuser", sample_portfolio.id, "AAPL", "SELL", 5, 180.0)
        
        transactions = db.query_transactions_by_user("testuser")
        assert len(transactions) >= 2
    
    def test_query_transactions_by_portfolio(self, test_db, sample_user, sample_portfolio, sample_security):
        """Test querying transactions by portfolio"""
        # Record some transactions
        db.record_transaction("testuser", sample_portfolio.id, "AAPL", "BUY", 10, 175.0)
        
        transactions = db.query_transactions_by_portfolio(sample_portfolio.id)
        assert len(transactions) >= 1
    
    def test_query_transactions_by_security(self, test_db, sample_user, sample_portfolio, sample_security):
        """Test querying transactions by security"""
        # Record some transactions
        db.record_transaction("testuser", sample_portfolio.id, "AAPL", "BUY", 10, 175.0)
        
        transactions = db.query_transactions_by_security("AAPL")
        assert len(transactions) >= 1
    
    def test_transaction_timestamp(self, test_db, sample_user, sample_portfolio, sample_security):
        """Test that transactions have timestamps"""
        transaction = db.record_transaction(
            "testuser",
            sample_portfolio.id,
            "AAPL",
            "BUY",
            10,
            175.0
        )
        
        assert transaction.timestamp is not None
