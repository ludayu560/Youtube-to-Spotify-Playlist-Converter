import os
from dotenv import load_dotenv
import requests

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')

#   Steps:
#   Get a YT playlist
#   Signin to spotify w/ OAuth and gain access to make playlists
#   Run spotify search for the song names and retrieve the Spotify song ids
#   Make a new playlist with the song ids, output all those which werent found
playlistID = "7lCDEYXw3mM"
URLParams = "&part=snippet,contentDetails,statistics,status"
URL = "https://www.googleapis.com/youtube/v3/videos?id=" + playlistID + "&key=" + YOUTUBE_API_KEY + URLParams

response = requests.get(url = URL).json()

print(response)