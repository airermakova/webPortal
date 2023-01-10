from flair.data import Corpus
from flair.datasets import ColumnCorpus
from flair.embeddings import WordEmbeddings, StackedEmbeddings, FlairEmbeddings
from flair.models import SequenceTagger
from flair.trainers import ModelTrainer
from flair.data import MultiCorpus
from flair.datasets import UD_ENGLISH
import sys
import os
import io
from threading import *


valFileNm = "val.txt"
valFileTs = "tst.txt"
corpuses = []
threads = []
sema = Semaphore(1)

trainset = str(sys.argv[1])
colName = str(sys.argv[2])
maxEpoch = int(sys.argv[3])
learnRate = float(sys.argv[4])
path = str(sys.argv[5])
print("ARGUMENTS READ")

# define columns
columns = {0: 'text', 1: 'pos', 2: colName}

# this is the folder in which train, test and dev files reside
data_folder=path

fileHandle = open(trainset, "r", encoding="utf8")
texts = fileHandle.readlines()
fileHandle.close()

print("INPUT READ")
crpLen = len(texts)

def prepareVal(fileNm, st, fn):
    fileHandle = open(fileNm, "w", encoding="utf8")
    if len(texts)<st or len(texts)<fn:
        for i in texts: 
            fileHandle.write(i)
    elif len(texts)>fn:
        for i in range(st,fn+st):
            fileHandle.write(texts[i])
    fileHandle.close()


def prepareCorp(fileNm, vl, ts, st, div):
    prepareVal(os.path.join(path, vl), 0, 50)
    prepareVal(os.path.join(path, ts), 0, 30)
    stVal = int(st*crpLen/div)
    Ln = int(crpLen/div)
    prepareVal(os.path.join(path, fileNm), stVal, Ln)
    my_corpus: Corpus = ColumnCorpus(data_folder, columns,
                              train_file=fileNm,
                              test_file=ts,
                              dev_file=vl)
    sema.acquire()
    corpuses.append(my_corpus)
    sema.release()
    threads.pop(0)
    print("TREAD FINISH")
    if len(threads)==0:
        startTraining()

try:    
    for cnt in range(0,3):
        fn = "tr" + str(cnt) + ".txt"
        vl = "vl" + str(cnt) + ".txt"
        ts = "ts" + str(cnt) + ".txt"
        print("create thread")
        processThread = Thread(target=prepareCorp, args=[fn, vl, ts, cnt, 3])
        print("thread created")
        threads.append(processThread)


    for ph in threads:
        print("thread to create corpus started")
        ph.start()


    print("START TO PREPARE VALIDATION")


except Exception as e:
    print("EXCEPTION FINISH TRAINING" + str(e))
    with io.open("training.log",'w',encoding='utf8') as f:
       f.write("trainig failed")

def startTraining():
 try:
     print("START TO TRAINING")
     #init a corpus using column format, data folder and the names of the train, dev and test files
     #my_corpus: Corpus = ColumnCorpus(data_folder, columns,
     #                         train_file=trainset,
     #                         test_file=valFileTs,
     #                         dev_file=valFileNm)

     #english_corpus = UD_ENGLISH().downsample(0.1)
     corpus = MultiCorpus([corpuses[0], corpuses[1], corpuses[2]]).downsample(0.1)
     #corpus = my_corpus

     print("CORPUS READ")
     print(len(corpus.train))


     # 2. what label do we want to predict?
     label_type = colName

     # 3. make the label dictionary from the corpus
     label_dict = corpus.make_label_dictionary(label_type=label_type)

     print("DICTIONARY READ")
     print(label_dict)

     # 4. initialize embedding stack with Flair and GloVe
     embedding_types = [
        WordEmbeddings('glove'),
        #FlairEmbeddings('news-forward'),
        #FlairEmbeddings('news-backward'),
      ]

     embeddings = StackedEmbeddings(embeddings=embedding_types)


     print("EMBEDDINGS")

     # 5. initialize sequence tagger
     tagger = SequenceTagger(hidden_size=256,
                        embeddings=embeddings,
                        tag_dictionary=label_dict,
                        tag_type=label_type,
                        use_crf=True)

     # 6. initialize trainer
     trainer = ModelTrainer(tagger, corpus)

     # 7. start training
     trainer.train(os.path.join(path,"trainedModel"),
              learning_rate=learnRate,
              mini_batch_size=32,
              mini_batch_chunk_size=2,
              embeddings_storage_mode='cpu',
              max_epochs=maxEpoch)
     print("FINISH TRAINING")

 except Exception as e:
    print("EXCEPTION FINISH TRAINING")
    with io.open("training.log",'w',encoding='utf8') as f:
       f.write("trainig failed")
