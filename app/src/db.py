import sqlite3


def create_tables(db):
    conn = sqlite3.connect(db)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS auth_table ('''
              '''username message_text, '''
              '''password message_text, '''
              '''firstname message_text, '''
              '''lastname message_text, '''
              '''email message_text, '''
              '''classes message_text);''')

    c.execute('''CREATE TABLE IF NOT EXISTS data_table ('''
              '''username message_text, '''
              '''noise integer, '''
              '''collab integer, '''
              '''learn_style integer, '''
              '''env integer);''')

    c.execute('''CREATE TABLE IF NOT EXISTS class_table ('''
              '''username message_text, '''
              '''firstname message_text, '''
              '''lastname message_text, '''
              '''email message_text);''')

    c.execute('''CREATE TABLE IF NOT EXISTS matches_table ('''
              '''username message_text, '''
              '''swipes message_text, '''
              '''swiped_on message_text, '''
              '''matches message_text);''')

    conn.commit()
    conn.close()


def create_user(db, username, password, firstname, lastname, email):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    user = c.execute('''SELECT * FROM auth_table WHERE username=?;''',
                     (username,)).fetchone()
    if not user:
        c.execute('''INSERT into auth_table VALUES (?,?,?,?,?,?);''',
                  (username, password, firstname, lastname, email, 'PLACEHOLDER'))
    conn.commit()
    conn.close()

    if not user:
        return True
    return False


def login_user(db, username, password):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    user = c.execute('''SELECT * FROM auth_table WHERE username=? AND password=?;''',
                     (username, password)).fetchone()
    conn.commit()
    conn.close()

    if user:
        return user
    return False


def get_next_match(db):
    raise NotImplementedError
