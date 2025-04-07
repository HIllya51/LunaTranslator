import os, re

os.chdir(os.path.dirname(__file__))


def psp():
    with open(
        "../LunaHook/engines/ppsspp/specialgames.hpp", "r", encoding="utf8"
    ) as ff:
        content = ff.read().split(" = {")[-1]
    ret = []
    for match in re.finditer(r"^		// (.*?)\n", content, re.MULTILINE):
        game = match.groups()[0]
        m = re.search("(.*?) //(.*)", game)
        if m:
            _id = m.groups()[1]
            game = m.groups()[0].strip()
        else:
            _id = " & ".join(
                re.findall('"(.*?)"', content[match.span()[1] :].split("\n")[0])
            )
        ret.append((_id, game))
    return ret


def ns():
    with open("../LunaHook/engine64/yuzu.cpp", "r", encoding="utf8") as ff:
        content = ff.read().split(" = {")[-1]
    ret = []
    for match in re.finditer(r"^            // (.*?)\n", content, re.MULTILINE):
        game = match.groups()[0]
        m = re.search(r"(.*?) //([\w\d]{16})", game)
        if m:
            _id = m.groups()[1]
            game = m.groups()[0].strip()
        else:
            _id = " & ".join(
                re.findall(
                    r"0x([\w\d]{16})ull", content[match.span()[1] :].split("\n")[0]
                )
            )
            game = game.split("//")[0].strip()

        ret.append((_id, game))
    return ret


def psv():
    with open("../LunaHook/engine64/vita3k.cpp", "r", encoding="utf8") as ff:
        content = ff.read().split(" = {")[-1]
    ret = []
    for match in re.finditer(r"^            // (.*?)\n", content, re.MULTILINE):
        game = match.groups()[0]
        m = re.search("(.*?) //(.*)", game)
        if m:
            _id = m.groups()[1]
            game = m.groups()[0].strip()
        else:
            _id = " & ".join(
                re.findall('"(.*?)"', content[match.span()[1] :].split("\n")[0])
            )
        ret.append((_id, game))
    return ret


def rpcs3():
    with open("../LunaHook/engine64/rpcs3.cpp", "r", encoding="utf8") as ff:
        content = ff.read()
    ret = []
    for match in re.finditer(r"^            // (.*?)\n", content, re.MULTILINE):
        game = match.groups()[0]
        m = re.search("(.*?) //(.*)", game)
        if m:
            _id = m.groups()[1]
            game = m.groups()[0].strip()
        else:
            _id = " & ".join(
                re.findall('"(.*?)"', content[match.span()[1] :].split("\n")[0])
            )
        ret.append((_id, game))
    return ret


def pcsx2():
    with open("../LunaHook/engine64/PCSX2.cpp", "r", encoding="utf8") as ff:
        content = ff.read()
    ret = []
    for match in re.finditer(r"^            // (.*?)\n", content, re.MULTILINE):
        game = match.groups()[0]
        m = re.search("(.*?) //(.*)", game)
        if m:
            _id = m.groups()[1]
            game = m.groups()[0].strip()
        else:
            _id = " & ".join(
                re.findall('"(.*?)"', content[match.span()[1] :].split("\n")[0])
            )
        ret.append((_id, game))
    return ret


psp = psp()
ns = ns()
psv = psv()
rpcs3 = rpcs3()
pcsx2 = pcsx2()


def maketable(lst):
    res = """
|  | ID       | Game                |
| ---- | ---------- | ------------------- |"""
    for i, (_id, game) in enumerate(lst):
        res += "\n" + f"|  | {_id} | {game} |"
    return res


for lang in ["zh", "en", "ja"]:
    with open(
        f"../../../../docs/{lang}/emugames_template.md", "r", encoding="utf8"
    ) as ff:
        temp = ff.read()

    temp = temp.replace("NS_GAME_LIST", maketable(ns))
    temp = temp.replace("PSP_GAME_LIST", maketable(psp))
    temp = temp.replace("PSV_GAME_LIST", maketable(psv))
    temp = temp.replace("PS3_GAME_LIST", maketable(rpcs3))
    temp = temp.replace("PS2_GAME_LIST", maketable(pcsx2))
    with open(f"../../../../docs/{lang}/emugames.md", "w", encoding="utf8") as ff:
        ff.write(temp)
