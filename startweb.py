from flask import Flask, render_template, Response, request, redirect, url_for
from urllib.request import urlopen
import mechanicalsoup

import sys
import os

testmodelpath=os.getcwd()+"/testmodel"


app = Flask(__name__)
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/gettrainingset/')
def gettrainingset():
    return render_template('gettrainingset.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in "pt"

@app.route('/getchecknn/', methods=['GET','POST'])
def getchecknn():
    path=""
    output=""
    args = []
    if request.method == "POST":
        print("POST")
        #phrases number area
        inputN = request.form.get('inputN')
        num = request.form['inputN']
        inputN = request.form.get('inputF')
        st = request.form['inputF']
        if num == None or num=="":
             num = "0"
        if st == None or st=="":
             st = "0"
        print(num + "..." + st)
        #file uploading area
        file = request.files['file']
        if file.filename == '':
            output = 'No model file selected'
        elif allowed_file(file.filename):
            file.save(os.path.join(testmodelpath,file.filename))
            args.append(os.path.join(testmodelpath,"patents.txt"))
            args.append(st)
            args.append(num)
            args.append(os.path.join(testmodelpath,file.filename))
            command = "C:/Users/airer/AppData/Local/Programs/Python/Python36/python.exe FlaiNNTestMultiThreading.py " + " ".join(args)
            os.system(command)
            with open('NNStatistics.txt', 'r') as file:
                output = file.read()
        else:
            output="uploaded file has to have .pt extention"            
    return render_template('getchecknn.html', outputP=output)


@app.route('/getusers/', methods=['GET','POST'])
def getusers():
    path=""
    output=""
    if request.method == "POST":
        inputP = request.form.get('inputP')
        path = request.form['inputP']
        print("POST "+str(path))
        if len(str(path))>1:
            myString = str(path).strip('\n\t')
            arg = myString.replace(" ", "_")
            print(arg)
            command = "C:/Users/airer/AppData/Local/Programs/Python/Python36/python.exe demoForNNFullNN.py " + arg
            os.system(command)
            with open('results.txt', 'r') as file:
                output = file.read().replace(".", "\n")
            
    return render_template('getusers.html', inputP=path, outputP=output)




if __name__ == '__main__':
    app.run(debug=True)


