from myutils.config import _TR
from qtsymbols import *
from elawidgettools import ElaWindow


class LElaWindow(ElaWindow):

    def __init__(self, *argc, **kwarg):
        ElaWindow.__init__(self, *argc, **kwarg)
        self._title = None

    def setWindowTitle(self, t):
        self._title = t
        super().setWindowTitle(_TR(t))

    def updatelangtext(self):
        if self._title:
            super().setWindowTitle(_TR(self._title))
