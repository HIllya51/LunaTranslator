import winreg
from traceback import print_exc


class HKey:
    def __init__(self, hkey: int):
        self.hkey = hkey

    def __del__(self):
        try:
            winreg.CloseKey(self.hkey)
        except Exception:
            pass

    def query(self, key: str):
        try:
            return winreg.QueryValueEx(self.hkey, key)[0]
        except FileNotFoundError:
            return None

    def open(self, subpath: str, read: bool = False, query: bool = False):
        access = winreg.KEY_QUERY_VALUE if query else (winreg.KEY_READ if read else 0)
        try:
            h = winreg.OpenKey(self.hkey, subpath, 0, access)
            return HKey(h)
        except FileNotFoundError:
            return None

    def enum(self):
        idx = 0
        while True:
            try:
                yield winreg.EnumKey(self.hkey, idx)
                idx += 1
            except OSError:
                break


CURRENT_USER = HKey(winreg.HKEY_CURRENT_USER)
LOCAL_MACHINE = HKey(winreg.HKEY_LOCAL_MACHINE)
