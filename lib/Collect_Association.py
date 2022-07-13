
from lib.System import System

from lib.Process_Data import Process_Data
from lib.Collect_Research_Data import Collect_Research_Data
from lib.TextModel import TextModel

from progressbar import ProgressBar

from pandas import DataFrame
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules

class Association_Stats:
    def __init__ (self, antecedents, consequents, support, confidience, lift, cluster_topics):
        self.antecedents         = antecedents
        self.consequents         = consequents
        self.support             = support
        self.confidience         = confidience
        self.lift                = lift
        self.cluster_topics      = cluster_topics

class Collect_Association(Collect_Research_Data):

    def __init__(self, file_name="Association_Stats"):
        super(Collect_Association, self).__init__(file_name)
        self.topic_list = []
        self.language_list = []
        self.unique_items = {}
        self.lang_topic_stats = {}

    def _str2item (self, item):
        if isinstance (item, str):
            item = eval (item)
            if isinstance (item, list):
                item = item [0]
        return item
    
    def _insert_item (self, item):
        item = self._str2item (item)
        if (self.unique_items.get (item, None) == None):
            self.unique_items [item] = True
    
    def _update_statistics(self, correlation_item):

        self.topic_list.append (correlation_item.cluster_topic_id)
        self._insert_item (correlation_item.cluster_topic_id)

        combination = "".join(correlation_item.language)
        combination = combination.replace (" ", "_")
        self.language_list.append (combination)
        self._insert_item (combination)

    def _output_encoding (self, ohe_df):
        import csv
        with open('debug_encoding.csv', 'w') as DEF:
            writer = csv.writer(DEF)
            headers = ohe_df.columns.values.tolist()
            writer.writerow(headers)
            for index, row in ohe_df.iterrows ():
                writer.writerow(row)

    def _one_hot_encoding (self, df, unique_items):
        encoded_vals = []
        for index, row in df.iterrows():
            x = self._str2item (row.x)
            y = self._str2item (row.y)
            row_set = set ([x, y])

            labels = {}
            uncommons = list(set(unique_items) - row_set)
            commons = list(set(unique_items).intersection(row_set))

            for uc in uncommons:
                labels[uc] = 0
            for com in commons:
                labels[com] = 1

            #deal with the inclution
            for com in commons:
                if not isinstance (com, str):
                    continue

                com_list = com.split ('_')
                for uc in uncommons:
                    if not isinstance (uc, str):
                        continue
                    uc_list = uc.split ('_')
                    ins = list(set(com_list).intersection(uc_list))
                    if len (ins) == len (com_list):
                        labels[uc] = 1
                        
            encoded_vals.append(labels)

        return encoded_vals

    def _get_set_value (self, set_item):
        list_item = list (set_item)
        return len(list_item), list_item[0]

    def _update(self):
        unique_items = [key for key in self.unique_items.keys()]
        print ("unique_items num = %d/%d" %(len(unique_items), len(self.topic_list)))
        
        Data = {'x': self.topic_list, 'y': self.language_list}  
        df = DataFrame(Data, columns=['x', 'y'])

        encoded_vals = self._one_hot_encoding (df, unique_items)
        ohe_df = pd.DataFrame(encoded_vals)
        self._output_encoding (ohe_df)

        freq_items = apriori(ohe_df, min_support=0.01, use_colnames=True)
        print ("freq_items:")
        print (freq_items.head(100))

        rules = association_rules(freq_items, metric="lift", min_threshold=1)
        print ("association_rules:")
        print (rules.head(100))

        #load cluster information
        #cluster_stats = Process_Data.load_data(file_path=System.getdir_stat(), file_name="Cluster_Stats")
        #cluster_stats = Process_Data.dict_to_list(cluster_stats)
        CateId2Cate = self.LoadSwCate()

        for index, item in rules.iterrows():
            asize, antecedents = self._get_set_value(item['antecedents'])
            csize, consequents = self._get_set_value(item['consequents'])
            if asize > 1 or csize > 1:
                continue

            antecedents = str (antecedents)
            consequents = str (consequents)
            support     = item['support']
            confidence  = item['confidence']
            lift        = item['lift']

            if (antecedents.isdigit()):
                cluster_topics = CateId2Cate[int(antecedents)]
                self.research_stats [index] = Association_Stats (antecedents, consequents, support, confidence, lift, cluster_topics)
            elif (consequents.isdigit()):
                cluster_topics = CateId2Cate[int(consequents)]
                self.lang_topic_stats [index] = Association_Stats (antecedents, consequents, support, confidence, lift, cluster_topics)
        
        print ("Topic Associat to Language = %d, Language Associat to Topic = %d"\
               %(len(self.research_stats), len(self.lang_topic_stats)))

    def save_data(self):
        if (len (self.research_stats)):
            super(Collect_Association, self).save_data(self.research_stats, "Domain_Associat_to_Languages")

        if (len (self.lang_topic_stats)):
            super(Collect_Association, self).save_data(self.lang_topic_stats, "Languages_Associat_to_Domain")
    
    def _object_to_list(self, value):
        return super(Collect_Association, self)._object_to_list(value)
    
    def _object_to_dict(self, value):
        return super(Collect_Association, self)._object_to_dict(value)
    
    def _get_header(self, data):
        return super(Collect_Association, self)._get_header(data)



