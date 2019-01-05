# -*- coding: utf8 -*- 
import os
import xml.etree.ElementTree as ET
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import re
import chardet
import gzip
import porter

def change_query_form(QueryLines):
    fp = open('./xml_form/topics.xml', 'w')
    fp.write('<query>\n\n')
    QueryLines = QueryLines.replace('<title>', '</num>\n\n<title>').replace('<desc>', '</title>\n\n<desc>')\
        .replace('<narr>', '</desc>\n\n<narr>').replace('</top>', '</narr>\n\n</top>')
    fp.write(QueryLines)
    fp.write('\n</query>\n\n')
    fp.close()

def change_document_form(DocumentLines, type):
    fp = open('./xml_form/' + type + '.xml', 'w')
    fp.write('<document>\n\n')
    strCodingFmt = chardet.detect(DocumentLines)['encoding']
    if strCodingFmt == 'ISO-8859-1':
        lines_tmp = DocumentLines.decode('utf-8', 'ignore')
    else:
        lines_tmp = DocumentLines.decode()
    if type[:2] == 'ZF':
        fp.write(lines_tmp.replace('&', '').replace('<ABSTRACT>', '\n').replace('</ABSTRACT>', '\n'))
    elif type[:2] == 'FR':
        lines_tmp1 = lines_tmp.replace('&', '').replace('<DOC>', '(Document_FR_DOC1)')\
            .replace('</DOC>', '(Document_FR_DOC2)').replace('<DOCNO>', '(Document_FR_DOCNO1)')\
            .replace('</DOCNO>', '(Document_FR_DOCNO2)').replace('<DOCID>', '(Document_FR_DOCID1)')\
            .replace('</DOCID>', '(Document_FR_DOCID2)').replace('<TEXT>', '(Document_FR_TEXT1)')\
            .replace('</TEXT>', '(Document_FR_TEXT2)')
        lines_tmp2 = re.sub(r'<.*>', ' ', lines_tmp1)
        lines_tmp3 = lines_tmp2.replace('(Document_FR_DOC1)', '<DOC>').replace('(Document_FR_DOC2)', '</DOC>')\
            .replace('(Document_FR_DOCNO1)', '<DOCNO>').replace('(Document_FR_DOCNO2)', '</DOCNO>')\
            .replace('(Document_FR_DOCID1)', '<DOCID>').replace('(Document_FR_DOCID2)', '</DOCID>')\
            .replace('(Document_FR_TEXT1)', '<TEXT>').replace('(Document_FR_TEXT2)', '</TEXT>')
        fp.write(lines_tmp3)
    else:
        fp.write(lines_tmp.replace('&', ''))
    fp.write('\n</document>\n\n')
    fp.close()

def pre_process(word_list):
    word_stem_list = []
    for sentence in word_list:
        tokens = nltk.word_tokenize(sentence.lower())
        lemmatizaer = WordNetLemmatizer()
        stem_list = [(porter.Stemmer()).stem(lemmatizaer.lemmatize(w)) for w in tokens \
                     if (w not in stopwords.words('english'))]
        tmp = re.split('[][():;/|.,*"+=> \\\?!^@_$#%{}-]+', ' '.join(stem_list))
        word_stem_list.append(' '.join(tmp))
    return word_stem_list

def query_process():
    root = ET.parse('./xml_form/topics.xml')
    num = []
    title = []
    desc = []
    narr = []
    for file in root.findall('top'):
        i = file.find('num').text
        num.append(i)
        temp = i.strip('\n').replace('Number:', '').strip(' ')
        query_num.append(temp)
        title.append(file.find('title').text)
        desc.append(file.find('desc').text)
        narr.append(file.find('narr').text)

    stem_num = pre_process(num)
    stem_title = pre_process(title)
    stem_desc = pre_process(desc)
    stem_narr = pre_process(narr)
    j = 0
    for file in root.findall('top'):
        elem = file.find('num')
        elem.text = stem_num[j]
        elem = file.find('title')
        elem.text = stem_title[j]
        elem = file.find('desc')
        elem.text = stem_desc[j]
        elem = file.find('narr')
        elem.text = stem_narr[j]
        j += 1
    root.write('./xml_form/topics.xml')

def query_depart():
    file = open('./xml_form/topics.xml', 'r')
    Lines = file.readlines()
    file.close()
    k = 0
    start = 0
    for line in Lines:
        temp1 = line.strip('\n')
        if temp1 == '<top>':
            start = 1
            file = open('./Answer/query/Topic_' + query_num[k] + '.xml', 'w')
        if start == 1:
            file.write(line)
        if temp1 == '</top>':
            file.close()
            print('Topic_' + query_num[k] + ' succeed')
            start = 0
            k += 1
    os.remove('./xml_form/topics.xml')

def document_process(type, title_list, remove_list):
    root = ET.parse('./xml_form/' + type + '.xml')
    DOCNO = []
    TEXT = []
    for file in root.findall('DOC'):
        i = file.find('DOCNO').text
        DOCNO.append(i)
        temp = i.strip('\n').strip(' ')
        title_list.append(temp)
        temp2 = [f.text for f in file.findall('TEXT')]
        if temp2 != [None]:
            TEXT.append('\n'.join(temp2))
        else:
            TEXT.append('\n')
        for remove_elem in remove_list:
            for k in file.findall(remove_elem):
                file.remove(k)

    stem_DOCNO = pre_process(DOCNO)
    stem_TEXT = pre_process(TEXT)
    j = 0
    for file in root.findall('DOC'):
        elem = file.find('DOCNO')
        elem.text = stem_DOCNO[j]
        i = 0
        for elem in file.findall('TEXT'):
            if stem_TEXT[j] == '':
                elem.text = ' '
                break
            if i != 0:
                file.remove(elem)
            else:
                elem.text = stem_TEXT[j]
                i = 1
        j += 1
    root.write('./xml_form/' + type + '.xml')

