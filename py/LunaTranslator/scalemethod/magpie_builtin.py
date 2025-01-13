from scalemethod.base import scalebase
import json
import windows, gobject
from myutils.config import globalconfig, magpie_config
import winsharedutils


class Method(scalebase):
    def saveconfig(self):
        with open(self.jspath, "w", encoding="utf-8") as ff:
            ff.write(
                json.dumps(magpie_config, ensure_ascii=False, sort_keys=False, indent=4)
            )

    def messagecallback(self, msg, status):
        if msg == 1:
            self.setuistatus(int(bool(status)))

    def init(self):
        self.messagecallback__ = winsharedutils.globalmessagelistener_cb(
            self.messagecallback
        )
        winsharedutils.globalmessagelistener(self.messagecallback__)
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

    def changestatus(self, hwnd, full):
        if full:
            profiles_index = globalconfig["profiles_index"]
            if profiles_index > len(magpie_config["profiles"]):
                profiles_index = 0

            self.saveconfig()
            windows.SendMessage(
                windows.FindWindow("WNDCLS_Magpie_Core_CLI_Message", None),
                windows.RegisterWindowMessage("Magpie_Core_CLI_Message_Start"),
                profiles_index,
                hwnd,
            )
        else:
            windows.SendMessage(
                windows.FindWindow("WNDCLS_Magpie_Core_CLI_Message", None),
                windows.RegisterWindowMessage("Magpie_Core_CLI_Message_Stop"),
            )
        return False
