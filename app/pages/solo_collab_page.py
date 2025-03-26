from pathlib import Path
from dash import html, dcc, Input, Output
import plotly.express as px
import pandas as pd
from app.app import app

data_path = Path(__file__).resolve(
).parents[2] / 'data' / 'final_data' / 'global_17-24_with_spotifyextras.csv'
df = pd.read_csv(data_path)

colab_counts = df['is_colab'].value_counts().reset_index()
colab_counts.columns = ['is_colab', 'count']

pie_colab = px.pie(
    colab_counts,
    names='is_colab',
    values='count',
    color_discrete_sequence=px.colors.qualitative.Vivid
)

pie_colab.update_traces(textinfo='percent+label')

pie_colab.update_layout(template="plotly_dark",
                        showlegend=False,
                        autosize=False,
                        width=900,
                        height=400,
                        yaxis_title_font=dict(family='Arial', weight='bold'),
                        paper_bgcolor="rgba(20,20,20,0.5)",
                        plot_bgcolor="rgba(20,20,20,0.5)"
)

label_map = {True: 'Collab', False: 'Solo'}

pie_colab.data[0].labels = [label_map.get(
    v, str(v)) for v in pie_colab.data[0].labels]

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
        html.H2("How do collaborations of music artists influence the success of their songs in comparison to solo songs on Spotify?")
    ], className='question'),

    html.Div([
        html.H2("Network of all artists who collaborated")
    ], className='title'),

    html.Div([
        html.Iframe(src="/assets/artist_collab_network.html",
                        width="100%", height="800px"),
        html.Div(
            "This Network shows every artist and the colabs he had over the last years the size is scaling with the amount of collabaration he has.",
            style=textstyle)
    ], className='container_colab'),

    html.Div([
        html.H2("Distribution of Collborations in the Charts")
    ], className='title'),

    html.Div([
        dcc.Graph(figure=pie_colab),
        html.Div(
            "The Pie chart shows that there are slighly more single artists songs in the charts than there are collabs but do they perform equally? \n \n"
            "Max Days on Chart: The total number of days a song stayed in the charts.\n"
            "Total Streams: The total number of streams a song accumulated while in the charts.\n"
            "Rank: The highest chart position a song reached (lower = better).",
            style=textstyle)
    ], className='container_colab_pie'),

    html.Div([
        html.H2("Medium Total Streams by Collaboration Status")
    ], className='title'),

    html.Div([
        dcc.Dropdown(
            id='metric-dropdown',
            options=[
                {'label': 'Median Total Streams', 'value': 'total_streams'},
                {'label': 'Max Days on Chart', 'value': 'max_days_on_chart'},
                {'label': 'Min Peak Rank', 'value': 'min_peak_rank'}],
            value='total_streams',
            clearable=False,
            style={
                'backgroundColor': 'white',
                'color': 'black',
                'font-size': '18px',
                'border-radius': '5px',
                'font-weight': 'bold'}),
        dcc.Graph(id='bar_colab'),
        html.Div(
            "There appears to be a slight advantage for collaborations across the three attributes we examined.",
            style=textstyle)
    ], className='container_colab')

])


@app.callback(
    Output('bar_colab', 'figure'),
    [Input('metric-dropdown', 'value')]
)
def update_bar_chart(selected_metric):
    metric_label = {
        'total_streams': 'Median Total Streams',
        'max_days_on_chart': 'Median Max Days on Chart',
        'min_peak_rank': 'Median Min Peak Rank'
    }

    grouped_data = df.groupby('is_colab')[
        selected_metric].median().reset_index()

    fig = px.bar(
        grouped_data,
        x='is_colab',
        y=selected_metric,
        labels={'is_colab': 'Collaboration',
                selected_metric: metric_label[selected_metric]},
        color='is_colab',
        color_discrete_sequence=px.colors.qualitative.Vivid
    )

    fig.update_layout(
        showlegend=False,
        xaxis_title="Collaboration",
        yaxis_title=metric_label[selected_metric],
        template="plotly_dark",
        xaxis=dict(
            title="Collaboration",
            tickmode='array',
            tickvals=[False, True],
            ticktext=['Solo', 'Collab']),
        yaxis_title_font=dict(family='Arial', weight='bold'),
        paper_bgcolor="rgba(20,20,20,0.5)",
        plot_bgcolor="rgba(20,20,20,0.5)"
    )

    return fig
