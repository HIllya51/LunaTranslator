from traceback import print_exc
from queue import Queue
from threading import Thread
import time, types
import gobject
import json
import functools
from myutils.config import globalconfig, translatorsetting
from myutils.utils import (
    stringfyerror,
    autosql,
    PriorityQueue,
    dynamicapiname,
)
from myutils.commonbase import ArgsEmptyExc, commonbase


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

    def init(self):
        pass

    def translate(self, content):
        return ""

    ############################################################
    _globalconfig_key = "fanyi"
    _setting_dict = translatorsetting
    using_gpt_dict = False
    _compatible_flag_is_sakura_less_than_5_52_3 = True

    def __init__(self, typename):
        super().__init__(typename)
        if (self.transtype == "offline") and (not self.is_gpt_like):
            globalconfig["fanyi"][self.typename]["useproxy"] = False
        self.queue = PriorityQueue()
        self.sqlqueue = None
        try:
            self._private_init()
        except Exception as e:
            gobject.baseobject.displayinfomessage(
                dynamicapiname(self.typename)
                + " init translator failed : "
                + str(stringfyerror(e)),
                "<msg_error_Translator>",
            )
            print_exc()

        self.lastrequesttime = 0
        self._cache = {}

        self.newline = None

        if self.transtype != "pre":
            try:

                self.sqlwrite2 = autosql(
                    gobject.gettranslationrecorddir(
                        "cache/{}.sqlite".format(self.typename)
                    ),
                    check_same_thread=False,
                    isolation_level=None,
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
        self.init()
        self.initok = True

    def _sqlitethread(self):
        while self.using:
            task = self.sqlqueue.get()
            if task is None:
                break
            try:
                src, trans = task
                self.sqlwrite2.execute(
                    "DELETE from cache WHERE (srclang=? and tgtlang=? and source=?)",
                    (str(self.srclang_1), str(self.tgtlang_1), src),
                )
                self.sqlwrite2.execute(
                    "INSERT into cache VALUES(?,?,?,?)",
                    (str(self.srclang_1), str(self.tgtlang_1), src, trans),
                )
            except:
                print_exc()

    @property
    def use_trans_cache(self):
        return globalconfig["fanyi"][self.typename].get("use_trans_cache", True)

    @property
    def is_gpt_like(self):
        return globalconfig["fanyi"][self.typename].get("is_gpt_like", False)

    @property
    def onlymanual(self):
        # Only used during manual translation, not used during automatic translation
        return globalconfig["fanyi"][self.typename].get("manual", False)

    @property
    def using(self):
        return globalconfig["fanyi"][self.typename]["use"]

    @property
    def transtype(self):
        # free/dev/api/offline/pre
        # dev/offline 无视请求间隔
        # pre全都有额外的处理，不走该pipeline，不使用翻译缓存
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
                "SELECT trans FROM cache WHERE (( (srclang=? and tgtlang=?) or  (srclang=? and tgtlang=?)) and source=?)",
                (
                    str(self.srclang_1),
                    str(self.tgtlang_1),
                    str(self.srclang),
                    str(self.tgtlang),
                    src,
                ),
            ).fetchone()
            if ret:
                return ret[0]
            return None
        except:
            print_exc()
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
        if self.is_gpt_like and not is_auto_run:
            return None
        if not self.use_trans_cache:
            return
        res = self.shorttermcacheget(content)
        if res:
            return res
        res = self.longtermcacheget(content)
        if res:
            return res
        return None

    def intervaledtranslate(self, content):
        interval = globalconfig["requestinterval"]
        current = time.time()
        self.current = current
        sleeptime = interval - (current - self.lastrequesttime)

        if sleeptime > 0:
            time.sleep(sleeptime)
        self.lastrequesttime = time.time()
        if (current != self.current) or (self.using == False):
            raise Exception()

        return self.multiapikeywrapper(self.translate)(content)

    def _gptlike_createquery(self, query, usekey, tempk):
        user_prompt = (
            self.config.get(tempk, "") if self.config.get(usekey, False) else ""
        )
        if "{sentence}" not in user_prompt:
            user_prompt += "{sentence}"
        return user_prompt.replace("{sentence}", query)

    def _gptlike_createsys(self, usekey, tempk):

        if self.config[usekey]:
            template = self.config[tempk]
        else:
            template = "You are a translator. Please help me translate the following {srclang} text into {tgtlang}. You should only tell me the translation result without any additional explanations."
        template = template.replace("{srclang}", self.srclang)
        template = template.replace("{tgtlang}", self.tgtlang)
        return template

    def _gptlike_create_prefill(self, usekey, tempk):
        user_prompt = (
            self.config.get(tempk, "") if self.config.get(usekey, False) else ""
        )
        return user_prompt

    def _gpt_common_parse_context(
        self, messages: list, context: "list[dict]", num: int, query=None, cachecontext=False
    ):
        offset = 0
        _i = 0
        msgs = []
        dedump = set([query])
        while (_i + offset < (len(context) // 2)) and (_i < num):
            i = len(context) // 2 - _i - offset - 1
            if isinstance(context[i * 2], dict):
                c_q: str = context[i * 2].get("content")
            else:
                c_q: str = context[i * 2]
            if (not cachecontext) and c_q and isinstance(c_q, str) and c_q in dedump:
                offset += 1
                continue
            dedump.add(c_q)
            msgs.append(context[i * 2 + 1])
            msgs.append(context[i * 2])
            _i += 1
        messages.extend(reversed(msgs))

    def maybeneedreinit(self):
        if not (self.needreinit or not self.initok):
            return
        self.needreinit = False
        self.renewsesion()
        try:
            self._private_init()
        except Exception as e:
            raise Exception("init translator failed : " + str(stringfyerror(e)))

    def maybezhconvwrapper(self, callback, tgtlang_1):
        def __maybeshow(callback, tgtlang_1, res, is_iter_res):
            if self.needzhconv:
                res = self.checklangzhconv(tgtlang_1, res)
            callback(res, is_iter_res)

        return functools.partial(__maybeshow, callback, tgtlang_1)

    def translate_and_collect(self, tgtlang_1, contentsolved, is_auto_run, callback):
        if isinstance(contentsolved, dict):
            if self._compatible_flag_is_sakura_less_than_5_52_3:
                query_use = json.dumps(contentsolved)
                cache_use = contentsolved["text"]
            else:
                query_use = contentsolved
                cache_use = contentsolved["contentraw"]
        else:
            cache_use = query_use = contentsolved

        res = self.shortorlongcacheget(cache_use, is_auto_run)
        if not res:
            res = self.intervaledtranslate(query_use)
        # 不能因为被打断而放弃后面的操作，发出的请求不会因为不再处理而无效，所以与其浪费不如存下来
        # gettranslationcallback里已经有了是否为当前请求的校验，这里无脑输出就行了

        callback = self.maybezhconvwrapper(callback, tgtlang_1)
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
        self.shorttermcacheset(cache_use, res)
        self.longtermcacheset(cache_use, res)

    def __parse_gpt_dict(self, contentsolved, optimization_params):
        gpt_dict = []
        contentraw = contentsolved
        for _ in optimization_params:
            if isinstance(_, dict):
                _gpt_dict = _.get("gpt_dict", None)
                if not _gpt_dict:
                    continue
                gpt_dict = _gpt_dict
                contentraw = _.get("gpt_dict_origin")
                break

        return {
            "text": contentsolved,
            "gpt_dict": gpt_dict,
            "contentraw": contentraw,
        }

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

                self.maybeneedreinit()

                if self.using_gpt_dict:
                    contentsolved = self.__parse_gpt_dict(
                        contentsolved, optimization_params
                    )

                func = functools.partial(
                    self.translate_and_collect,
                    self.tgtlang_1,
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
                if not (self.using):
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
