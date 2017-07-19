#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import re
import os
import sys
import time
import logging
import marshal
import tempfile
import threading
import loukou
import loukou.posseg as lp
import compatitator

__version__ = '0.01'
__license__ = 'MIT'


PATH_AND_DEFAULT = "AND.txt"

dir_mod = os.path.split(os.path.realpath(__file__))[0]

_get_abs_path = lambda path: os.path.normpath(os.path.join(os.getcwd(), path))


class Guguxia(object):

    def __init__(self, lk_instance):
        self.tokenizer = lp.POSTokenizer(lk_instance)
        self.signs_AND = []
        self.load_AND()

    def load_AND(self, path_and=PATH_AND_DEFAULT):
        path_and = os.path.join(dir_mod, path_and)
        with open(path_and, "r") as f_in:
            content = compatitator.strdecode(f_in.read())
            for line in content.split("\n"):
                self.signs_AND.append(line.strip())
        f_in.close()

    def sumup2NTseq_AND(self, list_pair, dict_T2NT, trie_alt, tag_target):
        list_rt = []
        list_sign_idx = []

        for i in range(len(list_pair)):
            if list_pair[i].word in self.signs_AND:
                list_sign_idx.append(i)

        # if len(list_sign_idx) > 0:
        #     if 0 != list_sign_idx[0]:
        #         if list_pair[list_sign_idx[0] - 1] in list_target:

        list_seq = []
        for item in list_pair:
            flag_tmp = dict_T2NT[item.flag] if item.flag in dict_T2NT else item.flag
            list_seq.append(loukou.posseg.Pair(item.word, flag_tmp))

        # list_TGT = []
        # for item in list_target:
        #     list_TGT.append(dict_T2NT[item] if item in dict_T2NT else item)

        flag_merge = True
        while flag_merge:
            flag_merge = False
            list_tuple_merge = []
            for i in range(len(list_seq)):
                if list_seq[i].flag == dict_T2NT[tag_target]:
                    if i - 1 >= 0:
                        if list_seq[i - 1].word in self.signs_AND and i - 3 >= 0:
                            if list_seq[i - 3].word in self.signs_AND:
                                if list_seq[i - 2].flag != dict_T2NT[tag_target]:
                                    list_tuple_merge.append((i - 2, i - 2))
                                    flag_merge = True
                            elif i - 4 >= 0:
                                if list_seq[i - 4].word in self.signs_AND:
                                    list_tuple_merge.append((i - 3, i - 2))
                                    flag_merge = True
                    if i + 1 < len(list_seq):
                        if list_seq[i + 1].word in self.signs_AND and i + 3 < len(list_seq):
                            if list_seq[i + 3].word in self.signs_AND:
                                if list_seq[i + 2].flag != dict_T2NT[tag_target]:
                                    list_tuple_merge.append((i + 2, i + 2))
                                    flag_merge = True
                        elif i + 4 < len(list_seq):
                            if list_seq[i + 4].word in self.signs_AND:
                                list_tuple_merge.append((i + 2, i + 3))
                                flag_merge = True

            list_tuple_merge = sorted(list(set(list_tuple_merge)), key=lambda t: t[0])

            if not flag_merge:
                break

            list_seq_temp = []
            k = 0
            t_tmp = list_tuple_merge[k]
            list_word = [item.word for item in list_seq]
            i = 0
            while i < len(list_seq):
                if k >= len(list_tuple_merge):
                    list_seq_temp.extend(list_seq[i:])
                    break

                if i == t_tmp[0]:
                    list_seq_temp.append(lp.Pair("".join(list_word[t_tmp[0]: t_tmp[1] + 1]), dict_T2NT[tag_target]))
                    i = t_tmp[1]
                    k += 1
                else:
                    list_seq_temp.append(lp.Pair(list_seq[i].word, list_seq[i].flag))
                i += 1
            list_seq = list(list_seq_temp)

        list_all = []
        for i in range(len(list_seq)):
            if i + 2 < len(list_seq):
                if list_seq[i].flag == dict_T2NT[tag_target]:
                    if list_seq[i + 1].word in self.signs_AND \
                            and list_seq[i + 2].flag == dict_T2NT[tag_target]:
                        list_all.append(set([i, i + 2]))
                    else:
                        list_all.append(set([i]))
        list_all_temp = []
        flag_changed = True
        while flag_changed:
            flag_changed = False
            list_all_temp = []
            list_flag = []
            for i in range(len(list_all)):
                if i in list_flag:
                    continue
                for j in range(i + 1, len(list_all)):
                    if j in list_flag:
                        break
                    if len(list_all[i] & list_all[j]) > 0:
                        list_all_temp.append(list_all[i] | list_all[j])
                        list_flag.append(j)
                        flag_changed = True
                        break
                else:
                    list_all_temp.append(list_all[i])
            list_all = list(list_all_temp)

        # Sum up to pattern
        list_ptn = sorted([sorted(list(item)) for item in list_all], key=lambda l: l[0])

        i = 0
        k = 0

        while i < len(list_seq):
            if k >= len(list_ptn):
                # 假设i是下一个没加入的东西
                for j in range(i, len(list_seq)):
                    list_rt.append(u"RAW->%s" % list_seq[i].word)
                break
            if i != list_ptn[k][0]:
                list_rt.append(u"RAW->%s" % list_seq[i].word)
            else:
                str_tmp = u"TGT"
                for idx in list_ptn[k]:
                    str_tmp = str_tmp + u"->" + list_seq[idx].word
                list_rt.append(str_tmp)
                i = list_ptn[k][-1]
                k += 1
            i += 1
        print u"||".join(list_rt)
        print "db"
