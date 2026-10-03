"""ExPillBar —— FluentUI PillTabs 风格的可换行 pill 条。

QTabBar 不支持多行换行（长列表只能出滚动按钮）；本控件按插件
drawPillTab 的绘制配方（fluentui3style.cpp / fluentui3colors.h）
自绘：圆角 2px，选中(tabBarSelectedBackground)/悬停(
tabBarHoverBackground)/窗底三态填充 + controlStrokePrimary 描边，
右端 × 关闭区（ChromeClose 字形，悬停点亮）。横向排满自动换行。
API 对齐 QTabBar 子集：addTab/insertTab/removeTab/tabText/count +
tabClicked/tabCloseRequested（游戏数据-标签 用）。"""

from qtsymbols import (
    QColor,
    QFont,
    QMouseEvent,
    QPainter,
    QPalette,
    QPen,
    QRect,
    QRectF,
    QSize,
    QSizePolicy,
    Qt,
    QWidget,
    pyqtSignal,
)
from gui.fluent.expander import _exp_is_dark_palette

# ChromeClose（Segoe Fluent Icons）
_ICON_CHROME_CLOSE = ""


class ExPillBar(QWidget):
    tabClicked = pyqtSignal(int)
    tabCloseRequested = pyqtSignal(int)

    _PILL_H = 26
    _PAD_X = 9      # pill 内文本左右留白
    _CLOSE_W = 16   # × 区宽度
    _GAP = 4        # pill 间距
    _ROW_GAP = 4
    _MARGIN = 2

    def __init__(self, parent=None):
        super().__init__(parent)
        self._texts = []
        self._rects = []
        self._hover = -1
        self._hover_close = False
        self._pressed = -1
        self._current = -1
        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

    # ---- QTabBar 子集 ----
    def count(self):
        return len(self._texts)

    def tabText(self, index):
        if 0 <= index < len(self._texts):
            return self._texts[index]
        return ""

    def addTab(self, text):
        self._texts.append(text)
        self._relayout()
        return len(self._texts) - 1

    def insertTab(self, index, text):
        index = max(0, min(index, len(self._texts)))
        self._texts.insert(index, text)
        self._relayout()
        return index

    def removeTab(self, index):
        if not 0 <= index < len(self._texts):
            return
        self._texts.pop(index)
        if self._hover >= index:
            self._hover = -1
        if self._current == index:
            self._current = -1
        elif self._current > index:
            self._current -= 1
        self._relayout()

    # ---- 布局（换行；超长单标签钳宽 + 省略） ----
    def _relayout(self):
        self._rects = []
        fm = self.fontMetrics()
        maxw = max(0, self.width() - 2 * self._MARGIN)
        x = y = self._MARGIN
        for text in self._texts:
            w = (fm.horizontalAdvance(text) + self._PAD_X
                 + self._CLOSE_W + self._PAD_X)
            if w > maxw and maxw > 0:
                w = maxw
            if x > self._MARGIN and x + w > self._MARGIN + maxw:
                x = self._MARGIN
                y += self._PILL_H + self._ROW_GAP
            self._rects.append(QRect(x, y, w, self._PILL_H))
            x += w + self._GAP
        h = (y + self._PILL_H + self._MARGIN) if self._texts else (
            self._PILL_H + 2 * self._MARGIN)
        self.setFixedHeight(h)
        self.updateGeometry()
        self.update()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._relayout()

    def sizeHint(self):
        return QSize(120, self.height())

    # ---- 命中 ----
    def _close_rect(self, pill: QRect):
        return QRect(pill.right() - self._CLOSE_W - 3,
                     pill.top() + (pill.height() - self._CLOSE_W) // 2,
                     self._CLOSE_W, self._CLOSE_W)

    def _hit(self, pos):
        for i, r in enumerate(self._rects):
            if r.contains(pos):
                return i, self._close_rect(r).contains(pos)
        return -1, False

    # ---- 绘制（配色同插件 WINUI3Colors 的 pill 三态） ----
    def _colors(self):
        if _exp_is_dark_palette(self.palette()):
            # 暗：选中 82,82,84 / 悬停 12% 白 / 描边 7% 白
            return (QColor(82, 82, 84),
                    QColor(255, 255, 255, 31),
                    QColor(255, 255, 255, 18))
        # 亮：选中 206,206,206 / 悬停 7% 黑 / 描边 6% 黑
        return (QColor(206, 206, 206),
                QColor(0, 0, 0, 18),
                QColor(0, 0, 0, 15))

    def paintEvent(self, _):
        painter = QPainter(self)
        painter.setRenderHints(
            QPainter.RenderHint.Antialiasing
            | QPainter.RenderHint.TextAntialiasing)
        selected, hover, stroke = self._colors()
        window = self.palette().color(QPalette.ColorRole.Window)
        fm = self.fontMetrics()
        closefont = QFont("Segoe Fluent Icons")
        closefont.setPixelSize(10)
        for i, r in enumerate(self._rects):
            if i == self._current:
                fill = selected
            elif i == self._hover:
                fill = hover
            else:
                fill = window
            painter.setPen(QPen(stroke, 1.0))
            painter.setBrush(fill)
            painter.drawRoundedRect(QRectF(r), 2, 2)
            # 文本（超宽省略）。注意每轮显式设回 app 字体——上一轮画 ×
            # 时 setFont(图标字体) 会残留，后续 pill 文本会变成 10px 图标
            # 字体（首个 pill 与其余不一致的根源）
            cr = self._close_rect(r)
            tx = r.left() + self._PAD_X
            text = fm.elidedText(
                self._texts[i], Qt.TextElideMode.ElideRight, cr.left() - tx)
            painter.setFont(self.font())
            painter.setPen(self.palette().color(QPalette.ColorRole.Text))
            painter.drawText(QRect(tx, r.top(), cr.left() - tx, r.height()),
                             Qt.AlignmentFlag.AlignVCenter
                             | Qt.AlignmentFlag.AlignLeft, text)
            # ×（悬停点亮）
            closecolor = self.palette().color(QPalette.ColorRole.Text)
            closecolor.setAlpha(
                255 if (i == self._hover and self._hover_close) else 150)
            painter.setFont(closefont)
            painter.setPen(closecolor)
            painter.drawText(cr, Qt.AlignmentFlag.AlignCenter,
                             _ICON_CHROME_CLOSE)

    # ---- 交互 ----
    def mouseMoveEvent(self, e: QMouseEvent):
        i, close = self._hit(e.pos())
        changed = (i != self._hover) or (close != self._hover_close)
        self._hover, self._hover_close = i, close
        if i >= 0:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            self.unsetCursor()
        if changed:
            self.update()

    def leaveEvent(self, e):
        self._hover, self._hover_close = -1, False
        self.unsetCursor()
        self.update()
        super().leaveEvent(e)

    def mousePressEvent(self, e: QMouseEvent):
        if e.button() == Qt.MouseButton.LeftButton:
            self._pressed = self._hit(e.pos())[0]
        super().mousePressEvent(e)

    def mouseReleaseEvent(self, e: QMouseEvent):
        if e.button() == Qt.MouseButton.LeftButton:
            i, close = self._hit(e.pos())
            if i >= 0 and i == self._pressed:
                if close:
                    self.tabCloseRequested.emit(i)
                else:
                    self._current = i
                    self.tabClicked.emit(i)
        self._pressed = -1
        super().mouseReleaseEvent(e)
