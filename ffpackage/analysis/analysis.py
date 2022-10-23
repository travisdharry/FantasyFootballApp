import pandas as pd

def starterSelector(df, how, startersMax, posMax, posMin):
    # Calculate the number of available flex spots
    flexspots = startersMax - sum(posMin.values())
    # Rank players by position within their franchise (select only ROSTER, ignoring TAXI_SQUAD and INJURED_RESERVE)
    df.loc[df['rosterStatus']=='ROSTER', "rosterRank"] = df.loc[df['rosterStatus']=='ROSTER'].groupby(["franchiseID", "pos"])[how].rank(ascending=False)
    # Assign "Starter" to players who are top-ranked within their position
    for (position, rank) in posMin.items():
        df.loc[(df['rosterStatus']=='ROSTER') & (df['pos']==position) & (df['rosterRank']<=rank), 'starting'] = 'Starter'
    # Assign "Bench" to players who are bottom-ranked within their position
    for (position, rank) in posMax.items():
        df.loc[(df['rosterStatus']=='ROSTER') & (df['pos']==position) & (df['rosterRank']>rank), 'starting'] = 'Bench'
    # Re-rank players who are eligible for flex positions
    df.loc[(df['rosterStatus']=='ROSTER') & (df['starting'].isna()), 'rosterRank'] = df.loc[(df['rosterStatus']=='ROSTER') & (df['starting'].isna())].groupby("franchiseID")[how].rank(ascending=False)
    # Assign "Starter" to top-ranked flex players
    df.loc[(df['rosterStatus']=='ROSTER') & (df['starting'].isna()) & (df['rosterRank']<=flexspots), 'starting'] = 'Starter'
    # Assign "Bench" to all other players
    df.loc[df['starting'].isna(), 'starting'] = 'Bench'

    return df