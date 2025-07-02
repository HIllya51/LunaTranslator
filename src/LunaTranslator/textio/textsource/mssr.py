from textio.textsource.textsourcebase import basetext
from myutils.wrapper import threader
import NativeUtils, windows, uuid, os, gobject, time
from ctypes import c_int
from myutils.config import globalconfig, _TR
from myutils.mecab import punctuations


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


def findallmodel(checkX=False, check=None):
    __vis = []
    paths = []
    extra = globalconfig.get("MicrosoftWindows.Speech.License", "")
    for _, p in [(None, check)] + NativeUtils.FindPackages("MicrosoftWindows.Speech."):
        try:
            lc, lv = getlocaleandlv(p)
            if lv != "0" and not extra:
                continue
            __vis.append(lc)
        except:
            continue
        if checkX:
            return p
        paths.append(p)
    for _dir, _, __ in os.walk("."):
        if os.path.basename(_dir).startswith("MicrosoftWindows.Speech."):
            try:
                lc, lv = getlocaleandlv(_dir)
                if lv != "0" and not extra:
                    continue
                __vis.append(lc)
            except:
                continue
            if checkX:
                return _dir
            paths.append(_dir)
    if checkX:
        return None
    return __vis, paths


class mssr(basetext):
    def end(self):
        # listen里循环引用
        self.engine = None

    def runornot(self, _):
        windows.SetEvent(self.notify)

    def finddlldirectory(self):
        dll = "Microsoft.CognitiveServices.Speech.extension.embedded.sr.dll"
        checkdir = lambda d: d and os.path.isfile(os.path.join(d, dll))
        dllp = r"C:\Windows\SystemApps\MicrosoftWindows.Client.Core_cw5n1h2txyewy\LiveCaptions"
        if checkdir(dllp):
            return dllp
        for _dir, _, __ in os.walk("."):
            if checkdir(_dir):
                return os.path.abspath(_dir)

        for _dir, _, __ in os.walk(r"C:\Windows\SystemApps"):
            if checkdir(_dir):
                return os.path.abspath(_dir)

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

    @property
    def extralicense(self):
        return globalconfig.get("MicrosoftWindows.Speech.License", "")

    def init(self):

        self.startsql(gobject.gettranslationrecorddir("0_mssr.sqlite"))
        self.curr = ""
        path = globalconfig["sourcestatus2"]["mssr"]["path"]
        path = findallmodel(checkX=True, check=path)
        if not path:
            gobject.base.displayinfomessage(_TR("无可用语言"), "<msg_error_Origin>")
            return

        dll = self.finddlldirectory()
        if not dll:
            gobject.base.displayinfomessage(_TR("找不到运行时"), "<msg_error_Origin>")
            return
        print(path, dll)
        pipename = "\\\\.\\Pipe\\" + str(uuid.uuid4())
        waitsignal = str(uuid.uuid4())
        notify = str(uuid.uuid4())
        self.notify = NativeUtils.SimpleCreateEvent(notify)
        self.engine = NativeUtils.AutoKillProcess(
            'files/shareddllproxy64.exe mssr {} {} {} "{}" {} "{}" "{}"'.format(
                pipename,
                waitsignal,
                notify,
                path,
                self.getsource(),
                dll,
                self.extralicense if (getlocaleandlv(path)[1] != "0") else "",
            )
        )
        windows.WaitForSingleObject(NativeUtils.SimpleCreateEvent(waitsignal))
        windows.WaitNamedPipe(pipename)
        self.hPipe = windows.CreateFile(pipename)
        self.listen()
        if globalconfig["autorun"]:
            windows.SetEvent(self.notify)

    @threader
    def listen(self):
        punctuationswithoutspace = punctuations.copy()
        punctuationswithoutspace.remove(" ")
        last = ""
        lastt = 0
        while not self.ending:
            iserr = c_int.from_buffer_copy(windows.ReadFile(self.hPipe, 4)).value
            if iserr:
                sz = c_int.from_buffer_copy(windows.ReadFile(self.hPipe, 4)).value
                text = windows.ReadFile(self.hPipe, sz).decode()
                gobject.base.displayinfomessage(text, "<msg_error_Origin>")
                raise Exception(text)
            else:
                t = c_int.from_buffer_copy(windows.ReadFile(self.hPipe, 4)).value
                if t == 0:
                    ok = c_int.from_buffer_copy(windows.ReadFile(self.hPipe, 4)).value
                    offset = c_int.from_buffer_copy(
                        windows.ReadFile(self.hPipe, 4)
                    ).value
                    duration = c_int.from_buffer_copy(
                        windows.ReadFile(self.hPipe, 4)
                    ).value
                    sz = c_int.from_buffer_copy(windows.ReadFile(self.hPipe, 4)).value
                    text = windows.ReadFile(self.hPipe, sz).decode()
                    # print(bool(ok), offset, duration, text)
                    self.curr = text
                    increased = text[len(last) :] if text.startswith(last) else ""
                    #  print(increased, any(_ in punctuations for _ in increased))
                    last = text
                    thist = time.time()
                    self.updaterawtext(text)
                    if (
                        ok
                        or (
                            thist - lastt
                            > globalconfig["sourcestatus2"]["mssr"]["refreshinterval"]
                        )
                        or any(_ in punctuationswithoutspace for _ in increased)
                    ):
                        self.dispatchtext(text, updateTranslate=True)
                        lastt = thist
                elif t == 4:
                    gobject.base.displayinfomessage(
                        _TR("正在加载语音识别模型"), "<msg_info_refresh>"
                    )
                elif t == 1:
                    gobject.base.displayinfomessage(
                        _TR("加载完毕"), "<msg_info_refresh>"
                    )
                elif t == 2:
                    # 继续
                    pass
                elif t == 3:
                    # 暂停
                    pass

    def gettextonce(self):
        return self.curr
