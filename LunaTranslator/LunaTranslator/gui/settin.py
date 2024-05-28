from PyQt5.QtCore import pyqtSignal, Qt, QSize
from PyQt5.QtWidgets import (
    QWidget,
    QListWidget,
    QHBoxLayout,
    QListWidgetItem,
    QMenu,
    QAction,
)
from PyQt5.QtGui import QFont, QFontMetrics
from PyQt5.QtWidgets import QTabWidget
import qtawesome, gobject
import threading, windows, winsharedutils
from myutils.config import globalconfig, _TR
from myutils.utils import wavmp3player
from gui.settingpage1 import setTabOne, setTabOne_direct
from gui.settingpage2 import setTabTwo, settab2d
from gui.settingpage_xianshishezhi import setTabThree, setTabThree_direct
from gui.settingpage_tts import setTab5, setTab5_direct
from gui.settingpage_cishu import setTabcishu
from gui.settingpage_quick import setTab_quick, setTab_quick_direct
from gui.setting_lang import setTablang, setTablangd
from gui.setting_proxy import setTab_proxy
from gui.settingpage7 import setTab7, settab7direct
from gui.settingpage_about import setTab_about, setTab_about_dicrect
from gui.usefulwidget import closeashidewindow, makesubtab_lazy


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
        self.list_widget = QListWidget(self)
        self.list_widget.setStyleSheet("QListWidget:focus {outline: 0px;}")
        self.tab_widget = QTabWidget(self)
        self.tab_widget.tabBar().hide()
        layout.addWidget(self.list_widget)
        layout.addWidget(self.tab_widget)
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
        item.setTextAlignment(Qt.AlignCenter)
        item.setSizeHint(QSize(self.tab_widget.width(), 50))
        self.list_widget.addItem(item)
        if self.idx == 0:
            self.list_widget.setCurrentRow(0)
        self.idx += 1

    def currentWidget(self):
        return self.tab_widget.currentWidget()


class Settin(closeashidewindow):
    voicelistsignal = pyqtSignal(list, int)
    mp3playsignal = pyqtSignal(bytes, int, bool)
    versiontextsignal = pyqtSignal(str)
    progresssignal = pyqtSignal(str, int)
    fontbigsmallsignal = pyqtSignal(int)
    clicksourcesignal = pyqtSignal(str)
    opensolvetextsig = pyqtSignal()
    showandsolvesig = pyqtSignal(str)
    setstylesheetsignal = pyqtSignal()

    def __init__(self, parent):
        super(Settin, self).__init__(parent, globalconfig, "setting_geo_2")
        # self.setWindowFlag(Qt.Tool,False)
        # self.setWindowFlags(self.windowFlags()&~Qt.WindowMinimizeButtonHint)
        self.mp3player = wavmp3player()
        self.mp3playsignal.connect(self.mp3player.mp3playfunction)
        self.opensolvetextsig.connect(self.opensolvetextfun)

        self.setMinimumSize(100, 100)
        self.list_width = 100
        self.window_height = 500
        self.savelastrect = None

        self.hooks = []

        self.usevoice = 0
        setTabOne_direct(self)
        settab2d(self)
        settab7direct(self)
        setTabThree_direct(self)
        setTab5_direct(self)
        setTab_quick_direct(self)
        setTablangd(self)
        setTab_about_dicrect(self)

        self.setstylesheetsignal.connect(gobject.baseobject.setcommonstylesheet)
        threading.Thread(target=self.darklistener).start()

        self.setWindowTitle(_TR("设置"))
        self.setWindowIcon(qtawesome.icon("fa.gear"))

        self.tab_widget = makesubtab_lazy(klass=TabWidget)
        self.setCentralWidget(self.tab_widget)

        self.tab_widget.setStyleSheet(
            """QListWidget { 
                font:16pt  ;  }
            """
        )
        # self.tab_widget.setTabPosition(QTabWidget.West)
        setTabOne(self)
        setTabTwo(self)

        setTabThree(self)
        setTab7(self)
        setTabcishu(self)
        setTab5(self)

        setTab_quick(self)

        setTablang(self)
        setTab_proxy(self)
        setTab_about(self)

        width = 0
        fn = QFont()
        fn.setPixelSize(16)
        fn.setFamily(globalconfig["settingfonttype"])
        fm = QFontMetrics(fn)
        for title in self.tab_widget.titles:
            width = max(fm.width(title), width)
        width += 100
        self.tab_widget.list_widget.setFixedWidth(width)
        self.list_width = width

    def opensolvetextfun(self):
        self.show()
        self.tab_widget.setCurrentIndex(3)

    def darklistener(self):
        sema = winsharedutils.startdarklistener()
        while True:
            # 会触发两次
            windows.WaitForSingleObject(sema, windows.INFINITE)
            if globalconfig["darklight"] == 2:
                self.setstylesheetsignal.emit()
            windows.WaitForSingleObject(sema, windows.INFINITE)
