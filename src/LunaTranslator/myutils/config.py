import json
import os, time, uuid, re
from traceback import print_exc
from language import TransLanguages, Languages


def __mayberelpath(path):
    try:
        # https://bugs.python.org/issue36689
        # commonpath在低版本上不能跨盘比较
        if os.path.commonpath((os.getcwd(), path)) == os.getcwd():
            return os.path.relpath(path)
    except:
        pass
    return os.path.normpath(path)


def mayberelpath(path):
    p = __mayberelpath(path)
    if os.path.exists(p):
        return p
    return path


def isascii(s: str):
    try:
        return s.isascii()
    except:
        try:
            s.encode("ascii")
            return True
        except:
            return False


def tryreadconfig(path, default=None):
    path = os.path.join("userconfig", path)
    try:
        with open(path, "r", encoding="utf-8") as ff:
            return json.load(ff)
    except:
        return default if default else {}


def tryreadconfig_1(path, default=None, pathold=None):
    try:
        if not pathold:
            raise Exception()
        pathold = os.path.join("userconfig", pathold)
        with open(pathold, "r", encoding="utf-8") as ff:
            old = json.load(ff)
        os.remove(pathold)
        return old
    except:
        return tryreadconfig(path, default)


def tryreadconfig2(path):
    path = os.path.join("LunaTranslator/defaultconfig", path)
    with open(path, "r", encoding="utf-8") as ff:
        x = json.load(ff)
    return x


static_data = tryreadconfig2("static_data.json")
defaultpost = tryreadconfig2("postprocessconfig.json")
defaultglobalconfig = tryreadconfig2("config.json")
defaulterrorfix = tryreadconfig2("transerrorfixdictconfig.json")
dfmagpie_config = tryreadconfig2("Magpie/config.json")
translatordfsetting = tryreadconfig2("translatorsetting.json")
ocrdfsetting = tryreadconfig2("ocrsetting.json")
ocrerrorfixdefault = tryreadconfig2("ocrerrorfix.json")

ocrerrorfix = tryreadconfig("ocrerrorfix.json")
globalconfig: "dict[str, dict[str, str] | list[str] | str]" = tryreadconfig(
    "config.json"
)
magpie_config = tryreadconfig_1("Magpie/config.json", pathold="magpie_config.json")
postprocessconfig = tryreadconfig("postprocessconfig.json")

transerrorfixdictconfig = tryreadconfig("transerrorfixdictconfig.json")
_savehook = tryreadconfig("savegamedata_5.3.1.json")
if _savehook:
    # 新版
    # savehook_new_list: [uid,...]
    # savehook_new_data:{uid:dict,...}
    # savegametaged:[ None, {'games':[uid,...],'title':str,'opened':bool,'uid':str},...]
    # gamepath2uid:{gamepath:uid}
    savehook_new_list: list = _savehook[0]
    savehook_new_data: "dict[str, dict]" = _savehook[1]
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

if "localedpath" not in extradatas:
    extradatas["localedpath"] = {}
if "imagefrom" not in extradatas:
    extradatas["imagefrom"] = {}


def getdefaultsavehook(title=None):
    default = {
        "gamepath": "",  # 不要直接访问，要通过uid2gamepath来间接访问
        # "launchpath": "",
        # "hooksetting_follow_default": True,
        # "embed_follow_default": True,
        "embed_setting_private": {},
        "hooksetting_private": {},  # 显示时再加载，缺省用global中的键
        # "textproc_follow_default": True,
        "save_text_process_info": {
            "postprocessconfig": {},
            "rank": [],
            # "mypost":# 设置时再加载
        },
        # "lang_follow_default": True,
        # "private_srclang_2": 0,# 显示时再加载，缺省用global中的键
        # "private_tgtlang_2": 0,
        # "onloadautochangemode2": 0,
        # "embedablehook": [],
        # "statistic_wordcount": 0,
        # "statistic_wordcount_nodump": 0,
        # "hook": [],
        # "inserthooktimeout": 250,
        # "insertpchooks_string": False,
        # "needinserthookcode": [],
        # "removeforeverhook": [],
        # "tts_follow_default": True,
        # "tts_repair": False,
        # "tts_repair_regex": [{"regex": True, "key": "(.*?)「", "value": ""}],
        # "tts_skip": False,
        # "transoptimi_followdefault": True,
        # "tts_skip_regex": [],
        # "gamejsonfile": [],  # 之前是"",后面改成[]
        # "gamesqlitefile": "",
        # "istitlesetted": False,
        # "currentvisimage": None,
        # "currentmainimage": "",
        # "currenticon": "",
        # "noundictconfig_ex": [],
        # "noundict_use": False,
        # "noundict_merge": False,
        # "vndbnamemap_use": True,
        # "vndbnamemap_merge": False,
        # "transerrorfix_use": False,
        # "transerrorfix_merge": False,
        # "transerrorfix": [],
        # 元数据
        # "namemap2": [],
        # "namemap": {},  # 人名翻译映射，vndb独占，用于优化翻译
        #
        # "vid": 0,
        # "bgmsid": 0,
        # "dlsiteid": "RJ/VJXXXX",
        # "steamid": 0,
        "title": "",
        # "imagepath_all": [],
        "usertags": [],
        "developers": [],
        "webtags": [],  # 标签
        # "createtime":xx  添加时间
    }
    if title and len(title):
        default["title"] = title  # metadata

    return default


