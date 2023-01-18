from flask import Flask, render_template, request

import numpy
from PIL import Image
import os

from fingerprint_feature_extraction import generate_keys
from fingerprint_matching import find_best_match

app = Flask(__name__)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))


@app.route('/home')
def home():
    return render_template("home.html")


@app.route('/register')
def register():
    return render_template("register.html")


@app.route('/generate', methods=['POST', 'GET'])
def generate():

    if request.method == 'POST':
        # images fold used for user registration
        target = os.path.join(APP_ROOT, 'static/images/')

        # create image directory if not found
        if not os.path.isdir(target):
            os.mkdir(target)

        # retrieve file from html file-picker
        upload = request.files['image_upload']
        print("File name: {}".format(upload.filename))
        filename = upload.filename

        # file support verification
        ext = os.path.splitext(filename)[-1]
        if ext == ".BMP":
            print("File accepted")
        else:
            return render_template("error.html", message="The selected file is not supported"), 400

        # save file
        destination = "".join([target, filename])
        print("File saved to:", destination)
        upload.save(destination)

        # generating
        public_key, private_key = generate_keys(destination)
        print("Public key:", public_key)
        print("Private key:", private_key)

    return render_template("register.html", public_key=str(public_key), private_key=str(private_key))


@app.route('/login')
def login():
    return render_template("login.html")


@app.route('/match', methods=['POST', 'GET'])
def match():

    if request.method == 'POST' and request.files:
        # retrieve file from html file-picker
        upload = request.files['image_upload']
        print("File name: {}".format(upload.filename))

        # file support verification
        ext = os.path.splitext(upload.filename)[-1]
        if ext == ".BMP":
            print("File accepted")
        else:
            return render_template("error.html", message="The selected file is not supported"), 400

        # transform image
        image = numpy.array(Image.open(upload))

        # matching
        match, best_score = find_best_match(image)

    if match:
        return render_template("home.html", match=str(match), best_score=str(best_score))
    else:
        return render_template("error.html", message="User not registered"), 401