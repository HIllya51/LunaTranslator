import json
import windows, gobject
from myutils.config import globalconfig, magpie_config
import NativeUtils, functools
from myutils.wrapper import threader


class AdapterService:
    AdaptersServiceStartMonitor_Callback_ptr = None

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
        AdapterService.AdaptersServiceStartMonitor_Callback_ptr = (
            NativeUtils.AdaptersServiceStartMonitor_Callback(
                functools.partial(
                    AdapterService.AdaptersServiceStartMonitor_Callback, callback
                )
            )
        )
        NativeUtils.AdaptersServiceStartMonitor(
            AdapterService.AdaptersServiceStartMonitor_Callback_ptr
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
        # gobject.baseobject.translation_ui.magpiecallback.disconnect()

    def changestatus(self, hwnd, full, windowmode):
        if full:
            profiles_index = globalconfig["profiles_index"]
            if profiles_index > len(magpie_config["profiles"]):
                profiles_index = 0

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
