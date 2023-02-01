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
import codecs
import shutil
from flair.embeddings import FlairEmbeddings, TransformerWordEmbeddings
from threading import *

valFileTr = "trn.txt"
valFileNm = "val.txt"
valFileTs = "tst.txt"
print(sys.argv)
trainset = str(sys.argv[1])
colName = str(sys.argv[2])
maxEpoch = int(sys.argv[3])
learnRate = float(sys.argv[4])
path = str(sys.argv[5])
print("ARGUMENTS READ")

start = 0
length = 3000

# define columns
columns = {0: 'text', 1: 'pos', 2: colName}

# this is the folder in which train, test and dev files reside
data_folder=path

fileHandle = open(trainset, "r", encoding="utf8")
texts = fileHandle.readlines()
fileHandle.close()

#prepare validation, test and training sets
def prepareVal(fileNm, st, fn):
    fileHandle = open(fileNm, "w", encoding="utf8")
    if len(texts)<st: 
        for i in texts: 
            fileHandle.write(i)
    elif len(texts)>st and len(texts)<(st+fn):
        print(texts[st])
        for i in range(st,len(texts)-st):
            fileHandle.write(texts[i])
    elif len(texts)>(st+fn):
        print(texts[st])
        for i in range(st,fn+st):
            fileHandle.write(texts[i])
    fileHandle.close()

def writeexception(e):
    print("EXCEPTION FINISH TRAINING" + str(e))
    with codecs.open(os.path.join(path,"training.log"),'w', "utf-8") as f:
       f.write("trainig failed" + str(e))


#control if all training set processed
def trainChecker():
     try:
        start = 0
        length = int(len(texts)/5)
        corpuses = []
        while((start+length)<=len(texts)-1):
           print("START CORP READING")
           prepareVal(os.path.join(path, valFileTr), start, length)
           my_corpus: Corpus = ColumnCorpus(data_folder, columns,
                              train_file=valFileTr,
                              test_file=valFileTs,
                              dev_file=valFileNm,
                              in_memory=False)
           corpuses.append(my_corpus)
           start = start + length
           print("STOP CORP READING")
        train(corpuses)
        print("FINISH TRAINING")
        shutil.copy(os.path.join(path,"trainedModel","training.log"), os.path.join(path,"training.log"))
     except Exception as e:
        writeexception(str(e))


#training neural network function
def train(corpuses):
     #prepareVal(os.path.join(path, valFileTr), start, length)
     print("START TO READ CORPUS")

     #init a corpus using column format, data folder and the names of the train, dev and test files
     #my_corpus: Corpus = ColumnCorpus(data_folder, columns,
     #                         train_file=valFileTr,
     #                         test_file=valFileTs,
     #                         dev_file=valFileNm,
     #                         in_memory=False)

     #english_corpus = UD_ENGLISH().downsample(0.1)
     if len(corpuses)<5: 
         with io.open(os.path.join(path,"training.log"),'w',encoding='utf8') as f:
             f.write("trainig failed, corpus length less than 5")
         return 
     corpus = MultiCorpus([corpuses[0], corpuses[1], corpuses[2], corpuses[3], corpuses[4]]).downsample(0.1)
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
     #bert_embedding = TransformerWordEmbeddings('bert-base-multilingual-cased')
     embeddings = StackedEmbeddings(embedding_types)

     print("EMBEDDINGS")

     # 5. initialize sequence tagger
     tagger = SequenceTagger(hidden_size=256,
                        embeddings=embeddings,
                        tag_dictionary=label_dict,
                        tag_type=label_type,
                        use_crf=True)

     # 6. initialize trainer
     print("INIZIALIZE TRAINER")
     trainer = ModelTrainer(tagger, corpus)

     # 7. check if another trained model exists
     pt = os.path.join(data_folder, "trainedModel", "final-model.pt")
     if(os.path.exists(pt)):
        # 8. resume training
        print("RESUME TRAINING")
        trained_model = SequenceTagger.load(pt)
        trainer.resume(trained_model,
              base_path=os.path.join(path,"trainedModel"),
              mini_batch_size=32,
              mini_batch_chunk_size=2,
              embeddings_storage_mode='cpu',
              max_epochs=maxEpoch
               )
     else:
         # 9. start training
         print("START TRAINING")
         trainer.train(os.path.join(path,"trainedModel"),
              learning_rate=learnRate,
              mini_batch_size=32,
              mini_batch_chunk_size=2,
              embeddings_storage_mode='cpu',
              max_epochs=maxEpoch)
         print("FINISH TRAINING STAGE")


try:

     prepareVal(os.path.join(path, valFileNm), 0, int(len(texts)/5))
     prepareVal(os.path.join(path, valFileTs), 0, int(len(texts)/5))
     mainThread = Thread(target=trainChecker)     
     mainThread.start()

except Exception as e:
    writeexception(str(e))
