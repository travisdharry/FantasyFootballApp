# Import dependencies
import pandas as pd
# Dependencies for random forest model
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from joblib import dump, load

### Predict future points based on position
def makePredictions(df, pos):
    # Create variables based on player position
    dummy1 = f'posRank_{pos}1'
    dummy2 = f'posRank_{pos}2'
    dummy3 = f'posRank_{pos}3'
    modelPath = f'../models/rfmodel_{pos}1.joblib'
    # Specify column names for features and labels
    featureColumns = [
        'week', 'age', 'pos', 'posRank', # basic player info
        'passA_curr', 'passC_curr', 'passY_curr', 'passT_curr', 'passI_curr', 'pass2_curr', # passing
        'rushA_curr', 'rushY_curr', 'rushT_curr', 'rush2_curr', # rushing
        'recC_curr', 'recY_curr', 'recT_curr', 'rec2_curr', 'fum_curr', # receiving
        'XPA_curr', 'XPM_curr', 'FGA_curr', 'FGM_curr', 'FG50_curr', # punt/kicking
        'defSack_curr', 'defI_curr', 'defSaf_curr', 'defFum_curr', 'defBlk_curr', 'defT_curr', # defensive
        'defPtsAgainst_curr', 'defPassYAgainst_curr', 'defRushYAgainst_curr', 'defYdsAgainst_curr', # opponent
        'gamesPlayed_curr', # games played
        'gamesPlayed_prior1', # games played
        'passA_prior1', 'passC_prior1', 'passY_prior1', 'passT_prior1', 'passI_prior1', 'pass2_prior1', 
        'rushA_prior1', 'rushY_prior1', 'rushT_prior1', 'rush2_prior1', 
        'recC_prior1', 'recY_prior1', 'recT_prior1', 'rec2_prior1', 'fum_prior1', 
        'XPA_prior1', 'XPM_prior1', 'FGA_prior1', 'FGM_prior1', 'FG50_prior1', 
        'defSack_prior1', 'defI_prior1', 'defSaf_prior1', 'defFum_prior1', 'defBlk_prior1', 'defT_prior1', 
        'defPtsAgainst_prior1', 'defPassYAgainst_prior1', 'defRushYAgainst_prior1', 'defYdsAgainst_prior1', 
        'gamesPlayed_prior2', 
        'passA_prior2', 'passC_prior2', 'passY_prior2', 'passT_prior2', 'passI_prior2', 'pass2_prior2', 
        'rushA_prior2', 'rushY_prior2', 'rushT_prior2', 'rush2_prior2', 
        'recC_prior2', 'recY_prior2', 'recT_prior2', 'rec2_prior2', 'fum_prior2', 
        'XPA_prior2', 'XPM_prior2', 'FGA_prior2', 'FGM_prior2', 'FG50_prior2', 
        'defSack_prior2', 'defI_prior2', 'defSaf_prior2', 'defFum_prior2', 'defBlk_prior2', 'defT_prior2', 
        'defPtsAgainst_prior2', 'defPassYAgainst_prior2', 'defRushYAgainst_prior2', 'defYdsAgainst_prior2', 
        'defSack_curr_opp', 'defI_curr_opp', 'defSaf_curr_opp', 'defFum_curr_opp', 'defBlk_curr_opp', 'defT_curr_opp', 
        'defPtsAgainst_curr_opp', 'defPassYAgainst_curr_opp', 'defRushYAgainst_curr_opp', 'defYdsAgainst_curr_opp', 
        'defSack_prior1_opp', 'defI_prior1_opp', 'defSaf_prior1_opp', 'defFum_prior1_opp', 'defBlk_prior1_opp', 'defT_prior1_opp', 
        'defPtsAgainst_prior1_opp', 'defPassYAgainst_prior1_opp', 'defRushYAgainst_prior1_opp', 'defYdsAgainst_prior1_opp'
    ]
    labelColumns = [
        'passA', 'passC', 'passY', 'passT', 'passI', 'pass2', 
        'rushA', 'rushY', 'rushT', 'rush2', 
        'recC', 'recY', 'recT', 'rec2', 'fum', 
        'XPA', 'XPM', 'FGA', 'FGM', 'FG50', 
        'defSack', 'defI', 'defSaf', 'defFum', 'defBlk', 'defT', 
        'defPtsAgainst', 'defPassYAgainst', 'defRushYAgainst', 'defYdsAgainst'  
    ]
    headerColumns = [
            'id_mfl',
            'season',
            'week',
            'team',
            'playerName',
            'age',
            'sharkRank', 
            'adp',
            'KR',
            'PR',
            'RES',
            'pos',
            'posRank',
            'opponent'
        ]
    # Select only one player position
    df = df.loc[df['pos']==pos]
    df = df.dropna()
    df = df.reset_index(drop=True)
    # Select features
    header = df[headerColumns]
    X = df[featureColumns]
    # Encode categorical features
    X = pd.get_dummies(X, columns = ['pos', 'posRank'])
    # Check if there were the correct number of posRanks in the dataset
    # (For instance, if there were no TE3s then this would cause a problem for the predictive model)
    for rank in [dummy1, dummy2, dummy3]:
        if rank not in list(X.columns):
            X[rank] = 0
    # The model did not include DF2s or DF3s)
    if "posRank_DF3" in X.columns:
        X = X.drop(columns=['posRank_DF3', 'posRank_DF2'])
    #load saved model
    regressor = load(modelPath)
    # Run model
    y_pred = regressor.predict(X)
    # Format output score projections as dataframe with named columns, then merge back in with player info
    y_pred = pd.DataFrame(y_pred)
    y_pred.columns = labelColumns
    y_pred = header.merge(y_pred, left_index=True, right_index=True)
    # Return result
    return y_pred
