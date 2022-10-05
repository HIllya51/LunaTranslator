#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module implements a simple conversion and localization between simplified and traditional Chinese using tables from MediaWiki.
It doesn't contains a segmentation function and uses maximal forward matching, so it's simple.
For a complete and accurate solution, see OpenCC.
For Chinese segmentation, see Jieba.

    >>> print(convert('我幹什麼不干你事。', 'zh-cn'))
    我干什么不干你事。
    >>> print(convert('人体内存在很多微生物', 'zh-tw'))
    人體內存在很多微生物

Support MediaWiki's convertion format:

    >>> print(convert_for_mw('在现代，机械计算-{}-机的应用已经完全被电子计算-{}-机所取代', 'zh-hk'))
    在現代，機械計算機的應用已經完全被電子計算機所取代
    >>> print(convert_for_mw('-{zh-hant:資訊工程;zh-hans:计算机工程学;}-是电子工程的一个分支，主要研究计算机软硬件和二者间的彼此联系。', 'zh-tw'))
    資訊工程是電子工程的一個分支，主要研究計算機軟硬體和二者間的彼此聯繫。
    >>> print(convert_for_mw('張國榮曾在英國-{zh:利兹;zh-hans:利兹;zh-hk:列斯;zh-tw:里茲}-大学學習。', 'zh-sg'))
    张国荣曾在英国利兹大学学习。

