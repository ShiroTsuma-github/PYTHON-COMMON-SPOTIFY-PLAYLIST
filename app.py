import pickle
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
        self.accessToken = None
        self.spotify = None

    def getAuth(self) -> SpotifyOAuth:
        return self.OAuth

    def getSpotify(self):
        if self.accessToken is None:
            raise ValueError("Token not set")
        return spotipy.Spotify(auth=self.accessToken)

    def isAccess(self):
        return self.accessToken is not None

    def setAccessToken(self, code):
        self.accessToken = self.OAuth.get_access_token(code)['access_token']

    def getAuthUrl(self) -> str:
        return self.OAuth.get_authorize_url()


@app.route("/artists")
def get_artists():
    sp_plus = pickle.loads(session['sp_plus'])
    if not sp_plus.isAccess():
        return redirect(url_for('login'))
    sp = sp_plus.getSpotify()
    res = sp.current_user_followed_artists()
    res = [res.get('artists').get('items')[i].get('name')
           for i in range(len(res.get('artists').get('items')))]
    session['res'] = res
    return redirect(url_for('.main_page'))


@app.route('/login')
def login():
    sp_plus = pickle.loads(session['sp_plus'])
    return redirect(sp_plus.getAuthUrl())


@app.route('/redirect')
def redirectPage():
    sp_plus = pickle.loads(session['sp_plus'])
    sp_plus.setAccessToken(request.args.get('code'))
    session['sp_plus'] = pickle.dumps(sp_plus)
    return redirect(url_for('get_profile'))


@app.route("/clear")
def clear_session():
    session.clear()
    os.remove('.cache')
    return redirect(url_for('.main_page'))


@app.route("/me")
def get_profile():
    sp_plus = pickle.loads(session['sp_plus'])
    if not sp_plus.isAccess():
        return redirect(url_for('main_page'))
    sp = sp_plus.getSpotify()
    res = sp.current_user()
    nick = res.get('display_name')
    img = None if len(res.get('images')) == 0 else res.get('images')[0].get('url')
    id = res.get('id')
    email = res.get('email')
    session['me'] = [nick, img, id, email]
    return redirect(url_for('.main_page'))


@app.route("/")
def main_page():
    if 'sp_plus' not in session:
        sp_plus = SpotifyPlus(
            "user-follow-read,playlist-modify-public,user-follow-modify,user-library-modify,user-library-read,user-read-email,user-read-private",
            url_for('redirectPage', _external=True))
        session['sp_plus'] = pickle.dumps(sp_plus)
    messages = session.get('res', [])
    me = session.get('me', None)
    return render_template("mainpage.html", messages=messages, me=me)
