from dash import html

# Cards
cards = [
    {"title": "Genres", "img": "/assets/genres.png", "link": "/genres"},
    {"title": "Polarity", "img": "/assets/polarity.png", "link": "/polarity"},
    {"title": "Solo artists vs. Collaborations", "img": "/assets/solo_collab.png", "link": "/solo_collab"},
    {"title": "Time between Release and Charting", "img": "/assets/release_time.png", "link": "/release_time"},
    {"title": "Influence of Corona Crisis", "img": "/assets/corona_crisis.png", "link": "/crisis"},
    {"title": "Happiness Score", "img": "/assets/happiness_score.png", "link": "/happiness_score"},
    {"title": "Predict the Explicity", "img": "/assets/explicity_prediction.png", "link": "/explicity_prediction"},
    {"title": "Checkout your Spotify Statistics", "img": "/assets/spotify_stats.png", "link": "/spotify_stats"},
]

# Layout with cards for content and imprint
layout = html.Div([
    html.Div([
        html.A(
            html.Div([
                html.Img(src=card["img"], className="card-img"),
                html.Div([
                    html.H3(card["title"], className="card-title"),
                ], className="card-content"),
            ], className="card"),
            href=card["link"],
            className="card-link",
        )
        for card in cards
    ], className="grid-container"),

    html.Div([
        html.P("Imprint", className="footer-title"),
        html.P("This Website was created by Julius, Milan, and Navid (Group MJN) as part of the Data Science Project (CAU Kiel)"),
        html.P("The logos for the topics were created with ChatGPT.")
    ], className="footer")
])