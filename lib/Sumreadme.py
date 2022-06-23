
import os
import re
import csv
from lib.Process_Data import Process_Data
from lib.Collect_Research_Data import Collect_Research_Data
from lib.TextModel import TextModel
from eazymind.nlp.eazysum import Summarizer


class SumItem ():
    def __init__(self, id, summarization, tokens):
        self.id = id
        self.summarization = summarization
        self.tokens = tokens

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

        # Default file 
        Header = ['id', 'summarization', 'tokens']
        SfFile = self.file_path + "Sumreadme" + '.csv'
        with open(SfFile, 'w', encoding='utf-8') as CsvFile:       
            writer = csv.writer(CsvFile)
            writer.writerow(Header)

    def _update(self):
        self.save_data ()

    def _update_statistics(self, repo_item):
        #print (self.Index, " -> [", self.StartNo, ", ", self.EndNo, "]")
        if self.Index < self.StartNo or self.Index > self.EndNo:
            self.Index += 1
            return
        
        ReppId  = repo_item.id
        RepoDir = "./Data/Repository/" + str(ReppId)
        if not os.path.exists (RepoDir):
            self.Index += 1
            return

        RepoDir += "/" + os.path.basename (repo_item.url)
        self.SumText(ReppId, RepoDir)
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

    def SumText (self, ReppId, RepoDir):
        RdMe = RepoDir + "/" + "README.md"
        if not os.path.exists (RdMe):
            return

        with open (RdMe, "r") as RMF:
            AllLines = RMF.readlines ()
            AllLines = self.CleanText (AllLines)
            
            Sum = self.EasyMind.run (AllLines)
            Tokens = self.TM.preprocess_text (Sum)
            
            self.research_stats [ReppId] = SumItem (ReppId, Sum, Tokens)

    def save_data(self, file_name=None):
        if (len(self.research_stats) == 0):
            return

        SfFile = self.file_path + self.file_name + '.csv'
        with open(SfFile, 'a', encoding='utf-8') as CsvFile:       
            writer = csv.writer(CsvFile)
            for Id, SumItem in self.research_stats.items():
                row = [SumItem.id, SumItem.summarization, SumItem.tokens]
                writer.writerow(row)
        self.research_stats = {}
             
    def _object_to_list(self, value):
        return super(Sumreadme, self)._object_to_list(value)
    
    def _object_to_dict(self, value):
        return super(Sumreadme, self)._object_to_dict(value)
    
    def _get_header(self, data):
        return super(Sumreadme, self)._get_header(data)
