#!/usr/bin/python

import os
import sys, getopt
import time, csv
import pandas as pd
from progressbar import ProgressBar

from lib.System import System
from lib.Process_Data import Process_Data
from lib.Collect_RepoStats import Collect_RepoStats
from lib.Github_API import Github_API

from lib.Language_Stats import Language_Stats
from lib.Collect_LangStats import Collect_LangStats
from lib.Collect_DiscripStats import Collect_DiscripStats
from lib.Collect_ComboTopicStats import Collect_ComboTopicStats, Correlation_Data,Correlation_Lic2Langs

from lib.Collect_Association import Collect_Association, Collect_AssociationML2LIC, Collect_AssociationDomain2ML, Collect_AssociationDomain2LIC,Collect_AssociationLIC2Langs
from lib.Collect_CmmtLogs import Collect_Issues
from lib.Collect_CmmtLogs import Collect_CmmtLogs
from lib.Collect_Nbr import Collect_Nbr
from lib.Collect_NbrAPI import Collect_NbrAPI
from lib.Collect_NbrSingleLang import Collect_NbrSingleLang
from lib.LangApiSniffer import LangApiSniffer
from lib.CloneRepo import CloneRepo
from lib.Sample import Sample
from lib.Collect_SpearMan import Collect_SpearMan
from lib.Sumreadme import Sumreadme
from lib.SWCate import SWCate

def Daemonize(pid_file=None):
    pid = os.fork()
    if pid:
        sys.exit(0)
 
    #os.chdir('/')
    os.umask(0)
    os.setsid()

    _pid = os.fork()
    if _pid:
        sys.exit(0)
 
    sys.stdout.flush()
    sys.stderr.flush()
 
    with open('/dev/null') as read_null, open('/dev/null', 'w') as write_null:
        os.dup2(read_null.fileno(), sys.stdin.fileno())
        os.dup2(write_null.fileno(), sys.stdout.fileno())
        os.dup2(write_null.fileno(), sys.stderr.fileno())
 
    if pid_file:
        with open(pid_file, 'w+') as f:
            f.write(str(os.getpid()))
        atexit.register(os.remove, pid_file)


def TransCsv2Pikle (file_name):
    item_list = []
    df = pd.read_csv(file_name)
    for index, row in df.iterrows():
        if 'Repository_List' in file_name:
            row['language_dictionary'] = eval (row['language_dictionary'])
            row['topics'] = eval (row['topics'])
        
        if 'Cluster_Stats' in file_name:
            row['cluster_topics'] = eval (row['cluster_topics'])
            row['languages'] = eval (row['languages'])
            row['combinations'] = eval (row['combinations'])
            
        item_list.append (row)

    pikleName = os.path.basename(file_name).split('.')[0]
    Process_Data.store_data(file_path='./', file_name=pikleName, data=item_list)


def GenCorData ():
    RepoId2LangCombo = {}
    RsFile = 'Data/StatData/Repository_Stats.csv'
    df = pd.read_csv(RsFile)
    for index, row in df.iterrows():
        RepoId2LangCombo[int (row['id'])] = row['language_combinations']
    
    correlation_data = {}
    Inputs = 'Data/StatData/RepoCategory.csv'
    df = pd.read_csv(Inputs)
    EmptyNum = 0
    TotalNum = 0

    with open('Data/StatData/Correlation_Data.csv', 'w') as CDF:
        writer = csv.writer(CDF)   
        writer.writerow(['cluster_topic','cluster_topic_id','language'])
                
    for index, row in df.iterrows():
        TotalNum += 1
        
        repo_id = int (row ['repo_id'])
        lang_combo = RepoId2LangCombo[repo_id]
        if lang_combo == '[]':
            EmptyNum += 1
            continue
        
        #print (row['combinations'] + '  ----->  ' + lang_combo)

        coorData = Correlation_Data (row['cate'], row['cate_id'], 0, 0, lang_combo, 0)
        correlation_data[index] = coorData

        with open('Data/StatData/Correlation_Data.csv', 'a') as CDF:
            writer = csv.writer(CDF)
            writer.writerow([coorData.cluster_topic, coorData.cluster_topic_id, coorData.language])

        serialized_objects = {key: value.__dict__ for key, value in correlation_data.items()}
        Process_Data.store_data(file_path='./Data/StatData/', file_name='Correlation_Data', data=serialized_objects)
    print ("EmptyRate   ----> %.2f (%d/%d)" %(EmptyNum*1.0/TotalNum, EmptyNum, TotalNum))


