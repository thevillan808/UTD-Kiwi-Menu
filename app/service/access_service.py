from app.db import db
from app.models.PortfolioAccess import PortfolioAccess


class AccessError(Exception):
    pass


def grant_access(portfolio_id, username, role):
    if role not in ('viewer', 'manager'):
        raise AccessError(f'role must be viewer or manager, got: {role}')
    existing = db.session.query(PortfolioAccess).filter_by(
        portfolio_id=portfolio_id, username=username
    ).one_or_none()
    if existing:
        existing.role = role
    else:
        db.session.add(PortfolioAccess(portfolio_id=portfolio_id, username=username, role=role))
    db.session.flush()


def revoke_access(portfolio_id, username):
    record = db.session.query(PortfolioAccess).filter_by(
        portfolio_id=portfolio_id, username=username
    ).one_or_none()
    if not record:
        raise AccessError(f'user {username} does not have access to portfolio {portfolio_id}')
    db.session.delete(record)
    db.session.flush()


def get_role(portfolio_id, username):
    record = db.session.query(PortfolioAccess).filter_by(
        portfolio_id=portfolio_id, username=username
    ).one_or_none()
    if record is None:
        return None
    return record.role


def can_view(portfolio_id, username):
    role = get_role(portfolio_id, username)
    return role in ('viewer', 'manager')


def can_manage(portfolio_id, username):
    return get_role(portfolio_id, username) == 'manager'
