import os
from dotenv import load_dotenv
import requests
import json
load_dotenv("./api_keys.env")

YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
SPOTIFY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
SPOTIFY_REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')

#   Steps:
#   Get a YT playlist
#   Signin to spotify w/ OAuth and gain access to make playlists
#   Run spotify search for the song names and retrieve the Spotify song ids
#   Make a new playlist with the song ids, output all those which werent found

#   Getting a YT playlist
results = []
input = input("Enter link to YouTube playlist: ")
playlistID = input.split("?list=")[1]
part = "snippet"
maxResults = "50"   # Max is 50 (0-49) as per current youtube guidelines
nextPageToken = ""
doWhile = True

#   brain stuck in c++ land. this is thge equivalent of a dowhile right?
while nextPageToken != "" or doWhile == True:
    doWhile = False
    
    #   youtube has a library to handle API requests like this.
    #   doing this statically as I think the extra dependancy 
    #   isnt worth saving a couple lines of code
    URL = "https://www.googleapis.com/youtube/v3/playlistItems?playlistId=" + playlistID + "&key=" + YOUTUBE_API_KEY + "&part=" +  part + "&maxResults=" + maxResults + "&pageToken=" + nextPageToken
    response = requests.get(URL).json()

    for item in response['items']:
        results.append(item['snippet']['title'])

    if 'nextPageToken' not in response:
        nextPageToken = ""
    else:
        nextPageToken = response['nextPageToken']

f = open("out.txt", "w", encoding="utf-8")
for title in results:
    f.write(title + '\n')
f.close()   