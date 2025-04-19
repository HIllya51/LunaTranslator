from qtsymbols import *
import functools
from gui.setting.display_buttons import createbuttonwidget
from gui.setting.display_text import xianshigrid_style
from gui.setting.display_ui import uisetting
from gui.setting.display_scale import makescalew
from gui.usefulwidget import makesubtab_lazy, makescrollgrid


def setTabThree_lazy(self, basel: QLayout):
    titles = ["文本设置", "界面设置", "工具按钮", "窗口缩放"]
    funcs = [
        lambda l: makescrollgrid(xianshigrid_style(self), l),
        lambda l: makescrollgrid(uisetting(self), l),
        functools.partial(createbuttonwidget, self),
        lambda l: makescrollgrid(makescalew(), l),
    ]
    tab, do = makesubtab_lazy(
        titles,
        funcs,
        delay=True,
    )

    basel.addWidget(tab)
    do()
