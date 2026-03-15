import pytest
from pydantic import ValidationError

from app.schemas import BuyTradeRequest, CreatePortfolioRequest, CreateUserRequest, SellTradeRequest, GrantAccessRequest


def test_buy_trade_request_valid():
    req = BuyTradeRequest(ticker='AAPL', portfolio_id=1, quantity=10)
    assert req.ticker == 'AAPL'
    assert req.portfolio_id == 1
    assert req.quantity == 10


def test_buy_trade_request_missing_ticker():
    with pytest.raises(ValidationError):
        BuyTradeRequest(portfolio_id=1, quantity=10)


def test_buy_trade_request_missing_portfolio_id():
    with pytest.raises(ValidationError):
        BuyTradeRequest(ticker='AAPL', quantity=10)


def test_buy_trade_request_wrong_type():
    with pytest.raises(ValidationError):
        BuyTradeRequest(ticker='AAPL', portfolio_id='not_an_int', quantity=10)


def test_sell_trade_request_valid():
    req = SellTradeRequest(ticker='MSFT', portfolio_id=2, quantity=5)
    assert req.ticker == 'MSFT'


def test_sell_trade_request_missing_quantity():
    with pytest.raises(ValidationError):
        SellTradeRequest(ticker='MSFT', portfolio_id=2)


def test_create_portfolio_request_valid():
    req = CreatePortfolioRequest(username='alice', name='My Portfolio', description='desc')
    assert req.username == 'alice'


def test_create_portfolio_request_missing_name():
    with pytest.raises(ValidationError):
        CreatePortfolioRequest(username='alice', description='desc')


def test_create_user_request_valid():
    req = CreateUserRequest(username='bob', password='pw', firstname='Bob', lastname='Smith', balance=100.0)
    assert req.balance == 100.0


def test_create_user_request_wrong_balance_type():
    with pytest.raises(ValidationError):
        CreateUserRequest(username='bob', password='pw', firstname='Bob', lastname='Smith', balance='notanumber')


def test_grant_access_request_valid():
    req = GrantAccessRequest(username='alice', role='viewer')
    assert req.role == 'viewer'


def test_grant_access_request_missing_role():
    with pytest.raises(ValidationError):
        GrantAccessRequest(username='alice')


def test_validation_error_handler_returns_422(client):
    from unittest.mock import patch
    from pydantic import ValidationError as VE

    with patch('app.auth.auth.validate_token') as mock_val:
        mock_val.return_value = {'cognito:username': 'admin'}
        # Send bad JSON body to a POST endpoint that uses Pydantic
        resp = client.post(
            '/trades/buy',
            json={'bad_field': 'wrong'},
            headers={'Authorization': 'Bearer fake'},
        )
        assert resp.status_code == 422
