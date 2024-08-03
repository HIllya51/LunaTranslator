import windows, os, winreg, winsharedutils, re, functools
from qtsymbols import *
from myutils.config import savehook_new_data, uid2gamepath
from gui.usefulwidget import (
    getlineedit,
    getsimplecombobox,
    getspinbox,
    getsimpleswitch,
    LFocusCombo,
    getspinbox,
    SplitLine,
)
from traceback import print_exc


class Launcher:
    name = ...
    id = ...

    def run(self, gameexe, config): ...

    def setting(self, layout, config): ...


class LEbase(Launcher):

    def runX(self, exe, usearg, dirpath, config): ...
    def run(self, game, config):
        dirpath = os.path.dirname(game)
        if game.lower()[-4:] not in [".lnk", ".exe"]:
            # 对于其他文件，需要AssocQueryStringW获取命令行才能正确le，太麻烦，放弃。
            windows.ShellExecute(None, "open", game, "", dirpath, windows.SW_SHOW)
            return

        execheck3264 = game
        usearg = '"{}"'.format(game)
        if game.lower()[-4:] == ".lnk":
            exepath, args, iconpath, dirp = winsharedutils.GetLnkTargetPath(game)

            if args != "":
                usearg = '"{}" {}'.format(exepath, args)
            elif exepath != "":
                usearg = '"{}"'.format(exepath)

            if exepath != "":
                execheck3264 = exepath

            if dirp != "":
                dirpath = dirp
        self.runX(execheck3264, usearg, dirpath, config)


class settingxx:
    use_which = ...

    def switchidx(self, w, config, idx):
        w.setCurrentIndex(idx)
        config[self.use_which] = idx

    def settingxx(self, layout, config, valid, call1, call2):

        stackw = QStackedWidget()
        stackw.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        if valid:
            switch = LFocusCombo()
            switch.addItems(["内置", "系统"])
            switch.currentIndexChanged.connect(
                functools.partial(self.switchidx, stackw, config)
            )
            layout.addRow("优先使用", switch)
            layout.addRow(SplitLine())

        w = QWidget()
        default = QFormLayout()
        default.setContentsMargins(0, 0, 0, 0)
        w.setLayout(default)

        call1(default, config)

        stackw.addWidget(w)
        layout.addRow(stackw)
        if valid:

            w = QWidget()
            default = QFormLayout()
            default.setContentsMargins(0, 0, 0, 0)
            w.setLayout(default)
            call2(default, config)
            stackw.addWidget(w)
            switch.setCurrentIndex(config.get(self.use_which, 0))


