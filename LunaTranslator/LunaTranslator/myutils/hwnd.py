import windows
import threading
from PyQt5.QtGui import QPixmap, QColor, QIcon
from PyQt5.QtWidgets import QApplication
import gobject, ctypes
import os, subprocess
import time, winrtutils, winsharedutils, hashlib
from myutils.wrapper import threader


@threader
def grabwindow(callback=None):

    fnamebase = "./cache/screenshot/{}".format(0)
    try:
        if gobject.baseobject.textsource.md5 != "0":
            fnamebase = "./cache/screenshot/{}".format(
                gobject.baseobject.textsource.basename
            )
    except:
        pass
    if os.path.exists(fnamebase) == False:
        os.mkdir(fnamebase)
    fname = "{}/{}".format(
        fnamebase, time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
    )

    hwnd = windows.FindWindow(
        "Window_Magpie_967EB565-6F73-4E94-AE53-00CC42592A22", None
    )
    if hwnd:

        @threader
        def _():
            winrtutils._winrt_capture_window(fname + "_winrt_magpie.png", hwnd)
            if callback and os.path.exists(fname + "_winrt_magpie.png"):
                callback(os.path.abspath(fname + "_winrt_magpie.png"))

        _()
    hwnd = windows.FindWindow("LosslessScaling", None)
    if hwnd:

        @threader
        def _():
            winrtutils._winrt_capture_window(fname + "_winrt_lossless.png", hwnd)
            if callback and os.path.exists(fname + "_winrt_lossless.png"):
                callback(os.path.abspath(fname + "_winrt_lossless.png"))

        _()
    try:
        hwnd = gobject.baseobject.textsource.hwnd
    except:
        hwnd = windows.GetForegroundWindow()

    _ = windows.GetClientRect(hwnd)
    rate = dynamic_rate(hwnd, _)
    w, h = int(_[2] / rate), int(_[3] / rate)
    p = QApplication.primaryScreen().grabWindow(hwnd, 0, 0, w, h)
    p = p.toImage().copy(0, 0, w, h)
    if not p.allGray():
        p.save(fname + "_gdi.png")
        if callback and os.path.exists(fname + "_gdi.png"):
            callback(os.path.abspath(fname + "_gdi.png"))

    if not callback:

        gobject.baseobject.translation_ui.displaystatus.emit(
            "saved to " + fname, "red", True, True
        )

    @threader
    def _():
        winrtutils._winrt_capture_window(fname + "_winrt.png", hwnd)
        if callback and os.path.exists(fname + "_winrt.png"):
            callback(os.path.abspath(fname + "_winrt.png"))

    if p.allGray() or (not callback):
        _()


def dynamic_rate(hwnd, rect):
    if getscreenp() == (rect[2], rect[3]):
        rate = 1
    else:
        rate = hwndscalerate(hwnd)
    return rate


def getscreenp():  # 一些游戏全屏时会修改分辨率，但不会修改系统gdi
    hDC = windows.GetDC(0)
    h = windows.GetDeviceCaps(hDC, 8)
    w = windows.GetDeviceCaps(hDC, 10)
    windows.ReleaseDC(None, hDC)
    return h, w


def hwndscalerate(hwnd):
    dpi = windows.GetDpiForWindow(hwnd)
    rate = QApplication.instance().devicePixelRatio() * 96 / dpi
    return rate


def getprocesslist():

    pids = windows.EnumProcesses()
    return pids


def getpidexe(pid):
    hwnd1 = windows.AutoHandle(
        windows.OpenProcess(windows.PROCESS_ALL_ACCESS, False, (pid))
    )
    if hwnd1 == 0:

        hwnd1 = windows.OpenProcess(
            windows.PROCESS_QUERY_LIMITED_INFORMATION, False, (pid)
        )
    if hwnd1 == 0:
        name_ = None
    else:
        name_ = windows.GetProcessFileName(hwnd1)
    return name_


def testprivilege(pid):
    hwnd1 = windows.AutoHandle(
        windows.OpenProcess(windows.PROCESS_INJECT_ACCESS, False, (pid))
    )
    return hwnd1 != 0


def ListProcess(filt=True):
    ret = []
    pids = getprocesslist()
    for pid in pids:
        if os.getpid() == pid:
            continue
        try:
            name_ = getpidexe(pid)
            if name_ is None:
                continue
            name = name_.lower()
            if filt:
                if (
                    ":\\windows\\" in name
                    or "\\microsoft\\" in name
                    or "\\windowsapps\\" in name
                ):
                    continue
            ret.append([pid, name_])
        except:
            pass
    kv = {}
    for pid, exe in ret:
        if exe in kv:
            kv[exe]["pid"].append(pid)
        else:
            kv[exe] = {"pid": [pid]}
    # for exe in kv:
    #         if len(kv[exe]['pid'])>1:
    #                 mems=[getprocessmem(_) for _ in kv[exe]['pid']]
    #                 _i=argsort(mems)
    #                 kv[exe]['pid']=[kv[exe]['pid'][_i[-1]]]
    xxx = []
    for exe in kv:
        xxx.append([kv[exe]["pid"], exe])
    return xxx


def getExeIcon(name, icon=True, cache=False):
    if name.lower()[-4:] == ".lnk":
        exepath, args, iconpath, dirp = winsharedutils.GetLnkTargetPath(name)
        if os.path.exists(iconpath):
            name = iconpath
        elif os.path.exists(exepath):
            name = exepath
    data = winsharedutils.extracticon2data(name)
    if cache:
        os.makedirs("./cache/icon", exist_ok=True)
        fn = "./cache/icon/{}.bmp".format(hashlib.md5(name.encode("utf8")).hexdigest())
    if data:
        pixmap = QPixmap()
        pixmap.loadFromData(data)
        if cache:
            with open(fn, "wb") as ff:
                ff.write(data)
    else:
        succ = False
        if cache and os.path.exists(fn):
            try:
                with open(fn, "rb") as ff:
                    data = ff.read()
                pixmap = QPixmap()
                pixmap.loadFromData(data)
                succ = True
            except:
                pass
                # print_exc()
        if succ == False:
            pixmap = QPixmap(100, 100)
            pixmap.fill(QColor.fromRgba(0))
    if icon:
        return QIcon(pixmap)
    else:
        return pixmap


def injectdll(injectpids, injecter, dll):
    pid = " ".join([str(_) for _ in injectpids])
    if any(map(testprivilege, injectpids)) == False:
        windows.ShellExecute(
            0,
            "runas",
            injecter,
            'dllinject {} "{}"'.format(pid, dll),
            None,
            windows.SW_HIDE,
        )
    else:
        ret = subprocess.run(
            '"{}" dllinject {} "{}"'.format(injecter, pid, dll)
        ).returncode
        if ret == 0:
            windows.ShellExecute(
                0,
                "runas",
                injecter,
                'dllinject {} "{}"'.format(pid, dll),
                None,
                windows.SW_HIDE,
            )


def mouseselectwindow(callback):

    def _loop():
        while True:
            keystate = windows.GetKeyState(
                windows.VK_LBUTTON
            )  # 必须使用GetKeyState, GetAsyncKeyState或SetWindowHookEx都无法检测到高权限应用上的点击事件。
            if keystate < 0:
                break
            time.sleep(0.01)
        try:
            pos = windows.GetCursorPos()
            hwnd = windows.GetAncestor(windows.WindowFromPoint(pos))
            pid = windows.GetWindowThreadProcessId(hwnd)
            callback(pid, hwnd)
        except:
            pass

    threading.Thread(target=_loop).start()
