import pytest
import app.service.user_service as user_service
from app.models import User


def test_get_all_users(db_session):
    users = user_service.get_all_users()
    assert len(users) >= 1


def test_create_user(db_session):
    users_before = user_service.get_all_users()
    count = len(users_before)
    user_service.create_user('test_user75', 'xxx', 'Test', 'User', 100.00)
    db_session.commit()
    users_after = user_service.get_all_users()
    assert len(users_after) == count + 1
    u = user_service.get_user_by_username('test_user75')
    assert u is not None
    assert u.firstname == 'Test'
    assert u.balance == 100.00


def test_create_user_duplicate_username_raises(db_session):
    with pytest.raises(user_service.UnsupportedUserOperationError):
        user_service.create_user('admin', 'xxx', 'Admin', 'User', 100.00)


def test_delete_user(db_session):
    user_service.create_user('test_user77', 'xxx', 'Test', 'User', 150.00)
    db_session.commit()
    count = len(user_service.get_all_users())
    user_service.delete_user('test_user77')
    db_session.commit()
    assert len(user_service.get_all_users()) == count - 1


def test_delete_admin_user_raises(db_session):
    with pytest.raises(user_service.UnsupportedUserOperationError) as exc:
        user_service.delete_user('admin')
    assert 'Cannot delete admin user' in str(exc.value)


def test_delete_nonexistent_user_raises(db_session):
    with pytest.raises(user_service.UnsupportedUserOperationError) as exc:
        user_service.delete_user('nobody_here')
    assert 'does not exist' in str(exc.value)


def test_update_user_balance(db_session):
    user_service.update_user_balance('admin', 500.00)
    db_session.commit()
    u = user_service.get_user_by_username('admin')
    assert u.balance == 500.00


def test_update_nonexistent_user_balance_raises(db_session):
    with pytest.raises(user_service.UnsupportedUserOperationError):
        user_service.update_user_balance('nobody', 300.00)


def test_get_user_by_username(db_session):
    u = user_service.get_user_by_username('admin')
    assert u is not None
    assert u.username == 'admin'


def test_get_user_by_username_nonexistent(db_session):
    u = user_service.get_user_by_username('nonexistent_user')
    assert u is None


def test_get_user_by_username_empty_raises(db_session):
    with pytest.raises(user_service.UnsupportedUserOperationError):
        user_service.get_user_by_username('')


def test_delete_user_with_dependencies_raises(db_session):
    from app.service import portfolio_service
    user_service.create_user('user_dep', 'xxx', 'Dep', 'User', 200.00)
    db_session.commit()
    u = user_service.get_user_by_username('user_dep')
    portfolio_service.create_portfolio('My Portfolio', 'desc', u)
    db_session.commit()
    with pytest.raises(user_service.UnsupportedUserOperationError) as exc:
        user_service.delete_user('user_dep')
    assert 'dependencies' in str(exc.value)
