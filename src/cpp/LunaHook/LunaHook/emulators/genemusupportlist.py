import os, re

os.chdir(os.path.dirname(__file__))


def psp():
    with open("ppsspp_1.cpp", "r", encoding="utf8") as ff:
        content = ff.read().split(" = {")[-1]
    ret = []
    for match in re.finditer(r"^    // (.*?)\n", content, re.MULTILINE):
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
    with open("yuzu_1.cpp", "r", encoding="utf8") as ff:
        content = ff.read().split(" = {")[-1]
    content = content[: content.find("};")]
    ret = []
    for match in re.finditer(r"^    // (.*?)\n", content, re.MULTILINE):
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
    with open("vita3k_1.cpp", "r", encoding="utf8") as ff:
        content = ff.read().split(" = {")[-1]
    ret = []
    for match in re.finditer(r"^    // (.*?)\n", content, re.MULTILINE):
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
    with open("rpcs3.cpp", "r", encoding="utf8") as ff:
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
    with open("PCSX2_1.cpp", "r", encoding="utf8") as ff:
        content = ff.read()
    ret = []
    for match in re.finditer(r"^    // (.*?)\n", content, re.MULTILINE):
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


append = r"""
| - | - |
| NS | yuzu(&ge;1616), [sudachi](https://github.com/emuplace/sudachi.emuplace.app), [Citron](https://git.citron-emu.org/Citron/Citron), [Eden](https://git.eden-emu.dev/eden-emu/eden) |
| PSP | [PPSSPP](https://github.com/hrydgard/ppsspp) &ge;v1.15.0 |
| PSV | [Vita3K](https://github.com/Vita3K/Vita3K) &ge;v0.1.9.3339 |
| PS2 | [PCSX2](https://github.com/PCSX2/pcsx2) &ge;v1.7.4473 |
<!-- | PS3 | [RPCS3](https://github.com/RPCS3/rpcs3) |-->
:::

::: tabs

== NS

NS_GAME_LIST

== PSP

PSP_GAME_LIST

== PSV

PSV_GAME_LIST

== PS2

PS2_GAME_LIST

:::"""

for lang in ["zh", "en", "ja", "vi"]:
    with open(
        f"../../../../../docs/{lang}/emugames_template.md", "r", encoding="utf8"
    ) as ff:
        temp = ff.read()

    append = append.replace("NS_GAME_LIST", maketable(ns))
    append = append.replace("PSP_GAME_LIST", maketable(psp))
    append = append.replace("PSV_GAME_LIST", maketable(psv))
    append = append.replace("PS3_GAME_LIST", maketable(rpcs3))
    append = append.replace("PS2_GAME_LIST", maketable(pcsx2))
    with open(f"../../../../../docs/{lang}/emugames.md", "w", encoding="utf8") as ff:
        ff.write(temp + append)
