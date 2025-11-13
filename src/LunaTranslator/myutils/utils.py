import os, time
import codecs, hashlib, shutil
import socket, gobject, uuid, functools
import importlib, json, requests
from qtsymbols import *
from traceback import print_exc
from myutils.config import (
    _TR,
    dynamiclink,
    globalconfig,
    static_data,
    getlanguse,
    uid2gamepath,
    savehook_new_data,
    findgameuidofpath,
    getdefaultsavehook,
    gamepath2uid_index,
    defaultglobalconfig,
    dynamicapiname,
    urlpathjoin,
)
from myutils.keycode import vkcode_map, mod_map
from language import Languages, TransLanguages
import threading, winreg
import re, heapq, NativeUtils
from myutils.wrapper import tryprint, threader
from html.parser import HTMLParser
from myutils.audioplayer import bass_code_cast


class localcachehelper:
    def __init__(self, name):
        self.name = name
        self.cache = {}

    def __getitem__(self, url: str) -> "str|None":
        _ = self.cache.get(url)
        if _:
            return _
        b64 = hashlib.md5(url.encode("utf8")).hexdigest()
        fn = gobject.getcachedir(os.path.join(self.name, b64))
        if not os.path.isfile(fn):
            return None
        with open(fn, "r", encoding="utf8") as ff:
            data = ff.read()
        self.cache[url] = data
        return data

    def __setitem__(self, url: str, data: str):
        self.cache[url] = data
        b64 = hashlib.md5(url.encode("utf8")).hexdigest()
        fn = gobject.getcachedir(os.path.join(self.name, b64))
        with open(fn, "w", encoding="utf8") as ff:
            ff.write(data)

    get = __getitem__
    set = __setitem__


def qimage2binary(qimage: QImage, fmt="BMP") -> bytes:
    byte_array = QByteArray()
    buffer = QBuffer(byte_array)
    buffer.open(QBuffer.OpenModeFlag.WriteOnly)
    qimage.save(buffer, fmt)
    buffer.close()
    image_data = byte_array.data()
    return image_data


def checkisusingwine() -> bool:
    iswine = True
    try:
        winreg.OpenKeyEx(
            winreg.HKEY_CURRENT_USER,
            r"Software\Wine",
            0,
            winreg.KEY_QUERY_VALUE,
        )
    except FileNotFoundError:
        iswine = False
    return iswine


def __internal__getlang(k1: str, k2: str) -> str:
    try:
        for _ in (0,):
            gameuid = gobject.base.gameuid
            if not gameuid:
                break
            if savehook_new_data[gameuid].get("lang_follow_default", True):
                break

            return savehook_new_data[gameuid][k1], globalconfig[k2]
    except:
        pass
    return globalconfig[k2], globalconfig[k2]


def __translate_exits(fanyi):
    _fs = [
        "Lunatranslator/translator/{}.py".format(fanyi),
        gobject.getconfig("copyed/{}.py".format(fanyi)),
    ]
    for i, _ in enumerate(_fs):
        if os.path.exists(_):
            return i
    return None


def translate_exits(fanyi, which=False):
    # 不再加载废弃接口，以免煞笔问煞笔问题。
    _ = __translate_exits(fanyi)

    isdeprecated = (0 == _) and (
        (fanyi not in defaultglobalconfig["fanyi"]) and fanyi != "chatgpt-offline"
    )
    if which:
        if isdeprecated:
            return None
        return _
    else:
        return _ is not None


def all_langs(src=True):
    vis = (["自动"] if src else []) + [_.zhsname for _ in TransLanguages]
    internal = (["auto"] if src else []) + [_.code for _ in TransLanguages]
    for extra in globalconfig["extraLangs"]:
        internal.append(extra["code"])
        vis.append("[[" + extra["name"] + "]]")
    return vis, internal


def __fucklang(src, _) -> Languages:
    code, code2 = _
    _ = Languages.fromcode(code)
    if not _:
        name = None
        for extra in globalconfig["extraLangs"]:
            if code == extra["code"]:
                name = extra["name"]
                break
        if not name:
            if code2 != code:
                return __fucklang(code2, code2)
            else:
                return Languages.Auto if src else Languages.Chinese
        name = name or code
        _ = Languages(code, name, name, name)
    return _


