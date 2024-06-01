import functools
from qtsymbols import *
from myutils.config import globalconfig
import gobject
from gui.gui_xianshi_buttons import createbuttonwidget
from gui.gui_xianshi_text import xianshigrid
from gui.gui_xianshi_ui import uisetting
from gui.gui_xianshi_scale import makescalew
from gui.usefulwidget import (
    D_getspinbox,
    makesubtab_lazy,
    makescrollgrid,
    D_getsimpleswitch,
)


def _xingw():

    xingweigrid = [
        [
            ("游戏最小化时窗口隐藏", 6),
            (D_getsimpleswitch(globalconfig, "minifollow"), 1),
        ],
        [
            ("游戏失去焦点时窗口隐藏", 6),
            (D_getsimpleswitch(globalconfig, "focusfollow"), 1),
        ],
        [
            ("游戏失去焦点时取消置顶", 6),
            (D_getsimpleswitch(globalconfig, "focusnotop"), 1),
        ],
        [
            ("游戏窗口移动时同步移动", 6),
            (D_getsimpleswitch(globalconfig, "movefollow"), 1),
        ],
        [
            ("固定窗口尺寸", 6),
            D_getsimpleswitch(globalconfig, "fixedheight"),
        ],
        [
            ("自动隐藏窗口", 6),
            (D_getsimpleswitch(globalconfig, "autodisappear"), 1),
            "",
            ("隐藏延迟(s)", 3),
            (D_getspinbox(1, 100, globalconfig, "disappear_delay"), 2),
        ],
        [
            ("任务栏中显示_翻译窗口", 6),
            D_getsimpleswitch(
                globalconfig,
                "showintab",
                callback=lambda _: gobject.baseobject.setshowintab(),
            ),
        ],
        [
            ("任务栏中显示_其他", 6),
            D_getsimpleswitch(
                globalconfig,
                "showintab_sub",
                callback=lambda _: gobject.baseobject.setshowintab(),
            ),
        ],
        [
            ("选择文本窗口中文本框只读", 6),
            D_getsimpleswitch(
                globalconfig,
                "textboxreadonly",
                callback=lambda x: gobject.baseobject.hookselectdialog.textOutput.setReadOnly(
                    x
                ),
            ),
        ],
        [
            ("可选取模式", 6),
            D_getsimpleswitch(
                globalconfig,
                "selectable",
                callback=lambda x: gobject.baseobject.translation_ui.translate_text.setselectable(),
            ),
        ],
    ]
    return xingweigrid


def setTabThree_lazy(self, basel):

    tab, do = makesubtab_lazy(
        ["文本设置", "界面主题", "窗口行为", "工具按钮", "窗口缩放"],
        [
            lambda l: makescrollgrid(xianshigrid(self), l),
            lambda l: makescrollgrid(uisetting(self), l),
            lambda l: makescrollgrid(_xingw(), l),
            functools.partial(createbuttonwidget, self),
            functools.partial(makescalew, self),
        ],
        delay=True,
    )

    basel.addWidget(tab)
    do()