def GenCorDataML2LIC ():
    RepoId2ML = {}
    RsFile = 'Data/StatData/Repository_Stats.csv'
    df = pd.read_csv(RsFile)
    for index, row in df.iterrows():
        RepoId2ML[int (row['id'])] = row['main_language']
    
    correlation_data = {}
    Inputs = 'Data/StatData/ApiSniffer.csv'
    df = pd.read_csv(Inputs)
    EmptyNum = 0
    TotalNum = 0

    with open('Data/StatData/Correlation_ML2LIC.csv', 'w') as CDF:
        writer = csv.writer(CDF)   
        writer.writerow(['classifier','clftype','language'])
                
    for index, row in df.iterrows():
        TotalNum += 1
        
        repo_id  = int (row ['id'])
        MainLang = RepoId2ML[repo_id]
        
        #print (row['combinations'] + '  ----->  ' + lang_combo)

        coorData = Correlation_Data (row['classifier'], row['clfType'], 0, 0, MainLang, 0)
        correlation_data[index] = coorData

        with open('Data/StatData/Correlation_ML2LIC.csv', 'a') as CDF:
            writer = csv.writer(CDF)
            writer.writerow([coorData.cluster_topic, coorData.cluster_topic_id, coorData.language])

        serialized_objects = {key: value.__dict__ for key, value in correlation_data.items()}
        Process_Data.store_data(file_path='./Data/StatData/', file_name='Correlation_ML2LIC', data=serialized_objects)

def GenCorDataDomain2ML ():
    RepoId2ML = {}
    RsFile = 'Data/StatData/Repository_Stats.csv'
    df = pd.read_csv(RsFile)
    for index, row in df.iterrows():
        RepoId2ML[int (row['id'])] = row['main_language']
    
    correlation_data = {}
    Inputs = 'Data/StatData/RepoCategory.csv'
    df = pd.read_csv(Inputs)
    with open('Data/StatData/Correlation_Domain2ML.csv', 'w') as CDF:
        writer = csv.writer(CDF)   
        writer.writerow(['cluster_topic','cluster_topic_id','main_language'])
                
    for index, row in df.iterrows():
        repo_id = int (row ['repo_id'])
        main_lang = RepoId2ML.get (repo_id)
        if main_lang == None:
            continue
        
        #print (row['combinations'] + '  ----->  ' + lang_combo)

        coorData = Correlation_Data (row['cate'], row['cate_id'], 0, 0, main_lang, 0)
        correlation_data[index] = coorData

        with open('Data/StatData/Correlation_Domain2ML.csv', 'a') as CDF:
            writer = csv.writer(CDF)
            writer.writerow([coorData.cluster_topic, coorData.cluster_topic_id, coorData.language])

        serialized_objects = {key: value.__dict__ for key, value in correlation_data.items()}
        Process_Data.store_data(file_path='./Data/StatData/', file_name='Correlation_Domain2ML', data=serialized_objects)

def GenCorDataDomain2LIC ():
    RepoId2LIC = {}
    RsFile = 'Data/StatData/ApiSniffer.csv'
    df = pd.read_csv(RsFile)
    for index, row in df.iterrows():
        RepoId2LIC[int (row['id'])] = row['clfType']
    
    correlation_data = {}
    Inputs = 'Data/StatData/RepoCategory.csv'
    df = pd.read_csv(Inputs)
    with open('Data/StatData/Correlation_Domain2LIC.csv', 'w') as CDF:
        writer = csv.writer(CDF)   
        writer.writerow(['cluster_topic','cluster_topic_id','lic'])
                
    for index, row in df.iterrows():
        repo_id = int (row ['repo_id'])
        lic = RepoId2LIC.get (repo_id)
        if lic == None:
            continue
        
        #print (row['combinations'] + '  ----->  ' + lang_combo)

        coorData = Correlation_Data (row['cate'], row['cate_id'], 0, 0, lic, 0)
        correlation_data[index] = coorData

        with open('Data/StatData/Correlation_Domain2LIC.csv', 'a') as CDF:
            writer = csv.writer(CDF)
            writer.writerow([coorData.cluster_topic, coorData.cluster_topic_id, coorData.language])

        serialized_objects = {key: value.__dict__ for key, value in correlation_data.items()}
        Process_Data.store_data(file_path='./Data/StatData/', file_name='Correlation_Domain2LIC', data=serialized_objects)