def getlangsrc() -> Languages:
    return __fucklang(True, __internal__getlang("private_srclang_2", "srclang4"))


def getlangtgt() -> Languages:

    return __fucklang(False, __internal__getlang("private_tgtlang_2", "tgtlang4"))


def findenclose(text: str, tag: str) -> str:
    i = 0
    if tag == "link":
        tags = "<link"
        tage = ">"
    else:
        tags = "<{}".format(tag)
        tage = "</{}>".format(tag)
    collect = ""
    __ = 0
    while True:
        if text.startswith(tags):
            i += 1
            text = text[len(tags) :]
            collect += tags
        elif text.startswith(tage):
            i -= 1
            text = text[len(tage) :]
            collect += tage
        else:
            _1 = text.find(tags)
            _2 = text.find(tage)
            if _1 != -1 and _2 != -1:
                m = min(_1, _2)
            elif _1 != -1:
                m = _1
            elif _2 != -1:
                m = _2
            else:
                break
            collect += text[:m]
            text = text[m:]
        if i == 0:
            break

    return collect


def simplehtmlparser(text: str, tag: str, sign: str) -> str:
    text = text[text.find(sign) :]
    inner = findenclose(text, tag)
    return inner


def simplehtmlparser_all(text: str, tag: str, sign: str) -> "list[str]":
    inners = []
    while True:
        idx = text.find(sign)
        if idx == -1:
            break
        text = text[idx:]
        inner = findenclose(text, tag)
        inners.append(inner.replace("\n", ""))
        text = text[len(inners) :]
    return inners


def nowisdark() -> bool:
    dl = globalconfig["darklight2"]
    if dl == 1:
        dark = False
    elif dl == 2:
        dark = True
    elif dl == 0:
        dark = NativeUtils.IsDark()
    return dark


class PriorityQueue:
    def __init__(self):
        self._heap = []
        self._sema = threading.Semaphore(0)
        self._idx = 0

    def put(self, item, priority=0):
        heapq.heappush(self._heap, (-priority, self._idx, item))
        self._idx += 1
        self._sema.release()

    def get(self):
        self._sema.acquire()
        return heapq.heappop(self._heap)[-1]

    def empty(self):
        return bool(len(self._heap) == 0)


def guessmaybetitle(gamepath, title):

    __t = []

    print(gamepath)
    for _ in [
        title,
        os.path.basename(os.path.dirname(gamepath)),
        os.path.basename(gamepath)[:-4],
    ]:
        if not _:
            continue
        _ = _.replace("(同人ゲーム)", "").replace("(18禁ゲーム)", "")
        _ = re.sub(r"\[RJ(.*?)\]", "", _)
        _ = re.sub(r"\[\d{4}-?\d{2}\-?\d{2}\]", "", _)
        __t.append(_)
        _ = re.sub(r"\[(.*?)\]", "", _)
        if _ != __t[-1]:
            __t.append(_)
        _ = re.sub(r"\((.*?)\)", "", _)
        if _ != __t[-1]:
            __t.append(_)
    lst = []
    for i, t in enumerate(__t):
        t = t.strip()
        if t in lst:
            continue
        if (len(t) < 10) and (all(ord(c) < 128 for c in t)):
            continue
        lst.append(t)
    print(lst)
    return lst


targetmod = {}


def dispatchsearchfordata(gameuid, target, vid):
    targetmod[target].dispatchsearchfordata(gameuid, vid)


@threader
def trysearchforid_1(gameuid, searchargs: list, target=None):
    if target is None:
        __ = []
        for k in targetmod:
            if not globalconfig["metadata"][k]["auto"]:
                continue
            __.append(k)
    else:
        __ = [target]
    for key in __:
        vid = None
        for arg in searchargs:
            if not arg:
                continue
            try:
                vid = targetmod[key].getidbytitle(arg)
            except:
                print_exc()
                continue
            if vid:
                break
        if not vid:
            continue
        idname = targetmod[key].idname
        savehook_new_data[gameuid][idname] = vid
        gobject.base.translation_ui.displayglobaltooltip.emit(
            "{}: found {}".format(key, vid)
        )
        dispatchsearchfordata(gameuid, key, vid)


