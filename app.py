from typing import Literal
from flask import Flask, render_template, url_for, redirect, session, request
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from key_generator.key_generator import generate
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('API_KEY')
api_sec = os.getenv('API_SECRET')
flask_sec = os.getenv('FLASK_SECRET')

app = Flask(__name__)

app.secret_key = generate().get_key()
sp = None


class SpotifyPlus():
    def __init__(self, scope: str, redirect: str) -> None:
        self.sp = None
        self.scope: str = scope
        self.redirect: str = redirect
        self.OAuth = SpotifyOAuth(
            client_id=api_key,
            client_secret=api_sec,
            redirect_uri=self.redirect,
            scope=self.scope)
        self.__token = None
        self.__atoken = None
        self.__spotify = None

    def getAuth(self) -> SpotifyOAuth:
        return self.OAuth

    def getSpotify(self):
        if self.__spotify is not None:
            return self.__spotify
        raise ValueError("Token not set")

    def isAccess(self):
        if self.__atoken is None:
            return False
        return True

    def setAccessToken(self, code):
        self.__token = self.OAuth.get_access_token(code)
        self.__atoken = self.__token['access_token']
        self.__spotify = spotipy.Spotify(self.__atoken)

    def getAuthUrl(self) -> str:
        return self.OAuth.get_authorize_url()


@app.route("/artists")
def get_artists():
    sp_plus = session.get('sp_plus')
    if not sp_plus.isAccess():
        return redirect(url_for('.login'))
    sp = sp_plus.getSpotify()
    res = sp.current_user_followed_artists()
    res = [res.get('artists').get('items')[i].get('name')
           for i in range(len(res.get('artists').get('items')))]
    session['res'] = res
    return redirect(url_for('.main_page'))


@app.route('/login')
def login():
    sp_plus = session.get('sp_plus')
    if sp_plus is None:
        return redirect(url_for('.main_page'))
    return redirect(sp_plus.getAuthUrl())


@app.route('/redirect')
def redirectPage():
    sp_plus = session.get('sp_plus')
    if sp_plus is None:
        return redirect(url_for('.main_page'))
    sp_plus.setAccessToken(request.args['code'])

    return redirect(url_for('.main_page'))


@app.route("/clear")
def clear_session():
    session.clear()
    os.remove('.cache')
    return redirect(url_for('.main_page'))


@app.route("/me")
def get_profile():
    sp_plus = session.get('sp_plus')
    if not sp_plus.isAccess():
        return redirect(url_for('.main_page'))
    sp = sp_plus.getSpotify()
    res = sp.current_user()
    session['me'] = res
    return redirect(url_for('.main_page'))


@app.route("/")
def main_page():
    global sp_plus
    sp_plus = SpotifyPlus(
        "user-follow-read,playlist-modify-public",
        url_for('.redirectPage', _external=True))
    session['sp_plus'] = sp_plus
    messages = session.get('res')
    me = session.get('me')
    return render_template("mainpage.html", messages=messages, me=me)
