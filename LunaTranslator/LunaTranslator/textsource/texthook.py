import threading
import re, os
import time, gobject, windows
from collections import OrderedDict
import codecs, functools
from winsharedutils import Is64bit
from myutils.config import (
    globalconfig,
    savehook_new_data,
    static_data,
    findgameuidofpath,
)
from textsource.textsourcebase import basetext
from myutils.utils import checkchaos, getfilemd5, getlangtgt, getlanguagespace, copytree
from myutils.hwnd import injectdll, test_injectable, ListProcess, getpidexe
from myutils.wrapper import threader
from traceback import print_exc
import subprocess, hashlib, requests, zipfile, shutil
from myutils.proxy import getproxy


from ctypes import (
    CDLL,
    CFUNCTYPE,
    c_bool,
    Structure,
    c_int,
    c_char_p,
    c_wchar_p,
    c_uint64,
    c_void_p,
    cast,
    c_wchar,
    c_uint32,
    c_uint8,
    c_uint,
    c_char,
)
from ctypes.wintypes import DWORD, LPCWSTR
from gui.usefulwidget import getQMessageBox

MAX_MODULE_SIZE = 120
HOOK_NAME_SIZE = 60
HOOKCODE_LEN = 500
oncecheckversion = True


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
        return "(%s,%s,%s,%s)" % (self.processId, self.addr, self.ctx, self.ctx2)


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
        ("padding", c_uint64),
        ("minAddress", c_uint64),
        ("maxAddress", c_uint64),
        ("boundaryModule", c_wchar * 120),
        ("exportModule", c_wchar * 120),
        ("text", c_wchar * 30),
        ("jittype", c_int),
    ]


findhookcallback_t = CFUNCTYPE(None, c_wchar_p, c_wchar_p)
ProcessEvent = CFUNCTYPE(None, DWORD)
ThreadEvent = CFUNCTYPE(None, c_wchar_p, c_char_p, ThreadParam)
OutputCallback = CFUNCTYPE(c_bool, c_wchar_p, c_char_p, ThreadParam, c_wchar_p)
ConsoleHandler = CFUNCTYPE(None, c_wchar_p)
HookInsertHandler = CFUNCTYPE(None, c_uint64, c_wchar_p)
EmbedCallback = CFUNCTYPE(None, c_wchar_p, ThreadParam)


def splitembedlines(trans: str):
    if len(trans) and globalconfig["embedded"]["limittextlength_use"]:
        length = globalconfig["embedded"]["limittextlength_length"]
        lines = trans.split("\n")
        newlines = []
        space = getlanguagespace(getlangtgt())
        for line in lines:
            line = line.split(space) if space else line
            while len(line):
                newlines.append(space.join(line[:length]))
                line = line[length:]
        trans = "\n".join(newlines)
    return trans


