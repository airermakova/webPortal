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


try:
     print("START TO READ CORPUS")
     #init a corpus using column format, data folder and the names of the train, dev and test files
     my_corpus: Corpus = ColumnCorpus(data_folder, columns,
                              train_file=trainset,
                              test_file=trainset,
                              dev_file=trainset)

     #english_corpus = UD_ENGLISH().downsample(0.1)
     #corpus = MultiCorpus([english_corpus , my_corpus]).downsample(0.1)
     corpus = my_corpus

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

except:
    print("EXCEPTION FINISH TRAINING")
    with io.open("training.log",'w',encoding='utf8') as f:
       f.write("trainig failed")
