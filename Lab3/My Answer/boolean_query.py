# -*- coding: utf8 -*-
import os
import re
import json

def query_index(token):
    if token[0] >= 'a' and token[0] <= 'z':
        path = '../lab2/index_file/index_' + token[0] + '.json'
    else:
        path = '../lab2/index_file/index__other.json'
    file1 = open(path, 'r')
    index_dict = json.load(file1)
    file1.close()
    docno_list = [key for key in index_dict[token]['pos'].keys()]
    return docno_list

if (not (os.path.exists('./boolean_query_topics'))):
    os.mkdir('./boolean_query_topics')

time = input('Please enter your query number:')
print('Please enter your boolean query:')
boolean_str = input()
print()

file2 = open('../lab2/map.json', 'r')
docno_dict = json.load(file2)
file2.close()

str_list = re.split(' ', boolean_str)
posting_list = query_index(str_list[0])
boolean_way = ''
for i in range(1, len(str_list)):
    if str_list[i] == 'AND' or str_list[i] == 'OR':
        boolean_way = str_list[i]
    elif str_list[i] == 'NOT':
        boolean_way += ' NOT'
    else:
        posting_list2 = query_index(str_list[i])
        if boolean_way == 'AND':
            posting_list_tmp = [docno for docno in posting_list if docno in posting_list2]
        elif boolean_way == 'OR':
            posting_list_tmp0 = posting_list + posting_list2
            posting_list_tmp1 = [int(elem) for elem in posting_list_tmp0]
            posting_list_tmp1.sort()
            i = 1
            while (i < len(posting_list_tmp1)):
                if posting_list_tmp1[i] == posting_list_tmp1[i - 1]:
                    posting_list_tmp1.remove(posting_list_tmp1[i - 1])
                else:
                    i += 1
            posting_list_tmp = [str(elem) for elem in posting_list_tmp1]
        elif boolean_way == 'AND NOT':
            posting_list_tmp = [docno for docno in posting_list if docno not in posting_list2]
        else:
            docno_list = [value for value in docno_dict.values()]
            list_tmp = [docno for docno in posting_list2 if docno not in posting_list]
            posting_list_tmp = [docno for docno in docno_list if docno not in list_tmp]
        posting_list = posting_list_tmp

posting_list_int = [int(elem) for elem in posting_list]
posting_list_int.sort()
file3 = open('./boolean_query_topics/boolean_query_res' + str(time) + '.txt', 'w')
file3.write('query number: ' + str(time) + '\n')
file3.write('boolean query: ' + boolean_str + '\n')
file3.write('boolean query result:\n')
print('boolean query result:')
number = 0
for key,value in docno_dict.items():
    if value == posting_list_int[number]:
        print(key[:-4])
        file3.write(key[:-4] + '\n')
        number += 1
        if number == len(posting_list_int):
            break
