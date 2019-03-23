from flask import Flask
import os
from flask import session
from flask import request, render_template, make_response, redirect, send_from_directory
import hashlib, binascii
import datetime
import redis
import uuid
import json
from werkzeug.utils import secure_filename
import jwt
import requests

UPLOAD_FOLDER = os.getcwd()+'/protected/'
with open('configuration.json') as file:
    data = json.load(file)
file.close()
app = Flask(__name__,static_url_path='/wasikm/webapp/static')
app.secret_key = data["app_secret"].encode("utf-8")
secret = data["jwt_secret"]
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
)
RED = redis.Redis()


@app.route('/')
def red():
    return redirect("/wasikm/webapp/login/")


@app.route('/wasikm/webapp/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if check_user(username, password):
            resp = make_response(redirect('wasikm/webapp/home'),301)
            return resp
        return render_template('login.html', error='Nieprawidłowe dane')
    elif not session.get('logged_in'):
        return render_template('login.html')
    return home()


def check_user(username, password):
    flag = False
    if RED.exists('wasikm:webapp:'+username):
        salt = RED.hget('wasikm:webapp:'+username, 'salt')
        password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        password = binascii.hexlify(password)
        passw = RED.hget('wasikm:webapp:'+username, username)
        if password == passw:
            flag = True
            session['logged_in'] = True
            sid = uuid.uuid4()
            sid = str(sid)
            RED.hset('wasikm:webapp:'+sid, 'login', username)
            RED.hset('wasikm:webapp:'+sid, 'sid', sid)
            session['sid'] = sid
    return flag


@app.route("/wasikm/webapp/home")
def home():
    sid = session.get('sid')
    username = check_session_id(sid)
    if session.get('logged_in') and username:
        files = get_files(username, UPLOAD_FOLDER+username)
        icons = get_files(username, UPLOAD_FOLDER+username+"/icons")
        flash = request.args.get('flash')
        return render_template('home.html',user=username, files=files,flash=flash,username=username)
    return render_template('login.html',error='Zaloguj się aby otrzymać dostęp do plików')


@app.route('/wasikm/webapp/icons/<path:username>/<path:filename>', methods=['GET'])
def get_icon(username,filename):
    sid = session.get('sid')
    username2 = check_session_id(sid)
    if session.get('logged_in') and username2 == username:
        return send_from_directory(UPLOAD_FOLDER+secure_filename(username)+'/icons',secure_filename(filename))
    return 'Unauthorized 401', 401


@app.route("/wasikm/webapp/logout")
def logout():
    session.pop('logged_in', None)
    sid = session.pop('sid', None)
    session.clear()
    RED.delete('wasikm:webapp:'+sid)
    return login()


def check_session_id(sid):
    if sid and RED.exists('wasikm:webapp:'+sid):
        sid_redis = RED.hget('wasikm:webapp:'+sid,'sid')
        user_redis = RED.hget('wasikm:webapp:'+sid,'login')
        if sid_redis.decode("utf-8") == str(sid):
            return user_redis.decode('utf-8')
    return 0


def get_files(username, folder):
    files = []
    for filename in os.listdir(folder):
        path = os.path.join(folder, filename)
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
        return render_template('upload.html',user=username,error='Dodałeś maksymalną liczbę plików(5)',block=1)
    return render_template("login.html",error='Aby móc dodawać pliki zaloguj się')


@app.route('/wasikm/webapp/download/<path:filename>', methods=['GET'])
def get_file(filename):
    sid = session.get('sid')
    username = check_session_id(sid)
    if session.get('logged_in') and username:
        token = jwt.encode({'username': username, 'filename':filename, 'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=300)},secret, algorithm='HS256').decode('utf-8')
        return redirect('https://localhost/wasikm/dl/download?jwt='+token) 
    return render_template('login.html', error='Zaloguj się aby otrzymać dostęp do plików')


@app.route('/wasikm/webapp/delete/<path:filename>', methods=['GET'])
def delete(filename):
    sid = session.get('sid')
    username = check_session_id(sid)
    if session.get('logged_in') and username:
        token = jwt.encode({'username': username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=300)},secret, algorithm='HS256').decode('utf-8')
        return redirect('https://localhost/wasikm/dl/delete/'+filename+'?jwt='+token) 
    return render_template('login.html', error='Zaloguj się aby otrzymać dostęp do plików')


@app.route('/wasikm/webapp/share/<path:filename>', methods=['GET'])
def share(filename):
    sid = session.get('sid')
    username = check_session_id(sid)
    if session.get('logged_in') and username:
        #url = request.url_root + "wasikm/dl/download"
        url = "https://localhost/wasikm/dl/download"
        token = jwt.encode({'username': username, 'filename' : filename}, secret, algorithm='HS256').decode('utf-8')
        url = url + "?jwt=" + token
        return render_template('share.html',file=filename, user=username, url = url)
    return render_template('login.html', error='Zaloguj się aby otrzymać dostęp do plików')


if __name__ == "__main__":
    app.run(host= '127.0.0.1')

