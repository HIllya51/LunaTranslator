import gobject
from myutils.config import _TR
from qtsymbols import *


class LLabel(QLabel):
    def __init__(self, *argc):
        self.__s = None
        self._ToolTip = None
        self._acc = None
        if len(argc) == 1:
            if isinstance(argc[0], str):
                self.__s = argc[0]
                argc = (_TR(argc[0]),)
        elif len(argc) == 2:
            self.__s = argc[0]
            argc = _TR(argc[0]), argc[1]
        super().__init__(*argc)

    def setText(self, s):
        self.__s = s
        super().setText(_TR(self.__s))

    def updatelangtext(self):
        if self.__s:
            super().setText(_TR(self.__s))
        if self._ToolTip:
            super().setToolTip(_TR(self._ToolTip))
        if self._acc:
            super().setAccessibleName(_TR(self._acc))

    def setToolTip(self, t):
        self._ToolTip = t
        super().setToolTip(_TR(t))

    def setAccessibleName(self, t):
        self._acc = t
        super().setAccessibleName(_TR(t))


class LPushButton(QPushButton):
    def __init__(self, *argc):
        self._text = None
        self._ToolTip = None
        if len(argc) == 1:

            if isinstance(argc[0], str):
                self._text = argc[0]
                argc = (_TR(argc[0]),)
        super().__init__(*argc)

    def setText(self, t):
        self._text = t
        super().setText(_TR(t))

    def updatelangtext(self):
        if self._text:
            super().setText(_TR(self._text))
        if self._ToolTip:
            super().setToolTip(_TR(self._ToolTip))

    def setToolTip(self, t):
        self._ToolTip = t
        super().setToolTip(_TR(t))


class LAction(QAction):
    def updatelangtext(self):
        if self._text:
            self.setText(_TR(self._text))

    def __init__(self, *argc, **kwargv):
        self._text = None
        newarg = []
        for arg in argc:
            if isinstance(arg, str):
                self._text = arg
                newarg.append(_TR(arg))
            else:
                newarg.append((arg))
        super().__init__(*newarg, **kwargv)


class LCheckBox(QCheckBox):
    def __init__(self, text):
        super().__init__(_TR(text))
        self._text = text

    def updatelangtext(self):
        if self._text:
            super().setText(_TR(self._text))


class LGroupBox(QGroupBox):

    def __init__(self, *argc, **kwarg):
        super().__init__(*argc, **kwarg)
        self._text = None

    def setTitle(self, t):
        self._text = t
        super().setTitle(_TR(self._text))

    def updatelangtext(self):
        if self._text:
            super().setTitle(_TR(self._text))


class LListWidgetItem(QListWidgetItem):
    def __init__(self, text):
        self.__text = text
        super().__init__(_TR(text))

    def updatelangtext(self):
        self.setText(_TR(self.__text))


class LListWidget(QListWidget):
    def updatelangtext(self):
        for i in range(self.count()):
            item = self.item(i)
            if isinstance(item, LListWidgetItem):
                item.updatelangtext()

    def wheelEvent(self, e: QWheelEvent) -> None:
        self.setCurrentRow(
            (self.currentRow() + [-1, 1][e.angleDelta().y() < 0] + self.count())
            % self.count()
        )
        return super().wheelEvent(e)


class LFormLayout(QFormLayout):
    def addRow(self, *argc):
        if len(argc) == 2:
            text, widget = argc
            if isinstance(text, str):
                text = LLabel(text)
                argc = text, widget
        super().addRow(*argc)

    def insertRow(self, row, *argc):
        if len(argc) == 2:
            text, widget = argc
            if isinstance(text, str):
                text = LLabel(text)
                argc = text, widget
        super().insertRow(row, *argc)


traceonepostion = {}


class LDialog(QDialog):
    def moveEvent(self, e):
        traceonepostion[self.parent()] = self.pos()

    def __init__(self, *argc, **kwarg):
        super().__init__(*argc, **kwarg)
        if self.parent() == gobject.base.commonstylebase:
            if traceonepostion.get(self.parent(), None):
                self.move(traceonepostion.get(self.parent(), None))
        self._title = None

    def setWindowTitle(self, t):
        self._title = t
        super().setWindowTitle(_TR(t))

    def updatelangtext(self):
        if self._title:
            super().setWindowTitle(_TR(self._title))


class LMainWindow(QMainWindow):

    def __init__(self, *argc, **kwarg):
        QMainWindow.__init__(self, *argc, **kwarg)
        self._title = None

    def setWindowTitle(self, t):
        self._title = t
        super().setWindowTitle(_TR(t))

    def updatelangtext(self):
        if self._title:
            super().setWindowTitle(_TR(self._title))


class LRadioButton(QRadioButton):
    def __init__(self, t):
        self.__t = t
        super().__init__(_TR(t))

    def updatelangtext(self):
        self.setText(_TR(self.__t))


class LTabBar(QTabBar):
    def __init__(self, *argc, **kwarg):
        super().__init__(*argc, **kwarg)
        self.__titles = []

    def insertTab(self, idx, t):
        self.__titles.insert(idx, t)
        super().insertTab(idx, _TR(t))

    def removeTab(self, i):
        self.__titles.pop(i)
        super().removeTab(i)

    def addTab(self, t):
        self.__titles.append(t)
        super().addTab(_TR(t))

    def updatelangtext(self):
        for i in range(self.count()):
            self.setTabText(i, _TR(self.__titles[i]))


class LTabWidget(QTabWidget):
    def __init__(self, *argc, **kwarg):
        super().__init__(*argc, **kwarg)
        self.__titles = []

    def addTab(self, w, t):
        self.__titles.append(t)
        super().addTab(w, _TR(t))

    def updatelangtext(self):
        for i in range(self.count()):
            self.setTabText(i, _TR(self.__titles[i]))


class LStandardItemModel(QStandardItemModel):
    def __init__(self, *argc, **kwarg):
        super().__init__(*argc, **kwarg)
        self.__ls = []

    def setHorizontalHeaderLabels(self, ls: list):
        self.__ls = ls.copy()
        super().setHorizontalHeaderLabels(_TR(ls))

    def updatelangtext(self):
        if self.__ls:
            super().setHorizontalHeaderLabels(_TR(self.__ls))

    def insertColumn(self, column: int, items):
        self.__ls.insert(column, "")
        super().insertColumn(column, items)

    def removeColumn(self, col):
        self.__ls.pop(col)
        super().removeColumn(col)


class IconToolButton(QToolButton):
    def __init__(self, *argc, **kwarg):
        super().__init__(*argc, **kwarg)
        self.__resizedirect()

    def event(self, e):
        if e.type() == QEvent.Type.FontChange:
            self.__resizedirect()
        return super().event(e)

    def __resizedirect(self):
        h = QFontMetricsF(self.font()).ascent()
        sz = QSizeF(h, h).toSize()
        self.setIconSize(sz)


class LToolButton(IconToolButton):
    def __init__(self, *argc, **kwarg):
        super().__init__(*argc, **kwarg)
        self._text = self.text()
        super().setText(_TR(self._text))

    def setText(self, t):
        self._text = t
        super().setText(_TR(t))

    def updatelangtext(self):
        if self._text:
            super().setText(_TR(self._text))
