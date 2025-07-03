import threading
import re, os
import time, gobject, windows
from qtsymbols import *
import zhconv, functools
from myutils.config import (
    globalconfig,
    savehook_new_data,
    findgameuidofpath,
    getlanguse,
    _TR,
)
from textio.textsource.textsourcebase import basetext
from myutils.utils import getlangtgt, safe_escape, stringfyerror
from myutils.kanjitrans import kanjitrans
from myutils.hwnd import test_injectable, ListProcess
from myutils.wrapper import threader
from traceback import print_exc
import subprocess, NativeUtils
from ctypes import (
    CDLL,
    CFUNCTYPE,
    c_bool,
    Structure,
    c_int,
    c_char_p,
    c_wchar_p,
    c_uint64,
    c_int64,
    c_void_p,
    c_wchar,
    c_uint32,
    c_uint8,
    c_uint,
    c_char,
)
from ctypes.wintypes import DWORD, LPCWSTR


class ThreadParam(Structure):
    _fields_ = [
        ("processId", c_uint),
        ("addr", c_uint64),
        ("ctx", c_uint64),
        ("ctx2", c_uint64),
    ]

    def __hash__(self):
        return hash((self.processId, self.addr, self.ctx, self.ctx2))

    def __eq__(self, __value):
        return self.__hash__() == __value.__hash__()

    def __repr__(self):
        return "(%s,%x,%x,%x)" % (self.processId, self.addr, self.ctx, self.ctx2)


class SearchParam(Structure):
    _fields_ = [
        ("pattern", c_char * 30),
        ("address_method", c_int),
        ("search_method", c_int),
        ("length", c_int),
        ("offset", c_int),
        ("searchTime", c_int),
        ("maxRecords", c_int),
        ("codepage", c_int),
        ("padding", c_int64),
        ("minAddress", c_uint64),
        ("maxAddress", c_uint64),
        ("boundaryModule", c_wchar * 120),
        ("exportModule", c_wchar * 120),
        ("text", c_wchar * 30),
        ("isjithook", c_bool),
        ("sharememname", c_wchar * 64),
        ("sharememsize", c_uint64),
    ]


FindHooksCallback_t = CFUNCTYPE(None, c_wchar_p, c_wchar_p)
ProcessEvent = CFUNCTYPE(None, DWORD)
ThreadEvent_maybeEmbed = CFUNCTYPE(None, c_wchar_p, c_char_p, ThreadParam, c_bool)
ThreadEvent = CFUNCTYPE(None, c_wchar_p, c_char_p, ThreadParam)
OutputCallback = CFUNCTYPE(None, c_wchar_p, c_char_p, ThreadParam, c_wchar_p)
HostInfoHandler = CFUNCTYPE(None, c_int, c_wchar_p)
HookInsertHandler = CFUNCTYPE(None, DWORD, c_uint64, c_wchar_p)
EmbedCallback = CFUNCTYPE(None, c_wchar_p, ThreadParam)
QueryHistoryCallback = CFUNCTYPE(None, c_wchar_p)


