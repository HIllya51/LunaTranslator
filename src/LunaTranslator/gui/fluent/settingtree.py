"""FluentSettingTree —— 设置页列表树基类。

工具按钮 / 文本预处理 / 翻译优化 / 快捷键 等设置列表页共用：
- 列标题（titles）经 _TR 翻译 + 居中，语言切换 updatelangtext 重翻译；
  titles=None 时隐藏标题栏（无标题形态，如快捷键页）
- 行内控件经 setItemWidget 挂载；_cell 构建行内格子（center 居中）、
  _slot 以同尺寸控件保留可选按钮的槽位（行间对齐）
- 拖拽排序为自管 DnD（draggable=True）：Qt 的 InternalMove 对带 item
  widget 的行是 remove+insert 重建、widget 全部丢失（同侧栏导航树，
  见 _gamelistnav 注释）。落点经 _ondrop(idx1, idx2) 交给子类改写
  数据并整体重建行（列表页行数有限，重建成本可忽略）
"""

from qtsymbols import (
    QAbstractItemView,
    QApplication,
    QDrag,
    QFrame,
    QHBoxLayout,
    QMimeData,
    QSizePolicy,
    Qt,
    QTreeWidget,
    QVBoxLayout,
    QWidget,
)
import functools

from gui.usefulwidget import D_getIconButton_mousefollow
from myutils.config import _TR

# 自管拖拽的 mime 标记（同视图内重排，无携带数据）
_RANKMOVE_MIME = "lunarankmove"


class FluentSettingTree(QTreeWidget):
    def __init__(self, parent=None, titles=None, draggable=False,
                 indentation=0):
        super().__init__(parent)
        self._titles = list(titles) if titles else None
        if self._titles is not None:
            self.setColumnCount(len(self._titles))
            self.setHeaderLabels([_TR(t) for t in self._titles])
            self.header().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            self.setHeaderHidden(True)
        self._draggable = draggable
        self._dragitem = None
        self._dragpos = None
        self.setRootIsDecorated(False)
        self.setIndentation(indentation)
        self.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        if draggable:
            # 自管拖拽（不启用 Qt 的 dragDropMode）
            self.setAcceptDrops(True)
            self.viewport().setAcceptDrops(True)
            self.setDropIndicatorShown(True)
        # 透明：让所在包裹（StyledPanel/卡）的底色透出（QSS 只作用于
        # 本控件类，见 makescroll 注释）
        self.setStyleSheet(
            "QTreeWidget{background-color:transparent;border:0;}")
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Expanding)

    def updatelangtext(self):
        # 语言切换：列标题重翻译（app 级事件过滤器驱动，同 LLabel）
        if self._titles is not None:
            for i, t in enumerate(self._titles):
                self.headerItem().setText(i, _TR(t))

    # ---- 行构建助手 ----
    def _cell(self, *ws, center=False):
        """行内格子：水平排布若干控件；center 时两侧 stretch 居中。"""
        w = QWidget()
        lay = QHBoxLayout(w)
        lay.setContentsMargins(6, 4, 6, 4)
        lay.setSpacing(8)
        if center:
            lay.addStretch(1)
        for x in ws:
            if x is not None:
                lay.addWidget(x)
        if center:
            lay.addStretch(1)
        return w

    def _slot(self, ref):
        """等宽占位：可选控件缺席时保留槽位（尺寸取 ref 控件），行间对齐。"""
        sp = QWidget()
        sp.setFixedSize(ref.size())
        return sp

    def _movecell(self, onmove):
        """上下移按钮（右键 = 置顶/置底），独占一列（无标题）。
        onmove(up: bool, tomax: bool) 由子类实现数据序调整 + 重建。"""
        return self._cell(
            D_getIconButton_mousefollow(
                callback=functools.partial(onmove, True, False),
                icon="fa.arrow-up",
                callback2=functools.partial(onmove, True, True),
                tips="上移",
            ),
            D_getIconButton_mousefollow(
                callback=functools.partial(onmove, False, False),
                icon="fa.arrow-down",
                callback2=functools.partial(onmove, False, True),
                tips="下移",
            ),
            center=True,
        )

    # ---- 自管拖拽（子类实现 _ondrop：改写数据序 + 重建行）----
    def mousePressEvent(self, ev):
        self._dragitem = self.itemAt(ev.pos())
        self._dragpos = ev.pos()
        return super().mousePressEvent(ev)

    def mouseMoveEvent(self, e):
        if (
            self._dragitem is not None
            and self._draggable
            and (e.buttons() & Qt.MouseButton.LeftButton)
            and (e.pos() - self._dragpos).manhattanLength()
            >= QApplication.startDragDistance()
        ):
            mime = QMimeData()
            mime.setText(_RANKMOVE_MIME)
            drag = QDrag(self)
            drag.setMimeData(mime)
            drag.exec(Qt.DropAction.MoveAction)
            return
        super().mouseMoveEvent(e)

    def _isrankmove(self, e):
        return e.mimeData().text().startswith(_RANKMOVE_MIME)

    def dragEnterEvent(self, e):
        if self._isrankmove(e):
            e.acceptProposedAction()
        else:
            e.ignore()

    def dragMoveEvent(self, e):
        if self._isrankmove(e):
            e.acceptProposedAction()
        else:
            e.ignore()

    def dropEvent(self, e):
        if not self._isrankmove(e):
            e.ignore()
            return
        src = self._dragitem
        self._dragitem = None
        if src is None or src.parent() is not None:
            e.ignore()  # 仅顶层行参与排序
            return
        idx1 = self.indexOfTopLevelItem(src)
        if idx1 < 0:
            e.ignore()
            return
        pos = e.pos()
        dst = self.itemAt(pos)
        if dst is None:
            # 落在内容之下：移到末尾
            idx2 = self.topLevelItemCount()
        else:
            if dst.parent() is not None:
                dst = dst.parent()
            r = self.visualItemRect(dst)
            idx2 = self.indexOfTopLevelItem(dst) + (
                1 if pos.y() > r.center().y() else 0)
        if idx1 < idx2:
            idx2 -= 1
        if 0 <= idx2 < self.topLevelItemCount() and idx2 != idx1:
            self._ondrop(idx1, idx2)
        e.acceptProposedAction()


def wrap_setting_tree(tree, margins=(0, 0, 0, 0)):
    """QFrame::StyledPanel 包裹（Gallery 包表格/树的方式：插件 PE_Frame
    = Base 底色 + 6px 圆角 + lineEdit 式描边）。"""
    frame = QFrame()
    frame.setFrameShape(QFrame.Shape.StyledPanel)
    flay = QVBoxLayout(frame)
    flay.setContentsMargins(*margins)
    flay.addWidget(tree)
    return frame
