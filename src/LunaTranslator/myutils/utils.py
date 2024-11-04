import windows
import os, time
import codecs, hashlib, shutil
import socket, gobject, uuid, subprocess, functools
import ctypes, importlib, json
import ctypes.wintypes
from qtsymbols import *
from string import Formatter
from ctypes import CDLL, c_void_p, CFUNCTYPE, c_size_t, cast, c_char, POINTER
from ctypes.wintypes import HANDLE
from traceback import print_exc
from myutils.config import (
    globalconfig,
    static_data,
    getlanguse,
    uid2gamepath,
    savehook_new_data,
    findgameuidofpath,
    getdefaultsavehook,
    gamepath2uid_index,
)
import threading, winreg
import re, heapq, winsharedutils
from myutils.wrapper import tryprint, threader
from html.parser import HTMLParser


def qimage2binary(qimage: QImage, fmt="BMP"):
    byte_array = QByteArray()
    buffer = QBuffer(byte_array)
    buffer.open(QBuffer.OpenModeFlag.WriteOnly)
    qimage.save(buffer, fmt)
    buffer.close()
    image_data = byte_array.data()
    return image_data


def checkisusingwine():
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


def __internal__getlang(k1, k2):
    try:
        for _ in (0,):
            gameuid = gobject.baseobject.gameuid
            if not gameuid:
                break
            if savehook_new_data[gameuid]["lang_follow_default"]:
                break

            return savehook_new_data[gameuid][k1]
    except:
        pass
    return globalconfig[k2]


def translate_exits(fanyi, which=False):
    _fs = [
        "./Lunatranslator/translator/{}.py".format(fanyi),
        "./userconfig/copyed/{}.py".format(fanyi),
    ]
    if not which:
        if all([not os.path.exists(_) for _ in _fs]):
            return False
        return True
    else:
        for i, _ in enumerate(_fs):
            if os.path.exists(_):
                return i
        return None


def getlangsrc():
    return __internal__getlang("private_srclang_2", "srclang4")


def getlangtgt():

    return __internal__getlang("private_tgtlang_2", "tgtlang4")


def getlanguagespace(lang=None):
    if lang is None:
        lang = getlanguse()
    return "" if (lang in ("zh", "ja", "cht")) else " "


def findenclose(text, tag):
    i = 0
    if tag == "link":
        tags = "<link"
        tage = ">"
    else:
        tags = f"<{tag}"
        tage = f"</{tag}>"
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
            collect += text[0]
            text = text[1:]
        if i == 0:
            break

    return collect


def simplehtmlparser(text, tag, sign):
    text = text[text.find(sign) :]
    inner = findenclose(text, tag)
    return inner


def simplehtmlparser_all(text, tag, sign):
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


def nowisdark():
    dl = globalconfig["darklight2"]
    if dl == 1:
        dark = False
    elif dl == 2:
        dark = True
    elif dl == 0:
        dark = winsharedutils.isDark()
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


def trysearchforid_1(gameuid, searchargs: list, target=None):
    infoid = None
    if target is None:
        primitivtemetaorigin = globalconfig["primitivtemetaorigin"]
        __ = []
        if primitivtemetaorigin:
            __.append(primitivtemetaorigin)
        for k in targetmod:
            if k == primitivtemetaorigin:
                continue
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
        gobject.baseobject.translation_ui.displayglobaltooltip.emit(
            f"{key}: found {vid}"
        )
        if infoid is None or key == primitivtemetaorigin:
            infoid = key, vid
    if infoid:
        key, vid = infoid
        dispatchsearchfordata(gameuid, key, vid)


def trysearchforid(*argc):
    threading.Thread(target=trysearchforid_1, args=argc).start()


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
    uid = f"{time.time()}_{uuid.uuid4()}"
    savehook_new_data[uid] = gamepath2uid_index_helper(getdefaultsavehook(title), uid)
    return uid


def duplicateconfig(uidold):
    uid = f"{time.time()}_{uuid.uuid4()}"
    savehook_new_data[uid] = json.loads(json.dumps(savehook_new_data[uidold]))
    return uid


def find_or_create_uid(targetlist, gamepath, title=None):
    uids = findgameuidofpath(gamepath, findall=True)
    if len(uids) == 0:
        uid = initanewitem(title)
        if title is None:
            savehook_new_data[uid]["title"] = (
                os.path.basename(os.path.dirname(gamepath))
                + "/"
                + os.path.basename(gamepath)
            )
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


kanjichs2ja = str.maketrans(static_data["kanjichs2ja"])


