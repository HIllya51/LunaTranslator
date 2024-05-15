import threading, windows
from queue import Queue
import re, os
import time, gobject
from collections import OrderedDict
import codecs, functools
from winsharedutils import Is64bit
from myutils.config import globalconfig, savehook_new_data, static_data
from textsource.textsourcebase import basetext
from myutils.utils import checkchaos
from myutils.hwnd import injectdll
from myutils.wrapper import threader
from ctypes import (
    CDLL,
    CFUNCTYPE,
    c_bool,
    POINTER,
    Structure,
    c_int,
    pointer,
    c_char_p,
    c_wchar_p,
    c_uint64,
    sizeof,
    c_void_p,
    cast,
    c_wchar,
    c_uint32,
    c_uint8,
    c_uint,
    c_char,
)
from ctypes.wintypes import DWORD, LPCWSTR, HANDLE
from gui.usefulwidget import getQMessageBox

MAX_MODULE_SIZE = 120
HOOK_NAME_SIZE = 60
HOOKCODE_LEN = 500


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


class texthook(basetext):
    def __init__(
        self, pids, hwnd, pname, autostarthookcode=None, needinserthookcode=None
    ):
        if autostarthookcode is None:
            autostarthookcode = []
        if needinserthookcode is None:
            needinserthookcode = []
        self.keepref = []
        self.newline = Queue()
        self.newline_delaywait = Queue()
        self.is64bit = Is64bit(pids[0])
        self.hookdatacollecter = OrderedDict()
        self.hooktypecollecter = OrderedDict()
        self.currentname = None
        self.reverse = {}
        self.forward = []
        self.selectinghook = None
        self.selectedhook = []
        self.selectedhookidx = []
        self.allow_set_text_name = globalconfig["allow_set_text_name"]

        self.pids = pids
        self.connectedpids = []
        self.pname = pname
        self.hwnd = hwnd
        self.runonce_line = ""
        self.autostarthookcode = [tuple(__) for __ in autostarthookcode]
        self.isremoveuseless = savehook_new_data[self.pname]["removeuseless"] and len(
            self.autostarthookcode
        )
        self.needinserthookcode = needinserthookcode
        self.removedaddress = []

        gobject.baseobject.hookselectdialog.changeprocessclearsignal.emit()
        if (
            len(autostarthookcode) == 0
            and len(savehook_new_data[self.pname]["embedablehook"]) == 0
        ):
            gobject.baseobject.hookselectdialog.realshowhide.emit(True)

        self.delaycollectallselectedoutput()

        super(texthook, self).__init__(*self.checkmd5prefix(pname))
        self.declare()
        self.start()

    def declare(self):
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

    def QueryThreadHistory(self, tp):
        ws = self.Luna_QueryThreadHistory(tp)
        string = cast(ws, c_wchar_p).value
        self.Luna_FreePtr(ws)
        return string

    def Luna_Startup(self):
        procs = [
            ProcessEvent(self.onprocconnect),
            ProcessEvent(self.connectedpids.remove),
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

    def start(self):

        self.Luna_Startup()
        self.setsettings()

        injectpids = []
        for pid in self.pids:
            if globalconfig["use_yapi"]:
                self.Luna_Inject(pid, os.path.abspath("./files/plugins/LunaHook"))
            else:
                if self.Luna_CreatePipeAndCheck(pid):
                    injectpids.append(pid)
        if len(injectpids):
            arch = ["32", "64"][self.is64bit]
            injecter = os.path.abspath(
                "./files/plugins/shareddllproxy{}.exe".format(arch)
            )
            dll = os.path.abspath(
                "./files/plugins/LunaHook/LunaHook{}.dll".format(arch)
            )
            print(injecter, os.path.exists(injecter))
            print(dll, os.path.exists(dll))
            # subprocess.Popen('"{}" dllinject {} "{}"'.format(injecter,pid,dll))
            injectdll(injectpids, injecter, dll)

    def onprocconnect(self, pid):
        self.connectedpids.append(pid)
        time.sleep(savehook_new_data[self.pname]["inserthooktimeout"] / 1000)
        for hookcode in self.needinserthookcode:
            self.Luna_InsertHookCode(pid, hookcode)
        self.showgamename()
        self.flashembedsettings(pid)

    def newhookinsert(self, addr, hcode):
        for _hc, _addr, _ctx1, _ctx2 in savehook_new_data[self.pname]["embedablehook"]:
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

    def getembedtext(self, text, tp):
        if self.safeembedcheck(text) == False:
            self.embedcallback(text, text)
            self.newline.put((text, True, lambda trans: 1, True))
            return
        if globalconfig["autorun"] == False:
            self.embedcallback(text, text)
            return
        if self.checkisusingembed(tp.addr, tp.ctx, tp.ctx2):
            self.newline.put(
                (text, True, functools.partial(self.embedcallback, text), True)
            )

    def embedcallback(self, text, trans):

        for pid in self.connectedpids:
            self.Luna_embedcallback(pid, text, trans)

    def flashembedsettings(self, pid=None):
        if pid:
            pids = [pid]
        else:
            pids = self.connectedpids.copy()
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

    def match_compatibility(self, tp, hc, autostarthookcode):
        base = (tp.ctx & 0xFFFF, tp.ctx2 & 0xFFFF, hc) == (
            autostarthookcode[2] & 0xFFFF,
            autostarthookcode[3] & 0xFFFF,
            autostarthookcode[5],
        )
        name = (hc[:8] == "UserHook" and autostarthookcode[-1][:8] == "UserHook") or (
            hc == autostarthookcode[-1]
        )
        return base and name

    def onnewhook(self, hc, hn, tp):
        key = (hc, hn.decode("utf8"), tp)

        self.hookdatacollecter[key] = []
        self.hooktypecollecter[key] = 0

        if self.isremoveuseless:
            if tp.addr not in [_[1] for _ in self.autostarthookcode]:
                self.Luna_RemoveHook(tp.processId, tp.addr)
                return False

        select = False
        for _i, autostarthookcode in enumerate(self.autostarthookcode):
            if self.match_compatibility(tp, hc, autostarthookcode):
                self.selectedhook += [key]
                self.selectinghook = key
                select = True
                break
        gobject.baseobject.hookselectdialog.addnewhooksignal.emit(key, select)
        return True

    def setsettings(self):
        self.Luna_Settings(
            globalconfig["textthreaddelay"],
            globalconfig["direct_filterrepeat"],
            self.codepage(),
            globalconfig["maxBufferSize"],
            globalconfig["maxHistorySize"],
        )

    def codepage(self):
        try:
            cpi = savehook_new_data[self.pname]["codepage_index"]
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
        usestruct.boundaryModule = os.path.basename(self.pname)
        usestruct.jittype = 0
        return usestruct

    @threader
    def findhook(self, usestruct):
        savefound = {}
        pids = self.connectedpids.copy()
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
        for pid in self.connectedpids:
            succ = self.Luna_InsertHookCode(pid, hookcode) and succ
        if succ == False:
            getQMessageBox(
                gobject.baseobject.hookselectdialog,
                "Error",
                "Invalie Hook Code Format!",
            )

    def removehook(self, pid, address):
        for pid in self.connectedpids:
            self.Luna_RemoveHook(pid, address)

    @threader
    def delaycollectallselectedoutput(self):
        collector = []
        while True:
            _ = self.newline_delaywait.get()
            collector.append(_)
            time.sleep(globalconfig["textthreaddelay"] / 1000)
            while self.newline_delaywait.empty() == False:
                collector.append(self.newline_delaywait.get())
            self.newline.put(collector)
            self.runonce_line = collector
            collector = []

    def handle_output(self, hc, hn, tp, output):

        if globalconfig["filter_chaos_code"] and checkchaos(output):
            return False
        key = (hc, hn.decode("utf8"), tp)

        if self.hooktypecollecter[key] == 1:
            self.currentname = output
        if len(self.selectedhook) == 1:
            if key in self.selectedhook:
                self.newline.put(output)
                self.runonce_line = output
        else:
            if key in self.selectedhook:
                self.newline_delaywait.put(output)
        if key == self.selectinghook:
            gobject.baseobject.hookselectdialog.getnewsentencesignal.emit(output)

        self.hookdatacollecter[key].append(output)
        self.hookdatacollecter[key] = self.hookdatacollecter[key][-100:]
        gobject.baseobject.hookselectdialog.update_item_new_line.emit(key, output)

        return True

    def serialkey(self, key):
        hc, hn, tp = key
        return (tp.processId, tp.addr, tp.ctx, tp.ctx2, hn, hc)

    def serialselectedhook(self):
        xx = []
        for key in self.selectedhook:
            xx.append(self.serialkey(key))
        return xx

    def checkisusingembed(self, address, ctx1, ctx2):
        for pid in self.connectedpids:
            if self.Luna_checkisusingembed(pid, address, ctx1, ctx2):
                return True
        return False

    def useembed(self, address, ctx1, ctx2, use):
        for pid in self.connectedpids:
            self.Luna_useembed(pid, address, ctx1, ctx2, use)

    def gettextthread(self):
        text = self.newline.get()
        while self.newline.empty() == False:
            text = self.newline.get()
        return text

    def gettextonce(self):

        return self.runonce_line

    def end(self):
        for pid in self.connectedpids:
            self.Luna_Detach(pid)
        time.sleep(0.1)
        super().end()
