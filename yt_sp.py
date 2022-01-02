import os
from dotenv import load_dotenv
import requests
import re

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
playlistID = input.split("?list=")[1]
doWhile = True
results = []

#   brain stuck in c++ land. this is thge equivalent of a dowhile right?
while nextPageToken != "" or doWhile == True:
    doWhile = False
    
    #   youtube has a library to handle API requests like this.
    #   doing this statically as I think the extra dependancy 
    #   isnt worth saving a couple lines of code
    URL = "https://www.googleapis.com/youtube/v3/playlistItems?playlistId=" + playlistID + "&key=" + YOUTUBE_API_KEY + "&part=" +  part + "&maxResults=" + maxResults + "&pageToken=" + nextPageToken
    response = requests.get(URL).json()

    for item in response['items']:
        results.append(SanitizeString(item['snippet']['title']))

    if 'nextPageToken' not in response:
        nextPageToken = ""
    else:
        nextPageToken = response['nextPageToken']

#   Spotify signin







#debug 
f = open("out.txt", "w", encoding="utf-8")
for title in results:
    f.write(title + '\n')
f.close()
##

