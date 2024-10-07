from translator.basetranslator import basetrans
from myutils.config import globalconfig, savehook_new_data
import os
import json
import winsharedutils
import gobject


class TS(basetrans):
    def checkfilechanged(self, p1, p):
        if self.paths == (p1, p):
            return
        self.paths = (p1, p)
        self.json = {}
        self.lines = None
        if p:
            for pp in p:
                self.safeload(pp)
        if p1:
            for pp in p1:
                self.safeload(pp)

    def safeload(self, pp):
        if not os.path.exists(pp):
            return
        with open(pp, "r", encoding="utf8") as f:
            try:
                self.json.update(json.load(f))
            except:
                pass

    def unsafegetcurrentgameconfig(self):
        try:
            gameuid = gobject.baseobject.gameuid
            _path = savehook_new_data[gameuid]["gamejsonfile"]
            if isinstance(_path, str):
                _path = [_path]
            return tuple(_path)
        except:
            return None

    def inittranslator(self):
        self.paths = (None, None)
        self.checkfilechanged(
            self.unsafegetcurrentgameconfig(), tuple(self.config["jsonfile"])
        )

    def analyze_result(self, obj):
        if type(obj) == str:
            return obj
        if type(obj) != dict:
            return None

        savet = obj.get("userTrans")
        if savet:
            return savet

        savet = obj.get("machineTrans")
        if savet:
            return savet

        return None

    def delayloadlines(self):
        if self.lines is not None:
            return
        self.lines = {}
        for k, v in self.json.items():
            if "\n" not in k:
                continue
            v = self.analyze_result(v)
            if not v:
                continue
            ks = k.split("\n")
            vs = v.split("\n")
            if len(ks) != len(vs):
                continue
            for i in range(len(ks)):
                self.lines[ks[i]] = vs[i]

    def tryfindtranslate(self, content: str, _js: dict, _js2: dict = None):
        if globalconfig["premtsimiuse"]:

            maxsim = 0
            savet = None
            for jx in (_js, _js2):
                if not jx:
                    continue
                for jc in jx:
                    dis = winsharedutils.distance_ratio(content, jc)
                    if dis > maxsim:
                        maxsim = dis
                        if maxsim * 100 >= globalconfig["premtsimi2"]:
                            savet = self.analyze_result(jx[jc])
            return savet

        else:
            if content in _js:
                return self.analyze_result(_js[content])
            if _js2 and (content in _js2):
                return self.analyze_result(_js2[content])
            return None

    def tryfindtranslate_single(self, content: str):
        self.delayloadlines()
        if "\n" not in content:
            return self.tryfindtranslate(content, self.json, self.lines)

        collect = []
        for line in content.split("\n"):
            line = self.tryfindtranslate(line, self.json, self.lines)
            if not line:
                return None
            collect.append(line)
        return "\n".join(collect)

    def translate(self, content: str):
        self.checkfilechanged(
            self.unsafegetcurrentgameconfig(), tuple(self.config["jsonfile"])
        )
        if globalconfig["premtmatcheveryline"]:
            res = self.tryfindtranslate_single(content)
        else:
            res = self.tryfindtranslate(content, self.json)
        if not res:
            raise Exception(f"can't find: {content}")
        return res
