import re

from transformers import BertTokenizer,ElectraTokenizer
from utils.extract_chinese_and_punct import ChineseAndPunctuationExtractor
# from extract_chinese_and_punct import ChineseAndPunctuationExtractor
from transformers import AutoTokenizer

chineseandpunctuationextractor = ChineseAndPunctuationExtractor()
# moren_tokenizer = BertTokenizer.from_pretrained("bert-large-uncased",do_lower_case=True)
# moren_tokenizer = BertTokenizer.from_pretrained('pred_ere/', do_lower_case=True)
#moren_tokenizer = ElectraTokenizer.from_pretrained('/apdcephfs/common/disease_data/yunyandata/ft_local/pretrain_chinese/electra-large', do_lower_case=True)
#moren_tokenizer = BertTokenizer.from_pretrained('/apdcephfs/common/disease_data/yunyandata/ft_local/pretrain_chinese/nezha', do_lower_case=True)
#moren_tokenizer = BertTokenizer.from_pretrained('/apdcephfs/common/disease_data/yunyandata/ft_local/pretrain_chinese/chinese_wwm_ext_pytorch', do_lower_case=True)
def covert_to_tokens(text, tokenizer=None, return_orig_index=False, max_seq_length=300):
    if not tokenizer:
        tokenizer =moren_tokenizer
    sub_text = []
    buff = ""
    flag_en = False
    flag_digit = False

    def _is_delimiter(c):
        if c>='A' and c<="Z":
            return False
        elif c>="a" and c<="z":
            return False
        elif c>="0" and c<="9":
            return False
        else:
            return True

    prev_is_delimiter = True
    for idx, c in enumerate(text):
        # if chineseandpunctuationextractor.is_chinese_or_punct(char):
        #     if buff != "":
        #         sub_text.append(buff)
        #         buff = ""
        #     sub_text.append(char)
        #     # flag_en = False
        #     # flag_digit = False
        # else:
        if _is_delimiter(c):
            prev_is_delimiter = True
            sub_text.append(c)
        else:
            if prev_is_delimiter:
                sub_text.append(c)
            else:
                sub_text[-1] += c
            prev_is_delimiter = False
    #         if re.compile('\d').match(char):  # 数字
    #             if buff != "" and flag_en:
    #                 sub_text.append(buff)
    #                 buff = ""
    #                 flag_en = False
    #             flag_digit = True
    #             buff += char
    #         # elif char >='A' and char<='Z':
    #         #     flag_digit = True
    #         #     buff += char
    #         # elif char >='a' and char<='z':
    #         #     flag_digit = True
    #         #     buff += char
    #         else:
    #             if buff != "" and flag_digit:
    #                 sub_text.append(buff)
    #                 buff = ""
    #                 flag_digit = False
    #             flag_en = True
    #             buff += char
    # if buff != "":
    #     sub_text.append(buff)

    tok_to_orig_start_index = []
    tok_to_orig_end_index = []
    tokens = []
    text_tmp = ''
    for (i, token) in enumerate(sub_text):
        sub_tokens = tokenizer.tokenize(token) if token != ' ' else []
        text_tmp += token
        for sub_token in sub_tokens:
            tok_to_orig_start_index.append(len(text_tmp) - len(token))
            tok_to_orig_end_index.append(len(text_tmp) - 1)
            tokens.append(sub_token)
            if len(tokens) >= max_seq_length - 2:
                break
        else:
            continue
        break
    if return_orig_index:
        return tokens, tok_to_orig_start_index, tok_to_orig_end_index
    else:
        return tokens


