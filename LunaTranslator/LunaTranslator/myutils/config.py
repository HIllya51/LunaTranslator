import json
import os, time, uuid
from traceback import print_exc


def tryreadconfig(path, default=None):
    path = os.path.join("userconfig", path)
    if not os.path.exists(path):
        path += ".tmp"
    dfret = default if default else {}
    if not os.path.exists(path):
        return dfret
    try:
        with open(path, "r", encoding="utf-8") as ff:
            x = json.load(ff)

        return x
    except:
        return dfret


def tryreadconfig2(path):
    path = os.path.join("files/defaultconfig", path)
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
_savehook = tryreadconfig("savegamedata_5.3.1.json")
if _savehook:
    # 新版
    # savehook_new_list: [uid,...]
    # savehook_new_data:{uid:dict,...}
    # savegametaged:[ None, {'games':[uid,...],'title':str,'opened':bool,'uid':str},...]
    # gamepath2uid:{gamepath:uid}
    savehook_new_list = _savehook[0]
    savehook_new_data = _savehook[1]
    savegametaged = _savehook[2]
    # gamepath2uid = _savehook[3] 不再使用，允许重复的path
else:

    _savehook = tryreadconfig("savehook_new_1.39.4.json", default=[[], {}])

    # savehook_new_list: [gamepath,...]
    # savehook_new_data:{gamepath:dict,...}
    # savegametaged: 可能没有该项 [ None, {'games':[gamepath,...],'title':str,'opened':bool,'uid':str},...]
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

    # 将savehook_new_data转换为新的格式
    __gamepath2uid = {}
    __savehook_new_data = {}
    for k in savehook_new_data:
        uid = f"{time.time()}_{uuid.uuid4()}"

        __savehook_new_data[uid] = savehook_new_data[k]
        __savehook_new_data[uid].update(gamepath=k)
        __gamepath2uid[k] = uid
    savehook_new_data = __savehook_new_data

    # 将global游戏表和自定义子列表都转换成新格式
    def parselist(ls):
        for i in range(len(ls)):
            ori = ls[i]
            if ori not in __gamepath2uid:
                continue
            ls[i] = __gamepath2uid[ori]

    parselist(savehook_new_list)
    for sub in savegametaged:
        if sub is None:
            continue
        parselist(sub["games"])
translatorsetting = tryreadconfig("translatorsetting.json")
ocrsetting = tryreadconfig("ocrsetting.json")


def getdefaultsavehook(title=None):
    default = {
        "gamepath": "",  # 不要直接访问，要通过uid2gamepath来间接访问
        "hooksetting_follow_default": True,
        "hooksetting_private": {},  # 显示时再加载，缺省用global中的键
        "textproc_follow_default": True,
        "save_text_process_info": {
            "postprocessconfig": {},
            "rank": [],
            # "mypost":# 设置时再加载
        },
        "lang_follow_default": True,
        # "private_srclang": 0,# 显示时再加载，缺省用global中的键
        # "private_tgtlang": 0,
        "follow_default_ankisettings": True,
        # "anki_DeckName":str
        "localeswitcher": 0,
        "onloadautochangemode2": 0,
        "needinserthookcode": [],
        "embedablehook": [],
        "statistic_playtime": 0,
        "statistic_wordcount": 0,
        "statistic_wordcount_nodump": 0,
        "leuse": True,
        "startcmd": '"{exepath}"',
        "startcmduse": False,
        "hook": [],
        "inserthooktimeout": 0,
        "needinserthookcode": [],
        # "allow_tts_auto_names": "",#->v4
        # "allow_tts_auto_names_v4": [],
        "tts_follow_default": True,
        "tts_repair": False,
        "tts_repair_regex": [{"regex": True, "key": "(.*?)「", "value": ""}],
        "tts_skip": False,
        "transoptimi_followdefault": True,
        "tts_skip_regex": [],
        # "hooktypeasname": {},
        "use_saved_text_process": False,
        # "searchnoresulttime": 0,
        "gamejsonfile": [],  # 之前是"",后面改成[]
        "gamesqlitefile": "",
        "relationlinks": [],
        # "vndbtags": [],#->webtags
        "usertags": [],
        # "traceplaytime_v2": [],  # [[start,end]]->db.traceplaytime_v4，这个东西增加到太快了，有点膨胀
        # "autosavesavedata": "",
        # 判断是否为自定义元数据，避免覆写
        # "isimagepathusersetted": False,
        # "isimagepathusersetted_much": False,
        "istitlesetted": False,
        "currentvisimage": None,
        "currentmainimage": "",
        "noundictconfig": [],
        # 元数据
        "namemap": {},  # 人名翻译映射，vndb独占，用于优化翻译
        #
        "vid": 0,
        "bgmsid": 0,
        "dlsiteid": "RJ/VJXXXX",
        "fanzaid": "",
        "steamid": 0,
        "title": "",
        # "imagepath": None,  # 封面->imagepath_all[0]
        # "imagepath_much2": [],  # 截图->imagepath_all[1:]
        "imagepath_all": [],
        "developers": [],
        "webtags": [],  # 标签
        # "infopath": None,  # 离线存储的主页
    }
    if title and len(title):
        default["title"] = title  # metadata

    return default


