# Imports
from pathlib import Path
from dash import html, dcc
import plotly.express as px
import pandas as pd

# Read the data
data_path = Path(__file__).resolve().parents[2] / 'data' / 'final_data' / 'all_regions_24.csv'
df = pd.read_csv(data_path)

# This data was manuelly added from https://en.wikipedia.org/wiki/List_of_countries_and_dependencies_by_population
population_data = {
    'Egypt': 105_914_499,
    'Finland': 5_638_675,
    'Germany': 83_555_478,
    'Japan': 123_440_000,
    'Ukraine': 32_962_000,
    'United Kingdom': 68_265_209,
    'United States': 340_110_988
}

df['population'] = df['country'].map(population_data)
df['streams_per_capita'] = df['streams'] / df['population']

data_path_happiness = Path(__file__).resolve().parents[2] / 'data' / 'final_data' / 'happiness.xlsx'
happy = pd.read_excel(data_path_happiness)

happy = happy[happy['Year'] == 2024]

grouped_by_country = df.groupby('country', as_index=False).agg({
    'streams': 'sum',
    'population': 'first',
})
grouped_by_country['streams_per_capita'] = grouped_by_country['streams'] / \
    grouped_by_country['population']

merged_df = grouped_by_country.merge(
    happy,
    left_on='country',
    right_on='Country name',
    how='inner'
)
merged_df.drop(columns=['Year', 'Rank', 'upperwhisker',
               'lowerwhisker'], inplace=True, errors='ignore')
merged_df.rename(columns=lambda col: col.replace(
    'Explained by: ', ''), inplace=True)

# Static choropleth: Happiness scores
choropleth_happy = px.choropleth(
    happy,
    locations='Country name',
    locationmode='country names',
    color='Ladder score',
    color_continuous_scale='Viridis',
    template='plotly_dark'
)
choropleth_happy.update_layout(
    geo=dict(showframe=False, showcoastlines=True),
    height=700
)

# Heatmap: Correlation of numerical columns
numeric_df = merged_df.select_dtypes(include='number')
corr = numeric_df.corr()

heatmap_happy = px.imshow(
    corr,
    text_auto=True,
    color_continuous_scale='Viridis',
    template='plotly_dark',
    height=700
)

# Animated choropleth: Streams per capital over time
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
    geo=dict(showframe=False, showcoastlines=True),
    height=700,
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
    }]
)

# Scatter Plot: Streams per capital vs ladder score
scatter_happy = px.scatter(
    merged_df,
    x='Ladder score',
    y='streams_per_capita',
    hover_name='country',
    template='plotly_dark',
    labels={
        'streams_per_capita': 'Streams per Capita',
        'Ladder score': 'Ladder Score'
    },
    color='country'
)
scatter_happy.update_traces(marker=dict(size=15))

# Style definiton for textstyle
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
        html.H2('How does the overall happiness score and music listening frequency on Spotify relate to each other?')
    ], className='question'),

    html.Div([
        html.H2('World Happiness Score (2024)')
    ], className='title'),

    html.Div([
        dcc.Graph(id='choropleth-happy', figure=choropleth_happy),
        html.Div(
            "Er ist weder bearbeitbar noch kann seine Größe verändert werden. "
            "Er ist weder bearbeitbar noch kann seine Größe verändert werden. "
            "Er ist weder bearbeitbar noch kann seine Größe verändert werden.",
            style=textstyle),
    ], className='container_happiness'),

    html.Div([
        html.H2('Heatmap Happiness and Charts')
    ], className='title'),

    html.Div([
        dcc.Graph(id='heatmap-happy', figure=heatmap_happy),
        html.Div(
            "Er ist weder bearbeitbar noch kann seine Größe verändert werden. "
            "Er ist weder bearbeitbar noch kann seine Größe verändert werden. "
            "Er ist weder bearbeitbar noch kann seine Größe verändert werden.",
            style=textstyle),
    ], className='container_happiness'),

    html.Div([
        html.H2('Daily spotify streams per capital by country (2024)')
    ], className='title'),

    html.Div([
        dcc.Graph(id='choropleth-time-happy', figure=choropleth_time_happy),
        html.Div(
            "Er ist weder bearbeitbar noch kann seine Größe verändert werden. "
            "Er ist weder bearbeitbar noch kann seine Größe verändert werden. "
            "Er ist weder bearbeitbar noch kann seine Größe verändert werden.",
            style=textstyle),
    ], className='container_happiness'),

    html.Div([
        html.H2('Streams per Capital vs. Ladder Score (with Regression Line????)')
    ], className='title'),

    html.Div([
        dcc.Graph(id='scatter-happy',figure=scatter_happy),
        html.Div(
            "Er ist weder bearbeitbar noch kann seine Größe verändert werden. "
            "Er ist weder bearbeitbar noch kann seine Größe verändert werden. "
            "Er ist weder bearbeitbar noch kann seine Größe verändert werden.",
            style=textstyle),
    ], className='container_happiness')

])
