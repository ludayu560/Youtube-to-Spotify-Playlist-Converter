import os
from dotenv import load_dotenv
import requests
import time
import re
from flask import Flask, request, url_for, session, redirect
import spotipy
from spotipy.oauth2 import SpotifyOAuth
load_dotenv("./api_keys.env")

YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REDIRECT_URI="http://localhost/8008/spotify/callback"
SPOTIFY_MAXIMUM_PER_REQUEST = 50
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
input = input("Enter link to YouTube playlist: ")
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


# create endpoints with flask
app = Flask(__name__)

app.secret_key = "dqlow9213e-di723"
app.config['SESSION_COOKIE_NAME'] = 'YTSPCookie'
TOKEN_INFO = "token_info"

@app.route("/")
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    print("please go to: http://127.0.0.1:5000/")
    return redirect(auth_url)

@app.route("/authorize")
def authorize():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect(url_for('finish', _external=True))

@app.route("/finish")
def finish():

    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))

    # create the new playlist
    playlist = sp.user_playlist_create(
        user=sp.me()['id'], 
        name="Converted Playlist" + time.strftime("%H:%M:%S", time.localtime()), 
        public=False, 
        collaborative=False, 
        description="Created by a BotBot!!!")
    
    # convert from titles to a singular list of ids
    trackItem = []
    for title in results:
        res = sp.search(q=title,limit=1)
        if res['tracks']['total'] == 0:
            print("Not Found: " + title)
            continue
        else:
            trackItem.append(res['tracks']['items'][0]['id'])
    playlistID = playlist['id']

    # add the newly found songs to the new playlist
    while len(trackItem) > SPOTIFY_MAXIMUM_PER_REQUEST:
        sp.playlist_add_items(playlistID, trackItem[:SPOTIFY_MAXIMUM_PER_REQUEST])
        trackItem = trackItem[SPOTIFY_MAXIMUM_PER_REQUEST:len(trackItem)]
    sp.playlist_add_items(playlistID, trackItem)

    return "Done! check your Spotify"

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=url_for('authorize', _external=True),
        scope="playlist-modify-private, user-library-read"
    )