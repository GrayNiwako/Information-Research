# -*- coding: utf8 -*-
import os
import re
import json
import xml.etree.ElementTree as ET
import math
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer

def query_index(token):
    if token[0] >= 'a' and token[0] <= 'z':
        path = '../lab2/index_file/index_' + token[0] + '.json'
    else:
        path = '../lab2/index_file/index__other.json'
    file1 = open(path, 'r')
    index_dict = json.load(file1)
    file1.close()
    if token in index_dict.keys():
        return index_dict[token]
    else:
        return -1

def conine_score(u, v):
    fenzi = 0
    fenmu1 = 0
    fenmu2 = 0
    for i in range(len(u)):
        fenzi += u[i] * v[i]
        fenmu1 += u[i] * u[i]
        fenmu2 += v[i] * v[i]
    return fenzi / (math.sqrt(fenmu1) * math.sqrt(fenmu2)) * 1.0

def query_synonym_expansion(word_list):
    tmp_list = []
    for word in word_list:
        tmp_list.append(word)
        synsets = wn.synsets(word)
        if len(synsets) != 0:
            for name in synsets[0].lemma_names():
                name = name.lower()
                if name == word:
                    continue
                if (name.find('-') != -1) or (name.find('_') != -1):
                    continue
                if name not in stopwords.words('english'):
                    name_preprocess = porter_stemmer.stem(lemmatizaer.lemmatize(name))
                    if name_preprocess not in tmp_list:
                        tmp_list.append(name_preprocess)
    return tmp_list

def get_result(topic, score, method):
    sort_tmp = sorted(score.items(), key=lambda x: x[1], reverse=True)
    sort_score = {}
    for elem in sort_tmp:
        sort_score[elem[0]] = elem[1]

    rank = 1
    for docno in sort_score.keys():
        print(topic + ' 0 ' + docno_dict[docno]['DOC_name'] + ' ' + str(rank) + ' ' +
              str(sort_score[docno]) + ' 10152130122_' + method + '_synonym')
        if method == 'TF-IDF':
            file3.write(topic + ' 0 ' + docno_dict[docno]['DOC_name'] + ' ' + str(rank) + ' ' +
                        str(sort_score[docno]) + ' 10152130122_' + method + '_synonym\n')
        elif method == 'BM25':
            file4.write(topic + ' 0 ' + docno_dict[docno]['DOC_name'] + ' ' + str(rank) + ' ' +
                        str(sort_score[docno]) + ' 10152130122_' + method + '_synonym\n')
        else:
            file5.write(topic + ' 0 ' + docno_dict[docno]['DOC_name'] + ' ' + str(rank) + ' ' +
                        str(sort_score[docno]) + ' 10152130122_' + method + '_synonym\n')
        rank += 1
        if rank == 1001:
            break

    print('query Topic_' + topic + ' ' + method + ' succeed')

if (not (os.path.exists('./synonym_expansion_result'))):
    os.mkdir('./synonym_expansion_result')

total_file_num = 741856
total_file_len = 189470967

file2 = open('../lab3/map2.json', 'r')
docno_dict = json.load(file2)
file2.close()
print('map2 load succeed')

avg_file_len = total_file_len / total_file_num * 1.0
print('avg_file_len = ' + str(avg_file_len)) # 255.40127329293017

lemmatizaer = WordNetLemmatizer()
porter_stemmer = PorterStemmer()

k = 1.5
b = 0.75
file3 = open(u'./synonym_expansion_result/10152130122_钱庭涵_TF-IDF_synonym.res', 'w')
file4 = open(u'./synonym_expansion_result/10152130122_钱庭涵_BM25_synonym.res', 'w')
file5 = open(u'./synonym_expansion_result/10152130122_钱庭涵_VSM_synonym.res', 'w')

for a in os.walk('../lab1/code/Answer/query'):
    document_files = a[2]
    for f in document_files:
        tree = ET.parse('../lab1/code/Answer/query/' + f)
        root = tree.getroot()
        query_title = re.split(' ', root.find('title').text.strip(' ').replace('`', '').replace("'", "")[6:])
        query_desc = re.split(' ', root.find('desc').text.strip(' ').replace('`', '').replace("'", "")[9:])
        query_narr = re.split(' ', root.find('narr').text.strip(' ').replace('`', '').replace("'", "")[5:])
        query_list0 = query_title + query_desc + query_narr
        while '' in query_list0:
            query_list0.remove('')

        query_list = query_synonym_expansion(query_list0)

        score_tf_idf = {}
        score_bm25 = {}
        query_tf = {}
        idf_token = {}
        doc_w = {}
        for i in range(len(query_list)):
            if query_list[i] not in query_tf:
                query_tf[query_list[i]] = 1
            else:
                query_tf[query_list[i]] += 1

            token_dict = query_index(query_list[i])
            if token_dict == -1:
                idf_token[query_list[i]] = 0
                continue

            idf_t = math.log(total_file_num / len(token_dict['pos']) * 1.0)
            idf_qi = math.log((total_file_num - len(token_dict['pos']) + 0.5) /
                              (len(token_dict['pos']) + 0.5) * 1.0)
            if query_list[i] not in idf_token:
                idf_token[query_list[i]] = math.log(total_file_num / len(token_dict['pos']) * 1.0)

            for docno in token_dict['pos'].keys():
                if docno not in score_tf_idf.keys():
                    score_tf_idf[docno] = 0
                    score_bm25[docno] = 0
                    doc_w[docno] = {}
                score_tf_idf[docno] += token_dict['pos'][docno]['rate'] * idf_t
                score_bm25[docno] += idf_qi * token_dict['pos'][docno]['rate'] * (k+1) / \
                                     (token_dict['pos'][docno]['rate'] + k *
                                      (1-b + b * docno_dict[docno]['DOC_length'] / avg_file_len * 1.0)) * 1.0
                doc_w[docno][query_list[i]] = token_dict['pos'][docno]['rate'] * idf_token[query_list[i]]

        query_vector = []
        for i in range(len(query_list)):
            query_vector.append(query_tf[query_list[i]] / len(query_list) * 1.0 * idf_token[query_list[i]])

        score_VSM = {}
        for docno in doc_w.keys():
            doc_vector = []
            for i in range(len(query_list)):
                if query_list[i] in doc_w[docno]:
                    doc_vector.append(doc_w[docno][query_list[i]])
                else:
                    doc_vector.append(0)
            score_VSM[docno] = conine_score(query_vector, doc_vector)

        get_result(f[6:-4], score_tf_idf, 'TF-IDF')
        get_result(f[6:-4], score_bm25, 'BM25')
        get_result(f[6:-4], score_VSM, 'VSM')

        print('query ' + f[:-4] + ' succeed')

file3.close()
file4.close()
file5.close()
