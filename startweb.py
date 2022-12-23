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
    if(os.path.exists(os.path.join(userpath, pyscriptname))==False):
         shutil.copyfile(pyscriptname, os.path.join(userpath, pyscriptname))
    if(os.path.exists(os.path.join(userpath, "usersList.txt"))==False):
        shutil.copyfile(os.path.join(testmodelpath, "usersList.txt"), os.path.join(userpath, "usersList.txt"))
    if(file is not None):
        file.save(os.path.join(userpath,file.filename))


@ray.remote
def runCommand(command):
    print(command)
    os.system(command)


def run_remotely(command):
    ray.shutdown()
    ray.init()
    start_time = time.time()
    results = ray.get([runCommand.remote(command) for _ in range(os.cpu_count())])
    duration = time.time() - start_time
    print('Sequence size: {}, Remote execution time: {}'.format(command, duration)) 


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in "pt"



@app.route('/uploads/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    # Appending app path to upload folder path within app root folder
    uploads = os.path.join(current_app.root_path)
    # Returning file from appended path
    return send_from_directory(os.getcwd(), "trainnrC1.txt")


@app.route('/downloads/<path:filename>', methods=['GET', 'POST'])
def downloads(filename):
    # Appending app path to upload folder path within app root folder
    userpath=os.path.join(userdatapath, current_user.username)
    # Returning file from appended path
    return send_file(os.path.join(userpath,filename), as_attachment=True)


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
            prepareUsersFiles(file, current_user.username, "prepareTestSetsComplexUsersNoRepeat.py")
            userpath=os.path.join(userdatapath, current_user.username)
            args.append(os.path.join(userpath,file.filename))
            args.append(st)
            args.append(num)
            args.append(userpath)
            command = "C:/Users/airer/AppData/Local/Programs/Python/Python36/python.exe " + str(os.path.join(userpath,'prepareTestSetsComplexUsersNoRepeat.py')) + " " + " ".join(args)
            print(command)
            run_remotely(command)
            with open(os.path.join(userpath,'onlyDetectedUsersNR1.txt'), 'r') as file:
                output = file.read()
            print(os.path.join(userpath,"trainnrC1.txt"))
            send_from_directory(userpath, "trainnrC1.txt")
        else:
            output="uploaded file has to have .txt extention"
        os.remove(os.path.join(userpath,"prepareTestSetsComplexUsersNoRepeat.py"))
    return render_template('gettrainingset.html', outputP=output)


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
            userpath=os.path.join(userdatapath, current_user.username)
            prepareUsersFiles(file, current_user.username, "FlaiNNTestMultiThreading.py")
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
            command = "C:/Users/airer/AppData/Local/Programs/Python/Python36/python.exe " + os.path.join(userpath,"FlaiNNTestMultiThreading.py") + " " + " ".join(args)
            run_remotely(command)
            with open(os.path.join(userpath,'NNStatistics.txt'), 'r') as file:
                output = file.read()
        else:
            output="uploaded file has to have .pt extention"
        os.remove(os.path.join(userpath,"FlaiNNTestMultiThreading.py"))            
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
        args=[]
        if len(str(path))>1:
            cars = str(path).splitlines()
            for c in cars:
                arg+=c.replace(" ","_") + "."
        userpath=os.path.join(userdatapath, current_user.username)
        #file uploading area
        file = request.files['pat']
        
        if file.filename != '':    
            prepareUsersFiles(file, current_user.username, "demoForNNFullNN.py")        
            cars=[]
            with open(os.path.join(os.getcwd(),file.filename), 'r') as file:
               cars += file.read().splitlines()             
            for c in cars:
                arg+=c.replace(" ","_") + "."
            args.append(arg)
            args.append(userpath)
        else:
            prepareUsersFiles(None, current_user.username, "demoForNNFullNN.py") 
        #print(arg)
        if len(arg)>0:
            command = "C:/Users/airer/AppData/Local/Programs/Python/Python36/python.exe " + os.path.join(userpath, "demoForNNFullNN.py") + " " + " ".join(args)
            run_remotely(command)
            with open(os.path.join(userpath,'results.txt'), 'r') as file:
                output = file.read().replace(".", "\n")
        os.remove(os.path.join(userpath,"demoForNNFullNN.py"))
    return render_template('getusers.html', inputP=path, outputP=output)


@app.route('/trainnn/', methods=['GET','POST'])
def trainnn():
    path=""
    output=""
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
            prepareUsersFiles(file, current_user.username, "FlaiNNTrainingScriptNR.py")
            userpath=os.path.join(userdatapath, current_user.username)
            args.append(os.path.join(userpath,file.filename))
            args.append(inputPred)
            args.append(inputME)
            args.append(inputLR)
            args.append(userpath)
            command = "C:/Users/airer/AppData/Local/Programs/Python/Python36/python.exe " + str(os.path.join(userpath,'FlaiNNTrainingScriptNR.py')) + " " + " ".join(args)
            print(command)
            run_remotely(command)
            while os.path.exists(os.path.join(userpath,"trainedModel",'training.log'))==False:
                time.sleep(1)
            with open(os.path.join(userpath,"trainedModel",'training.log'), 'r') as file:
                output = file.read()
            #send_from_directory(os.path.join(userpath,"trainedModel"), "final-model.pt")
        else:
            output="uploaded file has to have .txt extention"
        os.remove(os.path.join(userpath,"FlaiNNTrainingScriptNR.py"))
    return render_template('trainnn.html', input=path, results=output)



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


