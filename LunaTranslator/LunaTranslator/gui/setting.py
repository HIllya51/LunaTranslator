from qtsymbols import *
import functools
import qtawesome
from myutils.config import globalconfig, _TR, _TRL
from myutils.utils import wavmp3player
from gui.usefulwidget import closeashidewindow, makesubtab_lazy
from gui.setting_textinput import setTabOne_lazy
from gui.setting_translate import setTabTwo_lazy, checkconnected
from gui.setting_display import setTabThree_lazy
from gui.setting_display_text import maybehavefontsizespin
from gui.setting_tts import setTab5, showvoicelist
from gui.setting_cishu import setTabcishu
from gui.setting_hotkey import setTab_quick, registrhotkeys
from gui.setting_lang import setTablang
from gui.setting_proxy import setTab_proxy
from gui.setting_transopti import setTab7_lazy, delaysetcomparetext
from gui.setting_about import (
    setTab_aboutlazy,
    setTab_update,
    versionlabelmaybesettext,
    updateprogress,
    versioncheckthread,
)


class TabWidget(QWidget):
    currentChanged = pyqtSignal(int)

    def setCurrentIndex(self, idx):
        self.list_widget.setCurrentRow(idx)

    def __init__(self, parent=None):
        super(TabWidget, self).__init__(parent)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)
        self.splitter = QSplitter()
        layout.addWidget(self.splitter)
        self.list_widget = QListWidget(self)
        self.list_widget.setStyleSheet("QListWidget:focus {outline: 0px;}")
        self.tab_widget = QTabWidget(self)
        self.tab_widget.tabBar().hide()
        self.splitter.addWidget(self.list_widget)
        self.splitter.addWidget(self.tab_widget)
        self.currentChanged.connect(
            self.tab_widget.setCurrentIndex
        )  # 监听 Tab 切换事件
        self.list_widget.currentRowChanged.connect(self.currentChanged)
        self.idx = 0
        self.titles = []

    def addTab(self, widget, title):
        self.titles.append(title)
        self.tab_widget.addTab(widget, title)
        item = QListWidgetItem(title)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        item.setSizeHint(QSize(self.tab_widget.width(), 50))
        self.list_widget.addItem(item)
        if self.idx == 0:
            self.list_widget.setCurrentRow(0)
        self.idx += 1

    def currentWidget(self):
        return self.tab_widget.currentWidget()


class Setting(closeashidewindow):
    voicelistsignal = pyqtSignal(list, int)
    mp3playsignal = pyqtSignal(bytes, int, bool)
    versiontextsignal = pyqtSignal(str)
    progresssignal = pyqtSignal(str, int)
    fontbigsmallsignal = pyqtSignal(int)
    opensolvetextsig = pyqtSignal()
    showandsolvesig = pyqtSignal(str)

    def __init__(self, parent):
        super(Setting, self).__init__(parent, globalconfig["setting_geo_2"])
        self.setWindowIcon(qtawesome.icon("fa.gear"))
        self.mp3player = wavmp3player()
        self.mp3playsignal.connect(self.mp3player.mp3playfunction)
        self.opensolvetextsig.connect(self.opensolvetextfun)
        self.showandsolvesig.connect(functools.partial(delaysetcomparetext, self))
        self.fontbigsmallsignal.connect(functools.partial(maybehavefontsizespin, self))
        self.voicelistsignal.connect(functools.partial(showvoicelist, self))
        self.versiontextsignal.connect(
            functools.partial(versionlabelmaybesettext, self)
        )
        self.progresssignal.connect(functools.partial(updateprogress, self))
        self.isfirst = True
        versioncheckthread(self)
        checkconnected(self)
        registrhotkeys(self)

    def showEvent(self, e: QShowEvent):
        if self.isfirst:
            self.isfirst = False
            self.firstshow()
        super().showEvent(e)

    def firstshow(self):

        self.setMinimumSize(100, 100)
        self.setWindowTitle(_TR("设置"))

        self.tab_widget, do = makesubtab_lazy(
            _TRL(
                [
                    "文本输入",
                    "翻译设置",
                    "显示设置",
                    "文本处理",
                    "辞书设置",
                    "语音合成",
                    "快捷按键",
                    "语言设置",
                    "网络设置",
                    "版本更新",
                    "资源下载",
                ]
            ),
            [
                functools.partial(setTabOne_lazy, self),
                functools.partial(setTabTwo_lazy, self),
                functools.partial(setTabThree_lazy, self),
                functools.partial(setTab7_lazy, self),
                functools.partial(setTabcishu, self),
                functools.partial(setTab5, self),
                functools.partial(setTab_quick, self),
                functools.partial(setTablang, self),
                functools.partial(setTab_proxy, self),
                functools.partial(setTab_update, self),
                functools.partial(setTab_aboutlazy, self),
            ],
            klass=TabWidget,
            delay=True,
        )
        self.setCentralWidget(self.tab_widget)
        do()
        width = 0
        fn = QFont()
        fn.setPointSizeF(globalconfig["settingfontsize"] + 4)
        fn.setFamily(globalconfig["settingfonttype"])
        fm = QFontMetrics(fn)
        for title in self.tab_widget.titles:
            width = max(fm.size(0, title).width(), width)
        width += 50
        self.tab_widget.splitter.setStretchFactor(0, 0)
        self.tab_widget.splitter.setStretchFactor(1, 1)
        self.tab_widget.splitter.setSizes([width, self.tab_widget.width() - width])

    def opensolvetextfun(self):
        self.show()
        self.tab_widget.setCurrentIndex(3)
