from textio.textsource.textsourcebase import basetext
from myutils.wrapper import threader
import NativeUtils, windows, uuid, os, gobject, time
from LunaSubProcess import LunaSubProcess
from myutils.config import globalconfig, _TR


class atendrestorwindow(NativeUtils.AutoKillProcess):
    def __del__(self):
        if not self.b:
            NativeUtils.ShowLiveCaptionsWindow(self.pid, True)

    def __init__(self, pidorexe, kill: bool):
        super().__init__(pidorexe, kill=kill, hide=False)
        self.b = True

    def show(self, b):
        self.b = b
        NativeUtils.ShowLiveCaptionsWindow(self.pid, b)


class LiveCaptions:

    @threader
    def __dointernal(self, pid):
        last = ""
        lasttt = ""
        lastt = 0
        first = True
        uid = self.ref.uuid
        while (uid == self.ref.uuid) and (not self.ref.ending):
            if not self.ref.isautorunning:
                time.sleep(0.1)
                continue
            interval = globalconfig["sourcestatus2"]["mssr"]["refreshinterval2"]
            this = NativeUtils.GetLiveCaptionsText(pid)
            if first and this is not None:
                first = False
                self.engine.show(
                    not globalconfig["sourcestatus2"]["mssr"]["hidewindow"]
                )
            if not this:
                time.sleep(0.1)
                continue
            lines = this.splitlines()

            this = lines[-1]
            thist = time.time()
            need = this != last
            if thist - lastt > interval:
                if lasttt != this:
                    self.ref.dispatchtext(this, updateTranslate=True)
                lastt = thist
                lasttt = this
            if need:
                self.ref.updaterawtext(this)
            last = this

            time.sleep(0.1)

    def __init__(self, ref: "mssr"):
        self.ref = ref
        self.curr = ""
        pid = self.findlcpid()
        pidorexe = pid if pid else self.lcexe
        self.engine = atendrestorwindow(
            pidorexe, kill=globalconfig["sourcestatus2"]["mssr"]["autokill"]
        )

        self.__dointernal(self.engine.pid)

    lcexe = r"C:\Windows\{}\LiveCaptions.exe".format(
        ("Sysnative", "System32")[gobject.runtime_bit_64]
    )

    def findlcpid(self):
        for pid, exebase in NativeUtils.ListProcesses():
            if exebase.lower() != "livecaptions.exe":
                continue
            name_ = windows.GetProcessFileName(pid)
            if name_.lower() == self.lcexe.lower():
                return pid
        return None


