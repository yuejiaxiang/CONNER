# -*- coding: UTF-8 -*-
# @Time    : 2021/1/8
# @Author  : xiangyuejia@qq.com
# Apache License
# Copyright©2020-2021 xiangyuejia@qq.com All Rights Reserved

import os
import json
import pickle
import random
import shutil
import re
import pandas as pd
from data_process.rule_base_unit import RuleBaseUnit
rbu = RuleBaseUnit()
random.seed(10)


def get_mod(ori_text, ori_input=''):
    # IsMean 只处理了10%，带有average的
    # IsMeanHasSD 放弃
    # IsMeanHasTolerance 放弃
    # IsMeanIsRange 放弃
    # IsRangeHasTolerance 放弃
    # 以下是IsList所还没有考虑的情况
    # 20 × 20 degrees
    # 6 kg to 13 kg
    # 85/15%
    mods = set()
    text = ori_text.lower()
    input = ori_input.lower()
    approximate = ['approximately', '∼', '≈', '≳', '≲', 'nominally', 'about', 'around', 'close to', 'circa', 'the order of', 'near', 'roughly']
    range = [' – ', '<', '>', '≤', '≥', '⩽', '⩾', '≳', '≲', 'above', 'at least', 'greater than', 'up to', 'to', 'after', 'as low as', 'as much as', 'at least', 'before', 'below', 'between', 'down to', 'last', 'less than', 'more than', 'over', 'range', 'ranging', 'since', 'top', 'up to', 'upto', 'upper', 'within', 'to']
    if '±' in text:
        mods.add('HasTolerance')
    for app in approximate:
        if app in text:
            mods.add('IsApproximate')
            break
    if 'from' in text and 'to' in text:
        mods.add('IsApproximate')
    if 'and' in text or 'or' in text:
        mods.add('IsList')
    if 'average' in text:
        mods.add('IsMean')
    if 'median' in input or 'median' in text:
        mods.add('IsMedian')
    for ran in range:
        if ran in text:
            mods.add('IsRange')
            break
    if re.search('\d-\d', text):
        mods.add('IsRange')
    # if len(mods) == 0:
    #     if '.' not in text:
    #         mods.add('IsCount')
    return list(mods)


class Mod:
    def __init__(self, text_path, mod_path):
        self.read_data(text_path, mod_path)

    def read_data(self, text_path, mod_path):
        with open(text_path, 'r', encoding='utf8') as fin:
            text = [d.strip().split('\t')[0] for d in fin.readlines()]
        with open(mod_path, 'r', encoding='utf8') as fin:
            mod = [d.strip() for d in fin.readlines()]
        self.mod = dict()
        for t,m in zip(text[1:], mod):
            self.mod[t] = m

    def get_mod(self, ori_text, ori_input=''):
        if ori_text in self.mod:
            ori_label = self.mod[ori_text]
            if ori_label == 'Empty':
                return []
            return ori_label.split('&')
        else:
            return get_mod(ori_text, ori_input=ori_input)


# 切.有难度，先不切
def text2list(text):
    # text: 'ab cd'
    # text_list: ['ab', 'cd']
    # index2list: 00011
    text_list = []
    index2list = {}
    tmp = ''
    for t in range(len(text)):
        index2list[t] = len(text_list)
        if text[t] == ' ':
            if len(tmp) > 0:
                text_list.append(tmp)
                tmp = ''
        else:
            tmp += text[t]
    if len(tmp) > 0:
        text_list.append(tmp)
    return text_list, index2list


def choose_key(data, keyname):
    all_data = []
    for d in data:
        new_d = dict()
        for k in keyname:
            new_d[k] = d[k]
        all_data.append(new_d)
    return all_data


