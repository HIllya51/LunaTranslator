from network.server.tcpservice import (
    WSHandler,
    HTTPHandler,
    FileResponse,
    TCPService,
    RequestInfo,
    RedirectResponse,
    ResponseWithHeader,
)
from sometypes import TranslateResult, TranslateError, WordSegResult
from urllib.parse import urlencode
import json, gobject, base64
from myutils.ocrutil import ocr_run
from gui.rendertext.webview import TextBrowser, somecommon as somecommon_1
from gui.transhist import somecommon as somecommon_2, wvtranshist
from network.server.servicecollection_1 import (
    mainuiwsoutputsave,
    transhistwsoutputsave,
    wsoutputsave,
)
import threading, functools
from qtsymbols import *
from myutils.config import globalconfig, _TR
from myutils.utils import dynamiccishuname, dynamicapiname
from tts.basettsclass import TTSResult


class internalservicetranshistws(WSHandler, somecommon_2):
    path = "/__internalservice/transhistws"

    def parse(self, info):
        transhistwsoutputsave.append(self)

    def onmessage(self, message: str):
        message: dict = json.loads(message)
        function = message["function"]
        args = message.get("args", tuple())
        dict(calllunaloadready=self.calllunaloadready)[function](*args)

    def debugeval(self, js: str):
        self.send_text(js)


class Pagetranshist(HTTPHandler):
    path = "/page/transhist"

    def parse(self, _):
        return FileResponse(wvtranshist.loadex_())


class internalservicemainuiws(WSHandler, somecommon_1):
    path = "/__internalservice/mainuiws"

    def __init__(self, info, sock):
        super().__init__(info, sock)
        somecommon_1.__init__(self)

    def parse(self, info):
        mainuiwsoutputsave.append(self)

    def onmessage(self, message: str):
        message: dict = json.loads(message)
        function = message["function"]
        args = message.get("args", tuple())
        dict(
            calllunaloadready=self.calllunaloadready,
            calllunaclickedword=gobject.baseobject.clickwordcallback,
        )[function](*args)

    def debugeval(self, js: str):
        self.send_text(js)

    def refreshcontent(self):
        traces = gobject.baseobject.translation_ui.translate_text.trace.copy()
        self.clear()
        for t, trace in traces:
            if t == 0:
                self.append(*trace)
            elif t == 1:
                self.iter_append(*trace)


class PageSearchWord(HTTPHandler):
    path = "/page/dictionary"

    def parse(self, _: RequestInfo):
        page = r"LunaTranslator\htmlcode\service\dictionary.html"
        if not _.query.get("word"):
            return FileResponse(page)
        word = WordSegResult.from_dict(_.query)
        if not word._prototype:
            return FileResponse(page)
        wordwhich = lambda key: (word.word, word.prototype)[
            globalconfig["usewordoriginfor"].get(
                key, globalconfig.get("usewordorigin", False)
            )
        ]
        word = wordwhich("searchword")
        if word:
            __ = _.query.copy()
            __.update(word=word)
            if "prototype" in __:
                __.pop("prototype")
            return RedirectResponse(r"/page/dictionary?" + urlencode(__))
        else:
            return FileResponse(page)


class Pagetranslate(HTTPHandler):
    path = "/page/translate"

    def parse(self, _: RequestInfo):
        page = r"LunaTranslator\htmlcode\service\translate.html"
        return FileResponse(page)


class APImecab(HTTPHandler):
    path = "/api/mecab"

    def parse(self, _: RequestInfo):
        text = _.query.get("text")
        if not text:
            raise Exception()
        return tuple(_.as_dict() for _ in gobject.baseobject.parsehira(text))


class APItts(HTTPHandler):
    path = "/api/tts"

    def parse(self, _: RequestInfo):
        text = _.query.get("text")
        if not text:
            raise Exception()
        ret: "list[TTSResult]" = []
        sema = threading.Semaphore(0)
        gobject.baseobject.reader.ttscallback(
            text,
            functools.partial(self.callbacktts, sema, ret),
        )
        sema.acquire()
        if ret[0].error:
            return {"error": ret[0].error}
        return ResponseWithHeader(
            data=ret[0].data, headers={"content-type": ret[0].mime}
        )

    def callbacktts(self, sema: threading.Semaphore, ret: list, result: TTSResult):
        ret.append(result)
        sema.release()


class APIocr(HTTPHandler):
    path = "/api/ocr"
    method = "POST"

    def parse(self, _: RequestInfo):
        image = _.body.json.get("image")
        if not image:
            raise Exception()
        img = base64.b64decode(image)
        qi = QImage()
        qi.loadFromData(img)
        if qi.isNull():
            raise Exception()
        result = ocr_run(qi)
        return result.json


