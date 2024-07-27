from traceback import print_exc
from queue import Queue
from threading import Thread
import time, types
import zhconv, gobject
import sqlite3, os
import functools
from myutils.config import globalconfig, translatorsetting
from myutils.utils import stringfyerror, autosql, PriorityQueue, getlangtgt
from myutils.commonbase import ArgsEmptyExc, commonbase


class TimeOut(Exception):
    pass


class Threadwithresult(Thread):
    def __init__(self, func, defalut, ignoreexceptions):
        super(Threadwithresult, self).__init__()
        self.func = func
        self.result = defalut
        self.istimeout = True
        self.ignoreexceptions = ignoreexceptions
        self.exception = None

    def run(self):
        try:
            self.result = self.func()
        except Exception as e:
            self.exception = e
        self.istimeout = False

    def get_result(self, timeout=1, checktutukufunction=None):
        # Thread.join(self,timeout)
        # 不再超时等待，只检查是否是最后一个请求，若是则无限等待，否则立即放弃。
        while checktutukufunction and checktutukufunction() and self.istimeout:
            Thread.join(self, 0.1)

        if self.ignoreexceptions:
            return self.result
        else:
            if self.istimeout:
                raise TimeOut()
            elif self.exception:
                raise self.exception
            else:
                return self.result


def timeoutfunction(
    func, timeout=100, default=None, ignoreexceptions=False, checktutukufunction=None
):
    t = Threadwithresult(func, default, ignoreexceptions)
    t.start()
    return t.get_result(timeout, checktutukufunction)


