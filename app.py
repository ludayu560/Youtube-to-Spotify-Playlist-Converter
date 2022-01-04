import os
from dotenv import load_dotenv
import requests
import re
from flask import Flask, request, url_for, session, redirect
import spotipy
from spotipy.oauth2 import SpotifyOAuth
load_dotenv("./api_keys.env")

YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REDIRECT_URI="http://localhost/8008/spotify/callback"

#   Steps:
#   Get a YT playlist
#   Signin to spotify w/ OAuth and gain access to make playlists
#   Run spotify search for the song names and retrieve the Spotify song ids
#   Make a new playlist with the song ids, output all those which werent found

#   Helper function to optimize search terms in Spotify search
#   the regular expressions are segmented and commented so you can turn on/off
#   whatever search parameters you like.
#   there surely is a better way to do this but I learned regex this semester
#   and I want to try it out
def SanitizeString(str):

    # removes anything in [] or () brackets.
    # intended use case is for titles containing (official) or [featuring ...]
    str = re.sub("[\(\[].*?[\)\]]", "", str)

    # remove all instances of names beyond the first listed.
    # possibly by removing all names after the first ',' and before the last '-'

    # korean songs are not accounted for here... they don't have nice formatting.
    # only optimization may be to remove instances of 'MV' and etc...
    str = re.sub("MV|M/V", "", str)

    # apparently some korean songs dont like putting 'official' in brackets.
    str = re.sub("official", "", str, flags=re.IGNORECASE)
    str = re.sub("video", "", str, flags=re.IGNORECASE)
    str = re.sub("music", "", str, flags=re.IGNORECASE)
    return str


#   Getting a YT playlist

# Max is 50 (0-49) as per current youtube guidelines
maxResults = "50"
nextPageToken = ""
part = "snippet"
# input = input("Enter link to YouTube playlist: ")
input = "https://www.youtube.com/playlist?list=PLDIoUOhQQPlXr63I_vwF9GD8sAKh77dWU"
input = "https://www.youtube.com/playlist?list=PLOHoVaTp8R7dfrJW5pumS0iD_dhlXKv17"
youtubeBaseURL = "https://www.googleapis.com/youtube/v3/playlistItems?playlistId="
playlistID = input.split("?list=")[1]
doWhile = True
results = []

#   brain stuck in c++ land. this is thge equivalent of a dowhile right?
while nextPageToken != "" or doWhile == True:
    doWhile = False
    
    #   youtube has a library to handle API requests like this.
    #   doing this statically as I think the extra dependancy 
    #   isnt worth saving a couple lines of code
    URL = youtubeBaseURL + playlistID + "&key=" + YOUTUBE_API_KEY + "&part=" +  part + "&maxResults=" + maxResults + "&pageToken=" + nextPageToken
    response = requests.get(URL).json()

    for item in response['items']:
        results.append(SanitizeString(item['snippet']['title']))

    if 'nextPageToken' not in response:
        nextPageToken = ""
    else:
        nextPageToken = response['nextPageToken']


# create an endpoint using Flask
app = Flask(__name__)

app.secret_key = "dqlow9i723"
app.config['SESSION_COOKIE_NAME'] = 'YTSPCookie'


@app.route("/")
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    print(auth_url)
    return redirect(auth_url)

@app.route("/authorize")
def authorize():
    return "redirect page"

@app.route("/convert")
def convert():
    return "convert page"

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=url_for('authorize', _external=True),
        scope="playlist-modify-private"
    )




#   Spotify signin
scope = "playlist-modify-private"
responseType = "code"
spotifyProviderURL = "https://accounts.spotify.com/authorize"
URL = spotifyProviderURL + '?' + "client_id=" + SPOTIFY_CLIENT_ID + "&scope=" + scope + "&redirect_uri=" + SPOTIFY_REDIRECT_URI + "&response_type=" + responseType
requests.get(URL)




# #debug 
# f = open("out.txt", "w", encoding="utf-8")
# for title in results:
#     f.write(title + '\n')
# f.close()
# ##

