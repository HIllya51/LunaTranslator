import windows
import os, time
import codecs, hashlib
import os, time
import socket, gobject, uuid
import ctypes, importlib
import time
import ctypes.wintypes
import time
from qtsymbols import *
from traceback import print_exc
from myutils.config import (
    globalconfig,
    static_data,
    getlanguse,
    savehook_new_data,
    uid2gamepath,
    gamepath2uid,
    getdefaultsavehook,
)
from ctypes import c_float, pointer, c_void_p
import threading
import re, heapq, winsharedutils
from myutils.wrapper import tryprint


def __internal__getlang(k1, k2):
    try:
        for _ in (0,):

            if not gobject.baseobject.textsource:
                break

            gameuid = gobject.baseobject.textsource.gameuid
            if not gameuid:
                break
            if savehook_new_data[gameuid]["lang_follow_default"]:
                break

            return static_data["language_list_translator_inner"][
                savehook_new_data[gameuid][k1]
            ]
    except:
        pass
    return static_data["language_list_translator_inner"][globalconfig[k2]]


def getlangsrc():
    return __internal__getlang("private_srclang", "srclang3")


def getlangtgt():

    return __internal__getlang("private_tgtlang", "tgtlang3")


def findenclose(text, tag):
    i = 0
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


searchvndbqueue = PriorityQueue()


def guessmaybetitle(gamepath, title):

    __t = []

    print(gamepath)
    for _ in [
        title,
        os.path.basename(os.path.dirname(gamepath)),
        os.path.basename(gamepath)[:-4],
    ]:
        if not title:
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
    return lst


targetmod = {}


def trysearchforid(gameuid, searchargs: list):
    infoid = None
    primitivtemetaorigin = globalconfig["primitivtemetaorigin"]
    __ = list(targetmod.keys())
    if primitivtemetaorigin not in __:
        primitivtemetaorigin = __[0]
    __.remove(primitivtemetaorigin)
    __.insert(0, primitivtemetaorigin)

    for key in __:
        vid = None
        for arg in searchargs:
            vid = targetmod[key].getidbytitle(arg)
            if vid:
                break
        if not vid:
            continue
        idname = globalconfig["metadata"][key]["target"]
        savehook_new_data[gameuid][idname] = vid
        if infoid is None or key == primitivtemetaorigin:
            infoid = key, vid
            if key == primitivtemetaorigin:
                break
    if infoid:
        searchvndbqueue.put((1, gameuid, infoid))
        return infoid


def everymethodsthread():
    while True:
        _ = searchvndbqueue.get()
        _type, gameuid, arg = _
        try:
            if _type == 0:
                infoid = trysearchforid(gameuid, arg)
                key, vid = infoid
                gobject.baseobject.translation_ui.displayglobaltooltip.emit(
                    f"{key}: found {vid}"
                )

            elif _type == 1:
                key, vid = arg
                targetmod[key].dispatchsearchfordata(gameuid, vid)

        except:
            print_exc()


def idtypecheck(key, idname, gameuid, vid):
    if vid == "":
        return

    try:
        if globalconfig["metadata"][key].get("idtype", 1) == 0:
            try:
                vid = int(vid)
            except:
                print(vid)
                return
        savehook_new_data[gameuid][idname] = vid
    except:
        print_exc()


def gamdidchangedtask(key, idname, gameuid):
    vid = savehook_new_data[gameuid][idname]
    searchvndbqueue.put((1, gameuid, (key, vid)), 1)


def titlechangedtask(gameuid, title):
    savehook_new_data[gameuid]["title"] = title
    savehook_new_data[gameuid]["istitlesetted"] = True
    searchvndbqueue.put((0, gameuid, [title]), 1)


def initanewitem(gamepath, title):
    uid = f"{time.time()}_{uuid.uuid4()}"
    gamepath2uid[gamepath] = uid
    savehook_new_data[uid] = getdefaultsavehook(gamepath, title)
    uid2gamepath[uid] = gamepath
    return uid


def checkifnewgame(targetlist, gamepath, title=None):
    if gamepath not in gamepath2uid:
        uid = initanewitem(gamepath, title)
        searchvndbqueue.put((0, uid, [title] + guessmaybetitle(gamepath, title)))
    else:
        uid = gamepath2uid[gamepath]
    isnew = uid not in targetlist
    if isnew:
        targetlist.insert(0, uid)
        return uid
    else:
        return None


kanjichs2ja = str.maketrans(static_data["kanjichs2ja"])


def kanjitrans(k):
    return k.translate(kanjichs2ja)