_dfsavehook = getdefaultsavehook("")
for gameconfig in savehook_new_data.values():

    for __k, __v in _dfsavehook.items():
        if __k not in gameconfig:
            if isinstance(__v, (list, dict)):
                __v = __v.copy()
            gameconfig[__k] = __v


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


def syncconfig(config1, default, drop=False, deep=0):

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

syncconfig(magpie_config, dfmagpie_config)
syncconfig(
    magpie_config["profiles"][globalconfig["profiles_index"]],
    dfmagpie_config["profiles"][0],
)
syncconfig(translatorsetting, translatordfsetting)

syncconfig(ocrsetting, ocrdfsetting)
syncconfig(ocrerrorfix, ocrerrorfixdefault)
syncconfig(postprocessconfig, defaultpost, deep=3)


def _checkcpsetting(_d):
    if "codepage_index" in _d:
        _d["codepage_value"] = static_data["codepage_real"][_d.pop("codepage_index")]


_checkcpsetting(globalconfig)
for _ in savehook_new_data.values():
    _checkcpsetting(_.get("hooksetting_private", {}))

for key in defaultglobalconfig["toolbutton"]["buttons"]:
    if key not in globalconfig["toolbutton"]["rank2"]:
        globalconfig["toolbutton"]["rank2"].append(key)
___ = []
for key in globalconfig["toolbutton"]["rank2"]:
    if key not in defaultglobalconfig["toolbutton"]["buttons"]:
        ___.append(key)
for key in ___:
    globalconfig["toolbutton"]["rank2"].remove(key)

language_last = None

languageshow = {}


def getlanguse() -> Languages:
    return Languages.fromcode(globalconfig["languageuse2"])


def langfile(lang) -> str:
    return "files/lang/{}.json".format(lang)


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


def __parsenottr(match: re.Match):
    return "{}{}{}".format(_TR(match.group(1)), match.group(2), _TR(match.group(3)))


def __partagA(match: re.Match):
    return "{}{}{}".format(match.group(1), _TR(match.group(2)), match.group(3))


def ___TR(k: str) -> str:
    if "\n" in k:
        return "\n".join(_TR(k.split("\n")))
    if not k:
        return ""
    if k == "√":
        return k
    if "[[" in k and "]]" in k:
        return re.sub(r"(.*)\[\[(.*?)\]\](.*)", __parsenottr, k)
    if k.startswith("(") and k.endswith(")"):
        return "(" + ___TR(k[1:-1]) + ")"
    if k.startswith("<a") and k.endswith("</a>"):
        return re.sub("(<a.*?>)(.*?)(</a>)", __partagA, k)
    if "_" in k:
        fnd = k.find("_")
        return ___TR(k[:fnd]) + " " + ___TR(k[fnd + 1 :])
    if isascii(k):
        return k
    loadlanguage()
    __ = languageshow.get(k)
    if __:
        return __
    languageshow[k] = ""
    return k


def _TR(k: str | list[str]) -> str | list[str]:
    if isinstance(k, str):
        return ___TR(k)
    return [___TR(_) for _ in k]


def unsafesave(fname: str, js, beatiful=True):
    # 有时保存时意外退出，会导致config文件被清空
    os.makedirs(os.path.dirname(fname), exist_ok=True)

    js = json.dumps(
        js, ensure_ascii=False, sort_keys=False, indent=4 if beatiful else None
    )
    with open(fname + ".tmp", "w", encoding="utf-8") as ff:
        ff.write(js)
    os.replace(fname + ".tmp", fname)


def safesave(errorcollect: list, *argc, **kw):
    try:
        unsafesave(*argc, **kw)
    except Exception as e:
        errorcollect.append((e, argc[0]))
        print_exc()


def saveallconfig(test=False):
    errorcollect = []
    safesave(errorcollect, "userconfig/config.json", globalconfig)
    safesave(errorcollect, "userconfig/postprocessconfig.json", postprocessconfig)
    safesave(
        errorcollect, "userconfig/transerrorfixdictconfig.json", transerrorfixdictconfig
    )
    safesave(errorcollect, "userconfig/translatorsetting.json", translatorsetting)
    safesave(errorcollect, "userconfig/ocrerrorfix.json", ocrerrorfix)
    safesave(errorcollect, "userconfig/ocrsetting.json", ocrsetting)
    safesave(
        errorcollect,
        "userconfig/savegamedata_5.3.1.json",
        [savehook_new_list, savehook_new_data, savegametaged, None, extradatas],
        beatiful=False,
    )
    safesave(errorcollect, "userconfig/Magpie/config.json", magpie_config)
    if not test:
        safesave(errorcollect, "files/lang/{}.json".format(getlanguse()), languageshow)
    return errorcollect
