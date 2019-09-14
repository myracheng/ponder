import sqlite3
from .user import PonderUser


db = 'ponder.db'  # TODO: actually connect a db to this D:


def auth(username, password):
    # TODO actually implement this
    if username == 'username' and password == 'password':
        return PonderUser(username, 'User', 'Name')
    return False
