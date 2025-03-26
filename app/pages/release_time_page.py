# Imports
from pathlib import Path
from dash import html, dcc, Input, Output
import plotly.express as px
import pandas as pd
from app.app import app

# Read the data
data_path = Path(__file__).resolve().parents[2] / 'data' / 'final_data' / 'global_17-24_with_spotifyextras.csv'
df = pd.read_csv(data_path)

# Pie Chart
bin_counts = df['relase-chart_days_bins'].value_counts().reindex(
    ['0 days', '<1 week', '1-2 weeks', '2-3 weeks', '3-4 weeks', '4+ weeks']
)

pie_release = px.pie(
    names=bin_counts.index,
    values=bin_counts.values,
    color=bin_counts.index,
    color_discrete_sequence=px.colors.qualitative.Vivid)

pie_release.update_layout(height=500)
pie_release.update_traces(textinfo='percent+label')
pie_release.update_layout(template="plotly_dark")

# Bar chart
mean_values = df.groupby('relase-chart_days_bins')[
    ['max_days_on_chart', 'total_streams', 'min_peak_rank']
].mean().reindex(['0 days', '<1 week', '1-2 weeks', '2-3 weeks', '3-4 weeks', '4+ weeks'])

overall_means = df[['max_days_on_chart',
                    'total_streams', 'min_peak_rank']].mean()

bar_release = px.bar(
    x=mean_values.index,
    y=mean_values['max_days_on_chart'],
    text=mean_values['max_days_on_chart'].round(1),
    labels={'x': 'Time Baskets', 'y': 'Average Max Days on Chart'},
    color=mean_values.index,
    color_discrete_sequence=px.colors.qualitative.Vivid
)

bar_release.add_hline(
    y=overall_means['max_days_on_chart'],
    line_dash="dash",
    line_color="red",
    annotation_text=f"Overall Mean: {overall_means['max_days_on_chart']:.1f}",
    annotation_position="top left"
)

bar_release.update_traces(textposition='outside')
bar_release.update_layout(
    xaxis_title="Time Baskets",
    yaxis_title="Average Max Days on Chart",
    template="plotly_dark"
)

# Violin chart
violin_release = px.violin(
    df,
    x='relase-chart_days_bins',
    y='max_days_on_chart',
    box=True,
    points='all',
    color='relase-chart_days_bins',
    color_discrete_sequence=px.colors.qualitative.Vivid
)

overall_median = df['max_days_on_chart'].median()
violin_release.add_hline(
    y=overall_median,
    line_dash="dash",
    line_color="red",
    annotation_text=f"Overall Median: {overall_median:.1f}",
    annotation_position="top left"
)

violin_release.update_layout(
    xaxis_title="Time Baskets",
    yaxis_title="Max Days on Chart",
    yaxis=dict(range=[0, 200]),
    template="plotly_dark",
)

# Style definition for text style
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
        html.H2("How long does it take for a song to enter the charts after its release and is there a connection to the length of time the song is in the charts on Spotify?")
    ], className='question'),

    html.Div([
        html.H2("Time between release and entering the charts")
    ], className='title'),

    html.Div([
        dcc.Graph(figure=pie_release),
        html.Div(
            "Er ist weder bearbeitbar noch kann seine Größe verändert werden. "
            "Er ist weder bearbeitbar noch kann seine Größe verändert werden. "
            "Er ist weder bearbeitbar noch kann seine Größe verändert werden.",
            style=textstyle)
    ],className='container_release_pie'),

    html.Div([
        html.H2("Max days in charts, total streams of charted songs per time interval and minimum peak rank in charts per time interval")
    ], className='title'),

    # Div: Dropdown with bar chart and description
    html.Div([
        dcc.Dropdown(
            id='metric-dropdown',
            options=[
                {'label': 'Max days in charts', 'value': 'max_days_on_chart'},
                {'label': 'Total streams of charted songs per time interval', 'value': 'total_streams'},
                {'label': 'Minimum rank in charts per time interval', 'value': 'min_peak_rank'},],
            value='min_peak_rank',
            style = {
                'backgroundColor': 'white',
                'color': 'black',
                'font-size': '18px',
                'border-radius': '5px',
                'font-weight': 'bold'}),
        dcc.Graph(id='bar-release', figure=bar_release),
        html.Div(
            "Er ist weder bearbeitbar noch kann seine Größe verändert werden."
            "Er ist weder bearbeitbar noch kann seine Größe verändert werden."
            "Er ist weder bearbeitbar noch kann seine Größe verändert werden.",
            style=textstyle)
    ], className='container_release'),

    html.Div([
        html.H2("Distribution of max days in charts")
    ], className='title'),

    # Div: Violin Chart with description
    html.Div([
        dcc.Graph(figure=violin_release),
        html.Div(
            "Er ist weder bearbeitbar noch kann seine Größe verändert werden. "
            "Er ist weder bearbeitbar noch kann seine Größe verändert werden. "
            "Er ist weder bearbeitbar noch kann seine Größe verändert werden.",
            style=textstyle)
    ], className='container_release'),

])

# Callback to update the bar chart
@app.callback(
    Output('bar-release', 'figure'),
    [Input('metric-dropdown', 'value')]
)
def update_bar_release(selected_metric):
    updated_bar_release = px.bar(
        x=mean_values.index,
        y=mean_values[selected_metric],
        text=mean_values[selected_metric].round(1),
        labels={'x': 'Time Baskets',
                'y': f'Average {selected_metric.replace("_", " ").title()}'},
        color=mean_values.index,
        color_discrete_sequence=px.colors.qualitative.Vivid
    )

    updated_bar_release.add_hline(
        y=overall_means[selected_metric],
        line_dash="dash",
        line_color="red",
        annotation_text=f"Overall Mean: {overall_means[selected_metric]:.1f}",
        annotation_position="top left"
    )

    updated_bar_release.update_traces(textposition='outside')
    updated_bar_release.update_layout(
        xaxis_title="Time Baskets",
        yaxis_title=f"Average {selected_metric.replace('_', ' ').title()}",
        template="plotly_dark"
    )

    return updated_bar_release
