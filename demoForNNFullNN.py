from flair.data import Corpus
from flair.datasets import ColumnCorpus
from flair.embeddings import WordEmbeddings, StackedEmbeddings
from flair.models import SequenceTagger
from flair.trainers import ModelTrainer
from flair.data import Sentence
import sys
import re
import nltk
import numpy
import random
import codecs
from langdetect import detect
from threading import *
import time
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

phrases = []
fphrases = []
users = []
allSimUsers = []
allComUsers = []
usersCounts = []
comUsersCounts = []
threadsL = []
sema = Semaphore(1)
simpleF = open("markedSimpleUsersOnlyFullNN.txt", "w")
markedPhrasesFile = open("markedPhrasesFullNN.txt", "w")
complexPhrasesFile = open("markedComplexUsersOnlyFullNN.txt", "w")
userStatistics = open("markedUsersStatisticsFullNN.txt", "w")

#simpleF.close()
markedPhrasesFile.close()
#complexPhrasesFile.close()
#userStatistics.close()
#usersNotInListFile.close()

markedPhrasesFileName = "markedPhrasesFullNN.txt"

model = SequenceTagger.load("C:/Users/airer/Documents/Pisa/Classifier/trainerNRFinal10Rep/final-model.pt")

#TO GET PHRASES
def getPhrasesFromFile(phr):
    phrases= []  
    finArr = []  
    tokenized_phrases = []
    try:
       phrases = phr.split(".")
       return phrases
    except:
      print("Error in reading " + fileName)
      exit()

#TO MARK USERS AS WE HAVE DONE FOR TRAIN SET

def getDataFromFile(fileName):
    users = []        
    try:
       word_file = open (fileName, "r", encoding='utf-8')
       print("file object created")
       for l in word_file:
           users.append(l.replace('\r', '').replace('\n', ''))
       word_file.close()
       return users
    except:
      print("Error in reading " + fileName)
      if len(users)>0:
          print(users[len(users)-1])
      exit()

#TO MARK USERS IN PHRASES 

def markUsers(phrases):
    finArr = []
    for phrase in phrases:
       marked = getUsersFromNN(phrase)
       #print(marked)
       finArr.append(marked)
    return finArr    

   
def getUsersFromNN(phrase):
    # create example sentence
    sentence = Sentence(phrase)
    # predict tags and print
    model.predict(sentence)
    sent = sentence.to_tagged_string()
    onlusers = sent.split("[")
    #create tuples
    onlyUsers = []
    if len(onlusers)<2:
        return onlyUsers
    tupleArr = onlusers[1].split(",")
    if len(tupleArr)<1:
        return onlyUsers
    for tp in tupleArr: 
        t = tp.split("/")
        if len(t)>1:
            if t[1] == "<unk>" or t[1] == "<unk>]":
                t[1] = "O"
            onlyUsers.append(tuple(t))
    return onlyUsers

#TO STORE MARKED PHRASES IN FINAL FILE

def writeUsersFile(finalArray):
    finStr = ""
    for arr in finalArray:
           finStr = finStr + (' '.join(str(s) for s in arr) + "\n\n") 
    with open(markedPhrasesFileName, 'a') as f:    
        f.write(finStr.encode("utf-8").decode())  


def writeOnlySimpleUsersFile(finalArray):
    for i in range(0, len(finalArray)-2):
        found = False
        wr = False
        arr = list(finalArray[i])
        for y in range(0, len(arr)-2):
            for s in arr[y]:
                 if s == "B":
                     found = True
            if found == True:
                for s in arr[y+1]:
                    if s!= "I":
                        wr = True
        if wr == True:
            simpleF.write(' '.join(str(s) for s in finalArray[i]) + "\n\n")  



def writeOnlyComUsersFile(finalArray):    
    for i in range(0, len(finalArray)-2):
        found = False
        wr = False
        arr = list(finalArray[i])        
        for y in range(0, len(arr)-2):
            for s in arr[y]:
                 if s == "B":
                     found = True
            if found == True:
                for s in arr[y+1]:
                    if s == "I":
                        wr = True
        if wr == True:
            complexPhrasesFile.write(' '.join(str(s) for s in finalArray[i]) + "\n\n") 


def getUsersStatistics(finalArray):           
     for i in range(0, len(finalArray)-2):
        found = False
        wr = False
        arr = list(finalArray[i])
        for y in range(0, len(arr)-2):
            for s in arr[y]:
                 suser = s
                 if s == "B":
                     found = True
            if found == True:
                for s in arr[y+1]:
                    if s == "I":
                        wr = True
        if wr == True:
            str = ""
            for y in range(0, len(arr)-2):
                us = list(arr[y])
                if us[1] == "B": 
                    str = us[0]
                if us[1] == "I":
                    str = str + " " + us[0]
                if us[1]!="B" and us[1]!="I" and len(str)>0:
                    if str not in allComUsers: 
                        allComUsers.append(str)
                        comUsersCounts.append(1)
                    else: 
                        ind = allComUsers.index(str)
                        if ind>=0:
                            comUsersCounts[ind] = comUsersCounts[ind] + 1                   
        elif wr == False and found == True:
            for y in range(0, len(arr)-2):
                us = list(arr[y])
                if us[1] == "B":
                    if us[0] not in allSimUsers: 
                        allSimUsers.append(us[0])
                        usersCounts.append(1)
                    else: 
                        ind = allSimUsers.index(us[0])
                        if ind>=0:
                            usersCounts[ind] = usersCounts[ind] + 1
                    

def writeUsersStatFile():   
    for i in range(0, len(allSimUsers)-1):
        tw = allSimUsers[i] + "-" + str(usersCounts[i]) + "\n"
        simpleF.write(tw)
        userStatistics.write(tw)
    for i in range(0, len(allComUsers)-1):
        tw = allComUsers[i] + "-" + str(comUsersCounts[i])+ "\n"
        userStatistics.write(tw)
        complexPhrasesFile.write(tw)
            
def printData():
    print(allSimUsers)
    print(allComUsers)


#MAIN SCRIPT

def writeUsers():
    phr = []  
    threadsL.append(1) 
    while len(phrases)>1:
        try: 
            sema.acquire()
            if len(phrases)>=10:
                for i in range(0,10):
                    phr.append(phrases[i]) 
            else:
                phr = phrases
            for i in range(0,len(phr)):
                phrases.pop(0)   
            sema.release()   
            finalArray = markUsers(phr)
            getUsersStatistics(finalArray) 
            writeUsersFile(finalArray)     
            printData()
        except:
            print("Exception")     
    threadsL.pop(0)
    print("THREAD FINISHED " + str(len(threadsL)))
    if len(threadsL)<=1:
        writeUsersStatFile()
        print("STATISTICS WRITTEN ")
    

text = str(sys.argv[1])
textdata = text.replace("_", " ")
print("INPUT TEXT " + textdata)

phrases = getPhrasesFromFile(textdata)
print("Taken phrases - " + str(len(phrases)))
print(phrases)

threads = []
for cnt in range(0,10):
    threads.append(Thread(target=writeUsers))


for ph in threads:
    print("thread start")
    ph.start()

