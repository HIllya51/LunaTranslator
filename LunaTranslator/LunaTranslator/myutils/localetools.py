import windows, os


class leXX:
    name = ...

    @staticmethod
    def run(bit, config, usearg, dirpath): ...


class LocaleEmulator(leXX):
    name = "Locale Emulator"

    @staticmethod
    def run(bit, config, usearg, dirpath):
        shareddllproxy = os.path.abspath("./files/plugins/shareddllproxy32")
        param = '{ANSICodePage} {OEMCodePage} {LCID} "{dirname}" {RedirectRegistry} {HookUILanguageAPI}'.format(
            LCID=0x11,
            OEMCodePage=932,
            ANSICodePage=932,
            dirname=dirpath,
            RedirectRegistry=int(False),
            HookUILanguageAPI=int(False),
        )
        windows.CreateProcess(
            None,
            '"{}" {} {} {}'.format(shareddllproxy, "le", param, usearg),
            None,
            None,
            False,
            0,
            None,
            dirpath,
            windows.STARTUPINFO(),
        )


class NTLEAS(leXX):
    name = "Ntleas"

    @staticmethod
    def run(bit, config, usearg, dirpath):
        shareddllproxy = os.path.abspath(
            ("./files/plugins/shareddllproxy32", "./files/plugins/shareddllproxy64")[
                bit == 6
            ]
        )
        param = '{dwCompOption} {dwCodePage} {dwLCID} {dwTimeZone}'.format(
            dwCompOption=0,
            dwCodePage=932,
            dwLCID=0x411,
            dwTimeZone=-540,
        )
        windows.CreateProcess(
            None,
            '"{}" {} {} {}'.format(shareddllproxy, "ntleas",  param,usearg),
            None,
            None,
            False,
            0,
            None,
            dirpath,
            windows.STARTUPINFO(),
        )


class LocaleRemulator(leXX):
    name = "Locale Remulator"

    @staticmethod
    def run(bit, config, usearg, dirpath):
        shareddllproxy = os.path.abspath("./files/plugins/shareddllproxy32")
        param = "{CodePage} {LCID} {Bias} {HookIME} {HookLCID}".format(
            LCID=0x0411,
            CodePage=932,
            Bias=540,
            HookIME=0,
            HookLCID=1,
        )
        windows.CreateProcess(
            None,
            '"{}" {} {} {}'.format(shareddllproxy, "LR", param, usearg),
            None,
            None,
            False,
            0,
            None,
            dirpath,
            windows.STARTUPINFO(),
        )


x86tools = [LocaleEmulator, LocaleRemulator, NTLEAS]
x64tools = [LocaleRemulator, NTLEAS]


def getgamecamptools(gameexe):
    b = windows.GetBinaryType(gameexe)
    if b == 6:
        _methods = x64tools
    else:
        _methods = x86tools
    return _methods


def getgamecamptoolsname(gameexe):
    return [_.name for _ in getgamecamptools(gameexe)]


def localeswitchedrun(gameexe, idx, usearg, dirpath):
    b = windows.GetBinaryType(gameexe)
    tools = getgamecamptools(gameexe)
    if idx < 0 or idx >= len(tools):
        idx = 0

    tool = tools[idx]
    tool.run(b, 0, usearg, dirpath)