class MSSR:
    @staticmethod
    def getlocaleandlv(path):
        with open(os.path.join(path, "sr.ini"), "r", encoding="utf8") as ff:
            lines = ff.read()
        lines = lines.splitlines()
        kv = {}
        for l in lines:
            ls = l.split("=")
            if len(ls) != 2:
                continue
            kv[ls[0]] = ls[1]
        locale_id = kv["locale-id"]
        locale = windows.LCIDToLocaleName(int(locale_id))
        lv = kv.get("license-version", "0")
        return locale, lv

    @staticmethod
    def findallmodel(checkX=False, check=None):
        __vis = []
        paths = []
        for _, p in [(None, check)] + NativeUtils.FindPackages(
            "MicrosoftWindows.Speech."
        ):
            try:
                lc, lv = MSSR.getlocaleandlv(p)
                __vis.append(lc)
            except:
                continue
            if checkX:
                return p
            paths.append(p)
        for _dir, _, __ in os.walk("."):
            if os.path.basename(_dir).startswith("MicrosoftWindows.Speech."):
                try:
                    lc, lv = MSSR.getlocaleandlv(_dir)
                    __vis.append(lc)
                except:
                    continue
                if checkX:
                    return _dir
                paths.append(_dir)
        if checkX:
            return None
        return __vis, paths

    def finddlldirectory(self):
        checkdir = lambda d: d and os.path.isfile(os.path.join(d, self.cogdll))
        dllp = r"C:\Windows\SystemApps\MicrosoftWindows.Client.Core_cw5n1h2txyewy\LiveCaptions"
        if checkdir(dllp):
            return dllp
        for _dir, _, __ in os.walk("."):
            if checkdir(_dir):
                return os.path.abspath(_dir)

        for _dir, _, __ in os.walk(r"C:\Windows\SystemApps"):
            if checkdir(_dir):
                return os.path.abspath(_dir)

    cogdll = "Microsoft.CognitiveServices.Speech.extension.embedded.sr.dll"

    def __init__(self, ref: "mssr"):
        self.ref = ref
        self.curr = ""

        path = globalconfig["sourcestatus2"]["mssr"]["path"]
        path = self.findallmodel(checkX=True, check=path)
        path: str = os.path.abspath(path) if path else None
        if not path:
            raise Exception("无可用语言")
        if not path.isascii():
            raise Exception("请勿使用非英文路径")

        dll = self.finddlldirectory()
        if not dll:
            raise Exception("找不到运行时")
        print(path, dll, NativeUtils.QueryVersion(os.path.join(dll, self.cogdll)))
        self.engine = LunaSubProcess.mssr(
            path,
            self.getsource(),
            dll,
            self.extralicense if (self.getlocaleandlv(path)[1] != "0") else "",
        )
        self.hwndChanged(self.ref.hwnd)
        self.listen()
        if globalconfig.get("autorun", True):
            self.runornot(True)

    def runornot(self, _):
        self.engine.runornot(_)

    def gethwndppid(self, hwnd):
        pid = windows.GetWindowThreadProcessId(hwnd)
        if not pid:
            return 0
        pexe = windows.GetProcessFileName(pid)
        ppid = pid
        while True:
            _ = NativeUtils.GetParentProcessID(ppid)
            if _ in (0, ppid):
                break
            if windows.GetProcessFileName(_) != pexe:
                break
            ppid = _
        return ppid

    def hwndChanged(self, hwnd):
        self.engine.write_pid(self.gethwndppid(hwnd))

    @property
    def extralicense(self):
        return globalconfig.get("MicrosoftWindows.Speech.License", "")

    def getsource(self):
        sources = ["loopback", "i", "o"]
        ins = []
        outs = []
        for _, _id in NativeUtils.ListEndpoints(True):
            sources.append(_id)
            ins.append(_id)
            print(_, _id)
        for _, _id in NativeUtils.ListEndpoints(False):
            sources.append(_id)
            outs.append(_id)
            print(_, _id)
        source = globalconfig["sourcestatus2"]["mssr"]["source"]
        if source and (source[1:] in sources) and (sources[0] in ("i", "o")):
            return source
        if source not in sources:
            source = sources[0]
        if source in outs:
            source = "o" + source
        elif source in ins:
            source = "i" + source
        return source

    @threader
    def listen(self):
        last = ""
        lastt = 0
        uid = self.ref.uuid
        while (uid == self.ref.uuid) and (not self.ref.ending):
            try:
                rec = self.engine.read_record()
            except BrokenPipeError:
                break  # mssr 子进程已退出 / 管道断开，退出监听
            kind = rec[0]
            if kind == "error":
                text = rec[1]
                if text.startswith("??"):
                    err = text[2:]
                    text = _TR("系统不支持环回录制")
                    if err:
                        hr = int(err)
                        text += ": {} {}".format(hex(hr)[2:], windows.FormatMessage(hr))
                gobject.base.displayinfomessage(text, "<msg_error_Origin>")
                raise Exception(text)
            elif kind == "result":
                _, ok, offset, duration, text = rec
                self.curr = text
                increased = text[len(last) :] if text.startswith(last) else ""
                last = text
                thist = time.time()
                if ok or (
                    thist - lastt
                    > globalconfig["sourcestatus2"]["mssr"]["refreshinterval"]
                ):
                    self.ref.dispatchtext(text, updateTranslate=True, statusok=ok)
                    lastt = thist
                self.ref.updaterawtext(text)
            elif kind == "status":
                t = rec[1]
                if t == 4:
                    gobject.base.displayinfomessage(
                        _TR("正在加载语音识别模型"), "<msg_info_refresh>"
                    )
                elif t == 1:
                    gobject.base.displayinfomessage(
                        _TR("加载完毕"), "<msg_info_refresh>"
                    )
                # t == 2 / 3：继续 / 暂停，忽略


class mssr(basetext):
    def end(self):
        self.engine = None

    def init(self):
        self.end()
        self.hwnd = None
        self.uuid = uuid.uuid4()
        if (
            os.path.exists(LiveCaptions.lcexe)
            and globalconfig["sourcestatus2"]["mssr"]["mode"] == "indirect"
        ):
            self.engine = LiveCaptions(self)
        else:
            try:
                self.engine = MSSR(self)
            except Exception as e:
                gobject.base.displayinfomessage(_TR(str(e)), "<msg_error_Origin>")

    def hwndChanged(self, hwnd):
        self.hwnd = hwnd
        if isinstance(self.engine, MSSR):
            self.engine.hwndChanged(hwnd)

    def runornot(self, _):
        if isinstance(self.engine, MSSR):
            self.engine.runornot(_)

    def gettextonce(self):
        if not self.engine:
            return ""
        return self.engine.curr
