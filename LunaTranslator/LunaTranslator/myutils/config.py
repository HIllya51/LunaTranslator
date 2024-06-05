import json
import os, time
from traceback import print_exc


def tryreadconfig(path, default=None):
    try:
        path = os.path.join("./userconfig/", path)
        if os.path.exists(path) == False:
            path += ".tmp"
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as ff:
                x = json.load(ff)
        else:
            x = default if default else {}
        return x
    except:
        return {}


def tryreadconfig2(path):
    path = os.path.join("./files/defaultconfig/", path)
    with open(path, "r", encoding="utf-8") as ff:
        x = json.load(ff)
    return x


static_data = tryreadconfig2("static_data.json")
defaultpost = tryreadconfig2("postprocessconfig.json")
defaultglobalconfig = tryreadconfig2("config.json")
defaulterrorfix = tryreadconfig2("transerrorfixdictconfig.json")
dfmagpie_config = tryreadconfig2("magpie_config.json")
defaultnoun = tryreadconfig2("noundictconfig.json")
translatordfsetting = tryreadconfig2("translatorsetting.json")
ocrdfsetting = tryreadconfig2("ocrsetting.json")
ocrerrorfixdefault = tryreadconfig2("ocrerrorfix.json")

ocrerrorfix = tryreadconfig("ocrerrorfix.json")
globalconfig = tryreadconfig("config.json")
magpie_config = tryreadconfig("magpie_config.json")
postprocessconfig = tryreadconfig("postprocessconfig.json")
noundictconfig = tryreadconfig("noundictconfig.json")
transerrorfixdictconfig = tryreadconfig("transerrorfixdictconfig.json")
_savehook = tryreadconfig("savehook_new_1.39.4.json", default=[[], {}])
try:
    savehook_new_list = _savehook[0]
    savehook_new_data = _savehook[1]
except:
    savehook_new_list = []
    savehook_new_data = {}

try:
    savegametaged = _savehook[2]
except:
    savegametaged = [None]

translatorsetting = tryreadconfig("translatorsetting.json")
ocrsetting = tryreadconfig("ocrsetting.json")

vndbtagdata = tryreadconfig("vndbtagdata.json")


def getdefaultsavehook(gamepath, title=None):
    default = {
        "localeswitcher": 0,
        "onloadautochangemode2": 0,
        "onloadautoswitchsrclang": 0,
        "needinserthookcode": [],
        "embedablehook": [],
        "imagepath": None,
        "imagepath_much2": [],
        "isimagepathusersetted": False,
        "isimagepathusersetted_much": False,
        "istitlesetted": False,
        "infopath": None,
        "vid": 0,
        "namemap": {},
        "statistic_playtime": 0,
        "statistic_wordcount": 0,
        "statistic_wordcount_nodump": 0,
        "leuse": True,
        "startcmd": '"{exepath}"',
        "startcmduse": False,
        "hook": [],
        "inserthooktimeout": 0,
        "needinserthookcode": [],
        "removeuseless": False,
        "codepage_index": 0,
        # "allow_tts_auto_names": "",
        "allow_tts_auto_names_v4": [],
        "tts_repair": False,
        "tts_repair_regex": [],
        "hooktypeasname": {},
        "use_saved_text_process": False,
        "searchnoresulttime": 0,
        "relationlinks": [],
        "gamejsonfile": "",
        "gamesqlitefile": "",
        "vndbtags": [],
        "usertags": [],
        "traceplaytime_v2": [],  # [[start,end]]
        "autosavesavedata": "",
        "developers": [],
    }
    if title and len(title):
        default["title"] = title
    else:
        default["title"] = (
            os.path.basename(os.path.dirname(gamepath))
            + "/"
            + os.path.basename(gamepath)
        )

    return default


