from qtsymbols import *
import functools
from traceback import print_exc
import qtawesome
from gui.gamemanager.v3 import dialog_savedgame_v3
from myutils.wrapper import Singleton
from myutils.config import globalconfig
from gui.usefulwidget import saveposwindow, create_centered_rect
from gui.fluent.frameless import FluentFramelessWindowMixin
from gui.fluent.titlebar import FluentTitleBar


@Singleton
class dialog_savedgame_integrated(FluentFramelessWindowMixin, saveposwindow):
    def selectlayout(self, type):
        try:
            # 仅剩 v3 一个视图；旧存档的 0（legacy）/2（旧网格）都迁移过来
            type = 0
            globalconfig["gamemanager_integrated_internal_layout"] = type
            klass = [dialog_savedgame_v3][type]
            _old = self.internallayout.takeAt(0).widget()
            _old.hide()
            _ = klass(self)
            self.__internal = _
            self.internallayout.addWidget(_)
            _.directshow()
            _old.deleteLater()
        except:
            print_exc()

    # ---- Fluent 标题栏 / 无边框（同设置窗口）----
    def _install_fluent_chrome(self):
        self._fluent_title_bar = FluentTitleBar(self)
        # 汉堡在侧边栏第一行（v3 内），标题栏不再放导航按钮
        self._fluent_title_bar.setNavButtonVisible(False)
        self._fluent_title_bar.navToggleRequested.connect(self._toggle_nav)
        self.setMenuWidget(self._fluent_title_bar)
        self.setProperty("fluentFrameless", True)
        # 窗口激活态 -> 标题栏 bar-active 属性（插件据此调标题栏底色）
        self.installEventFilter(self)

    def _toggle_nav(self):
        if self.__internal is not None:
            self.__internal._toggle_nav()

    def hitTestWidgets(self):
        bar = self._fluent_title_bar
        if bar is None:
            return []
        return [bar.navButton(), bar.minButton(), bar.maxButton(), bar.closeButton()]

    def __init__(self, parent) -> None:
        super().__init__(
            parent,
            posinit=globalconfig.get(
                "savegamedialoggeo", create_centered_rect(800, 600).getRect()
            ),
            possave=functools.partial(globalconfig.__setitem__, "savegamedialoggeo"),
        )
        self.setWindowTitle("游戏管理")
        self.setWindowIcon(
            qtawesome.icon(globalconfig["toolbutton"]["buttons"]["gamepad_new"]["icon"])
        )
        self._fluent_title_bar = None
        self.__internal = None
        self._install_fluent_chrome()
        w = QWidget()
        self.internallayout = QHBoxLayout(w)
        self.internallayout.setContentsMargins(0, 0, 0, 0)
        self.internallayout.addWidget(QWidget())
        self.setCentralWidget(w)

        self.show()
        self.selectlayout(globalconfig.get("gamemanager_integrated_internal_layout", 1))
