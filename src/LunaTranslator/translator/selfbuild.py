from translator.basetranslator import basetrans
from myutils.utils import checkmd5reloadmodule
import gobject


class TS(basetrans):
    def mayreinit(self):
        module = checkmd5reloadmodule(gobject.getconfig("selfbuild.py"), "selfbuild")
        if module and (module.TS != self.__lastm):
            self.__lastm = module.TS
            self.internal = module.TS("selfbuild")

    def init(self):
        self.internal = None
        self.__lastm = None
        self.mayreinit()

    def langmap(self):
        self.mayreinit()
        if not self.internal:
            return {}
        return self.internal.langmap()

    def translate(self, content):
        self.mayreinit()
        if not self.internal:
            return ""
        return self.internal.translate(content)
