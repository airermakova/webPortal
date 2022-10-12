from flask import Flask, render_template, Response, request, redirect, url_for
from urllib.request import urlopen
import mechanicalsoup


app = Flask(__name__)
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/gettrainingset/')
def gettrainingset():
    return render_template('gettrainingset.html')


@app.route('/getchecknn/')
def getchecknn():
    return render_template('checknn.html')


@app.route('/getusers/', methods=['GET','POST'])
def getusers():
    if request.method == "POST":
        path = request.form['inputP']
        print("POST "+str(path))
    return render_template('getusers.html')


@app.route('/gettext/', methods=['GET','POST'])
def gettext():
    path = request.form['inputP']
    if request.method == "POST":
        print("POST ")
        if path is not None:
            print("GG")
    else:
        print("GET")
    return render_template('getusers.html')


if __name__ == '__main__':
    app.run(debug=True)


