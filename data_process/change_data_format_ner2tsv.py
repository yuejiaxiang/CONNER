# -*- coding: UTF-8 -*-
# @Time    : 2021/1/15
# @Author  : xiangyuejia@qq.com
# Apache License
# Copyright©2020-2021 xiangyuejia@qq.com All Rights Reserved
import os
import json
import sys
import getopt


def main_process(ner_file='', ere_file='', mod_file='', post_file=''):
    from data_process.change_data_format_unit import ner2tsv, save_data, connet, add_rel, select_sentx_pre, clean_pre_tsv_format, save_data_json, save_data_pickle
    sentx_file = 'ner_json_format_sentx_noBIO_cut_sentence_notpad_test'
    if ner_file == '':
        ner_output_file = '../ner_process/output/20210118/predict_10_vote_7.json'
    else:
        ner_output_file = ner_file
    if ere_file == '':
        ere_input_path = '../ere_process/input/unknown/ere_input_test'
    else:
        ere_input_path = ere_file
    if mod_file == '':
        mod_input_path = '../mod_process/output/unknown/mod_input_test.json'
    else:
        mod_input_path = mod_file
    if post_file == '':
        post_path = '../post_process/unknown/ner_entities.json'
        post_sent_path = '../post_process/unknown/ner_sent_entities.pkl'
    else:
        post_path = post_file
        post_sent_path = os.path.join(os.path.split(post_file)[0], 'ner_sent_entities.pkl')
    tsv_output_path = '../ner_process/pre_tsv_format'


    with open(sentx_file, 'r', encoding='utf8') as fin:
        sentx_data = json.load(fin)
    with open(ner_output_file, 'r', encoding='utf8') as fin:
        pre_data = [json.loads(l.strip()) for l in fin.readlines()]
    clean_pre_tsv_format()
    old_id = ''
    all_data_for_one_case = []
    post_sent_data = {}
    sentx_data, pre_data = select_sentx_pre(sentx_data, pre_data)
    for sentx, pre in zip(sentx_data, pre_data):
        def update_post_sent_data(post_sent_data, sentx, pre):
            ner_data = pre['label']
            id = (sentx['id'], sentx['text'])
            if id not in post_sent_data:
                post_sent_data[id] = {}
            for k, v in ner_data.items():
                if k not in post_sent_data[id]:
                    post_sent_data[id][k] = []
                for vn, vp in v.items():
                    for vpi in vp:
                        post_sent_data[id][k].append([vn, vpi[0]])

        update_post_sent_data(post_sent_data, sentx, pre)

        if sentx['text'] != pre['text']:
            print('error')
        if sentx['id'] != old_id:
            if old_id == '':
                old_id = sentx['id']
            else:
                data_pls, anno_set, rel = add_rel(connet(all_data_for_one_case))

                data = ner2tsv(anno_set, rel, old_id, sent=sentx['text'])
                out_put_file = os.path.join(tsv_output_path, old_id + '.tsv')
                save_data(data, out_put_file)
                old_id = sentx['id']
                all_data_for_one_case = []
        all_data_for_one_case.append([sentx['sentx'], pre])
    data_pls, anno_set, rel = add_rel(connet(all_data_for_one_case))
    data = ner2tsv(anno_set, rel, old_id)
    out_put_file = os.path.join(tsv_output_path, sentx['id'] + '.tsv')
    save_data(data, out_put_file)


    # for ere input
    ere_input_data = []
    for sentx, pre in zip(sentx_data, pre_data):
        q_l = []
        if 'Quantity' in pre['label']:
            for qu in pre['label']['Quantity'].keys():
                q_l.append([qu, pre['label']['Quantity'][qu][0][0]])
        ere_input_data.append(json.dumps({
            'id': sentx['id'],
            'text': sentx['text'],
            "quantity": q_l,
        }))
    save_data(ere_input_data, ere_input_path)


    # for cls input
    quantities = set()
    for sentx, pre in zip(sentx_data, pre_data):
        if 'Quantity' in pre['label']:
            for qu in pre['label']['Quantity'].keys():
                quantities.add(qu)
    data = ['text\tlabel']
    for q in sorted(list(quantities)):
        data.append('{}\tEmpty'.format(q))
    save_data(data, mod_input_path)

    # for post sent-level input
    save_data_pickle(post_sent_data, post_sent_path)

    # for post input
    post_data = {}
    for sentx, pre in zip(sentx_data, pre_data):
        id = sentx['id']
        pos = sentx['sentx'][0]
        if id not in post_data:
            post_data[id] = {}
        for k, v in pre['label'].items():
            if k not in post_data[id]:
                post_data[id][k] = []
            for vn, vp in v.items():
                for vpi in vp:
                    post_data[id][k].append([vn, vpi[0]+pos])

    save_data_json(post_data, post_path)


if __name__ == '__main__':
    ner_file = ''
    ere_file = ''
    mod_file = ''
    post_file = ''
    opts, args = getopt.getopt(sys.argv[1:], '-n:-e:-m:-p:', ['ner_file=', 'ere_file=', 'mod_file=', 'post_file='])
    for opt_name, opt_value in opts:
        if opt_name in ('-n', '--ner_file'):
            ner_file = opt_value
    for opt_name, opt_value in opts:
        if opt_name in ('-e', '--ere_file'):
            ere_file = opt_value
    for opt_name, opt_value in opts:
        if opt_name in ('-m', '--mod_file'):
            mod_file = opt_value
    for opt_name, opt_value in opts:
        if opt_name in ('-p', '--post_file'):
            post_file = opt_value



    main_process(ner_file=ner_file, ere_file=ere_file, mod_file=mod_file, post_file=post_file)
