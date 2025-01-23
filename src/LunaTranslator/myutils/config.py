import json
import os, time, uuid, shutil, sys, platform
from traceback import print_exc
from language import TransLanguages, Languages
import winsharedutils


def isascii(s: str):
    try:
        return s.isascii()
    except:
        try:
            s.encode("ascii")
            return True
        except:
            return False


def namemapcast(namemap):
    bettermap = namemap.copy()
    for k, v in namemap.items():
        for sp in ["・", " "]:
            spja = k.split(sp)
            spen = v.split(sp if k == v else " ")
            if len(spja) == len(spen) and len(spen) > 1:
                for i in range(len(spja)):
                    if len(spja[i]) >= 2:
                        bettermap[spja[i]] = spen[i]
    return bettermap


def tryreadconfig(path, default=None):
    path = os.path.join("userconfig", path)
    try:
        with open(path, "r", encoding="utf-8") as ff:
            return json.load(ff)
    except:
        try:
            with open(path + ".tmp", "r", encoding="utf-8") as ff:
                return json.load(ff)
        except:
            return default if default else {}


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
translatordfsetting = tryreadconfig2("translatorsetting.json")
ocrdfsetting = tryreadconfig2("ocrsetting.json")
ocrerrorfixdefault = tryreadconfig2("ocrerrorfix.json")

ocrerrorfix = tryreadconfig("ocrerrorfix.json")
globalconfig = tryreadconfig("config.json")
magpie_config = tryreadconfig("magpie_config.json")
postprocessconfig = tryreadconfig("postprocessconfig.json")

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
        uid = "{}_{}".format(time.time(), uuid.uuid4())

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

try:
    extradatas = _savehook[4]
except:
    extradatas = {}
translatorsetting = tryreadconfig("translatorsetting.json")
ocrsetting = tryreadconfig("ocrsetting.json")

if "imagerefmp3" not in extradatas:
    extradatas["imagerefmp3"] = {}
if "imagecomment" not in extradatas:
    extradatas["imagecomment"] = {}
if "localedpath" not in extradatas:
    extradatas["localedpath"] = {}
if "imagefrom" not in extradatas:
    extradatas["imagefrom"] = {}


def getdefaultsavehook(title=None):
    default = {
        "gamepath": "",  # 不要直接访问，要通过uid2gamepath来间接访问
        # "launchpath": "",
        "hooksetting_follow_default": True,
        "hooksetting_private": {},  # 显示时再加载，缺省用global中的键
        "textproc_follow_default": True,
        "save_text_process_info": {
            "postprocessconfig": {},
            "rank": [],
            # "mypost":# 设置时再加载
        },
        "lang_follow_default": True,
        # "private_srclang_2": 0,# 显示时再加载，缺省用global中的键
        # "private_tgtlang_2": 0,
        "follow_default_ankisettings": True,
        # "localeswitcher": 0,废弃
        "onloadautochangemode2": 0,
        "needinserthookcode": [],
        "embedablehook": [],
        "statistic_wordcount": 0,
        "statistic_wordcount_nodump": 0,
        # "leuse": True, 废弃
        "hook": [],
        "inserthooktimeout": 500,
        "insertpchooks_string": False,
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
        # "currentmainimage": "",
        # "currenticon": "",
        # "noundictconfig": [],
        "noundictconfig_ex": [],
        "noundict_use": False,
        "noundict_merge": False,
        "vndbnamemap_use": True,
        "vndbnamemap_merge": False,
        "transerrorfix_use": False,
        "transerrorfix_merge": False,
        "transerrorfix": [],
        # 元数据
        "namemap2": [],
        # "namemap": {},  # 人名翻译映射，vndb独占，用于优化翻译
        #
        # "vid": 0,
        # "bgmsid": 0,
        # "dlsiteid": "RJ/VJXXXX",
        # "steamid": 0,
        "title": "",
        # "imagepath": None,  # 封面->imagepath_all[0]
        # "imagepath_much2": [],  # 截图->imagepath_all[1:]
        "imagepath_all": [],
        "developers": [],
        "webtags": [],  # 标签
        # "description": "",  # 简介
        # "infopath": None,  # 离线存储的主页
    }
    if title and len(title):
        default["title"] = title  # metadata

    return default