def GenCorDataLIC2Langs ():
    RepoId2LIC = {}
    RsFile = 'Data/StatData/ApiSniffer.csv'
    df = pd.read_csv(RsFile)
    for index, row in df.iterrows():
        RepoId2LIC[int (row['id'])] = row['clfType']
    
    correlation_data = {}
    Inputs = 'Data/StatData/Repository_Stats.csv'
    df = pd.read_csv(Inputs)
    with open('Data/StatData/Correlation_LIC2Langs.csv', 'w') as CDF:
        writer = csv.writer(CDF)   
        writer.writerow(['lic','language_combinations'])
                
    for index, row in df.iterrows():
        repo_id = int (row ['id'])
        lic = RepoId2LIC.get (repo_id)
        if lic == None:
            continue

        langs = eval (row['language_combinations'])
        if len (langs) == 0:
            continue
        
        coorData = Correlation_Lic2Langs (lic, str(langs))
        correlation_data[index] = coorData

        with open('Data/StatData/Correlation_LIC2Langs.csv', 'a') as CDF:
            writer = csv.writer(CDF)
            writer.writerow([coorData.lic, coorData.langs])

        serialized_objects = {key: value.__dict__ for key, value in correlation_data.items()}
        Process_Data.store_data(file_path='./Data/StatData/', file_name='Correlation_LIC2Langs', data=serialized_objects)


def TimeTag (Tag):
    localtime = time.asctime( time.localtime(time.time()) )
    print ("%s : %s" %(Tag, localtime))
 

# collect from github
def CollectRepo(year=0):
    TimeTag(">>>>>>>>>>>> [%d]Collect repositories fom github..." %year)
    # Retrieves repo data from Github by page
    origin_repo = Github_API()

    if (year == 0):
        origin_repo.collect_repositories()
    else:
        origin_repo.collect_repositories_by_year (year)
    
    return origin_repo.list_of_repositories

def UpdateRepo():
    TimeTag(">>>>>>>>>>>> [%d]Update repositories fom github...")
    # Retrieves repo data from Github by page
    Ga = Github_API()
    Ga.update_repolist()


# repo stats
def RepoStats(original_repo_list=None, TopLangNum=50):
    TimeTag(">>>>>>>>>>>> Statistic on repositories...")
    if (original_repo_list == None):
        original_repo_list = Process_Data.load_data(file_path=System.getdir_collect(), file_name='Repository_List')

    #proceed to analysics
    repository_data = Collect_RepoStats(top_langs_num=TopLangNum)
    repository_data.process_data(original_repo_list)
    repository_data.save_data()

# language stats
def LangStats(repo_stats=None):
    TimeTag(">>>>>>>>>>>> Statistic on languages...")
    file_path=System.getdir_stat()
    if (repo_stats == None):
        repo_stats = Process_Data.load_data(file_path=file_path, file_name='Repository_Stats')
        repo_stats = Process_Data.dict_to_list(repo_stats)
        
    research_data = Collect_LangStats() 
    research_data.process_data(list_of_repos=repo_stats)
    research_data.save_data()

# discription stats
def DiscripStats(repo_stats=None):
    TimeTag(">>>>>>>>>>>> Statistic on discriptions...")
    file_path=System.getdir_stat()
    if (repo_stats == None):
        repo_stats = Process_Data.load_data(file_path=file_path, file_name='Repository_Stats')
        repo_stats = Process_Data.dict_to_list(repo_stats)
    
    research_data = Collect_DiscripStats()
    research_data.process_data(list_of_repos=repo_stats)
    research_data.save_data()    

