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

# FluentUI3 主题
from gui.fluent.frameless import FluentFramelessWindowMixin
from gui.fluent.titlebar import FluentTitleBar
from gui.fluent.tabwidget import FluentTabWidget


class _SettingBase(FluentFramelessWindowMixin, closeashidewindow):
    pass


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

        self.setMinimumSize(560, 360)
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
            klass=FluentTabWidget,
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
