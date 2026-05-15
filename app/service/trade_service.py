import datetime

from app.db import db
from app.models import Investment, Portfolio, Transaction
from app.service.alpha_vantage_client import get_quote


class TradeExecutionException(Exception):
    pass


class InsufficientFundsError(Exception):
    pass


def execute_purchase_order(portfolio_id: int, ticker: str, quantity: int):
    if portfolio_id is None or not ticker or not quantity or quantity <= 0:
        raise TradeExecutionException(
            f'Invalid purchase order parameters [portfolio_id={portfolio_id}, ticker={ticker}, quantity={quantity}]'
        )

    portfolio = db.session.query(Portfolio).filter_by(id=portfolio_id).one_or_none()
    if not portfolio:
        raise TradeExecutionException(f'Portfolio with id {portfolio_id} does not exist.')
    user = portfolio.user
    if not user:
        raise TradeExecutionException(f'User associated with the portfolio ({portfolio_id}) does not exist.')

    quote = get_quote(ticker)
    if not quote:
        raise TradeExecutionException(f'Security with ticker {ticker} does not exist.')

    total_cost = quote.price * quantity
    if user.balance < total_cost:
        raise InsufficientFundsError('Insufficient funds to complete the purchase.')

    existing_investment = None
    for inv in portfolio.investments:
        if inv.ticker == ticker:
            existing_investment = inv
            break
    if existing_investment:
        existing_investment.quantity += quantity
    else:
        portfolio.investments.append(Investment(ticker=ticker, quantity=quantity))

    user.balance -= total_cost
    db.session.add(
        Transaction(
            portfolio_id=portfolio.id,
            username=user.username,
            ticker=ticker,
            quantity=quantity,
            price=quote.price,
            transaction_type='BUY',
            date_time=datetime.datetime.now(),
        )
    )
    db.session.flush()


def liquidate_investment(portfolio_id: int, ticker: str, quantity: int):
    portfolio = db.session.query(Portfolio).filter_by(id=portfolio_id).one_or_none()
    if not portfolio:
        raise TradeExecutionException(f'Portfolio with id {portfolio_id} does not exist')
    user = portfolio.user

    quote = get_quote(ticker)
    if not quote:
        raise TradeExecutionException(f'Security with ticker {ticker} does not exist.')

    investment = None
    for inv in portfolio.investments:
        if inv.ticker == ticker:
            investment = inv
            break
    if not investment:
        raise TradeExecutionException(
            f'No investment with ticker {ticker} exists in portfolio with id {portfolio_id}'
        )
    if investment.quantity < quantity:
        raise TradeExecutionException(
            f'Cannot liquidate {quantity} shares of {ticker}. Only {investment.quantity} shares available in portfolio'
        )

    sale_price = quote.price
    total_proceeds = sale_price * quantity
    user.balance += total_proceeds
    if investment.quantity == quantity:
        db.session.delete(investment)
    else:
        investment.quantity -= quantity
    db.session.add(
        Transaction(
            portfolio_id=portfolio.id,
            username=user.username,
            ticker=ticker,
            quantity=quantity,
            price=sale_price,
            transaction_type='SELL',
            date_time=datetime.datetime.now(),
        )
    )
    db.session.flush()
