from qtsymbols import *
import functools
from myutils.config import _TRL
from gui.setting_display_buttons import createbuttonwidget
from gui.setting_display_text import xianshigrid_style, xianshigrid_text
from gui.setting_display_ui import uisetting,themesetting
from gui.setting_display_scale import makescalew
from gui.usefulwidget import (
    makesubtab_lazy,
    makescrollgrid,
)


def setTabThree_lazy(self, basel):

    tab, do = makesubtab_lazy(
        _TRL(["字体样式", "显示内容", "界面设置", "主题效果", "工具按钮", "窗口缩放"]),
        [
            lambda l: makescrollgrid(xianshigrid_style(self), l),
            lambda l: makescrollgrid(xianshigrid_text(self), l),
            lambda l: makescrollgrid(uisetting(self), l),
            lambda l: makescrollgrid(themesetting(self), l),
            functools.partial(createbuttonwidget, self),
            functools.partial(makescalew, self),
        ],
        delay=True,
    )

    basel.addWidget(tab)
    do()