needcast = False
if "xxxcast" not in globalconfig:
    globalconfig["xxxcast"] = True
    needcast = True


def findFixedRuntime():
    hasset = os.environ.get("WEBVIEW2_BROWSER_EXECUTABLE_FOLDER")
    if hasset:
        # 已设置的环境变量会影响检测。直接返回就行了
        return hasset
    maxversion = (0, 0, 0, 0)
    maxvf = None
    for f in os.listdir("."):
        f = os.path.abspath(f)
        version = winsharedutils.detect_webview2_version(f)
        # 这个API似乎可以检测runtime是否是有效的，比自己查询版本更好
        if not version:
            continue
        if version > maxversion:
            maxversion = version
            maxvf = f
            print(maxversion, f)
    return maxvf


if "rendertext_using" not in globalconfig:
    v = platform.version().split(".")
    iswin8later = tuple(int(_) for _ in platform.version().split(".")[:2]) <= (6, 1)
    webview2version = winsharedutils.detect_webview2_version()
    if iswin8later:
        if findFixedRuntime():
            # 如果手动放置，那一定选手动的，不管功能完不完整。
            globalconfig["rendertext_using"] = "webview"
        else:
            if webview2version and webview2version >= (100, 0, 0, 0):
                # <=99的功能不完整
                globalconfig["rendertext_using"] = "webview"
            else:
                globalconfig["rendertext_using"] = "textbrowser"
    else:
        # win7上无边框窗口渲染有问题，所以一定不优先
        globalconfig["rendertext_using"] = "textbrowser"

