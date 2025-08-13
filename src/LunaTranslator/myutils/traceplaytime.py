import sqlite3, gobject, time, windows
import time
import os
from qtsymbols import *
from myutils.config import findgameuidofpath, globalconfig
from myutils.hwnd import ListProcess
from myutils.wrapper import threader
import windows
import gobject


class playtimemanager:
    def all(self):
        res = self.sqlsavegameinfo.execute(
            "SELECT gameinternalid_v2.gameuid, trace_strict.timestart, trace_strict.timestop FROM gameinternalid_v2 JOIN trace_strict ON gameinternalid_v2.gameinternalid = trace_strict.gameinternalid "
        ).fetchall()
        mp = {}
        for uid, s, e in res:
            if uid not in mp:
                mp[uid] = []
            mp[uid].append((s, e))
        return mp

    def __init__(self):

        self.sqlsavegameinfo = sqlite3.connect(
            gobject.getuserconfigdir("savegame.db"),
            check_same_thread=False,
            isolation_level=None,
        )
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

    def querytraceplaytime(self, gameuid):
        table = ["trace_loose", "trace_strict"][globalconfig["is_tracetime_strict"]]
        gameinternalid = self.get_gameinternalid(gameuid)
        return self.sqlsavegameinfo.execute(
            "SELECT timestart,timestop FROM {} WHERE gameinternalid = ?".format(table),
            (gameinternalid,),
        ).fetchall()

    def get_gameinternalid(self, gameuid):
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
            gameinternalid = self.get_gameinternalid(uid)
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
