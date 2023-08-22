from flask import Flask, render_template, url_for, redirect, session, request
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('API_KEY')
api_sec = os.getenv('API_SECRET')
flask_sec = os.getenv('FLASK_SECRET')

app = Flask(__name__)
app.secret_key = flask_sec
sp = None
scope = "user-follow-read,playlist-modify-public"
sp_oauth = SpotifyOAuth(
    client_id=api_key,
    client_secret=api_sec,
    redirect_uri=url_for('callback', _external=True),
    scope=scope
)



@app.route("/artists")
def get_artists():
    res = sp.current_user_followed_artists()
    # hub = sp.user_playlist('31t6ia672oq43efxisyppa26wiq4')
    res = [res.get('artists').get('items')[i].get('name') for i in range(len(res.get('artists').get('items')))]
    session['res'] = res
    return redirect(url_for('.main_page'))


@app.route("/callback")
def callback():

    session.clear()  # Clear any previous session data
    token_info = sp_oauth.get_access_token(request.args['code'])

    # Store the token info in the session for later use
    session['token_info'] = token_info

    return redirect(url_for('.main_page'))


@app.route("/clear")
def clear_session():
    session.clear()
    return redirect(url_for('.main_page'))

@app.route("/me")
def get_profile():
    res = sp.current_user()
    session['me'] = res
    return redirect(url_for('.main_page'))

@app.route("/")
def main_page():
    token_info = session.get('token_info')
    if not token_info:
        return redirect(url_for('.callback'))
    access_token = token_info['access_token']
    global sp
    sp = spotipy.Spotify(auth=access_token)
    messages = session.get('res')
    me = session.get('me')
    return render_template("mainpage.html", messages=messages, me=me)

# http://localhost:5000/?code=AQDyrFC-E_GHQcAWQJOjlC0lac360HjU7_xaPPl0AtuoTbw70KQMD0lLIyqZQnLyNciV2b_mpXrDUWIs6wE24PXTmIAkwb523ID5K24kCZgNyV4KSyrNaVIBsJTNFbjUzf85_qoEhqqNkJErKk076MP5HN2p46Sa6wN_gllmFkVUWYS3Yo76bACi429smOrdBj8qcbyXq5_qoE-QhtAuMIolyQ
