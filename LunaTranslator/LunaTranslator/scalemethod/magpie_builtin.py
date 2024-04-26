from scalemethod.base import scalebase
import os, json
import windows
from myutils.config import globalconfig, magpie_config
from myutils.subproc import subproc_w
from myutils.wrapper import threader
from winsharedutils import startmaglistener, endmaglistener


class Method(scalebase):
    def saveconfig(self):
        with open(self.jspath, "w", encoding="utf-8") as ff:
            ff.write(
                json.dumps(magpie_config, ensure_ascii=False, sort_keys=False, indent=4)
            )

    @threader
    def statuslistener(self):
        listener = windows.AutoHandle(startmaglistener())
        while not self.hasend:
            status = windows.c_int.from_buffer_copy(windows.ReadFile(listener, 4)).value
            self.setuistatus(status)

        endmaglistener(listener)

    def init(self):
        self.statuslistener()
        self.jspath = os.path.abspath("./cache/magpie.config.json")
        self.engine = subproc_w(
            './files/plugins/Magpie/Magpie.Core.exe "{}"'.format(self.jspath),
            cwd="./files/plugins/Magpie/",
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
