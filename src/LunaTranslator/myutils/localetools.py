import windows, os, NativeUtils, functools
from qtsymbols import *
from myutils.config import savehook_new_data, get_launchpath, globalconfig, _TR
from gobject import sys_le_xp
from gui.usefulwidget import getlineedit, getsimplecombobox, getsimplepatheditor
from traceback import print_exc
import xml.etree.ElementTree as ET


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
            exepath, args, iconpath, dirp = NativeUtils.GetLnkTargetPath(game)

            if args != "":
                usearg = '"{}" {}'.format(exepath, args)
            elif exepath != "":
                usearg = '"{}"'.format(exepath)

            if exepath != "":
                execheck3264 = exepath

            if dirp != "":
                dirpath = dirp
        self.runX(execheck3264, usearg, dirpath, config)


class le_internal(LEbase):
    name = "Locale Emulator"
    id = "le"
    default = dict(
        LCID=0x11, CodePage=932, RedirectRegistry=False, HookUILanguageAPI=False
    )

    def getlrpath(self, show=False):
        LEProc = globalconfig.get("le_extra_path", "")
        if not (LEProc and os.path.exists(LEProc)):
            if show:
                return _TR("内置")
            LEProc = "files/Locale/Locale.Emulator/LEProc.exe"
        return os.path.abspath(LEProc)

    def profiles(self, config):
        _Names = []
        _Guids = []
        _run_as_admins = []
        exe = config.get("gamepath", None)

        def parseone(xmlpath):
            Names, Guids, run_as_admins = [], [], []
            with open(xmlpath, "r", encoding="utf8") as ff:
                root = ET.fromstring(ff.read())
                profiles = root.find("Profiles").findall("Profile")

                for profile in profiles:
                    Names.append(profile.attrib.get("Name"))
                    Guids.append(profile.attrib.get("Guid"))
                    run_as_admins.append(
                        profile.find("RunAsAdmin").text.lower() == "true"
                    )

            return Names, Guids, run_as_admins

        finds = [os.path.join(os.path.dirname(self.getlrpath()), "LEConfig.xml")]
        if exe:
            finds.append(exe + ".le.config")
        for f in finds:
            try:
                Names, Guids, run_as_admins = parseone(f)
                _Guids += Guids
                _Names += Names
                _run_as_admins += run_as_admins
            except:
                pass

        return _Names, _Guids, _run_as_admins

    def runX(self, exe, usearg, dirpath, config):
        LEProc = self.getlrpath()
        prof = self.profiles(config)
        prof_ = self.profiles({})
        guid = config.get("leguid", None)
        if guid not in prof[1]:
            guid = prof[1][0]
        if guid in prof_[1]:
            idx = prof_[1].index(guid)
            admin = prof_[2][idx]
            arg = "-runas {} {}".format(guid, usearg)
        else:
            # 程序的配置运行
            arg = "-run {}".format(usearg)
            admin = False
        windows.ShellExecute(
            None,
            "runas" if admin else "open",
            LEProc,
            arg,
            dirpath,
            windows.SW_SHOWNORMAL,
        )

    def reselect(self, config, Guids, path):
        globalconfig["le_extra_path"] = path
        Names, _Guids, _ = self.profiles(config)
        self.__profiles.clear()
        self.__profiles.addItems(Names)
        Guids.clear()
        Guids.extend(_Guids)

    def setting(self, layout, config):
        Names, Guids, _ = self.profiles(config)
        self.__profiles = getsimplecombobox(
            Names, config, "leguid", internal=Guids, static=True
        )
        layout.addRow(
            "路径",
            getsimplepatheditor(
                self.getlrpath(show=True),
                False,
                False,
                filter1="LEProc.exe",
                callback=functools.partial(self.reselect, config, Guids),
                clearset=lambda: _TR("内置"),
                icons=("fa.gear", "fa.refresh"),
            ),
        )
        layout.addRow("Profile", self.__profiles)

    def loaddf(self, config):
        for k, v in self.default.items():
            k = "LE_" + k
            if k in config:
                continue
            config[k] = v


