
import os
import re
import csv
import pandas as pd
from lib.Process_Data import Process_Data
from lib.Collect_Research_Data import Collect_Research_Data
from lib.TextModel import TextModel
from eazymind.nlp.eazysum import Summarizer


class SumItem ():
    def __init__(self, id, summarization, tokens, topics, description):
        self.id = id
        self.summarization = summarization
        self.tokens = tokens
        self.topics = topics
        self.description = description

class Sumreadme (Collect_Research_Data):
    def __init__(self, StartNo=0, EndNo=65535, file_name='Sumreadme'):
        super(Sumreadme, self).__init__(file_name=file_name)
        self.StartNo = StartNo
        self.EndNo   = EndNo
        self.Index   = 0
        self.EasyMind = Summarizer('b889f099ad771f4f693208979f247b1f')
        self.Filters  = ['](http', '<p', '<a', '<div', '<td', '</td>', '<br', '<img', '<tr', '</tr>', '<!--', '- [',
                         'src=', '</a>', '/>', 'http://', 'https://']
        self.TM = TextModel ()
        self.RdSum = {}

        # Default file
        self.SfFile = self.file_path + 'Sumreadme.csv'
        
        if not os.path.exists (self.SfFile):
            Header = ['id', 'summarization', 'tokens', 'topics', 'description']       
            with open(self.SfFile, 'w', encoding='utf-8') as CsvFile:       
                writer = csv.writer(CsvFile)
                writer.writerow(Header)
        else:
            self.LoadRdSum ()

        self.ReadMeInfo = {}
        ReadMeFile = self.file_path + "ReadMeData.csv"
        if os.path.exists (ReadMeFile):
            df = pd.read_csv(ReadMeFile)
            for index, row in df.iterrows():
                repo_id = row ['id']
                readme  = str(row ['readme'])
                if readme == 'nan':
                    continue
                
                self.ReadMeInfo[repo_id] = readme

    def LoadRdSum (self):
        RsFile = self.file_path + 'Sumreadme.csv'
        if not os.path.exists (RsFile):
            return
        df = pd.read_csv(RsFile)
        for index, row in df.iterrows():
            self.RdSum [row['id']] = True

    def CollectReadMe (self):
        ReadMeFile = self.file_path + "ReadMeData.csv"
        with open(ReadMeFile, 'w') as CDF:
            writer = csv.writer(CDF)   
            writer.writerow(['id','readme'])

        RsFile = self.file_path + 'Repository_Stats.csv'
        df = pd.read_csv(RsFile)
        for index, row in df.iterrows():
            repo_id   = row['id']
            repo_name = os.path.basename (row['url'])

            Readme = './Data/Repository/' + str(repo_id) + '/' + repo_name + "/README.md"
            if not os.path.exists (Readme):
                continue
            print (Readme)
            with open (Readme, "r", encoding='latin-1') as RMF:
                AllLines = RMF.readlines ()
                AllLines = self.CleanText (AllLines)

                with open(ReadMeFile, 'a') as CDF:
                    writer = csv.writer(CDF)   
                    writer.writerow([repo_id, AllLines])

    def _update(self):
        self.save_data ()

    def _update_statistics(self, repo_item):
        print ("[%d]%d  --->  [%d, %d]" %(self.Index, repo_item.id, self.StartNo, self.EndNo))
        if self.Index < self.StartNo or self.Index > self.EndNo:
            self.Index += 1
            return
        
        ReppId  = repo_item.id
        RepoDir = "./Data/Repository/" + str(ReppId)

        if self.RdSum.get (ReppId) != None:
            self.Index += 1
            return
        
        Readme = self.ReadMeInfo.get (ReppId)
        if Readme == None and not os.path.exists (RepoDir):
            with open(self.SfFile, 'a', encoding='utf-8') as CsvFile:       
                writer = csv.writer(CsvFile)
                writer.writerow([ReppId, '', '', repo_item.topics, repo_item.description])
            self.Index += 1
        else:
            RepoDir += "/" + os.path.basename (repo_item.url)
            self.SumText(ReppId, RepoDir, repo_item.topics, repo_item.description, Readme)
            self.Index += 1

    def IsHtml (self, Line):
        for filter in self.Filters:
            if filter in Line:
                return True
        return False

    def Rmstring (self, Line, rmstr):
        while Line.find (rmstr) != -1:
            Line = Line.replace (rmstr, ' ')
        return Line
        
    def CleanText (self, AllLines):
        CleanLines = ""
        for line in AllLines:
            if len (line) < 10:
                continue
            if line[0:1] == '#':
                continue
            if self.IsHtml (line):
                continue
                
            line = self.Rmstring (line, "\n")
            line = self.Rmstring (line, "  ")
            line = self.TM.clean_text (line)
            
            CleanLines += " " + line
        return CleanLines

    def SumText (self, ReppId, RepoDir, Topics, Description, Readme):
        Tokens = []
        Sum    = ''
 
        if Readme == None:          
            RdMe = RepoDir + "/" + "README.md"
            if not os.path.exists (RdMe):
                return
            
            with open (RdMe, "r", encoding='latin-1') as RMF:
                Readme = RMF.readlines ()
                Readme = self.CleanText (Readme)

        Sum = self.EasyMind.run (Readme)
        if Sum.find ('application-error.html') == -1:  
            Tokens = self.TM.preprocess_text (Sum)
        else:
            Tokens = []
            Sum    = ''

        #self.research_stats [ReppId] = SumItem (ReppId, Sum, Tokens, Topics, Description)
        with open(self.SfFile, 'a', encoding='utf-8') as CsvFile:       
            writer = csv.writer(CsvFile)
            writer.writerow([ReppId, Sum, Tokens, Topics, Description])

    def save_data(self, file_name=None):
        if (len(self.research_stats) == 0):
            return

        SfFile = self.file_path + self.file_name + '.csv'
        with open(SfFile, 'a', encoding='utf-8') as CsvFile:       
            writer = csv.writer(CsvFile)
            for Id, SumItem in self.research_stats.items():
                row = [SumItem.id, SumItem.summarization, SumItem.tokens, SumItem.topics, SumItem.description]
                writer.writerow(row)
        self.research_stats = {}
             
    def _object_to_list(self, value):
        return super(Sumreadme, self)._object_to_list(value)
    
    def _object_to_dict(self, value):
        return super(Sumreadme, self)._object_to_dict(value)
    
    def _get_header(self, data):
        return super(Sumreadme, self)._get_header(data)
