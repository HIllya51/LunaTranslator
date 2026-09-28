import functools
from gui.setting.display_buttons import createbuttonwidget
from gui.setting.display_text import xianshigrid_style
from gui.setting.display_ui import uisetting
from gui.setting.display_scale import makescalew
from gui.usefulwidget import makescrollgrid


def display_nav_children(self):
    """显示设置的四个子页（原页内子页签）：返回 (标题, 构建器) 列表，
    由设置窗口挂到主导航 显示设置 节点下（FluentTabWidget.addNavChildPage）；
    首项同时作为父项页面内容。"""
    return [
        ("文本设置", lambda l: makescrollgrid(xianshigrid_style(self), l)),
        ("界面设置", lambda l: makescrollgrid(uisetting(self), l)),
        ("工具按钮", functools.partial(createbuttonwidget, self)),
        ("窗口缩放", lambda l: makescrollgrid(makescalew(), l)),
    ]
