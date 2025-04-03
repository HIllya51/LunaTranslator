from textoutput.outputerbase import Base
from network.tcpservice import WSHandler, RequestInfo
import gobject

wsoutputsave: list[WSHandler] = []


class TextOutputOrigin(WSHandler):
    path = "/text_origin"

    def parse(self, _: RequestInfo):
        wsoutputsave.append(self)


class TextOutputTrans(WSHandler):
    path = "/text_trans"

    def parse(self, _: RequestInfo):
        wsoutputsave.append(self)


class Outputer(Base):
    def init(self):
        gobject.baseobject.service.register(TextOutputOrigin)
        gobject.baseobject.service.register(TextOutputTrans)

    @property
    def using(self):
        return bool(len(wsoutputsave))

    def dispatch(self, text: str, isorigin: bool):
        bad = []
        for handle in wsoutputsave:
            try:
                if isorigin and isinstance(handle, TextOutputOrigin):
                    handle.sendtext(text)
                elif (not isorigin) and isinstance(handle, TextOutputTrans):
                    handle.sendtext(text)
            except:
                bad.append(handle)
        for _ in bad:
            try:
                wsoutputsave.remove(_)
            except:
                pass
