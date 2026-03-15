from unittest.mock import MagicMock, patch

import pytest

from app.service.alpha_vantage_client import get_company_name, get_price_data, get_quote
from app.service.security_service import SecurityException, get_all_securities, get_security_by_ticker
from app.models.Security import Security
from app.db import db as _db


FAKE_OVERVIEW = {
    'Name': 'Apple Inc.',
    'Symbol': 'AAPL',
}

FAKE_TIME_SERIES = {
    'Time Series (Daily)': {
        '2024-01-02': {
            '1. open': '185.00',
            '2. high': '188.00',
            '3. low': '184.00',
            '4. close': '186.50',
            '5. volume': '50000000',
        }
    }
}


def test_get_company_name_returns_name(app):
    with patch('app.service.alpha_vantage_client.requests.get') as mock_get:
        mock_resp = MagicMock()
        mock_resp.json.return_value = FAKE_OVERVIEW
        mock_get.return_value = mock_resp

        result = get_company_name('AAPL')
        assert result == 'Apple Inc.'
        mock_get.assert_called_once()


def test_get_company_name_returns_none_on_empty_response(app):
    with patch('app.service.alpha_vantage_client.requests.get') as mock_get:
        mock_resp = MagicMock()
        mock_resp.json.return_value = {}
        mock_get.return_value = mock_resp

        result = get_company_name('FAKEXYZ')
        assert result is None


def test_get_price_data_returns_dict(app):
    with patch('app.service.alpha_vantage_client.requests.get') as mock_get:
        mock_resp = MagicMock()
        mock_resp.json.return_value = FAKE_TIME_SERIES
        mock_get.return_value = mock_resp

        result = get_price_data('AAPL')
        assert result is not None
        assert result['close'] == 186.50
        assert result['date'] == '2024-01-02'


def test_get_price_data_returns_none_on_empty(app):
    with patch('app.service.alpha_vantage_client.requests.get') as mock_get:
        mock_resp = MagicMock()
        mock_resp.json.return_value = {}
        mock_get.return_value = mock_resp

        result = get_price_data('FAKEXYZ')
        assert result is None


def test_get_company_name_uses_cache(app):
    from app.extensions import cache
    cache.set('company_name:MSFT', 'Microsoft Corp.')

    with patch('app.service.alpha_vantage_client.requests.get') as mock_get:
        result = get_company_name('MSFT')
        assert result == 'Microsoft Corp.'
        mock_get.assert_not_called()


def test_get_price_data_uses_cache(app):
    from app.extensions import cache
    cached_val = {'date': '2024-01-02', 'close': 300.0, 'open': 295.0, 'high': 305.0, 'low': 294.0, 'volume': 1000000}
    cache.set('price_data:MSFT', cached_val)

    with patch('app.service.alpha_vantage_client.requests.get') as mock_get:
        result = get_price_data('MSFT')
        assert result == cached_val
        mock_get.assert_not_called()


def test_get_quote_returns_security_quote(app):
    with patch('app.service.alpha_vantage_client.get_company_name') as mock_name, \
         patch('app.service.alpha_vantage_client.get_price_data') as mock_price:
        mock_name.return_value = 'Apple Inc.'
        mock_price.return_value = {'date': '2024-01-02', 'close': 186.50, 'open': 185.0, 'high': 188.0, 'low': 184.0, 'volume': 5000000}

        result = get_quote('AAPL')
        assert result is not None
        assert result.ticker == 'AAPL'
        assert result.issuer == 'Apple Inc.'
        assert result.price == 186.50


# --- security_service tests ---

def test_get_all_securities_returns_empty_list(app):
    result = get_all_securities()
    assert result == []


def test_get_all_securities_returns_seeded_security(app):
    sec = Security(ticker='AAPL', issuer='Apple Inc.', price=186.50)
    _db.session.add(sec)
    _db.session.commit()

    result = get_all_securities()
    assert len(result) == 1
    assert result[0].ticker == 'AAPL'


def test_get_security_by_ticker_returns_none_when_missing(app):
    result = get_security_by_ticker('FAKEXYZ')
    assert result is None


def test_get_security_by_ticker_returns_security(app):
    sec = Security(ticker='TSLA', issuer='Tesla Inc.', price=250.0)
    _db.session.add(sec)
    _db.session.commit()

    result = get_security_by_ticker('TSLA')
    assert result is not None
    assert result.ticker == 'TSLA'


def test_get_all_securities_raises_on_db_error(app):
    with patch('app.service.security_service.db') as mock_db:
        mock_db.session.query.side_effect = Exception('DB error')
        with pytest.raises(SecurityException):
            get_all_securities()


def test_get_security_by_ticker_raises_on_db_error(app):
    with patch('app.service.security_service.db') as mock_db:
        mock_db.session.query.side_effect = Exception('DB error')
        with pytest.raises(SecurityException):
            get_security_by_ticker('AAPL')


def test_get_quote_returns_none_when_ticker_not_found(app):
    with patch('app.service.alpha_vantage_client.get_company_name') as mock_name:
        mock_name.return_value = None
        result = get_quote('BADTICKER')
        assert result is None
