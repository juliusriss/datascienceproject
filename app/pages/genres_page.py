from dash import html, dcc, Input, Output
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from app.app import app
from pathlib import Path

# Read the data
data_path = Path(__file__).resolve(
    ).parents[2]/ 'data' / 'final_data' / 'global_17-24_daily_with_exploded_'\
                                                                 'genres.csv'
df = pd.read_csv(data_path)

# Ensure 'date' column is string
df['date'] = df['date'].astype(str)

# Extract available years and genres for dropdown menus
available_years = sorted(df['date'].str[:4].unique(), key=int)
available_genres = sorted(df['genres'].unique(), key=str)
available_genres.remove('Not Found')

def generate_bar_chart(year):
    '''
    Generates a bar chart showing the genre distribution (as percentages) for a
    given year.

    Arguments:
        year (int): The year to filter the dataset.

    Returns:
        plotly.express.Figure: A bar chart showing the genre distribution
        as percentages.
    '''

    # Filter data for the selected year and exlude Not Found
    df_year = df[(df['date'].str[:4] == str(year))].copy()

    # Count occurrences of each genre and convert to percentage
    genre_counts_year = df_year['genres'].value_counts(normalize=True
                                                       ).reset_index()
    genre_counts_year.columns = ['Genre', 'Percentage']
    genre_counts_year['Percentage'] = genre_counts_year['Percentage'] * 100

    # Sort genres by percentage
    genre_counts_year = genre_counts_year.sort_values(by='Percentage',
                                                      ascending=False)

    # Generate bar chart
    bar_fig = px.bar(
        genre_counts_year,
        x='Genre',
        y='Percentage',
        color='Genre',
        color_discrete_sequence=px.colors.qualitative.Vivid
    )

    # Improve readability and styling
    bar_fig.update_layout(
        paper_bgcolor='rgba(20,20,20,0.5)',
        plot_bgcolor='rgba(20,20,20,0.5)',
        font=dict(color='white'),
        legend=dict(
            title=dict(text='Genres', font=dict(size=16, weight='bold')),
            font=dict(size=14)),
        xaxis=dict(
            title=dict(text='Genre', font=dict(size=16, weight='bold')),
            tickfont=dict(size=14), 
            tickangle=45
        ),
        yaxis=dict(
            title=dict(text='Genre Represenatation (%)', font=dict(size=16, 
                                                             weight='bold')),
            tickfont=dict(size=14),
            showgrid=True,
            gridcolor='rgba(200, 200, 200, 0.3)',
            gridwidth=0.5
        )
    )

    # Format y-axis to show percentage signs
    bar_fig.update_yaxes(ticksuffix='%')

    return bar_fig

