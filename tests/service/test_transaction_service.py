import datetime
import pytest
from app.models import Portfolio, Transaction, User
from app.service import transaction_service


@pytest.fixture(autouse=True)
def setup(db_session):
    test_user = User(username='txuser', password='pass', firstname='Tx', lastname='User', balance=500.00)
    db_session.add(test_user)
    db_session.commit()
    test_portfolio = Portfolio(name='Tx Portfolio', description='for tx tests', user=test_user)
    db_session.add(test_portfolio)
    db_session.commit()
    txs = [
        Transaction(
            portfolio_id=test_portfolio.id,
            username=test_user.username,
            ticker='AAPL',
            quantity=10,
            price=150.00,
            transaction_type='BUY',
            date_time=datetime.datetime.now(),
        ),
        Transaction(
            portfolio_id=test_portfolio.id,
            username=test_user.username,
            ticker='GOOGL',
            quantity=5,
            price=250.00,
            transaction_type='BUY',
            date_time=datetime.datetime.now(),
        ),
    ]
    db_session.add_all(txs)
    db_session.commit()
    yield {'user': test_user, 'portfolio': test_portfolio}


def test_get_transactions_by_user(setup, db_session):
    user = setup['user']
    txs = transaction_service.get_transactions_by_user(user.username)
    assert len(txs) == 2
    assert all(t.username == user.username for t in txs)


def test_get_transactions_by_portfolio(setup, db_session):
    portfolio = setup['portfolio']
    txs = transaction_service.get_transactions_by_portfolio_id(portfolio.id)
    assert len(txs) == 2
    assert all(t.portfolio_id == portfolio.id for t in txs)


def test_get_transactions_by_ticker(setup, db_session):
    txs = transaction_service.get_transactions_by_ticker('AAPL')
    assert len(txs) == 1
    assert txs[0].ticker == 'AAPL'
