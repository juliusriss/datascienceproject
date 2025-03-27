# Imports
import re
from pathlib import Path
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import CacheHandler
import pandas as pd
import plotly.express as px
from app.app import app

# Function for normalizing the track and artist names for matching
def normalize_string(s):
    s = s.lower()
    s = re.sub(r'[.,]', '', s)
    return s

# Match the requested spotify data with the charts data from the df
def match_tracks(spotify_tracks, df):
    df['normalized_track_name'] = df['track_name'].apply(normalize_string)
    df['normalized_artists'] = df['artist_names'].apply(lambda x: [normalize_string(a) for a in x.split(',')])

    matched_years = []

    for track in spotify_tracks:
        track_name = normalize_string(track['name'])
        track_artists = [normalize_string(artist['name']) for artist in track['artists']]

        for _, row in df.iterrows():
            if track_name == row['normalized_track_name'] and any(artist in row['normalized_artists'] for artist in track_artists):
                matched_years.append(row['year'])
                break

    return matched_years

# Read the data
data_path = Path(__file__).resolve().parents[2] / 'data' / 'final_data' / 'all_locations_with_polarity_and_spotify.csv'
df = pd.read_csv(data_path)

# Spotify API credentials
SPOTIPY_CLIENT_ID = '213250a911734e19ba80a69269f564e4'
SPOTIPY_CLIENT_SECRET = '08053b9acca043e8807b86b27f52fd0b'
SPOTIPY_REDIRECT_URI = 'http://127.0.0.1:8050/callback'

# Scope for user data
SCOPE = 'user-top-read'

# Class to prevent caching the access token
class NoCache(CacheHandler):
    def get_cached_token(self):
        return None

    def save_token_to_cache(self, token_info):
        pass

# Spotify OAuth authentication
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                               client_secret=SPOTIPY_CLIENT_SECRET,
                                               redirect_uri=SPOTIPY_REDIRECT_URI,
                                               scope=SCOPE,
                                               cache_handler=NoCache()))

# Style definitions for dropdown and textstyle
dropdown_style = {
    'backgroundColor': 'white',
    'color': 'black',
    'font-size': '18px',
    'border-radius': '5px',
    'font-weight': 'bold'
}

textstyle={
    'font-size': '18px',
    'line-height': '1.6',
    'color': '#f2f2f2',
    'font-weight': '600',
    'margin-top': '20px',
    'white-space': 'pre-wrap',
    'word-wrap': 'break-word',
    'font-family': 'Arial, sans-serif'
}

# Layout for the sections
layout = html.Div([

    html.Div([
        html.H2('How does a users music taste change over a year and how many of a specific users favorite songs can be found in the charts?')
    ], className='question'),

    # Div: Dropdowns for data scope
    html.Div([

        # Div: Dropdown for top tracks fetch
        html.Div([
            dcc.Dropdown(
                id='top-n-dropdown',
                options=[
                    {'label': 'Top 10 Tracks', 'value': '10'},
                    {'label': 'Top 20 Tracks', 'value': '20'},
                    {'label': 'Top 30 Tracks', 'value': '30'},
                    {'label': 'Top 40 Tracks', 'value': '40'},
                    {'label': 'Top 50 Tracks', 'value': '50'},],
                value='10',
                searchable=False,
                style=dropdown_style)
        ]),

        # Div: Dropdown for selection for time period
        html.Div([
            dcc.Dropdown(
                id='time-selection-dropdown',
                options=[
                    {'label': 'Last Month', 'value': 'short_term'},
                    {'label': 'Last 6 Months', 'value': 'medium_term'},
                    {'label': 'Last 12 Months', 'value': 'long_term'}
                ],
                value='short_term',
                searchable=False,
                style=dropdown_style)
        ]),

    ], className='container_spotify_dropdown'),

    html.Div([
        html.H2("Songs You Listened to with their Release Date and their Popularity")
    ], className='title'),

    # Div: Visualisation for listened songs in relation to their release date
    html.Div([
        dcc.Graph(id='bubble-chart-release-date'),
        html.Div(
            "You can see all songs you listened to up to the last year (dropdown) with their release date. "
            "The color of the bubles represents the different artists and the size represents the polularity of the songs",
            style=textstyle),
    ], className='container_spotify'),

    html.Div([
        html.H2(
            "Songs You listened to with their First Appearance in the Charts and their Popularity (2017-2024)")
    ], className='title'),

    # Div: Visualisation for listend songs in relation to their release date
    html.Div([
        dcc.Graph(id='bubble-chart-charts-date'),
        html.Div(
            "This graphic shows the appearance of songs you listened to in the charts (time range 2017 - 2024). "
            "The color of the bubles represents the different artists and the size represents the polularity of the songs",
            style=textstyle),
    ], className='container_spotify'),

    html.Div([
        html.H2("Your top tracks")
    ], className='title'),

    # Div: Top-n top tracks visualisation
    html.Div([
        html.Div(id='top-tracks')
    ], className='container_toptracks')

])

