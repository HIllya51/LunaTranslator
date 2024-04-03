import os, json
import windows, winsharedutils
from myutils.config import globalconfig, magpie10_config
from myutils.hwnd import letfullscreen, recoverwindow, ListProcess, injectdll
from traceback import print_exc
from myutils.subproc import subproc_w
import time
from myutils.wrapper import threader
import re


class fullscreen:
    def __init__(self, _externalfsend) -> None:
        self.savewindowstatus = None
        self._externalfsend = _externalfsend
        self.status = False
        self.lasthwnd = None

    def end(self):
        if self.status and self.lasthwnd:
            self.__call__(self.lasthwnd, not self.status)

    @property
    def fsmethod(self):
        return globalconfig["fullscreenmethod_3"]

    def internal_stopped(self):
        self._externalfsend()
        self.status = False

    @threader
    def _wait_lossless_stop_external(self):
        while windows.FindWindow("LosslessScaling", None) == 0:
            time.sleep(0.5)
        while windows.FindWindow("LosslessScaling", None):
            time.sleep(0.5)
        self.internal_stopped()

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
                    dll = os.path.abspath("./files/plugins/hookmagpie.dll")
                    injecter = os.path.abspath(
                        "./files/plugins/shareddllproxy{}.exe".format("64")
                    )
                    injectdll(pid, injecter, dll)
                    break

    def _external_lossless(self, hwnd, full):

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

    def runmagpie10(self):
        if windows.FindWindow("Magpie_Hotkey", None) == 0:
            subproc_w(
                os.path.join(globalconfig["magpie10path"], "Magpie.exe"),
                cwd=globalconfig["magpie10path"],
                name="magpie10",
            )
            while windows.FindWindow("Magpie_Hotkey", None) == 0:
                time.sleep(0.5)
        if globalconfig["hookmagpie"]:
            pid = windows.GetWindowThreadProcessId(
                windows.FindWindow("Magpie_Hotkey", None)
            )
            dll = os.path.abspath("./files/plugins/hookmagpie.dll")
            injecter = os.path.abspath(
                "./files/plugins/shareddllproxy{}.exe".format("64")
            )
            injectdll([pid], injecter, dll)

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
        self.internal_stopped()

    def _external_magpie10(self, hwnd, full):

        configpath = os.path.join(globalconfig["magpie10path"], "config/config.json")

        if os.path.exists(configpath) == False:
            version = winsharedutils.queryversion(
                os.path.join(globalconfig["magpie10path"], "Magpie.exe")
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
            return

        with open(configpath, "r", encoding="utf8") as ff:
            config = json.load(ff)
        autoRestore = config["autoRestore"]
        shortcuts = config["shortcuts"]["scale"]
        mp1 = {"SHIFT": 16, "WIN": 91, "CTRL": 17, "ALT": 18}
        mp = {0x100: "WIN", 0x200: "CTRL", 0x400: "ALT", 0x800: "SHIFT"}

        if full:
            self.runmagpie10()
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

    # def _4(self,hwnd,full):
    #     if full:
    #         self.engine= subproc_w(r'./files/plugins/shareddllproxy64.exe lossless "{}" "{}" {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {}'.format(globalconfig['lossless']['path'],hwnd,

    #         globalconfig['lossless']['scalingMode'],
    #         globalconfig['lossless']['scalingFitMode'],
    #         globalconfig['lossless']['scalingType'],
    #         globalconfig['lossless']['scalingSubtype'],
    #         globalconfig['lossless']['scaleFactor'],
    #         globalconfig['lossless']['resizeBeforeScale'],
    #         globalconfig['lossless']['windowedMode'],
    #         globalconfig['lossless']['sharpness'],
    #         globalconfig['lossless']['VRS'],
    #         globalconfig['lossless']['clipCursor'],
    #         globalconfig['lossless']['cursorSensitivity'],
    #         globalconfig['lossless']['hideCursor'],
    #         globalconfig['lossless']['scaleCursor'],
    #         globalconfig['lossless']['doubleBuffering'],
    #         globalconfig['lossless']['vrrSupport'],
    #         globalconfig['lossless']['hdrSupport'],
    #         globalconfig['lossless']['allowTearing'],
    #         globalconfig['lossless']['legacyCaptureApi'],
    #         globalconfig['lossless']['drawFps'],
    #         globalconfig['lossless']['gpuId'],
    #         globalconfig['lossless']['displayId'],
    #         globalconfig['lossless']['captureOffsetLeft'],
    #         globalconfig['lossless']['captureOffsetTop'],
    #         globalconfig['lossless']['captureOffsetRight'],
    #         globalconfig['lossless']['captureOffsetBottom'],
    #         globalconfig['lossless']['multiDisplayMode'],
    #         os.getpid(),
    #         globalconfig['lossless']['frameGeneration'],
    #         globalconfig['lossless']['syncInterval']),cwd=globalconfig['lossless']['path'])
    #         self._waitenginestop()
    #     else:
    #         endevent =windows.AutoHandle(windows.CreateEvent(False, False,'LOSSLESS_WAITFOR_STOP_SIGNAL'+str(self.engine.pid)))
    #         windows.SetEvent(endevent)

    @threader
    def _waitenginestop_magpie(self):
        self.engine.wait()
        self.internal_stopped()

    def _magpie_builtin(self, hwnd, full):
        if full:
            profiles_index = globalconfig["profiles_index"]
            if profiles_index > len(magpie10_config["profiles"]):
                profiles_index = 0

            jspath = os.path.abspath("./userconfig/magpie10_config.json")
            with open(jspath, "w", encoding="utf-8") as ff:
                ff.write(
                    json.dumps(
                        magpie10_config, ensure_ascii=False, sort_keys=False, indent=4
                    )
                )
            self.engine = subproc_w(
                './files/plugins/Magpie10/Magpie.Core.exe {} {} "{}"'.format(
                    profiles_index, hwnd, jspath
                ),
                cwd="./files/plugins/Magpie10/",
            )
            self._waitenginestop_magpie()
        else:
            windows.SendMessage(
                windows.FindWindow("Magpie_Core_CLI_Message", None),
                windows.RegisterWindowMessage("Magpie_Core_CLI_Message_Stop"),
            )

    # magpie9
    # def _0(self,hwnd,full):
    #     if full:
    #         SetForegroundWindow(hwnd )
    #         callmagpie(('./files/plugins/Magpie_v0.9.1'),hwnd,globalconfig['magpiescalemethod'],globalconfig['magpieflags'],globalconfig['magpiecapturemethod'])
    #     else:
    #         hwnd=FindWindow('Window_Magpie_967EB565-6F73-4E94-AE53-00CC42592A22',None)
    #         if hwnd==0:
    #             return
    #         WM_DESTORYHOST=RegisterWindowMessage( "MAGPIE_WM_DESTORYHOST")
    #         SendMessage(hwnd, WM_DESTORYHOST)
    def _alt_enter(self, hwnd, full):
        windows.SetForegroundWindow(hwnd)
        windows.keybd_event(18, 0, 0, 0)  # alt
        windows.keybd_event(13, 0, 0, 0)  # enter

        windows.keybd_event(13, 0, windows.KEYEVENTF_KEYUP, 0)
        windows.keybd_event(18, 0, windows.KEYEVENTF_KEYUP, 0)

    def _SW_SHOWMAXIMIZED(self, hwnd, full):
        if full:
            self.savewindowstatus = letfullscreen(hwnd)
        else:
            recoverwindow(hwnd, self.savewindowstatus)

    @threader
    def __call__(self, hwnd=0, full=False):
        try:
            [
                self._magpie_builtin,
                self._alt_enter,
                self._SW_SHOWMAXIMIZED,
                self._external_lossless,
                self._external_magpie10,
            ][self.fsmethod](hwnd, full)
            self.status = full
            self.lasthwnd = hwnd
        except:
            print_exc()
