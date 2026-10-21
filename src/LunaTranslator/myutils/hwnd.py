import windows
from qtsymbols import *
import gobject
import os, functools
import NativeUtils, hashlib
from urllib.parse import quote
from myutils.config import savehook_new_data, globalconfig, relpath, _TR
from myutils.wrapper import threader
from myutils.utils import qimage2binary, get_time_stamp
from traceback import print_exc


def clipboard_set_image(p: QImage):
    if not p:
        return
    if isinstance(p, str):
        qimg = QImage()
        qimg.load(p)
        p = qimg
    if p.isNull():
        return
    NativeUtils.ClipBoard.image = qimage2binary(p)


def __getuidandfname(app):
    tmsp = get_time_stamp(forfilename=True)
    tmsp += "." + app
    hwndx = gobject.base.hwnd
    if not hwndx:
        hwndx = windows.GetForegroundWindow()
    hwndx = windows.GetAncestor(hwndx)
    gamepath = NativeUtils.GetProcessFileName(windows.GetWindowThreadProcessId(hwndx))
    exename = os.path.splitext(os.path.basename(gamepath))[0]
    uid = gobject.base.gameuid
    screenshot_savepath: str = globalconfig.get("screenshot_savepath", "")

    class __Exception(Exception):
        pass

    try:
        if not screenshot_savepath:
            raise __Exception()
        try:
            if "{exename}" in screenshot_savepath:
                dirname = screenshot_savepath.format(exename=exename)
            else:
                raise __Exception()
        except:
            try:
                if "{}" in screenshot_savepath:
                    dirname = screenshot_savepath.format(exename)
                else:
                    raise __Exception()
            except:
                dirname = screenshot_savepath
                tmsp = exename + "-" + tmsp
        os.makedirs(dirname, exist_ok=True)
        fname = os.path.join(dirname, tmsp)
    except Exception as e:
        if not isinstance(e, __Exception):
            print_exc()
        fname = gobject.getcachedir(r"screenshot\{}\{}".format(exename, tmsp))
    return uid, relpath(fname)


def callback_1(callback_origin, tocliponly: bool, app, p: QPixmap):
    if p.isNull():
        return False
    if tocliponly:
        clipboard_set_image(p)
        gobject.base.displayinfomessage(_TR("已保存到剪贴板"), "<msg_info_refresh>")
        return True
    if callback_origin:
        callback_origin(p)
        return True
    uid, fname = __getuidandfname(app)
    p.save(fname)
    gobject.base.translation_ui.showMarkDownSig.emit(
        "{}\n[{}](OPEN-{}) [{}](OPEN-{}) [{}](SCREENSHOTSETTING)".format(
            _TR("已保存为： {}").format(fname),
            _TR("打开图片"),
            quote(fname),
            _TR("打开路径"),
            quote(os.path.dirname(fname)),
            _TR("保存路径"),
        )
    )
    if uid:
        if "imagepath_all" not in savehook_new_data[uid]:
            savehook_new_data[uid]["imagepath_all"] = []
        savehook_new_data[uid]["imagepath_all"].append(fname)
    return True


@threader
def grabwindow(app="PNG", callback=None, tocliponly=False):
    callback_2 = functools.partial(callback_1, callback, tocliponly, app)

    hwnd = windows.FindWindow(
        "Window_Magpie_967EB565-6F73-4E94-AE53-00CC42592A22", None
    )
    if hwnd:
        p = safepixmap(NativeUtils.WinRT.capture_window(hwnd, blackborderremove=True))
        if callback_2(p):
            return

    hwnd = gobject.base.hwnd
    if not hwnd:
        return
    hwnd = windows.GetAncestor(hwnd)
    p = safepixmap(NativeUtils.GdiGrabWindow(hwnd))
    if callback_2(p):
        return
    p = safepixmap(NativeUtils.WinRT.capture_window(hwnd))
    if callback_2(p):
        return


def getExeIcon(name: str, icon=True, cache=False, large=False):
    if name.lower().endswith(".lnk"):
        exepath, args, iconpath, dirp = NativeUtils.GetLnkTargetPath(name)
        if os.path.exists(iconpath):
            name = iconpath
        elif os.path.exists(exepath):
            name = exepath
    data = NativeUtils.ExtractExeIconData(name, large=large)
    if cache:
        fn = gobject.getcachedir(
            "icon/{}.png".format(hashlib.md5(name.encode("utf8")).hexdigest())
        )
    if data:
        pixmap = QPixmap()
        pixmap.loadFromData(data)
        if cache:
            pixmap.save(fn)
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
            pixmap = QPixmap()
    if icon:
        return QIcon(pixmap)
    else:
        return pixmap


def safepixmap(bs):
    if not bs:
        return QPixmap()
    pixmap = QPixmap()
    pixmap.loadFromData(bs)
    if pixmap.isNull():
        return QPixmap()
    return pixmap

