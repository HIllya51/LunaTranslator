import sqlite3, gobject, time, windows
import time
import os
from qtsymbols import *
from myutils.config import findgameuidofpath, globalconfig
from myutils.hwnd import ListProcess
from myutils.wrapper import threader
import threading
import windows
import gobject


class somedatabase:
    def all(self):
        res = self.sqlsavegameinfo.execute(
            "SELECT gameinternalid_v2.gameuid, trace_strict.timestart, trace_strict.timestop FROM gameinternalid_v2 JOIN trace_strict ON gameinternalid_v2.gameinternalid = trace_strict.gameinternalid "
        ).fetchall()
        mp: "dict[str, list]" = {}
        for uid, s, e in res:
            if uid not in mp:
                mp[uid] = []
            mp[uid].append((s, e))
        return mp

    def append_word(self, word, sentence=None):
        sentence = sentence if sentence else ""
        self.sqlsavegameinfo.execute(
            "INSERT INTO search_word_history VALUES(NULL,?,?,?,?)".format(),
            (word, sentence, time.time(), 0),
        )

    def removewhich(self, _id):
        self.sqlsavegameinfo.execute(
            "DELETE FROM search_word_history WHERE id=?", (_id,)
        )

    def allwords(self):
        return self.sqlsavegameinfo.execute(
            "SELECT * FROM search_word_history ORDER BY id DESC"
        ).fetchall()

    def __init__(self):
        self.locked = threading.Lock()
        self.sqlsavegameinfo = sqlite3.connect(
            gobject.getconfig("savegame.db"),
            check_same_thread=False,
            isolation_level=None,
        )
        try:
            self.sqlsavegameinfo.execute(
                "CREATE TABLE search_word_history(id INTEGER PRIMARY KEY AUTOINCREMENT,WORD TEXT, SENTENCE TEXT ,timestamp BIGINT, status INT);"
            )
        except:
            pass
        try:
            self.sqlsavegameinfo.execute(
                "CREATE TABLE traceplaytime_v4(id INTEGER PRIMARY KEY AUTOINCREMENT,gameinternalid INT,timestart BIGINT,timestop BIGINT);"
            )
        except:
            pass
        try:
            self.sqlsavegameinfo.execute(
                "CREATE TABLE gameinternalid_v2(gameinternalid INTEGER PRIMARY KEY AUTOINCREMENT,gameuid TEXT);"
            )
            self.trycastoldversion()
        except:
            pass
        try:
            self.sqlsavegameinfo.execute(
                "CREATE TABLE trace_strict(gameinternalid INT,timestart BIGINT,timestop BIGINT);"
            )
            self.sqlsavegameinfo.execute(
                "INSERT INTO trace_strict SELECT gameinternalid,timestart,timestop FROM traceplaytime_v4"
            )
            self.sqlsavegameinfo.execute(
                "CREATE TABLE trace_loose(gameinternalid INT,timestart BIGINT,timestop BIGINT);"
            )
            self.sqlsavegameinfo.execute(
                "INSERT INTO trace_loose SELECT gameinternalid,timestart,timestop FROM traceplaytime_v4"
            )
            self.sqlsavegameinfo.commit()
        except:
            pass

        self.checkgameplayingthread()

    def trycastoldversion(self):
        for _id, gamepath in self.sqlsavegameinfo.execute(
            "SELECT * from gameinternalid"
        ).fetchall():
            gameuid = findgameuidofpath(gamepath)
            if not gameuid:
                continue
            self.sqlsavegameinfo.execute(
                "INSERT INTO gameinternalid_v2 VALUES(?,?)", (_id, gameuid[0])
            )
        self.sqlsavegameinfo.commit()

    def lockdata(self):
        self.locked.acquire()

    def unlockdata(self):
        self.locked.release()

    def settraceplaytime(self, gameuid, lst: "list[tuple[float, float]]"):
        table = ["trace_loose", "trace_strict"][globalconfig["is_tracetime_strict"]]
        gameinternalid = self.__get_gameinternalid(gameuid)
        self.sqlsavegameinfo.execute(
            "DELETE FROM {} WHERE gameinternalid = ?".format(table), (gameinternalid,)
        )
        for s, e in lst:
            self.sqlsavegameinfo.execute(
                "INSERT INTO {} VALUES(?,?,?)".format(table),
                (gameinternalid, s, e),
            )
        self.sqlsavegameinfo.commit()

    def querytraceplaytime(self, gameuid) -> "list[tuple[float, float]]":
        table = ["trace_loose", "trace_strict"][globalconfig["is_tracetime_strict"]]
        gameinternalid = self.__get_gameinternalid(gameuid)
        return self.sqlsavegameinfo.execute(
            "SELECT timestart,timestop FROM {} WHERE gameinternalid = ?".format(table),
            (gameinternalid,),
        ).fetchall()

    def __get_gameinternalid(self, gameuid):
        while True:
            ret = self.sqlsavegameinfo.execute(
                "SELECT * FROM gameinternalid_v2 WHERE gameuid = ?",
                (gameuid,),
            ).fetchone()
            if ret is None:
                self.sqlsavegameinfo.execute(
                    "INSERT INTO gameinternalid_v2 VALUES(NULL,?)", (gameuid,)
                )
                self.sqlsavegameinfo.commit()
            else:
                return ret[0]

    def stricttraceexe(self):
        hwnd = windows.GetForegroundWindow()
        pid = windows.GetWindowThreadProcessId(hwnd)
        exe = windows.GetProcessFileName(pid)
        exes = set()
        exes.add(exe)

        gamehwnd = gobject.base.hwnd
        if gamehwnd:
            gamepid = windows.GetWindowThreadProcessId(gamehwnd)
            if gamepid and pid == os.getpid():
                exes.add(windows.GetProcessFileName(gamepid))
        return exes

    def finduids(self, exes):
        uids = []
        for exe in exes:
            uid, _ = findgameuidofpath(exe)
            if not uid:
                continue
            uids.append(uid)
        return uids

    def tracex(self, _t: float, uids: list, dic: dict, table: str):
        for uid in uids:
            gameinternalid = self.__get_gameinternalid(uid)
            if uid in dic:
                self.sqlsavegameinfo.execute(
                    "UPDATE {} SET timestop = ? WHERE (gameinternalid = ? and timestart = ?)".format(
                        table
                    ),
                    (_t, gameinternalid, dic[uid]),
                )

            else:
                dic[uid] = _t
                self.sqlsavegameinfo.execute(
                    "INSERT INTO {} VALUES(?,?,?)".format(table),
                    (gameinternalid, _t, _t),
                )
        for k in list(dic.keys()):
            if k not in uids:
                dic.pop(k)

    @threader
    def checkgameplayingthread(self):
        self.trace_loose = {}
        self.trace_strict = {}
        tlast = None
        t = time.time()
        while True:
            with self.locked:
                tlast = t
                t = time.time()
                if t - tlast > 10:
                    # 虚拟机暂停
                    self.trace_loose.clear()
                    self.trace_strict.clear()
                    continue

                self.tracex(
                    t, self.finduids(ListProcess()), self.trace_loose, "trace_loose"
                )
                self.tracex(
                    t,
                    self.finduids(self.stricttraceexe()),
                    self.trace_strict,
                    "trace_strict",
                )
                self.sqlsavegameinfo.commit()
            time.sleep(5)