# fmt: off
oldlanguage = ["zh","ja","en","ru","es","ko","fr","cht","vi","tr","pl","uk","it","ar","th","bo","de","sv","nl"]
# fmt: on
_dfsavehook = getdefaultsavehook("")
for gameconfig in savehook_new_data.values():
    if "noundictconfig_ex" not in gameconfig:

        gameconfig["noundictconfig_ex"] = []
        if "noundictconfig" in gameconfig:

            for k, v in gameconfig["noundictconfig"]:
                gameconfig["noundictconfig_ex"].append(dict(src=k, dst=v, info=""))
        if "gptpromptdict" in gameconfig:

            gameconfig["noundictconfig_ex"].extend(gameconfig["gptpromptdict"])
    if (
        ("allow_tts_auto_names_v4" not in gameconfig)
        and ("allow_tts_auto_names" in gameconfig)
        and len(gameconfig["allow_tts_auto_names"])
    ):
        gameconfig["allow_tts_auto_names_v4"] = gameconfig[
            "allow_tts_auto_names"
        ].split("|")

    if ("allow_tts_auto_names_v4" in gameconfig) and (
        "tts_skip_regex" not in gameconfig
    ):
        gameconfig["tts_skip_regex"] = []
        for name in gameconfig["allow_tts_auto_names_v4"]:
            gameconfig["tts_skip_regex"].append(
                {"regex": False, "key": name, "condition": 0}
            )
    if ("private_srclang" in gameconfig) and ("private_srclang_2" not in gameconfig):
        gameconfig["private_srclang_2"] = oldlanguage[gameconfig["private_srclang"]]
        gameconfig["private_tgtlang_2"] = oldlanguage[gameconfig["private_tgtlang"]]

    if "namemap" in gameconfig:
        gameconfig["namemap2"] = []
        for k, v in namemapcast(gameconfig.pop("namemap")).items():
            gameconfig["namemap2"].append(
                {"key": k, "value": v, "regex": False, "escape": False}
            )

    for __k, __v in _dfsavehook.items():
        if __k not in gameconfig:
            if isinstance(__v, (list, dict)):
                __v = __v.copy()
            gameconfig[__k] = __v

    if not gameconfig.get("leuse", True):
        gameconfig.pop("leuse")
        gameconfig["launch_method"] = "direct"
    if needcast:
        if "save_text_process_info" not in gameconfig:
            continue
        if "rank" not in gameconfig["save_text_process_info"]:
            continue
        if "postprocessconfig" not in gameconfig["save_text_process_info"]:
            continue
        items = []
        try:
            ifuse = False
            for post in gameconfig["save_text_process_info"]["rank"]:
                # 简单
                if post == "_7":
                    ifuse = (
                        ifuse
                        or gameconfig["save_text_process_info"]["postprocessconfig"][
                            "_7"
                        ]["use"]
                    )
                    gameconfig["save_text_process_info"]["postprocessconfig"]["_7"][
                        "use"
                    ] = False
                    for k, v in gameconfig["save_text_process_info"][
                        "postprocessconfig"
                    ]["_7"]["args"]["替换内容"].items():
                        items.append(
                            {"regex": False, "escape": False, "key": k, "value": v}
                        )
                if post == "_7_zhuanyi":
                    ifuse = (
                        ifuse
                        or gameconfig["save_text_process_info"]["postprocessconfig"][
                            "_7_zhuanyi"
                        ]["use"]
                    )
                    gameconfig["save_text_process_info"]["postprocessconfig"][
                        "_7_zhuanyi"
                    ]["use"] = False
                    for k, v in gameconfig["save_text_process_info"][
                        "postprocessconfig"
                    ]["_7_zhuanyi"]["args"]["替换内容"].items():
                        items.append(
                            {"regex": False, "escape": True, "key": k, "value": v}
                        )
                # 正则
                if post == "_8":
                    ifuse = (
                        ifuse
                        or gameconfig["save_text_process_info"]["postprocessconfig"][
                            "_8"
                        ]["use"]
                    )
                    gameconfig["save_text_process_info"]["postprocessconfig"]["_8"][
                        "use"
                    ] = False
                    for k, v in gameconfig["save_text_process_info"][
                        "postprocessconfig"
                    ]["_8"]["args"]["替换内容"].items():
                        items.append(
                            {"regex": True, "escape": True, "key": k, "value": v}
                        )
            if len(items):
                gameconfig["save_text_process_info"]["rank"].append("stringreplace")
                gameconfig["save_text_process_info"]["postprocessconfig"][
                    "stringreplace"
                ] = {
                    "args": {"internal": items},
                    "use": ifuse,
                    "name": "字符串替换",
                }
        except:
            print_exc()
if "global_namemap" in globalconfig:
    globalconfig["global_namemap2"] = []
    for k, v in namemapcast(globalconfig.pop("global_namemap")).items():
        globalconfig["global_namemap2"].append(
            {"key": k, "value": v, "regex": False, "escape": False}
        )


class __uid2gamepath:
    def __setitem__(self, uid, value):

        savehook_new_data[uid]["gamepath"] = value

    def __getitem__(self, uid):
        return savehook_new_data.get(uid, {}).get("gamepath", None)


uid2gamepath = __uid2gamepath()

# 建立索引，当游戏特别多的时候，节省时间
gamepath2uid_index = {}
for uid in savehook_new_data:
    _p = os.path.abspath(savehook_new_data[uid]["gamepath"])
    if _p not in gamepath2uid_index:
        gamepath2uid_index[_p] = []
    gamepath2uid_index[_p].append(uid)


def get_launchpath(uid) -> str:
    launch = savehook_new_data[uid].get("launchpath", "")
    if not launch:
        launch = uid2gamepath[uid]
    return launch


