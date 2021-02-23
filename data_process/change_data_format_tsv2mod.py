# -*- coding: UTF-8 -*-
# @Time    : 2021/1/27
# @Author  : xiangyuejia@qq.com
# Apache License
# Copyright©2020-2021 xiangyuejia@qq.com All Rights Reserved
import json
import csv
from data_process.change_data_format_unit import text2list, read_semeval_list, split_data, choose_key, get_mod_data, split_train_test, clean_pre_tsv_format

method_text, expend, method_label, rate_train_eval = [0, 0, 0, 0.8]
# method_text, expend, method_label, rate_train_eval = [1, 10, 0, 0.8]
# method_text, expend, method_label, rate_train_eval = [2, 5, 0, 0.8]
# method_text, expend, method_label, rate_train_eval = [2, 2, 0, 0.8]

mode = 'all' # 'all' or 'part', all will put all data in train

pre_dir = '../mod_process/data/t' + str(method_text) + \
          '_e' + str(expend) + \
          '_l' + str(method_label) + \
          '_r' + str(rate_train_eval) + \
          '_' + mode + '/'

path_text = [
    '../MeasEval/data/train/text',
    '../MeasEval/data/trial/txt'
]  # 输入数据的位置
path_tsv = [
    '../MeasEval/data/train/tsv',
    '../MeasEval/data/trial/tsv'
]  # train的输入数据的位置
out_file_all = pre_dir + 'all_tsv'
out_file_train = pre_dir + 'train.tsv'
out_file_test = pre_dir + 'dev.tsv'
clean_pre_tsv_format(path=pre_dir)
# 读入原始数据
whole_ann = read_semeval_list(path_tsv, path_text)
all_ner_data = get_mod_data(whole_ann, method_text=method_text, expend=expend, method_label=method_label)

# 为'dict' format 输出train数据
train_ner_data, test_ner_data = split_train_test(all_ner_data, rate_train_eval, mode=mode)
with open(out_file_all, 'w', encoding='utf8') as fout:
    tsv_w = csv.writer(fout, delimiter='\t')
    tsv_w.writerows([['text', 'label']] + all_ner_data)  # 单行写入
with open(out_file_train, 'w', encoding='utf8') as fout:
    tsv_w = csv.writer(fout, delimiter='\t')
    tsv_w.writerows([['text', 'label']] + train_ner_data)  # 单行写入
with open(out_file_test, 'w', encoding='utf8') as fout:
    tsv_w = csv.writer(fout, delimiter='\t')
    tsv_w.writerows([['text', 'label']] + test_ner_data)  # 单行写入
