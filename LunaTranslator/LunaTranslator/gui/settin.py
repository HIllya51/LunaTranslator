from PyQt5.QtCore import pyqtSignal, Qt, QSize, QObject, QEvent
from PyQt5.QtWidgets import (
    QLabel,
    QScrollArea,
    QWidget,
    QGridLayout,
    QVBoxLayout,
    QListWidget,
    QHBoxLayout,
    QListWidgetItem,
    QApplication,
)
from PyQt5.QtGui import QResizeEvent
from PyQt5.QtWidgets import QTabWidget
import qtawesome, darkdetect, ctypes
import functools
from traceback import print_exc
from myutils.config import globalconfig, _TR
from myutils.utils import wavmp3player
from myutils.config import static_data
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
from gui.usefulwidget import closeashidewindow


class gridwidget(QWidget):
    pass


class Settin(closeashidewindow):
    voicelistsignal = pyqtSignal(list, int)
    mp3playsignal = pyqtSignal(str, int)
    versiontextsignal = pyqtSignal(str)
    progresssignal = pyqtSignal(str, int)
    fontbigsmallsignal = pyqtSignal(int)
    clicksourcesignal = pyqtSignal(str)
    opensolvetextsig = pyqtSignal()
    showandsolvesig = pyqtSignal(str)

    def resizefunction(self):

        for w in self.needfitwidgets:
            w.setFixedWidth(
                int(self.size().width() - self.window_width * 0.2 - self.scrollwidth)
            )
        for grid, maxl in self.needfitcols:
            for c in range(maxl):
                grid.setColumnMinimumWidth(
                    c,
                    int(
                        self.size().width()
                        - self.window_width * 0.2
                        - self.scrollwidth // maxl
                    ),
                )

    def resizeEvent(self, a0: QResizeEvent) -> None:

        self.resizefunction()
        return super().resizeEvent(a0)

    def automakegrid(self, grid, lis, save=False, savelist=None):
        maxl = 0

        for nowr, line in enumerate(lis):
            nowc = 0
            if save:
                ll = []
            for i in line:
                if type(i) == str:
                    cols = 1
                    wid = QLabel(_TR(i))
                elif type(i) != tuple:
                    wid, cols = i, 1
                elif len(i) == 2:

                    wid, cols = i
                    if type(wid) == str:
                        wid = QLabel(_TR(wid))
                elif len(i) == 3:
                    wid, cols, arg = i
                    if type(wid) == str:
                        wid = QLabel((wid))
                        if arg == "link":
                            wid.setOpenExternalLinks(True)
                grid.addWidget(wid, nowr, nowc, 1, cols)
                if save:
                    ll.append(wid)
                nowc += cols
            maxl = max(maxl, nowc)
            if save:
                savelist.append(ll)

            grid.setRowMinimumHeight(nowr, 35)
        self.needfitcols.append([grid, maxl])

    def __init__(self, parent):
        self.needfitwidgets = []
        self.needfitcols = []
        super(Settin, self).__init__(parent, globalconfig, "setting_geo_2")
        # self.setWindowFlag(Qt.Tool,False)
        # self.setWindowFlags(self.windowFlags()&~Qt.WindowMinimizeButtonHint)
        self.mp3player = wavmp3player()
        self.mp3playsignal.connect(self.mp3player.mp3playfunction)
        self.opensolvetextsig.connect(self.opensolvetextfun)

        self.setMinimumSize(100, 100)
        # 界面尺寸
        self.window_width = 900 if globalconfig["languageuse"] == 0 else 1200

        self.window_height = 500
        self.scrollwidth = 20
        self.savelastrect = None

        self.hooks = []

        self.usevoice = 0
        self.isfirstshow = True

        setTabOne_direct(self)
        settab2d(self)
        settab7direct(self)
        setTabThree_direct(self)
        setTab5_direct(self)
        setTab_quick_direct(self)
        setTablangd(self)
        setTab_about_dicrect(self)

        self.setstylesheet()

    def opensolvetextfun(self):
        self.show()
        self.tab_widget.setCurrentIndex(3)

    def showEvent(self, e):
        if self.isfirstshow:
            self.setWindowTitle(_TR("设置"))
            self.setWindowIcon(qtawesome.icon("fa.gear"))

            class TabWidget(QWidget):
                currentChanged = pyqtSignal(int)

                def __init__(self, parent=None):
                    super(TabWidget, self).__init__(parent)
                    layout = QHBoxLayout()
                    layout.setContentsMargins(0, 0, 0, 0)
                    self.setLayout(layout)
                    self.list_widget = QListWidget(self)
                    self.tab_widget = QTabWidget(self)
                    self.tab_widget.tabBar().hide()  # 隐藏默认的 TabBar
                    self.tab_widget.setTabPosition(QTabWidget.West)  # 将 Tab 放在左侧
                    layout.addWidget(self.list_widget)
                    layout.addWidget(self.tab_widget)
                    self.currentChanged.connect(
                        self.tab_widget.setCurrentIndex
                    )  # 监听 Tab 切换事件
                    self.list_widget.currentRowChanged.connect(self.currentChanged)
                    self.idx = 0

                def addTab(self, widget, title):
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

            self.tab_widget = self.makesubtab_lazy(klass=TabWidget)
            self.setCentralWidget(self.tab_widget)
            self.tab_widget.list_widget.setFixedWidth(int(self.window_width * 0.2))

            self.tab_widget.setStyleSheet(
                """QListWidget { 
                    font:%spt  ;  }
                """
                % (
                    globalconfig["tabfont_chs"]
                    if globalconfig["languageuse"] == 0
                    else globalconfig["tabfont_otherlang"]
                )
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
            self.isfirstshow = False

    def setstylesheet(self):

        dl = globalconfig["darklight"]
        if dl == 0:
            dark = False
        elif dl == 1:
            dark = True
        elif dl == 2:
            dark = darkdetect.isDark()
        darklight = ["light", "dark"][dark]

        top_level_widgets = QApplication.topLevelWidgets()

        def ChangeDWMAttrib(hWnd: int, attrib: int, color) -> None:
            try:
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    hWnd, attrib, ctypes.byref(color), ctypes.sizeof(ctypes.c_int)
                )
            except:
                pass

        def darkchange(hwnd):
            if dark:
                ChangeDWMAttrib(hwnd, 19, ctypes.c_int(1))
                ChangeDWMAttrib(hwnd, 20, ctypes.c_int(1))
            else:
                ChangeDWMAttrib(hwnd, 19, ctypes.c_int(0))
                ChangeDWMAttrib(hwnd, 20, ctypes.c_int(0))

        class WindowEventFilter(QObject):
            def eventFilter(self, obj, event):
                if event.type() == QEvent.Type.WindowTitleChange:
                    darkchange(int(obj.winId()))
                return False

        self.__filter = WindowEventFilter()
        QApplication.instance().installEventFilter(self.__filter)
        for widget in top_level_widgets:
            darkchange(int(widget.winId()))

        try:
            idx = globalconfig[darklight + "theme"] - int(not dark)
            if idx == -1:
                raise Exception()
            with open(
                "./files/themes/{}".format(
                    static_data["themes"][darklight][idx]["file"]
                ),
                "r",
            ) as ff:
                style = ff.read()
        except:
            # print_exc()
            style = ""
        style += (
            "*{font: %spt '" % (globalconfig["settingfontsize"])
            + (globalconfig["settingfonttype"])
            + "' ;  }"
        )
        self.setStyleSheet(style)

    def makevbox(self, wids):
        q = QWidget()
        v = QVBoxLayout()
        q.setLayout(v)
        v.setContentsMargins(0, 0, 0, 0)
        for wid in wids:
            v.addWidget(wid)
        return q

    def makegrid(self, grid, save=False, savelist=None, savelay=None):

        gridlayoutwidget = gridwidget()
        gridlay = QGridLayout()
        gridlayoutwidget.setLayout(gridlay)
        gridlayoutwidget.setStyleSheet("gridwidget{background-color:transparent;}")
        self.needfitwidgets.append(gridlayoutwidget)
        gridlayoutwidget.setFixedHeight(len(grid) * 35)
        margins = gridlay.contentsMargins()
        gridlay.setContentsMargins(margins.left(), 0, margins.right(), 0)
        self.automakegrid(gridlay, grid, save, savelist)
        if save:
            savelay.append(gridlay)
        return gridlayoutwidget

    def makescroll(self, widget):
        scroll = QScrollArea()
        scroll.setHorizontalScrollBarPolicy(1)
        scroll.setStyleSheet("""QScrollArea{background-color:transparent;border:0px}""")
        scroll.verticalScrollBar().setStyleSheet(
            "QScrollBar{width:%spx;}" % self.scrollwidth
        )

        self.needfitwidgets.append(widget)
        scroll.setWidget(widget)
        return scroll

    def makesubtab(self, titles, widgets):
        tab = QTabWidget()
        for i, wid in enumerate(widgets):
            self.tabadd(tab, titles[i], wid)
        return tab

    def makesubtab_lazy(self, titles=None, functions=None, klass=None):
        if klass:
            tab = klass()
        else:
            tab = QTabWidget()

        def __(t, i):
            try:
                w = t.currentWidget()
                if "lazyfunction" in dir(w):
                    w.lazyfunction()
                    delattr(w, "lazyfunction")
                    self.resizefunction()
            except:
                print_exc()

        tab.currentChanged.connect(functools.partial(__, tab))
        if titles and functions:
            for i, func in enumerate(functions):
                self.tabadd_lazy(tab, titles[i], func)
        return tab

    def tabadd_lazy(self, tab, title, getrealwidgetfunction):
        q = QWidget()
        v = QVBoxLayout()
        q.setLayout(v)
        v.setContentsMargins(0, 0, 0, 0)
        q.lazyfunction = lambda: v.addWidget(getrealwidgetfunction())
        self.tabadd(tab, title, q)

    def tabadd(self, tab, title, widgets):
        tab.addTab(widgets, _TR(title))
