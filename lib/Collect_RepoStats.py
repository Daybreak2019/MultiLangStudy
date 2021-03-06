import os
import pandas as pd
from lib.System import System
from lib.Process_Data import Process_Data
from lib.Collect_Research_Data import Collect_Research_Data
from lib.Repository_Stats import Repository_Stats
from lib.LangProj_Stats   import LangProj_Stats
from lib.LangCombo_Stats  import LangCombo_Stats

from progressbar import ProgressBar


class Collect_LICStats ():
    def __init__(self, TopLangs):
        self.TopLangs = TopLangs
        self.FilePath = System.getdir_stat() +  'ApiSniffer.csv'
        self.Lic = {}
        self.LicStats = {}
        self.LicIndivalStats = {}

        self.LoadLic ()
        self.RunStat ()

    def LoadLic (self):
        if not os.path.exists (self.FilePath):
            print ('@@@@@@ %s not exist..........' %self.FilePath)
            return
        df = pd.read_csv(self.FilePath)
        for index, row in df.iterrows():
            self.Lic [row['id']] = row['clfType']

    def RunStat (self):
        import csv
        for id, lic in self.Lic.items ():
            count = self.LicStats.get (lic)
            if count  != None:
                self.LicStats [lic] = count + 1
            else:
                self.LicStats [lic] = 0

            subLics = list (lic.split('_'))
            for slic in subLics:
                count = self.LicIndivalStats.get (slic)
                if count  != None:
                    self.LicIndivalStats [slic] = count + 1
                else:
                    self.LicIndivalStats [slic] = 0

        licStatFile = System.getdir_stat() +  'LicStats.csv'
        with open (licStatFile, "w") as LSF:
            writer = csv.writer(LSF)   
            writer.writerow(['lic','count'])
            for lic, count in self.LicStats.items ():
                writer.writerow([lic,count])

        licStatFile = System.getdir_stat() +  'LicStats_Indidual.csv'
        with open (licStatFile, "w") as LSF:
            writer = csv.writer(LSF)   
            writer.writerow(['lic','count'])
            for lic, count in self.LicIndivalStats.items ():
                writer.writerow([lic,count])

class AvgLangStat ():
    def __init__ (self, avg, std, min, max, median):
        self.avg = avg
        self.std = std
        self.min = min
        self.max = max
        self.median = median


