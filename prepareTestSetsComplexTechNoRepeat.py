from flair.data import Corpus
from flair.datasets import ColumnCorpus
from flair.embeddings import WordEmbeddings, StackedEmbeddings
from flair.models import SequenceTagger
from flair.trainers import ModelTrainer
from flair.data import Sentence
import re
import os
import sys
import nltk
import numpy
import random
import codecs
import shutil
from threading import *
from langdetect import detect
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')
nltk.download('conll2002')
nltk.download('conll2000')
nltk.download('brown')
nltk.download('universal_tagset')
from nltk import word_tokenize,pos_tag
from nltk.chunk import conlltags2tree, tree2conlltags
from pprint import pprint
from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import words
from nltk.corpus import conll2000, conll2002
from nltk import sent_tokenize
from translate import Translator
from langdetect import detect
from googletrans import Translator, constants
from pprint import pprint



trainSet = []
techs = []
goldsets = []
globalUsers = []
globalCount = []
onlyUsers = []
foundUsers = []
threadsL = []
sema = Semaphore(1)
stemmer = SnowballStemmer("english")


#TO GET PHRASES
def getPhrasesFromFile(fileName, st, fin):
    phrases= []  
    finArr = []  
    tokenized_phrases = []
    try:
       with codecs.open(fileName, 'r', "utf-8") as file:
           phrases = file.read().split(".")
       if fin > len(phrases) or fin == 0:
           return phrases
       for i in range(st,fin):
           finArr.append(phrases[i])
       return finArr
    except Exception as e:
      print("Error in reading " + fileName)
      writeException(e)
      exit()


#TO MARK USERS AS WE HAVE DONE FOR TRAIN SET

def getDataFromFile(fileName):
    users = []        
    try:
       word_file = open (fileName, "r", encoding='utf-8')
       #print("file object created")
       for l in word_file:
           user = l.replace('\r', '').replace('\n', '')
           #    user = stemmer.stem(m)
           #else:
           #    user = m
           users.append(user)
       return users
    except:
      print("Error in reading " + fileName)
      if len(users)>0:
          print(users[len(users)-1])
      exit()

#TO GET ROOTS FROM GOLDEN SETS

def getWordsFromGoldenSet(fileName):
    users = []        
    try:
       word_file = open (fileName, "r", encoding='utf-8')
       print("file object created")
       for l in word_file:
           users.append(l.replace('\r', '').replace('\n', ''))
       return users
    except:
      print("Error in reading " + fileName)
      if len(users)>0:
          print(users[len(users)-1])
      
      exit()


def checkMarkedArrayPresence(phr):
    registeredUser = []
    for phrase in phr:
        nltk_tags = pos_tag(word_tokenize(phrase))  
        iob_tagged = tree2conlltags(nltk_tags) 
        userFound = False
        for user in techs: 
            us = []
            #user = getUserInPatentLanguage(phrase, oneuser)  
            if user in phrase: 
               print(user)   
               if " " in user:                    
                   us = user.split(" ")
               else:
                   print(user)
                   us.append(user)               
                   iob_tagged = markUser(iob_tagged, us)
                   print(iob_tagged)                     
        regStr = ""
        newLen = 0
        allowAppend = False         
        for iob in iob_tagged:
             if iob[2]=="B-label" :
                 regStr = iob[0]             
             if iob[2]=="I-label":
                 regStr += " " + iob[0]
             if iob[2]=="O" and len(regStr)>0:
                 registeredUser.append(regStr)
                 if len(regStr.split(" "))>1:
                     allowAppend = True
                 elif len(regStr)>0 and regStr[len(regStr) - 2:]=="er":
                     allowAppend = True
                 if regStr not in globalUsers:
                     globalUsers.append(regStr)
                     globalCount.append(1)
                 else:
                     ind = globalUsers.index(regStr)
                     globalCount[ind] = globalCount[ind]+1
                 regStr = ""
                 newLen = newLen + 1
        if newLen>0 or len(regStr)>0:
            if regStr!="" and regStr not in globalUsers:
                    globalUsers.append(regStr)
                    globalCount.append(1)
            elif regStr!="":
                    ind = globalUsers.index(regStr)
                    globalCount[ind] = globalCount[ind]+1
            if regStr not in foundUsers or foundUsers.count(regStr)<10:
                    foundUsers.append(regStr)
                    allowAppend = True
            if allowAppend == True:
                onlyUsers.append(iob_tagged)
                print(iob_tagged)
    return onlyUsers

         
def getUserInPatentLanguage(trainSet):
    sent = ""
    usr = ""
    translator = Translator()
    try:
        for ph in trainSet:
            langCode = detect(ph)
            if langCode != "en":
                translated_text = translator.translate(ph,src=langCode, dest="en")
                trainSet.append(translated_text.text)  
                print(translated_text.text)     
    except Exception as e:
       print("Failed to translate non English patents " + str(e))
    
        
       