def get_excel_format(ann_all):
    excel_list = {}
    annot_2_q = {}
    annot_2_t = {}
    # add Quantity
    for i, ann in enumerate(ann_all):
        startOffset, endOffset, annotType, annotType_append, text, annotId, other = ann
        if annotType == 'Quantity':
            excel_list[annotId] = {'Quantity': [text, startOffset]}
            for k,v in other.items():
                excel_list[annotId][k] = v
            annot_2_q[annotId] = annotId
            annot_2_t[annotId] = annotType
    # add hasQuantity
    for i, ann in enumerate(ann_all):
        startOffset, endOffset, annotType, annotType_append, text, annotId, other = ann
        for k, v in other.items():
            if k == 'HasQuantity' and v in excel_list:
                excel_list[v][annotType] = [text, startOffset]
                annot_2_q[annotId] = v
                annot_2_t[annotId] = annotType
    # add hasProperty
    for i, ann in enumerate(ann_all):
        startOffset, endOffset, annotType, annotType_append, text, annotId, other = ann
        for k, v in other.items():
            if k == 'HasProperty' and v in annot_2_q:
                excel_list[annot_2_q[v]][annotType] = [text, startOffset]
                annot_2_q[annotId] = annot_2_q[v]
                annot_2_t[annotId] = annotType
    # add Qualifies
    # 不确定是否会有重复
    for i, ann in enumerate(ann_all):
        startOffset, endOffset, annotType, annotType_append, text, annotId, other = ann
        for k, v in other.items():
            if k == 'Qualifies' and v in annot_2_q:
                excel_list[annot_2_q[v]]['Qualifier_' + annot_2_t[v]] = [text, startOffset]
    return excel_list


def get_ere_format(ann_all):
    triples = []
    excel_list = get_excel_format(ann_all)
    for k, v in excel_list.items():
        q_name = v['Quantity']
        for m, p in zip(['MeasuredEntity', 'MeasuredProperty', 'Qualifier_Quantity'],
                        ['toEntity', 'toProperty', 'toQualifier']):
            if m in v:
                triples.append([q_name, p, v[m]])
    return triples, excel_list


def get_label_format(ann_all, additional_type='append'):
    this_entity = dict()
    for ann in ann_all:
        startOffset, endOffset, annotType, annotType_append, text, _, _ = ann
        for t in range(startOffset, endOffset):
            type_this = annotType
            if annotType_append and additional_type == 'append':
                type_this = annotType + '-' + annotType_append
        if type_this not in this_entity:
            this_entity[type_this] = {}
        if text not in this_entity[type_this]:
            this_entity[type_this][text] = []
        if [startOffset, endOffset - 1] not in this_entity[type_this][text]:
            this_entity[type_this][text].append([startOffset, endOffset - 1])
    return this_entity


def correct_boundary(b, e, text):
    or_b = b
    or_e = e
    max_id = len(text)
    while text[b].isalpha() and b > 0 and text[b-1].isalpha():
        b -= 1
    while text[e-1].isalpha() and e <= max_id-1 and text[e].isalpha():
        e += 1
    if e != or_e or b != or_b:
        print('### correct_boundary ###')
        print('ori: {}'.format(text[or_b:or_e]))
        print('cor: {}'.format(text[b:e]))
    return b, e, text[b:e]


def read_semeval(path_tsv, path_text, mode='train', additional_type='append', do_correct_boundary=True):
    whole_ann = []
    files = os.listdir(path_text)
    for file in files:
        if '.txt' not in file:
            continue
        full_file = os.path.join(path_text, file)
        core, _ = os.path.splitext(file)
        tsv_p = os.path.join(path_tsv, core + '.tsv')
        with open(full_file, 'r', encoding='utf8') as fin:
            text_all = fin.readlines()
            if len(text_all) > 1:
                print('warning: len(text) > 1: ', full_file)
                text_all = ''.join(text_all)
                text_all = text_all.replace('.\n', '\n')
                text_all = [text_all.replace('\n', '. ')]
            input_text = text_all[0].strip()

        if mode == 'test':
            whole_ann.append({'text': input_text, 'id':core})
            continue

        if not os.path.exists(tsv_p):
            print('tsv not exist for {}'.format(full_file))
            continue
        data = pd.read_csv(tsv_p, sep='\t', header=0)

        ann_all = []
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

            if do_correct_boundary:
                startOffset, endOffset, text = correct_boundary(startOffset, endOffset, text_all[0])

            if input_text[startOffset: endOffset] != text:
                print('error: text not match: {}'.format(text))

            annotType_append = None
            if 'mods' in other:
                if len(other['mods']) > 1:
                    # print('mods > 1: {}'.format(core))
                    pass
                annotType_append = '&'.join(sorted(other['mods']))
            ann_all.append([startOffset, endOffset, annotType, annotType_append, text, annotId, other])

        this_entity = get_label_format(ann_all, additional_type=additional_type)
        whole_ann.append({'text': input_text, 'anns': ann_all, 'label': this_entity, 'id':core})
    return whole_ann