def stringfyerror(e):
    return str(type(e))[8:-2] + " " + str(e).replace("\n", "").replace("\r", "")


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
    pre, offline, free, dev, api = set(), set(), set(), set(), set()
    for k in globalconfig["fanyi"]:
        try:
            {"pre": pre, "offline": offline, "free": free, "dev": dev, "api": api}[
                globalconfig["fanyi"][k].get("type", "free")
            ].add(k)
        except:
            pass

    return offline, pre, free, dev, api


def argsort(l):
    ll = list(range(len(l)))
    ll.sort(key=lambda x: l[x])
    return ll


class wavmp3player:
    def __init__(self):
        self.i = 0
        self.lastfile = None
        self.tasks = None
        self.lock = threading.Lock()
        self.lock.acquire()
        threading.Thread(target=self.dotasks).start()

    def mp3playfunction(self, binary, volume, force):
        try:
            self.tasks = (binary, volume, force)
            self.lock.release()
        except:
            pass

    def dotasks(self):
        durationms = 0
        try:
            while True:
                self.lock.acquire()
                task = self.tasks
                self.tasks = None
                if task is None:
                    continue
                binary, volume, force = task
                durationms = self._playsoundWin(binary, volume)

                if durationms and globalconfig["ttsnointerrupt"]:
                    while durationms > 0:
                        durationms -= 100
                        time.sleep(0.1)
                        if self.tasks and self.tasks[-1]:
                            break
        except:
            print_exc()

    def _playsoundWin(self, binary, volume):
        try:
            if self.lastfile:
                winsharedutils.PlayAudioInMem_Stop(self.lastfile[0], self.lastfile[1])
            duration = c_float()
            device = c_void_p()
            decoder = c_void_p()
            succ = winsharedutils.PlayAudioInMem(
                binary,
                len(binary),
                volume / 100,
                pointer(decoder),
                pointer(device),
                pointer(duration),
            )
            if succ != 0:
                return 0
            self.lastfile = decoder, device
            durationms = duration.value * 1000
        except:
            durationms = 0

        return durationms


def selectdebugfile(path: str, ismypost=False):
    if ismypost:
        path = f"./userconfig/posts/{path}.py"
    p = os.path.abspath((path))
    os.makedirs(os.path.dirname(p), exist_ok=True)

    if os.path.exists(p) == False:
        with open(p, "w", encoding="utf8") as ff:
            if path == "./userconfig/selfbuild.py":
                ff.write(
                    """
import requests
from translator.basetranslator import basetrans
class TS(basetrans): 
    def translate(self,content):  
        #在这里编写
        return content
"""
                )
            elif path == "./userconfig/mypost.py" or ismypost:
                ff.write(
                    """
def POSTSOLVE(line): 
    #请在这里编写自定义处理
    return line
"""
                )
            elif path == "./userconfig/myprocess.py":
                ff.write(
                    """
class Process:
    def process_before(self, text):
        context = {}
        return text, context

    def process_after(self, res, context):
        return res
    
    @staticmethod
    def get_setting_window(parent_window):
        pass
"""
                )
    os.startfile(p)
    return p


