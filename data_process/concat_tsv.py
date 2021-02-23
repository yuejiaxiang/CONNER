# -*- coding: UTF-8 -*-
# @Time    : 2021/1/18
# @Author  : xiangyuejia@qq.com
# Apache License
# Copyright©2020-2021 xiangyuejia@qq.com All Rights Reserved
import os

path_tsv = '/Users/apricot/semeval_task8/ner_process/pre_tsv_format'
output = '/Users/apricot/semeval_task8/ner_process/pre_tsv_format_concat/pre_all.tsv'
# path_tsv = '/Users/apricot/semeval_task8/MeasEval/data/human_eval_anno3'
# output = '/Users/apricot/semeval_task8/MeasEval/data/human_eval_concat/anno3.tsv'

all_data = ['docId	annotSet	annotType	startOffset	endOffset	annotId	text	other']
files = os.listdir(path_tsv)
for file in files:
    if '.tsv' not in file:
        continue
    full_file = os.path.join(path_tsv, file)
    with open(full_file, 'r', encoding='utf8') as fin:
        data = [l.strip() for l in fin.readlines()]
    all_data += data[1:]

with open(output, 'w', encoding='utf8') as fout:
    for d in all_data:
        print(d, file=fout)
