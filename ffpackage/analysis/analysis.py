import pandas as pd

def starterSelector(df, predMethod, totalStarters, posmax, posmin):
    # Calculate the number of available flex spots
    flexspots = totalStarters - sum(posmin.values())
    # Rank players by position within their franchise (ignoring TAXI_SQUAD and INJURED_RESERVE)
    df.loc[df['rosterStatus']=='ROSTER', "rosterRank"] = df.loc[df['rosterStatus']=='ROSTER'].groupby(["franchiseID", "pos"])[predMethod].rank(ascending=False)
    # Assign "Starter" to players who are top-ranked within their position
    for (position, rank) in posmin.items():
        df.loc[(df['rosterStatus']=='ROSTER') & (df['pos']==position) & (df['rosterRank']<=rank), 'starting'] = 'Starter'
    # Assign "Bench" to players who are bottom-ranked within their position
    for (position, rank) in posmax.items():
        df.loc[(df['rosterStatus']=='ROSTER') & (df['pos']==position) & (df['rosterRank']>rank), 'starting'] = 'Bench'
    # Re-rank players who are eligible for flex positions
    df.loc[(df['rosterStatus']=='ROSTER') & (df['starting'].isna()), 'rosterRank'] = df.loc[(df['rosterStatus']=='ROSTER') & (df['starting'].isna())].groupby("franchiseID")[predMethod].rank(ascending=False)
    # Assign "Starter" to top-ranked flex players
    df.loc[(df['rosterStatus']=='ROSTER') & (df['starting'].isna()) & (df['rosterRank']<=flexspots), 'starting'] = 'Starter'
    # Assign "Bench" to all other players
    df.loc[df['starting'].isna(), 'starting'] = 'Bench'

    return df