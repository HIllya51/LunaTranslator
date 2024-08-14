import sqlite3, gobject, threading, time, windows
import time
import os, threading
from qtsymbols import *
from traceback import print_exc
from myutils.config import (
    uid2gamepath,
    findgameuidofpath,
    savehook_new_list,
    savehook_new_data,
)
from myutils.hwnd import getpidexe
import windows
import gobject


class playtimemanager:
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

        threading.Thread(target=self.checkgameplayingthread).start()

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

    def querytraceplaytime_v4(self, gameuid):
        gameinternalid = self.get_gameinternalid(gameuid)
        return self.sqlsavegameinfo.execute(
            "SELECT timestart,timestop FROM traceplaytime_v4 WHERE gameinternalid = ?",
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
            else:
                return ret[0]

    def traceplaytime(self, gameuid, start, end, new):

        gameinternalid = self.get_gameinternalid(gameuid)
        if new:
            self.sqlsavegameinfo.execute(
                "INSERT INTO traceplaytime_v4 VALUES(NULL,?,?,?)",
                (gameinternalid, start, end),
            )
        else:
            self.sqlsavegameinfo.execute(
                "UPDATE traceplaytime_v4 SET timestop = ? WHERE (gameinternalid = ? and timestart = ?)",
                (end, gameinternalid, start),
            )

    def checkgameplayingthread(self):
        self.__currentexe = None
        self.__statistictime = time.time()
        while True:
            __t = time.time()
            time.sleep(1)
            _t = time.time()

            def isok(gameuid):
                # 可能开着程序进行虚拟机暂停，导致一下子多了很多时间。不过测试vbox上应该没问题
                maybevmpaused = (_t - __t) > 60
                if not maybevmpaused:
                    savehook_new_data[gameuid]["statistic_playtime"] += _t - __t
                if (not maybevmpaused) and (self.__currentexe == name_):
                    self.traceplaytime(gameuid, self.__statistictime - 1, _t, False)

                else:
                    self.__statistictime = time.time()
                    self.__currentexe = name_
                    self.traceplaytime(
                        gameuid,
                        self.__statistictime - 1,
                        self.__statistictime,
                        True,
                    )

            _hwnd = windows.GetForegroundWindow()
            _pid = windows.GetWindowThreadProcessId(_hwnd)
            try:
                if len(gobject.baseobject.textsource.pids) == 0:
                    raise Exception()
                if _pid in gobject.baseobject.textsource.pids or _pid == os.getpid():
                    isok(gobject.baseobject.textsource.gameuid)
                else:
                    self.__currentexe = None
            except:
                name_ = getpidexe(_pid)
                if not name_:
                    return
                uid = findgameuidofpath(name_)
                try:
                    if uid:
                        isok(uid[0])
                    else:
                        self.__currentexe = None
                except:
                    print_exc()
