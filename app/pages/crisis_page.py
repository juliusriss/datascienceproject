# Imports
from pathlib import Path
import pandas as pd
import plotly.express as px
import dash
from dash import html, dcc, Input, Output
from app.app import app

# Load the Spotify data
data_path = Path(__file__).resolve(
).parents[2] / 'data' / 'final_data' / 'global_17-24_daily.csv'
df = pd.read_csv(data_path)

# Process date info
df['date'] = pd.to_datetime(df['date'])
df_grouped = df.groupby('date')['streams'].sum().reset_index()
df_grouped['month'] = df_grouped['date'].dt.month
df_grouped['month_name'] = df_grouped['date'].dt.strftime('%B')
df_grouped['weekday'] = df_grouped['date'].dt.weekday
df_grouped['weekday_name'] = df_grouped['date'].dt.strftime('%A')

# Load the covid data
data_path = Path(__file__).resolve(
).parents[2] / 'data' / 'final_data' / 'covid.csv'
covid = pd.read_csv(data_path)

covid['Date_reported'] = pd.to_datetime(covid['Date_reported'])
covid_grouped = covid.groupby('Date_reported')['New_cases'].sum().reset_index()

# Merge data
merged_df = pd.merge(covid_grouped, df_grouped,
                     left_on='Date_reported', right_on='date', how='inner')
bin_edges = [-1e11, 1000, 5000, 10000, 50000, 100000, 500000, float('inf')]
bin_labels = ['0-1000', '1000-5000', '5000-10000',
              '10000-50000', '50000-100000', '100000-500000', '500000+']
merged_df['New_cases_binned'] = pd.cut(
    merged_df['New_cases'], bins=bin_edges, labels=bin_labels)

# Bar chart: Median daily streams per weekday
df_weekday = merged_df.groupby(['weekday', 'weekday_name'])[
    'streams'].median().reset_index()
df_weekday = df_weekday.sort_values(by='weekday')

bar_covid_week = px.bar(
    df_weekday,
    x='weekday_name',
    y='streams',
    labels={'weekday_name': 'Weekday', 'streams': 'Median Streams'},
    text_auto=True,
    color='weekday_name',
    color_discrete_sequence=px.colors.qualitative.Vivid
)
bar_covid_week.update_layout(
    template='plotly_dark',
    xaxis_title='Day of the Week',
    yaxis_title='Total Streams',
    showlegend=False,
    xaxis_title_font=dict(family='Arial', weight='bold'),
    yaxis_title_font=dict(family='Arial', weight='bold'),
    paper_bgcolor="rgba(20,20,20,0.5)",
    plot_bgcolor="rgba(20,20,20,0.5)"
)

# Bar chart: Median daily streams per month
df_month = merged_df.groupby(['month', 'month_name'])[
    'streams'].median().reset_index()
df_month = df_month.sort_values(by='month')

bar_covid_month = px.bar(
    df_month,
    x='month_name',
    y='streams',
    labels={'month_name': 'Month', 'streams': 'Median Streams'},
    text_auto=True,
    color='month_name',
    color_discrete_sequence=px.colors.qualitative.Vivid
)
bar_covid_month.update_layout(
    template='plotly_dark',
    xaxis_title='Month',
    yaxis_title='Total Streams',
    showlegend=False,
    xaxis_title_font=dict(family='Arial', weight='bold'),
    yaxis_title_font=dict(family='Arial', weight='bold'),
    paper_bgcolor="rgba(20,20,20,0.5)",
    plot_bgcolor="rgba(20,20,20,0.5)"
)

# Box plot: Streams distribution based on COVID-19 case intervals
boxplot_covid = px.box(
    merged_df,
    x='New_cases_binned',
    y='streams',
    labels={'New_cases_binned': 'Intervalls of COVID-19 Cases',
            'streams': 'Streams'},
    color='New_cases_binned',
    color_discrete_sequence=px.colors.qualitative.Vivid,
    category_orders={'New_cases_binned': bin_labels}
)
boxplot_covid.update_layout(
    xaxis_tickangle=-45,
    template='plotly_dark',
    xaxis_title_font=dict(family='Arial', weight='bold'),
    yaxis_title_font=dict(family='Arial', weight='bold'),
    paper_bgcolor="rgba(20,20,20,0.5)",
    plot_bgcolor="rgba(20,20,20,0.5)"
)

# Scatter plot: Weekly average streams vs COVID cases
merged_df['streams_7day_avg'] = merged_df['streams'].rolling(window=7).mean()
merged_df['Week'] = merged_df['Date_reported'].dt.to_period('W').dt.start_time
merged_df = merged_df[merged_df['New_cases'] >= 0]
merged_df['size_scaled'] = merged_df['New_cases'] + 500000

scatter_covid = px.scatter(
    merged_df,
    x='Week',
    y='streams_7day_avg',
    size='size_scaled',
    color='New_cases',
    labels={
        'streams_7day_avg': 'Weekly Average of Streams',
        'Week': 'Week',
        'New_cases': 'COVID Cases'
    },
    color_continuous_scale=px.colors.sequential.YlOrRd
)
scatter_covid.update_layout(
    template='plotly_dark',
    xaxis_title='Week',
    yaxis_title='Weekly Average of Streams',
    legend_title='COVID cases',
    coloraxis=dict(cmin=0, cmax=500000),
    xaxis_title_font=dict(family='Arial', weight='bold'),
    yaxis_title_font=dict(family='Arial', weight='bold'),
    paper_bgcolor="rgba(20,20,20,0.5)",
    plot_bgcolor="rgba(20,20,20,0.5)"
)

# Style definition for textstyle
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
        html.H2("How did the corona crisis effect global listening trends on Spotify?")
    ], className='question'),

    html.Div([
        html.H2("Median Daily Streams per Weekday/Month")
    ], className='title'),

    html.Div([
        dcc.Dropdown(
            id='timeframe-dropdown',
            options=[
                {'label': 'Weekly', 'value': 'weekly'},
                {'label': 'Monthly', 'value': 'monthly'}],
            value='weekly',
            style={
                'backgroundColor': 'white',
                'color': 'black',
                'font-size': '18px',
                'border-radius': '5px',
                'font-weight': 'bold'}),
        dcc.Graph(id='streams-graph'),
        html.Div(
            "Before diving into the impact of COVID on globally streamed songs, we first explore general listening trends by day and month."
            "Sundays and December stand out as outliers especially December 24/25th, as we’ll see in the COVID scatterplot below.",
            style=textstyle)
    ], className='container_covid'),

    html.Div([
        html.H2("Streams Distribution based on Covid-19 Case Intervalls")
    ], className='title'),

    html.Div([
        dcc.Graph(figure=boxplot_covid),
        html.Div(
            "This boxplot clearly shows a slight negative correlation between COVID-19 cases and the number of songs listened to.",
            style=textstyle)
    ], className='container_covid'),

    html.Div([
        html.H2("Streams with Weekly Streams and Covid-19 cases")
    ], className='title'),

    html.Div([
        dcc.Graph(figure=scatter_covid),
        html.Div(
            "The time series data illustrates this even more clearly, showing a slight decline in listening activity during periods with high COVID-19 case numbers - especially noticeable in early 2022."
            "It’s also worth noting that December is a major outlier, which helps explain the unusual data points seen in December 2023.",
            style=textstyle)
    ], className='container_covid')

])

# Callback to update the weekday/month graph


@app.callback(
    Output('streams-graph', 'figure'),
    Input('timeframe-dropdown', 'value')
)
def update_graph(selected_timeframe):
    if selected_timeframe == 'weekly':
        return bar_covid_week
    else:
        return bar_covid_month
