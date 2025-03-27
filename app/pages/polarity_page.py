# Imports
import io
import base64
from pathlib import Path
from collections import Counter
import pandas as pd
import plotly.express as px
from dash import dcc, html, Input, Output
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from wordcloud import WordCloud
from sklearn.feature_extraction.text import CountVectorizer
import nltk
from nltk.corpus import stopwords
from app.app import app

# Read the data
data_path = Path(__file__).resolve().parents[2] / 'data' / 'final_data' / 'all_locations_with_polarity_and_spotify.csv'
df = pd.read_csv(data_path)

# Convert 'first_appearance' column to datetime format
df['first_appearance'] = pd.to_datetime(df['first_appearance'], errors='coerce')

# Extract all years from first_appearance
all_years = sorted(df['first_appearance'].dt.year.unique())

# Extract all artists and get the top 15 based on appearances for top15 dropdown and visualisation
artists_list = [artist.strip() for artists in df['artist_names'] for artist in artists.split(',')]
artist_counts = Counter(artists_list)
top_15_artists = [artist for artist, _ in artist_counts.most_common(15)]

# Get stop words for wordclouds
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

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

# Layout for sections
layout = html.Div([

    html.Div([
        html.H2("What is the contribution of positive and negative words (polarity) in english-language songs at different locations and different artists and how did it evolve on Spotify since 2017?")
    ], className='question'),

    # Div: Dropdown for charts area selection
    html.Div([
        dcc.Dropdown(
            id='location-dropdown',
            options=[{'label': loc, 'value': loc} for loc in df['location'].unique()],
            value='Global',
            searchable=False,
            style=dropdown_style
        ),
    ], className='container_polarity_location_dropdown'),

    html.Div([
        html.H2("Wordcloud from Lyrics per Year (Single words, Bigram, Trigram)")
    ], className='title'),

    # Div: Dropdown, visualisation and description for the wordcloud
    html.Div([
        dcc.Dropdown(
            id='year-dropdown-wordcloud',
            options=[{'label': str(year), 'value': str(year)} for year in all_years],
            value='2020',
            searchable=False,
            style=dropdown_style),
        dcc.Graph(id='wordcloud-graphs'),
        html.Div(
            "To give you a good insight on the lyrics, you can look at the most used single words, bigrams (two words used together) and trigrams (three words used together).",
            style=textstyle)
    ], className='container_polarity'),

    html.Div([
        html.H2("Polarity of Songs per Month per Year")
    ], className='title'),

    # Div: Dropdown, visualisation and description for the polarity of songs per month per year
    html.Div([
        dcc.Dropdown(
            id='year-dropdown',
            options=[{'label': str(year), 'value': str(year)} for year in all_years],
            value='2020',
            searchable=False,
            style=dropdown_style),
        dcc.Graph(id='polarity-graph'),
        html.Div(
            "This plot shows the distribution of the polarity over all months per year. You can adjust the year in the drodown.",
            style=textstyle)
    ], className='container_polarity'),
    
    html.Div([
        html.H2("Polarity, Song Duration, and Chart Days of Top 50 Artists per Year")
    ], className='title'),

    # Div: Dropdown, visualisation and description for the polarity, duration, and chart days of top 50 artists per year
    html.Div([
        dcc.Dropdown(
            id='year-dropdown-top50',
            options=[{'label': str(year), 'value': str(year)} for year in all_years],
            value='2020',
            searchable=False,
            style=dropdown_style),
        dcc.Graph(id='polarity-graph-top-50'),
        html.Div(
            "You can compare the different polarities with the duration of a song and the days a song stayed in the charts (size of the bubbles).",
            style=textstyle)
    ], className='container_polarity'),
    
    html.Div([
        html.H2("Polarity of Songs from Top 15 Artists over all Years")
    ], className='title'),

    # Div: Dropdown, visualisation and description for the polarity of songs from top 15 artists over all years
    html.Div([
        dcc.Dropdown(
            id='artist-dropdown',
            options=[{'label': artist, 'value': artist} for artist in top_15_artists],
            multi=True,
            value=[top_15_artists[0], top_15_artists[1]],
            searchable=False,
            style=dropdown_style
        ),
        dcc.Graph(id='polarity-graph-artist'),
        html.Div(
            "The top 15 artists per location based on appearing most often in the charts are available to compare their polarity.",
            style=textstyle)
    ], className='container_polarity'),

    html.Div([
        html.H2("Top 5 Songs with Highest and Lowest Polarity per Year")
    ], className='title'),

    # Div: Dropdown, visualisation and description for the top 5 songs with highest and lowest polarity per year
    html.Div([

        dcc.Dropdown(
            id='year-dropdown-top5',
            options=[{'label': str(year), 'value': str(year)} for year in all_years],
            value='2020',
            searchable=False,
            style=dropdown_style),
        dcc.Graph(id='polarity-graph-top-bottom'),
            html.Div(
            "Visualisation of top 5 positive and negative (polarity) songs per year.",
            style=textstyle)
    ], className='container_polarity'),
    
])

