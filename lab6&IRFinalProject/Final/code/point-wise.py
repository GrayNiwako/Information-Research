# -*- coding: utf8 -*-
import os
import nltk
import xml.etree.ElementTree as ET
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer
import re
import json
import math

def create_necessary_folders(data):
    if (not (os.path.exists('./' + data))):
        os.mkdir('./' + data)
    if (not (os.path.exists('./' + data + '/query'))):
        os.mkdir('./' + data + '/query')
    if (not (os.path.exists('./' + data + '/document'))):
        os.mkdir('./' + data + '/document')
    if (not (os.path.exists('./' + data + '/index_file'))):
        os.mkdir('./' + data + '/index_file')
    if (not (os.path.exists('./' + data + '/document_len_map'))):
        os.mkdir('./' + data + '/document_len_map')
    if (not (os.path.exists('./' + data + '/document_total'))):
        os.mkdir('./' + data + '/document_total')
    if (not (os.path.exists('./' + data + '/features'))):
        os.mkdir('./' + data + '/features')
    if (not (os.path.exists('./' + data + '/total_features'))):
        os.mkdir('./' + data + '/total_features')
    if data == 'training':
        if (not (os.path.exists('./' + data + '/labels'))):
            os.mkdir('./' + data + '/labels')

def preprocess_query(data):
    query_path = '../2017TAR/' + data + '/extracted_data'

    for a in os.walk(query_path):
        document_files = a[2]
        for document_file in document_files:
            if document_file[-5:] == '.pids':
                file1 = open(query_path + '/' + document_file, 'r')
                lines = file1.readlines()
                file1.close()
                file2 = open('./' + data + '/query/' + document_file, 'w')
                for line in lines:
                    tmp1 = re.split(' ', line.strip('\n'))
                    file2.write(tmp1[1] + '\n')
                file2.close()

            if document_file[-6:] == '.title':
                file3 = open(query_path + '/' + document_file, 'r')
                lines = file3.read()
                file3.close()
                tmp2 = re.split(' ', lines.strip('\n'))
                tmp3 = wordlist_pre_process(' '.join(tmp2[1:]))
                file4 = open('./' + data + '/query/' + document_file, 'w')
                file4.write(tmp3 + '\n')
                file4.close()

            print(document_file, 'process succeed')

def wordlist_pre_process(sentence):
    tokens = nltk.word_tokenize(sentence.lower())
    lemmatizaer = WordNetLemmatizer()
    stem_list = [PorterStemmer().stem(lemmatizaer.lemmatize(w)) for w in tokens \
                    if (w not in stopwords.words('english'))]
    tmp = re.split('[][():;/|.,*"+=<> \\?!^@_$#%{}-]+', ' '.join(stem_list))
    tmp1 = ' '.join(tmp)
    process_sentence = tmp1.replace('`', '').replace("'", "").strip(' ')
    return process_sentence

def preprocess_document(data):
    document_path = '../docs.' + data + '/topics_raw_docs'
    count = 0
    for a in os.walk(document_path):
        if count == 0:
            count = 1
            continue
        folder_tmp = re.split('/', a[0].replace('\\', '/'))
        folder = folder_tmp[-1]
        document_files = a[2]

        if (not (os.path.exists('./' + data + '/document/' + folder))):
            os.mkdir('./' + data + '/document/' + folder)

        for document_file in document_files:
            try:
                root = ET.parse(document_path + '/' + folder + '/' + document_file)
                tmp1 = root.find('MedlineCitation').find('Article')
                title = tmp1.find('ArticleTitle').text
                new_title = wordlist_pre_process(title)
                new_text = ''
                tmp2 = tmp1.find('Abstract')
                if tmp2 != None:
                    tmp3 = [f.text for f in tmp2.findall('AbstractText')]
                    text = ' '.join(tmp3)
                    new_text = wordlist_pre_process(text)
                file1 = open('./' + data + '/document/' + folder + '/' + document_file + '.xml', 'w')
                file1.write('<document>\n<title>' + new_title + '</title>\n<text>' + new_text + '</text>\n</document>')
                file1.close()
                print(folder, document_file, 'process succeed')
            except:
                print(folder, document_file, 'process fail')