class texthook(basetext):

    @property
    def embedconfig(self) -> dict:
        if self.hconfig.get("embed_follow_default", True):
            return globalconfig["embedded"]

        class __shitdict(dict):
            def __getitem__(self, key):
                if key in self:
                    return super().__getitem__(key)
                else:
                    return globalconfig["embedded"][key]

        return __shitdict(self.hconfig["embed_setting_private"])

    @property
    def config(self) -> dict:
        if self.hconfig.get("hooksetting_follow_default", True):
            return globalconfig

        class __shitdict(dict):
            def __getitem__(self, key):
                if key in self:
                    return super().__getitem__(key)
                else:
                    return globalconfig[key]

        return __shitdict(self.hconfig["hooksetting_private"])

    @property
    def hconfig(self) -> dict:
        return savehook_new_data.get(self.gameuid, {})

    def init(self):

        self.pids = []
        self.maybepids = []
        self.maybepidslock = threading.Lock()
        self.keepref = []
        self.selectinghook = None
        self.selectedhook = []
        self.usermanualaccepthooks = []
        self.multiselectedcollector = []
        self.multiselectedcollectorlock = threading.Lock()
        self.lastflushtime = 0
        self.runonce_line = ""
        gobject.base.autoswitchgameuid = False
        self.initdll()
        self.delaycollectallselectedoutput()
        self.autohookmonitorthread()

    def edit_selectedhook_remove(self, key):
        try:
            self.selectedhook.remove(key)
        except:
            pass
        _, _, tp = key
        self.Luna_SyncThread(tp, False)

    def edit_selectedhook_insert(self, key, idx=-1):
        if idx == -1:
            idx = len(self.selectedhook)
        self.selectedhook.insert(idx, key)
        _, _, tp = key
        self.Luna_SyncThread(tp, True)

    def initdll(self):
        LunaHost = CDLL(
            gobject.GetDllpath(
                ("LunaHost32.dll", "LunaHost64.dll"),
                os.path.abspath("files/LunaHook"),
            )
        )
        self.Luna_SyncThread = LunaHost.Luna_SyncThread
        self.Luna_SyncThread.argtypes = ThreadParam, c_bool
        self.Luna_InsertPCHooks = LunaHost.Luna_InsertPCHooks
        self.Luna_InsertPCHooks.argtypes = (DWORD, c_int)
        self.Luna_Settings = LunaHost.Luna_Settings
        self.Luna_Settings.argtypes = c_int, c_bool, c_int, c_int, c_int
        self.Luna_Start = LunaHost.Luna_Start
        self.Luna_Start.argtypes = (
            ProcessEvent,
            ProcessEvent,
            ThreadEvent_maybeEmbed,
            ThreadEvent,
            OutputCallback,
            HostInfoHandler,
            HookInsertHandler,
            EmbedCallback,
        )
        self.Luna_ConnectProcess = LunaHost.Luna_ConnectProcess
        self.Luna_ConnectProcess.argtypes = (DWORD,)
        self.Luna_CheckIfNeedInject = LunaHost.Luna_CheckIfNeedInject
        self.Luna_CheckIfNeedInject.argtypes = (DWORD,)
        self.Luna_CheckIfNeedInject.restype = c_bool
        self.Luna_InsertHookCode = LunaHost.Luna_InsertHookCode
        self.Luna_InsertHookCode.argtypes = DWORD, LPCWSTR
        self.Luna_InsertHookCode.restype = c_bool
        self.Luna_RemoveHook = LunaHost.Luna_RemoveHook
        self.Luna_RemoveHook.argtypes = DWORD, c_uint64
        self.Luna_DetachProcess = LunaHost.Luna_DetachProcess
        self.Luna_DetachProcess.argtypes = (DWORD,)
        self.Luna_SetLanguage = LunaHost.Luna_SetLanguage
        self.Luna_SetLanguage.argtypes = (c_char_p,)
        self.Luna_FindHooks = LunaHost.Luna_FindHooks
        self.Luna_FindHooks.argtypes = (
            DWORD,
            SearchParam,
            FindHooksCallback_t,
            c_wchar_p,
        )
        self.Luna_EmbedSettings = LunaHost.Luna_EmbedSettings
        self.Luna_EmbedSettings.argtypes = (
            DWORD,
            c_uint32,
            c_uint8,
            c_bool,
            c_wchar_p,
            c_uint32,
            c_bool,
            c_bool,
        )
        self.Luna_CheckIsUsingEmbed = LunaHost.Luna_CheckIsUsingEmbed
        self.Luna_CheckIsUsingEmbed.argtypes = (ThreadParam,)
        self.Luna_CheckIsUsingEmbed.restype = c_bool
        self.Luna_UseEmbed = LunaHost.Luna_UseEmbed
        self.Luna_UseEmbed.argtypes = ThreadParam, c_bool
        self.Luna_EmbedCallback = LunaHost.Luna_EmbedCallback
        self.Luna_EmbedCallback.argtypes = ThreadParam, LPCWSTR, LPCWSTR

        self.Luna_QueryThreadHistory = LunaHost.Luna_QueryThreadHistory
        self.Luna_QueryThreadHistory.argtypes = (ThreadParam, c_bool, c_void_p)
        procs = [
            ProcessEvent(self.onprocconnect),
            ProcessEvent(self.removeproc),
            ThreadEvent_maybeEmbed(self.onnewhook),
            ThreadEvent(self.onremovehook),
            OutputCallback(self.handle_output),
            HostInfoHandler(gobject.base.hookselectdialog.sysmessagesignal.emit),
            HookInsertHandler(self.newhookinsert),
            EmbedCallback(self.getembedtext),
        ]
        self.keepref += procs
        self.Luna_Start(*procs)
        self.setsettings()
        self.setlang()

    def listprocessm(self):
        cachefname = gobject.gettempdir("{}.txt".format(time.time()))
        arch = "64" if self.is64bit else "32"
        exe = os.path.abspath("files/shareddllproxy{}.exe".format(arch))
        pid = " ".join([str(_) for _ in self.pids])
        subprocess.run('"{}"  listpm "{}" {}'.format(exe, cachefname, pid))

        with open(cachefname, "r", encoding="utf-16-le") as ff:
            readf = ff.read()
        os.remove(cachefname)
        _list = readf.split("\n")
        print("\n".join(sorted(_list)))
        ret = []
        hasprogram = "c:\\program files" in _list[0].lower()
        for name_ in _list:
            name = name_.lower()
            if (
                ":\\windows\\" in name
                or "\\microsoft\\" in name
                or "\\windowsapps\\" in name
            ):
                continue
            if hasprogram == False and "c:\\program files" in name:
                continue
            fn = name_.split("\\")[-1]
            if fn in ret:
                continue
            if fn.lower() in ["lunahook32.dll", "lunahook64.dll"]:
                continue
            ret.append(fn)
        return sorted(ret)

    def connecthwnd(self, hwnd):
        if (
            gobject.base.AttachProcessDialog
            and gobject.base.AttachProcessDialog.isVisible()
        ):
            return
        pid = windows.GetWindowThreadProcessId(hwnd)
        if pid == os.getpid():
            return
        name_ = windows.GetProcessFileName(pid)
        if not name_:
            return
        uid, reflist = findgameuidofpath(name_)
        if not uid:
            return
        pids = ListProcess(name_)
        if self.ending:
            return
        if len(self.pids):
            return
        if globalconfig["startgamenototop"] == False:
            idx = reflist.index(uid)
            reflist.insert(0, reflist.pop(idx))
        self.start(hwnd, pids, name_, uid, autostart=True)
        return True

    @threader
    def autohookmonitorthread(self):
        while (not self.ending) and (len(self.pids) == 0):
            try:
                hwnd = windows.GetForegroundWindow()
                hwnd = windows.GetAncestor(hwnd)
                if self.connecthwnd(hwnd):
                    break
            except:
                print_exc()
            time.sleep(0.1)

    @property
    def gameuid(self):
        return gobject.base.gameuid

    @gameuid.setter
    def gameuid(self, gameuid):
        gobject.base.gameuid = gameuid

    def start(self, hwnd, pids, gamepath, gameuid, autostart=False):
        for pid in pids:
            self.waitend(pid)
        gobject.base.hwnd = hwnd
        self.gameuid = gameuid
        self.detachall()
        _filename, _ = os.path.splitext(os.path.basename(gamepath))
        sqlitef = gobject.gettranslationrecorddir(
            "{}_{}.sqlite".format(_filename, gameuid)
        )
        self.startsql(sqlitef)
        if autostart:
            autostarthookcode = self.hconfig.get("hook", [])
            needinserthookcode = self.hconfig.get("needinserthookcode", [])
            injecttimeout = self.hconfig.get("inserthooktimeout", 250) / 1000
        else:
            injecttimeout = 0
            autostarthookcode = []
            needinserthookcode = []

        self.autostarthookcode = [self.deserial(__) for __ in autostarthookcode]

        self.needinserthookcode = needinserthookcode
        self.removedaddress = []

        self.gamepath = gamepath
        self.is64bit = NativeUtils.Is64bit(pids[0])
        if (
            len(autostarthookcode) == 0
            and len(self.hconfig.get("embedablehook", [])) == 0
            and globalconfig["autoopenselecttext"]
        ):
            gobject.base.hookselectdialog.realshowhide.emit(True)
        self.injectproc(injecttimeout, pids)

    def QueryThreadHistory(self, tp, _latest=False):
        ret = []
        self.Luna_QueryThreadHistory(tp, _latest, QueryHistoryCallback(ret.append))
        return ret[0]

    def removeproc(self, pid):
        self.pids.remove(pid)
        if len(self.pids) == 0:
            self.gameuid = 0
            self.autohookmonitorthread()

    def start_unsafe(self, pids):
        injectpids = []
        for pid in pids:
            self.Luna_ConnectProcess(pid)
            if self.Luna_CheckIfNeedInject(pid):
                injectpids.append(pid)
        if len(injectpids):
            arch = ["32", "64"][self.is64bit]
            dll = os.path.abspath("files/LunaHook/LunaHook{}.dll".format(arch))
            self.injectdll(injectpids, arch, dll)

    def injectdll(self, injectpids, bit, dll):

        injecter = os.path.abspath("files/shareddllproxy{}.exe".format(bit))
        pid = " ".join([str(_) for _ in injectpids])
        for _ in (0,):
            if not test_injectable(injectpids):
                break

            ret = subprocess.run(
                '"{}" dllinject {} "{}"'.format(injecter, pid, dll)
            ).returncode
            if ret:
                return
            pids = NativeUtils.collect_running_pids(injectpids)
            pid = " ".join([str(_) for _ in pids])

        windows.ShellExecute(
            0,
            "runas",
            injecter,
            'dllinject {} "{}"'.format(pid, dll),
            None,
            windows.SW_HIDE,
        )

    @threader
    def injectproc(self, injecttimeout, pids):
        if injecttimeout:
            time.sleep(injecttimeout)
            _list = ListProcess(self.gamepath)
            if set(pids) != set(_list):
                # 部分cef/v8引擎的游戏，会在一段启动时间后，启动子进程用于渲染
                return self.injectproc(injecttimeout, _list)

        if self.ending:
            return
        try:
            self.start_unsafe(pids)
        except Exception as e:
            print_exc()
            gobject.base.translation_ui.displaymessagebox.emit("错误", stringfyerror(e))

    @threader
    def waitend(self, pid):
        # 如果有进程一闪而逝，没来的及注入，导致无法自动重连
        self.maybepids.append(pid)
        windows.WaitForSingleObject(
            windows.OpenProcess(windows.SYNCHRONIZE, False, pid)
        )
        with self.maybepidslock:
            if len(self.pids) == 0 and len(self.maybepids):
                # 如果进程连接，则剔除maybepids
                # 当进程结束，且发现是被试探过&未曾连接，则重试
                self.maybepids.clear()
                self.autohookmonitorthread()

    def onprocconnect(self, pid):
        self.pids.append(pid)
        try:
            self.maybepids.remove(pid)
        except:
            pass
        for hookcode in self.needinserthookcode:
            self.Luna_InsertHookCode(pid, hookcode)
        if self.hconfig.get("insertpchooks_string", False):
            self.Luna_InsertPCHooks(pid, 0)
            self.Luna_InsertPCHooks(pid, 1)
        gobject.base.displayinfomessage(self.hconfig["title"], "<msg_info_refresh>")
        self.flashembedsettings(pid)
        self.setsettings()

    def InsertPCHooks(self, which):
        for pid in self.pids:
            self.Luna_InsertPCHooks(pid, which)

    def newhookinsert(self, pid, addr, hcode):
        if hcode in self.hconfig.get("removeforeverhook", []):
            self.Luna_RemoveHook(pid, addr)
            return
        for _hc, _, _ctx1, _ctx2 in self.hconfig.get("embedablehook", []):
            if hcode == _hc:
                tp = ThreadParam()
                tp.processId = pid
                tp.addr = addr
                tp.ctx = _ctx1
                tp.ctx2 = _ctx2
                self.Luna_UseEmbed(tp, True)

    def safeembedcheck(self, text):
        try:
            if not self.embedconfig["safecheck_use"]:
                return True
            for regex in self.embedconfig["safecheckregexs"]:
                if re.match(safe_escape(regex), text):
                    return False
            return True
        except:
            return False

    @threader
    def getembedtext(self, text: str, tp):
        if not self.isautorunning:
            return self.embedcallback(text, "", tp)
        if self.safeembedcheck(text):
            trans = self.waitfortranslation(text)
        else:
            collect = []
            for _ in text.split("\n"):
                if _ and self.safeembedcheck(_):
                    _ = self.waitfortranslation(_)
                    if not _:
                        continue
                collect.append(_)
            trans = "\n".join(collect)
        if not trans:
            trans = ""
        if self.embedconfig["trans_kanji"]:
            trans = kanjitrans(zhconv.convert(trans, "zh-tw"))
        self.embedcallback(text, trans, tp)

    def embedcallback(self, text: str, trans: str, tp: ThreadParam):
        trans = self.splitembedlines(trans)
        self.Luna_EmbedCallback(tp, text, trans)

    def splitembedlines(self, trans: str):
        if len(trans) and self.embedconfig["limittextlength_use"]:
            length = self.embedconfig["limittextlength_length"]
            lines = trans.split("\n")
            newlines = []
            space = getlangtgt().space
            for line in lines:
                line = line.split(space) if space else line
                while len(line):
                    newlines.append(space.join(line[:length]))
                    line = line[length:]
            trans = "\n".join(newlines)
        return trans

    def flashembedsettings(self, pid=None):
        if pid:
            pids = [pid]
        else:
            pids = self.pids.copy()
        for pid in pids:
            self.Luna_EmbedSettings(
                pid,
                int(1000 * self.embedconfig["timeout_translate"]),
                2,  # static_data["charsetmap"][globalconfig['embedded']['changecharset_charset']]
                False,  # globalconfig['embedded']['changecharset']
                (
                    self.embedconfig["changefont_font"]
                    if self.embedconfig["changefont"]
                    else ""
                ),
                self.embedconfig["displaymode"],
                True,
                self.embedconfig["clearText"],
            )

    def onremovehook(self, hc, hn: bytes, tp):
        key = (hc, hn.decode("utf8"), tp)
        gobject.base.hookselectdialog.removehooksignal.emit(key)

    def match_compatibility(self, key, key2):
        hc, hn, tp = key
        _hc, _hn, _tp = key2
        base = (tp.ctx & 0xFFFF, tp.ctx2 & 0xFFFF, hc) == (
            _tp.ctx & 0xFFFF,
            _tp.ctx2 & 0xFFFF,
            _hc,
        )
        name = (hc[:8] == "UserHook" and _hc[:8] == "UserHook") or (hc == _hc)
        return base and name

    def matchkeyindex(self, key):
        for _i, autostarthookcode in enumerate(self.autostarthookcode):
            if self.match_compatibility(key, autostarthookcode):
                return _i
        return -1

    def onnewhook(self, hc, hn: bytes, tp, isembedable):
        if hc in self.hconfig.get("removeforeverhook", []):
            return
        key = (hc, hn.decode("utf8"), tp)
        autoindex = self.matchkeyindex(key)
        select = autoindex != -1
        if select:
            self.selectinghook = key
            insertindex = len(self.selectedhook) - 1
            for j in range(len(self.selectedhook)):
                if self.selectedhook[j] in self.usermanualaccepthooks:
                    continue
                idx = self.matchkeyindex(self.selectedhook[j])
                if idx == -1:
                    continue
                if autoindex < idx:
                    insertindex = j
                else:
                    insertindex = j + 1
            self.edit_selectedhook_insert(key, insertindex)
        gobject.base.hookselectdialog.addnewhooksignal.emit(key, select, isembedable)

    def setlang(self):
        self.Luna_SetLanguage(getlanguse().encode())

    def setsettings(self):
        self.Luna_Settings(
            self.config["textthreaddelay"],
            False,  # 不使用内置去重
            self.codepage(),
            self.config["maxBufferSize"],
            self.config["maxHistorySize"],
        )

    def codepage(self):
        return self.config.get("codepage_value", 932)

    def defaultsp(self):
        usestruct = SearchParam()
        if not self.is64bit:
            usestruct.pattern = bytes([0x55, 0x8B, 0xEC])
            usestruct.length = 3
            usestruct.offset = 0
            usestruct.maxAddress = 0xFFFFFFFF
        else:
            usestruct.pattern = bytes([0xCC, 0xCC, 0x48, 0x89])
            usestruct.length = 4
            usestruct.offset = 2
            usestruct.maxAddress = 0xFFFFFFFFFFFFFFFF
        usestruct.address_method = 0
        usestruct.padding = 0
        usestruct.minAddress = 0
        usestruct.search_method = 0
        usestruct.searchTime = 30000
        usestruct.maxRecords = 100000
        usestruct.codepage = self.codepage()
        usestruct.boundaryModule = os.path.basename(self.gamepath)
        usestruct.isjithook = False
        return usestruct

    @threader
    def findhook(self, usestruct, addresses):
        savefound: "dict[str, list]" = {}
        pids = self.pids.copy()
        cntref = []

        def __callback(cntref: list, hcode, text):
            if hcode not in savefound:
                savefound[hcode] = []
            savefound[hcode].append(text)
            cntref.append(0)

        _callback = FindHooksCallback_t(functools.partial(__callback, cntref))
        self.keepref.append(_callback)
        for pid in pids:
            self.Luna_FindHooks(pid, usestruct, _callback, addresses)

        while True:
            lastsize = len(cntref)
            time.sleep(2)
            if lastsize == len(cntref) and lastsize != 0:
                break
        gobject.base.hookselectdialog.getfoundhooksignal.emit(savefound)

    def inserthook(self, hookcode):
        succ = True
        for pid in self.pids.copy():
            succ = self.Luna_InsertHookCode(pid, hookcode) and succ
        if succ == False:
            QMessageBox.critical(
                gobject.base.hookselectdialog, _TR("错误"), _TR("特殊码无效")
            )

    @threader
    def delaycollectallselectedoutput(self):
        while not self.ending:
            time.sleep(0.01)
            if time.time() < self.lastflushtime + min(
                0.1, self.config["textthreaddelay"] / 1000
            ):
                continue
            if len(self.multiselectedcollector) == 0:
                continue
            with self.multiselectedcollectorlock:
                self.dispatchtextlines(self.multiselectedcollector)
                self.multiselectedcollector.clear()

    def dispatchtextlines(self, keyandtexts: list):
        try:
            keyandtexts.sort(key=lambda xx: self.selectedhook.index(xx[0]))
        except:
            pass
        _collector = globalconfig["multihookmergeby"].join([_[1] for _ in keyandtexts])
        self.dispatchtext(_collector)

    def dispatchtext_multiline_delayed(self, key, text):
        with self.multiselectedcollectorlock:
            self.lastflushtime = time.time()
            self.multiselectedcollector.append((key, text))

    def handle_output(self, hc, hn: bytes, tp, output):

        key = (hc, hn.decode("utf8"), tp)
        if key in self.selectedhook:
            if len(self.selectedhook) == 1:
                self.dispatchtext(output)
            else:
                self.dispatchtext_multiline_delayed(key, output)
        if key == self.selectinghook:
            gobject.base.hookselectdialog.getnewsentencesignal.emit(output)

        gobject.base.hookselectdialog.update_item_new_line.emit(key, output)

    def serialkey(self, key):
        hc, hn, tp = key
        return (tp.processId, tp.addr, tp.ctx, tp.ctx2, hn, hc)

    def deserial(self, lst):
        tp = ThreadParam()
        tp.processId, tp.addr, tp.ctx, tp.ctx2, hn, hc = lst
        return hc, hn, tp

    def serialselectedhook(self):
        xx = []
        for key in self.selectedhook:
            xx.append(self.serialkey(key))
        return xx

    def dispatchtext(self, text):
        self.runonce_line = text

        donttrans = (windows.GetKeyState(windows.VK_CONTROL) < 0) or (
            windows.GetKeyState(windows.VK_SHIFT) < 0
        )
        return super().dispatchtext(text, donttrans=donttrans)

    def gettextonce(self):
        return self.runonce_line

    def end(self):
        self.detachall()
        time.sleep(0.1)

    def detachall(self):
        for pid in self.pids.copy():
            self.Luna_DetachProcess(pid)
