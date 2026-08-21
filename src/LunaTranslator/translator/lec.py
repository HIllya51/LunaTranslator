from translator.basetranslator import basetrans
from myutils.config import _TR
from language import Languages
from LunaSubProcess import LunaSubProcess


class TS(basetrans):
    def init(self):
        self.path = None
        self.pair = None
        self.checkpath()

    def langmap(self):
        return {Languages.Auto: "ja"}

    def checkpath(self):

        pairs = (self.srclang, self.tgtlang)
        if pairs == self.pair:
            return
        self.pair = pairs
        self._proc = LunaSubProcess.lec(self.srclang, self.tgtlang)

    def translate(self, content: str):

        self.checkpath()
        r = self._proc.translate(content)
        if r is None:
            raise Exception(_TR("未安装"))
        return r
