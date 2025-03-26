from pathlib import Path
from dash import html, dcc, Input, Output
import plotly.express as px
import pandas as pd
from app.app import app

data_path = Path(__file__).resolve().parents[2] / 'data' / 'final_data' / 'global_17-24_with_spotifyextras.csv'
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
                        autosize=False,
                        width=900,
                        height=400,)

# Style definition for textstyle
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
            html.H2("How do collaborations of music artists influence the success of their songs in comparison to solo songs on Spotify?")
        ], className='question'),

        html.Div([
            html.H2("Network of all artists who collaborated")
        ], className='title'),

        html.Div([
            html.Iframe(src="/assets/artist_collab_network.html", width="100%", height="800px"),
            html.Div(
                "Er ist weder bearbeitbar noch kann seine Größe verändert werden. "
                "Er ist weder bearbeitbar noch kann seine Größe verändert werden. "
                "Er ist weder bearbeitbar noch kann seine Größe verändert werden.",
                style=textstyle)
        ], className='container_colab'),

        html.Div([
            html.H2("Distribution of collborations in the charts")
        ], className='title'),

        html.Div([
            dcc.Graph(figure=pie_colab),
            html.Div(
                "Er ist weder bearbeitbar noch kann seine Größe verändert werden. "
                "Er ist weder bearbeitbar noch kann seine Größe verändert werden. "
                "Er ist weder bearbeitbar noch kann seine Größe verändert werden.",
                style=textstyle)
        ], className='container_colab_pie'),

        html.Div([
            html.H2("Medium total streams by collaborations status")
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
                style = {
                    'backgroundColor': 'white',
                    'color': 'black',
                    'font-size': '18px',
                    'border-radius': '5px',
                    'font-weight': 'bold'}),
            dcc.Graph(id='bar_colab'),
            html.Div(
                "Er ist weder bearbeitbar noch kann seine Größe verändert werden. "
                "Er ist weder bearbeitbar noch kann seine Größe verändert werden. "
                "Er ist weder bearbeitbar noch kann seine Größe verändert werden.",
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
        xaxis_title="Collaboration",
        yaxis_title=metric_label[selected_metric],
        template="plotly_dark"
    )

    return fig