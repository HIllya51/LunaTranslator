from textio.textoutput.outputerbase import Base
from network.server.servicecollection import TextOutputOrigin, TextOutputTrans
from network.server.servicecollection_1 import WSForEach, wsoutputsave


class Outputer(Base):

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
