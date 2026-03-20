from textio.textoutput.outputerbase import Base
import NativeUtils


class Outputer(Base):
    def dispatch(self, text: str, isorigin: bool):
        if not (
            (isorigin and self.config["origin"])
            or ((not isorigin) and self.config["trans"])
        ):
            return

        NativeUtils.ClipBoard.text = text