class basetrans(commonbase):
    def langmap(self):
        # The mapping between standard language code and API language code, if not declared, defaults to using standard language code.
        # But the exception is cht. If api support cht, if must be explicitly declared the support of cht, otherwise it will translate to chs and then convert to cht.
        return {}

    def inittranslator(self):
        pass

    def translate(self, content):
        return ""

    @property
    def multiapikeycurrent(self):

        class alternatedict(dict):
            def __getitem__(self2, __key):
                t = super().__getitem__(__key)
                if type(t) != str:
                    raise Exception("Incorrect use of multiapikeycurrent")
                if "|" in t:
                    ts = t.split("|")
                    t = ts[self.multiapikeycurrentidx % len(ts)]
                return t.strip()

        return alternatedict(translatorsetting[self.typename]["args"])

    ############################################################
    _globalconfig_key = "fanyi"
    _setting_dict = translatorsetting

    def level2init(self):
        self.multiapikeycurrentidx = -1
        self.queue = PriorityQueue()
        self.sqlqueue = None
        try:
            self._private_init()
        except Exception as e:
            gobject.baseobject.textgetmethod(
                "<msg_error_not_refresh>"
                + globalconfig["fanyi"][self.typename]["name"]
                + " inittranslator failed : "
                + str(stringfyerror(e))
            )
            print_exc()

        self.lastrequesttime = 0
        self.requestid = 0
        self._cache = {}

        self.newline = None

        if self.transtype != "pre":
            try:

                self.sqlwrite2 = autosql(
                    sqlite3.connect(
                        gobject.gettranslationrecorddir(
                            "cache/{}.sqlite".format(self.typename)
                        ),
                        check_same_thread=False,
                        isolation_level=None,
                    )
                )
                try:
                    self.sqlwrite2.execute(
                        "CREATE TABLE cache(srclang,tgtlang,source,trans);"
                    )
                except:
                    pass
            except:
                print_exc
            self.sqlqueue = Queue()
            Thread(target=self._sqlitethread).start()
        Thread(target=self._fythread).start()

    def notifyqueuforend(self):
        if self.sqlqueue:
            self.sqlqueue.put(None)
        self.queue.put(None, 999)

    def _private_init(self):
        self.initok = False
        self.inittranslator()
        self.initok = True

    def _sqlitethread(self):
        while self.using:
            task = self.sqlqueue.get()
            if task is None:
                break
            try:
                src, trans = task
                self.sqlwrite2.execute(
                    "DELETE from cache WHERE (srclang,tgtlang,source)=(?,?,?)",
                    (self.srclang, self.tgtlang, src),
                )
                self.sqlwrite2.execute(
                    "INSERT into cache VALUES(?,?,?,?)",
                    (self.srclang, self.tgtlang, src, trans),
                )
            except:
                print_exc()

    @property
    def is_gpt_like(self):
        # Don't use short-term cache, only use long-term cache, useful for gpt like apis to modify prompt
        return globalconfig["fanyi"][self.typename].get("is_gpt_like", False)

    @property
    def onlymanual(self):
        # Only used during manual translation, not used during automatic translation
        return globalconfig["fanyi"][self.typename].get("manual", False)

    @property
    def needzhconv(self):
        # The API does not support direct translation to Traditional Chinese, only Simplified Chinese can be translated first and then converted to Traditional Chinese
        l = getlangtgt()
        return l == "cht" and "cht" not in self.langmap()

    @property
    def using(self):
        return globalconfig["fanyi"][self.typename]["use"]

    @property
    def transtype(self):
        # free/dev/api/offline/pre
        return globalconfig["fanyi"][self.typename].get("type", "free")

    def gettask(self, content):
        callback, contentraw, contentsolved, embedcallback, is_auto_run = content

        if embedcallback:
            priority = 1
        else:
            priority = 0
        self.queue.put(content, priority)

    def longtermcacheget(self, src):
        try:
            ret = self.sqlwrite2.execute(
                "SELECT trans FROM cache WHERE (srclang,tgtlang,source)=(?,?,?)",
                (self.srclang, self.tgtlang, src),
            ).fetchone()
            if ret:
                return ret[0]
            return None
        except:
            return None

    def longtermcacheset(self, src, tgt):
        self.sqlqueue.put((src, tgt))

    def shorttermcacheget(self, src):
        langkey = (self.srclang, self.tgtlang)
        if langkey not in self._cache:
            self._cache[langkey] = {}
        try:
            return self._cache[langkey][src]
        except KeyError:
            return None

    def shorttermcacheset(self, src, tgt):
        langkey = (self.srclang, self.tgtlang)

        if langkey not in self._cache:
            self._cache[langkey] = {}
        self._cache[langkey][src] = tgt

    def cached_translate(self, contentsolved, is_auto_run):
        is_using_gpt_and_retrans = is_auto_run == False and self.is_gpt_like
        if is_using_gpt_and_retrans == False:
            res = self.shorttermcacheget(contentsolved)
            if res:
                return res
        if globalconfig["uselongtermcache"]:
            res = self.longtermcacheget(contentsolved)
            if res:
                return res

        if self.transtype == "offline":
            res = self.translate(contentsolved)
        else:
            res = self.intervaledtranslate(contentsolved)
        return res

    def cachesetatend(self, contentsolved, res):
        if self.transtype == "pre":
            return
        if globalconfig["uselongtermcache"]:
            self.longtermcacheset(contentsolved, res)
        self.shorttermcacheset(contentsolved, res)

    def maybecachetranslate(self, contentraw, contentsolved, is_auto_run):
        if self.transtype == "pre":
            res = self.translate(contentraw)
        else:
            res = self.cached_translate(contentsolved, is_auto_run)
        return res

    def intervaledtranslate(self, content):
        interval = globalconfig["requestinterval"]
        current = time.time()
        self.current = current
        sleeptime = interval - (current - self.lastrequesttime)

        if sleeptime > 0:
            time.sleep(sleeptime)
        self.lastrequesttime = time.time()
        if (current != self.current) or (self.using == False):
            raise Exception

        self.multiapikeycurrentidx += 1

        res = self.translate(content)

        return res

    def _iterget(self, __callback, rid, __res):
        succ = True
        for _res in __res:
            if self.requestid != rid:
                succ = False
                break
            __callback(_res, 1)
        if succ:
            __callback("", 2)

    def __callback(self, collectiterres, callback, embedcallback, ares, is_iter_res):
        if self.needzhconv:
            ares = zhconv.convert(ares, "zh-tw")
        if ares == "\0":  # 清除前面的输出
            collectiterres.clear()
            pass
        else:
            collectiterres.append(ares)
        __ = ""
        for ares in collectiterres:
            if ares is None:
                continue
            __ += ares
        callback(__, embedcallback, is_iter_res)

    def reinitandtrans(self, contentraw, contentsolved, is_auto_run):
        if self.needreinit or self.initok == False:
            self.needreinit = False
            self.renewsesion()
            try:
                self._private_init()
            except Exception as e:
                raise Exception("inittranslator failed : " + str(stringfyerror(e)))
        return self.maybecachetranslate(contentraw, contentsolved, is_auto_run)

    def _fythread(self):
        self.needreinit = False
        while self.using:

            _ = self.queue.get()
            if _ is None:
                break
            (callback, contentraw, contentsolved, embedcallback, is_auto_run) = _
            if self.onlymanual and is_auto_run:
                continue
            if self.using == False:
                break
            if self.srclang_1 == self.tgtlang_1:
                callback(contentsolved, embedcallback, False)
                continue
            self.requestid += 1
            try:
                checktutukufunction = (
                    lambda: ((embedcallback is not None) or self.queue.empty())
                    and self.using
                )
                if checktutukufunction():

                    res = timeoutfunction(
                        functools.partial(
                            self.reinitandtrans, contentraw, contentsolved, is_auto_run
                        ),
                        checktutukufunction=checktutukufunction,
                    )
                    collectiterres = []

                    __callback = functools.partial(
                        self.__callback, collectiterres, callback, embedcallback
                    )
                    if isinstance(res, types.GeneratorType):

                        timeoutfunction(
                            functools.partial(
                                self._iterget, __callback, self.requestid, res
                            ),
                            checktutukufunction=checktutukufunction,
                        )

                    else:
                        if globalconfig["fix_translate_rank"]:
                            # 这个性能会稍微差一点，不然其实可以全都这样的。
                            __callback(res, 1)
                            __callback("", 2)
                        else:
                            __callback(res, 0)
                    if all([_ is not None for _ in collectiterres]):
                        self.cachesetatend(contentsolved, "".join(collectiterres))
            except Exception as e:
                if self.using and globalconfig["showtranexception"]:
                    if isinstance(e, ArgsEmptyExc):
                        msg = str(e)
                    elif isinstance(e, TimeOut):
                        # 更改了timeout机制。timeout只会发生在队列非空时，故直接放弃
                        continue
                    else:
                        print_exc()
                        msg = stringfyerror(e)
                        self.needreinit = True
                    msg = "<msg_translator>" + msg

                    callback(msg, embedcallback, False)
