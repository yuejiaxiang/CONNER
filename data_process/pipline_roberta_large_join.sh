#!/bin/bash
#python change_data_format_tsv2ner.py
#run ner model
python change_data_format_ner2tsv.py \
  --ner_file ../ner_process/output/20210128/roberta_large_10_result.json \
  --ere_file ../ere_process/input/20210128_roberta_large_10_result/ere_input_test \
  --mod_file ../mod_process/input/20210128_roberta_large_10_result/mod_input_test \
  --post_file ../post_process/20210128_roberta_large_10_result/ner_entities.json
#python change_data_format_tsv2mod.py
#export BERT_BASE_DIR=/dockerdata/yuejiaxiang/semeval_task8/mod_process/BERT_BASE_DIR/uncased_L-12_H-768_A-12
#export DATA_DIR=/dockerdata/yuejiaxiang/semeval_task8/mod_process/data/t0_e0_l0_r0.8_all
#export CHECK_DIR=/dockerdata/yuejiaxiang/semeval_task8/mod_process/output_t0_e0_l0_r0.8_all
#CUDA_VISIBLE_DEVICES=1 python run_classifier.py \
#  --task_name=MRPC \
#  --do_train=true \
#  --do_eval=true \
#  --data_dir=$DATA_DIR \
#  --vocab_file=$BERT_BASE_DIR/vocab.txt \
#  --bert_config_file=$BERT_BASE_DIR/bert_config.json \
#  --init_checkpoint=$BERT_BASE_DIR/bert_model.ckpt \
#  --max_seq_length=128 \
#  --train_batch_size=32 \
#  --learning_rate=2e-5 \
#  --num_train_epochs=3.0 \
#  --output_dir=$CHECK_DIR
cd ../mod_process
rm -r tmp
mkdir tmp
cp data/t0_e0_l0_r0.8_all/train.tsv tmp/train.tsv
cp ../mod_process/input/20210128_roberta_large_10_result/mod_input_test tmp/dev.tsv
export BERT_BASE_DIR=/dockerdata/yuejiaxiang/semeval_task8/mod_process/BERT_BASE_DIR/uncased_L-12_H-768_A-12
export DATA_DIR=../mod_process/tmp
export CHECK_DIR=/dockerdata/yuejiaxiang/semeval_task8/mod_process/output_t0_e0_l0_r0.8_all
CUDA_VISIBLE_DEVICES=1 python run_classifier.py \
  --task_name=MRPC \
  --do_train=false \
  --do_eval=false \
  --do_predict=true \
  --data_dir=$DATA_DIR \
  --vocab_file=$BERT_BASE_DIR/vocab.txt \
  --bert_config_file=$BERT_BASE_DIR/bert_config.json \
  --init_checkpoint=$BERT_BASE_DIR/bert_model.ckpt \
  --max_seq_length=128 \
  --train_batch_size=32 \
  --learning_rate=2e-5 \
  --num_train_epochs=3.0 \
  --output_dir=$CHECK_DIR
sz output_t0_e0_l0_r0.8_all/test_results.tsv.label
mv output_t0_e0_l0_r0.8_all/test_results.tsv.label ../mod_process/output/20210118_predict_10_vote_7/t0_e0_l0_r0.8_all
#run ere model
python change_data_format_ere2tsv.py \
  --ere_in_file ../ere_process/input/20210128_roberta_large_10_result/ere_input_test \
  --ere_out_file ../ere_process/output/20210128_roberta_large_10_result/ere_pred.json \
  --mod_in_file ../mod_process/input/20210128_roberta_large_10_result/mod_input_test \
  --mod_out_file ../mod_process/output/20210128_roberta_large_10_result/t0_e0_l0_r0.8_all \
#  --add_qualifier
python concat_tsv.py
