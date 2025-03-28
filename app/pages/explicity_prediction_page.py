# Imports
import io
import base64
from pathlib import Path
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import plotly.subplots as sp
import pandas as pd
from wordcloud import WordCloud
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from app.app import app

# Function for model prediction
def model_prediction(text, model, num_labels=2):
    # Load tokenizer and model from directory
    tokenizer = AutoTokenizer.from_pretrained(model)
    model = AutoModelForSequenceClassification.from_pretrained(model, num_labels=num_labels)

    # Tokenize the input lyrics
    inputs = tokenizer(text, padding='max_length', truncation=True, return_tensors='pt')

    # Prediction
    outputs = model(**inputs)
    predictions = outputs.logits.argmax(dim=-1)

    # Result
    return 'Explicit' if predictions.item() == 1 else 'Not Explicit'

# Read the data
data_path = Path(__file__).resolve().parents[2] / 'data' / 'final_data' / 'all_locations_with_polarity_and_spotify_without_duplicates.csv'
df = pd.read_csv(data_path)

#Wordcloud visualisation (Subplot is from ChatGPT)
explicit_lyrics = ' '.join(df[df['explicit']]['lyrics'])
non_explicit_lyrics = ' '.join(df[~df['explicit']]['lyrics'])

# Convert to base64
def wordcloud_to_base64(wordcloud):
    buffer = io.BytesIO()
    wordcloud.to_image().save(buffer, format="PNG")
    buffer.seek(0)
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"

# Generate wordcloud
wordcloud_explicit = WordCloud(width=1000, height=1000, colormap='Spectral').generate(explicit_lyrics)
wordcloud_non_explicit = WordCloud(width=1000, height=1000, colormap='Spectral').generate(non_explicit_lyrics)

# Convert to base 64
explicit_base64 = wordcloud_to_base64(wordcloud_explicit)
non_explicit_base64 = wordcloud_to_base64(wordcloud_non_explicit)

# Create subplot
fig_wordcloud = sp.make_subplots(rows=1, cols=2)

# Add wordcloud as a picture
fig_wordcloud.add_trace(go.Image(source=explicit_base64), row=1, col=1)
fig_wordcloud.add_trace(go.Image(source=non_explicit_base64), row=1, col=2)
fig_wordcloud.update_layout(
    template='plotly_dark',
    showlegend=False,
    margin=dict(l=20, r=20, t=0, b=0),
    paper_bgcolor="rgba(20,20,20,0.5)",
    plot_bgcolor="rgba(20,20,20,0.5)",
    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    xaxis2=dict(showgrid=False, zeroline=False, showticklabels=False),
    yaxis2=dict(showgrid=False, zeroline=False, showticklabels=False))

# Distribution chart
# Rename the label to real name and not binary values
df['explicit_label'] = df['explicit'].replace({True: 'Explicit', False: 'Not Explicit'})

# Calculate the distribution of explicit and not explicit lyrics
distribution = df['explicit_label'].value_counts().reset_index()
distribution.columns = ['Explicit', 'Count']
distribution['Percentage'] = (distribution['Count'] / distribution['Count'].sum()) * 100

# Visualise as a bar chart
fig = px.bar(distribution, x='Explicit', y='Count', 
             labels={'Explicit': 'Explicit/Not Explicit', 'Count': 'Count'}
)

# Set the colors for "Explicit" and "Not Explicit"
fig.update_traces(
    text=distribution['Percentage'].round(2).astype(str) + '%',
    textposition='inside',
    marker=dict(color=distribution['Explicit'].map({'Explicit': 'red', 'Not Explicit': 'green'}))
)

# Adjust the layout
fig.update_layout(
    template='plotly_dark',
    xaxis_title_font=dict(family='Arial', weight='bold'),
    yaxis_title_font=dict(family='Arial', weight='bold'),
    paper_bgcolor="rgba(20,20,20,0.5)",
    plot_bgcolor="rgba(20,20,20,0.5)"
)

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

# Layout for Sections
layout = html.Div([

    html.Div([
        html.H2('How well can a pretrained roberta model predict the explicity label of a songs lyrics?')
    ], className='question'),

    html.Div([
        html.H2('Wordcloud for Song Lyrics (Explicit and Not Explicit) among all locations (Global, Usa, Uk).')
    ], className='title'),

    # Div: Wordcloud visualisation wirh description
    html.Div([
        dcc.Graph(figure=fig_wordcloud),
        html.Div(
            "To give you an insight on the words included in explicit and not explicit songs, you can check out the wordcloud from above.",
            style=textstyle),
    ], className='container_explicity'),

    html.Div([
        html.H2('Distribution of Class Labels among all Charts Data')
    ], className='title'),

    # Div: Visualisation of the label distribution with description
    html.Div([
        dcc.Graph(figure=fig),
        html.Div(
            "This plot shows the distribution of the explicit labels among all locations (Global, Usa, Uk)."
            "Global and Uk both have quite balanced labels, but the Usa stands out with 5870 to 4100 labels "
            "marked as explicit and not explicit.",
            style=textstyle),
    ], className='container_explicity'),

    html.Div([
        html.H2('Explicity Prediction')
    ], className='title'),
    
    # Div: Textarea for lyrics input and prediction output field
    html.Div([

            dcc.Textarea(id='lyrics-input', placeholder='Enter your lyrics here...', style={'width': '100%', 'height': 200}),
            html.Div(id='prediction-output', style={'marginTop': '20px'}),
    ], className='container_explicity')

])

# Callback for changes in the text field
@app.callback(
    Output('prediction-output', 'children'),
    [Input('lyrics-input', 'value')]
)
def update_prediction(lyrics):
    if lyrics:
        model = Path(__file__).resolve().parents[2] / 'data' / 'trained_model_explicity'
        prediction = model_prediction(lyrics, model)
        return f'The song is probably: {prediction}'
    return 'Please enter some lyrics first.'
