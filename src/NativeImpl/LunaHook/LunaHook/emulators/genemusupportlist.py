import os, re
from collections import defaultdict

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


def extract_game_info_robust(cpp_code):
    result = defaultdict(list)
    game_positions = []
    for match in re.finditer(r"//\s*([^\n]+?)$", cpp_code, re.MULTILINE):
        game_name = match.group(1).strip()
        start_pos = match.end()
        next_comment = re.search(r"//", cpp_code[start_pos:])
        if next_comment:
            end_pos = start_pos + next_comment.start()
        else:
            end_pos = len(cpp_code)

        game_positions.append((game_name, start_pos, end_pos))
    for game_name, start, end in game_positions:
        section = cpp_code[start:end]
        ids = re.findall(r'"(\w+)"', section)
        vector_ids = re.findall(r"vector<[^>]+>\s*\{([^}]+)\}", section)
        for vector_section in vector_ids:
            ids.extend(re.findall(r'"([^"]+)"', vector_section))
        if ids:
            result[game_name] = list(dict.fromkeys(ids))
    return dict(result)


def rpcs3():
    with open("rpcs3_1.cpp", "r", encoding="utf8") as ff:
        content = ff.read()
    ret = []
    for name, ids in extract_game_info_robust(content).items():
        _id = " & ".join(ids)
        ret.append((_id, name))
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
    res = """|  | ID       | Game                |
| ---- | ---------- | ------------------- |"""
    for i, (_id, game) in enumerate(lst):
        res += "\n" + f"|  | {_id} | {game} |"
    return res


for k, f in (("ns", ns), ("psp", psp), ("ps2", pcsx2), ("psv", psv), ("ps3", rpcs3)):
    with open(f"../../../../../docs/emusupportlist/{k}.md", "w", encoding="utf8") as ff:
        ff.write(maketable(f))
