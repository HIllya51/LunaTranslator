import json
import windows, gobject, os, copy
from myutils.config import magpie_config, uid2gamepath, savehook_new_data
import NativeUtils, functools
from myutils.wrapper import threader


class MagpieConfig:
    @staticmethod
    def remove(gameuid):
        path = os.path.normpath(uid2gamepath[gameuid])
        for profile in magpie_config["profiles"].copy():
            if path == profile.get("pathRule"):
                magpie_config["profiles"].remove(profile)
                break

    @staticmethod
    def findHWNDIndex(hwnd):
        if not hwnd:
            return 0
        path = windows.GetProcessFileName(windows.GetWindowThreadProcessId(hwnd))
        for i, profile in enumerate(magpie_config["profiles"]):
            if path == profile.get("pathRule"):
                return i
        return 0

    @staticmethod
    def find(gameuid, notexitscreate=False):
        if not gameuid:
            return magpie_config["profiles"][0]
        path = os.path.normpath(uid2gamepath[gameuid])
        found = None
        for profile in magpie_config["profiles"]:
            if path == profile.get("pathRule"):
                found = profile
                break
        if notexitscreate and not found:
            cp = copy.deepcopy(magpie_config["profiles"][0])
            cp["pathRule"] = path
            cp["name"] = savehook_new_data[gameuid]["title"]
            cp["packaged"] = False
            cp["classNameRule"] = "PLACEHOLDER"
            cp["launcherPath"] = ""
            cp["launchParameters"] = ""
            cp["autoScale"] = 0
            magpie_config["profiles"].append(cp)
            found = cp
        return found


class AdapterService:
    AdaptersServiceStartMonitor_Callback_ptrs = []

    @staticmethod
    def AdaptersServiceStartMonitor_Callback(callback):
        callback(AdapterService.Infos())

    @staticmethod
    def Infos():
        ret = []

        def __(idx, vendorId, deviceId, description):
            ret.append([idx, vendorId, deviceId, description])

        NativeUtils.AdaptersServiceAdapterInfos(
            NativeUtils.AdaptersServiceAdapterInfos_Callback(__)
        )
        return ret

    @staticmethod
    def init(callback):
        AdaptersServiceStartMonitor_Callback_ptr = (
            NativeUtils.AdaptersServiceStartMonitor_Callback(
                functools.partial(
                    AdapterService.AdaptersServiceStartMonitor_Callback, callback
                )
            )
        )
        AdapterService.AdaptersServiceStartMonitor_Callback_ptrs.append(
            AdaptersServiceStartMonitor_Callback_ptr
        )
        NativeUtils.AdaptersServiceStartMonitor(
            AdaptersServiceStartMonitor_Callback_ptr
        )

    @staticmethod
    def uninit():
        NativeUtils.AdaptersServiceUninitialize()


class MagpieBuiltin:
    def __init__(self, setuistatus) -> None:

        self._setuistatus = setuistatus
        self.full = True
        self.hwnd = None
        self.hasend = False
        self.init()

    def setuistatus(self, current):
        if self.hasend:
            return
        self._setuistatus(current)
        self.full = not current

    @threader
    def callstatuschange(self, hwnd, windowmode):
        self.callstatuschange_(hwnd, windowmode)

    def callstatuschange_(self, hwnd, windowmode):
        hwnd = windows.GetAncestor(hwnd)
        self.hwnd = hwnd
        if self.changestatus(hwnd, self.full, windowmode):
            self.setuistatus(self.full)

    @threader
    def endX(self):
        self.hasend = True
        ret = False
        if not self.full and self.hwnd:
            self.callstatuschange_(self.hwnd, False)
            ret = True
        self.end()

        return ret

    def saveconfig(self):
        with open(self.jspath, "w", encoding="utf-8") as ff:
            ff.write(
                json.dumps(magpie_config, ensure_ascii=False, sort_keys=False, indent=4)
            )

    def init(self):
        self.jspath = gobject.gettempdir("magpie.config.json")
        self.engine = NativeUtils.AutoKillProcess(
            'files/Magpie/Magpie.Core.exe "{}"'.format(self.jspath),
            "files/Magpie",
        )
        self.__reload()
        waitsignal = "Magpie_notify_prepared_ok_" + str(self.engine.pid)
        windows.WaitForSingleObject(NativeUtils.SimpleCreateEvent(waitsignal))

    @threader
    def __reload(self):
        windows.WaitForSingleObject(
            windows.OpenProcess(windows.SYNCHRONIZE, False, self.engine.pid)
        )
        self.setuistatus(False)
        self.init()

    def end(self):
        windows.SendMessage(
            windows.FindWindow("WNDCLS_Magpie_Core_CLI_Message", None),
            windows.RegisterWindowMessage("Magpie_Core_CLI_Message_Exit"),
        )
        # gobject.base.translation_ui.magpiecallback.disconnect()

    def changestatus(self, hwnd, full, windowmode):
        if full:
            profiles_index = MagpieConfig.findHWNDIndex(gobject.base.hwnd)
            profile = magpie_config["profiles"][profiles_index]
            scalingMode = profile["scalingMode"]
            if scalingMode >= len(magpie_config["scalingModes"]):
                scalingMode = 0

            self.saveconfig()
            windows.SendMessage(
                windows.FindWindow("WNDCLS_Magpie_Core_CLI_Message", None),
                windows.RegisterWindowMessage(
                    [
                        "Magpie_Core_CLI_Message_Start",
                        "Magpie_Core_CLI_Message_Start_WindowedMode",
                    ][windowmode]
                ),
                profiles_index,
                hwnd,
            )
        else:
            windows.SendMessage(
                windows.FindWindow("WNDCLS_Magpie_Core_CLI_Message", None),
                windows.RegisterWindowMessage("Magpie_Core_CLI_Message_Stop"),
            )
        return False
