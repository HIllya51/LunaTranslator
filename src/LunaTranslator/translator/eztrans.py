from translator.basetranslator import basetrans
from myutils.config import _TR
import os
from LunaSubProcess import LunaSubProcess


class TS(basetrans):
    def init(self):
        self.path = None
        self.userdict = None
        self.checkpath()

    def checkpath(self):
        if self.config["path"] == "":
            return False
        if os.path.exists(self.config["path"]) == False:
            return False
        if self.config["path"] != self.path:
            self.path = self.config["path"]
            self._proc = LunaSubProcess.eztrans(
                os.path.normpath(os.path.dirname(os.path.abspath(self.path)))
            )
        return True

    def translate(self, content: str):

        if not self.checkpath():
            raise Exception(_TR("翻译器加载失败"))
        r = self._proc.translate(content)
        if r is None:
            raise Exception(_TR("未安装"))
        return r
