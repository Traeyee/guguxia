#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re

sys.path.append("..")
from compatitator import *


str_test = r"好像是之你是肥仔，是大家肥，肥，大概是引致的我也是肥仔"


class Pattern(object):

    def __init__(self, list_pair):
        self.pattern = []
        for item in list_pair:
            self.pattern.append(item)


class Pair(object):

    def __init__(self, flag, content):
        self.flag = flag
        # Form of 'content': word1;;word2;;word3
        self.list_word = []
        self.list_word.extend(content.split(u";;"))


list_pattern = []
with open("CE.txt", "r") as f_in:
    for line in f_in:
        list_temp2 = []
        for item in strdecode(line.strip()).split(u"||"):
            list_temp = item.split(u"->")
            list_temp2.append(Pair(list_temp[0], list_temp[1]))
        list_pattern.append(Pattern(list_temp2))
f_in.close()


def analyze(str0):
    list_cause = []
    list_effect = []
    str1 = strdecode(str0)
    for ptn in list_pattern:
        # list_mch = []
        # for pr in ptn:
        #     if pr.flag != u"RAW":
        #         list_mch.append(pr.list_word)

        # flag_matched = False

        # k = 0
        # for i in range(len(list_mch)):
        #     for item in list_mch[i]:  # 潜在case: 因为我是肥仔和因为他也是肥仔，所以我们惺惺相惜。(但此是病句)
        #         pos = str1.find(item, k)
        #         if -1 == pos:
        i = 0
        pos = 0
        dict_rst = {}
        flag_hit = False
        while i < len(ptn.pattern):
            flag_hit = False
            if ptn.pattern[i].flag == u"RAW":
                str_saved = u""
                while pos < len(str1):
                    for word in ptn.pattern[i].list_word:
                        if str1[pos:].startswith(word):
                            if i > 0:
                                dict_rst[ptn.pattern[i - 1].flag] = str_saved
                            pos += len(word)
                            flag_hit = True
                            break
                    if flag_hit:
                        break
                    str_saved += str1[pos]
                    pos += 1
            i += 1
            if len(ptn.pattern) == i + 1 and u"RAW" != ptn.pattern[i].flag \
                and flag_hit:
                dict_rst[ptn.pattern[i].flag] = str1[pos:]
                break
        if flag_hit:
            list_cause.append(dict_rst[u"CAUSE"])
            list_effect.append(dict_rst[u"EFFECT"])
            # print dict_rst[u"CAUSE"]
            # print dict_rst[u"EFFECT"]
            break
    return list_cause, list_effect

if __name__ == "__main__":
    lc, le = analyze(str_test)
    for stn in lc:
        print stn
    for stn in le:
        print stn
