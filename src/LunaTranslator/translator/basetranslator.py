from traceback import print_exc
from queue import Queue
from threading import Thread
import time, types
import zhconv, gobject
import sqlite3, json
import functools
from myutils.config import globalconfig, translatorsetting
from myutils.utils import stringfyerror, autosql, PriorityQueue, SafeFormatter
from myutils.commonbase import ArgsEmptyExc, commonbase
from myutils.languageguesser import guess


class Interrupted(Exception):
    pass


class Threadwithresult(Thread):
    def __init__(self, func):
        super(Threadwithresult, self).__init__()
        self.func = func
        self.isInterrupted = True
        self.exception = None

    def run(self):
        try:
            self.result = self.func()
        except Exception as e:
            self.exception = e
        self.isInterrupted = False

    def get_result(self, checktutukufunction=None):
        # Thread.join(self,timeout)
        # 不再超时等待，只检查是否是最后一个请求，若是则无限等待，否则立即放弃。
        while checktutukufunction and checktutukufunction() and self.isInterrupted:
            Thread.join(self, 0.1)

        if self.isInterrupted:
            raise Interrupted()
        elif self.exception:
            raise self.exception
        else:
            return self.result


def timeoutfunction(func, checktutukufunction=None):
    t = Threadwithresult(func)
    t.start()
    return t.get_result(checktutukufunction)


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

    def parse_maybe_autolang(self, content):
        if self.srclang != "auto":
            return self.srclang
        gs = guess(content)
        return self.langmap_.get(gs, gs)

    ############################################################
    _globalconfig_key = "fanyi"
    _setting_dict = translatorsetting
    using_gpt_dict = False

    def level2init(self):
        if (self.transtype == "offline") and (not self.is_gpt_like):
            globalconfig["fanyi"][self.typename]["useproxy"] = False
        self.multiapikeycurrentidx = -1
        self.queue = PriorityQueue()
        self.sqlqueue = None
        try:
            self._private_init()
        except Exception as e:
            gobject.baseobject.displayinfomessage(
                globalconfig["fanyi"][self.typename]["name"]
                + " init translator failed : "
                + str(stringfyerror(e)),
                "<msg_error_not_refresh>",
            )
            print_exc()

        self.lastrequesttime = 0
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
                    (self.srclang_1, self.tgtlang_1, src),
                )
                self.sqlwrite2.execute(
                    "INSERT into cache VALUES(?,?,?,?)",
                    (self.srclang_1, self.tgtlang_1, src, trans),
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
        return self.tgtlang_1 == "cht" and "cht" not in self.langmap()

    @property
    def using(self):
        return globalconfig["fanyi"][self.typename]["use"]

    @property
    def transtype(self):
        # free/dev/api/offline/pre
        # dev/offline/pre 无视请求间隔
        # pre不使用翻译缓存
        # offline不被新的请求打断
        return globalconfig["fanyi"][self.typename].get("type", "free")

    def gettask(self, content):
        # fmt: off
        callback, contentsolved, callback, is_auto_run, optimization_params = content
        # fmt: on
        if callback:
            priority = 1
        else:
            priority = 0
        self.queue.put(content, priority)

    def longtermcacheget(self, src):
        try:
            ret = self.sqlwrite2.execute(
                "SELECT trans FROM cache WHERE (((srclang,tgtlang)=(?,?) or (srclang,tgtlang)=(?,?)) and (source= ?))",
                (self.srclang_1, self.tgtlang_1, self.srclang, self.tgtlang, src),
            ).fetchone()
            if ret:
                return ret[0]
            return None
        except:
            return None

    def longtermcacheset(self, src, tgt):
        self.sqlqueue.put((src, tgt))

    def shorttermcacheget(self, src):
        langkey = (self.srclang_1, self.tgtlang_1)
        if langkey not in self._cache:
            self._cache[langkey] = {}
        try:
            return self._cache[langkey][src]
        except KeyError:
            return None

    def shorttermcacheset(self, src, tgt):
        langkey = (self.srclang_1, self.tgtlang_1)

        if langkey not in self._cache:
            self._cache[langkey] = {}
        self._cache[langkey][src] = tgt

    def shortorlongcacheget(self, content, is_auto_run):
        # 除了预翻译不使用翻译缓存，以及手动触发gpt翻译外，其他不管什么翻译都缓存下来。
        if self.is_gpt_like and not is_auto_run:
            return None
        if self.transtype == "pre":
            return None
        res = self.shorttermcacheget(content)
        if res:
            return res
        if not globalconfig["uselongtermcache"]:
            return None
        res = self.longtermcacheget(content)
        if res:
            return res
        return None

    def maybecachetranslate(self, contentsolved, is_auto_run):
        res = self.shortorlongcacheget(contentsolved, is_auto_run)
        if res:
            return res
        return self.intervaledtranslate(contentsolved)

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

    def _gptlike_createquery(self, query, usekey, tempk):
        user_prompt = (
            self.config.get(tempk, "") if self.config.get(usekey, False) else ""
        )
        fmt = SafeFormatter()
        return fmt.format(user_prompt, must_exists="sentence", sentence=query)

    def _gptlike_createsys(self, usekey, tempk):

        fmt = SafeFormatter()
        if self.config[usekey]:
            template = self.config[tempk]
        else:
            template = "You are a translator. Please help me translate the following {srclang} text into {tgtlang}, and you should only tell me the translation."
        return fmt.format(template, srclang=self.srclang, tgtlang=self.tgtlang)

    def _gptlike_create_prefill(self, usekey, tempk):
        user_prompt = (
            self.config.get(tempk, "") if self.config.get(usekey, False) else ""
        )
        return user_prompt

    def _gpt_common_parse_context(self, messages: list, context: list, num: int):

        for _i in range(min(len(context) // 2, num)):
            i = len(context) // 2 - min(len(context) // 2, num) + _i
            messages.append(context[i * 2])
            messages.append(context[i * 2 + 1])

    def reinitandtrans(self, contentsolved, is_auto_run):
        if self.needreinit or self.initok == False:
            self.needreinit = False
            self.renewsesion()
            try:
                self._private_init()
            except Exception as e:
                raise Exception("init translator failed : " + str(stringfyerror(e)))
        return self.maybecachetranslate(contentsolved, is_auto_run)

    def translate_and_collect(
        self,
        contentsolved,
        is_auto_run,
        callback,
    ):
        def __maybeshow(callback, res, is_iter_res):

            if self.needzhconv:
                res = zhconv.convert(res, "zh-tw")
            callback(res, is_iter_res)

        callback = functools.partial(__maybeshow, callback)

        res = self.reinitandtrans(contentsolved, is_auto_run)
        # 不能因为被打断而放弃后面的操作，发出的请求不会因为不再处理而无效，所以与其浪费不如存下来
        # gettranslationcallback里已经有了是否为当前请求的校验，这里无脑输出就行了
        if isinstance(res, types.GeneratorType):
            collectiterres = ""
            for _res in res:
                if _res == "\0":
                    collectiterres = ""
                else:
                    collectiterres += _res
                callback(collectiterres, 1)
            callback(collectiterres, 2)
            res = collectiterres

        else:
            if globalconfig["fix_translate_rank"]:
                # 这个性能会稍微差一点，不然其实可以全都这样的。
                callback(res, 1)
                callback(res, 2)
            else:
                callback(res, 0)

        # 保存缓存
        # 不管是否使用翻译缓存，都存下来
        if self.transtype == "pre":
            return
        self.shorttermcacheset(contentsolved, res)
        self.longtermcacheset(contentsolved, res)

    def _fythread(self):
        self.needreinit = False
        while self.using:

            content = self.queue.get()
            if not self.using:
                break
            if content is None:
                break
            # fmt: off
            callback, contentsolved, waitforresultcallback, is_auto_run, optimization_params = content
            # fmt: on
            if self.onlymanual and is_auto_run:
                continue
            if self.srclang_1 == self.tgtlang_1:
                callback(contentsolved, 0)
                continue
            try:
                checktutukufunction = (
                    lambda: ((waitforresultcallback is not None) or self.queue.empty())
                    and self.using
                )
                if not checktutukufunction():
                    # 检查请求队列是否空，请求队列有新的请求，则放弃当前请求。但对于内嵌翻译请求，不可以放弃。
                    continue
                if self.transtype == "pre" or self.using_gpt_dict:
                    gpt_dict = None
                    contentraw = contentsolved
                    for _ in optimization_params:
                        if isinstance(_, dict):
                            _gpt_dict = _.get("gpt_dict", None)
                            if _gpt_dict is None:
                                continue
                            gpt_dict = _gpt_dict
                            contentraw = _.get("gpt_dict_origin")

                    contentsolved = json.dumps(
                        {
                            "text": contentsolved,
                            "gpt_dict": gpt_dict,
                            "contentraw": contentraw,
                        }
                    )

                func = functools.partial(
                    self.translate_and_collect,
                    contentsolved,
                    is_auto_run,
                    callback,
                )
                if self.transtype == "offline":
                    # 离线翻译例如sakura不要被中断，因为即使中断了，部署的服务仍然在运行，直到请求结束
                    func()
                else:
                    timeoutfunction(
                        func,
                        checktutukufunction=checktutukufunction,
                    )
            except Exception as e:
                if not (self.using and globalconfig["showtranexception"]):
                    continue
                if isinstance(e, ArgsEmptyExc):
                    msg = str(e)
                elif isinstance(e, Interrupted):
                    # 因为有新的请求而被打断
                    continue
                else:
                    print_exc()
                    msg = stringfyerror(e)
                    self.needreinit = True
                callback(msg, 0, True)
