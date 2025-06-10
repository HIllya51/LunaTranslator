from translator.basetranslator import basetrans
from myutils.config import globalconfig, savehook_new_data
from myutils.utils import autosql
import os
import gobject
import json
import sqlite3
import NativeUtils


class TS(basetrans):
    def unsafegetcurrentgameconfig(self):
        try:
            gameuid = gobject.base.gameuid
            _path = savehook_new_data[gameuid]["gamesqlitefile"]
            return _path
        except:
            return None

    def checkfilechanged(self, p1, p):
        if self.paths != (p1, p):
            self.sql = None
            if p:
                if os.path.exists(p):
                    self.sql = autosql(p, check_same_thread=False)
            if p1:
                if os.path.exists(p1):
                    self.sql = autosql(p1, check_same_thread=False)
            self.paths = (p1, p)

    def init(self):
        self.sql = None
        self.paths = (None, None)
        self.checkfilechanged(
            self.unsafegetcurrentgameconfig(), self.config["sqlitefile"]
        )

    def translate(self, content):
        self.checkfilechanged(
            self.unsafegetcurrentgameconfig(), self.config["sqlitefile"]
        )
        if self.sql is None:
            try:
                sql = gobject.base.textsource.sqlwrite2
            except:
                return {}
        else:
            sql = self.sql
        if globalconfig["premtsimi2"] < 100:
            maxsim = 0
            savet = "{}"
            ret = sql.execute("SELECT * FROM artificialtrans  ").fetchall()
            if not ret:
                return {}
            for line in ret:
                text = line[1]
                trans = line[2]
                dis = NativeUtils.similarity(content, text)
                if dis > maxsim:
                    maxsim = dis
                    if maxsim * 100 >= globalconfig["premtsimi2"]:
                        savet = trans
            try:
                ret = json.loads(savet)
            except:
                # 旧版兼容
                ret = {"premt": ret[0]}

        else:

            ret = sql.execute(
                "SELECT machineTrans FROM artificialtrans WHERE source = ?", (content,)
            ).fetchone()
            if not ret:
                return {}
            try:
                ret = json.loads(ret[0])
            except:
                ret = {"premt": ret[0]}
        if self.config["仅使用激活的翻译"]:
            realret = {}
            for key in ret:
                if key in globalconfig["fanyi"] and globalconfig["fanyi"][key]["use"]:
                    realret[key] = ret[key]
            ret = realret
        return ret