def document_index_create(data, folder):
    if (not (os.path.exists('./' + data + '/index_file/' + folder))):
        os.mkdir('./' + data + '/index_file/' + folder)

    document_path = './' + data + '/document/' + folder
    document_len_map = {}
    total_file_num = 0
    block_num = 0
    start = 0

    for a in os.walk(document_path):
        document_files = a[2]
        while start < len(document_files):
            end = start + 10000
            if end > len(document_files):
                end = len(document_files)
            document_len_map, block_num, total_file_num = SPIMI_Invert(data, document_files[start:end], folder,
                                                                       document_len_map, block_num, total_file_num)
            start += 10000
            block_num += 1

    print(folder, 'block_num =', str(block_num))

    index_dict = {}

    for b in os.walk('./' + data + '/index_file/' + folder):
        index_files = b[2]
        count = len(index_files)
        for index_name in index_files:
            file1 = open('./' + data + '/index_file/'+ folder + '/' + index_name, 'r')
            dict_tmp = json.load(file1)
            file1.close()
            if count % block_num == 0:
                index_dict = dict_tmp.copy()
                count -= 1
            else:
                for word in dict_tmp.keys():
                    if word not in index_dict.keys():
                        index_dict[word] = dict_tmp[word]
                    else:
                        index_dict[word].update(dict_tmp[word])
                count -= 1
            print(folder, index_name[:-5], 'load succeed')
            os.remove('./' + data + '/index_file/' + folder + '/' + index_name)

            if count % block_num == 0:
                index_dict = sort_dictionary(index_dict)
                file2 = open('./' + data + '/index_file/' + folder + '/' + index_name[:-7] + '.json', 'w')
                json.dump(index_dict, file2)
                file2.close()
                print(folder, index_name[:-7] + ' succeed')

        print(folder, 'index create succeed')

    file3 = open('./' + data + '/document_len_map/document_len_map_' + folder + '.json', 'w')
    json.dump(document_len_map, file3)
    file3.close()
    file4 = open('./' + data + '/document_total/document_total_' + folder + '.txt', 'w')
    file4.write('total_file_num = ' + str(total_file_num) + '\ntotal_file_len = ' + str(len(document_len_map)) + '\n')

    print(folder, 'document_len_map total_file_num total_file_len succeed')

def sort_dictionary(unsort_dict):
    keys = sorted(unsort_dict.keys())
    sort_dict = {}
    for key in keys:
        sort_dict[key] = unsort_dict[key]
    return sort_dict

def SPIMI_Invert(data, file_stream, folder, document_len_map, block_num, total_file_num):
    dictionary = {}
    for file in file_stream:
        try:
            tree = ET.parse('./' + data + '/document/' + folder + '/' + file)
            root = tree.getroot()
            file_name = file[:-4]

            token_list = re.split('[ ]+', root.find('title').text)
            tmp1 = root.find('text').text
            if tmp1 != None:
                token_list += re.split('[ ]+', tmp1)
            document_len_map[file_name] = len(token_list)
            total_file_num += document_len_map[file_name]

            for i in range(len(token_list)):
                if token_list[i] not in dictionary.keys():
                    dictionary[token_list[i]] = {file_name: 1}
                else:
                    if file_name not in dictionary[token_list[i]].keys():
                        dictionary[token_list[i]][file_name] = 0
                    dictionary[token_list[i]][file_name] += 1
        except:
            os.remove('./' + data + '/document/' + folder + '/' + file)

    token_dict_tmp = {'a': {}, 'b': {}, 'c': {}, 'd': {}, 'e': {}, 'f': {}, 'g': {},
                      'h': {}, 'i': {}, 'j': {}, 'k': {}, 'l': {}, 'm': {}, 'n': {},
                      'o': {}, 'p': {}, 'q': {}, 'r': {}, 's': {}, 't': {},
                      'u': {}, 'v': {}, 'w': {}, 'x': {}, 'y': {}, 'z': {}, '_other': {}}

    for token in dictionary.keys():
        for file_name in dictionary[token].keys():
            dictionary[token][file_name] = dictionary[token][file_name] / document_len_map[file_name] * 1.0
        if token == '':
            token_dict_tmp['_other'][token] = dictionary[token]
        elif token[0] in token_dict_tmp.keys():
            token_dict_tmp[token[0]][token] = dictionary[token]
        else:
            token_dict_tmp['_other'][token] = dictionary[token]

    for key in token_dict_tmp.keys():
        token_dict_tmp[key] = sort_dictionary(token_dict_tmp[key])
        file1 = open('./' + data + '/index_file/' + folder + '/index_' + key + '_' + str(block_num) + '.json', 'w')
        json.dump(token_dict_tmp[key], file1)
        file1.close()
        print(folder,'index_' + key + '_' + str(block_num), 'succeed')

    return document_len_map, block_num, total_file_num

