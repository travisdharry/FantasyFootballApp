# Import dependencies
# Standard python libraries
import os
import json

# Third-party libraries
from flask import Flask, redirect, request, url_for, render_template, session
from flask_login import (
    UserMixin,
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from oauthlib.oauth2 import WebApplicationClient
import requests
import pandas as pd
import numpy as np
import plotly

# Internal imports
from ffpackage import mfl, analysis, viz
from appmanager import db, user

# Configuration (These variables are stored as environment variables)
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_DISCOVERY_URL = ("https://accounts.google.com/.well-known/openid-configuration")

# Create a new Flask instance
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

# Log in users
# User session management setup using Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
# OAuth 2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)
# function to get provider configuration, which will tell us the authorization endpoint
def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()
# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


# Create Flask route for login
@app.route('/')
def index():
    if current_user.is_authenticated:
        return render_template("landing.html", user_id=current_user.id)
    else:
        return render_template("index.html")

# If user is not already logged in they are redirected here
@app.route("/login")
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

# When Google has logged the user in the information is sent here:
@app.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")
    # Find out what URL to hit to get tokens that allow you to ask for things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]
    # Prepare and send a request to get tokens
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )
    # Parse the tokens
    client.parse_request_body_response(json.dumps(token_response.json()))
    # Find and hit the URL from Google that gives the user's profile information,
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
    # Make sure their email is verified.
    # The user authenticated with Google, authorized your app, and now you've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400
    
    # Create a user with the information provided by Google
    user = User(
        id_=users_email
    )

    if not User.get(users_email):
        # Send user to failure page
        return '<p>"Login failure"</p>'
    else: 
        # Begin user session by logging the user in
        login_user(user)
        # Send user back to index page
        return redirect(url_for("index"))



### Landing pages

@app.route('/landing')
#@login_required
def landing():
    # Check if the user has entered a league and franchise
    user_franchise = session.get('user_franchise', None)
    user_league = session.get('user_league', None)
    return render_template("landing.html", user_league=user_league, user_franchise=user_franchise)

@app.route("/landing/leagueCallback", methods=['GET', 'POST'])
#@login_required
def leagueCallback():
    # The user will input their leagueID into the site
    user_league = request.form["user_league"]
    # Save the user's leagueID in the session data
    session['user_league'] = user_league
    # Send the user to the getFrnachise page to enter their franchise
    return redirect(url_for("getFranchise"))

@app.route('/getFranchise', methods=['GET', 'POST'])
#@login_required
def getFranchise():
    # Retrieve the user's league they entered on the getLeague page
    user_league = session.get("user_league")
    # Find the franchises that are in the user's reported league; these will go into a dropdown menu for the user
    franchise_list = mfl.get_franchises(user_league)['franchiseName'].to_list()
    # Render the page
    return render_template("getFranchise.html", franchise_list=franchise_list)

@app.route("/getFranchise/franchiseCallback", methods=['GET', 'POST'])
#@login_required
def franchiseCallback():
    # Retrieve the user's franchise they entered on the getFranchise page
    user_franchise = request.form["FranchiseName"]
    # Save the user's franchiseName in the session data
    session['user_franchise'] = user_franchise
    # return the user to the landing page
    return redirect(url_for("landing"))




### Views


@app.route("/allPlayers")
#@login_required
def allPlayers():
    # get all player info that is stored in the app's database
    player_df = db.read_db("predictions")
    # convert to html tables
    tables = [player_df.to_html(classes='data')]
    titles=player_df.columns.values
    # Render html
    return render_template("allPlayers.html", tables=tables, titles=titles)

