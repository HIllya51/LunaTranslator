from translator.basetranslator import basetrans
import os
from myutils.config import _TR
from language import Languages
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
            paths = set()
            for _dir, _, _fs in os.walk(self.path):
                for _f in _fs:
                    path = os.path.normpath(os.path.abspath(os.path.join(_dir, _f)))
                    base, _ = os.path.splitext(os.path.basename(_f))
                    if base == "Jcuser":
                        paths.add(os.path.dirname(path))

            self.dllpath = os.path.abspath(os.path.join(self.path, "JBJCT.dll"))
            dicts = []
            for d in sorted(list(paths), key=lambda x: -len(x))[:3]:
                dicts.append(os.path.abspath(os.path.join(d, "Jcuser")))
            self._proc = LunaSubProcess.jb7(self.dllpath, dicts)
        return True

    def translate(self, content: str):
        if self.tgtlang not in ["936", "950"]:
            return ""
        if self.checkpath() == False:
            raise Exception(_TR("翻译器加载失败"))
        return self._proc.translate(content, int(self.tgtlang))

    def langmap(self):
        return {Languages.Chinese: "936", Languages.TradChinese: "950"}
