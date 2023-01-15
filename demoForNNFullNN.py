from flair.data import Corpus
from flair.datasets import ColumnCorpus
from flair.embeddings import WordEmbeddings, StackedEmbeddings
from flair.models import SequenceTagger
from flair.trainers import ModelTrainer
from flair.data import Sentence
import sys
import os
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
priorPosList=["NN","JJ"]
lastPosList=["NN","RB","DT"]

path = str(sys.argv[1])
fname = str(sys.argv[2])

pt = os.path.join(path,"model.pt")
print(pt)


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

def getUsers(p):
    sent = markSentence(p)
    fusers = extractUsers(sent, p)
    return fusers

def extractUsers(sent, phrase):
    changedsent = sent.replace("[","").replace("]","").replace("<","").replace(">","")
    pos = list(pos_tag(phrase.split(" ")))    
    words = changedsent.split(",")  
    i=0
    for wrd in words:
        user = wrd.split("/")
        if len(user)>1:
            us = ''.join(e for e in user[0] if e.isalnum())
            if user[1]=="B" and pos[i][1] in priorPosList: 
                arg = us+" "               
                users.append(arg)
            elif user[1]=="I" and pos[i][1] in lastPosList:
                users[len(users)-1] += us + " "
        i=i+1
    return users


def markSentence(p):
    sentence = Sentence(p)
    model.predict(sentence)
    sent = sentence.to_tagged_string()
    return sent

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
                for i in range(0,len(phrases)):
                    phr.append(phrases[i]) 

            for i in range(0,len(phr)):
                phrases.pop(0) 
            sema.release() 
            for p in phr:
                us = getUsers(p)                
        except:
            print("Exception")     
    threadsL.pop(0)
    print("THREAD FINISHED " + str(len(threadsL)))
    if len(threadsL)<=1:        
        finUsers=[]
        f = open(os.path.join(path, "results.txt"),"w")
        print(len(users))
        for us in users:
            ar = ''.join(str(u) for u in us)
            if ar not in finUsers:
                finUsers.append(ar)
        for us in finUsers:
                print("user - " + us)
                f.write(us+".")
        f.close()
        if os.path.exists(pt):
            os.remove(pt)
        if os.path.exists(os.path.join(path, fname)):
            os.remove(os.path.join(path, fname))
        print("STATISTICS WRITTEN ")

    
if os.path.exists(os.path.join(path, "results.txt"))==True:
    f = open(os.path.join(path, "results.txt"),"w")
    f.close()

if fname!=None:
    word_file = open (os.path.join(path, fname), "r", encoding='utf-8')
    for l in word_file:
           phrases.append(l.replace('\r', '').replace('\n', ''))

try:
    model = None
    if os.path.exists(os.path.join(path, "model.pt")):
        model = SequenceTagger.load(os.path.join(path, "model.pt"))
    else:
        model = SequenceTagger.load(pt)
    if model is not None:
        print("MODEL LOADED")      

    threads = []
    for cnt in range(0,10):
        threads.append(Thread(target=writeUsers))


    for ph in threads:
        print("thread start")
        ph.start()

except Exception as e:
    print("Raised exception: " + str(e))
    f = open(os.path.join(path, "results.txt"),"w")
    f.write("Failed to get users")
    f.close()

