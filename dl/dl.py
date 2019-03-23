from flask import Flask
import pika
import os
from os import path
from flask import request, render_template, make_response, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
import json
import jwt
import requests

UPLOAD_FOLDER = os.getcwd()+'/protected/'
app = Flask(__name__)
with open('configuration.json') as file:
    data = json.load(file)
file.close()
app.secret_key = data["app_secret"].encode("utf-8")
secret = data["jwt_secret"]
STATUS_401 = 'Unauthorized 401, Authentication token is invalid or expired'

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.exchange_declare(exchange='Resize64',exchange_type='topic')

@app.route('/wasikm/dl/upload', methods=['POST'])
def upload():
    encoded = request.form['jwt']
    try:
        decoded = jwt.decode(encoded, secret, algorithms='HS256')
    except:
        return STATUS_401, 401 
    if decoded:
        username = decoded['username']
        if len(os.listdir(UPLOAD_FOLDER + username)) < 5:
            file = request.files['file']
            if 'file' not in request.files:
                return render_template('upload.html', error='No selected file')
            if file:
                filename = secure_filename(file.filename)
                file.save(os.path.join(UPLOAD_FOLDER+secure_filename(username),filename))
                parts = filename.split(".")
                if(parts[-1] == "jpg" or parts[-1] == "jpeg" or parts[-1] == "png" ):
                    message = UPLOAD_FOLDER + username +"/"+ filename
                    channel.basic_publish(exchange='Resize64', routing_key="resize.picture",body=message)

                headers = {'content-type': 'application/x-www-form-urlencoded'}
                try:
                    requests.post('https://localhost:3000/wasikm/notification', verify=False, headers=headers, data='user=' + username) #verify=""
                except requests.exceptions.RequestException:
                    return redirect("https://localhost/wasikm/webapp/upload?flash=1"), 301
                return redirect("https://localhost/wasikm/webapp/upload?flash=1"), 301
        return redirect("https://localhost/wasikm/webapp/home?flash=1"), 301
    return STATUS_401, 401


@app.route('/wasikm/dl/download', methods=['GET'])
def get_file():
    encoded = request.args.get('jwt')
    try:
        decoded = jwt.decode(encoded, secret, algorithms='HS256')
    except : #jwt.ExpiredSignatureError
        return STATUS_401, 401
    if decoded:
        filename = decoded['filename']
        username = decoded['username'] 
        return send_from_directory(UPLOAD_FOLDER+secure_filename(username),secure_filename( filename), as_attachment=True)
    return STATUS_401, 401


@app.route('/wasikm/dl/delete/<path:filename>', methods=['GET'])
def delete_item(filename):
    encoded = request.args.get('jwt')
    try:
        decoded = jwt.decode(encoded, secret, algorithms='HS256')
    except:
        return 'Unauthorized', 401
    if decoded:
        username = decoded['username']
        if path.exists(os.path.join(UPLOAD_FOLDER+secure_filename(username), secure_filename(filename))):
            os.remove(os.path.join(UPLOAD_FOLDER+secure_filename(username), secure_filename(filename))) 
            if path.exists(os.path.join(UPLOAD_FOLDER+username+"/icons",filename)):
                os.remove(os.path.join(UPLOAD_FOLDER+secure_filename(username)+"/icons",secure_filename(filename)))
            return 'No Content', 204
        else :
            return 'NOT FOUND 404, The file you want to delete does not exists', 404
    return STATUS_401, 401


if __name__ == "__main__":
    app.run(port='5555')

