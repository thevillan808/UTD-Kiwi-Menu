"""
Additional tests to increase coverage to 80%+.
Tests error handling paths and edge cases.
"""

import pytest
from app.service import user_service, portfolio_service
from app import db
from app.exceptions import (
    InvalidUsernameException,
    InvalidPasswordException,
    InvalidRoleException,
    DataAccessException
)


class TestUserServiceErrorHandling:
    """Test error handling in user service"""
    
    def test_add_user_empty_username(self, test_db):
        with pytest.raises(InvalidUsernameException):
            user_service.add_user("", "password", "First", "Last")
    
    def test_add_user_whitespace_username(self, test_db):
        with pytest.raises(InvalidUsernameException):
            user_service.add_user("   ", "password", "First", "Last")
    
    def test_add_user_none_username(self, test_db):
        with pytest.raises(InvalidUsernameException):
            user_service.add_user(None, "password", "First", "Last")
    
    def test_add_user_empty_password(self, test_db):
        with pytest.raises(InvalidPasswordException):
            user_service.add_user("testuser", "", "First", "Last")
    
    def test_add_user_whitespace_password(self, test_db):
        with pytest.raises(InvalidPasswordException):
            user_service.add_user("testuser", "   ", "First", "Last")
    
    def test_add_user_none_password(self, test_db):
        with pytest.raises(InvalidPasswordException):
            user_service.add_user("testuser", None, "First", "Last")
    
    def test_add_user_invalid_role(self, test_db):
        with pytest.raises(InvalidRoleException):
            user_service.add_user("testuser", "password", "First", "Last", role="superuser")
    
    def test_delete_user_empty_username(self, test_db):
        with pytest.raises(InvalidUsernameException):
            user_service.delete_user("")
    
    def test_delete_user_whitespace_username(self, test_db):
        with pytest.raises(InvalidUsernameException):
            user_service.delete_user("   ")
    
    def test_change_role_empty_username(self, test_db):
        with pytest.raises(InvalidUsernameException):
            user_service.change_role("", "admin")
    
    def test_change_role_invalid_role(self, test_db):
        with pytest.raises(InvalidRoleException):
            user_service.change_role("testuser", "superadmin")
    
    def test_get_user_empty_username(self, test_db):
        with pytest.raises(InvalidUsernameException):
            user_service.get_user("")
    
    def test_get_user_whitespace_username(self, test_db):
        with pytest.raises(InvalidUsernameException):
            user_service.get_user("   ")


class TestPortfolioServiceErrorHandling:
    """Test error handling in portfolio service"""
    
    def test_get_portfolio_price_map(self, test_db):
        # Test that get_price_map returns the default prices
        price_map = portfolio_service.get_price_map()
        assert "AAPL" in price_map
        assert "GOOGL" in price_map
        assert price_map["AAPL"] == 175.0
    
    def test_set_test_price_map(self, test_db):
        # Test setting custom prices for testing
        custom_prices = {"AAPL": 200.0, "GOOGL": 150.0}
        portfolio_service.set_test_price_map(custom_prices)
        
        price_map = portfolio_service.get_price_map()
        assert price_map["AAPL"] == 200.0
        assert price_map["GOOGL"] == 150.0
        
        # Clear test price map
        portfolio_service.clear_test_price_map()
        price_map = portfolio_service.get_price_map()
        assert price_map["AAPL"] == 175.0
    
    def test_list_portfolios(self, test_db, sample_portfolio):
        # Test listing portfolios
        portfolios = portfolio_service.list_portfolios()
        assert len(portfolios) >= 1
        assert any(p.id == sample_portfolio.id for p in portfolios)
    
    def test_get_portfolio(self, test_db, sample_portfolio):
        # Test getting a portfolio by ID
        portfolio = portfolio_service.get_portfolio(sample_portfolio.id)
        assert portfolio is not None
        assert portfolio.id == sample_portfolio.id
    
    def test_get_nonexistent_portfolio(self, test_db):
        # Test getting a portfolio that doesn't exist
        portfolio = portfolio_service.get_portfolio(99999)
        assert portfolio is None
    
    def test_update_portfolio_success(self, test_db, sample_user, sample_portfolio):
        # Test updating portfolio as owner
        result = portfolio_service.update_portfolio(
            pid=sample_portfolio.id,
            actor_username=sample_user.username,
            name="Updated Name",
            description="Updated Description"
        )
        assert result is True
    
    def test_delete_portfolio_success(self, test_db, sample_user, sample_portfolio):
        # Test deleting portfolio as owner
        result = portfolio_service.delete_portfolio(
            pid=sample_portfolio.id,
            actor_username=sample_user.username
        )
        assert result is True
    
    def test_create_portfolio(self, test_db, sample_user):
        # Test creating a new portfolio
        portfolio = portfolio_service.create_portfolio(
            name="New Portfolio",
            description="Test Description",
            investment_strategy="Growth",
            username=sample_user.username
        )
        assert portfolio is not None
        assert portfolio.name == "New Portfolio"


