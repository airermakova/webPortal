from flask import Flask, render_template, Response, request, redirect, url_for
from urllib.request import urlopen
import mechanicalsoup

import sys
import os

phrases=""

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
    path=""
    output=""
    if request.method == "POST":
        inputP = request.form.get('inputP')
        path = request.form['inputP']
        print("POST "+str(path))
        if len(str(path))>1:
            phrases = path
            arg = str(path).replace(" ", "_")
            print(arg)
            command = "C:/Users/airer/AppData/Local/Programs/Python/Python36/python.exe demoForNNFullNN.py " + arg
            os.system(command)
            with open('results.txt', 'r') as file:
                output = file.read()
    return render_template('getusers.html', inputP=path, outputP=output)




if __name__ == '__main__':
    app.run(debug=True)


