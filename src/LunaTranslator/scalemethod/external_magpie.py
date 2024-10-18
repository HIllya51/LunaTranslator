from scalemethod.base import scalebase
import os, json
import windows, winsharedutils
from myutils.config import globalconfig
from myutils.hwnd import injectdll
from myutils.subproc import subproc_w
import time
from myutils.wrapper import threader


class Method(scalebase):
    def init(self):
        self.injectedpids = set()

    def runmagpie(self):
        if windows.FindWindow("Magpie_Hotkey", None) == 0:
            subproc_w(
                os.path.join(globalconfig["magpiepath"], "Magpie.exe"),
                cwd=globalconfig["magpiepath"],
                name="magpie",
            )
            while windows.FindWindow("Magpie_Hotkey", None) == 0:
                time.sleep(0.5)
        if True:
            pid = windows.GetWindowThreadProcessId(
                windows.FindWindow("Magpie_Hotkey", None)
            )
            if pid in self.injectedpids:
                return
            dll = os.path.abspath("./files/plugins/hookmagpie.dll")
            injectdll([pid], 64, dll)
            self.injectedpids.add(pid)

    @threader
    def _wait_magpie_stop_external(self):
        while (
            windows.FindWindow(
                "Window_Magpie_967EB565-6F73-4E94-AE53-00CC42592A22", None
            )
            == 0
        ):
            time.sleep(0.5)
        while windows.FindWindow(
            "Window_Magpie_967EB565-6F73-4E94-AE53-00CC42592A22", None
        ):
            time.sleep(0.5)
        self.setuistatus(False)
    
    def changestatus(self, hwnd, full):

        configpath = os.path.join(globalconfig["magpiepath"], "config/config.json")

        if os.path.exists(configpath) == False:
            version = winsharedutils.queryversion(
                os.path.join(globalconfig["magpiepath"], "Magpie.exe")
            )
            checks = [
                os.path.join(
                    os.environ["LOCALAPPDATA"], "Magpie/config/v2/config.json"
                ),
                os.path.join(os.environ["LOCALAPPDATA"], "Magpie/config/config.json"),
            ]
            if version:
                if version[:3] >= (0, 10, 100):  # v0.11.0-preview1
                    checks = [checks[0]]
                else:
                    checks = [checks[1]]
            for ck in checks:
                if os.path.exists(ck):
                    configpath = ck
                    break

        if os.path.exists(configpath) == False:
            return False

        with open(configpath, "r", encoding="utf8") as ff:
            config = json.load(ff)
        autoRestore = config["autoRestore"]
        shortcuts = config["shortcuts"]["scale"]
        mp1 = {"SHIFT": 16, "WIN": 91, "CTRL": 17, "ALT": 18}
        mp = {0x100: "WIN", 0x200: "CTRL", 0x400: "ALT", 0x800: "SHIFT"}

        if full:
            self.runmagpie()
            if autoRestore == False:
                self._wait_magpie_stop_external()

            windows.SetForegroundWindow(hwnd)
            time.sleep(0.1)

        for k in mp:
            if shortcuts & k != 0:
                windows.keybd_event(mp1[mp[k]], 0, 0, 0)

        k2 = shortcuts & 0xFF
        windows.keybd_event(k2, 0, 0, 0)
        windows.keybd_event(k2, 0, windows.KEYEVENTF_KEYUP, 0)
        for k in mp:
            if shortcuts & k != 0:
                windows.keybd_event(mp1[mp[k]], 0, windows.KEYEVENTF_KEYUP, 0)
        return True