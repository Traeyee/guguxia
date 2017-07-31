#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import loukou
import loukou.lexical as ll
from compatitator import *

__version__ = '0.01'
__license__ = 'MIT'

switch_debug = False

PATH_PARATAXIS_DEFAULT = "PARATAXIS.txt"
PATH_EFFECT_DEFAULT = "EFFECT.txt"
PATH_REASONING_DEFAULT = "REASONING.txt"
PATH_INCLUDING_DEFAULT = "INCLUDING.txt"

dir_mod = os.path.split(os.path.realpath(__file__))[0]

_get_abs_path = lambda path: os.path.normpath(os.path.join(os.getcwd(), path))

str_test = r"因为你是肥仔，所以我也是肥仔"
# str_test = r"这个是可以缓解症状的"
# str_test = r"用于治疗和预防全身所有部位的骨关节炎，包括膝关节、肩关节、髋关节、手腕关节、颈及脊椎关节和踝关节等。可缓解和消除骨关节炎的疼痛、肿胀等症状，改善关节活动功能。"
str_test = r"用于治疗和预防全身所有部位的骨关节炎，包括膝关节、肩关节、髋关节、手腕关节、颈及脊椎关节和踝关节等"
# str_test = r"全身所有部位的骨关节炎，包括膝关节、肩关节、髋关节、手腕关节、颈及脊椎关节和踝关节等"
str_test = r"皮肤黏膜的过敏，如荨麻疹、过敏性鼻炎、皮肤瘙痒症、药疹，对虫咬症和接触性皮炎也有效。"


chars_strip = [u"，", u",", u'"', u"。"]
class Juzi(object):

    def __init__(self, str_given):
        self.string = strdecode(str_given)

    def strip(self):
        str_rt = self.string
        flag_changed = True
        while flag_changed:
            str_tmp = str_rt
            flag_changed = False
            str_rt = str_rt.strip()
            for item in chars_strip:
                str_rt = str_rt.strip(item)
            if str_tmp != str_rt:
                flag_changed = True
        return str_rt

    def test(self):
        print self.string


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