def markUser(phrase,user):
  try:
    finTuple = []
    found = False       
    if len(user)>1:
       nonFirst = False
       cnt = 0
       ucnt = 0
       for ph in phrase:
           ls = list(ph)
           if ls[2] == "B":
               ls[2] = "B-label"
           if ls[2] == "I":
               ls[2] = "I-label"
           finTuple.append(tuple(ls))
           ucnt = ucnt +1
           found = False
           for u in user: 
               if ph[0]==u:
                   found = True
           if found == True:
               cnt = cnt + 1
           else:
               cnt = cnt - 1           
           if cnt == len(user)-1:             
               ls = list(phrase[ucnt-cnt-1])
               ls[2]="B-label"
               finTuple[ucnt-cnt-1]=tuple(ls)
               for i in range(cnt):
                   ls = list(phrase[ucnt-cnt+i])
                   ls[2]="I-label"
                   finTuple[ucnt-cnt+i]=tuple(ls)
               cnt = 0
    else:
        for i in range(0, len(phrase)):
           ls = list(phrase[i])
           if ls[2] == "B":
               ls[2] = "B-label"
           if ls[2] == "I":
               ls[2] = "I-label"
           finTuple.append(tuple(ls))         
           if phrase[i][0] == user[0] and phrase[i][1][0]=="N":  
               cnt = i-1
               found = False
               while cnt>=0 and phrase[cnt][1]=="JJ" or cnt>=0 and phrase[cnt][1]=="NNP" or cnt>=0 and phrase[cnt][1]=="VBN":
                   ls = list(phrase[cnt])
                   ls[2]="I-label"
                   finTuple[cnt] = (tuple(ls))
                   cnt = cnt - 1 
                   found = True
               ls = list(phrase[i])
               if found == False:
                   ls[2]="B-label"
               else:
                   ls[2]="I-label"
               finTuple[len(finTuple)-1] = (tuple(ls))
               if found == True:
                   ls = list(phrase[cnt+1])
                   ls[2]="B-label"
                   finTuple[cnt+1] = (tuple(ls))
    return finTuple
  except Exception as e:
     writeException(e)


def writeResultFile(trainSet):
    with open(trName, 'a') as f:
        for arr in trainSet:
            for s in arr:
                for st in s:
                    try:
                        f.write((st + " ").encode("utf-8").decode())
                    except:
                        print("error")
                f.write("\n")            
            f.write("\n\n\n") 
        t = 0
    with open(vName, 'a') as v:
        for arr in trainSet:
            t = t+1
            if t>3:
                t = 0
                for s in arr:
                    for st in s:
                        try:
                            v.write((st + " ").encode("utf-8").decode())
                        except:
                            print("error")
                    v.write("\n")
                v.write("\n\n\n") 
        t = 0
    with open(teName, 'a') as te:
        for arr in trainSet:
            t = t+1
            if t>4:
                t = 0
                for s in arr:
                    for st in s:
                        try:
                            te.write((st + " ").encode("utf-8").decode())
                        except:
                            print("error")
                    te.write("\n")
                te.write("\n\n\n") 
     
         
def writeUsersFile():    
    if len(globalUsers) != len(globalCount):
        return
    usersFile = open(os.path.join(path,"onlyDetectedTechsNR.txt"), "w")
    for i in range(0, len(globalCount)):
        usersFile.write(str(globalUsers[i]))
        usersFile.write(": ")
        usersFile.write(str(globalCount[i]))
        usersFile.write("\n") 
    usersFile.close()
    shutil.copyfile(os.path.join(path, "onlyDetectedTechsNR.txt"), os.path.join(path, "onlyDetectedTechsNR1.txt"))
    os.remove(os.path.join(path,"onlyDetectedTechsNR.txt"))


#TO PREPARE USERS RECOGNITION FOR MULTITHREADING
def writeUsers():
    try:
       phr = []  
       threadsL.append(1) 
       while len(trainSet)>0:
           try: 
               sema.acquire()
               finVal = 10
               if len(trainSet)<10:
                  finVal = len(trainSet)            
               for i in range(0,finVal):
                  phr.append(trainSet[i])
               for i in range(0,len(phr)):
                  trainSet.pop(0) 
               sema.release() 
               checkMarkedArrayPresence(phr)
               phr.clear()
           except Exception as e:
               writeException(e)
       threadsL.pop(0)
       #print("THREAD FINISHED " + str(len(threadsL)))
       if len(threadsL)==0:
           writeResultFile(onlyUsers)
           writeUsersFile()
           print("STATISTICS WRITTEN ")
           if os.path.exists(os.path.join(path,dataFileName)):
               os.remove(os.path.join(path,dataFileName))
    except Exception as e:
       writeException(e)
        
def writeException(e):
    print("Raised exception: " + str(e))
    f = open(os.path.join(path, "onlyDetectedTechsNR1.txt"),"w")
    f.write("Failed to prepare train set. Exception: "+ str(e))
    f.close()


#MAIN SCRIPTS

try:   
   dataFileName = str(sys.argv[1])
   print(dataFileName)
   phSt = int(sys.argv[2])
   print(phSt)
   phNum = int(sys.argv[3])
   print(phNum)
   path = str(sys.argv[4])
   print(path)
   trName = str(os.path.join(path,"trainthC1.txt"))
   vName = str(os.path.join(path,"valthC1.txt"))
   teName = str(os.path.join(path,"testthC1.txt"))
   tr = open(trName, "w")
   v = open(vName, "w")
   te = open(teName, "w")
   tr.close()
   v.close()
   te.close()
   #TO GET DATA FROM TEST FILE AND USERS FILE
   testmodelpath= os.path.join(os.getcwd(),"trainmodel")
   trainSet = getPhrasesFromFile(dataFileName, phSt, phNum)
   print("Taken phrases - " + str(trainSet))
   techs = getDataFromFile(os.path.join(testmodelpath,"techList.txt"))
   print("Taken techs - " + str(len(techs)))
   getUserInPatentLanguage(trainSet)
   #goldsets = getWordsFromGoldenSet("GoldenSet.txt")
   #print("Taken goldsets - ")
   #print(len(goldsets))
   rep = 0
   i=0

   threads = []
   for cnt in range(0,10):
      threads.append(Thread(target=writeUsers))


   for ph in threads:
       #print("thread start")
       ph.start()

except Exception as e:
    writeException(e)




