import plotly
import plotly.express as px

def compareFranchises(df, how):
    fig = px.bar(df, 
                x="franchiseAbbrev", 
                y='relativeValue', 
                color="pos", 
                text='player', 
                color_discrete_map={
                    "QB": "hsla(210, 60%, 25%, 1)", 
                    "RB": "hsla(12, 50%, 45%, 1)", 
                    "WR": "hsla(267, 40%, 45%, 1)", 
                    "TE": "hsla(177, 68%, 36%, 1)", 
                    "PK": "hsla(14, 30%, 40%, 1)", 
                    "DF": "hsla(35, 70%, 65%, 1)"}, 
                category_orders={
                    "pos": ["QB", "RB", "WR", "TE", "PK", "DF"]},
                hover_name="player",
                hover_data={
                    'relativeValue':True, how:True,
                    'player':False, 'pos':False, 'franchiseName':False
                    },
                labels={
                    "franchiseName":"Franchise",
                    "relativeValue":"Relative Value",
                    how:"Predicted Points",
                }
                )
    fig.update_layout(
                barmode='stack', 
                xaxis={'categoryorder':'total descending'},
                plot_bgcolor='rgba(0,0,0,0)',
                title="Franchise Comparison",
                font_family="Skia",
                showlegend=False
                )
    return fig


def liveScoring(df):
    # Sort values to put franchises and players in order of expected live score
    df = df.sort_values(by='expectedLiveScore', ascending=False, ignore_index=True)
    # Order franchises along x-axis by total expected live score
    fran_rank = df.groupby('franchiseName').sum().sort_values(by='expectedLiveScore', ascending=False)
    sorter = fran_rank.index
    df['franchiseName'] = df['franchiseName'].astype("category")
    df['franchiseName'].cat.set_categories(sorter, inplace=True)
    df.sort_values(["franchiseName"], inplace=True)
    # Create bar chart
    fig = px.bar(df, 
                x="franchiseName", 
                y="expectedLiveScore", 
                color="playerName", 
                color_discrete_sequence=list(df['color']),
                category_orders={
                    "pos": ["QB", "RB", "WR", "TE", "PK", "DF"]},
                text='playerName', 
                hover_name="playerName",
                hover_data={
                    'expectedLiveScore':True, 
                    'scoreTotal':True, 
                    'liveScore':True,
                    'playerName':False, 
                    'pos':False, 
                    'franchiseAbbrev':False
                    },
                labels={
                    "franchiseName":"Franchise",
                    "liveScore":"Current Score",
                    "expectedLiveScore":"Projected Score",
                    "scoreTotal":"Initial Prediction"
                }
                )
    fig.update_layout(
                barmode='stack', 
                xaxis={'categoryorder':'total descending'},
                plot_bgcolor='rgba(0,0,0,0)',
                title="Live Scoring",
                font_family="Skia",
                showlegend=False
                )
    return fig
