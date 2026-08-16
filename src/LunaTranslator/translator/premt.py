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
            self._sql_path = None
            self._rows_cache = None  # 路径变化，失效全表缓存
            if p:
                if os.path.exists(p):
                    self.sql = autosql(p, check_same_thread=False)
                    self._sql_path = p
            if p1:
                if os.path.exists(p1):
                    self.sql = autosql(p1, check_same_thread=False)
                    self._sql_path = p1
            self.paths = (p1, p)

    def _fetchallrows(self, sql):
        # 模糊匹配模式下每次翻译都要扫全表，按数据库文件修改时间缓存，
        # 避免每条文本都读盘 + 全表相似度扫描。
        path = self._sql_path
        if path is not None:
            try:
                mt = os.path.getmtime(path)
            except OSError:
                mt = None
            cache = self._rows_cache
            if cache is not None and cache[0] == mt and cache[1] == path:
                return cache[2]
            rows = sql.execute("SELECT * FROM artificialtrans").fetchall()
            if mt is not None:
                self._rows_cache = (mt, path, rows)
            return rows
        return sql.execute("SELECT * FROM artificialtrans").fetchall()

    def init(self):
        self.sql = None
        self.paths = (None, None)
        self._sql_path = None
        self._rows_cache = None
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
        if self.config["premtsimi2"] < 100:
            maxsim = 0
            savet = "{}"
            ret = self._fetchallrows(sql)
            if not ret:
                return {}
            for line in ret:
                text = line[1]
                trans = line[2]
                dis = NativeUtils.similarity(content, text)
                if dis > maxsim:
                    maxsim = dis
                    if maxsim * 100 >= self.config["premtsimi2"]:
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
