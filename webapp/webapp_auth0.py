from flask import Flask
import os
from flask import session
from flask import request, render_template, make_response, redirect, send_from_directory
import hashlib, binascii
from flask import url_for
import datetime
import redis
import uuid
import json
import jwt
from authlib.flask.client import OAuth
from six.moves.urllib.parse import urlencode
import requests

UPLOAD_FOLDER = os.getcwd()+'/protected/'
with open('configuration.json') as file:
    data = json.load(file)
file.close()
app = Flask(__name__,static_url_path='/wasikm/webapp/static')
app.secret_key = data["app_secret"].encode("utf-8")
secret = data["jwt_secret"]
app.config.update(
    #SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
)
RED = redis.Redis()
oauth = OAuth(app)

auth0 = oauth.register(
    'auth0',
    client_id=data["client_id"],
    client_secret=data["client_secret"],
    api_base_url=data["api_base_url"],
    access_token_url=data["api_base_url"]+'/oauth/token',
    authorize_url=data["api_base_url"]+'/authorize',
    client_kwargs={
        'scope': 'openid email',
    },
)


@app.route('/')
def red():
    return redirect("/wasikm/webapp/login/")


@app.route('/wasikm/webapp/auth0')
def redirect_to_auth0():
    return auth0.authorize_redirect(redirect_uri='http://127.0.0.1:5000/wasikm/webapp/authorize', audience=data["api_base_url"]+"/userinfo")


@app.route('/wasikm/webapp/login/', methods=['GET'])
def login():
    if not session.get('logged_in'):
        return render_template('login.html')
    return home()


@app.route('/wasikm/webapp/authorize')
def check_user():
    auth0.authorize_access_token()
    resp = auth0.get('userinfo')
    userinfo = resp.json()
    username = userinfo["email"]
    username = username.split("@")[0]
    session['logged_in'] = True
    sid = uuid.uuid4()
    sid = str(sid)
    RED.hset('wasikm:webapp:'+sid, 'login', username)
    RED.hset('wasikm:webapp:'+sid, 'sid', sid)
    session['sid'] = sid
    return redirect('http://127.0.0.1:5000/wasikm/webapp/home')


@app.route("/wasikm/webapp/home")
def home():
    sid = session.get('sid')
    username = check_session_id(sid)
    if session.get('logged_in') and username:
        files = get_files(username)
        flash = request.args.get('flash')
        return render_template('home.html',user=username, files=files,flash=flash,username=username)
    return render_template('login.html',error='Zaloguj się aby otrzymać dostęp do plików')


@app.route("/wasikm/webapp/logout")
def logout():
    session.pop('logged_in', None)
    sid = session.pop('sid', None)
    session.clear()
    RED.delete('wasikm:webapp:'+sid)
    params = {'returnTo': url_for('login', _external=True), 'client_id': data['client_id']}
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))


def check_session_id(sid):
    if sid and RED.exists('wasikm:webapp:'+sid):
        sid_redis = RED.hget('wasikm:webapp:'+sid,'sid')
        user_redis = RED.hget('wasikm:webapp:'+sid,'login')
        if sid_redis.decode("utf-8") == str(sid):
            return user_redis.decode('utf-8')
    return 0


def get_files(username):
    files = []
    for filename in os.listdir(UPLOAD_FOLDER+username):
        path = os.path.join(UPLOAD_FOLDER+username, filename)
        if os.path.isfile(path):
            files.append(filename)
    return files


@app.route('/wasikm/webapp/upload', methods=['GET'])
def upload():
    sid = session.get('sid')
    username = check_session_id(sid)
    if session.get('logged_in') and username:
        if len(os.listdir(UPLOAD_FOLDER + username)) < 5:
            token = jwt.encode({'username': username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=300)}, secret,algorithm='HS256').decode('utf-8')
            flash = request.args.get('flash')
            return render_template('upload.html',user=username,jwt=token,block=0,flash=flash)
        return render_template('upload.html',error='Dodałeś maksymalną liczbę plików(5)',block=1)
    return render_template("login.html",error='Aby móc dodawać pliki zaloguj się')


@app.route('/wasikm/webapp/download/<path:filename>', methods=['GET'])
def get_file(filename):
    sid = session.get('sid')
    username = check_session_id(sid)
    if session.get('logged_in') and username:
        token = jwt.encode({'username': username, 'filename':filename, 'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=300)},secret, algorithm='HS256').decode('utf-8')
        return redirect('http://127.0.0.1:5555/wasikm/dl/download?jwt='+token) 
    return render_template('login.html', error='Zaloguj się aby otrzymać dostęp do plików')


@app.route('/wasikm/webapp/delete/<path:filename>', methods=['GET'])
def delete(filename):
    sid = session.get('sid')
    username = check_session_id(sid)
    if session.get('logged_in') and username:
        token = jwt.encode({'username': username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=300)},secret, algorithm='HS256').decode('utf-8')
        return redirect('http://127.0.0.1:5555/wasikm/dl/delete/'+filename+'?jwt='+token) 
    return render_template('login.html', error='Zaloguj się aby otrzymać dostęp do plików')


@app.route('/wasikm/webapp/share/<path:filename>', methods=['GET'])
def share(filename):
    sid = session.get('sid')
    username = check_session_id(sid)
    if session.get('logged_in') and username:
        #url = request.url_root + "wasikm/dl/download"
        url = "http://127.0.0.1:5555/wasikm/dl/download"
        token = jwt.encode({'username': username, 'filename' : filename}, secret, algorithm='HS256').decode('utf-8')
        url = url + "?jwt=" + token
        return render_template('share.html', url = url)
    return render_template('login.html', error='Zaloguj się aby otrzymać dostęp do plików')


if __name__ == "__main__":
    app.run()

