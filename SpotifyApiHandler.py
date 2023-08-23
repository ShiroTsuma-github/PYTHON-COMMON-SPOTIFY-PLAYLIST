import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('API_KEY')
api_sec = os.getenv('API_SECRET')
flask_sec = os.getenv('FLASK_SECRET')

scope = "user-library-read"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=api_key,
    client_secret=api_sec,
    redirect_uri='http://localhost:5000/callback',
    scope=scope))

results = sp.current_user_saved_tracks()
for idx, item in enumerate(results['items']):
    track = item['track']
    print(idx, track['artists'][0]['name'], " – ", track['name'])