# -*- coding: UTF-8 -*-
# @Time    : 2021/1/6
# @Author  : xiangyuejia@qq.com
# Apache License
# Copyright©2020-2021 xiangyuejia@qq.com All Rights Reserved
import json
from data_process.change_data_format_unit import text2list, read_semeval_list, split_data, choose_key

def main_process():
    # 参数设置
    use_BIO = 'noBIO'  # 是否添加BIO标签，'noBIO' or 'useBIO'
    mode = 'train'  # 处理训练集数据还是测试集数据，'train' or 'test'
    method = 'cut_sentence'  # 切句子的不同模式，按句切分或滑动窗口，'cut_sentence' or 'sliding_window'
    additional_type = 'notpad'  # 是否对Quantity标签做扩展 'append' or 'notpad'

    # mode = 'train'
    mode = 'train'
    path_text = [
        '../MeasEval/data/train/text',
        '../MeasEval/data/trial/txt'
    ]  # 输入数据的位置
    path_tsv = [
        '../MeasEval/data/train/tsv',
        '../MeasEval/data/trial/tsv'
    ]  # train的输入数据的位置
    out_file_dict_format = '_'.join(['ner_json_format', use_BIO, method, additional_type, mode])  # 'dict' format 的输出文件的名称
    # 读入原始数据
    whole_ann = read_semeval_list(path_tsv, path_text, mode=mode, additional_type=additional_type)
    whole_ann = split_data(whole_ann, mode=mode, method=method, additional_type=additional_type)
    # 为'dict' format 输出train数据
    all_ner_data = choose_key(whole_ann, ['text', 'label'])
    all_ner_data_id = choose_key(whole_ann, ['id'])
    with open(out_file_dict_format, 'w', encoding='utf8') as fout:
        for d, id in zip(all_ner_data, all_ner_data_id):
            xd = json.dumps(d, ensure_ascii=False)
            # print(d['text'])
            # print(id['id'])
            print(xd, file=fout)

    # mode = 'test'
    mode = 'test'
    # 下面这个是假的测试集
    # path_text = [
    #     '../MeasEval/data/train/text',
    #     '../MeasEval/data/trial/txt'
    # ]
    # path_tsv = ['pass', 'pass']
    # # 下面这个是真的测试集
    path_text = ['../MeasEval/data/eval/text']  # 输入数据的位置
    path_tsv = ['pass']  # train的输入数据的位置
    out_file_dict_format = '_'.join(['ner_json_format', use_BIO, method, additional_type, mode])  # 'dict' format 的输出文件的名称
    out_file_dict_format_sentx = '_'.join(['ner_json_format_sentx', use_BIO, method, additional_type, mode])  # 'dict' format 的输出文件的名称
    # 读入原始数据
    whole_ann = read_semeval_list(path_tsv, path_text, mode=mode, additional_type=additional_type)
    whole_ann = split_data(whole_ann, mode=mode, method=method, additional_type=additional_type)
    # 为'dict' format 输出train数据
    all_ner_data = choose_key(whole_ann, ['text'])
    all_ner_data_id = choose_key(whole_ann, ['id'])
    with open(out_file_dict_format, 'w', encoding='utf8') as fout:
        for d, id in zip(all_ner_data, all_ner_data_id):
            xd = json.dumps(d, ensure_ascii=False)
            # print(d['text'])
            # print(id['id'])
            print(xd, file=fout)
    all_sentx_data = choose_key(whole_ann, ['text', 'sentx', 'id'])
    with open(out_file_dict_format_sentx, 'w', encoding='utf8') as fout:
        json.dump(all_sentx_data, fout)


if __name__ == '__main__':
    main_process()



# 为'dict' format 输出test数据


# # for 'list'
#
# 'list' format 的输出文件的名称
# out_file_list_format_1 = '_'.join(['ner_list_format_texts', use_BIO, method, additional_type, mode])
# out_file_list_format_2 = '_'.join(['ner_list_format_types', use_BIO, method, additional_type, mode])
#
#
# ner_texts = []
# ner_types = []
# all_types_set = set()
#
# for wa in whole_ann:
#     input_text = wa['text']
#     ann_all = wa['anns']
#
#     text_list, index2list = text2list(input_text)
#
#     ner_type = ['O'] * len(text_list)
#     writed_type = [0] * len(text_list)  # 保护每个位置最多写一次label
#     for ann in ann_all:
#         startOffset, endOffset, annotType, annotType_append, text = ann
#         all_world = set()
#         for t in range(startOffset, endOffset):
#             x = index2list[t]
#             all_world.add(text_list[x])
#             type_this = annotType
#             if annotType_append and additional_type == 'append':
#                 type_this = annotType + '-' + annotType_append
#             all_types_set.add(type_this)
#
#             if use_BIO == 'useBIO':
#                 if t == startOffset:
#                     type_this = 'B-' + type_this
#                 else:
#                     type_this = 'I-' + type_this
#             if writed_type[x] == 0:
#                 ner_type[x] = type_this
#                 writed_type[x] = 1
#
#         print(text)
#         print(all_world)
#
#     assert len(text_list) == len(ner_type)
#     ner_texts.append(text_list)
#     ner_types.append(ner_type)
#
# with open(out_file_list_format_1, 'w', encoding='utf8') as fout:
#     for d in ner_texts:
#         print(' '.join(d), file=fout)
#
# with open(out_file_list_format_2, 'w', encoding='utf8') as fout:
#     for d in ner_types:
#         print(' '.join(d), file=fout)
#
#
# print(all_types_set)