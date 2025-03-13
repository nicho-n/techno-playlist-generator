import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Spotify API credentials from environment variables
CLIENT_ID = 'd607dbb1455e4911864f1434c83443d2'
CLIENT_SECRET = ''
REDIRECT_URI = 'https://127.0.0.1'
SCOPE = "playlist-modify-public playlist-modify-private user-library-read"

# Initialize Spotipy with credentials
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URI,
                                               scope=SCOPE))

# The specific playlist ID to use
PLAYLIST_ID = '3Oof1Q9vwZpJrj0L9ohkOc'

# Function to search for a song on Spotify and return the track URI
def search_spotify(song_name, artist_name):
    query = f"track:{song_name} artist:{artist_name}"
    result = sp.search(query, limit=1, type="track", market="US")
    
    if result['tracks']['items']:
        track_uri = result['tracks']['items'][0]['uri']
        return track_uri
    return None

# Function to get all tracks from the specified playlist to avoid duplicates
def get_playlist_tracks(playlist_id):
    tracks = []
    results = sp.playlist_tracks(playlist_id)
    
    # Get all tracks in the playlist
    while results:
        for item in results['items']:
            track_uri = item['track']['uri']
            tracks.append(track_uri)
        
        # Check if there are more pages of tracks
        if results['next']:
            results = sp.next(results)
        else:
            break
    return tracks

# Function to add new songs to the playlist
def add_songs_to_playlist(playlist_id, songs):
    track_uris = []
    existing_tracks = get_playlist_tracks(playlist_id)  # Get existing tracks to avoid duplicates
    
    for song in songs:
        song_details = song.strip().split(' by ')
        if len(song_details) == 2:
            song_name = song_details[0]
            artist_name = song_details[1]

            # Search for the song on Spotify
            track_uri = search_spotify(song_name, artist_name)
            if track_uri:
                if track_uri not in existing_tracks:  # Only add if not already in the playlist
                    track_uris.append(track_uri)
                    print(f"Added {song_name} by {artist_name} to the playlist.")
            else:
                print(f"Could not find {song_name} by {artist_name} on Spotify.")
    
    # Add tracks to the playlist if there are any new ones
    if track_uris:
        sp.user_playlist_add_tracks(sp.current_user()['id'], playlist_id, track_uris)
        print(f"Added {len(track_uris)} new tracks to the playlist.")
    else:
        print("No new tracks to add.")

# Function to continuously add songs to the specified playlist
def continuously_add_songs():
    while True:
        # Read songs from the file
        with open("song_playlist.txt", "r") as file:
            songs = file.readlines()

        # Add new songs to the playlist
        add_songs_to_playlist(PLAYLIST_ID, songs)
        
        # Wait for 3 minutes (180 seconds) before the next request
        time.sleep(180)

# Run the function to continuously add songs
continuously_add_songs()
