import re, inspect, unicodedata
from traceback import print_exc
from collections import Counter
import gobject
import math
from myutils.utils import (
    checkmd5reloadmodule,
    LRUCache,
    getlangsrc,
    parsemayberegexreplace,
    safe_escape,
    is_ascii_symbol,
    is_ascii_control,
)
from myutils.config import postprocessconfig, globalconfig, savehook_new_data

lrucache = LRUCache(0)


def isqrt(n):
    return int(math.sqrt(n))


def dedup_by_cache(line: str, args: dict) -> str:
    size = args["cachesize"]
    lrucache.setcap(size)
    return "" if lrucache.test(line) else line


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
        newline = []
        i = 0
        while i < len(line):
            newline.append(line[i])
            nextn = line[i : i + guesstimes]
            # print(guesstimes,nextn,len(set(nextn)))
            if len(nextn) == guesstimes and len(set(nextn)) == 1:
                i += guesstimes
            else:
                i += 1
        line = "".join(newline)
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
    cache = []

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
                    cache.append(current)
                last = current
                line = line[dumplength:]
                break
        if last is None:
            cache.append(line[0])
            line = line[1:]

    return "".join(cache)


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


def remove_braces(line: str) -> str:
    line = re.sub(r"\{(\w+)(.*?)\}(.*?)\{\/\1\}", r"\3", line)
    line = re.sub(r"\{([^}]*?)[:/](.*?)\}", r"\1", line)
    line = re.sub(r"\{.*?\}", r"", line)
    return line


def remove_angle_brackets(line: str) -> str:
    line = re.sub(r"<(.*?)>", r"", line)
    return line


def remove_line_breaks(line: str) -> str:
    ws = getlangsrc().space
    line = ws.join(sect for sect in line.splitlines() if sect)
    return line


def remove_digits(line: str) -> str:
    line = re.sub(r"([0-9]+)", r"", line)
    return line


def remove_alphabets(line: str) -> str:
    line = re.sub(r"([a-zA-Z]+)", r"", line)
    return line


def string_replace(line: str, args: "dict[str, list]") -> str:
    filters = args["internal"].copy()
    if args.get("merge", False):
        filters += postprocessconfig["stringreplace"]["args"]["internal"]
    return parsemayberegexreplace(filters, line)


def legacy_string_replace_with_escape(line: str, args: dict) -> str:
    filters = args["替换内容"]
    for fil in filters:
        if fil:
            line = line.replace(safe_escape(fil), safe_escape(filters[fil]))
    return line


def legacy_string_replace(line: str, args: dict) -> str:
    filters = args["替换内容"]
    for fil in filters:
        if fil:
            line = line.replace(fil, filters[fil])
    return line


def legacy_regex_replace(line: str, args: dict) -> str:
    filters = args["替换内容"]
    for fil in filters:
        if fil:
            try:
                line = re.sub(safe_escape(fil), safe_escape(filters[fil]), line)
            except:
                print_exc()
    return line


def _remove_non_shiftjis_char(line: str) -> str:
    return line.encode("shift-jis", "ignore").decode("shift-jis")


def _remove_symbol(line: str) -> str:
    return "".join(r for r in line if not is_ascii_symbol(r))


def _remove_control(line: str) -> str:
    return "".join(r for r in line if not is_ascii_control(r))


def _remove_not_in_ja_bracket(line: str) -> str:
    sections = re.findall(r"「[^」]*」", line)
    return "".join(sections) if sections else line


def slice_lines(line: str, args: dict) -> str:
    max_lines = args["maxzishu"]
    splits = line.splitlines()
    if len(splits) > abs(max_lines):
        reverse = args.get("cut_reverse", True)
        splits = splits[-max_lines:] if reverse else splits[:max_lines]
        return "\n".join(splits)  # ambiguous result when max_lines==0
    return line


def _mypost_process(line: str, file: str, module: str) -> str:
    mod = checkmd5reloadmodule(file, module)
    # 这个是单独函数的模块，不需要用isnew来判断是否需要重新初始化
    return mod.POSTSOLVE(line) if mod else line


def unicode_normalization(text: str, args: dict) -> str:
    return unicodedata.normalize(args.get("type", "NFKC"), text)


processfunctions = {
    "_remove_symbo": _remove_symbol,
    "_2": _2_f,
    "_3": _3_f,
    "_3_2": _3_2,
    "_10": _10_f,
    "_1": remove_braces,
    "_4": remove_angle_brackets,
    "_6": remove_line_breaks,  # 废弃，重定向到新的实现
    "_6EX": remove_line_breaks,
    "_91": remove_digits,
    "_92": remove_alphabets,
    "_7": legacy_string_replace,  # depracated
    "_8": legacy_regex_replace,  # depracated
    "_13": _13_f,  # depracated
    "_13EX": _13_fEX,
    "_7_zhuanyi": legacy_string_replace_with_escape,  # depracated
    "_remove_non_shiftjis_char": _remove_non_shiftjis_char,
    "_remove_control": _remove_control,
    # "_remove_chaos": _remove_chaos,
    "_remove_not_in_ja_bracket": _remove_not_in_ja_bracket,
    "dedump": dedup_by_cache,  # depracated
    "lines_threshold_1": slice_lines,
    "_11": _mypost_process,
    "stringreplace": string_replace,
    "fulltohalf": unicode_normalization,
}

globalconfig["postprocess_rank"] = [
    key for key in globalconfig["postprocess_rank"] if key in processfunctions.keys()
]
globalconfig["postprocess_rank"].extend(
    processfunctions.keys() - set(globalconfig["postprocess_rank"])
)


def POSTSOLVE(
    line: str, isEx=False, isFromHook=False, useAll=False, skippreprocess=False
) -> str:
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
            textprocinfo = savehook_new_data[gameuid]["save_text_process_info"]
            useranklist = textprocinfo["rank"]
            usedpostprocessconfig = textprocinfo["postprocessconfig"]
            if textprocinfo.get("mypost", None):
                usemodule = "posts." + textprocinfo["mypost"]
                usemypostpath = "posts/{}.py".format(textprocinfo["mypost"])
    except:
        print_exc()

    for postitem in useranklist:
        if postitem not in processfunctions:
            continue
        if postitem not in usedpostprocessconfig:
            continue

        config = usedpostprocessconfig[postitem]
        if not config["use"]:
            continue
        if not useAll and isEx and not config.get("isExUse", False):
            continue
        if not useAll and not isFromHook and config.get("isHookOnly", False):
            continue

        try:
            _f = processfunctions[postitem]
            sig = inspect.signature(_f)
            np = len(sig.parameters)

            if postitem == "_11":
                line = _f(line, gobject.getconfig(usemypostpath), usemodule)
            elif np == 1:
                line = _f(line)
            elif np == 2:
                line = _f(line, config.get("args", {}))
            else:
                raise Exception("unsupported parameters num")
        except:
            print_exc()
    return line
