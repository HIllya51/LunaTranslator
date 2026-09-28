from qtsymbols import *
import functools
import qtawesome
import time, gobject
from myutils.config import globalconfig
from gui.usefulwidget import closeashidewindow, makesubtab_lazy, create_centered_rect
from gui.setting.textinput import setTabOne_lazy
from gui.setting.translate import setTabTwo_lazy, show_tscolor_setting_guide
from gui.setting.display import setTabThree_lazy
from gui.setting.tts import setTab5
from gui.setting.cishu import setTabcishu
from gui.setting.hotkey import setTab_quick, registrhotkeys
from gui.setting.transopti import setTab7_lazy
from gui.setting.about import setTab_about
from gui.dynalang import LListWidgetItem, LListWidget

# FluentUI3 主题（非 Fluent 主题时 mixin 全部钩子直通，行为与原来一致）
import gui.fluent as _fluent
from gui.fluent.frameless import FluentFramelessWindowMixin
from gui.fluent.titlebar import FluentTitleBar
from gui.fluent.tabwidget import FluentTabWidget


class _SettingBase(FluentFramelessWindowMixin, closeashidewindow):
    pass


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
        self.list_widget.setObjectName("NOBORDER")
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


class Setting(_SettingBase):

    def __init__(self, parent):
        super(Setting, self).__init__(
            parent,
            posinit=globalconfig.get(
                "setting_geo_2", create_centered_rect(1000, 600).getRect()
            ),
            possave=functools.partial(globalconfig.__setitem__, "setting_geo_2"),
        )
        self.setWindowIcon(qtawesome.icon("fa.gear"))
        self._fluent_title_bar = None
        if _fluent.is_fluent_theme():
            self._install_fluent_chrome()
        self.isfirst = True
        registrhotkeys(self)
        gobject.base.settin_ui_showsignal.connect(self.showsignal)

    # ---- Fluent 标题栏 / 无边框 ----
    def _install_fluent_chrome(self):
        self._fluent_title_bar = FluentTitleBar(self)
        self._fluent_title_bar.navToggleRequested.connect(self._toggle_fluent_nav)
        self.setMenuWidget(self._fluent_title_bar)
        self.setProperty("fluentFrameless", True)
        # 窗口激活态 -> 标题栏 bar-active 属性（插件据此调标题栏底色）
        self.installEventFilter(self)

    def _toggle_fluent_nav(self):
        if getattr(self, "tab_widget", None) is not None and hasattr(
            self.tab_widget, "toggleNavigation"
        ):
            self.tab_widget.toggleNavigation()

    def hitTestWidgets(self):
        bar = self._fluent_title_bar
        if bar is None:
            return []
        return [bar.navButton(), bar.minButton(), bar.maxButton(), bar.closeButton()]

    def showEvent(self, e: QShowEvent):
        if self.isfirst:
            self.isfirst = False
            self.firstshow()
        super().showEvent(e)

    def firstshow(self):

        self.setMinimumSize(560 if self._fluent_title_bar else 100, 360 if self._fluent_title_bar else 100)
        self.setWindowTitleWithVersionWithUserconfig("设置")

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
            klass=(FluentTabWidget if self._fluent_title_bar is not None else TabWidget),
            delay=True,
        )
        self.setCentralWidget(self.tab_widget)
        do()
        self.tab_widget.adjust_list_widget_width()
        index = 0
        self.tab_widget.setCurrentIndex(index)
        gobject.base.switchtotspage.connect(
            lambda: (self.tab_widget.setCurrentIndex(1), show_tscolor_setting_guide())
        )
