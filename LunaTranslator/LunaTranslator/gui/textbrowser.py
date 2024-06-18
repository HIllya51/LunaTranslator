from qtsymbols import *
from myutils.config import globalconfig
import importlib


class Textbrowser(QLabel):
    contentsChanged = pyqtSignal(QSize)

    _padding = 10

    def __makeborder(self, size: QSize):
        _padding = self._padding
        self.masklabel_right.move(self.width() - _padding, 0)
        self.masklabel_bottom.move(0, 0 + size.height() - _padding)
        self.masklabel_left.resize(_padding, size.height())
        self.masklabel_right.resize(_padding, size.height())
        self.masklabel_bottom.resize(size.width(), _padding)

    def resizeEvent(self, event: QResizeEvent):
        _padding = self._padding
        self.textbrowser.setGeometry(
            _padding,
            0,
            event.size().width() - 2 * _padding,
            event.size().height() - _padding,
        )
        self.__makeborder(event.size())

    def _contentsChanged(self, size: QSize):
        self.contentsChanged.emit(QSize(size.width(), size.height()))

    def loadinternal(self):
        tb = importlib.import_module(
            f'rendertext.{globalconfig["rendertext_using"]}'
        ).TextBrowser

        self.textbrowser = tb(self)
        self.textbrowser.setMouseTracking(True)
        self.textbrowser.contentsChanged.connect(self._contentsChanged)

    def __init__(self, parent):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.cleared = True
        self.loadinternal()
        self.masklabel_left = QLabel(self)
        self.masklabel_left.setMouseTracking(True)
        # self.masklabel_left.setStyleSheet('background-color:red')
        self.masklabel_right = QLabel(self)
        # self.masklabel_right.setStyleSheet('background-color:red')
        self.masklabel_right.setMouseTracking(True)
        self.masklabel_bottom = QLabel(self)
        self.masklabel_bottom.setMouseTracking(True)
        # self.masklabel_bottom.setStyleSheet('background-color:red')
        self.setselectable()

    def setselectable(self):
        self.textbrowser.setselectable(globalconfig["selectable"])

    def iter_append(self, iter_context_class, origin, atcenter, text, color):
        cleared = self.cleared
        self.cleared = False
        self.textbrowser.iter_append(
            iter_context_class, origin, atcenter, text, color, cleared
        )

    def append(self, origin, atcenter, text, tag, flags, color):
        cleared = self.cleared
        self.cleared = False
        self.textbrowser.append(origin, atcenter, text, tag, flags, color, cleared)

    def clear(self):
        self.cleared = True
        self.textbrowser.clear()
