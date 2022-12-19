from flask import Flask, render_template, Response, request, redirect, url_for, send_from_directory, current_app, send_file
from urllib.request import urlopen
import mechanicalsoup
from flask import Flask,render_template,request,redirect
from flask_login import login_required, current_user, login_user, logout_user
from models import UserModel,db,login
import sys
import os

testmodelpath=os.getcwd()+"/testmodel"

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


@app.route('/uploads/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    # Appending app path to upload folder path within app root folder
    uploads = os.path.join(current_app.root_path)
    # Returning file from appended path
    return send_from_directory(os.getcwd(), "trainnrC1.txt")


@app.route('/downloads/<path:filename>', methods=['GET', 'POST'])
def downloads(filename):
    # Appending app path to upload folder path within app root folder
    uploads = os.path.join(current_app.root_path)
    # Returning file from appended path
    return send_file(os.path.join(os.getcwd(),filename), as_attachment=True)


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