def generate_line_plot(threshold=0.05):
    '''
    Generates a line plot showing the genre representation (as percentages) over
    the entire data (2017 - 2024). A threshold can be applied filter the genres
    dropping all genres which overall representation does not meet threshold

    Arguments:
        threshold (float): The threshold do filter the genres. Default is 0.05
        i.d. 5%.

    Returns:
        plotly.graph_objects.Figure: A bar chart showing the genre distribution
        as percentages.
    '''
    df_copy = df.copy()
    df_copy['year-month'] = df_copy['date'].str[:7]

    # Compute genre counts and percentages
    genre_counts = df_copy.groupby(['year-month', 'genres']
                                   ).size().unstack(fill_value=0)
    genre_percentages = genre_counts.div(genre_counts.sum(axis=1), axis=0) * 100

    # Drop genres which do not meet threshold
    total_counts = genre_counts.sum().sum()
    dynamic_threshold = total_counts * threshold
    dropped = genre_counts.columns[genre_counts.sum() < dynamic_threshold]
    genre_percentages = genre_percentages.drop(columns=dropped)

    # Remove 'Not Found' genre
    if 'Not Found' in genre_counts.columns:
        genre_percentages = genre_percentages.drop(columns=['Not Found'])

    # Smooth data for line plot
    smoothed_genre_percentages = genre_percentages.rolling(window=3,
                                                           min_periods=1).mean()

    # Reduce number of x-axis labels
    x_tickvals = smoothed_genre_percentages.index[::5]

    # Create color map to use custom colors for each genre line
    colors = px.colors.qualitative.Vivid
    color_map = {genre: colors[i % len(colors)]
                 for i, genre in enumerate(smoothed_genre_percentages.columns)}

    # Create Line Plot
    line_fig = go.Figure()
    for genre in smoothed_genre_percentages.columns:
        line_fig.add_trace(go.Scatter(
            x=smoothed_genre_percentages.index,
            y=smoothed_genre_percentages[genre],
            mode='lines',
            name=genre,
            line=dict(color=color_map[genre])
        ))

    # Customize layout
    line_fig.update_layout(
        height=600,
        legend=dict(
            title=dict(text='Genre', font=dict(size=16, weight='bold')),
            font=dict(size=14)
        ),
        paper_bgcolor='rgba(20,20,20,0.5)',
        plot_bgcolor='rgba(20,20,20,0.5)',
        font=dict(color='white'),
        xaxis=dict(
            title=dict(text='Month', font=dict(size=16, weight='bold')),
            tickfont=dict(size=14),
            tickvals=x_tickvals,
            tickmode='array',
            tickangle=45,
            showgrid=True,
            gridcolor='rgba(200, 200, 200, 0.3)',
            gridwidth=0.5
        ),
        yaxis=dict(
            title=dict(text='Genre Representation (%)',
                       font=dict(size=16, weight='bold', family='Arial')),
            tickfont=dict(size=16),
            showgrid=True,
            gridcolor='rgba(200, 200, 200, 0.3)',
            gridwidth=0.5
        )
    )

    return line_fig

def generate_pie_chart(genre):
    '''
    Generates a pie chart showing the genre distribution (as percentages)
    across three rank ranges for a given genre.

    Arguments:
        genre (str): The genre to show the distribution for

    Returns:
        plotly.express.Figure: A pie chart showing the genre distribution
        across three rank ranges as percentages.
    '''
    # Define the rank ranges
    rank_ranges = {
        'Upper': (1, 66),
        'Mid': (67, 133),
        'Lower': (134, 200)
    }

    # Initialize a dictionary to store the results
    genre_counts = {}

    # Loop through each rank range and count songs per genre
    for range_name, (start, end) in rank_ranges.items():
        # Filter the DataFrame for the current rank range
        filtered_df = df[(df['rank'] >= start) & (df['rank'] <= end)]

        # Count the number of songs per genre in the filtered DataFrame
        genre_counts[range_name] = filtered_df['genres'].value_counts(
                                                       ).rename(range_name)

    # Combine the results into a single DataFrame
    result_df = pd.concat(genre_counts, axis=1).fillna(0).astype(int)

    # Ensure the genre exists in the dataset
    if genre not in result_df.index:
        print(f'Genre "{genre}" not found in dataset.')
        return None

    # Get the data for the selected genre
    data = result_df.loc[genre, ['Upper', 'Mid', 'Lower']]

    # Create a pie chart
    fig = px.pie(
        values=data,
        names=data.index,
        labels={'names': 'Rank Range', 'values': 'Number of Songs'},
        hole=0.3,
        color_discrete_sequence=px.colors.qualitative.Vivid
    )

    # Improve readability
    fig.update_traces(textposition='inside', textinfo='percent+label')

    # Dark mode styling
    fig.update_layout(
        paper_bgcolor='rgba(20,20,20,0.5)',
        plot_bgcolor='rgba(20,20,20,0.5)',
        font=dict(color='white')
    )

    return fig

def generate_boxplot(genre):
    '''
    Generates a boxplot showing the genre distribution (as percentages)
    across the ranks for a given genre.

    Arguments:
        genre (str): The genre to show the distribution for

    Returns:
        plotly.express.Figure: A boxplot showing the genre distribution
        across the ranks as percentages.
    '''
    # Filter data for the selected genre
    df_genre = df[df['genres'] == genre].copy()
    
    # Create a box plot
    rank_fig = px.box(
        df_genre,
        y='rank',
        labels={'rank': 'Chart Rank'},
        color_discrete_sequence=px.colors.qualitative.Vivid
    )

    # Improve styling
    rank_fig.update_layout(
        paper_bgcolor='rgba(20,20,20,0.5)',
        plot_bgcolor='rgba(20,20,20,0.5)',
        font=dict(color='white'),
        yaxis=dict(
            title=dict(text='Rank', font=dict(size=16, weight='bold')),
            tickfont=dict(size=14),
            autorange='reversed',
            showgrid=True,
            gridcolor='rgba(200, 200, 200, 0.3)',
            gridwidth=0.5
        )
    )

    return rank_fig