def document_depart(type, title_list, folder_name):
    file = open('./xml_form/' + type + '.xml', 'r')
    Lines = file.readlines()
    file.close()
    k = 0
    start = 0
    for line in Lines:
        temp1 = line.strip('\n')
        if temp1 == '<DOC>':
            start = 1
            file = open('./Answer/document/' + folder_name + '/' + title_list[k] + '.xml', 'w')
        if start == 1:
            file.write(line)
        if temp1 == '</DOC>':
            file.close()
            print(title_list[k] + ' succeed')
            start = 0
            k += 1
    os.remove('./xml_form/' + type + '.xml')

if (not (os.path.exists('./xml_form'))):
    os.mkdir('./xml_form')
if (not (os.path.exists('./Answer'))):
    os.mkdir('./Answer')
if (not (os.path.exists('./Answer/query'))):
    os.mkdir('./Answer/query')
if (not (os.path.exists('./Answer/document'))):
    os.mkdir('./Answer/document')
if (not (os.path.exists('./Answer/document/AP'))):
    os.mkdir('./Answer/document/AP')
if (not (os.path.exists('./Answer/document/DOE'))):
    os.mkdir('./Answer/document/DOE')
if (not (os.path.exists('./Answer/document/FR'))):
    os.mkdir('./Answer/document/FR')
if (not (os.path.exists('./Answer/document/WSJ'))):
    os.mkdir('./Answer/document/WSJ')
if (not (os.path.exists('./Answer/document/ZIFF'))):
    os.mkdir('./Answer/document/ZIFF')

file1 = open('./query&document/topics.151-200', 'r')
Query_Lines = file1.read()
file1.close()

change_query_form(Query_Lines)
query_num = []
query_process()

query_depart()

path = []
path.append('./query&document/disk12/disk1/AP')
path.append('./query&document/disk12/disk2/AP')
path.append('./query&document/disk12/disk1/DOE')
path.append('./query&document/disk12/disk1/WSJ')
path.append('./query&document/disk12/disk2/WSJ/1990')
path.append('./query&document/disk12/disk2/WSJ/1991')
path.append('./query&document/disk12/disk2/WSJ/1992')
path.append('./query&document/disk12/disk1/ZIFF')
path.append('./query&document/disk12/disk2/ZIFF')
path.append('./query&document/disk12/disk1/FR')
path.append('./query&document/disk12/disk2/FR')

elem_type = []
AP_remove_elem = ['FILEID', 'NOTE', 'UNK', 'FIRST', 'SECOND', 'HEAD', 'DATELINE', 'BYLINE']
elem_type.append(AP_remove_elem)
DOE_remove_elem = []
elem_type.append(DOE_remove_elem)
WSJ_remove_elem = ['AN', 'AUTHOR', 'CO', 'DATELINE', 'DOCID', 'DATE', 'LP', 'DD', 'DO', 'G',
                   'GV', 'HL', 'IN', 'SO', 'MS', 'ST', 'RE', 'NS']
elem_type.append(WSJ_remove_elem)
ZF_remove_elem = ['JOURNAL', 'TITLE', 'AUTHOR', 'SUMMARY', 'DESCRIPT', 'DOCID', 'PRODUCT',
                  'ADDRESS', 'COMPANY', 'CATEGORY', 'SPECS', 'NOTE']
elem_type.append(ZF_remove_elem)
FR_remove_elem = ['DOCID']
elem_type.append(FR_remove_elem)

for count in range(len(path)):
    for a in os.walk(path[count]):
        document_files = a[2]
        for document_file in document_files:
            if document_file != 'README.gz':
                file2 = gzip.GzipFile(path[count] + '/' + document_file, 'r')
                document_lines = file2.read()
                file2.close()
                document_file_name = document_file.replace('.gz', '')
                change_document_form(document_lines, document_file_name)
                if document_file[:2] == 'AP':
                    AP_title = []
                    document_process(document_file_name, AP_title, elem_type[0])
                    document_depart(document_file_name, AP_title, 'AP')
                if document_file[:3] == 'DOE':
                    DOE_title = []
                    document_process(document_file_name, DOE_title, elem_type[1])
                    document_depart(document_file_name, DOE_title, 'DOE')
                if document_file[:3] == 'WSJ':
                    WSJ_title = []
                    document_process(document_file_name, WSJ_title, elem_type[2])
                    document_depart(document_file_name, WSJ_title, 'WSJ')
                if document_file[:2] == 'ZF':
                    ZF_title = []
                    document_process(document_file_name, ZF_title, elem_type[3])
                    document_depart(document_file_name, ZF_title, 'ZIFF')
                if document_file[:2] == 'FR':
                    FR_title = []
                    document_process(document_file_name, FR_title, elem_type[4])
                    document_depart(document_file_name, FR_title, 'FR')

os.rmdir('./xml_form')
