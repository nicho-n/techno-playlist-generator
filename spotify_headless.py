import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import time
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Spotify API credentials from environment variables
CLIENT_ID = "d607dbb1455e4911864f1434c83443d2"
CLIENT_SECRET = "3a46148a3f5d476ca39378a638f8a5d0"
REFRESH_TOKEN = "AQDqEqxDG9MJslHemZWRPyGaMb9JLr6i25uqK07jDHZRnPMV4nzAMyn6cPnfEb6vu1PJLIbTcIzcig5FE5-XirNKygY-qJDlcnMAg3QKJffSxBu7ntZmLkm5Vlrc6PRjzgs"
TOKEN_URL = "https://accounts.spotify.com/api/token"
PLAYLIST_ID = "3Oof1Q9vwZpJrj0L9ohkOc"

# API URL for the current track
FLUX_URL = "https://fluxmusic.api.radiosphere.io/channels/c7d49649-081e-4790-adda-99d8e22b19a5/current-track"

# Function to refresh the Spotify access token
def refresh_access_token():
    response = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "refresh_token",
            "refresh_token": REFRESH_TOKEN,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"Failed to refresh token: {response.json()}")

# Get a Spotify client
def get_spotify_client():
    access_token = refresh_access_token()
    return spotipy.Spotify(auth=access_token)

# Function to get the current song from Flux

def get_current_song():
    current_time = int(time.time() * 1000)
    response = requests.get(FLUX_URL, params={"time": current_time})
    
    if response.status_code == 200:
        data = response.json()
        song_name = data.get('trackInfo', {}).get('title', 'Unknown Track')
        artist_name = data.get('trackInfo', {}).get('artistCredits', 'Unknown Artist')
        return f"{song_name} by {artist_name}"
    else:
        print(f"Failed to fetch current track. Status code: {response.status_code}")
        return None

# Function to write song to file if it's not a duplicate
def write_song_to_file(song):
    try:
        try:
            with open("song_playlist.txt", "r") as file:
                existing_songs = file.readlines()
        except FileNotFoundError:
            existing_songs = []
        
        if song + "\n" not in existing_songs:
            with open("song_playlist.txt", "a") as file:
                file.write(song + "\n")
            print(f"Added: {song}")
        else:
            print(f"Duplicate song found: {song}")
    except Exception as e:
        print(f"Error writing to file: {e}")

# Function to search for a song on Spotify
def search_spotify(song_name, artist_name, sp):
    query = f"track:{song_name} artist:{artist_name}"
    result = sp.search(query, limit=1, type="track", market="US")
    
    if result['tracks']['items']:
        return result['tracks']['items'][0]['uri']
    return None

# Function to get all tracks in the playlist
def get_playlist_tracks(sp, playlist_id):
    tracks = []
    results = sp.playlist_tracks(playlist_id)
    
    while results:
        for item in results['items']:
            tracks.append(item['track']['uri'])
        if results['next']:
            results = sp.next(results)
        else:
            break
    
    return tracks

# Function to add new songs to Spotify playlist
def add_songs_to_playlist(sp, playlist_id, songs):
    track_uris = []
    existing_tracks = get_playlist_tracks(sp, playlist_id)
    
    for song in songs:
        song_details = song.strip().split(' by ')
        if len(song_details) == 2:
            song_name, artist_name = song_details
            track_uri = search_spotify(song_name, artist_name, sp)
            if track_uri:
                if track_uri not in existing_tracks:
                    track_uris.append(track_uri)
                    print(f"Added {song_name} by {artist_name}.")
                else:
                    print(f"{song_name} by {artist_name} is already in the playlist.")
            else:
                print(f"Could not find {song_name} by {artist_name} on Spotify.")
    
    if track_uris:
        sp.user_playlist_add_tracks(sp.current_user()['id'], playlist_id, track_uris)
        print(f"Added {len(track_uris)} new tracks.")
    else:
        print("No new tracks to add.")

# Main function to continuously fetch songs and add to playlist
def run_script():
    while True:
        print("Fetching current song...")
        current_song = get_current_song()
        
        if current_song:
            write_song_to_file(current_song)
        
        sp = get_spotify_client()
        with open("song_playlist.txt", "r") as file:
            songs = file.readlines()
        
        add_songs_to_playlist(sp, PLAYLIST_ID, songs)
        
        time.sleep(180)

# Start the script
if __name__ == "__main__":
    run_script()