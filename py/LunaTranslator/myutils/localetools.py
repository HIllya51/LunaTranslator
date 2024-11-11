import windows, os, winsharedutils, re, functools
from qtsymbols import *
from myutils.config import savehook_new_data, get_launchpath, globalconfig
from gui.usefulwidget import (
    getlineedit,
    getsimplecombobox,
    getspinbox,
    getsimpleswitch,
    SuperCombo,
    getspinbox,
    SplitLine,
    getsimplepatheditor,
    clearlayout,
)
from gui.dynalang import LFormLayout


class Launcher:
    name = ...
    id = ...

    def run(self, gameexe, config): ...

    def setting(self, layout, config): ...


class LEbase(Launcher):

    def runX(self, exe, usearg, dirpath, config): ...
    def run(self, game: str, config):
        dirpath = os.path.dirname(game)
        if not (game.lower().endswith(".exe") or game.lower().endswith(".lnk")):
            # 对于其他文件，需要AssocQueryStringW获取命令行才能正确le，太麻烦，放弃。
            windows.ShellExecute(None, "open", game, "", dirpath, windows.SW_SHOW)
            return

        execheck3264 = game
        usearg = '"{}"'.format(game)
        if game.lower().endswith(".lnk"):
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

    def switchidx(self, lay1, lay2, call1, call2, config, idx):
        clearlayout(lay1)
        clearlayout(lay2)
        config[self.use_which] = idx
        (call1, call2)[1 - idx](lay1, config)

    def settingxx(self, layout, config, call1, call2):

        switch = SuperCombo()
        switch.addItems(["外部", "内置"])
        lay1 = LFormLayout()
        lay2 = LFormLayout()
        layout.addRow("优先使用", switch)
        layout.addRow(SplitLine())
        layout.addRow(lay1)
        layout.addRow(lay2)

        switch.setCurrentIndex(config.get(self.use_which, 0))
        switch.currentIndexChanged.connect(
            functools.partial(self.switchidx, lay1, lay2, call1, call2, config)
        )
        switch.currentIndexChanged.emit(switch.currentIndex())


