from textoutput.outputerbase import Base
from network.tcpservice import WSHandler, RequestInfo, WSForEach
import gobject
from typing import List

wsoutputsave: List[WSHandler] = []


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
        def __(handle):
            if isorigin and isinstance(handle, TextOutputOrigin):
                handle.send_text(text)
            elif (not isorigin) and isinstance(handle, TextOutputTrans):
                handle.send_text(text)

        WSForEach(wsoutputsave, __)
