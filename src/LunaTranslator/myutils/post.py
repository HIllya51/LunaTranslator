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
    is_ascii_symbol,
    is_ascii_control,
)
from myutils.config import postprocessconfig, globalconfig, savehook_new_data

lrucache = LRUCache(0)


def dedup_by_cache(line: str, args: dict) -> str:
    size = args["cachesize"]
    lrucache.setcap(size)
    return "" if lrucache.test(line) else line


def dedup_char(line: str, args: dict) -> str:
    """AAABBBCCC -> ABC"""

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


def dedup_string(line: str, args: dict) -> str:
    """ABCDABCDABCD -> ABCD"""

    rept_cnt = args["重复次数(若为1则自动分析去重)"]

    if rept_cnt >= 2:
        return line[: len(line) // rept_cnt]

    # string doubling trick
    idx = (line + line).find(line, 1, -1)
    result = line[:idx] if idx != -1 else line
    return result


def dedup_multi_string(line: str) -> str:
    """S1S1S1S2S2S3S3S3 -> S1S2S3"""

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


def dedup_decreasing_string(line: str) -> str:
    """ABCDBCDCDD -> ABCD"""

    # math trick with a strong assumption
    length = isqrt(len(line) * 2)
    result = line[:length] if (length * (length + 1) == len(line) * 2) else line
    return result


def dedup_increasing_string(line: str) -> str:
    """AABABCABCD -> ABCD"""

    # math trick with a strong assumption
    length = isqrt(len(line) * 2)
    result = line[-length:] if (length * (length + 1) == len(line) * 2) else line
    return result


def dedup_multi_increasing_string(line: str) -> str:
    """AABABCABCDXXYXYZ -> ABCDXYZ"""

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


def remove_braces(line: str) -> str:
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
    if len(splits) > max_lines:
        reverse = args.get("cut_reverse", True)
        splits = splits[-max_lines:] if reverse else splits[:max_lines]
        return "\n".join(splits)
    return line


def _mypost_process(line: str, file: str, module: str) -> str:
    mod = checkmd5reloadmodule(file, module)
    # 这个是单独函数的模块，不需要用isnew来判断是否需要重新初始化
    return mod.POSTSOLVE(line) if mod else line


def unicode_normalization(text: str, args: dict) -> str:
    return unicodedata.normalize(args.get("type", "NFKC"), text)


processfunctions = {
    "_remove_symbo": _remove_symbol,
    "_2": dedup_char,
    "_3": dedup_string,
    "_3_2": dedup_multi_string,
    "_10": dedup_decreasing_string,
    "_1": remove_braces,
    "_4": remove_angle_brackets,
    "_6": remove_line_breaks,  # 废弃，重定向到新的实现
    "_6EX": remove_line_breaks,
    "_91": remove_digits,
    "_92": remove_alphabets,
    "_7": legacy_string_replace,  # depracated
    "_8": legacy_regex_replace,  # depracated
    "_13": dedup_increasing_string,  # depracated
    "_13EX": dedup_multi_increasing_string,
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
    key for key in globalconfig["postprocess_rank"]
    if key in processfunctions.keys()
]
globalconfig["postprocess_rank"].extend(
    processfunctions.keys() - set(globalconfig["postprocess_rank"])
)


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
