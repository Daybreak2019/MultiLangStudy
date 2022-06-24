
import os
import csv 
import sys
import pandas as pd
from lib.System import System
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

class Cate():      
    def __init__ (self, id, category, keywords, example, parent=0):
        self.id       = id
        self.category = category
        self.keywords = keywords
        self.parent   = parent
        self.example  = example

class SWCate():
    def __init__ (self, FileName='SoftwareCategory.csv'):
        self.swCates = {}
        self.FileName = FileName
        self.LoadSwCate ()

    def LoadSwCate (self):
        FilePath = "Data/OriginData/" + self.FileName
        df = pd.read_csv(FilePath)
        for index, row in df.iterrows():
            CateId = row['id']
            self.swCates[CateId] = Cate (CateId, row['category'], row['keywords'], 
                                         row['example'], row['parent'])
            print ("[%d]%d -----> %s: %s" %(row['parent'], CateId, row['category'], row['keywords']))


    def FuzzMatch(self, Message, threshhold=90):  
        fuzz_results = {}
        for id, swCate in self.swCates.items ():
            Keywords = eval(swCate.keywords)
            for str in Keywords:
                key_len = len(str.split())
                msg_len = len (Message)
                gram_meg = []

                #print ("key   --->  [%d]%s   -> msg[%d]:%s" %(key_len, str, msg_len, Message))
                if key_len < msg_len:
                    for i in range (0, len (Message)):
                        end = i + key_len
                        if end > msg_len:
                            break
                        msg = " ".join(Message[i:end])
                        gram_meg.append (msg)

                        result = process.extractOne(str, gram_meg, scorer=fuzz.ratio)
                        if (result[1] >= threshhold):
                            fuzz_results[result[0]] = int (result[1])
                            return swCate.category, fuzz_results 
                elif key_len == msg_len:
                    msg = " ".join(Message)
                    gram_meg.append (msg)
                    result = process.extractOne(str, gram_meg, scorer=fuzz.ratio)
                    if (result[1] >= threshhold):
                        fuzz_results[result[0]] = int (result[1])
                        return swCate.category, fuzz_results          
                
        return None, None

    def Categorize (self):
        SumFile = "Data/StatData/Sumreadme.csv"
        df = pd.read_csv(SumFile)
        for index, row in df.iterrows():
            Message = row['summarization'] + row['description']
            Message = Message.split (' ')
            
            topics = eval(row['topics'])
            if len (topics) != 0:
                Message = Message + topics
            
            result, score = self.FuzzMatch (Message)
            if result != None:
                print ("%s  ----> %s" %(result, str(score)))


 