_dfsavehook = getdefaultsavehook("")
for game in savehook_new_data:
    if ("traceplaytime_v2" not in savehook_new_data[game]) and (
        "statistic_playtime" in savehook_new_data[game]
    ):
        savehook_new_data[game]["traceplaytime_v2"] = [
            [
                0,
                savehook_new_data[game]["statistic_playtime"],
            ]
        ]
    if (
        ("allow_tts_auto_names_v4" not in savehook_new_data[game])
        and ("allow_tts_auto_names" in savehook_new_data[game])
        and len(savehook_new_data[game]["allow_tts_auto_names"])
    ):
        savehook_new_data[game]["allow_tts_auto_names_v4"] = savehook_new_data[game][
            "allow_tts_auto_names"
        ].split("|")

    for k in _dfsavehook:
        if k not in savehook_new_data[game]:
            savehook_new_data[game][k] = _dfsavehook[k]


def syncconfig(config1, default, drop=False, deep=0, skipdict=False):

    for key in default:
        if key not in config1:
            config1[key] = default[key]

        elif key in ("name", "tip"):
            config1[key] = default[key]
        elif key == "argstype":
            config1[key] = default[key]
        elif key == "args":
            _nuse = []
            for k in default[key]:
                if k not in config1[key]:
                    config1[key][k] = default[key][k]
            for k in config1[key]:
                if k not in default[key]:
                    _nuse.append(k)
            for k in _nuse:
                config1[key].pop(k)

        else:
            if type(default[key]) != type(config1[key]) and (
                type(default[key]) == dict or type(default[key]) == list
            ):
                config1[key] = default[key]
            elif type(default[key]) == dict:
                if skipdict == False:
                    syncconfig(config1[key], default[key], drop, deep - 1)

    if drop and deep > 0:
        for key in list(config1.keys()):
            if key not in default:
                config1.pop(key)


syncconfig(globalconfig, defaultglobalconfig)
syncconfig(transerrorfixdictconfig, defaulterrorfix)
if True:  # transerrorfixdictconfig cast v1 to v2:
    if "dict" in transerrorfixdictconfig:
        for key in transerrorfixdictconfig["dict"]:
            value = transerrorfixdictconfig["dict"][key]
            transerrorfixdictconfig["dict_v2"].append(
                {"key": key, "value": value, "regex": False}
            )
        transerrorfixdictconfig.pop("dict")


syncconfig(noundictconfig, defaultnoun)
syncconfig(magpie_config, dfmagpie_config, skipdict=True)
syncconfig(translatorsetting, translatordfsetting)

syncconfig(ocrsetting, ocrdfsetting)

if ocrerrorfix == {}:
    if "_100" in postprocessconfig:
        ocrerrorfix = postprocessconfig["_100"]
    else:
        ocrerrorfix = ocrerrorfixdefault
syncconfig(postprocessconfig, defaultpost, True, 3)

for key in defaultglobalconfig["toolbutton"]["buttons"]:
    if key not in globalconfig["toolbutton"]["rank2"]:
        globalconfig["toolbutton"]["rank2"].append(key)
___ = []
for key in globalconfig["toolbutton"]["rank2"]:
    if key not in defaultglobalconfig["toolbutton"]["buttons"]:
        ___.append(key)
for key in ___:
    globalconfig["toolbutton"]["rank2"].remove(key)


def getlanguse():
    global language, languageshow
    return static_data["language_list_translator_inner"][language]


def getlangsrc():
    return static_data["language_list_translator_inner"][globalconfig["srclang3"]]


def getlangtgt():
    return static_data["language_list_translator_inner"][globalconfig["tgtlang3"]]


def setlanguage():
    global language, languageshow
    language = globalconfig["languageuse"]
    try:
        with open(
            "./files/lang/{}.json".format(getlanguse()),
            "r",
            encoding="utf8",
        ) as ff:
            languageshow = json.load(ff)
    except:
        languageshow = {}


setlanguage()


def _TR(k):
    global language, languageshow
    if k == "":
        return ""
    try:
        k.encode("ascii")
        return k
    except:
        if "_" in k:
            splits = k.split("_")
            return " ".join([_TR(_) for _ in splits])

        if k not in languageshow or languageshow[k] == "":
            languageshow[k] = ""
            return k
        else:
            return languageshow[k]


