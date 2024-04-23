from scalemethod.base import scalebase
import os
import windows
from myutils.config import globalconfig
from myutils.hwnd import ListProcess, injectdll
from myutils.subproc import subproc_w
import time
from myutils.wrapper import threader
import re


class Method(scalebase):

    @threader
    def _wait_lossless_stop_external(self):
        while windows.FindWindow("LosslessScaling", None) == 0:
            time.sleep(0.5)
        while windows.FindWindow("LosslessScaling", None):
            time.sleep(0.5)
        self.setuistatus(False)

    def init(self):
        self.injectedpids = set()

    def runlossless(self):
        exes = [_[1] for _ in ListProcess()]
        path = globalconfig["lossless"]["path"]
        pexe = os.path.join(path, "LosslessScaling.exe")
        if pexe.replace("/", "\\") not in exes:
            subproc_w(pexe, cwd=path, name="LosslessScaling")
            time.sleep(1)

        if globalconfig["hooklossless"]:
            for pid, exe in ListProcess():
                if exe == pexe.replace("/", "\\"):
                    if pid in self.injectedpids:
                        continue
                    dll = os.path.abspath("./files/plugins/hookmagpie.dll")
                    injecter = os.path.abspath(
                        "./files/plugins/shareddllproxy{}.exe".format("64")
                    )
                    injectdll(pid, injecter, dll)
                    self.injectedpids.add(pid)
                    break

    def changestatus(self, hwnd, full):

        if full:
            self.runlossless()
            # self._wait_lossless_stop_external()

            windows.SetForegroundWindow(hwnd)
            time.sleep(0.1)
        configpath = os.path.join(
            os.environ["LOCALAPPDATA"], "Lossless Scaling/Settings.xml"
        )
        if os.path.exists(configpath) == False:
            return
        with open(configpath, "r", encoding="utf8") as ff:
            config = ff.read()

        Hotkey = re.findall("<Hotkey>(.*?)</Hotkey>", config)[0]
        hotkHotkeyModifierKeysey = re.findall(
            "<HotkeyModifierKeys>(.*?)</HotkeyModifierKeys>", config
        )[0]

        mods = hotkHotkeyModifierKeysey.split(" ")

        vkcode = windows.MapVirtualKey(Hotkey)
        mp1 = {"Shift": 16, "Windows": 91, "Control": 17, "Alt": 18}
        for k in mods:
            windows.keybd_event(mp1[k], 0, 0, 0)
        windows.keybd_event(vkcode, 0, 0, 0)
        windows.keybd_event(vkcode, 0, windows.KEYEVENTF_KEYUP, 0)
        for k in mods:
            windows.keybd_event(mp1[k], 0, windows.KEYEVENTF_KEYUP, 0)
