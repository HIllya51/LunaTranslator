import sys, os, json
import rapidfuzz

os.chdir(os.path.dirname(__file__))
root = os.getcwd()

os.chdir(r"..\src")
sys.path.append("LunaTranslator")
from myutils.config import _TR, globalconfig


with open(
    r"..\src\LunaTranslator\defaultconfig\config.json", "r", encoding="utf8"
) as ff:
    js = json.load(ff)
    buttons = js["toolbutton"]["buttons"]
    fastkeys = js["quick_setting"]["all"]

with open(
    r"..\src\LunaTranslator\defaultconfig\postprocessconfig.json", "r", encoding="utf8"
) as ff:
    postprocessconfig = json.load(ff)


with open(
    r"..\src\LunaTranslator\defaultconfig\static_data.json", "r", encoding="utf8"
) as ff:
    transoptimi = json.load(ff)["transoptimi"]


def parsewhich(md, getk, starter="1. ####"):

    newlines = []
    with open(root + "/" + r"zh/" + md, "r", encoding="utf8") as ff:
        ls = ff.read().splitlines()

    saveinfo = []
    savename = []
    savel = []

    for l in ls:
        if not l.startswith(starter.strip() + " "):
            newlines.append(l)
            continue
        l = l.split("{#")[0].strip()
        name = l.split("</i>")[-1].strip()
        name = name.split("#")[-1].strip()
        usek, usename = getk(name)
        l = l.split(name)[0]
        savel.append(l)
        l += _TR(usename)
        l += " {#anchor-" + usek + "}"
        saveinfo.append(usek)
        newlines.append(l)
        savename.append(usename)

    with open(root + "/" + r"zh/" + md, "w", encoding="utf8") as ff:
        ff.write("\n".join(newlines))

    for lang in os.listdir(root):
        if not os.path.exists(root + "/" + lang + "/" + md):
            continue
        print(lang + "/" + md)
        newlines.clear()
        with open(root + "/" + lang + "/" + md, "r", encoding="utf8") as ff:
            ls = ff.read().splitlines()
        globalconfig["languageuse2"] = lang
        i = 0
        for l in ls:
            if not l.startswith(starter.strip() + " "):
                newlines.append(l)
                continue
            l = savel[i]
            l += _TR(savename[i])
            l += " {#anchor-" + saveinfo[i] + "}"
            i += 1
            newlines.append(l)
        if i != len(saveinfo):
            raise Exception(lang + "/" + md)
        with open(root + "/" + lang + "/" + md, "w", encoding="utf8") as ff:
            ff.write("\n".join(newlines))


def getkbuttons(name):
    mindis = 999
    usek = None
    for k in buttons:
        dis = rapidfuzz.distance.Levenshtein.distance(buttons[k]["tip"], name)
        if dis < mindis:
            mindis = dis
            usek = k
            usename = buttons[k]["tip"]
    return usek, usename


def getktextprocess(name):
    mindis = 999
    usek = None
    for k in postprocessconfig:
        dis = rapidfuzz.distance.Levenshtein.distance(
            postprocessconfig[k]["name"], name
        )
        if dis < mindis:
            mindis = dis
            usek = k
            usename = postprocessconfig[k]["name"]
    return usek, usename


def gettransoptimik(name):
    mindis = 999
    usek = None
    for d in transoptimi:
        dis = rapidfuzz.distance.Levenshtein.distance(d["visname"], name)
        if dis < mindis:
            mindis = dis
            usek = d["name"]
            usename = d["visname"]
    return usek, usename


def getfk(name):
    mindis = 999
    usek = None
    for k in fastkeys:
        dis = rapidfuzz.distance.Levenshtein.distance(fastkeys[k]["name"], name)
        if dis < mindis:
            mindis = dis
            usek = k
            usename = fastkeys[k]["name"]
    return usek, usename


parsewhich("alltoolbuttons.md", getkbuttons)
parsewhich("textprocess.md", getktextprocess)
parsewhich("fastkeys.md", getfk)
parsewhich("transoptimi.md", gettransoptimik, "1. ##")
