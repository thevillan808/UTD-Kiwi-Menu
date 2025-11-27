"""
Configuration for pytest tests.

Sets up test database and fixtures for testing.
"""

import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from app.models import Base
from app import db

# Use SQLite for testing
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def test_engine():
    """Create test database engine"""
    engine = create_engine(TEST_DATABASE_URL, echo=False)
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture(scope="function")
def test_session(test_engine):
    """Create a new test database session for each test"""
    connection = test_engine.connect()
    transaction = connection.begin()
    
    Session = sessionmaker(bind=connection)
    session = Session()
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def test_db(test_session, monkeypatch):
    """Patch database functions to use test session"""
    original_get_session = db.get_session
    original_close_session = db.close_session
    
    def mock_get_session():
        return test_session
    
    def mock_close_session(session):
        # Don't actually close in tests
        pass
    
    monkeypatch.setattr(db, 'get_session', mock_get_session)
    monkeypatch.setattr(db, 'close_session', mock_close_session)
    
    yield test_session
    
    # Restore original functions
    monkeypatch.setattr(db, 'get_session', original_get_session)
    monkeypatch.setattr(db, 'close_session', original_close_session)


@pytest.fixture
def sample_user(test_db):
    """Create a sample user for testing"""
    from app.models import UserModel
    from app import db
    
    user = UserModel(
        username="testuser",
        password=db.hash_password("password123"),
        first_name="Test",
        last_name="User",
        balance=1000.0,
        role="user"
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def sample_admin(test_db):
    """Create a sample admin for testing"""
    from app.models import UserModel
    from app import db
    
    admin = UserModel(
        username="admin",
        password=db.hash_password("admin123"),
        first_name="Admin",
        last_name="User",
        balance=10000.0,
        role="admin"
    )
    test_db.add(admin)
    test_db.commit()
    test_db.refresh(admin)
    return admin


@pytest.fixture
def sample_portfolio(test_db, sample_user):
    """Create a sample portfolio for testing"""
    from app.models import PortfolioModel
    
    portfolio = PortfolioModel(
        name="Test Portfolio",
        description="Test Description",
        investment_strategy="Growth",
        user_id=sample_user.id
    )
    test_db.add(portfolio)
    test_db.commit()
    test_db.refresh(portfolio)
    return portfolio


@pytest.fixture
def sample_security(test_db):
    """Create a sample security for testing"""
    from app.models import SecurityModel
    
    security = SecurityModel(
        ticker="AAPL",
        name="Apple Inc.",
        reference_price=175.0
    )
    test_db.add(security)
    test_db.commit()
    test_db.refresh(security)
    return security


@pytest.fixture
def sample_investment(test_db, sample_portfolio, sample_security):
    """Create a sample investment for testing"""
    from app.models import InvestmentModel
    
    investment = InvestmentModel(
        portfolio_id=sample_portfolio.id,
        security_id=sample_security.id,
        quantity=10
    )
    test_db.add(investment)
    test_db.commit()
    test_db.refresh(investment)
    return investment