def trysearchforid(*argc):
    trysearchforid_1(*argc)


def gamdidchangedtask(key, idname, gameuid):
    vid = savehook_new_data[gameuid].get(idname, "")
    if not vid:
        trysearchforid(gameuid, [savehook_new_data[gameuid]["title"]], key)
    else:
        dispatchsearchfordata(gameuid, key, vid)


def titlechangedtask(gameuid, title):
    savehook_new_data[gameuid]["title"] = title
    savehook_new_data[gameuid]["istitlesetted"] = True
    trysearchforid(gameuid, [title])


class gamepath2uid_index_helper(dict):
    def __init__(self, d, uid):
        super().__init__(d)
        self.uid = uid

    def __setitem__(self, key, value):

        if key == "gamepath":
            origin = os.path.abspath(self.get(key))
            if origin in gamepath2uid_index and self.uid in gamepath2uid_index[origin]:
                try:
                    gamepath2uid_index[origin].remove(self.uid)
                except:
                    pass
            absv = os.path.abspath(value)
            if absv not in gamepath2uid_index:
                gamepath2uid_index[absv] = []
            gamepath2uid_index[absv].append(self.uid)
        super().__setitem__(key, value)


def initanewitem(title):
    t = time.time()
    uid = "{}_{}".format(t, uuid.uuid4())
    savehook_new_data[uid] = gamepath2uid_index_helper(getdefaultsavehook(title), uid)
    savehook_new_data[uid]["createtime"] = t
    return uid


def duplicateconfig(uidold):
    t = time.time()
    uid = "{}_{}".format(t, uuid.uuid4())
    savehook_new_data[uid] = json.loads(json.dumps(savehook_new_data[uidold]))
    savehook_new_data[uid]["createtime"] = t
    return uid


def find_or_create_uid(targetlist, gamepath: str, title=None):
    uids = findgameuidofpath(gamepath, findall=True)
    if len(uids) == 0:
        uid = initanewitem(title)
        if title is None:
            savehook_new_data[uid]["title"] = (
                os.path.basename(os.path.dirname(gamepath))
                + "/"
                + os.path.basename(gamepath)
            )
        if gamepath.lower().endswith(".lnk"):
            exepath, _, _, _ = NativeUtils.GetLnkTargetPath(gamepath)
            uid2gamepath[uid] = exepath
            savehook_new_data[uid]["launchpath"] = gamepath
        else:
            uid2gamepath[uid] = gamepath
        trysearchforid(uid, [title] + guessmaybetitle(gamepath, title))
        return uid
    else:
        intarget = uids[0]
        index = len(targetlist)
        for uid in uids:
            if uid in targetlist:
                thisindex = targetlist.index(uid)
                if thisindex < index:
                    index = thisindex
                    intarget = uid
        return intarget


