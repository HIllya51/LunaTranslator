from qtsymbols import *
import functools
from gui.setting.display_buttons import createbuttonwidget
from gui.setting.display_text import xianshigrid_style
from gui.setting.display_ui import uisetting
from gui.setting.display_scale import makescalew
from gui.usefulwidget import makesubtab_lazy, makescrollgrid
from myutils.config import get_platform


def setTabThree_lazy(self, basel: QLayout):
    titles = ["文本设置", "界面设置", "工具按钮", "窗口缩放"]
    funcs = [
        lambda l: makescrollgrid(xianshigrid_style(self), l),
        functools.partial(uisetting, self),
        functools.partial(createbuttonwidget, self),
        lambda l: makescrollgrid(makescalew(), l),
    ]
    if get_platform() == "xp":
        titles.pop(3)
        funcs.pop(3)
    tab, do = makesubtab_lazy(
        titles,
        funcs,
        delay=True,
    )

    basel.addWidget(tab)
    do()
