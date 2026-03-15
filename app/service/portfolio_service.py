from app.db import db
from app.models.Investment import Investment
from app.models.Portfolio import Portfolio


class UnsupportedPortfolioOperationError(Exception):
    pass


def get_all_portfolios():
    return db.session.query(Portfolio).all()


def get_portfolio_by_id(portfolio_id):
    return db.session.query(Portfolio).filter_by(id=portfolio_id).one_or_none()


def get_portfolios_by_user(user):
    return db.session.query(Portfolio).filter_by(owner=user.username).all()


def create_portfolio(name, description, user):
    if not name:
        raise UnsupportedPortfolioOperationError('Portfolio name cannot be empty')
    if not description:
        raise UnsupportedPortfolioOperationError('Portfolio description cannot be empty')
    portfolio = Portfolio(name=name, description=description, user=user)
    db.session.add(portfolio)
    db.session.flush()
    return portfolio.id


def delete_portfolio(portfolio_id):
    portfolio = get_portfolio_by_id(portfolio_id)
    if portfolio is None:
        raise UnsupportedPortfolioOperationError(f'Portfolio {portfolio_id} not found')
    db.session.delete(portfolio)
    db.session.flush()


def list_investments(portfolio_id):
    return db.session.query(Investment).filter_by(portfolio_id=portfolio_id).all()