def calculate_features(data, folder):
    if (not (os.path.exists('./' + data + '/features/' + folder))):
        os.mkdir('./' + data + '/features/' + folder)

    file1 = open('./' + data + '/document_len_map/document_len_map_' + folder + '.json', 'r')
    docno_dict = json.load(file1)
    file1.close()

    file2 = open('./' + data + '/document_total/document_total_' + folder + '.txt', 'r')
    lines = file2.readlines()
    file2.close()
    total_file_num = int(lines[0].strip('\n')[17:])
    total_file_len = int(lines[1].strip('\n')[17:])
    avg_file_len = total_file_len / total_file_num * 1.0

    file6 = open('./' + data + '/query/' + folder + '.title')
    tmp1 = file6.read()
    file6.close()
    query_list = re.split(' ', tmp1.strip('\n'))

    file7 = open('./' + data + '/query/' + folder + '.pids')
    tmp2 = file7.readlines()
    file7.close()
    doc_list = [pid.strip('\n') for pid in tmp2]

    k = 1.5
    b = 0.75
    file3 = open('./' + data + '/features/' + folder + '/TF-IDF.res', 'w')
    file4 = open('./' + data + '/features/' + folder + '/BM25.res', 'w')
    file5 = open('./' + data + '/features/' + folder + '/VSM.res', 'w')

    query_tf = {}
    score_tf_idf = {}
    score_bm25 = {}
    score_VSM = {}
    doc_w = {}
    for doc in doc_list:
        score_tf_idf[doc] = 0.0
        score_bm25[doc] = 0.0
        score_VSM[doc] = 0.0
        doc_w[doc] = {}

    for i in range(len(query_list)):
        if query_list[i] not in query_tf:
            query_tf[query_list[i]] = 1
        else:
            query_tf[query_list[i]] += 1

        token_dict = query_index(query_list[i], data, folder)
        if token_dict == -1:
            continue

        idf_t = math.log(total_file_num / len(token_dict) * 1.0)
        idf_qi = math.log((total_file_num - len(token_dict) + 0.5) / (len(token_dict) + 0.5) * 1.0)

        for docno in token_dict.keys():
            if docno in doc_list:
                score_tf_idf[docno] += token_dict[docno] * idf_t
                score_bm25[docno] += idf_qi * (token_dict[docno] * (k + 1) / (
                        token_dict[docno] + k * (1 - b + b * docno_dict[docno] / avg_file_len * 1.0)) * 1.0)
                doc_w[docno][query_list[i]] = token_dict[docno]

    query_vector = []
    for i in range(len(query_list)):
        query_vector.append(query_tf[query_list[i]] / len(query_list) * 1.0)

    for docno in doc_w.keys():
        doc_vector = []
        if_0 = 0
        for i in range(len(query_list)):
            if query_list[i] in doc_w[docno]:
                if_0 = 1
                doc_vector.append(doc_w[docno][query_list[i]])
            else:
                doc_vector.append(0)
        if if_0 == 0:
            score_VSM[docno] = 0.0
        else:
            score_VSM[docno] = conine_score(query_vector, doc_vector)

    sort_score_tf_idf = sorted(score_tf_idf.items(), key=lambda x: x[1], reverse=True)
    sort_score_bm25 = sorted(score_bm25.items(), key=lambda x: x[1], reverse=True)
    sort_score_VSM = sorted(score_VSM.items(), key=lambda x: x[1], reverse=True)

    rank = 1
    for item in sort_score_tf_idf:
        print('TF-IDF ' + item[0] + ' ' + str(rank) + ' ' + str(item[1]))
        file3.write(item[0] + ' ' + str(rank) + ' ' + str(item[1]) + '\n')
        rank += 1

    rank = 1
    for item in sort_score_bm25:
        print('BM25 ' + item[0] + ' ' + str(rank) + ' ' + str(item[1]))
        file4.write(item[0] + ' ' + str(rank) + ' ' + str(item[1]) + '\n')
        rank += 1

    rank = 1
    for item in sort_score_VSM:
        print('VSM ' + item[0] + ' ' + str(rank) + ' ' + str(item[1]))
        file5.write(item[0] + ' ' + str(rank) + ' ' + str(item[1]) + '\n')
        rank += 1

    file3.close()
    file4.close()
    file5.close()

    print(folder, 'calculate features succeed')

def query_index(token, data, folder):
    if token[0] >= 'a' and token[0] <= 'z':
        path = './' + data + '/index_file/' + folder + '/index_' + token[0] + '.json'
    else:
        path = './' + data + '/index_file/' + folder + '/index__other.json'
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

