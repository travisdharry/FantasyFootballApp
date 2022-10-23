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