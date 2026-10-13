from myutils.utils import checkmd5reloadmodule
import gobject, inspect
from cishu.cishubase import cishubase


class Cishu(cishubase):
    def __init__(self, *a):
        self.internal = None
        self.__lastm = None
        super().__init__(*a)

    def mayreinit(self):
        module = checkmd5reloadmodule(
            gobject.getconfig("selfbuild_cishu.py"), "selfbuild_cishu"
        )
        if module and (module.MyCishu != self.__lastm):
            self.__lastm = module.MyCishu
            self.internal: cishubase = module.MyCishu("selfbuild")
            self.internal.init()

    def search(self, word, sentence=None) -> str:
        self.mayreinit()
        if not self.internal:
            return None
        sig = inspect.signature(self.internal.search)
        np = len(sig.parameters)
        if np == 1:
            return self.internal.search(word)
        elif np == 2:
            return self.internal.search(word, sentence=sentence)
        else:
            raise Exception("unknown args")

    def getUrl(self, word) -> str:
        self.mayreinit()
        if not self.internal:
            return None
        return self.internal.getUrl(word)
