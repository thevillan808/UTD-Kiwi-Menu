import pytest
import app.service.portfolio_service as portfolio_service
import app.service.user_service as user_service
from app.models import Investment, Portfolio, User


@pytest.fixture(autouse=True)
def setup(db_session):
    user = User(username='testuser', password='testpass', firstname='Test', lastname='User', balance=1000.0)
    db_session.add(user)
    db_session.commit()
    portfolio1 = Portfolio(name='Portfolio 1', description='First portfolio', user=user)
    portfolio2 = Portfolio(name='Portfolio 2', description='Second portfolio', user=user)
    db_session.add_all([portfolio1, portfolio2])
    db_session.flush()
    inv = Investment(ticker='AAPL', quantity=10)
    inv.portfolio_id = portfolio1.id
    db_session.add(inv)
    db_session.commit()
    return {
        'user': user,
        'portfolio1': portfolio1,
        'portfolio2': portfolio2,
    }


def test_get_all_portfolios(setup, db_session):
    portfolios = portfolio_service.get_all_portfolios()
    names = [p.name for p in portfolios]
    assert 'Portfolio 1' in names
    assert 'Portfolio 2' in names


def test_get_portfolio_by_id(setup, db_session):
    p = setup['portfolio1']
    retrieved = portfolio_service.get_portfolio_by_id(p.id)
    assert retrieved is not None
    assert retrieved.name == 'Portfolio 1'


def test_get_portfolio_by_invalid_id(db_session):
    assert portfolio_service.get_portfolio_by_id(9999) is None


def test_get_portfolios_by_user(setup, db_session):
    user = setup['user']
    portfolios = portfolio_service.get_portfolios_by_user(user)
    assert len(portfolios) == 2


def test_create_portfolio(setup, db_session):
    user = setup['user']
    portfolio_service.create_portfolio('New Portfolio', 'A description', user)
    db_session.commit()
    portfolios = portfolio_service.get_portfolios_by_user(user)
    assert len(portfolios) == 3


def test_create_portfolio_invalid_input(setup, db_session):
    user = setup['user']
    with pytest.raises(portfolio_service.UnsupportedPortfolioOperationError):
        portfolio_service.create_portfolio('', 'desc', user)
    with pytest.raises(portfolio_service.UnsupportedPortfolioOperationError):
        portfolio_service.create_portfolio('Name', '', user)


def test_delete_portfolio(setup, db_session):
    user = setup['user']
    p = Portfolio(name='To Delete', description='delete me', user=user)
    db_session.add(p)
    db_session.commit()
    portfolio_service.delete_portfolio(p.id)
    db_session.commit()
    assert portfolio_service.get_portfolio_by_id(p.id) is None


def test_delete_portfolio_invalid_id(db_session):
    with pytest.raises(portfolio_service.UnsupportedPortfolioOperationError):
        portfolio_service.delete_portfolio(9999)
