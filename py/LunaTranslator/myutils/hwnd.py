import windows
import threading
from qtsymbols import *
import gobject
import os, subprocess, functools
import time, winrtutils, winsharedutils, hashlib
from myutils.config import savehook_new_data, globalconfig
from myutils.wrapper import threader
from myutils.utils import qimage2binary


def clipboard_set_image(p: QImage):
    if not p:
        return
    if isinstance(p, str):
        qimg = QImage()
        qimg.load(p)
        p = qimg
    if p.isNull():
        return
    winsharedutils.clipboard_set_image(qimage2binary(p))


@threader
def grabwindow(app="PNG", callback_origin=None, tocliponly=False):
    tmsp = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
    if tocliponly:
        fname = ""
        uid = None
    elif callback_origin or tocliponly:
        if callback_origin:
            fname = gobject.gettempdir(tmsp)
        else:
            fname = ""
        uid = None
    else:

        hwndx = gobject.baseobject.hwnd
        if not hwndx:
            hwndx = windows.GetForegroundWindow()
        hwndx = windows.GetAncestor(hwndx)
        gamepath = getpidexe(windows.GetWindowThreadProcessId(hwndx))
        exename = os.path.splitext(os.path.basename(gamepath))[0]
        uid = gobject.baseobject.gameuid
        screenshot_savepath: str = globalconfig.get("screenshot_savepath", "")

        try:
            if not screenshot_savepath:
                raise
            dirname = screenshot_savepath.format(exename=exename)
            os.makedirs(dirname, exist_ok=True)
            fname = os.path.join(dirname, tmsp)
        except:
            fname = gobject.getcachedir(
                "screenshot/{}/{}".format(exename, tmsp), abspath=False
            )

    def callback_1(callback_origin, uid, tocliponly, p: QPixmap, fn):
        if p.isNull():
            return
        if tocliponly:
            clipboard_set_image(p)
            return
        p.save(fn)
        if callback_origin:
            callback_origin(os.path.abspath(fn))
        if uid:
            savehook_new_data[uid]["imagepath_all"].append(fn)

    callback = functools.partial(callback_1, callback_origin, uid, tocliponly)

    hwnd = gobject.baseobject.hwnd
    if not hwnd:
        return
    hwnd = windows.GetAncestor(hwnd)
    _ = windows.GetClientRect(hwnd)
    p = gdi_screenshot(0, 0, _[2], _[3], hwnd)
    callback(p, fname + "_gdi." + app)
    isshit = (not callback_origin) and (not tocliponly)
    if p.isNull() or isshit:

        @threader
        def _():
            p = winrt_capture_window(hwnd)
            callback(p, fname + "_winrt." + app)

        _()

    if isshit:
        gobject.baseobject.translation_ui.displaystatus.emit(
            "saved to " + fname, False, True
        )

        hwnd = windows.FindWindow(
            "Window_Magpie_967EB565-6F73-4E94-AE53-00CC42592A22", None
        )
        if hwnd:

            @threader
            def _():
                p = winrt_capture_window(hwnd)
                callback(p, fname + "_winrt_magpie." + app)

            _()
    elif tocliponly:
        gobject.baseobject.translation_ui.displaystatus.emit(
            "saved to clipboard", False, True
        )


def getpidexe(pid):
    hproc = windows.AutoHandle(
        windows.OpenProcess(windows.PROCESS_ALL_ACCESS, False, pid)
    )
    if not hproc:

        hproc = windows.AutoHandle(
            windows.OpenProcess(windows.PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        )
    if not hproc:
        name_ = None
    else:
        name_ = windows.GetProcessFileName(hproc)
    return name_


def getcurrexe():
    return os.environ.get("LUNA_EXE_NAME", "")


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


def getExeIcon(name: str, icon=True, cache=False):
    if name.lower().endswith(".lnk"):
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
                pixmap = QPixmap()
                pixmap.load(fn)
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


def injectdll(injectpids, bit, dll):

    injecter = os.path.abspath("./files/plugins/shareddllproxy{}.exe".format(bit))
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


def safepixmap(bs):
    if not bs:
        return QPixmap()
    pixmap = QPixmap()
    pixmap.loadFromData(bs)
    if pixmap.isNull():
        return QPixmap()
    return pixmap


def hwndratex(hwnd):
    _dpi = windows.GetDpiForWindow(hwnd)
    mdpi = winsharedutils.GetMonitorDpiScaling(hwnd)
    return mdpi / _dpi


def gdi_screenshot(x1, y1, x2, y2, hwnd=None):
    if hwnd:
        rate = hwndratex(hwnd)
        x1, y1, x2, y2 = (int(_ / rate) for _ in (x1, y1, x2, y2))
    bs = winsharedutils.gdi_screenshot(x1, y1, x2, y2, hwnd)
    return safepixmap(bs)


def winrt_capture_window(hwnd):
    bs = winrtutils.winrt_capture_window(hwnd)
    return safepixmap(bs)
