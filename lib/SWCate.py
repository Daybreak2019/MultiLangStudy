
import os
import csv 
import sys
import pandas as pd
from lib.System import System
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

app_lib_cate_id = 5

class Cate():      
    def __init__ (self, id, category, keywords, example, parent=0):
        self.id       = id
        self.category = category
        self.keywords = keywords
        self.parent   = parent
        self.example  = example

class SWCate():
    def __init__ (self, FileName='SoftwareCategory.csv', CateAct=True):
        self.swCates = {}
        self.FileName = FileName
        self.LoadSwCate ()

        self.Output = System.getdir_stat() + "RepoCategory.csv"
        if CateAct == True:
            with open (self.Output, 'w') as Rcf:
                writer = csv.writer(Rcf)
                writer.writerow(['repo_id', 'message', 'cate_id', 'cate', 'fuzz_res'])

    def SaveResult (self, RepoId, Message, CateId, Cate, FuzzRes):
        row = [RepoId, Message, CateId, Cate, FuzzRes]
        with open (self.Output, 'a') as Rcf:
            writer = csv.writer(Rcf)
            writer.writerow(row)
        
    def LoadSwCate (self):
        FilePath = "Data/OriginData/" + self.FileName
        df = pd.read_csv(FilePath)
        for index, row in df.iterrows():
            CateId = row['id']
            self.swCates[CateId] = Cate (CateId, row['category'], row['keywords'], 
                                         row['example'], row['parent'])
            #print ("[%d]%d -----> %s: %s" %(row['parent'], CateId, row['category'], row['keywords']))
        return self.swCates

  
    def FuzzMatch(self, Message, SpecCateId, threshhold=85):  
        fuzz_results = {}
        for CateId in range (len (self.swCates), 0, -1):
            if SpecCateId != 0:
                if CateId != SpecCateId:
                    continue
            else:
                if CateId == app_lib_cate_id:
                    continue
            
            swCate = self.swCates.get (CateId)
            if swCate == None:
                continue

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
                            return swCate.id, swCate.category, fuzz_results 
                elif key_len == msg_len:
                    msg = " ".join(Message)
                    gram_meg.append (msg)
                    result = process.extractOne(str, gram_meg, scorer=fuzz.ratio)
                    if (result[1] >= threshhold):
                        fuzz_results[result[0]] = int (result[1])
                        return swCate.id, swCate.category, fuzz_results          
                
        return None, None, None

    def Categorize (self):
        SumFile = System.getdir_stat() + "Sumreadme.csv"
        df = pd.read_csv(SumFile)
        for index, row in df.iterrows():
            repo_id = int (row ['id'])
            #if repo_id != 29028775:
            #    continue
            
            tokens = eval (row ['tokens'])
            if len (tokens) != 0:
                Message = row['summarization'] + row['description']
            else:
                Message = row['description']
            Message = Message.split (' ')[0:1000]
            
            topics = eval(row['topics'])
            if len (topics) != 0:
                Message = Message + topics
            
            cate_id, result, score = self.FuzzMatch (Message, 0)
            if result != None:
                print ("[%d]%s  ----> %s" %(index, result, str(score)))
                self.SaveResult (row['id'], Message, cate_id, result, str(score))
            else:
                cate_id, result, score = self.FuzzMatch (Message, app_lib_cate_id)
                if result != None:
                    print ("[%d]%s  ----> %s" %(index, result, str(score)))
                    self.SaveResult (row['id'], Message, cate_id, result, str(score))


    def CategorizeOne (self, Message):
        cate_id, result, score = self.FuzzMatch (Message, 0)
        print ("%s  ----> %s" %(result, str(score)))
        if result == None:
            cate_id, result, score = self.FuzzMatch (Message, app_lib_cate_id)
            print ("%s  ----> %s" %(result, str(score)))
            return result
        else:
            return result


 
