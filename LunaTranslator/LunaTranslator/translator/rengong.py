from translator.basetranslator import basetrans
from myutils.config import globalconfig, savehook_new_data
import os
import json
import winsharedutils
import gobject


class TS(basetrans):
    def checkfilechanged(self, p1, p):
        if self.paths != (p1, p):
            self.json = {}
            if p:
                for pp in p.split("|"):
                    if os.path.exists(pp):
                        with open(pp, "r", encoding="utf8") as f:
                            self.json.update(json.load(f))
            if p1:
                if os.path.exists(p1):
                    with open(p1, "r", encoding="utf8") as f:
                        self.json.update(json.load(f))
            self.paths = (p1, p)

    def unsafegetcurrentgameconfig(self):
        try:
            _path = gobject.baseobject.textsource.pname
            _path = savehook_new_data[_path]["gamejsonfile"]
            return _path
        except:
            return None

    def inittranslator(self):
        self.paths = (None, None)
        self.checkfilechanged(
            self.unsafegetcurrentgameconfig(), self.config["json文件"]
        )

    def translate(self, content):
        self.checkfilechanged(
            self.unsafegetcurrentgameconfig(), self.config["json文件"]
        )
        if globalconfig["premtsimiuse"]:
            maxsim = 0
            savet = None
            for jc in self.json:
                dis = winsharedutils.distance_ratio(content, jc)
                if dis > maxsim:
                    maxsim = dis
                    if maxsim * 100 >= globalconfig["premtsimi2"]:
                        if type(self.json[jc]) == str:
                            savet = self.json[jc]
                        elif (
                            self.json[jc]["userTrans"]
                            and self.json[jc]["userTrans"] != ""
                        ):
                            savet = self.json[jc]["userTrans"]

                        elif (
                            self.json[jc]["machineTrans"]
                            and self.json[jc]["machineTrans"] != ""
                        ):
                            savet = self.json[jc]["machineTrans"]
            if savet is None:
                raise Exception(f"can't find: {content}")
            return savet
        else:
            if content not in self.json:
                raise Exception(f"can't find: {content}")
            if type(self.json[content]) == str:
                return self.json[content]
            elif (
                self.json[content]["userTrans"]
                and self.json[content]["userTrans"] != ""
            ):
                return self.json[content]["userTrans"]

            elif (
                self.json[content]["machineTrans"]
                and self.json[content]["machineTrans"] != ""
            ):
                return self.json[content]["machineTrans"]