def combine_features(data, folder):
    file1 = open('./' + data + '/features/' + folder + '/TF-IDF.res', 'r')
    tmp1 = file1.readlines()
    file1.close()
    file2 = open('./' + data + '/features/' + folder + '/BM25.res', 'r')
    tmp2 = file2.readlines()
    file2.close()
    file3 = open('./' + data + '/features/' + folder + '/VSM.res', 'r')
    tmp3 = file3.readlines()
    file3.close()

    features_dict = {}
    for i in range(len(tmp1)):
        tmp1_list = re.split(' ', tmp1[i].strip('\n'))
        tmp2_list = re.split(' ', tmp2[i].strip('\n'))
        tmp3_list = re.split(' ', tmp3[i].strip('\n'))
        if tmp1_list[0] not in features_dict.keys():
            features_dict[tmp1_list[0]] = [tmp1_list[1], tmp1_list[2], 0, 0, 0, 0]
        else:
            features_dict[tmp1_list[0]][0] = tmp1_list[1]
            features_dict[tmp1_list[0]][1] = tmp1_list[2]
        if tmp2_list[0] not in features_dict.keys():
            features_dict[tmp2_list[0]] = [0, 0, tmp2_list[1], tmp2_list[2], 0, 0]
        else:
            features_dict[tmp2_list[0]][2] = tmp2_list[1]
            features_dict[tmp2_list[0]][3] = tmp2_list[2]
        if tmp3_list[0] not in features_dict.keys():
            features_dict[tmp3_list[0]] = [0, 0, 0, 0, tmp3_list[1], tmp3_list[2]]
        else:
            features_dict[tmp3_list[0]][4] = tmp3_list[1]
            features_dict[tmp3_list[0]][5] = tmp3_list[2]

    file4 = open('./' + data + '/total_features/' + folder, 'w')
    for key in features_dict.keys():
        file4.write(key + ' ' + features_dict[key][0] + ' ' + features_dict[key][1] + ' ' + features_dict[key][2]
            + ' ' + features_dict[key][3] + ' ' + features_dict[key][4] + ' ' + features_dict[key][5] + '\n')
    file4.close()
    print(folder, 'features combine succeed')

def get_label(data):
    file1 = open('../2017TAR/' + data + '/qrels/qrel_abs_train', 'r')
    lines = file1.readlines()
    label_dict = {}
    for line in lines:
        tmp1 = line.strip('\n').strip(' ')
        tmp2 = re.split('[ ]+', tmp1)
        if tmp2[0] not in label_dict.keys():
            label_dict[tmp2[0]] = {}
        label_dict[tmp2[0]][tmp2[2]] = tmp2[3]

    for topic in label_dict.keys():
        file3 = open('./' + data + '/total_features/' + topic, 'r')
        lines = file3.readlines()
        file3.close()
        file2 = open('./' + data + '/labels/' + topic, 'w')
        for line in lines:
            tmp3 = re.split(' ', line.strip('\n'))
            file2.write(tmp3[0] + ' ' + label_dict[topic][tmp3[0]] + '\n')
        file2.close()
        print(topic, 'get label succeed')

def logistic(data, folder_list):
    dataX = []
    dataY = []

    for folder in folder_list:
        file1 = open('./' + data + '/total_features/' + folder, 'r')
        TrainLines = file1.readlines()
        file1.close()
        for line in TrainLines:
            tmp1 = re.split(' ', line.strip('\n'))
            tmp1 = tmp1[1:]
            tmp2 = [float(elem) for elem in tmp1]
            dataX.append(tmp2)

        file2 = open('./' + data + '/labels/' + folder, 'r')
        lines = file2.readlines()
        file2.close()
        for line in lines:
            tmp3 = re.split(' ', line.strip('\n'))
            dataY.append(float(tmp3[1]))

    alpha = 0.0001
    count = 2000
    loss_function = 0
    data_num = len(dataX)
    x_length = len(dataX[0])

    max_data = []
    min_data = []
    for i in range(x_length):
        max_data.append(max([line[i] for line in dataX]))
        min_data.append(min([line[i] for line in dataX]))

    for line in dataX:
        for i in range(x_length):
            line[i] = line[i] / (max_data[i] - min_data[i]) * 1.0

    theta = [1 for i in range(x_length)]

    print('train data process succeed, start calculate theta')

    while True:
        for i in range(data_num):
            thetaTx = 0
            for j in range(x_length):
                thetaTx += theta[j] * dataX[i][j]
            h_theta = 1. / (1 + math.exp(-thetaTx))
            for j in range(x_length):
                theta[j] += alpha * (dataY[i] - h_theta) * dataX[i][j]

        for i in range(data_num):
            thetaTx = 0
            for j in range(x_length):
                thetaTx += theta[j] * dataX[i][j]
            h_theta = 1. / (1 + math.exp(-thetaTx))
            if h_theta < 1:
                loss_function += dataY[i] * math.log(abs(h_theta)) + (1 - dataY[i]) * math.log(abs(1 - h_theta))
        loss_function = - loss_function / data_num * 1.0

        count -= 1
        print('count =', count)
        if count == 0:
            break

    print(theta)
    file3 = open('./' + data + '/theta.predict', 'w')
    for i in range(x_length):
        if i != x_length - 1:
            file3.write(str(theta[i]) + ' ')
        else:
            file3.write(str(theta[i]) + '\n')
    file3.close()
    print('logistic regressor succeed')

