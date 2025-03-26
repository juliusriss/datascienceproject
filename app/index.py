import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from app.pages import home_page, genres_page, polarity_page, solo_collab_page, release_time_page, crisis_page, happiness_score_page
from app.app import app

# Make sure the server instance is defined at the top
server = app.server

# Define the head
head = html.Div([

    # Title
    html.Div("Spotify Charts", className="nav-title"),

    # Navbar
    html.Div([
        dcc.Link('Home', href='/', className="nav-link"),
        dcc.Link('Genres', href='/genres', className="nav-link"),
        dcc.Link('Polarity', href='/polarity', className="nav-link"),
        dcc.Link('Solo vs. Collaboration', href='/solo_collab', className="nav-link"),
        dcc.Link('Release Time', href='/release_time', className="nav-link"),
        dcc.Link('Happiness Score', href='/happiness_score', className="nav-link"),
        dcc.Link('Crisis', href='/crisis', className="nav-link"),
        dcc.Link('Explicity Prediction', href='/explicity_prediction', className="nav-link"),
        dcc.Link('Spotify Stats', href='/spotify_stats', className="nav-link"),
    ], className="nav-links")
], className="navbar")

# Define the layout of the app
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    head,
    html.Div(id='page-content')
])

# Define the callback to display the correct page


@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname in ('', '/', 'home', ' '):
        return home_page.layout
    elif pathname == '/genres':
        return genres_page.layout
    elif pathname == '/polarity':
        return polarity_page.layout
    elif pathname == '/solo_collab':
        return solo_collab_page.layout
    elif pathname == '/release_time':
        return release_time_page.layout
    elif pathname == '/crisis':
        return crisis_page.layout
    elif pathname == '/happiness_score':
        return happiness_score_page.layout
    else:
        return html.H3("404 - Could not find page")

if __name__ == '__main__':
    app.run(debug=False, port=8051)