class Collect_AssociationML2LIC(Collect_Research_Data):

    def __init__(self, file_name="AssoMainLang2LIC_Stats"):
        super(Collect_AssociationML2LIC, self).__init__(file_name)
        self.topic_list = []
        self.language_list = []
        self.unique_items = {}
        self.lang_topic_stats = {}
    
    def _insert_item (self, item):
        if (self.unique_items.get (item, None) == None):
            self.unique_items [item] = True
    
    def _update_statistics(self, correlation_item):

        self.topic_list.append (correlation_item.cluster_topic_id)
        self._insert_item (correlation_item.cluster_topic_id)

        self.language_list.append (correlation_item.language)
        self._insert_item (correlation_item.language)

    def _output_encoding (self, ohe_df):
        import csv
        with open('debug_encoding_ml2lic.csv', 'w') as DEF:
            writer = csv.writer(DEF)
            headers = ohe_df.columns.values.tolist()
            writer.writerow(headers)
            for index, row in ohe_df.iterrows ():
                writer.writerow(row)

    def _one_hot_encoding (self, df, unique_items):
        encoded_vals = []
        for index, row in df.iterrows():
            x = row.x
            y = row.y
            row_set = set ([x, y])

            labels = {}
            uncommons = list(set(unique_items) - row_set)
            commons = list(set(unique_items).intersection(row_set))

            for uc in uncommons:
                labels[uc] = 0
            for com in commons:
                labels[com] = 1

            #deal with the inclution
            for com in commons:
                if not isinstance (com, str):
                    continue

                com_list = com.split ('_')
                for uc in uncommons:
                    if not isinstance (uc, str):
                        continue
                    uc_list = uc.split ('_')
                    ins = list(set(com_list).intersection(uc_list))
                    if len (ins) == len (com_list):
                        labels[uc] = 1
                        
            encoded_vals.append(labels)

        return encoded_vals

    def _get_set_value (self, set_item):
        list_item = list (set_item)
        return len(list_item), list_item[0]
    
    def _update(self):
        unique_items = [key for key in self.unique_items.keys()]
        print ("unique_items num = %d/%d" %(len(unique_items), len(self.topic_list)))
        
        Data = {'x': self.language_list, 'y': self.topic_list}  
        df = DataFrame(Data, columns=['x', 'y'])

        encoded_vals = self._one_hot_encoding (df, unique_items)
        ohe_df = pd.DataFrame(encoded_vals)
        self._output_encoding (ohe_df)

        freq_items = apriori(ohe_df, min_support=0.01, use_colnames=True)
        print ("freq_items:")
        print (freq_items.head(100))

        rules = association_rules(freq_items, metric="lift", min_threshold=1)
        print ("association_rules:")
        print (rules.head(100))

        for index, item in rules.iterrows():
            asize, antecedents = self._get_set_value(item['antecedents'])
            csize, consequents = self._get_set_value(item['consequents'])
            if asize > 1 or csize > 1:
                continue

            antecedents = str (antecedents)
            consequents = str (consequents)
            support     = item['support']
            confidence  = item['confidence']
            lift        = item['lift']

            if (antecedents in self.language_list):
                self.research_stats [index] = Association_Stats (antecedents, consequents, support, confidence, lift, '')
            else:
                self.lang_topic_stats [index] = Association_Stats (antecedents, consequents, support, confidence, lift, '')
        
        print ("MainLang Associat to LIC = %d, LIC Associat to MainLang = %d"\
               %(len(self.research_stats), len(self.lang_topic_stats)))

    def save_data(self):
        if (len (self.research_stats)):
            super(Collect_AssociationML2LIC, self).save_data(self.research_stats, "ML_Associat_to_LIC")

        if (len (self.lang_topic_stats)):
            super(Collect_AssociationML2LIC, self).save_data(self.lang_topic_stats, "LIC_Associat_to_ML")
    
    def _object_to_list(self, value):
        return super(Collect_AssociationML2LIC, self)._object_to_list(value)
    
    def _object_to_dict(self, value):
        return super(Collect_AssociationML2LIC, self)._object_to_dict(value)
    
    def _get_header(self, data):
        return super(Collect_AssociationML2LIC, self)._get_header(data)    


