from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from app.app import app
from pathlib import Path

rq1_bar_text = """The pie bar provides an overview of genre representation in \
the daily global Spotify Charts for each year, offering insights into how \
different genres have been distributed over time."""

rq1_line_text = """The graphic on the right illustrates the evolution of genre \
representation in the daily global Spotify Charts from 2017 to 2025. The x-axis \
represents months, while the y-axis shows the relative frequency of \
each genre.
For some tracks the genre could not be identified. In total, ~22.57% of tracks \
fell victim to this. To maintain clarity, genres that appeared in less than \
5% of the dataset were excluded from this visualization.
The three most prominent genres—**Electronic, Hip Hop, and Pop**—exhibit \
distinct trends:
- **Electronic music** saw a sharp decline, starting at around 25% in 2017 and \
gradually dropping to just 10% by the end of 2024.
- **Hip Hop** followed a similar pattern. It began at ~14%, rising steadily to \
a peak of 22% in March 2019, before plunging to 15% by mid-2019. After a brief \
recovery to ~19% in mid-2020, it continued to decline, reaching just ~7% by \
late 2024.
- **Pop** remained relatively stable, consistently fluctuating between 20-25%. \
Several smaller genres also show noticeable trends:
- **Alternative/Indie** steadily increased in representation. Initially at ~5% \
in early 2017, it briefly dipped to 4% a year later before rising consistently, \
reaching ~12% by 2025.
- A similar trend is observed in **Rock music**, which grew from ~6% to ~10%. \
The correlation between Rock and Alternative/Indie may stem from shared \
stylistic traits, leading to overlapping classifications.
- **R&B/Soul** experienced significant fluctuations, with a sharp drop in \
mid-2017, followed by a slow recovery and continued volatility.
- **Latin music** displayed a dramatic rise and fall. Starting at ~3% in 2017, \
it peaked at nearly 10% in mid-2023 before declining steeply, returning to ~3% \
by the end of 2024.
"""  

rq2_text = """
The visualization consists of two plots—a pie chart and a box plot—both of \
which update dynamically based on the selected genre from the dropdown menu.
The pie chart illustrates the distribution of songs within the selected genre \
across three ranking tiers: upper (1-66), mid (67-133), and lower (134-200). \
It provides a clear visual representation of whether a genre is predominantly \
found in higher, middle, or lower ranks.
The box plot shows the rank distribution of the selected genre in more detail, \
displaying key statistical values such as the median, interquartile range \
(IQR), and potential outliers. The box represents the middle 50% of rankings, \
with the horizontal line indicating the median position. The whiskers extend to \
the minimum and maximum ranks within a reasonable range, while any outliers are \
plotted separately.
Together, these plots offer insights into how each genre performs in the \
charts, helping to determine whether certain genres tend to dominate specific \
rank ranges.
The analysis examines how different music genres are distributed across chart \
ranks and whether certain genres dominate specific rank ranges. The ranking \
data is categorized into three tiers: upper (1-66), mid (67-133), and lower \
(134-200), providing insights into how genres perform across the chart. \
Some genres show a strong preference for particular rank ranges. Classical \
music is heavily concentrated in the lower ranks, with 62.1% of its songs \
appearing between 134 and 200. The median rank is 148, with an interquartile \
range (IQR) of 113-175, indicating that most Classical songs struggle to reach \
higher chart positions, aside from a few outliers. In contrast, African Music \
is predominantly found in the upper ranks, with 50.2% of its songs appearing \
between 1 and 66. Its median rank is 66, with an IQR of 30-127, suggesting a \
clear tendency toward higher placements. Reggae and Christmas music also lean \
toward the upper ranks, with Reggae having 39.7% of its songs in this range and \
a median rank of 86. Christmas music follows a similar trend, with 43.9% in the \
upper ranks and a median of 78.
Other genres display a more balanced distribution but still show slight \
tendencies toward certain rank ranges. Blues, Country, and Folk are skewed \
toward the lower ranks, with median rankings of 120, 111, and 121, \
respectively. Rock also tends to perform weaker, with 40.7% of its songs \
ranking in the lower tier and a median of 117. Movie/Game Music is more \
centered around mid-ranks, with a median of 101 and an IQR of 64-149. Jazz has \
a broader spread but remains mostly in the mid and lower ranks, with only \
limited presence in the upper tier.
Some genres are more evenly distributed across all rank categories. \
Alternative/Indie, Asian Music, Chill, Electronic, Hip-Hop, Jazz, Latin Music, \
Metal, Pop, and R&B/Soul do not show strong dominance in any specific tier. \
However, there are slight tendencies; for example, Jazz leans slightly toward \
mid and lower ranks, while Latin Music has a mild preference for the upper \
ranks.
Overall, the data suggests that while certain genres, like Classical and \
African Music, are strongly concentrated in specific rank ranges, others \
maintain a more balanced distribution. Reggae, Christmas, and Latin Music tend \
to perform better in the upper ranks, while Blues, Country, and Rock struggle \
to break into the top tier. This distribution highlights how different genres \
perform on the charts and whether some have an advantage in reaching higher \
positions.
"""

# Read the data
data_path = Path(__file__).resolve().parents[2] / 'data' / 'final_data' / 'global_17-24_daily_with_exploded_genres.csv'
df = pd.read_csv(data_path)

# Ensure 'date' column is string
df['date'] = df['date'].astype(str)