def kanjitrans(k):
    return k.translate(kanjichs2ja)


def stringfyerror(e):
    return str(type(e))[8:-2] + " " + str(e).replace("\n", " ").replace("\r", "")


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
    pre, offline, free, dev, api = [], [], [], [], []
    for k in globalconfig["fanyi"]:
        try:
            {"pre": pre, "offline": offline, "free": free, "dev": dev, "api": api}[
                globalconfig["fanyi"][k].get("type", "free")
            ].append(k)
        except:
            pass

    return offline, pre, free, dev, api


def splitocrtypes(dic):
    offline, online = [], []
    for k in dic:
        try:
            {"online": online, "offline": offline}[dic[k].get("type", "online")].append(
                k
            )
        except:
            pass

    return offline, online


def argsort(l):
    ll = list(range(len(l)))
    ll.sort(key=lambda x: l[x])
    return ll


def selectdebugfile(path: str, ismypost=False):
    if ismypost:
        path = f"./userconfig/posts/{path}.py"
    p = os.path.abspath((path))
    os.makedirs(os.path.dirname(p), exist_ok=True)
    print(path)
    if os.path.exists(p) == False:
        tgt = {
            "./userconfig/selfbuild.py": "selfbuild.py",
            "./userconfig/mypost.py": "mypost.py",
            "./userconfig/myprocess.py": "myprocess.py",
        }.get(path)
        if ismypost:
            tgt = "mypost.py"
        shutil.copy(
            "LunaTranslator/myutils/template/" + tgt,
            p,
        )
    threading.Thread(
        target=subprocess.run, args=(f'notepad "{os.path.normpath(p)}"',)
    ).start()
    return p


def checkencoding(code):

    try:
        codecs.lookup(code)
        return True
    except LookupError:
        return False


def getfilemd5(file, default="0"):
    try:
        with open(file, "rb") as ff:
            bs = ff.read(1024 * 1024 * 32)  # 32mb，有些游戏会把几个G打包成单文件
        md5 = hashlib.md5(bs).hexdigest()
        return md5
    except:
        return default


def minmaxmoveobservefunc(self):

    user32 = ctypes.windll.user32

    WinEventProcType = ctypes.CFUNCTYPE(
        None,
        ctypes.wintypes.HANDLE,
        ctypes.wintypes.DWORD,
        ctypes.wintypes.HWND,
        ctypes.wintypes.LONG,
        ctypes.wintypes.LONG,
        ctypes.wintypes.DWORD,
        ctypes.wintypes.DWORD,
    )
    self.lastpos = None

    def win_event_callback(
        hWinEventHook, event, hwnd, idObject, idChild, dwEventThread, dwmsEventTime
    ):
        try:
            myhwnd = gobject.baseobject.hwnd
            if not myhwnd:
                return
            if (
                event == windows.EVENT_OBJECT_DESTROY
                and idObject == windows.OBJID_WINDOW
            ):
                if hwnd == myhwnd:
                    gobject.baseobject.hwnd = None
                    return
            p_pids = windows.GetWindowThreadProcessId(myhwnd)
            if not p_pids:
                # 有时候谜之没有EVENT_OBJECT_DESTROY/僵尸进程
                gobject.baseobject.hwnd = None
                return
            _focusp = windows.GetWindowThreadProcessId(hwnd)
            if event != windows.EVENT_SYSTEM_FOREGROUND:
                return
            if not (globalconfig["keepontop"] and globalconfig["focusnotop"]):
                return
            if _focusp == os.getpid():
                return
            if windows.FindWindow(
                "Window_Magpie_967EB565-6F73-4E94-AE53-00CC42592A22", None
            ):
                return
            if _focusp == p_pids:
                gobject.baseobject.translation_ui.thistimenotsetop = False
                gobject.baseobject.translation_ui.settop()
            else:
                gobject.baseobject.translation_ui.thistimenotsetop = True
                gobject.baseobject.translation_ui.canceltop()
                windows.SetWindowPos(
                    hwnd,
                    windows.HWND_TOP,
                    0,
                    0,
                    0,
                    0,
                    windows.SWP_NOACTIVATE | windows.SWP_NOSIZE | windows.SWP_NOMOVE,
                )

        except:
            print_exc()

    win_event_callback_cfunc = WinEventProcType(win_event_callback)

    eventpairs = (
        (windows.EVENT_SYSTEM_FOREGROUND, windows.EVENT_SYSTEM_FOREGROUND),
        (windows.EVENT_OBJECT_DESTROY, windows.EVENT_OBJECT_DESTROY),
    )

    def _():
        for pair in eventpairs:
            hook_id = user32.SetWinEventHook(
                pair[0], pair[1], 0, win_event_callback_cfunc, 0, 0, 0
            )

        msg = ctypes.wintypes.MSG()
        while ctypes.windll.user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
            ctypes.windll.user32.TranslateMessage(ctypes.byref(msg))
            ctypes.windll.user32.DispatchMessageW(ctypes.byref(msg))

        ctypes.windll.user32.UnhookWindowsHookEx(hook_id)

    _()


