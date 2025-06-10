from qtsymbols import *
import qtawesome
import gobject
from myutils.config import globalconfig
from gui.ui2.usefulwidget import closeashidewindow
from gui.setting.hotkey import registrhotkeys
from elawidgettools import *


class Setting2(closeashidewindow):

    def __init__(self, parent):
        super().__init__(parent, globalconfig["setting_geo_2"])
        self.setWindowIcon(qtawesome.icon("fa.gear"))
        self.setWindowTitle("设置")
        self.setMinimumSize(100, 100)
        self.isfirst = True
        registrhotkeys(self)
        gobject.signals.settin_ui_showsignal.connect(self.showsignal)
        self.setUserInfoCardVisible(False)

    def showEvent(self, e: QShowEvent):
        if self.isfirst:
            self.isfirst = False
            self.firstshow()
        super().showEvent(e)

    def firstshow(self):
        1

        _, _aboutKey = self.addFooterNode(
            "关于软件", None, 0, ElaIconType.IconName.User
        )

    # self.setCentralWidget(self.tab_widget)