def findgameuidofpath(gamepath, findall=False):
    if not gamepath:
        # getpidexe在部分情况下可能为None，导致崩溃
        if findall:
            return []
        else:
            return None, None
    gamepath = os.path.normpath(gamepath)
    uids = gamepath2uid_index.get(gamepath, [])
    if findall:
        return uids
    collect = []
    for sub in savegametaged:
        if sub is None:
            use = savehook_new_list
        else:
            use = sub["games"]
        minidx = len(use)
        minuid = None
        for uid in uids:
            if uid in use:
                idx = use.index(uid)
                if minidx > idx:
                    minidx = idx
                    minuid = uid
        if minuid:
            return minuid, use
    if findall:
        return collect
    else:
        return None, None


def syncconfig(config1, default, drop=False, deep=0, skipdict=False):

    for key in default:
        if key not in config1:
            config1[key] = default[key]

        elif key in ("name", "tip", "argstype", "type"):
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


syncconfig(magpie_config, dfmagpie_config, skipdict=True)
syncconfig(translatorsetting, translatordfsetting)

syncconfig(ocrsetting, ocrdfsetting)

if ocrerrorfix == {}:
    if "_100" in postprocessconfig:
        ocrerrorfix = postprocessconfig["_100"]
    else:
        ocrerrorfix = ocrerrorfixdefault
syncconfig(postprocessconfig, defaultpost, deep=3)