# Extract available years and genres for dropdown menus
available_years = sorted(df['date'].str[:4].unique(), key=int)
available_genres = sorted(df['genres'].unique(), key=str)
available_genres.remove('Not Found')  # Remove Not Found

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
        title=f'Genre Distribution for {year} (%)',
        color='Genre',
        color_discrete_sequence=px.colors.qualitative.Set3  # Color scheme
    )

    # Improve readability and styling
    bar_fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",  # Fully transparent background
        plot_bgcolor="rgba(0,0,0,0)",   # Fully transparent plot area
        font=dict(color="white"),
        xaxis_title="Genre",
        yaxis_title="Percentage of Songs",
        xaxis=dict(tickangle=45)  # Rotate x-axis labels for better visibility
    )

    # Format y-axis to show percentage signs
    bar_fig.update_yaxes(ticksuffix="%")

    return bar_fig

# Function to generate line plot for genre evolution
def generate_line_plot(threshold=0.05):
    '''
    Generates a line plot showing the representation of all genre over the
    entire data. Underrepresented genres can be filtered a threshold.

    Arguments:
        threshold (float): The percentage threshold a genre has to pass to be
        included in the line plot. Default is 0.05 (so 5%)

    Returns:
        plotly.graph_objects.Figure: A line plot showing the genre
        representation accross the data.
    '''
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
    smoothed_genre_percentages = genre_percentages.rolling(window=3, 
                                                           min_periods=1).mean()

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
            line=dict(color=color_map[genre])  # Assign color to each genre
        ))

    # Customize layout
    line_fig.update_layout(
        height=800,
        title='Evolution of Genre Representation in Daily Global Chart Songs ' \
        '(2017-2024)',
        xaxis_title='Month',
        yaxis_title='Genre Representation (%)',
        xaxis=dict(tickmode='array', tickvals=x_tickvals, tickangle=45),
        legend_title='Genre',
        paper_bgcolor="rgba(0,0,0,0)",  # Fully transparent background
        plot_bgcolor="rgba(0,0,0,0)",   # Fully transparent plot area
        font=dict(color="white")
    )

    return line_fig

def generate_pie_chart(genre):
    '''
    Generates a pie chart showing the distribution of a selected genre across
    different rank ranges.

    Arguments:
        genre (str): The name of the genre to visualize.

    Returns:
        plotly.graph_objects.Figure: A pie chart showing the genre distribution
        across rank ranges.
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
        title=f'Distribution of Songs for Genre: {genre}',
        labels={'names': 'Rank Range', 'values': 'Number of Songs'},
        hole=0.3,  # Donut-style chart
        color_discrete_sequence=px.colors.qualitative.Pastel  # Soft color scheme
    )

    # Improve readability
    fig.update_traces(textposition='inside', textinfo='percent+label')

    # Dark mode styling
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",  # Fully transparent background
        plot_bgcolor="rgba(0,0,0,0)",   # Fully transparent plot area
        font=dict(color="white")
    )

    return fig

def generate_boxplot(genre):
    '''
    Generates a boxplot showing the distribution of a selected genre across
    different rank ranges.

    Arguments:
        genre (str): The name of the genre to visualize.

    Returns:
        plotly.express.Figure: A boxplot showing the genre distribution
        across rank ranges.
    '''
    # Filter data for the selected genre
    df_genre = df[df['genres'] == genre].copy()
    
    # Create a box plot
    rank_fig = px.box(
        df_genre,
        y='rank',
        title=f'Rank Distribution of {genre}',
        labels={'rank': 'Chart Rank'},
        color_discrete_sequence=px.colors.qualitative.Vivid
    )

    # Improve styling
    rank_fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",  # Fully transparent background
        plot_bgcolor="rgba(0,0,0,0)",   # Fully transparent plot area
        font=dict(color="white"),
        yaxis=dict(title="Rank (Lower is Better)", autorange="reversed")  # Flip y-axis (Rank 1 is better)
    )

    return rank_fig


# Generate initial plots
initial_year = 2017
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
        html.H2("Evolution of genres in daily global charts (2017-2024)")
    ], className='title'),

    # html.Div([
    #     html.Div([
    #         dcc.Graph(id='genre-trend-plot', figure=line_fig),
    #         html.Div("Your descriptive text for trend plot...", style=textstyle)
    #     ], className='container_genres'),

    #     html.Div([
    #         dcc.Graph(id='genre-bar-plot', figure=year_bar_fig),
    #         html.Div("Your descriptive text for bar plot...", style=textstyle)
    #     ], className='container_genres'),
    # ], className='grid-container'),

    html.Div([
        dcc.Graph(id='genre-trend-plot', figure=line_fig),
        html.Div(
            rq1_line_text,
        style=textstyle)
    ], className='container_genres'),

    html.Div([
        html.H2("Genre distribution over the years")
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
            "Er ist weder bearbeitbar noch kann seine Größe verändert werden."
            "Er ist weder bearbeitbar noch kann seine Größe verändert werden.",
            style=textstyle),
    ], className='container_genres'),

    html.Div([
        html.H2("Distribution of Songs by Genre")
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
            "Er ist weder bearbeitbar noch kann seine Größe verändert werden."
            "Er ist weder bearbeitbar noch kann seine Größe verändert werden.",
            style=textstyle),

        dcc.Graph(id='genre-box-plot', figure=rank_box_fig),
        html.Div(
            rq2_text,
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

# #Define callback to update line plot
# @app.callback(
#     Output('genre-trend-plot', 'figure'),
#     Input('threshold-slider', 'value')
# )
# def update_line_plot(threshold):
#     return generate_line_plot(threshold)

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

