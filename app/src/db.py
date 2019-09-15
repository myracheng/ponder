import os
import sqlite3
import pandas as pd
import numpy as np
import json
import random


class PonderUser:
    def __init__(self, username, firstname, lastname, major='Course 6', tagline='lets get this bread', shared_courses='6.006', img='https://static.thenounproject.com/png/33874-200.png?fbclid=IwAR2yz6_wN5QrbNJJXytATKJlePB20nhWVRYN4OzxUhp021dmAvwLMI1Zopc'):
        self.username = username
        self.firstname = firstname
        self.lastname = lastname
        self.major = 'Course ' + ', '.join([str(random.randint(1, 24)) for _ in range(random.randint(1, 3))])
        self.tagline = tagline
        self.shared_courses = shared_courses
        self.img = img


def create_tables():
    conn = sqlite3.connect('ponder.db')
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
              '''classes message_text, '''
              '''major message_text, '''
              '''env integer);''')

    c.execute('''CREATE TABLE IF NOT EXISTS status_table ('''
              '''username message_text, '''
              '''suggestions message_text,'''
              '''swipe_to message_text, ''' #people they swiped on
              '''swiped_from message_text, ''' #people who swiped on them
              '''nos message_text,''' #people who are rejected
              '''pairs message_text);''')

    conn.commit()
    conn.close()

#find pairwise groups (for get_groups)
def get_pairs():
    con = sqlite3.connect('ponder.db')
    c = con.cursor()
    df = pd.read_sql_query('''SELECT username, swipe_to, swiped_from from status_table''', con)
    all_pairs = []
    for ind, row in df.iterrows():
        pairs = []
        for user in json.loads(row['swipe_to']):
            if user in json.loads(row['swiped_from']):
                pairs.append(user)
        all_pairs.append(json.dumps(pairs))

    c.execute('''REPLACE into status_table (pairs) VALUES (?)''', json.dumps(all_pairs))    


#get chatrooms
def get_groups():
    conn = sqlite3.connect('ponder.db')
    df = pd.read_sql_query('''SELECT username, pairs FROM status_table;''', conn)
    print(df)
    study_groups = make_groups_from_df(df)
    return study_groups


def update_nos(user, new_no):
    conn = sqlite3.connect('ponder.db')
    c = conn.cursor()
    nos = json.loads(c.execute(f'''SELECT nos from status_table WHERE username='{user}';''').fetchone()[0])
    nos.append(new_no)
    nosjson = json.dumps(nos)
    sql_query = f'''UPDATE status_table SET nos='{nosjson}' WHERE username='{user}';'''
    c.execute(sql_query)
    print("after nos")
    conn.commit()
    conn.close()


def update_yes(user, new_yes):
    conn = sqlite3.connect('ponder.db')
    c = conn.cursor()
    yes = json.loads(c.execute(f'''SELECT swipe_to from status_table WHERE username='{user}';''').fetchone()[0])
    yes.append(new_yes)
    yeejson = json.dumps(yes)
    sql_query = f'''UPDATE status_table SET swipe_to='{yeejson}' WHERE username='{user}';'''
    c.execute(sql_query)
    print("after yes")
    conn.commit()
    conn.close()


def get_suggestions(username):
    con = sqlite3.connect('ponder.db')
    c = con.cursor()
    df = pd.read_sql_query('''SELECT * from data_table;''', con)
    # try: 
    nos = json.loads(c.execute(f'''SELECT nos from status_table WHERE username = '{username}';''').fetchone()[0])
    # except:
        # nos = []
    # try:
    swipe_to = json.loads(c.execute(f'''SELECT swipe_to from status_table WHERE username='{username}';''').fetchone()[0])
    # except:
        # swipe_to = []

    suggestions = get_suggestions_from_df(df, username)
    sql_query = f'''SELECT * from status_table WHERE username='{username}';'''
    status_info = pd.read_sql_query(sql_query, con)
    print('''suggestions are!''')
    print(suggestions)
    # filter out people already rejected or accepted
    for name in suggestions:
        if name in nos or name in swipe_to:
            suggestions.remove(name)
    suggs = json.dumps(suggestions)
    print('''suggestions are! after filtering''')
    print(suggs)
    # print(type(suggs))

    # c.execute('''REPLACE into status_table VALUES (?,?,?,?,?,?)''', (username, suggs, status_info['swipe_to'][0],status_info['swiped_from'][0],status_info['nos'][0], status_info['pairs'][0]))

    sql_query = f'''UPDATE status_table SET suggestions='{suggs}' WHERE username='{username}';'''
    c.execute(sql_query)


    con.commit()
    con.close()


