import sqlite3

db = 'ponder.db'


def dump_db():
    conn = sqlite3.connect(db)
    c = conn.cursor()

    sql_query = c.execute(f'''SELECT * from status_table;''').fetchall()
    print(c.execute('''PRAGMA table_info(status_table);''').fetchall())

    print(sql_query)

    conn.commit()
    conn.close()


def delete_db_row(username):
    conn = sqlite3.connect(db)
    c = conn.cursor()

    c.execute(f'''DELETE from status_table WHERE username='{username}';''')

    c.execute(f'''DELETE from auth_table WHERE username='{username}';''')

    c.execute(f'''DELETE from data_table WHERE username='{username}';''')

    conn.commit()
    conn.close()


def delete_db_rows():
    conn = sqlite3.connect(db)
    c = conn.cursor()

    c.execute(f'''DELETE from status_table;''')

    c.execute(f'''DELETE from auth_table;''')

    c.execute(f'''DELETE from data_table;''')

    conn.commit()
    conn.close()


if __name__ == '__main__':
    dump_db()
