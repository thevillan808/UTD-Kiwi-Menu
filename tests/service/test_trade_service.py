from unittest.mock import MagicMock, patch

import pytest

from app.models import Investment, Portfolio, User
from app.service import trade_service, transaction_service
from app.service.trade_service import InsufficientFundsError, TradeExecutionException


@pytest.fixture(autouse=True)
def setup(db_session):
    user = User(username='trader', password='pass', firstname='Trade', lastname='User', balance=5000.00)
    db_session.add(user)
    db_session.commit()
    portfolio = Portfolio(name='Trade Portfolio', description='for trades', user=user)
    db_session.add(portfolio)
    db_session.commit()
    return {'user': user, 'portfolio': portfolio}


def _mock_quote(ticker, price=150.0):
    from dataclasses import dataclass

    @dataclass
    class Q:
        ticker: str
        date: str
        price: float
        issuer: str

    return Q(ticker=ticker, date='2024-01-02', price=price, issuer='Test Corp')


def test_buy_creates_investment(setup, db_session):
    portfolio = setup['portfolio']
    user = setup['user']
    with patch('app.service.trade_service.get_quote') as mock_q:
        mock_q.return_value = _mock_quote('AAPL', 150.0)
        trade_service.execute_purchase_order(portfolio.id, 'AAPL', 2)
        db_session.commit()

    inv = db_session.query(Investment).filter_by(portfolio_id=portfolio.id, ticker='AAPL').one_or_none()
    assert inv is not None
    assert inv.quantity == 2
    db_session.refresh(user)
    assert user.balance == 5000.00 - 300.00


def test_buy_adds_transaction_record(setup, db_session):
    portfolio = setup['portfolio']
    with patch('app.service.trade_service.get_quote') as mock_q:
        mock_q.return_value = _mock_quote('MSFT', 300.0)
        trade_service.execute_purchase_order(portfolio.id, 'MSFT', 1)
        db_session.commit()

    txs = transaction_service.get_transactions_by_portfolio_id(portfolio.id)
    assert len(txs) == 1
    assert txs[0].ticker == 'MSFT'
    assert txs[0].transaction_type == 'BUY'
    assert txs[0].quantity == 1
    assert txs[0].price == 300.0


def test_buy_insufficient_funds(setup, db_session):
    portfolio = setup['portfolio']
    with patch('app.service.trade_service.get_quote') as mock_q:
        mock_q.return_value = _mock_quote('AAPL', 10000.0)
        with pytest.raises(InsufficientFundsError):
            trade_service.execute_purchase_order(portfolio.id, 'AAPL', 10)


def test_buy_invalid_ticker(setup, db_session):
    portfolio = setup['portfolio']
    with patch('app.service.trade_service.get_quote') as mock_q:
        mock_q.return_value = None
        with pytest.raises(TradeExecutionException):
            trade_service.execute_purchase_order(portfolio.id, 'FAKEXXX', 1)


def test_buy_invalid_portfolio(db_session):
    with patch('app.service.trade_service.get_quote') as mock_q:
        mock_q.return_value = _mock_quote('AAPL', 150.0)
        with pytest.raises(TradeExecutionException):
            trade_service.execute_purchase_order(9999, 'AAPL', 1)


def test_sell_reduces_investment(setup, db_session):
    portfolio = setup['portfolio']
    user = setup['user']
    # first buy some shares
    with patch('app.service.trade_service.get_quote') as mock_q:
        mock_q.return_value = _mock_quote('AAPL', 150.0)
        trade_service.execute_purchase_order(portfolio.id, 'AAPL', 10)
        db_session.commit()

    with patch('app.service.trade_service.get_quote') as mock_q:
        mock_q.return_value = _mock_quote('AAPL', 160.0)
        trade_service.liquidate_investment(portfolio.id, 'AAPL', 5)
        db_session.commit()

    inv = db_session.query(Investment).filter_by(portfolio_id=portfolio.id, ticker='AAPL').one_or_none()
    assert inv is not None
    assert inv.quantity == 5


def test_sell_removes_investment_when_all_sold(setup, db_session):
    portfolio = setup['portfolio']
    with patch('app.service.trade_service.get_quote') as mock_q:
        mock_q.return_value = _mock_quote('AAPL', 150.0)
        trade_service.execute_purchase_order(portfolio.id, 'AAPL', 5)
        db_session.commit()

    with patch('app.service.trade_service.get_quote') as mock_q:
        mock_q.return_value = _mock_quote('AAPL', 150.0)
        trade_service.liquidate_investment(portfolio.id, 'AAPL', 5)
        db_session.commit()

    inv = db_session.query(Investment).filter_by(portfolio_id=portfolio.id, ticker='AAPL').one_or_none()
    assert inv is None


def test_sell_insufficient_quantity(setup, db_session):
    portfolio = setup['portfolio']
    with patch('app.service.trade_service.get_quote') as mock_q:
        mock_q.return_value = _mock_quote('AAPL', 150.0)
        trade_service.execute_purchase_order(portfolio.id, 'AAPL', 3)
        db_session.commit()

    with patch('app.service.trade_service.get_quote') as mock_q:
        mock_q.return_value = _mock_quote('AAPL', 150.0)
        with pytest.raises(TradeExecutionException) as exc:
            trade_service.liquidate_investment(portfolio.id, 'AAPL', 100)
        assert 'Cannot liquidate' in str(exc.value)


def test_sell_no_investment_for_ticker(setup, db_session):
    portfolio = setup['portfolio']
    with patch('app.service.trade_service.get_quote') as mock_q:
        mock_q.return_value = _mock_quote('MSFT', 300.0)
        with pytest.raises(TradeExecutionException):
            trade_service.liquidate_investment(portfolio.id, 'MSFT', 1)