# Callback for top-n tracks and bubble charts
@app.callback(
    [Output('top-tracks', 'children'),
     Output('bubble-chart-release-date', 'figure'),
     Output('bubble-chart-charts-date', 'figure')],
    [Input('top-n-dropdown', 'value'),
     Input('time-selection-dropdown', 'value')]
)
# ChatGPT helped me creating this function as well as the alingment from the top tracks (#top tracks in CSS file)
def fetch_top_tracks_and_bubble_chart(top_n, time_range):
    # Fetch user's top tracks based on the dropdown selection
    try:
        results = sp.current_user_top_tracks(limit=int(top_n), time_range=time_range)
        top_tracks = results['items']
        
        # Prepare the track data for display
        tracks_data = []
        for idx, track in enumerate(top_tracks):
            tracks_data.append(html.Div([
                html.Img(src=track['album']['images'][0]['url'], style={'width': '100px'}),
                html.H3(f"{idx+1}. {track['name']} by {track['artists'][0]['name']}")
            ]))

        # Match the tracks with the charts data
        matched_year_months = []
        matched_first_appearance = []
        for track in top_tracks:
            # Extract the release year and month from the album's release date
            album_release_date = track['album']['release_date']
            year_month = album_release_date[:7]
            matched_year_months.append(year_month)

            # Match first_appearance from df
            track_name = track['name']
            track_artists = ', '.join([artist['name'] for artist in track['artists']])
            matched_row = df[(df['track_name'] == track_name) & (df['artist_names'].str.contains(track_artists))]
            if not matched_row.empty:
                first_appearance = matched_row.iloc[0]['first_appearance']
                matched_first_appearance.append(first_appearance)
            else:
                matched_first_appearance.append(None)

        # Bubble Chart for release date
        bubble_data_release = []
        for track, year_month in zip(top_tracks, matched_year_months):
            artists = ', '.join([artist['name'] for artist in track['artists']])
            popularity = track['popularity']

            bubble_data_release.append({
                'year_month': year_month,
                'track_name': track['name'],
                'artists': artists,
                'popularity': popularity
            })

        bubble_df_release = pd.DataFrame(bubble_data_release)

        if bubble_df_release.empty:
            # No matches to visualise
            fig_release = px.scatter(title='No matches found', template='plotly_dark')
        else:

            # Visualise as a scatter plot
            fig_release = px.scatter(bubble_df_release, 
                                    x='year_month',
                                    y='track_name', 
                                    size='popularity',
                                    color='artists',
                                    hover_name='track_name',
                                    hover_data=['artists', 'popularity'],
                                    template='plotly_dark',
                                    labels={'year_month': 'Release Date', 'artists': 'Artist(s)', 'track_name': 'Trackname', 'popularity': 'Popularity'})

            # Update the axes
            fig_release.update_yaxes(title='Trackname', title_font=dict(size=14, family='Arial', weight='bold'))
            fig_release.update_xaxes(title='Year', title_font=dict(size=14, family='Arial', weight='bold'))

            # Adjust the background
            fig_release.update_layout(showlegend=False, plot_bgcolor='rgba(20,20,20,0.5)', paper_bgcolor='rgba(20,20,20,0.5)')

        # Bubble Chart for first appearance
        bubble_data_appearance = []

        for track, first_appearance in zip(top_tracks, matched_first_appearance):
            if first_appearance:
                artists = ', '.join([artist['name'] for artist in track['artists']])
                popularity = track['popularity']
                bubble_data_appearance.append({
                    'first_appearance': first_appearance,
                    'track_name': track['name'],
                    'artists': artists,
                    'popularity': popularity})

        bubble_df_appearance = pd.DataFrame(bubble_data_appearance)

        if bubble_df_appearance.empty:
            # No matches to visualise
            fig_appearance = px.scatter(title='No matches found', template='plotly_dark')
        else:
            # Visualise as a scatter plot
            fig_appearance = px.scatter(bubble_df_appearance, 
                                        x='first_appearance',
                                        y='track_name', 
                                        size='popularity',
                                        color='artists',
                                        hover_name='track_name',
                                        hover_data=['artists', 'popularity'],
                                        template='plotly_dark',
                                        labels={'first_appearance': 'First Appearance', 'artists': 'Artist(s)', 'track_name': 'Trackname', 'popularity': 'Popularity'})

            # Update the axes
            fig_appearance.update_yaxes(title='Trackname', title_font=dict(size=14, family='Arial', weight='bold'))
            fig_appearance.update_xaxes(title='Year', title_font=dict(size=14, family='Arial', weight='bold'))

            # Adjust the background
            fig_appearance.update_layout(showlegend=False, plot_bgcolor='rgba(20,20,20,0.5)', paper_bgcolor='rgba(20,20,20,0.5)')

        return tracks_data, fig_release, fig_appearance

    except Exception as e:
        fig_release = px.scatter(title=f'Error: {str(e)}', template='plotly_dark')
        fig_appearance = px.scatter(title=f'Error: {str(e)}', template='plotly_dark')
        
        return f'Error: {str(e)}', fig_release, fig_appearance