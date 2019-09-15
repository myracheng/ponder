import sqlite3

from .user import PonderUser
from .db import login_user, create_user

def auth_user(username, password):
    user = login_user(username, password)

    if not user:
        return False
    return PonderUser(user[0], user[2], user[3])


def register_user(username, password, firstname, lastname, email):
    return create_user(username, password, firstname, lastname, email)
