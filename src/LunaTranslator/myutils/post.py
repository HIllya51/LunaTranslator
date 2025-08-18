import re, inspect
from traceback import print_exc
from collections import Counter
import gobject
from myutils.utils import (
    checkmd5reloadmodule,
    LRUCache,
    getlangsrc,
    parsemayberegexreplace,
    safe_escape,
    is_ascii_symbo,
    is_ascii_control,
)
from myutils.config import postprocessconfig, globalconfig, savehook_new_data

lrucache = LRUCache(0)


def dedump(line, args):
    size = args["cachesize"]
    lrucache.setcap(size)
    if lrucache.test(line):
        return ""
    else:
        return line


def _2_f(line, args):
    if len(line) == 0:
        return
    keepnodump = args["保持非重复字符"]
    times = args["重复次数(若为1则自动分析去重)"]

    if times >= 2:
        guesstimes = times
    else:
        dumptime = Counter()
        cntx = 1
        lastc = None
        for c in list(line) + [0]:
            if c != lastc:
                dumptime[cntx] += 1
                lastc = c
                cntx = 1
            else:
                cntx += 1
        _max = max(dumptime.values())
        xx = []
        for _, _2 in dumptime.items():
            if _2 == _max:
                xx.append(_)

        guesstimes = sorted(xx)
        if guesstimes[0] == 1 and len(guesstimes) > 1:
            guesstimes = guesstimes[1:]
        guesstimes = guesstimes[0]
    if keepnodump:
        newline = ""
        i = 0
        while i < len(line):
            newline += line[i]
            nextn = line[i : i + guesstimes]
            # print(guesstimes,nextn,len(set(nextn)))
            if len(nextn) == guesstimes and len(set(nextn)) == 1:
                i += guesstimes
            else:
                i += 1
        line = newline
    else:
        newline = [line[i * guesstimes] for i in range(len(line) // guesstimes)]
        line = "".join(newline)
    return line


def _3_f(line, args):
    times = args["重复次数(若为1则自动分析去重)"]

    if times >= 2:
        guesstimes = times
    else:
        guesstimes = len(line)
        while guesstimes >= 1:
            if line[: len(line) // guesstimes] * guesstimes == line:
                break
            guesstimes -= 1
    line = line[: len(line) // guesstimes]
    return line


def _3_2(line):
    cache = ""

    while len(line):
        last = None
        dumplength = len(line) // 2
        while dumplength > 1:
            bad = False
            for i in range(dumplength):
                _i = i + dumplength
                if line[i] != line[_i]:
                    bad = True
                    break
            if bad:
                dumplength -= 1
            else:
                current = line[:dumplength]
                if last and last != current:
                    cache += current
                last = current
                line = line[dumplength:]
                break
        if last is None:
            cache += line[0]
            line = line[1:]

    return cache


def _10_f(line: str):
    cnt = Counter(line)
    saveline = []
    for k in sorted(cnt.keys(), key=lambda x: -cnt[x]):
        last = line.rfind(k)

        length = 1
        while True:
            if last - length < 0:
                break

            if line[last] == line[last - length]:
                last = last - length
            if last - length > 0:
                length += 1
            else:
                break
        saveline.append(line[last - length : last + 1])

    line = sorted(saveline, key=len, reverse=True)[0]
    return line


def _13_f(line: str):  # 递增式
    cnt = Counter(line)
    saveline = []
    for k in sorted(cnt.keys(), key=lambda x: -cnt[x]):

        first = line.find(k)
        length = 1
        while True:
            if first + length >= len(line):
                break

            if line[first] == line[first + length]:
                first += length
            if first + length < len(line):

                length += 1
            else:
                break
        saveline.append(line[first : first + length])

    line = sorted(saveline, key=len, reverse=True)[0]
    return line


def _13_fEX(line: str):
    saves = []
    while len(line):
        for i in range(len(line)):
            maxlongline = line[i:]
            shengyu = line
            _maxlong = maxlongline
            succ = True
            while len(_maxlong):
                if shengyu.endswith(_maxlong) == False:
                    succ = False
                    break
                shengyu = shengyu[: -len(_maxlong)]
                _maxlong = _maxlong[:-1]
            if succ:
                break
        saves.append(maxlongline)
        line = line[: -((len(maxlongline) * (1 + len(maxlongline)))) // 2]
    return "".join(reversed(saves))


def _1_f(line):
    line = re.sub(r"\{(\w+)(.*?)\}(.*?)\{\/\1\}", r"\3", line)
    line = re.sub(r"\{([^}]?)[:/](.*?)\}", r"\1", line)
    line = re.sub(r"\{.*?\}", r"", line)
    return line


def _4_f(line):
    line = re.sub("<(.*?)>", "", line)
    line = re.sub("</(.*?)>", "*", line)
    return line


def _6_fEX(line: str):
    white = getlangsrc().space
    line = white.join(sec for sec in line.splitlines() if sec)
    return line


def _91_f(line):
    line = re.sub("([0-9]+)", "", line)
    return line


def _92_f(line):
    line = re.sub("([a-zA-Z]+)", "", line)
    return line


def stringreplace(line, args):
    filters = args["internal"]
    return parsemayberegexreplace(filters, line)


def _7_zhuanyi_f(line: str, args):
    filters = args["替换内容"]
    for fil in filters:
        if fil == "":
            continue
        else:
            line = line.replace(safe_escape(fil), safe_escape(filters[fil]))
    return line


def _7_f(line: str, args):
    filters = args["替换内容"]
    for fil in filters:
        if fil == "":
            continue
        else:
            line = line.replace(fil, filters[fil])
    return line


def _8_f(line, args):
    filters = args["替换内容"]
    for fil in filters:
        if fil == "":
            continue
        else:
            try:
                line = re.sub(safe_escape(fil), safe_escape(filters[fil]), line)
            except:
                print_exc()
    return line


def _remove_non_shiftjis_char(line: str):
    newline = ""
    for char in line:
        try:
            char.encode("shiftjis")
            newline += char
        except:
            pass
    return newline


def _remove_symbo(line):

    newline = ""
    for r in line:
        if is_ascii_symbo(r):
            continue
        newline += r
    return newline


def _remove_control(line):
    newline = ""
    for r in line:
        if is_ascii_control(r):
            continue
        newline += r
    return newline


def _remove_not_in_ja_bracket(line: str):
    if "「" in line and "」" in line:
        _1 = line.index("「")
        _2 = line.rindex("」")
        if _1 < _2:
            return line[_1 : _2 + 1]
    return line


def lines_threshold(line: str, args: dict):
    sps = line.splitlines()
    if len(sps) >= abs(args["maxzishu"]):
        if args.get("cut_reverse", True):
            return "\n".join(sps[-args["maxzishu"] :])
        else:
            return "\n".join(sps[: args["maxzishu"]])
    return line


def _mypostloader(line, file, module):

    _ = checkmd5reloadmodule(file, module)
    # 这个是单独函数的模块，不需要用isnew来判断是否需要重新初始化
    if not _:
        return line
    return _.POSTSOLVE(line)


processfunctions = {
    "_remove_symbo": _remove_symbo,
    "_2": _2_f,
    "_3": _3_f,
    "_3_2": _3_2,
    "_10": _10_f,
    "_1": _1_f,
    "_4": _4_f,
    "_6": _6_fEX,  # 废弃，重定向到新的实现
    "_6EX": _6_fEX,
    "_91": _91_f,
    "_92": _92_f,
    "_7": _7_f,  # depracated
    "_8": _8_f,  # depracated
    "_13": _13_f,  # depracated
    "_13EX": _13_fEX,
    "_7_zhuanyi": _7_zhuanyi_f,  # depracated
    "_remove_non_shiftjis_char": _remove_non_shiftjis_char,
    "_remove_control": _remove_control,
    # "_remove_chaos": _remove_chaos,
    "_remove_not_in_ja_bracket": _remove_not_in_ja_bracket,
    "dedump": dedump,  # depracated
    "lines_threshold_1": lines_threshold,
    "_11": _mypostloader,
    "stringreplace": stringreplace,
}


def POSTSOLVE(line, isEx=False, isFromHook=False, useAll=False):
    if line == "":
        return ""
    useranklist = globalconfig["postprocess_rank"]
    usedpostprocessconfig = postprocessconfig
    usemypostpath = "mypost.py"
    usemodule = "mypost"
    try:

        gameuid = gobject.base.gameuid
        if gameuid and not savehook_new_data[gameuid].get(
            "textproc_follow_default", True
        ):
            useranklist = savehook_new_data[gameuid]["save_text_process_info"]["rank"]
            usedpostprocessconfig = savehook_new_data[gameuid][
                "save_text_process_info"
            ]["postprocessconfig"]
            if savehook_new_data[gameuid]["save_text_process_info"].get("mypost", None):
                usemodule = (
                    "posts."
                    + savehook_new_data[gameuid]["save_text_process_info"]["mypost"]
                )
                usemypostpath = "posts/{}.py".format(
                    savehook_new_data[gameuid]["save_text_process_info"]["mypost"]
                )
    except:
        print_exc()
    for postitem in useranklist:
        if postitem not in processfunctions:
            continue
        if postitem not in usedpostprocessconfig:
            continue
        if usedpostprocessconfig[postitem]["use"]:
            if not useAll:
                if isEx and not (usedpostprocessconfig[postitem].get("isExUse", False)):
                    continue
                if (not isFromHook) and (
                    usedpostprocessconfig[postitem].get("isHookOnly", False)
                ):
                    continue
            try:
                _f = processfunctions[postitem]
                if postitem == "_11":
                    line = processfunctions[postitem](line, gobject.getconfig(usemypostpath), usemodule)
                else:
                    sig = inspect.signature(_f)
                    np = len(sig.parameters)
                    if np == 1:
                        line = processfunctions[postitem](line)
                    elif np == 2:
                        line = processfunctions[postitem](
                            line, usedpostprocessconfig[postitem].get("args", {})
                        )
                    else:
                        raise Exception("unsupported parameters num")

            except:
                print_exc()
    return line
