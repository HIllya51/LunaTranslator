import os
from collections import defaultdict

os.chdir(os.path.dirname(__file__))
cnt = defaultdict(int)
basepath = os.getcwd()


def countfls(f):
    _, ext = os.path.splitext(f)
    with open(f, "r", encoding="utf8", errors="ignore") as fp:
        ll = len(fp.readlines())
        # print(ff, ll)
        cnt[ext] += ll


def checkskip(f):
    _, ext = os.path.splitext(f)
    return ext in (".pyc", ".ico", ".zip", ".7z", ".json")


def checkdir(dd, skips=None):
    __ = os.path.normpath(os.path.join(basepath, dd))
    for d, _2, fs in os.walk(__):
        if skips and any(d[len(__) + 1 :].startswith(_) for _ in skips):
            continue
        for f in fs:
            if checkskip(f):
                continue
            countfls(os.path.join(d, f))


checkdir("LunaTranslator")
checkdir(r"files\html")
checkdir(
    "cpp",
    (
        "libs\\",
        "build",
        "builds",
        r"wcocr\wechat-ocr",
        r"LunaHook\build",
        r"LunaHook\builds",
        r"LunaHook\LunaHost\GUI\Plugin\extensions",
    ),
)
print(cnt)
print(sum(cnt.values()))