class Collect_AssociationDomain2ML(Collect_Research_Data):

    def __init__(self, file_name="AssoDomain2ML_Stats"):
        super(Collect_AssociationDomain2ML, self).__init__(file_name)
        self.topic_list = []
        self.language_list = []
        self.unique_items = {}
        self.ml2domain_stats = {}
    
    def _insert_item (self, item):
        if (self.unique_items.get (item, None) == None):
            self.unique_items [item] = True
    
    def _update_statistics(self, correlation_item):

        self.topic_list.append (correlation_item.cluster_topic_id)
        self._insert_item (correlation_item.cluster_topic_id)

        self.language_list.append (correlation_item.language)
        self._insert_item (correlation_item.language)

    def _output_encoding (self, ohe_df):
        import csv
        with open('debug_encoding_dm2ml.csv', 'w') as DEF:
            writer = csv.writer(DEF)
            headers = ohe_df.columns.values.tolist()
            writer.writerow(headers)
            for index, row in ohe_df.iterrows ():
                writer.writerow(row)

    def _one_hot_encoding (self, df, unique_items):
        encoded_vals = []
        for index, row in df.iterrows():
            x = row.x
            y = row.y
            row_set = set ([x, y])

            labels = {}
            uncommons = list(set(unique_items) - row_set)
            commons = list(set(unique_items).intersection(row_set))

            for uc in uncommons:
                labels[uc] = 0
            for com in commons:
                labels[com] = 1

            #deal with the inclution
            for com in commons:
                if not isinstance (com, str):
                    continue

                com_list = com.split ('_')
                for uc in uncommons:
                    if not isinstance (uc, str):
                        continue
                    uc_list = uc.split ('_')
                    ins = list(set(com_list).intersection(uc_list))
                    if len (ins) == len (com_list):
                        labels[uc] = 1
                        
            encoded_vals.append(labels)

        return encoded_vals

    def _get_set_value (self, set_item):
        list_item = list (set_item)
        return len(list_item), list_item[0]
    
    def _update(self):
        unique_items = [key for key in self.unique_items.keys()]
        print ("unique_items num = %d/%d" %(len(unique_items), len(self.topic_list)))
        
        Data = {'x': self.language_list, 'y': self.topic_list}  
        df = DataFrame(Data, columns=['x', 'y'])

        encoded_vals = self._one_hot_encoding (df, unique_items)
        ohe_df = pd.DataFrame(encoded_vals)
        self._output_encoding (ohe_df)

        freq_items = apriori(ohe_df, min_support=0.01, use_colnames=True)
        print ("freq_items:")
        print (freq_items.head(100))

        rules = association_rules(freq_items, metric="lift", min_threshold=1)
        print ("association_rules:")
        print (rules.head(100))

        CateId2Cate = self.LoadSwCate()

        for index, item in rules.iterrows():
            asize, antecedents = self._get_set_value(item['antecedents'])
            csize, consequents = self._get_set_value(item['consequents'])
            if asize > 1 or csize > 1:
                continue

            antecedents = str (antecedents)
            consequents = str (consequents)
            support     = item['support']
            confidence  = item['confidence']
            lift        = item['lift']

            if (antecedents in self.language_list):
                domain = CateId2Cate[consequents]
                self.ml2domain_stats [index] = Association_Stats (antecedents, consequents, support, confidence, lift, domain)
            else:
                domain = CateId2Cate[antecedents]
                self.research_stats [index] = Association_Stats (antecedents, consequents, support, confidence, lift, '')
        
        print ("Domain Associat to MainLang = %d, MainLang Associat to Domain = %d"\
               %(len(self.research_stats), len(self.ml2domain_stats)))

    def save_data(self):
        if (len (self.research_stats)):
            super(Collect_AssociationDomain2ML, self).save_data(self.research_stats, "Domain_Associat_to_ML")

        if (len (self.ml2domain_stats)):
            super(Collect_AssociationDomain2ML, self).save_data(self.ml2domain_stats, "ML_Associat_to_Domain")
    
    def _object_to_list(self, value):
        return super(Collect_AssociationDomain2ML, self)._object_to_list(value)
    
    def _object_to_dict(self, value):
        return super(Collect_AssociationDomain2ML, self)._object_to_dict(value)
    
    def _get_header(self, data):
        return super(Collect_AssociationDomain2ML, self)._get_header(data)   
        
        

