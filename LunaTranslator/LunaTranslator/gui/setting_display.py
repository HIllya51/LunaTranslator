from qtsymbols import *
import functools
import gobject
from myutils.config import globalconfig, _TRL
from gui.setting_display_buttons import createbuttonwidget
from gui.setting_display_text import xianshigrid
from gui.setting_display_ui import uisetting
from gui.setting_display_scale import makescalew
from gui.usefulwidget import (
    D_getspinbox,
    makesubtab_lazy,
    makescrollgrid,
    D_getsimpleswitch,
)


def _xingw():

    xingweigrid = [
        [
            (
                dict(
                    title="伴随游戏窗口",
                    grid=(
                        [
                            "游戏最小化时窗口隐藏",
                            D_getsimpleswitch(globalconfig, "minifollow"),
                        ],
                        [
                            "游戏失去焦点时取消置顶",
                            D_getsimpleswitch(globalconfig, "focusnotop"),
                        ],
                        [
                            "游戏窗口移动时同步移动",
                            D_getsimpleswitch(globalconfig, "movefollow"),
                        ],
                    ),
                ),
                0,
                "group",
            )
        ],
        [
            (
                dict(
                    title="窗口尺寸",
                    grid=(
                        [
                            "自动延展",
                            D_getsimpleswitch(globalconfig, "auto_expand"),
                        ],
                        [
                            "自动收缩",
                            D_getsimpleswitch(globalconfig, "auto_shrink"),
                        ],
                    ),
                ),
                0,
                "group",
            )
        ],
        [
            (
                dict(
                    title="其他",
                    grid=(
                        [
                            "自动隐藏窗口",
                            D_getsimpleswitch(globalconfig, "autodisappear"),
                        ],
                        [
                            "隐藏延迟(s)",
                            D_getspinbox(1, 100, globalconfig, "disappear_delay"),
                        ],
                        [
                            "任务栏中显示_翻译窗口",
                            D_getsimpleswitch(
                                globalconfig,
                                "showintab",
                                callback=lambda _: gobject.baseobject.setshowintab(),
                            ),
                        ],
                        [
                            "任务栏中显示_其他",
                            D_getsimpleswitch(
                                globalconfig,
                                "showintab_sub",
                                callback=lambda _: gobject.baseobject.setshowintab(),
                            ),
                        ],
                        [
                            "可选取模式",
                            D_getsimpleswitch(
                                globalconfig,
                                "selectable",
                                callback=lambda x: gobject.baseobject.translation_ui.translate_text.setselectable(),
                            ),
                        ],
                    ),
                ),
                0,
                "group",
            )
        ],
    ]
    return xingweigrid


def setTabThree_lazy(self, basel):

    tab, do = makesubtab_lazy(
        _TRL(["文本设置", "界面主题", "窗口行为", "工具按钮", "窗口缩放"]),
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
