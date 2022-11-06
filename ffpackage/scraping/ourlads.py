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

# Set Selenium/Chrome settings
chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
capa = DesiredCapabilities.CHROME
capa["pageLoadStrategy"] = "none"
driver = webdriver.Chrome(
    executable_path=os.environ.get("CHROMEDRIVER_PATH"), 
    chrome_options=chrome_options, 
    desired_capabilities=capa)

# Scrape OurLads site to see how highly ranked players are on the rosters of their NFL teams
def scrape_depthcharts():
    # Define OurLads URL
    url = f"https://www.ourlads.com/nfldepthcharts/depthcharts.aspx"
    # Tell Selenium to wait until the page has time to fully load
    wait = WebDriverWait(driver, 20)
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
    df.melt(id_vars=["Team", "Pos"], 
        var_name="posRank", 
        value_name="playerName")
    # Clean the scraped data
    return df


# Transform columns into rows
scrape21 = scrape2[['Team', 'Pos', 'Player 1']]
scrape21 = scrape21.rename(columns={'Player 1':'Player'})
scrape21['posRank'] = "1"

scrape22 = scrape2[['Team', 'Pos', 'Player 2']]
scrape22 = scrape22.rename(columns={'Player 2':'Player'})
scrape22['posRank'] = "2"

scrape23 = scrape2[['Team', 'Pos', 'Player 3']]
scrape23 = scrape23.rename(columns={'Player 3':'Player'})
scrape23['posRank'] = "3"

scrape24 = scrape2[['Team', 'Pos', 'Player 4']]
scrape24 = scrape24.rename(columns={'Player 4':'Player'})
scrape24['posRank'] = "4"

scrape25 = scrape2[['Team', 'Pos', 'Player 5']]
scrape25 = scrape25.rename(columns={'Player 5':'Player'})
scrape25['posRank'] = "5"

scrape2_complete = pd.concat([scrape21, scrape22, scrape23, scrape24, scrape25], axis=0, ignore_index=True)

# Clean Position column
# Select only relevant positions
posList = ['LWR', 'RWR', 'SWR', 'TE', 'QB', 'RB', 'PK', 'PR', 'KR', 'RES']
scrape2_final = scrape2_complete.loc[scrape2_complete['Pos'].isin(posList)]
# Convert WR roles to "WR"
scrape2_final['Pos'].replace(["LWR", "RWR", "SWR"], "WR", inplace=True)
scrape2_final['posRank'] = scrape2_final['Pos'] + scrape2_final['posRank']
scrape2_final = scrape2_final.reset_index(drop=True)
scrape2_final.dropna(inplace=True)
scrape2_final.drop_duplicates(subset=['Player', 'Team', 'Pos'], inplace=True)

# Create columns for KRs and PRs
krs = scrape2_final.loc[scrape2_final.Pos=='KR']
krs = krs.drop(columns=['Pos'])
krs.columns = ['Team', 'Player', 'KR']
prs = scrape2_final.loc[scrape2_final.Pos=='PR']
prs = prs.drop(columns=['Pos'])
prs.columns = ['Team', 'Player', 'PR']
# Join pr and pk scrape2s back onto main ourlads scrape2
scrape2_final = scrape2_final.merge(krs, how='left', on=['Player', 'Team']).merge(prs, how='left', on=['Player', 'Team'])
scrape2_final['KR'].fillna("NO", inplace=True)
scrape2_final['PR'].fillna("NO", inplace=True)

# Clean name column
names = scrape2_final['Player'].str.split(" ", n=2, expand=True)
names.columns = ['a', 'b', 'c']
names['a'] = names['a'].str.replace(",", "")
scrape2_final['Player'] = names['b'] + " " + names['a']
# Change to Upper Case
scrape2_final['Player'] = scrape2_final['Player'].str.upper()
# Drop punctuation
scrape2_final['Player'] = scrape2_final['Player'].str.replace(".", "")
scrape2_final['Player'] = scrape2_final['Player'].str.replace(",", "")
scrape2_final['Player'] = scrape2_final['Player'].str.replace("'", "")

# Change column names and order
scrape2_final = scrape2_final[['Player', 'Pos', 'Team', 'posRank', 'KR', 'PR']]
scrape2_final.columns = ['player', 'pos_ol', 'team', 'posRank', 'KR', 'PR']

# Remove separate rows for PRs and KRs
scrape2_final = scrape2_final.loc[(scrape2_final.pos_ol!="KR")]
scrape2_final = scrape2_final.loc[(scrape2_final.pos_ol!="PR")]

# Drop position column
scrape2_final.drop(columns=['pos_ol'], inplace=True)
scrape2_final

# Rename team abbreviations
teamDict = {
    'ARZ':'ARI', 'ATL':'ATL', 'BAL':'BAL', 'BUF':'BUF', 'CAR':'CAR', 'CHI':'CHI', 'CIN':'CIN', 'CLE':'CLE', 
    'DAL':'DAL', 'DEN':'DEN', 'DET':'DET', 'GB':'GBP', 'HOU':'HOU', 'IND':'IND', 'JAX':'JAC', 'KC':'KCC', 
    'LAC':'LAC', 'LAR':'LAR', 'LV':'LVR', 'MIA':'MIA', 'MIN':'MIN', 'NE':'NEP', 'NO':'NOS', 'NYG':'NYG', 
    'NYJ':'NYJ', 'PHI':'PHI', 'PIT':'PIT', 'SEA':'SEA', 'SF':'SFO', 'TB':'TBB', 'TEN':'TEN', 'WAS':'WAS'
    }
scrape2_final['team'] = scrape2_final['team'].map(teamDict)
