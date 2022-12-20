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


markedPhrasesFileName = "markedPhrasesFullNN.txt"
model = SequenceTagger.load(os.getcwd() + "/trainerNRFinal10Rep/final-model.pt")
if model is not None:
    print("MODEL LOADED")
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
    fusers = extractUsers(sent)
    return fusers

def extractUsers(sent):
    changedsent = sent.replace("[","").replace("]","").replace("<","").replace(">","")
    words = changedsent.split(",")    
    for wrd in words:
        user = wrd.split("/")
        if len(user)>1:
            us = ''.join(e for e in user[0] if e.isalnum())
            if user[1]=="B": 
                arg = us+" "               
                users.append(arg)
            elif user[1]=="I":
                users[len(users)-1] += us + " "
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
        print("STATISTICS WRITTEN ")
    

text = str(sys.argv[1])
path = str(sys.argv[2])
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

