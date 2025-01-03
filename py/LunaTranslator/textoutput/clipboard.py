from textoutput.outputerbase import Base
from myutils.config import globalconfig
import gobject
from qtsymbols import *


class Outputer(Base):
    def dispatch(self, text):
        if globalconfig["sourcestatus2"]["copy"]["use"] and (
            not globalconfig["excule_from_self"]
        ):
            return
        gobject.baseobject.clipboardhelper.setText.emit(text)
