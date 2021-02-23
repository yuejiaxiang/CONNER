# -*- coding: UTF-8 -*-
# @Time    : 2021/1/25
# @Author  : xiangyuejia@qq.com
# Apache License
# Copyright©2020-2021 xiangyuejia@qq.com All Rights Reserved
import json
import os
import math
import pandas as pd
import numpy as np
from data_process.change_data_format_unit import excel2tsv_unit, save_data, clean_pre_tsv_format


def isnan(thing):
    if type(thing) != float:
        return False
    return math.isnan(thing)


def get_b(text, item, slice_idx, token):
    token = token.replace('10.0', '10')
    token = token.replace('11.0', '11')
    token = token.replace('12.0', '12')
    token = token.replace('13.0', '13')
    token = token.replace('14.0', '14')
    token = token.replace('15.0', '15')
    token = token.replace('16.0', '16')
    token = token.replace('17.0', '17')
    token = token.replace('18.0', '18')
    token = token.replace('19.0', '19')
    token = token.replace('1.0', '1')
    token = token.replace('2.0', '2')
    token = token.replace('3.0', '3')
    token = token.replace('4.0', '4')
    token = token.replace('5.0', '5')
    token = token.replace('6.0', '6')
    token = token.replace('7.0', '7')
    token = token.replace('8.0', '8')
    token = token.replace('9.0', '9')
    token = token.replace('0.0', '0')
    t1 = 0
    t2 = 1
    try:
        if len(token) > 0:
            if '-' in token:
                x = str(token).split('-')
            else:
                x = str(token).split('$')
            t1 = int(x[0])
            if len(x) > 1:
                t2 = int(x[1])
    except Exception as e:
        return -1

    if t1 >= len(slice_idx):
        return -1
    end = slice_idx[t1]
    for i in range(t2):
        b = text.find(item, end)
        end = b + len(item)
    return b


def excel2tsv(data, out_path):
    ann_id = 0
    token_id = 0
    para_id_old = '-1'
    anno_set = {}
    rel = {}
    um = {}
    for excel_line, d in enumerate(data):
        if not isnan(d[0]):
            para_id = d[0] if not isnan(d[0]) else ''
            sent_idx = json.loads(d[1]) if not isnan(d[1]) else ''
            sent_text = str(d[2]) if not isnan(d[2]) else ''
            slice_idx = json.loads(d[3]) if not isnan(d[3]) else ''
        quantity = str(d[5]) if not isnan(d[5]) else ''
        quantity_line = str(d[6]).strip() if not isnan(d[6]) else ''
        unit = str(d[7]).strip() if not isnan(d[7]) else ''
        mod = str(d[8]).strip().split(' ') if not isnan(d[8]) else ['']
        property = str(d[9]) if not isnan(d[9]) else ''
        property_line = str(d[10]).strip() if not isnan(d[10]) else ''
        entity = str(d[11]) if not isnan(d[11]) else ''
        entity_line = str(d[12]).strip() if not isnan(d[12]) else ''
        quantity_Tid = ''
        property_Tid = ''

        for mo in mod:
            if mo not in ['', 'IsApproximate', 'IsCount', 'IsRange', 'IsList', 'IsMean', 'IsMedian', 'IsMeanHasSD', 'HasTolerance', 'IsRangeHasTolerance']:
                print('illegal mod {} - {}'.format(excel_line + 2, mo))

        if para_id:
            if para_id != para_id_old:
                if len(anno_set) > 0:
                    tsv = excel2tsv_unit(anno_set, rel, um, para_id_old)
                    out_put_file = os.path.join(out_path, para_id_old + '.tsv')
                    save_data(tsv, out_put_file)
                ann_id = 0
                token_id = 0
                anno_set = {}
                rel = {}
                um = {}
                para_id_old = para_id

        anno_set[ann_id] = []

        if quantity:
            b = get_b(sent_text, quantity, slice_idx, quantity_line)
            e = b + len(quantity)
            if sent_text[b:e] != quantity:
                print('not match {} - {}'.format(excel_line+2, 'quantity'))
            token_name = 'T' + str(ann_id) + '-' + str(token_id)
            quantity_Tid = token_name
            token_id += 1
            um[token_name] = {'Unit': unit, 'modifier': mod}
            anno_set[ann_id].append([b+sent_idx[0], e+sent_idx[0], ann_id, token_name, 'Quantity', quantity])

        if property:
            b = get_b(sent_text, property, slice_idx, property_line)
            e = b + len(property)
            if sent_text[b:e] != property:
                print('not match {} - {}'.format(excel_line+2, 'property'))
            token_name = 'T' + str(ann_id) + '-' + str(token_id)
            property_Tid = token_name
            token_id += 1
            anno_set[ann_id].append([b+sent_idx[0], e+sent_idx[0], ann_id, token_name, 'MeasuredProperty', property])
            rel[token_name] = ['HasQuantity', quantity_Tid]

        if entity:
            b = get_b(sent_text, entity, slice_idx, entity_line)
            e = b + len(entity)
            if sent_text[b:e] != entity:
                print('not match {} - {}'.format(excel_line+2, 'entity'))
            token_name = 'T' + str(ann_id) + '-' + str(token_id)
            token_id += 1
            anno_set[ann_id].append([b+sent_idx[0], e+sent_idx[0], ann_id, token_name, 'MeasuredEntity', entity])
            if property_Tid:
                rel[token_name] = ['HasProperty', property_Tid]
            else:
                rel[token_name] = ['HasQuantity', quantity_Tid]

        ann_id += 1
    if len(anno_set) > 0:
        tsv = excel2tsv_unit(anno_set, rel, um, para_id)
        out_put_file = os.path.join(out_path, para_id_old + '.tsv')
        save_data(tsv, out_put_file)
    return


def generate_tsv(file, out_path):
    clean_pre_tsv_format(path=out_path)
    sheet = pd.read_excel(file, header=None, skiprows=1)
    data = np.array(sheet).tolist()
    excel2tsv(data, out_path)


if __name__ == '__main__':
    # generate_tsv('human/test_anno1_20210126.xlsx', '../MeasEval/data/human_eval_anno1')
    # generate_tsv('human/test_anno2.xlsx', '../MeasEval/data/human_eval_anno2')
    # generate_tsv('human/test_anno3.xlsx', '../MeasEval/data/human_eval_anno3')
    generate_tsv('data_enhancement/NER_union_roberta_quantity_with_roberta_joint_ERE_isoQ_MOD1.xlsx',
                 '../ner_process/pre_tsv_format')