lastapppath = globalconfig["lastapppath"]
thisapppath = os.path.normpath(os.getcwd())

if lastapppath is None:
    lastapppath = thisapppath
else:
    lastapppath = os.path.normpath(lastapppath)

globalconfig["lastapppath"] = thisapppath


def dynamicrelativepath(abspath):
    if os.path.exists(abspath):
        return abspath
    _ = os.path.normpath(abspath)
    if _.startswith(lastapppath):
        np = thisapppath + _[len(lastapppath) :]
        if os.path.exists(np):
            return np
    return abspath


def parsetarget(dict_, key):
    t = dict_[key]

    if isinstance(t, list):
        t = [dynamicrelativepath(_) for _ in t]
    else:
        t = dynamicrelativepath(t)
    dict_[key] = t


def autoparsedynamicpath():
    for dic, routine, target in (
        (globalconfig, ("cishu", "mdict", "args"), "paths"),
        (globalconfig, ("cishu", "mdict", "args"), "path_dir"),
        (globalconfig, ("cishu", "edict", "args"), "path"),
        (globalconfig, ("cishu", "linggesi", "args"), "path"),
        (globalconfig, ("cishu", "xiaoxueguan", "args"), "path"),
        (globalconfig, ("hirasetting", "mecab", "args"), "path"),
        (globalconfig, ("hirasetting", "mecab", "args"), "path"),
        (globalconfig, ("reader", "voiceroid2", "args"), "path"),
        (translatorsetting, ("dreye", "args"), "path"),
        (translatorsetting, ("jb7", "args"), "path"),
        (translatorsetting, ("jb7", "args"), "path_userdict3"),
        (translatorsetting, ("jb7", "args"), "path_userdict1"),
        (translatorsetting, ("jb7", "args"), "path_userdict2"),
        (translatorsetting, ("kingsoft", "args"), "path"),
        (translatorsetting, ("ort_sp", "args"), "path"),
        (translatorsetting, ("premt", "args"), "sqlitefile"),
        (translatorsetting, ("rengong", "args"), "jsonfile"),
    ):
        try:
            for _k in routine:
                dic = dic.get(_k, None)
                if dic is None:
                    break
            if dic is None:
                continue
            parsetarget(dic, target)
        except:
            print_exc()


if thisapppath != lastapppath:
    autoparsedynamicpath()


def _TRL(kk):
    x = []
    for k in kk:
        x.append(_TR(k))
    return x


def saveallconfig():
    def safesave(fname, js):
        # 有时保存时意外退出，会导致config文件被清空
        with open(fname + ".tmp", "w", encoding="utf-8") as ff:
            ff.write(json.dumps(js, ensure_ascii=False, sort_keys=False, indent=4))
        if os.path.exists(fname):
            os.remove(fname)
        os.rename(fname + ".tmp", fname)

    os.makedirs("./userconfig", exist_ok=True)
    safesave("./userconfig/config.json", globalconfig)
    safesave("./userconfig/magpie_config.json", magpie_config)
    safesave("./userconfig/postprocessconfig.json", postprocessconfig)
    safesave("./userconfig/transerrorfixdictconfig.json", transerrorfixdictconfig)
    safesave("./userconfig/noundictconfig.json", noundictconfig)
    safesave("./userconfig/translatorsetting.json", translatorsetting)
    safesave("./userconfig/ocrerrorfix.json", ocrerrorfix)
    safesave("./userconfig/ocrsetting.json", ocrsetting)
    safesave("./userconfig/vndbtagdata.json", vndbtagdata)
    safesave(
        "./userconfig/savehook_new_1.39.4.json",
        [savehook_new_list, savehook_new_data, savegametaged],
    )
    safesave(
        "./files/lang/{}.json".format(getlanguse()),
        languageshow,
    )
