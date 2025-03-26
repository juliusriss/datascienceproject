# data-science-project - Spotify Charts - Group MJN

# Introduction
Spotify is a constant companion in most of your pockets. But what kind of data is behind the streaming platform and which data features are worth further investigation? 

# Research questions
1. How did the diversity of listened music genres evolve on Spotify since 2017 and are there genres dominating some rank ranges?
2. What is the contribution of positive and negative words (polarity) in english-language songs at different locations and how does different artists differ on Spotify since 2017?
3. How do collaborations of music artists influence the success of their songs in comparison to solo songs on Spotify?
4. How long does it take for a song to enter the charts after its release and is there a connection to the length of time the song is in the charts on Spotify?
5. How does the overall happiness score and music listening frequency on Spotify relate to each other? (Milan)
6. How did Crisis effect global listening trends on Spotify? (Milan)
7. How good can deep learning predict the explicity label of a song's lyrics?
8. How does a user's music taste change over a year in terms of how many of a specific user's favorite songs can be found in the charts and is there a connection to the release dates of listened songs?

# Data and data pipeline
The project is based on Spotify charts data from 2017 to 2024. This data was automatically downloaded for several countries and cleaned, because songs normally dont only stay one day in the charts, the combined daily data per region always included many duplicates, which were removed due to cleaning the data. In addition, different sources and API´s were used to fetch additional data (Spotify API (add_lyrics.ipynb), Genius API & Last.fm API (find_genre.ipynb), Wikipedia population data, Covid Crisis data) and were also cleaned.

Polarity: The lyrics had to be added and then cleaned (clean_lyrics.ipynb) in terms of removing unnessacary white space, because the format provided by the Genius API was not very structured.In addition they had to be filtered for english language (also clean_lyrics.piynb), because it was not possible to translate so many lyrics without reaching the requesting limit by far. Besides that, some songs didnt get the right lyrics and had to be removed. After that is was possible to get the polarity for english language songs.

Genres: Because there was no source for genres per song, the genres had to be collected via the artist and the album. It was not possible to get a genre for every song so these also had to be removed. In the next step, all data could be used for further analysis. The final data can be found in the final_data folder. The folder includes all data, which is used on one or more pages of the dash app.

# Progress of building the website
The website is divided into multiple pages to have a clear overview over all topics, which are based on the research questions. Every page has its own visualisations with interactive parts (some more or less) and also some interesting play arounds to get great insights into the data. Every page has one or two data files to read for the visualisations.

# How to start the website
1. Install all modules from the requirements.txt (requirements.txt is placed in the app folder)
2. Open a new terminal
3. Run the following command in your terminal: gunicorn app.index:server
4. Access the website (mostly: http://127.0.0.1:8000, but exact ip should be shown in your terminal)
5. kill <pid> to shut down the website before starting it again, else: choose a different port (e.g. 8001)