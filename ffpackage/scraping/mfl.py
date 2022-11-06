# Import dependencies
from bs4 import BeautifulSoup
import requests
import pandas as pd


# Retrieve player information from My Fantasy League website
def get_players():
    # Connect to MFL API, which responds with data in xml format
    urlString = "https://api.myfantasyleague.com/2022/export?TYPE=players"
    response = requests.get(urlString)
    # Parse xml response with BeautifulSoup
    soup = BeautifulSoup(response.content,'xml')
    # Create empty list to hold data during loop
    data = []
    # Tell BeautifulSoup to find each element in the xml structure
    players = soup.find_all('player')
    # Loop through the rows to get the data within, then append to the empty data list
    for i in range(len(players)):
        rows = [players[i].get("id"), players[i].get("name"), players[i].get("position"), players[i].get("team")]
        data.append(rows)
    # Convert data list to pandas DataFrame
    df = pd.DataFrame(data)
    df.columns=['id_mfl','playerName', 'pos', 'team']
    return df

# Retrieve franchise info from My Fantasy League website
def get_franchises(user_league):
    # Connect to MFL API, which responds with data in xml format
    urlString = f"https://www54.myfantasyleague.com/2022/export?TYPE=league&L={user_league}"
    response = requests.get(urlString)
    # Parse xml response with BeautifulSoup
    soup = BeautifulSoup(response.content,'xml')
    # Create empty list to hold data during loop
    data = []
    # Tell BeautifulSoup to find each element in the xml structure
    elems = soup.find_all('franchise')
    # Loop through the rows to get the data within, then append to the empty data list
    for i in range(len(elems)):
        rows = [elems[i].get("id"), elems[i].get("name"), elems[i].get("abbrev")]
        data.append(rows)
    # Convert data list to pandas DataFrame
    df = pd.DataFrame(data)
    df.columns=['franchiseID','franchiseName', 'franchiseAbbrev']
    return df

# Retrieve roster info from My Fantasy League website
def get_rosters(user_league, user_franchise=""):
    # Connect to MFL API, which responds with data in xml format
    urlString = f"https://www54.myfantasyleague.com/2022/export?TYPE=rosters&L={user_league}&FRANCHISE={user_franchise}"
    response = requests.get(urlString)
    # Parse xml response with BeautifulSoup
    soup = BeautifulSoup(response.content,'xml')
    # Create empty list to hold data during loop
    data = []
    # Tell BeautifulSoup to find each element in the xml structure
    franchises = soup.find_all('franchise')
    # Loop through the rows of franchises to get the players within
    for i in range(0,len(franchises)):
        current_franchise = franchises[i].find_all('player')
        # Loop through the players in each franchise to get the player data, then append to empty data list
        for j in range(0,len(current_franchise)):
            rows = [franchises[i].get("id"), franchises[i].get("week"), current_franchise[j].get("id"), current_franchise[j].get("status")]
            data.append(rows)
    # Convert to pandas dataframe
    df = pd.DataFrame(data)
    df.columns=['franchiseID','week', 'id_mfl', 'rosterStatus']
    return df

# Retrieve list of Free Agents from My Fantasy League website
def get_freeAgents(user_league):
    # Connect to MFL API, which responds with data in xml format
    urlString = f"https://www54.myfantasyleague.com/2022/export?TYPE=freeAgents&L={user_league}"
    response = requests.get(urlString)
    # Parse xml response with BeautifulSoup
    soup = BeautifulSoup(response.content,'xml')
    # Create empty list to hold data during loop
    data = []
    # Tell BeautifulSoup to find each element in the xml structure
    freeAgents = soup.find_all('player')
    # Loop through the rows to get the data within, then append to the empty data list
    for i in range(len(freeAgents)):
        rows = ["FA", "", freeAgents[i].get("id"), "Free Agent"]
        data.append(rows)
    # Convert to pandas dataframe
    df = pd.DataFrame(data)
    df.columns = ['franchiseID', 'week', 'id_mfl', 'rosterStatus']
    return df

