import pytest

from app import create_app
from app.config import TestConfig
from app.db import db as _db
from app.models.User import User


@pytest.fixture(scope='function')
def app():
    flask_app = create_app(TestConfig)
    ctx = flask_app.app_context()
    ctx.push()
    _db.create_all()
    admin = User(username='admin', password='admin', firstname='Admin', lastname='User', balance=1000.0)
    _db.session.add(admin)
    _db.session.commit()
    yield flask_app
    _db.session.remove()
    _db.drop_all()
    ctx.pop()


@pytest.fixture(scope='function')
def db_session(app):
    yield _db.session


@pytest.fixture(scope='function')
def client(app):
    return app.test_client()