def read_semeval_list(path_tsv_list, path_text_list, mode='train', additional_type='notpad'):
    whole_ann = []
    for path_tsv, path_text in zip(path_tsv_list, path_text_list):
        whole_ann += read_semeval(path_tsv, path_text, mode=mode, additional_type=additional_type)
    return whole_ann


##分句函数
def cut_sentence(text):
    re_exp = re.compile("(?<=[^A-Z]\.) (?![0-9%])")
    raw_sentences = re.split(re_exp,text)
    offset = 0
    sentences = []
    for idx,senten in enumerate(raw_sentences):
        if not sentences:
            sentences.append(senten)
        else:
            if len(senten)<100:
                sentences[-1] = sentences[-1]+" "+senten
            else:
                sentences.append(senten)
    sentence_offset = []
    for sent in sentences:
        sentence_offset.append([offset, offset + len(sent)])
        offset += (len(sent)+1)
    return (sentences, sentence_offset)


def cut_sentence_old(text):
    sents = []
    sents_indx = []
    p = 0
    for t in range(len(text)):
        if t >= 1 and text[t-1:t+1] == '. ':
            sents.append(text[p:t])
            sents_indx.append([p, t])
            p = t+1
    if p < len(text):
        sents.append(text[p:t+1])
        sents_indx.append([p, t+1])
    print('text: ', text)
    print('sents: ', sents)
    print('sents_indx: ', sents_indx)
    return sents, sents_indx


def sliding_window(text, window=50, step=20):
    sents = []
    sents_indx = []
    max_t = len(text)
    for t in range(max_t):
        if t % step == 0:
            e = min(max_t, t+window)
            sents.append(text[t:e])
            sents_indx.append([t, e])
    return sents, sents_indx

def split_data(whole_ann, mode='train', method='cut_sentence', additional_type='notpad'):
    new_whole_ann = []
    if method == 'cut_sentence':
        split_method = cut_sentence
    if method == 'sliding_window':
        split_method = sliding_window
    for wann in whole_ann:
        text = wann['text']
        if mode == 'train':
            anns = wann['anns']

        sents, sents_indx = split_method(text)
        for sent, sentx in zip(sents, sents_indx):
            if mode == 'test':
                new_whole_ann.append({
                    'text': sent,
                    'sentx':sentx,
                    'id': wann['id'],
                    'quantity': [],
                    'excel': [],
                })
                continue
            new_anns = []
            for ann in anns:
                startOffset, endOffset, annotType, annotType_append, text, annotId, other = ann
                if startOffset >= sentx[0] and endOffset <= sentx[1]:
                    new_anns.append([startOffset-sentx[0], endOffset-sentx[0], annotType, annotType_append, text, annotId, other])
            ann_dict_format = get_label_format(new_anns, additional_type=additional_type)
            ere_triple_format, excel_list = get_ere_format(new_anns)
            new_whole_ann.append({
                'text': sent,
                'anns': new_anns,
                'label': ann_dict_format,
                'quantity': ere_triple_format,
                'excel': excel_list,
                'sentx':sentx,
                'id': wann['id']
            })
    return new_whole_ann


def add_rel(data):
    anno_set = {}
    id = 0
    for type, v in data.items():
        for text in v:
            for vi in v[text]:
                anno_id = vi[2]
                if anno_id not in anno_set:
                    anno_set[anno_id] = []
                annotId = 'T' + str(id)
                id += 1
                vi.append(annotId)
                anno_set[anno_id].append(vi + [type, text])

    rel = {}
    for anno_id, v in anno_set.items():
        anno_set[anno_id].sort(key=lambda x: x[0])
        q = []
        q_rel = {}
        for i, vi in enumerate(v):
            if vi[4] == 'Quantity':
                q.append(vi)
                q_rel[vi[3]] = []
        for i, vi in enumerate(v):
            if vi[4] == 'Quantity':
                continue
            this_dis = []
            for j, qi in enumerate(q):
                dis = min(abs(qi[0]-vi[1]), abs(qi[1]-vi[0]))
                this_dis.append([dis, j])
            this_dis.sort(key=lambda x: x[0])
            if len(this_dis) > 0:
                q_rel[q[this_dis[0][1]][3]].append(vi)

        for k, v in q_rel.items():
            # p2q
            p = []
            for vi in v:
                if vi[4] == 'MeasuredProperty':
                    p.append(vi[3])
                    rel[vi[3]] = ['HasQuantity', k]
                if vi[4] == 'Qualifier':
                    rel[vi[3]] = ['Qualifies', k]
            for vi in v:
                if vi[4] == 'MeasuredEntity':
                    if not p:
                        rel[vi[3]] = ['HasQuantity', k]
                    else:
                        rel[vi[3]] = ['HasProperty', p[0]]
    return data, anno_set, rel


