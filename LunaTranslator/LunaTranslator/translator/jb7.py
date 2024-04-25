from translator.basetranslator import basetrans
import ctypes
import os, time
import windows
from myutils.subproc import subproc_w, autoproc


class TS(basetrans):
    def inittranslator(self):

        self.path = None
        self.userdict = None
        self.checkpath()

    def checkpath(self):
        if self.config["路径"] == "":
            return False
        if os.path.exists(self.config["路径"]) == False:
            return False
        if self.config["路径"] != self.path or self.userdict != (
            self.config["用户词典1(可选)"],
            self.config["用户词典2(可选)"],
            self.config["用户词典3(可选)"],
        ):
            self.path = self.config["路径"]
            self.userdict = (
                self.config["用户词典1(可选)"],
                self.config["用户词典2(可选)"],
                self.config["用户词典3(可选)"],
            )
            self.dllpath = os.path.join(self.path, "JBJCT.dll")
            dictpath = ""
            for d in self.userdict:
                if os.path.exists(d):
                    d = os.path.join(d, "Jcuser")
                    dictpath += ' "{}" '.format(d)

            t = time.time()
            t = str(t)
            pipename = "\\\\.\\Pipe\\jbj7_" + t
            waitsignal = "jbjwaitload_" + t

            self.engine = autoproc(
                subproc_w(
                    './files/plugins/shareddllproxy32.exe jbj7 "{}" {} {} '.format(
                        self.dllpath, pipename, waitsignal
                    )
                    + dictpath,
                    name="jbj7",
                )
            )
            #!!!!!!!!!!!!!!stdout=subprocess.PIPE 之后，隔一段时间之后，exe侧writefile就写不进去了！！！！！不知道为什么！！！

            windows.WaitForSingleObject(
                windows.AutoHandle(windows.CreateEvent(False, False, waitsignal)),
                windows.INFINITE,
            )
            windows.WaitNamedPipe(pipename, windows.NMPWAIT_WAIT_FOREVER)
            self.hPipe = windows.AutoHandle(
                windows.CreateFile(
                    pipename,
                    windows.GENERIC_READ | windows.GENERIC_WRITE,
                    0,
                    None,
                    windows.OPEN_EXISTING,
                    windows.FILE_ATTRIBUTE_NORMAL,
                    None,
                )
            )
        return True

    def packuint32(self, i):  # int -> str
        return bytes(
            chr((i >> 24) & 0xFF)
            + chr((i >> 16) & 0xFF)
            + chr((i >> 8) & 0xFF)
            + chr(i & 0xFF),
            encoding="latin-1",
        )

    def unpackuint32(self, s):  #
        print(s)
        return ((s[0]) << 24) | ((s[1]) << 16) | ((s[2]) << 8) | (s[3])

    def x64(self, content: str):
        if self.tgtlang not in ["936", "950"]:
            return ""
        t = time.time()
        if self.checkpath() == False:
            return "error"
        content = content.replace("\r", "\n")
        lines = content.split("\n")
        ress = []
        for line in lines:
            if len(line) == 0:
                continue
            code1 = line.encode("utf-16-le")
            windows.WriteFile(self.hPipe, self.packuint32(int(self.tgtlang)) + code1)
            xx = windows.ReadFile(self.hPipe, 65535)
            xx = xx.decode("utf-16-le", errors="ignore")
            ress.append(xx)
        return "\n".join(ress)

    def x86(self, content):
        CODEPAGE_JA = 932
        CODEPAGE_GB = 936
        CODEPAGE_BIG5 = 950
        BUFFER_SIZE = 3000
        # if globalconfig['fanjian'] in [0,1,4]:
        #     code=CODEPAGE_GB
        # else:
        #     code=CODEPAGE_BIG5
        code = CODEPAGE_GB

        size = BUFFER_SIZE
        out = ctypes.create_unicode_buffer(size)
        buf = ctypes.create_unicode_buffer(size)
        outsz = ctypes.c_int(size)
        bufsz = ctypes.c_int(size)
        try:
            self.dll.JC_Transfer_Unicode(
                0,  # int, unknown
                CODEPAGE_JA,  # uint     from, supposed to be 0x3a4 (cp932)
                code,  # uint to, eighter cp950 or cp932
                1,  # int, unknown
                1,  # int, unknown
                content,  # python 默认unicode 所有不用u'
                out,  # wchar_t*
                ctypes.byref(outsz),  # ∫
                buf,  # wchar_t*
                ctypes.byref(bufsz),
            )  # ∫
        except:
            pass
        return out.value

    def translate(self, content):

        return self.x64(content)

    def langmap(self):
        return {"zh": "936", "cht": "950"}
