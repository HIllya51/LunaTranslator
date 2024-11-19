import os, re


def parsecode(code: str):
    # PyQt
    code = code.replace("self.screen().geometry().height()", "99999")
    code = code.replace("self.parent().devicePixelRatioF()", "1")
    code = code.replace("self.devicePixelRatioF()", "1")
    code = re.sub(
        r"(Q[a-zA-Z0-9_]+)\.[a-zA-Z0-9_]+\.([a-zA-Z0-9_]+)([ \)\n,:])", r"\1.\2\3", code
    )
    # 移除类型注解
    code = re.sub(r": [a-zA-Z0-9_]+\)", ")", code)
    code = re.sub(r"([a-zA-Z0-9_]): [a-zA-Z0-9_]+,", r"\1,", code)
    code = re.sub(r": [a-zA-Z0-9_]+ =", " =", code)
    return code


for _dir, _, _fs in os.walk("./LunaTranslator"):
    for _f in _fs:
        if not _f.endswith(".py"):
            continue
        path = os.path.normpath(os.path.abspath(os.path.join(_dir, _f)))
        with open(path, "r", encoding="utf8") as ff:
            code = ff.read()
        with open(path, "w", encoding="utf8") as ff:
            ff.write(parsecode(code))