def connet(data):
    all_label = {}
    for ann, [idx, d] in enumerate(data):
        for k,v in d['label'].items():
            if k not in all_label:
                all_label[k] = {}
            for k1,v1 in d['label'][k].items():
                if k1 not in all_label[k]:
                    all_label[k][k1] = []
                for v2 in d['label'][k][k1]:
                    v2[0] = int(v2[0])
                    v2[1] = int(v2[1])
                    if v2 not in all_label[k][k1]:
                        all_label[k][k1].append([v2[0]+idx[0], v2[1]+idx[0]+1, ann])
    return all_label


def connet_ere(data, all_ner_data, append_iso_q=True):
    all_label = {}
    for ann, [idx, d] in enumerate(data):
        text = d['text']

        all_ner_quantity = set()
        all_ere_quantity = set()
        if (d['id'], text) not in all_ner_data:
            print('not match in all_ner_data')
        for tn in all_ner_data[(d['id'], text)]:
            all_ner_quantity.add((tn[0], tn[1]))

        for rel in d['quantity']:
            all_ere_quantity.add((rel[0][0], rel[0][1]))
            h = rel[0][0]
            h_idx = [rel[0][1]+idx[0], rel[0][1]+idx[0]+ len(h)]
            h_id = (h_idx[0], h_idx[1], text[rel[0][1]:rel[0][1]+len(h)], ann)
            relation = rel[1]
            t = rel[2][0]
            t_idx = [rel[2][1]+idx[0], rel[2][1]+idx[0] + len(t)]
            t_id = (t_idx[0], t_idx[1], text[rel[2][1]:rel[2][1]+len(t)])
            if h_id not in all_label:
                all_label[h_id] = {}
            all_label[h_id][relation] = t_id

        iso_quantity = all_ner_quantity - all_ere_quantity
        if append_iso_q:
            for iq in iso_quantity:
                h_idx = [iq[1] + idx[0], iq[1] + idx[0] + len(iq[0])]
                h_id = (h_idx[0], h_idx[1], text[iq[1]:iq[1] + len(iq[0])], ann)
                all_label[h_id] = {}

    return all_label


def add_rel_ere(data):
    Tid2type = {}
    anno_set = {}
    raw_rel = {}
    rel = {}
    id = 0
    head_id = 0
    for head, r in data.items():
        idx2Tid = {}
        head_text = head[2]
        if head_text == '':
            print('head_text is empty')
        ann = head[3]
        if ann not in anno_set:
            anno_set[ann] = []
        if (head[0], head[1]) not in idx2Tid:
            Tid = 'T' + str(head_id) + '-' + str(id)
            idx2Tid[(head[0], head[1])] = Tid
            id += 1
            anno_set[ann].append([head[0], head[1], ann, Tid, 'Quantity', head_text])
            Tid2type[Tid] = 'Quantity'
        else:
            Tid = idx2Tid[(head[0], head[1])]

        for rel_name, tail in r.items():
            tail_text = tail[2]
            if (tail[0], tail[1]) not in idx2Tid:
                Tid = 'T' + str(head_id) + '-' + str(id)
                idx2Tid[(tail[0], tail[1])] = Tid
                id += 1
                if rel_name == 'toEntity':
                    tail_type = 'MeasuredEntity'
                if rel_name == 'toProperty':
                    tail_type = 'MeasuredProperty'
                if rel_name == 'toQualifier':
                    tail_type = 'Qualifier'
                anno_set[ann].append([tail[0], tail[1], ann, Tid, tail_type, tail_text])
                Tid2type[Tid] = tail_type
            else:
                Tid = idx2Tid[(tail[0], tail[1])]

        Tid_head = idx2Tid[(head[0], head[1])]
        for rel_name, tail in r.items():
            Tid_tail = idx2Tid[(tail[0], tail[1])]
            if Tid_head not in raw_rel:
                raw_rel[Tid_head] = {}
            raw_rel[Tid_head][rel_name] = Tid_tail

        head_id += 1

    for head, r in raw_rel.items():
        for rel_name, tail in r.items():
            if rel_name == 'toQualifier':
                if Tid2type[tail] != 'Qualifier':
                    print('rel & type dismatch')
                    continue
                rel[tail] = ['Qualifies', head]
            if rel_name == 'toProperty':
                if Tid2type[tail] != 'MeasuredProperty':
                    print('rel & type dismatch')
                    continue
                rel[tail] = ['HasQuantity', head]
            if rel_name == 'toEntity':
                if Tid2type[tail] != 'MeasuredEntity':
                    print('rel & type dismatch')
                    continue
                if 'toProperty' not in r:
                    rel[tail] = ['HasQuantity', head]
                else:
                    rel[tail] = ['HasProperty', r['toProperty']]

    return None, anno_set, rel