# relation between language combination and topic stats
def RelComboTopics(descrip_stats=None):
    TimeTag(">>>>>>>>>>>> Statistic on combinations and topics...")
    file_path=System.getdir_stat()
    if (descrip_stats == None):
        descrip_stats = Process_Data.load_data(file_path=file_path, file_name='Description_Stats')
        descrip_stats = Process_Data.dict_to_list(descrip_stats)
        
    research_data = Collect_ComboTopicStats()
    research_data.process_data (list_of_repos=descrip_stats)
    research_data.save_data()

# Association
def Association(correlation_stat=None):
    TimeTag(">>>>>>>>>>>> Statistic on Association...")
    GenCorData ()
    
    file_path=System.getdir_stat()
    if (correlation_stat == None):
        correlation_stat = Process_Data.load_data(file_path=file_path, file_name='Correlation_Data')
        correlation_stat = Process_Data.dict_to_list(correlation_stat)
        
    research_data = Collect_Association()
    research_data.process_data (list_of_repos=correlation_stat)
    research_data.save_data()

def AssociationML2LIC(correlation_stat=None):
    TimeTag(">>>>>>>>>>>> Statistic on Association ML2LIC...")
    GenCorDataML2LIC()
    
    file_path=System.getdir_stat()
    if (correlation_stat == None):
        correlation_stat = Process_Data.load_data(file_path=file_path, file_name='Correlation_ML2LIC')
        correlation_stat = Process_Data.dict_to_list(correlation_stat)
        
    research_data = Collect_AssociationML2LIC()
    research_data.process_data (list_of_repos=correlation_stat)
    research_data.save_data()

def AssociationDomain2Main(correlation_stat=None):
    TimeTag(">>>>>>>>>>>> Statistic on Association Domain2Main...")
    GenCorDataDomain2ML()
    
    file_path=System.getdir_stat()
    if (correlation_stat == None):
        correlation_stat = Process_Data.load_data(file_path=file_path, file_name='Correlation_Domain2ML')
        correlation_stat = Process_Data.dict_to_list(correlation_stat)
        
    research_data = Collect_AssociationDomain2ML ()
    research_data.process_data (list_of_repos=correlation_stat)
    research_data.save_data()

def AssociationDomain2Lic(correlation_stat=None):
    TimeTag(">>>>>>>>>>>> Statistic on Association Domain2Lic...")
    GenCorDataDomain2LIC()
    
    file_path=System.getdir_stat()
    if (correlation_stat == None):
        correlation_stat = Process_Data.load_data(file_path=file_path, file_name='Correlation_Domain2LIC')
        correlation_stat = Process_Data.dict_to_list(correlation_stat)
        
    research_data = Collect_AssociationDomain2LIC ()
    research_data.process_data (list_of_repos=correlation_stat)
    research_data.save_data()
    

def AssociationLic2Langs(correlation_stat=None):
    TimeTag(">>>>>>>>>>>> Statistic on Association Lic2Langs...")
    GenCorDataLIC2Langs()
    
    file_path=System.getdir_stat()
    if (correlation_stat == None):
        correlation_stat = Process_Data.load_data(file_path=file_path, file_name='Correlation_LIC2Langs')
        correlation_stat = Process_Data.dict_to_list(correlation_stat)
        
    research_data = Collect_AssociationLIC2Langs ()
    research_data.process_data (list_of_repos=correlation_stat)
    research_data.save_data()


# Commits log analysis
def CommitLog(StartNo=0, EndNo=65535, repo_stats=None):
    TimeTag(">>>>>>>>>>>> Statistic on CommitLog...")
    file_path=System.getdir_stat()
    if (repo_stats == None):
        repo_stats = Process_Data.load_data(file_path=file_path, file_name='Repository_Stats')
        repo_stats = Process_Data.dict_to_list(repo_stats)
        
    research_data = Collect_CmmtLogs(StartNo, EndNo) 
    research_data.process_data(list_of_repos=repo_stats)
    research_data.save_data()

# Commits log NBR analysis
def CommitLogNbr(repo_no, repo_stats=None):
    TimeTag(">>>>>>>>>>>> Statistic on CommitLogNbr...")
    file_path=System.getdir_stat()
    if (repo_stats == None):
        repo_stats = Process_Data.load_data(file_path=file_path, file_name='Repository_Stats')
        repo_stats = Process_Data.dict_to_list(repo_stats)
        
    research_data = Collect_Nbr(repo_no) 
    research_data.process_data(list_of_repos=repo_stats)
    research_data.save_data()

    research_data = Collect_NbrAPI(repo_no) 
    research_data.process_data(list_of_repos=repo_stats)
    research_data.save_data()

    research_data = Collect_NbrSingleLang (repo_no)
    research_data.process_data(list_of_repos=repo_stats)
    research_data.save_data()


