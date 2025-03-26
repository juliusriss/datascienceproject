import pandas as pd

# Read CSV
df_polarity = pd.read_csv('/Users/juliusriss/Desktop/data-science-project-local/data/usa_17-24_with_polarity.csv')
df_spotify = pd.read_csv('/Users/juliusriss/Desktop/data-science-project-local/data/usa_17-24_with_spotify.csv')

# Merge the files
df_merged = df_polarity.merge(df_spotify, on=["artist_names", "track_name"], how="left", suffixes=("", "_drop"))

# Remove duplicate columns
columns_to_drop = [col for col in df_merged.columns if col.endswith("_drop")]
df_merged = df_merged.drop(columns=columns_to_drop)

# Add seconds column
df_merged['duration_seconds'] = df_merged['duration_ms'] / 1000

# Create new csv
df_merged.to_csv('/Users/juliusriss/Desktop/data-science-project-local/data/usa_17-24_with_polarity_and_spotify.csv', index=False)