def add_rel_ere_v2(data):
    Tid2type = {}
    anno_set = {}
    raw_rel = {}
    rel = {}
    id = 0
    head_id = 0
    for head, r in data.items():
        idx2Tid = {}
        head_text = head[2]
        if head_text == '':
            print('head_text is empty')
        ann = head[3]
        if ann not in anno_set:
            anno_set[ann] = []
        if (head[0], head[1]) not in idx2Tid:
            Tid = 'T' + str(head_id) + '-' + str(id)
            idx2Tid[(head[0], head[1])] = Tid
            id += 1
            anno_set[ann].append([head[0], head[1], ann, Tid, 'Quantity', head_text])
            Tid2type[Tid] = 'Quantity'
        else:
            Tid = idx2Tid[(head[0], head[1])]

        for rel_name, tail in r.items():
            tail_text = tail[2]
            if (tail[0], tail[1]) not in idx2Tid:
                Tid = 'T' + str(head_id) + '-' + str(id)
                idx2Tid[(tail[0], tail[1])] = Tid
                id += 1
                if rel_name == 'toEntity':
                    tail_type = 'MeasuredEntity'
                if rel_name == 'toProperty':
                    tail_type = 'MeasuredProperty'
                if rel_name == 'toQualifier':
                    tail_type = 'Qualifier'
                anno_set[ann].append([tail[0], tail[1], ann, Tid, tail_type, tail_text])
                Tid2type[Tid] = tail_type
            else:
                Tid = idx2Tid[(tail[0], tail[1])]

        Tid_head = idx2Tid[(head[0], head[1])]
        for rel_name, tail in r.items():
            Tid_tail = idx2Tid[(tail[0], tail[1])]
            if Tid_head not in raw_rel:
                raw_rel[Tid_head] = {}
            raw_rel[Tid_head][rel_name] = Tid_tail

        head_id += 1

    for head, r in raw_rel.items():
        for rel_name, tail in r.items():
            if rel_name == 'toQualifier':
                if Tid2type[tail] != 'Qualifier':
                    print('rel & type dismatch')
                    continue
                rel[tail] = ['Qualifies', head]
            if rel_name == 'toProperty':
                if Tid2type[tail] != 'MeasuredProperty':
                    print('rel & type dismatch')
                    continue
                rel[tail] = ['HasQuantity', head]
            if rel_name == 'toEntity':
                if Tid2type[tail] != 'MeasuredEntity':
                    print('rel & type dismatch')
                    continue
                if 'toProperty' not in r:
                    rel[tail] = ['HasQuantity', head]
                else:
                    rel[tail] = ['HasProperty', r['toProperty']]

    return None, anno_set, rel


def change_annotSet(data, rel):
    QuantityId = 0
    id2ann = {}
    for _, entities in data.items():
        for entity in entities:
            if entity[4] == 'Quantity':
                entity[2] = QuantityId
                id2ann[entity[3]] = entity[2]
                QuantityId += 1
    for _, entities in data.items():
        for entity in entities:
            if entity[4] == 'MeasuredProperty':
                entity[2] = id2ann[rel[entity[3]][1]]
                id2ann[entity[3]] = entity[2]
    for _, entities in data.items():
        for entity in entities:
            if entity[4] == 'MeasuredEntity':
                entity[2] = id2ann[rel[entity[3]][1]]
    return data


