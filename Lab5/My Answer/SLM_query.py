# -*- coding: utf8 -*-
import os
import re
import json
import xml.etree.ElementTree as ET

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

def get_result(topic, score, method):
    sort_tmp = sorted(score.items(), key=lambda x: x[1], reverse=True)
    sort_score = {}
    for elem in sort_tmp:
        sort_score[elem[0]] = elem[1]

    rank = 1
    for docno in sort_score.keys():
        print(topic + ' 0 ' + docno_dict[docno]['DOC_name'] + ' ' + str(rank) + ' ' +
              str(sort_score[docno]) + ' 10152130122_SLM_' + method)
        if method == 'Interpolate':
            file3.write(topic + ' 0 ' + docno_dict[docno]['DOC_name'] + ' ' + str(rank) + ' ' +
                        str(sort_score[docno]) + ' 10152130122_SLM_' + method + '\n')
        else:
            file4.write(topic + ' 0 ' + docno_dict[docno]['DOC_name'] + ' ' + str(rank) + ' ' +
                        str(sort_score[docno]) + ' 10152130122_SLM_' + method + '\n')
        rank += 1
        if rank == 1001:
            break

    print('query Topic_' + topic + ' ' + method + ' succeed')

if (not (os.path.exists('./SLM_query_topics'))):
    os.mkdir('./SLM_query_topics')

file2 = open('../lab3/map2.json', 'r')
docno_dict = json.load(file2)
file2.close()
print('map2 load succeed')

alpha1 = 0.95
alpha2 = 0.9
file3 = open(u'./SLM_query_topics/10152130122_钱庭涵_SLM_Interpolate.res', 'w')
file4 = open(u'./SLM_query_topics/10152130122_钱庭涵_SLM_Dirichlet.res', 'w')

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

        score_SLM_interpolate = {}
        score_SLM_dirichlet = {}
        effective_token_dict = {}

        for i in range(len(query_list)):
            token_dict = query_index(query_list[i])
            if token_dict == -1:
                continue

            effective_token_dict[query_list[i]] = {'total_rate': token_dict['rate'],
                                                   'docno_list': token_dict['pos'].keys()}
            for docno in token_dict['pos'].keys():
                if docno not in score_SLM_interpolate.keys():
                    score_SLM_interpolate[docno] = 1
                    score_SLM_dirichlet[docno] = 1
                score_SLM_interpolate[docno] *= (
                        alpha1 * token_dict['pos'][docno]['rate'] + (1 - alpha1) * token_dict['rate'])
                score_SLM_dirichlet[docno] *= (
                        (int(token_dict['pos'][docno]['rate'] * docno_dict[docno]['DOC_length'])
                         + alpha2 * token_dict['rate']) / (docno_dict[docno]['DOC_length'] + alpha2) * 1.0)
        print('LM succeedd')

        for token in effective_token_dict.keys():
            for docno in score_SLM_interpolate.keys():
                if docno not in effective_token_dict[token]['docno_list']:
                    score_SLM_interpolate[docno] *= ((1 - alpha1) * effective_token_dict[token]['total_rate'])
                    score_SLM_dirichlet[docno] *= (
                            (alpha2 * effective_token_dict[token]['total_rate']) / (
                            docno_dict[docno]['DOC_length'] + alpha2) * 1.0)
        print('smoothing succeed')

        get_result(f[6:-4], score_SLM_interpolate, 'Interpolate')
        get_result(f[6:-4], score_SLM_dirichlet, 'Dirichlet')

        print('query ' + f[:-4] + ' succeed')

file3.close()
file4.close()
