from typing import Literal
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


@app.route("/artists")
def get_artists():
    token_info = session.get('token_info')
    if not token_info:
        return redirect(url_for('.login'))

    access_token = token_info['access_token']
    sp = spotipy.Spotify(auth=access_token)
    res = sp.current_user_followed_artists()
    # hub = sp.user_playlist('31t6ia672oq43efxisyppa26wiq4')
    res = [res.get('artists').get('items')[i].get('name') for i in range(len(res.get('artists').get('items')))]
    session['res'] = res
    return redirect(url_for('.main_page'))


@app.route('/login')
def login():
    global sp_oauth
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)


@app.route('/redirect')
def redirectPage() -> Literal['redirect']:
    token_info = sp_oauth.get_access_token(request.args['code'])
    session['token_info'] = token_info

    return redirect(url_for('.main_page'))


def create_spotify_oauth() -> SpotifyOAuth:
    scope = "user-follow-read,playlist-modify-public"
    return SpotifyOAuth(
        client_id=api_key,
        client_secret=api_sec,
        redirect_uri=url_for('.redirectPage', _external=True),
        scope=scope)


@app.route("/clear")
def clear_session():
    session.clear()
    return redirect(url_for('.main_page'))


@app.route("/me")
def get_profile():
    token_info = session.get('token_info')
    if not token_info:
        return redirect(url_for('.login'))

    access_token = token_info['access_token']
    sp = spotipy.Spotify(auth=access_token)
    res = sp.current_user()
    session['me'] = res
    return redirect(url_for('.main_page'))

@app.route("/")
def main_page():
    messages = session.get('res')
    me = session.get('me')
    return render_template("mainpage.html", messages=messages, me=me)

# http://localhost:5000/?code=AQDyrFC-E_GHQcAWQJOjlC0lac360HjU7_xaPPl0AtuoTbw70KQMD0lLIyqZQnLyNciV2b_mpXrDUWIs6wE24PXTmIAkwb523ID5K24kCZgNyV4KSyrNaVIBsJTNFbjUzf85_qoEhqqNkJErKk076MP5HN2p46Sa6wN_gllmFkVUWYS3Yo76bACi429smOrdBj8qcbyXq5_qoE-QhtAuMIolyQ
