import sqlite3
import pandas as pd
import numpy as np
import json

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
              '''classes message_text, '''
              '''major message_text, '''
              '''env integer);''')

    c.execute('''CREATE TABLE IF NOT EXISTS matches_table ('''
              '''username message_text, '''
              '''suggestions message_text,'''
              '''swipe_to message_text, ''' #people they swiped on
              '''swiped_from message_text, ''' #people who swiped on them
              '''nos message_text,''' #people who are rejected
              '''matches message_text);''')

    conn.commit()
    conn.close()

#find pairwise groups (for get_groups)
def get_matches(db):
    df = pd.read_sql_query("SELECT username, swipe_to, swiped_from from matches_table", con)
    all_matches = []
    for ind, row in df.iterrows():
        matches = []
        for user in json.load(row['swipe_to']):
            if user in json.load(row['swiped_from']):
                matches.append(user)
        all_matches.append(json.dump(matches))

    c.execute("REPLACE into matches_table (matches) VALUES (json.dump(all_matches))")    

#get chatrooms
def get_groups(db):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    df = pd.read_sql_query('''SELECT username, matches FROM matches_table;''', conn)
    study_groups = make_groups_from_df(df)
    return study_groups
        
# def update_nos(): TODO

def get_suggestions(db, user):
    con = sqlite3.connect(db)
    df = pd.read_sql_query("SELECT * from data_table", con)
    nos = c.execute("SELECT nos from matches_table WHERE username = user", con)
    nos = json.load(nos)
    suggestions = get_suggestions_from_df(df, username)

    # filter out people already rejected
    for name in suggestions:
        if name in nos:
            suggestions.delete(name)

    c.execute("REPLACE into matches_table (suggestions) VALUES (json.dump(suggestions)) WHERE username = user")    

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

def get_suggestions_from_df(df, username):
    matches = {}
    if row1['noise'] == 0:
        second_df = df[df['noise'] == 0]
    else:
        second_df = df[df['noise'] != 0]
    for ind2, row2 in second_df[second_df['collab'] == row1['collab']].iterrows():
        shared_classes = set(row1['classes']).intersection(row2['classes'])
        if bool(shared_classes):
            soft_dot1 = row1[['style', 'env', 'noise']].values
            soft_dot2 = row2[['style', 'env', 'noise']].values
            num_shared_classes = len(shared_classes)
            for course in shared_classes:
                soft_dot1.append(row1['classes'][course])
                soft_dot2.append(row1['classes'][course])
            preferences = num_shared_classes + np.dot(soft_dot1, soft_dot2)
            matches[ind2] = preferences
    return [i[0] for i in sorted(matches.items(),key=lambda item: item[1],reverse=True)]

def make_groups_from_df(matches_df):
    sgroups3 = []
    sgroups4 = []
    seen = set()
    output_df = pd.DataFrame({'names': matches_df['name']})
    for ind, row in matches_df.iterrows():
        for student in row['matched']: #all possible pairs... find if 3rd persn
            possible_thirds = set(matches_df[matches_df['name'] == student]['matched'].values[0]).intersection(row['matched'])
            for name in possible_thirds:
                sgroup = frozenset([row['name'], student, name])
                if sgroup not in seen and not seen.add(sgroup):
                    possible_fourths = set.intersection(set((matches_df[matches_df['name'] == name]['matched'].values[0])), set(matches_df[matches_df['name'] == student]['matched'].values[0]), set(row['matched']))
                    if bool(possible_fourths):
                        for name2 in possible_fourths:
                            sgroup4 = frozenset([row['name'], student, name, name2])
                            if sgroup4 not in seen and not seen.add(sgroup4):
                                sgroups4.append(sgroup4)
                    else:
                        sgroups3.append(sgroup)
    sgroups3.extend(sgroups4)
    return [list(x) for x in sgroups3]