# Callbacks to update the visualisations
# Callback for the wordcloud
@app.callback(
    Output('wordcloud-graphs', 'figure'),
    [Input('year-dropdown-wordcloud', 'value'),
     Input('location-dropdown', 'value')]
)
def update_wordclouds(selected_year, selected_location):
    # Filter the selected year and location
    df_filtered = df[(df['first_appearance'].dt.year == int(selected_year)) & (df['location'] == selected_location)]
    
    # Get the lyrics for the selected year
    lyrics = df_filtered['lyrics'].dropna().astype(str).tolist()

    # Remove the stop words from the lyrics
    filtered_lyrics = [' '.join([word for word in lyric.split() if word.lower() not in stop_words]) for lyric in lyrics]

    # Creating three different wordclouds to align them in one row and to remove the axes for every one
    # Wordcloud one for single words
    wordcloud_1 = WordCloud(
        colormap='Spectral',
        mode="RGBA",
        background_color=None,
        max_words=50,
        width=400,
        height=400,
    ).generate(' '.join(filtered_lyrics))
    
    # Convert the first wordcloud image to base64
    img_byte_arr_1 = io.BytesIO()
    wordcloud_1.to_image().save(img_byte_arr_1, format='PNG')
    img_byte_arr_1.seek(0)
    img_base64_1 = base64.b64encode(img_byte_arr_1.getvalue()).decode('utf-8')

    # Wordcloud two for bigrams
    vectorizer_bigram = CountVectorizer(ngram_range=(2, 2), stop_words='english')
    bigrams = vectorizer_bigram.fit_transform(filtered_lyrics)
    bigram_counts = bigrams.sum(axis=0).A1
    bigram_terms = vectorizer_bigram.get_feature_names_out()
    bigram_freq = dict(zip(bigram_terms, bigram_counts))

    wordcloud_2 = WordCloud(
        colormap='Spectral',
        background_color=None,
        mode="RGBA",
        max_words=50,
        width=400,
        height=400,
    ).generate_from_frequencies(bigram_freq)
    
    # Convert the second wordcloud image to base64
    img_byte_arr_2 = io.BytesIO()
    wordcloud_2.to_image().save(img_byte_arr_2, format='PNG')
    img_byte_arr_2.seek(0)
    img_base64_2 = base64.b64encode(img_byte_arr_2.getvalue()).decode('utf-8')

    # Wordcloud three for trigrams
    vectorizer_trigram = CountVectorizer(ngram_range=(3, 3), stop_words='english')
    trigrams = vectorizer_trigram.fit_transform(filtered_lyrics)
    trigram_counts = trigrams.sum(axis=0).A1
    trigram_terms = vectorizer_trigram.get_feature_names_out()
    trigram_freq = dict(zip(trigram_terms, trigram_counts))

    wordcloud_3 = WordCloud(
        colormap='Spectral',
        background_color=None,
        mode="RGBA",
        max_words=75,
        width=400,
        height=400,
    ).generate_from_frequencies(trigram_freq)
    
    # Convert the third wordcloud image to base64
    img_byte_arr_3 = io.BytesIO()
    wordcloud_3.to_image().save(img_byte_arr_3, format='PNG')
    img_byte_arr_3.seek(0)
    img_base64_3 = base64.b64encode(img_byte_arr_3.getvalue()).decode('utf-8')

    # Create a subplot with three wordcloud images (Subplot is from ChatGPT)
    fig = make_subplots(rows=1, cols=3,)

    # Add the first WordCloud image (single)
    fig.add_trace(go.Image(source=f'data:image/png;base64,{img_base64_1}'),row=1, col=1)

    # Add the second wordcloud image (bigram)
    fig.add_trace(go.Image(source=f'data:image/png;base64,{img_base64_2}'),row=1, col=2)

    # Add the third wordcloud image (trigram)
    fig.add_trace(go.Image(source=f'data:image/png;base64,{img_base64_3}'),row=1, col=3)

    # Adjust the layout
    fig.update_layout(
        template='plotly_dark',
        showlegend=False,
        margin=dict(l=20, r=20, t=0, b=0),
        paper_bgcolor="rgba(20,20,20,0.5)",
        plot_bgcolor="rgba(20,20,20,0.5)",
        
        # Remove the axis for every plot alone (otherwise its showing 2/3 axis)
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        xaxis2=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis2=dict(showgrid=False, zeroline=False, showticklabels=False),
        xaxis3=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis3=dict(showgrid=False, zeroline=False, showticklabels=False),
    )

    return fig