def clean_data_for_ner2tsv(data, rel, add_qualifier=False):
    enw_data = {}
    matched_id = set()
    for _, entities in data.items():
        for entity in entities:
            if entity[4] == 'Quantity':
                matched_id.add(entity[3])
    for _, entities in data.items():
        for entity in entities:
            if add_qualifier and entity[4] == 'Qualifier':
                if entity[3] in rel and rel[entity[3]][1] in matched_id:
                    matched_id.add(entity[3])
    for _, entities in data.items():
        for entity in entities:
            if entity[4] == 'MeasuredProperty':
                if entity[3] in rel and rel[entity[3]][1] in matched_id:
                    matched_id.add(entity[3])
    for _, entities in data.items():
        for entity in entities:
            if entity[4] == 'MeasuredEntity':
                if entity[3] in rel and rel[entity[3]][1] in matched_id:
                    matched_id.add(entity[3])
    for setId, entities in data.items():
        for entity in entities:
            annotId = entity[3]
            annotType = entity[4]
            if annotType != 'Quantity' and annotId not in rel:
                print('error: has no rel')
                continue
            if annotId not in matched_id:
                continue
            if setId not in enw_data:
                enw_data[setId] = []
            enw_data[setId].append(entity)
    return enw_data


def ner2tsv(data, rel, id, sent='', mod_tool=None, add_qualifier=False):
    data = clean_data_for_ner2tsv(data, rel, add_qualifier=add_qualifier)
    data = change_annotSet(data, rel)

    tsv = ['docId	annotSet	annotType	startOffset	endOffset	annotId	text	other']
    for _, entities in data.items():
        for entity in entities:
            docId = id
            annotSet = str(entity[2])
            annotType = entity[4]
            startOffset = str(entity[0])
            endOffset = str(entity[1])
            annotId = entity[3]
            text = entity[5]
            if annotType == 'Quantity':
                other_all = {}
                other_unit = rbu.get_unit(text)
                if mod_tool:
                    base_mod = get_mod(text, sent)
                    other_mod = mod_tool.get_mod(text, sent)
                    if base_mod != other_mod:
                        pass
                else:
                    other_mod = get_mod(text, sent)
                if other_unit != '':
                    other_all['unit'] = other_unit
                if other_mod != []:
                    other_all['mods'] = other_mod
                other = json.dumps(other_all)
                # if other_all != {}:
                #     other = json.dumps(other_all)
                # else:
                #     other = ''
            else:
                if annotId not in rel:
                    print('error: has no rel')
                    continue
                other = json.dumps({rel[annotId][0]: rel[annotId][1]})

            newline = [docId, annotSet, annotType, startOffset, endOffset, annotId, text, other]
            tsv.append('\t'.join(newline))
    return tsv


def excel2tsv_unit(data, rel, um, id):
    data = clean_data_for_ner2tsv(data, rel)
    # data = change_annotSet_excel2tsv(data, rel)

    tsv = ['docId	annotSet	annotType	startOffset	endOffset	annotId	text	other']
    for _, entities in data.items():
        for entity in entities:
            docId = id
            annotSet = str(entity[2])
            annotType = entity[4]
            startOffset = str(entity[0])
            endOffset = str(entity[1])
            annotId = entity[3]
            text = entity[5]
            if annotType == 'Quantity':
                other_all = {}
                if annotId in um and 'Unit' in um[annotId] and um[annotId]['Unit']:
                    other_all['unit'] = um[annotId]['Unit']
                if annotId in um and 'modifier' in um[annotId] and um[annotId]['modifier'] != ['']:
                    other_all['mods'] = um[annotId]['modifier']
                other = json.dumps(other_all)
                # if other_all != {}:
                #     other = json.dumps(other_all)
                # else:
                #     other = ''
            else:
                if annotId not in rel:
                    print('error: has no rel')
                    continue
                other = json.dumps({rel[annotId][0]: rel[annotId][1]})

            newline = [docId, annotSet, annotType, startOffset, endOffset, annotId, text, other]
            if annotSet != annotId[1]:
                xxx = 1

            tsv.append('\t'.join(newline))
    return tsv