class texthook(basetext):

    @property
    def config(self):
        try:
            df = savehook_new_data[self.gameuid]["hooksetting_follow_default"]
        except:
            df = True
        if df:
            return globalconfig
        else:

            class __shitdict(dict):
                def __getitem__(self, key):
                    if key in self:
                        return super().__getitem__(key)
                    else:
                        return globalconfig[key]

            return __shitdict(savehook_new_data[self.gameuid]["hooksetting_private"])

    def tryqueryfromhost(self):

        for i, main_server in enumerate(static_data["main_server"]):
            try:
                res = requests.get(
                    "{main_server}/version_lunahook".format(main_server=main_server),
                    verify=False,
                    proxies=getproxy(("update", "lunatranslator")),
                )
                res = res.json()
                return res
            except:
                pass

    @threader
    def checkversion(self):
        if not globalconfig["autoupdate"]:
            return
        dlls = ["LunaHook32.dll", "LunaHook64.dll", "LunaHost32.dll", "LunaHost64.dll"]
        sha256 = {}
        for dll in dlls:
            f = os.path.join("files/plugins/LunaHook", dll)
            with open(f, "rb") as ff:
                bs = ff.read()
            sha = hashlib.sha256(bs).hexdigest()
            sha256[dll] = sha
        res = self.tryqueryfromhost()
        if not res:
            return
        isnew = True
        for _, sha in res["sha256"].items():
            if sha256[_] != sha:
                isnew = False
                break
        if isnew:
            return

        url = res["download"]
        savep = gobject.getcachedir("update/LunaHook.zip")
        if url.startswith("https://github.com"):
            __x = "github"
        else:
            __x = "lunatranslator"
        data = requests.get(
            url, verify=False, proxies=getproxy(("update", __x))
        ).content
        with open(savep, "wb") as ff:
            ff.write(data)
        tgt = gobject.getcachedir("update/LunaHook")
        with zipfile.ZipFile(savep) as zipf:
            zipf.extractall(tgt)
        if os.path.exists(os.path.join(tgt, "Release_English", "LunaHook32.dll")):
            copytree(os.path.join(tgt, "Release_English"), "files/plugins/LunaHook")
        else:
            copytree(tgt, "files/plugins/LunaHook")

    def init(self):
        self.pids = []
        self.maybepids = []
        self.maybepidslock = threading.Lock()
        self.keepref = []
        self.hookdatacollecter = OrderedDict()
        self.reverse = {}
        self.forward = []
        self.selectinghook = None
        self.selectedhook = []
        self.selectedhookidx = []

        self.multiselectedcollector = []
        self.multiselectedcollectorlock = threading.Lock()
        self.lastflushtime = 0
        self.runonce_line = ""
        gobject.baseobject.autoswitchgameuid = False
        self.delaycollectallselectedoutput()
        self.autohookmonitorthread()
        self.initdllonce = True
        self.initdlllock = threading.Lock()

        global oncecheckversion
        if oncecheckversion:
            oncecheckversion = False
            self.checkversion()

    def delayinit(self):
        with self.initdlllock:
            if not self.initdllonce:
                return
            self.initdllonce = False
            self.__delayinit()

    def __delayinit(self):
        LunaHost = CDLL(
            gobject.GetDllpath(
                ("LunaHost32.dll", "LunaHost64.dll"),
                os.path.abspath("files/plugins/LunaHook"),
            )
        )
        self.Luna_Settings = LunaHost.Luna_Settings
        self.Luna_Settings.argtypes = c_int, c_bool, c_int, c_int, c_int
        self.Luna_Start = LunaHost.Luna_Start
        self.Luna_Start.argtypes = (
            c_void_p,
            c_void_p,
            c_void_p,
            c_void_p,
            c_void_p,
            c_void_p,
            c_void_p,
            c_void_p,
        )
        self.Luna_Inject = LunaHost.Luna_Inject
        self.Luna_Inject.argtypes = DWORD, LPCWSTR
        self.Luna_CreatePipeAndCheck = LunaHost.Luna_CreatePipeAndCheck
        self.Luna_CreatePipeAndCheck.argtypes = (DWORD,)
        self.Luna_CreatePipeAndCheck.restype = c_bool
        self.Luna_InsertHookCode = LunaHost.Luna_InsertHookCode
        self.Luna_InsertHookCode.argtypes = DWORD, LPCWSTR
        self.Luna_InsertHookCode.restype = c_bool
        self.Luna_RemoveHook = LunaHost.Luna_RemoveHook
        self.Luna_RemoveHook.argtypes = DWORD, c_uint64
        self.Luna_Detach = LunaHost.Luna_Detach
        self.Luna_Detach.argtypes = (DWORD,)
        self.Luna_FindHooks = LunaHost.Luna_FindHooks
        self.Luna_FindHooks.argtypes = (
            DWORD,
            SearchParam,
            c_void_p,
        )
        self.Luna_EmbedSettings = LunaHost.Luna_EmbedSettings
        self.Luna_EmbedSettings.argtypes = (
            DWORD,
            c_uint32,
            c_uint8,
            c_bool,
            c_wchar_p,
            c_uint32,
            c_uint32,
            c_bool,
        )
        self.Luna_checkisusingembed = LunaHost.Luna_checkisusingembed
        self.Luna_checkisusingembed.argtypes = DWORD, c_uint64, c_uint64, c_uint64
        self.Luna_checkisusingembed.restype = c_bool
        self.Luna_useembed = LunaHost.Luna_useembed
        self.Luna_useembed.argtypes = DWORD, c_uint64, c_uint64, c_uint64, c_bool
        self.Luna_embedcallback = LunaHost.Luna_embedcallback
        self.Luna_embedcallback.argtypes = DWORD, LPCWSTR, LPCWSTR

        self.Luna_FreePtr = LunaHost.Luna_FreePtr
        self.Luna_FreePtr.argtypes = (c_void_p,)

        self.Luna_QueryThreadHistory = LunaHost.Luna_QueryThreadHistory
        self.Luna_QueryThreadHistory.argtypes = (ThreadParam,)
        self.Luna_QueryThreadHistory.restype = c_void_p
        procs = [
            ProcessEvent(self.onprocconnect),
            ProcessEvent(self.removeproc),
            ThreadEvent(self.onnewhook),
            ThreadEvent(self.onremovehook),
            OutputCallback(self.handle_output),
            ConsoleHandler(gobject.baseobject.hookselectdialog.sysmessagesignal.emit),
            HookInsertHandler(self.newhookinsert),
            EmbedCallback(self.getembedtext),
        ]
        self.keepref += procs
        ptrs = [cast(_, c_void_p).value for _ in procs]
        self.Luna_Start(*ptrs)

    def listprocessm(self):
        cachefname = gobject.gettempdir("{}.txt".format(time.time()))
        arch = "64" if self.is64bit else "32"
        exe = os.path.abspath("./files/plugins/shareddllproxy{}.exe".format(arch))
        pid = " ".join([str(_) for _ in self.pids])
        subprocess.run('"{}"  listpm "{}" {}'.format(exe, cachefname, pid))

        with open(cachefname, "r", encoding="utf-16-le") as ff:
            readf = ff.read()

        os.remove(cachefname)
        _list = readf.split("\n")[:-1]
        if len(_list) == 0:
            return []

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
        return ret

    def connecthwnd(self, hwnd):
        if (
            gobject.baseobject.AttachProcessDialog
            and gobject.baseobject.AttachProcessDialog.isVisible()
        ):
            return
        pid = windows.GetWindowThreadProcessId(hwnd)
        if pid == os.getpid():
            return
        name_ = getpidexe(pid)
        if not name_:
            return
        found = findgameuidofpath(name_)
        if not found:
            return
        uid, reflist = found
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

    def start(self, hwnd, pids, gamepath, gameuid, autostart=False):
        self.delayinit()
        for pid in pids:
            self.waitend(pid)
        gobject.baseobject.hwnd = hwnd
        gobject.baseobject.gameuid = gameuid
        self.gameuid = gameuid
        self.detachall()
        _filename, _ = os.path.splitext(os.path.basename(gamepath))
        sqlitef = gobject.gettranslationrecorddir(f"{_filename}_{gameuid}.sqlite")
        if os.path.exists(sqlitef) == False:
            md5 = getfilemd5(gamepath)
            f2 = gobject.gettranslationrecorddir(f"{_filename}_{md5}.sqlite")
            try:
                os.rename(f2, sqlitef)
            except:
                pass
        self.startsql(sqlitef)
        self.setsettings()
        if autostart:
            autostarthookcode = savehook_new_data[gameuid]["hook"]
            needinserthookcode = savehook_new_data[gameuid]["needinserthookcode"]
            injecttimeout = savehook_new_data[gameuid]["inserthooktimeout"] / 1000
        else:
            injecttimeout = 0
            autostarthookcode = []
            needinserthookcode = []

        self.autostarthookcode = [self.deserial(__) for __ in autostarthookcode]

        self.needinserthookcode = needinserthookcode
        self.removedaddress = []

        self.gamepath = gamepath
        self.is64bit = Is64bit(pids[0])
        if (
            len(autostarthookcode) == 0
            and len(savehook_new_data[self.gameuid]["embedablehook"]) == 0
        ):
            gobject.baseobject.hookselectdialog.realshowhide.emit(True)
        self.injectproc(injecttimeout, pids)

    def QueryThreadHistory(self, tp):
        ws = self.Luna_QueryThreadHistory(tp)
        string = cast(ws, c_wchar_p).value
        self.Luna_FreePtr(ws)
        return string

    def removeproc(self, pid):
        self.pids.remove(pid)
        if len(self.pids) == 0:
            self.autohookmonitorthread()

    def start_unsafe(self, pids):
        caninject = test_injectable(pids)
        injectpids = []
        for pid in pids:
            if caninject and globalconfig["use_yapi"]:
                self.Luna_Inject(pid, os.path.abspath("./files/plugins/LunaHook"))
            else:
                if self.Luna_CreatePipeAndCheck(pid):
                    injectpids.append(pid)
        if len(injectpids):
            arch = ["32", "64"][self.is64bit]
            dll = os.path.abspath(f"./files/plugins/LunaHook/LunaHook{arch}.dll")
            injectdll(injectpids, arch, dll)

    @threader
    def injectproc(self, injecttimeout, pids):
        if injecttimeout:
            time.sleep(injecttimeout)
            if set(pids) != set(ListProcess(self.gamepath)):
                # 部分cef/v8引擎的游戏，会在一段启动时间后，启动子进程用于渲染
                return self.injectproc(injecttimeout, pids)

        if self.ending:
            return
        try:
            self.start_unsafe(pids)
        except:
            print_exc()
            gobject.baseobject.translation_ui.displaymessagebox.emit(
                "错误", "权限不足，请以管理员权限运行！"
            )

    @threader
    def waitend(self, pid):
        # 如果有进程一闪而逝，没来的及注入，导致无法自动重连
        self.maybepids.append(pid)
        windows.WaitForSingleObject(
            windows.AutoHandle(windows.OpenProcess(windows.SYNCHRONIZE, False, pid)),
            windows.INFINITE,
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
        gobject.baseobject.displayinfomessage(
            savehook_new_data[self.gameuid]["title"], "<msg_info_refresh>"
        )
        self.flashembedsettings(pid)

    def newhookinsert(self, addr, hcode):
        for _hc, _addr, _ctx1, _ctx2 in savehook_new_data[self.gameuid][
            "embedablehook"
        ]:
            if hcode == _hc:
                self.useembed(addr, _ctx1, _ctx2, True)

    def safeembedcheck(self, text):
        try:
            if globalconfig["embedded"]["safecheck_use"] == False:
                return True
            for regex in globalconfig["embedded"]["safecheckregexs"]:
                if re.match(
                    codecs.escape_decode(bytes(regex, "utf-8"))[0].decode("utf-8"), text
                ):
                    return False
            return True
        except:
            return False

    @threader
    def getembedtext(self, text, tp):
        if self.safeembedcheck(text) == False:
            self.embedcallback(text, "")
            return
        if not self.isautorunning:
            self.embedcallback(text, "")
            return
        if self.checkisusingembed(tp.addr, tp.ctx, tp.ctx2):
            trans = self.waitfortranslation(text)
            if not trans:
                trans = ""
            self.embedcallback(text, trans)

    def embedcallback(self, text: str, trans: str):
        trans = splitembedlines(trans)
        for pid in self.pids.copy():
            self.Luna_embedcallback(pid, text, trans)

    def flashembedsettings(self, pid=None):
        if pid:
            pids = [pid]
        else:
            pids = self.pids.copy()
        for pid in pids:
            self.Luna_EmbedSettings(
                pid,
                int(1000 * globalconfig["embedded"]["timeout_translate"]),
                2,  # static_data["charsetmap"][globalconfig['embedded']['changecharset_charset']]
                False,  # globalconfig['embedded']['changecharset']
                (
                    globalconfig["embedded"]["changefont_font"]
                    if globalconfig["embedded"]["changefont"]
                    else ""
                ),
                globalconfig["embedded"]["insertspace_policy"],
                globalconfig["embedded"]["keeprawtext"],
                True,
            )

    def onremovehook(self, hc, hn, tp):
        key = (hc, hn.decode("utf8"), tp)
        self.hookdatacollecter.pop(key)
        gobject.baseobject.hookselectdialog.removehooksignal.emit(key)

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

    def onnewhook(self, hc, hn, tp):
        key = (hc, hn.decode("utf8"), tp)

        self.hookdatacollecter[key] = []

        select = False
        for _i, autostarthookcode in enumerate(self.autostarthookcode):
            if self.match_compatibility(key, autostarthookcode):
                self.selectedhook += [key]
                self.selectinghook = key
                select = True
                break
        gobject.baseobject.hookselectdialog.addnewhooksignal.emit(key, select)
        return True

    def setsettings(self):
        self.Luna_Settings(
            self.config["textthreaddelay"],
            self.config["direct_filterrepeat"],
            self.codepage(),
            self.config["maxBufferSize"],
            self.config["maxHistorySize"],
        )

    def codepage(self):
        try:
            cpi = self.config["codepage_index"]
            cp = static_data["codepage_real"][cpi]
        except:
            cp = 932
        return cp

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
        usestruct.jittype = 0
        return usestruct

    @threader
    def findhook(self, usestruct):
        savefound = {}
        pids = self.pids.copy()
        cntref = []

        def __callback(cntref, hcode, text):
            if hcode not in savefound:
                savefound[hcode] = []
            savefound[hcode].append(text)
            cntref.append(0)

        _callback = findhookcallback_t(functools.partial(__callback, cntref))
        self.keepref.append(_callback)
        for pid in pids:
            self.Luna_FindHooks(pid, usestruct, cast(_callback, c_void_p).value)

        while True:
            lastsize = len(cntref)
            time.sleep(2)
            if lastsize == len(cntref) and lastsize != 0:
                break
        gobject.baseobject.hookselectdialog.getfoundhooksignal.emit(savefound)

    def inserthook(self, hookcode):
        succ = True
        for pid in self.pids.copy():
            succ = self.Luna_InsertHookCode(pid, hookcode) and succ
        if succ == False:
            getQMessageBox(
                gobject.baseobject.hookselectdialog,
                "Error",
                "Invalie Hook Code Format!",
            )

    def removehook(self, pid, address):
        for pid in self.pids.copy():
            self.Luna_RemoveHook(pid, address)

    @threader
    def delaycollectallselectedoutput(self):
        while not self.ending:
            time.sleep(0.01)
            if time.time() < self.lastflushtime + self.config["textthreaddelay"] / 1000:
                continue
            if len(self.multiselectedcollector) == 0:
                continue
            with self.multiselectedcollectorlock:
                try:
                    self.multiselectedcollector.sort(
                        key=lambda xx: self.selectedhook.index(xx[0])
                    )
                except:
                    pass
                _collector = "\n".join([_[1] for _ in self.multiselectedcollector])
                self.dispatchtext(_collector)
                self.multiselectedcollector.clear()

    def dispatchtext_multiline_delayed(self, key, text):
        with self.multiselectedcollectorlock:
            self.lastflushtime = time.time()
            self.multiselectedcollector.append((key, text))

    def handle_output(self, hc, hn, tp, output):

        if self.config["filter_chaos_code"] and checkchaos(output):
            return False
        key = (hc, hn.decode("utf8"), tp)
        if key in self.selectedhook:
            if len(self.selectedhook) == 1:
                self.dispatchtext(output)
            else:
                self.dispatchtext_multiline_delayed(key, output)
        if key == self.selectinghook:
            gobject.baseobject.hookselectdialog.getnewsentencesignal.emit(output)

        self.hookdatacollecter[key].append(output)
        self.hookdatacollecter[key] = self.hookdatacollecter[key][-100:]
        gobject.baseobject.hookselectdialog.update_item_new_line.emit(key, output)

        return True

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

    def checkisusingembed(self, address, ctx1, ctx2):
        for pid in self.pids.copy():
            if self.Luna_checkisusingembed(pid, address, ctx1, ctx2):
                return True
        return False

    def useembed(self, address, ctx1, ctx2, use):
        for pid in self.pids.copy():
            self.Luna_useembed(pid, address, ctx1, ctx2, use)

    def dispatchtext(self, text):
        self.runonce_line = text
        return super().dispatchtext(text)

    def gettextonce(self):
        return self.runonce_line

    def end(self):
        self.detachall()
        time.sleep(0.1)

    def detachall(self):
        for pid in self.pids.copy():
            self.Luna_Detach(pid)
