import re, inspect, unicodedata
from traceback import print_exc
from collections import Counter
from math import isqrt
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
    return "" if lrucache.test(line) else line


def _2_f(line, args):
    rept_len = args["重复次数(若为1则自动分析去重)"]
    fit_rept = args["保持非重复字符"]

    if rept_len == 1:
        # record length of each repeating unit
        hist = Counter({0:-1})  # placeholder
        step, char = 0, 0
        for c in line:
            if c != char:  # found one repeating unit
                hist[step] += 1
                step, char = 0, c
            step += 1
        # last repeating unit
        hist[step] += 1

        # length of the most common repeating unit
        ncnt, mcnt = hist.pop(1, 0), max(hist.values())
        rept_len = min(k for k,v in hist.items() if v == mcnt) if (ncnt <= mcnt) else 1

    if fit_rept:
        result = ""
        idx = 0
        while idx < len(line):
            result += line[idx]
            sect = line[idx : idx + rept_len]
            idx += rept_len if (len(sect) == rept_len * len(set(sect))) else 1
    else:
        result = "".join(line[idx] for idx in range(0, len(line), rept_len))
    return result


def _3_f(line, args):
    rept_cnt = args["重复次数(若为1则自动分析去重)"]

    if rept_cnt >= 2:
        return line[: len(line) // rept_cnt]

    # string doubling trick
    idx = (line + line).find(line, 1, -1)
    result = line[:idx] if idx != -1 else line
    return result


def _3_2(line):
    result = ""
    idx = 0
    while idx < len(line):
        # try to find the longest repeating unit
        for length in range((len(line) - idx) // 2, 0, -1):
            unit = line[idx : idx + length]
            repts = 1
            while line[idx + repts * length : idx + (repts + 1) * length] == unit:
                repts += 1
            if repts > 1:   # found repetition
                result += unit
                idx += repts * length
                break
        else:   # no repetition, copy one char
            result += line[idx]
            idx += 1
    return result


def _10_f(line: str):
    # math trick with a strong assumption
    length = isqrt(len(line) * 2)
    result = line[:length] if (length * (length + 1) == len(line) * 2) else line
    return result


def _13_f(line: str):  # 递增式
    # math trick with a strong assumption
    length = isqrt(len(line) * 2)
    result = line[-length:] if (length * (length + 1) == len(line) * 2) else line
    return result


def _13_fEX(line: str):
    result = ""
    idx = 0
    while idx < len(line):
        # try to find the longest parttern unit
        for length in range(isqrt((len(line) - idx) * 2), 0, -1):
            sect = line[idx : idx + length * (length + 1) // 2]
            unit = sect[-length:]
            # match parttern
            if "".join(unit[: k - length] for k in range(length)) == sect[:-length]:
                result += unit
                idx += length * (length + 1) // 2
                break
        else:   # no parttern, copy one char
            result += line[idx]
            idx += 1
    return result


def _1_f(line):
    # line = re.sub(r"\{(\w+)(.*?)\}(.*?)\{\/\1\}", r"\3", line)    # redundant
    line = re.sub(r"\{([^}]*?)[:/](.*?)\}", r"\1", line)
    line = re.sub(r"\{.*?\}", r"", line)
    return line


def _4_f(line):
    line = re.sub("<(.*?)>", "", line)
    # line = re.sub("</(.*?)>", "*", line)  # no effect
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


def stringreplace(line, args: "dict[str, list]"):
    filters = args["internal"].copy()
    if args.get("merge", False):
        filters += postprocessconfig["stringreplace"]["args"]["internal"]
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
    newline = []
    for char in line:
        try:
            char.encode("shiftjis")
            newline.append(char)
        except:
            pass
    return "".join(newline)


def _remove_symbo(line):

    return "".join(r for r in line if not is_ascii_symbo(r))


def _remove_control(line):
    return "".join(r for r in line if not is_ascii_control(r))


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


def fulltohalf(text: str, args: dict) -> str:
    return unicodedata.normalize(args.get("type", "NFKC"), text)


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
    "fulltohalf": fulltohalf,
}

for k in postprocessconfig:
    if k not in globalconfig["postprocess_rank"]:
        globalconfig["postprocess_rank"].append(k)
_bads = []
for _ in globalconfig["postprocess_rank"]:
    if _ not in processfunctions:
        _bads.append(_)
for _ in _bads:
    globalconfig["postprocess_rank"].remove(_)


def POSTSOLVE(line: str, isEx=False, isFromHook=False, useAll=False, skippreprocess=False) -> str:
    if skippreprocess:
        return line
    if not line:
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
                    line = processfunctions[postitem](
                        line, gobject.getconfig(usemypostpath), usemodule
                    )
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
