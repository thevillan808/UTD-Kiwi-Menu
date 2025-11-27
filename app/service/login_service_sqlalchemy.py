from typing import Optional
from .. import db_sqlalchemy as db
from ..domain.User import User

def authenticate(username: str, password: str) -> Optional[User]:
    """Authenticate a user."""
    return db.authenticate(username, password)


def get_current_user() -> Optional[User]:
    """Return the currently logged-in user (session)."""
    return db.get_current_user()


def set_current_user(user: Optional[User]):
    """Set the current session user."""
    db.set_current_user(user)
