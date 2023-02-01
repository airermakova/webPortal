from flask import Flask, render_template, Response, request, redirect, url_for, send_from_directory, current_app, send_file
from urllib.request import urlopen
import mechanicalsoup
from flask import Flask,render_template,request,redirect
from flask_login import login_required, current_user, login_user, logout_user
from models import UserModel,db,login
import sys
import os
import shutil
import ray
import time
import codecs
import subprocess
import win32com.client


testmodelpath=os.path.join(os.getcwd(),"testmodel")
userdatapath=os.path.join(os.getcwd(),"userdata")


app = Flask(__name__)
app.secret_key = 'xyz' 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
login.init_app(app)
login.login_view = 'login'
 
@app.before_first_request
def create_all():
    db.create_all()


@app.route('/')
@login_required
def home():
    return render_template('index.html')


def allowed_txt_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in "txt"

def prepareUsersFiles(file, username, pyscriptname):
    userpath=os.path.join(userdatapath, username)
    if(os.path.exists(userpath)==False):
         os.mkdir(userpath)
    for script in pyscriptname:
        if(os.path.exists(os.path.join(userpath, script))==False):
            shutil.copyfile(script, os.path.join(userpath, script))
    if(os.path.exists(os.path.join(userpath, "usersList.txt"))==False):
        shutil.copyfile(os.path.join(testmodelpath, "usersList.txt"), os.path.join(userpath, "usersList.txt"))
    if(os.path.exists(os.path.join(userpath, "techList.txt"))==False):
        shutil.copyfile(os.path.join(testmodelpath, "techList.txt"), os.path.join(userpath, "techList.txt"))
    if(file is not None):
        file.save(os.path.join(userpath,file.filename))

def removeFiles(dirpath, filenames):
    for file in filenames: 
        filePath = os.path.join(dirpath, file)
        if os.path.exists(filePath):
            os.remove(filePath)


@ray.remote
def runCommand(command):
    WshShell = win32com.client.Dispatch("WScript.Shell")
    WshShell.run(command) 
    #print(command)
    #os.system(command)

def run_remotely(script, userpath, args):    
    command = "C:/Users/airer/AppData/Local/Programs/Python/Python36/python.exe " + str(os.path.join(userpath,script))+ " " + " ".join(args)
    print(command)
    ray.init()
    start_time = time.time()
    results = ray.get([runCommand.remote(command) for _ in range(os.cpu_count())])
    duration = time.time() - start_time
    print('Sequence size: {}, Remote execution time: {}'.format(command, duration)) 
    ray.shutdown()

def getUIArguments(request, names, nonVal):
    vals=[]
    for nm in names:
        st = request.form[nm]
        if st == None or st == "":
            st = nonVal
        print(str(st))
        vals.append(str(st))
    return vals

def waitForFile(filesToAwait, userpath, fileToSee):
    output=""
    filesPath=[]
    for fl in filesToAwait:    
        filesPath.append(os.path.join(userpath,fl))
    for fl in filesPath:
        while os.path.exists(fl)==False:
            time.sleep(5)
        print(str(fl))
        file = open(str(fl), "r", encoding="utf8")
        lns = file.readlines()
        for st in lns:
            output +=st
        file.close()
    if os.path.exists(os.path.join(userpath,fileToSee))==True:
        send_from_directory(userpath,fileToSee)
    print("READ")
    return output


def waitForRemoval(filesToAwait, userpath, filesToRemove):
    output=""
    filesPath=[]
    for fl in filesToAwait:    
        filesPath.append(os.path.join(userpath,fl))
    for fl in filesPath:
        while os.path.exists(fl)==False:
            time.sleep(1)
    for fl in filesToRemove:
        if os.path.exists(os.path.join(userpath,fl)):    
            os.remove(os.path.join(userpath,fl))


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in "pt"