class Guguxia(object):

    def __init__(self, lk_instance=None):
        # if lk_instance:
        #     self.tokenizer = ll.Lexical(lk_instance)
        # else:
        #     self.tokenizer = ll.Lexical(loukou.Loukou())
        self.signs_parataxis = []
        self.signs_effect = []
        self.loaded_effect = False
        self.loaded_reasoning= False
        self.loaded_parataxis = False
        self.loaded_including = False
        self.patterns_effect = []
        self.patterns_reasoning = []
        self.patterns_including = []

    def engine_normal(self, str0, list_pattern):
        list_tang = []
        list_song = []
        str1 = strdecode(str0)
        for ptn in list_pattern:
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
                            # 对于此Pair内的每一个word，都去尝试
                            if str1[pos:].startswith(word):
                                if i > 0 and u"RAW" != ptn.pattern[i - 1].flag:
                                    dict_rst[ptn.pattern[i - 1].flag] = str_saved
                                pos += len(word)  # 跳到下一个位置
                                flag_hit = True
                                # 命中则跳出尝试
                                break
                        if flag_hit:
                            # 前面匹配了，跳到此Pattern的下一个Pair
                            break
                        str_saved += str1[pos]
                        pos += 1
                    if not flag_hit:
                        # 若没命中则跳出
                        break
                i += 1
                if len(ptn.pattern) == i + 1 and u"RAW" != ptn.pattern[i].flag \
                        and flag_hit:
                    # 若
                    # 下一个Pair是最后一个Pair 且 是非RAW Pair 且刚才命中了Pair
                    # 说明命中了这个Pattern
                    dict_rst[ptn.pattern[i].flag] = str1[pos:]
                    break
            if flag_hit:
                list_tang.append(dict_rst[u"TANG"])
                list_song.append(dict_rst[u"SONG"])
                break
                # print dict_rst[u"TANG"]
                # print dict_rst[u"SONG"]
            # break
        dict_rt = {}
        dict_rt[u"TANG"] = list_tang
        dict_rt[u"SONG"] = list_song
        return dict_rt


    def pointer_effect(self, str0, complex=True):
        if not self.loaded_effect:
            with open(os.path.join(dir_mod, PATH_EFFECT_DEFAULT), "r") as f_in:
                for line in f_in:
                    self.signs_effect.append(line.decode("utf-8").strip())
            f_in.close()
            content = u";;".join(self.signs_effect)
            self.patterns_effect.append(Pattern([Pair(u"TANG", u"*"),
                                                 Pair(u"RAW", content),
                                                 Pair(u"SONG", u"*")]))
            self.loaded_effect = True
        dict_rst = self.engine_normal(str0, self.patterns_effect)
        dict_rst_map = {}
        dict_rst_map[u"OBJECT"] = dict_rst[u"TANG"]
        dict_rst_map[u"SUBJECT"] = []

        if complex:
            for subj in dict_rst[u"SONG"]:
                dict_idx = {}
                for sign in self.signs_effect:
                    idx = subj.find(sign)
                    if idx in dict_idx and len(dict_idx[idx]) > len(sign):
                        continue
                    dict_idx[idx] = sign
                list_idx = [t[0] for t in sorted(dict_idx.items(), key=lambda d: d[0])]
                flag_break = False
                for idx in list_idx:
                    if -1 != idx:
                        if not self.loaded_parataxis:
                            self.tool_parataxis(u"")
                        for sign_para in self.signs_parataxis:
                            if subj[: idx].endswith(sign_para):
                                # dict_rst_map[u"SUBJECT"].append(subj[:
                                # (idx - len(sign_para))])
                                dict_temp = self.tool_including(subj[: (idx - len(sign_para))])
                                for dad in dict_temp[u"FATHER"]:
                                    if len(dad) > 0:
                                        dict_rst_map[u"SUBJECT"].append(dad)
                                for son in dict_temp[u"SON"]:
                                    if len(son) > 0:
                                        dict_rst_map[u"SUBJECT"].append(son)
                                dict_temp = self.pointer_effect(subj[idx:])
                                for subj_tmp in dict_temp[u"SUBJECT"]:
                                    if len(subj_tmp) > 0:
                                        dict_rst_map[u"SUBJECT"].append(subj_tmp)
                                #     dict_temp2 = self.tool_including(subj_tmp)
                                #     for dad in dict_temp2[u"FATHER"]:
                                #         if len(dad) > 0:
                                #             dict_rst_map[u"SUBJECT"].append(dad)
                                #     for son in dict_temp2[u"SON"]:
                                #         if len(son) > 0:
                                #             dict_rst_map[u"SUBJECT"].append(son)
                                    # for sub_subj_tmp in self.tool_parataxis(subj_tmp):
                                        # dict_rst_map[u"SUBJECT"].append(sub_subj_tmp)
                                flag_break = True
                                break
                        else:
                            if switch_debug:
                                print ("Debug(1): %s" % subj).encode("utf-8")
                    elif switch_debug:
                        print ("Debug(2): %s" % subj).encode("utf-8")

                    if flag_break:
                        break
                else:
                    dict_temp3 = self.tool_including(subj)
                    for dad in dict_temp3[u"FATHER"]:
                        if len(dad) > 0:
                            dict_rst_map[u"SUBJECT"].append(dad)
                    for son in dict_temp3[u"SON"]:
                        if len(son) > 0:
                            dict_rst_map[u"SUBJECT"].append(son)
        return dict_rst_map

    def tool_reasoning(self, str0):
        if not self.loaded_reasoning:
            with open(os.path.join(dir_mod, PATH_REASONING_DEFAULT), "r") as f_in:
                for line in f_in:
                    list_temp2 = []
                    for item in strdecode(line.strip()).split(u"||"):
                        list_temp = item.split(u"->")
                        flag_tmp = u""
                        if u"CAUSE" == list_temp[0]:
                            flag_tmp = u"TANG"
                        elif u"EFFECT" == list_temp[0]:
                            flag_tmp = u"SONG"
                        elif u"RAW" == list_temp[0]:
                            flag_tmp = u"RAW"
                        else:
                            list_temp2 = []
                            break
                        list_temp2.append(Pair(flag_tmp, list_temp[1]))
                    self.patterns_reasoning.append(Pattern(list_temp2))
            f_in.close()
            self.loaded_reasoning = True
        dict_rst = self.engine_normal(str0, self.patterns_reasoning)
        dict_rst_map = {}
        dict_rst_map[u"CAUSE"] = dict_rst[u"TANG"]
        dict_rst_map[u"EFFECT"] = dict_rst[u"SONG"]
        return dict_rst_map

    def tool_parataxis(self, str0, method=None):
        if not self.loaded_parataxis:
            with open(os.path.join(dir_mod, PATH_PARATAXIS_DEFAULT), "r") as f_in:
                content = strdecode(f_in.read())
                for line in content.split("\n"):
                    self.signs_parataxis.append(line.strip())
            f_in.close()
            self.loaded_parataxis = True
        list_rt = []
        dict_idx = {}
        for sign in self.signs_parataxis:
            idx = str0.find(sign)
            if idx in dict_idx and len(dict_idx[idx]) > len(sign):
                continue
            dict_idx[idx] = sign
        list_idx = [t[0] for t in sorted(dict_idx.items(), key=lambda d: d[0])]
        for idx in list_idx:
            if idx > 0:
                list_rt.append(str0[: idx])
                for item in self.tool_parataxis(str0[(idx + len(dict_idx[idx])):]):
                    if len(item) > 0:
                        list_rt.append(item)
                break
        else:
            list_rt.append(str0)
        return list_rt

    def tool_including(self, str0):
        if not self.loaded_including:
            with open(os.path.join(dir_mod, PATH_INCLUDING_DEFAULT), "r") as f_in:
                for line in f_in:
                    list_temp2 = []
                    for item in strdecode(line.strip()).split(u"||"):
                        list_temp = item.split(u"->")
                        flag_tmp = u""
                        if u"FATHER" == list_temp[0]:
                            flag_tmp = u"TANG"
                        elif u"SON" == list_temp[0]:
                            flag_tmp = u"SONG"
                        elif u"RAW" == list_temp[0]:
                            flag_tmp = u"RAW"
                        else:
                            list_temp2 = []
                            break
                        list_temp2.append(Pair(flag_tmp, list_temp[1]))
                    self.patterns_including.append(Pattern(list_temp2))
            f_in.close()
            self.loaded_including = True
        dict_rst = self.engine_normal(str0, self.patterns_including)
        dict_rst_map = {}
        dict_rst_map[u"FATHER"] = []
        dict_rst_map[u"SON"] = []

        for item1 in dict_rst[u"TANG"]:
            for item2 in self.tool_parataxis(item1):
                if len(item1) > 0:
                    dict_rst_map[u"FATHER"].append(item2)

        for item1 in dict_rst[u"SONG"]:
            for item2 in self.tool_parataxis(item1):
                if len(item1) > 0:
                    dict_rst_map[u"SON"].append(item2)

        if 0 == len(dict_rst_map[u"SON"]) + len(dict_rst_map[u"FATHER"]):
            dict_rst_map[u"FATHER"].extend(self.tool_parataxis(str0))
            # dict_rst_map[u"FATHER"].append(str0)

        return dict_rst_map

    def load_parataxis(self, path_and=PATH_PARATAXIS_DEFAULT):
        path_and = os.path.join(dir_mod, path_and)
        with open(path_and, "r") as f_in:
            content = strdecode(f_in.read())
            for line in content.split("\n"):
                self.signs_parataxis.append(line.strip())
        f_in.close()

    def sumup2NTseq_parataxis(self, list_pair, dict_T2NT, trie_alt, tag_target):
        list_rt = []
        list_sign_idx = []

        for i in range(len(list_pair)):
            if list_pair[i].word in self.signs_parataxis:
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
                        if list_seq[i - 1].word in self.signs_parataxis and i - 3 >= 0:
                            if list_seq[i - 3].word in self.signs_parataxis:
                                if list_seq[i - 2].flag != dict_T2NT[tag_target]:
                                    list_tuple_merge.append((i - 2, i - 2))
                                    flag_merge = True
                            elif i - 4 >= 0:
                                if list_seq[i - 4].word in self.signs_parataxis:
                                    list_tuple_merge.append((i - 3, i - 2))
                                    flag_merge = True
                    if i + 1 < len(list_seq):
                        if list_seq[i + 1].word in self.signs_parataxis and i + 3 < len(list_seq):
                            if list_seq[i + 3].word in self.signs_parataxis:
                                if list_seq[i + 2].flag != dict_T2NT[tag_target]:
                                    list_tuple_merge.append((i + 2, i + 2))
                                    flag_merge = True
                        elif i + 4 < len(list_seq):
                            if list_seq[i + 4].word in self.signs_parataxis:
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
                    if list_seq[i + 1].word in self.signs_parataxis \
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
                    list_rt.append(u"RAW->%s" % list_seq[j].word)
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
        return u"||".join(list_rt)

    def extract_pattern(self, str_parsed, list_key):
        line = strdecode(str_parsed)
        if u"->" not in line:
            return u""
        list_item = line.split(u"||")
        list_flag = [item.split(u"->")[0] for item in list_item]
        list_word = [item.split(u"->")[1] for item in list_item]
        list_ptn = []
        if u"TGT" in list_flag:
            for item in list_key:
                if item in list_word:
                    for i in xrange(len(list_item)):
                        if list_flag[i] == u"TGT":
                            list_ptn.append(u"TGT")
                        else:
                            list_ptn.append(list_word[i])
                    return u"||".join(list_ptn)
        return u""




if __name__ == "__main__":
    lk = loukou.Loukou()
    ggx = Guguxia(lk)
    # 测试 including
    dict_rst = ggx.tool_including(str_test)
    for item in dict_rst[u"FATHER"]:
        print item
    for item in dict_rst[u"SON"]:
        print item
    # dict_rst = ggx.tool_reasoning(str_test)
    # for item in dict_rst[u"CAUSE"]:
    #     print item
    # for item in dict_rst[u"EFFECT"]:
    #     print item
    # dict_rst = ggx.pointer_effect(str_test)
    # for item in dict_rst[u"OBJECT"]:
    #     print item
    # for item in dict_rst[u"SUBJECT"]:
    #     print item
    # print " ".join(ggx.tool_parataxis(str_test))
