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

def get_orignal_query(way):
    file2 = open('./query_topics/10152130122_钱庭涵_' + query_res_list[way] + '.res', 'r')
    lines = file2.readlines()
    file2.close()
    query_dict = {}
    count = 0
    for topic in range(151, 201):
        query_dict[topic] = []
        while count < 1000:
            res = re.split(' ', lines[count + (topic - 151) * 1000].strip('\n'))
            query_dict[topic].append(res[2])
            count += 1
        count = 0
    print('orignal query 10152130122_钱庭涵_' + query_res_list[way] + '.res load succeed')
    return query_dict

def get_qrels():
    file3 = open('../lab3/qrels_for_disk12/qrels.res', 'r')
    lines = file3.readlines()
    file3.close()
    qrels_dict = {}
    for line in lines:
        tmp_line = re.split(' ', line.strip('\n'))
        if tmp_line[0] not in qrels_dict.keys():
            qrels_dict[tmp_line[0]] = {'Cr':[], 'Cnr':[]}
        if tmp_line[3] == '0':
            qrels_dict[tmp_line[0]]['Cnr'].append(tmp_line[2])
        else:
            qrels_dict[tmp_line[0]]['Cr'].append(tmp_line[2])
    print('qrels.res load succeed')
    return qrels_dict

def relevance_feedback(doc_list, number, k):
    Cr = []
    Cnr = []
    for doc in doc_list[:k]:
        if doc in qrels[number]['Cr']:
            Cr.append(doc)
        else:
            Cnr.append(doc)
    return Cr, Cnr

def pseudo_relevance_feedback(doc_list, k):
    return doc_list[:k], doc_list[k:]

def query_update(query_0, doc_vector, Cr, Cnr, alpha, beta, gama):
    query_m = query_0
    for i in range(len(query_0)):
        sum_cr = 0
        sum_cnr = 0
        for docname in Cr:
            sum_cr += doc_vector[docname][i]
        for docname in Cnr:
            sum_cnr += doc_vector[docname][i]
        if len(Cr) == 0:
            query_m[i] = alpha * query_0[i] - gama / len(Cnr) * sum_cnr * 1.0
        elif len (Cnr) == 0:
            query_m[i] = alpha * query_0[i] + beta / len(Cr) * sum_cr * 1.0
        else:
            query_m[i] = alpha * query_0[i] + beta / len(Cr) * sum_cr * 1.0 - gama / len(Cnr) * sum_cnr * 1.0
    return query_m

def conine_score(u, v):
    fenzi = 0
    fenmu1 = 0
    fenmu2 = 0
    for i in range(len(u)):
        fenzi += u[i] * v[i]
        fenmu1 += u[i] * u[i]
        fenmu2 += v[i] * v[i]
    return fenzi / (math.sqrt(fenmu1) * math.sqrt(fenmu2)) * 1.0

def new_query(query_m, doc_vector, feedback, topic):
    score = {}
    for docname in doc_vector.keys():
        score[docname] = conine_score(query_m, doc_vector[docname])

    sort_tmp = sorted(score.items(), key=lambda x: x[1], reverse=True)
    sort_score = {}
    for elem in sort_tmp:
        sort_score[elem[0]] = elem[1]

    rank = 1
    for docname in sort_score.keys():
        print(topic + ' 0 ' + docname + ' ' + str(rank) + ' ' +
              str(sort_score[docname]) + ' 10152130122_' + query_res_list[int(method)] + '_' + feedback)
        if feedback == 'RF':
            file4.write(topic + ' 0 ' + docname + ' ' + str(rank) + ' ' + str(sort_score[docname])
                        + ' 10152130122_' + query_res_list[int(method)] + '_RF\n')
        else:
            file5.write(topic + ' 0 ' + docname + ' ' + str(rank) + ' ' + str(sort_score[docname])
                        + ' 10152130122_' + query_res_list[int(method)] + '_PRF\n')
        rank += 1

    print('query Topic_' + topic + ' ' + feedback + ' succeed')

if (not (os.path.exists('./query_expansion_result'))):
    os.mkdir('./query_expansion_result')

query_res_list = ['TF-IDF', 'BM25', 'VSM']
method = input('Please enter your query method:')
# 0 = TF-IDF, 1 = BM25, 2 = VSM
orignal_query = get_orignal_query(int(method))
qrels = get_qrels()

total_file_num = 741856
top_k1 = 50
alpha1 = 1
beta1 = 1
gama1 = 1
top_k2 = 10
alpha2 = 1
beta2 = 0
gama2 = 0.15

file0 = open('../lab3/map2.json', 'r')
docno_dict = json.load(file0)
file0.close()
print('map2 load succeed')

file4 = open('./query_expansion_result/10152130122_钱庭涵_' + query_res_list[int(method)] + '_RF.res', 'w')
file5 = open('./query_expansion_result/10152130122_钱庭涵_' + query_res_list[int(method)] + '_PRF.res', 'w')

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

        document_list = orignal_query[int(f[6:-4])]

        RF_Cr, RF_Cnr = relevance_feedback(document_list, f[6:-4], top_k1)
        print('RF_Cr and RF_Cnr succeed')
        PRF_Cr, PRF_Cnr = pseudo_relevance_feedback(document_list, top_k2)
        print('PRF_Cr and PRF_Cnr succeed')

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
                docname = docno_dict[docno]['DOC_name']
                if docname not in document_list:
                    continue
                if docname not in doc_w.keys():
                    doc_w[docname] = {}
                doc_w[docname][query_list[i]] = token_dict['pos'][docno]['rate'] * idf_token[query_list[i]]

        q0 = []
        for i in range(len(query_list)):
            q0.append(query_tf[query_list[i]] / len(query_list) * 1.0 * idf_token[query_list[i]])
        print('query vector succeed')

        doc_vector_dict = {}
        for docname in doc_w.keys():
            doc_vector_dict[docname] = []
            for i in range(len(query_list)):
                if query_list[i] in doc_w[docname]:
                    doc_vector_dict[docname].append(doc_w[docname][query_list[i]])
                else:
                    doc_vector_dict[docname].append(0)
        print('doc vector succeed')

        RF_qm = query_update(q0, doc_vector_dict, RF_Cr, RF_Cnr, alpha1, beta1, gama1)
        print('RF query update succeed')
        PRF_qm = query_update(q0, doc_vector_dict, PRF_Cr, PRF_Cnr, alpha2, beta2, gama2)
        print('PRF query update succeed')

        new_query(RF_qm, doc_vector_dict, 'RF', f[6:-4])
        new_query(PRF_qm, doc_vector_dict, 'PRF', f[6:-4])

        print('query ' + f[:-4] + ' succeed')

file4.close()
file5.close()
