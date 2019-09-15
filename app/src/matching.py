import pandas as pd
import numpy as np

def find_matches(df):
    matches = {}
    for ind, row1 in df.iterrows(): #iterate through users
        temp_matches = {}
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
                temp_matches[ind2] = preferences
        matches[ind] = [i[0] for i in sorted(b.items(),key=lambda item: item[1],reverse=True)]

def make_groups(matches_df):
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

def test():
    df = pd.DataFrame(data=[['a',['b','c','d']], ['b',['a','c','d','e']], ['c',['b','a','d', 'e']], ['d',['b','c','a']], ['e',['b']]], columns=['name','matched'])
    output_df = make_groups(df)
    print(output_df)
