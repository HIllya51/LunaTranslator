from qtsymbols import *
import functools, gobject
from myutils.post import POSTSOLVE
from myutils.utils import (
    selectdebugfile,
    checkpostlangmatch,
    loadpostsettingwindowmethod,
)
from myutils.config import globalconfig, postprocessconfig, static_data
from gui.usefulwidget import (
    D_getIconButton,
    getIconButton,
    D_getsimpleswitch,
    D_getdoclink,
)
from gui.dynalang import LLabel
from gui.fluent.settingtree import FluentSettingTree, wrap_setting_tree
from gui.inputdialog import (
    postconfigdialog,
    autoinitdialog,
    autoinitdialog_items,
    stringreplacedialog,
)


def getcomparelayout(self):

    w = QWidget()
    w.setFixedHeight(100)
    layout = QHBoxLayout(w)
    layout.setContentsMargins(0, 0, 0, 0)
    fromtext = QPlainTextEdit()
    totext = QPlainTextEdit()
    solvebutton = getIconButton(
        callback=lambda: totext.setPlainText(
            POSTSOLVE(fromtext.toPlainText(), useAll=True)
        ),
        icon="fa.chevron-right",
    )

    layout.addWidget(fromtext)
    layout.addWidget(solvebutton)
    layout.addWidget(totext)
    gobject.base.connectsignal(
        gobject.base.showandsolvesig,
        lambda s, x: (fromtext.setPlainText(s), totext.setPlainText(x)),
    )

    return w


