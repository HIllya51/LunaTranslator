import os
import sys, hashlib
from build_lunatranslator import buildPlugins

arch = sys.argv[1]
target = sys.argv[2]
if target == "winxp":
    # xp版先不做
    exit()


def getpyfiles():
    res = {}
    for _dir, _, _fs in os.walk("./LunaTranslator"):
        for _f in _fs:
            if not _f.endswith(".py"):
                continue
            path = os.path.normpath(os.path.join(_dir, _f))
            with open(path, "rb") as ff:
                code = ff.read()
            hs = hashlib.sha512(code).hexdigest()
            res[path.replace("\\", "/")] = hs
    s = ""
    for k, v in res.items():
        s += '{L"' + k + '", {parse_hex_string("' + v + '")}},'
    return s


def getpefiles():
    # 获取dll/exe
    return ""


def buildexe(arch, target):
    pys = getpyfiles()
    pes = getpefiles()

    path = r"NativeImpl\exec\checksigs.hpp"
    with open(path, "r", encoding="utf8") as ff:
        code = ff.read()
    with open(path, "w", encoding="utf8") as ff:
        code = code.replace("CHECK_DIGEST_LIST", "\n" + pys).replace(
            "CHECK_CERT_LIST", "\n" + pes
        )
        ff.write(code)
    buildPlugins(arch, target, " -DBUILD_EXEC_ONLY=ON")


buildexe(arch, target)
