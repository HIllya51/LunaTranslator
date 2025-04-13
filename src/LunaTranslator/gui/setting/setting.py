from qtsymbols import *
import functools
import qtawesome
from myutils.config import globalconfig
from gui.usefulwidget import closeashidewindow, makesubtab_lazy
from gui.setting.textinput import setTabOne_lazy
from gui.setting.translate import setTabTwo_lazy
from gui.setting.display import setTabThree_lazy
from gui.setting.tts import setTab5, showvoicelist
from gui.setting.cishu import setTabcishu
from gui.setting.hotkey import setTab_quick, registrhotkeys
from gui.setting.proxy import setTab_proxy
from gui.setting.transopti import setTab7_lazy, delaysetcomparetext
from gui.setting.about import (
    setTab_about,
    versionlabelmaybesettext,
    versioncheckthread,
)
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
        if self.__first:
            self.__first = False
            return
        globalconfig["isopensettingfirsttime1"] = idx

    def __init__(self, parent=None):
        super(TabWidget, self).__init__(parent)
        layout = QHBoxLayout(self)
        self.__first = True
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
        self.idx = 0
        self.titles = []

    def addTab(self, widget, title):
        self.titles.append(title)
        self.tab_widget.addTab(widget, title)
        item = LListWidgetItem(title)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.list_widget.addItem(item)
        if self.idx == 0:
            self.list_widget.setCurrentRow(0)
        self.idx += 1

    def currentWidget(self):
        return self.tab_widget.currentWidget()


class Setting(closeashidewindow):
    voicelistsignal = pyqtSignal(object)
    versiontextsignal = pyqtSignal(str)
    progresssignal2 = pyqtSignal(str, int)
    progresssignal4 = pyqtSignal(str, int)
    progresssignal3 = pyqtSignal(int)
    showandsolvesig = pyqtSignal(str, str)
    safeinvokefunction = pyqtSignal(list)
    thresholdsett2 = pyqtSignal(str)
    thresholdsett1 = pyqtSignal(str)

    def _progresssignal4(self, text, val):
        try:
            self.downloadprogress.setValue(val)
            self.downloadprogress.setFormat(text)
            if val or text:
                self.updatelayout.setRowVisible(1, True)
        except:
            self.downloadprogress_cache = text, val

    def __init__(self, parent):
        super(Setting, self).__init__(parent, globalconfig["setting_geo_2"])
        self.setWindowIcon(qtawesome.icon("fa.gear"))
        self.safeinvokefunction.connect(lambda _: _[0]())
        self.progresssignal4.connect(self._progresssignal4)
        self.showandsolvesig.connect(functools.partial(delaysetcomparetext, self))
        self.voicelistsignal.connect(functools.partial(showvoicelist, self))
        self.versiontextsignal.connect(
            functools.partial(versionlabelmaybesettext, self)
        )
        self.isfirst = True
        versioncheckthread(self)
        registrhotkeys(self)

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
                "网络设置",
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
                functools.partial(setTab_proxy, self),
                functools.partial(setTab_about, self),
            ],
            klass=TabWidget,
            delay=True,
        )
        self.setCentralWidget(self.tab_widget)
        do()
        self.tab_widget.adjust_list_widget_width()
        last = self.tab_widget.list_widget.count() - 1
        if "isopensettingfirsttime1" not in globalconfig:
            globalconfig["isopensettingfirsttime1"] = last
        if globalconfig["isopensettingfirsttime1"] == last:
            self.tab_widget.setCurrentIndex(last)
