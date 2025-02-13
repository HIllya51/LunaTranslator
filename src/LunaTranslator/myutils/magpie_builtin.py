import json
import windows, gobject
from myutils.config import globalconfig, magpie_config
import winsharedutils
from myutils.wrapper import threader


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
        self.engine = winsharedutils.AutoKillProcess(
            './files/plugins/Magpie/Magpie.Core.exe "{}"'.format(self.jspath),
            "./files/plugins/Magpie/",
        )
        waitsignal = "Magpie_notify_prepared_ok_" + str(self.engine.pid)
        windows.WaitForSingleObject(
            windows.AutoHandle(windows.CreateEvent(False, False, waitsignal)),
            windows.INFINITE,
        )

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
