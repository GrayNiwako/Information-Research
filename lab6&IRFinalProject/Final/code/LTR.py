# -*- coding: utf8 -*-
import os
import re
import json
import math
from sklearn.svm import SVC

def create_necessary_folders(data):
    if (not (os.path.exists('./' + data + '/rank_features'))):
        os.mkdir('./' + data + '/rank_features')

def ranking_query(method, folder):
    file1 = open('./testing/features/' + folder + '/' + method + '.res', 'r')
    tmp1 = file1.readlines()
    file1.close()

    file2 = open('./testing/10152130122_钱庭涵_' + method + '.res', 'a')
    for i in range(len(tmp1)):
        tmp1_list = re.split(' ', tmp1[i].strip('\n'))
        print(folder, '0', tmp1_list[0], tmp1_list[1], tmp1_list[2], '10152130122_' + method)
        file2.write(folder + ' 0 ' + tmp1_list[0] + ' ' + tmp1_list[1] + ' ' + tmp1_list[2]
                    + ' 10152130122_' + method + '\n')
    file2.close()
    print(folder, method, 'succeed')

def get_rank_features(data, folder):
    file1 = open('./' + data + '/total_features/' + folder, 'r')
    tmp1 = file1.readlines()
    file1.close()

    file2 = open('./' + data + '/rank_features/' + folder, 'w')
    for i in range(len(tmp1)):
        tmp1_list = re.split(' ', tmp1[i].strip('\n'))
        print(tmp1_list[0], tmp1_list[1], tmp1_list[3], tmp1_list[5])
        file2.write(tmp1_list[0] + ' ' + tmp1_list[1] + ' ' + tmp1_list[3] + ' ' + tmp1_list[5] + '\n')
    file2.close()

def logistic(data, folder_list):
    dataX = []
    dataY = []

    for folder in folder_list:
        file1 = open('./' + data + '/rank_features/' + folder, 'r')
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

def prediction(train, test, folder, method):
    pids = []
    testX = []
    testY = []
    file1 = open('./' + test + '/rank_features/' + folder, 'r')
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

    file3 = open('./' + test + '/10152130122_钱庭涵_' + method + '.res', 'a')
    rank = 1
    for i in range(test_num):
        print(sort_predict_tuples[i][0], '0', sort_predict_tuples[i][1], str(rank), str(sort_predict_tuples[i][2]),
              '10152130122_' + method)
        file3.write(sort_predict_tuples[i][0] + ' 0 ' + sort_predict_tuples[i][1] + ' ' + str(rank) + ' ' + str(
            sort_predict_tuples[i][2]) + ' 10152130122_' + method + '\n')
        rank += 1
    file3.close()
    print(folder, 'prediction succeed')

def svm_prediction(train, test, folder_list1, folder_list2, method):
    dataX = []
    dataY = []

    for folder in folder_list1:
        file1 = open('./' + train + '/rank_features/' + folder, 'r')
        TrainLines = file1.readlines()
        file1.close()
        for line in TrainLines:
            tmp1 = re.split(' ', line.strip('\n'))
            tmp1 = tmp1[1:]
            tmp2 = [float(elem) for elem in tmp1]
            dataX.append(tmp2)

        file2 = open('./' + train + '/labels/' + folder, 'r')
        lines = file2.readlines()
        file2.close()
        for line in lines:
            tmp3 = re.split(' ', line.strip('\n'))
            dataY.append(float(tmp3[1]))

    data_x_length = len(dataX[0])

    max_data = []
    min_data = []
    for i in range(data_x_length):
        max_data.append(max([line[i] for line in dataX]))
        min_data.append(min([line[i] for line in dataX]))

    for line in dataX:
        for i in range(data_x_length):
            line[i] = line[i] / (max_data[i] - min_data[i]) * 1.0

    print('train data process succeed, start create model')

    clf = SVC(C=1.0, kernel='linear', probability=True)
    clf.fit(dataX, dataY)
    print('create model succeed')

    file4 = open('./' + test + '/10152130122_钱庭涵_' + method + '.res', 'w')
    for folder in folder_list2:
        pids = []
        testX = []
        file3 = open('./' + test + '/rank_features/' + folder, 'r')
        TestLines = file3.readlines()
        file3.close()
        for line in TestLines:
            tmp4 = re.split(' ', line.strip('\n'))
            pids.append(tmp4[0])
            tmp4 = tmp4[1:]
            tmp5 = [float(elem) for elem in tmp4]
            testX.append(tmp5)

        test_num = len(testX)
        test_x_length = len(testX[0])

        max_testdata = []
        min_testdata = []
        for i in range(test_x_length):
            max_testdata.append(max([line[i] for line in testX]))
            min_testdata.append(min([line[i] for line in testX]))

        for line in testX:
            for i in range(test_x_length):
                line[i] = line[i] / (max_testdata[i] - min_testdata[i]) * 1.0

        label_rate = clf.predict_proba(testX)

        predict_tuples = []
        for i in range(test_num):
            predict_tuples.append((folder, pids[i], label_rate[i][1]))
        sort_predict_tuples = sorted(predict_tuples, key=lambda x: x[2], reverse=True)

        rank = 1
        for i in range(test_num):
            print(sort_predict_tuples[i][0], '0', sort_predict_tuples[i][1], str(rank), str(sort_predict_tuples[i][2]),
                  '10152130122_' + method)
            file4.write(sort_predict_tuples[i][0] + ' 0 ' + sort_predict_tuples[i][1] + ' ' + str(rank) + ' ' + str(
                sort_predict_tuples[i][2]) + ' 10152130122_' + method + '\n')
            rank += 1
        print(folder, 'prediction succeed')

    file4.close()

if __name__ == '__main__':
    # 创建训练集和测试集所需文件夹
    create_necessary_folders('training')
    create_necessary_folders('testing')

    for a in os.walk('./training/document'):
        train_folder_list = a[1]
        break

    for a in os.walk('./testing/document'):
        test_folder_list = a[1]
        break

    # 单用TF-IDF BM25 VSM得到的结果
    for folder in test_folder_list:
        for method in ['TF-IDF', 'BM25', 'VSM']:
            ranking_query(method, folder)

    # 使用TF-IDF_RANK BM25_RANK VSM_RANK 3个特征进行训练
    # 训练集和测试集获取3个排名特征
    for folder in train_folder_list:
        get_rank_features('training', folder)
    for folder in test_folder_list:
        get_rank_features('testing', folder)

    # 训练集逻辑回归
    logistic('training', train_folder_list)

    # 测试集预测
    for folder in test_folder_list:
        prediction('training', 'testing', folder, 'rank3')

    # pair-wise, 使用sklearn中的svm算法
    svm_prediction('training', 'testing', train_folder_list, test_folder_list, 'sklearn-SVM')

