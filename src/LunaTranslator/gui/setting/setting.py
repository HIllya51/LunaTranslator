from qtsymbols import *
import functools
import qtawesome
import random, gobject
from myutils.config import globalconfig
from gui.usefulwidget import closeashidewindow, makesubtab_lazy
from gui.setting.textinput import setTabOne_lazy
from gui.setting.translate import setTabTwo_lazy
from gui.setting.display import setTabThree_lazy
from gui.setting.tts import setTab5
from gui.setting.cishu import setTabcishu
from gui.setting.hotkey import setTab_quick, registrhotkeys
from gui.setting.transopti import setTab7_lazy
from gui.setting.about import setTab_about
from gui.dynalang import LListWidgetItem, LListWidget


class TabWidget(QWidget):
    currentChanged = pyqtSignal(int)

    def adjust_list_widget_width(self):
        list_widget = self.list_widget
        font_metrics = list_widget.fontMetrics()
        max_width = 0
        for i in range(list_widget.count()):
            item = list_widget.item(i)
            width = font_metrics.size(
                0, item.text() + item.text()[0] + item.text()[-1]
            ).width()
            max_width = max(max_width, width)
            item.setSizeHint(QSize(0, int(font_metrics.ascent() * 2)))
        list_widget.setFixedWidth(max_width)

    def changeEvent(self, a0: QEvent):
        if a0.type() in (QEvent.Type.LanguageChange, QEvent.Type.FontChange):
            self.adjust_list_widget_width()
        return super().changeEvent(a0)

    def setCurrentIndex(self, idx):
        self.list_widget.setCurrentRow(idx)

    def __currentChanged(self, idx):
        self.tab_widget.setCurrentIndex(idx)

    def __init__(self, parent=None):
        super(TabWidget, self).__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.list_widget = LListWidget(self)
        self.list_widget.setStyleSheet(
            "QListWidget:focus {outline: 0px;} QListWidget {border: none;}"
        )
        self.tab_widget = QTabWidget(self)
        self.tab_widget.tabBar().hide()
        layout.addWidget(self.list_widget)
        layout.addWidget(self.tab_widget)
        self.currentChanged.connect(self.__currentChanged)
        self.list_widget.currentRowChanged.connect(self.currentChanged)
        self.titles = []

    def addTab(self, widget, title):
        self.titles.append(title)
        self.tab_widget.addTab(widget, title)
        item = LListWidgetItem(title)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.list_widget.addItem(item)

    def currentWidget(self):
        return self.tab_widget.currentWidget()


class Setting(closeashidewindow):

    def __init__(self, parent):
        super(Setting, self).__init__(parent, globalconfig["setting_geo_2"])
        self.setWindowIcon(qtawesome.icon("fa.gear"))
        self.isfirst = True
        registrhotkeys(self)
        gobject.base.settin_ui_showsignal.connect(self.showsignal)

    def showEvent(self, e: QShowEvent):
        if self.isfirst:
            self.isfirst = False
            self.firstshow()
        super().showEvent(e)

    def firstshow(self):

        self.setMinimumSize(100, 100)
        self.setWindowTitle("设置")

        self.tab_widget, do = makesubtab_lazy(
            [
                "核心设置",
                "翻译设置",
                "显示设置",
                "文本处理",
                "辞书设置",
                "语音合成",
                "快捷按键",
                "关于软件",
            ],
            [
                functools.partial(setTabOne_lazy, self),
                functools.partial(setTabTwo_lazy, self),
                functools.partial(setTabThree_lazy, self),
                functools.partial(setTab7_lazy, self),
                functools.partial(setTabcishu, self),
                functools.partial(setTab5, self),
                functools.partial(setTab_quick, self),
                functools.partial(setTab_about, self),
            ],
            klass=TabWidget,
            delay=True,
        )
        self.setCentralWidget(self.tab_widget)
        do()
        self.tab_widget.adjust_list_widget_width()
        last = self.tab_widget.list_widget.count() - 1
        self.tab_widget.setCurrentIndex(last)
