from qtsymbols import *
import functools
import qtawesome
import gobject, time
from myutils.config import globalconfig
from gui.usefulwidget import closeashidewindow, makesubtab_lazy, create_centered_rect
from gui.setting.textinput import setTabOne_lazy
from gui.setting.translate import setTabTwo_lazy, show_tscolor_setting_guide
from gui.setting.display import display_nav_children
from gui.setting.tts import setTab5
from gui.setting.cishu import setTabcishu
from gui.setting.hotkey import setTab_quick, registrhotkeys
from gui.setting.transopti import transopti_nav_children
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
        # 汉堡在导航窗格第一行（FluentTabWidget 内，同游戏管理器），
        # 标题栏不放导航按钮
        self._fluent_title_bar.setNavButtonVisible(False)
        self._fluent_title_bar.navToggleRequested.connect(self._toggle_fluent_nav)
        self.setMenuWidget(self._fluent_title_bar)
        self.setProperty("fluentFrameless", True)
        # 窗口激活态 -> 标题栏 bar-active 属性（插件据此调标题栏底色）
        self.installEventFilter(self)

    def _toggle_fluent_nav(self):
        if getattr(self, "tab_widget", None) is not None and hasattr(
            self.tab_widget, "toggleNavigation"
        ):
            # 折叠状态由 navigationExpandedChanged 信号统一持久化
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

        display_children = display_nav_children(self)
        transopti_children = transopti_nav_children(self)
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
                display_children[0][1],  # 显示设置页 = 首子页（文本设置）
                transopti_children[0][1],  # 文本处理页 = 首子页（文本预处理）
                functools.partial(setTabcishu, self),
                functools.partial(setTab5, self),
                functools.partial(setTab_quick, self),
                functools.partial(setTab_about, self),
            ],
            klass=FluentTabWidget,
            delay=True,
            bare=False,
        )
        self.setCentralWidget(self.tab_widget)
        do()
        # 显示设置的四个子页 → 主导航层级子节点（同 Gallery add_nav_child）；
        # 首子项复用父项页面，点击父项即进入首个子页
        self.tab_widget.addNavChildPage(
            "显示设置", display_children[0][0], display_children[0][1],
            page_index=self.tab_widget.navPageIndex("显示设置"))
        for _title, _func in display_children[1:]:
            self.tab_widget.addNavChildPage("显示设置", _title, _func)
        # 文本处理的两个子页 → 主导航层级子节点
        self.tab_widget.addNavChildPage(
            "文本处理", transopti_children[0][0], transopti_children[0][1],
            page_index=self.tab_widget.navPageIndex("文本处理"))
        for _title, _func in transopti_children[1:]:
            self.tab_widget.addNavChildPage("文本处理", _title, _func)
        self.tab_widget.adjust_list_widget_width()
        # 侧边栏折叠状态：任意来源（汉堡/程序性展开）都经信号持久化
        self.tab_widget.nav.navigationExpandedChanged.connect(
            lambda exp: globalconfig.__setitem__(
                "setting_nav_collapsed", not exp))
        self.tab_widget.setNavigationExpanded(
            not globalconfig.get("setting_nav_collapsed", False), animated=False)
        index = 0
        self.tab_widget.setCurrentIndex(index)
        gobject.base.switchtotspage.connect(
            lambda: (self.tab_widget.setCurrentIndex(1), show_tscolor_setting_guide())
        )

        if time.time() - globalconfig.get("lasttime3", 0) > 3600 * 24 * 3:
            self.showabout()
            globalconfig["lasttime3"] = time.time()
        elif time.time() - globalconfig.get("lasttime2", 0) > 3600 * 24 * 1:
            self.showabout()
        globalconfig["lasttime2"] = time.time()

    def showabout(self):
        self.tab_widget.setCurrentIndex(7)
