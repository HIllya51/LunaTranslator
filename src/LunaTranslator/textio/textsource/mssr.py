from textio.textsource.textsourcebase import basetext
from myutils.wrapper import threader
import NativeUtils, windows, uuid, os, gobject
from ctypes import c_int
from myutils.config import globalconfig, _TR
from myutils.mecab import punctuations


class mssr(basetext):
    def end(self):
        # listen里循环引用
        self.engine = None

    def runornot(self, _):
        windows.SetEvent(self.notify)

    def init(self):
        self.startsql(gobject.gettranslationrecorddir("0_mssr.sqlite"))
        self.curr = ""
        try:
            path = globalconfig["sourcestatus2"]["mssr"]["path"]
            if not (path and os.path.exists(path)):
                path = NativeUtils.FindPackages("MicrosoftWindows.Speech.")[0][1]
                globalconfig["sourcestatus2"]["mssr"]["path"] = path
        except:
            gobject.baseobject.translation_ui.displaymessagebox.emit(
                "错误", "无可用语言"
            )
            return

        pipename = "\\\\.\\Pipe\\" + str(uuid.uuid4())
        waitsignal = str(uuid.uuid4())
        notify = str(uuid.uuid4())
        self.notify = NativeUtils.SimpleCreateEvent(notify)
        self.engine = NativeUtils.AutoKillProcess(
            'files/shareddllproxy64.exe mssr {} {} {} "{}" {}'.format(
                pipename,
                waitsignal,
                notify,
                path,
                globalconfig["sourcestatus2"]["mssr"]["source"],
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
        last = ""
        while not self.ending:
            iserr = c_int.from_buffer_copy(windows.ReadFile(self.hPipe, 4)).value
            if iserr:
                sz = c_int.from_buffer_copy(windows.ReadFile(self.hPipe, 4)).value
                text = windows.ReadFile(self.hPipe, sz).decode()
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
                    if ok or any(_ in punctuations for _ in increased):
                        self.dispatchtext(text)
                elif t == 4:
                    gobject.baseobject.displayinfomessage(
                        _TR("正在加载语音识别模型"), "<msg_info_refresh>"
                    )
                elif t == 1:
                    gobject.baseobject.displayinfomessage(
                        _TR("加载完毕"), "<msg_info_refresh>"
                    )
                elif t == 2:
                    # 继续
                    pass
                elif t == 3:
                    gobject.baseobject.displayinfomessage(
                        _TR("已暂停"), "<msg_info_refresh>"
                    )

    def gettextonce(self):
        return self.curr