class APITranslators(HTTPHandler):
    path = "/api/list/translator"

    def parse(self, _: RequestInfo):
        res = []
        for engine in globalconfig["fix_translate_rank_rank"]:
            if engine not in gobject.baseobject.translators:
                continue
            res.append(dict(id=engine, name=_TR(dynamicapiname(engine))))
        return res


class APIdicts(HTTPHandler):
    path = "/api/list/dictionary"

    def parse(self, _: RequestInfo):
        res = []
        for engine in globalconfig["cishuvisrank"]:
            if engine not in gobject.baseobject.cishus:
                continue
            res.append(dict(id=engine, name=_TR(dynamiccishuname(engine))))
        return res


class APITranslate(HTTPHandler):
    path = "/api/translate"

    def parse(self, _: RequestInfo):
        text = _.query.get("text")
        if not text:
            raise Exception()
        tsid = _.query.get("id")

        ret = []
        error = []
        sema = threading.Semaphore(0)
        gobject.baseobject.textgetmethod(
            text,
            False,
            waitforresultcallback=functools.partial(self.__notify, sema, ret),
            waitforresultcallbackengine=tsid,
            waitforresultcallbackengine_force=True,
            erroroutput=error.append,
        )
        sema.acquire()
        if error:
            error: TranslateError = error[0]
            err = dict(error=error.message)
            if error.id:
                err.update(name=_TR(dynamicapiname(error.id)), id=error.id)
            return err
        result: TranslateResult = ret[0]
        if not result:
            return {}
        return dict(
            name=_TR(dynamicapiname(result.id)), result=result.result, id=result.id
        )

    def __notify(self, sema: threading.Semaphore, ret: list, result):
        ret.append(result)
        sema.release()


class APISearchWord(HTTPHandler):
    path = "/api/dictionary"

    def iterhelper(self, word):
        cnt = 0
        ret = []
        sema = threading.Semaphore(0)
        for k, cishu in gobject.baseobject.cishus.items():
            cnt += 1
            cishu.safesearch(functools.partial(self.__notify, k, sema, ret), word)
        for _ in range(cnt):
            sema.acquire()
            k, result = ret[_]
            if not result:
                continue
            yield dict(name=_TR(dynamiccishuname(k)), result=result, id=k)

    def parse(self, _: RequestInfo):
        word = _.query.get("word")
        if not word:
            raise Exception()
        dictid = _.query.get("id")
        if not dictid:
            return self.iterhelper(word)

        cishu = gobject.baseobject.cishus.get(dictid)
        if not cishu:
            return {}
        ret = []
        sema = threading.Semaphore(0)
        cishu.safesearch(functools.partial(self.__notify, dictid, sema, ret), word)
        sema.acquire()
        k, result = ret[0]
        if not result:
            return {}
        return dict(name=_TR(dynamiccishuname(k)), result=result, id=k)

    def __notify(self, k, sema: threading.Semaphore, ret: list, result):
        ret.append((k, result))
        sema.release()


class PageMainui(HTTPHandler):
    path = "/page/mainui"

    def parse(self, _):
        return FileResponse(TextBrowser.loadex_())


class Pageocr(HTTPHandler):
    path = "/page/ocr"

    def parse(self, _):
        page = r"LunaTranslator\htmlcode\service\ocr.html"
        return FileResponse(page)


class TextOutputOrigin(WSHandler):
    path = "/api/ws/text/origin"

    def parse(self, _):
        wsoutputsave.append(self)


class TextOutputTrans(WSHandler):
    path = "/api/ws/text/trans"

    def parse(self, _):
        wsoutputsave.append(self)


class BasePage(HTTPHandler):
    path = "/"

    def parse(self, _):
        return FileResponse(r"LunaTranslator\htmlcode\service\basepage.html")


def registerall(service: TCPService):
    service.register(BasePage)
    service.register(APISearchWord)
    service.register(APImecab)
    service.register(APITranslators)
    service.register(APIdicts)
    service.register(APItts)
    service.register(APIocr)
    service.register(APITranslate)
    service.register(PageSearchWord)
    service.register(Pagetranslate)
    service.register(Pageocr)
    service.register(PageMainui)
    service.register(internalservicemainuiws)
    service.register(Pagetranshist)
    service.register(internalservicetranshistws)
    service.register(TextOutputOrigin)
    service.register(TextOutputTrans)
