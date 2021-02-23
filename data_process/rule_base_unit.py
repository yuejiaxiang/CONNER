# -*- coding: UTF-8 -*-
# @Time    : 2021/1/19
# @Author  : xiangyuejia@qq.com
# Apache License
# Copyright©2020-2021 xiangyuejia@qq.com All Rights Reserved


class RuleBaseUnit:
    def __init__(self):
        with open('statistic/all_u.txt', 'r', encoding='utf8') as fin:
            self.data = [l.strip() for l in fin.readlines()]
        self.data.sort(key=lambda x: len(x), reverse=True)
        self.stopword = set([' ',])

    def get_unit_match(self, text):
        for t in self.data:
            if t in text:
                if text[-len(t):] == t:
                    return t
        return ''

    def get_unit_split(self, text):
        text = text.strip()
        if 'and' in text:
            text = text.split('and')[-1].strip()
        p = len(text)-1
        if ' ' in text:
            idx = text.find(' ')
            if text[idx-1].isalpha():
                p = idx-1
            else:
                return text[idx+1:].strip()
        test = p
        while (not text[test].isdigit()) and test >= 0:
            test -= 1
        if test == -1:
            return text[p+1:].strip()
        return text[test+1:].strip()

    def get_unit(self, text):
        unit = self.get_unit_match(text)
        if unit == '':
            unit = self.get_unit_split(text)
        if unit in ['/']:
            unit = ''
        return unit


if __name__ == '__main__':
    rbu = RuleBaseUnit()
    print('### test for get_unit_match ###')
    print(rbu.get_unit_match('1 μbar'))
    print(rbu.get_unit_match('0 and 2000 ppm'))
    print(rbu.get_unit_match('5%'))
    print(rbu.get_unit_match('5Rp'))
    print(rbu.get_unit_match('eight'))
    print('### test for get_unit_split ###')
    print(rbu.get_unit_split('1 μbar'))
    print(rbu.get_unit_split('0 and 2000 ppm'))
    print(rbu.get_unit_split('5%'))
    print(rbu.get_unit_split('5Rp'))
    print(rbu.get_unit_split('eight'))
    print('### test for get_unit ###')
    print(rbu.get_unit('1 μbar'))
    print(rbu.get_unit('0 and 2000 ppm'))
    print(rbu.get_unit('5%'))
    print(rbu.get_unit('5Rp'))
    print(rbu.get_unit('5Rp'))