# Language API sniffer
def LangSniffer(StartNo, EndNo, FileName):
    TimeTag(">>>>>>>>>>>> Statistic LangAPISniffer...")
    file_path=System.getdir_stat()
    repo_stats = Process_Data.load_data(file_path=file_path, file_name='Repository_Stats')
    repo_stats = Process_Data.dict_to_list(repo_stats)
        
    research_data = LangApiSniffer(StartNo, EndNo, FileName) 
    research_data.process_data(list_of_repos=repo_stats)
    research_data.save_data()

def CloneRepos (startNo=0, endNo=65535):
    CR = CloneRepo ("Repository_List.csv", startNo, endNo)
    CR.Clone ()

def CollectSamples (Stat=False):
    if Stat == False:
        Cs = Sample (50, 500)
        Cs.ValidSmapling ()
    else:
        Cs = Sample (2, 100)
        Cs.StatSampling ()

def CollectIssues (StartNo=0, EndNo=65535, repo_stats=None):
    TimeTag(">>>>>>>>>>>> Statistic on Issues...")
    file_path=System.getdir_stat()
    if (repo_stats == None):
        repo_stats = Process_Data.load_data(file_path=file_path, file_name='Repository_Stats')
        repo_stats = Process_Data.dict_to_list(repo_stats)
        
    research_data = Collect_Issues(StartNo, EndNo) 
    research_data.process_data(list_of_repos=repo_stats)
    research_data.save_data()

def CollectSpearman ():
    Sm = Collect_SpearMan ()

def CollectSumReadMe (StartNo=0, EndNo=65535):
    TimeTag(">>>>>>>>>>>> Statistic on SumReadMe...")
    file_path=System.getdir_stat()
    repo_stats = Process_Data.load_data(file_path=file_path, file_name='Repository_Stats')
    repo_stats = Process_Data.dict_to_list(repo_stats)

    if not os.path.exists ('Data/StatData/ReadMeData.csv'):
        SumRd = Sumreadme ()
        SumRd.CollectReadMe ()
        
    research_data = Sumreadme(StartNo, EndNo) 
    research_data.process_data(list_of_repos=repo_stats)
    research_data.save_data()


def StatAll ():
    original_repo_list = Process_Data.load_data(file_path=System.getdir_collect(), file_name='Repository_List')
    RepoStats(original_repo_list)

    repo_stats = Process_Data.load_data(file_path=System.getdir_stat (), file_name='Repository_Stats')
    repo_stats = Process_Data.dict_to_list(repo_stats)        
    LangStats(repo_stats)
    DiscripStats(repo_stats)
                
    RelComboTopics(None)
    Association(None)