@app.route('/waiverWire', methods=['GET', 'POST'])
#@login_required
def waiverWire():
    user_league = session.get('user_league', None)
    user_franchise = session.get('user_franchise', None)

    # Get Franchises in the league
    franchise_df = mfl.get_franchises(user_league)
    # Append a row to carry free agents
    freeAgentRow =  {"franchiseID":["FA"], "franchiseName":["Free Agent"], "franchiseAbbrev":["FA"]}
    freeAgentRow = pd.DataFrame.from_dict(freeAgentRow)
    franchise_df = pd.concat([franchise_df, freeAgentRow], axis=0, ignore_index=True)

    # Get franchise rosters
    rosters_df = mfl.get_rosters(user_league)

    # Get Free Agents
    freeAgent_df = mfl.get_freeAgents(user_league)

    # Combine Franchise rosters with free agents to get all players
    rosters_df = pd.concat([rosters_df, freeAgent_df], axis=0)

    # Get all players, sharkRank, and ADP
    player_df = db.read_db("predictions")

    # Merge all dfs
    complete = player_df.merge(rosters_df, on=['id_mfl', 'week'], how='left').merge(franchise_df, on='franchiseID', how='left')
    complete = complete.loc[complete['franchiseID'].notna()]

    ## Calculate fantasy scores customized based on league-specific scoring rules
    scoringDict = {
        'passA': {"multiplier":0, "bins":[-np.inf, np.inf], "labels":[0]},
        'passC': {"multiplier":0, "bins":[-np.inf, np.inf], "labels":[0]},
        'passY': {"multiplier":0.04, "bins":[-np.inf, np.inf], "labels":[0]},
        'passT': {"multiplier":4, "bins":[-np.inf, np.inf], "labels":[0]},
        'passI': {"multiplier":-2, "bins":[-np.inf, np.inf], "labels":[0]},
        'pass2': {"multiplier":2, "bins":[-np.inf, np.inf], "labels":[0]},
        'rushA': {"multiplier":0.1, "bins":[-np.inf, np.inf], "labels":[0]},
        'rushY': {"multiplier":0.1, "bins":[-np.inf, np.inf], "labels":[0]},
        'rushT': {"multiplier":6, "bins":[-np.inf, np.inf], "labels":[0]},
        'rush2': {"multiplier":2, "bins":[-np.inf, np.inf], "labels":[0]},
        'recC': {"multiplier":0.25, "bins":[-np.inf, np.inf], "labels":[0]},
        'recY': {"multiplier":0.1, "bins":[-np.inf, np.inf], "labels":[0]},
        'recT': {"multiplier":6, "bins":[-np.inf, np.inf], "labels":[0]},
        'rec2': {"multiplier":2, "bins":[-np.inf, np.inf], "labels":[0]},
        'fum': {"multiplier":-2, "bins":[-np.inf, np.inf], "labels":[0]},
        'XPA': {"multiplier":0, "bins":[-np.inf, np.inf], "labels":[0]},
        'XPM': {"multiplier":3, "bins":[-np.inf, np.inf], "labels":[0]},
        'FGA': {"multiplier":0, "bins":[-np.inf, np.inf], "labels":[0]},
        'FGM': {"multiplier":3, "bins":[-np.inf, np.inf], "labels":[0]},
        'FG50': {"multiplier":5, "bins":[-np.inf, np.inf], "labels":[0]},
        'defSack': {"multiplier":1, "bins":[-np.inf, np.inf], "labels":[0]},
        'defI': {"multiplier":2, "bins":[-np.inf, np.inf], "labels":[0]},
        'defSaf': {"multiplier":2, "bins":[-np.inf, np.inf], "labels":[0]},
        'defFum': {"multiplier":2, "bins":[-np.inf, np.inf], "labels":[0]},
        'defBlk': {"multiplier":1.5, "bins":[-np.inf, np.inf], "labels":[0]},
        'defT': {"multiplier":6, "bins":[-np.inf, np.inf], "labels":[0]},
        'defPtsAgainst': {"multiplier":0, "bins":[-5,0,6,13,17,21,27,34,45,59,99], "labels":[10,8,7,5,3,2,0,-1,-3,-5]},
        'defPassYAgainst': {"multiplier":0, "bins":[-np.inf, np.inf], "labels":[0]},
        'defRushYAgainst': {"multiplier":0, "bins":[-np.inf, np.inf], "labels":[0]},
        'defYdsAgainst': {"multiplier":0, "bins":[0,274,324,375,425,999], "labels":[5,2,0,-2,-5]}
    }
    # Run Calculation function
    analyzed = analysis.calculate_scoresFF(complete, scoringDict)

    # Render html
    return render_template("waiverWire.html", tables=[analyzed.to_html(classes='data')], titles=analyzed.columns.values)


