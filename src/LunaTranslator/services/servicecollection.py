from services.tcpservice import (
    WSHandler,
    HTTPHandler,
    FileResponse,
    TCPService,
    RequestInfo,
    RedirectResponse,
)
from sometypes import TranslateResult, TranslateError, WordSegResult
from urllib.parse import quote
import json, gobject, re, base64
from myutils.ocrutil import ocr_run
from gui.rendertext.webview import TextBrowser, somecommon as somecommon_1
from gui.transhist import somecommon as somecommon_2, wvtranshist
from services.servicecollection_1 import (
    mainuiwsoutputsave,
    transhistwsoutputsave,
    wsoutputsave,
)
import threading, functools
from qtsymbols import *
from myutils.config import globalconfig, _TR
from myutils.utils import dynamiccishuname, dynamicapiname


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
    path = re.compile(r"/page/searchword(\?.*)?")

    def parse(self, _: RequestInfo):
        page = r"files\html\service\searchword.html"
        if not _.query.get("word"):
            return FileResponse(page)
        seg = WordSegResult.from_dict(_.query)
        if not seg._prototype:
            return FileResponse(page)
        word = (seg.word, seg.prototype)[globalconfig["usewordorigin"]]
        if word:
            return RedirectResponse(r"/page/searchword?word=" + quote(word))
        else:
            return FileResponse(page)


class APImecab(HTTPHandler):
    path = re.compile(r"/api/mecab(\?.*)?")

    def parse(self, _: RequestInfo):
        text = _.query.get("text")
        if not text:
            raise Exception("")
        return tuple(_.as_dict() for _ in gobject.baseobject.parsehira(text))


class APItts(HTTPHandler):
    path = re.compile(r"/api/tts(\?.*)?")

    def parse(self, _: RequestInfo):
        text = _.query.get("text")
        if not text:
            raise Exception("")
        ret = []
        sema = threading.Semaphore(0)
        gobject.baseobject.reader.ttscallback(
            text,
            functools.partial(self.callbacktts, sema, ret),
        )
        sema.acquire()
        return ret[0]

    def callbacktts(self, sema: threading.Semaphore, ret: list, result):
        ret.append(result)
        sema.release()


class APIocr(HTTPHandler):
    path = re.compile(r"/api/ocr")
    method = "POST"

    def parse(self, _: RequestInfo):
        image = _.body.json.get("image")
        if not image:
            raise Exception("")
        img = base64.b64decode(image)
        qi = QImage()
        qi.loadFromData(img)
        if qi.isNull():
            raise Exception("")
        result = ocr_run(qi)
        return result.json


class APITranslate(HTTPHandler):
    path = re.compile(r"/api/translate(\?.*)?")

    def parse(self, _: RequestInfo):
        text = _.query.get("text")
        if not text:
            raise Exception("")
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
    path = re.compile(r"/api/searchword(\?.*)?")

    def iterhelper(self, word):
        cnt = 0
        ret = []
        sema = threading.Semaphore(0)
        for k, cishu in gobject.baseobject.cishus.items():
            cnt += 1
            cishu.safesearch(word, functools.partial(self.__notify, k, sema, ret))
        for _ in range(cnt):
            sema.acquire()
            k, result = ret[_]
            if not result:
                continue
            yield dict(name=_TR(dynamiccishuname(k)), result=result, id=k)

    def parse(self, _: RequestInfo):
        word = _.query.get("word")
        if not word:
            raise Exception("")
        dictid = _.query.get("id")
        if not dictid:
            return self.iterhelper(word)

        cishu = gobject.baseobject.cishus.get(dictid)
        if not cishu:
            return {}
        ret = []
        sema = threading.Semaphore(0)
        cishu.safesearch(word, functools.partial(self.__notify, dictid, sema, ret))
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
        return FileResponse(r"files\html\service\basepage.html")


def registerall(service: TCPService):
    service.register(BasePage)
    service.register(APISearchWord)
    service.register(APImecab)
    service.register(APItts)
    service.register(APIocr)
    service.register(APITranslate)
    service.register(PageSearchWord)
    service.register(PageMainui)
    service.register(internalservicemainuiws)
    service.register(Pagetranshist)
    service.register(internalservicetranshistws)
    service.register(TextOutputOrigin)
    service.register(TextOutputTrans)