# Callback to update polarity graph
@app.callback(
    Output('polarity-graph', 'figure'),
    [Input('year-dropdown', 'value'),
     Input('location-dropdown', 'value')]
)
def update_violin_plot(selected_year, selected_location):
    # Filter the selected year and location
    df_filtered = df[(df['first_appearance'].dt.year == int(selected_year)) & (df['location'] == selected_location)]
    
    # Convert numbers to monthnames
    month_mapping = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 
                     7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
    
    # Replace the numbers with monthnames
    df_filtered['month_name'] = df_filtered['first_appearance'].dt.month.map(month_mapping)
    
    # Visualize as a violin plot with color by month_name
    fig = px.violin(df_filtered, x='month_name', y='polarity', points=False,
                    color='month_name',
                    labels={'month_name': 'Month', 'polarity': 'Polarity'},
                    color_discrete_sequence=px.colors.qualitative.Vivid
    )
    
    # Sort the monthnames on the x axis
    fig.update_xaxes(categoryorder='array', categoryarray=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                                                           'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])

    # Adjust the layout
    fig.update_layout(
        template='plotly_dark',
        showlegend=False,
        xaxis_title='Month',
        xaxis_title_font=dict(family='Arial', weight='bold'),
        yaxis_title='Polarity',
        yaxis_title_font=dict(family='Arial', weight='bold'),
        paper_bgcolor="rgba(20,20,20,0.5)",
        plot_bgcolor="rgba(20,20,20,20.5)"
    )

    return fig

# Callback for the polarity of top 50 artists based on max chart days
@app.callback(
    Output('polarity-graph-top-50', 'figure'),
    [Input('year-dropdown-top50', 'value'),
     Input('location-dropdown', 'value')]
)
def update_top50_scatter(selected_year, selected_location):
    # Filter the selected year and location
    df_filtered = df[(df['first_appearance'].dt.year == int(selected_year)) & (df['location'] == selected_location)]
    
    # Get the top 50 artists based on chart days
    grouped_df = df_filtered.groupby('artist_names').agg({'polarity': 'mean', 'duration_seconds': 'mean', 'max_days_on_chart': 'sum'}).reset_index()
    top_50_artists = grouped_df.nlargest(50, 'max_days_on_chart')

    # Visualize as a scatter plot
    fig = px.scatter(top_50_artists,
                     x='polarity',
                     y='duration_seconds',
                     size='max_days_on_chart',
                     color='artist_names',
                     hover_name='artist_names',
                     labels={'polarity': 'Polarity (avg)', 'duration_seconds': 'Duration (avg in sec)', 'max_days_on_chart': 'Chart Days'}
    )
    
    # Adjust the layout
    fig.update_layout(template='plotly_dark',
                      showlegend=False,
                      yaxis=dict(title='Duration (avg in sec)', range=[100, 350], dtick=50),
                      xaxis_title_font=dict(family='Arial', weight='bold'),
                      xaxis=dict(title='Polarity (avg)', range=[-0.75, 0.75], dtick=0.25),
                      yaxis_title_font=dict(family='Arial', weight='bold'),
                      paper_bgcolor="rgba(20,20,20,0.5)",
                      plot_bgcolor="rgba(20,20,20,0.5)"
    )
    
    return fig

# Callback for polarity of top 5 songs
@app.callback(
    Output('polarity-graph-top-bottom', 'figure'),
    [Input('year-dropdown-top5', 'value'),
     Input('location-dropdown', 'value')]
)
def update_top5_songs(selected_year, selected_location):
    # Filter the selected year and location
    df_filtered = df[(df['first_appearance'].dt.year == int(selected_year)) & (df['location'] == selected_location)].copy()
    
    # Get the main artist for the songs
    def get_main_artist(artist_names):
        artist_list = [artist.strip() for artist in artist_names.split(',')]
        return artist_list[0] if len(artist_list) > 1 else artist_list[0]

    df_filtered['main_artist'] = df_filtered['artist_names'].apply(get_main_artist)

    # Shorten the track name
    def shorten_track_name(track_name):
        return track_name.split('(')[0].strip() if '(' in track_name else track_name

    df_filtered['shortened_track_name'] = df_filtered['track_name'].apply(shorten_track_name)

    # Don't show the same song twice
    df_filtered.drop_duplicates(subset=['main_artist', 'shortened_track_name'], inplace=True)

    # Extract top 5 top and bottom polarity
    top_polarity = df_filtered.nlargest(5, 'polarity')
    bottom_polarity = df_filtered.nsmallest(5, 'polarity')
    
    # Add polarity types
    top_polarity['Polarity Type'] = 'Positive'
    bottom_polarity['Polarity Type'] = 'Negative'

    # Combine top and bottom polarity rows
    combined_df = pd.concat([top_polarity, bottom_polarity])

    # Visualize as a bar chart
    fig = px.bar(
        combined_df, 
        y='main_artist', 
        x='polarity', 
        color='Polarity Type',
        labels={'shortened_track_name': 'Trackname', 'polarity': 'Polarity', 'main_artist': 'Main Artist'},
        hover_data=['main_artist', 'shortened_track_name'],
        color_discrete_map={
            'Positive': 'rgb(93, 105, 177, 0.5)',
            'Negative': 'rgb(229, 134, 6, 0.5)'},
        text='shortened_track_name'
    )

    # Adjust the layout
    fig.update_layout(
        template='plotly_dark',
        showlegend=False,
        xaxis=dict(range=[-1, 1], dtick=0.5, title='Polarity'),
        xaxis_title_font=dict(family='Arial', weight='bold'),
        yaxis=dict(
            title='Main Artist',
            fixedrange=True,
            categoryorder='array',
            categoryarray=combined_df['main_artist'].tolist()),
        yaxis_title_font=dict(family='Arial', weight='bold'),
        autosize=True,
        margin=dict(l=150, r=80, t=80, b=80),
        paper_bgcolor="rgba(20,20,20,0.5)",
        plot_bgcolor="rgba(20,20,20,0.5)")

    fig.update_traces(
        textfont=dict(family='Arial', size=16, color='white', weight='bold'),
        textposition='inside'
    )

    return fig

# Callback for polarity comparison
@app.callback(
    Output('polarity-graph-artist', 'figure'),
    [Input('artist-dropdown', 'value'),
     Input('location-dropdown', 'value')]
)
def update_artist_polarity(selected_artists, selected_location):
    # Get all rows which include one top 15 artist and selected location
    def match_artist(artist_names):
        return any(artist in [a.strip() for a in artist_names.split(',')] for artist in selected_artists)

    df_selected = df[df['artist_names'].apply(match_artist) & (df['location'] == selected_location)]
        
    # Get the main artist (first one) for the visualisation (space reason)
    def get_main_artist(artist_names):
        found_artists = [artist for artist in selected_artists if artist in [a.strip() for a in artist_names.split(',')]]
        if found_artists:
            return found_artists[0]
        return artist_names

    # Filter the main artist
    df_selected['main_artist'] = df_selected['artist_names'].apply(get_main_artist)
    
    # Convert 'first_appearance' to a period and then to a string (YYYY-MM)
    df_selected['year_month'] = df_selected['first_appearance'].dt.to_period('M').astype(str)
    
    # Group by 'year_month' and 'main_artist', and calculate the average polarity
    polarity_by_month = df_selected.groupby(['year_month', 'main_artist'])['polarity'].mean().reset_index()
    
    # Visualize as a line plot
    fig = px.line(polarity_by_month, x='year_month', y='polarity', color='main_artist', labels={'year_month': 'Date', 'polarity': 'Polarity', 'main_artist': 'Artist'})

    # Adjust the layout
    fig.update_layout(
        template='plotly_dark', 
        legend_title='Artist(s)',
        xaxis=dict(showgrid=True, fixedrange=True, title='Year-Month'),
        xaxis_title='Year',
        xaxis_title_font=dict(family='Arial', weight='bold'),
        yaxis=dict(range=[-1, 1], dtick=0.5, fixedrange=True),
        yaxis_title='Polarity',
        yaxis_title_font=dict(family='Arial', weight='bold'),
        autosize=True,
        margin=dict(l=80, r=80, t=80, b=80),
        paper_bgcolor="rgba(20,20,20,0.5)",
        plot_bgcolor="rgba(20,20,20,0.5)"
    )

    fig.update_yaxes(categoryorder='array', categoryarray=selected_artists)
    
    return fig