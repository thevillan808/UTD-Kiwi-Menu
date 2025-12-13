import pytest
from app import create_app
from app.db import db
from app.models import UserModel, PortfolioModel, SecurityModel


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


@pytest.fixture
def app():
    app = create_app()
    app.config.from_object(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def sample_data(app):
    with app.app_context():
        user = UserModel(
            username='testuser',
            password='test123',
            first_name='Test',
            last_name='User',
            balance=1000.0,
            role='user'
        )
        db.session.add(user)
        
        security = SecurityModel(
            ticker='AAPL',
            name='Apple Inc',
            reference_price=150.0
        )
        db.session.add(security)
        
        portfolio = PortfolioModel(
            name='My Portfolio',
            description='Test portfolio',
            investment_strategy='Growth',
            user_id=1
        )
        db.session.add(portfolio)
        db.session.commit()
        yield


# User endpoint tests
def test_get_users(client):
    response = client.get('/api/users')
    assert response.status_code == 200


def test_create_user(client):
    data = {
        'username': 'john',
        'password': 'pass123',
        'first_name': 'John',
        'last_name': 'Doe',
        'balance': 500.0,
        'role': 'user'
    }
    response = client.post('/api/users', json=data)
    assert response.status_code == 201


def test_get_user(client, sample_data):
    response = client.get('/api/users/testuser')
    assert response.status_code == 200
    assert response.json['username'] == 'testuser'


def test_delete_user(client, sample_data):
    response = client.delete('/api/users/testuser')
    assert response.status_code == 200


# Portfolio endpoint tests
def test_get_portfolios(client):
    response = client.get('/api/portfolios')
    assert response.status_code == 200


def test_create_portfolio(client, sample_data):
    data = {
        'username': 'testuser',
        'name': 'New Portfolio',
        'description': 'My new portfolio',
        'investment_strategy': 'Value'
    }
    response = client.post('/api/portfolios', json=data)
    assert response.status_code == 201


def test_get_portfolio(client, sample_data):
    response = client.get('/api/portfolios/1')
    assert response.status_code == 200
    assert response.json['name'] == 'My Portfolio'


def test_delete_portfolio(client, sample_data):
    response = client.delete('/api/portfolios/1')
    assert response.status_code == 200


def test_add_security_to_portfolio(client, sample_data):
    data = {'ticker': 'AAPL', 'quantity': 10}
    response = client.post('/api/portfolios/1/securities', json=data)
    assert response.status_code == 201


def test_remove_security_from_portfolio(client, sample_data):
    # First add the security
    client.post('/api/portfolios/1/securities', json={'ticker': 'AAPL', 'quantity': 10})
    # Then remove it
    response = client.delete('/api/portfolios/1/securities/AAPL')
    assert response.status_code == 200


# Security endpoint tests
def test_get_securities(client):
    response = client.get('/api/securities')
    assert response.status_code == 200


def test_create_security(client):
    data = {
        'ticker': 'MSFT',
        'name': 'Microsoft',
        'asset_type': 'Stock'
    }
    response = client.post('/api/securities', json=data)
    assert response.status_code == 201


# Error handling tests
def test_user_not_found(client):
    response = client.get('/api/users/nonexistent')
    assert response.status_code == 404


def test_portfolio_not_found(client):
    response = client.get('/api/portfolios/999')
    assert response.status_code == 404


def test_invalid_json(client):
    response = client.post('/api/users', data='invalid', content_type='application/json')
    assert response.status_code in [400, 500]
