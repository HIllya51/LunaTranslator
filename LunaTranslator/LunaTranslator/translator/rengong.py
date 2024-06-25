from translator.basetranslator import basetrans
from myutils.config import globalconfig, savehook_new_data
import os
import json
import winsharedutils
import gobject


class TS(basetrans):
    def checkfilechanged(self, p1, p):
        if self.paths != (p1, p):
            self.jsons = []
            if p:
                for pp in p:
                    if os.path.exists(pp):
                        with open(pp, "r", encoding="utf8") as f:
                            self.jsons.append(json.load(f))
            if p1:
                for pp in p1:
                    if os.path.exists(pp):
                        with open(pp, "r", encoding="utf8") as f:
                            self.jsons.append(json.load(f))
            self.paths = (p1, p)

    def unsafegetcurrentgameconfig(self):
        try:
            gameuid = gobject.baseobject.textsource.gameuid
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

    def translate(self, content):
        self.checkfilechanged(
            self.unsafegetcurrentgameconfig(), tuple(self.config["jsonfile"])
        )
        collect = []
        if globalconfig["premtsimiuse"]:
            for _js in self.jsons:
                maxsim = 0
                savet = None
                for jc in _js:
                    dis = winsharedutils.distance_ratio(content, jc)
                    if dis > maxsim:
                        maxsim = dis
                        if maxsim * 100 >= globalconfig["premtsimi2"]:
                            if type(_js[jc]) == str:
                                savet = _js[jc]
                            elif _js[jc]["userTrans"] and _js[jc]["userTrans"] != "":
                                savet = _js[jc]["userTrans"]

                            elif (
                                _js[jc]["machineTrans"]
                                and _js[jc]["machineTrans"] != ""
                            ):
                                savet = _js[jc]["machineTrans"]
                if savet is None:
                    continue
                else:
                    collect.append(savet)

        else:
            for _js in self.jsons:
                if content not in _js:
                    continue
                if type(_js[content]) == str:
                    collect.append(_js[content])
                elif _js[content]["userTrans"] and _js[content]["userTrans"] != "":
                    collect.append(_js[content]["userTrans"])

                elif (
                    _js[content]["machineTrans"] and _js[content]["machineTrans"] != ""
                ):
                    collect.append(_js[content]["machineTrans"])
        if len(collect) == 0:
            raise Exception(f"can't find: {content}")
        return "\n".join(collect)