# Retrieve live score info from My Fantasy League website
def get_liveScoring(user_league):
    # Connect to MFL API, which responds with data in xml format
    urlString = f"https://www54.myfantasyleague.com/2022/export?TYPE=liveScoring&DETAILS=1&L={user_league}"
    response = requests.get(urlString)
    # Parse xml response with BeautifulSoup
    soup = BeautifulSoup(response.content,'xml')
    # Create empty list to hold data during loop
    data = []
    # Tell BeautifulSoup to find each element in the xml structure
    matchups = soup.find_all('matchup')
    # Loop through the rows to get the data within, then append to the empty data list
    for k in range(len(matchups)):
        franchises = matchups[k].find_all('franchise')
        for i in range(0,len(franchises)):
            current_franchise = franchises[i].find_all('player')
            for j in range(0,len(current_franchise)):
                rows = [k, franchises[i].get("id"), current_franchise[j].get("id"), current_franchise[j].get("score"), current_franchise[j].get("gameSecondsRemaining"), current_franchise[j].get("status")]
                data.append(rows)
    # Convert to pandas dataframe
    df = pd.DataFrame(data)
    df.columns = ["matchup", "franchiseID", "id_mfl", "liveScore", "secondsRemaining", "status"]
    return df

# Retrieve point predictions based on FantasySharks predictions
def get_sharkRanks():
    # Connect to MFL API, which responds with data in xml format
    urlString = "https://api.myfantasyleague.com/2022/export?TYPE=playerRanks"
    response = requests.get(urlString)
    # Parse xml response with BeautifulSoup
    soup = BeautifulSoup(response.content,'xml')
    # Create empty list to hold data during loop
    data = []
    # Tell BeautifulSoup to find each element in the xml structure
    players = soup.find_all('player')
    # Loop through the rows to get the data within, then append to the empty data list
    for i in range(len(players)):
        rows = [players[i].get("id"), players[i].get("rank")]
        data.append(rows)
    # Convert to pandas dataframe
    df = pd.DataFrame(data)
    # Change column names
    df.columns=['id_mfl','sharkRank']
    # Set datatype
    df['sharkRank'] = df['sharkRank'].astype('int32')
    return df

# Retrieve average draft pick info
def get_adp():
    # Connect to MFL API, which responds with data in xml format
    urlString = "https://api.myfantasyleague.com/2022/export?TYPE=adp"
    response = requests.get(urlString)
    # Parse xml response with BeautifulSoup
    soup = BeautifulSoup(response.content,'xml')
    # Create empty list to hold data during loop
    data = []
    # Tell BeautifulSoup to find each element in the xml structure
    players = soup.find_all('player')
    # Loop through the rows to get the data within, then append to the empty data list
    for i in range(len(players)):
        rows = [players[i].get("id"), players[i].get("averagePick")]
        data.append(rows)
    # Convert to pandas dataframe
    df = pd.DataFrame(data)
    # Change column names
    df.columns=['id_mfl','adp']
    # Set datatype
    df['adp'] = df['adp'].astype('float32')
    return df

# Get playerProfiles from My Fantasy League and find their dates of birth
def get_playerProfiles(idList):
    # Connect to MFL API, which responds with data in xml format
    urlString = f"https://api.myfantasyleague.com/2022/export?TYPE=playerProfile&P={idList}"
    response = requests.get(urlString)
    # Parse xml response with BeautifulSoup
    soup = BeautifulSoup(response.content,'xml')
    # Create empty list to hold data during loop
    data = []
    # Tell BeautifulSoup to find each element in the xml structure
    profiles = soup.find_all('playerProfile')
    players = soup.find_all('player')
    # Loop through the rows to get the data within, then append to the empty data list
    for i in range(len(profiles)):
        rows = [profiles[i].get("id"), players[i].get("dob")]
        data.append(rows)
    # Convert to pandas dataframe
    df = pd.DataFrame(data)
    # Change column names
    df.columns = ['id_mfl', 'dob']
    return df

## Not yet utilized
# Retrieve projected score info from My Fantasy League website
def get_projectedScores(user_league, week):
    urlString = f"https://www54.myfantasyleague.com/2022/export?TYPE=projectedScores&W={week}&L={user_league}"
    response = requests.get(urlString)
    soup = BeautifulSoup(response.content,'xml')
    data = []
    elems = soup.find_all('playerScore')
    for i in range(len(elems)):
        rows = [elems[i].get("id"), elems[i].get("score")]
        data.append(rows)
    df = pd.DataFrame(data)
    df.columns=['id_mfl','sharkProjection']
    return df