class Collect_RepoStats(Collect_Research_Data):

    def __init__(self, file_name='Repository_Stats', top_langs_num=50):
        super(Collect_RepoStats, self).__init__(file_name=file_name)
        self.top_langs = []
        self.load_top_langs (top_langs_num)
        print (self.top_langs)
        
        self.all_language_combo_count = 0
        
        self.combination_stats = {}
        self.all_combination_stats = {}
        self.language_used_list = []

        self.avg_lang_stats = {}

    def load_top_langs (self, top_langs_num=50):
        LangFile = 'Data/OriginData/programming_languages.txt'
        
        if top_langs_num == 0:
            top_langs_num = 100
            LangFile = 'Data/OriginData/all_languages.txt'
        
        
        with open (LangFile, 'r') as LF:
            AllLines = LF.readlines ()
            lang_num = 0
            for line in AllLines:
                lang = line.replace('\n', '')
                self.top_langs.append (lang.lower())
                lang_num += 1
                if lang_num >= top_langs_num:
                    break
        

    def _update_statistics(self, repo_item):
        #CmmtFile = System.cmmt_file (repo_item.id)
        #if System.is_exist(CmmtFile) == False:
        #    return
        repo_stat = Repository_Stats(repo_item, self.top_langs)
        repo_id   = repo_stat.id
        self.research_stats[repo_id] = repo_stat
        
        #update count of each combination
        if (repo_stat.languages_used > 1):
            self._language_combo_stat(repo_stat)

        #the distribution of the projects over different numbers of languages used
        self._language_proj_stat(repo_stat)

        self.language_used_list.append (repo_stat.languages_used)

    def _language_combo_stat(self, repo_stat):
        for combo in repo_stat.language_combinations:
            combo = ' '.join(combo)
            #print ("===> combo = " + str(combo))
            langcombo_stat = self.combination_stats.get(combo, None)
            if (langcombo_stat == None):
                langcombo_stat = LangCombo_Stats(0, combo)
                self.combination_stats[combo] = langcombo_stat
            langcombo_stat.update()  

    def _language_proj_stat(self, repo_stat):
        lang_count = repo_stat.languages_used
        lang_proj_stat = self.lang_proj_stats.get(lang_count, None)
        if (lang_proj_stat == None):
            lang_proj_stat = LangProj_Stats(lang_count)
            self.lang_proj_stats[lang_count] = lang_proj_stat  
        lang_proj_stat.update ()

    def _get_lang_set (self, combo):
        language = []
        for lang in combo.split(" "):
            language.append (lang)
        return set (language)
        
    def _update(self):
        self.combination_stats = self._get_top_combinations(50)
        for combo, stat in self.combination_stats.items():
            stat.update_distribution (self.all_language_combo_count)

        print ("---> Update repo with top language combination...")
        self._update_repo_combination()

        project_count = len(self.research_stats)
        for lang_count in self.lang_proj_stats.keys():
            self.lang_proj_stats[lang_count].update_distribution(project_count)

        # compute average languages userd
        lang_stats = Process_Data.calculate_stats (self.language_used_list)
        avg_lang_stat = AvgLangStat (lang_stats["avg"], lang_stats["std"],\
                                     min(self.language_used_list),\
                                     max(self.language_used_list), lang_stats["median"])
        self.avg_lang_stats[0] = avg_lang_stat

        # stat for lic
        Collect_LICStats (self.top_langs)

    def _update_repo_combination(self):
        repo_items = {}
        pbar = ProgressBar()
        for repo_id, repo_item in pbar(self.research_stats.items()):
            update_combinations = []
  
            for combo in reversed(repo_item.language_combinations):
                combo = ' '.join(combo)            
                if (combo in self.combination_stats.keys()):
                    update_combinations.append(combo)
                    break
            repo_item.language_combinations = update_combinations
            repo_items[repo_id] = repo_item
        
        self.research_stats = repo_items

    def _get_top_combinations(self, top_num=1000):
        combination_stats = {}
        
        #get top combination_count combinations
        combination_sort = self._sort_combo_by_count()
        combination_id = 0
        for lang in combination_sort.keys():
            combo_stat = self.combination_stats[lang]
            combo_stat.combo_id = combination_id
            
            if (combination_id <= top_num):     
                combination_stats[lang] = combo_stat
                self.all_language_combo_count = self.all_language_combo_count + combo_stat.count

            self.all_combination_stats[lang] = combo_stat
            combination_id = combination_id + 1

        return combination_stats
    

    def _sort_combo_by_count(self):
        #collect items whose count > 1
        combinations = {}
        for combo, stat in self.combination_stats.items():
            if (stat.count > 1):
                combinations[combo] = stat.count

        #sort dict
        return Process_Data.dictsort_value (combinations, True)


    def save_data(self):
        super(Collect_RepoStats, self).save_data(self.research_stats)
        
        super(Collect_RepoStats, self).save_data(self.all_combination_stats, "LangCombo_Stats")

        super(Collect_RepoStats, self).save_data(self.lang_proj_stats, "LangProj_Stats")

        super(Collect_RepoStats, self).save_data(self.avg_lang_stats, "AvgLangUsage_Stats")
  
    def _object_to_list(self, value):
        return super(Collect_RepoStats, self)._object_to_list(value)

    def _object_to_dict(self, value):
        return super(Collect_RepoStats, self)._object_to_dict(value)

    def _get_header(self, data):
        return super(Collect_RepoStats, self)._get_header(data)


