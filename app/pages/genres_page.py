from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from app.app import app
from pathlib import Path

# Read the data
data_path = Path(__file__).resolve().parents[2] / 'data' / 'final_data' / 'global_17-24_daily_with_exploded_genres.csv'
df = pd.read_csv(data_path)

# Ensure 'date' column is string
df['date'] = df['date'].astype(str)

# Extract available years and genres for dropdown menus
available_years = sorted(df['date'].str[:4].unique(), key=int)
available_genres = sorted(df['genres'].unique(), key=str)
available_genres.remove('Not Found')

def generate_bar_chart(year):
    '''
    Generates a bar chart showing the genre distribution (as percentages) for a given year.

    Arguments:
        year (int): The year to filter the dataset.

    Returns:
        plotly.graph_objects.Figure: A bar chart showing the genre distribution as percentages.
    '''

    # Filter data for the selected year
    df_year = df[df['date'].str[:4] == str(year)].copy()

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
        color_discrete_sequence=px.colors.qualitative.Set3
    )

    # Improve readability and styling
    bar_fig.update_layout(
        paper_bgcolor="rgba(20,20,20,0.5)",
        plot_bgcolor="rgba(20,20,20,0.5)",
        font=dict(color="white"),
        xaxis_title="Genre",
        yaxis_title="Percentage of Songs",
        xaxis=dict(tickangle=45)
    )

    # Format y-axis to show percentage signs
    bar_fig.update_yaxes(ticksuffix="%")

    return bar_fig

# Function to generate line plot for genre evolution
def generate_line_plot(threshold=0.05):
    df_copy = df.copy()
    df_copy['year-month'] = df_copy['date'].str[:7]

    # Compute genre counts and percentages
    genre_counts = df_copy.groupby(['year-month', 'genres']
                                   ).size().unstack(fill_value=0)
    genre_percentages = genre_counts.div(genre_counts.sum(axis=1), axis=0) * 100

    # Drop genres using percentage
    total_counts = genre_counts.sum().sum()
    dynamic_threshold = total_counts * threshold
    dropped = genre_counts.columns[genre_counts.sum() < dynamic_threshold]
    genre_counts = genre_counts.drop(columns=dropped)
    genre_percentages = genre_percentages.drop(columns=dropped)

    # Remove 'Not Found' genre
    if 'Not Found' in genre_counts.columns:
        genre_counts = genre_counts.drop(columns=['Not Found'])
        genre_percentages = genre_percentages.drop(columns=['Not Found'])

    # Smooth data for line plot
    smoothed_genre_percentages = genre_percentages.rolling(window=3, min_periods=1).mean()

    # Reduce number of x-axis labels
    x_tickvals = smoothed_genre_percentages.index[::5]

    # Get colors from px.colors.qualitative.Vivid
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
        xaxis_title='Month',
        yaxis_title='Genre Representation (%)',
        xaxis=dict(tickmode='array', tickvals=x_tickvals, tickangle=45),
        legend_title='Genre',
        paper_bgcolor="rgba(20,20,20,0.5)",
        plot_bgcolor="rgba(20,20,20,0.5)",
        font=dict(color="white")
    )

    return line_fig

def generate_pie_chart(genre):

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
        genre_counts[range_name] = filtered_df['genres'].value_counts().rename(range_name)

    # Combine the results into a single DataFrame
    result_df = pd.concat(genre_counts, axis=1).fillna(0).astype(int)

    # Ensure the genre exists in the dataset
    if genre not in result_df.index:
        print(f"Genre '{genre}' not found in dataset.")
        return None

    # Get the data for the selected genre
    data = result_df.loc[genre, ['Upper', 'Mid', 'Lower']]

    # Create a pie chart
    fig = px.pie(
        values=data,
        names=data.index,
        labels={'names': 'Rank Range', 'values': 'Number of Songs'},
        hole=0.3,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )

    # Improve readability
    fig.update_traces(textposition='inside', textinfo='percent+label')

    # Dark mode styling
    fig.update_layout(
        paper_bgcolor="rgba(20,20,20,0.5)",
        plot_bgcolor="rgba(20,20,20,0.5)",
        font=dict(color="white")
    )

    return fig

def generate_boxplot(genre):
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
        paper_bgcolor="rgba(20,20,20,0.5)",
        plot_bgcolor="rgba(20,20,20,0.5)",
        font=dict(color="white"),
        yaxis=dict(title="Rank", autorange="reversed")
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
        html.H2("How did the diversity of listened music genres evolve on Spotify since 2017 and are the genre distributed among the chart ranks and are there genres dominating some rank ranges?")
    ], className='question'),

    html.Div([
        html.H2("Evolution of Genres in Daily Global Charts (2017-2024)")
    ], className='title'),

    html.Div([
        dcc.Graph(id='genre-trend-plot', figure=line_fig),
        html.Div(
            "The graphic on the right illustrates the evolution of genre representation in the daily global Spotify Charts from 2017 to 2025."
            "The x-axis represents months, while the y-axis shows the relative frequency of each genre. For some tracks the genre could not be identified",
        style=textstyle)
    ], className='container_genres'),

    html.Div([
        html.H2("Genre Distribution over the Years")
    ], className='title'),

    html.Div([
        dcc.Dropdown(
            id='year-dropdown',
            options=[{'label': year, 'value': year} for year in available_years],
            value=initial_year,
            clearable=False,
            persistence=True,
            persistence_type='session',
            style=dropdown_style),
        dcc.Graph(id='genre-bar-plot', figure=year_bar_fig),
        html.Div(
            "Er ist weder bearbeitbar noch kann seine Größe verändert werden."
            "Er ist weder bearbeitbar noch kann seine Größe verändert werden.",
            style=textstyle),
    ], className='container_genres'),

    html.Div([
        html.H2("Distribution of Songs by Genre and Rank")
    ], className='title'),

    html.Div([
        dcc.Dropdown(
            id='genre-dropdown',
            options=[{'label': genre, 'value': genre} for genre in available_genres],
            value=initial_genre,
            clearable=False,
            persistence=True,
            persistence_type='session',
            style=dropdown_style),

        dcc.Graph(id='genre-pie-plot', figure=rank_pie_fig),
        html.Div(
            "Er ist weder bearbeitbar noch kann seine Größe verändert werden."
            "Er ist weder bearbeitbar noch kann seine Größe verändert werden.",
            style=textstyle),

        dcc.Graph(id='genre-box-plot', figure=rank_box_fig),
        html.Div(
            "Er ist weder bearbeitbar noch kann seine Größe verändert werden."
            "Er ist weder bearbeitbar noch kann seine Größe verändert werden.",
            style=textstyle),
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

