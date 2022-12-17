import pandas as pd
import numpy as np
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
        df.loc[(df['rosterStatus']=='ROSTER') & (df['pos']==position) & (df['rosterRank']<=rank), 'startSelector'] = 'Starter'
    # Assign "Bench" to players who are bottom-ranked within their position
    for (position, rank) in posMax.items():
        df.loc[(df['rosterStatus']=='ROSTER') & (df['pos']==position) & (df['rosterRank']>rank), 'startSelector'] = 'Bench'
    # Re-rank players who are eligible for flex positions
    df.loc[(df['rosterStatus']=='ROSTER') & (df['startSelector'].isna()), 'rosterRank'] = df.loc[(df['rosterStatus']=='ROSTER') & (df['startSelector'].isna())].groupby("franchiseID")[how].rank(ascending=False)
    # Assign "Starter" to top-ranked flex players
    df.loc[(df['rosterStatus']=='ROSTER') & (df['startSelector'].isna()) & (df['rosterRank']<=flexspots), 'startSelector'] = 'Starter'
    # Assign "Bench" to all other players
    df.loc[df['startSelector'].isna(), 'startSelector'] = 'Bench'

    return df

# Calculate each player's liveScoring Projections based on amount of time remaining
def expectedLiveScore(row):
    # Use a different calculation method for defenses since defenses do not accrue points; they lose points
    if row["pos"] == "DF":
        # The defensive players' score moves from the weeklyPrediction to the liveScore as the game goes on
        result = (row['scoreTotal'] * row['secondsRemaining'] + row['liveScore'] * (3600 - row['secondsRemaining'])) / 3600
    # For players other than defenses:
    else:
        # Multiply the weekly prediction by the proportion of the game yet to be played. Games are 60 minutes = 3600 seconds
        # Add these expected points remaining to the points the player has already scored
        result = row['liveScore'] + (row['scoreTotal'] * row['secondsRemaining'] / 3600)
    return result

# Set colors for chart 
def colorPicker(row):
    # Calculate difference between projection/actual to visualize how well a player is doing vs their expected value
    diff = row['expectedLiveScore'] - row['scoreTotal']
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

# Calculate FANTASY points customized based on league-specific scoring rules
def calculate_scoresFF(df, scoringDict):
    # Multiply the nflStats by the mulitplier row to get base scores
    multiplier = {key:value["multiplier"] for (key, value) in scoringDict.items()}
    scoresBase = df.copy()
    scoresBase.loc[:, scoringDict.keys()] = scoresBase.loc[:, scoringDict.keys()].mul(multiplier)
    # Bin and cut the nflStats into a bonus score df
    scoresBonus = df.copy()
    for colName in scoringDict.keys():
        scoresBonus[colName] = pd.cut(
            scoresBonus[colName], 
            bins=scoringDict[colName]["bins"], 
            include_lowest=True, 
            labels=scoringDict[colName]["labels"]
        )
    # Remove defensive scoring bonuses from offensive players
    defensiveCategories = ['defBlk', 'defT', 'defPtsAgainst', 'defPassYAgainst', 'defRushYAgainst', 'defYdsAgainst']
    scoresBonus.loc[scoresBonus['pos']!='DF', defensiveCategories] = 0
    scoresBonus.loc[:, scoringDict.keys()] = scoresBonus.loc[:, scoringDict.keys()].astype('float64')
    # Add base scores and bonus scores 
    scoresTotal = scoresBase.loc[:, scoringDict.keys()].add(scoresBonus.loc[:, scoringDict.keys()])
    # Create summary table 
    analyzed = df.drop(columns=scoringDict.keys())
    # Add together scores from each scoring category (sum across the row)
    analyzed['scoreTotal'] = scoresTotal.sum(axis=1)
    return analyzed