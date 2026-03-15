from sqlalchemy.exc import IntegrityError

from app.db import db
from app.models.User import User


class UnsupportedUserOperationError(Exception):
    pass


def get_all_users():
    return db.session.query(User).all()


def get_user_by_username(username):
    if not username:
        raise UnsupportedUserOperationError('Username cannot be empty')
    return db.session.query(User).filter_by(username=username).one_or_none()


def create_user(username, password, first_name, last_name, balance):
    user = User(
        username=username,
        password=password,
        firstname=first_name,
        lastname=last_name,
        balance=balance,
    )
    db.session.add(user)
    try:
        db.session.flush()
    except IntegrityError:
        db.session.rollback()
        raise UnsupportedUserOperationError(f'User {username} already exists')
    return user


def delete_user(username):
    user = get_user_by_username(username)
    if user is None:
        raise UnsupportedUserOperationError(f'User {username} does not exist')
    if username == 'admin':
        raise UnsupportedUserOperationError('Cannot delete admin user')
    if user.portfolios:
        raise UnsupportedUserOperationError(f'User {username} has dependencies and cannot be deleted')
    db.session.delete(user)
    db.session.flush()


def update_user_balance(username, amount):
    user = get_user_by_username(username)
    if user is None:
        raise UnsupportedUserOperationError(f'User {username} does not exist')
    user.balance = amount
    db.session.flush()
