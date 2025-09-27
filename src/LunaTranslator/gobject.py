import platform, os, sys
from ctypes import windll, Structure, POINTER, pointer
from ctypes.wintypes import DWORD, WCHAR

thisuserconfig = "userconfig"
runtime_bit_64 = platform.architecture()[0] == "64bit"


def GetDllpath(_, base=None):

    if base is None:
        base = os.path.abspath("files/DLL" + ("32", "64")[runtime_bit_64])
    if isinstance(_, str):
        return os.path.join(base, _)
    elif isinstance(_, (list, tuple)):
        return os.path.join(base, _[runtime_bit_64])


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


def getconfig(name):
    return __getdir(name, thisuserconfig)


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
    from LunaTranslator import BASEOBJECT
base: "BASEOBJECT" = None
isRunningMutex = None
serverindex = 0
serverindex2 = 0
istest = False


class Consts:
    buttoncolor = "#FF69B4"
    buttoncolor_disable = "#afafaf"
    btnscale = 1.2
    toolwdivh = 4 / 3
    toolscale = 1.5
    IconSizeHW = 1.1


runtime_for_xp = tuple(sys.version_info)[:2] == (3, 4)
runtime_for_win10 = tuple(sys.version_info)[:2] >= (3, 9)

if runtime_for_win10:
    runtimedir = "runtime31264"
elif runtime_for_xp:
    runtimedir = "runtime3432"
elif runtime_bit_64:
    runtimedir = "runtime3764"
else:
    runtimedir = "runtime3732"
runtimedir = "files/" + runtimedir
sys_le_xp = int(platform.version().split(".")[0]) <= 5


class RTL_OSVERSIONINFOW(Structure):
    _fields_ = [
        ("_1", DWORD),
        ("_2", DWORD),
        ("_3", DWORD),
        ("dwBuildNumber", DWORD),
        ("_4", DWORD),
        ("_5", WCHAR * 128),
    ]


RtlGetVersion = windll.ntdll.RtlGetVersion
RtlGetVersion.argtypes = (POINTER(RTL_OSVERSIONINFOW),)
__version = RTL_OSVERSIONINFOW()
RtlGetVersion(pointer(__version))
sys_ge_win_11 = __version.dwBuildNumber >= 22000  # 21h2
sys_ge_win_10 = int(platform.version().split(".")[0]) >= 10
sys_ge_win8 = tuple(int(_) for _ in platform.version().split(".")[:2]) >= (6, 2)
sys_le_win7 = tuple(int(_) for _ in platform.version().split(".")[:2]) <= (6, 1)
sys_le_win81 = int(platform.version().split(".")[0]) <= 6
