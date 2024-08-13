baseobject = None
global_dialog_savedgame_new = None
global_dialog_setting_game = None
import io, sys, platform, os
from ctypes import windll, wintypes

isbit64 = platform.architecture()[0] == "64bit"
DLL3264path = os.path.abspath("files/plugins/DLL" + ("32", "64")[isbit64])


def GetDllpath(_, base=None):
    if base is None:
        base = DLL3264path
    if isinstance(_, str):
        return os.path.join(base, _)
    elif isinstance(_, (list, tuple)):
        return os.path.join(base, _[isbit64])


def getcachedir(name, basedir="cache", abspath=True):

    fd = os.path.dirname(name)
    fn = os.path.basename(name)
    if abspath:
        fn1 = os.path.abspath(basedir)
    else:
        fn1 = basedir
    fn1 = os.path.join(fn1, fd)
    os.makedirs(fn1, exist_ok=True)
    fn1 = os.path.join(fn1, fn)
    return fn1


def getuserconfigdir(name):
    return getcachedir(name, "userconfig")


def gettranslationrecorddir(name):
    return getcachedir(name, "translation_record")


def gettempdir_1():
    tgt = getcachedir("temp")
    return tgt


def gettempdir(filename):
    tgt = getcachedir(os.path.join(f"temp/{os.getpid()}", filename))
    return tgt


def dopathexists(file):
    if not file:
        return False
    if not file.strip():
        return False
    PathFileExists = windll.Shlwapi.PathFileExistsW
    PathFileExists.argtypes = (wintypes.LPCWSTR,)
    PathFileExists.restype = wintypes.BOOL
    return bool(PathFileExists(os.path.abspath(file)))


def overridepathexists():
    # win7上，如果假如没有D盘，然后os.path.exists("D:/...")，就会弹窗说不存在D盘
    os.path.exists = dopathexists


def testuseqwebengine():
    return os.path.exists("./LunaTranslator/runtime/PyQt5/Qt5/bin/Qt5WebEngineCore.dll")


serverindex = 0