_dfsavehook = getdefaultsavehook("")
for uid in savehook_new_data:
    if (
        ("allow_tts_auto_names_v4" not in savehook_new_data[uid])
        and ("allow_tts_auto_names" in savehook_new_data[uid])
        and len(savehook_new_data[uid]["allow_tts_auto_names"])
    ):
        savehook_new_data[uid]["allow_tts_auto_names_v4"] = savehook_new_data[uid][
            "allow_tts_auto_names"
        ].split("|")

    if ("allow_tts_auto_names_v4" in savehook_new_data[uid]) and (
        "tts_skip_regex" not in savehook_new_data[uid]
    ):
        savehook_new_data[uid]["tts_skip_regex"] = []
        for name in savehook_new_data[uid]["allow_tts_auto_names_v4"]:
            savehook_new_data[uid]["tts_skip_regex"].append(
                {"regex": False, "key": name, "condition": 0}
            )

    for k in _dfsavehook:
        if k not in savehook_new_data[uid]:
            savehook_new_data[uid][k] = _dfsavehook[k]


class __uid2gamepath:
    def __setitem__(self, uid, value):

        savehook_new_data[uid]["gamepath"] = value

    def __getitem__(self, uid):
        return savehook_new_data.get(uid, {}).get("gamepath", None)


uid2gamepath = __uid2gamepath()


def findgameuidofpath(gamepath, targetlist=None, findall=False):
    # 一般只在save_game_list里查找，用于从getpidexe获取uid
    # 因为有可能有过去的不再使用的uid，发生碰撞。
    # 只在添加游戏时，全面查找。
    if not gamepath:
        if findall:
            return []
        else:
            return None
    # 遍历的速度非常快，1w条的速度也就0.001x秒
    # 但1w条数据时，load/dump的速度就有点慢了，能2秒多

    checkin = targetlist
    if checkin is None:
        checkin = savehook_new_data.keys()
    collect = []
    for uid in checkin:
        if savehook_new_data[uid]["gamepath"] == gamepath:
            if findall:
                collect.append(uid)
            else:
                return uid
    if findall:
        return collect
    else:
        return None


def syncconfig(config1, default, drop=False, deep=0, skipdict=False):

    for key in default:
        if key not in config1:
            config1[key] = default[key]

        elif key in ("name", "tip", "argstype"):
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
    if isinstance(config1, dict) and isinstance(default, dict):
        for key in ("name", "tip", "argstype", "args"):
            if key in config1 and key not in default:
                config1.pop(key)
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


for group in ["webview", "textbrowser"]:

    if (
        globalconfig["rendertext_using_internal"][group]
        not in static_data["textrender"][group]
    ):
        globalconfig["rendertext_using_internal"][group] = static_data["textrender"][
            group
        ][0]


def getlanguse():
    global language, languageshow
    return static_data["language_list_translator_inner"][language]


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


def safesave(fname, js, beatiful=True):
    # 有时保存时意外退出，会导致config文件被清空
    os.makedirs("./userconfig", exist_ok=True)
    with open(fname + ".tmp", "w", encoding="utf-8") as ff:
        if beatiful:
            ff.write(json.dumps(js, ensure_ascii=False, sort_keys=False, indent=4))
        else:
            # savegamedata 1w条时，indent=4要2秒，不indent 0.37秒，不ensure_ascii 0.27秒，用不着数据库了
            ff.write(json.dumps(js, sort_keys=False))
    if os.path.exists(fname):
        os.remove(fname)
    os.rename(fname + ".tmp", fname)


def saveallconfig():

    safesave("./userconfig/config.json", globalconfig)
    safesave("./userconfig/magpie_config.json", magpie_config)
    safesave("./userconfig/postprocessconfig.json", postprocessconfig)
    safesave("./userconfig/transerrorfixdictconfig.json", transerrorfixdictconfig)
    safesave("./userconfig/noundictconfig.json", noundictconfig)
    safesave("./userconfig/translatorsetting.json", translatorsetting)
    safesave("./userconfig/ocrerrorfix.json", ocrerrorfix)
    safesave("./userconfig/ocrsetting.json", ocrsetting)
    safesave(
        "./userconfig/savegamedata_5.3.1.json",
        [savehook_new_list, savehook_new_data, savegametaged, None],
        beatiful=False,
    )
    safesave(
        "./files/lang/{}.json".format(getlanguse()),
        languageshow,
    )