#return PonderUser
def get_next_suggestion(username):
    get_suggestions(username)
    con = sqlite3.connect('ponder.db')
    c = con.cursor()
    df = pd.read_sql_query('''SELECT * from status_table''', con)
    print(df)
    # print(c.execute("SELECT suggestions from status_table WHERE username = (?)",str(username)).fetchone())
    suggs = json.loads(c.execute(f'''SELECT suggestions from status_table WHERE username='{username}';''').fetchone()[0])
    already_seen = json.loads(c.execute(f'''SELECT swipe_to from status_table WHERE username='{username}';''').fetchone()[0])
    already_seen.extend(json.loads(c.execute(f'''SELECT nos from status_table WHERE username='{username}';''').fetchone()[0]))
    print('AAAAAAAAAAAAAA', suggs)

    for sugg in suggs:
        if sugg not in already_seen:
            break

    user = c.execute(f'''SELECT * FROM auth_table WHERE username='{sugg}';''').fetchone()
    return PonderUser(user[0], user[2], user[3])


def get_user(username):
    conn = sqlite3.connect('ponder.db')
    c = conn.cursor()
    get_suggestions(username) # make sure it's updated
    suggested = json.loads(c.execute('''SELECT * FROM auth_table WHERE username=?;''',
                     (username, )).fetchone())[0]
    conn.commit()
    conn.close()
    return PonderUser(suggested[0], suggested[2], suggested[3])


def create_user(username, password, firstname, lastname, email):
    conn = sqlite3.connect('ponder.db')
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


def create_profile(username, noise, collab, learn_style, classes, major, env):
    conn = sqlite3.connect('ponder.db')
    c = conn.cursor()
    c.execute('''REPLACE into data_table VALUES (?,?,?,?,?,?,?);''',
                (username, noise, collab, learn_style, classes, major, env))
    print('''FIRST CWD IS ''' + str(os.getcwd()))
    c.execute('''REPLACE into status_table VALUES (?,?,?,?,?,?);''',
              (username, '[]', '[]', '[]', '[]', '[]'))
    conn.commit()
    conn.close()


def login_user(username, password):
    conn = sqlite3.connect('ponder.db')
    c = conn.cursor()
    user = c.execute('''SELECT * FROM auth_table WHERE username=? AND password=?;''',
                     (username, password)).fetchone()
    conn.commit()
    conn.close()

    if user:
        return user
    return False

def get_suggestions_from_df(df, username):
    print(df)
    output = df['username'].unique().tolist()
    print(output)
    return output

def make_groups_from_df(pairs_df):

    # print(pairs_df)
    # return [['a', 'b', 'c']]
    # return [list(x) for x in pairs_df[0]['pairs']]
    # try:
        sgroups3 = []
        sgroups4 = []
        seen = set()
        output_df = pd.DataFrame({'names': pairs_df['username']})
        for ind, row in pairs_df.iterrows():
            for student in row['pairs']: #all possible pairs... find if 3rd persn
                possible_thirds = set(pairs_df[pairs_df['username'] == student]['pairs'].values[0]).intersection(row['pairs'])
                for name in possible_thirds:
                    sgroup = frozenset([row['username'], student, name])
                    # if sgroup not in seen and not seen.add(sgroup):
                    #     possible_fourths = set.intersection(set((pairs_df[pairs_df['username'] == name]['pairs'].values[0])), set(pairs_df[pairs_df['username'] == student]['pairs'].values[0]), set(row['pairs']))
                    #     if bool(possible_fourths):
                    #         for name2 in possible_fourths:
                    #             sgroup4 = frozenset([row['username'], student, name, name2])
                    #             if sgroup4 not in seen and not seen.add(sgroup4):
                    #                 sgroups4.append(sgroup4)
                    #     else:
                    sgroups3.append(sgroup)
        # sgroups3.extend(sgroups4)
        return [list(x) for x in sgroups3]
    # except Error:
    #     return []