def search_spo_index(tokens, subject_sub_tokens, object_sub_tokens):
    subject_start_index, object_start_index = -1, -1
    forbidden_index = None
    if len(subject_sub_tokens) > len(object_sub_tokens):
        for index in range(
                len(tokens) - len(subject_sub_tokens) + 1):
            if tokens[index:index + len(
                    subject_sub_tokens)] == subject_sub_tokens:
                subject_start_index = index
                forbidden_index = index
                break

        for index in range(
                len(tokens) - len(object_sub_tokens) + 1):
            if tokens[index:index + len(
                    object_sub_tokens)] == object_sub_tokens:
                if forbidden_index is None:
                    object_start_index = index
                    break
                # check if labeled already
                elif index < forbidden_index or index >= forbidden_index + len(
                        subject_sub_tokens):
                    object_start_index = index

                    break

    else:
        for index in range(
                len(tokens) - len(object_sub_tokens) + 1):
            if tokens[index:index + len(
                    object_sub_tokens)] == object_sub_tokens:
                object_start_index = index
                forbidden_index = index
                break

        for index in range(
                len(tokens) - len(subject_sub_tokens) + 1):
            if tokens[index:index + len(
                    subject_sub_tokens)] == subject_sub_tokens:
                if forbidden_index is None:
                    subject_start_index = index
                    break
                elif index < forbidden_index or index >= forbidden_index + len(
                        object_sub_tokens):
                    subject_start_index = index
                    break

    return subject_start_index, object_start_index


def search_first(pattern, sequence):
    """从sequence中寻找子串pattern
    如果找到，返回第一个下标；否则返回-1。
    """
    n = len(pattern)
    for i in range(len(sequence)):
        if sequence[i:i + n] == pattern:
            return i
    return -1


def search_all(pattern, sequence):
    n = len(pattern)
    counts = 0
    starts = []
    for i in range(len(sequence)):
        if sequence[i:i+n] == pattern:
            counts += 1
            starts.append(i)
    return starts

# def search_all(word, sentence):
#     count = 0
#     starts = []
#     index = sentence.find(word)
#     while index != -1:
#         starts.append(index)
#         count += 1
#         index = sentence.find(word, index + len(word))
#     return count, starts

if __name__ == '__main__':
    text = 'ct患者1月余前无明显诱因下出现失语，只能发单音，有理解困难，右侧肢体活动不利，表现右上肢无法在床面移动，右下肢制动（石膏固定在位），无恶心呕吐，无神志不清，无发热，无肢体抽搐，无大小便失禁，遂由家属送至我院急诊，查“颅脑CT+肺部CT：右侧基底节区软化灶。心脏二尖瓣置换术后，左心明显增大，冠脉钙化，心包少量积液。左侧胸膜反应”，未予特殊处理，转至神经内科，予“盐酸川穹嗪针活血，依达拉奉针清除氧自由基，华法林（2.5mgqn自备）抗凝，瑞代营养支持，格列齐特控制血糖及对症支持治疗”等，上述症状有所好转。出院后在我科康复治疗，目前患者言语不利，吐词不清，右侧肢体活动不利，右上肢偶可见自主活动，右下肢未见自主活动，有咳嗽咳痰，无恶心呕吐，无发热，无胸痛心悸，无腹痛腹泻等不适'
    # text = 'Eg≈2.0 eV'
    # text='A precision of 1.00 (US = UH) means the hash function is 100% accurate (i.e., it produces a unique hash value for every distinct slice) whereas a precision of 1/US means that the hash function produces the same hash value for every slice leaving UH = 1.'
    # text='•SOC stocks decreased by 12.4% in Costa Rica and 0.13% in Nicaragua after establishment of coffee AFS.•SOC stocks increased in the top 10 cm of soil; greater reduction occurred at 20–40 cm.•Organic management caused a greater increase in 0–10 cm SOC but did not influence reduction at depth.•Shade type effects on SOC were smaller; no significant difference between shaded and unshaded coffee.•SOC stocks tend to converge on a level determined by site environment during establishment.'
    # tokenizer = AutoTokenizer.from_pretrained('/Users/zhangyunyan/Downloads/python库/pretrained/bert-base-uncased')
    tokenizer = AutoTokenizer.from_pretrained('/Users/zhangyunyan/Downloads/python库/pre-trained-chinese/MedBert-base')
    tokens, tok_s, tok_e = covert_to_tokens(text, tokenizer=tokenizer,return_orig_index=True)
    print('1')