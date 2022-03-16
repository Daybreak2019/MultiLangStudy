#!/usr/bin/python

from lib.Process_Data import Process_Data
from lib.Collect_Research_Data import Collect_Research_Data
from lib.Repository_Stats import Repository_Stats
from lib.System import System
from lib.TextModel import TextModel
import pandas as pd
import csv
from scipy.stats import spearmanr

class Collect_SpearMan():

    def __init__(self, ComboFile='Data/StatData/combo_file.csv', LimFile='Data/StatData/lim_file.csv'):
        self.ComboData = {}
        self.LimData = {}
    
        self.LangCombo2Coff = {}
        self.Lang2Coff = {}
        self.LIM2Coff = {}
        self.InitCoff ()
        
        self.GenData (ComboFile, LimFile);
        self.CalSpearman ()

    def CalSpearman (self):
        Files = ['Data/StatData/langcombo_2_lim.csv', 'Data/StatData/langcombo_2_slang-max.csv',
                 'Data/StatData/langcombo_2_slang-min.csv', 'Data/StatData/langcombo_2_slang-avg.csv']
        
        Index  = 0
        Coff   = 0
        pValue = 0
        for file in Files:
            cdf = pd.read_csv(file )
            if Index == 0:
                Coff, pValue = spearmanr(cdf['coff_lcombo'], cdf['coff_lim'])
            else:
                Coff, pValue = spearmanr(cdf['coff_lcombo'], cdf['coff_slang'])
            print ("\n[CalSpearman]" + file)
            print ("\t@@@ Coff = %f, pValue = %f" %(Coff, pValue))
            Index += 1

    def CalMaxCoffSlang (self, Combo):
        slangs = Combo.split ('_')
        MaxCoff = -1
        for sl in slangs:
            coff = self.Lang2Coff.get (sl)
            if coff == None:
                continue

            if coff > MaxCoff:
                MaxCoff = coff
        return MaxCoff


    def CalMinCoffSlang (self, Combo):
        slangs = Combo.split ('_')
        MinCoff = 1
        for sl in slangs:
            coff = self.Lang2Coff.get (sl)
            if coff == None:
                continue
            if coff < MinCoff:
                MinCoff = coff
        return MinCoff


    def CalAvgCoffSlang (self, Combo):
        slangs = Combo.split ('_')
        SumCoff = 0
        for sl in slangs:
            coff = self.Lang2Coff.get (sl)
            if coff == None:
                continue
            SumCoff += coff
        return SumCoff / len (slangs)

    
    def GenData (self, ComboFile, LimFile):
        cdf = pd.read_csv(ComboFile)
        for index, row in cdf.iterrows():
            repo  = row['repo_id']
            combo = row['combo']
            if combo == "":
                continue
            self.ComboData [repo] = combo
 
        cdf = pd.read_csv(LimFile)
        for index, row in cdf.iterrows():
            repo  = row['repo_id']
            Lim   = row['apity']
            if Lim == "":
                continue
            self.LimData [repo] = Lim

        with open ('Data/StatData/langcombo_2_lim.csv', 'w') as lcl:
            writer = csv.writer (lcl)
            writer.writerow (['coff_lcombo', 'coff_lim'])
            for repo, combo in self.ComboData.items ():
                lim = self.LimData.get (repo)
                if lim == None:
                    continue

                coff_lcombo = self.LangCombo2Coff.get (combo)
                coff_lim    = self.LIM2Coff.get (lim)
                if coff_lcombo == None or coff_lim == None:
                    continue

                writer.writerow ([coff_lcombo, coff_lim])

        with open ('Data/StatData/langcombo_2_slang-max.csv', 'w') as lcsl:
            writer = csv.writer (lcsl)
            writer.writerow (['coff_lcombo', 'coff_slang'])
            for repo, combo in self.ComboData.items ():
                coff_lcombo = self.LangCombo2Coff.get (combo)
                if coff_lcombo == None:
                    continue
                coff_slang  = self.CalMaxCoffSlang (combo)
                writer.writerow ([coff_lcombo, coff_slang])

        with open ('Data/StatData/langcombo_2_slang-min.csv', 'w') as lcsl:
            writer = csv.writer (lcsl)
            writer.writerow (['coff_lcombo', 'coff_slang'])
            for repo, combo in self.ComboData.items ():
                coff_lcombo = self.LangCombo2Coff.get (combo)
                if coff_lcombo == None:
                    continue
                coff_slang  = self.CalMinCoffSlang (combo)
                writer.writerow ([coff_lcombo, coff_slang])

        with open ('Data/StatData/langcombo_2_slang-avg.csv', 'w') as lcsl:
            writer = csv.writer (lcsl)
            writer.writerow (['coff_lcombo', 'coff_slang'])
            for repo, combo in self.ComboData.items ():
                coff_lcombo = self.LangCombo2Coff.get (combo)
                if coff_lcombo == None:
                    continue
                coff_slang  = self.CalAvgCoffSlang (combo)
                writer.writerow ([coff_lcombo, coff_slang])
                
    def InitCoff (self):
        self.LangCombo2Coff ['css_html_javascript'] = -0.0841
        self.LangCombo2Coff ['python_shell'] = 0.2818
        self.LangCombo2Coff ['go_shell'] = 0.3234
        self.LangCombo2Coff ['c_cpp_python_shell'] = -0.1922
        self.LangCombo2Coff ['javascript_python'] = -0.0925
        self.LangCombo2Coff ['css_html_javascript_shell'] = 0.1522
        self.LangCombo2Coff ['c_cpp_python'] = -0.0300
        self.LangCombo2Coff ['objectivec_ruby'] = -0.2838
        self.LangCombo2Coff ['html_python'] = -0.4557
        self.LangCombo2Coff ['css_html_javascript_python'] = -0.0666
        self.LangCombo2Coff ['cpp_python'] = 0.4613
        self.LangCombo2Coff ['html_ruby'] = -0.1324
        self.LangCombo2Coff ['c_python'] = 0.6253     
        self.LangCombo2Coff ['c_cpp_shell'] = 0.7641
        self.LangCombo2Coff ['java_shell'] = 0.2766
        self.LangCombo2Coff ['javascript_shell'] = -0.2041
        self.LangCombo2Coff ['javascript_php'] = 0.1061
        self.LangCombo2Coff ['html_java'] = -0.1493
        self.LangCombo2Coff ['java_javascript'] = 0.2197
        self.LangCombo2Coff ['c_shell'] = 0.3019

        self.Lang2Coff['html'] = -0.0747
        self.Lang2Coff['javascript'] = 0.0451
        self.Lang2Coff['shell'] = 0.1329
        self.Lang2Coff['ruby'] = 0.2004
        self.Lang2Coff['go'] = 0.4894
        self.Lang2Coff['java'] = 0.6584
        self.Lang2Coff['css'] = 0.0074
        self.Lang2Coff['python'] = 0.0531
        self.Lang2Coff['c'] = 0.5444
        self.Lang2Coff['cpp'] = 0.4271
        self.Lang2Coff['php'] = 0.2480
        self.Lang2Coff['objectivec'] = 0.3827
    
        self.LIM2Coff['FFI'] = 0.2817
        self.LIM2Coff['FFI_IMI'] = 0.1676
        self.LIM2Coff['FFI_EBD'] = -0.1454
        self.LIM2Coff['FFI_IMI_EBD'] = 0.7576
        self.LIM2Coff['IMI'] = 0.6441
        self.LIM2Coff['IMI_EBD'] = -0.3059
        self.LIM2Coff['EBD'] = -0.0811
        self.LIM2Coff['HIT'] = 0.4998


