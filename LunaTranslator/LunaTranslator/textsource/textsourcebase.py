import threading, gobject, queue
import time, sqlite3, json, os
from traceback import print_exc
from myutils.config import globalconfig, savehook_new_data
from myutils.utils import getfilemd5, autosql


class basetext:
    def __init__(self, md5, basename):
        self.textgetmethod = gobject.baseobject.textgetmethod
        self.ending = False
        self.sqlqueue = queue.Queue()
        if "hwnd" not in dir(self):
            self.hwnd = 0
        if "pids" not in dir(self):
            self.pids = []
        self.md5 = md5
        self.basename = basename
        os.makedirs("./translation_record", exist_ok=True)
        sqlfname_all_old = (
            "./translation_record/" + md5 + "_" + basename + ".pretrans_common.sqlite"
        )
        sqlfname_all = "./translation_record/" + basename + "_" + md5 + ".sqlite"
        if os.path.exists(sqlfname_all_old):
            sqlfname_all = sqlfname_all_old
        self.uuname = basename + "_" + md5
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
                        savehook_new_data[self.pname]["statistic_wordcount"] += lensrc
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
                            savehook_new_data[self.pname][
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

    def checkmd5prefix(self, pname):
        md5 = getfilemd5(pname)
        name = os.path.basename(pname).replace(
            "." + os.path.basename(pname).split(".")[-1], ""
        )
        return md5, name

    def showgamename(self):
        if "showonce" not in dir(self):
            gobject.baseobject.textgetmethod(
                "<msg_info_refresh>" + savehook_new_data[self.pname]["title"]
            )
            self.showonce = 1

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
                    if type(t) == tuple:
                        self.textgetmethod(*t)
                    else:
                        self.textgetmethod(t)
            except:
                print_exc()

    def runonce(self):
        t = self.gettextonce()
        if t:
            self.textgetmethod(t, False)