class TestUserServiceAdditional:
    """Additional user service tests"""
    
    def test_add_user_with_whitespace_fields(self, test_db):
        # Test adding user with whitespace that should be trimmed
        result = user_service.add_user(
            "  testuser2  ",
            "  password  ",
            "  First  ",
            "  Last  "
        )
        assert result is True
        
        # Verify user was created with trimmed fields
        user = db.query_user("testuser2")
        assert user is not None
        assert user.username == "testuser2"
    
    def test_change_role_nonexistent_user(self, test_db):
        from app.exceptions import UserNotFoundException
        with pytest.raises(UserNotFoundException):
            user_service.change_role("nonexistent_user_12345", "admin")


class TestDatabaseErrorHandling:
    """Test database error handling"""
    
    def test_query_nonexistent_user(self, test_db):
        # Query user that doesn't exist
        user = db.query_user("nonexistent_user_12345")
        assert user is None
    
    def test_query_nonexistent_portfolio(self, test_db):
        # Query portfolio that doesn't exist
        portfolio = db.query_portfolio(99999)
        assert portfolio is None
    
    def test_query_nonexistent_security(self, test_db):
        # Query security that doesn't exist
        security = db.query_security("INVALID")
        assert security is None
    
    def test_get_nonexistent_investment(self, test_db, sample_portfolio):
        # Get investment that doesn't exist
        investment = db.get_investment(sample_portfolio.id, "INVALID")
        assert investment is None
    
    def test_update_portfolio_nonexistent(self, test_db):
        # Try to update portfolio that doesn't exist
        result = db.update_portfolio(99999, name="Test")
        assert result is False
    
    def test_delete_portfolio_nonexistent(self, test_db):
        # Try to delete portfolio that doesn't exist
        result = db.delete_portfolio(99999)
        assert result is False
    
    def test_update_user_role_nonexistent(self, test_db):
        # Try to update role for user that doesn't exist
        result = db.update_user_role("nonexistent_user_12345", "admin")
        assert result is False
    
    def test_update_user_balance_nonexistent(self, test_db):
        # Try to update balance for user that doesn't exist
        result = db.update_user_balance("nonexistent_user_12345", 1000.0)
        assert result is False
    
    def test_update_investment_invalid_security(self, test_db, sample_portfolio):
        # Try to update investment with invalid security
        result = db.update_investment(sample_portfolio.id, "INVALID", 10)
        assert result is False
    
    def test_query_all_securities(self, test_db, sample_security):
        # Query all securities
        securities = db.query_all_securities()
        assert len(securities) >= 1
        assert any(s.ticker == sample_security.ticker for s in securities)
    
    def test_initialize_securities(self, test_db):
        # Test initializing securities
        securities = {
            "TEST": ("Test Security", 100.0),
            "TEST2": ("Test Security 2", 200.0)
        }
        db.initialize_securities(securities)
        
        # Verify they were created
        test_sec = db.query_security("TEST")
        assert test_sec is not None
        assert test_sec.name == "Test Security"
    
    def test_initialize_default_admin(self, test_db):
        # Test initializing default admin
        db.initialize_default_admin()
        
        # Verify admin exists
        admin = db.query_user("admin")
        assert admin is not None
        assert admin.role == "admin"

