# Import dependencies
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

# Scrape OurLads site to see how highly ranked players are on the rosters of their NFL teams
def scrape_depthcharts():
    # Set Selenium/Chrome settings
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN") # Enable this in deployed version
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    capa = DesiredCapabilities.CHROME
    capa["pageLoadStrategy"] = "none"
    driver = webdriver.Chrome(
        # executable_path=os.environ.get("CHROMEDRIVER_PATH"), # Enable this in deployed version
        service=Service("/Applications/chromedriver"), # Enable this when running locally
        chrome_options=chrome_options, 
        desired_capabilities=capa)
    # Tell Selenium to wait until the page has time to fully load
    wait = WebDriverWait(driver, 20)

    # Scrape OurLads website
    url = f"https://www.ourlads.com/nfldepthcharts/depthcharts.aspx"
    # Use Selenium Chromedriver to read OurLads scouting website
    driver.get(url)
    # Tell Selenium the item that we want to watch for to see it fully load, then stop running
    wait.until(EC.presence_of_element_located((By.XPATH, "//table[@id='ctl00_phContent_gvChart']")))
    driver.execute_script("window.stop();")

    # Put the scraped html table into a dataframe
    df = pd.read_html(
        driver.find_element(By.XPATH, value="//table[@id='ctl00_phContent_gvChart']").get_attribute("outerHTML")
        )[0]
    # Filter for only the needed columns
    df = df.loc[:, ['Team', 'Pos', 'Player 1', 'Player 2', 'Player 3', 'Player 4', 'Player 5']]
    # Rename columns of Position Ranks; limit number of ranks to three
    df = df.rename(columns={
        'Player 1':'1',
        'Player 2':'2',
        'Player 3':'3',
        'Player 4':'3',
        'Player 5':'3',
    })
    # Filter only relevant positions
    posList = ['LWR', 'RWR', 'SWR', 'TE', 'QB', 'RB', 'PK', 'PR', 'KR', 'RES']
    df = df.loc[df['Pos'].isin(posList)]
    # Transpose columns to rows to get position ranks in row form rather than column
    df = df.melt(id_vars=["Team", "Pos"], 
        var_name="posRank", 
        value_name="playerName")
        # Rename columns to match MyFantasyLeague
    df = df.rename(columns={'Team':'team', 'Pos':'pos'})
    # Clean the Team column to match My Fantasy League abbreviations
    teamDict = {
    'ARZ':'ARI', 'ATL':'ATL', 'BAL':'BAL', 'BUF':'BUF', 'CAR':'CAR', 'CHI':'CHI', 'CIN':'CIN', 'CLE':'CLE', 
    'DAL':'DAL', 'DEN':'DEN', 'DET':'DET', 'GB':'GBP', 'HOU':'HOU', 'IND':'IND', 'JAX':'JAC', 'KC':'KCC', 
    'LAC':'LAC', 'LAR':'LAR', 'LV':'LVR', 'MIA':'MIA', 'MIN':'MIN', 'NE':'NEP', 'NO':'NOS', 'NYG':'NYG', 
    'NYJ':'NYJ', 'PHI':'PHI', 'PIT':'PIT', 'SEA':'SEA', 'SF':'SFO', 'TB':'TBB', 'TEN':'TEN', 'WAS':'WAS'
    }
    df['team'] = df['team'].map(teamDict)
    # Clean the Name column
    df = df.loc[df['playerName'].notna()]
    # Change "last, first" format to "first last" format
    lNames = df['playerName'].str.split(", ", expand=True)[0]
    fNames = df['playerName'].str.split(" ", expand=True)[1]
    df['playerName'] = fNames + " " + lNames
    # Convert to all upper Case
    df.loc[:, 'playerName'] = df.loc[:, 'playerName'].str.upper()
    # Drop punctuation
    df.loc[:, 'playerName'] = df.loc[:, 'playerName'].str.replace(".", "")
    df.loc[:, 'playerName'] = df.loc[:, 'playerName'].str.replace(",", "")
    df.loc[:, 'playerName'] = df.loc[:, 'playerName'].str.replace("'", "")
    # Create a playerID column
    df['id_ol'] = df['team'] + df['playerName']
    # Clean the Position column
    # Generalize wide receiver specific positions to WR
    df['pos'].replace(["LWR", "RWR", "SWR"], "WR", inplace=True)
    # Identify punt returners, kick returners, and injuredReserve, then drop those rows from the df
    prs = df.loc[df['pos']=='PR']
    krs = df.loc[df['pos']=='KR']
    res = df.loc[df['pos']=='RES']
    df.loc[df['id_ol'].isin(prs['id_ol']), 'PR'] = "YES"
    df.loc[df['id_ol'].isin(krs['id_ol']), 'KR'] = "YES"
    df.loc[df['id_ol'].isin(res['id_ol']), 'RES'] = "YES"
    df = df.loc[(df['pos']!="PR") & (df['pos']!="KR")]
    # Clean the posRank column
    df['posRank'] = df['pos'] + df['posRank']
    # Drop the id column
    df = df.drop(columns=['id_ol', 'pos'])

    return df



