from translator.basetranslator import basetrans
from myutils.config import _TR
import os
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
        if self.config["path"] == "":
            return False
        if os.path.exists(self.config["path"]) == False:
            return False
        pairs = (self.srclang, self.tgtlang)
        if self.config["path"] != self.path or pairs != self.pair:
            self.path = self.config["path"]

            self.pair = pairs
            mp = {("zh", "en"): 2, ("en", "zh"): 1, ("zh", "ja"): 3, ("ja", "zh"): 10}
            path = os.path.abspath(os.path.join(self.path, "DreyeMT\\SDK\\bin"))
            if mp[pairs] in [3, 10]:
                path2 = os.path.join(path, "TransCOM.dll")
            else:
                path2 = os.path.join(path, "TransCOMEC.dll")
            self._proc = LunaSubProcess.dreye(path, path2, mp[pairs])
        return True

    def translate(self, content: str):

        if not self.checkpath():
            raise Exception(_TR("翻译器加载失败"))
        codes = {
            Languages.Chinese: "gbk",
            Languages.Japanese: "shift-jis",
            Languages.English: "utf8",
        }
        return self._proc.translate(content, codes[self.srclang], codes[self.tgtlang])
