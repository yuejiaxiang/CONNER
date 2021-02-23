# -*- coding: UTF-8 -*-
# @Time    : 2021/1/19
# @Author  : xiangyuejia@qq.com
# Apache License
# Copyright©2020-2021 xiangyuejia@qq.com All Rights Reserved

import os
import json
import pandas as pd

path_text = [
    '../MeasEval/data/train/text',
    '../MeasEval/data/trial/txt'
]  # 输入数据的位置
path_tsv = [
    '../MeasEval/data/train/tsv',
    '../MeasEval/data/trial/tsv'
]  # train的输入数据的位置



formats = []
span_all = []
all_q = dict()
all_p = dict()
all_e = dict()
all_u = dict()
all_Qualifier = dict()
p_set = set()
count_q = 0
count_p = 0
count_e = 0
count_u = 0
count_Qualifier = 0
count_mods = {}
case_mods = {}

for path_text, path_tsv in zip(path_text, path_tsv):
    files = os.listdir(path_tsv)
    for file in files:
        full_file = os.path.join(path_tsv, file)
        core, _ = os.path.splitext(file)
        text_p = os.path.join(path_text, core + '.txt')
        with open(text_p, 'r', encoding='utf8') as fin:
            text_all = fin.readlines()
            if len(text_all) > 1:
                print('len(text) > 1: ', text_p)
            input_text = text_all[0].strip()
        data = pd.read_csv(full_file, sep='\t', header=0)

        for index, row in data.iterrows():
            annotSet = int(row['annotSet'])
            annotType = row['annotType']
            startOffset = int(row['startOffset'])
            endOffset = int(row['endOffset'])
            annotId = row['annotId']
            text = row['text']
            if pd.isnull(row['other']):
                other = {}
            else:
                other = json.loads(row['other'])

            if 'mods' in other:
                for mod in other['mods']:
                    if mod not in count_mods:
                        count_mods[mod] = {}
                        case_mods[mod] = {}
                    if text not in count_mods[mod]:
                        count_mods[mod][text] = 0
                        case_mods[mod][text] = []
                    count_mods[mod][text] += 1
                    case_mods[mod][text].append(input_text[startOffset-20: endOffset+20])

            if 'unit' in other:
                count_u += 1
                if other['unit'] not in all_u:
                    all_u[other['unit']] = 0
                all_u[other['unit']] += 1

            if annotType == 'Quantity':
                count_q += 1
                if text not in all_q:
                    all_q[text] = 0
                all_q[text] += 1
            if annotType == 'Qualifier':
                count_Qualifier += 1
                if text not in all_Qualifier:
                    all_Qualifier[text] = 0
                all_Qualifier[text] += 1
            if annotType == 'MeasuredProperty':
                count_p += 1
                if text not in all_p:
                    all_p[text] = 0
                all_p[text] += 1
            if annotType == 'MeasuredEntity':
                count_e += 1
                if text not in all_e:
                    all_e[text] = 0
                all_e[text] += 1

print('q {} {}'.format(len(all_q), count_q))
print('p {} {}'.format(len(all_p), count_p))
print('e {} {}'.format(len(all_e), count_e))
print('u {} {}'.format(len(all_u), count_u))
print('Qualifier {} {}'.format(len(all_Qualifier), count_Qualifier))
with open('statistic/all_q.txt', 'w', encoding='utf8') as fout:
    data = sorted([[k, v] for k, v in all_q.items()], key=lambda x: [-x[1], x[0]])
    for d in data:
        print(d[0], file=fout)
with open('statistic/all_p.txt', 'w', encoding='utf8') as fout:
    data = sorted([[k, v] for k, v in all_p.items()], key=lambda x: [-x[1], x[0]])
    for d in data:
        print(d[0], file=fout)
with open('statistic/all_e.txt', 'w', encoding='utf8') as fout:
    data = sorted([[k, v] for k, v in all_e.items()], key=lambda x: [-x[1], x[0]])
    for d in data:
        print(d[0], file=fout)
with open('statistic/all_u.txt', 'w', encoding='utf8') as fout:
    data = sorted([[k, v] for k, v in all_u.items()], key=lambda x: [-x[1], x[0]])
    for d in data:
        print(d[0], file=fout)
with open('statistic/all_Qualifier.txt', 'w', encoding='utf8') as fout:
    data = sorted([[k, v] for k, v in all_Qualifier.items()], key=lambda x: [-x[1], x[0]])
    for d in data:
        print(d[0], file=fout)

for k, v in count_mods.items():
    with open('statistic/mod_' + k + '.txt', 'w', encoding='utf8') as fout:
        data = sorted([[k, v] for k, v in count_mods[k].items()], key=lambda x: [-x[1], x[0]])
        for d in data:
            print(d[0], file=fout)
            # print('{}'.format(case_mods[k][d[0]]), file=fout)



path_text = [
    '../MeasEval/data/train/text',
    '../MeasEval/data/trial/txt'
]  # 输入数据的位置
path_tsv = [
    '../MeasEval/data/train/tsv',
    '../MeasEval/data/trial/tsv'
]  # train的输入数据的位置
from data_process.change_data_format_unit import text2list, read_semeval_list, split_data, choose_key, cut_text
whole_ann = read_semeval_list(path_tsv, path_text)
whole_ann = split_data(whole_ann)
count_all= {}
for ann in whole_ann:
    for item in ann['excel']:
        for k in ann['excel'][item].keys():
            if k not in count_all:
                count_all[k] = 0
            count_all[k] += 1
print(count_all)