class NTLEAS64(LEbase):
    name = "Ntleas"
    id = "ntleas"
    bit = 6
    bit64 = True
    default = dict(LCID=0x411, CodePage=932, TimeZone=540)

    def loaddf(self, config):
        for k, v in self.default.items():
            k = "NT_" + k
            if k in config:
                continue
            config[k] = v

    def getlrpath(self, show=False):
        LEProc = globalconfig.get("ntleas_extra_path", "")
        if not (LEProc and os.path.exists(LEProc)):
            if show:
                return _TR("内置")
            LEProc = "files/Locale/ntleas046_x64/Placeholder"
        return os.path.abspath(LEProc)

    def runX(self, exe, usearg, dirpath, config):
        LEProc = os.path.join(
            os.path.dirname(self.getlrpath()),
            ["x86", "x64"][self.bit64],
            "ntleas.exe",
        )
        if not LEProc:
            return

        arg = "{} {}".format(
            usearg,
            config.get("ntleasparam", '"C932" "L1041" "FMS PGothic" "P4"'),
        )
        windows.ShellExecute(
            None,
            "open",
            LEProc,
            arg,
            dirpath,
            windows.SW_SHOWNORMAL,
        )

    def reselect(self, path):
        globalconfig["ntleas_extra_path"] = path

    def setting(self, layout, config):
        if "ntleasparam" not in config:
            config["ntleasparam"] = '"C932" "L1041" "FMS PGothic" "P4"'
        layout.addRow(
            "路径",
            getsimplepatheditor(
                self.getlrpath(show=True),
                False,
                False,
                filter1="ntleasWin.exe",
                callback=self.reselect,
                clearset=lambda: _TR("内置"),
                icons=("fa.gear", "fa.refresh"),
            ),
        )
        layout.addRow(
            "params",
            getlineedit(config, "ntleasparam"),
        )


class NTLEAS32(NTLEAS64):
    bit = 3
    bit64 = False


class lr_internal(LEbase):
    name = "Locale Remulator"
    id = "lr"
    default = dict(LCID=0x411, CodePage=932, TimeZone=540, HookIME=False, HookLCID=True)

    def loaddf(self, config):
        for k, v in self.default.items():
            k = "LR_" + k
            if k in config:
                continue
            config[k] = v

    def profiles(self, config):

        Names, Guids = [], []
        run_as_admins = []
        try:

            with open(
                os.path.join(
                    os.path.dirname(self.getlrpath()),
                    "LRConfig.xml",
                ),
                "r",
                encoding="utf8",
            ) as ff:
                root = ET.fromstring(ff.read())
                profiles = root.find("Profiles").findall("Profile")

                for profile in profiles:
                    Names.append(profile.attrib.get("Name"))
                    Guids.append(profile.attrib.get("Guid"))
                    run_as_admins.append(
                        profile.find("RunAsAdmin").text.lower() == "true"
                    )
        except:
            print_exc()
        return Names, Guids, run_as_admins

    def getlrpath(self, show=False):
        LEProc = globalconfig.get("lr_extra_path", "")
        if not (LEProc and os.path.exists(LEProc)):
            if show:
                return _TR("内置")
            LEProc = "files/Locale/Locale_Remulator/LRProc.exe"
        return os.path.abspath(LEProc)

    def runX(self, exe, usearg, dirpath, config):

        LEProc = self.getlrpath()
        prof = self.profiles(config)
        guid = config.get("lrguid", None)
        if guid not in prof[1]:
            guid = prof[1][0]
        idx = prof[1].index(guid)
        admin = prof[2][idx]
        windows.ShellExecute(
            None,
            "runas" if admin else "open",
            LEProc,
            "{} {}".format(guid, usearg),
            dirpath,
            windows.SW_SHOWNORMAL,
        )

    def reselect(self, config, Guids, path):
        globalconfig["lr_extra_path"] = path
        Names, _Guids, _ = self.profiles(config)
        self.__profiles.clear()
        self.__profiles.addItems(Names)
        Guids.clear()
        Guids.extend(_Guids)

    def setting(self, layout, config):
        Names, Guids, _ = self.profiles(config)
        self.__profiles = getsimplecombobox(
            Names, config, "lrguid", internal=Guids, static=True
        )
        layout.addRow(
            "路径",
            getsimplepatheditor(
                self.getlrpath(show=True),
                False,
                False,
                filter1="LRProc.exe",
                callback=functools.partial(self.reselect, config, Guids),
                clearset=lambda: _TR("内置"),
                icons=("fa.gear", "fa.refresh"),
            ),
        )
        layout.addRow("Profile", self.__profiles)


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


x86tools: "list[LEbase]" = [
    le_internal,
    lr_internal,
    NTLEAS32,
    CommandLine,
    Direct,
]
x64tools = [lr_internal, NTLEAS64, CommandLine, Direct]

if sys_le_xp:
    x86tools.remove(NTLEAS32)
    x86tools.insert(0, NTLEAS32)


def getgamecamptools(gameexe, b=None):
    if b is None:
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
    gameexe = get_launchpath(gameuid)
    gameexe = os.path.abspath(gameexe)
    b = windows.GetBinaryType(gameexe)
    launch_method = config.get("launch_method", {6: "direct", 0: x86tools[0].id}.get(b))
    tools = getgamecamptools(gameexe, b)
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
