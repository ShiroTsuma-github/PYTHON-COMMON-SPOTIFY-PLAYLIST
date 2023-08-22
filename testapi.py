from spotipy.oauth2 import SpotifyOAuth
import spotipy
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('API_KEY')
api_sec = os.getenv('API_SECRET')


scope = "playlist-modify-public"
auman = SpotifyOAuth(
    client_id=api_key,
    client_secret=api_sec,
    redirect_uri="http://example.com",
    scope=scope)
sp = spotipy.Spotify(auth_manager=auman)

res = sp.user_playlists('31t6ia672oq43efxisyppa26wiq4')
print(res)