def dynamiclink(text):
    return text.format(
        main_server=static_data["main_server"][gobject.serverindex],
        docs_server=static_data["docs_server"][gobject.serverindex],
    )


def makehtml(text, show=None):

    if text[-8:] == "releases":
        __ = False
    elif text[-1] == "/":
        __ = False
    else:
        __ = True
    text = dynamiclink(text)
    if show:
        pass
    elif __:
        show = text.split("/")[-1]
    else:
        show = text
    return '<a href="{}">{}</a>'.format(text, show)


import sqlite3


class autosql(sqlite3.Connection):
    def __new__(cls, v) -> None:
        return v

    def __del__(self):
        self.close()


def safe_escape(string: str):
    try:
        return codecs.escape_decode(bytes(string, "utf-8"))[0].decode("utf-8")
    except:
        print_exc()
        return string


def case_insensitive_replace(text, old, new):
    def replace_match(_):
        return new

    return re.sub(re.escape(old), replace_match, text, flags=re.IGNORECASE)


@tryprint
def parsemayberegexreplace(lst: list, line: str):
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
            gameuid = gobject.baseobject.gameuid
            if not gameuid:
                break
            if savehook_new_data[gameuid]["transoptimi_followdefault"]:
                break
            if savehook_new_data[gameuid][name2]:
                if savehook_new_data[gameuid][merge]:
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
    checkpath = "./LunaTranslator/transoptimi/" + name + ".py"
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
            gameuid = gobject.baseobject.gameuid
            if not gameuid:
                break
            return loadpostsettingwindowmethod_private(name)(parent, gameuid)
        except:
            print_exc()
            break
    loadpostsettingwindowmethod(name)(parent)


class unsupportkey(Exception):
    pass


def parsekeystringtomodvkcode(keystring, modes=False):
    keys = []
    mode = 0
    _modes = []
    if keystring[-1] == "+":
        keys += ["+"]
        keystring = keystring[:-2]
    ksl = keystring.split("+")
    ksl = ksl + keys
    unsupports = []
    if ksl[-1].upper() in static_data["vkcode_map"]:
        vkcode = static_data["vkcode_map"][ksl[-1].upper()]
    else:
        unsupports.append(ksl[-1])

    for k in ksl[:-1]:
        if k.upper() in static_data["mod_map"]:
            mode = mode | static_data["mod_map"][k.upper()]
            _modes.append(static_data["mod_map"][k.upper()])
        else:
            unsupports.append(k)
    if len(unsupports):
        raise unsupportkey(unsupports)
    if modes:
        mode = _modes
    return mode, vkcode


def str2rgba(string, alpha100):
    return "rgba(%s, %s, %s, %s)" % (
        int(string[1:3], 16),
        int(string[3:5], 16),
        int(string[5:7], 16),
        alpha100 / 100,
    )


def get_time_stamp(ct=None, ms=True):
    if ct is None:
        ct = time.time()
    local_time = time.localtime(ct)
    data_head = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
    if ms:
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


def checkmd5reloadmodule(filename, module):
    if not os.path.exists(filename):
        # reload重新加载不存在的文件时不会报错。
        return True, None
    key = (filename, module)
    md5 = getfilemd5(filename)
    cachedmd5 = globalcachedmodule.get(key, {}).get("md5", None)
    if md5 != cachedmd5:
        try:
            _ = importlib.import_module(module)
            _ = importlib.reload(_)
        except ModuleNotFoundError:
            return True, None
        # 不要捕获其他错误，缺少模块时直接跳过，只报实现错误
        # except:
        #     print_exc()
        #     return True, None
        globalcachedmodule[key] = {"md5": md5, "module": _}

        return True, _
    else:

        return False, globalcachedmodule.get(key, {}).get("module", None)


