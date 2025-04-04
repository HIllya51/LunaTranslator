from translator.basetranslator import basetrans
from myutils.config import globalconfig, savehook_new_data
import os
import json
import winsharedutils
import gobject


class TS(basetrans):
    _compatible_flag_is_sakura_less_than_5_52_3 = False

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
                for k, v in json.load(f).items():
                    if k not in self.json:
                        self.json[k] = []
                    self.json[k].append(v)
            except:
                pass

    def unsafegetcurrentgameconfig(self):
        try:
            gameuid = gobject.baseobject.gameuid
            _path = savehook_new_data[gameuid].get("gamejsonfile", [])
            if isinstance(_path, str):
                _path = [_path]
            return tuple(_path)
        except:
            return None

    def init(self):
        self.paths = (None, None)
        self.checkfilechanged(
            self.unsafegetcurrentgameconfig(), tuple(self.config["jsonfile"])
        )

    def analyze_result__(self, obj):
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

    def analyze_result(self, obj):
        _x = []
        for _ in obj:
            __ = self.analyze_result__(_)
            if __:
                _x.append(__)
        return _x

    def delayloadlines(self):
        if self.lines is not None:
            return
        self.lines = {}
        for k, vs in self.json.items():
            if "\n" not in k:
                continue
            vs = self.analyze_result(vs)
            if not vs:
                continue
            ks = k.split("\n")

            vss = [v.split("\n") for v in vs]
            for vs in vss:
                if len(ks) != len(vs):
                    continue
                for i in range(len(ks)):
                    if ks[i] not in self.lines:
                        self.lines[ks[i]] = []
                    self.lines[ks[i]].append(vs[i])

    def tryfindtranslate(self, content: str, _js: dict, _js2: dict = None):
        if globalconfig["premtsimi2"] < 100:

            maxsim = 0
            savet = None
            for jx in (_js, _js2):
                if not jx:
                    continue
                for jc in jx:
                    dis = winsharedutils.similarity(content, jc)
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
        collect = []
        for line in content.splitlines():
            line = self.tryfindtranslate(line, self.json, self.lines)
            if not line:
                return None
            collect.append("\n".join(line))
        return collect

    def translate(self, content):
        self.checkfilechanged(
            self.unsafegetcurrentgameconfig(), tuple(self.config["jsonfile"])
        )
        res = self.tryfindtranslate(content, self.json)
        if not res:
            res = self.tryfindtranslate_single(content)
        if not res:
            raise Exception("can't find: " + content)
        return "\n".join(res)
