from unittest.mock import patch

import pytest

from app.models import Portfolio, User
from app.service import access_service


@pytest.fixture()
def owner_and_portfolio(db_session):
    owner = User(username='owner', password='pw', firstname='Own', lastname='Er', balance=1000.0)
    viewer = User(username='viewer_user', password='pw', firstname='View', lastname='Er', balance=500.0)
    manager = User(username='manager_user', password='pw', firstname='Mgr', lastname='User', balance=500.0)
    other = User(username='other_user', password='pw', firstname='Other', lastname='User', balance=500.0)
    db_session.add_all([owner, viewer, manager, other])
    db_session.commit()

    portfolio = Portfolio(name='Auth Portfolio', description='testing auth', user=owner)
    db_session.add(portfolio)
    db_session.commit()

    access_service.grant_access(portfolio.id, 'viewer_user', 'viewer')
    access_service.grant_access(portfolio.id, 'manager_user', 'manager')
    db_session.commit()

    return {'owner': owner, 'viewer': viewer, 'manager': manager, 'other': other, 'portfolio': portfolio}


def test_owner_can_view_portfolio(client, owner_and_portfolio):
    portfolio = owner_and_portfolio['portfolio']
    with patch('app.auth.auth.validate_token') as mock_val:
        mock_val.return_value = {'cognito:username': 'owner'}
        resp = client.get(f'/portfolios/{portfolio.id}', headers={'Authorization': 'Bearer fake'})
        assert resp.status_code == 200


def test_viewer_can_view_portfolio(client, owner_and_portfolio):
    portfolio = owner_and_portfolio['portfolio']
    with patch('app.auth.auth.validate_token') as mock_val:
        mock_val.return_value = {'cognito:username': 'viewer_user'}
        resp = client.get(f'/portfolios/{portfolio.id}', headers={'Authorization': 'Bearer fake'})
        assert resp.status_code == 200


def test_user_with_no_access_cannot_view(client, owner_and_portfolio):
    portfolio = owner_and_portfolio['portfolio']
    with patch('app.auth.auth.validate_token') as mock_val:
        mock_val.return_value = {'cognito:username': 'other_user'}
        resp = client.get(f'/portfolios/{portfolio.id}', headers={'Authorization': 'Bearer fake'})
        assert resp.status_code == 403


def test_viewer_cannot_trade(client, owner_and_portfolio):
    portfolio = owner_and_portfolio['portfolio']
    with patch('app.auth.auth.validate_token') as mock_val:
        mock_val.return_value = {'cognito:username': 'viewer_user'}
        resp = client.post(
            '/trades/buy',
            json={'ticker': 'AAPL', 'portfolio_id': portfolio.id, 'quantity': 1},
            headers={'Authorization': 'Bearer fake'},
        )
        assert resp.status_code == 403


def test_manager_can_trade(client, owner_and_portfolio):
    portfolio = owner_and_portfolio['portfolio']
    with patch('app.auth.auth.validate_token') as mock_val, \
         patch('app.service.trade_service.get_quote') as mock_q:
        mock_val.return_value = {'cognito:username': 'manager_user'}
        from dataclasses import dataclass

        @dataclass
        class Q:
            ticker: str
            date: str
            price: float
            issuer: str

        mock_q.return_value = Q(ticker='AAPL', date='2024-01-02', price=150.0, issuer='Apple')
        resp = client.post(
            '/trades/buy',
            json={'ticker': 'AAPL', 'portfolio_id': portfolio.id, 'quantity': 1},
            headers={'Authorization': 'Bearer fake'},
        )
        assert resp.status_code == 201


def test_manager_cannot_delete_portfolio(client, owner_and_portfolio):
    portfolio = owner_and_portfolio['portfolio']
    with patch('app.auth.auth.validate_token') as mock_val:
        mock_val.return_value = {'cognito:username': 'manager_user'}
        resp = client.delete(f'/portfolios/{portfolio.id}', headers={'Authorization': 'Bearer fake'})
        assert resp.status_code == 403


def test_owner_can_delete_portfolio(client, owner_and_portfolio, db_session):
    owner = owner_and_portfolio['owner']
    new_portfolio = Portfolio(name='Temp Portfolio', description='to be deleted', user=owner)
    db_session.add(new_portfolio)
    db_session.commit()
    with patch('app.auth.auth.validate_token') as mock_val:
        mock_val.return_value = {'cognito:username': 'owner'}
        resp = client.delete(f'/portfolios/{new_portfolio.id}', headers={'Authorization': 'Bearer fake'})
        assert resp.status_code == 200


def test_grant_access_endpoint(client, owner_and_portfolio):
    portfolio = owner_and_portfolio['portfolio']
    with patch('app.auth.auth.validate_token') as mock_val:
        mock_val.return_value = {'cognito:username': 'owner'}
        resp = client.post(
            f'/portfolios/{portfolio.id}/access',
            json={'username': 'other_user', 'role': 'viewer'},
            headers={'Authorization': 'Bearer fake'},
        )
        assert resp.status_code == 201


def test_non_owner_cannot_grant_access(client, owner_and_portfolio):
    portfolio = owner_and_portfolio['portfolio']
    with patch('app.auth.auth.validate_token') as mock_val:
        mock_val.return_value = {'cognito:username': 'viewer_user'}
        resp = client.post(
            f'/portfolios/{portfolio.id}/access',
            json={'username': 'other_user', 'role': 'viewer'},
            headers={'Authorization': 'Bearer fake'},
        )
        assert resp.status_code == 403