class audiocapture:
    def __datacollect(self, ptr, size):
        self.data = cast(ptr, POINTER(c_char))[:size]
        self.stoped.release()

    def __mutexcb(self, mutex):
        self.mutex = mutex

    def stop(self):
        _ = self.mutex
        if _:
            self.mutex = None
            self.StopCaptureAsync(_)
            self.stoped.acquire()
        _ = self.data
        self.data = None
        return _

    def __del__(self):
        self.stop()

    def __init__(self) -> None:

        loopbackaudio = CDLL(gobject.GetDllpath("loopbackaudio.dll"))
        StartCaptureAsync = loopbackaudio.StartCaptureAsync
        StartCaptureAsync.argtypes = c_void_p, c_void_p
        StartCaptureAsync.restype = HANDLE
        StopCaptureAsync = loopbackaudio.StopCaptureAsync
        StopCaptureAsync.argtypes = (HANDLE,)
        self.StopCaptureAsync = StopCaptureAsync
        self.mutex = None
        self.stoped = threading.Lock()
        self.stoped.acquire()
        self.data = None
        self.cb1 = CFUNCTYPE(None, c_void_p, c_size_t)(self.__datacollect)
        self.cb2 = CFUNCTYPE(None, c_void_p)(self.__mutexcb)
        threading.Thread(target=StartCaptureAsync, args=(self.cb1, self.cb2)).start()


class loopbackrecorder:
    def __init__(self):
        try:
            self.capture = audiocapture()
        except:
            self.capture = None

    @threader
    def end(self, callback):
        if not self.capture:
            return callback("")
        wav = self.capture.stop()
        if not wav:
            return callback("")
        mp3 = winsharedutils.encodemp3(wav)
        if not mp3:
            file = gobject.gettempdir(str(time.time()) + ".wav")
            with open(file, "wb") as ff:
                ff.write(wav)
            callback(file)
        else:
            file = gobject.gettempdir(str(time.time()) + ".mp3")
            with open(file, "wb") as ff:
                ff.write(mp3)
            callback(file)


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


class SafeFormatter(Formatter):
    def format(self, format_string, must_exists=None, *args, **kwargs):
        if must_exists:
            check = "{" + must_exists + "}"
            if check not in format_string:
                format_string += check

        return super().format(format_string, *args, **kwargs)

    def get_value(self, key, args, kwargs):
        if key in kwargs:
            return super().get_value(key, args, kwargs)
        else:
            print(f"{key} is missing")
            return key


def checkv1(api_url: str):
    # 傻逼豆包大模型是非要v3，不是v1
    # 智谱AI v4
    for i in range(1, 10):
        if api_url.endswith(f"/v{i}"):
            return api_url
        elif api_url.endswith(f"/v{i}/"):
            return api_url[:-1]
    if api_url.endswith("/"):
        return api_url + "v1"
    else:
        return api_url + "/v1"


def urlpathjoin(*argc):
    urlx = []
    for i, u in enumerate(argc):
        if u.startswith("/") and i != 0:
            u = u[1:]
        if u.endswith("/") and i != len(argc) - 1:
            u = u[:-1]
        urlx.append(u)
    return "/".join(urlx)


def createurl(url: str):
    if url.endswith("/chat/completions"):
        pass
    else:
        url = urlpathjoin(checkv1(url), "/chat/completions")
    return url


def createenglishlangmap():
    mp = dict(
        zip(
            [_["code"] for _ in static_data["lang_list_all"]],
            [_["en"] for _ in static_data["lang_list_all"]],
        )
    )
    mp.update({"auto": ""})
    return mp


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


def getimageformatlist():
    _ = [_.data().decode() for _ in QImageWriter.supportedImageFormats()]
    if globalconfig["imageformat"] == -1 or globalconfig["imageformat"] >= len(_):
        globalconfig["imageformat"] = _.index("png")
    return _


def getimagefilefilter():
    return " ".join(("*." + _ for _ in getimageformatlist()))


def dynamicapiname(apiuid):
    return globalconfig["fanyi"][apiuid].get(
        "name_self_set", globalconfig["fanyi"][apiuid]["name"]
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
    return cinranges(c, (0, 0x1F), (0x7F, 0xA0))


def checkchaos(text):
    code = globalconfig["accept_encoding"]
    text = filter(lambda x: x not in globalconfig["accept_character"], text)

    if globalconfig["accept_use_unicode"]:
        _start = globalconfig["accept_use_unicode_start"]
        _end = globalconfig["accept_use_unicode_end"]
        return not all(cinranges(c, (_start, _end)) for c in text)
    else:
        text = "".join(text)
        for c in code:
            try:
                text.encode(c)
                return False
            except:
                pass
        return True
