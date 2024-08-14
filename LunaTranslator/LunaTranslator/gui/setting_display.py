from qtsymbols import *
import functools
from gui.setting_display_buttons import createbuttonwidget
from gui.setting_display_text import xianshigrid_style
from gui.setting_display_ui import uisetting
from gui.setting_display_scale import makescalew
from gui.usefulwidget import makesubtab_lazy, makescrollgrid


def setTabThree_lazy(self, basel):

    tab, do = makesubtab_lazy(
        ["文本设置", "界面设置", "工具按钮", "窗口缩放"],
        [
            lambda l: makescrollgrid(xianshigrid_style(self), l),
            functools.partial(uisetting, self),
            functools.partial(createbuttonwidget, self),
            functools.partial(makescalew, self),
        ],
        delay=True,
    )

    basel.addWidget(tab)
    do()