def clean_pre_tsv_format(path='/Users/apricot/semeval_task8/ner_process/pre_tsv_format'):
    dir_name = path
    if os.path.exists(dir_name):
        shutil.rmtree(dir_name)
    os.mkdir(dir_name)


def save_data(data, file):
    file_path, _ = os.path.split(file)
    if not os.path.exists(file_path):
        os.mkdir(file_path)
    with open(file, 'w', encoding='utf8') as fout:
        for d in data:
            print(d, file=fout)


def save_data_json(data, file):
    file_path, _ = os.path.split(file)
    if not os.path.exists(file_path):
        os.mkdir(file_path)
    with open(file, 'w', encoding='utf8') as fout:
        json.dump(data, fout)


def save_data_pickle(data, file):
    file_path, _ = os.path.split(file)
    if not os.path.exists(file_path):
        os.mkdir(file_path)
    with open(file, 'wb') as fout:
        pickle.dump(data, fout)


def cut_text(text, line_len=50):
    ids = []
    nums = 0
    slice = []
    out_text = ''
    text_len = len(text)
    text_spl = text.split(' ')
    text_spl_len = len(text_spl)
    i = 0
    while True:
        step = 1
        step_len = len(text_spl[i])
        while i+step < text_spl_len:
            if step_len + len(text_spl[i+step]) + 1 > line_len:
                break
            step_len += len(text_spl[i+step]) + 1
            step += 1
        slice.append(' '.join(text_spl[i: i+step]))
        ids.append(nums)
        i += step
        nums += len(slice[-1]) + 1
        if nums > text_len:
            break
    for i, s in enumerate(slice):
        out_text += str(i) + ' '*(2-len(str(i))) + '$  ' + s + '\n'
    out_text = out_text.strip()
    return out_text, ids, slice


def get_slice_line(idx, slice_list):
    line = 0
    for i, p in enumerate(slice_list):
        if idx > p:
            line = i
    return line


def ambiguity(text, token):
    if text.count(token) > 1:
        return True
    return False


def select_sentx_pre(sentx, pre):
    out_sentx = []
    out_pre = []
    text2p = {}
    for i, p in enumerate(pre):
        text2p[p['text']] = i
    for sent in sentx:
        if sent['text'] in text2p:
            out_sentx.append(sent)
            out_pre.append(pre[text2p[sent['text']]])
    return out_sentx, out_pre


def get_mod_text(b, e, text, expend=0, method=0):
    if method == 0:
        return text[b:e]
    if method == 1:
        return text[max(0, b-expend):e+expend]
    if method == 2:
        b = max(0, b-expend)
        e = min(len(text), e+expend)
        while b > 0:
            if text[b] == ' ':
                break
            b -= 1
        while e < len(text):
            if text[e] == ' ':
                break
            e += 1
        return text[b+1: e]

def get_mod_label(label_dic, method=0):
    label = 'Empty'
    if method == 0:
        if 'mods' in label_dic:
            label = '&'.join(sorted(label_dic['mods']))
    return label


def get_mod_data(data, method_text=0, expend=0, method_label=0):
    mod_data = []
    for d in data:
        whole_text = d['text']
        for a in d['anns']:
            if a[2] == 'Quantity':
                text = get_mod_text(a[0], a[1], whole_text, expend=expend, method=method_text)
                label = get_mod_label(a[6], method=method_label)
                mod_data.append([text, label])
    return mod_data


def split_train_test(data, rate, mode='part'):
    train_labels = set()
    train = []
    test = []
    for d in data:
        if d[1] in train_labels and random.random() > rate:
            test.append(d)
            if mode == 'all':
                train.append(d)
        else:
            train.append(d)
            train_labels.add(d[1])
    return train, test


def get_all_ner_quantity(file):
    with open(file, 'r', encoding='utf8') as fin:
        data = [json.loads(d.strip()) for d in fin.readlines()]
    ner = dict()
    for d in data:
        ner[(d['id'], d['text'])] = d['quantity']
    return ner


if __name__ == '__main__':
    text = 'ascsssss. b. cdsssscdssssssssssssSSSSSsssSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSScdssssssssssssSSSSSsssSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSssssssssSSSSSsssSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS'
    a = cut_sentence(text)
    print(a)