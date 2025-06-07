import threading, gobject, queue
import json
from traceback import print_exc
from myutils.config import globalconfig, savehook_new_data
from myutils.utils import autosql
from sometypes import TranslateResult


class basetext:

    def gettextonce(self):
        return None

    def init(self): ...
    def end(self): ...
    def runornot(self, b): ...
    def __init__(self):
        #

        self.textgetmethod = gobject.baseobject.textgetmethod

        self.ending = False
        self.sqlqueue = None
        self.init()

    def startsql(self, sqlfname_all):
        self.sqlqueueput(None)
        self.sqlqueue = queue.Queue()
        try:

            # self.sqlwrite=sqlite3.connect(self.sqlfname,check_same_thread = False, isolation_level=None)
            self.sqlwrite2 = autosql(
                sqlfname_all, check_same_thread=False, isolation_level=None
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
            print_exc()
        threading.Thread(target=self.sqlitethread).start()

    def dispatchtext(self, *arg, **kwarg):
        if self.ending or not self.isautorunning:
            return
        self.textgetmethod(*arg, **kwarg)

    def waitfortranslation(self, text):
        resultwaitor = queue.Queue()
        self.textgetmethod(
            text,
            is_auto_run=True,
            waitforresultcallback=resultwaitor.put,
            waitforresultcallbackengine=globalconfig["toppest_translator"],
        )
        tsres: TranslateResult = resultwaitor.get()
        return tsres.result

    @property
    def isautorunning(self):
        return globalconfig["autorun"]

    ##################
    def endX(self):
        self.ending = True
        self.sqlqueueput(None)
        self.end()

    def sqlqueueput(self, xx):
        try:
            self.sqlqueue.put(xx)
        except:
            pass

    def sqlitethread(self):
        while not self.ending:
            task = self.sqlqueue.get()
            if not task:
                break
            try:
                if len(task) == 2:
                    src, origin = task
                    lensrc = len(src)
                    ret = self.sqlwrite2.execute(
                        "SELECT * FROM artificialtrans WHERE source = ?", (src,)
                    ).fetchone()
                    try:
                        if (
                            "statistic_wordcount"
                            not in savehook_new_data[gobject.baseobject.gameuid]
                        ):
                            savehook_new_data[gobject.baseobject.gameuid][
                                "statistic_wordcount"
                            ] = 0
                        savehook_new_data[gobject.baseobject.gameuid][
                            "statistic_wordcount"
                        ] += lensrc
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
                            if (
                                "statistic_wordcount_nodump"
                                not in savehook_new_data[gobject.baseobject.gameuid]
                            ):
                                savehook_new_data[gobject.baseobject.gameuid][
                                    "statistic_wordcount_nodump"
                                ] = 0
                            savehook_new_data[gobject.baseobject.gameuid][
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

    def runonce(self):
        t = self.gettextonce()
        if t:
            self.textgetmethod(t, False)