class Collect_AssociationDomain2LIC(Collect_Research_Data):

    def __init__(self, file_name="AssoDomain2LIC_Stats"):
        super(Collect_AssociationDomain2LIC, self).__init__(file_name)
        self.topic_list = []
        self.language_list = []
        self.unique_items = {}
        self.lic2domain_stats = {}
    
    def _insert_item (self, item):
        if (self.unique_items.get (item, None) == None):
            self.unique_items [item] = True
    
    def _update_statistics(self, correlation_item):

        self.topic_list.append (correlation_item.cluster_topic_id)
        self._insert_item (correlation_item.cluster_topic_id)

        self.language_list.append (correlation_item.language)
        self._insert_item (correlation_item.language)

    def _output_encoding (self, ohe_df):
        import csv
        with open('debug_encoding_ml2lic.csv', 'w') as DEF:
            writer = csv.writer(DEF)
            headers = ohe_df.columns.values.tolist()
            writer.writerow(headers)
            for index, row in ohe_df.iterrows ():
                writer.writerow(row)

    def _one_hot_encoding (self, df, unique_items):
        encoded_vals = []
        for index, row in df.iterrows():
            x = row.x
            y = row.y
            row_set = set ([x, y])

            labels = {}
            uncommons = list(set(unique_items) - row_set)
            commons = list(set(unique_items).intersection(row_set))

            for uc in uncommons:
                labels[uc] = 0
            for com in commons:
                labels[com] = 1

            #deal with the inclution
            for com in commons:
                if not isinstance (com, str):
                    continue

                com_list = com.split ('_')
                for uc in uncommons:
                    if not isinstance (uc, str):
                        continue
                    uc_list = uc.split ('_')
                    ins = list(set(com_list).intersection(uc_list))
                    if len (ins) == len (com_list):
                        labels[uc] = 1
                        
            encoded_vals.append(labels)

        return encoded_vals

    def _get_set_value (self, set_item):
        list_item = list (set_item)
        return len(list_item), list_item[0]
    
    def _update(self):
        unique_items = [key for key in self.unique_items.keys()]
        print ("unique_items num = %d/%d" %(len(unique_items), len(self.topic_list)))
        
        Data = {'x': self.language_list, 'y': self.topic_list}  
        df = DataFrame(Data, columns=['x', 'y'])

        encoded_vals = self._one_hot_encoding (df, unique_items)
        ohe_df = pd.DataFrame(encoded_vals)
        self._output_encoding (ohe_df)

        freq_items = apriori(ohe_df, min_support=0.01, use_colnames=True)
        print ("freq_items:")
        print (freq_items.head(100))

        rules = association_rules(freq_items, metric="lift", min_threshold=1)
        print ("association_rules:")
        print (rules.head(100))

        CateId2Cate = self.LoadSwCate()
        for index, item in rules.iterrows():
            asize, antecedents = self._get_set_value(item['antecedents'])
            csize, consequents = self._get_set_value(item['consequents'])
            if asize > 1 or csize > 1:
                continue

            antecedents = str (antecedents)
            consequents = str (consequents)
            support     = item['support']
            confidence  = item['confidence']
            lift        = item['lift']

            if antecedents.isdigit () == True:
                domain = CateId2Cate[antecedents]
                self.research_stats [index] = Association_Stats (antecedents, consequents, support, confidence, lift, '')
            else:
                domain = CateId2Cate[antecedents]
                self.lic2domain_stats [index] = Association_Stats (antecedents, consequents, support, confidence, lift, '')
        
        print ("Domain Associat to LIC = %d, LIC Associat to Domain = %d"\
               %(len(self.research_stats), len(self.lic2domain_stats)))

    def save_data(self):
        if (len (self.research_stats)):
            super(Collect_AssociationDomain2LIC, self).save_data(self.research_stats, "Domain_Associat_to_LIC")

        if (len (self.lic2domain_stats)):
            super(Collect_AssociationDomain2LIC, self).save_data(self.lic2domain_stats, "LIC_Associat_to_Domain")
    
    def _object_to_list(self, value):
        return super(Collect_AssociationDomain2LIC, self)._object_to_list(value)
    
    def _object_to_dict(self, value):
        return super(Collect_AssociationDomain2LIC, self)._object_to_dict(value)
    
    def _get_header(self, data):
        return super(Collect_AssociationDomain2LIC, self)._get_header(data)   