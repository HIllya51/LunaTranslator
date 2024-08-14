import threading, gobject, queue
import time, sqlite3, json, os, windows, winsharedutils
from traceback import print_exc
from myutils.config import (
    globalconfig,
    savehook_new_data,
    findgameuidofpath,
    uid2gamepath,
)
from myutils.utils import autosql, getfilemd5
from myutils.hwnd import getpidexe
from myutils.wrapper import threader


class hwndchecker:
    def __del__(self):
        if self.ref.hwnd:
            return
        gobject.baseobject.translation_ui.processismuteed = False
        gobject.baseobject.translation_ui.isbindedwindow = False
        gobject.baseobject.translation_ui.refreshtooliconsignal.emit()
        gobject.baseobject.translation_ui.thistimenotsetop = False
        if globalconfig["keepontop"]:
            gobject.baseobject.translation_ui.settop()

    def __init__(self, hwnd, ref) -> None:
        self.hwnd = hwnd
        self.ref = ref
        self.end = False

        _mute = winsharedutils.GetProcessMute(
            windows.GetWindowThreadProcessId(self.hwnd)
        )

        gobject.baseobject.translation_ui.processismuteed = _mute
        gobject.baseobject.translation_ui.isbindedwindow = True
        gobject.baseobject.translation_ui.refreshtooliconsignal.emit()
        self.__checkthread()

    @threader
    def __checkthread(self):
        while not self.end:
            pid = windows.GetWindowThreadProcessId(self.hwnd)
            if not pid:
                self.hwnd = None
                self.__del__()
                break
            _mute = winsharedutils.GetProcessMute(pid)
            if gobject.baseobject.translation_ui.processismuteed != _mute:
                gobject.baseobject.translation_ui.processismuteed = _mute
                gobject.baseobject.translation_ui.refreshtooliconsignal.emit()
            time.sleep(0.5)


class basetext:
    @property
    def hwnd(self):

        if self.__hwnd is None:
            return None
        return self.__hwnd.hwnd

    @hwnd.setter
    def hwnd(self, _hwnd):
        if self.__hwnd:
            self.__hwnd.end = True
        self.__hwnd = None
        self.pids = []
        self.gameuid = None
        self.md5 = "0"
        self.basename = self.__basename
        if _hwnd:

            self.__hwnd = hwndchecker(_hwnd, self)

            self.pids = [windows.GetWindowThreadProcessId(_hwnd)]
            gameuid = findgameuidofpath(getpidexe(self.pids[0]))
            if gameuid:
                self.gameuid = gameuid[0]
                self.md5 = getfilemd5(uid2gamepath[gameuid[0]])
                gamepath = uid2gamepath[self.gameuid]
                self.basename = os.path.basename(gamepath).replace(
                    "." + os.path.basename(gamepath).split(".")[-1], ""
                )

    def __init__(self, md5, basename):
        self.md5 = md5
        self.__basename = self.basename = basename
        self.__hwnd = None
        self.pids = []
        self.gameuid = None
        #

        self.textgetmethod = gobject.baseobject.textgetmethod

        self.ending = False
        self.sqlqueue = queue.Queue()

        sqlfname_all_old = gobject.gettranslationrecorddir(
            md5 + "_" + basename + ".pretrans_common.sqlite"
        )
        sqlfname_all = gobject.gettranslationrecorddir(basename + "_" + md5 + ".sqlite")
        if os.path.exists(sqlfname_all_old):
            sqlfname_all = sqlfname_all_old
        try:

            # self.sqlwrite=sqlite3.connect(self.sqlfname,check_same_thread = False, isolation_level=None)
            self.sqlwrite2 = autosql(
                sqlite3.connect(
                    sqlfname_all, check_same_thread=False, isolation_level=None
                )
            )
            # try:
            #     self.sqlwrite.execute('CREATE TABLE artificialtrans(id INTEGER PRIMARY KEY AUTOINCREMENT,source TEXT,machineTrans TEXT,userTrans TEXT);')
            # except:
            #     pass
            try:
                self.sqlwrite2.execute(
                    "CREATE TABLE artificialtrans(id INTEGER PRIMARY KEY AUTOINCREMENT,source TEXT,machineTrans TEXT,origin TEXT);"
                )
            except:
                pass
        except:
            print_exc
        threading.Thread(target=self.sqlitethread).start()
        threading.Thread(target=self.gettextthread_).start()

    def gettextthread(self):
        return None

    def gettextonce(self):
        return None

    def end(self):
        self.ending = True

    ##################
    def sqlqueueput(self, xx):
        try:
            self.sqlqueue.put(xx)
        except:
            pass

    def sqlitethread(self):
        while True:
            task = self.sqlqueue.get()
            try:
                if len(task) == 2:
                    src, origin = task
                    lensrc = len(src)
                    ret = self.sqlwrite2.execute(
                        "SELECT * FROM artificialtrans WHERE source = ?", (src,)
                    ).fetchone()
                    try:
                        savehook_new_data[self.gameuid]["statistic_wordcount"] += lensrc
                    except:
                        pass
                    if ret is None:
                        try:
                            self.sqlwrite2.execute(
                                "INSERT INTO artificialtrans VALUES(NULL,?,?,?);",
                                (src, json.dumps({}), origin),
                            )
                        except:
                            self.sqlwrite2.execute(
                                "INSERT INTO artificialtrans VALUES(NULL,?,?);",
                                (src, json.dumps({})),
                            )
                        try:
                            savehook_new_data[self.gameuid][
                                "statistic_wordcount_nodump"
                            ] += lensrc
                        except:
                            pass
                elif len(task) == 3:
                    src, clsname, trans = task
                    ret = self.sqlwrite2.execute(
                        "SELECT machineTrans FROM artificialtrans WHERE source = ?",
                        (src,),
                    ).fetchone()

                    ret = json.loads((ret[0]))
                    ret[clsname] = trans
                    ret = json.dumps(ret, ensure_ascii=False)
                    self.sqlwrite2.execute(
                        "UPDATE artificialtrans SET machineTrans = ? WHERE source = ?",
                        (ret, src),
                    )
            except:
                print_exc()

    def gettextthread_(self):
        while True:
            if self.ending:
                break
            if globalconfig["autorun"] == False:
                time.sleep(0.1)
                continue

            # print(globalconfig['autorun'])
            try:
                t = self.gettextthread()
                if t and globalconfig["autorun"]:
                    if isinstance(t, tuple):
                        self.textgetmethod(*t)
                    else:
                        self.textgetmethod(t)
            except:
                print_exc()

    def runonce(self):
        t = self.gettextonce()
        if t:
            self.textgetmethod(t, False)