@app.route('/uploads/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    # Appending app path to upload folder path within app root folder
    userpath=os.path.join(userdatapath, current_user.username)
    # Returning file from appended path
    #if(os.path.exists(os.path.join(userpath,filename))==True):
    return send_file(os.path.join(userpath,filename))


@app.route('/downloads/<path:filename>', methods=['GET', 'POST'])
def downloads(filename):
    # Appending app path to upload folder path within app root folder
    userpath=os.path.join(userdatapath, current_user.username)
    # Returning file from appended path
    if(os.path.exists(os.path.join(userpath,filename))==True):
        return send_file(os.path.join(userpath,filename), as_attachment=True)


@app.route('/gettechtrainingset/', methods=['GET','POST'])
def gettechtrainingset():
    path=""
    output=""
    visUs="hidden"
    visTh="hidden"
    args = []
    if request.method == "POST":
        #file uploading area
        file = request.files['file']
        if file.filename == '':
            output = 'No text file selected'
        elif allowed_txt_file(file.filename):                  
            fileNm = file.filename            
            userpath=os.path.join(userdatapath, current_user.username) 
            prepareUsersFiles(file, current_user.username, ["prepareTestSetsComplexTechNoRepeat.py"])            
            #phrases number area
            arg = getUIArguments(request, ['inputN','inputF'], "0")
            num = arg[0]
            st = arg[1]
            print("phrase number: " + num + " start phrase: " + st)
            args.append(os.path.join(userpath,file.filename))
            args.append(st)
            args.append(num)
            args.append(userpath)              
            flsToWait=[]
            resFile=[]
            if request.form.get('users'):
                flsToWait.append("onlyDetectedUsersNR1.txt")
            if request.form.get('techs'):
                flsToWait.append("onlyDetectedTechsNR1.txt")  
            
            if request.form.get('users'):
                args.append("us")
                run_remotely('prepareTestSetsComplexTechNoRepeat.py',userpath,args)
                output = waitForFile(["onlyDetectedUsersNR1.txt"],userpath,"trainnrC1.txt") 
                visUs="visible"
                args.remove("us")
            if request.form.get('techs'):     
                args.append("tech")
                run_remotely('prepareTestSetsComplexTechNoRepeat.py',userpath,args) 
                output = waitForFile(flsToWait,userpath,"trainthC1.txt") 
                visTh="visible"
            waitForRemoval(flsToWait,userpath,["prepareTestSetsComplexTechNoRepeat.py",fileNm])
        else:
            output="uploaded file has to have .txt extention"        
    return render_template('gettechtrainingset.html', outputP=output, visibilitynr=visUs, visibilityth=visTh)



@app.route('/getchecknn/', methods=['GET','POST'])
def getchecknn():
    path=""
    output=""
    args = []
    if request.method == "POST":
        print("POST")
        #phrases number area
        dataFile = ""
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
            dataFile = file.filename
            scripts=[]
            if request.form.get('users'):
                scripts.append("FlaiNNTestMultiThreading.py")                
            if request.form.get('techs'):
                scripts.append("FlaiNNTestMultiThreadingTech.py") 
            userpath=os.path.join(userdatapath, current_user.username)
            prepareUsersFiles(file, current_user.username, scripts)
            #arguments construction
            txt = request.files['text']
            txtname = "patents.txt"
            if txt.filename != '':
                txtname = txt.filename
                txt.save(os.path.join(userpath,txt.filename))
            args.append(os.path.join(userpath,txtname))
            args.append(st)
            args.append(num)
            args.append(os.path.join(userpath,file.filename))
            args.append(userpath)
            command = ""
            if request.form.get('users'):                
                run_remotely("FlaiNNTestMultiThreading.py", userpath, args)
                output = waitForFile('NNStatistics.txt',userpath,None)
            if request.form.get('techs'):
                run_remotely("FlaiNNTestMultiThreadingTech.py", userpath, args) 
                output += waitForFile('NNStatisticsTech.txt',userpath,None)
            if output!="":
                removeFiles(userpath,["FlaiNNTestMultiThreadingTech.py","FlaiNNTestMultiThreading.py","patents.txt",dataFile])  
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
        if len(str(path))>1:
            wf = open (os.path.join(userpath,"data.txt"), "w", encoding='utf-8')
            wf.write(str(path))  
            wf.close()
        print("POST "+str(path))
        userpath=os.path.join(userdatapath, current_user.username)
        arg="None"
        fileName = ""
        # get user model
        model = request.files['custmod']
        if model.filename != '':
            model.save(os.path.join(userpath,"model.pt"))
        # get patent to take users from
        args=[]        
        args.append(userpath)
        file = request.files['pat']
        if file.filename != '':
            fileName = file.filename   
            args.append(file.filename)
            prepareUsersFiles(file, current_user.username, ["demoForNNFullNN.py"])					
        else:            
            args.append("data.txt")          
            prepareUsersFiles(None, current_user.username, ["demoForNNFullNN.py"])         
        # start processing request
        command = ""
        if request.form.get('users'):  
            shutil.copyfile(os.path.join(os.getcwd(),"trainerNRFinal10Rep","final-model.pt"), os.path.join(userpath, "model.pt"))     
            command = "C:/Users/airer/AppData/Local/Programs/Python/Python36/python.exe " + os.path.join(userpath, "demoForNNFullNN.py") + " " + " ".join(args)
            run_remotely(command)
            output = waitForFile("results.txt",userpath,"results.txt")
        if request.form.get('techs'):
            shutil.copyfile(os.path.join(os.getcwd(),"trainerNRFinal10Rep","final-model_tech.pt"), os.path.join(userpath, "model.pt"))  
            command = "C:/Users/airer/AppData/Local/Programs/Python/Python36/python.exe " + os.path.join(userpath, "demoForNNFullNN.py") + " " + " ".join(args)
            run_remotely(command)
            output += waitForFile("results.txt",userpath,"results.txt")
        if output !="":            
            removeFiles(userpath,["demoForNNFullNN.py","data.txt",fileName,"model.pt"])
    return render_template('getusers.html', inputP=path, outputP=output)


@app.route('/trainnn/', methods=['GET','POST'])
def trainnn():
    path=""
    output=""
    visTr = "hidden"
    args = []
    if request.method == "POST":
        print("POST")
        #training settings area
        inputME = request.form.get('inputME')
        inputLR = request.form.get('inputLR')
        inputPred = request.form['inputPred']
        if inputME == None or inputME=="":
             inputME = "10"
        if inputLR == None or inputLR=="":
             inputLR = "0.1"
        if inputPred == None or inputPred=="":
             inputPred = "ner"
        #file uploading area
        file = request.files['file']
        if file.filename == '':
            output = 'No training set uploaded'
        elif allowed_txt_file(file.filename):
            path = file.filename
            prepareUsersFiles(file, current_user.username, ["FlaiNNTrainingScriptNR.py"])
            userpath=os.path.join(userdatapath, current_user.username)
            args.append(os.path.join(userpath,file.filename))
            args.append(inputPred)
            args.append(inputME)
            args.append(inputLR)
            args.append(userpath)
            run_remotely('FlaiNNTrainingScriptNR.py',userpath,args)
            output = waitForFile(["training.log"],userpath,"final-model.pt") 
            waitForRemoval(["training.log"], userpath, ["FlaiNNTrainingScriptNR.py"])
            visTr = "visible"
            #send_from_directory(os.path.join(userpath,"trainedModel"), "final-model.pt")
        else:
            output="uploaded file has to have .txt extention"
        if (os.path.exists(os.path.join(userpath,"FlaiNNTrainingScriptNR.py"))==True):
            os.remove(os.path.join(userpath,"FlaiNNTrainingScriptNR.py"))
    return render_template('trainnn.html', input=path, results=output, visibleTr=visTr)



@app.route('/login', methods = ['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect('/')
     
    if request.method == 'POST':
        email = request.form['email']
        user = UserModel.query.filter_by(email = email).first()
        if user is not None and user.check_password(request.form['password']):
            login_user(user)
            return redirect('/')     
    return render_template('login.html')

 
@app.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect('/')
     
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
 
        if UserModel.query.filter_by(email=email).first():
            return ('Email already Present')
             
        user = UserModel(email=email, username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    return render_template('register.html')
 
 
@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')




if __name__ == '__main__':
    app.run(debug=True)


