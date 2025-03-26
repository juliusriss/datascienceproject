import dash

# Create the Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Spotify Charts"