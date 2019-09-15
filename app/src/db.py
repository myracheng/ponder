import os
import sqlite3
import pandas as pd
import numpy as np
import json


class PonderUser:
    def __init__(self, username, firstname, lastname):
        self.username = username
        self.firstname = firstname
        self.lastname = lastname


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
    df = pd.read_sql_query("SELECT username, swipe_to, swiped_from from status_table", con)
    all_pairs = []
    for ind, row in df.iterrows():
        pairs = []
        for user in json.loads(row['swipe_to']):
            if user in json.loads(row['swiped_from']):
                pairs.append(user)
        all_pairs.append(json.dumps(pairs))

    c.execute("REPLACE into status_table (pairs) VALUES (?)", json.dumps(all_pairs))    


#get chatrooms
def get_groups():
    conn = sqlite3.connect('ponder.db')
    df = pd.read_sql_query('''SELECT username, pairs FROM status_table;''', conn)
    study_groups = make_groups_from_df(df)
    return study_groups


def update_nos(user, new_no):
    conn = sqlite3.connect('ponder.db')
    c = conn.cursor()
    nos = json.loads(c.execute("SELECT nos from status_table WHERE username = user"))
    nos.append(new_no)
    c.execute("REPLACE into status_table (nos) VALUES (json.dumps(nos)) WHERE username = user")    

def update_yes(user, new_yes):
    conn = sqlite3.connect('ponder.db')
    c = conn.cursor()
    yes = json.loads(c.execute("SELECT swipe_to from status_table WHERE username = user"))
    yes.append(new_yes)
    c.execute("REPLACE into status_table (swipe_to) VALUES (json.dumps(yes)) WHERE username = user")    


def get_suggestions(username):

    con = sqlite3.connect('ponder.db')
    c = con.cursor()
    df = pd.read_sql_query("SELECT * from data_table", con)
    try: 
        nos = json.loads(c.execute("SELECT nos from status_table WHERE username = (?)",str(username)).fetchone())
    except:
        nos = []
    try:
        swipe_to = json.loads(c.execute("SELECT swipe_to from status_table WHERE username = (?)",str(username)).fetchone())
    except:
        swipe_to = []

    suggestions = get_suggestions_from_df(df, username)
    sql_query = f'''SELECT * from status_table WHERE username='{username}';'''
    status_info = pd.read_sql_query(sql_query, con)
    # filter out people already rejected or accepted
    for name in suggestions:
        if name in nos or name in swipe_to:
            suggestions.delete(name)
    suggs = json.dumps(suggestions)
    # print("suggestions are!\")
    print(suggs)

    print("UPDATE CWD IS " + str(os.getcwd()))
    c.execute('''REPLACE into status_table VALUES (?,?,?,?,?,?)''', (username, suggs, status_info['swipe_to'][0],status_info['swiped_from'][0],status_info['nos'][0], status_info['pairs'][0]))

    sql_query = '''UPDATE status_table SET suggestions='{suggs}' WHERE username='{username}';'''
    c.execute(sql_query)
    con.commit()
    con.close()


#return PonderUser
def get_next_suggestion(username):
    get_suggestions(username)
    con = sqlite3.connect('ponder.db')
    c = con.cursor()
    df = pd.read_sql_query("SELECT * from status_table", con)
    print(df)
    print(c.execute("SELECT suggestions from status_table WHERE username = (?)",str(username)).fetchone())
    suggs = json.loads(c.execute("SELECT suggestions from status_table WHERE username = (?)",str(username)).fetchone()[0])[0]
    print('AAAAAAAAAAAAAA', suggs)
    user = c.execute('''SELECT * FROM auth_table WHERE username=?;''',(str(suggs))).fetchone()
    PonderUser(user[0], user[2], user[3])
     
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
    print("FIRST CWD IS " + str(os.getcwd()))
    c.execute('''REPLACE into status_table VALUES (?,?,?,?,?,?);''',
            (username, '[1]','[2]','[3]','[4]','[5]'))
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
    suggestions = {}
    row1 = df[df['username'] == username]

    if (row1['noise'].values[0] == 0):
        second_df = df[df['noise'] == 0]
    else:
        second_df = df[df['noise'] != 0]
    
    for ind2, row2 in second_df[second_df['collab'] == row1['collab'].values[0]].iterrows():
        if row1['classes'].values[0] == row2['classes']:
            print()
            soft_dot1 = row1[['learn_style', 'env', 'noise']].values
            soft_dot2 = row2[['learn_style', 'env', 'noise']].values
            preferences = np.dot(soft_dot1, soft_dot2)
            suggestions[ind2] = preferences
    # print(suggestions.items())
    # todo key=lambda item: item[1],reverse=True
    return [i[0] for i in sorted(suggestions.items())]


def make_groups_from_df(pairs_df):
    sgroups3 = []
    sgroups4 = []
    seen = set()
    output_df = pd.DataFrame({'names': pairs_df['name']})
    for ind, row in pairs_df.iterrows():
        for student in row['matched']: #all possible pairs... find if 3rd persn
            possible_thirds = set(pairs_df[pairs_df['name'] == student]['matched'].values[0]).intersection(row['matched'])
            for name in possible_thirds:
                sgroup = frozenset([row['name'], student, name])
                if sgroup not in seen and not seen.add(sgroup):
                    possible_fourths = set.intersection(set((pairs_df[pairs_df['name'] == name]['matched'].values[0])), set(pairs_df[pairs_df['name'] == student]['matched'].values[0]), set(row['matched']))
                    if bool(possible_fourths):
                        for name2 in possible_fourths:
                            sgroup4 = frozenset([row['name'], student, name, name2])
                            if sgroup4 not in seen and not seen.add(sgroup4):
                                sgroups4.append(sgroup4)
                    else:
                        sgroups3.append(sgroup)
    sgroups3.extend(sgroups4)
    return [list(x) for x in sgroups3]
