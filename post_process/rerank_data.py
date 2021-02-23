# -*- coding: UTF-8 -*-
# @Time    : 2021/2/1
# @Author  : xiangyuejia@qq.com
# Apache License
# Copyright©2020-2021 xiangyuejia@qq.com All Rights Reserved
import pandas as pd
import numpy as np
import json

def formated(data):
    data_reranked = {}
    for d in data:
        data_reranked[d[2]] = d
    eid = data_reranked['Quantity'][3]
    return eid, data_reranked


def get_ori_data():
    infile = '../ner_process/pre_tsv_format_concat/union3.tsv'
    data = pd.read_csv(infile, sep='\t', header=0)
    all_datas = []
    doc_datas = {}
    tmp_datas = []
    doc_rank = []
    last_doc_id = ''
    for index, row in data.iterrows():
        docId = row['docId']
        annotSet = row['annotSet']
        annotType = row['annotType']
        startOffset = int(row['startOffset'])
        endOffset = int(row['endOffset'])
        annotId = row['annotId']
        text = row['text']
        if pd.isnull(row['other']):
            other = {}
        else:
            other = json.loads(row['other'])
        data = [docId, annotSet, annotType, startOffset,
                endOffset, annotId, text, other]

        if annotType == 'Quantity':
            if len(tmp_datas) != 0:
                eid, data_formated = formated(tmp_datas)
                doc_datas[(last_doc_id, eid)] = data_formated
                tmp_datas = []

        if docId not in doc_rank:
            if doc_datas != {}:
                all_datas.append(doc_datas)
                doc_datas = {}
        doc_rank.append(docId)

        tmp_datas.append(data)
        last_doc_id = docId

    if len(tmp_datas) != 0:
        eid, data_formated = formated(tmp_datas)
        doc_datas[(last_doc_id, eid)] = data_formated
    if doc_datas != {}:
        all_datas.append(doc_datas)
        doc_datas = {}
    return all_datas


def rerank_data(data):
    reranked_data = []

    for doc in data:
        id = 0
        k_rank = sorted(list(doc.keys()), key=lambda x: x[1])
        for k in k_rank:
            id += 1
            anno = doc[k]
            q = anno['Quantity']
            q[1] = id
            q[5] = 'T1-' + str(id)
            reranked_data.append(q)
            if 'MeasuredProperty' in anno and 'MeasuredEntity' not in anno:
                p = anno['MeasuredProperty']
                p[1] = id
                p[5] = 'T2-' + str(id)
                p[7]['HasQuantity'] = q[5]
                reranked_data.append(p)
            if 'MeasuredProperty' not in anno and 'MeasuredEntity' in anno:
                e = anno['MeasuredEntity']
                e[1] = id
                e[5] = 'T3-' + str(id)
                e[7]['HasQuantity'] = q[5]
                reranked_data.append(e)
            if 'MeasuredProperty' in anno and 'MeasuredEntity' in anno:
                p = anno['MeasuredProperty']
                p[1] = id
                p[5] = 'T2-' + str(id)
                p[7]['HasQuantity'] = q[5]
                reranked_data.append(p)
                e = anno['MeasuredEntity']
                e[1] = id
                e[5] = 'T3-' + str(id)
                e[7]['HasProperty'] = p[5]
                reranked_data.append(e)

    out_data = ['docId\tannotSet\tannotType\tstartOffset\tendOffset\tannotId\ttext\tother']
    for d in reranked_data:
        d[7] = json.dumps(d[7])
        d[1] = str(d[1])
        d[3] = str(d[3])
        d[4] = str(d[4])
        newline = [d[0], d[1], d[2], d[3], d[4], d[5], d[6], d[7]]
        out_data.append('\t'.join(newline))

    return out_data


import json
import math
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

def isnan(thing):
    if type(thing) != float:
        return False
    return math.isnan(thing)


def build_quantity_dictionary(total_df):
    quantity_dictionary = {}
    time = 0
    for excel_line, d in total_df.iterrows():
        if time == 0:
            time = 1
            continue
        if not isnan(d[0]):
            para_id = d[0] if not isnan(d[0]) else ''
            sent_idx = eval(d[1]) if not isnan(d[1]) else ''
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
        score = str(d[14]).strip() if not isnan(d[14]) else ''
        if score not in ['4']:
            continue
        quantity_Tid = ''
        property_Tid = ''
        begin_quantity_index = get_b(sent_text,quantity,slice_idx,quantity_line)+sent_idx[0]
        begin_property_index = get_b(sent_text,property,slice_idx,property_line)+sent_idx[0]
        begin_entity_index = get_b(sent_text,entity,slice_idx,entity_line)+sent_idx[0]
        quantity_key = tuple([para_id,quantity,begin_quantity_index])
        data_dict = {}
        data_dict['unit'] = unit
        data_dict['mod'] = mod
        data_dict['property'] = tuple([property,begin_property_index])
        data_dict['entity'] = tuple([entity,begin_entity_index])
        quantity_dictionary[quantity_key] = data_dict
    return quantity_dictionary


def update_human(data, human):
    hm = {}
    change = 0
    for k,v in human.items():
        hm[(k[0], k[2])] = k
    for pid, d in enumerate(data):
        for k,v in d.items():
            if k in hm:
                anno = human[hm[k]]
                if 'entity' in anno and 'MeasuredEntity' in d[k]:
                    if anno['entity'][0] != d[k]['MeasuredEntity'][6]:
                        print(pid, k, d[k]['MeasuredEntity'][6], '###', anno['entity'][0])
                        d[k]['MeasuredEntity'][6] = anno['entity'][0]
                        d[k]['MeasuredEntity'][3] = str(anno['entity'][1])
                        d[k]['MeasuredEntity'][4] = str(anno['entity'][1] + len(anno['entity'][0]))
                        change += 1
    print(change)
    return data




ori_data = get_ori_data()
# out_data = rerank_data(ori_data)

xlsx_file = 'anno_we.xlsx'
sheet = pd.read_excel(xlsx_file, header=None, skiprows=1)
data = np.array(sheet).tolist()
pd_data = pd.read_excel(xlsx_file, index_col=None, header=None)
human = build_quantity_dictionary(pd_data)

ori_data_new = update_human(ori_data, human)
out_data = rerank_data(ori_data_new)

with open('out_rerank.tsv', 'w', encoding='utf8') as fout:
    for d in out_data:
        print(d, file=fout)
