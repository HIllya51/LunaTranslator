from winreg import *
from . import stylelight_rc


def stylesheet():
    try:
        registry = ConnectRegistry(None, HKEY_CURRENT_USER)
        key = OpenKey(
            registry, r"SOFTWARE\\Microsoft\Windows\\CurrentVersion\\Explorer\\Accent"
        )
        key_value = QueryValueEx(key, "AccentColorMenu")
        accent_int = key_value[0]
    except:
        accent_int = 0xFFD47800
    accent = accent_int - 4278190080
    accent = str(hex(accent)).split("x")[1]
    accent = accent[4:6] + accent[2:4] + accent[0:2]
    accent = "rgb" + str(tuple(int(accent[i : i + 2], 16) for i in (0, 2, 4)))
    with open(__file__[:-2] + "qss", "r") as ff:
        return ff.read().replace("{accent}", accent)
