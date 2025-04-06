from translator.basetranslator import basetrans
from myutils.utils import checkmd5reloadmodule


class TS(basetrans):
    def mayreinit(self):
        isnew, module = checkmd5reloadmodule("userconfig/selfbuild.py", "selfbuild")
        if (not isnew) and self.internal:
            return
        if module:
            self.internal = module.TS("selfbuild")

    def init(self):
        self.internal = None
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
