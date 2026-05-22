import os
from collections import defaultdict

os.chdir(os.path.dirname(__file__))
cnt = defaultdict(int)
basepath = os.getcwd()


def countfls(f: str):
    _, ext = os.path.splitext(f)
    with open(f, "r", encoding="utf8", errors="ignore") as fp:
        ll = len(fp.readlines())
        # print(ff, ll)
        cnt[ext.split(".")[-1]] += ll


def checkkeep(f):
    _, ext = os.path.splitext(f)
    return ext in (
        ".cpp",
        ".c",
        ".cc",
        ".h",
        ".hpp",
        ".cmake",
        ".py",
        ".html",
        ".css",
        ".js",
    )


def checkdir(dd, skips=None):
    __ = os.path.normpath(os.path.join(basepath, dd))
    for d, _2, fs in os.walk(__):
        if skips and any(d[len(__) + 1 :].startswith(_) for _ in skips):
            continue
        for f in fs:
            if not checkkeep(os.path.join(d, f)):
                continue
            countfls(os.path.join(d, f))


checkdir("LunaTranslator")
checkdir(
    "NativeImpl",
    (
        "build",
        "builds",
        r"LunaHook\build",
        r"LunaHook\builds",
    ),
)
# print(cnt)
cntx = defaultdict(int)
for k in cnt:
    if k in ("cpp", "c", "cc", "h", "hpp", "cmake"):
        cntx["cpp"] += cnt[k]
    else:
        cntx[k] = cnt[k]
print(cntx)
print(sum(cnt.values()))
