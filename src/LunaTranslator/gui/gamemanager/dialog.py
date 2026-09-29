from qtsymbols import *
import functools
from traceback import print_exc
import qtawesome
from gui.gamemanager.v3 import dialog_savedgame_v3
from myutils.wrapper import Singleton
from myutils.config import globalconfig
from gui.usefulwidget import saveposwindow, create_centered_rect


@Singleton
class dialog_savedgame_integrated(saveposwindow):
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

    def __init__(self, parent) -> None:
        super().__init__(
            parent,
            flags=Qt.WindowType.WindowMinMaxButtonsHint
            | Qt.WindowType.WindowCloseButtonHint,
            posinit=globalconfig.get(
                "savegamedialoggeo", create_centered_rect(800, 600).getRect()
            ),
            possave=functools.partial(globalconfig.__setitem__, "savegamedialoggeo"),
        )
        self.setWindowTitle("游戏管理")
        self.setWindowIcon(
            qtawesome.icon(globalconfig["toolbutton"]["buttons"]["gamepad_new"]["icon"])
        )
        w = QWidget()
        self.internallayout = QHBoxLayout(w)
        self.internallayout.setContentsMargins(0, 0, 0, 0)
        self.__internal = None
        self.internallayout.addWidget(QWidget())
        self.setCentralWidget(w)

        self.show()
        self.selectlayout(globalconfig.get("gamemanager_integrated_internal_layout", 1))