class le_internal(LEbase, settingxx):
    name = "Locale Emulator"
    id = "le"
    use_which = "le_use_which"
    default = dict(
        LCID=0x11, CodePage=932, RedirectRegistry=False, HookUILanguageAPI=False
    )

    def profiles(self, config):
        _Names = []
        _Guids = []
        exe = config.get("gamepath", None)

        def parseone(xmlpath):
            Names, Guids = [], []
            with open(xmlpath, "r", encoding="utf8") as ff:
                for Name, Guid in re.findall('Name="(.*?)" Guid="(.*?)"', ff.read()):
                    Names.append(Name)
                    Guids.append(Guid)
            return Names, Guids

        finds = [
            os.path.join(
                os.path.dirname(globalconfig.get("le_extra_path", "")), "LEConfig.xml"
            )
        ]
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
        LEProc = globalconfig.get("le_extra_path", "")
        if not LEProc:
            return
        guids = self.profiles(config)[1]
        guids_ = self.profiles({})[1]
        guid = config.get("leguid", None)
        if guid not in guids:
            guid = guids[0]
        if guid in guids_:
            arg = '"{}" -runas {} {}'.format(LEProc, guid, usearg)
        else:
            # 程序的配置运行
            arg = '"{}" -run {}'.format(LEProc, usearg)
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

    def reselect(self, config, Guids, path):
        globalconfig["le_extra_path"] = path
        Names, _Guids = self.profiles(config)
        self.__profiles.clear()
        self.__profiles.addItems(Names)
        Guids.clear()
        Guids.extend(_Guids)

    def settingX(self, layout, config):
        Names, Guids = self.profiles(config)
        self.__profiles = getsimplecombobox(Names, config, "leguid", internal=Guids)
        layout.addRow(
            "路径",
            getsimplepatheditor(
                globalconfig.get("le_extra_path", ""),
                False,
                False,
                filter1="LEProc.exe",
                callback=functools.partial(self.reselect, config, Guids),
            ),
        )
        layout.addRow(
            "Profile",
            self.__profiles,
        )

    def loaddf(self, config):
        for k, v in self.default.items():
            k = "LE_" + k
            if k in config:
                continue
            config[k] = v

    def runX(self, exe, usearg, dirpath, config):
        if config.get(self.use_which, 0) == 0:

            valid = os.path.exists(globalconfig.get("le_extra_path", ""))
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

    def setting(self, layout, config):
        self.settingxx(layout, config, self.setting1, self.settingX)

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
        if config.get(self.use_which, 0) == 0:

            valid = os.path.exists(self.__path())
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
        self.settingxx(layout, config, self.setting1, self.settingX)

    def __path(self):
        return os.path.join(
            os.path.dirname(globalconfig.get("ntleas_extra_path", "")),
            ["x86", "x64"][self.bit64],
            "ntleas.exe",
        )

    def runXX(self, exe, usearg, dirpath, config):
        LEProc = self.__path()
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

    def reselect(self, path):
        globalconfig["ntleas_extra_path"] = path

    def settingX(self, layout, config):
        if "ntleasparam" not in config:
            config["ntleasparam"] = '"C932" "L1041" "FMS PGothic" "P4"'
        layout.addRow(
            "路径",
            getsimplepatheditor(
                globalconfig.get("ntleas_extra_path", ""),
                False,
                False,
                filter1="ntleasWin.exe",
                callback=self.reselect,
            ),
        )
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
        if config.get(self.use_which, 0) == 0:

            valid = os.path.exists(globalconfig.get("lr_extra_path", ""))
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
        self.settingxx(layout, config, self.setting1, self.settingX)

    def setting1(self, layout, config):
        self.loaddf(config)

        layout.addRow("LCID", getspinbox(0, 0xFFFFF, config, "LR_LCID"))
        layout.addRow("CodePage", getspinbox(0, 0xFFFFF, config, "LR_CodePage"))
        layout.addRow("TimeZone", getspinbox(0, 0xFFFFF, config, "LR_TimeZone"))
        layout.addRow("HookIME", getsimpleswitch(config, "LR_HookIME"))
        layout.addRow("HookLCID", getsimpleswitch(config, "LR_HookLCID"))

    def profiles(self, config):

        Names, Guids = [], []
        try:

            with open(
                os.path.join(
                    os.path.dirname(globalconfig.get("lr_extra_path", "")),
                    "LRConfig.xml",
                ),
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
        LEProc = globalconfig.get("lr_extra_path", "")
        if not LEProc:
            return
        guids = self.profiles(config)[1]
        guid = config.get("lrguid", None)
        if guid not in guids:
            guid = guids[0]
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

    def reselect(self, config, Guids, path):
        globalconfig["lr_extra_path"] = path
        Names, _Guids = self.profiles(config)
        self.__profiles.clear()
        self.__profiles.addItems(Names)
        Guids.clear()
        Guids.extend(_Guids)

    def settingX(self, layout, config):
        Names, Guids = self.profiles(config)
        self.__profiles = getsimplecombobox(Names, config, "lrguid", internal=Guids)
        layout.addRow(
            "路径",
            getsimplepatheditor(
                globalconfig.get("lr_extra_path", ""),
                False,
                False,
                filter1="LRProc.exe",
                callback=functools.partial(self.reselect, config, Guids),
            ),
        )
        layout.addRow(
            "Profile",
            self.__profiles,
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
    gameexe = get_launchpath(gameuid)
    gameexe = os.path.abspath(gameexe)
    tools = getgamecamptools(gameexe)
    ids = [_.id for _ in tools]
    if launch_method not in ids:
        index = 0
    else:
        index = ids.index(launch_method)
    tool: Launcher = tools[index]()
    tool.run(gameexe, config)


def maycreatesettings(layout, config, launcherid):
    launcher = fundlauncher(launcherid)()
    launcher.setting(layout, config)
