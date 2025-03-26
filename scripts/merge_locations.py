import pandas as pd

# CSV-Dateien einlesen
df_global = pd.read_csv('/Users/juliusriss/Desktop/data-science-project-local/data/global_17-24_with_polarity_and_spotify.csv')
df_usa = pd.read_csv('/Users/juliusriss/Desktop/data-science-project-local/data/usa_17-24_with_polarity_and_spotify.csv')

# Beide DataFrames vertikal zusammenführen (alle Zeilen beider DataFrames behalten)
df_merged = pd.concat([df_global, df_usa], ignore_index=True)

# Optional: das zusammengeführte DataFrame in eine neue CSV-Datei speichern
df_merged.to_csv('/Users/juliusriss/Desktop/data-science-project-local/data/all_locations_with_polarity_and_spotify.csv', index=False)