if "noundictconfig" not in globalconfig:

    noundictconfig = tryreadconfig("noundictconfig.json", {"dict": {}})
    globalconfig["noundictconfig"] = []
    for k, v in noundictconfig["dict"].items():
        if len(v) % 2 != 0:
            continue
        for i in range(len(v) // 2):
            md5, ts = v[i * 2], v[i * 2 + 1]
            globalconfig["noundictconfig"].append((k, ts))

if "noundictconfig_ex" not in globalconfig:
    globalconfig["noundictconfig_ex"] = []
    for k, v in globalconfig["noundictconfig"]:
        globalconfig["noundictconfig_ex"].append(dict(src=k, dst=v, info=""))
    if "gptpromptdict" in globalconfig:

        globalconfig["noundictconfig_ex"].extend(globalconfig["gptpromptdict"])


if needcast:
    ifuse = False
    for post in globalconfig["postprocess_rank"]:
        # 简单
        if post == "_7":
            ifuse = ifuse or postprocessconfig["_7"]["use"]
            postprocessconfig["_7"]["use"] = False
            for k, v in postprocessconfig["_7"]["args"]["替换内容"].items():
                postprocessconfig["stringreplace"]["args"]["internal"].append(
                    {"regex": False, "escape": False, "key": k, "value": v}
                )
        if post == "_7_zhuanyi":
            ifuse = ifuse or postprocessconfig["_7_zhuanyi"]["use"]
            postprocessconfig["_7_zhuanyi"]["use"] = False
            for k, v in postprocessconfig["_7_zhuanyi"]["args"]["替换内容"].items():
                postprocessconfig["stringreplace"]["args"]["internal"].append(
                    {"regex": False, "escape": True, "key": k, "value": v}
                )
        # 正则
        if post == "_8":
            ifuse = ifuse or postprocessconfig["_8"]["use"]
            postprocessconfig["_8"]["use"] = False
            for k, v in postprocessconfig["_8"]["args"]["替换内容"].items():
                postprocessconfig["stringreplace"]["args"]["internal"].append(
                    {"regex": True, "escape": True, "key": k, "value": v}
                )
    postprocessconfig["stringreplace"]["use"] = ifuse

for key in defaultglobalconfig["toolbutton"]["buttons"]:
    if key not in globalconfig["toolbutton"]["rank2"]:
        globalconfig["toolbutton"]["rank2"].append(key)
___ = []
for key in globalconfig["toolbutton"]["rank2"]:
    if key not in defaultglobalconfig["toolbutton"]["buttons"]:
        ___.append(key)
for key in ___:
    globalconfig["toolbutton"]["rank2"].remove(key)

if "DeckName" in globalconfig["ankiconnect"]:
    deckname = globalconfig["ankiconnect"].pop("DeckName")
    if deckname not in globalconfig["ankiconnect"]["DeckNameS"]:
        globalconfig["ankiconnect"]["DeckNameS"].append(deckname)

    for data in savehook_new_data.values():
        deck = data.get("anki_DeckName", "")
        if not deck:
            continue
        if deck in globalconfig["ankiconnect"]["DeckNameS"]:
            continue
        globalconfig["ankiconnect"]["DeckNameS"].append(deck)

for group in ["webview", "textbrowser"]:

    if (
        globalconfig["rendertext_using_internal"][group]
        not in static_data["textrender"][group]
    ):
        globalconfig["rendertext_using_internal"][group] = static_data["textrender"][
            group
        ][0]

language_last = None

languageshow = {}

static_data["language_list_translator_inner"] = [_.code for _ in TransLanguages]

static_data["language_list_translator_inner_english"] = [
    _.engname for _ in TransLanguages
]


def getlanguse() -> Languages:
    return Languages.fromcode(globalconfig["languageuse2"])


def langfile(lang) -> str:
    return "./files/lang/{}.json".format(lang)


def loadlanguage():
    global language_last, languageshow
    _language = getlanguse()
    if _language == language_last:
        return
    language_last = _language
    try:
        with open(langfile(_language), "r", encoding="utf8") as ff:
            languageshow = json.load(ff)
    except:
        languageshow = {}


def _TR(k: str) -> str:
    if not k:
        return ""
    if "_" in k:
        splits = k.split("_")
        return " ".join([_TR(_) for _ in splits])
    if k.startswith("(") and k.endswith(")"):
        return "(" + _TR(k[1:-1]) + ")"
    if isascii(k):
        return k
    loadlanguage()
    __ = languageshow.get(k)
    if __:
        return __
    languageshow[k] = ""
    return k


def _TRL(kk):
    x = []
    for k in kk:
        x.append(_TR(k))
    return x


def getlang_inner2show(langcode):
    return dict(
        zip(
            [_.code for _ in TransLanguages],
            [_.zhsname for _ in TransLanguages],
        )
    ).get(langcode, "??")


def safesave(fname, js, beatiful=True):
    # 有时保存时意外退出，会导致config文件被清空
    os.makedirs("./userconfig", exist_ok=True)
    with open(fname + ".tmp", "w", encoding="utf-8") as ff:
        if beatiful:
            ff.write(json.dumps(js, ensure_ascii=False, sort_keys=False, indent=4))
        else:
            # savegamedata 1w条时，indent=4要2秒，不indent 0.37秒，不ensure_ascii 0.27秒，用不着数据库了
            ff.write(json.dumps(js, ensure_ascii=False, sort_keys=False))
    if os.path.exists(fname):
        os.remove(fname)
    shutil.copy(fname + ".tmp", fname)
    os.remove(fname + ".tmp")
    # wine上MoveFile会权限问题失败，不知道为什么，WinError 32


def saveallconfig(test=False):

    safesave("./userconfig/config.json", globalconfig)
    safesave("./userconfig/magpie_config.json", magpie_config)
    safesave("./userconfig/postprocessconfig.json", postprocessconfig)
    safesave("./userconfig/transerrorfixdictconfig.json", transerrorfixdictconfig)
    safesave("./userconfig/translatorsetting.json", translatorsetting)
    safesave("./userconfig/ocrerrorfix.json", ocrerrorfix)
    safesave("./userconfig/ocrsetting.json", ocrsetting)
    safesave(
        "./userconfig/savegamedata_5.3.1.json",
        [savehook_new_list, savehook_new_data, savegametaged, None, extradatas],
        beatiful=False,
    )
    if not test:
        safesave(
            "./files/lang/{}.json".format(getlanguse()),
            languageshow,
        )


# font_default_used = {}
def get_platform():
    if tuple(sys.version_info)[:2] == (3, 4):
        bit = "xp"
    elif platform.architecture()[0] == "64bit":
        bit = "64"
    elif platform.architecture()[0] == "32bit":
        bit = "32"
    return bit
