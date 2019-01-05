# -*- coding: utf8 -*-
import os
import re
import json
import xml.etree.ElementTree as ET
import math

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

total_file_num = 741856

file2 = open('../lab3/map2.json', 'r')
docno_dict = json.load(file2)
file2.close()

file3 = open(u'./query_topics/10152130122_钱庭涵_VSM.res', 'w')

for a in os.walk('../lab1/code/Answer/query'):
    document_files = a[2]
    for f in document_files:
        tree = ET.parse('../lab1/code/Answer/query/' + f)
        root = tree.getroot()
        query_title = re.split(' ', root.find('title').text.strip(' ').replace('`', '').replace("'", "")[6:])
        query_desc = re.split(' ', root.find('desc').text.strip(' ').replace('`', '').replace("'", "")[9:])
        query_narr = re.split(' ', root.find('narr').text.strip(' ').replace('`', '').replace("'", "")[5:])
        query_list = query_title + query_desc + query_narr
        while '' in query_list:
            query_list.remove('')

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

            if query_list[i] not in idf_token:
                idf_token[query_list[i]] = math.log(total_file_num / len(token_dict['pos']) * 1.0)

            for docno in token_dict['pos'].keys():
                if docno not in doc_w.keys():
                    doc_w[docno] = {}
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

        sort_tmp1 = sorted(score_VSM.items(), key=lambda x: x[1], reverse=True)
        sort_score_VSM = {}
        for elem in sort_tmp1:
            sort_score_VSM[elem[0]] = elem[1]

        rank = 1
        for docno in sort_score_VSM.keys():
            print(f[6:-4] + ' 0 ' + docno_dict[docno]['DOC_name'] + ' ' + str(rank) + ' ' +
                  str(sort_score_VSM[docno]) + ' 10152130122_VSM')
            file3.write(f[6:-4] + ' 0 ' + docno_dict[docno]['DOC_name'] + ' ' + str(rank) +
                        ' ' + str(sort_score_VSM[docno]) + ' 10152130122_VSM\n')
            rank += 1
            if rank == 1001:
                break

        print('query ' + f[:-4] + ' succeed')

file3.close()
