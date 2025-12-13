from typing import Optional
from .. import data_access as db
from ..domain.User import User

def authenticate(username: str, password: str) -> Optional[User]:
    return db.authenticate(username, password)


def get_current_user() -> Optional[User]:
    return db.get_current_user()


def set_current_user(user: Optional[User]):
    db.set_current_user(user)
