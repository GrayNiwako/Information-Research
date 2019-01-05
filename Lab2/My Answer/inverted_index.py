# -*- coding: utf8 -*-
import os
import xml.etree.ElementTree as ET
import re
import json

def sort_dictionary(unsort_dict):
    keys = sorted(unsort_dict.keys())
    sort_dict = {}
    for key in keys:
        sort_dict[key] = unsort_dict[key]
    return sort_dict

def SPIMI_Invert(file_stream, path_count, total_word):
    dictionary = {}
    file_len = {}
    for file in file_stream:
        tree = ET.parse(path[path_count] + '/' + file)
        file_ID = document_map[file]
        root = tree.getroot()
        token_list = re.split(' ', root.find('TEXT').text)
        total_word += len(token_list)
        file_len[file_ID] = len(token_list)
        for i in range(len(token_list)):
            if token_list[i] not in dictionary.keys():
                dictionary[token_list[i]] = {'rate': 1, 'pos': {file_ID: {'rate': 1, 'pos': [i]}}}
            else:
                dictionary[token_list[i]]['rate'] += 1
                if file_ID not in dictionary[token_list[i]]['pos'].keys():
                    dictionary[token_list[i]]['pos'][file_ID] = {'rate': 1, 'pos': [i]}
                else:
                    dictionary[token_list[i]]['pos'][file_ID]['rate'] += 1
                    dictionary[token_list[i]]['pos'][file_ID]['pos'].append(i)

    token_dict_tmp = {'a': {}, 'b': {}, 'c': {}, 'd': {}, 'e': {}, 'f': {}, 'g': {},
                'h': {}, 'i': {}, 'j': {}, 'k': {}, 'l': {}, 'm': {}, 'n': {},
                'o': {}, 'p': {}, 'q': {}, 'r': {}, 's': {}, 't': {},
                'u': {}, 'v': {}, 'w': {}, 'x': {}, 'y': {}, 'z': {}, '_other': {}}
    for token in dictionary.keys():
        for name in dictionary[token]['pos'].keys():
            dictionary[token]['pos'][name]['rate'] = dictionary[token]['pos'][name]['rate'] / file_len[name] * 1.0
        if token == '':
            token_dict_tmp['_other'][token] = dictionary[token]
        elif token[0] in token_dict_tmp.keys():
            token_dict_tmp[token[0]][token] = dictionary[token]
        else:
            token_dict_tmp['_other'][token] = dictionary[token]
    for key in token_dict_tmp.keys():
        token_dict_tmp[key] = sort_dictionary(token_dict_tmp[key])
        file1 = open('./index_file/index_' + key + '_' + str(block_num) + '.json', 'w')
        json.dump(token_dict_tmp[key], file1)
        file1.close()
        print('index_' + key + '_' + str(block_num) + ' succeed')
    return total_word

if (not (os.path.exists('./index_file'))):
    os.mkdir('./index_file')

path = []
path.append('../lab1/code/Answer/document/AP')
path.append('../lab1/code/Answer/document/DOE')
path.append('../lab1/code/Answer/document/FR')
path.append('../lab1/code/Answer/document/WSJ')
path.append('../lab1/code/Answer/document/ZIFF')

file_num = 0
document_map = {}
for count in range(len(path)):
    for a in os.walk(path[count]):
        document_files = a[2]
        for f in document_files:
            document_map[f] = file_num
            file_num += 1
file0 = open('./map.json', 'w')
json.dump(document_map, file0)
file0.close()
print('map succeed')

block_num = 0
total_word = 0

for count in range(len(path)):
    for a in os.walk(path[count]):
        document_files = a[2]
        start = 0
        while start < len(document_files):
            end = start + 10000
            if end > len(document_files):
                end = len(document_files)
            total_word = SPIMI_Invert(document_files[start:end], count, total_word)
            start += 10000
            block_num += 1

print('block_num = ' + str(block_num))  # block_num = 77
print('total_word = ' + str(total_word))  # total_word = 190163909

index_dict = {}

for a in os.walk('./index_file'):
    document_files = a[2]
    count = len(document_files)
    for file_name in document_files:
        file2 = open('./index_file/' + file_name, 'r')
        dict_tmp = json.load(file2)
        file2.close()
        if count % block_num == 0:
            index_dict = dict_tmp.copy()
            count -= 1
        else:
            for word in dict_tmp.keys():
                if word not in index_dict.keys():
                    index_dict[word] = dict_tmp[word]
                else:
                    index_dict[word]['rate'] += dict_tmp[word]['rate']
                    index_dict[word]['pos'].update(dict_tmp[word]['pos'])
            count -= 1
        print(file_name[:-5] + ' load succeed')
        os.remove('./index_file/' + file_name)

        if count % block_num == 0:
            for word in index_dict.keys():
                index_dict[word]['rate'] = index_dict[word]['rate'] / total_word * 1.0
            index_dict = sort_dictionary(index_dict)
            file3 = open('./index_file/' + file_name[:-7] + '.json', 'w')
            json.dump(index_dict, file3)
            file3.close()
            print(file_name[:-7] + ' succeed')