def main(argv):
    step = ''
    by_year  = False
    year_val = 0
    repo_no  = 0
    IsDaemon = False
    FileName = ""
    StartNo  = 0
    EndNo    = 65535
    TopLangNum = 50
    TransFlag  = False
   
    # get step
    try:
        opts, args = getopt.getopt(argv,"dhs:y:n:f:b:e:l:t",["step=", "year=", "no="])
    except getopt.GetoptError:
        print ("./collect.py -s <step_name>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ("collect.py -s <step_name>");
            sys.exit()
        elif opt in ("-s", "--step"):
            step = arg;
        elif opt in ("-n", "--no"):
            repo_no = int(arg);
        elif opt in ("-y", "--year"):
            by_year = True;
            year_val = int(arg)
            print ("by_year = %d, year_val = %d" %(by_year, year_val))
        elif opt in ("-d", "--daemon"):
            IsDaemon = True
        elif opt in ("-f", "--filename"):
            FileName = arg
        elif opt in ("-b", "--beginno"):
            StartNo = int(arg)
        elif opt in ("-e", "--endno"):
            EndNo = int(arg)
        elif opt in ("-l", "--language num"):
            TopLangNum = int(arg)
        elif opt in ("-t", "--trans csv to pikle"):
            TransFlag = True

    if IsDaemon:
        Daemonize ()
        
    if TransFlag == True:
        if FileName == "":
            return
        TransCsv2Pikle (FileName)


    if (step == "all"):
        if (by_year == True):
            for year in range (System.START_YEAR, System.END_YEAR+1, 1):
                if (year_val != 0 and year_val != year):
                    continue
                print ("\nYear-%d" %year, end="")
                System.setdir (str(year), str(year))
                StatAll()
        else:
            StatAll ()
    elif (step == "update"):
        UpdateRepo ()
    elif (step == "collect"):
        if (by_year == True):
            for year in range (System.START_YEAR, System.END_YEAR+1, 1):
                if (year_val != 0 and year_val != year):
                    continue
                print ("\nYear-%d" %year, end="")
                System.setdir (str(year), str(year))
                CollectRepo(year)
        else:
            CollectRepo()
                
    elif (step == "repostats"):
        if (by_year == True):
            for year in range (System.START_YEAR, System.END_YEAR+1, 1):
                if (year_val != 0 and year_val != year):
                    continue
                print ("\nYear-%d" %year, end="")
                System.setdir (str(year), str(year))
                RepoStats(None)
        else:
            RepoStats(None, TopLangNum)
    elif (step == "langstats"):
        if (by_year == True):
            for year in range (System.START_YEAR, System.END_YEAR+1, 1):
                if (year_val != 0 and year_val != year):
                    continue
                print ("\nYear-%d" %year, end="")
                System.setdir (str(year), str(year))
                LangStats(None)
        else:
            LangStats(None)
    elif (step == "discripstats"):
        if (by_year == True):
            for year in range (System.START_YEAR, System.END_YEAR+1, 1):
                if (year_val != 0 and year_val != year):
                    continue
                print ("\nYear-%d" %year, end="")
                System.setdir (str(year), str(year))
                DiscripStats(None)
        else:
            DiscripStats(None)
    elif (step == "topics"):
        if (by_year == True):
            for year in range (System.START_YEAR, System.END_YEAR+1, 1):
                if (year_val != 0 and year_val != year):
                    continue
                print ("\nYear-%d" %year, end="")
                System.setdir (str(year), str(year))
                RelComboTopics(None)
        else:
            RelComboTopics(None)
    elif (step == "asso"):
        if (by_year == True):
            for year in range (System.START_YEAR, System.END_YEAR+1, 1):
                if (year_val != 0 and year_val != year):
                    continue
                print ("\nYear-%d" %year, end="")
                System.setdir (str(year), str(year))
                Association(None)
        else:
            Association(None)
    elif (step == "assoml"):
        if (by_year == True):
            for year in range (System.START_YEAR, System.END_YEAR+1, 1):
                if (year_val != 0 and year_val != year):
                    continue
                print ("\nYear-%d" %year, end="")
                System.setdir (str(year), str(year))
                AssociationML2LIC(None)
                AssociationDomain2Main(None)
                AssociationDomain2Lic(None)
                AssociationLic2Langs(None)
        else:
            AssociationML2LIC(None)
            AssociationDomain2Main(None)
            AssociationDomain2Lic(None)
            AssociationLic2Langs(None)
            
    elif (step == "cmmts"):
        CommitLog (StartNo, EndNo)
    elif (step == "issue"):
        CollectIssues (StartNo, EndNo)
    elif (step == "nbr"):
        CommitLogNbr (repo_no)
    elif (step == "apisniffer"):
        LangSniffer (StartNo, EndNo, FileName)
    elif (step == "clone"):
        CloneRepos (StartNo, EndNo)
    elif (step == "sample"):
        CollectSamples ()
    elif (step == "statsample"):
        CollectSamples (True)
    elif (step == "spearman"):
        CollectSpearman ()
    elif (step == "readme"):
        CollectSumReadMe ()
    elif (step == "swc"):
        swCt = SWCate ()
        swCt.Categorize ()
    else:
        print ("collect.py -s <all/collect/repostats/langstats/discripstats/topics/asso/cmmts/nbr/apisniffer/clone>") 

    TimeTag (">>>>>>>>>>>> End")

if __name__ == "__main__":
    main(sys.argv[1:])
