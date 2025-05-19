import platform, os, sys


def GetDllpath(_, base=None):
    isbit64 = platform.architecture()[0] == "64bit"

    if base is None:
        base = os.path.abspath("files/DLL" + ("32", "64")[isbit64])
    if isinstance(_, str):
        return os.path.join(base, _)
    elif isinstance(_, (list, tuple)):
        return os.path.join(base, _[isbit64])


def __getdir(name="", basedir="cache"):

    fd = os.path.dirname(name)
    fn = os.path.basename(name)
    fn1 = os.path.abspath(basedir)
    fn1 = os.path.join(fn1, fd)
    os.makedirs(fn1, exist_ok=True)
    fn1 = os.path.join(fn1, fn)
    return fn1


def getcachedir(name=""):
    return __getdir(name)


def getuserconfigdir(name):
    return __getdir(name, "userconfig")


def gettranslationrecorddir(name):
    return __getdir(name, "translation_record")


def gettempdir_1():
    tgt = __getdir("temp")
    return tgt


def gettempdir(filename=""):
    tgt = __getdir(os.path.join("temp/{}".format(os.getpid()), filename))
    return tgt


try:
    TYPE_CHECKING = False
    from typing import TYPE_CHECKING
except:
    pass
if TYPE_CHECKING:
    from LunaTranslator import MAINUI
baseobject: "MAINUI" = None
global_dialog_savedgame_new = None
global_dialog_setting_game = None
serverindex = 0
edittrans = None


class Consts:
    buttoncolor = "#FF69B4"
    buttoncolor_disable = "#afafaf"
    btnscale = 1.2
    toolwdivh = 4 / 3
    toolscale = 1.5


runtime_bit_64 = platform.architecture()[0] == "64bit"
runtime_for_xp = tuple(sys.version_info)[:2] == (3, 4)
runtime_for_win10 = tuple(sys.version_info)[:2] >= (3, 9)

sys_le_xp = int(platform.version().split(".")[0]) <= 5
sys_ge_win_11 = sys.getwindowsversion().build >= 22000  # 21h2
sys_ge_win8 = tuple(int(_) for _ in platform.version().split(".")[:2]) >= (6, 2)
sys_le_win7 = tuple(int(_) for _ in platform.version().split(".")[:2]) <= (6, 1)
sys_le_win81 = int(platform.version().split(".")[0]) <= 6
