import requests
import time
from datetime import datetime, timedelta

# API URL for the current track
url = "https://fluxmusic.api.radiosphere.io/channels/c7d49649-081e-4790-adda-99d8e22b19a5/current-track"

# Function to get the current song for a specific timestamp
def get_current_song():
    # Get the current timestamp in milliseconds (without decimals)
    current_time = int(time.time() * 1000)  # Truncate to integer

    # Send the GET request with the current timestamp
    response = requests.get(url, params={"time": current_time})

    if response.status_code == 200:
        data = response.json()
        song_name = data.get('trackInfo', {}).get('title', 'Unknown Track')
        artist_name = data.get('trackInfo', {}).get('artistCredits', 'Unknown Artist')
        return f"{song_name} by {artist_name}"
    else:
        print(f"Failed to fetch current track. Status code: {response.status_code}")
        return None

# Function to write the song to the file if it's not a duplicate
def write_song_to_file(song):
    try:
        # Check if the file exists
        try:
            with open("song_playlist.txt", "r") as file:
                existing_songs = file.readlines()
        except FileNotFoundError:
            # If the file does not exist, create an empty list for the first run
            existing_songs = []

        # Check if the song is already in the file
        if song + "\n" not in existing_songs:
            with open("song_playlist.txt", "a") as file:
                file.write(song + "\n")
            print(f"Added: {song}")
        else:
            print(f"Duplicate song found: {song}")
    except Exception as e:
        print(f"Error writing to file: {e}")

# Function to run every 3 minutes and fetch songs
def run_every_3_minutes():
    while True:
        print("Fetching current song...")
        current_song = get_current_song()

        if current_song:
            write_song_to_file(current_song)
        
        # Wait for 3 minutes (180 seconds) before the next request
        time.sleep(180)

# Start the script
run_every_3_minutes()