# Generate initial plots with initial values
initial_year = '2020'
initial_genre = 'Pop'

year_bar_fig = generate_bar_chart(initial_year)
line_fig = generate_line_plot()
rank_pie_fig = generate_pie_chart(initial_genre)
rank_box_fig = generate_boxplot(initial_genre)

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

layout = html.Div([

    html.Div([
        html.H2('How did the Diversity of Music Genres in the Spotify Daily '
        'Global Charts since 2017 evolve? '
        'How are the Genres distributed among the Chart Ranks and are there '
        'Genres dominating some Rank ranges?')
    ], className='question'),

    html.Div([
        html.H2('Evolution of Genres in Daily Global Charts (2017-2024)')
    ], className='title'),

    html.Div([
        dcc.Graph(id='genre-trend-plot', figure=line_fig),
        html.Div(
            'This line chart illustrates the evolution of genre representation '
            'in the daily global Spotify Charts from 2017 to 2025. '
            'The x-axis represents the months over the years, while the y-axis '
            'shows the relative frequency of each genre. For some tracks the '
            'genre could not be identified. In total, ~22.57% of tracks were '
            'affected by this. To maintain clarity, genres that appeared in'
            'less than 5% of the dataset were excluded from this'
            'visualization.',
        style=textstyle)
    ], className='container_genres'),

    html.Div([
        html.H2('Genre Distribution for a Year')
    ], className='title'),

    html.Div([
        dcc.Dropdown(
            id='year-dropdown',
            options=[{'label': year, 'value': year}
                     for year in available_years],
            value=initial_year,
            clearable=False,
            style=dropdown_style),
        dcc.Graph(id='genre-bar-plot', figure=year_bar_fig),
        html.Div(
            'This bar chart provides the distribution of representation of all '
            'found music genres for a given year.It is meant to provide a more '
            'detailed look by showing all found genres, including a '
            'representation for all not identified genres (in "Not Found").',
            style=textstyle),
    ], className='container_genres'),

    html.Div([
        html.H2('Distribution of a Genre\'s Representation by Rank and '
                'Rank ranges')
    ], className='title'),

    html.Div([
        dcc.Dropdown(
            id='genre-dropdown',
            options=[{'label': genre, 'value': genre} 
                     for genre in available_genres],
            value=initial_genre,
            clearable=False,
            style=dropdown_style),

        dcc.Graph(id='genre-pie-plot', figure=rank_pie_fig),
        html.Div(
            'This pie chart visualizes how different music genres are '
            'distributed across chart rank ranges and whether certain genres '
            'dominate specific rank ranges. The rank ranges are categorized '
            'into three tiers: upper (1-66), mid (67-133), and lower '
            '(134-200).',
            style=textstyle),

        dcc.Graph(id='genre-box-plot', figure=rank_box_fig),
        html.Div(
            'This boxplot visualizes how different music genres are '
            'distributed across chart ranks. It is meant to provide a more '
            'detailed insight into the distribution of music genres across '
            'ranks in contrast to the previous pie chart.',
            style=textstyle)
    ], className='container_genres')

])

# Define callback to update bar chart
@app.callback(
    Output('genre-bar-plot', 'figure'),
    Input('year-dropdown', 'value')
)
def update_bar_chart(year):
    return generate_bar_chart(year)

# Define callback for pie chart and box plot
@app.callback(
    [Output('genre-pie-plot', 'figure'),
     Output('genre-box-plot', 'figure')],
    Input('genre-dropdown', 'value')
)
def update_figures(genre):
    pie_chart = generate_pie_chart(genre)
    box_plot = generate_boxplot(genre)
    return pie_chart, box_plot
