from translator.basetranslator import basetrans
from myutils.config import _TR
from LunaSubProcess import LunaSubProcess


class TS(basetrans):
    def init(self):
        self._proc = LunaSubProcess.atlas()

    def translate(self, content: str):
        r = self._proc.translate(content)
        if r is None:
            raise Exception(_TR("未安装"))
        return r
