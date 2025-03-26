from pathlib import Path
from dash import html, dcc
import plotly.express as px
import pandas as pd

# Look at the EDA_happiness_score.ipynb for more detailed documentation
data_path = Path(__file__).resolve(
).parents[2] / 'data' / 'final_data' / 'all_regions_24.csv'
df = pd.read_csv(data_path)

# This data was manuelly added from https://en.wikipedia.org/wiki/List_of_countries_and_dependencies_by_population
population_data = {
    'Australia': 27_100_000,
    'Spain': 47_890_000,
    'Brazil': 212_812_000,
    'Sweden': 10_500_000,
    'South Africa': 64_747_000,
    'Nigeria': 237_528_000,
    'Greece': 10_300_000,
    'India': 1_454_606_724,
    'Egypt': 105_914_499,
    'Finland': 5_638_675,
    'Germany': 83_555_478,
    'Japan': 123_440_000,
    'Ukraine': 32_962_000,
    'United Kingdom': 68_265_209,
    'United States': 340_110_988
}

# Per capita
df['population'] = df['country'].map(population_data)
df['streams_per_capita'] = df['streams'] / df['population']

# Read happiness data
data_path_happiness = Path(__file__).resolve(
).parents[2] / 'data' / 'final_data' / 'happiness.xlsx'
happy = pd.read_excel(data_path_happiness)

happy = happy[happy['Year'] == 2024]
happy.rename(columns={'Ladder score': 'happiness'}, inplace=True)

# Get per capita streams for each country
grouped_by_country = df.groupby('country', as_index=False).agg({
    'streams': 'sum',
    'population': 'first',
})
grouped_by_country['streams_per_capita'] = grouped_by_country['streams'] / \
    grouped_by_country['population']

# Merge dfs
merged_df = grouped_by_country.merge(
    happy,
    left_on='country',
    right_on='Country name',
    how='inner'
)
# Drop for heatmap later on
merged_df.drop(columns=['Year', 'Rank', 'upperwhisker',
               'lowerwhisker'], inplace=True, errors='ignore')
merged_df.rename(columns=lambda col: col.replace(
    'Explained by: ', ''), inplace=True)

# Static choropleth: Happiness scores
choropleth_happy = px.choropleth(
    happy,
    locations='Country name',
    locationmode='country names',
    color='happiness',
    color_continuous_scale='Viridis'
)

choropleth_happy.update_layout(
    geo=dict(
        showframe=False,
        showcoastlines=True,
        bgcolor="rgba(20,20,20,0.5)"),
    template='plotly_dark',
    height=800,
    paper_bgcolor="rgba(0,0,0,0)"
)

# Heatmap: Correlation of numerical columns
numeric_df = merged_df.select_dtypes(include='number')
corr = numeric_df.corr().round(2)

heatmap_happy = px.imshow(
    corr,
    text_auto=True,
    color_continuous_scale='Viridis',
    template='plotly_dark',
    height=700
)
heatmap_happy.update_layout(
    paper_bgcolor="rgba(20,20,20,0.5)",
    plot_bgcolor="rgba(20,20,20,0.5)"
)

df = df.groupby(
    [df['date'], 'country']
).agg({
    'streams_per_capita': 'sum'
}).reset_index()

# Animated choropleth: Streams per capita over time
choropleth_time_happy = px.choropleth(
    df,
    locations='country',
    locationmode='country names',
    color='streams_per_capita',
    animation_frame=df['date'].astype(str),
    color_continuous_scale='Viridis',
    template='plotly_dark',
    range_color=(0, df['streams_per_capita'].max())
)
choropleth_time_happy.update_layout(
    geo=dict(showframe=False,
            showcoastlines=True,
            bgcolor="rgba(20,20,20,0.5)"),
    height=800,
    margin=dict(l=0, r=0, t=50, b=0),
    updatemenus=[{
        'type': 'buttons',
        'showactive': False,
        'buttons': [{
            'label': 'Play',
            'method': 'animate',
            'args': [None, {
                'frame': {'duration': 20, 'redraw': True},
                'transition': {'duration': 50},
                'fromcurrent': True,
                'mode': 'immediate'
            }]
        }, {
            'label': 'Pause',
            'method': 'animate',
            'args': [[None], {'mode': 'immediate'}]
        }]
    }],
    paper_bgcolor="rgba(0,0,0,0)"
)

# Scatter Plot: Streams per  vs ladder score
scatter_happy = px.scatter(
    merged_df,
    x='happiness',
    y='streams_per_capita',
    hover_name='country',
    template='plotly_dark',
    labels={
        'streams_per_capita': 'Streams per Capita',
        'hapiness': 'Happiness Score'
    },
    color='country'
)

scatter_happy.update_layout(
    paper_bgcolor="rgba(20,20,20,0.5)",
    plot_bgcolor="rgba(20,20,20,0.5)"
)

scatter_happy.update_traces(marker=dict(size=15))

# Style definiton for textstyle
textstyle = {
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
        html.H2('How does the overall happiness score and music listening frequency on Spotify relate to each other?')
    ], className='question'),

    html.Div([
        html.H2('World Happiness Score (2024)')
    ], className='title'),

    html.Div([
        dcc.Graph(id='choropleth-happy', figure=choropleth_happy),
        html.Div(
            "This choropleth world map shows the happiness scores of most countries in the world.",
            style=textstyle),
    ], className='container_happiness'),

    html.Div([
        html.H2('Heatmap Happiness and Charts')
    ], className='title'),

    html.Div([
        dcc.Graph(id='heatmap-happy', figure=heatmap_happy),
        html.Div(
            "This heatmap shows the correlation between streamed music and happiness scores across 15 countries.\n"
            "Particularly interesting is the strong correlation of 0.8 between streams per capita and happiness.\n"
            "Log GDP: The GDP of a country on a logarithmic scale\n"
            "Social support: If you were in trouble, do you have relatives or friends you can count on to help you whenever you need them?\n"
            "Generosity: Have you donated money to a charity in the past month?\n"
            "Dystopia/Residual: Baseline score plus other unmeasured or unexplained factors",
            style=textstyle),
    ], className='container_happiness'),

    html.Div([
        html.H2('Daily Spotify Streams per Capita by Country (2024)')
    ], className='title'),

    html.Div([
        dcc.Graph(id='choropleth-time-happy', figure=choropleth_time_happy),
        html.Div(
            "This choropleth world map shows the Spotify streams per capita on a daily basis of the year 2024."
            "It shows a similarity to the happiness world map but there are outliers like Greece or the US.",
            style=textstyle),
    ], className='container_happiness'),

    html.Div([
        html.H2('Streams per Capita vs. Happiness Score')
    ], className='title'),

    html.Div([
        dcc.Graph(id='scatter-happy', figure=scatter_happy),
        html.Div(
            "This Scatter plot shows a clear correlation between happiness and streams per capita. Obviously this data did not account for smartphone access or diffrent streaming services.",
            style=textstyle),
    ], className='container_happiness')

])
