from services.tcpservice import (
    WSHandler,
    HTTPHandler,
    FileResponse,
    TCPService,
    RequestInfo,
    RedirectResponse,
)
from urllib.parse import quote
import json, gobject, re, os
from rendertext.webview import TextBrowser, somecommon as somecommon_1
from gui.transhist import somecommon as somecommon_2, wvtranshist
from services.servicecollection_1 import (
    mainuiwsoutputsave,
    transhistwsoutputsave,
    wsoutputsave,
)
import threading, functools
from myutils.config import globalconfig
from myutils.utils import dynamiccishuname


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


class PageSearchWord(HTTPHandler):
    path = re.compile(r"/page/searchword(\?.*)?")

    def parse(self, _: RequestInfo):
        page = os.path.join(os.path.dirname(__file__), "pagesearchword.html")
        if _.query.get("word"):
            return FileResponse(page)

        if globalconfig["usewordorigin"] == False:
            word = _.query.get("orig")
        else:
            word = _.query.get("origorig", word.get("orig"))
        if word:
            return RedirectResponse(r"/page/searchword?word=" + quote(word))
        else:
            return FileResponse(page)


class APISearchWord(HTTPHandler):
    path = re.compile(r"/api/searchword(\?.*)?")

    def parse(self, _: RequestInfo):
        word = _.query.get("word")
        if not word:
            raise Exception("")
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
            yield dict(name=dynamiccishuname(k), result=result)

    def __notify(self, k, sema: threading.Semaphore, ret: list, result):
        ret.append((k, result))
        sema.release()


class PageMainui(HTTPHandler):
    path = "/page/mainui"

    def parse(self, _):
        return FileResponse(TextBrowser.loadex_())


class TextOutputOrigin(WSHandler):
    path = "/text_origin"

    def parse(self, _):
        wsoutputsave.append(self)


class TextOutputTrans(WSHandler):
    path = "/text_trans"

    def parse(self, _):
        wsoutputsave.append(self)


def registerall(service: TCPService):

    service.register(APISearchWord)
    service.register(PageSearchWord)
    service.register(PageMainui)
    service.register(internalservicemainuiws)
    service.register(Pagetranshist)
    service.register(internalservicetranshistws)
    service.register(TextOutputOrigin)
    service.register(TextOutputTrans)