def is_port_listening(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        print_exc()
        return False


def stringfyerror(e: Exception):
    if e.args and isinstance(e.args[0], requests.Response):
        from myutils.commonbase import maybejson

        return "{} {}: {}".format(
            e.args[0].status_code,
            e.args[0].reason,
            str(maybejson(e.args[0])).replace("\n", " ").replace("\r", ""),
        )
    error = str(type(e))[8:-2] + " " + str(e)
    if len(error.splitlines()) > 5:
        error = error.replace("\n", " ").replace("\r", "")

    if isinstance(e, requests.RequestException):
        error = _TR("网络错误") + ": " + error
        if e.proxy:
            try:
                hostname, port = e.proxy.split(":")
                if not is_port_listening(hostname, int(port)):
                    error += "\n" + _TR(
                        "使用的网络代理可能无效，请进行检查！({})"
                    ).format(e.proxy)
            except:
                print_exc()
    return error


def checkportavailable(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(("localhost", port))
        return True
    except OSError:
        return False
    finally:
        sock.close()


def splittranslatortypes():
    class __:
        def __init__(self):
            self.pre, self.offline, self.free, self.api = [], [], [], []
            self.other = []

    ls = __()
    for k in globalconfig["fanyi"]:
        {
            "pre": ls.pre,
            "offline": ls.offline,
            "free": ls.free,
            "api": ls.api,
            "other": ls.other,
        }.get(globalconfig["fanyi"][k].get("type", "free"), ls.free).append(k)

    return ls


def splitocrtypes(dic, other=False):
    offline, online, other = [], [], []
    for k in dic:
        try:
            {"online": online, "offline": offline, "other": other}[
                dic[k].get("type", "online")
            ].append(k)
        except:
            pass
    if other:
        return offline, online, other
    return offline, online


def selectdebugfile(path: str, ismypost=False, ishotkey=False, istts=False):
    if ismypost or istts:
        p = gobject.getconfig("posts/{}.py".format(path))
    else:
        p = gobject.getconfig(path)
    if not os.path.exists(p):
        if istts:
            tgt = "mypost_tts.py"
        elif ismypost:
            tgt = "mypost.py"
        elif ishotkey:
            tgt = "hotkey.py"
        else:
            tgt = os.path.basename(path)
        shutil.copy(
            "LunaTranslator/myutils/template/" + tgt,
            p,
        )
    NativeUtils.OpenFileEx(os.path.normpath(p))
    return p


def makehtml(text: str, show=None, docs=False) -> str:

    if (not text) or (text[0] == "/"):
        text = dynamiclink(text, docs=docs)
    if text[-8:] == "releases":
        __ = False
    elif text[-1] == "/":
        __ = False
    else:
        __ = True
    if show:
        pass
    elif __:
        show = text.split("/")[-1]
    else:
        show = text
    return '<a href="{}">{}</a>'.format(text, show)


import sqlite3


class autosql(sqlite3.Connection):

    def __del__(self):
        self.close()
        try:
            super().__del__()
        except:
            pass


def safe_escape(string: str) -> str:
    try:
        return codecs.escape_decode(bytes(string, "utf-8"))[0].decode("utf-8")
    except:
        print_exc()
        return string


def case_insensitive_replace(text: str, old: str, new: str) -> str:
    def replace_match(_):
        return new

    return re.sub(re.escape(old), replace_match, text, flags=re.IGNORECASE)


@tryprint
def parsemayberegexreplace(lst: "list[dict]", line: str) -> str:
    if not line:
        line = ""
    for fil in lst:
        regex = fil.get("regex", False)
        escape = fil.get("escape", regex)
        key = fil.get("key", "")
        value = fil.get("value", "")
        if key == "":
            continue
        if regex:
            if escape:
                line = re.sub(safe_escape(key), safe_escape(value), line)
            else:
                line = re.sub(key, value, line)
        else:
            if escape:
                line = line.replace(safe_escape(key), safe_escape(value))
            else:
                line = line.replace(key, value)

    return line


def checklangisusing(langs):
    if langs is None:
        return True
    elif isinstance(langs, list):
        return getlanguse() in langs
    elif isinstance(langs, str):
        return getlanguse() == langs
    raise Exception(langs)


def checkpostlangmatch(name):
    for item in static_data["transoptimi"]:
        if name == item["name"]:
            try:
                return checklangisusing(item.get("languageuse", None))
            except:
                return True

    return False


def checkpostusing(name):
    use = globalconfig["transoptimi"][name]
    return use and checkpostlangmatch(name)


def postusewhich(name1):
    name2 = name1 + "_use"
    merge = name1 + "_merge"
    for _ in (0,):
        try:
            gameuid = gobject.base.gameuid
            if not gameuid:
                break
            if savehook_new_data[gameuid].get("transoptimi_followdefault", True):
                break
            if savehook_new_data[gameuid].get(name2, False):
                if savehook_new_data[gameuid].get(merge, False):
                    return 3
                return 2
            else:
                return 0

        except:
            print_exc()
            break
    if checkpostusing(name1):
        return 1
    else:
        return 0


def loadpostsettingwindowmethod_1(xx, name):
    checkpath = "LunaTranslator/transoptimi/{}.py".format(name)
    if os.path.exists(checkpath) == False:
        return None
    mm = "transoptimi." + name

    try:
        Process = importlib.import_module(mm).Process
        if xx:
            return tryprint(Process.get_setting_window)
        else:
            return tryprint(Process.get_setting_window_gameprivate)
    except:
        return None


loadpostsettingwindowmethod = functools.partial(loadpostsettingwindowmethod_1, True)
loadpostsettingwindowmethod_private = functools.partial(
    loadpostsettingwindowmethod_1, False
)


def loadpostsettingwindowmethod_maybe(name, parent):
    for _ in (0,):
        try:
            gameuid = gobject.base.gameuid
            if not gameuid:
                break
            if savehook_new_data[gameuid].get("transoptimi_followdefault", True):
                break
            return loadpostsettingwindowmethod_private(name)(parent, gameuid)
        except:
            print_exc()
            break
    loadpostsettingwindowmethod(name)(parent)


class unsupportkey(Exception):
    pass


def parsekeystringtomodvkcode(keystring: str, modes=False, canonlymod=False):
    keystring = keystring.upper()
    keys = []
    mode = 0
    _modes = []
    if keystring[-1] == "+":
        keys += ["+"]
        keystring = keystring[:-2]
    ksl = keystring.split("+")
    ksl = ksl + keys
    unsupports = []
    lastkey = ksl[-1]
    modkeys = ksl[:-1]
    if lastkey in vkcode_map:
        vkcode = vkcode_map[lastkey]
    else:
        if canonlymod and lastkey in mod_map:
            vkcode = None
            modkeys.append(lastkey)
        else:
            unsupports.append(lastkey)

    for k in modkeys:
        if k in mod_map:
            mode = mode | mod_map[k]
            _modes.append(mod_map[k])
        else:
            unsupports.append(k)
    if len(unsupports):
        raise unsupportkey(unsupports)
    if modes:
        mode = _modes
    return mode, vkcode


def get_time_stamp(ct=None, ms=True, forfilename=False):
    if ct is None:
        ct = time.time()
    local_time = time.localtime(ct)
    data_head = time.strftime(
        "%Y-%m-%d %H-%M-%S" if forfilename else "%Y-%m-%d %H:%M:%S", local_time
    )
    if ms and not forfilename:
        data_secs = (ct - int(ct)) * 1000
        time_stamp = "%s.%03d" % (data_head, data_secs)
        return time_stamp
    else:
        return data_head


class LRUCache:
    def __init__(self, capacity: int):
        self.cache = {}
        self.Lock = threading.Lock()
        self.capacity = capacity
        self.order = []

    def setcap(self, cap):
        with self.Lock:
            if cap == -1:
                cap = 9999999999
            self.capacity = cap
            while len(self.cache) > self.capacity:
                self.cache.popitem(last=False)

    def __get(self, key):
        if key in self.cache:
            self.order.remove(key)
            self.order.append(key)
            return self.cache[key]
        return None

    def get(self, key):
        with self.Lock:
            return self.__get(key)

    def __put(self, key, value=True) -> None:
        if not self.capacity:
            return
        if key in self.cache:
            self.order.remove(key)
        elif len(self.order) == self.capacity:
            old_key = self.order.pop(0)
            del self.cache[old_key]
        self.cache[key] = value
        self.order.append(key)

    def put(self, key, value=True) -> None:
        with self.Lock:
            self.__put(key, value)

    def test(self, key):
        with self.Lock:
            _ = self.__get(key)
            if not _:
                self.__put(key)
            return _


globalcachedmodule = {}


def getfilemd5(file: str, default="0") -> str:
    try:
        with open(file, "rb") as ff:
            bs = ff.read()
        md5 = hashlib.md5(bs).hexdigest()
        return md5
    except:
        return default


def checkmd5reloadmodule(filename: str, module: str):
    # -> isnew, option<module>
    if not os.path.exists(filename):
        # reload重新加载不存在的文件时不会报错。
        return None
    key = (filename, module)
    md5 = getfilemd5(filename)
    cachedmd5 = globalcachedmodule.get(key, {}).get("md5", None)
    if md5 != cachedmd5:
        try:
            _ = importlib.import_module(module)
            _ = importlib.reload(_)
        except ModuleNotFoundError:
            print_exc()
            return None
        # 不要捕获其他错误，缺少模块时直接跳过，只报实现错误
        # except:
        #     print_exc()
        #     return True, None
        globalcachedmodule[key] = {"md5": md5, "module": _}

        return _
    else:

        return globalcachedmodule.get(key, {}).get("module", None)


class loopbackrecorder:
    def __init__(self):
        self.capture = NativeUtils.loopbackrecorder()

    def stop(self):
        if not self.capture:
            return None
        self.capture.stop()

    def stop_save(self):
        if not self.capture:
            return None
        self.capture.stop()
        wav = self.capture.data
        if not wav:
            return None
        new, ext = bass_code_cast(wav, "wav")
        file = gobject.gettempdir(str(time.time()) + "." + ext)
        with open(file, "wb") as ff:
            ff.write(new)
        return file


def copytree(src, dst, copy_function=shutil.copy2):
    names = os.listdir(src)

    os.makedirs(dst, exist_ok=True)
    for name in names:

        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if os.path.isdir(srcname):
                copytree(srcname, dstname, copy_function)
            else:
                copy_function(srcname, dstname)
        except:
            pass


def checkv1(api_url: str):
    # 傻逼豆包大模型是非要v3，不是v1
    # 智谱AI v4
    for i in range(1, 10):
        if api_url.endswith("/v{}".format(i)):
            return api_url
        elif api_url.endswith("/v{}/".format(i)):
            return api_url[:-1]
    if api_url.endswith("/"):
        return api_url + "v1"
    else:
        return api_url + "/v1"


def createurl(url: str, checkend="/chat/completions"):
    if "openai.azure.com/openai/deployments/" in url:
        return url
    if url.endswith(checkend):
        pass
    elif url.endswith("#"):
        return url[:-1]
    else:
        ex = "/chat/completions"
        if url.endswith(ex):
            url = url[: -len(ex)]
        url = urlpathjoin(checkv1(url), checkend)
    return url


def parsecoheremodellist(proxies, apikey):
    js = requests.get(
        "https://api.cohere.com/v1/models",
        headers={"Authorization": "Bearer {}".format(apikey.strip())},
        proxies=proxies,
    )
    try:
        models = js.json()["models"]
    except:
        raise Exception(js)
    mm = []
    for m in models:
        endpoints = m["endpoints"]
        if "chat" not in endpoints:
            continue
        mm.append(m["name"])
    return sorted(mm)


def parsegeminimodellist(proxies, apikey):
    js = requests.get(
        "https://generativelanguage.googleapis.com/v1beta/models",
        params={"key": apikey},
        proxies=proxies,
    )
    try:
        models = js.json()["models"]
    except:
        raise Exception(js)
    mm = []
    for m in models:
        name: str = m["name"]
        supportedGenerationMethods: list = m["supportedGenerationMethods"]
        if "generateContent" not in supportedGenerationMethods:
            continue
        if name.startswith("models/"):
            name = name[7:]
        mm.append(name)
    return sorted(mm)


def parseclaudemodellist(proxies, apikey):
    # 它文档里有这个API，但不知道为什么我只收到404
    resp = requests.get(
        "https://api.anthropic.com/v1/models",
        headers={"anthropic-version": "2023-06-01", "X-Api-Key": apikey},
        proxies=proxies,
    )
    try:
        return sorted([_["id"] for _ in resp.json()["data"]])
    except:
        raise Exception(resp)


def common_list_models(proxies, apiurl: str, apikey: str, checkend="/chat/completions"):
    apiurl = apiurl.strip()
    apikey = apikey.strip()
    if apiurl.startswith("https://api.cohere."):
        return parsecoheremodellist(proxies, apikey)
    elif apiurl.startswith("https://generativelanguage.googleapis.com"):
        return parsegeminimodellist(proxies, apikey)
    elif apiurl.startswith("https://api.anthropic.com/v1/messages"):
        return parseclaudemodellist(proxies, apikey)
    params = dict(headers={"Authorization": "Bearer {}".format(apikey)})
    modellink = urlpathjoin(
        createurl(apiurl, checkend=checkend)[: -len(checkend) + 1], "models"
    )
    resp = requests.get(modellink, proxies=proxies, **params)
    if resp.status_code == 404:
        extra = _TR(
            "API接口地址填写错误，或者当前平台不支持自动获取模型列表。\n请检查API接口地址，或手动填写模型名。"
        )
        raise Exception(resp, extra)
    try:
        return sorted([_["id"] for _ in resp.json()["data"]])
    except:
        raise Exception(resp)


def common_create_gpt_data(config: dict, message, extrabody):
    temperature = config["Temperature"]

    data = dict(
        model=config["model"],
        messages=message,
        # n=1,
        # stop=None,
        temperature=temperature,
    )
    use_max_completion_tokens = config.get("use_max_completion_tokens", False)
    key_tokens = ("max_tokens", "max_completion_tokens")[use_max_completion_tokens]
    data.update({key_tokens: config["max_tokens"]})
    if config.get("流式输出", False):
        data.update(stream=True)
    if config.get("frequency_penalty_use", False):
        data.update(frequency_penalty=config["frequency_penalty"])
    if config.get("top_p_use", True):
        data.update(top_p=config["top_p"])
    if config.get("reasoning_effort_use", False):
        data.update(reasoning_effort=config["reasoning_effort"])
    if extrabody:
        data.update(extrabody)
    return data


def common_create_gemini_request(
    proxysession: requests.Session,
    config: dict,
    key,
    sysprompt,
    contents,
    extraheader,
    extrabody,
):
    gen_config = {
        "stopSequences": [" \n"],
        "temperature": config["Temperature"],
        "maxOutputTokens": config["max_tokens"],
        "topP": config["top_p"],
    }
    if config.get("frequency_penalty_use", False):
        gen_config.update(frequencyPenalty=config["frequency_penalty"])
    if config.get("reasoning_effort_use", False):
        # https://ai.google.dev/gemini-api/docs/thinking?hl=zh-cn#set-budget
        gen_config.update(
            thinkingConfig=dict(
                thinkingBudget={"low": 512, "medium": -1, "high": 24576, "minimal": 0}[
                    config["reasoning_effort"]
                ]
            )
        )
    model: str = config["model"]
    safety = [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_CIVIC_INTEGRITY",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_NONE",
        },
    ]
    # https://discuss.ai.google.dev/t/gemma-3-missing-features-despite-announcement/71692/13
    sys_message = (
        {"systemInstruction": {"parts": {"text": sysprompt}}} if sysprompt else {}
    )
    usingstream = config.get("流式输出", False)
    payload = {}
    payload.update(contents=contents)
    payload.update(safety_settings=safety)
    if not model.startswith("gemma-3"):
        payload.update(sys_message)
    payload.update(generationConfig=gen_config)
    payload.update(extrabody)
    res = proxysession.post(
        "https://generativelanguage.googleapis.com/v1beta/models/{}:{}".format(
            model, ["generateContent", "streamGenerateContent"][usingstream]
        ),
        headers=extraheader,
        params={"key": key},
        json=payload,
        stream=usingstream,
    )
    return res


def common_parse_normal_response_1(response: requests.Response, apiurl: str):
    try:
        js = response.json()
        if apiurl.startswith("https://api.anthropic.com/v1/messages"):
            return js["content"][0]["text"], None
        elif apiurl.startswith("https://generativelanguage.googleapis.com"):
            return js["candidates"][0]["content"]["parts"][0]["text"], None
        else:
            message: dict = js["choices"][0]["message"]
            return message["content"], message.get("reasoning")
    except:
        raise Exception(response)


def common_parse_normal_response(
    response: requests.Response, apiurl: str, hidethinking=False, splitthink=False
):
    resp, reasoning = common_parse_normal_response_1(response, apiurl)
    if hidethinking:
        # 有时，会没有<think>只有</think>比如使用prefill的时候。移除第一个</think>之前的内容
        resp = re.sub(r"([\s\S]*)</think>\n*", "", resp)
    elif splitthink:
        if reasoning:
            return reasoning, resp
        resp = re.split(r"<think>([\s\S]*)</think>", resp)
        if len(resp) == 1:
            return None, resp[0]
        _, think, resp = resp
        return think, resp
    return resp


class IDParser(HTMLParser):
    """Modified HTMLParser that isolates a tag with the specified id"""

    def __init__(self, attr, attrv):
        self.id = attr, attrv
        self.result = None
        self.started = False
        self.depth = {}
        self.html = None
        self.watch_startpos = False
        HTMLParser.__init__(self)

    def loads(self, html):
        self.html = html
        self.feed(html)
        self.close()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if self.started:
            self.find_startpos(None)
        if self.id[0] in attrs and attrs[self.id[0]] == self.id[1]:
            self.result = [tag]
            self.started = True
            self.watch_startpos = True
        if self.started:
            if not tag in self.depth:
                self.depth[tag] = 0
            self.depth[tag] += 1

    def handle_endtag(self, tag):
        if self.started:
            if tag in self.depth:
                self.depth[tag] -= 1
            if self.depth[self.result[0]] == 0:
                self.started = False
                self.result.append(self.getpos())

    def find_startpos(self, x):
        """Needed to put the start position of the result (self.result[1])
        after the opening tag with the requested id"""
        if self.watch_startpos:
            self.watch_startpos = False
            self.result.append(self.getpos())

    handle_entityref = handle_charref = handle_data = handle_comment = handle_decl = (
        handle_pi
    ) = unknown_decl = find_startpos

    def get_result(self):
        if self.result == None:
            return None
        if len(self.result) != 3:
            return None
        lines = self.html.split("\n")
        lines = lines[self.result[1][0] - 1 : self.result[2][0]]
        lines[0] = lines[0][self.result[1][1] :]
        if len(lines) == 1:
            lines[-1] = lines[-1][: self.result[2][1] - self.result[1][1]]
        lines[-1] = lines[-1][: self.result[2][1]]
        return "\n".join(lines).strip()


def get_element_by(attr, attrv, html):
    """Return the content of the tag with the specified id in the passed HTML document"""
    parser = IDParser(attr, attrv)
    parser.loads(html)
    res = parser.get_result()
    if res is None:
        return ""
    return res


def __getimageformatlist():
    _ = sorted([_.data().decode() for _ in QImageWriter.supportedImageFormats()])
    if "png" in _:
        _.remove("png")
        _.insert(0, "png")
    if "jpeg" in _:
        _.remove("jpeg")
        _.insert(0, "jpeg")
    if "jpg" in _:
        _.remove("jpg")
        _.insert(0, "jpg")
    if "webp" in _:
        _.remove("webp")
        _.insert(0, "webp")
    return _


__imageformatlist = __getimageformatlist()


def getimageformatlist():
    return __imageformatlist


def getimageformat():
    fmt = globalconfig["imageformat2"]
    __ = getimageformatlist()
    if fmt not in __:
        return __[0]
    return fmt


def getimagefilefilter():
    return " ".join(("*." + _ for _ in getimageformatlist()))


def dynamiccishuname(apiuid):
    return globalconfig["cishu"][apiuid].get(
        "name_self_set", globalconfig["cishu"][apiuid]["name"]
    )


def getannotatedapiname(x):
    tp = globalconfig["fanyi"][x].get("type", "free")
    is_gpt_like = globalconfig["fanyi"][x].get("is_gpt_like", False)
    return (
        dynamicapiname(x)
        + "_("
        + {
            "free": "传统",
            "api": ("传统_API", "大模型")[is_gpt_like],
            "pre": "预翻译",
            "offline": ("过时的", "大模型_离线翻译")[is_gpt_like],
        }.get(tp, "unknown type")
        + ")"
    )


def inrange(n, s, e):
    return n >= s and n <= e


def inranges(n, *argc):
    for s, e in argc:
        if inrange(n, s, e):
            return True
    return False


def cinranges(n, *argc):
    return inranges(ord(n), *argc)


def is_ascii_symbo(c: str):
    return cinranges(c, (0x21, 0x2F), (0x3A, 0x40), (0x5B, 0x60), (0x7B, 0x7E))


def is_ascii_control(c: str):
    # 不要管\r\n
    return cinranges(c, (0, 0x9), (0xB, 0xC), (0xE, 0x1F), (0x7F, 0xA0))
