import windows
import os, time
from traceback import print_exc
import codecs, hashlib
import os, time
import socket, gobject
import ctypes
import time
import ctypes.wintypes
import time
from myutils.hwnd import getScreenRate
from traceback import print_exc
from myutils.config import (
    globalconfig,
    static_data,
    savehook_new_list,
    savehook_new_data,
    getdefaultsavehook,
)
import threading, queue
import re
from myutils.vndb import searchforidimage


def checkimage(gamepath):
    return (savehook_new_data[gamepath]["imagepath"] is None) or (
        os.path.exists(savehook_new_data[gamepath]["imagepath"]) == False
    )


def checkinfo(gamepath):
    return (savehook_new_data[gamepath]["infopath"] is None) or (
        (savehook_new_data[gamepath]["infopath"][:4].lower() != "http")
        and os.path.exists(savehook_new_data[gamepath]["infopath"]) == False
    )


def checkvid(gamepath):
    if savehook_new_data[gamepath]["vid"]:
        return checkimage(gamepath) or checkinfo(gamepath)
    else:
        return (
            time.time() - savehook_new_data[gamepath]["searchnoresulttime"]
            > 3600 * 24 * 7
        )


def checkneed(gamepath):
    return (gamepath in savehook_new_data) and (checkvid(gamepath))


searchvndbqueue = queue.Queue()


def dispatachtask(gamepath):
    if checkneed(gamepath) == False:
        return
    __t = []
    if savehook_new_data[gamepath]["vid"]:
        searchvndbqueue.put((gamepath, [savehook_new_data[gamepath]["vid"]]))
    else:
        for _ in [
            savehook_new_data[gamepath]["title"],
            os.path.basename(os.path.dirname(gamepath)),
            os.path.basename(gamepath)[:-4],
        ]:
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
        searchvndbqueue.put((gamepath, lst))


def everymethodsthread():
    while True:
        gamepath, searchargs = searchvndbqueue.get()

        if checkneed(gamepath) == False:
            continue
        print(gamepath)
        succ = False
        for searcharg in searchargs:
            try:
                data = searchforidimage(searcharg)
            except:
                print_exc()
                continue
            saveimg = data.get("imagepath", None)
            saveinfo = data.get("infopath", None)
            vid = data.get("vid", None)
            print(data)
            if not vid:
                continue
            savehook_new_data[gamepath]["vid"] = int(vid[1:])
            if checkimage(gamepath):
                savehook_new_data[gamepath]["imagepath"] = saveimg
            savehook_new_data[gamepath]["infopath"] = saveinfo
            succ = True
            break
        if succ == False:
            savehook_new_data[gamepath]["searchnoresulttime"] = time.time()


threading.Thread(target=everymethodsthread).start()


def checkifnewgame(gamepath, title=None):
    if gamepath not in savehook_new_list:
        savehook_new_list.insert(0, gamepath)
    if gamepath not in savehook_new_data:
        savehook_new_data[gamepath] = getdefaultsavehook(gamepath, title)
    if gamepath != "0":
        dispatachtask(gamepath)


checkifnewgame("0")
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

    def mp3playfunction(self, path, volume):
        if os.path.exists(path) == False:
            return
        self._playsoundWin(path, volume)

    def _playsoundWin(self, sound, volume):
        try:

            windows.mciSendString(("stop lunatranslator_mci_{}".format(self.i)))
            windows.mciSendString(("close lunatranslator_mci_{}".format(self.i)))
            self.i += 1
            if self.lastfile:
                os.remove(self.lastfile)
            self.lastfile = sound
            windows.mciSendString(
                'open "{}" type mpegvideo  alias lunatranslator_mci_{}'.format(
                    sound, self.i
                )
            )
            windows.mciSendString(
                "setaudio lunatranslator_mci_{} volume to {}".format(
                    self.i, volume * 10
                )
            )
            windows.mciSendString(("play lunatranslator_mci_{}".format(self.i)))
        except:
            pass


def selectdebugfile(path):

    p = os.path.abspath((path))

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
        return content"""
                )
            elif path == "./userconfig/mypost.py":
                ff.write(
                    """
def POSTSOLVE(line): 
    #请在这里编写自定义处理
    return line"""
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
                if globalconfig["focusfollow"]:
                    if _focusp == os.getpid():
                        pass
                    elif _focusp in gobject.baseobject.textsource.pids:
                        self.hookfollowsignal.emit(3, (hwnd,))
                    else:
                        self.hookfollowsignal.emit(4, (0, 0))
                if globalconfig["keepontop"] and globalconfig["focusnotop"]:
                    if _focusp == os.getpid():
                        pass
                    elif _focusp in gobject.baseobject.textsource.pids:
                        gobject.baseobject.translation_ui.settop()
                    else:
                        gobject.baseobject.translation_ui.canceltop()
            if _focusp != windows.GetWindowThreadProcessId(
                gobject.baseobject.textsource.hwnd
            ):
                return

            rect = windows.GetWindowRect(hwnd)
            if event == windows.EVENT_SYSTEM_MINIMIZEEND:
                if globalconfig["minifollow"]:
                    self.hookfollowsignal.emit(3, (hwnd,))
            elif event == windows.EVENT_SYSTEM_MINIMIZESTART:
                if globalconfig["minifollow"]:
                    self.hookfollowsignal.emit(4, (0, 0))
            elif event == windows.EVENT_SYSTEM_MOVESIZESTART:  #
                self.lastpos = rect
            elif event == windows.EVENT_SYSTEM_MOVESIZEEND:  #
                if globalconfig["movefollow"]:
                    if self.lastpos:
                        rate = getScreenRate()
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
        (windows.EVENT_SYSTEM_MINIMIZESTART, windows.EVENT_SYSTEM_MINIMIZEEND),
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