def prediction(train, test, folder):
    pids = []
    testX = []
    testY = []
    file1 = open('./' + test + '/total_features/' + folder, 'r')
    TestLines = file1.readlines()
    file1.close()
    for line in TestLines:
        tmp1 = re.split(' ', line.strip('\n'))
        pids.append(tmp1[0])
        tmp1 = tmp1[1:]
        tmp2 = [float(elem) for elem in tmp1]
        testX.append(tmp2)

    test_num = len(testX)
    x_length = len(testX[0])

    max_testdata = []
    min_testdata = []
    for i in range(x_length):
        max_testdata.append(max([line[i] for line in testX]))
        min_testdata.append(min([line[i] for line in testX]))

    for line in testX:
        for i in range(x_length):
            line[i] = line[i] / (max_testdata[i] - min_testdata[i]) * 1.0

    file2 = open('./' + train + '/theta.predict', 'r')
    tmp3 = file2.read()
    file2.close()
    tmp4 = re.split(' ', tmp3.strip('\n'))
    theta = [float(elem) for elem in tmp4]

    for i in range(test_num):
        thetaTx = 0
        for j in range(x_length):
            thetaTx += theta[j] * testX[i][j]
        h_theta = 1. / (1 + math.exp(-thetaTx))
        testY.append(h_theta)

    predict_tuples = []
    for i in range(test_num):
        predict_tuples.append((folder, pids[i], testY[i]))
    sort_predict_tuples = sorted(predict_tuples, key=lambda x: x[2], reverse=True)

    file3 = open('./' + test + '/10152130122_钱庭涵_point-wise.res', 'a')
    rank = 1
    for i in range(test_num):
        print(sort_predict_tuples[i][0], '0', sort_predict_tuples[i][1], str(rank), str(sort_predict_tuples[i][2]),
              '10152130122_point-wise')
        file3.write(sort_predict_tuples[i][0] + ' 0 ' + sort_predict_tuples[i][1] + ' ' + str(rank) + ' ' + str(
            sort_predict_tuples[i][2]) + ' 10152130122_point-wise\n')
        rank += 1
    file3.close()
    print(folder, 'prediction succeed')

if __name__ == '__main__':
    # 创建训练集所需文件夹
    create_necessary_folders('training')

    # 训练集预处理
    preprocess_query('training')
    preprocess_document('training')

    # 训练集建立索引
    for a in os.walk('./training/document'):
        train_folder_list = a[1]
        break

    for folder in train_folder_list:
        document_index_create('training', folder)

    # 训练集计算特征
    for folder in train_folder_list:
        calculate_features('training', folder)

    # 训练集合并特征
    for folder in train_folder_list:
        combine_features('training', folder)

    # 训练集获得01标签
    get_label('training')

    # 训练集逻辑回归
    logistic('training', train_folder_list)

    # 创建测试集所需文件夹
    create_necessary_folders('testing')

    # 测试集预处理
    preprocess_query('testing')
    preprocess_document('testing')

    # 测试集建立索引
    for a in os.walk('./testing/document'):
        test_folder_list = a[1]
        break

    for folder in test_folder_list:
        document_index_create('testing', folder)

    # 测试集计算特征
    for folder in test_folder_list:
        calculate_features('testing', folder)

    # 测试集合并特征
    for folder in test_folder_list:
        combine_features('testing', folder)

    # 测试集预测
    for folder in test_folder_list:
        prediction('training', 'testing', folder)