#@app.route('/compareFranchises')
#@login_required
def compareFranchises():
    # Retrieve the user's leagueID from the session data
    user_league = session.get('user_league', None)

    # Get Franchises in the league
    franchise_df = mfl.get_franchises(user_league)
    # Append a franchise for free agents
    franchise_df = franchise_df.append({"franchiseID":"FA", "franchiseName":"Free Agent", "franchiseAbbrev":"FA"}, ignore_index=True)

    # Get franchise rosters
    rosters_df = mfl.get_rosters(user_league)

    # Get Free Agents
    freeAgent_df = mfl.get_freeAgents(user_league)

    # Get all players, sharkRank, and ADP
    predictions = db.read_db("predictions")

    # Merge all dfs
    complete = predictions.merge(rosters_df, on='id_mfl', how='left').merge(franchise_df[['franchiseID', 'franchiseName', 'franchiseAbbrev']], on='franchiseID', how='left')
    complete['franchiseID'].fillna("FA", inplace=True)
    complete['franchiseName'].fillna("Free Agent", inplace=True)
    complete['rosterStatus'].fillna("Free Agent", inplace=True)

    # Get info on available slots from MFL site
    posMax = {"QB":2, "RB":5, "WR":6, "TE":5, "PK":2, "DF":2}
    posMin = {"QB":1, "RB":2, "WR":2, "TE":2, "PK":2, "DF":2}
    totalStarters = 15
    predMethod = "pred"

    # Select starters
    df = analysis.starterSelector(complete, how=predMethod, startersMax=totalStarters, posMax=posMax, posMin=posMin)

    # Find the lowest scoring player on the field and set them as the low bar
    for x in ["QB", "RB", "WR", "TE", "PK", "DF"]:
        positionMinPred = df.loc[(df['pos']==x) & (df['starting']=='Starter'), predMethod].min()
        # Calculate relative values
        df.loc[df['pos']==x, 'relativeValue'] = df.loc[df['pos']==x, predMethod] - positionMinPred

    # Visualize the data
    fig = viz.compareFranchises(df, how=predMethod)
    # Encode in JSON format
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    # Render html template in flask
    return render_template('compareFranchises.html', graphJSON=graphJSON)

@app.route('/liveScoring')
#@login_required
def liveScoring():
    # Retrieve the user's leagueID from the session data
    user_league = session.get("user_league")

    # Get MFL scoring data
    liveScores = mfl.get_liveScoring(user_league)
    # Get Franchises in the league
    franchises = mfl.get_franchises(user_league)
    # Get all players and predictions
    predictions = db.get_df("predictions")

    # Merge: merge liveScores, franchises, and predictions
    df = liveScores.merge(franchises, how='left', on='franchiseID').merge(predictions, how='left', on='id_mfl')

    # Clean: convert to float data types
    df['liveScore'] = df['liveScore'].astype('float64')
    df['secondsRemaining'] = df['secondsRemaining'].astype('float64')

    # Filter:
    df = df.loc[df['status']=="starter"]

    # Analyze:
    # Divide the player's annual prediction by the number of weeks (17) to get a weekly prediction
    df['weeklyPred'] = df['pred'] / 17
    # Calculate each player's expected score at the end of the game
    df['expectedLiveScore'] = df.apply(analysis.expectedLiveScore, axis=1)
    # Set colors for chart 
    df['color'] = df.apply(analysis.colorPicker, axis=1)

    # Visualize:
    fig = viz.liveScoring(df)
    # Encode in JSON format
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    # Render html template in flask
    return render_template('liveScoring.html', graphJSON=graphJSON)


@app.route("/logout")
#@login_required
def logout():
    logout_user()
    return render_template("logout.html")