def checkchaos(text):
    code = globalconfig["accept_encoding"]

    text = filter(lambda x: x not in globalconfig["accept_character"], text)

    if globalconfig["accept_use_unicode"]:
        _start = globalconfig["accept_use_unicode_start"]
        _end = globalconfig["accept_use_unicode_end"]
        chaos = False
        for ucode in map(lambda x: ord(x), text):
            print(ucode, _start, _end)
            if ucode < _start or ucode > _end:
                chaos = True
                break
    else:
        chaos = True
        text = "".join(text)
        for c in code:
            try:
                text.encode(c)
                chaos = False
                break
            except:
                pass
        return chaos


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
            if gobject.baseobject.textsource is None:
                return
            if gobject.baseobject.textsource.hwnd == 0:
                return

            _focusp = windows.GetWindowThreadProcessId(hwnd)
            if event == windows.EVENT_SYSTEM_FOREGROUND:
                if globalconfig["keepontop"] and globalconfig["focusnotop"]:
                    if _focusp == os.getpid():
                        pass
                    else:
                        hwndmagpie = windows.FindWindow(
                            "Window_Magpie_967EB565-6F73-4E94-AE53-00CC42592A22", None
                        )
                        hwndlossless = windows.FindWindow("LosslessScaling", None)
                        if (
                            len(gobject.baseobject.textsource.pids) == 0
                            or _focusp in gobject.baseobject.textsource.pids
                            or hwnd == hwndmagpie
                            or hwnd == hwndlossless
                        ):
                            gobject.baseobject.translation_ui.thistimenotsetop = False
                            gobject.baseobject.translation_ui.settop()
                        else:
                            gobject.baseobject.translation_ui.thistimenotsetop = True
                            if gobject.baseobject.translation_ui.istopmost():
                                gobject.baseobject.translation_ui.canceltop()
            if _focusp != windows.GetWindowThreadProcessId(
                gobject.baseobject.textsource.hwnd
            ):
                return

            rect = windows.GetWindowRect(hwnd)
            if event == windows.EVENT_SYSTEM_MOVESIZESTART:  #
                self.lastpos = rect
            elif event == windows.EVENT_SYSTEM_MOVESIZEEND:  #
                if globalconfig["movefollow"]:
                    if self.lastpos:
                        rate = QApplication.instance().devicePixelRatio()
                        self.hookfollowsignal.emit(
                            5,
                            (
                                int((rect[0] - self.lastpos[0]) / rate),
                                int((rect[1] - self.lastpos[1]) / rate),
                            ),
                        )

        except:
            print_exc()

    win_event_callback_cfunc = WinEventProcType(win_event_callback)

    eventpairs = (
        (windows.EVENT_SYSTEM_MOVESIZESTART, windows.EVENT_SYSTEM_MOVESIZEEND),
        (windows.EVENT_SYSTEM_FOREGROUND, windows.EVENT_SYSTEM_FOREGROUND),
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


def makehtml(text, base=False, show=None):
    if base:
        show = text.split("/")[-1]
    elif show:
        pass
    else:
        show = text
    return '<a href="{}">{}</a>'.format(text, show)


import sqlite3


class autosql(sqlite3.Connection):
    def __new__(cls, v) -> None:
        return v

    def __del__(self):
        self.close()


def parsemayberegexreplace(dict, res):
    for item in dict:
        if item["regex"]:
            res = re.sub(
                codecs.escape_decode(bytes(item["key"], "utf-8"))[0].decode("utf-8"),
                codecs.escape_decode(bytes(item["value"], "utf-8"))[0].decode("utf-8"),
                res,
            )
        else:
            if (
                res.isascii()
                and item["key"].isascii()
                and item["value"].isascii()
                and (" " not in item["key"])
            ):  # 目标可能有空格
                resx = res.split(" ")
                for i in range(len(resx)):
                    if resx[i] == item["key"]:
                        resx[i] = item["value"]
                res = " ".join(resx)
            else:
                res = res.replace(item["key"], item["value"])
    return res


def checkpostlangmatch(name):
    for item in static_data["transoptimi"]:
        if name == item["name"]:
            try:
                return getlanguse() == item["languageuse"]
            except:
                return True

    return False


def checkpostusing(name):
    use = globalconfig["transoptimi"][name]
    return use and checkpostlangmatch(name)


def getpostfile(name):
    if name == "myprocess":
        mm = "myprocess"
        checkpath = "./userconfig/myprocess.py"
    else:
        mm = "transoptimi." + name
        checkpath = "./LunaTranslator/transoptimi/" + name + ".py"
    if os.path.exists(checkpath) == False:
        return None
    return mm


def loadpostsettingwindowmethod(name):
    if name == "myprocess":
        return lambda _: selectdebugfile("./userconfig/myprocess.py")
    mm = getpostfile(name)
    if not mm:
        return None

    try:
        Process = importlib.import_module(mm).Process
        return tryprint(Process.get_setting_window)
    except:
        return None


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


def get_time_stamp():
    ct = time.time()
    local_time = time.localtime(ct)
    data_head = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
    data_secs = (ct - int(ct)) * 1000
    time_stamp = "%s.%03d" % (data_head, data_secs)
    return time_stamp


class LRUCache:
    def __init__(self, capacity: int):
        self.cache = {}
        self.capacity = capacity
        self.order = []

    def setcap(self, cap):
        if cap == -1:
            cap = 9999999999
        self.capacity = cap
        while len(self.cache) > self.capacity:
            self.cache.popitem(last=False)

    def get(self, key: int) -> bool:
        if key in self.cache:
            self.order.remove(key)
            self.order.append(key)
            return True
        return False

    def put(self, key: int) -> None:
        if not self.capacity:
            return
        if key in self.cache:
            self.order.remove(key)
        elif len(self.order) == self.capacity:
            old_key = self.order.pop(0)
            del self.cache[old_key]
        self.cache[key] = None
        self.order.append(key)

    def test(self, key):
        _ = self.get(key)
        if not _:
            self.put(key)
        return _


for k in globalconfig["metadata"]:
    try:
        targetmod[k] = importlib.import_module(f"metadata.{k}").searcher(k)
    except:
        print_exc()


threading.Thread(target=everymethodsthread).start()
