import pandas as pd


def test():
    df = pd.DataFrame(data=[['a',['b','c','d']], ['b',['a','c','d','e']], ['c',['b','a','d', 'e']], ['d',['b','c','a']], ['e',['b']]], columns=['name','matched'])
    output_df = make_groups(df)
    print(output_df)
