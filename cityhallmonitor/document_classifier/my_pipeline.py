from __future__ import print_function

import sys
from time import time
import os

import psycopg2
import collections

from title_analysis import *

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

def getDocs():
    print("loading city hall monitor documents")

    documents = []
    titles = []

    ############ Connect to the database
    try:
        conn = psycopg2.connect(database='cityhallmonitor',user='cityhallmonitor',password='cityhallmonitor',host='localhost')
               #psycopg2.connect("dbname='cityhallmonitor' user='Bomani' host='localhost' password='wolfbite1'")
        print("Database Connected!")
    except:
        print("I am unable to connect to the database")

    cur = conn.cursor()
    t0 = time()
    cur.execute('select matter_attachment_id, title, text from cityhallmonitor_document')
    # cur.execute('select matter_attachment_id, title, text from cityhallmonitor_matter m , cityhallmonitor_matterattachment ma , cityhallmonitor_document d where m.id=ma.matter_id and ma.id=d.matter_attachment_id')

    ############ Format data: make a dictionary of keys:values = matter_id:[title, text]
    documentDict = {}
    for row in cur:
      documentDict[row[0]] = [row[1], row[2]]

    print("%d documents" % len(documentDict.keys()))
    print()
    print("getDocs() done in %fs" % (time() - t0))

    return documentDict

#####################################

def classify(documentDict):
    t0 = time()

    #Classify all titles
    keys = documentDict.keys()

    for key in keys:
        title = documentDict[key][0]
        title = cleanTitle(title)
        result = classifyTitle(title)
        documentDict[key][0] = title #replace with clean title
        documentDict[key] = documentDict[key] + [result]

    #documentDict now contains key=matter_id, value=(title, text, classification/None)
    print("classify() done in %fs" % (time() - t0))
    return documentDict

######################## Print classifications:

def makeGroups():
    documentDict = getDocs()
    documentDict = classify(documentDict)


    count = 0.0
    keys = documentDict.keys()
    for key in keys:
        result = documentDict[key][2]
        if result == None:
            count +=1
        else:
            directory = 'results'
            if not os.path.exists(directory):
              os.makedirs(directory)

            filename = directory + '/{}'.format(result)
            output_file = open(filename, 'a')
            output_file.write("%s\n" % documentDict[key][0])
            output_file.close()

    print("No. files remaining: " + str(count) + " - " + str(count/len(list(keys))) + "%")