class _PreProcessTree(FluentSettingTree):
    """文本预处理列表：使用 / 设置（无标题列）/预处理方法 / 移动（末列），
    拖拽或上下移按钮排序。上下移在可见列表内循环（首行再上移到末尾、
    末行再下移到开头；右键置顶/置底）。排序写回 postprocess_rank：
    可见项按新序填回原可见槽位（不在 postprocessconfig 的项原地保留，
    等价于旧版逐次交换的累计效果）。"""

    def __init__(self, host, parent=None):
        super().__init__(
            parent,
            titles=["使用", "", "预处理方法", ""],
            draggable=True,
        )
        self._host = host
        hdr = self.header()
        for c in (0, 1, 3):
            hdr.setSectionResizeMode(
                c, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.rebuild()

    def rebuild(self):
        self.clear()
        for post in globalconfig["postprocess_rank"]:
            if post not in postprocessconfig:
                continue
            conf = postprocessconfig[post]
            item = QTreeWidgetItem()
            item.setData(0, Qt.ItemDataRole.UserRole, post)
            self.addTopLevelItem(item)
            btn = self._configbtn(post, conf)
            namecell = self._cell(
                D_getdoclink(
                    "textprocess.html#anchor-" + post,
                    tipsfor=conf["name"],
                )(),
                LLabel(conf["name"]),
            )
            self.setItemWidget(
                item, 0, self._cell(
                    D_getsimpleswitch(conf, "use")(), center=True))
            # 设置按钮独占一列（无标题；缺席则空）
            if btn is not None:
                self.setItemWidget(item, 1, self._cell(btn, center=True))
            self.setItemWidget(item, 2, namecell)
            # 上下移按钮列（末列，右键置顶/置底）
            self.setItemWidget(
                item, 3, self._movecell(functools.partial(self._move, post)))

    def _configbtn(self, post, conf):
        """设置按钮：_11=编辑脚本；有 args=设置弹窗；无=None（槽位）。"""
        if post == "_11":
            return D_getIconButton(
                callback=lambda: selectdebugfile("mypost.py"),
                icon="fa.edit",
                tips=conf["name"] + "_编辑",
            )()
        if "args" not in conf:
            return None
        if post == "stringreplace":
            callback = functools.partial(
                stringreplacedialog, self._host, conf)
        elif isinstance(list(conf["args"].values())[0], dict):
            callback = functools.partial(
                postconfigdialog,
                self._host,
                conf["args"]["替换内容"],
                conf["name"],
                ["原文内容", "替换为"],
            )
        else:
            items = autoinitdialog_items(conf)
            callback = functools.partial(
                autoinitdialog, self._host, conf["args"],
                conf["name"], 600, items,
            )
        return D_getIconButton(
            callback=callback, tips=conf["name"] + "_设置")()

    def _applymove(self, idx1, idx2):
        """可见列表内 idx1 -> idx2，重映射回 postprocess_rank。"""
        rank = globalconfig["postprocess_rank"]
        filtered = [p for p in rank if p in postprocessconfig]
        post = filtered.pop(idx1)
        filtered.insert(idx2, post)
        it = iter(filtered)
        globalconfig["postprocess_rank"] = [
            next(it) if p in postprocessconfig else p for p in rank]
        self.rebuild()

    def _ondrop(self, idx1, idx2):
        self._applymove(idx1, idx2)

    def _move(self, post, up, tomax):
        """上下移按钮：可见列表内循环移一位（首行再上移到末尾、末行
        再下移到开头），右键（tomax）置顶/置底。"""
        filtered = [p for p in globalconfig["postprocess_rank"]
                    if p in postprocessconfig]
        idx1 = filtered.index(post)
        if tomax:
            idx2 = 0 if up else len(filtered) - 1
        else:
            idx2 = (idx1 + (-1 if up else 1)) % len(filtered)
        if idx2 == idx1:
            return
        self._applymove(idx1, idx2)


class _TransOptimiTree(FluentSettingTree):
    """翻译优化列表：使用 / 设置（无标题列）/名称 三列（静态，无排序）。"""

    def __init__(self, host, parent=None):
        super().__init__(
            parent,
            titles=["使用", "", "名称"],
        )
        self._host = host
        hdr = self.header()
        for c in (0, 1):
            hdr.setSectionResizeMode(
                c, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.rebuild()

    def rebuild(self):
        self.clear()
        for item_ in static_data["transoptimi"]:
            name = item_["name"]
            visname = item_["visname"]
            if not checkpostlangmatch(name):
                continue
            item = QTreeWidgetItem()
            item.setData(0, Qt.ItemDataRole.UserRole, name)
            self.addTopLevelItem(item)
            setting = loadpostsettingwindowmethod(name)

            def __(f, host):
                return f(host)

            btn = None
            if setting:
                kwarg = dict(
                    callback=functools.partial(__, setting, self._host))
                kwarg.update(tips=visname + "_设置")
                if name == "myprocess":
                    kwarg.update(icon="fa.edit")
                    kwarg.update(tips=visname + "_编辑")
                btn = D_getIconButton(**kwarg)()
            namecell = self._cell(
                D_getdoclink(
                    "transoptimi.html#anchor-" + name, tipsfor=visname)(),
                LLabel(visname),
            )
            self.setItemWidget(
                item, 0, self._cell(
                    D_getsimpleswitch(globalconfig["transoptimi"], name)(),
                    center=True))
            # 设置按钮独占一列（无标题；缺席则空）
            if btn is not None:
                self.setItemWidget(item, 1, self._cell(btn, center=True))
            self.setItemWidget(item, 2, namecell)


def transopti_nav_children(self):
    """文本处理的两个子页（原页内子页签 文本预处理/翻译优化）：由设置窗口
    挂到主导航 文本处理 节点下（FluentTabWidget.addNavChildPage）；首项
    同时作为父项页面内容。"""

    def ___(lay: QVBoxLayout):
        content = QWidget()
        vlay = QVBoxLayout(content)
        vlay.setContentsMargins(16, 16, 16, 12)
        vlay.setSpacing(8)
        lay.addWidget(content)
        vlay.addWidget(wrap_setting_tree(_PreProcessTree(self)), 1)
        vlay.addWidget(getcomparelayout(self))

    def ___2(lay: QVBoxLayout):
        content = QWidget()
        vlay = QVBoxLayout(content)
        vlay.setContentsMargins(16, 16, 16, 12)
        lay.addWidget(content)
        vlay.addWidget(wrap_setting_tree(_TransOptimiTree(self)), 1)

    return [("文本预处理", ___), ("翻译优化", ___2)]
