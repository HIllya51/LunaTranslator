from textio.textoutput.outputerbase import Base
from myutils.config import globalconfig
import NativeUtils


class Outputer(Base):
    def dispatch(self, text: str, isorigin: bool):
        if not (
            (isorigin and self.config["origin"])
            or ((not isorigin) and self.config["trans"])
        ):
            return
        if globalconfig["sourcestatus2"]["copy"]["use"] and (
            not globalconfig["excule_from_self"]
        ):
            return

        NativeUtils.ClipBoard.text = text
