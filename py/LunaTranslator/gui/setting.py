from qtsymbols import *
import functools
import qtawesome
from myutils.config import globalconfig, _TRL
from gui.usefulwidget import closeashidewindow, makesubtab_lazy
from gui.setting_textinput import setTabOne_lazy
from gui.setting_translate import setTabTwo_lazy
from gui.setting_display import setTabThree_lazy
from gui.setting_tts import setTab5, showvoicelist
from gui.setting_cishu import setTabcishu
from gui.setting_hotkey import setTab_quick, registrhotkeys
from gui.setting_proxy import setTab_proxy
from gui.setting_transopti import setTab7_lazy, delaysetcomparetext
from gui.setting_about import (
    setTab_about,
    versionlabelmaybesettext,
    versioncheckthread,
)
from gui.dynalang import LListWidgetItem, LListWidget


class TabWidget(QWidget):
    currentChanged = pyqtSignal(int)

    def setCurrentIndex(self, idx):
        self.list_widget.setCurrentRow(idx)

    def __init__(self, parent=None):
        super(TabWidget, self).__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.splitter = QSplitter()
        layout.addWidget(self.splitter)
        self.list_widget = LListWidget(self)
        self.list_widget.setStyleSheet("QListWidget:focus {outline: 0px;}")
        self.tab_widget = QTabWidget(self)
        self.tab_widget.tabBar().hide()
        self.splitter.addWidget(self.list_widget)
        self.splitter.addWidget(self.tab_widget)
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)
        self.currentChanged.connect(
            self.tab_widget.setCurrentIndex
        )  # 监听 Tab 切换事件
        self.list_widget.currentRowChanged.connect(self.currentChanged)
        self.idx = 0
        self.titles = []

    def addTab(self, widget, title):
        self.titles.append(title)
        self.tab_widget.addTab(widget, title)
        item = LListWidgetItem(title)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        item.setSizeHint(QSize(self.tab_widget.width(), 50))
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
    progresssignal3 = pyqtSignal(int)
    showandsolvesig = pyqtSignal(str, str)

    def __init__(self, parent):
        super(Setting, self).__init__(parent, globalconfig["setting_geo_2"])
        self.setWindowIcon(qtawesome.icon("fa.gear"))

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

        if globalconfig.get("setting_split"):
            self.tab_widget.splitter.setSizes(globalconfig["setting_split"])
        else:
            width = 0
            fn = QFont()
            fn.setPointSizeF(globalconfig["settingfontsize"] + 4)
            fn.setFamily(globalconfig["settingfonttype"])
            fm = QFontMetrics(fn)
            for title in _TRL(self.tab_widget.titles):
                width = max(fm.size(0, title).width(), width)
            width += 50
            self.tab_widget.splitter.setSizes([width, self.tab_widget.width() - width])

        def __(_):
            globalconfig["setting_split"] = self.tab_widget.splitter.sizes()

        self.tab_widget.splitter.splitterMoved.connect(__)
