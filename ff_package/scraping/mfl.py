# Import dependencies
# Standard python libraries
from bs4 import BeautifulSoup
import requests
import pandas as pd



def get_league(user_league):
    urlString = f"https://www54.myfantasyleague.com/2022/export?TYPE=league&L={user_league}"
    response = requests.get(urlString)
    soup = BeautifulSoup(response.content,'xml')
    data = []
    elems = soup.find_all('franchise')
    for i in range(len(elems)):
        rows = [elems[i].get("id"), elems[i].get("name")]
        data.append(rows)
    df = pd.DataFrame(data)
    df.columns=['franchiseID','franchiseName']
    return df

def get_liveScoring(user_league):
    urlString = f"https://www54.myfantasyleague.com/2022/export?TYPE=liveScoring&DETAILS=1&L={user_league}"
    response = requests.get(urlString)
    soup = BeautifulSoup(response.content,'xml')
    data = []
    matchups = soup.find_all('matchup')
    for k in range(len(matchups)):
        franchises = matchups[k].find_all('franchise')
        for i in range(0,len(franchises)):
            current_franchise = franchises[i].find_all('player')
            for j in range(0,len(current_franchise)):
                rows = [k, franchises[i].get("id"), current_franchise[j].get("id"), current_franchise[j].get("score"), current_franchise[j].get("gameSecondsRemaining"), current_franchise[j].get("status")]
                data.append(rows)
    df = pd.DataFrame(data)
    df.columns = ["matchup", "franchiseID", "id_mfl", "liveScore", "secondsRemaining", "status"]
    return df

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