"""
# Only Python3 can pass the doctest here due to unicode problems.
__version__ = '1.4.3'

import os
import sys
import re
import json

try:
    from pkg_resources import resource_stream
    get_module_res = lambda *res: resource_stream(__name__, os.path.join(*res))
except ImportError:
    get_module_res = lambda *res: open(os.path.normpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__), *res)), 'rb')

# Locale fallback order lookup dictionary
Locales = {
    'zh-cn': ('zh-cn', 'zh-hans', 'zh-sg', 'zh'),
    'zh-hk': ('zh-hk', 'zh-hant', 'zh-tw', 'zh'),
    'zh-tw': ('zh-tw', 'zh-hant', 'zh-hk', 'zh'),
    'zh-sg': ('zh-sg', 'zh-hans', 'zh-cn', 'zh'),
    'zh-my': ('zh-my', 'zh-sg', 'zh-hans', 'zh-cn', 'zh'),
    'zh-mo': ('zh-mo', 'zh-hk', 'zh-hant', 'zh-tw', 'zh'),
    'zh-hant': ('zh-hant', 'zh-tw', 'zh-hk', 'zh'),
    'zh-hans': ('zh-hans', 'zh-cn', 'zh-sg', 'zh'),
    'zh': ('zh',) # special value for no conversion
}

_DEFAULT_DICT = "zhcdict.json"
DICTIONARY = _DEFAULT_DICT

zhcdicts = None
dict_zhcn = None
dict_zhsg = None
dict_zhtw = None
dict_zhhk = None
pfsdict = {}

RE_langconv = re.compile(r'(-\{|\}-)')
RE_splitflag = re.compile(r'\s*\|\s*')
RE_splitmap = re.compile(r'\s*;\s*')
RE_splituni = re.compile(r'\s*=>\s*')
RE_splitpair = re.compile(r'\s*:\s*')

def loaddict(filename=DICTIONARY):
    """
    Load the dictionary from a specific JSON file.
    """
    global zhcdicts
    if zhcdicts:
        return
    if filename == _DEFAULT_DICT:
        zhcdicts = json.loads(get_module_res(filename).read().decode('utf-8'))
    else:
        with open(filename, 'rb') as f:
            zhcdicts = json.loads(f.read().decode('utf-8'))
    zhcdicts['SIMPONLY'] = frozenset(zhcdicts['SIMPONLY'])
    zhcdicts['TRADONLY'] = frozenset(zhcdicts['TRADONLY'])

def getdict(locale):
    """
    Generate or get convertion dict cache for certain locale.
    Dictionaries are loaded on demand.
    """
    global zhcdicts, dict_zhcn, dict_zhsg, dict_zhtw, dict_zhhk, pfsdict
    if zhcdicts is None:
        loaddict(DICTIONARY)
    if locale == 'zh-cn':
        if dict_zhcn:
            got = dict_zhcn
        else:
            dict_zhcn = zhcdicts['zh2Hans'].copy()
            dict_zhcn.update(zhcdicts['zh2CN'])
            got = dict_zhcn
    elif locale == 'zh-tw':
        if dict_zhtw:
            got = dict_zhtw
        else:
            dict_zhtw = zhcdicts['zh2Hant'].copy()
            dict_zhtw.update(zhcdicts['zh2TW'])
            got = dict_zhtw
    elif locale == 'zh-hk' or locale == 'zh-mo':
        if dict_zhhk:
            got = dict_zhhk
        else:
            dict_zhhk = zhcdicts['zh2Hant'].copy()
            dict_zhhk.update(zhcdicts['zh2HK'])
            got = dict_zhhk
    elif locale == 'zh-sg' or locale == 'zh-my':
        if dict_zhsg:
            got = dict_zhsg
        else:
            dict_zhsg = zhcdicts['zh2Hans'].copy()
            dict_zhsg.update(zhcdicts['zh2SG'])
            got = dict_zhsg
    elif locale == 'zh-hans':
        got = zhcdicts['zh2Hans']
    elif locale == 'zh-hant':
        got = zhcdicts['zh2Hant']
    else:
        got = {}
    if locale not in pfsdict:
        pfsdict[locale] = getpfset(got)
    return got

def getpfset(convdict):
    pfset = []
    for word in convdict:
        for ch in range(len(word)):
            pfset.append(word[:ch+1])
    return frozenset(pfset)

def issimp(s, full=False):
    """
    Detect text is whether Simplified Chinese or Traditional Chinese.
    Returns True for Simplified; False for Traditional; None for unknown.
    If full=False, it returns once first simplified- or traditional-only
    character is encountered, so it's for quick and rough identification;
    else, it compares the count and returns the most likely one.
    Use `is` (True/False/None) to check the result.

    `s` must be unicode (Python 2) or str (Python 3), or you'll get None.
    """
    if zhcdicts is None:
        loaddict(DICTIONARY)
    simp, trad = 0, 0
    if full:
        for ch in s:
            if ch in zhcdicts['SIMPONLY']:
                simp += 1
            elif ch in zhcdicts['TRADONLY']:
                trad += 1
        if simp > trad:
            return True
        elif simp < trad:
            return False
        else:
            return None
    else:
        for ch in s:
            if ch in zhcdicts['SIMPONLY']:
                return True
            elif ch in zhcdicts['TRADONLY']:
                return False
        return None

def fallback(locale, mapping):
    for l in Locales[locale]:
        if l in mapping:
            return mapping[l]
    return convert(tuple(mapping.values())[0], locale)

def convtable2dict(convtable, locale, update=None):
    """
    Convert a list of conversion dict to a dict for a certain locale.

    >>> sorted(convtable2dict([{'zh-hk': '列斯', 'zh-hans': '利兹', 'zh': '利兹', 'zh-tw': '里茲'}, {':uni': '巨集', 'zh-cn': '宏'}], 'zh-cn').items())
    [('列斯', '利兹'), ('利兹', '利兹'), ('巨集', '宏'), ('里茲', '利兹')]
    """
    rdict = update.copy() if update else {}
    for r in convtable:
        if ':uni' in r:
            if locale in r:
                rdict[r[':uni']] = r[locale]
        elif locale[:-1] == 'zh-han':
            if locale in r:
                for word in r.values():
                    rdict[word] = r[locale]
        else:
            v = fallback(locale, r)
            for word in r.values():
                rdict[word] = v
    return rdict

def tokenize(s, locale, update=None):
    """
    Tokenize `s` according to corresponding locale dictionary.
    Don't use this for serious text processing.
    """
    zhdict = getdict(locale)
    pfset = pfsdict[locale]
    if update:
        zhdict = zhdict.copy()
        zhdict.update(update)
        newset = set()
        for word in update:
            for ch in range(len(word)):
                newset.add(word[:ch+1])
        pfset = pfset | newset
    ch = []
    N = len(s)
    pos = 0
    while pos < N:
        i = pos
        frag = s[pos]
        maxword = None
        maxpos = 0
        while i < N and frag in pfset:
            if frag in zhdict:
                maxword = frag
                maxpos = i
            i += 1
            frag = s[pos:i+1]
        if maxword is None:
            maxword = s[pos]
            pos += 1
        else:
            pos = maxpos + 1
        ch.append(maxword)
    return ch

def convert(s, locale, update=None):
    """
    Main convert function.

    :param s: must be `unicode` (Python 2) or `str` (Python 3).
    :param locale: should be one of ``('zh-hans', 'zh-hant', 'zh-cn', 'zh-sg'
                               'zh-tw', 'zh-hk', 'zh-my', 'zh-mo')``.
    :param update: a dict which updates the conversion table, eg.
        ``{'from1': 'to1', 'from2': 'to2'}``

    >>> print(convert('我幹什麼不干你事。', 'zh-cn'))
    我干什么不干你事。
    >>> print(convert('我幹什麼不干你事。', 'zh-cn', {'不干': '不幹'}))
    我干什么不幹你事。
    >>> print(convert('人体内存在很多微生物', 'zh-tw'))
    人體內存在很多微生物
    """
    if locale == 'zh' or locale not in Locales:
        # "no conversion"
        return s
    zhdict = getdict(locale)
    pfset = pfsdict[locale]
    newset = set()
    if update:
        # TODO: some sort of caching
        #zhdict = zhdict.copy()
        #zhdict.update(update)
        newset = set()
        for word in update:
            for ch in range(len(word)):
                newset.add(word[:ch+1])
        #pfset = pfset | newset
    ch = []
    N = len(s)
    pos = 0
    while pos < N:
        i = pos
        frag = s[pos]
        maxword = None
        maxpos = 0
        while i < N and (frag in pfset or frag in newset):
            if update and frag in update:
                maxword = update[frag]
                maxpos = i
            elif frag in zhdict:
                maxword = zhdict[frag]
                maxpos = i
            i += 1
            frag = s[pos:i+1]
        if maxword is None:
            maxword = s[pos]
            pos += 1
        else:
            pos = maxpos + 1
        ch.append(maxword)
    return ''.join(ch)

def convert_for_mw(s, locale, update=None):
    """
    Recognizes MediaWiki's human conversion format.
    Use locale='zh' for no conversion.

    Reference: (all tests passed)
    https://zh.wikipedia.org/wiki/Help:高级字词转换语法
    https://www.mediawiki.org/wiki/Writing_systems/Syntax

    >>> print(convert_for_mw('在现代，机械计算-{}-机的应用已经完全被电子计算-{}-机所取代', 'zh-hk'))
    在現代，機械計算機的應用已經完全被電子計算機所取代
    >>> print(convert_for_mw('-{zh-hant:資訊工程;zh-hans:计算机工程学;}-是电子工程的一个分支，主要研究计算机软硬件和二者间的彼此联系。', 'zh-tw'))
    資訊工程是電子工程的一個分支，主要研究計算機軟硬體和二者間的彼此聯繫。
    >>> print(convert_for_mw('張國榮曾在英國-{zh:利兹;zh-hans:利兹;zh-hk:列斯;zh-tw:里茲}-大学學習。', 'zh-hant'))
    張國榮曾在英國里茲大學學習。
    >>> print(convert_for_mw('張國榮曾在英國-{zh:利兹;zh-hans:利兹;zh-hk:列斯;zh-tw:里茲}-大学學習。', 'zh-sg'))
    张国荣曾在英国利兹大学学习。
    >>> convert_for_mw('-{zh-hant:;\\nzh-cn:}-', 'zh-tw') == ''
    True
    >>> print(convert_for_mw('毫米(毫公分)，符號mm，是長度單位和降雨量單位，-{zh-hans:台湾作-{公釐}-或-{公厘}-;zh-hant:港澳和大陸稱為-{毫米}-（台灣亦有使用，但較常使用名稱為毫公分）;zh-mo:台灣作-{公釐}-或-{公厘}-;zh-hk:台灣作-{公釐}-或-{公厘}-;}-。', 'zh-tw'))
    毫米(毫公分)，符號mm，是長度單位和降雨量單位，港澳和大陸稱為毫米（台灣亦有使用，但較常使用名稱為毫公分）。
    >>> print(convert_for_mw('毫米(毫公分)，符號mm，是長度單位和降雨量單位，-{zh-hans:台湾作-{公釐}-或-{公厘}-;zh-hant:港澳和大陸稱為-{毫米}-（台灣亦有使用，但較常使用名稱為毫公分）;zh-mo:台灣作-{公釐}-或-{公厘}-;zh-hk:台灣作-{公釐}-或-{公厘}-;}-。', 'zh-cn'))
    毫米(毫公分)，符号mm，是长度单位和降雨量单位，台湾作公釐或公厘。
    >>> print(convert_for_mw('毫米(毫公分)，符號mm，是長度單位和降雨量單位，-{zh-hans:台湾作-{公釐}-或-{公厘}-;zh-hant:港澳和大陸稱為-{毫米}-（台灣亦有使用，但較常使用名稱為毫公分）;zh-mo:台灣作-{公釐}-或-{公厘}-;zh-hk:台灣作-{公釐}-或-{公厘', 'zh-hk'))  # unbalanced test
    毫米(毫公分)，符號mm，是長度單位和降雨量單位，台灣作公釐或公厘
    >>> print(convert_for_mw('报头的“-{參攷消息}-”四字摘自鲁迅笔迹-{zh-hans:，“-{參}-”是“-{参}-”的繁体字，读音cān，与简体的“-{参}-”字相同；;zh-hant:，;}-“-{攷}-”是“考”的异体字，读音kǎo，与“考”字相同。', 'zh-tw'))
    報頭的「參攷消息」四字摘自魯迅筆跡，「攷」是「考」的異體字，讀音kǎo，與「考」字相同。
    >>> print(convert_for_mw('报头的“-{參攷消息}-”四字摘自鲁迅笔迹-{zh-hans:，“-{參}-”是“-{参}-”的繁体字，读音cān，与简体的“-{参}-”字相同；;zh-hant:，;}-“-{攷}-”是“考”的异体字，读音kǎo，与“考”字相同。', 'zh-cn'))
    报头的“參攷消息”四字摘自鲁迅笔迹，“參”是“参”的繁体字，读音cān，与简体的“参”字相同；“攷”是“考”的异体字，读音kǎo，与“考”字相同。
    >>> print(convert_for_mw('{{Col-break}}--&gt;', 'zh-hant'))
    {{Col-break}}--&gt;
    """
    ch = []
    rules = []
    ruledict = update.copy() if update else {}
    nested = 0
    block = ''
    for frag in RE_langconv.split(s):
        if frag == '-{':
            nested += 1
            block += frag
        elif frag == '}-':
            if not nested:
                # bogus }-
                ch.append(frag)
                continue
            block += frag
            nested -= 1
            if nested:
                continue
            newrules = []
            delim = RE_splitflag.split(block[2:-2].strip(' \t\n\r\f\v;'))
            if len(delim) == 1:
                flag = None
                mapping = RE_splitmap.split(delim[0])
            else:
                flag = RE_splitmap.split(delim[0].strip(' \t\n\r\f\v;'))
                mapping = RE_splitmap.split(delim[1])
            rule = {}
            for m in mapping:
                uni = RE_splituni.split(m)
                if len(uni) == 1:
                    pair = RE_splitpair.split(uni[0])
                else:
                    if rule:
                        newrules.append(rule)
                        rule = {':uni': uni[0]}
                    else:
                        rule[':uni'] = uni[0]
                    pair = RE_splitpair.split(uni[1])
                if len(pair) == 1:
                    rule['zh'] = convert_for_mw(pair[0], 'zh', ruledict)
                else:
                    rule[pair[0]] = convert_for_mw(pair[1], pair[0], ruledict)
            newrules.append(rule)
            if not flag:
                ch.append(fallback(locale, newrules[0]))
            elif any(ch in flag for ch in 'ATRD-HN'):
                for f in flag:
                    # A: add rule for convert code (all text convert)
                    # H: Insert a conversion rule without output
                    if f in ('A', 'H'):
                        for r in newrules:
                            if not r in rules:
                                rules.append(r)
                        if f == 'A':
                            if ':uni' in r:
                                if locale in r:
                                    ch.append(r[locale])
                                else:
                                    ch.append(convert(r[':uni'], locale))
                            else:
                                ch.append(fallback(locale, newrules[0]))
                    # -: remove convert
                    elif f == '-':
                        for r in newrules:
                            try:
                                rules.remove(r)
                            except ValueError:
                                pass
                    # D: convert description (useless)
                    #elif f == 'D':
                        #ch.append('; '.join(': '.join(x) for x in newrules[0].items()))
                    # T: title convert (useless)
                    # R: raw content (implied above)
                    # N: current variant name (useless)
                    #elif f == 'N':
                        #ch.append(locale)
                ruledict = convtable2dict(rules, locale, update)
            else:
                fblimit = frozenset(flag) & frozenset(Locales[locale])
                limitedruledict = update.copy() if update else {}
                for r in rules:
                    if ':uni' in r:
                        if locale in r:
                            limitedruledict[r[':uni']] = r[locale]
                    else:
                        v = None
                        for l in Locales[locale]:
                            if l in r and l in fblimit:
                                v = r[l]
                                break
                        for word in r.values():
                            limitedruledict[word] = v if v else convert(word, locale)
                ch.append(convert(delim[1], locale, limitedruledict))
            block = ''
        elif nested:
            block += frag
        else:
            ch.append(convert(frag, locale, ruledict))
    if nested:
        # unbalanced
        ch.append(convert_for_mw(block + '}-'*nested, locale, ruledict))
    return ''.join(ch)

def test_convert_mw(locale, update=None):
    s = ('英國-{zh:利兹;zh-hans:利兹;zh-hk:列斯;zh-tw:里茲}-大学\n'
        '-{zh-hans:计算机; zh-hant:電腦;}-\n'
        '-{H|巨集=>zh-cn:宏;}-\n'
        '测试：巨集、宏\n'
        '-{简体字繁體字}-\n'
        '北-{}-韓、北朝-{}-鲜\n'
        '-{H|zh-cn:博客; zh-hk:網誌; zh-tw:部落格;}-\n'
        '测试：博客、網誌、部落格\n'
        '-{A|zh-cn:博客; zh-hk:網誌; zh-tw:部落格;}-\n'
        '测试：博客、網誌、部落格\n'
        '-{H|zh-cn:博客; zh-hk:網誌; zh-tw:部落格;}-\n'
        '测试1：博客、網誌、部落格\n'
        '-{-|zh-cn:博客; zh-hk:網誌; zh-tw:部落格;}-\n'
        '测试2：博客、網誌、部落格\n'
        '-{T|zh-cn:汤姆·汉克斯; zh-hk:湯·漢斯; zh-tw:湯姆·漢克斯;}-\n'
        '-{D|zh-cn:汤姆·汉克斯; zh-hk:湯·漢斯; zh-tw:湯姆·漢克斯;}-\n'
        '-{H|zh-cn:博客; zh-hk:網誌; zh-tw:部落格;}-\n'
        '测试1：-{zh;zh-hans;zh-hant|博客、網誌、部落格}-\n'
        '测试2：-{zh;zh-cn;zh-hk|博客、網誌、部落格}-')
    return convert_for_mw(s, locale, update)

def main():
    """
    Simple stdin/stdout interface.
    """
    if len(sys.argv) == 2 and sys.argv[1] in Locales:
        locale = sys.argv[1]
        convertfunc = convert
    elif len(sys.argv) == 3 and sys.argv[1] == '-w' and sys.argv[2] in Locales:
        locale = sys.argv[2]
        convertfunc = convert_for_mw
    else:
        thisfile = __file__ if __name__ == '__main__' else 'python -mzhconv'
        print("usage: %s [-w] {zh-cn|zh-tw|zh-hk|zh-sg|zh-hans|zh-hant|zh} < input > output" % thisfile)
        sys.exit(1)

    loaddict()
    ln = sys.stdin.readline()
    while ln:
        l = ln.rstrip('\r\n')
        if sys.version_info[0] < 3:
            l = unicode(l, 'utf-8')
        res = convertfunc(l, locale)
        if sys.version_info[0] < 3:
            print(res.encode('utf-8'))
        else:
            print(res)
        ln = sys.stdin.readline()

if __name__ == '__main__':
    main()
