from __future__ import print_function

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction import text

from sklearn import tree, ensemble #decision tree & random forest
from sklearn import neighbors #knn
from sklearn import naive_bayes

import logging
import sys
from time import time
import os

import numpy as np
import collections
import pandas as pd

from my_pipeline import *


from sklearn import pipeline
from sklearn import feature_selection #feature selection
from sklearn import cross_validation #cross val
from sklearn import metrics

from sklearn import grid_search


# Display progress logs on stdout
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')


###############################################################################

#Function for clearly printing a dictionary's values
def dictPrint(dictIn):
  try: 
    for attribute, value in dictIn.items():
      print('{} : {}'.format(attribute, value))
    print('\n')
  except:
    f1.write('\n =============================== \n PRINTING ISSUE \n =============================== \n')

###############################################################################




################ 1. Get and prep data: choose a vectorizer, dummy code labels

#### a. get data
documentDict = getDocs()
documentDict = classify(documentDict)#documentDict contains key=matter_id, value=(title, text, classification/None)

#pull data from documentDict
t0 = time()
labeled_ids = []
labeled_titles = []
labeled_text = []
labels = []

unlabeled_ids = []
unlabeled_titles = []
unlabeled_text = []
for key in documentDict.keys():
    if documentDict[key][2] == None:
        unlabeled_ids = unlabeled_ids + [key]
        unlabeled_titles = unlabeled_titles + [documentDict[key][0]]
        unlabeled_text = unlabeled_text + [documentDict[key][1]]
    else:
        labeled_ids = labeled_ids + [key]
        labeled_titles = labeled_titles + [documentDict[key][0]]
        labeled_text = labeled_text + [documentDict[key][1]]
        labels = labels + [documentDict[key][2]]
print("Copying from documentDict done in %fs" % (time() - t0))

##### b. initialize a vectorizer
t0 = time()

#Option 1: TF-IDF


#my_stop_words = text.ENGLISH_STOP_WORDS.union({"designation", "amendment", "municipal", "code"})
vectorizer = TfidfVectorizer(analyzer='word', max_df=0.5, #max_features=5,
                                 min_df=0.25, stop_words='english',
                                 ngram_range=(2, 3)
				)

#Option 2: Perform an IDF normalization on the output of HashingVectorizer
#hasher = HashingVectorizer(#n_features=opts.n_features,
#                                   stop_words='english', non_negative=True,
#                                   norm=None, binary=False, ngram_range=(1, 3))
#vectorizer = pipeline.make_pipeline(hasher, TfidfTransformer())


#### c. apply vectorizer to labeled and unlabeled titles
X_all = vectorizer.fit_transform(labeled_text+unlabeled_text)
k = len(labels)
X_matrix = X_all[:k,:]
X_matrix_unlab = X_all[k:,:]

print("vectorizer dimensions (all data): " + str(X_all.shape))
print("vectorizer done in %fs" % (time() - t0))

####### d. dummy code labels

def to_ints(my_list):
    #function to code all variables as integers

    values = set(my_list) #get unique values
    
    #create conversion dictionary
    conversion = dict()
    for pos, val in enumerate(values):
        conversion[val] = pos

    dictPrint(conversion)
    #convert all entries
    my_list = list(map(lambda val: conversion[val], my_list))
    return my_list

t0 = time()
label_dum = np.asarray(to_ints(labels))
print("labels dimensions: " + str(label_dum.shape))
print("dummy coding done in %fs" % (time() - t0))

###############################################################################

###################### 2. pipeline it all together 
############ feature select, classify, test-set validate, report

selector = feature_selection.SelectKBest(k=100)
classifier = naive_bayes.MultinomialNB(class_prior = np.reshape(np.repeat(np.array([[1.0/12.0]]),12,axis=1), (12,))) #flat priors

steps = [('feature_selection', selector), ('multinomial_nb', classifier)]

pipeline = pipeline.Pipeline(steps)
 
t0 = time()
X_train, X_test, y_train, y_test = cross_validation.train_test_split(X_matrix, label_dum, test_size=0.33, random_state=30)
print("X_train dimensions: " + str(X_train.shape))
print("y_train dimensions: " + str(y_train.shape))

### fit your pipeline on X_train and y_train
pipeline.fit( X_train, y_train )
### call pipeline.predict() on your X_test data to make a set of test predictions
y_prediction = pipeline.predict( X_test )
### test your predictions using sklearn.classification_report()
report = metrics.classification_report( y_test, y_prediction )
### and print the report
print("Classifying unlabeled data done in: %fs" % (time()-t0))
print(report)

kfeatures = np.asarray(selector.get_support(indices=True))
print(np.asarray(vectorizer.get_feature_names())[kfeatures])

#################################################################
###### 3. Use classifier on unlabelled data

pred_unlab = pipeline.predict(X_matrix_unlab).tolist()

directory = 'results'
if not os.path.exists(directory):
    os.makedirs(directory)

probs = np.asmatrix(pipeline.predict_proba(X_matrix_unlab))

for i in range(len(unlabeled_titles)):
    m = max(max(probs[i,:].tolist()))
    if m < .5:
        filename = directory + '/unsorted'
        output_file = open(filename, 'a')
        output_file.write("%s\n" % unlabeled_titles[i])
        output_file.close()
    else:
        filename = directory + '/{}'.format(pred_unlab[i])
        output_file = open(filename, 'a')
        output_file.write("%s\n" % unlabeled_titles[i])
        output_file.close()


