from flask import Flask, render_template, Response, request, redirect, url_for, send_from_directory, current_app
from urllib.request import urlopen
import mechanicalsoup

import sys
import os

testmodelpath=os.getcwd()+"/testmodel"


app = Flask(__name__)
@app.route('/')
def home():
    return render_template('index.html')


def allowed_txt_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in "txt"


@app.route('/uploads/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    # Appending app path to upload folder path within app root folder
    uploads = os.path.join(current_app.root_path)
    # Returning file from appended path
    return send_from_directory(os.getcwd(), "trainnrC1.txt")


@app.route('/gettrainingset/', methods=['GET','POST'])
def gettrainingset():
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
            output = 'No text file selected'
        elif allowed_txt_file(file.filename):
            file.save(os.path.join(testmodelpath,file.filename))
            args.append(os.path.join(testmodelpath,file.filename))
            args.append(st)
            args.append(num)
            command = "C:/Users/airer/AppData/Local/Programs/Python/Python36/python.exe prepareTestSetsComplexUsersNoRepeat.py " + " ".join(args)
            os.system(command)
            with open('onlyDetectedUsersNR1.txt', 'r') as file:
                output = file.read()
            print(os.path.join(os.getcwd(),"trainnrC1.txt"))
            send_from_directory(os.getcwd(), "trainnrC1.txt")   
        else:
            output="uploaded file has to have .txt extention"            
    return render_template('gettrainingset.html', outputP=output)




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
            #arguments construction
            txt = request.files['text']
            txtname = "patents.txt"
            if txt.filename != '':
                txtname = txt.filename
                txt.save(os.path.join(testmodelpath,txt.filename))
            args.append(os.path.join(testmodelpath,txtname))
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
        arg=""
        if len(str(path))>1:
            cars = str(path).splitlines()
            for c in cars:
                arg+=c.replace(" ","_") + "."

        #file uploading area
        file = request.files['pat']
        if file.filename != '':
            file.save(os.path.join(os.getcwd(),file.filename))
            cars=[]
            with open(os.path.join(os.getcwd(),file.filename), 'r') as file:
               cars += file.read().splitlines()             
            for c in cars:
                arg+=c.replace(" ","_") + "."
        print(arg)
        if len(arg)>0:
            command = "C:/Users/airer/AppData/Local/Programs/Python/Python36/python.exe demoForNNFullNN.py " + arg
            os.system(command)
            with open('results.txt', 'r') as file:
                output = file.read().replace(".", "\n")
            
    return render_template('getusers.html', inputP=path, outputP=output)




if __name__ == '__main__':
    app.run(debug=True)


