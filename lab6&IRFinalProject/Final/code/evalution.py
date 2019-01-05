# -*- coding: utf8 -*-
import os
import math
import re

def eval_map(rele_dict, res_dict):
    map_list = []
    for topic in rele_dict.keys():
        map = 0
        count = 0
        for i in range(len(rele_dict[topic]['rele_list'])):
            pid = rele_dict[topic]['rele_list'][i]
            if pid in res_dict[topic].keys():
                count += 1
                map += count / res_dict[topic][pid]['rank'] * 1.0
        map = map / rele_dict[topic]['rele_num']
        map_list.append(map)

    avg = sum(map_list) / len(map_list) * 1.0
    return avg

def get_rank(rate):
    if rate < 0.2:
        return 1
    elif rate < 0.4:
        return 2
    elif rate < 0.6:
        return 3
    elif rate < 0.8:
        return 4
    else:
        return 5

def eval_ndcg(res_dict, p):
    NDCG_list = []
    for topic in res_dict.keys():
        DCG = 0
        IDCG = 0
        i = 1
        for pid in res_dict[topic]:
            rel = get_rank(res_dict[topic][pid]['rate'])
            if i <= p:
                DCG += (math.pow(2, rel) - 1) / math.log(1+i, 2) * 1.0
            IDCG += (math.pow(2, rel) - 1) / math.log(1 + i, 2) * 1.0
            i += 1
        NDCG = DCG / IDCG * 1.0
        NDCG_list.append(NDCG)

    avg = sum(NDCG_list) / len(NDCG_list) * 1.0
    return avg

if __name__ == '__main__':
    method = 'rank3'

    qrel_path = '../2017_test_qrels/qrel_abs_test.txt'
    res_path = './testing/10152130122_钱庭涵_' + method + '.res'

    file1 = open(qrel_path, 'r')
    lines = file1.readlines()
    file1.close()
    # file0 = open('./qrels_testing.res', 'w')
    rele_dict = {}
    for line in lines:
        tmp1 = line.strip('\n').strip(' ')
        tmp2 = re.split('[ ]+', tmp1)
        # file0.write(tmp2[0] + ' ' + tmp2[1] + ' ' + tmp2[2] + ' ' + tmp2[3] + '\n')
        if tmp2[0] not in rele_dict.keys():
            rele_dict[tmp2[0]] = {'rele_num': 0, 'rele_list': []}
        if int(tmp2[3]) == 1:
            rele_dict[tmp2[0]]['rele_num'] += 1
            rele_dict[tmp2[0]]['rele_list'].append(tmp2[2])
    # file0.close()
    print('qrel dictionary succeed')

    file2 = open(res_path, 'r')
    lines = file2.readlines()
    file2.close()
    res_dict = {}
    for line in lines:
        tmp1 = line.strip('\n')
        tmp2 = re.split(' ', tmp1)
        if tmp2[0] not in res_dict.keys():
            res_dict[tmp2[0]] = {}
        res_dict[tmp2[0]][tmp2[2]] = {'rank': int(tmp2[3]), 'rate': float(tmp2[4])}
    print('result dictionary succeed')

    file3 = open('./final/own_MAP_NDCG/MAP_NDCG_' + method + '.res', 'w')
    file3.write('result = ' + '10152130122_' + method + '\n')
    MAP = eval_map(rele_dict, res_dict)
    print('MAP =', MAP)
    file3.write('MAP = ' + str(MAP) + '\n')

    NDCG = eval_ndcg(res_dict, 10)
    print('NDCG@10 =', NDCG)
    file3.write('NDCG@10 = ' + str(NDCG) + '\n')

    NDCG = eval_ndcg(res_dict, 20)
    print('NDCG@20 =', NDCG)
    file3.write('NDCG@20 = ' + str(NDCG) + '\n')

    NDCG = eval_ndcg(res_dict, 50)
    print('NDCG@50 =', NDCG)
    file3.write('NDCG@50 = ' + str(NDCG) + '\n')

    NDCG = eval_ndcg(res_dict, 100)
    print('NDCG@100 =', NDCG)
    file3.write('NDCG@100 = ' + str(NDCG) + '\n')

    NDCG = eval_ndcg(res_dict, 200)
    print('NDCG@200 =', NDCG)
    file3.write('NDCG@200 = ' + str(NDCG) + '\n')

    file3.close()