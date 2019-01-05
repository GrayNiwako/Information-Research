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

if (not (os.path.exists('./ranking_query_topics'))):
    os.mkdir('./ranking_query_topics')

document_path = []
document_path.append('../lab1/code/Answer/document/AP')
document_path.append('../lab1/code/Answer/document/DOE')
document_path.append('../lab1/code/Answer/document/FR')
document_path.append('../lab1/code/Answer/document/WSJ')
document_path.append('../lab1/code/Answer/document/ZIFF')

total_file_num = 0
total_file_len = 0
document_map = {}
for count in range(len(document_path)):
    for a in os.walk(document_path[count]):
        document_files = a[2]
        for f in document_files:
            tree = ET.parse(document_path[count] + '/' + f)
            root = tree.getroot()
            token_list = re.split(' ', root.find('TEXT').text.strip(' '))
            total_file_len += len(token_list)
            document_map[total_file_num] = {'DOC_name': f[:-4], 'DOC_length': len(token_list)}
            total_file_num += 1
file0 = open('./map2.json', 'w')
json.dump(document_map, file0)
file0.close()
print('map2 succeed')
print('total_file_num = ' + str(total_file_num)) # 741856
print('total_file_len = ' + str(total_file_len)) # 189470967

# total_file_num = 741856
# total_file_len = 189470967

file2 = open('./map2.json', 'r')
docno_dict = json.load(file2)
file2.close()

avg_file_len = total_file_len / total_file_num * 1.0
print('avg_file_len = ' + str(avg_file_len)) # 255.40127329293017

k = 1.5
b = 0.75
file3 = open(u'./ranking_query_topics/10152130122_钱庭涵_TF-IDF.res', 'w')
file4 = open(u'./ranking_query_topics/10152130122_钱庭涵_BM25.res', 'w')

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

        score_tf_idf = {}
        score_bm25 = {}
        for i in range(len(query_list)):
            token_dict = query_index(query_list[i])
            if token_dict == -1:
                continue
            idf_t = math.log(total_file_num / len(token_dict['pos']) * 1.0)
            idf_qi = math.log((total_file_num - len(token_dict['pos']) + 0.5) /
                              (len(token_dict['pos']) + 0.5) * 1.0)

            for docno in token_dict['pos'].keys():
                if docno not in score_tf_idf.keys():
                    score_tf_idf[docno] = 0
                    score_bm25[docno] = 0
                score_tf_idf[docno] += token_dict['pos'][docno]['rate'] * idf_t
                score_bm25[docno] += idf_qi * token_dict['pos'][docno]['rate'] * (k+1) / \
                                     (token_dict['pos'][docno]['rate'] + k *
                                      (1-b + b * docno_dict[docno]['DOC_length'] / avg_file_len * 1.0)) * 1.0

        sort_tmp1 = sorted(score_tf_idf.items(), key=lambda x: x[1], reverse=True)
        sort_score_tf_idf = {}
        for elem in sort_tmp1:
            sort_score_tf_idf[elem[0]] = elem[1]
        sort_tmp2 = sorted(score_bm25.items(), key=lambda x: x[1], reverse=True)
        sort_score_bm25 = {}
        for elem in sort_tmp2:
            sort_score_bm25[elem[0]] = elem[1]

        rank = 1
        for docno in sort_score_tf_idf.keys():
            print(f[6:-4] + ' 0 ' + docno_dict[docno]['DOC_name'] + ' ' + str(rank) + ' ' +
                  str(sort_score_tf_idf[docno]) + ' 10152130122_TF-IDF')
            file3.write(f[6:-4] + ' 0 ' + docno_dict[docno]['DOC_name'] + ' ' + str(rank) +
                        ' ' + str(sort_score_tf_idf[docno]) + ' 10152130122_TF-IDF\n')
            rank += 1
            if rank == 1001:
                break

        rank = 1
        for docno in sort_score_bm25.keys():
            print(f[6:-4] + ' 0 ' + docno_dict[docno]['DOC_name'] + ' ' + str(rank) + ' ' +
                  str(sort_score_bm25[docno]) + ' 10152130122_BM25')
            file4.write(f[6:-4] + ' 0 ' + docno_dict[docno]['DOC_name'] + ' ' + str(rank) +
                        ' ' + str(sort_score_bm25[docno]) + ' 10152130122_BM25\n')
            rank += 1
            if rank == 1001:
                break

        print('query ' + f[:-4] + ' succeed')

file3.close()
file4.close()
