from dataclasses import dataclass

import requests
from flask import current_app


@dataclass
class SecurityQuote:
    ticker: str
    date: str
    price: float
    issuer: str


def _get_api_key():
    return current_app.config.get('ALPHA_VANTAGE_API_KEY', '')


def get_company_name(ticker):
    from app.extensions import cache

    cache_key = f'company_name:{ticker}'
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    api_key = _get_api_key()
    url = 'https://www.alphavantage.co/query'
    params = {
        'function': 'OVERVIEW',
        'symbol': ticker,
        'apikey': api_key,
    }
    response = requests.get(url, params=params, timeout=10)
    data = response.json()

    name = data.get('Name')
    if not name:
        return None

    cache.set(cache_key, name)
    return name


def get_price_data(ticker):
    from app.extensions import cache

    cache_key = f'price_data:{ticker}'
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    api_key = _get_api_key()
    url = 'https://www.alphavantage.co/query'
    params = {
        'function': 'TIME_SERIES_DAILY',
        'symbol': ticker,
        'apikey': api_key,
    }
    response = requests.get(url, params=params, timeout=10)
    data = response.json()

    time_series = data.get('Time Series (Daily)')
    if not time_series:
        return None

    dates = list(time_series.keys())
    dates.sort()
    latest_date = dates[-1]
    day = time_series[latest_date]
    result = {
        'date': latest_date,
        'open': float(day['1. open']),
        'high': float(day['2. high']),
        'low': float(day['3. low']),
        'close': float(day['4. close']),
        'volume': int(day['5. volume']),
    }

    cache.set(cache_key, result)
    return result


def get_quote(ticker):
    name = get_company_name(ticker)
    if not name:
        return None

    price_data = get_price_data(ticker)
    if not price_data:
        return None

    return SecurityQuote(
        ticker=ticker,
        date=price_data['date'],
        price=price_data['close'],
        issuer=name,
    )
