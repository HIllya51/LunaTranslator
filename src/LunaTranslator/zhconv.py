import json

_DEFAULT_DICT = "files/static/zhcdict.json"
DICTIONARY = _DEFAULT_DICT

zhcdicts = None
dict_zhcn = None
dict_zhsg = None
dict_zhtw = None
dict_zhhk = None
dict_zhhans = None
dict_zhhant = None
pfsdict = {}


def loaddict(filename=DICTIONARY):
    """
    Load the dictionary from a specific JSON file.
    """
    global zhcdicts
    if zhcdicts:
        return
    if filename == _DEFAULT_DICT:
        zhcdicts = json.loads(open(filename, "rb").read().decode("utf-8"))
    else:
        with open(filename, "rb") as f:
            zhcdicts = json.loads(f.read().decode("utf-8"))


def getdict(locale):
    """
    Generate or get convertion dict cache for certain locale.
    Dictionaries are loaded on demand.
    """
    global zhcdicts, dict_zhcn, dict_zhsg, dict_zhtw, dict_zhhk, dict_zhhans, dict_zhhant, pfsdict
    if zhcdicts is None:
        loaddict(DICTIONARY)
    if locale == "zh-cn":
        if dict_zhcn:
            got = dict_zhcn
        else:
            dict_zhcn = zhcdicts["zh2Hans"].copy()
            dict_zhcn.update(zhcdicts["zh2CN"])
            got = dict_zhcn
    elif locale == "zh-tw":
        if dict_zhtw:
            got = dict_zhtw
        else:
            dict_zhtw = zhcdicts["zh2Hant"].copy()
            dict_zhtw.update(zhcdicts["zh2TW"])
            got = dict_zhtw
    elif locale == "zh-hans":
        if dict_zhhans:
            got = dict_zhhans
        else:
            dict_zhhans = zhcdicts["zh2Hans"].copy()
            got = dict_zhhans
    elif locale == "zh-hant":
        if dict_zhhant:
            got = dict_zhhant
        else:
            dict_zhhant = zhcdicts["zh2Hant"].copy()
            got = dict_zhhant

    if locale not in pfsdict:
        pfsdict[locale] = getpfset(got)
    return got


def getpfset(convdict):
    pfset = []
    for word in convdict:
        for ch in range(len(word)):
            pfset.append(word[: ch + 1])
    return frozenset(pfset)


def convert(s, locale):
    zhdict = getdict(locale)
    pfset = pfsdict[locale]
    newset = set()

    ch = []
    N = len(s)
    pos = 0
    while pos < N:
        i = pos
        frag = s[pos]
        maxword = None
        maxpos = 0
        while i < N and (frag in pfset or frag in newset):
            if frag in zhdict:
                maxword = zhdict[frag]
                maxpos = i
            i += 1
            frag = s[pos : i + 1]
        if maxword is None:
            maxword = s[pos]
            pos += 1
        else:
            pos = maxpos + 1
        ch.append(maxword)
    return "".join(ch)
