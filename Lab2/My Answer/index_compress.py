# -*- coding: utf8 -*-
import os
import json

if (not (os.path.exists('./index_compress_file'))):
    os.mkdir('./index_compress_file')

file1 = open('./map.json', 'r')
document_map = json.load(file1)
file1.close()

for a in os.walk('./index_file'):
    document_files = a[2]
    for file in document_files:
        file2 = open('./index_file/' + file, 'r')
        index_dict = json.load(file2)
        file2.close()
        for word in index_dict.keys():
            pos_tmp = [key for key in index_dict[word]['pos'].keys()]
            pos_list_cpy = pos_tmp.copy()
            pos_y_encode = []
            pos_list = [int(key, 10) for key in pos_tmp]
            start_ID = pos_list[0]
            for i in range(len(pos_list)):
                if i != 0:
                    pos_list[i] -= start_ID
                if pos_list[i] == 1:
                    encode = '0'
                else:
                    offset = str(bin(pos_list[i]))[3:]
                    length = ''
                    for j in range(len(offset)):
                        length += '1'
                    length += '0'
                    encode = length + offset
                pos_y_encode.append(encode)

            new_dict = {}
            for i in range(len(pos_y_encode)):
                new_dict[pos_y_encode[i]] = index_dict[word]['pos'][pos_list_cpy[i]]
            index_dict[word]['pos'] = new_dict

        file3 = open('./index_compress_file/' + file[:-5] + '_compress.json', 'w')
        json.dump(index_dict, file3)
        file3.close()
        print(file[:-5] + '_compress succeed')


