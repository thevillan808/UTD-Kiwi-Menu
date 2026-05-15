from unittest.mock import MagicMock, patch

import jwt
import pytest

from app.auth.auth import validate_token


def test_no_token_returns_403(client):
    resp = client.get('/users/')
    assert resp.status_code == 403


def test_bad_token_returns_403(client):
    resp = client.get('/users/', headers={'Authorization': 'Bearer bad.token.here'})
    assert resp.status_code == 403


def test_missing_bearer_prefix_returns_403(client):
    resp = client.get('/users/', headers={'Authorization': 'notabearer'})
    assert resp.status_code == 403


def test_validate_token_raises_on_bad_token(app):
    with pytest.raises(Exception):
        validate_token('not.a.real.jwt')


def test_valid_token_allows_access(client, app):
    with patch('app.auth.auth.validate_token') as mock_validate:
        mock_validate.return_value = {'cognito:username': 'admin'}
        resp = client.get('/users/', headers={'Authorization': 'Bearer fake_token'})
        # should not be 403 since token is valid
        assert resp.status_code != 403