class le_internal(LEbase, settingxx):
    name = "Locale Emulator"
    id = "le"
    use_which = "le_use_which"
    default = dict(
        LCID=0x11, CodePage=932, RedirectRegistry=False, HookUILanguageAPI=False
    )

    def fundleproc(self):

        for key in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
            try:
                k = winreg.OpenKeyEx(
                    key,
                    r"Software\Classes\CLSID\{C52B9871-E5E9-41FD-B84D-C5ACADBEC7AE}\InprocServer32",
                    0,
                    winreg.KEY_QUERY_VALUE,
                )

                LEContextMenuHandler: str = winreg.QueryValueEx(k, "CodeBase")[0]
                winreg.CloseKey(k)
                if not LEContextMenuHandler.startswith("file:///"):
                    continue
                LEContextMenuHandler = LEContextMenuHandler[8:]
                LEProc = os.path.join(
                    os.path.dirname(LEContextMenuHandler), "LEProc.exe"
                )
                if not os.path.exists(LEProc):
                    continue
                return LEProc
            except:
                continue
        return None

    def valid(self):
        return (self.fundleproc() is not None) and (len(self.profiles()[1]) > 0)

    def profiles(self, exe=None):
        _Names = []
        _Guids = []

        def parseone(xmlpath):
            Names, Guids = [], []
            with open(xmlpath, "r", encoding="utf8") as ff:
                for Name, Guid in re.findall('Name="(.*?)" Guid="(.*?)"', ff.read()):
                    Names.append(Name)
                    Guids.append(Guid)
            return Names, Guids

        finds = [os.path.join(os.path.dirname(self.fundleproc()), "LEConfig.xml")]
        if exe:
            finds.append(exe + ".le.config")
        for f in finds:
            try:
                Names, Guids = parseone(f)
                _Guids += Guids
                _Names += Names
            except:
                pass

        return _Names, _Guids

    def runXX(self, exe, usearg, dirpath, config):
        LEProc = self.fundleproc()
        if not LEProc:
            return
        guids = self.profiles(config["gamepath"])[1]
        guid = config.get("leguid", None)
        if guid not in guids:
            guids = guids[0]
        arg = '"{}" -runas {} {}'.format(LEProc, guid, usearg)
        windows.CreateProcess(
            None,
            arg,
            None,
            None,
            False,
            0,
            None,
            dirpath,
            windows.STARTUPINFO(),
        )

    def settingX(self, layout, config):
        Names, Guids = self.profiles(config["gamepath"])
        layout.addRow(
            "Profile",
            getsimplecombobox(Names, config, "leguid", internal=Guids),
        )

    def loaddf(self, config):
        for k, v in self.default.items():
            k = "LE_" + k
            if k in config:
                continue
            config[k] = v

    def runX(self, exe, usearg, dirpath, config):
        if config.get(self.use_which, 0) == 1:

            valid = self.valid()
            if valid:
                return self.runXX(exe, usearg, dirpath, config)
        shareddllproxy = os.path.abspath("./files/plugins/shareddllproxy32")

        def _get(k):
            return config.get("LE_" + k, self.default[k])

        param = '{ANSICodePage} {OEMCodePage} {LCID} "{dirname}" {RedirectRegistry} {HookUILanguageAPI}'.format(
            LCID=_get("LCID"),
            OEMCodePage=_get("CodePage"),
            ANSICodePage=_get("CodePage"),
            dirname=dirpath,
            RedirectRegistry=int(_get("RedirectRegistry")),
            HookUILanguageAPI=int(_get("HookUILanguageAPI")),
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

    def switchidx(self, w, config, idx):
        w.setCurrentIndex(idx)
        config[self.use_which] = idx

    def setting(self, layout, config):
        valid = self.valid()
        self.settingxx(layout, config, valid, self.setting1, self.settingX)

    def setting1(self, layout, config):

        self.loaddf(config)
        layout.addRow("LCID", getspinbox(0, 0xFFFFF, config, "LE_LCID"))
        layout.addRow("CodePage", getspinbox(0, 0xFFFFF, config, "LE_CodePage"))
        layout.addRow(
            "RedirectRegistry", getsimpleswitch(config, "LE_RedirectRegistry")
        )
        layout.addRow(
            "HookUILanguageAPI", getsimpleswitch(config, "LE_HookUILanguageAPI")
        )


class NTLEAS64(LEbase, settingxx):
    name = "Ntleas"
    id = "ntleas"
    bit = 6
    bit64 = True
    use_which = "ntleas_use_which"
    default = dict(LCID=0x411, CodePage=932, TimeZone=540)

    def loaddf(self, config):
        for k, v in self.default.items():
            k = "NT_" + k
            if k in config:
                continue
            config[k] = v

    def runX(self, exe, usearg, dirpath, config):
        if config.get(self.use_which, 0) == 1:

            valid = self.valid()
            if valid:
                return self.runXX(exe, usearg, dirpath, config)
        shareddllproxy = os.path.abspath(
            ("./files/plugins/shareddllproxy32", "./files/plugins/shareddllproxy64")[
                self.bit == 6
            ]
        )

        def _get(k):
            return config.get("NT_" + k, self.default[k])

        param = "{dwCompOption} {dwCodePage} {dwLCID} {dwTimeZone}".format(
            dwCompOption=0,
            dwCodePage=_get("CodePage"),
            dwLCID=_get("LCID"),
            dwTimeZone=-_get("TimeZone"),
        )
        windows.CreateProcess(
            None,
            '"{}" {} {} {}'.format(shareddllproxy, "ntleas", param, usearg),
            None,
            None,
            False,
            0,
            None,
            dirpath,
            windows.STARTUPINFO(),
        )

    def setting1(self, layout, config):
        self.loaddf(config)

        layout.addRow("LCID", getspinbox(0, 0xFFFFF, config, "NT_LCID"))
        layout.addRow("CodePage", getspinbox(0, 0xFFFFF, config, "NT_CodePage"))
        layout.addRow("TimeZone", getspinbox(0, 0xFFFFF, config, "NT_TimeZone"))

    def setting(self, layout, config):
        valid = self.valid()
        self.settingxx(layout, config, valid, self.setting1, self.settingX)

    def fundleproc(self):

        try:
            CLSID = "{9C31DD66-412C-4B28-BD17-1F0BEBE29E8B}"

            k = winreg.OpenKeyEx(
                winreg.HKEY_LOCAL_MACHINE,
                rf"Software\Classes\CLSID\{CLSID}\InprocServer32",
                0,
                winreg.KEY_QUERY_VALUE,
            )

            LRSubMenuExtension: str = winreg.QueryValueEx(k, "")[0]
            winreg.CloseKey(k)
            LRProc = os.path.join(
                os.path.dirname(LRSubMenuExtension),
                ["x86", "x64"][self.bit64],
                "ntleas.exe",
            )
            if not os.path.exists(LRProc):
                return None
            return LRProc
        except:
            return None

    def valid(self):
        return self.fundleproc() is not None

    def runXX(self, exe, usearg, dirpath, config):
        LEProc = self.fundleproc()
        if not LEProc:
            return

        arg = '"{}"  {} {}'.format(
            LEProc,
            usearg,
            config.get("ntleasparam", '"C932" "L1041" "FMS PGothic" "P4"'),
        )
        windows.CreateProcess(
            None,
            arg,
            None,
            None,
            False,
            0,
            None,
            dirpath,
            windows.STARTUPINFO(),
        )

    def settingX(self, layout, config):
        if "ntleasparam" not in config:
            config["ntleasparam"] = '"C932" "L1041" "FMS PGothic" "P4"'

        layout.addRow(
            "params",
            getlineedit(config, "ntleasparam"),
        )


class NTLEAS32(NTLEAS64):
    bit = 3
    bit64 = False


class lr_internal(LEbase, settingxx):
    name = "Locale Remulator"
    id = "lr"
    use_which = "lr_use_which"
    default = dict(LCID=0x411, CodePage=932, TimeZone=540, HookIME=False, HookLCID=True)

    def loaddf(self, config):
        for k, v in self.default.items():
            k = "LR_" + k
            if k in config:
                continue
            config[k] = v

    def runX(self, exe, usearg, dirpath, config):
        if config.get(self.use_which, 0) == 1:

            valid = self.valid()
            if valid:
                return self.runXX(exe, usearg, dirpath, config)

        shareddllproxy = os.path.abspath("./files/plugins/shareddllproxy32")

        def _get(k):
            return config.get("LR_" + k, self.default[k])

        param = "{CodePage} {LCID} {Bias} {HookIME} {HookLCID}".format(
            LCID=_get("LCID"),
            CodePage=_get("CodePage"),
            Bias=_get("TimeZone"),
            HookIME=int(_get("HookIME")),
            HookLCID=int(_get("HookLCID")),
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

    def setting(self, layout, config):
        valid = self.valid()
        self.settingxx(layout, config, valid, self.setting1, self.settingX)

    def setting1(self, layout, config):
        self.loaddf(config)

        layout.addRow("LCID", getspinbox(0, 0xFFFFF, config, "LR_LCID"))
        layout.addRow("CodePage", getspinbox(0, 0xFFFFF, config, "LR_CodePage"))
        layout.addRow("TimeZone", getspinbox(0, 0xFFFFF, config, "LR_TimeZone"))
        layout.addRow("HookIME", getsimpleswitch(config, "LR_HookIME"))
        layout.addRow("HookLCID", getsimpleswitch(config, "LR_HookLCID"))

    def fundleproc(self):

        try:
            k = winreg.OpenKeyEx(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Classes\LRSubMenus.LRSubMenuExtension\CLSID",
                0,
                winreg.KEY_QUERY_VALUE,
            )
            CLSID: str = winreg.QueryValueEx(k, "")[0]

            winreg.CloseKey(k)
            k = winreg.OpenKeyEx(
                winreg.HKEY_LOCAL_MACHINE,
                rf"Software\Classes\CLSID\{CLSID}\InprocServer32",
                0,
                winreg.KEY_QUERY_VALUE,
            )

            LRSubMenuExtension: str = winreg.QueryValueEx(k, "CodeBase")[0]
            winreg.CloseKey(k)
            if not LRSubMenuExtension.startswith("file:///"):
                return None
            LRSubMenuExtension = LRSubMenuExtension[8:]
            LRProc = os.path.join(os.path.dirname(LRSubMenuExtension), "LRProc.exe")
            if not os.path.exists(LRProc):
                return None
            return LRProc
        except:

            return None

    def valid(self):
        return (self.fundleproc() is not None) and (len(self.profiles()[1]) > 0)

    def profiles(self):

        Names, Guids = [], []
        try:

            with open(
                os.path.join(os.path.dirname(self.fundleproc()), "LRConfig.xml"),
                "r",
                encoding="utf8",
            ) as ff:
                for Name, Guid in re.findall('Name="(.*?)" Guid="(.*?)"', ff.read()):
                    Names.append(Name)
                    Guids.append(Guid)
        except:
            pass
        return Names, Guids

    def runXX(self, exe, usearg, dirpath, config):
        LEProc = self.fundleproc()
        if not LEProc:
            return
        guids = self.profiles()[1]
        guid = config.get("lrguid", None)
        if guid not in guids:
            guids = guids[0]
        arg = '"{}"  {} {}'.format(LEProc, guid, usearg)
        windows.CreateProcess(
            None,
            arg,
            None,
            None,
            False,
            0,
            None,
            dirpath,
            windows.STARTUPINFO(),
        )

    def settingX(self, layout, config):
        Names, Guids = self.profiles()
        layout.addRow(
            "Profile",
            getsimplecombobox(Names, config, "lrguid", internal=Guids),
        )


class CommandLine(Launcher):
    name = "命令行启动"
    id = "cmd"

    def run(self, gameexe, config):
        dirpath = os.path.dirname(gameexe)

        usearg = config.get("startcmd", "{exepath}").format(exepath=gameexe)
        windows.CreateProcess(
            None,
            usearg,
            None,
            None,
            False,
            0,
            None,
            dirpath,
            windows.STARTUPINFO(),
        )

    def setting(self, layout, config):
        if "startcmd" not in config:
            config["startcmd"] = "{exepath}"

        layout.addRow(
            "命令行启动",
            getlineedit(config, "startcmd"),
        )


class Direct(Launcher):
    name = "直接启动"
    id = "direct"

    def run(self, gameexe, argsdict):
        dirpath = os.path.dirname(gameexe)
        windows.ShellExecute(None, "open", gameexe, "", dirpath, windows.SW_SHOW)


x86tools = [
    le_internal,
    lr_internal,
    NTLEAS32,
    CommandLine,
    Direct,
]
x64tools = [lr_internal, NTLEAS64, CommandLine, Direct]


def getgamecamptools(gameexe):
    b = windows.GetBinaryType(gameexe)
    if b == 6:
        _methods = x64tools
    else:
        _methods = x86tools
    ms = []
    for _ in _methods:
        ms.append(_)
    return ms


def fundlauncher(_id):
    for _ in x86tools + x64tools:
        if _.id != _id:
            continue
        return _
    return None


def localeswitchedrun(gameuid):
    config = savehook_new_data[gameuid]
    launch_method = config.get("launch_method", None)
    gameexe = uid2gamepath[gameuid]
    tools = getgamecamptools(gameexe)
    ids = [_.id for _ in getgamecamptools(uid2gamepath[gameuid])]
    if launch_method not in ids:
        index = 0
    else:
        index = ids.index(launch_method)
    tool: Launcher = tools[index]()
    tool.run(gameexe, config)


def maycreatesettings(layout, config, launcherid):
    launcher = fundlauncher(launcherid)()
    launcher.setting(layout, config)
