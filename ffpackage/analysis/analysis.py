import pandas as pd
from datetime import datetime, date
from dateutil.relativedelta import *

# Find the best possible combination of starters for each franchise
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

# Calculate each player's liveScoring Projections based on amount of time remaining
def expectedLiveScore(row):
    # Use a different calculation method for defenses since defenses do not accrue points; they lose points
    if row["pos"] == "DF":
        # The defensive players' score moves from the weeklyPrediction to the liveScore as the game goes on
        result = (row['weeklyPred'] * row['secondsRemaining'] + row['liveScore'] * (3600 - row['secondsRemaining'])) / 3600
    # For players other than defenses:
    else:
        # Multiply the weekly prediction by the proportion of the game yet to be played. Games are 60 minutes = 3600 seconds
        # Add these expected points remaining to the points the player has already scored
        result = row['liveScore'] + (row['weeklyPred'] * row['secondsRemaining'] / 3600)
    return result

# Set colors for chart 
def colorPicker(row):
    # Calculate difference between projection/actual to visualize how well a player is doing vs their expected value
    diff = row['expectedLiveScore'] - row['weeklyPred']
    # Cap outliers at 20 points over/under their prediction
    if diff > 20:
        diff = 20
    if diff < -20:
        diff = -20
    # Normalize difference to a scale of 255 generate the color Red-Green-Blue values
    scalar = int(round(diff * 255 / 20, 0))
    # The higher the player scores over their prediction, the darker green their block will be
    if scalar >= 0:
        red = 255 - scalar
        green = 255
        blue = 255 - scalar
    # The lower the player scores under their prediction, the darker red their block will be
    else:
        red = 255 
        green = 255 + scalar
        blue = 255 + scalar
    color = f'rgb({red},{green},{blue})'
    return color

# Calculate player ages using datetime's relativedelta
def calculate_age(dob):
    today = date.today()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    return age

# # Calculate FANTASY scores from predicted NFL stats
# def
#     # Define scoring multiplier based on league settings
#     multiplier = [
#         0,0,.04,4,-2,2,.1,.1,6,2,.25,.1,6,2,-2,0,1,0,3,5,1,2,2,2,1.5,6,0,0,0,0,1,1
#     ]
#     # Define bins for defensive PointsAgainst and YardsAgainst based on MFL scoring categories
#     binList_defPts = [-5,0,6,13,17,21,27,34,45,59,99]
#     binList_defYds = [0,274,324,375,425,999]
#     # Define correlating scores for defensive PointsAgainst and YardsAgainst based on league settings
#     ptList_defPts = [10,8,7,5,3,2,0,-1,-3,-5]
#     ptList_defYds = [5,2,0,-2,-5]
#     # Bin and cut the defensive predictions
#     y_pred['defPtsBin'] = pd.cut(y_pred['defPtsAgainst'], bins=binList_defPts, include_lowest=True, labels=ptList_defPts)
#     y_pred['defYdsBin'] = pd.cut(y_pred['defYdsAgainst'], bins=binList_defYds, include_lowest=True, labels=ptList_defYds)
#     # Merge predictions with header columns so we know the players' position
#     a_pred = header.merge(y_pred, left_index=True, right_index=True)
#     # Assign value of zero to all non-defensive players' bins
#     a_pred.loc[a_pred['pos']!='DF', 'defPtsBin'] = 0
#     a_pred.loc[a_pred['pos']!='DF', 'defYdsBin'] = 0
#     # Drop the header columns again
#     a_pred = a_pred.drop(columns=['id_mfl', 'week','season','team','playerName','age','sharkRank','adp','pos','KR','PR','RES','posRank','opponent'])
#     # Create function to apply scoring multiplier
#     def multer(row):
#         return row.multiply(multiplier)
#     # Apply scoring multiplier to predictions
#     c = a_pred.apply(multer, axis=1)
#     c = c.apply(np.sum, axis=1)
#     c = pd.DataFrame(c, columns=['pred'])