import windows
import threading
from qtsymbols import *
import gobject
import os, subprocess, functools
import time, winrtutils, winsharedutils, hashlib
from myutils.config import savehook_new_data
from myutils.wrapper import threader


@threader
def grabwindow(app="PNG", callback_origin=None):
    if callback_origin:
        fname = gobject.gettempdir(time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()))
        uid = None
    else:
        dirname = "0"
        try:
            uid = gobject.baseobject.textsource.gameuid
        except:
            uid = None
        try:
            if gobject.baseobject.textsource.md5 != "0":
                dirname = gobject.baseobject.textsource.basename
        except:
            pass
        fname = gobject.getcachedir(
            f"screenshot/{dirname}/"
            + time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()),
            abspath=False,
        )

    def callback_1(callback, uid, fn):
        if not os.path.exists(fn):
            return
        if callback:
            callback(os.path.abspath(fn))
        if uid:
            savehook_new_data[uid]["imagepath_all"].append(fn)

    callback = functools.partial(callback_1, callback_origin, uid)
    hwnd = windows.FindWindow(
        "Window_Magpie_967EB565-6F73-4E94-AE53-00CC42592A22", None
    )
    if hwnd:

        @threader
        def _():
            winrtutils._winrt_capture_window(fname + "_winrt_magpie." + app, hwnd)
            callback(fname + "_winrt_magpie." + app)

        _()
    hwnd = windows.FindWindow("LosslessScaling", None)
    if hwnd:

        @threader
        def _():
            winrtutils._winrt_capture_window(fname + "_winrt_lossless." + app, hwnd)
            callback(fname + "_winrt_lossless." + app)

        _()
    try:
        hwnd = gobject.baseobject.textsource.hwnd
        if not hwnd:
            raise
    except:
        hwnd = windows.GetForegroundWindow()

    _ = windows.GetClientRect(hwnd)
    p = screenshot(0, 0, _[2], _[3], hwnd).toImage()
    if not p.allGray():
        p.save(fname + "_gdi." + app)
        callback(fname + "_gdi." + app)

    if not callback_origin:

        gobject.baseobject.translation_ui.displaystatus.emit(
            "saved to " + fname, "red", True, True
        )

    @threader
    def _():
        winrtutils._winrt_capture_window(fname + "_winrt." + app, hwnd)
        callback(fname + "_winrt." + app)

    if p.allGray() or (not callback_origin):
        _()


def getpidexe(pid):
    hproc = windows.AutoHandle(
        windows.OpenProcess(windows.PROCESS_ALL_ACCESS, False, pid)
    )
    if not hproc:

        hproc = windows.OpenProcess(
            windows.PROCESS_QUERY_LIMITED_INFORMATION, False, pid
        )
    if not hproc:
        name_ = None
    else:
        name_ = windows.GetProcessFileName(hproc)
    return name_


def test_injectable_1(pid):
    return bool(
        windows.AutoHandle(
            windows.OpenProcess(windows.PROCESS_INJECT_ACCESS, False, pid)
        )
    )


def test_injectable(pids):
    for pid in pids:
        if not test_injectable_1(pid):
            return False
    return True


def ListProcess(exe=None):
    ret = {}
    for pid, exebase in winsharedutils.Getprcesses():
        if os.getpid() == pid:
            continue
        try:
            if exe is not None:
                if exebase.lower() != os.path.basename(exe).lower():
                    continue
            name_ = getpidexe(pid)
            if name_ is None:
                continue
            name = name_.lower()
            if exe is None:
                if (
                    ":\\windows\\" in name
                    or "\\microsoft\\" in name
                    or "\\windowsapps\\" in name
                ):
                    continue
            if name_ not in ret:
                ret[name_] = []
            ret[name_].append(pid)
        except:
            pass
    if exe is None:
        return ret
    return ret.get(exe, [])


def getExeIcon(name, icon=True, cache=False):
    if name.lower()[-4:] == ".lnk":
        exepath, args, iconpath, dirp = winsharedutils.GetLnkTargetPath(name)
        if os.path.exists(iconpath):
            name = iconpath
        elif os.path.exists(exepath):
            name = exepath
    data = winsharedutils.extracticon2data(name)
    if cache:
        fn = gobject.getcachedir(
            "icon/{}.bmp".format(hashlib.md5(name.encode("utf8")).hexdigest())
        )
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
    for _ in (0,):
        if not test_injectable(injectpids):
            break

        ret = subprocess.run(
            '"{}" dllinject {} "{}"'.format(injecter, pid, dll)
        ).returncode
        if ret:
            return
        pids = winsharedutils.collect_running_pids(injectpids)
        pid = " ".join([str(_) for _ in pids])

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
            keystate = windows.GetKeyState(windows.VK_LBUTTON)
            # 必须使用GetKeyState, GetAsyncKeyState或SetWindowHookEx都无法检测到高权限应用上的点击事件。
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


def screenshot(x1, y1, x2, y2, hwnd=None):
    if hwnd:
        _r = QApplication.instance().devicePixelRatio()
        _dpi = windows.GetDpiForWindow(hwnd)
        x1, y1, x2, y2 = (int(_ * _dpi / 96 / _r) for _ in (x1, y1, x2, y2))
    bs = winsharedutils.gdi_screenshot(x1, y1, x2, y2, hwnd)
    pixmap = QPixmap()
    if bs:
        pixmap.loadFromData(bs)
    return pixmap
