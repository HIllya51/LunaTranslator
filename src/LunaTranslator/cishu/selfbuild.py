from myutils.utils import checkmd5reloadmodule
import gobject
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

    def search(self, word) -> str:
        self.mayreinit()
        if not self.internal:
            return None
        return self.internal.search(word)

    def getUrl(self, word) -> str:
        self.mayreinit()
        if not self.internal:
            return None
        return self.internal.getUrl(word)
