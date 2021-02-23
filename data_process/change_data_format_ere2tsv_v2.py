# -*- coding: UTF-8 -*-
# @Time    : 2021/1/21
# @Author  : xiangyuejia@qq.com
# Apache License
# Copyright©2020-2021 xiangyuejia@qq.com All Rights Reserved

import os
import json
import sys
import getopt
from data_process.change_data_format_unit import ner2tsv, save_data, connet_ere, add_rel_ere_v2, select_sentx_pre, \
    clean_pre_tsv_format, Mod, get_all_ner_quantity


def main_process(
        sentx_file='',
        ere_in_file='',
        ere_out_file='',
        mod_in_file='',
        mod_out_file='',
        tsv_path='',
        not_use_iso=False,
        not_use_mod=False,
        add_qualifier=False,
):
    if sentx_file == '':
        sentx_file = 'ner_json_format_sentx_noBIO_cut_sentence_notpad_test'
    if ere_in_file == '':
        ere_in_file = '../ere_process/input/20210118_predict_10_vote_7/ere_input_test'
    if ere_out_file == '':
        ere_out_file = '../ere_process/output/20210122_20200118join/ere_pred.json'
    if mod_in_file == '':
        mod_in_file = '../mod_process/input/20210118_predict_10_vote_7/mod_input_test'
    if mod_out_file == '':
        mod_out_file = '../mod_process/output_t0_e0_l0_r0.8_all/eval_results.txt'
    if tsv_path == '':
        tsv_path = '../ner_process/pre_tsv_format'

    # ere_file = '/Users/apricot/semeval_task8/ere_process/output/20210121/ere_json_format_cut_sentence_train'
    # ere_file = '/Users/apricot/semeval_task8/ere_process/output/20210121/ere_pred.json'
    # ere_file = '/Users/apricot/semeval_task8/ere_process/output/20210122_20200118join/ere_pred.json'
    # ere_file = '/Users/apricot/semeval_task8/ere_process/output/20210122_20210120seperate/ere_pred.json'
    # ere_file = '/Users/apricot/semeval_task8/ere_process/output/20210126/pred_train_bycv.json'
    if not_use_iso:
        append_iso_q = False
    else:
        append_iso_q = True
    if not_use_mod:
        mod_tool = None
    else:
        mod_tool = Mod(mod_in_file, mod_out_file)

    with open(sentx_file, 'r', encoding='utf8') as fin:
        sentx_data = json.load(fin)
    with open(ere_out_file, 'r', encoding='utf8') as fin:
        pre_data = [json.loads(l.strip()) for l in fin.readlines()]
    clean_pre_tsv_format()
    # with open(ere_file, 'r', encoding='utf8') as fin:
    #      pre_data = json.load(fin)

    old_id = ''
    all_data_for_one_case = []
    sentx_data, pre_data = select_sentx_pre(sentx_data, pre_data)
    all_ner_data = get_all_ner_quantity(ere_in_file)

    for sentx, pre in zip(sentx_data, pre_data):
        if sentx['text'] != pre['text']:
            print('error')
        all_rels = set([p[1] for p in pre['quantity']])
        if 'toQualifier' in all_rels:
            find_toQualifier = True
        if sentx['id'] != old_id:
            if old_id == '':
                old_id = sentx['id']
            else:
                data_pls, anno_set, rel = add_rel_ere_v2(connet_ere(all_data_for_one_case, all_ner_data, append_iso_q=append_iso_q))
                data = ner2tsv(anno_set, rel, old_id, sent=sentx['text'], mod_tool=mod_tool, add_qualifier=add_qualifier)
                out_put_file = os.path.join(tsv_path, old_id + '.tsv')
                save_data(data, out_put_file)
                old_id = sentx['id']
                all_data_for_one_case = []
        all_data_for_one_case.append([sentx['sentx'], pre])
    data_pls, anno_set, rel = add_rel_ere_v2(connet_ere(all_data_for_one_case, all_ner_data, append_iso_q=append_iso_q))
    data = ner2tsv(anno_set, rel, old_id, sent=sentx['text'], mod_tool=mod_tool)
    out_put_file = os.path.join(tsv_path, sentx['id'] + '.tsv')
    save_data(data, out_put_file)


if __name__ == '__main__':
    sentx_file = ''
    ere_in_file = ''
    ere_out_file = ''
    mod_in_file = ''
    mod_out_file = ''
    tsv_path = ''
    not_use_iso = False
    not_use_mod = False
    add_qualifier = False
    opts, args = getopt.getopt(
        sys.argv[1:], '-s:-n:-e:-i:-o:-t:', [
            'sentx_file=',
            'ere_in_file=',
            'ere_out_file=',
            'mod_in_file=',
            'mod_out_file=',
            'tsv_path=',
            'not_use_iso',
            'not_use_mod',
            'add_qualifier',
    ])
    for opt_name, opt_value in opts:
        if opt_name in ('-s', '--sentx_file'):
            sentx_file = opt_value
    for opt_name, opt_value in opts:
        if opt_name in ('-n', '--ere_in_file'):
            ere_in_file = opt_value
    for opt_name, opt_value in opts:
        if opt_name in ('-e', '--ere_out_file'):
            ere_out_file = opt_value
    for opt_name, opt_value in opts:
        if opt_name in ('-m', '--mod_in_file'):
            mod_in_file = opt_value
    for opt_name, opt_value in opts:
        if opt_name in ('-m', '--mod_out_file'):
            mod_out_file = opt_value
    for opt_name, opt_value in opts:
        if opt_name in ('-t', '--tsv_path'):
            tsv_path = opt_value
    for opt_name, opt_value in opts:
        if opt_name in ('--not_use_iso'):
            not_use_iso = True
    for opt_name, opt_value in opts:
        if opt_name in ('--not_use_mod'):
            not_use_mod = True
    for opt_name, opt_value in opts:
        if opt_name in ('--add_qualifier'):
            add_qualifier = True

    main_process(
        sentx_file=sentx_file,
        ere_in_file=ere_in_file,
        ere_out_file=ere_out_file,
        mod_in_file=mod_in_file,
        mod_out_file=mod_out_file,
        tsv_path=tsv_path,
        not_use_iso=not_use_iso,
        not_use_mod=not_use_mod,
        add_qualifier=add_qualifier,
    )

