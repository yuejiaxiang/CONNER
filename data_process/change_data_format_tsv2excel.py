# -*- coding: UTF-8 -*-
# @Time    : 2021/1/20
# @Author  : xiangyuejia@qq.com
# Apache License
# Copyright©2020-2021 xiangyuejia@qq.com All Rights Reserved
import json
import pandas as pd
from styleframe import StyleFrame
from tqdm import tqdm
from data_process.change_data_format_unit import read_semeval_list, split_data, choose_key, cut_text, get_slice_line, ambiguity

def get_excel(whole_ann):
    out_datas = [['paragraph ID', 'sentence ID', 'sentence', 'sliced info', 'sliced sent',
                  'quantity', 'quantity_line', 'unit', 'mod',
                  'property', 'property_line', 'entity', 'entity_line']]
    for ann in tqdm(whole_ann):
        slice_text, slice_ids, slice = cut_text(ann['text'])

        id = ann['id']
        text_idx = json.dumps(ann['sentx'])
        raw_text = ann['text']
        line_idx = json.dumps(slice_ids)
        slice_text = slice_text

        if len(ann['excel']) == 0:
            out_datas.append([
                id, text_idx, raw_text, line_idx, slice_text,
                '', '', '', '', '', '', '', ''
            ])

        for i, caseID in enumerate(ann['excel']):
            case = ann['excel'][caseID]
            quantity = ''
            quantity_line = ''
            unit = ''
            mod = ''
            property = ''
            property_line = ''
            entity = ''
            entity_line = ''

            if 'Quantity' in case:
                quantity = case['Quantity'][0]
                if ambiguity(raw_text, quantity):
                    quantity_line = get_slice_line(case['Quantity'][1], slice_ids)

            if 'unit' in case:
                unit = case['unit']

            if 'mods' in case:
                mod = ' '.join(case['mods'])

            if 'MeasuredProperty' in case:
                property = case['MeasuredProperty'][0]
                if ambiguity(raw_text, property):
                    property_line = get_slice_line(case['MeasuredProperty'][1], slice_ids)

            if 'MeasuredEntity' in case:
                entity = case['MeasuredEntity'][0]
                if ambiguity(raw_text, entity):
                    entity_line = get_slice_line(case['MeasuredEntity'][1], slice_ids)

            if i == 0:
                out_datas.append([
                    id, text_idx, raw_text, line_idx, slice_text,
                    quantity, quantity_line, unit, mod, property, property_line, entity, entity_line
                ])
            else:
                out_datas.append([
                    '', '', '', '', '',
                    quantity, quantity_line, unit, mod, property, property_line, entity, entity_line
                ])
    return out_datas

def generate_gold():
    path_text = [
        '../MeasEval/data/train/text',
        '../MeasEval/data/trial/txt'
    ]  # 输入数据的位置
    path_tsv = [
        '../MeasEval/data/train/tsv',
        '../MeasEval/data/trial/tsv'
    ]  # train的输入数据的位置
    whole_ann = read_semeval_list(path_tsv, path_text)
    whole_ann = split_data(whole_ann)
    out_datas = get_excel(whole_ann)
    ds = pd.DataFrame(out_datas)
    StyleFrame(ds).to_excel('data_enhancement/train.xlsx', index=False, header=False).save()


def generate_test():
    path_text = [
        '../MeasEval/data/eval/text',
    ]  # 输入数据的位置
    path_tsv = [
        '../ner_process/pre_tsv_format',
    ]  # train的输入数据的位置
    whole_ann = read_semeval_list(path_tsv, path_text)
    whole_ann = split_data(whole_ann)
    out_datas = get_excel(whole_ann)
    ds = pd.DataFrame(out_datas)
    StyleFrame(ds).to_excel('data_enhancement/NER_union_roberta_quantity_with_roberta_joint_ERE_isoQ_MOD1.xlsx', index=False, header=False).save()



def generate_raw(paths, out_file):
    mode = 'test'
    path_text = paths  # 输入数据的位置
    path_tsv = ['pass']  # train的输入数据的位置
    # 读入原始数据
    whole_ann = read_semeval_list(path_tsv, path_text, mode=mode)
    whole_ann = split_data(whole_ann, mode=mode)
    out_datas = get_excel(whole_ann)
    ds = pd.DataFrame(out_datas)
    StyleFrame(ds).to_excel(out_file, index=False, header=False).save()


if __name__ == '__main__':
    generate_gold()
    # generate_test()
    # generate_raw(['../MeasEval/data/eval/text'], 'data_enhancement/eval.xlsx')
    # generate_raw(['../MeasEval/data/SimpleText_auto'], 'data_enhancement/add.xlsx')